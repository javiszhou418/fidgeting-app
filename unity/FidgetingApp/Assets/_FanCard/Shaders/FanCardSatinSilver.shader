Shader "FidgetingApp/FanCardSatinSilver"
{
    Properties
    {
        _BaseColor("Warm Silver", Color) = (0.40, 0.385, 0.36, 1)
        _Metallic("Metallic", Range(0, 1)) = 1.0
        _Smoothness("Smoothness", Range(0, 1)) = 0.36
        [Normal] _BumpMap("Bead Normal", 2D) = "bump" {}
        _BumpScale("Bead Strength", Range(0, 1)) = 0.06
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

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Packing.hlsl"

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
                float3 positionOS : TEXCOORD1;
                half3 normalWS : TEXCOORD2;
                half3 tangentWS : TEXCOORD3;
                half3 bitangentWS : TEXCOORD4;
                float2 bumpUv : TEXCOORD5;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionOS = input.positionOS.xyz;
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
                float broadSpecular = pow(
                    saturate(dot(normalWS, halfVector)),
                    lerp(5.0, 12.0, _Smoothness));

                // A large reflected panel sweeps diagonally over each satin
                // face. It is intentionally broad enough to read on a phone,
                // while the normal map keeps the highlight bead-blasted.
                float2 panelDelta = float2(
                    (input.positionOS.x + 0.010) / 0.040,
                    (input.positionOS.z - 0.014) / 0.056);
                float softPanel = exp2(-dot(panelDelta, panelDelta) * 1.35);
                float diagonalBand = smoothstep(
                    -0.65,
                    0.55,
                    input.positionOS.z * 24.0 - input.positionOS.x * 15.0);
                softPanel *= lerp(0.72, 1.0, diagonalBand);
                float bandCoordinate = input.positionOS.x * 0.80
                    + input.positionOS.z * 0.30;
                float reflectedBand = exp2(-pow(
                    (bandCoordinate + 0.004) / 0.012,
                    2.0) * 1.55);
                softPanel = max(softPanel * 0.48, reflectedBand);

                half3 color = _BaseColor.rgb
                    * (0.54 + nDotL * mainLight.shadowAttenuation * 0.32);
                color += half3(0.94, 0.84, 0.69) * softPanel * 0.42;
                color += half3(0.62, 0.70, 0.78) * broadSpecular * 0.11;
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
