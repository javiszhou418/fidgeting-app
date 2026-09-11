using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace FidgetingApp.Product
{
    /// <summary>
    /// One camera grading for every shipping product scene: Neutral tonemapping
    /// plus a single subtle exposure lift. Post exposure brightens the whole
    /// frame, backdrop included, so the four toys can only share one canyon if
    /// they share one value. The slide tile's own +0.55 EV was the reason its
    /// background read brighter than the other three (user 2026-09-09).
    /// </summary>
    public static class SpinnerSharedPresentationGrading
    {
        public const string VolumeProfileName = "SharedPresentationGrading_Runtime";
        public const float VolumePriority = 50f;
        public const float PostExposureEv = 0.15f;
        public const TonemappingMode Tonemapping = TonemappingMode.Neutral;

        /// <summary>Linear brightness factor of <see cref="PostExposureEv"/>.</summary>
        public static float PostExposureLinearGain => Mathf.Pow(2f, PostExposureEv);

        public static Volume Ensure(Camera camera)
        {
            if (camera == null)
            {
                return null;
            }

            camera.allowHDR = true;
            UniversalAdditionalCameraData cameraData =
                camera.GetUniversalAdditionalCameraData();
            if (cameraData != null)
            {
                if (!Application.isPlaying)
                {
                    cameraData.hideFlags = HideFlags.DontSaveInEditor;
                }
                cameraData.renderPostProcessing = true;
            }

            Volume volume = camera.GetComponent<Volume>();
            if (volume == null)
            {
                volume = camera.gameObject.AddComponent<Volume>();
            }
            if (!Application.isPlaying)
            {
                volume.hideFlags = HideFlags.DontSaveInEditor;
            }
            volume.isGlobal = true;
            volume.priority = VolumePriority;
            volume.weight = 1f;
            volume.enabled = true;

            VolumeProfile profile = volume.profile;
            if (profile == null || profile.name != VolumeProfileName)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>();
                profile.name = VolumeProfileName;
                profile.hideFlags = HideFlags.HideAndDontSave;
                volume.profile = profile;
            }

            if (!profile.TryGet(out Tonemapping tonemapping))
            {
                tonemapping = profile.Add<Tonemapping>(true);
            }
            tonemapping.active = true;
            tonemapping.mode.Override(Tonemapping);

            if (!profile.TryGet(out ColorAdjustments color))
            {
                color = profile.Add<ColorAdjustments>(true);
            }
            color.active = true;
            color.postExposure.Override(PostExposureEv);
            color.contrast.Override(0f);
            color.colorFilter.Override(Color.white);

            if (!profile.TryGet(out WhiteBalance whiteBalance))
            {
                whiteBalance = profile.Add<WhiteBalance>(true);
            }
            whiteBalance.active = true;
            whiteBalance.temperature.Override(0f);
            whiteBalance.tint.Override(0f);
            return volume;
        }

        public static bool TryReadExposure(Camera camera, out float postExposureEv, out TonemappingMode mode)
        {
            postExposureEv = 0f;
            mode = TonemappingMode.None;
            Volume volume = camera != null ? camera.GetComponent<Volume>() : null;
            VolumeProfile profile = volume != null ? volume.profile : null;
            if (profile == null)
            {
                return false;
            }
            if (profile.TryGet(out ColorAdjustments color))
            {
                postExposureEv = color.postExposure.value;
            }
            if (profile.TryGet(out Tonemapping tonemapping))
            {
                mode = tonemapping.mode.value;
            }
            return true;
        }
    }
}
