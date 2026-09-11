Shader "FidgetingApp/Candidates/MakeItShineCc0ContourRimR013"
{
    Properties
    {
        [MainColor] _RimColor("Warm Neutral Rim", Color) = (1, 0.68, 0.36, 1)
        _Progress("SG Title Sphere Sweep", Range(0, 1)) = 0
        _Intensity("Rim Intensity", Range(0, 2)) = 0
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
            Name "ContourRim"
            Tags { "LightMode" = "UniversalForward" }
            Cull Off
            ZWrite Off
            ZTest LEqual
            Blend One One

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/MakeItShineCc0Masks.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _RimColor;
                half _Progress;
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
                half sweep = FidgetingCc0SphereMask(
                    float3(input.uv, 0.0f),
                    float3(lerp(-0.18f, 1.18f, _Progress), 0.5f, 0.0f),
                    0.82h,
                    0.42h);
                half crossFade = sin(saturate(_Progress) * 3.14159265h);
                half alpha = sweep * crossFade * _Intensity * _RimColor.a;
                clip(alpha - 0.002h);
                return half4(_RimColor.rgb * alpha, alpha);
            }
            ENDHLSL
        }
    }
}
