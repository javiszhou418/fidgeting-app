Shader "FidgetingApp/PremiumAcrylicLiquidGlass"
{
    Properties
    {
        _BaseColor("Neutral Acrylic Tint", Color) = (0.72, 0.80, 0.84, 1)
        _RimColor("Edge Light", Color) = (0.92, 0.97, 1.0, 1)
        _Opacity("Base Opacity", Range(0, 1)) = 0.11
        _RimStrength("Rim Strength", Range(0, 2)) = 0.82
        _RimPower("Rim Tightness", Range(0.5, 8)) = 3.6
        _SpecularStrength("Specular Strength", Range(0, 3)) = 1.35
        _RevealVisibility("Reveal Visibility", Range(0, 1)) = 1
        _RevealSweep("Reveal Sweep", Range(0, 1)) = 1
        _ParallaxTilt("Parallax Tilt", Vector) = (0, 0, 0, 0)
    }

    SubShader
    {
        Tags
        {
            "Queue"="Transparent+20"
            "RenderType"="Transparent"
            "RenderPipeline"="UniversalPipeline"
        }
        LOD 200
        Blend SrcAlpha OneMinusSrcAlpha
        ZWrite Off
        Cull Off

        Pass
        {
            Name "LiquidGlassForward"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.0

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _BaseColor;
                half4 _RimColor;
                half _Opacity;
                half _RimStrength;
                half _RimPower;
                half _SpecularStrength;
                half _RevealVisibility;
                half _RevealSweep;
                float4 _ParallaxTilt;
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
                float2 glassCoordinate : TEXCOORD2;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                VertexPositionInputs positions = GetVertexPositionInputs(input.positionOS.xyz);
                VertexNormalInputs normals = GetVertexNormalInputs(input.normalOS);
                output.positionCS = positions.positionCS;
                output.positionWS = positions.positionWS;
                output.normalWS = normals.normalWS;
                output.glassCoordinate = input.positionOS.xy
                    + _ParallaxTilt.xy * float2(0.018, 0.012);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half3 normalWS = normalize(input.normalWS);
                half3 viewDirection = SafeNormalize(
                    GetWorldSpaceViewDir(input.positionWS));
                half fresnel = pow(
                    1.0h - saturate(abs(dot(normalWS, viewDirection))),
                    _RimPower);

                half3 virtualKey = normalize(half3(-0.42h, 0.68h, -0.60h));
                half3 reflected = reflect(-viewDirection, normalWS);
                half tightSpecular = pow(
                    saturate(dot(reflected, virtualKey)),
                    84.0h) * _SpecularStrength;
                half broadSpecular = pow(
                    saturate(dot(reflected, normalize(half3(0.58h, 0.32h, -0.74h)))),
                    16.0h) * 0.22h;

                half sweepCoordinate = input.glassCoordinate.y * 4.2h
                    + input.glassCoordinate.x * 2.1h;
                half sweepCenter = lerp(-0.72h, 0.72h, _RevealSweep);
                half revealSweep = exp2(
                    -110.0h * (sweepCoordinate - sweepCenter)
                    * (sweepCoordinate - sweepCenter));
                revealSweep *= smoothstep(0.03h, 0.35h, _RevealVisibility);

                half3 color = _BaseColor.rgb * (0.16h + fresnel * 0.22h);
                color += _RimColor.rgb * fresnel * _RimStrength;
                color += _RimColor.rgb
                    * (tightSpecular + broadSpecular + revealSweep * 0.82h);
                half alpha = (_Opacity
                    + fresnel * 0.24h
                    + tightSpecular * 0.08h
                    + revealSweep * 0.12h)
                    * saturate(_RevealVisibility);
                return half4(color, saturate(alpha));
            }
            ENDHLSL
        }
    }
}
