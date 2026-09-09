Shader "FidgetingApp/FanCardSatinSilver"
{
    Properties
    {
        _BaseColor("Warm Silver", Color) = (0.40, 0.385, 0.36, 1)
        _Metallic("Metallic", Range(0, 1)) = 1.0
        _Smoothness("Smoothness", Range(0, 1)) = 0.24
        [Normal] _BumpMap("Bead Normal", 2D) = "bump" {}
        _BumpScale("Bead Strength", Range(0, 1)) = 0.13
    }

    SubShader
    {
        Tags
        {
            "RenderPipeline" = "UniversalPipeline"
            "RenderType" = "Opaque"
            "Queue" = "Geometry"
        }

        Pass
        {
            Name "UniversalForward"
            Tags { "LightMode" = "UniversalForward" }
            ZWrite On
            ZTest LEqual
            Cull Back

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.0
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Packing.hlsl"
            #include "FanCardMovingLights.hlsl"

            TEXTURE2D(_BumpMap);
            SAMPLER(sampler_BumpMap);

            CBUFFER_START(UnityPerMaterial)
                float4 _BumpMap_ST;
                half4 _BaseColor;
                half _Metallic;
                half _Smoothness;
                half _BumpScale;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float4 tangentOS : TANGENT;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                half3 normalWS : TEXCOORD1;
                half3 tangentWS : TEXCOORD2;
                half3 bitangentWS : TEXCOORD3;
                float2 bumpUv : TEXCOORD4;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionWS = TransformObjectToWorld(input.positionOS.xyz);
                output.positionCS = TransformWorldToHClip(output.positionWS);
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                output.tangentWS = TransformObjectToWorldDir(input.tangentOS.xyz);
                half tangentSign = input.tangentOS.w * GetOddNegativeScale();
                output.bitangentWS = cross(output.normalWS, output.tangentWS)
                    * tangentSign;
                output.bumpUv = TRANSFORM_TEX(input.uv, _BumpMap);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half3 tangentNormal = UnpackNormalScale(
                    SAMPLE_TEXTURE2D(_BumpMap, sampler_BumpMap, input.bumpUv),
                    _BumpScale);
                float3 normalWS = normalize(
                    input.tangentWS * tangentNormal.x
                    + input.bitangentWS * tangentNormal.y
                    + input.normalWS * tangentNormal.z);
                float3 viewWS = SafeNormalize(GetWorldSpaceViewDir(input.positionWS));
                Light mainLight = GetMainLight(
                    TransformWorldToShadowCoord(input.positionWS));
                float nDotL = saturate(dot(normalWS, mainLight.direction));
                float3 halfVector = SafeNormalize(mainLight.direction + viewWS);
                float nDotH = saturate(dot(normalWS, halfVector));
                float nDotV = saturate(dot(normalWS, viewWS));
                float roughness = saturate(1.0 - _Smoothness);
                // Bead-blast silver keeps a wide lobe. The narrow term only
                // shapes a readable band; it must never become a mirror dot.
                float broadSpecular = pow(
                    nDotH,
                    lerp(2.0, 9.0, _Smoothness));
                float bandSpecular = pow(
                    nDotH,
                    lerp(9.0, 34.0, _Smoothness));
                half attenuation = mainLight.distanceAttenuation
                    * mainLight.shadowAttenuation;
                half3 ambientIrradiance = SampleSH(normalWS);
                half3 f0 = lerp(
                    half3(0.04, 0.04, 0.04),
                    _BaseColor.rgb,
                    _Metallic);
                half3 fresnel = f0 + (1.0 - f0)
                    * pow(1.0 - nDotV, 5.0);
                float3 reflectionWS = FanCardRotateReflection(
                    reflect(-viewWS, normalWS));
                half3 environmentSpecular = GlossyEnvironmentReflection(
                    reflectionWS,
                    roughness,
                    1.0);
                float hemisphere = saturate(normalWS.y * 0.5 + 0.5);

                // Top-down key plus SH/cubemap carry the room. Do not add an
                // unexplained diagonal stripe or restore a grey SH floor.
                half3 color = _BaseColor.rgb * (
                    0.05
                    + hemisphere * 0.17
                    + ambientIrradiance * 0.46);
                color += _BaseColor.rgb
                    * mainLight.color
                    * nDotL
                    * attenuation
                    * lerp(1.0, 0.86, _Metallic);
                color += mainLight.color
                    * fresnel
                    * broadSpecular
                    * attenuation
                    * lerp(0.10, 0.30, _Metallic)
                    * (1.0 - roughness * 0.12);
                color += mainLight.color
                    * fresnel
                    * bandSpecular
                    * attenuation
                    * lerp(0.12, 0.62, _Metallic);
                color += FanCardSampleAdditionalLights(
                    input.positionWS,
                    input.positionCS,
                    _BaseColor.rgb,
                    normalWS,
                    viewWS,
                    _Metallic,
                    _Smoothness);
                color += environmentSpecular
                    * fresnel
                    * lerp(0.12, 0.42, _Metallic);
                return half4(color, 1.0);
            }
            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }
            ZWrite On
            ZTest LEqual
            ColorMask 0
            Cull Back

            HLSLPROGRAM
            #pragma vertex ShadowVert
            #pragma fragment ShadowFrag
            #pragma target 3.0
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings { float4 positionCS : SV_POSITION; };

            Varyings ShadowVert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                return output;
            }

            half4 ShadowFrag(Varyings input) : SV_Target { return 0; }
            ENDHLSL
        }
    }
}
