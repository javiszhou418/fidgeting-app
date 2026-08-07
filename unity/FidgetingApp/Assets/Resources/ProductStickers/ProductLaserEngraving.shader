Shader "FidgetingApp/Product Laser Engraving"
{
    Properties
    {
        [MainTexture] _BaseMap("Engraving Mask", 2D) = "white" {}
        [MainColor] _EngraveColor("Engraved Metal", Color) = (0.045, 0.052, 0.060, 1)
        _EdgeColor("Cut Edge", Color) = (0.76, 0.80, 0.84, 1)
        _Strength("Engraving Strength", Range(0, 1)) = 0.88
        _BevelStrength("Cut Edge Strength", Range(0, 1)) = 0.88
        _SurfaceAlignment("Top Surface Alignment", Range(-1, 1)) = 0.12
        _SurfaceLift("Surface Lift", Range(0, 0.0004)) = 0.00018
    }

    SubShader
    {
        Tags
        {
            "RenderPipeline" = "UniversalPipeline"
            "Queue" = "AlphaTest+25"
            "RenderType" = "TransparentCutout"
            "IgnoreProjector" = "True"
        }

        Pass
        {
            Name "LaserEngraving"
            Tags { "LightMode" = "SRPDefaultUnlit" }

            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite On
            ZTest LEqual
            Cull Back
            Offset -4, -4
            AlphaToMask On

            HLSLPROGRAM
            #pragma target 2.0
            #pragma vertex Vert
            #pragma fragment Frag

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            TEXTURE2D(_BaseMap);
            SAMPLER(sampler_BaseMap);

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                float4 _BaseMap_TexelSize;
                half4 _EngraveColor;
                half4 _EdgeColor;
                half _Strength;
                half _BevelStrength;
                half _SurfaceAlignment;
                half _SurfaceLift;
                float4x4 _ReceiverToProjector;
                float4 _ProjectionNormalOS;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                half3 normalOS : TEXCOORD1;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                float3 liftedPositionOS = input.positionOS.xyz
                    + normalize(input.normalOS) * _SurfaceLift;
                output.positionCS = TransformObjectToHClip(liftedPositionOS);
                float3 projection = mul(
                    _ReceiverToProjector,
                    input.positionOS).xyz;
                output.uv = (projection.xy + 0.5) * _BaseMap_ST.xy
                    + _BaseMap_ST.zw;
                output.normalOS = input.normalOS;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float2 inside = min(input.uv, 1.0 - input.uv);
                clip(min(inside.x, inside.y));

                half surfaceAlignment = dot(
                    normalize(input.normalOS),
                    normalize(_ProjectionNormalOS.xyz));
                clip(surfaceAlignment - _SurfaceAlignment);

                half coverage = SAMPLE_TEXTURE2D(
                    _BaseMap,
                    sampler_BaseMap,
                    input.uv).a;
                clip(coverage - 0.06h);

                // Use a screen-aware inner cut edge. A one-texture-texel edge
                // vanishes after minification and at oblique angles; fwidth
                // keeps the machined highlight narrow but readable on both
                // bright and dark metal reflections.
                float2 bevelOffset = max(
                    _BaseMap_TexelSize.xy * 1.75,
                    fwidth(input.uv) * 1.35);
                half left = SAMPLE_TEXTURE2D(
                    _BaseMap,
                    sampler_BaseMap,
                    input.uv - float2(bevelOffset.x, 0.0)).a;
                half right = SAMPLE_TEXTURE2D(
                    _BaseMap,
                    sampler_BaseMap,
                    input.uv + float2(bevelOffset.x, 0.0)).a;
                half lower = SAMPLE_TEXTURE2D(
                    _BaseMap,
                    sampler_BaseMap,
                    input.uv - float2(0.0, bevelOffset.y)).a;
                half upper = SAMPLE_TEXTURE2D(
                    _BaseMap,
                    sampler_BaseMap,
                    input.uv + float2(0.0, bevelOffset.y)).a;
                half neighborFloor = min(min(left, right), min(lower, upper));
                half inwardEdge = saturate((coverage - neighborFloor) * 2.2h);
                half gradientEdge = saturate(
                    length(half2(right - left, upper - lower)));
                half bevel = saturate(max(inwardEdge, gradientEdge)
                    * _BevelStrength);
                half core = saturate(coverage * _Strength);
                half3 color = lerp(
                    _EngraveColor.rgb,
                    _EdgeColor.rgb,
                    saturate(bevel * 0.92h));
                half alpha = saturate(max(core, bevel * 0.95h));
                return half4(color, alpha);
            }
            ENDHLSL
        }
    }

    FallBack Off
}
