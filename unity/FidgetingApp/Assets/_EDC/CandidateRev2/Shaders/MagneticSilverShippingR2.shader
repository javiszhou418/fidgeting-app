Shader "FidgetingApp/EDC/MagneticSilverShippingR2"
{
    Properties
    {
        _BaseColor("Polished Silver", Color) = (0.90, 0.89, 0.86, 1)
        _Roughness("Roughness", Range(0.01, 0.4)) = 0.06
        _ReflectionStrength("Reflection Strength", Range(0, 2)) = 0.92
        _DiffuseLift("Diffuse Lift", Range(0, 1)) = 0.12
        _SeamWorldY("Assembly Seam World Y", Float) = 0
        _SeamWidth("Assembly Seam Width", Range(0.00005, 0.001)) = 0.00024
        _SeamDarkness("Assembly Seam Darkness", Range(0, 1)) = 0.88
    }
    SubShader
    {
        Tags
        {
            "RenderType" = "Opaque"
            "RenderPipeline" = "UniversalPipeline"
            "Queue" = "Geometry"
        }
        Pass
        {
            Name "UniversalForward"
            Tags { "LightMode" = "UniversalForward" }
            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_fragment _ _MAIN_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BLENDING
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BOX_PROJECTION
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/GlobalIllumination.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _BaseColor;
                half _Roughness;
                half _ReflectionStrength;
                half _DiffuseLift;
                float _SeamWorldY;
                float _SeamWidth;
                half _SeamDarkness;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                half3 normalWS : TEXCOORD1;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                VertexPositionInputs position = GetVertexPositionInputs(input.positionOS.xyz);
                output.positionCS = position.positionCS;
                output.positionWS = position.positionWS;
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half3 normalWS = normalize(input.normalWS);
                half3 viewWS = SafeNormalize(GetWorldSpaceViewDir(input.positionWS));
                float4 shadowCoord = TransformWorldToShadowCoord(input.positionWS);
                Light mainLight = GetMainLight(shadowCoord);
                half nDotL = saturate(dot(normalWS, mainLight.direction));
                half nDotV = saturate(dot(normalWS, viewWS));
                half fresnel = pow(1.0h - nDotV, 5.0h);

                half3 reflectionDirection = reflect(-viewWS, normalWS);
                half2 screenUv = GetNormalizedScreenSpaceUV(input.positionCS);
                half3 environment = GlossyEnvironmentReflection(
                    reflectionDirection,
                    input.positionWS,
                    _Roughness,
                    1.0h,
                    screenUv);
                half3 baseLift = _BaseColor.rgb
                    * _DiffuseLift
                    * (0.65h + 0.35h * nDotL);
                half3 reflected = environment
                    * _ReflectionStrength
                    * (0.72h + 0.28h * fresnel);

                half3 halfVector = SafeNormalize(mainLight.direction + viewWS);
                half directSpecular = pow(
                    saturate(dot(normalWS, halfVector)),
                    112.0h)
                    * mainLight.shadowAttenuation;
                half sideMask = saturate(1.0h - abs(normalWS.y));
                half seam = 1.0h - smoothstep(
                    0.0h,
                    max(_SeamWidth, 0.000001h),
                    abs(input.positionWS.y - _SeamWorldY));
                half seamFactor = saturate(seam * sideMask);
                half3 color = baseLift
                    + reflected
                    + directSpecular * mainLight.color * 0.42h;
                color *= lerp(1.0h, 1.0h - _SeamDarkness, seamFactor);
                return half4(color, 1.0h);
            }
            ENDHLSL
        }
    }
    FallBack Off
}
