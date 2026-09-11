Shader "FidgetingApp/Candidates/MakeItShineCc0PackR013"
{
    Properties
    {
        [MainTexture] _BaseMap("Pack Artwork", 2D) = "white" {}
        [MainColor] _BaseColor("Pack Tint", Color) = (1, 1, 1, 1)
        _Dissolve("CC0 Discard Progress", Range(0, 1)) = 0
        _EdgeWidth("Discard Edge Width", Range(0.001, 0.1)) = 0.018
        _EdgeColor("Discard Edge Color", Color) = (0.95, 0.70, 0.40, 1)
        _EdgeStrength("Discard Edge Strength", Range(0, 2)) = 0.42
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
                half _Dissolve;
                half _EdgeWidth;
                half _EdgeStrength;
                half _Cutoff;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
                half4 color : COLOR;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                half4 color : COLOR;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                output.color = input.color;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half4 artwork = SAMPLE_TEXTURE2D(
                    _BaseMap,
                    sampler_BaseMap,
                    input.uv) * _BaseColor;
                half topDepth = 1.0h - input.uv.y;
                half discardActive = smoothstep(0.001h, 0.020h, _Dissolve);
                half contourDistance = topDepth - _Dissolve;
                clip(artwork.a - _Cutoff);
                clip(contourDistance);

                half discardBand = 1.0h - smoothstep(
                    0.0h,
                    _EdgeWidth,
                    abs(contourDistance));
                artwork.rgb += _EdgeColor.rgb
                    * discardBand
                    * _EdgeStrength
                    * discardActive;
                return half4(artwork.rgb, 1.0h);
            }
            ENDHLSL
        }
    }
}
