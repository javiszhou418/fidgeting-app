using System;
using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    public readonly struct PremiumDisplayCaseExplodedSample
    {
        public PremiumDisplayCaseExplodedSample(float visibility, Vector3 offset)
        {
            Visibility = visibility;
            Offset = offset;
        }

        public float Visibility { get; }
        public Vector3 Offset { get; }
    }

    public static class PremiumDisplayCaseExplodedLayout
    {
        public const float AssemblyDurationSeconds = 1.35f;

        public static PremiumDisplayCaseExplodedSample Evaluate(
            int layerIndex,
            int layerCount,
            float explodedProgress,
            Vector3 authoredOffset)
        {
            int safeCount = Mathf.Max(1, layerCount);
            int safeIndex = Mathf.Clamp(layerIndex, 0, safeCount - 1);
            float stagger = safeCount <= 1
                ? 0f
                : safeIndex / (float)(safeCount - 1) * 0.22f;
            float local = Mathf.InverseLerp(
                stagger,
                Mathf.Min(1f, stagger + 0.78f),
                Mathf.Clamp01(explodedProgress));
            float smooth = local * local * (3f - 2f * local);
            return new PremiumDisplayCaseExplodedSample(
                smooth,
                authoredOffset * smooth);
        }

        public static float EaseAssembly(float normalizedTime)
        {
            float t = Mathf.Clamp01(normalizedTime);
            float inverse = 1f - t;
            return 1f - inverse * inverse * inverse * inverse * inverse;
        }
    }

    /// <summary>
    /// Native-facing manipulation for the reusable case. Gesture recognition
    /// stays in SwiftUI; this component applies semantic orbit, zoom and
    /// assembly progress to the authored Blender layers.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class PremiumDisplayCaseInteractionController : MonoBehaviour
    {
        [SerializeField] private Transform interactionRoot;
        [SerializeField] private Transform[] explodedLayers = Array.Empty<Transform>();
        [SerializeField] private Vector3[] explodedOffsets = Array.Empty<Vector3>();
        [SerializeField] private Transform contentFollower;
        [SerializeField] private int contentFollowerLayerIndex = 3;
        [SerializeField, Range(0f, 1f)] private float explodedProgress;

        private Vector3[] assembledPositions = Array.Empty<Vector3>();
        private Vector3 contentFollowerAssembledPosition;
        private Quaternion interactionBaseRotation = Quaternion.identity;
        private Vector3 interactionBaseScale = Vector3.one;
        private float orbitYaw;
        private float orbitPitch;
        private float zoom = 1f;
        private float animationStart;
        private float animationTarget;
        private float animationElapsed;
        private bool animationPlaying;
        private bool authoringCaptured;

        public float ExplodedProgress => explodedProgress;
        public float Zoom => zoom;
        public Vector2 OrbitDegrees => new Vector2(orbitYaw, orbitPitch);

        private void Awake()
        {
            CaptureAuthoring();
            ApplyInteraction();
            ApplyExplodedProgress(explodedProgress);
        }

        private void Update()
        {
            if (!animationPlaying)
            {
                return;
            }

            animationElapsed += Mathf.Max(0f, Time.unscaledDeltaTime);
            float normalized = animationElapsed
                / PremiumDisplayCaseExplodedLayout.AssemblyDurationSeconds;
            float eased = PremiumDisplayCaseExplodedLayout.EaseAssembly(normalized);
            ApplyExplodedProgress(Mathf.Lerp(animationStart, animationTarget, eased));
            if (normalized >= 1f)
            {
                animationPlaying = false;
                ApplyExplodedProgress(animationTarget);
            }
        }

        public void ConfigureAuthoring(
            Transform authoredInteractionRoot,
            Transform[] authoredLayers,
            Vector3[] authoredOffsets,
            Transform authoredContentFollower = null,
            int authoredContentFollowerLayerIndex = 3)
        {
            interactionRoot = authoredInteractionRoot;
            explodedLayers = authoredLayers ?? Array.Empty<Transform>();
            explodedOffsets = authoredOffsets ?? Array.Empty<Vector3>();
            contentFollower = authoredContentFollower;
            contentFollowerLayerIndex = Mathf.Max(
                0,
                authoredContentFollowerLayerIndex);
            authoringCaptured = false;
            CaptureAuthoring();
            ApplyInteraction();
            ApplyExplodedProgress(explodedProgress);
        }

        public void SetExplodedProgress(float normalizedProgress)
        {
            animationPlaying = false;
            ApplyExplodedProgress(normalizedProgress);
        }

        public void PlayAssembly()
        {
            PlayTo(0f);
        }

        public void PlayExplode()
        {
            PlayTo(1f);
        }

        public void SetOrbitDegrees(float yawDegrees, float pitchDegrees)
        {
            orbitYaw = Mathf.Clamp(yawDegrees, -34f, 34f);
            orbitPitch = Mathf.Clamp(pitchDegrees, -22f, 22f);
            ApplyInteraction();
        }

        public void SetZoom(float normalizedZoom)
        {
            zoom = Mathf.Clamp(normalizedZoom, 0.84f, 1.18f);
            ApplyInteraction();
        }

        public void ResetInteraction()
        {
            orbitYaw = 0f;
            orbitPitch = 0f;
            zoom = 1f;
            ApplyInteraction();
        }

        public void SetExplodedProgressForPreview(float normalizedProgress)
        {
            SetExplodedProgress(normalizedProgress);
        }

        private void PlayTo(float target)
        {
            CaptureAuthoring();
            animationStart = explodedProgress;
            animationTarget = Mathf.Clamp01(target);
            animationElapsed = 0f;
            animationPlaying = true;
        }

        private void CaptureAuthoring()
        {
            if (authoringCaptured || interactionRoot == null)
            {
                return;
            }

            interactionBaseRotation = interactionRoot.localRotation;
            interactionBaseScale = interactionRoot.localScale;
            assembledPositions = new Vector3[explodedLayers.Length];
            for (int index = 0; index < explodedLayers.Length; index++)
            {
                assembledPositions[index] = explodedLayers[index] != null
                    ? explodedLayers[index].localPosition
                    : Vector3.zero;
            }
            contentFollowerAssembledPosition = contentFollower != null
                ? contentFollower.localPosition
                : Vector3.zero;
            authoringCaptured = true;
        }

        private void ApplyInteraction()
        {
            CaptureAuthoring();
            if (interactionRoot == null)
            {
                return;
            }
            interactionRoot.localRotation = interactionBaseRotation
                * Quaternion.Euler(orbitPitch, orbitYaw, 0f);
            interactionRoot.localScale = interactionBaseScale * zoom;
        }

        private void ApplyExplodedProgress(float normalizedProgress)
        {
            CaptureAuthoring();
            explodedProgress = Mathf.Clamp01(normalizedProgress);
            int count = Mathf.Min(
                explodedLayers.Length,
                Mathf.Min(explodedOffsets.Length, assembledPositions.Length));
            for (int index = 0; index < count; index++)
            {
                Transform layer = explodedLayers[index];
                if (layer == null)
                {
                    continue;
                }
                PremiumDisplayCaseExplodedSample sample =
                    PremiumDisplayCaseExplodedLayout.Evaluate(
                        index,
                        count,
                        explodedProgress,
                        explodedOffsets[index]);
                layer.localPosition = assembledPositions[index] + sample.Offset;
            }

            if (contentFollower != null && count > 0)
            {
                int index = Mathf.Clamp(contentFollowerLayerIndex, 0, count - 1);
                PremiumDisplayCaseExplodedSample sample =
                    PremiumDisplayCaseExplodedLayout.Evaluate(
                        index,
                        count,
                        explodedProgress,
                        explodedOffsets[index]);
                contentFollower.localPosition =
                    contentFollowerAssembledPosition + sample.Offset;
            }
        }
    }
}
