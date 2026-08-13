Shader "FidgetingApp/PremiumBadgeArtwork"
{
    Properties
    {
        _BaseMap("Badge Artwork", 2D) = "white" {}
        _EtchColor("Grey Silver Laser", Color) = (0.66, 0.69, 0.71, 1)
        _EtchOpacity("Etch Opacity", Range(0, 1)) = 0.88
        _GrainStrength("Laser Grain", Range(0, 0.2)) = 0.065
    }

    SubShader
    {
        Tags
        {
            "Queue"="Transparent+10"
            "RenderType"="Transparent"
            "RenderPipeline"="UniversalPipeline"
        }
        Blend SrcAlpha OneMinusSrcAlpha
        ZWrite Off
        Cull Off

        Pass
        {
            Name "BadgeArtworkForward"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.0

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURE2D(_BaseMap);
            SAMPLER(sampler_BaseMap);

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                half4 _EtchColor;
                half _EtchOpacity;
                half _GrainStrength;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                half3 normalWS : TEXCOORD2;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                VertexPositionInputs positionInputs =
                    GetVertexPositionInputs(input.positionOS.xyz);
                VertexNormalInputs normalInputs =
                    GetVertexNormalInputs(input.normalOS);
                output.positionCS = positionInputs.positionCS;
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                output.positionWS = positionInputs.positionWS;
                output.normalWS = normalInputs.normalWS;
                return output;
            }

            half LaserGrain(float2 coordinate)
            {
                float2 cell = floor(coordinate * 620.0);
                half noise = frac(sin(dot(cell, float2(12.9898, 78.233)))
                    * 43758.5453);
                return lerp(1.0h, 0.84h + noise * 0.16h, _GrainStrength / 0.2h);
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half4 artwork = SAMPLE_TEXTURE2D(
                    _BaseMap,
                    sampler_BaseMap,
                    input.uv);
                half alphaWidth = max(fwidth(artwork.a) * 1.4h, 0.006h);
                half mask = smoothstep(
                    0.10h - alphaWidth,
                    0.56h + alphaWidth,
                    artwork.a);
                half artworkLuma = dot(
                    artwork.rgb,
                    half3(0.2126h, 0.7152h, 0.0722h));

                half3 normalWS = normalize(input.normalWS);
                half3 viewDirection = SafeNormalize(
                    GetWorldSpaceViewDir(input.positionWS));
                Light mainLight = GetMainLight();
                half diffuse = saturate(abs(dot(normalWS, mainLight.direction)));
                half ambient = saturate(dot(
                    SampleSH(normalWS),
                    half3(0.3333h, 0.3333h, 0.3333h)));
                half facing = saturate(abs(dot(normalWS, viewDirection)));
                half illumination = saturate(
                    0.60h
                    + diffuse * 0.20h
                    + ambient * 0.12h
                    + (1.0h - facing) * 0.08h);
                half grain = LaserGrain(input.uv);
                half etchedDetail = lerp(0.78h, 1.0h, artworkLuma);
                half alpha = mask * _EtchOpacity * etchedDetail;
                clip(alpha - 0.012h);
                return half4(
                    _EtchColor.rgb * illumination * grain,
                    alpha);
            }
            ENDHLSL
        }
    }
}
