Shader "FidgetingApp/EDC/MagneticSilverShippingR3"
{
    Properties
    {
        _BaseColor("Conductor Tint", Color) = (0.970, 0.965, 0.940, 1)
        _Metallic("Metallic", Range(0, 1)) = 1
        _Roughness("Roughness", Range(0.015, 1)) = 0.03
        _ReflectionStrength("Reflection Strength", Range(0, 2)) = 1.12
        _ReflectionContrast("Reflection Contrast", Range(0.5, 2)) = 1.32
        _DiffuseLift("Diffuse Lift", Range(0, 0.25)) = 0.015
        _SeamWorldY("Seam World Y", Float) = -0.08
        _SeamWidth("Seam Width", Range(0.001, 0.2)) = 0.035
        _SeamDarkness("Seam Darkness", Range(0, 1)) = 0.68
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" "Queue"="Geometry" "RenderPipeline"="UniversalPipeline" }

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BLENDING
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BOX_PROJECTION

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/GlobalIllumination.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _BaseColor;
                half _Metallic;
                half _Roughness;
                half _ReflectionStrength;
                half _ReflectionContrast;
                half _DiffuseLift;
                half _SeamWorldY;
                half _SeamWidth;
                half _SeamDarkness;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                half3 normalOS : NORMAL;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                half3 normalWS : TEXCOORD1;
                float4 shadowCoord : TEXCOORD2;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                VertexPositionInputs positionInputs = GetVertexPositionInputs(input.positionOS.xyz);
                output.positionCS = positionInputs.positionCS;
                output.positionWS = positionInputs.positionWS;
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                output.shadowCoord = GetShadowCoord(positionInputs);
                return output;
            }

            half3 NeutralLayeredReflection(half3 direction)
            {
                half3 broadKey = normalize(half3(-0.70h, 0.30h, -0.64h));
                half3 topStrip = normalize(half3(0.12h, 0.98h, -0.16h));
                half3 sideFill = normalize(half3(0.78h, 0.04h, 0.62h));
                half key = pow(saturate(dot(direction, broadKey)), 4.0h);
                half strip = pow(saturate(dot(direction, topStrip)), 18.0h);
                half fill = pow(saturate(dot(direction, sideFill)), 7.0h);
                half horizon = pow(1.0h - abs(direction.y), 2.2h);
                half value = 0.29h
                    + 0.48h * key
                    + 0.54h * strip
                    + 0.25h * fill
                    + 0.12h * horizon;
                return value * half3(1.006h, 1.0h, 0.992h);
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half3 normalWS = normalize(input.normalWS);
                half3 viewDirWS = SafeNormalize(GetWorldSpaceViewDir(input.positionWS));
                Light mainLight = GetMainLight(input.shadowCoord);
                half3 lightDirWS = normalize(mainLight.direction);
                half3 halfDirWS = SafeNormalize(viewDirWS + lightDirWS);

                half ndl = saturate(dot(normalWS, lightDirWS));
                half ndh = saturate(dot(normalWS, halfDirWS));
                half ndv = saturate(dot(normalWS, viewDirWS));
                half fresnel = Pow4(1.0h - ndv);
                half3 conductorF0 = lerp(0.04h.xxx, _BaseColor.rgb, _Metallic);
                half3 conductorF = conductorF0 + (1.0h.xxx - conductorF0) * fresnel;

                half perceptualRoughness = saturate(_Roughness);
                half3 reflectionVector = reflect(-viewDirWS, normalWS);
                half2 screenUv = GetNormalizedScreenSpaceUV(input.positionCS);
                half3 environment = GlossyEnvironmentReflection(
                    reflectionVector,
                    input.positionWS,
                    perceptualRoughness,
                    1.0h,
                    screenUv
                );
                environment = max(
                    environment,
                    NeutralLayeredReflection(reflectionVector));
                environment = saturate(
                    (environment - 0.22h.xxx) * _ReflectionContrast + 0.22h.xxx
                );

                half specularPower = lerp(384.0h, 10.0h, perceptualRoughness);
                half directSpecular = pow(ndh, specularPower);
                half3 directReflection =
                    conductorF * directSpecular * mainLight.color * mainLight.shadowAttenuation;
                half3 environmentReflection =
                    environment * conductorF * _ReflectionStrength;
                half verticalPosition = saturate(
                    (input.positionWS.y + 0.006h) / 0.012h);
                half finiteSoftboxLayer = lerp(
                    0.78h,
                    1.18h,
                    smoothstep(0.0h, 1.0h, verticalPosition));
                finiteSoftboxLayer += 0.12h * exp(
                    -24.0h * (verticalPosition - 0.72h)
                    * (verticalPosition - 0.72h));
                environmentReflection *= finiteSoftboxLayer;

                half3 diffuse = _BaseColor.rgb * (1.0h - _Metallic);
                diffuse *= mainLight.color * ndl * mainLight.shadowAttenuation;
                diffuse += _BaseColor.rgb * _DiffuseLift * (0.45h + 0.55h * ndl);

                half seamDistance = abs(input.positionWS.y - _SeamWorldY);
                half sideFacing = smoothstep(0.36h, 0.76h, abs(normalWS.y));
                half seam = (1.0h - smoothstep(0.0h, _SeamWidth, seamDistance)) * sideFacing;
                half seamMultiplier = lerp(1.0h, 1.0h - _SeamDarkness, seam);

                half3 color =
                    (environmentReflection + directReflection + diffuse) * seamMultiplier;
                return half4(max(color, 0.0h.xxx), 1.0h);
            }
            ENDHLSL
        }

        UsePass "Universal Render Pipeline/Lit/ShadowCaster"
        UsePass "Universal Render Pipeline/Lit/DepthOnly"
    }
}
