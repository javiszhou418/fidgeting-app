// R007 rarity badge finish: die-struck sandblasted foil, like an enamel
// pin body. The alpha mask is the relief; its gradient becomes a polished
// bevel, the field inside carries a bead-blast grain and a warm-to-deep
// gradient, and the recess just outside the relief darkens. Lighting is a
// fixed virtual key so it matches the R005 plate without a probe. The
// bevel is measured in world metres from screen derivatives, so it works
// on a quad, a font atlas glyph, or the pack emblem alike.
Shader "FidgetingApp/Gate12R007SandblastFoil"
{
    Properties
    {
        _MainTex("Relief Mask (alpha)", 2D) = "white" {}
        _GrainTex("Sandblast Grain (RG tilt, B speckle)", 2D) = "bump" {}
        _FoilColor("Foil Tint", Color) = (0.96, 0.78, 0.38, 1)
        _GrainTilesPerMeter("Grain Tiles Per Metre", Range(1, 64)) = 16
        _GrainStrength("Grain Tilt", Range(0, 2)) = 0.9
        _SpeckleStrength("Grain Speckle", Range(0, 1)) = 0.35
        _BevelWidth("Bevel Width (m)", Range(0.00005, 0.002)) = 0.0004
        _BevelHeight("Bevel Tilt", Range(0, 4)) = 1.6
        _EdgeGain("Bevel Detect Gain", Range(0.5, 8)) = 3
        _EdgeDarken("Recess Darken", Range(0, 1)) = 0.55
        _RecessReach("Recess Reach (bevel widths)", Range(1, 2)) = 2
        _FaceGloss("Relief Face Polish", Range(0, 1)) = 0
        _GradientScale("Gradient Scale (object Y)", Float) = 1
        _GradientOffset("Gradient Offset", Range(-1, 1)) = 0
        _GradientStrength("Gradient Strength", Range(0, 1)) = 1
        _Cutoff("Coverage Cutoff", Range(0.05, 0.95)) = 0.5
        _SheenPhase("Tilt Phase (R053 driver)", Float) = 0
    }

    SubShader
    {
        Tags
        {
            "RenderType"="Transparent"
            "Queue"="Transparent"
            "RenderPipeline"="UniversalPipeline"
        }
        // TextMesh glyph quads carry no normals and font shaders draw both
        // sides; keep that so the tier word never culls away.
        Cull Off
        ZWrite Off
        ZTest LEqual
        Blend SrcAlpha OneMinusSrcAlpha

        Pass
        {
            Name "Gate12R007SandblastFoil"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.0

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            TEXTURE2D(_MainTex);
            SAMPLER(sampler_MainTex);
            TEXTURE2D(_GrainTex);
            SAMPLER(sampler_GrainTex);

            CBUFFER_START(UnityPerMaterial)
                float4 _MainTex_ST;
                float4 _GrainTex_ST;
                half4 _FoilColor;
                half _GrainTilesPerMeter;
                half _GrainStrength;
                half _SpeckleStrength;
                float _BevelWidth;
                half _BevelHeight;
                half _EdgeGain;
                half _EdgeDarken;
                half _RecessReach;
                half _FaceGloss;
                float _GradientScale;
                half _GradientOffset;
                half _GradientStrength;
                half _Cutoff;
                half _SheenPhase;
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
                VertexPositionInputs positions =
                    GetVertexPositionInputs(input.positionOS.xyz);
                output.positionCS = positions.positionCS;
                output.positionWS = positions.positionWS;
                // Glyph meshes have no normals; the readable side faces -Z.
                float3 normalOS = dot(input.normalOS, input.normalOS) < 1e-6
                    ? float3(0, 0, -1)
                    : input.normalOS;
                output.normalWS = TransformObjectToWorldNormal(normalOS);
                output.uv = input.uv;
                return output;
            }

            half Mask(float2 uv)
            {
                return SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, uv).a;
            }

            // UV step that moves `worldStep` metres across the surface,
            // solved from the screen-space Jacobians of position and uv.
            // Platform-independent (Metal/GL ddy sign cancels) and glyph
            // orientation independent.
            float2 UvStepForWorld(
                float3 worldStep,
                float3 dPdx, float3 dPdy,
                float2 dUdx, float2 dUdy)
            {
                float a = dot(dPdx, dPdx);
                float b = dot(dPdx, dPdy);
                float c = dot(dPdy, dPdy);
                float det = a * c - b * b;
                float rx = dot(dPdx, worldStep);
                float ry = dot(dPdy, worldStep);
                if (abs(det) < 1e-26)
                {
                    return (dUdx + dUdy) * 0.5;
                }
                float alpha = (rx * c - ry * b) / det;
                float beta = (a * ry - b * rx) / det;
                return alpha * dUdx + beta * dUdy;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float2 uv = input.uv;
                float3 dPdx = ddx(input.positionWS);
                float3 dPdy = ddy(input.positionWS);
                float2 dUdx = ddx(uv);
                float2 dUdy = ddy(uv);
                float pixelMetres = max(length(dPdx), length(dPdy));

                half3 view = SafeNormalize(GetWorldSpaceViewDir(input.positionWS));
                half3 N = normalize(input.normalWS);
                // Two-sided: light the side that faces the camera.
                N = dot(N, view) < 0.0h ? -N : N;
                float3 up = float3(0, 1, 0);
                float3 U = up - N * dot(up, N);
                U = length(U) < 1e-3 ? float3(1, 0, 0) : normalize(U);
                float3 R = normalize(cross(N, U));

                // Bevel never thinner than one pixel, so it survives the
                // hero distance; never wider than authored, so a macro
                // shows the true relief.
                float step = max(_BevelWidth, pixelMetres);
                float2 duvR = UvStepForWorld(R * step, dPdx, dPdy, dUdx, dUdy);
                float2 duvU = UvStepForWorld(U * step, dPdx, dPdy, dUdx, dUdy);

                half a0 = Mask(uv);
                half aRp = Mask(uv + duvR);
                half aRm = Mask(uv - duvR);
                half aUp = Mask(uv + duvU);
                half aUm = Mask(uv - duvU);
                half gx = (aRp - aRm) * 0.5h;
                half gy = (aUp - aUm) * 0.5h;

                half aa = max(fwidth(a0) * 0.7h, 0.01h);
                half coverage = smoothstep(_Cutoff - aa, _Cutoff + aa, a0);
                // Recess reaches _RecessReach bevel widths out, fading with
                // distance. Font-atlas glyphs keep it at 1 so the taps never
                // cross the 1-texel padding into a neighbouring glyph.
                half near = max(max(aRp, aRm), max(aUp, aUm));
                half far = max(
                    max(Mask(uv + duvR * _RecessReach), Mask(uv - duvR * _RecessReach)),
                    max(Mask(uv + duvU * _RecessReach), Mask(uv - duvU * _RecessReach)));
                half farWeight = saturate((_RecessReach - 1.0h)) * 0.45h;
                half recess = (1.0h - coverage)
                    * max(smoothstep(0.15h, 0.75h, near), smoothstep(0.15h, 0.75h, far) * farWeight);
                half edge = saturate(length(half2(gx, gy)) * _EdgeGain);

                // Bead-blast grain in a surface frame, so it turns with the case.
                float2 surface = float2(dot(input.positionWS, R), dot(input.positionWS, U));
                half3 grain = SAMPLE_TEXTURE2D(
                    _GrainTex, sampler_GrainTex, surface * _GrainTilesPerMeter).rgb;
                half2 tilt = (grain.rg * 2.0h - 1.0h) * _GrainStrength * (1.0h - edge * 0.85h);
                half speckle = (grain.b * 2.0h - 1.0h) * _SpeckleStrength * (1.0h - edge * 0.7h);

                half3 n = normalize(
                    N
                    - R * (gx * _BevelHeight + tilt.x)
                    - U * (gy * _BevelHeight + tilt.y));

                half3 key = normalize(half3(-0.34h, 0.72h, -0.60h));
                half3 fill = normalize(half3(0.55h, 0.25h, -0.75h));
                half3 halfKey = normalize(key + view);
                half3 halfFill = normalize(fill + view);

                half diffuseKey = saturate(dot(n, key));
                half diffuseFill = saturate(dot(n, fill));
                half nhK = saturate(dot(n, halfKey));
                half nhF = saturate(dot(n, halfFill));
                // Field: bead-blast satin. Relief face (_FaceGloss): polished,
                // a broad bright lobe plus a tight hot spot, like struck brass.
                half satin = pow(nhK, 28.0h) * 0.45h + pow(nhF, 20.0h) * 0.15h;
                half glossFace = pow(nhK, 12.0h) * 0.55h + pow(nhK, 90.0h) * 0.6h
                    + pow(nhF, 24.0h) * 0.25h;
                half face = lerp(satin, glossFace, _FaceGloss);
                half polish = pow(nhK, 160.0h) * 1.25h + pow(nhF, 90.0h) * 0.35h;
                half spec = lerp(face, polish, edge);
                half fresnel = pow(1.0h - saturate(dot(n, view)), 4.0h);

                half3 foil = _FoilColor.rgb;
                half luma = dot(foil, half3(0.299h, 0.587h, 0.114h));
                half3 deep = saturate(lerp(half3(luma, luma, luma), foil, 1.30h)) * 0.42h;
                // Top of the field lifts toward pale champagne.
                half3 light = saturate(lerp(foil, half3(1, 1, 1), 0.22h) * 1.08h);
                float objectY = TransformWorldToObject(input.positionWS).y;
                half gradient = saturate(objectY * _GradientScale + 0.5h + _GradientOffset);
                gradient = lerp(0.6h, gradient, _GradientStrength);
                half3 albedo = lerp(deep, light, gradient) * (1.0h + speckle);
                // Polished metal reads as bare bright metal, not grain.
                albedo = lerp(albedo, light, saturate(edge * 0.5h + _FaceGloss * 0.35h));

                half3 color = albedo * (0.30h + 0.62h * diffuseKey + 0.18h * diffuseFill)
                    + foil * spec
                    + foil * fresnel * 0.12h;
                color = min(color, 0.985h);

                half recessAlpha = recess * _EdgeDarken;
                half3 recessColor = deep * 0.25h;
                half alpha = coverage + (1.0h - coverage) * recessAlpha;
                half3 rgb = (color * coverage + recessColor * (1.0h - coverage) * recessAlpha)
                    / max(alpha, 1e-3h);
                return half4(rgb, alpha);
            }
            ENDHLSL
        }
    }
}
