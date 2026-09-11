Shader "FidgetingApp/Candidates/MakeItShineCc0PortR011"
{
    Properties
    {
        [MainTexture] _BaseMap("CC0 Flare", 2D) = "white" {}
        [MainColor] _BaseColor("Color", Color) = (1, 1, 1, 1)
        _Reveal("SG Lighting Strike Reveal", Range(0, 1)) = 1
        _Erode("SG Lighting Strike Erode", Range(0, 1)) = 0
        _Speed("SG Lighting Strike Speed", Float) = 0
        _Progress("Timeline Progress", Range(0, 1)) = 0
        _Intensity("Intensity", Range(0, 4)) = 1
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "Transparent"
            "Queue" = "Transparent"
            "RenderPipeline" = "UniversalPipeline"
        }

        Pass
        {
            Name "ForwardAdditive"
            Tags { "LightMode" = "UniversalForward" }
            Cull Off
            ZWrite Off
            ZTest LEqual
            Blend SrcAlpha One

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/MakeItShineCc0Masks.hlsl"

            TEXTURE2D(_BaseMap);
            SAMPLER(sampler_BaseMap);

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                half4 _BaseColor;
                half _Reveal;
                half _Erode;
                half _Speed;
                half _Progress;
                half _Intensity;
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
                output.uv.x = frac(output.uv.x + _Progress * _Speed);
                output.color = input.color;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half4 flare = SAMPLE_TEXTURE2D(
                    _BaseMap,
                    sampler_BaseMap,
                    input.uv);
                half sourceMask = max(flare.r, flare.a);
                half reveal = FidgetingCc0RevealThreshold(
                    sourceMask,
                    _Reveal);
                half eroded = smoothstep(
                    _Erode,
                    min(1.0h, _Erode + 0.08h),
                    sourceMask * reveal);
                half4 color = flare * _BaseColor * input.color;
                color.rgb *= _Intensity * eroded;
                color.a *= eroded;
                clip(color.a - 0.001h);
                return color;
            }
            ENDHLSL
        }
    }
}
