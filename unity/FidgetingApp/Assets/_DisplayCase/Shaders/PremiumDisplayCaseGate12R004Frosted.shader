Shader "FidgetingApp/Gate12R004MeshClippedFrosted"
{
    Properties
    {
        _BaseColor("Frosted Tint", Color) = (0.12, 0.15, 0.18, 1)
        _RimColor("Neutral Rim", Color) = (0.96, 0.94, 0.90, 1)
        _Opacity("Base Opacity", Range(0, 1)) = 0.03
        _RimStrength("Rim Strength", Range(0, 1)) = 0.18
        _RimPower("Rim Tightness", Range(0.5, 8)) = 3.8
        _SpecularStrength("Specular Strength", Range(0, 1)) = 0.22
        _LightRevealProgress("Arrival Rim Progress", Range(0, 1)) = 0
        _LightRevealWidth("Arrival Rim Width", Range(0.01, 0.5)) = 0.18
        _LightRevealStrength("Arrival Rim Strength", Range(0, 1)) = 0
        _RotationRimProgress("Object-bound Rotation Rim Progress", Range(0, 1)) = 0
        _RotationRimStrength("Object-bound Rotation Rim Strength", Range(0, 1)) = 0
        _SheenCenter("Mesh Sheen Center", Range(-1, 1)) = -0.62
        _SheenWidth("Mesh Sheen Width", Range(0.01, 0.5)) = 0.16
        _SheenStrength("Mesh Sheen Strength", Range(0, 1)) = 0
        _SheenFalloff("Mesh Sheen Falloff", Range(0.05, 0.95)) = 0.30
        _SheenObjectCenter("Mesh Sheen Object Center", Vector) = (0, 0, 0, 0)
        _SheenObjectInvSize("Mesh Sheen Object Inverse Size", Vector) = (1, 1, 1, 0)
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
            Name "Gate12R004MeshClippedFrosted"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.0

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/MakeItShineCc0Masks.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _BaseColor;
                half4 _RimColor;
                half _Opacity;
                half _RimStrength;
                half _RimPower;
                half _SpecularStrength;
                half _LightRevealProgress;
                half _LightRevealWidth;
                half _LightRevealStrength;
                half _RotationRimProgress;
                half _RotationRimStrength;
                half _SheenCenter;
                half _SheenWidth;
                half _SheenStrength;
                half _SheenFalloff;
                float4 _SheenObjectCenter;
                float4 _SheenObjectInvSize;
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

                float3 normalizedObject = (input.positionOS
                    - _SheenObjectCenter.xyz)
                    * _SheenObjectInvSize.xyz;
                half coordinate = normalizedObject.y * 0.78h
                    + normalizedObject.x * 0.46h;
                half rotationBand = FidgetingCc0DiagonalBand(
                    coordinate,
                    _RotationRimProgress,
                    0.18h,
                    0.30h);
                half arrivalRim = pow(
                    1.0h - saturate(abs(dot(normalWS, viewDirection))),
                    max(1.2h, _RimPower * 0.58h))
                    * _LightRevealStrength;
                half rotationRim = rotationBand
                    * (0.42h + fresnel * 0.58h)
                    * _RotationRimStrength;
                half sheenDistance = abs(coordinate - _SheenCenter);
                half sheen = 1.0h - smoothstep(
                    _SheenWidth * _SheenFalloff,
                    _SheenWidth,
                    sheenDistance);
                sheen *= _SheenStrength;

                half grain = (Hash(input.positionOS * 1900.0h) - 0.5h) * 0.018h;
                half3 color = _BaseColor.rgb * max(0.02h, diffuse + grain);
                color += _RimColor.rgb
                    * (fresnel * _RimStrength
                        + specular
                        + arrivalRim * 1.80h
                        + rotationRim * 1.55h
                        + sheen * 1.85h);
                color = min(color, 0.98h);
                half alpha = saturate(
                    _Opacity
                    + fresnel * _RimStrength * 0.40h
                    + specular * 0.10h
                    + arrivalRim * 0.62h
                    + rotationRim * 0.48h
                    + sheen * 0.68h);
                return half4(color, alpha);
            }
            ENDHLSL
        }
    }
}
