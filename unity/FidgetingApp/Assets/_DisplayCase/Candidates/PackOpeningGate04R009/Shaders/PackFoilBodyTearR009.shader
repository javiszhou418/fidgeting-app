Shader "FidgetingApp/Candidates/PackFoilBodyTearR009"
{
    Properties
    {
        [MainTexture] _BaseMap("Pack Artwork", 2D) = "white" {}
        [MainColor] _BaseColor("Tint", Color) = (1, 1, 1, 1)
        _Opening("Opening", Range(0, 1)) = 0
        _Retreat("Torn Edge Retreat", Range(0, 1)) = 0
        _TearEdge("Tear Edge", Range(0, 1)) = 0
        _FoilSweep("Foil Sweep", Range(-0.2, 1.2)) = -0.2
        _EdgeColor("Torn Edge Color", Color) = (0.72, 0.61, 0.84, 1)
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "TransparentCutout"
            "Queue" = "AlphaTest+20"
            "RenderPipeline" = "UniversalPipeline"
        }

        Pass
        {
            Name "ForwardUnlit"
            Tags { "LightMode" = "UniversalForward" }
            Cull Off
            ZWrite On
            Blend SrcAlpha OneMinusSrcAlpha

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
                float _Opening;
                float _Retreat;
                float _TearEdge;
                float _FoilSweep;
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
                float2 uv = input.uv;
                half4 artwork = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, uv)
                    * _BaseColor;
                clip(artwork.a - 0.015h);

                float opening = saturate(_Opening);
                float tearFrontX =
                    lerp(0.945, 0.055, opening)
                    + opening
                        * (
                            0.010 * sin(uv.y * 47.0 + 0.9)
                            + 0.005 * sin(uv.y * 83.0 + 2.4)
                        );
                float openedSpan = max(0.02, 0.965 - tearFrontX);
                float distanceBehindFront = saturate(
                    (uv.x - tearFrontX) / openedSpan);
                float depthEnvelope = smoothstep(
                    0.0,
                    0.18,
                    distanceBehindFront);
                float tornBottom =
                    0.715
                    + (1.0 - depthEnvelope) * 0.090
                    - opening * 0.105 * depthEnvelope
                    + opening
                        * depthEnvelope
                        * (
                            0.016 * sin(uv.x * 31.0 + 0.7)
                            + 0.009 * sin(uv.x * 67.0 + 2.1)
                            + 0.004 * sin(uv.x * 137.0 + 0.3)
                        );
                float behindFront = uv.x - tearFrontX;
                float aboveTornEdge = uv.y - tornBottom;
                if (
                    opening > 0.005
                    && behindFront > 0.0
                    && uv.x < 0.965
                    && aboveTornEdge > 0.0
                )
                {
                    clip(-1.0);
                }

                float retreatContour =
                    1.08
                    - saturate(_Retreat) * 1.34
                    + 0.030 * sin(uv.x * 13.0 + 0.4)
                    + 0.016 * sin(uv.x * 29.0 + 1.9);
                float retreatDistance = retreatContour - uv.y;
                if (_Retreat > 0.0001)
                {
                    clip(retreatDistance);
                }

                float horizontalTornEdge =
                    smoothstep(-0.026, -0.003, aboveTornEdge)
                    * (1.0 - step(0.0, aboveTornEdge))
                    * smoothstep(tearFrontX, tearFrontX + 0.035, uv.x);
                float advancingTearFront =
                    (1.0 - smoothstep(0.0, 0.018, abs(behindFront)))
                    * step(tornBottom - 0.035, uv.y);
                float openingEdge =
                    max(horizontalTornEdge, advancingTearFront)
                    * opening;
                float retreatEdge =
                    (1.0 - smoothstep(0.0, 0.034, retreatDistance))
                    * step(0.001, _Retreat);
                float tearEdge = saturate(max(openingEdge, retreatEdge) * _TearEdge);
                float narrowSweep =
                    pow(
                        saturate(
                            1.0
                            - abs(uv.x - _FoilSweep) / 0.030
                        ),
                        3.0
                    );

                half3 neutralFoil = artwork.rgb * (0.90h + 0.10h * uv.y);
                neutralFoil += narrowSweep * 0.16h;
                neutralFoil = lerp(
                    neutralFoil,
                    _EdgeColor.rgb + 0.20h,
                    tearEdge * 0.44h
                );
                return half4(neutralFoil, artwork.a);
            }
            ENDHLSL
        }
    }
}
