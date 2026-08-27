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
        _AdaptiveSurface("Adaptive Dark Surface", Float) = 0
        _AdaptiveBaseTop("Adaptive Base Top", Color) = (0.024, 0.026, 0.031, 1)
        _AdaptiveBaseBottom("Adaptive Base Bottom", Color) = (0.004, 0.005, 0.008, 1)
        _AdaptiveGrain("Adaptive Grain", Range(0, 0.03)) = 0.012
        _AdaptiveVignette("Adaptive Vignette", Range(0, 0.4)) = 0.18
        _GlowEnabled("Glow Enabled", Float) = 0
        _GlowColorA("Glow Color A", Color) = (0, 0, 0, 1)
        _GlowColorB("Glow Color B", Color) = (0, 0, 0, 1)
        _GlowCenterA("Glow Center A", Vector) = (0.25, 0.52, 0, 0)
        _GlowCenterB("Glow Center B", Vector) = (0.75, 0.42, 0, 0)
        _GlowScaleA("Glow Scale A", Vector) = (0.5625, 1, 0, 0)
        _GlowScaleB("Glow Scale B", Vector) = (0.5625, 1, 0, 0)
        _GlowRadius("Glow Radius", Range(0.01, 1)) = 0.28
        _GlowIntensity("Glow Intensity", Range(0, 2)) = 0
        _TopLightBottomBrightness("Top Light Bottom Brightness", Range(0, 1)) = 0.08
        _TopLightBottomSaturation("Top Light Bottom Saturation", Range(0, 1)) = 0.18
        _TopLightFalloff("Top Light Falloff", Range(0.25, 4)) = 1.25
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
                half _AdaptiveSurface;
                half4 _AdaptiveBaseTop;
                half4 _AdaptiveBaseBottom;
                half _AdaptiveGrain;
                half _AdaptiveVignette;
                half _GlowEnabled;
                half4 _GlowColorA;
                half4 _GlowColorB;
                float4 _GlowCenterA;
                float4 _GlowCenterB;
                float4 _GlowScaleA;
                float4 _GlowScaleB;
                half _GlowRadius;
                half _GlowIntensity;
                half _TopLightBottomBrightness;
                half _TopLightBottomSaturation;
                half _TopLightFalloff;
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
                half3 color;
                if (_AdaptiveSurface > 0.5h)
                {
                    half vertical = smoothstep(0.02h, 0.92h, input.uv.y);
                    color = lerp(
                        _AdaptiveBaseBottom.rgb,
                        _AdaptiveBaseTop.rgb,
                        vertical) * _BaseColor.rgb;

                    float2 vignetteUv = input.uv * 2.0 - 1.0;
                    vignetteUv.x *= 0.72;
                    half vignette = smoothstep(
                        0.30h,
                        1.18h,
                        length(vignetteUv));
                    color *= 1.0h - vignette * _AdaptiveVignette;

                    float2 grainPixel = floor(input.positionHCS.xy);
                    half grain = frac(sin(dot(
                        grainPixel,
                        float2(12.9898, 78.233))) * 43758.5453);
                    color += (grain - 0.5h) * _AdaptiveGrain;
                    sampled = half4(1, 1, 1, 1);
                }
                else
                {
                    color = sampled.rgb * _BaseColor.rgb;
                    half luminance = dot(
                        color,
                        half3(0.2126h, 0.7152h, 0.0722h));
                    color = lerp(luminance.xxx, color, _Saturation);
                }

                if (_GlowEnabled > 0.5h)
                {
                    if (_AdaptiveSurface > 0.5h)
                    {
                        // The reference light is mounted above the product:
                        // its narrow, saturated top opens softly downward,
                        // while both chroma and value continuously fall away.
                        half topProgress = smoothstep(0.03h, 0.98h, input.uv.y);
                        half topFalloff = pow(
                            topProgress,
                            max(0.25h, _TopLightFalloff));
                        half brightness = lerp(
                            _TopLightBottomBrightness,
                            1.0h,
                            topFalloff);
                        half saturation = lerp(
                            _TopLightBottomSaturation,
                            1.0h,
                            topFalloff);
                        half beamWidth = _GlowRadius * lerp(
                            0.92h,
                            0.52h,
                            topProgress);
                        half beamA = 1.0h - smoothstep(
                            0.22h,
                            1.0h,
                            abs(input.uv.x - _GlowCenterA.x)
                                / max(0.01h, beamWidth));
                        half beamB = 1.0h - smoothstep(
                            0.22h,
                            1.0h,
                            abs(input.uv.x - _GlowCenterB.x)
                                / max(0.01h, beamWidth));
                        half luminanceA = dot(
                            _GlowColorA.rgb,
                            half3(0.2126h, 0.7152h, 0.0722h));
                        half luminanceB = dot(
                            _GlowColorB.rgb,
                            half3(0.2126h, 0.7152h, 0.0722h));
                        half3 beamColorA = lerp(
                            luminanceA.xxx,
                            _GlowColorA.rgb,
                            saturation);
                        half3 beamColorB = lerp(
                            luminanceB.xxx,
                            _GlowColorB.rgb,
                            saturation);
                        color += (beamColorA * beamA + beamColorB * beamB)
                            * brightness * _GlowIntensity * sampled.a;
                    }
                    else
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
