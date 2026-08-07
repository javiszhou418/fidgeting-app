Shader "FidgetingApp/EnvironmentStarfield"
{
    Properties
    {
        _StarColor("Star Color", Color) = (0.75, 0.82, 0.78, 1)
        _Density("Density", Range(0, 0.2)) = 0.035
        _Grid("Grid", Range(16, 160)) = 72
        _Seed("Seed", Float) = 1
        _Intensity("Intensity", Range(0, 2)) = 0.65
        _PointRadius("Point Radius", Range(0.01, 0.45)) = 0.14
    }

    SubShader
    {
        Tags
        {
            "RenderPipeline" = "UniversalPipeline"
            "RenderType" = "Transparent"
            "Queue" = "Transparent"
        }

        Pass
        {
            Name "EnvironmentStarfield"
            Tags { "LightMode" = "UniversalForward" }
            Blend SrcAlpha One
            ZWrite Off
            ZTest LEqual
            Cull Off

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionHCS : SV_POSITION;
                float2 uv : TEXCOORD0;
            };

            CBUFFER_START(UnityPerMaterial)
                half4 _StarColor;
                half _Density;
                half _Grid;
                half _Seed;
                half _Intensity;
                half _PointRadius;
            CBUFFER_END

            float Hash21(float2 value)
            {
                value = frac(value * float2(123.34, 456.21));
                value += dot(value, value + 45.32 + _Seed);
                return frac(value.x * value.y);
            }

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionHCS = TransformObjectToHClip(input.positionOS.xyz);
                output.uv = input.uv;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float2 gridUv = input.uv * _Grid;
                float2 cell = floor(gridUv);
                float2 local = frac(gridUv) - 0.5;
                float randomValue = Hash21(cell + _Seed);
                float starExists = step(1.0 - _Density, randomValue);
                float radiusVariation = lerp(0.55, 1.0, Hash21(cell + _Seed * 3.17));
                float twinklePhase = Hash21(cell + _Seed * 7.91) * 6.2831853;
                float twinkleRate = lerp(0.55, 1.65, Hash21(cell + _Seed * 11.37));
                float twinkle = lerp(
                    0.58,
                    1.0,
                    0.5 + 0.5 * sin(_Time.y * twinkleRate + twinklePhase));
                float2 pointDelta = local;
                pointDelta.y *= 1.7778;
                float star = 1.0 - smoothstep(
                    _PointRadius * radiusVariation,
                    _PointRadius * radiusVariation + 0.045,
                    length(pointDelta));

                // Stars live in the exposed upper canyon opening. The side
                // feather avoids painting them across opaque foreground rock.
                float verticalMask = smoothstep(0.43, 0.64, input.uv.y);
                float sideMask = smoothstep(0.05, 0.24, input.uv.x)
                    * (1.0 - smoothstep(0.76, 0.95, input.uv.x));
                half alpha = starExists * star * verticalMask * sideMask
                    * _StarColor.a * _Intensity * twinkle;
                return half4(_StarColor.rgb * _Intensity * twinkle, alpha);
            }
            ENDHLSL
        }
    }
}
