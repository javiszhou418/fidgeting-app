Shader "FidgetingApp/MagneticSlideTile/NeutralCrystalR005"
{
    Properties
    {
        _BaseMap("Blood-red Base", 2D) = "white" {}
        _EnvironmentCube("Environment Cube", Cube) = "black" {}
        _MaskMap("Metal AO Detail Smoothness", 2D) = "white" {}
        [Normal] _BumpMap("Crystal Normal", 2D) = "bump" {}
        _ArtworkMask("Artwork Mask", 2D) = "black" {}
        _PerimeterMask("Perimeter Mask", 2D) = "black" {}
        _DeepBloodRed("Deep Blood Red", Color) = (0.18, 0.003, 0.008, 1)
        _BlackColor("Motif and Perimeter", Color) = (0.004, 0.0015, 0.0018, 1)
        _Smoothness("Crystal Smoothness", Range(0, 1)) = 0.50
        _BlackSmoothness("Black Smoothness", Range(0, 1)) = 0.82
        _NormalScale("Normal Strength", Range(0, 2)) = 0.75
        _ReflectionStrength("Reflection Strength", Range(0, 2)) = 0.52
        _DiffuseStrength("Diffuse Strength", Range(0, 2)) = 1.50
        _CoatStrength("Clear Coat", Range(0, 1)) = 0.48
        _CrystalDepth("Crystal Depth Cue", Range(0, 1)) = 0.26
        _ResponseBalance("Cross-engine Response Balance", Color) = (1, 1.07, 1.08, 1)
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
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BLENDING
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BOX_PROJECTION

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Packing.hlsl"

            TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
            TEXTURECUBE(_EnvironmentCube); SAMPLER(sampler_EnvironmentCube);
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
                half _DiffuseStrength;
                half _CoatStrength;
                half _CrystalDepth;
                half4 _ResponseBalance;
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
                half artwork = SAMPLE_TEXTURE2D(
                    _ArtworkMask, sampler_ArtworkMask, input.uv).r;
                half perimeter = SAMPLE_TEXTURE2D(
                    _PerimeterMask, sampler_PerimeterMask, input.uv).r;
                half3 tangentNormal = UnpackNormalScale(
                    SAMPLE_TEXTURE2D(_BumpMap, sampler_BumpMap, input.uv), _NormalScale);
                float3 normalWS = normalize(
                    input.tangentWS * tangentNormal.x
                    + input.bitangentWS * tangentNormal.y
                    + input.normalWS * tangentNormal.z);
                half derivedArtwork = 1.0h - smoothstep(
                    0.035h, 0.12h, max(baseSample.r, max(baseSample.g, baseSample.b)));
                half sideMask = 1.0h - smoothstep(0.42h, 0.72h, abs(normalWS.y));
                half blackMask = saturate(max(max(artwork, perimeter), max(derivedArtwork, sideMask)));
                float3 viewWS = SafeNormalize(GetWorldSpaceViewDir(input.positionWS));
                float3 reflectionWS = reflect(-viewWS, normalWS);
                float nDotV = saturate(dot(normalWS, viewWS));
                half detail = maskSample.b;
                half ao = lerp(0.54h, 1.0h, maskSample.g);
                half3 bloodRed = max(
                    baseSample.rgb,
                    _DeepBloodRed.rgb * (0.9h + detail * 0.7h));
                bloodRed *= lerp(0.84h, 1.18h, detail);
                half3 baseColor = lerp(bloodRed, _BlackColor.rgb, blackMask);
                half smoothness = lerp(_Smoothness, _BlackSmoothness, blackMask);
                half roughness = saturate(1.0h - smoothness);
                half3 reflected = SAMPLE_TEXTURECUBE_LOD(
                    _EnvironmentCube, sampler_EnvironmentCube,
                    reflectionWS, roughness * 6.0h).rgb;
                half3 coatReflected = SAMPLE_TEXTURECUBE_LOD(
                    _EnvironmentCube, sampler_EnvironmentCube,
                    reflectionWS, 0.21h).rgb;
                half3 irradiance = SAMPLE_TEXTURECUBE_LOD(
                    _EnvironmentCube, sampler_EnvironmentCube,
                    normalWS, 6.0h).rgb;
                half3 f0 = lerp(
                    0.04258h.xxx, half3(0.12h, 0.08h, 0.09h), blackMask * 0.35h);
                half3 fresnel = f0 + (1.0h - f0) * pow(1.0 - nDotV, 5.0);
                half depthCue = lerp(
                    0.88h, 1.12h, saturate(detail * 0.7h + (1.0h - nDotV) * 0.3h));
                half3 color = baseColor
                    * irradiance
                    * _DiffuseStrength
                    * ao
                    * lerp(1.0h, depthCue, _CrystalDepth);
                color += reflected * fresnel * _ReflectionStrength;
                half coatFresnel = 0.04h + 0.96h * pow(1.0 - nDotV, 5.0);
                color += coatReflected * coatFresnel * _CoatStrength;
                color *= _ResponseBalance.rgb;
                return half4(max(color, 0.0h), 1.0h);
            }
            ENDHLSL
        }
    }
}
