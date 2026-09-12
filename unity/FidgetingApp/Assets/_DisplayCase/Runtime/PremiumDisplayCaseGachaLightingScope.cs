using System;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.DisplayCase
{
    public static class PremiumDisplayCaseGachaLightingInstaller
    {
        public static PremiumDisplayCaseGachaLightingScope Install(Transform parent)
        {
            if (parent == null)
            {
                throw new ArgumentNullException(nameof(parent));
            }
            PremiumDisplayCaseGachaLightingProfile profile =
                Resources.Load<PremiumDisplayCaseGachaLightingProfile>(
                    PremiumDisplayCaseGachaLightingContract.ResourcesPath);
            if (profile == null)
            {
                throw new MissingReferenceException(
                    "Missing Resources/"
                    + PremiumDisplayCaseGachaLightingContract.ResourcesPath
                    + ".asset.");
            }

            var scopeObject = new GameObject("Gate12R011LightingScope");
            scopeObject.transform.SetParent(parent, false);
            var scope =
                scopeObject.AddComponent<PremiumDisplayCaseGachaLightingScope>();
            scope.Configure(profile);
            return scope;
        }
    }

    [DisallowMultipleComponent]
    public sealed class PremiumDisplayCaseGachaLightingScope : MonoBehaviour
    {
        private AmbientMode previousAmbientMode;
        private Color previousAmbientLight;
        private float previousAmbientIntensity;
        private DefaultReflectionMode previousReflectionMode;
        private Texture previousReflectionTexture;
        private float previousReflectionIntensity;
        private int previousReflectionBounces;
        private bool previousFog;
        private bool configured;

        public PremiumDisplayCaseGachaLightingProfile Profile { get; private set; }
        public int RealtimeLightCount { get; private set; }
        public bool IsWired =>
            configured
            && Profile != null
            && Profile.ReflectionCubemap != null
            && Profile.BeautyVolume != null
            && RealtimeLightCount
                == PremiumDisplayCaseGachaLightingContract.RealtimeLightCount;

        public void Configure(PremiumDisplayCaseGachaLightingProfile profile)
        {
            if (configured)
            {
                throw new InvalidOperationException(
                    "The Gacha lighting scope is already configured.");
            }
            if (profile == null)
            {
                throw new ArgumentNullException(nameof(profile));
            }

            Profile = profile;
            CaptureRenderSettings();
            ApplyRenderSettings(profile);
            CreateLights(profile.Lights);
            Volume volume = gameObject.AddComponent<Volume>();
            volume.isGlobal = true;
            volume.priority =
                PremiumDisplayCaseGachaLightingContract.VolumePriority;
            volume.sharedProfile = profile.BeautyVolume;
            configured = true;
        }

        private void CaptureRenderSettings()
        {
            previousAmbientMode = RenderSettings.ambientMode;
            previousAmbientLight = RenderSettings.ambientLight;
            previousAmbientIntensity = RenderSettings.ambientIntensity;
            previousReflectionMode = RenderSettings.defaultReflectionMode;
            previousReflectionTexture = RenderSettings.customReflectionTexture;
            previousReflectionIntensity = RenderSettings.reflectionIntensity;
            previousReflectionBounces = RenderSettings.reflectionBounces;
            previousFog = RenderSettings.fog;
        }

        private static void ApplyRenderSettings(
            PremiumDisplayCaseGachaLightingProfile profile)
        {
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = profile.AmbientLinear;
            RenderSettings.ambientIntensity = 1f;
            RenderSettings.defaultReflectionMode =
                DefaultReflectionMode.Custom;
            RenderSettings.customReflectionTexture =
                profile.ReflectionCubemap;
            RenderSettings.reflectionIntensity =
                profile.ReflectionIntensity;
            RenderSettings.reflectionBounces = 1;
            RenderSettings.fog = false;
        }

        private void CreateLights(PremiumDisplayCaseGachaLightSpec[] specs)
        {
            RealtimeLightCount = 0;
            for (int index = 0; index < specs.Length; index++)
            {
                PremiumDisplayCaseGachaLightSpec spec = specs[index];
                var lightObject = new GameObject(spec.name);
                lightObject.transform.SetParent(transform, false);
                lightObject.transform.localPosition = spec.position;
                lightObject.transform.localRotation = Quaternion.LookRotation(
                    spec.forward.normalized,
                    Vector3.up);
                Light light = lightObject.AddComponent<Light>();
                light.type = spec.type;
                light.color = spec.colorLinear;
                light.intensity = spec.intensity;
                light.shadows = spec.shadows;
                light.shadowStrength = 0.6f;
                light.shadowBias = 0.002f;
                light.shadowNormalBias = 0.2f;
                if (spec.type == LightType.Spot)
                {
                    light.range = spec.range;
                    light.spotAngle = spec.spotAngle;
                    light.innerSpotAngle = spec.innerSpotAngle;
                }
                RealtimeLightCount++;
            }
        }

        public void Restore()
        {
            if (!configured)
            {
                return;
            }
            RenderSettings.ambientLight = previousAmbientLight;
            RenderSettings.ambientIntensity = previousAmbientIntensity;
            RenderSettings.ambientMode = previousAmbientMode;
            RenderSettings.customReflectionTexture =
                previousReflectionTexture;
            RenderSettings.reflectionIntensity = previousReflectionIntensity;
            RenderSettings.reflectionBounces = previousReflectionBounces;
            RenderSettings.defaultReflectionMode = previousReflectionMode;
            RenderSettings.fog = previousFog;
            configured = false;
        }

        private void OnDisable()
        {
            Restore();
        }

        private void OnDestroy()
        {
            Restore();
        }
    }
}
