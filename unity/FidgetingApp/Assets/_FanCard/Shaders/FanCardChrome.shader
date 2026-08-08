Shader "FidgetingApp/FanCardChrome"
{
    Properties
    {
        _BaseColor("Chrome Tint", Color) = (0.93, 0.95, 0.98, 1)
        _Smoothness("Smoothness", Range(0, 1)) = 0.92
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

                // A fixed studio softbox is encoded procedurally so the small
                // axis ball keeps a readable chrome value on mobile without a
                // high-resolution reflection probe. The lower hemisphere stays
                // dark while the upper-left panel produces one broad highlight.
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
                    half3(0.035, 0.042, 0.050),
                    half3(0.28, 0.31, 0.35) * _BaseColor.rgb,
                    vertical);
                chrome += half3(1.0, 0.97, 0.92) * softbox * 0.94;
                chrome += half3(0.30, 0.48, 0.68) * coolStrip * 0.20;
                chrome += fresnel * half3(0.18, 0.20, 0.23);
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
