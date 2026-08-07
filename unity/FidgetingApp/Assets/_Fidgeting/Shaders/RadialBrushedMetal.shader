Shader "ThreeBlade/RadialBrushedMetal"
{
    Properties
    {
        _BaseColor("Base Color", Color) = (0.65, 0.67, 0.68, 1)
        _BaseMap("Radial Brush", 2D) = "white" {}
        [Normal] _BumpMap("Brush Normal", 2D) = "bump" {}
        _BumpScale("Brush Strength", Range(0, 1)) = 0.18
        _Metallic("Metallic", Range(0, 1)) = 1
        _Smoothness("Smoothness", Range(0, 1)) = 0.81
        _RadialContrast("Radial Specular Contrast", Range(0, 0.3)) = 0.12
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
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }

            HLSLPROGRAM
            #pragma target 2.0
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_fog
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURE2D(_BaseMap);
            SAMPLER(sampler_BaseMap);
            TEXTURE2D(_BumpMap);
            SAMPLER(sampler_BumpMap);

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                half4 _BaseColor;
                half _BumpScale;
                half _Metallic;
                half _Smoothness;
                half _RadialContrast;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                half3 normalOS : NORMAL;
                half4 tangentOS : TANGENT;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                half3 normalWS : TEXCOORD1;
                half4 tangentWS : TEXCOORD2;
                float2 uv : TEXCOORD3;
                half fogFactor : TEXCOORD4;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                VertexPositionInputs positionInputs =
                    GetVertexPositionInputs(input.positionOS.xyz);
                VertexNormalInputs normalInputs =
                    GetVertexNormalInputs(input.normalOS, input.tangentOS);
                output.positionCS = positionInputs.positionCS;
                output.positionWS = positionInputs.positionWS;
                output.normalWS = normalInputs.normalWS;
                output.tangentWS = half4(
                    normalInputs.tangentWS,
                    input.tangentOS.w * GetOddNegativeScale());
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                output.fogFactor = ComputeFogFactor(positionInputs.positionCS.z);
                return output;
            }

            half3 EvaluateLight(
                Light lightData,
                half3 baseColor,
                half3 normalWS,
                half3 viewDirectionWS,
                half smoothness,
                half metallic)
            {
                half3 lightDirection = normalize(lightData.direction);
                half nDotL = saturate(dot(normalWS, lightDirection));
                half3 halfDirection = normalize(lightDirection + viewDirectionWS);
                half nDotH = saturate(dot(normalWS, halfDirection));
                half specularPower = exp2(3.0h + smoothness * 8.0h);
                half specular = pow(nDotH, specularPower)
                    * (specularPower + 2.0h)
                    * 0.055h;
                half3 f0 = lerp(0.04h.xxx, baseColor, metallic);
                half3 diffuse = baseColor * (1.0h - metallic) * nDotL;
                half attenuation = lightData.distanceAttenuation
                    * lightData.shadowAttenuation;
                return (diffuse + f0 * specular * nDotL)
                    * lightData.color
                    * attenuation;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half4 brushSample = SAMPLE_TEXTURE2D(
                    _BaseMap,
                    sampler_BaseMap,
                    input.uv);
                half3 baseColor = _BaseColor.rgb * brushSample.rgb;

                half3 normalTS = UnpackNormalScale(
                    SAMPLE_TEXTURE2D(_BumpMap, sampler_BumpMap, input.uv),
                    _BumpScale);
                half3 tangentWS = normalize(input.tangentWS.xyz);
                half3 normalWSBase = normalize(input.normalWS);
                half3 bitangentWS = normalize(
                    cross(normalWSBase, tangentWS) * input.tangentWS.w);
                half3 normalWS = normalize(mul(
                    normalTS,
                    half3x3(tangentWS, bitangentWS, normalWSBase)));
                half3 viewDirectionWS = SafeNormalize(
                    GetWorldSpaceViewDir(input.positionWS));

                float2 centeredUv = input.uv - 0.5;
                half radialBand = sin(atan2(centeredUv.y, centeredUv.x) * 8.0);
                half localSmoothness = saturate(
                    _Smoothness + radialBand * _RadialContrast);

                half3 lighting = 0;
                float4 shadowCoord = TransformWorldToShadowCoord(input.positionWS);
                lighting += EvaluateLight(
                    GetMainLight(shadowCoord),
                    baseColor,
                    normalWS,
                    viewDirectionWS,
                    localSmoothness,
                    _Metallic);

                uint additionalLightCount = GetAdditionalLightsCount();
                for (uint lightIndex = 0u;
                    lightIndex < additionalLightCount;
                    ++lightIndex)
                {
                    lighting += EvaluateLight(
                        GetAdditionalLight(lightIndex, input.positionWS),
                        baseColor,
                        normalWS,
                        viewDirectionWS,
                        localSmoothness,
                        _Metallic);
                }

                half3 reflectionDirection = reflect(-viewDirectionWS, normalWS);
                half perceptualRoughness = 1.0h - localSmoothness;
                half reflectionMip = perceptualRoughness * 6.0h;
                half4 encodedReflection = SAMPLE_TEXTURECUBE_LOD(
                    unity_SpecCube0,
                    samplerunity_SpecCube0,
                    reflectionDirection,
                    reflectionMip);
                half3 reflection = DecodeHDREnvironment(
                    encodedReflection,
                    unity_SpecCube0_HDR);
                half3 f0 = lerp(0.04h.xxx, baseColor, _Metallic);
                half fresnel = pow(
                    1.0h - saturate(dot(normalWS, viewDirectionWS)),
                    5.0h);
                half3 color = baseColor * 0.50h
                    + lighting
                    + reflection * lerp(f0, 1.0h.xxx, fresnel) * 1.08h;
                color = MixFog(color, input.fogFactor);
                return half4(color, 1.0h);
            }
            ENDHLSL
        }

        UsePass "Universal Render Pipeline/Lit/ShadowCaster"
        UsePass "Universal Render Pipeline/Lit/DepthOnly"
    }
}
