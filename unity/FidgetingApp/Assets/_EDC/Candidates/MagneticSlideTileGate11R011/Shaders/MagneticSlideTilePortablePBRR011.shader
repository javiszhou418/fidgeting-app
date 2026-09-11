Shader "FidgetingApp/MagneticSlideTile/PortablePBRR011"
{
    Properties
    {
        [MainTexture] _BaseMap("Base Map", 2D) = "white" {}
        [MainColor] _BaseColor("Base Color", Color) = (1,1,1,1)
        _RoughnessMap("Linear Roughness", 2D) = "white" {}
        [Normal] _NormalMap("Tangent Normal", 2D) = "bump" {}
        _SharedEnvironment("Shared HDR Environment", Cube) = "" {}
        _UseBaseMap("Use Base Map", Float) = 0
        _UseRoughnessMap("Use Roughness Map", Float) = 0
        _UseNormalMap("Use Normal Map", Float) = 0
        _Metallic("Metallic", Range(0,1)) = 0
        _Roughness("Roughness", Range(0.01,1)) = 0.5
        _NormalScale("Normal Scale", Range(0,2)) = 0.35
        _ClearCoat("Clear Coat", Range(0,1)) = 0
        _ClearCoatRoughness("Clear Coat Roughness", Range(0.01,1)) = 0.1
        _SpecularFactor("glTF Specular Factor", Range(0,1)) = 1
        _EnvironmentIntensity("Environment Intensity", Range(0,2)) = 0.85
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "Opaque"
            "RenderPipeline" = "UniversalPipeline"
            "Queue" = "Geometry"
        }
        Cull Off
        ZWrite On

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

            TEXTURE2D(_BaseMap);
            SAMPLER(sampler_BaseMap);
            TEXTURE2D(_RoughnessMap);
            SAMPLER(sampler_RoughnessMap);
            TEXTURE2D(_NormalMap);
            SAMPLER(sampler_NormalMap);
            TEXTURECUBE(_SharedEnvironment);
            SAMPLER(sampler_SharedEnvironment);

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                float4 _BaseColor;
                float _UseBaseMap;
                float _UseRoughnessMap;
                float _UseNormalMap;
                float _Metallic;
                float _Roughness;
                float _NormalScale;
                float _ClearCoat;
                float _ClearCoatRoughness;
                float _SpecularFactor;
                float _EnvironmentIntensity;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float4 tangentOS : TANGENT;
                float2 uv : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                float4 tangentWS : TEXCOORD2;
                float2 uv : TEXCOORD3;
                UNITY_VERTEX_INPUT_INSTANCE_ID
                UNITY_VERTEX_OUTPUT_STEREO
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, output);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(output);
                VertexPositionInputs positions = GetVertexPositionInputs(input.positionOS.xyz);
                VertexNormalInputs normals = GetVertexNormalInputs(input.normalOS, input.tangentOS);
                output.positionCS = positions.positionCS;
                output.positionWS = positions.positionWS;
                output.normalWS = normals.normalWS;
                output.tangentWS = float4(
                    normals.tangentWS,
                    input.tangentOS.w * GetOddNegativeScale());
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                return output;
            }

            float3 ApplyNeutralDisplay(float3 linearRgb)
            {
                linearRgb = max(linearRgb, 0.0);
                return linearRgb / (1.0 + 0.18 * linearRgb);
            }

            half4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);

                float3 baseColor = _BaseColor.rgb;
                if (_UseBaseMap > 0.5)
                    baseColor *= SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, input.uv).rgb;

                float roughness = _Roughness;
                if (_UseRoughnessMap > 0.5)
                    roughness = SAMPLE_TEXTURE2D(
                        _RoughnessMap, sampler_RoughnessMap, input.uv).r;
                roughness = clamp(roughness, 0.015, 1.0);

                float3 normalWS = normalize(input.normalWS);
                if (_UseNormalMap > 0.5)
                {
                    float3 tangentWS = normalize(input.tangentWS.xyz);
                    float3 bitangentWS = normalize(
                        cross(normalWS, tangentWS) * input.tangentWS.w);
                    float3 normalTS = UnpackNormalScale(
                        SAMPLE_TEXTURE2D(_NormalMap, sampler_NormalMap, input.uv),
                        _NormalScale);
                    normalWS = normalize(
                        tangentWS * normalTS.x
                        + bitangentWS * normalTS.y
                        + normalWS * normalTS.z);
                }

                float3 viewWS = normalize(GetWorldSpaceViewDir(input.positionWS));
                float ndotv = saturate(dot(normalWS, viewWS));
                float3 environmentReflection = reflect(-viewWS, normalWS);
                float3 environmentNormal = normalWS;
                float smoothness = 1.0 - roughness;
                float alpha = 1.0;
                BRDFData brdfData;
                InitializeBRDFData(
                    baseColor, _Metallic, 0.04.xxx * _SpecularFactor,
                    smoothness, alpha, brdfData);
                brdfData.specular = lerp(
                    0.04.xxx * _SpecularFactor, baseColor, _Metallic);
                brdfData.reflectivity = Max3(
                    brdfData.specular.r,
                    brdfData.specular.g,
                    brdfData.specular.b);
                brdfData.grazingTerm =
                    saturate(smoothness + brdfData.reflectivity);

                float mip = PerceptualRoughnessToMipmapLevel(roughness);
                float3 envSpec = SAMPLE_TEXTURECUBE_LOD(
                    _SharedEnvironment, sampler_SharedEnvironment,
                    environmentReflection, mip).rgb;
                // URP's single-scatter IBL undercounts Blender's metallic response.
                // The factor is fitted from the isolated linear silver control.
                envSpec *= lerp(1.0, 1.70, _Metallic * _Metallic);
                float3 envDiffuse = SAMPLE_TEXTURECUBE_LOD(
                    _SharedEnvironment, sampler_SharedEnvironment,
                    environmentNormal, 7.0).rgb;
                float fresnelTerm = Pow4(1.0 - ndotv);
                float3 color = EnvironmentBRDF(
                    brdfData, envDiffuse, envSpec, fresnelTerm);

                BRDFData coatBrdf;
                InitializeBRDFDataClearCoat(
                    _ClearCoat, 1.0 - _ClearCoatRoughness,
                    brdfData, coatBrdf);
                float coatMip = PerceptualRoughnessToMipmapLevel(
                    _ClearCoatRoughness);
                float3 coatEnv = SAMPLE_TEXTURECUBE_LOD(
                    _SharedEnvironment, sampler_SharedEnvironment,
                    environmentReflection, coatMip).rgb;
                float3 coat = EnvironmentBRDFClearCoat(
                    coatBrdf, _ClearCoat, coatEnv, fresnelTerm);
                float coatFresnel = 0.04 + 0.96 * fresnelTerm;
                color = color * (1.0 - coatFresnel * _ClearCoat) + coat;
                return half4(
                    ApplyNeutralDisplay(color * _EnvironmentIntensity), 1.0);
            }
            ENDHLSL
        }

        UsePass "Universal Render Pipeline/Lit/DepthOnly"
        UsePass "Universal Render Pipeline/Lit/ShadowCaster"
    }
}
