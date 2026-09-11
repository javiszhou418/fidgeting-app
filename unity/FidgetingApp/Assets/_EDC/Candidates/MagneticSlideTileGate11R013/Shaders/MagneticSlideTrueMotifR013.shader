Shader "FidgetingApp/MagneticSlideTile/TrueMotifR013"
{
    Properties
    {
        _MotifMask("Independent Motif Mask", 2D) = "white" {}
        _PerimeterMask("Top Perimeter Mask", 2D) = "black" {}
        _SharedEnvironment("Approved HDR Environment", Cube) = "" {}
        _MotifColor("Black Motif", Color) = (0.010,0.012,0.016,1)
        _Roughness("Motif Roughness", Range(0.02,0.6)) = 0.16
        _Metallic("Motif Metallic", Range(0,1)) = 0.18
        _EnvironmentIntensity("Environment Intensity", Range(0,2)) = 0.78
        _Cutoff("Mask Cutoff", Range(0,1)) = 0.50
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "TransparentCutout"
            "RenderPipeline" = "UniversalPipeline"
            "Queue" = "AlphaTest+30"
        }
        Cull Back
        ZWrite On
        AlphaToMask On

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_instancing

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/ImageBasedLighting.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/BRDF.hlsl"

            TEXTURE2D(_MotifMask);
            SAMPLER(sampler_MotifMask);
            TEXTURE2D(_PerimeterMask);
            SAMPLER(sampler_PerimeterMask);
            TEXTURECUBE(_SharedEnvironment);
            SAMPLER(sampler_SharedEnvironment);

            CBUFFER_START(UnityPerMaterial)
                float4 _MotifMask_ST;
                float4 _MotifColor;
                float _Roughness;
                float _Metallic;
                float _EnvironmentIntensity;
                float _Cutoff;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                float2 uv : TEXCOORD2;
                UNITY_VERTEX_INPUT_INSTANCE_ID
                UNITY_VERTEX_OUTPUT_STEREO
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, output);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(output);
                VertexPositionInputs positions =
                    GetVertexPositionInputs(input.positionOS.xyz);
                output.positionCS = positions.positionCS;
                output.positionWS = positions.positionWS;
                output.normalWS =
                    TransformObjectToWorldNormal(input.normalOS);
                output.uv = TRANSFORM_TEX(input.uv, _MotifMask);
                return output;
            }

            float3 NeutralDisplay(float3 linearRgb)
            {
                linearRgb = max(linearRgb, 0.0);
                return linearRgb / (1.0 + 0.18 * linearRgb);
            }

            half4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);
                float authored = SAMPLE_TEXTURE2D(
                    _MotifMask, sampler_MotifMask, input.uv).r;
                float perimeter = SAMPLE_TEXTURE2D(
                    _PerimeterMask, sampler_PerimeterMask, input.uv).r;
                float motif = max(authored, perimeter);
                clip(motif - _Cutoff);

                float3 normal = normalize(input.normalWS);
                float3 view = normalize(GetWorldSpaceViewDir(input.positionWS));
                float ndotv = saturate(dot(normal, view));
                float3 reflected = SAMPLE_TEXTURECUBE_LOD(
                    _SharedEnvironment,
                    sampler_SharedEnvironment,
                    reflect(-view, normal),
                    PerceptualRoughnessToMipmapLevel(_Roughness)).rgb;
                float3 f0 = lerp(0.0426.xxx, _MotifColor.rgb, _Metallic);
                float3 fresnel =
                    f0 + (1.0 - f0) * pow(1.0 - ndotv, 5.0);
                float3 result = _MotifColor.rgb * (1.0 - _Metallic)
                    + NeutralDisplay(reflected) * fresnel * 0.58;
                return half4(
                    NeutralDisplay(result * _EnvironmentIntensity), 1.0);
            }
            ENDHLSL
        }

        UsePass "Universal Render Pipeline/Lit/DepthOnly"
        UsePass "Universal Render Pipeline/Lit/ShadowCaster"
    }
}
