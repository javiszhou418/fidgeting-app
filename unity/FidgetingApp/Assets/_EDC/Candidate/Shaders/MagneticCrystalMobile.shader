Shader "FidgetingApp/EDC/MagneticCrystalMobile"
{
    Properties
    {
        _BaseMap("Independent Artwork", 2D) = "white" {}
        _BaseColor("Blood Red Tint", Color) = (0.42, 0.002, 0.008, 1)
        _ClearCoat("Clear Coat", Range(0, 1)) = 0.92
        _Iridescence("Iridescence", Range(0, 1)) = 0.16
        _TransmissionApprox("Transmission Approximation", Range(0, 1)) = 0.18
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
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURE2D(_BaseMap);
            SAMPLER(sampler_BaseMap);

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                half4 _BaseColor;
                half _ClearCoat;
                half _Iridescence;
                half _TransmissionApprox;
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
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half3 normalWS = normalize(input.normalWS);
                half3 viewWS = SafeNormalize(GetWorldSpaceViewDir(input.positionWS));
                Light mainLight = GetMainLight();
                half nDotL = saturate(dot(normalWS, mainLight.direction));
                half fresnel = pow(1.0h - saturate(dot(normalWS, viewWS)), 4.0h);
                half3 artwork = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, input.uv).rgb;
                half3 bloodRed = artwork * _BaseColor.rgb;
                half phase = fresnel * 2.4h;
                half3 interference = 0.5h + 0.5h * cos(
                    6.28318h * (phase + half3(0.00h, 0.33h, 0.67h)));
                half3 diffuse = bloodRed
                    * lerp(0.26h, 1.0h, nDotL)
                    * mainLight.color;
                half3 halfVector = SafeNormalize(mainLight.direction + viewWS);
                half clearSpecular = pow(saturate(dot(normalWS, halfVector)), 96.0h)
                    * _ClearCoat;
                half backGlow = pow(saturate(dot(-normalWS, mainLight.direction)), 2.0h)
                    * _TransmissionApprox;
                half3 color = diffuse
                    + clearSpecular * mainLight.color
                    + interference * fresnel * _Iridescence
                    + bloodRed * backGlow;
                return half4(color, 1.0h);
            }
            ENDHLSL
        }
    }
    FallBack Off
}
