// R008 backing: silver holographic glitter stock. Two layers of sub-mm
// flakes with randomised normals; a flake lights up only when its normal
// mirrors the eye to a light, so the field twinkles as the slab turns.
// Flakes are tinted by a diffraction spectrum, and a broad rainbow sheen
// drifts across the sheet. HDR output for bloom.
Shader "FidgetingApp/Gate12R008GlitterHolo"
{
    Properties
    {
        _BaseColor("Stock Colour", Color) = (0.56, 0.58, 0.62, 1)
        _KeyDirection("Key Direction", Vector) = (0.45, 0.55, -0.70, 0)
        _FillDirection("Fill Direction", Vector) = (-0.70, 0.20, -0.65, 0)
        _FlakeDensity("Flake Density (cells per metre)", Range(200, 6000)) = 1500
        _FlakeSpread("Flake Normal Spread", Range(0, 1)) = 0.55
        _FlakeSharpness("Flake Sharpness", Range(8, 600)) = 160
        _FlakeIntensity("Flake Intensity", Range(0, 12)) = 4.5
        _FlakeSaturation("Flake Colour Saturation", Range(0, 1)) = 0.75
        _FineDensityScale("Fine Layer Density Multiplier", Range(1, 4)) = 2.3
        _SheenStrength("Rainbow Sheen", Range(0, 2)) = 0.45
        _SheenScale("Rainbow Sheen Scale", Range(0.5, 20)) = 3.5
        _SheenPhase("Tilt Phase", Float) = 0
        _SpecularStrength("Sheet Specular", Range(0, 3)) = 0.35
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
            Name "Gate12R008GlitterHolo"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.0

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _BaseColor;
                float4 _KeyDirection;
                float4 _FillDirection;
                float _FlakeDensity;
                half _FlakeSpread;
                half _FlakeSharpness;
                half _FlakeIntensity;
                half _FlakeSaturation;
                half _FineDensityScale;
                half _SheenStrength;
                half _SheenScale;
                half _SheenPhase;
                half _SpecularStrength;
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
                float2 uv : TEXCOORD2;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                VertexPositionInputs positions = GetVertexPositionInputs(input.positionOS.xyz);
                output.positionCS = positions.positionCS;
                output.positionWS = positions.positionWS;
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                output.uv = input.uv;
                return output;
            }

            float4 Hash4(float3 cell)
            {
                float3 p = frac(cell * float3(0.1031, 0.1030, 0.0973));
                p += dot(p, p.yxz + 33.33);
                return frac(float4(
                    (p.x + p.y) * p.z,
                    (p.x + p.z) * p.y,
                    (p.y + p.z) * p.x,
                    (p.x + p.y + p.z) * 0.5));
            }

            half3 Spectrum(half t)
            {
                return 0.5h + 0.5h * cos(6.28318h * (t + half3(0.0h, 0.33h, 0.67h)));
            }

            // One flake layer: cells in world space so density is physical.
            half3 Flakes(float3 positionWS, half3 normalWS, half3 viewDirection,
                half3 key, half3 fill, float density, half weight)
            {
                float3 scaled = positionWS * density;
                float3 cell = floor(scaled);
                float3 local = frac(scaled);
                float4 h = Hash4(cell);
                float4 h2 = Hash4(cell + 91.7);
                // One round flake per cell, off-centre and of random size, so
                // the glint is a soft dot rather than a filled square.
                float3 center = 0.25 + h2.xyz * 0.50;
                half radius = 0.22h + h2.w * 0.24h;
                half distance = length(local - center);
                half shape = 1.0h - smoothstep(radius * 0.35h, radius, distance);
                half3 jitter = (h.xyz - 0.5h) * 2.0h * _FlakeSpread;
                half3 flakeNormal = normalize(normalWS + jitter);
                half3 reflected = reflect(-viewDirection, flakeNormal);
                half glintKey = pow(saturate(dot(reflected, key)), _FlakeSharpness);
                half glintFill = pow(saturate(dot(reflected, fill)), _FlakeSharpness) * 0.45h;
                // Some flakes are simply brighter stock than others.
                half brightness = 0.35h + h.w * 0.65h;
                half3 tint = lerp(half3(1, 1, 1),
                    Spectrum(h.w + dot(viewDirection, flakeNormal) * 1.5h),
                    _FlakeSaturation);
                // Flakes that are not glinting still show as coloured
                // specks: that speckle field is what reads as glitter stock
                // from arm's length.
                half body = (0.06h + 0.16h * h.w) * saturate(dot(normalWS, key) + 0.4h);
                return tint * (glintKey + glintFill + body) * brightness * shape * weight;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half3 normalWS = normalize(input.normalWS);
                half3 viewDirection = SafeNormalize(GetWorldSpaceViewDir(input.positionWS));
                half3 key = normalize(_KeyDirection.xyz);
                half3 fill = normalize(_FillDirection.xyz);

                half diffuse = 0.42h
                    + saturate(dot(normalWS, key)) * 0.42h
                    + saturate(dot(normalWS, fill)) * 0.16h;
                half3 reflected = reflect(-viewDirection, normalWS);
                half specular = pow(saturate(dot(reflected, key)), 28.0h) * _SpecularStrength;

                // Broad diffraction sheen sweeping across the sheet.
                half facing = saturate(dot(normalWS, viewDirection));
                // Diagonal, broad, so it reads as a drifting rainbow wash
                // and not as vertical stripes.
                half sheenT = (input.uv.x * 0.55h + input.uv.y * 0.85h) * _SheenScale * 0.18h
                    + dot(viewDirection, half3(1, 0, 0)) * 1.1h
                    + _SheenPhase;
                half3 sheen = Spectrum(sheenT) * _SheenStrength * (0.45h + (1.0h - facing) * 0.55h);

                half3 flakes = Flakes(input.positionWS, normalWS, viewDirection, key, fill,
                        _FlakeDensity, 1.0h)
                    + Flakes(input.positionWS + 17.31, normalWS, viewDirection, key, fill,
                        _FlakeDensity * _FineDensityScale, 0.6h);
                flakes *= _FlakeIntensity;

                half3 color = _BaseColor.rgb * (diffuse + sheen) + specular + flakes;
                return half4(color, 1.0h);
            }
            ENDHLSL
        }
    }
}
