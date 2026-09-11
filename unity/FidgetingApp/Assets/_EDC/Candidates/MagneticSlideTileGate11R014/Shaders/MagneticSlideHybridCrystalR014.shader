Shader "FidgetingApp/MagneticSlideTile/HybridCrystalR014"
{
    Properties
    {
        _SharedEnvironment("Approved HDR Environment", Cube) = "" {}
        _CrystalTint("Crystal Tint", Color) = (0.995,0.998,1.0,1)
        _Ior("Crystal IOR", Range(1.1,2.0)) = 1.52
        _Roughness("Crystal Roughness", Range(0.005,0.2)) = 0.022
        _ThicknessMeters("Crystal Thickness Meters", Range(0,0.001)) = 0.00028
        _Transmission("Detail-Preserving Transmission", Range(0,1)) = 0.985
        _ReflectionStrength("Reflection Strength", Range(0,1)) = 0.68
        _RefractionPixels("Refraction Pixels", Range(0,2)) = 0.35
        _EnvironmentIntensity("Environment Intensity", Range(0,2)) = 0.84
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "Transparent"
            "RenderPipeline" = "UniversalPipeline"
            "Queue" = "Transparent+90"
        }
        Cull Off
        ZWrite Off
        Blend One OneMinusSrcAlpha

        Pass
        {
            Name "CrystalDepth"
            Tags { "LightMode" = "DepthOnly" }
            ZWrite On
            ColorMask 0

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex DepthVert
            #pragma fragment DepthFrag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct DepthAttributes
            {
                float4 positionOS : POSITION;
            };

            struct DepthVaryings
            {
                float4 positionCS : SV_POSITION;
            };

            DepthVaryings DepthVert(DepthAttributes input)
            {
                DepthVaryings output;
                output.positionCS =
                    TransformObjectToHClip(input.positionOS.xyz);
                return output;
            }

            half4 DepthFrag(DepthVaryings input) : SV_Target
            {
                return 0;
            }
            ENDHLSL
        }

        Pass
        {
            Name "ForwardCrystal"
            Tags { "LightMode" = "UniversalForward" }

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_instancing

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/ImageBasedLighting.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/BRDF.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareOpaqueTexture.hlsl"

            TEXTURECUBE(_SharedEnvironment);
            SAMPLER(sampler_SharedEnvironment);

            CBUFFER_START(UnityPerMaterial)
                float4 _CrystalTint;
                float _Ior;
                float _Roughness;
                float _ThicknessMeters;
                float _Transmission;
                float _ReflectionStrength;
                float _RefractionPixels;
                float _EnvironmentIntensity;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                float4 screenPosition : TEXCOORD2;
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
                output.screenPosition =
                    ComputeScreenPos(output.positionCS);
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
                float3 normal = normalize(input.normalWS);
                float3 view = normalize(
                    GetWorldSpaceViewDir(input.positionWS));
                float ndotv = saturate(dot(normal, view));
                float f0 = pow(
                    (_Ior - 1.0) / (_Ior + 1.0), 2.0);
                float fresnel =
                    f0 + (1.0 - f0) * pow(1.0 - ndotv, 5.0);
                float2 screenUv =
                    input.screenPosition.xy / input.screenPosition.w;
                float2 distortion = normal.xy
                    * (_RefractionPixels / _ScreenParams.xy)
                    * saturate(_ThicknessMeters / 0.00028);
                float3 refracted = SampleSceneColor(
                    screenUv + distortion);
                float3 reflected = SAMPLE_TEXTURECUBE_LOD(
                    _SharedEnvironment,
                    sampler_SharedEnvironment,
                    reflect(-view, normal),
                    PerceptualRoughnessToMipmapLevel(_Roughness)).rgb;
                reflected = NeutralDisplay(
                    reflected * _EnvironmentIntensity);
                float reflectionWeight = saturate(
                    fresnel * _ReflectionStrength * 0.24);
                float refractionWeight =
                    (1.0 - _Transmission) * 0.12;
                float alpha = saturate(
                    0.004 + refractionWeight
                    + reflectionWeight * 0.34);
                float3 premultiplied =
                    refracted * _CrystalTint.rgb * refractionWeight
                    + reflected * reflectionWeight * 0.48;
                return half4(premultiplied, alpha);
            }
            ENDHLSL
        }
    }
}
