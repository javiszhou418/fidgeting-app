Shader "FidgetingApp/Candidates/MakeItShineCc0PackR011"
{
    Properties
    {
        [MainTexture] _BaseMap("Pack Artwork", 2D) = "white" {}
        [MainColor] _BaseColor("Pack Tint", Color) = (1, 1, 1, 1)
        _NoiseMap("CC0 Source Mask (Audit Only)", 2D) = "gray" {}
        _Dissolve("CC0 Discard Progress", Range(0, 1)) = 0
        _DissolveScale("Sweep Slope", Range(0, 0.2)) = 0.05
        _EdgeWidth("Edge Width", Range(0.001, 0.2)) = 0.055
        _EdgeColor("Edge Color", Color) = (0.72, 0.88, 1, 1)
        _EdgeStrength("Edge Strength", Range(0, 2)) = 0.42
        _Cutoff("Alpha Cutoff", Range(0, 1)) = 0.018
        _DissolveJitter("Discard Boundary Jitter", Range(0, 0.12)) = 0.045
        _TearSweep("Tear Sweep Progress", Range(0, 1)) = 0
        _TearEdgeWidth("Tear Edge Band Width", Range(0.01, 1)) = 0.20
        _TearEdgeColor("Tear Edge Color", Color) = (1, 0.93, 0.82, 1)
        _TearEdgeStrength("Tear Edge Strength", Range(0, 4)) = 1.35
        _TearFrontBoost("Tear Front Boost", Range(0, 4)) = 1.9
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "TransparentCutout"
            "Queue" = "AlphaTest"
            "RenderPipeline" = "UniversalPipeline"
        }

        Pass
        {
            Name "ForwardUnlit"
            Tags { "LightMode" = "UniversalForward" }
            Cull Off
            ZWrite On

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            TEXTURE2D(_BaseMap);
            SAMPLER(sampler_BaseMap);
            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                half4 _BaseColor;
                half4 _EdgeColor;
                half4 _TearEdgeColor;
                half _Dissolve;
                half _DissolveScale;
                half _EdgeWidth;
                half _EdgeStrength;
                half _Cutoff;
                half _DissolveJitter;
                half _TearSweep;
                half _TearEdgeWidth;
                half _TearEdgeStrength;
                half _TearFrontBoost;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
                float2 contour : TEXCOORD1;
                float2 jitter : TEXCOORD2;
                half4 color : COLOR;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float2 contour : TEXCOORD1;
                float2 jitter : TEXCOORD2;
                half4 color : COLOR;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                output.contour = input.contour;
                output.jitter = input.jitter;
                output.color = input.color;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half4 artwork = SAMPLE_TEXTURE2D(
                    _BaseMap,
                    sampler_BaseMap,
                    input.uv) * _BaseColor * input.color;

                // Audited discard sweep. The boundary is offset per column so it
                // cannot resolve as a clean full-width horizontal rectangle.
                half sweepFront = lerp(1.03h, -0.03h, saturate(_Dissolve));
                half signedDistance = sweepFront
                    - input.uv.y
                    + (input.uv.x - 0.5h) * _DissolveScale
                    + (half)input.jitter.x * _DissolveJitter;
                clip(min(artwork.a - _Cutoff, signedDistance));

                half3 color = artwork.rgb;

                // The audited emissive edge, evaluated in torn-contour space.
                // contour.x is 0 exactly on the torn edge and rises with depth
                // below it, so the band hugs the tear at every tear progress and
                // is present while the Pack is still fully opaque.
                half contourBand =
                    1.0h - smoothstep(0.0h, _TearEdgeWidth, (half)input.contour.x);
                half frontHeat = (half)input.contour.y;
                // Gate on the opened region and the front itself, or the whole
                // sealed seam lights up before anything has torn.
                half torn = max((half)input.jitter.y, frontHeat);
                half tearGlow = contourBand
                    * _TearSweep
                    * torn
                    * (_TearEdgeStrength + _TearFrontBoost * frontHeat);
                color += _TearEdgeColor.rgb * tearGlow;

                // Discard edge, kept thin and confined near the torn contour so
                // widening it can never produce a flat band across the artwork.
                half discardEdge =
                    1.0h - smoothstep(0.0h, _EdgeWidth, signedDistance);
                half nearContour = 1.0h - smoothstep(0.35h, 1.0h, (half)input.contour.x);
                color += _EdgeColor.rgb
                    * discardEdge
                    * _EdgeStrength
                    * (0.30h + 0.70h * nearContour);

                return half4(color, 1.0h);
            }
            ENDHLSL
        }
    }
}
