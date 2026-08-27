Shader "FidgetingApp/EDC/MagneticCrystalShippingR2"
{
    Properties
    {
        _MaskMap("Artwork R / Border G / Combined B", 2D) = "black" {}
        _CrystalColor("Blood Red Crystal", Color) = (0.34, 0.008, 0.018, 1)
        _MotifColor("Black Etch", Color) = (0.003, 0.002, 0.003, 1)
        _Roughness("Crystal Roughness", Range(0.01, 0.5)) = 0.035
        _ClearCoat("Clear Coat", Range(0, 1)) = 1
        _ReflectionStrength("Environment Reflection", Range(0, 2)) = 0.72
        _Iridescence("Restrained Iridescence", Range(0, 0.5)) = 0.10
        _CrystalBrightness("Crystal Brightness", Range(0.5, 2)) = 1.18
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

            TEXTURE2D(_MaskMap);
            SAMPLER(sampler_MaskMap);

            CBUFFER_START(UnityPerMaterial)
                float4 _MaskMap_ST;
                half4 _CrystalColor;
                half4 _MotifColor;
                half _Roughness;
                half _ClearCoat;
                half _ReflectionStrength;
                half _Iridescence;
                half _CrystalBrightness;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                half3 normalWS : TEXCOORD1;
                float2 uv : TEXCOORD2;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                VertexPositionInputs position = GetVertexPositionInputs(input.positionOS.xyz);
                output.positionCS = position.positionCS;
                output.positionWS = position.positionWS;
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                output.uv = TRANSFORM_TEX(input.uv, _MaskMap);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half3 normalWS = normalize(input.normalWS);
                half3 viewWS = SafeNormalize(GetWorldSpaceViewDir(input.positionWS));
                half3 maskSample = SAMPLE_TEXTURE2D(
                    _MaskMap,
                    sampler_MaskMap,
                    input.uv).rgb;
                half motifMask = saturate(max(maskSample.r, maskSample.g));
                half crystalMask = 1.0h - motifMask;

                half3 baseColor = lerp(
                    _CrystalColor.rgb * _CrystalBrightness,
                    _MotifColor.rgb,
                    motifMask);
                float4 shadowCoord = TransformWorldToShadowCoord(input.positionWS);
                Light mainLight = GetMainLight(shadowCoord);
                half nDotL = saturate(dot(normalWS, mainLight.direction));
                half nDotV = saturate(dot(normalWS, viewWS));
                half fresnel = pow(1.0h - nDotV, 5.0h);

                half3 ambient = SampleSH(normalWS);
                half3 diffuse = baseColor
                    * (ambient * 0.48h
                        + mainLight.color
                        * (0.22h + 0.78h * nDotL)
                        * mainLight.shadowAttenuation);

                half3 halfVector = SafeNormalize(mainLight.direction + viewWS);
                half specularPower = lerp(180.0h, 38.0h, saturate(_Roughness * 2.0h));
                half directSpecular = pow(
                    saturate(dot(normalWS, halfVector)),
                    specularPower)
                    * _ClearCoat
                    * mainLight.shadowAttenuation;

                half3 reflectionDirection = reflect(-viewWS, normalWS);
                half2 screenUv = GetNormalizedScreenSpaceUV(input.positionCS);
                half3 environment = GlossyEnvironmentReflection(
                    reflectionDirection,
                    input.positionWS,
                    _Roughness,
                    1.0h,
                    screenUv);
                half reflectionWeight = _ReflectionStrength
                    * lerp(0.16h, 0.86h, fresnel)
                    * lerp(1.0h, 0.70h, motifMask);

                half phase = fresnel * 2.2h + nDotL * 0.18h;
                half3 interference = 0.5h + 0.5h * cos(
                    6.28318h * (phase + half3(0.00h, 0.33h, 0.67h)));
                half3 iridescent = interference
                    * _Iridescence
                    * crystalMask
                    * (0.3h + 0.7h * fresnel);

                half3 color = diffuse
                    + directSpecular * mainLight.color
                    + environment * reflectionWeight
                    + iridescent;
                return half4(color, 1.0h);
            }
            ENDHLSL
        }
    }
    FallBack Off
}
