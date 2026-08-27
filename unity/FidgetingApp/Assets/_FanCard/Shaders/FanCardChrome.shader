Shader "FidgetingApp/FanCardChrome"
{
    Properties
    {
        _BaseColor("Chrome Tint", Color) = (0.93, 0.95, 0.98, 1)
        _Smoothness("Smoothness", Range(0, 1)) = 0.78
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
            Name "UniversalForward"
            Tags { "LightMode" = "UniversalForward" }
            ZWrite On
            ZTest LEqual
            Cull Back

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.0

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _BaseColor;
                half _Smoothness;
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
                half3 normalWS : TEXCOORD1;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionWS = TransformObjectToWorld(input.positionOS.xyz);
                output.positionCS = TransformWorldToHClip(output.positionWS);
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float3 normalWS = normalize(input.normalWS);
                float3 viewWS = SafeNormalize(GetWorldSpaceViewDir(input.positionWS));
                float3 reflectionWS = reflect(-viewWS, normalWS);
                Light mainLight = GetMainLight();
                float3 halfVector = SafeNormalize(mainLight.direction + viewWS);
                float nDotH = saturate(dot(normalWS, halfVector));
                float spec = pow(nDotH, lerp(24.0, 72.0, _Smoothness));

                float3 panelForward = normalize(float3(-0.34, 0.82, -0.46));
                float3 panelRight = normalize(cross(float3(0.0, 1.0, 0.0), panelForward));
                float3 panelUp = normalize(cross(panelForward, panelRight));
                float panelFacing = saturate(dot(reflectionWS, panelForward));
                float panelX = 1.0 - smoothstep(
                    0.38,
                    0.72,
                    abs(dot(reflectionWS, panelRight)));
                float panelY = 1.0 - smoothstep(
                    0.28,
                    0.62,
                    abs(dot(reflectionWS, panelUp)));
                float softbox = smoothstep(0.34, 0.78, panelFacing)
                    * panelX
                    * panelY;

                float3 stripForward = normalize(float3(0.70, 0.18, 0.69));
                float coolStrip = smoothstep(
                    0.78,
                    0.96,
                    saturate(dot(reflectionWS, stripForward)));
                float vertical = saturate(reflectionWS.y * 0.68 + 0.34);
                float fresnel = pow(
                    1.0 - saturate(dot(normalWS, viewWS)),
                    lerp(3.2, 5.2, _Smoothness));

                half3 chrome = lerp(
                    half3(0.045, 0.050, 0.056),
                    half3(0.22, 0.24, 0.27) * _BaseColor.rgb,
                    vertical);
                chrome += half3(0.92, 0.90, 0.86) * softbox * 0.42;
                chrome += half3(0.28, 0.40, 0.52) * coolStrip * 0.10;
                chrome += mainLight.color * spec * 0.18;
                chrome += fresnel * half3(0.10, 0.11, 0.13);
                return half4(chrome, 1.0);
            }
            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }
            ZWrite On
            ZTest LEqual
            ColorMask 0
            Cull Back

            HLSLPROGRAM
            #pragma vertex ShadowVert
            #pragma fragment ShadowFrag
            #pragma target 3.0
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
            };

            Varyings ShadowVert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                return output;
            }

            half4 ShadowFrag(Varyings input) : SV_Target
            {
                return 0;
            }
            ENDHLSL
        }
    }
}
