Shader "FidgetingApp/MagneticSlideTile/HybridSubstrateR014"
{
    Properties
    {
        [MainTexture] _BaseMap("Rev12 Source Base", 2D) = "white" {}
        _RoughnessMap("Rev12 Source Roughness", 2D) = "white" {}
        [Normal] _NormalMap("Rev12 Source Normal", 2D) = "bump" {}
        _SharedEnvironment("Approved HDR Environment", Cube) = "" {}
        _SubstrateTint("Rev12 Substrate Tint", Color) = (1.0,0.62,0.70,1)
        _RoughnessMin("Rev12 Roughness Min", Range(0.01,0.3)) = 0.022
        _RoughnessMax("Rev12 Roughness Max", Range(0.02,0.4)) = 0.11
        _NormalScale("Rev12 Normal Scale", Range(0,1)) = 0.32
        _MicaScale("Rev12 Mica Scale", Range(4,64)) = 28
        _MicroflakeScale("Rev12 Microflake Scale", Range(24,160)) = 85
        _MicroflakeStrength("Rev12 Microflake Strength", Range(0,0.35)) = 0.16
        _IridescenceStrength("Rev12 Ruby Shift", Range(0,0.3)) = 0.12
        _EnvironmentIntensity("Rev12 Environment", Range(0,2)) = 0.85
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "Opaque"
            "RenderPipeline" = "UniversalPipeline"
            "Queue" = "Geometry+20"
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
                float4 _SubstrateTint;
                float _RoughnessMin;
                float _RoughnessMax;
                float _NormalScale;
                float _MicaScale;
                float _MicroflakeScale;
                float _MicroflakeStrength;
                float _IridescenceStrength;
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
                VertexPositionInputs positions =
                    GetVertexPositionInputs(input.positionOS.xyz);
                VertexNormalInputs normals =
                    GetVertexNormalInputs(input.normalOS, input.tangentOS);
                output.positionCS = positions.positionCS;
                output.positionWS = positions.positionWS;
                output.normalWS = normals.normalWS;
                output.tangentWS = float4(
                    normals.tangentWS,
                    input.tangentOS.w * GetOddNegativeScale());
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                return output;
            }

            float Hash21(float2 value)
            {
                value = frac(value * float2(123.34, 456.21));
                value += dot(value, value + 45.32);
                return frac(value.x * value.y);
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

                float3 geometricNormal = normalize(input.normalWS);
                float3 tangent = normalize(input.tangentWS.xyz);
                float3 bitangent = normalize(
                    cross(geometricNormal, tangent) * input.tangentWS.w);
                float3 normalTs = UnpackNormalScale(
                    SAMPLE_TEXTURE2D(_NormalMap, sampler_NormalMap, input.uv),
                    _NormalScale);
                float3 normal = normalize(
                    tangent * normalTs.x
                    + bitangent * normalTs.y
                    + geometricNormal * normalTs.z);
                float3 view = normalize(
                    GetWorldSpaceViewDir(input.positionWS));
                float ndotv = saturate(dot(normal, view));
                float mica = Hash21(floor(input.uv * _MicaScale));
                float flake = Hash21(
                    floor(input.uv * _MicroflakeScale) + 19.7);
                float sparkle = smoothstep(0.74, 0.82, flake);
                float variation = lerp(0.84, 1.15, mica)
                    + sparkle * _MicroflakeStrength;
                float3 source = SAMPLE_TEXTURE2D(
                    _BaseMap, sampler_BaseMap, input.uv).rgb;
                float grazing = pow(1.0 - ndotv, 5.0);
                float3 rubyShift = lerp(
                    float3(1.0, 0.97, 0.94),
                    lerp(
                        float3(0.88, 0.97, 1.06),
                        float3(0.92, 1.04, 0.92),
                        mica),
                    grazing * _IridescenceStrength);
                float3 substrate = saturate(
                    source * _SubstrateTint.rgb
                    * variation * rubyShift * 1.65);
                float sourceRoughness = SAMPLE_TEXTURE2D(
                    _RoughnessMap, sampler_RoughnessMap, input.uv).r;
                float roughness = lerp(
                    _RoughnessMin,
                    _RoughnessMax,
                    saturate(sourceRoughness * 0.82 + mica * 0.18));
                float3 specular = SAMPLE_TEXTURECUBE_LOD(
                    _SharedEnvironment,
                    sampler_SharedEnvironment,
                    reflect(-view, normal),
                    PerceptualRoughnessToMipmapLevel(roughness)).rgb;
                float3 diffuse = SAMPLE_TEXTURECUBE_LOD(
                    _SharedEnvironment,
                    sampler_SharedEnvironment,
                    normal,
                    7.0).rgb;
                specular = NeutralDisplay(specular);
                diffuse = NeutralDisplay(diffuse);
                float fresnel =
                    0.0426 + 0.9574 * pow(1.0 - ndotv, 5.0);
                float3 result = substrate
                    * (0.92 + diffuse * 0.10)
                    + specular * fresnel * 0.22
                    * lerp(0.72, 1.08, sparkle);
                return half4(
                    NeutralDisplay(result * _EnvironmentIntensity), 1.0);
            }
            ENDHLSL
        }

        UsePass "Universal Render Pipeline/Lit/DepthOnly"
        UsePass "Universal Render Pipeline/Lit/ShadowCaster"
    }
}
