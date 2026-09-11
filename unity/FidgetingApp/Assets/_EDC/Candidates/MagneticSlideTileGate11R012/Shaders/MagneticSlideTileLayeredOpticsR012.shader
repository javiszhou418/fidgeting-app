Shader "FidgetingApp/MagneticSlideTile/LayeredOpticsR012"
{
    Properties
    {
        [MainTexture] _BaseMap("Source Base", 2D) = "white" {}
        _RoughnessMap("Source Roughness", 2D) = "white" {}
        [Normal] _NormalMap("Source Normal", 2D) = "bump" {}
        _MotifMask("Independent Motif Mask", 2D) = "black" {}
        _PerimeterMask("Top Perimeter Mask", 2D) = "black" {}
        _SharedEnvironment("Approved HDR Environment", Cube) = "" {}
        _SubstrateTint("Blood Red Substrate Tint", Color) = (1.0,0.62,0.70,1)
        _MotifColor("Black Motif Reflectance", Color) = (0.018,0.020,0.024,1)
        _SubstrateRoughnessMin("Substrate Roughness Min", Range(0.01,0.3)) = 0.022
        _SubstrateRoughnessMax("Substrate Roughness Max", Range(0.02,0.4)) = 0.11
        _MotifRoughness("Motif Roughness", Range(0.02,0.6)) = 0.18
        _MotifMetallic("Motif Metallic", Range(0,1)) = 0.24
        _NormalScale("Micro Normal Scale", Range(0,1)) = 0.32
        _MicaScale("Mica Scale", Range(4,64)) = 28
        _MicroflakeScale("Microflake Scale", Range(24,160)) = 85
        _MicroflakeStrength("Microflake Strength", Range(0,0.35)) = 0.16
        _IridescenceStrength("Ruby Shift Strength", Range(0,0.3)) = 0.12
        _MotifRelief("Motif Relief", Range(0,0.004)) = 0.0012
        _CoatIor("Clear Cap IOR", Range(1.1,2)) = 1.52
        _CoatRoughness("Clear Cap Roughness", Range(0.01,0.2)) = 0.035
        _CoatStrength("Clear Cap Strength", Range(0,1)) = 0.78
        _LayerDepth("Layer Depth Cue", Range(0,0.004)) = 0.0016
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
            TEXTURE2D(_MotifMask);
            SAMPLER(sampler_MotifMask);
            TEXTURE2D(_PerimeterMask);
            SAMPLER(sampler_PerimeterMask);
            TEXTURECUBE(_SharedEnvironment);
            SAMPLER(sampler_SharedEnvironment);

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                float4 _SubstrateTint;
                float4 _MotifColor;
                float _SubstrateRoughnessMin;
                float _SubstrateRoughnessMax;
                float _MotifRoughness;
                float _MotifMetallic;
                float _NormalScale;
                float _MicaScale;
                float _MicroflakeScale;
                float _MicroflakeStrength;
                float _IridescenceStrength;
                float _MotifRelief;
                float _CoatIor;
                float _CoatRoughness;
                float _CoatStrength;
                float _LayerDepth;
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

            float Hash21(float2 value)
            {
                value = frac(value * float2(123.34, 456.21));
                value += dot(value, value + 45.32);
                return frac(value.x * value.y);
            }

            float3 FresnelSchlick(float cosine, float3 f0)
            {
                return f0 + (1.0 - f0) * pow(1.0 - cosine, 5.0);
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
#if defined(LAYERED_OPTICS_DIAGNOSTIC_RED)
                return half4(0.2, 0.0, 0.0, 1.0);
#else

                float3 geometricNormal = normalize(input.normalWS);
                float3 tangent = normalize(input.tangentWS.xyz);
                float3 bitangent = normalize(
                    cross(geometricNormal, tangent) * input.tangentWS.w);
                float3 view = normalize(GetWorldSpaceViewDir(input.positionWS));
                float3 viewTs = float3(
                    dot(view, tangent), dot(view, bitangent), dot(view, geometricNormal));

                float2 reliefUv = input.uv
                    - viewTs.xy * (_LayerDepth / max(abs(viewTs.z), 0.28));
                float authoredMask = SAMPLE_TEXTURE2D(
                    _MotifMask, sampler_MotifMask, reliefUv).r;
                float perimeterMask = SAMPLE_TEXTURE2D(
                    _PerimeterMask, sampler_PerimeterMask, reliefUv).r;

                float3 source = SAMPLE_TEXTURE2D(
                    _BaseMap, sampler_BaseMap, reliefUv).rgb;
                float sourceMotif = 1.0 - smoothstep(0.008, 0.055, source.r);
                float motif = max(sourceMotif, perimeterMask);
                motif = smoothstep(0.42, 0.58, motif);
                float reliefMask = max(1.0 - authoredMask, perimeterMask);
                float sourceRoughness = SAMPLE_TEXTURE2D(
                    _RoughnessMap, sampler_RoughnessMap, reliefUv).r;
                float3 normalTs = UnpackNormalScale(
                    SAMPLE_TEXTURE2D(_NormalMap, sampler_NormalMap, reliefUv),
                    _NormalScale);

                float mica = Hash21(floor(reliefUv * _MicaScale));
                float flake = Hash21(floor(reliefUv * _MicroflakeScale) + 19.7);
                float flakeAa = 0.04;
                float sparkle = smoothstep(
                    0.78 - flakeAa, 0.78 + flakeAa, flake);
                float variation = lerp(0.84, 1.15, mica)
                    + sparkle * _MicroflakeStrength;

                float3 normal = normalize(
                    tangent * normalTs.x
                    + bitangent * normalTs.y
                    + geometricNormal * normalTs.z);
                float ndotv = saturate(dot(normal, view));
                float grazing = pow(1.0 - ndotv, 5.0);

                float3 rubyShift = lerp(
                    float3(1.0, 0.97, 0.94),
                    lerp(float3(0.88, 0.97, 1.06), float3(0.92, 1.04, 0.92), mica),
                    grazing * _IridescenceStrength);
                float3 substrate = saturate(
                    source * _SubstrateTint.rgb
                    * variation * rubyShift * 1.65);
                float3 surfaceColor = lerp(substrate, _MotifColor.rgb, motif);

                float substrateRoughness = lerp(
                    _SubstrateRoughnessMin,
                    _SubstrateRoughnessMax,
                    saturate(sourceRoughness * 0.82 + mica * 0.18));
                float roughness = lerp(
                    substrateRoughness,
                    _MotifRoughness,
                    max(motif, reliefMask * _MotifRelief * 40.0));
                float metallic = motif * _MotifMetallic;

                float3 reflectionDirection = reflect(-view, normal);
                float reflectionMip = PerceptualRoughnessToMipmapLevel(roughness);
                float3 environmentSpecular = SAMPLE_TEXTURECUBE_LOD(
                    _SharedEnvironment, sampler_SharedEnvironment,
                    reflectionDirection, reflectionMip).rgb;
                float3 environmentDiffuse = SAMPLE_TEXTURECUBE_LOD(
                    _SharedEnvironment, sampler_SharedEnvironment,
                    normal, 7.0).rgb;
                environmentSpecular = NeutralDisplay(environmentSpecular);
                environmentDiffuse = NeutralDisplay(environmentDiffuse);

                float3 substrateF0 = lerp(0.0426.xxx, surfaceColor, metallic);
                float3 substrateFresnel = FresnelSchlick(ndotv, substrateF0);
                float3 diffuse = surfaceColor
                    * (0.92 + environmentDiffuse * 0.10)
                    * (1.0 - metallic);
                float3 substrateSpecular = environmentSpecular
                    * substrateFresnel * 0.22
                    * lerp(0.72, 1.08, sparkle * (1.0 - motif));

                float coatF0Scalar = pow((_CoatIor - 1.0) / (_CoatIor + 1.0), 2.0);
                float coatFresnel = coatF0Scalar
                    + (1.0 - coatF0Scalar)
                    * pow(1.0 - saturate(dot(geometricNormal, view)), 5.0);
                float3 coatReflection = SAMPLE_TEXTURECUBE_LOD(
                    _SharedEnvironment, sampler_SharedEnvironment,
                    reflect(-view, geometricNormal),
                    PerceptualRoughnessToMipmapLevel(_CoatRoughness)).rgb;
                coatReflection = NeutralDisplay(coatReflection) * 1.25;
                float3 refracted = normalize(
                    reflect(-view, geometricNormal)
                    + tangent * viewTs.x * _LayerDepth * 18.0
                    + bitangent * viewTs.y * _LayerDepth * 18.0);
                float3 depthColor = SAMPLE_TEXTURECUBE_LOD(
                    _SharedEnvironment, sampler_SharedEnvironment,
                    refracted, 3.0).rgb * substrate * 0.10 * (1.0 - motif);

                float coatWeight = coatFresnel * _CoatStrength * 0.34;
                float3 layered = (diffuse + substrateSpecular + depthColor)
                    * (1.0 - coatWeight)
                    + coatReflection * coatWeight;
                return half4(
                    NeutralDisplay(layered * _EnvironmentIntensity), 1.0);
#endif
            }
            ENDHLSL
        }

        UsePass "Universal Render Pipeline/Lit/DepthOnly"
        UsePass "Universal Render Pipeline/Lit/ShadowCaster"
    }
}
