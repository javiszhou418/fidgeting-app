using System;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.DisplayCase
{
    [Serializable]
    public struct PremiumDisplayCaseGachaLightSpec
    {
        public string name;
        public LightType type;
        public Vector3 position;
        public Vector3 forward;
        public Color colorLinear;
        public float intensity;
        public float range;
        public float spotAngle;
        public float innerSpotAngle;
        public LightShadows shadows;
    }

    public sealed class PremiumDisplayCaseGachaLightingProfile : ScriptableObject
    {
        [SerializeField] private Color ambientLinear;
        [SerializeField] private float reflectionIntensity = 1f;
        [SerializeField] private Cubemap reflectionCubemap;
        [SerializeField] private VolumeProfile beautyVolume;
        [SerializeField] private PremiumDisplayCaseGachaLightSpec[] lights =
            Array.Empty<PremiumDisplayCaseGachaLightSpec>();

        public Color AmbientLinear => ambientLinear;
        public float ReflectionIntensity => reflectionIntensity;
        public Cubemap ReflectionCubemap => reflectionCubemap;
        public VolumeProfile BeautyVolume => beautyVolume;
        public PremiumDisplayCaseGachaLightSpec[] Lights => lights;

        public void Configure(
            Color authoredAmbientLinear,
            float authoredReflectionIntensity,
            Cubemap authoredReflectionCubemap,
            VolumeProfile authoredBeautyVolume,
            PremiumDisplayCaseGachaLightSpec[] authoredLights)
        {
            if (authoredReflectionCubemap == null)
            {
                throw new ArgumentNullException(nameof(authoredReflectionCubemap));
            }
            if (authoredBeautyVolume == null)
            {
                throw new ArgumentNullException(nameof(authoredBeautyVolume));
            }
            if (authoredLights == null || authoredLights.Length != 4)
            {
                throw new ArgumentException(
                    "The approved Gate 09 rig requires exactly four realtime lights.",
                    nameof(authoredLights));
            }

            ambientLinear = authoredAmbientLinear;
            reflectionIntensity = Mathf.Max(0f, authoredReflectionIntensity);
            reflectionCubemap = authoredReflectionCubemap;
            beautyVolume = authoredBeautyVolume;
            lights = (PremiumDisplayCaseGachaLightSpec[])authoredLights.Clone();
        }
    }

    public static class PremiumDisplayCaseGachaLightingContract
    {
        public const string ResourcesPath =
            "Gacha/PremiumDisplayCaseGate12R011Lighting";
        public const int RealtimeLightCount = 4;
        public const int MainDirectionalLightCount = 1;
        public const int AdditionalRealtimeLightCount = 3;
        public const float VolumePriority = 100f;

        public static readonly Color AmbientLinear =
            new Color(0f, 0.00016693985f, 0.00050081955f, 1f);

        public static PremiumDisplayCaseGachaLightSpec[] CreateLightSpecs()
        {
            return new[]
            {
                Directional(
                    "LGT_PDC_SOFT_KEY",
                    new Vector3(-0.07226928f, 0.17165092f, -0.17335063f),
                    new Vector3(0.28173003f, -0.66915327f, 0.68764967f),
                    new Color(1f, 0.93837410f, 0.88348991f, 1f),
                    1.86804699f,
                    LightShadows.Soft),
                Directional(
                    "LGT_PDC_FRONT_FILL",
                    new Vector3(-0.03118106f, 0.20404692f, 0.07013907f),
                    new Vector3(0.14366117f, -0.94010848f, -0.30912372f),
                    new Color(1f, 0.96528697f, 0.92878336f, 1f),
                    0.34126285f,
                    LightShadows.None),
                Spot(
                    "LGT_PDC_EDGE_L_CYAN",
                    new Vector3(-0.14586850f, 0.01608011f, -0.01475774f),
                    new Vector3(0.98674458f, -0.10877568f, 0.12042856f),
                    new Color(0.07818742f, 0.64447969f, 1f, 1f),
                    0.01664598f),
                Spot(
                    "LGT_PDC_EDGE_R_MAGENTA",
                    new Vector3(0.10871321f, -0.01575272f, 0.10088272f),
                    new Vector3(-0.73903412f, 0.10708719f, -0.66510218f),
                    new Color(1f, 0.11443537f, 0.67244315f, 1f),
                    0.01536552f)
            };
        }

        private static PremiumDisplayCaseGachaLightSpec Directional(
            string name,
            Vector3 position,
            Vector3 forward,
            Color color,
            float intensity,
            LightShadows shadows)
        {
            return new PremiumDisplayCaseGachaLightSpec
            {
                name = name,
                type = LightType.Directional,
                position = position,
                forward = forward,
                colorLinear = color,
                intensity = intensity,
                range = 0f,
                spotAngle = 0f,
                innerSpotAngle = 0f,
                shadows = shadows
            };
        }

        private static PremiumDisplayCaseGachaLightSpec Spot(
            string name,
            Vector3 position,
            Vector3 forward,
            Color color,
            float intensity)
        {
            return new PremiumDisplayCaseGachaLightSpec
            {
                name = name,
                type = LightType.Spot,
                position = position,
                forward = forward,
                colorLinear = color,
                intensity = intensity,
                range = 0.8f,
                spotAngle = 120f,
                innerSpotAngle = 60f,
                shadows = LightShadows.None
            };
        }
    }
}
