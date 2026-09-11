Shader "FidgetingApp/MagneticSlideTile/NeutralSurfaceR005"
{
    Properties
    {
        _BaseColor("Base Color", Color) = (0.78, 0.77, 0.74, 1)
        _EnvironmentCube("Environment Cube", Cube) = "black" {}
        _Metallic("Metallic", Range(0, 1)) = 1
        _Smoothness("Smoothness", Range(0, 1)) = 0.925
        _ReflectionStrength("Reflection Strength", Range(0, 2)) = 1
        _DiffuseStrength("Diffuse Strength", Range(0, 4)) = 0.08
        _CoatStrength("Clear Coat", Range(0, 1)) = 0.08
        _ResponseBalance("Cross-engine Response Balance", Color) = (1, 1, 1, 1)
    }

    SubShader
    {
        Tags { "RenderPipeline" = "UniversalPipeline" "RenderType" = "Opaque" "Queue" = "Geometry" }
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
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BLENDING
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BOX_PROJECTION

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURECUBE(_EnvironmentCube); SAMPLER(sampler_EnvironmentCube);

            CBUFFER_START(UnityPerMaterial)
                half4 _BaseColor;
                half _Metallic;
                half _Smoothness;
                half _ReflectionStrength;
                half _DiffuseStrength;
                half _CoatStrength;
                half4 _ResponseBalance;
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
                VertexPositionInputs positions = GetVertexPositionInputs(input.positionOS.xyz);
                output.positionCS = positions.positionCS;
                output.positionWS = positions.positionWS;
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float3 normalWS = normalize(input.normalWS);
                float3 viewWS = SafeNormalize(GetWorldSpaceViewDir(input.positionWS));
                float3 reflectionWS = reflect(-viewWS, normalWS);
                float nDotV = saturate(dot(normalWS, viewWS));
                half roughness = saturate(1.0h - _Smoothness);
                half3 reflected = SAMPLE_TEXTURECUBE_LOD(
                    _EnvironmentCube, sampler_EnvironmentCube,
                    reflectionWS, roughness * 6.0h).rgb;
                half3 irradiance = SAMPLE_TEXTURECUBE_LOD(
                    _EnvironmentCube, sampler_EnvironmentCube,
                    normalWS, 6.0h).rgb;
                half3 coatReflected = SAMPLE_TEXTURECUBE_LOD(
                    _EnvironmentCube, sampler_EnvironmentCube,
                    reflectionWS, 0.27h).rgb;
                half3 dielectricF0 = 0.04h.xxx;
                half3 f0 = lerp(dielectricF0, _BaseColor.rgb, _Metallic);
                half3 fresnel = f0 + (1.0h - f0) * pow(1.0 - nDotV, 5.0);
                half3 diffuse = _BaseColor.rgb
                    * irradiance
                    * _DiffuseStrength
                    * (1.0h - _Metallic);
                half3 color = diffuse + reflected * fresnel * _ReflectionStrength;
                half coatFresnel = 0.04h + 0.96h * pow(1.0 - nDotV, 5.0);
                color += coatReflected * coatFresnel * _CoatStrength;
                color *= _ResponseBalance.rgb;
                return half4(max(color, 0.0h), 1.0h);
            }
            ENDHLSL
        }
    }
}
