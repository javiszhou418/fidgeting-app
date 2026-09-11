using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Candidates
{
    [DisallowMultipleComponent]
    public sealed class PackOpeningGate04R014Sequence : MonoBehaviour
    {
        public const float PackWidthMeters = 0.255f;
        public const float PackHeightMeters = 0.340f;
        public const float MouthDepthMeters = 0.070f;
        public const float FoilThicknessMeters = 0.00075f;
        public const float TopSealHeightFraction = 0.06470588f;

        private static readonly string[] PoseKeys =
        {
            "Pose_TabCatch",
            "Pose_NarrowPeel",
            "Pose_TearAdvance",
            "Pose_FormedMouth",
            "Pose_CaseContained",
            "Pose_ContinuousRise"
        };

        private static readonly int DissolveId = Shader.PropertyToID("_Dissolve");
        private static readonly int EdgeStrengthId =
            Shader.PropertyToID("_EdgeStrength");
        private static readonly int SweepProgressId =
            Shader.PropertyToID("_SweepProgress");
        private static readonly int IntensityId = Shader.PropertyToID("_Intensity");

        [SerializeField] private PackOpeningGate04R014Profile profile;
        [SerializeField] private Camera captureCamera;
        [SerializeField] private Transform packRoot;
        [SerializeField] private SkinnedMeshRenderer[] packRenderers =
            Array.Empty<SkinnedMeshRenderer>();
        [SerializeField] private SkinnedMeshRenderer frontFoil;
        [SerializeField] private SkinnedMeshRenderer topSeal;
        [SerializeField] private SkinnedMeshRenderer innerMouth;
        [SerializeField] private SkinnedMeshRenderer innerBackRim;
        [SerializeField] private SkinnedMeshRenderer rolledCrimpLip;
        [SerializeField] private SkinnedMeshRenderer tornContourRim;
        [SerializeField] private SkinnedMeshRenderer tornSealStrip;
        [SerializeField] private SkinnedMeshRenderer pullTab;
        [SerializeField] private Transform caseMotionRoot;
        [SerializeField] private PremiumDisplayCaseShippingPresentation casePresentation;

        private MaterialPropertyBlock packProperties;
        private MaterialPropertyBlock contourProperties;
        private Renderer[] caseRenderers = Array.Empty<Renderer>();
        private EntityId[] caseRendererIds = Array.Empty<EntityId>();
        private EntityId[] packRendererIds = Array.Empty<EntityId>();
        private Vector3 packBasePosition;
        private Vector3 caseBasePosition;
        private Quaternion caseBaseRotation;
        private Vector3 caseBaseScale;
        private bool initialized;
        private bool opticalSweepEnabled = true;
        private string sealedStateFingerprint = string.Empty;

        public PackOpeningGate04R014Profile Profile => profile;
        public PackOpeningGate04R014Sample CurrentSample { get; private set; }
        public float ElapsedSeconds { get; private set; }
        public float NormalizedTearProgress { get; private set; }
        public bool PackVisible => frontFoil != null && frontFoil.enabled;
        public bool OpticalSweepEnabled => opticalSweepEnabled;
        public bool MouthContactOcclusionActive =>
            rolledCrimpLip != null
            && rolledCrimpLip.enabled
            && NormalizedTearProgress >= 0.28f;
        public EntityId CaseRootEntityId =>
            caseMotionRoot == null ? EntityId.None : caseMotionRoot.GetEntityId();
        public IReadOnlyList<EntityId> CaseRendererIds => caseRendererIds;
        public IReadOnlyList<EntityId> PackRendererIds => packRendererIds;
        public int RigRendererCount => packRenderers.Length;
        public int RigBlendShapeCount => packRenderers.Sum(renderer =>
            renderer == null || renderer.sharedMesh == null
                ? 0
                : renderer.sharedMesh.blendShapeCount);
        public Vector3 CaseAuthoredScale => caseBaseScale;
        public Transform CaseMotionRoot => caseMotionRoot;
        public PremiumDisplayCaseShippingPresentation CasePresentation =>
            casePresentation;
        public string SealedStateFingerprint => sealedStateFingerprint;
        public string CurrentStateFingerprint => BuildStateFingerprint();

        public bool HasRequiredBindings =>
            profile != null
            && captureCamera != null
            && packRoot != null
            && packRenderers.Length == 10
            && packRenderers.All(renderer => renderer != null)
            && frontFoil != null
            && topSeal != null
            && innerMouth != null
            && innerBackRim != null
            && rolledCrimpLip != null
            && tornContourRim != null
            && tornSealStrip != null
            && pullTab != null
            && caseMotionRoot != null
            && casePresentation != null;

        public void Configure(
            PackOpeningGate04R014Profile authoredProfile,
            Camera authoredCamera,
            Transform authoredPackRoot,
            SkinnedMeshRenderer[] authoredPackRenderers,
            SkinnedMeshRenderer authoredFrontFoil,
            SkinnedMeshRenderer authoredTopSeal,
            SkinnedMeshRenderer authoredInnerMouth,
            SkinnedMeshRenderer authoredInnerBackRim,
            SkinnedMeshRenderer authoredRolledCrimpLip,
            SkinnedMeshRenderer authoredTornContourRim,
            SkinnedMeshRenderer authoredTornSealStrip,
            SkinnedMeshRenderer authoredPullTab,
            Transform authoredCaseMotionRoot,
            PremiumDisplayCaseShippingPresentation authoredCasePresentation)
        {
            profile = authoredProfile;
            captureCamera = authoredCamera;
            packRoot = authoredPackRoot;
            packRenderers = authoredPackRenderers;
            frontFoil = authoredFrontFoil;
            topSeal = authoredTopSeal;
            innerMouth = authoredInnerMouth;
            innerBackRim = authoredInnerBackRim;
            rolledCrimpLip = authoredRolledCrimpLip;
            tornContourRim = authoredTornContourRim;
            tornSealStrip = authoredTornSealStrip;
            pullTab = authoredPullTab;
            caseMotionRoot = authoredCaseMotionRoot;
            casePresentation = authoredCasePresentation;
            Initialize();
            SetTime(0f, false);
            sealedStateFingerprint = BuildStateFingerprint();
        }

        private void Awake()
        {
            Initialize();
            if (HasRequiredBindings)
            {
                SetTime(0f, false);
                sealedStateFingerprint = BuildStateFingerprint();
            }
        }

        public void SetTime(float elapsedSeconds, bool reduceMotion)
        {
            Initialize();
            if (!HasRequiredBindings)
            {
                throw new MissingReferenceException(
                    "Gate 04 R014 Pack-only rig bindings are incomplete.");
            }

            ElapsedSeconds = Mathf.Clamp(
                elapsedSeconds,
                0f,
                PackOpeningGate04R014Profile.TotalSeconds);
            CurrentSample = profile.Evaluate(ElapsedSeconds, reduceMotion);
            NormalizedTearProgress = CurrentSample.TearProgress;
            ApplyBlendShapeProgress(NormalizedTearProgress);
            ApplyPack(CurrentSample);
            ApplyCase(CurrentSample);
            ApplyContourSweep(CurrentSample);
            if (ElapsedSeconds <= 0f && string.IsNullOrEmpty(sealedStateFingerprint))
            {
                sealedStateFingerprint = BuildStateFingerprint();
            }
        }

        public void SetNormalizedTearProgress(float progress)
        {
            Initialize();
            if (!HasRequiredBindings)
            {
                throw new MissingReferenceException(
                    "Gate 04 R014 Pack-only rig bindings are incomplete.");
            }

            NormalizedTearProgress = Mathf.Clamp01(progress);
            ApplyBlendShapeProgress(NormalizedTearProgress);
            ApplyPack(new PackOpeningGate04R014Sample(
                PackOpeningGate04R014Phase.FormedMouth,
                PackOpeningGate04R014Occlusion.MouthOpening,
                NormalizedTearProgress,
                0f,
                0f,
                0f));
            ApplyCase(new PackOpeningGate04R014Sample(
                PackOpeningGate04R014Phase.CaseContained,
                PackOpeningGate04R014Occlusion.CaseContained,
                NormalizedTearProgress,
                0f,
                0f,
                0f));
            ApplyContourSweep(new PackOpeningGate04R014Sample(
                PackOpeningGate04R014Phase.FormedMouth,
                PackOpeningGate04R014Occlusion.MouthOpening,
                NormalizedTearProgress,
                0f,
                0f,
                0f));
        }

        public void SetOpticalSweepEnabled(bool enabled)
        {
            opticalSweepEnabled = enabled;
            ApplyContourSweep(CurrentSample);
        }

        public bool ReboundToSealed()
        {
            SetNormalizedTearProgress(0f);
            SetTime(0f, false);
            return string.Equals(
                BuildStateFingerprint(),
                sealedStateFingerprint,
                StringComparison.Ordinal);
        }

        public bool IsCaseContainedInMouth()
        {
            if (caseMotionRoot == null || packRoot == null)
            {
                return false;
            }

            float depth = caseMotionRoot.position.z - packRoot.position.z;
            return CurrentSample.Occlusion
                == PackOpeningGate04R014Occlusion.CaseContained
                && depth >= 0.020f
                && depth <= MouthDepthMeters + 0.006f;
        }

        public bool TryGetCaseViewportBounds(out Rect viewportBounds)
        {
            return TryGetViewportBounds(caseRenderers, out viewportBounds);
        }

        public bool TryGetPackViewportBounds(out Rect viewportBounds)
        {
            return TryGetViewportBounds(
                packRenderers.Cast<Renderer>().ToArray(),
                out viewportBounds);
        }

        private void Initialize()
        {
            if (initialized || !HasRequiredBindings)
            {
                return;
            }

            ValidateBlendShapes();
            packBasePosition = packRoot.localPosition;
            caseBasePosition = caseMotionRoot.localPosition;
            caseBaseRotation = caseMotionRoot.localRotation;
            caseBaseScale = caseMotionRoot.localScale;
            packProperties = new MaterialPropertyBlock();
            contourProperties = new MaterialPropertyBlock();
            caseMotionRoot.gameObject.SetActive(true);
            casePresentation.SetTimeForPreview(
                casePresentation.RevealProfile.TotalDurationSeconds);
            caseRenderers = casePresentation.GetComponentsInChildren<Renderer>(true)
                .Where(renderer => renderer != null)
                .ToArray();
            caseRendererIds = caseRenderers
                .Select(renderer => renderer.GetEntityId())
                .ToArray();
            packRendererIds = packRenderers
                .Select(renderer => renderer.GetEntityId())
                .ToArray();
            initialized = true;
        }

        private void ValidateBlendShapes()
        {
            foreach (SkinnedMeshRenderer renderer in packRenderers)
            {
                Mesh mesh = renderer.sharedMesh;
                if (mesh == null || mesh.blendShapeCount != PoseKeys.Length)
                {
                    throw new InvalidOperationException(
                        $"R014 rig mesh {renderer.name} has an invalid pose count.");
                }
                foreach (string key in PoseKeys)
                {
                    if (mesh.GetBlendShapeIndex(key) < 0)
                    {
                        throw new InvalidOperationException(
                            $"R014 rig mesh {renderer.name} is missing {key}.");
                    }
                }
            }
        }

        private void ApplyBlendShapeProgress(float progress)
        {
            float[] samples = PackOpeningGate04R014Profile.AuthoredPoseProgresses;
            int lower = 0;
            int upper = samples.Length - 1;
            for (int index = 1; index < samples.Length; index++)
            {
                if (progress <= samples[index])
                {
                    lower = index - 1;
                    upper = index;
                    break;
                }
            }
            if (progress >= samples[samples.Length - 1])
            {
                lower = samples.Length - 1;
                upper = lower;
            }

            float blend = lower == upper
                ? 0f
                : Mathf.InverseLerp(samples[lower], samples[upper], progress);
            foreach (SkinnedMeshRenderer renderer in packRenderers)
            {
                Mesh mesh = renderer.sharedMesh;
                for (int index = 0; index < PoseKeys.Length; index++)
                {
                    renderer.SetBlendShapeWeight(
                        mesh.GetBlendShapeIndex(PoseKeys[index]),
                        0f);
                }
                if (lower > 0)
                {
                    renderer.SetBlendShapeWeight(
                        mesh.GetBlendShapeIndex(PoseKeys[lower - 1]),
                        upper == lower ? 100f : (1f - blend) * 100f);
                }
                if (upper > 0 && upper != lower)
                {
                    renderer.SetBlendShapeWeight(
                        mesh.GetBlendShapeIndex(PoseKeys[upper - 1]),
                        blend * 100f);
                }
            }
        }

        private void ApplyPack(PackOpeningGate04R014Sample sample)
        {
            bool visible = sample.PackDissolve < 0.9995f;
            frontFoil.enabled = visible;
            topSeal.enabled = visible;
            innerMouth.enabled = visible && sample.TearProgress > 0.01f;
            innerBackRim.enabled = visible && sample.TearProgress > 0.01f;
            rolledCrimpLip.enabled = visible && sample.TearProgress > 0.04f;
            tornContourRim.enabled = visible && sample.TearProgress > 0.10f;
            tornSealStrip.enabled = visible
                && sample.TearProgress > 0.18f
                && sample.PackDissolve < 0.84f;
            pullTab.enabled = visible && sample.PackDissolve < 0.92f;
            foreach (SkinnedMeshRenderer renderer in packRenderers)
            {
                renderer.updateWhenOffscreen = true;
            }

            packRoot.localPosition = packBasePosition + new Vector3(
                0f,
                -0.018f * sample.PackDissolve,
                0.002f * sample.PackDissolve);
            ApplyPackProperties(frontFoil, sample.PackDissolve);
            ApplyPackProperties(topSeal, sample.PackDissolve);
        }

        private void ApplyPackProperties(
            Renderer renderer,
            float dissolve)
        {
            renderer.GetPropertyBlock(packProperties);
            packProperties.SetFloat(DissolveId, dissolve);
            packProperties.SetFloat(EdgeStrengthId, 0.10f);
            renderer.SetPropertyBlock(packProperties);
        }

        private void ApplyCase(PackOpeningGate04R014Sample sample)
        {
            float travel = sample.CaseTravel;
            caseMotionRoot.localPosition = caseBasePosition + new Vector3(
                0f,
                0.105f * travel,
                -0.055f * travel);
            caseMotionRoot.localRotation = caseBaseRotation
                * Quaternion.Euler(0f, -7f * (1f - travel), 0f);
            caseMotionRoot.localScale = caseBaseScale;
        }

        private void ApplyContourSweep(PackOpeningGate04R014Sample sample)
        {
            if (tornContourRim == null)
            {
                return;
            }

            tornContourRim.GetPropertyBlock(contourProperties);
            contourProperties.SetFloat(SweepProgressId, sample.TearProgress);
            contourProperties.SetFloat(
                IntensityId,
                opticalSweepEnabled ? sample.OpticalSweep * 0.26f : 0f);
            tornContourRim.SetPropertyBlock(contourProperties);
        }

        private bool TryGetViewportBounds(
            IReadOnlyList<Renderer> renderers,
            out Rect viewportBounds)
        {
            viewportBounds = default;
            if (captureCamera == null
                || !TryGetWorldBounds(renderers, out Bounds bounds))
            {
                return false;
            }

            Vector3 center = bounds.center;
            Vector3 extents = bounds.extents;
            float minX = float.PositiveInfinity;
            float minY = float.PositiveInfinity;
            float maxX = float.NegativeInfinity;
            float maxY = float.NegativeInfinity;
            for (int x = -1; x <= 1; x += 2)
            {
                for (int y = -1; y <= 1; y += 2)
                {
                    for (int z = -1; z <= 1; z += 2)
                    {
                        Vector3 viewport = captureCamera.WorldToViewportPoint(
                            center + Vector3.Scale(
                                extents,
                                new Vector3(x, y, z)));
                        if (viewport.z <= 0f)
                        {
                            continue;
                        }
                        minX = Mathf.Min(minX, viewport.x);
                        minY = Mathf.Min(minY, viewport.y);
                        maxX = Mathf.Max(maxX, viewport.x);
                        maxY = Mathf.Max(maxY, viewport.y);
                    }
                }
            }

            if (float.IsInfinity(minX)
                || float.IsInfinity(minY)
                || float.IsInfinity(maxX)
                || float.IsInfinity(maxY))
            {
                return false;
            }

            viewportBounds = Rect.MinMaxRect(minX, minY, maxX, maxY);
            return true;
        }

        private static bool TryGetWorldBounds(
            IReadOnlyList<Renderer> renderers,
            out Bounds bounds)
        {
            bounds = default;
            bool found = false;
            foreach (Renderer renderer in renderers)
            {
                if (renderer == null || !renderer.enabled)
                {
                    continue;
                }
                if (!found)
                {
                    bounds = renderer.bounds;
                    found = true;
                }
                else
                {
                    bounds.Encapsulate(renderer.bounds);
                }
            }
            return found;
        }

        private string BuildStateFingerprint()
        {
            if (!initialized)
            {
                return string.Empty;
            }

            var builder = new StringBuilder(2048);
            AppendVector(builder, packRoot.localPosition);
            AppendVector(builder, caseMotionRoot.localPosition);
            foreach (SkinnedMeshRenderer renderer in packRenderers)
            {
                builder.Append(renderer.enabled ? '1' : '0');
                Mesh mesh = renderer.sharedMesh;
                foreach (string key in PoseKeys)
                {
                    builder.Append(renderer.GetBlendShapeWeight(
                        mesh.GetBlendShapeIndex(key)).ToString("R")).Append('|');
                }
            }
            return builder.ToString();
        }

        private static void AppendVector(StringBuilder builder, Vector3 value)
        {
            builder.Append(value.x.ToString("R")).Append('|')
                .Append(value.y.ToString("R")).Append('|')
                .Append(value.z.ToString("R")).Append('|');
        }
    }
}
