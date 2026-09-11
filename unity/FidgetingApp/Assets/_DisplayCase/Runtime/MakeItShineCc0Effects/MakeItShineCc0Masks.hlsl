#ifndef FIDGETING_MAKE_IT_SHINE_CC0_MASKS_INCLUDED
#define FIDGETING_MAKE_IT_SHINE_CC0_MASKS_INCLUDED

half FidgetingCc0SphereMask(
    float3 coordinates,
    float3 center,
    half radius,
    half hardness)
{
    half safeSoftness = max(1.0h - saturate(hardness), 0.0001h);
    return 1.0h - saturate(
        (distance(coordinates, center) - radius) / safeSoftness);
}

half FidgetingCc0RevealThreshold(half mask, half reveal)
{
    return saturate(mask - (1.0h - saturate(reveal)));
}

half FidgetingCc0DiagonalBand(
    half coordinate,
    half progress,
    half width,
    half falloff)
{
    half center = lerp(-0.62h, 0.62h, saturate(progress));
    half distanceFromCenter = abs(coordinate - center);
    half band = 1.0h - smoothstep(
        width * saturate(falloff),
        max(width, 0.0001h),
        distanceFromCenter);
    return band;
}

half FidgetingCc0ProgressiveDiagonalBand(
    half coordinate,
    half progress,
    half width,
    half falloff)
{
    return FidgetingCc0RevealThreshold(
        FidgetingCc0DiagonalBand(
            coordinate,
            progress,
            width,
            falloff),
        progress);
}

#endif
