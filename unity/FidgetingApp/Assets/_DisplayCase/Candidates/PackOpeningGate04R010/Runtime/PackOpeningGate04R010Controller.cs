using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.DisplayCase.Candidates
{
    [DisallowMultipleComponent]
    public sealed class PackOpeningGate04R010Controller : MonoBehaviour
    {
        private static readonly int BaseMapId = Shader.PropertyToID("_BaseMap");
        private static readonly int BaseColorId = Shader.PropertyToID("_BaseColor");
        private static readonly int SaturationId = Shader.PropertyToID("_Saturation");
        private static readonly int OpacityId = Shader.PropertyToID("_Opacity");
        private static readonly int SheenCenterId = Shader.PropertyToID("_SheenCenter");
        private static readonly int SheenWidthId = Shader.PropertyToID("_SheenWidth");
        private static readonly int SheenStrengthId = Shader.PropertyToID("_SheenStrength");
        private static readonly int SheenFalloffId = Shader.PropertyToID("_SheenFalloff");

        public const int StripSegments = 48;
        public const int StripRows = 4;
        public const int BodyRows = 9;
        public const float PackWidth = 0.255f;
        public const float PackHeight = 0.340f;
        public const float TearSeamY = PackHeight * 0.320f;
        public const float StripHeight = 0.026f;
        public const float StripThickness = 0.00075f;
        public const float MaximumTearAmplitude = 0.00115f;
        public const float CaseScale = 1.02f;

        private const float PackHalfWidth = PackWidth * 0.47f;
        private const float PackBottomY = -PackHeight * 0.5f;
        private const float PackPlaneZ = 0f;
        private const float ApertureDepth = 0.091f;
        private const float FlapUvMin = 1f - 96f / 512f;
        private const float FlapUvMax = 1f - 57f / 512f;

        [SerializeField] private PackOpeningGate04R010Profile profile;
        [SerializeField] private Camera captureCamera;
        [SerializeField] private Renderer environmentRenderer;
        [SerializeField] private Texture2D environmentTexture;
        [SerializeField] private Transform packRoot;
        [SerializeField] private MeshFilter packBodyMeshFilter;
        [SerializeField] private Renderer packBodyRenderer;
        [SerializeField] private MeshFilter tearStripMeshFilter;
        [SerializeField] private Renderer tearStripRenderer;
        [SerializeField] private MeshFilter cavityMeshFilter;
        [SerializeField] private Renderer cavityRenderer;
        [SerializeField] private MeshFilter contactShadowMeshFilter;
        [SerializeField] private Renderer contactShadowRenderer;
        [SerializeField] private MeshFilter specularMeshFilter;
        [SerializeField] private Renderer specularRenderer;
        [SerializeField] private Transform caseMotionRoot;
        [SerializeField] private PremiumDisplayCaseShippingPresentation casePresentation;
        [SerializeField] private Transform localizedFlash;
        [SerializeField] private Renderer localizedFlashRenderer;
        [SerializeField] private Transform energyRing;
        [SerializeField] private Renderer energyRingRenderer;
        [SerializeField] private ParticleSystem foilShards;
        [SerializeField] private ParticleSystem glints;
        [SerializeField] private ParticleSystem directionalStreaks;
        [SerializeField] private Light openingLight;

        private readonly float[] tearOffsets = new float[StripSegments + 1];
        private readonly Vector3[] bodyVertices =
            new Vector3[(StripSegments + 1) * (BodyRows + 1)];
        private readonly Vector2[] bodyUvs =
            new Vector2[(StripSegments + 1) * (BodyRows + 1)];
        private readonly List<int> bodyTriangles =
            new List<int>(StripSegments * BodyRows * 6);
        private readonly Vector3[] stripVertices =
            new Vector3[(StripSegments + 1) * (StripRows + 1) * 2];
        private readonly Vector2[] stripUvs =
            new Vector2[(StripSegments + 1) * (StripRows + 1) * 2];
        private readonly Color[] stripColors =
            new Color[(StripSegments + 1) * (StripRows + 1) * 2];
        private readonly int[][] stripTriangles =
        {
            new int[StripSegments * StripRows * 6],
            new int[StripSegments * StripRows * 6],
            new int[StripSegments * 12 + StripRows * 12]
        };
        private readonly Vector3[] cavityVertices =
            new Vector3[(StripSegments + 1) * 4];
        private readonly Vector2[] cavityUvs =
            new Vector2[(StripSegments + 1) * 4];
        private readonly List<int> cavityTriangles =
            new List<int>(StripSegments * 18);
        private readonly Vector3[] contactShadowVertices = new Vector3[4];
        private readonly Vector2[] contactShadowUvs =
        {
            Vector2.zero,
            Vector2.up,
            Vector2.right,
            Vector2.one
        };
        private readonly int[] contactShadowTriangles = { 0, 1, 2, 2, 1, 3 };
        private readonly Vector3[] specularVertices = new Vector3[4];
        private readonly Vector2[] specularUvs =
        {
            Vector2.zero,
            Vector2.up,
            Vector2.right,
            Vector2.one
        };
        private readonly int[] specularTriangles = { 0, 1, 2, 2, 1, 3 };

        private Mesh bodyMesh;
        private Mesh stripMesh;
        private Mesh cavityMesh;
        private Mesh contactShadowMesh;
        private Mesh specularMesh;
        private MaterialPropertyBlock environmentProperties;
        private MaterialPropertyBlock accentProperties;
        private MaterialPropertyBlock caseProperties;
        private Vector3 cameraBasePosition;
        private Quaternion cameraBaseRotation;
        private float cameraBaseFov;
        private Vector3 packBaseScale;
        private Vector3 caseBasePosition;
        private Quaternion caseBaseRotation;
        private Vector3 caseBaseScale;
        private Renderer[] caseRenderers = Array.Empty<Renderer>();
        private Renderer[] caseTextRenderers = Array.Empty<Renderer>();
        private EntityId[] caseRendererEntityIds = Array.Empty<EntityId>();
        private bool initialized;
        private string sealedStateFingerprint = string.Empty;
        private float maximumAheadOfFrontSeparation;

        public PackOpeningGate04R010Profile Profile => profile;
        public PremiumDisplayCaseShippingPresentation CasePresentation =>
            casePresentation;
        public Transform CaseMotionRoot => caseMotionRoot;
        public float ElapsedSeconds { get; private set; }
        public bool ReduceMotion { get; private set; }
        public PackOpeningGate04R010Sample CurrentSample { get; private set; }
        public float TearFrontXLocal { get; private set; } = PackHalfWidth;
        public Vector3 TearFrontWorldPosition =>
            packRoot != null
                ? packRoot.TransformPoint(new Vector3(
                    TearFrontXLocal,
                    TearSeamY + TearOffsetAtX(TearFrontXLocal),
                    PackPlaneZ))
                : Vector3.zero;
        public IReadOnlyList<float> SharedTearOffsets => tearOffsets;
        public float MaximumAheadOfFrontSeparation =>
            maximumAheadOfFrontSeparation;
        public EntityId CaseRootEntityId =>
            caseMotionRoot != null
                ? caseMotionRoot.GetEntityId()
                : EntityId.None;
        public IReadOnlyList<EntityId> CaseRendererEntityIds =>
            caseRendererEntityIds;
        public Vector3 CaseAuthoredScale => caseBaseScale;
        public bool PackVisible =>
            packBodyRenderer != null && packBodyRenderer.enabled;
        public bool CavityVisible =>
            cavityRenderer != null && cavityRenderer.enabled;
        public string SealedStateFingerprint => sealedStateFingerprint;
        public string CurrentStateFingerprint => BuildStateFingerprint();

        public bool HasRequiredBindings =>
            profile != null
            && captureCamera != null
            && environmentRenderer != null
            && environmentTexture != null
            && packRoot != null
            && packBodyMeshFilter != null
            && packBodyRenderer != null
            && tearStripMeshFilter != null
            && tearStripRenderer != null
            && cavityMeshFilter != null
            && cavityRenderer != null
            && contactShadowMeshFilter != null
            && contactShadowRenderer != null
            && specularMeshFilter != null
            && specularRenderer != null
            && caseMotionRoot != null
            && casePresentation != null
            && localizedFlash != null
            && localizedFlashRenderer != null
            && energyRing != null
            && energyRingRenderer != null
            && foilShards != null
            && glints != null
            && directionalStreaks != null
            && openingLight != null;

        public void Configure(
            PackOpeningGate04R010Profile authoredProfile,
            Camera authoredCamera,
            Renderer authoredEnvironmentRenderer,
            Texture2D authoredEnvironmentTexture,
            Transform authoredPackRoot,
            MeshFilter authoredPackBodyMeshFilter,
            Renderer authoredPackBodyRenderer,
            MeshFilter authoredTearStripMeshFilter,
            Renderer authoredTearStripRenderer,
            MeshFilter authoredCavityMeshFilter,
            Renderer authoredCavityRenderer,
            MeshFilter authoredContactShadowMeshFilter,
            Renderer authoredContactShadowRenderer,
            MeshFilter authoredSpecularMeshFilter,
            Renderer authoredSpecularRenderer,
            Transform authoredCaseMotionRoot,
            PremiumDisplayCaseShippingPresentation authoredCasePresentation,
            Transform authoredLocalizedFlash,
            Renderer authoredLocalizedFlashRenderer,
            Transform authoredEnergyRing,
            Renderer authoredEnergyRingRenderer,
            ParticleSystem authoredFoilShards,
            ParticleSystem authoredGlints,
            ParticleSystem authoredDirectionalStreaks,
            Light authoredOpeningLight)
        {
            profile = authoredProfile;
            captureCamera = authoredCamera;
            environmentRenderer = authoredEnvironmentRenderer;
            environmentTexture = authoredEnvironmentTexture;
            packRoot = authoredPackRoot;
            packBodyMeshFilter = authoredPackBodyMeshFilter;
            packBodyRenderer = authoredPackBodyRenderer;
            tearStripMeshFilter = authoredTearStripMeshFilter;
            tearStripRenderer = authoredTearStripRenderer;
            cavityMeshFilter = authoredCavityMeshFilter;
            cavityRenderer = authoredCavityRenderer;
            contactShadowMeshFilter = authoredContactShadowMeshFilter;
            contactShadowRenderer = authoredContactShadowRenderer;
            specularMeshFilter = authoredSpecularMeshFilter;
            specularRenderer = authoredSpecularRenderer;
            caseMotionRoot = authoredCaseMotionRoot;
            casePresentation = authoredCasePresentation;
            localizedFlash = authoredLocalizedFlash;
            localizedFlashRenderer = authoredLocalizedFlashRenderer;
            energyRing = authoredEnergyRing;
            energyRingRenderer = authoredEnergyRingRenderer;
            foilShards = authoredFoilShards;
            glints = authoredGlints;
            directionalStreaks = authoredDirectionalStreaks;
            openingLight = authoredOpeningLight;
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

        private void OnDestroy()
        {
            DestroyOwned(bodyMesh);
            DestroyOwned(stripMesh);
            DestroyOwned(cavityMesh);
            DestroyOwned(contactShadowMesh);
            DestroyOwned(specularMesh);
        }

        public void SetTime(float elapsedSeconds, bool reduceMotion)
        {
            Initialize();
            if (!HasRequiredBindings)
            {
                throw new MissingReferenceException(
                    "Gate 04 rev 10 controller bindings are incomplete.");
            }

            ElapsedSeconds = Mathf.Clamp(
                elapsedSeconds,
                0f,
                PackOpeningGate04R010Profile.TotalSeconds);
            ReduceMotion = reduceMotion;
            CurrentSample = profile.Evaluate(ElapsedSeconds, reduceMotion);
            ApplyPack(CurrentSample);
            ApplyCase(CurrentSample);
            ApplyImpact(CurrentSample);
            ApplyCamera(CurrentSample);
            if (
                ElapsedSeconds <= 0f
                && string.IsNullOrEmpty(sealedStateFingerprint)
            )
            {
                sealedStateFingerprint = BuildStateFingerprint();
            }
        }

        public bool ReboundToSealed()
        {
            SetTime(0f, false);
            StopParticles(foilShards);
            StopParticles(glints);
            StopParticles(directionalStreaks);
            return string.Equals(
                BuildStateFingerprint(),
                sealedStateFingerprint,
                StringComparison.Ordinal);
        }

        public bool TryGetCaseViewportBounds(out Rect viewportBounds)
        {
            viewportBounds = default;
            if (
                captureCamera == null
                || caseRenderers == null
                || caseRenderers.Length == 0
            )
            {
                return false;
            }

            bool hasBounds = false;
            Bounds worldBounds = default;
            for (int index = 0; index < caseRenderers.Length; index++)
            {
                Renderer renderer = caseRenderers[index];
                if (renderer == null)
                {
                    continue;
                }
                if (!hasBounds)
                {
                    worldBounds = renderer.bounds;
                    hasBounds = true;
                }
                else
                {
                    worldBounds.Encapsulate(renderer.bounds);
                }
            }
            if (!hasBounds)
            {
                return false;
            }

            Vector3 center = worldBounds.center;
            Vector3 extents = worldBounds.extents;
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

            if (
                float.IsInfinity(minX)
                || float.IsInfinity(minY)
                || float.IsInfinity(maxX)
                || float.IsInfinity(maxY)
            )
            {
                return false;
            }
            viewportBounds = Rect.MinMaxRect(minX, minY, maxX, maxY);
            return true;
        }

        public bool TryGetPackViewportBounds(out Rect viewportBounds)
        {
            viewportBounds = default;
            if (
                captureCamera == null
                || packBodyRenderer == null
                || tearStripRenderer == null
                || !packBodyRenderer.enabled
            )
            {
                return false;
            }

            Bounds worldBounds = packBodyRenderer.bounds;
            if (tearStripRenderer.enabled)
            {
                worldBounds.Encapsulate(tearStripRenderer.bounds);
            }
            Vector3 center = worldBounds.center;
            Vector3 extents = worldBounds.extents;
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
            if (
                float.IsInfinity(minX)
                || float.IsInfinity(minY)
                || float.IsInfinity(maxX)
                || float.IsInfinity(maxY)
            )
            {
                return false;
            }
            viewportBounds = Rect.MinMaxRect(minX, minY, maxX, maxY);
            return true;
        }

        public float MeasureFreedTailCurvature(float tearProgress)
        {
            float progress = Mathf.Clamp01(tearProgress);
            if (progress <= 0.001f)
            {
                return 0f;
            }
            float front = Mathf.Lerp(PackHalfWidth, -PackHalfWidth, progress);
            Vector3 a = EvaluateTailPoint(front, 0.25f, progress);
            Vector3 b = EvaluateTailPoint(front, 0.50f, progress);
            Vector3 c = EvaluateTailPoint(front, 0.75f, progress);
            return (a - 2f * b + c).magnitude;
        }

        private void Initialize()
        {
            if (initialized || !HasRequiredBindings)
            {
                return;
            }

            GenerateTearOffsets();
            cameraBasePosition = captureCamera.transform.position;
            cameraBaseRotation = captureCamera.transform.rotation;
            cameraBaseFov = captureCamera.fieldOfView;
            packBaseScale = packRoot.localScale;
            caseBasePosition = caseMotionRoot.localPosition;
            caseBaseRotation = caseMotionRoot.localRotation;
            caseBaseScale = caseMotionRoot.localScale;
            environmentProperties = new MaterialPropertyBlock();
            accentProperties = new MaterialPropertyBlock();
            caseProperties = new MaterialPropertyBlock();
            BuildBodyMesh();
            BuildStripMesh();
            BuildCavityMesh();
            BuildContactShadowMesh();
            BuildSpecularMesh();
            ApplyEnvironment();
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
            caseRendererEntityIds = caseRenderers
                .Select(renderer => renderer.GetEntityId())
                .ToArray();
            StopParticles(foilShards);
            StopParticles(glints);
            StopParticles(directionalStreaks);
            initialized = true;
        }

        private void ApplyEnvironment()
        {
            environmentRenderer.GetPropertyBlock(environmentProperties);
            environmentProperties.SetTexture(BaseMapId, environmentTexture);
            environmentProperties.SetColor(
                BaseColorId,
                new Color(0.72f, 0.74f, 0.72f, 1f));
            environmentProperties.SetFloat(SaturationId, 0.44f);
            environmentProperties.SetFloat(OpacityId, 1f);
            environmentRenderer.SetPropertyBlock(environmentProperties);
        }

        private void ApplyPack(PackOpeningGate04R010Sample sample)
        {
            bool visible = sample.PackRetreat < 0.999f;
            packBodyRenderer.enabled = visible;
            tearStripRenderer.enabled = visible;
            cavityRenderer.enabled =
                visible
                && sample.ApertureProgress > 0.006f
                && sample.PackRetreat < 0.58f;
            contactShadowRenderer.enabled =
                visible
                && sample.TearProgress > 0.008f
                && sample.TearProgress < 0.995f
                && sample.PackRetreat < 0.20f;
            specularRenderer.enabled =
                visible
                && sample.TearProgress > 0.10f
                && sample.PackRetreat < 0.34f;
            packRoot.localScale = Vector3.Scale(
                packBaseScale,
                new Vector3(
                    1f + sample.PackCompression * 0.20f,
                    1f - sample.PackCompression,
                    1f));

            TearFrontXLocal = Mathf.Lerp(
                PackHalfWidth,
                -PackHalfWidth,
                sample.TearProgress);
            UpdateBodyMesh(sample);
            UpdateStripMesh(sample);
            UpdateCavityMesh(sample);
            UpdateContactShadow(sample);
            UpdateSpecularHighlight(sample);
        }

        private void ApplyCase(PackOpeningGate04R010Sample sample)
        {
            Vector3 concealed = caseBasePosition;
            Vector3 hero = new Vector3(
                caseBasePosition.x,
                caseBasePosition.y - 0.017f,
                caseBasePosition.z - 0.300f);
            Vector3 position = Vector3.Lerp(
                concealed,
                hero,
                sample.CaseTravel);
            position.y += sample.CaseSettleOffset;
            caseMotionRoot.localPosition = position;
            caseMotionRoot.localRotation = caseBaseRotation
                * Quaternion.Euler(0f, sample.CaseRotationDegrees, 0f);
            caseMotionRoot.localScale = caseBaseScale;
            bool labelsVisible = sample.PackRetreat >= 0.72f;
            for (int index = 0; index < caseTextRenderers.Length; index++)
            {
                if (caseTextRenderers[index] != null)
                {
                    caseTextRenderers[index].enabled = labelsVisible;
                }
            }

            float sheenStrength = sample.CaseSheen > 0f
                ? Mathf.Sin(sample.CaseSheen * Mathf.PI) * 0.16f
                : 0f;
            for (int index = 0; index < casePresentation.EffectRenderers.Count; index++)
            {
                Renderer renderer = casePresentation.EffectRenderers[index];
                if (renderer == null)
                {
                    continue;
                }
                renderer.GetPropertyBlock(caseProperties);
                caseProperties.SetFloat(
                    SheenCenterId,
                    Mathf.Lerp(-0.12f, 1.12f, sample.CaseSheen));
                caseProperties.SetFloat(SheenWidthId, 0.065f);
                caseProperties.SetFloat(SheenStrengthId, sheenStrength);
                caseProperties.SetFloat(SheenFalloffId, 0.32f);
                renderer.SetPropertyBlock(caseProperties);
            }
        }

        private void ApplyImpact(PackOpeningGate04R010Sample sample)
        {
            bool flashVisible = sample.LocalizedFlash > 0.001f;
            localizedFlash.gameObject.SetActive(flashVisible);
            if (flashVisible)
            {
                localizedFlash.localScale = new Vector3(
                    0.125f,
                    0.060f,
                    1f);
            }
            SetAccentColor(
                localizedFlashRenderer,
                new Color(
                    1f,
                    0.985f,
                    0.93f,
                    flashVisible ? sample.LocalizedFlash * 0.92f : 0f));

            bool ringVisible = sample.EnergyRingProgress > 0.001f;
            energyRing.gameObject.SetActive(ringVisible);
            if (ringVisible)
            {
                float progress = sample.EnergyRingProgress;
                float scale = Mathf.Lerp(0.092f, 0.142f, EaseOutQuart(progress));
                energyRing.localScale = new Vector3(
                    scale,
                    scale * 0.76f,
                    scale);
                SetAccentColor(
                    energyRingRenderer,
                    new Color(
                        0.50f,
                        0.42f,
                        0.60f,
                        Mathf.Sin(progress * Mathf.PI) * 0.16f));
            }

            SimulateImpactSystem(
                foilShards,
                sample.ImpactParticlesEnabled,
                sample.ImpactParticleAge);
            SimulateImpactSystem(
                glints,
                sample.ImpactParticlesEnabled,
                sample.ImpactParticleAge);
            SimulateImpactSystem(
                directionalStreaks,
                sample.DirectionalStreaksEnabled,
                sample.ImpactParticleAge);

            float energy = sample.LocalizedFlash * 2.5f
                + Mathf.Sin(sample.EnergyRingProgress * Mathf.PI) * 0.75f
                + Mathf.Sin(sample.CaseSheen * Mathf.PI) * 0.22f;
            openingLight.intensity = ReduceMotion ? energy * 0.16f : energy;
            openingLight.color = new Color(1f, 0.84f, 0.62f);
        }

        private void ApplyCamera(PackOpeningGate04R010Sample sample)
        {
            captureCamera.transform.position =
                cameraBasePosition
                + cameraBaseRotation * Vector3.forward * sample.CameraPush
                + cameraBaseRotation * new Vector3(
                    sample.CameraKick.x,
                    sample.CameraKick.y,
                    0f);
            captureCamera.transform.rotation = cameraBaseRotation;
            captureCamera.fieldOfView = cameraBaseFov
                - sample.CameraPush * 5.5f
                + Mathf.Abs(sample.CameraKick.x) * 18f;
        }

        private void GenerateTearOffsets()
        {
            const uint seed = 0x6A09E667u;
            uint state = seed;
            var raw = new float[tearOffsets.Length];
            for (int index = 0; index < raw.Length; index++)
            {
                state = state * 1664525u + 1013904223u;
                float unit = ((state >> 8) & 0x00FFFFFFu) / 16777215f;
                raw[index] = unit * 2f - 1f;
            }
            for (int index = 0; index < tearOffsets.Length; index++)
            {
                float previous = raw[Mathf.Max(0, index - 1)];
                float current = raw[index];
                float next = raw[Mathf.Min(raw.Length - 1, index + 1)];
                float lowFrequency = Mathf.Sin(index * 0.73f + 0.45f) * 0.38f;
                tearOffsets[index] = Mathf.Clamp(
                    (previous + current * 2f + next) * 0.125f
                    + lowFrequency,
                    -1f,
                    1f) * MaximumTearAmplitude;
            }
            tearOffsets[0] *= 0.45f;
            tearOffsets[tearOffsets.Length - 1] *= 0.45f;
        }

        private void BuildBodyMesh()
        {
            bodyMesh = new Mesh { name = "Gate04R010PhysicalPackOccluder" };
            bodyMesh.MarkDynamic();
            bodyMesh.vertices = bodyVertices;
            bodyMesh.uv = bodyUvs;
            bodyMesh.triangles = Array.Empty<int>();
            packBodyMeshFilter.sharedMesh = bodyMesh;
        }

        private void UpdateBodyMesh(PackOpeningGate04R010Sample sample)
        {
            bodyTriangles.Clear();
            for (int column = 0; column <= StripSegments; column++)
            {
                float column01 = column / (float)StripSegments;
                float x = Mathf.Lerp(-PackHalfWidth, PackHalfWidth, column01);
                bool released =
                    sample.TearProgress >= 0.999f
                    || x > TearFrontXLocal;
                float release = released
                    ? Mathf.Clamp01(
                        (x - TearFrontXLocal)
                        / Mathf.Max(0.0001f, PackHalfWidth - TearFrontXLocal))
                    : 0f;
                float openedBehindFront = released
                    ? Smooth01(Mathf.InverseLerp(0f, 0.16f, release))
                    : 0f;
                float edgeDepth =
                    ApertureDepth
                    * sample.ApertureProgress
                    * openedBehindFront;
                float originalTop = TearSeamY + tearOffsets[column];
                for (int row = 0; row <= BodyRows; row++)
                {
                    float row01 = row / (float)BodyRows;
                    float topInfluence = Mathf.Pow(row01, 4f);
                    float y = Mathf.Lerp(PackBottomY, originalTop, row01)
                        - edgeDepth * topInfluence;
                    float retreatThreshold =
                        (1f - row01) * 0.92f;
                    float localRetreat = sample.PackRetreat <= 0f
                        ? 0f
                        : Smooth01(Mathf.InverseLerp(
                            retreatThreshold - 0.07f,
                            retreatThreshold + 0.19f,
                            sample.PackRetreat));
                    float outward = Mathf.Sign(Mathf.Abs(x) < 0.0001f ? 1f : x);
                    int index = BodyIndex(column, row);
                    bodyVertices[index] = new Vector3(
                        x + outward * localRetreat * (0.028f + 0.065f * row01),
                        y - localRetreat * (0.035f + 0.105f * row01),
                        PackPlaneZ - localRetreat * (0.012f + 0.016f * row01));
                    bodyUvs[index] = new Vector2(
                        column01,
                        Mathf.Clamp01(
                            Mathf.Lerp(
                                0f,
                                originalTop / PackHeight + 0.5f,
                                row01)));
                }
            }

            for (int column = 0; column < StripSegments; column++)
            {
                float column01 = (column + 0.5f) / StripSegments;
                float x = Mathf.Lerp(-PackHalfWidth, PackHalfWidth, column01);
                for (int row = 0; row < BodyRows; row++)
                {
                    float row01 = (row + 0.5f) / BodyRows;
                    float threshold = (1f - row01) * 0.92f;
                    float removed = sample.PackRetreat <= 0f
                        ? 0f
                        : Smooth01(Mathf.InverseLerp(
                            threshold - 0.07f,
                            threshold + 0.19f,
                            sample.PackRetreat));
                    if (removed >= 0.82f)
                    {
                        continue;
                    }
                    int lower = BodyIndex(column, row);
                    int upper = BodyIndex(column, row + 1);
                    int nextLower = BodyIndex(column + 1, row);
                    int nextUpper = BodyIndex(column + 1, row + 1);
                    bodyTriangles.Add(lower);
                    bodyTriangles.Add(upper);
                    bodyTriangles.Add(nextLower);
                    bodyTriangles.Add(nextLower);
                    bodyTriangles.Add(upper);
                    bodyTriangles.Add(nextUpper);
                }
            }

            bodyMesh.Clear(false);
            bodyMesh.vertices = bodyVertices;
            bodyMesh.uv = bodyUvs;
            bodyMesh.SetTriangles(bodyTriangles, 0);
            bodyMesh.RecalculateNormals();
            bodyMesh.RecalculateBounds();
        }

        private void BuildStripMesh()
        {
            stripMesh = new Mesh
            {
                name = "Gate04R010SubdividedDeformableFoilStrip",
                subMeshCount = 3
            };
            stripMesh.MarkDynamic();
            int frontTriangle = 0;
            int backTriangle = 0;
            int edgeTriangle = 0;
            for (int column = 0; column < StripSegments; column++)
            {
                for (int row = 0; row < StripRows; row++)
                {
                    int frontLower = StripIndex(column, row, 0);
                    int frontUpper = StripIndex(column, row + 1, 0);
                    int frontNextLower = StripIndex(column + 1, row, 0);
                    int frontNextUpper = StripIndex(column + 1, row + 1, 0);
                    stripTriangles[0][frontTriangle++] = frontLower;
                    stripTriangles[0][frontTriangle++] = frontUpper;
                    stripTriangles[0][frontTriangle++] = frontNextLower;
                    stripTriangles[0][frontTriangle++] = frontNextLower;
                    stripTriangles[0][frontTriangle++] = frontUpper;
                    stripTriangles[0][frontTriangle++] = frontNextUpper;

                    int backLower = StripIndex(column, row, 1);
                    int backUpper = StripIndex(column, row + 1, 1);
                    int backNextLower = StripIndex(column + 1, row, 1);
                    int backNextUpper = StripIndex(column + 1, row + 1, 1);
                    stripTriangles[1][backTriangle++] = backLower;
                    stripTriangles[1][backTriangle++] = backNextLower;
                    stripTriangles[1][backTriangle++] = backUpper;
                    stripTriangles[1][backTriangle++] = backNextLower;
                    stripTriangles[1][backTriangle++] = backNextUpper;
                    stripTriangles[1][backTriangle++] = backUpper;
                }

                AddStripEdgeQuad(
                    column,
                    column + 1,
                    0,
                    ref edgeTriangle);
                AddStripEdgeQuad(
                    column + 1,
                    column,
                    StripRows,
                    ref edgeTriangle);
            }
            for (int row = 0; row < StripRows; row++)
            {
                AddStripCapQuad(0, row + 1, row, ref edgeTriangle);
                AddStripCapQuad(
                    StripSegments,
                    row,
                    row + 1,
                    ref edgeTriangle);
            }

            stripMesh.vertices = stripVertices;
            stripMesh.uv = stripUvs;
            stripMesh.colors = stripColors;
            stripMesh.SetTriangles(stripTriangles[0], 0);
            stripMesh.SetTriangles(stripTriangles[1], 1);
            stripMesh.SetTriangles(stripTriangles[2], 2);
            tearStripMeshFilter.sharedMesh = stripMesh;
        }

        private void AddStripEdgeQuad(
            int firstColumn,
            int secondColumn,
            int row,
            ref int triangle)
        {
            int firstFront = StripIndex(firstColumn, row, 0);
            int firstBack = StripIndex(firstColumn, row, 1);
            int secondFront = StripIndex(secondColumn, row, 0);
            int secondBack = StripIndex(secondColumn, row, 1);
            stripTriangles[2][triangle++] = firstFront;
            stripTriangles[2][triangle++] = secondFront;
            stripTriangles[2][triangle++] = firstBack;
            stripTriangles[2][triangle++] = firstBack;
            stripTriangles[2][triangle++] = secondFront;
            stripTriangles[2][triangle++] = secondBack;
        }

        private void AddStripCapQuad(
            int column,
            int firstRow,
            int secondRow,
            ref int triangle)
        {
            int firstFront = StripIndex(column, firstRow, 0);
            int firstBack = StripIndex(column, firstRow, 1);
            int secondFront = StripIndex(column, secondRow, 0);
            int secondBack = StripIndex(column, secondRow, 1);
            stripTriangles[2][triangle++] = firstFront;
            stripTriangles[2][triangle++] = secondFront;
            stripTriangles[2][triangle++] = firstBack;
            stripTriangles[2][triangle++] = firstBack;
            stripTriangles[2][triangle++] = secondFront;
            stripTriangles[2][triangle++] = secondBack;
        }

        private void UpdateStripMesh(PackOpeningGate04R010Sample sample)
        {
            maximumAheadOfFrontSeparation = 0f;
            for (int column = 0; column <= StripSegments; column++)
            {
                float column01 = column / (float)StripSegments;
                float originalX = Mathf.Lerp(
                    -PackHalfWidth,
                    PackHalfWidth,
                    column01);
                bool released =
                    sample.TearProgress > 0.0001f
                    && (
                        sample.TearProgress >= 0.999f
                        || originalX > TearFrontXLocal
                    );
                Vector3 center;
                Vector3 tangent;
                Vector3 widthDirection;
                Vector3 surfaceNormal;
                if (!released && sample.TearProgress < 0.999f)
                {
                    center = new Vector3(
                        originalX,
                        TearSeamY + tearOffsets[column] + StripHeight * 0.5f,
                        PackPlaneZ);
                    tangent = Vector3.right;
                    widthDirection = Vector3.up;
                    surfaceNormal = Vector3.forward;
                }
                else
                {
                    float tail = Mathf.Clamp01(
                        (originalX - TearFrontXLocal)
                        / Mathf.Max(0.0001f, PackHalfWidth - TearFrontXLocal));
                    EvaluateTailFrame(
                        TearFrontXLocal,
                        tail,
                        sample.TearProgress,
                        out center,
                        out tangent,
                        out widthDirection,
                        out surfaceNormal);
                    float retreat = sample.PackRetreat;
                    center += new Vector3(
                        retreat * (0.115f + 0.145f * tail),
                        retreat * (0.160f + 0.180f * tail),
                        -retreat * (0.018f + 0.030f * tail));
                }

                for (int row = 0; row <= StripRows; row++)
                {
                    float row01 = row / (float)StripRows;
                    float widthOffset = (row01 - 0.5f) * StripHeight;
                    Vector3 centerAtRow = center + widthDirection * widthOffset;
                    int frontIndex = StripIndex(column, row, 0);
                    int backIndex = StripIndex(column, row, 1);
                    stripVertices[frontIndex] =
                        centerAtRow - surfaceNormal * (StripThickness * 0.5f);
                    stripVertices[backIndex] =
                        centerAtRow + surfaceNormal * (StripThickness * 0.5f);
                    Vector2 uv = new Vector2(
                        column01,
                        Mathf.Lerp(FlapUvMin, FlapUvMax, row01));
                    stripUvs[frontIndex] = uv;
                    stripUvs[backIndex] = uv;
                    stripColors[frontIndex] = Color.white;
                    stripColors[backIndex] = Color.white;
                }

                if (!released)
                {
                    Vector3 stripBottom =
                        (stripVertices[StripIndex(column, 0, 0)]
                        + stripVertices[StripIndex(column, 0, 1)]) * 0.5f;
                    Vector3 bodyTop = bodyVertices[BodyIndex(column, BodyRows)];
                    maximumAheadOfFrontSeparation = Mathf.Max(
                        maximumAheadOfFrontSeparation,
                        Vector3.Distance(stripBottom, bodyTop));
                }
            }

            stripMesh.vertices = stripVertices;
            stripMesh.uv = stripUvs;
            stripMesh.colors = stripColors;
            stripMesh.RecalculateNormals();
            stripMesh.RecalculateBounds();
        }

        private void EvaluateTailFrame(
            float front,
            float tail,
            float tearProgress,
            out Vector3 center,
            out Vector3 tangent,
            out Vector3 widthDirection,
            out Vector3 surfaceNormal)
        {
            float frontOffset = TearOffsetAtX(front);
            float freeLength = Mathf.Max(0.001f, PackHalfWidth - front);
            Vector3 p0 = new Vector3(
                front,
                TearSeamY + frontOffset + StripHeight * 0.5f,
                PackPlaneZ);
            Vector3 p1 = p0 + new Vector3(
                Mathf.Min(0.052f, freeLength * 0.24f),
                0.010f + tearProgress * 0.012f,
                -0.006f);
            Vector3 p2 = new Vector3(
                PackHalfWidth + 0.016f + tearProgress * 0.007f,
                TearSeamY + StripHeight * 0.5f
                    + 0.050f + tearProgress * 0.040f,
                -0.023f - tearProgress * 0.022f);
            Vector3 p3 = new Vector3(
                PackHalfWidth - 0.028f - tearProgress * 0.078f,
                TearSeamY + StripHeight * 0.5f
                    + 0.056f + tearProgress * 0.025f,
                -0.014f - tearProgress * 0.043f);
            center = CubicBezier(p0, p1, p2, p3, tail);
            tangent = CubicBezierTangent(p0, p1, p2, p3, tail).normalized;
            float twistDegrees = Smooth01(tail)
                * Mathf.Lerp(56f, 168f, tearProgress);
            widthDirection =
                Quaternion.AngleAxis(twistDegrees, tangent) * Vector3.up;
            widthDirection = Vector3.ProjectOnPlane(widthDirection, tangent)
                .normalized;
            if (widthDirection.sqrMagnitude < 0.5f)
            {
                widthDirection = Vector3.up;
            }
            surfaceNormal = Vector3.Cross(tangent, widthDirection).normalized;
            if (surfaceNormal.sqrMagnitude < 0.5f)
            {
                surfaceNormal = Vector3.forward;
            }
        }

        private Vector3 EvaluateTailPoint(
            float front,
            float tail,
            float tearProgress)
        {
            EvaluateTailFrame(
                front,
                tail,
                tearProgress,
                out Vector3 center,
                out _,
                out _,
                out _);
            return center;
        }

        private void BuildCavityMesh()
        {
            cavityMesh = new Mesh
            {
                name = "Gate04R010ShapedParallaxCavity"
            };
            cavityMesh.MarkDynamic();
            cavityMesh.vertices = cavityVertices;
            cavityMesh.uv = cavityUvs;
            cavityMesh.triangles = Array.Empty<int>();
            cavityMeshFilter.sharedMesh = cavityMesh;
        }

        private void UpdateCavityMesh(PackOpeningGate04R010Sample sample)
        {
            cavityTriangles.Clear();
            for (int column = 0; column <= StripSegments; column++)
            {
                float column01 = column / (float)StripSegments;
                float x = Mathf.Lerp(-PackHalfWidth, PackHalfWidth, column01);
                bool released =
                    sample.TearProgress >= 0.999f
                    || x > TearFrontXLocal;
                float release = released
                    ? Mathf.Clamp01(
                        (x - TearFrontXLocal)
                        / Mathf.Max(0.0001f, PackHalfWidth - TearFrontXLocal))
                    : 0f;
                float openedBehindFront = released
                    ? Smooth01(Mathf.InverseLerp(0f, 0.16f, release))
                    : 0f;
                float bodyTop = TearSeamY
                    + tearOffsets[column]
                    - ApertureDepth
                        * sample.ApertureProgress
                        * openedBehindFront;
                float fold = 0.0016f * Mathf.Sin(column * 1.19f + 0.7f);
                int index = column * 4;
                cavityVertices[index] = new Vector3(
                    x,
                    bodyTop + 0.0012f,
                    PackPlaneZ + 0.0006f);
                cavityVertices[index + 1] = new Vector3(
                    x,
                    bodyTop + 0.006f + fold,
                    PackPlaneZ + 0.020f);
                cavityVertices[index + 2] = new Vector3(
                    x,
                    bodyTop - 0.013f + fold * 0.55f,
                    PackPlaneZ + 0.030f);
                cavityVertices[index + 3] = new Vector3(
                    x,
                    bodyTop - 0.004f,
                    PackPlaneZ + 0.0022f);
                cavityUvs[index] = new Vector2(column01, 1f);
                cavityUvs[index + 1] = new Vector2(column01, 0.72f);
                cavityUvs[index + 2] = new Vector2(column01, 0f);
                cavityUvs[index + 3] = new Vector2(column01, 0.28f);
            }

            for (int column = 0; column < StripSegments; column++)
            {
                float midpoint = Mathf.Lerp(
                    -PackHalfWidth,
                    PackHalfWidth,
                    (column + 0.5f) / StripSegments);
                if (
                    sample.TearProgress < 0.999f
                    && midpoint <= TearFrontXLocal
                )
                {
                    continue;
                }
                int current = column * 4;
                int next = (column + 1) * 4;
                for (int row = 0; row < 3; row++)
                {
                    cavityTriangles.Add(current + row);
                    cavityTriangles.Add(next + row);
                    cavityTriangles.Add(current + row + 1);
                    cavityTriangles.Add(current + row + 1);
                    cavityTriangles.Add(next + row);
                    cavityTriangles.Add(next + row + 1);
                }
            }

            cavityMesh.Clear(false);
            cavityMesh.vertices = cavityVertices;
            cavityMesh.uv = cavityUvs;
            cavityMesh.SetTriangles(cavityTriangles, 0);
            cavityMesh.RecalculateNormals();
            cavityMesh.RecalculateBounds();
        }

        private void BuildContactShadowMesh()
        {
            contactShadowMesh = new Mesh
            {
                name = "Gate04R010RestrainedContactShadow"
            };
            contactShadowMesh.vertices = contactShadowVertices;
            contactShadowMesh.uv = contactShadowUvs;
            contactShadowMesh.triangles = contactShadowTriangles;
            contactShadowMeshFilter.sharedMesh = contactShadowMesh;
        }

        private void UpdateContactShadow(PackOpeningGate04R010Sample sample)
        {
            float front = TearFrontXLocal;
            float x0 = Mathf.Max(-PackHalfWidth, front - 0.012f);
            float x1 = Mathf.Min(PackHalfWidth, front + 0.038f);
            float y = TearSeamY + TearOffsetAtX(front) - 0.0045f
                - sample.ApertureProgress * 0.010f;
            contactShadowVertices[0] = new Vector3(x0, y - 0.004f, -0.0011f);
            contactShadowVertices[1] = new Vector3(x0, y + 0.003f, -0.0011f);
            contactShadowVertices[2] = new Vector3(x1, y - 0.005f, -0.0011f);
            contactShadowVertices[3] = new Vector3(x1, y + 0.002f, -0.0011f);
            contactShadowMesh.vertices = contactShadowVertices;
            contactShadowMesh.RecalculateBounds();
        }

        private void BuildSpecularMesh()
        {
            specularMesh = new Mesh
            {
                name = "Gate04R010MovingNarrowFoilSpecular"
            };
            specularMesh.vertices = specularVertices;
            specularMesh.uv = specularUvs;
            specularMesh.triangles = specularTriangles;
            specularMeshFilter.sharedMesh = specularMesh;
        }

        private void UpdateSpecularHighlight(PackOpeningGate04R010Sample sample)
        {
            float center = Mathf.Lerp(0.24f, 0.70f, sample.TearProgress);
            float s0 = Mathf.Clamp01(center - 0.090f);
            float s1 = Mathf.Clamp01(center + 0.090f);
            EvaluateTailFrame(
                TearFrontXLocal,
                s0,
                sample.TearProgress,
                out Vector3 center0,
                out _,
                out Vector3 width0,
                out Vector3 normal0);
            EvaluateTailFrame(
                TearFrontXLocal,
                s1,
                sample.TearProgress,
                out Vector3 center1,
                out _,
                out Vector3 width1,
                out Vector3 normal1);
            float halfWidth = StripHeight * 0.060f;
            specularVertices[0] =
                center0 - width0 * halfWidth - normal0 * 0.00055f;
            specularVertices[1] =
                center0 + width0 * halfWidth - normal0 * 0.00055f;
            specularVertices[2] =
                center1 - width1 * halfWidth - normal1 * 0.00055f;
            specularVertices[3] =
                center1 + width1 * halfWidth - normal1 * 0.00055f;
            specularMesh.vertices = specularVertices;
            specularMesh.RecalculateNormals();
            specularMesh.RecalculateBounds();
        }

        private float TearOffsetAtX(float x)
        {
            float normalized = Mathf.InverseLerp(
                -PackHalfWidth,
                PackHalfWidth,
                x);
            float scaled = normalized * StripSegments;
            int lower = Mathf.Clamp(Mathf.FloorToInt(scaled), 0, StripSegments);
            int upper = Mathf.Min(StripSegments, lower + 1);
            return Mathf.Lerp(tearOffsets[lower], tearOffsets[upper], scaled - lower);
        }

        private string BuildStateFingerprint()
        {
            if (!initialized)
            {
                return string.Empty;
            }
            var builder = new StringBuilder(32768);
            AppendVector(builder, cameraBasePosition);
            AppendVector(builder, captureCamera.transform.position);
            AppendQuaternion(builder, captureCamera.transform.rotation);
            AppendFloat(builder, captureCamera.fieldOfView);
            AppendVector(builder, packRoot.localScale);
            AppendVector(builder, caseMotionRoot.localPosition);
            AppendQuaternion(builder, caseMotionRoot.localRotation);
            AppendVector(builder, caseMotionRoot.localScale);
            AppendFloat(builder, openingLight.intensity);
            AppendColor(builder, openingLight.color);
            builder.Append((int)openingLight.shadows).Append('|');
            builder.Append(packBodyRenderer.enabled ? '1' : '0');
            builder.Append(tearStripRenderer.enabled ? '1' : '0');
            builder.Append(cavityRenderer.enabled ? '1' : '0');
            builder.Append(contactShadowRenderer.enabled ? '1' : '0');
            builder.Append(specularRenderer.enabled ? '1' : '0');
            builder.Append(localizedFlash.gameObject.activeSelf ? '1' : '0');
            builder.Append(energyRing.gameObject.activeSelf ? '1' : '0');
            for (int index = 0; index < caseTextRenderers.Length; index++)
            {
                builder.Append(
                    caseTextRenderers[index] != null
                    && caseTextRenderers[index].enabled
                        ? '1'
                        : '0');
            }
            builder.Append('|')
                .Append((int)packBodyRenderer.shadowCastingMode)
                .Append('|')
                .Append((int)tearStripRenderer.shadowCastingMode)
                .Append('|')
                .Append((int)cavityRenderer.shadowCastingMode);
            builder.Append('|').Append(bodyMesh.GetIndexCount(0));
            builder.Append('|').Append(cavityMesh.GetIndexCount(0));
            AppendRendererProperties(
                builder,
                environmentRenderer,
                includeTexture: true);
            AppendRendererProperties(
                builder,
                localizedFlashRenderer,
                includeTexture: false);
            AppendRendererProperties(
                builder,
                energyRingRenderer,
                includeTexture: false);
            for (int index = 0; index < casePresentation.EffectRenderers.Count; index++)
            {
                AppendRendererProperties(
                    builder,
                    casePresentation.EffectRenderers[index],
                    includeTexture: false);
            }
            AppendVertices(builder, bodyVertices);
            AppendVertices(builder, stripVertices);
            AppendVertices(builder, cavityVertices);
            AppendVertices(builder, contactShadowVertices);
            AppendVertices(builder, specularVertices);
            AppendFloat(builder, maximumAheadOfFrontSeparation);
            return builder.ToString();
        }

        private static void AppendRendererProperties(
            StringBuilder builder,
            Renderer renderer,
            bool includeTexture)
        {
            if (renderer == null)
            {
                builder.Append("null|");
                return;
            }
            var properties = new MaterialPropertyBlock();
            renderer.GetPropertyBlock(properties);
            AppendColor(builder, properties.GetColor(BaseColorId));
            AppendFloat(builder, properties.GetFloat(SaturationId));
            AppendFloat(builder, properties.GetFloat(OpacityId));
            AppendFloat(builder, properties.GetFloat(SheenCenterId));
            AppendFloat(builder, properties.GetFloat(SheenWidthId));
            AppendFloat(builder, properties.GetFloat(SheenStrengthId));
            AppendFloat(builder, properties.GetFloat(SheenFalloffId));
            if (includeTexture)
            {
                Texture texture = properties.GetTexture(BaseMapId);
                builder.Append(texture != null ? texture.name : "null")
                    .Append('|');
            }
        }

        private static void AppendVertices(StringBuilder builder, Vector3[] vertices)
        {
            for (int index = 0; index < vertices.Length; index++)
            {
                AppendVector(builder, vertices[index]);
            }
        }

        private static void AppendVector(StringBuilder builder, Vector3 value)
        {
            AppendFloat(builder, value.x);
            AppendFloat(builder, value.y);
            AppendFloat(builder, value.z);
        }

        private static void AppendQuaternion(StringBuilder builder, Quaternion value)
        {
            AppendFloat(builder, value.x);
            AppendFloat(builder, value.y);
            AppendFloat(builder, value.z);
            AppendFloat(builder, value.w);
        }

        private static void AppendColor(StringBuilder builder, Color value)
        {
            AppendFloat(builder, value.r);
            AppendFloat(builder, value.g);
            AppendFloat(builder, value.b);
            AppendFloat(builder, value.a);
        }

        private static void AppendFloat(StringBuilder builder, float value)
        {
            builder.Append(value.ToString("R", CultureInfo.InvariantCulture))
                .Append('|');
        }

        private void SetAccentColor(Renderer renderer, Color color)
        {
            renderer.GetPropertyBlock(accentProperties);
            accentProperties.SetColor(BaseColorId, color);
            renderer.SetPropertyBlock(accentProperties);
        }

        private static void SimulateImpactSystem(
            ParticleSystem system,
            bool enabled,
            float age)
        {
            system.Stop(
                true,
                ParticleSystemStopBehavior.StopEmittingAndClear);
            if (!enabled || age < 0f)
            {
                return;
            }
            system.Simulate(age, true, true, true);
            system.Pause(true);
        }

        private static void StopParticles(ParticleSystem system)
        {
            if (system == null)
            {
                return;
            }
            system.Stop(
                true,
                ParticleSystemStopBehavior.StopEmittingAndClear);
        }

        private static Vector3 CubicBezier(
            Vector3 p0,
            Vector3 p1,
            Vector3 p2,
            Vector3 p3,
            float value)
        {
            float t = Mathf.Clamp01(value);
            float inverse = 1f - t;
            return inverse * inverse * inverse * p0
                + 3f * inverse * inverse * t * p1
                + 3f * inverse * t * t * p2
                + t * t * t * p3;
        }

        private static Vector3 CubicBezierTangent(
            Vector3 p0,
            Vector3 p1,
            Vector3 p2,
            Vector3 p3,
            float value)
        {
            float t = Mathf.Clamp01(value);
            float inverse = 1f - t;
            return 3f * inverse * inverse * (p1 - p0)
                + 6f * inverse * t * (p2 - p1)
                + 3f * t * t * (p3 - p2);
        }

        private static float Smooth01(float value)
        {
            float clamped = Mathf.Clamp01(value);
            return clamped * clamped * (3f - 2f * clamped);
        }

        private static float EaseOutQuart(float value)
        {
            float clamped = Mathf.Clamp01(value);
            return 1f - Mathf.Pow(1f - clamped, 4f);
        }

        private static int BodyIndex(int column, int row)
        {
            return column * (BodyRows + 1) + row;
        }

        private static int StripIndex(int column, int row, int side)
        {
            return (column * (StripRows + 1) + row) * 2 + side;
        }

        private static void DestroyOwned(UnityEngine.Object value)
        {
            if (value == null)
            {
                return;
            }
            if (Application.isPlaying)
            {
                Destroy(value);
            }
            else
            {
                DestroyImmediate(value);
            }
        }
    }
}
