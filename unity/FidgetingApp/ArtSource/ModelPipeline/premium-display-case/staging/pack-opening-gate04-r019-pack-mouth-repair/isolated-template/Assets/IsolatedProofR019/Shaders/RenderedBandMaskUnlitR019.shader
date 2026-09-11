Shader "FidgetingApp/Isolated/R019/RenderedBandMaskUnlit"
{
    Properties
    {
        [MainTexture] _BaseMap("Artwork", 2D) = "white" {}
        _BandMin("Band Min", Range(0, 1)) = 0
        _BandMax("Band Max", Range(0, 1)) = 1
        _MaskColor("Mask Color", Color) = (0, 1, 1, 1)
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "Opaque"
            "Queue" = "Geometry"
            "RenderPipeline" = "UniversalPipeline"
        }

        Pass
        {
            Name "RenderedBandMask"
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
                half _BandMin;
                half _BandMax;
                half4 _MaskColor;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half alpha = SAMPLE_TEXTURE2D(
                    _BaseMap,
                    sampler_BaseMap,
                    input.uv).a;
                clip(alpha - 0.018h);
                clip(input.uv.y - _BandMin);
                clip(_BandMax - input.uv.y);
                return _MaskColor;
            }
            ENDHLSL
        }
    }
}
