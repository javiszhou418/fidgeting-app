using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Candidates
{
    [DisallowMultipleComponent]
    public sealed class PackOpeningGate04R013Sequence : MonoBehaviour
    {
        public const int LongitudinalTearColumns = 96;
        public const float PackWidthMeters = 0.255f;
        public const float PackHeightMeters = 0.340f;
        public const float MouthDepthMeters = 0.300f;
        public const float FoilThicknessMeters = 0.00075f;

        private static readonly float[] BlendShapeSamples =
        {
            0f, 0.15f, 0.35f, 0.55f, 0.75f, 1f
        };

        private static readonly int DissolveId = Shader.PropertyToID("_Dissolve");
        private static readonly int EdgeStrengthId =
            Shader.PropertyToID("_EdgeStrength");
        private static readonly int ProgressId = Shader.PropertyToID("_Progress");
        private static readonly int IntensityId = Shader.PropertyToID("_Intensity");
        private static readonly int SheenCenterId =
            Shader.PropertyToID("_SheenCenter");
        private static readonly int SheenWidthId =
            Shader.PropertyToID("_SheenWidth");
        private static readonly int SheenStrengthId =
            Shader.PropertyToID("_SheenStrength");
        private static readonly int SheenFalloffId =
            Shader.PropertyToID("_SheenFalloff");

        [SerializeField] private PackOpeningGate04R013Profile profile;
        [SerializeField] private Camera captureCamera;
        [SerializeField] private Transform packRoot;
        [SerializeField] private SkinnedMeshRenderer[] packRigRenderers =
            Array.Empty<SkinnedMeshRenderer>();
        [SerializeField] private SkinnedMeshRenderer frontFoil;
        [SerializeField] private SkinnedMeshRenderer backFoil;
        [SerializeField] private SkinnedMeshRenderer topCrimp;
        [SerializeField] private SkinnedMeshRenderer tornContourRim;
        [SerializeField] private SkinnedMeshRenderer tornSealStrip;
        [SerializeField] private SkinnedMeshRenderer rolledFrontLip;
        [SerializeField] private Transform caseMotionRoot;
        [SerializeField] private PremiumDisplayCaseShippingPresentation casePresentation;
        [SerializeField] private Transform sourceEffectsRoot;
        [SerializeField] private ParticleSystem[] sourceEffectSystems =
            Array.Empty<ParticleSystem>();

        private MaterialPropertyBlock packProperties;
        private MaterialPropertyBlock rimProperties;
        private MaterialPropertyBlock sourceProperties;
        private MaterialPropertyBlock caseProperties;
        private Renderer[] caseRenderers = Array.Empty<Renderer>();
        private Renderer[] caseTextRenderers = Array.Empty<Renderer>();
        private EntityId[] caseRendererIds = Array.Empty<EntityId>();
        private EntityId[] packRendererIds = Array.Empty<EntityId>();
        private Vector3 cameraBasePosition;
        private Quaternion cameraBaseRotation;
        private float cameraBaseFov;
        private Vector3 packBasePosition;
        private Vector3 caseBasePosition;
        private Quaternion caseBaseRotation;
        private Vector3 caseBaseScale;
        private bool initialized;
        private string sealedStateFingerprint = string.Empty;

        public PackOpeningGate04R013Profile Profile => profile;
        public PackOpeningGate04R013Sample CurrentSample { get; private set; }
        public float ElapsedSeconds { get; private set; }
        public float NormalizedDragProgress { get; private set; }
        public bool PackVisible => frontFoil != null && frontFoil.enabled;
        public bool MouthContactOcclusionActive =>
            rolledFrontLip != null
            && rolledFrontLip.enabled
            && NormalizedDragProgress > 0.01f;
        public float MouthOpenWidthMeters =>
            PackWidthMeters * NormalizedDragProgress;
        public EntityId CaseRootEntityId =>
            caseMotionRoot == null ? EntityId.None : caseMotionRoot.GetEntityId();
        public IReadOnlyList<EntityId> CaseRendererIds => caseRendererIds;
        public IReadOnlyList<EntityId> PackRendererIds => packRendererIds;
        public IReadOnlyList<ParticleSystem> SourceEffectSystems =>
            sourceEffectSystems;
        public int RigRendererCount => packRigRenderers.Length;
        public int RigVertexCount => packRigRenderers.Sum(renderer =>
            renderer == null || renderer.sharedMesh == null
                ? 0
                : renderer.sharedMesh.vertexCount);
        public int RigBlendShapeCount => packRigRenderers.Sum(renderer =>
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
            && packRigRenderers.Length == 10
            && packRigRenderers.All(renderer => renderer != null)
            && frontFoil != null
            && backFoil != null
            && topCrimp != null
            && tornContourRim != null
            && tornSealStrip != null
            && rolledFrontLip != null
            && caseMotionRoot != null
            && casePresentation != null
            && sourceEffectsRoot != null
            && sourceEffectSystems.Length == 2
            && sourceEffectSystems.All(system => system != null);

        public void Configure(
            PackOpeningGate04R013Profile authoredProfile,
            Camera authoredCamera,
            Transform authoredPackRoot,
            SkinnedMeshRenderer[] authoredPackRigRenderers,
            SkinnedMeshRenderer authoredFrontFoil,
            SkinnedMeshRenderer authoredBackFoil,
            SkinnedMeshRenderer authoredTopCrimp,
            SkinnedMeshRenderer authoredTornContourRim,
            SkinnedMeshRenderer authoredTornSealStrip,
            SkinnedMeshRenderer authoredRolledFrontLip,
            Transform authoredCaseMotionRoot,
            PremiumDisplayCaseShippingPresentation authoredCasePresentation,
            Transform authoredSourceEffectsRoot,
            ParticleSystem[] authoredSourceEffectSystems)
        {
            profile = authoredProfile;
            captureCamera = authoredCamera;
            packRoot = authoredPackRoot;
            packRigRenderers = authoredPackRigRenderers;
            frontFoil = authoredFrontFoil;
            backFoil = authoredBackFoil;
            topCrimp = authoredTopCrimp;
            tornContourRim = authoredTornContourRim;
            tornSealStrip = authoredTornSealStrip;
            rolledFrontLip = authoredRolledFrontLip;
            caseMotionRoot = authoredCaseMotionRoot;
            casePresentation = authoredCasePresentation;
            sourceEffectsRoot = authoredSourceEffectsRoot;
            sourceEffectSystems = authoredSourceEffectSystems;
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
                    "Gate 04 R013 Pack-only rig bindings are incomplete.");
            }

            ElapsedSeconds = Mathf.Clamp(
                elapsedSeconds,
                0f,
                PackOpeningGate04R013Profile.TotalSeconds);
            CurrentSample = profile.Evaluate(ElapsedSeconds, reduceMotion);
            ApplyPack(CurrentSample);
            ApplyCase(CurrentSample);
            ApplySourceEffects(CurrentSample);
            ApplyCamera(CurrentSample);
            if (ElapsedSeconds <= 0f && string.IsNullOrEmpty(sealedStateFingerprint))
            {
                sealedStateFingerprint = BuildStateFingerprint();
            }
        }

        public void SetNormalizedDragProgress(float normalizedProgress)
        {
            Initialize();
            if (!HasRequiredBindings)
            {
                throw new MissingReferenceException(
                    "Gate 04 R013 Pack-only rig bindings are incomplete.");
            }

            NormalizedDragProgress = Mathf.Clamp01(normalizedProgress);
            ApplyBlendShapeProgress(NormalizedDragProgress);
            SetPackRendererVisibility(NormalizedDragProgress, 0f);
            ApplyPackProperties(frontFoil, 0f);
            ApplyPackProperties(backFoil, 0f);
            ApplyPackProperties(topCrimp, 0f);
            ApplyRimProperties(0f);
            RestoreCaseToContainedPose();
            StopSourceEffects();
            RestoreCamera();
        }

        public bool ReboundToSealed()
        {
            SetNormalizedDragProgress(0f);
            string current = BuildStateFingerprint();
            bool restored = string.Equals(
                current,
                sealedStateFingerprint,
                StringComparison.Ordinal);
            if (!restored)
            {
                Debug.LogWarning("Gate 04 R013 sealed rebound state did not match.");
            }
            return restored;
        }

        public bool IsCaseContainedInMouth()
        {
            if (caseMotionRoot == null || packRoot == null)
            {
                return false;
            }

            float depth = caseMotionRoot.position.z - packRoot.position.z;
            return NormalizedDragProgress >= 0.35f
                && depth > -0.03f
                && depth < MouthDepthMeters;
        }

        public bool TryGetCaseViewportBounds(out Rect viewportBounds)
        {
            return TryGetViewportBounds(caseRenderers, out viewportBounds);
        }

        public bool TryGetPackViewportBounds(out Rect viewportBounds)
        {
            return TryGetViewportBounds(
                packRigRenderers.Cast<Renderer>().ToArray(),
                out viewportBounds);
        }

        private void Initialize()
        {
            if (initialized || !HasRequiredBindings)
            {
                return;
            }

            ValidateBlendShapes();
            cameraBasePosition = captureCamera.transform.position;
            cameraBaseRotation = captureCamera.transform.rotation;
            cameraBaseFov = captureCamera.fieldOfView;
            packBasePosition = packRoot.localPosition;
            caseBasePosition = caseMotionRoot.localPosition;
            caseBaseRotation = caseMotionRoot.localRotation;
            caseBaseScale = caseMotionRoot.localScale;
            packProperties = new MaterialPropertyBlock();
            rimProperties = new MaterialPropertyBlock();
            sourceProperties = new MaterialPropertyBlock();
            caseProperties = new MaterialPropertyBlock();
            caseMotionRoot.gameObject.SetActive(true);
            casePresentation.SetTimeForPreview(
                casePresentation.RevealProfile.TotalDurationSeconds);
            caseRenderers = casePresentation
                .GetComponentsInChildren<Renderer>(true)
                .Where(renderer => renderer != null)
                .ToArray();
            caseTextRenderers = casePresentation
                .GetComponentsInChildren<TextMesh>(true)
                .Select(label => label.GetComponent<Renderer>())
                .Where(renderer => renderer != null)
                .ToArray();
            caseRendererIds = caseRenderers
                .Select(renderer => renderer.GetEntityId())
                .ToArray();
            packRendererIds = packRigRenderers
                .Select(renderer => renderer.GetEntityId())
                .ToArray();
            StopSourceEffects();
            initialized = true;
        }

        private void ValidateBlendShapes()
        {
            foreach (SkinnedMeshRenderer renderer in packRigRenderers)
            {
                Mesh mesh = renderer.sharedMesh;
                if (mesh == null || mesh.blendShapeCount != BlendShapeSamples.Length - 1)
                {
                    throw new InvalidOperationException(
                        $"R013 rig mesh {renderer.name} has an invalid blend-shape count.");
                }

                for (int index = 1; index < BlendShapeSamples.Length; index++)
                {
                    if (mesh.GetBlendShapeIndex(BlendShapeName(index)) < 0)
                    {
                        throw new InvalidOperationException(
                            $"R013 rig mesh {renderer.name} is missing {BlendShapeName(index)}.");
                    }
                }
            }
        }

        private void ApplyPack(PackOpeningGate04R013Sample sample)
        {
            NormalizedDragProgress = sample.TearProgress;
            ApplyBlendShapeProgress(sample.TearProgress);
            SetPackRendererVisibility(sample.TearProgress, sample.PackDissolve);
            packRoot.localPosition = packBasePosition + new Vector3(
                -0.005f * sample.PackDissolve,
                -0.008f * sample.PackDissolve,
                -0.004f * sample.PackDissolve);
            ApplyPackProperties(frontFoil, sample.PackDissolve);
            ApplyPackProperties(backFoil, sample.PackDissolve);
            ApplyPackProperties(topCrimp, sample.PackDissolve);
            ApplyRimProperties(sample.RimSweep);
        }

        private void ApplyBlendShapeProgress(float progress)
        {
            int lower = 0;
            int upper = BlendShapeSamples.Length - 1;
            for (int index = 1; index < BlendShapeSamples.Length; index++)
            {
                if (progress <= BlendShapeSamples[index])
                {
                    upper = index;
                    lower = index - 1;
                    break;
                }
            }
            if (progress >= BlendShapeSamples[BlendShapeSamples.Length - 1])
            {
                lower = BlendShapeSamples.Length - 1;
                upper = lower;
            }

            float blend = lower == upper
                ? 0f
                : Mathf.InverseLerp(
                    BlendShapeSamples[lower],
                    BlendShapeSamples[upper],
                    progress);
            foreach (SkinnedMeshRenderer renderer in packRigRenderers)
            {
                Mesh mesh = renderer.sharedMesh;
                for (int index = 1; index < BlendShapeSamples.Length; index++)
                {
                    renderer.SetBlendShapeWeight(
                        mesh.GetBlendShapeIndex(BlendShapeName(index)),
                        0f);
                }
                if (lower == upper && lower > 0)
                {
                    renderer.SetBlendShapeWeight(
                        mesh.GetBlendShapeIndex(BlendShapeName(lower)),
                        100f);
                }
                else
                {
                    if (lower > 0)
                    {
                        renderer.SetBlendShapeWeight(
                            mesh.GetBlendShapeIndex(BlendShapeName(lower)),
                            (1f - blend) * 100f);
                    }
                    if (upper > 0)
                    {
                        renderer.SetBlendShapeWeight(
                            mesh.GetBlendShapeIndex(BlendShapeName(upper)),
                            blend * 100f);
                    }
                }
            }
        }

        private void SetPackRendererVisibility(float tearProgress, float dissolve)
        {
            bool visible = dissolve < 0.99995f;
            foreach (SkinnedMeshRenderer renderer in packRigRenderers)
            {
                renderer.enabled = visible;
                renderer.updateWhenOffscreen = true;
            }
            tornContourRim.enabled = visible && tearProgress > 0.012f;
            tornSealStrip.enabled = visible && tearProgress > 0.014f;
            rolledFrontLip.enabled = visible && tearProgress > 0.012f;
        }

        private void ApplyPackProperties(
            Renderer renderer,
            float dissolve)
        {
            if (renderer == null)
            {
                return;
            }

            renderer.GetPropertyBlock(packProperties);
            packProperties.SetFloat(DissolveId, dissolve);
            packProperties.SetFloat(EdgeStrengthId, 0.44f);
            renderer.SetPropertyBlock(packProperties);
        }

        private void ApplyRimProperties(float sweep)
        {
            tornContourRim.GetPropertyBlock(rimProperties);
            rimProperties.SetFloat(ProgressId, NormalizedDragProgress);
            rimProperties.SetFloat(IntensityId, sweep * 1.20f);
            tornContourRim.SetPropertyBlock(rimProperties);
        }

        private void ApplyCase(PackOpeningGate04R013Sample sample)
        {
            Vector3 hero = caseBasePosition + new Vector3(0f, 0.040f, -0.425f);
            Vector3 position = Vector3.Lerp(
                caseBasePosition,
                hero,
                sample.CaseTravel);
            position.y = Mathf.Lerp(
                caseBasePosition.y,
                hero.y,
                sample.CaseLift);
            caseMotionRoot.localPosition = position;
            caseMotionRoot.localRotation = caseBaseRotation
                * Quaternion.Euler(0f, sample.CaseRotationDegrees, 0f);
            caseMotionRoot.localScale = caseBaseScale;
            bool labelsVisible = sample.CaseTravel >= 0.72f;
            foreach (Renderer renderer in caseTextRenderers)
            {
                renderer.enabled = labelsVisible;
            }

            float sheen = sample.CaseTravel > 0.62f
                ? Mathf.Sin(Mathf.Clamp01((sample.CaseTravel - 0.62f) / 0.38f)
                    * Mathf.PI) * 0.13f
                : 0f;
            foreach (Renderer renderer in casePresentation.EffectRenderers)
            {
                renderer.GetPropertyBlock(caseProperties);
                caseProperties.SetFloat(
                    SheenCenterId,
                    Mathf.Lerp(-0.12f, 1.12f, sample.CaseTravel));
                caseProperties.SetFloat(SheenWidthId, 0.060f);
                caseProperties.SetFloat(SheenStrengthId, sheen);
                caseProperties.SetFloat(SheenFalloffId, 0.34f);
                renderer.SetPropertyBlock(caseProperties);
            }
        }

        private void RestoreCaseToContainedPose()
        {
            packRoot.localPosition = packBasePosition;
            caseMotionRoot.localPosition = caseBasePosition;
            caseMotionRoot.localRotation = caseBaseRotation;
            caseMotionRoot.localScale = caseBaseScale;
            foreach (Renderer renderer in caseTextRenderers)
            {
                renderer.enabled = false;
            }
        }

        private void ApplySourceEffects(PackOpeningGate04R013Sample sample)
        {
            float x = Mathf.Lerp(PackWidthMeters * 0.5f, -PackWidthMeters * 0.5f,
                sample.TearProgress);
            sourceEffectsRoot.localPosition = new Vector3(
                x,
                0.108f - sample.TearProgress * 0.067f,
                -0.026f);
            for (int index = 0; index < sourceEffectSystems.Length; index++)
            {
                ParticleSystem system = sourceEffectSystems[index];
                system.Stop(
                    true,
                    ParticleSystemStopBehavior.StopEmittingAndClear);
                if (!sample.SourceEffectsEnabled)
                {
                    continue;
                }

                float age = Mathf.Max(0f, ElapsedSeconds - 0.70f - index * 0.22f);
                system.Simulate(age, true, true, true);
                system.Pause(true);
                ParticleSystemRenderer renderer =
                    system.GetComponent<ParticleSystemRenderer>();
                renderer.GetPropertyBlock(sourceProperties);
                sourceProperties.SetFloat(
                    ProgressId,
                    Mathf.Clamp01(age / 0.92f));
                sourceProperties.SetFloat(
                    IntensityId,
                    index == 0
                        ? sample.RimSweep * 1.40f
                        : sample.SourceImpact * 1.05f);
                renderer.SetPropertyBlock(sourceProperties);
            }
        }

        private void StopSourceEffects()
        {
            foreach (ParticleSystem system in sourceEffectSystems)
            {
                if (system != null)
                {
                    system.Stop(
                        true,
                        ParticleSystemStopBehavior.StopEmittingAndClear);
                }
            }
        }

        private void ApplyCamera(PackOpeningGate04R013Sample sample)
        {
            captureCamera.transform.position =
                cameraBasePosition
                + cameraBaseRotation * Vector3.forward * sample.CameraPush
                + cameraBaseRotation * new Vector3(
                    sample.CameraKick.x,
                    sample.CameraKick.y,
                    0f);
            captureCamera.transform.rotation = cameraBaseRotation;
            captureCamera.fieldOfView = cameraBaseFov - sample.CameraPush * 3.4f;
        }

        private void RestoreCamera()
        {
            captureCamera.transform.position = cameraBasePosition;
            captureCamera.transform.rotation = cameraBaseRotation;
            captureCamera.fieldOfView = cameraBaseFov;
        }

        private bool TryGetViewportBounds(
            IReadOnlyList<Renderer> renderers,
            out Rect viewportBounds)
        {
            viewportBounds = default;
            if (captureCamera == null || !TryGetWorldBounds(renderers, out Bounds bounds))
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

            var builder = new StringBuilder(4096);
            AppendVector(builder, captureCamera.transform.position);
            AppendVector(builder, packRoot.localPosition);
            AppendVector(builder, caseMotionRoot.localPosition);
            foreach (SkinnedMeshRenderer renderer in packRigRenderers)
            {
                builder.Append(renderer.enabled ? '1' : '0');
                Mesh mesh = renderer.sharedMesh;
                for (int index = 1; index < BlendShapeSamples.Length; index++)
                {
                    builder.Append(renderer.GetBlendShapeWeight(
                        mesh.GetBlendShapeIndex(BlendShapeName(index))).ToString("R"))
                        .Append('|');
                }
            }
            return builder.ToString();
        }

        private static string BlendShapeName(int sampleIndex)
        {
            return $"Tear_{Mathf.RoundToInt(BlendShapeSamples[sampleIndex] * 100f):000}";
        }

        private static void AppendVector(StringBuilder builder, Vector3 value)
        {
            builder.Append(value.x.ToString("R")).Append('|')
                .Append(value.y.ToString("R")).Append('|')
                .Append(value.z.ToString("R")).Append('|');
        }
    }
}
