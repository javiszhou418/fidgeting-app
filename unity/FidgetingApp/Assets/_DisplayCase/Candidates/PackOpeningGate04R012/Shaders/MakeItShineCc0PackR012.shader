Shader "FidgetingApp/Candidates/MakeItShineCc0PackR012"
{
    Properties
    {
        [MainTexture] _BaseMap("Pack Artwork", 2D) = "white" {}
        [MainColor] _BaseColor("Pack Tint", Color) = (1, 1, 1, 1)
        _NoiseMap("CC0 Noise (Audit Only)", 2D) = "gray" {}
        _Dissolve("CC0 Discard Progress", Range(0, 1)) = 0
        _EdgeWidth("Discard Edge Width", Range(0.001, 0.1)) = 0.012
        _EdgeColor("Discard Edge Color", Color) = (1, 0.94, 0.82, 1)
        _EdgeStrength("Discard Edge Strength", Range(0, 2)) = 0.50
        _TearSweep("Tear Sweep Progress", Range(0, 1)) = 0
        _TearEdgeWidth("Tear Edge Width", Range(0.005, 0.2)) = 0.048
        _TearEdgeColor("Tear Edge Color", Color) = (0.94, 0.82, 0.62, 1)
        _TearEdgeStrength("Tear Edge Strength", Range(0, 2)) = 0.34
        _Cutoff("Alpha Cutoff", Range(0, 1)) = 0.018
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
                half _EdgeWidth;
                half _EdgeStrength;
                half _TearSweep;
                half _TearEdgeWidth;
                half _TearEdgeStrength;
                half _Cutoff;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
                float2 contour : TEXCOORD1;
                float2 open : TEXCOORD2;
                half4 color : COLOR;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float2 contour : TEXCOORD1;
                float2 open : TEXCOORD2;
                half4 color : COLOR;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                output.contour = input.contour;
                output.open = input.open;
                output.color = input.color;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half4 artwork = SAMPLE_TEXTURE2D(
                    _BaseMap,
                    sampler_BaseMap,
                    input.uv) * _BaseColor * input.color;

                // SG_BoosterPack's discard edge is retargeted from the actual
                // per-column torn contour. The source noise is retained for
                // audit but never creates pixel-hole dissolve.
                half contourDistance = (half)input.contour.x
                    - _Dissolve
                    + (half)input.open.x * 0.0025h;
                clip(min(artwork.a - _Cutoff, contourDistance));

                half3 color = artwork.rgb;
                half tearBand = 1.0h - smoothstep(
                    0.0h,
                    _TearEdgeWidth,
                    (half)input.contour.x);
                half opened = smoothstep(0.01h, 0.32h, (half)input.contour.y);
                color += _TearEdgeColor.rgb
                    * tearBand
                    * opened
                    * _TearSweep
                    * _TearEdgeStrength;

                half discardBand = 1.0h - smoothstep(
                    0.0h,
                    _EdgeWidth,
                    abs(contourDistance));
                color += _EdgeColor.rgb
                    * discardBand
                    * _EdgeStrength
                    * saturate((half)input.contour.y + _Dissolve * 1.4h);
                return half4(color, 1.0h);
            }
            ENDHLSL
        }
    }
}
