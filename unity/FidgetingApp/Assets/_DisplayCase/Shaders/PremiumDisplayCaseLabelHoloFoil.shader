// R053 label plate: brushed metal foil with a view/tilt-driven spectral band
// (the "金属镭射" the carousel Packs already use), so the plate has a real
// reflective surface for highlights to land on. Opaque, single pass, no
// textures; grain is procedural along the plate's long (object X) axis.
Shader "FidgetingApp/PremiumDisplayCaseLabelHoloFoil"
{
    Properties
    {
        _BaseColor("Foil Base", Color) = (0.62, 0.63, 0.65, 1)
        _GrainStrength("Brushed Grain", Range(0, 0.5)) = 0.10
        _GrainScale("Grain Scale", Range(10, 400)) = 160
        _SpectralStrength("Spectral Strength", Range(0, 1)) = 0.34
        _SpectralScale("Spectral Scale", Range(0.1, 6)) = 1.8
        _SpectralStretch("Spectral Stretch Along Plate", Range(0, 4)) = 1.2
        _SheenPhase("Sheen Phase (driven)", Range(-4, 4)) = 0
        _SpecStrength("Specular Strength", Range(0, 2)) = 0.55
        _SpecPower("Specular Tightness", Range(4, 200)) = 48
        _KeyDir("Key Light Direction", Vector) = (-0.45, 0.72, -0.53, 0)
        _FresnelPower("Fresnel Power", Range(0.5, 8)) = 2.4
        _Saturation("Spectral Saturation", Range(0, 1)) = 0.72
    }

    SubShader
    {
        Tags
        {
            "Queue"="Geometry"
            "RenderType"="Opaque"
            "RenderPipeline"="UniversalPipeline"
        }

        Pass
        {
            Name "LabelHoloFoil"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.0

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _BaseColor;
                half _GrainStrength;
                half _GrainScale;
                half _SpectralStrength;
                half _SpectralScale;
                half _SpectralStretch;
                half _SheenPhase;
                half _SpecStrength;
                half _SpecPower;
                float4 _KeyDir;
                half _FresnelPower;
                half _Saturation;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                float3 positionOS : TEXCOORD2;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionWS = TransformObjectToWorld(input.positionOS.xyz);
                output.positionCS = TransformWorldToHClip(output.positionWS);
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                output.positionOS = input.positionOS.xyz;
                return output;
            }

            float Hash(float2 p)
            {
                return frac(sin(dot(p, float2(127.1, 311.7))) * 43758.5453);
            }

            half3 Spectrum(float phase)
            {
                // Smooth cosine palette: full hue cycle per unit of phase.
                half3 rainbow = 0.5 + 0.5 * cos(6.28318 * (phase + half3(0.0, 0.33, 0.67)));
                half grey = dot(rainbow, half3(0.333, 0.333, 0.333));
                return lerp(grey.xxx, rainbow, _Saturation);
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float3 n = normalize(input.normalWS);
                float3 v = normalize(GetWorldSpaceViewDir(input.positionWS));
                float3 longAxis = normalize(TransformObjectToWorldDir(float3(1, 0, 0)));

                // Fine brushed grain: rows along the long axis, jittered.
                float2 grainCoord = float2(
                    input.positionOS.z * _GrainScale,
                    floor(input.positionOS.x * _GrainScale * 0.08));
                half grain = Hash(grainCoord) - 0.5;
                half3 base = _BaseColor.rgb * (1.0 + grain * _GrainStrength);

                // Spectral band: moves with the view/tilt and the driven phase.
                float across = dot(v, longAxis);
                float phase = across * _SpectralScale
                    + input.positionOS.x * _SpectralStretch
                    + _SheenPhase;
                half fresnel = pow(1.0 - saturate(dot(n, v)), _FresnelPower);
                half3 spectral = Spectrum(phase) * _SpectralStrength * (0.35 + 0.65 * fresnel);

                // One key highlight so tilting changes the plate's gloss.
                float3 key = normalize(_KeyDir.xyz);
                float3 h = normalize(v + key);
                half spec = pow(saturate(dot(n, h)), _SpecPower) * _SpecStrength;

                half3 color = base + spectral + spec * half3(1.0, 0.98, 0.95);
                return half4(color, 1.0);
            }
            ENDHLSL
        }
    }
}
