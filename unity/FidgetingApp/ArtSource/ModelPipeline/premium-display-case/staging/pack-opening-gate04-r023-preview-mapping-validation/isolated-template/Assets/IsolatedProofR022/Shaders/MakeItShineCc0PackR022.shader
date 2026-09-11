Shader "FidgetingApp/Isolated/R022/MakeItShineCc0Pack"
{
    Properties
    {
        [MainTexture] _BaseMap("Pack Artwork", 2D) = "white" {}
        [MainColor] _BaseColor("Pack Tint", Color) = (1, 1, 1, 1)
        _Dissolve("CC0 Discard Progress", Range(0, 1)) = 0
        _EdgeWidth("Discard Edge Width", Range(0.001, 0.08)) = 0.014
        _EdgeColor("Warm Neutral Edge", Color) = (1, 0.82, 0.60, 1)
        _EdgeStrength("Edge Strength", Range(0, 1)) = 0
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
                float2 tearContour : TEXCOORD1;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float2 tearContour : TEXCOORD1;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                output.tearContour = input.tearContour;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half4 artwork = SAMPLE_TEXTURE2D(
                    _BaseMap,
                    sampler_BaseMap,
                    input.uv) * _BaseColor;
                half contourDistance = input.tearContour.x - _Dissolve;
                half edge = 1.0h - smoothstep(
                    0.0h,
                    max(_EdgeWidth, 0.0001h),
                    abs(contourDistance));
                clip(artwork.a - _Cutoff);
                clip(contourDistance);
                artwork.rgb += _EdgeColor.rgb * edge * _EdgeStrength;
                return half4(artwork.rgb, 1.0h);
            }
            ENDHLSL
        }
    }
}
