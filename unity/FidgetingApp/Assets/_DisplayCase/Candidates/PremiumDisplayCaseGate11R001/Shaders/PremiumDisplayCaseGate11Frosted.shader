Shader "FidgetingApp/Gate11MeshClippedFrosted"
{
    Properties
    {
        _BaseColor("Frosted Tint", Color) = (0.12, 0.15, 0.18, 1)
        _RimColor("Neutral Rim", Color) = (0.82, 0.88, 0.94, 1)
        _Opacity("Base Opacity", Range(0, 1)) = 0.03
        _RimStrength("Rim Strength", Range(0, 1)) = 0.18
        _RimPower("Rim Tightness", Range(0.5, 8)) = 3.8
        _SpecularStrength("Specular Strength", Range(0, 1)) = 0.22
        _SheenCenter("Mesh Sheen Center", Range(-1, 1)) = 0.12
        _SheenWidth("Mesh Sheen Width", Range(0.01, 0.5)) = 0.08
        _SheenStrength("Mesh Sheen Strength", Range(0, 1)) = 0.16
    }

    SubShader
    {
        Tags
        {
            "Queue"="Transparent"
            "RenderType"="Transparent"
            "RenderPipeline"="UniversalPipeline"
        }
        Blend SrcAlpha OneMinusSrcAlpha
        ZWrite Off
        Cull Off

        Pass
        {
            Name "Gate11MeshClippedFrosted"
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
                half _SheenCenter;
                half _SheenWidth;
                half _SheenStrength;
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
                VertexPositionInputs positions =
                    GetVertexPositionInputs(input.positionOS.xyz);
                VertexNormalInputs normals = GetVertexNormalInputs(input.normalOS);
                output.positionCS = positions.positionCS;
                output.positionWS = positions.positionWS;
                output.normalWS = normals.normalWS;
                output.positionOS = input.positionOS.xyz;
                return output;
            }

            half Hash(float3 value)
            {
                return frac(sin(dot(value, float3(12.9898, 78.233, 37.719)))
                    * 43758.5453);
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half3 normalWS = normalize(input.normalWS);
                half3 viewDirection = SafeNormalize(
                    GetWorldSpaceViewDir(input.positionWS));
                half fresnel = pow(
                    1.0h - saturate(abs(dot(normalWS, viewDirection))),
                    _RimPower);

                half3 virtualKey = normalize(half3(-0.34h, 0.72h, -0.60h));
                half diffuse = 0.12h
                    + saturate(dot(normalWS, virtualKey)) * 0.10h;
                half specular = pow(
                    saturate(dot(reflect(-viewDirection, normalWS), virtualKey)),
                    72.0h) * _SpecularStrength;

                half coordinate = input.positionOS.y * 3.2h
                    + input.positionOS.x * 1.7h;
                half sheenDistance = abs(coordinate - _SheenCenter);
                half sheen = 1.0h - smoothstep(
                    _SheenWidth * 0.35h,
                    _SheenWidth,
                    sheenDistance);
                sheen *= _SheenStrength;

                half grain = (Hash(input.positionOS * 1900.0h) - 0.5h) * 0.018h;
                half3 color = _BaseColor.rgb * max(0.02h, diffuse + grain);
                color += _RimColor.rgb
                    * (fresnel * _RimStrength + specular + sheen);
                half alpha = saturate(
                    _Opacity
                    + fresnel * _RimStrength * 0.40h
                    + specular * 0.10h
                    + sheen * 0.16h);
                return half4(color, alpha);
            }
            ENDHLSL
        }
    }
}
