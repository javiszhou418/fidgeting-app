#ifndef FIDGETING_FAN_CARD_MOVING_LIGHTS_INCLUDED
#define FIDGETING_FAN_CARD_MOVING_LIGHTS_INCLUDED

#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

float4 _FanCardViewReflectionTilt;

float3 FanCardRotateReflection(float3 reflectionWS)
{
    float yawSine;
    float yawCosine;
    sincos(_FanCardViewReflectionTilt.x, yawSine, yawCosine);
    float3 yawed = float3(
        reflectionWS.x * yawCosine + reflectionWS.z * yawSine,
        reflectionWS.y,
        -reflectionWS.x * yawSine + reflectionWS.z * yawCosine);
    float pitchSine;
    float pitchCosine;
    sincos(_FanCardViewReflectionTilt.y, pitchSine, pitchCosine);
    return SafeNormalize(float3(
        yawed.x,
        yawed.y * pitchCosine - yawed.z * pitchSine,
        yawed.y * pitchSine + yawed.z * pitchCosine));
}

// Gyro-tracked fill / bounce / view-highlight must move specular energy.
// They must not replace the authored metal color.
half3 FanCardEvaluateMovingLight(
    Light light,
    half3 albedo,
    float3 normalWS,
    float3 viewWS,
    half metallic,
    half smoothness)
{
    half nDotL = saturate(dot(normalWS, light.direction));
    float3 halfVector = SafeNormalize(light.direction + viewWS);
    float nDotH = saturate(dot(normalWS, halfVector));
    half attenuation = light.distanceAttenuation * light.shadowAttenuation;
    half spec = pow(nDotH, lerp(8.0, 48.0, smoothness));
    half3 diffuse = albedo
        * light.color
        * nDotL
        * attenuation
        * lerp(1.0, 0.10, metallic);
    half3 specular = light.color
        * spec
        * attenuation
        * lerp(0.04, 0.55, metallic);
    return diffuse + specular;
}

half3 FanCardSampleAdditionalLights(
    float3 positionWS,
    float4 positionCS,
    half3 albedo,
    float3 normalWS,
    float3 viewWS,
    half metallic,
    half smoothness)
{
    InputData inputData = (InputData)0;
    inputData.positionWS = positionWS;
    inputData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(positionCS);
    half3 lighting = 0;
#if USE_CLUSTER_LIGHT_LOOP
    UNITY_LOOP for (
        uint lightIndex = 0;
        lightIndex < min(URP_FP_DIRECTIONAL_LIGHTS_COUNT, MAX_VISIBLE_LIGHTS);
        lightIndex++)
    {
        lighting += FanCardEvaluateMovingLight(
            GetAdditionalLight(lightIndex, positionWS),
            albedo,
            normalWS,
            viewWS,
            metallic,
            smoothness);
    }
#endif
    uint pixelLightCount = GetAdditionalLightsCount();
    LIGHT_LOOP_BEGIN(pixelLightCount)
        lighting += FanCardEvaluateMovingLight(
            GetAdditionalLight(lightIndex, positionWS),
            albedo,
            normalWS,
            viewWS,
            metallic,
            smoothness);
    LIGHT_LOOP_END
    return lighting;
}

#endif
