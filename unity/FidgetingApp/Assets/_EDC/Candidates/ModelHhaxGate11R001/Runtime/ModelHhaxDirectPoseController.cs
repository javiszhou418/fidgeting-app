using System;
using UnityEngine;

namespace FidgetingApp.EDC.Candidates.ModelHhax
{
    /// <summary>
    /// Direct, deterministic pose control for the model-hhax reconstruction.
    /// There is deliberately no Update loop, easing, inertia, detent, haptic,
    /// or slide/rotation coupling. A caller must explicitly set every pose.
    /// </summary>
    public sealed class ModelHhaxDirectPoseController : MonoBehaviour
    {
        public const float MaximumTravelMm = 18.7f;

        [SerializeField] private Transform movingUpper;
        [SerializeField] private Transform rearRotor;
        [SerializeField] private Vector3 slideAxisLocal = Vector3.forward;
        [SerializeField] private Vector3 rotorAxisLocal = Vector3.up;

        private Vector3 upperClosedLocalPosition;
        private Quaternion rotorClosedLocalRotation;
        private bool configured;

        public Transform MovingUpper => movingUpper;
        public Transform RearRotor => rearRotor;
        public float TravelMm { get; private set; }
        public float RotorAngleDegrees { get; private set; }

        public void Configure(Transform upper, Transform rotor, Vector3 slideAxis, Vector3 rotorAxis)
        {
            movingUpper = upper != null ? upper : throw new ArgumentNullException(nameof(upper));
            rearRotor = rotor != null ? rotor : throw new ArgumentNullException(nameof(rotor));
            slideAxisLocal = slideAxis.normalized;
            rotorAxisLocal = rotorAxis.normalized;
            CaptureClosedPose();
            ResetPose();
        }

        private void Awake()
        {
            if (!configured && movingUpper != null && rearRotor != null)
                CaptureClosedPose();
        }

        private void CaptureClosedPose()
        {
            upperClosedLocalPosition = movingUpper.localPosition;
            rotorClosedLocalRotation = rearRotor.localRotation;
            configured = true;
        }

        public void SetTravelMm(float travelMm)
        {
            EnsureConfigured();
            TravelMm = Mathf.Clamp(travelMm, 0f, MaximumTravelMm);
            movingUpper.localPosition = upperClosedLocalPosition
                + slideAxisLocal * (TravelMm * 0.001f);
        }

        public void SetRotorAngleDegrees(float angleDegrees)
        {
            EnsureConfigured();
            RotorAngleDegrees = Mathf.Repeat(angleDegrees, 360f);
            rearRotor.localRotation = rotorClosedLocalRotation
                * Quaternion.AngleAxis(RotorAngleDegrees, rotorAxisLocal);
        }

        public void ResetPose()
        {
            EnsureConfigured();
            TravelMm = 0f;
            RotorAngleDegrees = 0f;
            movingUpper.localPosition = upperClosedLocalPosition;
            rearRotor.localRotation = rotorClosedLocalRotation;
        }

        private void EnsureConfigured()
        {
            if (configured) return;
            if (movingUpper == null || rearRotor == null)
                throw new InvalidOperationException(
                    "model-hhax direct-pose controller is not configured.");
            CaptureClosedPose();
        }
    }

    /// <summary>
    /// Applies the documented charged-dark material response without changing
    /// the imported material assets. Clearing the property blocks restores the
    /// approved daylight material state.
    /// </summary>
    public static class ModelHhaxArtworkEmission
    {
        public static void Set(GameObject candidate, float strength)
        {
            foreach (Renderer renderer in candidate.GetComponentsInChildren<Renderer>(true))
            {
                if (!UsesArtworkMaterial(renderer)) continue;
                MaterialPropertyBlock block = new MaterialPropertyBlock();
                renderer.GetPropertyBlock(block);
                block.SetColor("_EmissionColor", Color.white * strength);
                renderer.SetPropertyBlock(block);
            }
        }

        public static void Clear(GameObject candidate)
        {
            foreach (Renderer renderer in candidate.GetComponentsInChildren<Renderer>(true))
                if (UsesArtworkMaterial(renderer)) renderer.SetPropertyBlock(null);
        }

        private static bool UsesArtworkMaterial(Renderer renderer)
        {
            foreach (Material material in renderer.sharedMaterials)
                if (material != null
                    && (material.name == "MAT_FrontMOP" || material.name == "MAT_BackMOP"))
                    return true;
            return false;
        }
    }
}
