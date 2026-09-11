using FidgetingApp.Product;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace FidgetingApp.EDC
{
    public enum MagneticSlideLightingVariant
    {
        Build42Baseline,
        BalancedBrighter,
        EverydayD65,
    }

    public readonly struct MagneticSlideLightingValues
    {
        public MagneticSlideLightingValues(
            float postExposureEv,
            float ambientMultiplier,
            float reflectionIntensity,
            float keyIntensity,
            float fillIntensity,
            Color keyColor,
            Color fillColor,
            bool hdr,
            TonemappingMode tonemapping)
        {
            PostExposureEv = postExposureEv;
            AmbientMultiplier = ambientMultiplier;
            ReflectionIntensity = reflectionIntensity;
            KeyIntensity = keyIntensity;
            FillIntensity = fillIntensity;
            KeyColor = keyColor;
            FillColor = fillColor;
            Hdr = hdr;
            Tonemapping = tonemapping;
        }

        public float PostExposureEv { get; }
        public float AmbientMultiplier { get; }
        public float ReflectionIntensity { get; }
        public float KeyIntensity { get; }
        public float FillIntensity { get; }
        public Color KeyColor { get; }
        public Color FillColor { get; }
        public bool Hdr { get; }
        public TonemappingMode Tonemapping { get; }
        public bool PostProcessing => Tonemapping != TonemappingMode.None;
    }

    public static class MagneticSlideShippingLighting
    {
        public const float BaselinePostExposureEv = 0f;
        public const float BaselineAmbientMultiplier = 1f;
        public const float BaselineReflectionIntensity = 0.56f;
        public const float BaselineKeyIntensity = 0.54f;
        public const float BaselineFillIntensity = 0.42f;

        // Gate 12 lighting rev 4 shipped +0.55 EV / 0.68 / 0.54. Post exposure
        // lifts the shared canyon too, so the slide's background read brighter
        // than the other three toys. rev 5 moves to the shared +0.15 EV and
        // puts the missing 0.40 EV (x1.32) back on the model lights only.
        public const float BalancedPostExposureEv =
            SpinnerSharedPresentationGrading.PostExposureEv;
        public const float BalancedAmbientMultiplier = 1.25f;
        public const float BalancedReflectionIntensity = 0.70f;
        public const float Rev4PostExposureEv = 0.55f;
        public const float Rev4KeyIntensity = 0.68f;
        public const float Rev4FillIntensity = 0.54f;
        public const float BalancedKeyIntensity = 0.90f;
        public const float BalancedFillIntensity = 0.71f;

        public const float EverydayPostExposureEv = 2.35f;
        public const float EverydayAmbientMultiplier = 1.80f;
        public const float EverydayReflectionIntensity = 1.00f;
        public const float EverydayKeyIntensity = 1.08f;
        public const float EverydayFillIntensity = 0.86f;

        public static MagneticSlideLightingValues Resolve(
            MagneticSlideLightingVariant variant)
        {
            return variant switch
            {
                MagneticSlideLightingVariant.BalancedBrighter =>
                    new MagneticSlideLightingValues(
                        BalancedPostExposureEv,
                        BalancedAmbientMultiplier,
                        BalancedReflectionIntensity,
                        BalancedKeyIntensity,
                        BalancedFillIntensity,
                        new Color(0.96f, 0.98f, 1f, 1f),
                        new Color(0.90f, 0.95f, 1f, 1f),
                        true,
                        TonemappingMode.Neutral),
                MagneticSlideLightingVariant.EverydayD65 =>
                    new MagneticSlideLightingValues(
                        EverydayPostExposureEv,
                        EverydayAmbientMultiplier,
                        EverydayReflectionIntensity,
                        EverydayKeyIntensity,
                        EverydayFillIntensity,
                        Color.white,
                        new Color(0.96f, 0.98f, 1f, 1f),
                        true,
                        TonemappingMode.ACES),
                _ => new MagneticSlideLightingValues(
                    BaselinePostExposureEv,
                    BaselineAmbientMultiplier,
                    BaselineReflectionIntensity,
                    BaselineKeyIntensity,
                    BaselineFillIntensity,
                    new Color(1f, 0.93f, 0.82f, 1f),
                    new Color(0.52f, 0.68f, 1f, 1f),
                    false,
                    TonemappingMode.None),
            };
        }
    }

    [DisallowMultipleComponent]
    [RequireComponent(typeof(Camera))]
    public sealed class MagneticSlideShippingLightingController : MonoBehaviour
    {
        [SerializeField] private MagneticSlideLightingVariant variant =
            MagneticSlideLightingVariant.BalancedBrighter;
        [SerializeField] private Light keyLight;
        [SerializeField] private Light fillLight;

        private Volume volume;
        private VolumeProfile runtimeProfile;
        private Color baselineSky;
        private Color baselineEquator;
        private Color baselineGround;
        private bool capturedBaseline;

        public MagneticSlideLightingVariant Variant => variant;

        public void Configure(
            Light key,
            Light fill,
            MagneticSlideLightingVariant selectedVariant)
        {
            keyLight = key;
            fillLight = fill;
            variant = selectedVariant;
            CaptureBaseline();
            Apply();
        }

        public void ApplyVariant(MagneticSlideLightingVariant selectedVariant)
        {
            variant = selectedVariant;
            Apply();
        }

        private void OnEnable()
        {
            CaptureBaseline();
            Apply();
        }

        private void LateUpdate()
        {
            Apply();
        }

        private void CaptureBaseline()
        {
            if (capturedBaseline)
                return;
            baselineSky = RenderSettings.ambientSkyColor;
            baselineEquator = RenderSettings.ambientEquatorColor;
            baselineGround = RenderSettings.ambientGroundColor;
            capturedBaseline = true;
        }

        private void Apply()
        {
            CaptureBaseline();
            MagneticSlideLightingValues values =
                MagneticSlideShippingLighting.Resolve(variant);
            Camera camera = GetComponent<Camera>();
            camera.allowHDR = values.Hdr;

            UniversalAdditionalCameraData cameraData =
                camera.GetUniversalAdditionalCameraData();
            if (!Application.isPlaying)
                cameraData.hideFlags = HideFlags.DontSaveInEditor;
            cameraData.renderPostProcessing = values.PostProcessing;

            EnsureVolume();
            volume.enabled = values.PostProcessing;
            if (runtimeProfile.TryGet(out Tonemapping tonemapping))
            {
                tonemapping.mode.Override(values.Tonemapping);
            }
            if (runtimeProfile.TryGet(out ColorAdjustments color))
            {
                color.postExposure.Override(values.PostExposureEv);
                color.contrast.Override(0f);
                color.colorFilter.Override(Color.white);
            }
            if (runtimeProfile.TryGet(out WhiteBalance whiteBalance))
            {
                whiteBalance.temperature.Override(0f);
                whiteBalance.tint.Override(0f);
            }

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor =
                baselineSky * values.AmbientMultiplier;
            RenderSettings.ambientEquatorColor =
                baselineEquator * values.AmbientMultiplier;
            RenderSettings.ambientGroundColor =
                baselineGround * values.AmbientMultiplier;
            RenderSettings.reflectionIntensity = values.ReflectionIntensity;

            if (keyLight != null)
            {
                keyLight.color = values.KeyColor;
                keyLight.intensity = values.KeyIntensity;
            }
            if (fillLight != null)
            {
                fillLight.color = values.FillColor;
                fillLight.intensity = values.FillIntensity;
            }
        }

        private void EnsureVolume()
        {
            // Share the presenter's camera volume so the slide never carries a
            // second exposure the other three scenes do not have.
            volume = SpinnerSharedPresentationGrading.Ensure(GetComponent<Camera>());
            runtimeProfile = volume != null ? volume.profile : null;
        }
    }
}
