Shader "FidgetingApp/Isolated/R022/MakeItShineCc0ContourSweep"
{
    Properties
    {
        [MainColor] _RimColor("Warm Neutral Rim", Color) = (1, 0.78, 0.54, 1)
        _SweepProgress("Source Sphere Sweep", Range(0, 1)) = 0
        _Intensity("Sweep Intensity", Range(0, 1)) = 0
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
            Name "TornContourSweep"
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

            CBUFFER_START(UnityPerMaterial)
                half4 _RimColor;
                half _SweepProgress;
                half _Intensity;
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
                output.uv = input.uv;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half opened = smoothstep(
                    0.96h - _SweepProgress,
                    1.04h - _SweepProgress,
                    input.uv.x);
                half localX = input.uv.x * 1.20h - 0.60h;
                half sphere = FidgetingCc0SphereMask(
                    float3(localX, input.uv.y, 0.0f),
                    float3(lerp(0.60f, -0.60f, _SweepProgress), 0.5f, 0.0f),
                    0.13h,
                    0.94h);
                half sourceBand = FidgetingCc0DiagonalBand(
                    localX,
                    1.0h - _SweepProgress,
                    0.11h,
                    0.78h);
                half lipCenter = 1.0h - smoothstep(
                    0.10h,
                    0.50h,
                    abs(input.uv.y - 0.5h));
                half alpha = opened * sphere * sourceBand * lipCenter
                    * _Intensity * _RimColor.a;
                clip(alpha - 0.004h);
                return half4(_RimColor.rgb * alpha, alpha);
            }
            ENDHLSL
        }
    }
}
