Shader "FidgetingApp/EDC/MagneticCrystalShippingR3"
{
    Properties
    {
        _MaskMap("Motif R / Border G / Combined B", 2D) = "black" {}
        _CrystalColor("Blood Red Substrate", Color) = (0.225, 0.010, 0.018, 1)
        _MotifColor("Motif Reflectance", Color) = (0.020, 0.017, 0.020, 1)
        _BorderColor("Border Reflectance", Color) = (0.026, 0.022, 0.025, 1)
        _Roughness("Substrate Roughness", Range(0.02, 1)) = 0.20
        _ClearCoatMask("Clearcoat", Range(0, 1)) = 0.92
        _ClearCoatRoughness("Clearcoat Roughness", Range(0.015, 1)) = 0.055
        _ReflectionStrength("Reflection Strength", Range(0, 2)) = 0.72
        _Iridescence("Restrained Thin Film", Range(0, 1)) = 0.16
        _DepthVariation("Internal Depth", Range(0, 0.5)) = 0.18
        _RefractionCue("Refraction Cue", Range(0, 0.5)) = 0.12
        _CrystalBrightness("Substrate Brightness", Range(0, 2)) = 0.76
        _MotifReflectance("Motif Environment Reflectance", Range(0, 1)) = 0.30
        _BorderReflectance("Border Environment Reflectance", Range(0, 1)) = 0.38
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" "Queue"="Geometry" "RenderPipeline"="UniversalPipeline" }

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BLENDING
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BOX_PROJECTION

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/GlobalIllumination.hlsl"

            TEXTURE2D(_MaskMap);
            SAMPLER(sampler_MaskMap);

            CBUFFER_START(UnityPerMaterial)
                float4 _MaskMap_ST;
                half4 _CrystalColor;
                half4 _MotifColor;
                half4 _BorderColor;
                half _Roughness;
                half _ClearCoatMask;
                half _ClearCoatRoughness;
                half _ReflectionStrength;
                half _Iridescence;
                half _DepthVariation;
                half _RefractionCue;
                half _CrystalBrightness;
                half _MotifReflectance;
                half _BorderReflectance;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                half3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                half3 normalWS : TEXCOORD1;
                float2 uv : TEXCOORD2;
                float4 shadowCoord : TEXCOORD3;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                VertexPositionInputs positionInputs = GetVertexPositionInputs(input.positionOS.xyz);
                output.positionCS = positionInputs.positionCS;
                output.positionWS = positionInputs.positionWS;
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                output.uv = TRANSFORM_TEX(input.uv, _MaskMap);
                output.shadowCoord = GetShadowCoord(positionInputs);
                return output;
            }

            half3 ThinFilmColor(half phase)
            {
                half3 offsets = half3(0.0h, 2.0944h, 4.1888h);
                return 0.5h.xxx + 0.5h * cos(phase + offsets);
            }

            half InternalPattern(float2 uv)
            {
                half broad = sin(uv.x * 17.0h + uv.y * 11.0h);
                half cross = sin(uv.x * 37.0h - uv.y * 29.0h + broad * 0.85h);
                half fine = sin((uv.x + uv.y) * 71.0h + cross * 0.55h);
                return broad * 0.48h + cross * 0.34h + fine * 0.18h;
            }

            half3 NeutralLayeredReflection(half3 direction)
            {
                half3 broadKey = normalize(half3(-0.70h, 0.30h, -0.64h));
                half3 topStrip = normalize(half3(0.12h, 0.98h, -0.16h));
                half3 sideFill = normalize(half3(0.78h, 0.04h, 0.62h));
                half key = pow(saturate(dot(direction, broadKey)), 4.0h);
                half strip = pow(saturate(dot(direction, topStrip)), 18.0h);
                half fill = pow(saturate(dot(direction, sideFill)), 7.0h);
                half horizon = pow(1.0h - abs(direction.y), 2.2h);
                half value = 0.19h
                    + 0.42h * key
                    + 0.46h * strip
                    + 0.22h * fill
                    + 0.10h * horizon;
                return value * half3(1.006h, 1.0h, 0.992h);
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half3 normalWS = normalize(input.normalWS);
                half3 viewDirWS = SafeNormalize(GetWorldSpaceViewDir(input.positionWS));
                Light mainLight = GetMainLight(input.shadowCoord);
                half3 lightDirWS = normalize(mainLight.direction);
                half3 halfDirWS = SafeNormalize(viewDirWS + lightDirWS);

                half3 masks = SAMPLE_TEXTURE2D(_MaskMap, sampler_MaskMap, input.uv).rgb;
                half motifMask = smoothstep(0.16h, 0.72h, masks.r);
                half borderMask = smoothstep(0.16h, 0.72h, masks.g);
                motifMask *= 1.0h - borderMask;

                half ndl = saturate(dot(normalWS, lightDirWS));
                half ndh = saturate(dot(normalWS, halfDirWS));
                half ndv = saturate(dot(normalWS, viewDirWS));
                half fresnel = Pow4(1.0h - ndv);
                half internalPattern = InternalPattern(input.uv);
                half depthModulation = 1.0h + internalPattern * _DepthVariation;

                half3 reflectionVector = reflect(-viewDirWS, normalWS);
                half2 screenUv = GetNormalizedScreenSpaceUV(input.positionCS);
                half3 coatEnvironment = GlossyEnvironmentReflection(
                    reflectionVector,
                    input.positionWS,
                    _ClearCoatRoughness,
                    1.0h,
                    screenUv
                );
                half3 substrateEnvironment = GlossyEnvironmentReflection(
                    reflectionVector,
                    input.positionWS,
                    _Roughness,
                    1.0h,
                    screenUv
                );
                half3 refractedVector = refract(-viewDirWS, normalWS, 0.676h);
                half3 refractedEnvironment = GlossyEnvironmentReflection(
                    refractedVector,
                    input.positionWS,
                    saturate(_Roughness + 0.16h),
                    1.0h,
                    screenUv
                );
                half3 layeredReflection = NeutralLayeredReflection(reflectionVector);
                coatEnvironment = max(coatEnvironment, layeredReflection);
                substrateEnvironment = max(substrateEnvironment, layeredReflection);
                refractedEnvironment = max(
                    refractedEnvironment,
                    NeutralLayeredReflection(refractedVector));

                half3 substrate = _CrystalColor.rgb * depthModulation;
                substrate *= _CrystalBrightness;
                substrate *= lerp(1.0h, 0.64h, fresnel);
                half3 litSubstrate = substrate * (
                    0.52h.xxx
                    + mainLight.color * (0.12h + ndl * 0.46h)
                        * mainLight.shadowAttenuation
                );
                litSubstrate += refractedEnvironment * substrate * _RefractionCue;

                half coatPower = lerp(384.0h, 18.0h, _ClearCoatRoughness);
                half coatSpecular = pow(ndh, coatPower);
                half3 directCoat =
                    mainLight.color * coatSpecular * mainLight.shadowAttenuation;
                half thinFilmPhase = 10.0h * (1.0h - ndv) + internalPattern * 0.42h;
                half3 thinFilm = ThinFilmColor(thinFilmPhase);
                half iridescentWeight = _Iridescence * (0.18h + fresnel * 0.82h);
                half3 coatTint = lerp(1.0h.xxx, thinFilm, iridescentWeight);
                half3 coat = (
                    coatEnvironment * (0.08h + fresnel * 0.92h) * _ReflectionStrength
                    + directCoat * (0.20h + fresnel * 0.80h)
                ) * coatTint * _ClearCoatMask;

                half3 crystal = litSubstrate + coat;
                crystal += substrateEnvironment
                    * thinFilm
                    * iridescentWeight
                    * 0.22h;

                half3 motifReflection =
                    substrateEnvironment * _MotifReflectance
                    + directCoat * 0.12h;
                half3 motif = _MotifColor.rgb * (
                    0.34h + ndl * 0.38h
                ) + motifReflection;

                half3 borderReflection =
                    substrateEnvironment * _BorderReflectance
                    + directCoat * 0.16h;
                half3 border = _BorderColor.rgb * (
                    0.30h + ndl * 0.34h
                ) + borderReflection;

                half3 color = lerp(crystal, motif, motifMask);
                color = lerp(color, border, borderMask);
                return half4(max(color, 0.0h.xxx), 1.0h);
            }
            ENDHLSL
        }

        UsePass "Universal Render Pipeline/Lit/ShadowCaster"
        UsePass "Universal Render Pipeline/Lit/DepthOnly"
    }
}
