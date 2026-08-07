Shader "FidgetingApp/EnvironmentParallaxUnlit"
{
    Properties
    {
        _BaseMap("Texture", 2D) = "white" {}
        _BaseColor("Color", Color) = (1, 1, 1, 1)
        _Saturation("Saturation", Range(0, 2)) = 1
        _LayerMask("Layer Mask", Float) = 0
        _LayerMaskStart("Layer Mask Start", Range(0, 1)) = 0.38
        _LayerMaskFeather("Layer Mask Feather", Range(0.001, 0.5)) = 0.10
        _Opacity("Opacity", Range(0, 1)) = 1
        _GlowEnabled("Glow Enabled", Float) = 0
        _GlowColorA("Glow Color A", Color) = (0, 0, 0, 1)
        _GlowColorB("Glow Color B", Color) = (0, 0, 0, 1)
        _GlowCenterA("Glow Center A", Vector) = (0.25, 0.52, 0, 0)
        _GlowCenterB("Glow Center B", Vector) = (0.75, 0.42, 0, 0)
        _GlowScaleA("Glow Scale A", Vector) = (0.5625, 1, 0, 0)
        _GlowScaleB("Glow Scale B", Vector) = (0.5625, 1, 0, 0)
        _GlowRadius("Glow Radius", Range(0.01, 1)) = 0.28
        _GlowIntensity("Glow Intensity", Range(0, 2)) = 0
        _ShadowEnabled("Contact Shadow Enabled", Float) = 0
        _ShadowCenter("Contact Shadow Center", Vector) = (0.5, 0.305, 0, 0)
        _ShadowScale("Contact Shadow Scale", Vector) = (0.82, 11, 0, 0)
        _ShadowRadius("Contact Shadow Radius", Range(0.01, 1)) = 0.20
        _ShadowStrength("Contact Shadow Strength", Range(0, 1)) = 0
        [Enum(UnityEngine.Rendering.BlendMode)] _SrcBlend("Source Blend", Float) = 1
        [Enum(UnityEngine.Rendering.BlendMode)] _DstBlend("Destination Blend", Float) = 0
        [Toggle] _ZWrite("Z Write", Float) = 1
        [Enum(UnityEngine.Rendering.CompareFunction)] _ZTest("Z Test", Float) = 4
    }

    SubShader
    {
        Tags
        {
            "RenderPipeline" = "UniversalPipeline"
            "RenderType" = "Opaque"
            "Queue" = "Geometry"
        }

        Pass
        {
            Name "EnvironmentParallaxUnlit"
            Tags { "LightMode" = "UniversalForward" }
            Blend [_SrcBlend] [_DstBlend]
            ZWrite [_ZWrite]
            ZTest [_ZTest]
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

            TEXTURE2D(_BaseMap);
            SAMPLER(sampler_BaseMap);

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                half4 _BaseColor;
                half _Saturation;
                half _LayerMask;
                half _LayerMaskStart;
                half _LayerMaskFeather;
                half _Opacity;
                half _GlowEnabled;
                half4 _GlowColorA;
                half4 _GlowColorB;
                float4 _GlowCenterA;
                float4 _GlowCenterB;
                float4 _GlowScaleA;
                float4 _GlowScaleB;
                half _GlowRadius;
                half _GlowIntensity;
                half _ShadowEnabled;
                float4 _ShadowCenter;
                float4 _ShadowScale;
                half _ShadowRadius;
                half _ShadowStrength;
            CBUFFER_END

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionHCS = TransformObjectToHClip(input.positionOS.xyz);
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half4 sampled = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, input.uv);
                half3 color = sampled.rgb * _BaseColor.rgb;
                half luminance = dot(color, half3(0.2126h, 0.7152h, 0.0722h));
                color = lerp(luminance.xxx, color, _Saturation);

                if (_GlowEnabled > 0.5h)
                {
                    float2 deltaA = input.uv - _GlowCenterA.xy;
                    float2 deltaB = input.uv - _GlowCenterB.xy;
                    // Independent scales let the main halo remain soft and
                    // round while the second glow compresses into a contact-
                    // light pool on the baked stone ledge.
                    deltaA *= _GlowScaleA.xy;
                    deltaB *= _GlowScaleB.xy;
                    half glowA = saturate(1.0h - length(deltaA) / max(0.01h, _GlowRadius));
                    half glowB = saturate(1.0h - length(deltaB) / max(0.01h, _GlowRadius));
                    glowA *= glowA;
                    glowB *= glowB;
                    color += (_GlowColorA.rgb * glowA + _GlowColorB.rgb * glowB)
                        * _GlowIntensity * sampled.a;
                }

                if (_ShadowEnabled > 0.5h)
                {
                    float2 shadowDelta = input.uv - _ShadowCenter.xy;
                    shadowDelta *= _ShadowScale.xy;
                    half shadowDistance = length(shadowDelta);
                    half shadow = 1.0h - smoothstep(
                        _ShadowRadius * 0.28h,
                        max(0.011h, _ShadowRadius),
                        shadowDistance);
                    // Apply the contact layer after colored bounce so it stays
                    // legible beneath bright and mirror-finish products.
                    color *= 1.0h - shadow * _ShadowStrength;
                }

                half alpha = sampled.a * _BaseColor.a * _Opacity;
                if (_LayerMask > 0.5h)
                {
                    half feather = max(0.001h, _LayerMaskFeather);
                    alpha *= 1.0h - smoothstep(
                        _LayerMaskStart,
                        _LayerMaskStart + feather,
                        input.uv.y);
                }

                return half4(color, alpha);
            }
            ENDHLSL
        }
    }
}
