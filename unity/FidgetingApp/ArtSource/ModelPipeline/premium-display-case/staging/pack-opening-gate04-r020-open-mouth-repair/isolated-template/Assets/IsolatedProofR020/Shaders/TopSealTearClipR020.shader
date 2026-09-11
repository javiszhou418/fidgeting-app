Shader "FidgetingApp/Isolated/R020/TopSealTearClip"
{
    Properties
    {
        [MainTexture] _BaseMap("Crimp Artwork", 2D) = "white" {}
        [MainColor] _BaseColor("Crimp Tint", Color) = (1, 1, 1, 1)
        _TearFront("Normalized Tear Front", Range(0, 1)) = 0
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
                half _TearFront;
                half _Cutoff;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 artworkUv : TEXCOORD0;
                float physicalU : TEXCOORD1;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.artworkUv = TRANSFORM_TEX(input.uv, _BaseMap);
                output.physicalU = input.uv.x;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half4 crimp = SAMPLE_TEXTURE2D(
                    _BaseMap,
                    sampler_BaseMap,
                    input.artworkUv) * _BaseColor;
                // Physical U=0 is calibrated to the screen-right pull origin.
                clip(input.physicalU - _TearFront);
                clip(crimp.a - _Cutoff);
                return half4(crimp.rgb, 1.0h);
            }
            ENDHLSL
        }
    }
}
