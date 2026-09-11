Shader "FidgetingApp/MagneticSlideTile/Silver"
{
    Properties
    {
        _BaseColor("Silver Conductor Tint", Color) = (0.78, 0.77, 0.74, 1)
        _Smoothness("Smoothness", Range(0, 1)) = 0.925
        _ReflectionStrength("Reflection Strength", Range(0, 2)) = 1.0
        _DirectSpecularStrength("Direct Specular", Range(0, 2)) = 0.35
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
            Cull Off

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.0
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile _ _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BLENDING
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BOX_PROJECTION

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _BaseColor;
                half _Smoothness;
                half _ReflectionStrength;
                half _DirectSpecularStrength;
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
                VertexPositionInputs positionInputs =
                    GetVertexPositionInputs(input.positionOS.xyz);
                output.positionCS = positionInputs.positionCS;
                output.positionWS = positionInputs.positionWS;
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float3 normalWS = normalize(input.normalWS);
                float3 viewWS = SafeNormalize(
                    GetWorldSpaceViewDir(input.positionWS));
                float3 reflectionWS = reflect(-viewWS, normalWS);
                float nDotV = saturate(dot(normalWS, viewWS));
                float perceptualRoughness = saturate(1.0 - _Smoothness);

                half3 f0 = _BaseColor.rgb;
                half3 fresnel = f0 + (1.0h - f0)
                    * pow(1.0 - nDotV, 5.0);
                half3 environment = GlossyEnvironmentReflection(
                    reflectionWS,
                    perceptualRoughness,
                    1.0h);

                Light mainLight = GetMainLight(
                    TransformWorldToShadowCoord(input.positionWS));
                float3 halfVector = SafeNormalize(
                    mainLight.direction + viewWS);
                float nDotL = saturate(dot(normalWS, mainLight.direction));
                float nDotH = saturate(dot(normalWS, halfVector));
                float specPower = lerp(24.0, 256.0, _Smoothness);
                half directSpecular = pow(nDotH, specPower)
                    * nDotL
                    * mainLight.distanceAttenuation
                    * mainLight.shadowAttenuation;

                half3 color = environment
                    * fresnel
                    * _ReflectionStrength;
                color += mainLight.color
                    * fresnel
                    * directSpecular
                    * _DirectSpecularStrength;
                half broadSoftbox = pow(nDotH, 8.0h)
                    * nDotL
                    * mainLight.distanceAttenuation
                    * mainLight.shadowAttenuation;
                color += mainLight.color
                    * fresnel
                    * broadSoftbox
                    * 0.72h;
                color += SampleSH(normalWS) * _BaseColor.rgb * 0.025h;
                return half4(max(color, 0.0h), 1.0h);
            }
            ENDHLSL
        }

        UsePass "Universal Render Pipeline/Lit/ShadowCaster"
        UsePass "Universal Render Pipeline/Lit/DepthOnly"
    }
}
