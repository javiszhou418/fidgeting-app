Shader "FidgetingApp/MagneticSlideTile/PortableCrystalR003"
{
    Properties
    {
        _BaseMap("Blood-red Base", 2D) = "white" {}
        _MaskMap("Metal AO Detail Smoothness", 2D) = "white" {}
        [Normal] _BumpMap("Crystal Normal", 2D) = "bump" {}
        _ArtworkMask("Artwork Mask", 2D) = "black" {}
        _PerimeterMask("Perimeter Mask", 2D) = "black" {}
        _DeepBloodRed("Deep Blood Red", Color) = (0.18, 0.003, 0.008, 1)
        _BlackColor("Motif and Perimeter", Color) = (0.004, 0.0015, 0.0018, 1)
        _Smoothness("Crystal Smoothness", Range(0, 1)) = 0.94
        _BlackSmoothness("Black Smoothness", Range(0, 1)) = 0.84
        _NormalScale("Normal Strength", Range(0, 2)) = 0.75
        _ReflectionStrength("Reflection Strength", Range(0, 2)) = 1
        _CoatStrength("Clear Coat", Range(0, 1)) = 0.30
        _CrystalDepth("Crystal Depth Cue", Range(0, 1)) = 0.26
    }

    SubShader
    {
        Tags { "RenderPipeline" = "UniversalPipeline" "RenderType" = "Opaque" "Queue" = "Geometry" }
        Pass
        {
            Name "UniversalForward"
            Tags { "LightMode" = "UniversalForward" }
            ZWrite On
            ZTest LEqual
            Cull Off

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.0
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BLENDING
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BOX_PROJECTION

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Packing.hlsl"

            TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
            TEXTURE2D(_MaskMap); SAMPLER(sampler_MaskMap);
            TEXTURE2D(_BumpMap); SAMPLER(sampler_BumpMap);
            TEXTURE2D(_ArtworkMask); SAMPLER(sampler_ArtworkMask);
            TEXTURE2D(_PerimeterMask); SAMPLER(sampler_PerimeterMask);

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                half4 _DeepBloodRed;
                half4 _BlackColor;
                half _Smoothness;
                half _BlackSmoothness;
                half _NormalScale;
                half _ReflectionStrength;
                half _CoatStrength;
                half _CrystalDepth;
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
                float2 uv : TEXCOORD4;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                VertexPositionInputs positions = GetVertexPositionInputs(input.positionOS.xyz);
                output.positionCS = positions.positionCS;
                output.positionWS = positions.positionWS;
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                output.tangentWS = TransformObjectToWorldDir(input.tangentOS.xyz);
                half tangentSign = input.tangentOS.w * GetOddNegativeScale();
                output.bitangentWS = cross(output.normalWS, output.tangentWS) * tangentSign;
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half4 baseSample = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, input.uv);
                half4 maskSample = SAMPLE_TEXTURE2D(_MaskMap, sampler_MaskMap, input.uv);
                half artwork = SAMPLE_TEXTURE2D(_ArtworkMask, sampler_ArtworkMask, input.uv).r;
                half perimeter = SAMPLE_TEXTURE2D(_PerimeterMask, sampler_PerimeterMask, input.uv).r;
                half blackMask = saturate(max(artwork, perimeter));
                half3 tangentNormal = UnpackNormalScale(
                    SAMPLE_TEXTURE2D(_BumpMap, sampler_BumpMap, input.uv), _NormalScale);
                float3 normalWS = normalize(
                    input.tangentWS * tangentNormal.x
                    + input.bitangentWS * tangentNormal.y
                    + input.normalWS * tangentNormal.z);
                float3 viewWS = SafeNormalize(GetWorldSpaceViewDir(input.positionWS));
                float3 reflectionWS = reflect(-viewWS, normalWS);
                float nDotV = saturate(dot(normalWS, viewWS));
                half smoothness = lerp(max(maskSample.a, _Smoothness), _BlackSmoothness, blackMask);
                half detail = maskSample.b;
                half ao = lerp(0.42h, 1.0h, maskSample.g);
                half3 crystal = max(
                    baseSample.rgb,
                    _DeepBloodRed.rgb * (1.0h + detail * 0.65h));
                crystal *= lerp(0.88h, 1.20h, detail);
                half3 baseColor = lerp(crystal, _BlackColor.rgb, blackMask);
                half3 f0 = lerp(0.04258h.xxx, half3(0.14h, 0.10h, 0.11h), blackMask * 0.35h);
                half3 fresnel = f0 + (1.0h - f0) * pow(1.0 - nDotV, 5.0);
                half3 environment = GlossyEnvironmentReflection(
                    reflectionWS, saturate(1.0h - smoothness), 1.0h);
                Light mainLight = GetMainLight(TransformWorldToShadowCoord(input.positionWS));
                float nDotL = saturate(dot(normalWS, mainLight.direction));
                float3 halfVector = SafeNormalize(mainLight.direction + viewWS);
                float nDotH = saturate(dot(normalWS, halfVector));
                half directSpecular = pow(nDotH, lerp(18.0, 180.0, smoothness))
                    * nDotL * mainLight.shadowAttenuation;
                half3 ambient = SampleSH(normalWS);
                half depthCue = lerp(
                    0.86h, 1.10h, saturate(detail * 0.7h + (1.0h - nDotV) * 0.3h));
                half3 color = baseColor
                    * (0.18h + ambient)
                    * ao
                    * lerp(1.0h, depthCue, _CrystalDepth)
                    * lerp(0.55h, 1.0h, nDotL);
                color += environment * fresnel * _ReflectionStrength;
                color += mainLight.color
                    * fresnel
                    * directSpecular
                    * (0.18h + _CoatStrength * 0.42h);
                return half4(max(color, 0.0h), 1.0h);
            }
            ENDHLSL
        }
        UsePass "Universal Render Pipeline/Lit/ShadowCaster"
        UsePass "Universal Render Pipeline/Lit/DepthOnly"
    }
}
