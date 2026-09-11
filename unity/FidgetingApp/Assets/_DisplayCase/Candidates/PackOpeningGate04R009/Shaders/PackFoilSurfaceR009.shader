Shader "FidgetingApp/Candidates/PackFoilSurfaceR009"
{
    Properties
    {
        [MainTexture] _BaseMap("Foil Artwork", 2D) = "white" {}
        [MainColor] _BaseColor("Tint", Color) = (1, 1, 1, 1)
        _HighlightColor("Highlight", Color) = (1, 0.96, 0.88, 1)
        _VioletEdge("Epic Edge", Color) = (0.46, 0.30, 0.68, 1)
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "Transparent"
            "Queue" = "Transparent+30"
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
                half4 _HighlightColor;
                half4 _VioletEdge;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
                half4 color : COLOR;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 normalWS : TEXCOORD0;
                float2 uv : TEXCOORD1;
                half4 color : COLOR;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                output.color = input.color;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half4 artwork = SAMPLE_TEXTURE2D(
                    _BaseMap,
                    sampler_BaseMap,
                    input.uv
                ) * _BaseColor;
                clip(artwork.a - 0.012h);

                half3 normalWS = normalize(input.normalWS);
                half grazing = pow(
                    saturate(1.0h - abs(normalWS.z)),
                    3.0h
                );
                half narrowFold =
                    pow(
                        saturate(
                            1.0h
                            - abs(frac(input.uv.x * 9.0h) - 0.5h) * 5.0h
                        ),
                        4.0h
                    )
                    * input.color.r;
                half releasedEdge =
                    smoothstep(0.72h, 1.0h, input.color.r)
                    * smoothstep(0.0h, 0.12h, input.color.g);

                half3 color = artwork.rgb;
                color += _HighlightColor.rgb
                    * (0.20h * grazing + 0.26h * narrowFold);
                color = lerp(
                    color,
                    _VioletEdge.rgb + 0.16h,
                    releasedEdge * 0.16h
                );
                return half4(color, artwork.a);
            }
            ENDHLSL
        }
    }
}
