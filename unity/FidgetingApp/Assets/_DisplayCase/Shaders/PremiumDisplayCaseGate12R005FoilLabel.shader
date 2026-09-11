// R005 label plate finish: graphite metal with a brushed anisotropic
// highlight, a view-dependent diffraction (holographic) band, an optional
// guilloche print, and a foil tint for the rarity emblem and frame lines.
// Lighting is a fixed virtual key, like the frosted shell, so the plate
// reads as metal in the shipping scene without a reflection probe.
Shader "FidgetingApp/Gate12R005FoilLabel"
{
    Properties
    {
        _MainTex("Alpha Mask", 2D) = "white" {}
        _PatternTex("Guilloche Print", 2D) = "gray" {}
        _BaseColor("Base Metal", Color) = (0.09, 0.10, 0.12, 1)
        _FoilColor("Foil Tint", Color) = (0.82, 0.84, 0.88, 1)
        _Metalness("Foil Coverage", Range(0, 1)) = 0.35
        _BrushStrength("Brush Highlight", Range(0, 2)) = 0.9
        _BrushSharpness("Brush Sharpness", Range(4, 400)) = 90
        _HoloStrength("Diffraction Strength", Range(0, 2)) = 0.7
        _HoloScale("Diffraction Density", Range(0.5, 24)) = 7
        _HoloBandWidth("Diffraction Band Width", Range(0.02, 1.5)) = 0.36
        _PatternStrength("Print Strength", Range(0, 1)) = 0.35
        _SheenPhase("Tilt Phase (R053 driver)", Float) = 0
        _AlphaClip("Alpha Clip", Float) = 0
        _Cutoff("Alpha Cutoff", Range(0, 1)) = 0.5
    }

    SubShader
    {
        Tags
        {
            "RenderType"="Opaque"
            "RenderPipeline"="UniversalPipeline"
        }
        Cull Back
        ZWrite On

        Pass
        {
            Name "Gate12R005FoilLabel"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.0

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            TEXTURE2D(_MainTex);
            SAMPLER(sampler_MainTex);
            TEXTURE2D(_PatternTex);
            SAMPLER(sampler_PatternTex);

            CBUFFER_START(UnityPerMaterial)
                float4 _MainTex_ST;
                float4 _PatternTex_ST;
                half4 _BaseColor;
                half4 _FoilColor;
                half _Metalness;
                half _BrushStrength;
                half _BrushSharpness;
                half _HoloStrength;
                half _HoloScale;
                half _HoloBandWidth;
                half _PatternStrength;
                half _SheenPhase;
                half _AlphaClip;
                half _Cutoff;
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
                float3 normalWS : TEXCOORD1;
                float3 tangentWS : TEXCOORD2;
                float2 uv : TEXCOORD3;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                VertexPositionInputs positions =
                    GetVertexPositionInputs(input.positionOS.xyz);
                output.positionCS = positions.positionCS;
                output.positionWS = positions.positionWS;
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                // Brush grain runs along the plate's long axis. The label
                // mesh carries no tangents, so object X is the grain.
                output.tangentWS = TransformObjectToWorldDir(float3(1, 0, 0));
                output.uv = input.uv;
                return output;
            }

            half3 Spectrum(half t)
            {
                return 0.5h + 0.5h * cos(6.28318h * (t + half3(0.0h, 0.33h, 0.67h)));
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half mask = SAMPLE_TEXTURE2D(
                    _MainTex,
                    sampler_MainTex,
                    TRANSFORM_TEX(input.uv, _MainTex)).a;
                if (_AlphaClip > 0.5h)
                {
                    clip(mask - _Cutoff);
                }

                half3 normalWS = normalize(input.normalWS);
                half3 tangentWS = normalize(
                    input.tangentWS - normalWS * dot(input.tangentWS, normalWS));
                half3 viewDirection = SafeNormalize(
                    GetWorldSpaceViewDir(input.positionWS));
                half3 key = normalize(half3(-0.34h, 0.72h, -0.60h));
                half3 fill = normalize(half3(0.55h, 0.25h, -0.75h));
                half3 halfKey = normalize(key + viewDirection);
                half3 halfFill = normalize(fill + viewDirection);

                // Kajiya-Kay: a streak perpendicular to the grain.
                half tangentDotKey = dot(tangentWS, halfKey);
                half tangentDotFill = dot(tangentWS, halfFill);
                half brush = pow(
                    sqrt(saturate(1.0h - tangentDotKey * tangentDotKey)),
                    _BrushSharpness)
                    + 0.35h * pow(
                        sqrt(saturate(1.0h - tangentDotFill * tangentDotFill)),
                        _BrushSharpness * 0.5h);
                brush *= _BrushStrength;

                half facing = saturate(dot(normalWS, viewDirection));
                half fresnel = pow(1.0h - facing, 3.0h);
                half diffuse = 0.30h
                    + 0.55h * saturate(dot(normalWS, key))
                    + 0.20h * saturate(dot(normalWS, fill));

                half pattern = SAMPLE_TEXTURE2D(
                    _PatternTex,
                    sampler_PatternTex,
                    TRANSFORM_TEX(input.uv, _PatternTex)).r;
                half print = 1.0h + (pattern - 0.5h) * _PatternStrength;

                // Diffraction grating: hue walks with view angle and
                // position; the band sits where the grazing angle lets a
                // hologram catch light, so it moves as the case turns.
                half viewShift = dot(viewDirection, tangentWS) * 0.85h
                    + dot(viewDirection, normalWS) * 0.35h;
                // _SheenPhase is written per frame by PremiumDisplayCaseLabelFoil
                // from device gravity, so the band walks when the phone tilts.
                half phase = input.uv.x * _HoloScale
                    + input.uv.y * _HoloScale * 0.35h
                    + viewShift * 2.2h
                    + _SheenPhase;
                half bandCenter = 0.5h + viewShift * 0.9h + sin(_SheenPhase * 3.14159h) * 0.3h;
                half bandDistance = (input.uv.x + input.uv.y * 0.55h) - bandCenter;
                half band = exp(-(bandDistance * bandDistance)
                    / (_HoloBandWidth * _HoloBandWidth));
                half3 holo = Spectrum(phase)
                    * band
                    * (0.35h + fresnel * 0.65h)
                    * _HoloStrength;

                half3 metal = _FoilColor.rgb;
                half3 albedo = lerp(_BaseColor.rgb, metal * 0.55h, _Metalness) * print;
                half3 color = albedo * diffuse
                    + metal * brush * (0.6h + 0.4h * _Metalness)
                    + metal * fresnel * 0.18h
                    + holo * lerp(half3(1, 1, 1), metal, _Metalness * 0.5h);
                color = min(color, 0.985h);
                return half4(color, mask);
            }
            ENDHLSL
        }
    }
}
