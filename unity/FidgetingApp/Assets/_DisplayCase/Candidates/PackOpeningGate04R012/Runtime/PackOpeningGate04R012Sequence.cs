using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Candidates
{
    [DisallowMultipleComponent]
    public sealed class PackOpeningGate04R012Sequence : MonoBehaviour
    {
        private static readonly int DissolveId = Shader.PropertyToID("_Dissolve");
        private static readonly int TearSweepId = Shader.PropertyToID("_TearSweep");
        private static readonly int ProgressId = Shader.PropertyToID("_Progress");
        private static readonly int SheenCenterId =
            Shader.PropertyToID("_SheenCenter");
        private static readonly int SheenWidthId =
            Shader.PropertyToID("_SheenWidth");
        private static readonly int SheenStrengthId =
            Shader.PropertyToID("_SheenStrength");
        private static readonly int SheenFalloffId =
            Shader.PropertyToID("_SheenFalloff");

        public const int LongitudinalSegments = 128;
        public const int BodyRows = 28;
        public const int StripRows = 12;
        public const float PackWidth = 0.255f;
        public const float PackHeight = 0.340f;
        public const float PackHalfWidth = PackWidth * 0.47f;
        public const float PackBottomY = -PackHeight * 0.5f;
        public const float SealedRimY = PackHeight * 0.320f;
        public const float RearRimTopY = SealedRimY + 0.022f;
        public const float MouthMaximumHeight = 0.078f;
        public const float InnerLipDepth = 0.017f;
        public const float FoilStripWidth = 0.014f;
        public const float FoilStripThickness = 0.0008f;
        public const float TearContourMaximumAmplitude = 0.00105f;
        public const float CaseScale = 1.02f;

        private const float BackLayerCoincidentOffset = 0.00008f;
        private const float RearRimDepth = 0.058f;
        private const float OpeningTransitionMeters = 0.022f;
        private const float CavityBackClearance = 0.024f;
        private const float FlapUvMin = 1f - 96f / 512f;
        private const float FlapUvMax = 1f - 57f / 512f;

        [SerializeField] private PackOpeningGate04R012Profile profile;
        [SerializeField] private Camera captureCamera;
        [SerializeField] private Transform packRoot;
        [SerializeField] private MeshFilter frontLayerFilter;
        [SerializeField] private Renderer frontLayerRenderer;
        [SerializeField] private MeshFilter sealedBackLayerFilter;
        [SerializeField] private Renderer sealedBackLayerRenderer;
        [SerializeField] private MeshFilter rearRimFilter;
        [SerializeField] private Renderer rearRimRenderer;
        [SerializeField] private MeshFilter stripFilter;
        [SerializeField] private Renderer stripRenderer;
        [SerializeField] private MeshFilter cavityFilter;
        [SerializeField] private Renderer cavityRenderer;
        [SerializeField] private Transform pullTab;
        [SerializeField] private Renderer pullTabRenderer;
        [SerializeField] private Transform caseMotionRoot;
        [SerializeField] private PremiumDisplayCaseShippingPresentation casePresentation;
        [SerializeField] private Transform sourceEffectsRoot;
        [SerializeField] private ParticleSystem[] sourceEffectSystems =
            Array.Empty<ParticleSystem>();

        private readonly float[] tearOffsets = new float[LongitudinalSegments + 1];
        private readonly Vector3[] frontVertices =
            new Vector3[(LongitudinalSegments + 1) * (BodyRows + 1)];
        private readonly Vector2[] frontUvs =
            new Vector2[(LongitudinalSegments + 1) * (BodyRows + 1)];
        private readonly Vector2[] frontContourUvs =
            new Vector2[(LongitudinalSegments + 1) * (BodyRows + 1)];
        private readonly Vector2[] frontOpenUvs =
            new Vector2[(LongitudinalSegments + 1) * (BodyRows + 1)];
        private readonly int[] frontTriangles =
            new int[LongitudinalSegments * BodyRows * 6];
        private readonly Vector3[] sealedBackVertices =
            new Vector3[(LongitudinalSegments + 1) * (BodyRows + 1)];
        private readonly List<int> sealedBackTriangles =
            new List<int>(LongitudinalSegments * BodyRows * 6);
        private readonly Vector3[] rearRimVertices =
            new Vector3[(LongitudinalSegments + 1) * 2];
        private readonly Vector2[] rearRimUvs =
            new Vector2[(LongitudinalSegments + 1) * 2];
        private readonly int[] rearRimTriangles =
            new int[LongitudinalSegments * 6];
        private readonly Vector3[] stripVertices =
            new Vector3[(LongitudinalSegments + 1) * (StripRows + 1) * 2];
        private readonly Vector2[] stripUvs =
            new Vector2[(LongitudinalSegments + 1) * (StripRows + 1) * 2];
        private readonly List<int> stripFrontTriangles =
            new List<int>(LongitudinalSegments * StripRows * 6);
        private readonly List<int> stripUndersideTriangles =
            new List<int>(LongitudinalSegments * StripRows * 6);
        private readonly List<int> stripEdgeTriangles =
            new List<int>(LongitudinalSegments * 12);
        private readonly List<Vector3> cavityVertices =
            new List<Vector3>(LongitudinalSegments * 16);
        private readonly List<Vector2> cavityUvs =
            new List<Vector2>(LongitudinalSegments * 16);
        private readonly List<int> cavityInteriorTriangles =
            new List<int>(LongitudinalSegments * 24);
        private readonly List<int> cavityContactTriangles =
            new List<int>(LongitudinalSegments * 18);

        private Mesh frontMesh;
        private Mesh sealedBackMesh;
        private Mesh rearRimMesh;
        private Mesh stripMesh;
        private Mesh cavityMesh;
        private MaterialPropertyBlock packProperties;
        private MaterialPropertyBlock sourceProperties;
        private MaterialPropertyBlock caseProperties;
        private Renderer[] caseRenderers = Array.Empty<Renderer>();
        private Renderer[] caseTextRenderers = Array.Empty<Renderer>();
        private EntityId[] caseRendererIds = Array.Empty<EntityId>();
        private Vector3 cameraBasePosition;
        private Quaternion cameraBaseRotation;
        private float cameraBaseFov;
        private Vector3 packBasePosition;
        private Vector3 caseBasePosition;
        private Quaternion caseBaseRotation;
        private Vector3 caseBaseScale;
        private float cavityBackWallLocalZ;
        private bool initialized;
        private string sealedStateFingerprint = string.Empty;

        public PackOpeningGate04R012Profile Profile => profile;
        public PackOpeningGate04R012Sample CurrentSample { get; private set; }
        public float ElapsedSeconds { get; private set; }
        public float TearFrontXLocal { get; private set; } = PackHalfWidth;
        public int CavityVisibleColumnCount { get; private set; }
        public float CavityMaximumOpenHeight { get; private set; }
        public float MaximumAheadLayerSeparation { get; private set; }
        public float FoilMaximumCrossCurl { get; private set; }
        public float CavityBackWallLocalZ => cavityBackWallLocalZ;
        public bool PackVisible =>
            frontLayerRenderer != null && frontLayerRenderer.enabled;
        public EntityId CaseRootEntityId =>
            caseMotionRoot == null ? EntityId.None : caseMotionRoot.GetEntityId();
        public IReadOnlyList<EntityId> CaseRendererIds => caseRendererIds;
        public IReadOnlyList<float> TearOffsets => tearOffsets;
        public IReadOnlyList<ParticleSystem> SourceEffectSystems =>
            sourceEffectSystems;
        public PremiumDisplayCaseShippingPresentation CasePresentation =>
            casePresentation;
        public Transform CaseMotionRoot => caseMotionRoot;
        public Vector3 CaseAuthoredScale => caseBaseScale;
        public string SealedStateFingerprint => sealedStateFingerprint;
        public string CurrentStateFingerprint => BuildStateFingerprint();

        public bool HasRequiredBindings =>
            profile != null
            && captureCamera != null
            && packRoot != null
            && frontLayerFilter != null
            && frontLayerRenderer != null
            && sealedBackLayerFilter != null
            && sealedBackLayerRenderer != null
            && rearRimFilter != null
            && rearRimRenderer != null
            && stripFilter != null
            && stripRenderer != null
            && cavityFilter != null
            && cavityRenderer != null
            && pullTab != null
            && pullTabRenderer != null
            && caseMotionRoot != null
            && casePresentation != null
            && sourceEffectsRoot != null
            && sourceEffectSystems != null
            && sourceEffectSystems.All(system => system != null);

        public void Configure(
            PackOpeningGate04R012Profile authoredProfile,
            Camera authoredCamera,
            Transform authoredPackRoot,
            MeshFilter authoredFrontLayerFilter,
            Renderer authoredFrontLayerRenderer,
            MeshFilter authoredSealedBackLayerFilter,
            Renderer authoredSealedBackLayerRenderer,
            MeshFilter authoredRearRimFilter,
            Renderer authoredRearRimRenderer,
            MeshFilter authoredStripFilter,
            Renderer authoredStripRenderer,
            MeshFilter authoredCavityFilter,
            Renderer authoredCavityRenderer,
            Transform authoredPullTab,
            Renderer authoredPullTabRenderer,
            Transform authoredCaseMotionRoot,
            PremiumDisplayCaseShippingPresentation authoredCasePresentation,
            Transform authoredSourceEffectsRoot,
            ParticleSystem[] authoredSourceEffectSystems)
        {
            profile = authoredProfile;
            captureCamera = authoredCamera;
            packRoot = authoredPackRoot;
            frontLayerFilter = authoredFrontLayerFilter;
            frontLayerRenderer = authoredFrontLayerRenderer;
            sealedBackLayerFilter = authoredSealedBackLayerFilter;
            sealedBackLayerRenderer = authoredSealedBackLayerRenderer;
            rearRimFilter = authoredRearRimFilter;
            rearRimRenderer = authoredRearRimRenderer;
            stripFilter = authoredStripFilter;
            stripRenderer = authoredStripRenderer;
            cavityFilter = authoredCavityFilter;
            cavityRenderer = authoredCavityRenderer;
            pullTab = authoredPullTab;
            pullTabRenderer = authoredPullTabRenderer;
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

        private void OnDestroy()
        {
            DestroyOwned(frontMesh);
            DestroyOwned(sealedBackMesh);
            DestroyOwned(rearRimMesh);
            DestroyOwned(stripMesh);
            DestroyOwned(cavityMesh);
        }

        public void SetTime(float elapsedSeconds, bool reduceMotion)
        {
            Initialize();
            if (!HasRequiredBindings)
            {
                throw new MissingReferenceException(
                    "Gate 04 rev 12 sequence bindings are incomplete.");
            }

            ElapsedSeconds = Mathf.Clamp(
                elapsedSeconds,
                0f,
                PackOpeningGate04R012Profile.TotalSeconds);
            CurrentSample = profile.Evaluate(ElapsedSeconds, reduceMotion);
            TearFrontXLocal = Mathf.Lerp(
                PackHalfWidth,
                -PackHalfWidth,
                CurrentSample.TearProgress);
            ApplyPack(CurrentSample);
            ApplyCase(CurrentSample);
            ApplySourceEffects(CurrentSample);
            ApplyCamera(CurrentSample);
            if (ElapsedSeconds <= 0f
                && string.IsNullOrEmpty(sealedStateFingerprint))
            {
                sealedStateFingerprint = BuildStateFingerprint();
            }
        }

        public bool ReboundToSealed()
        {
            SetTime(0f, false);
            StopSourceEffects();
            string current = BuildStateFingerprint();
            bool restored = string.Equals(
                current,
                sealedStateFingerprint,
                StringComparison.Ordinal);
            if (!restored)
            {
                int mismatch = FirstMismatch(
                    sealedStateFingerprint,
                    current);
                Debug.LogWarning(
                    $"Gate 04 R012 sealed rebound mismatch at {mismatch}: "
                    + $"expected={FingerprintWindow(sealedStateFingerprint, mismatch)} "
                    + $"actual={FingerprintWindow(current, mismatch)}");
            }
            return restored;
        }

        public bool TryGetCaseViewportBounds(out Rect viewportBounds)
        {
            return TryGetViewportBounds(caseRenderers, out viewportBounds);
        }

        public bool TryGetPackViewportBounds(out Rect viewportBounds)
        {
            var renderers = new[]
            {
                frontLayerRenderer,
                sealedBackLayerRenderer,
                rearRimRenderer,
                stripRenderer,
                cavityRenderer,
                pullTabRenderer
            };
            return TryGetViewportBounds(renderers, out viewportBounds);
        }

        public float CaseRearWorldZ
        {
            get
            {
                if (!TryGetWorldBounds(caseRenderers, out Bounds bounds))
                {
                    return float.NaN;
                }
                return bounds.max.z;
            }
        }

        public float CavityBackWallWorldZ =>
            packRoot == null
                ? cavityBackWallLocalZ
                : packRoot.TransformPoint(
                    new Vector3(0f, 0f, cavityBackWallLocalZ)).z;

        public float MeasureFoilTailCurvature()
        {
            if (CurrentSample.TearProgress <= 0.02f)
            {
                return 0f;
            }

            Vector3 a = EvaluateStripSpine(0.30f, CurrentSample);
            Vector3 b = EvaluateStripSpine(0.50f, CurrentSample);
            Vector3 c = EvaluateStripSpine(0.70f, CurrentSample);
            return (a - 2f * b + c).magnitude;
        }

        private void Initialize()
        {
            if (initialized || !HasRequiredBindings)
            {
                return;
            }

            GenerateTearContour();
            cameraBasePosition = captureCamera.transform.position;
            cameraBaseRotation = captureCamera.transform.rotation;
            cameraBaseFov = captureCamera.fieldOfView;
            packBasePosition = packRoot.localPosition;
            caseBasePosition = caseMotionRoot.localPosition;
            caseBaseRotation = caseMotionRoot.localRotation;
            caseBaseScale = caseMotionRoot.localScale;
            packProperties = new MaterialPropertyBlock();
            sourceProperties = new MaterialPropertyBlock();
            caseProperties = new MaterialPropertyBlock();
            BuildStaticMeshes();
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
            cavityBackWallLocalZ = ResolveCavityBackWallLocalZ();
            StopSourceEffects();
            initialized = true;
        }

        private void BuildStaticMeshes()
        {
            frontMesh = new Mesh { name = "Gate04R012FineTearFrontLayer" };
            frontMesh.MarkDynamic();
            int triangle = 0;
            for (int column = 0; column < LongitudinalSegments; column++)
            {
                for (int row = 0; row < BodyRows; row++)
                {
                    int lower = BodyIndex(column, row);
                    int upper = BodyIndex(column, row + 1);
                    int nextLower = BodyIndex(column + 1, row);
                    int nextUpper = BodyIndex(column + 1, row + 1);
                    frontTriangles[triangle++] = lower;
                    frontTriangles[triangle++] = upper;
                    frontTriangles[triangle++] = nextLower;
                    frontTriangles[triangle++] = nextLower;
                    frontTriangles[triangle++] = upper;
                    frontTriangles[triangle++] = nextUpper;
                }
            }
            frontLayerFilter.sharedMesh = frontMesh;

            sealedBackMesh = new Mesh
            {
                name = "Gate04R012CoincidentSealedBackLayer"
            };
            sealedBackMesh.MarkDynamic();
            sealedBackLayerFilter.sharedMesh = sealedBackMesh;

            rearRimMesh = new Mesh { name = "Gate04R012RearFoilRim" };
            int rimTriangle = 0;
            for (int column = 0; column < LongitudinalSegments; column++)
            {
                int bottom = RearRimIndex(column, 0);
                int top = RearRimIndex(column, 1);
                int nextBottom = RearRimIndex(column + 1, 0);
                int nextTop = RearRimIndex(column + 1, 1);
                rearRimTriangles[rimTriangle++] = bottom;
                rearRimTriangles[rimTriangle++] = top;
                rearRimTriangles[rimTriangle++] = nextBottom;
                rearRimTriangles[rimTriangle++] = nextBottom;
                rearRimTriangles[rimTriangle++] = top;
                rearRimTriangles[rimTriangle++] = nextTop;
            }
            rearRimMesh.vertices = rearRimVertices;
            rearRimMesh.uv = rearRimUvs;
            rearRimMesh.triangles = rearRimTriangles;
            rearRimFilter.sharedMesh = rearRimMesh;

            stripMesh = new Mesh
            {
                name = "Gate04R012CurledNarrowTornSeal",
                subMeshCount = 3
            };
            stripMesh.MarkDynamic();
            stripFilter.sharedMesh = stripMesh;

            cavityMesh = new Mesh
            {
                name = "Gate04R012DeepPhysicalMouth",
                subMeshCount = 2
            };
            cavityMesh.MarkDynamic();
            cavityFilter.sharedMesh = cavityMesh;
        }

        private void ApplyPack(PackOpeningGate04R012Sample sample)
        {
            bool visible = sample.PackDissolve < 0.99995f;
            frontLayerRenderer.enabled = visible;
            sealedBackLayerRenderer.enabled = visible;
            rearRimRenderer.enabled = visible;
            stripRenderer.enabled = visible && sample.TearProgress > 0.006f;
            pullTabRenderer.enabled = visible;
            cavityRenderer.enabled = visible && sample.ApertureProgress > 0.008f;

            float retreat = sample.PackRetreat;
            packRoot.localPosition = packBasePosition + new Vector3(
                -0.008f * retreat,
                -0.011f * retreat,
                -0.006f * retreat);
            ApplyPackProperties(frontLayerRenderer, sample);
            ApplyPackProperties(sealedBackLayerRenderer, sample);
            UpdateFrontAndSealedBack(sample);
            UpdateRearRim(sample);
            UpdateCavity(sample);
            UpdateTearStrip(sample);
            UpdatePullTab(sample);
        }

        private void ApplyPackProperties(
            Renderer renderer,
            PackOpeningGate04R012Sample sample)
        {
            renderer.GetPropertyBlock(packProperties);
            packProperties.SetFloat(DissolveId, sample.PackDissolve);
            packProperties.SetFloat(TearSweepId, sample.SourceSweep);
            renderer.SetPropertyBlock(packProperties);
        }

        private void UpdateFrontAndSealedBack(PackOpeningGate04R012Sample sample)
        {
            sealedBackTriangles.Clear();
            MaximumAheadLayerSeparation = 0f;
            for (int column = 0; column <= LongitudinalSegments; column++)
            {
                float column01 = column / (float)LongitudinalSegments;
                float x = Mathf.Lerp(-PackHalfWidth, PackHalfWidth, column01);
                float release = ReleaseAtX(sample, x);
                float frontTop = FrontTopAtX(sample, x);
                for (int row = 0; row <= BodyRows; row++)
                {
                    float row01 = row / (float)BodyRows;
                    float topInfluence = Mathf.Pow(row01, 3.7f);
                    float y = Mathf.Lerp(PackBottomY, SealedRimY, row01)
                        + (frontTop - SealedRimY) * topInfluence;
                    int index = BodyIndex(column, row);
                    frontVertices[index] = new Vector3(x, y, 0f);
                    frontUvs[index] = new Vector2(
                        column01,
                        Mathf.Lerp(0f, 1f - 92f / 512f, row01));
                    float contourDepth = (frontTop - y)
                        / Mathf.Max(0.001f, frontTop - PackBottomY);
                    frontContourUvs[index] = new Vector2(
                        Mathf.Clamp01(contourDepth),
                        release);
                    frontOpenUvs[index] = new Vector2(
                        tearOffsets[column] / TearContourMaximumAmplitude,
                        release);
                    sealedBackVertices[index] = new Vector3(
                        x,
                        y,
                        BackLayerCoincidentOffset);
                    if (x < TearFrontXLocal - 0.0005f)
                    {
                        MaximumAheadLayerSeparation = Mathf.Max(
                            MaximumAheadLayerSeparation,
                            Vector3.Distance(
                                frontVertices[index],
                                sealedBackVertices[index]));
                    }
                }
            }

            for (int column = 0; column < LongitudinalSegments; column++)
            {
                float x0 = Mathf.Lerp(
                    -PackHalfWidth,
                    PackHalfWidth,
                    column / (float)LongitudinalSegments);
                float x1 = Mathf.Lerp(
                    -PackHalfWidth,
                    PackHalfWidth,
                    (column + 1) / (float)LongitudinalSegments);
                if (ReleaseAtX(sample, (x0 + x1) * 0.5f) > 0.008f)
                {
                    continue;
                }
                for (int row = 0; row < BodyRows; row++)
                {
                    int lower = BodyIndex(column, row);
                    int upper = BodyIndex(column, row + 1);
                    int nextLower = BodyIndex(column + 1, row);
                    int nextUpper = BodyIndex(column + 1, row + 1);
                    sealedBackTriangles.Add(lower);
                    sealedBackTriangles.Add(nextLower);
                    sealedBackTriangles.Add(upper);
                    sealedBackTriangles.Add(nextLower);
                    sealedBackTriangles.Add(nextUpper);
                    sealedBackTriangles.Add(upper);
                }
            }

            frontMesh.Clear(false);
            frontMesh.vertices = frontVertices;
            frontMesh.uv = frontUvs;
            frontMesh.uv2 = frontContourUvs;
            frontMesh.uv3 = frontOpenUvs;
            frontMesh.triangles = frontTriangles;
            frontMesh.RecalculateNormals();
            frontMesh.RecalculateBounds();

            sealedBackMesh.Clear(false);
            sealedBackMesh.vertices = sealedBackVertices;
            sealedBackMesh.uv = frontUvs;
            sealedBackMesh.uv2 = frontContourUvs;
            sealedBackMesh.uv3 = frontOpenUvs;
            sealedBackMesh.SetTriangles(sealedBackTriangles, 0);
            sealedBackMesh.RecalculateNormals();
            sealedBackMesh.RecalculateBounds();
        }

        private void UpdateRearRim(PackOpeningGate04R012Sample sample)
        {
            for (int column = 0; column <= LongitudinalSegments; column++)
            {
                float column01 = column / (float)LongitudinalSegments;
                float x = Mathf.Lerp(-PackHalfWidth, PackHalfWidth, column01);
                float release = ReleaseAtX(sample, x);
                float depth = RearRimDepth * release;
                float lift = 0.004f * release;
                int bottom = RearRimIndex(column, 0);
                int top = RearRimIndex(column, 1);
                rearRimVertices[bottom] = new Vector3(
                    x,
                    SealedRimY + 0.001f + lift,
                    depth);
                rearRimVertices[top] = new Vector3(
                    x,
                    RearRimTopY + lift,
                    depth);
                rearRimUvs[bottom] = new Vector2(column01, FlapUvMin);
                rearRimUvs[top] = new Vector2(column01, FlapUvMax);
            }
            rearRimMesh.vertices = rearRimVertices;
            rearRimMesh.uv = rearRimUvs;
            rearRimMesh.RecalculateNormals();
            rearRimMesh.RecalculateBounds();
        }

        private void UpdateCavity(PackOpeningGate04R012Sample sample)
        {
            cavityVertices.Clear();
            cavityUvs.Clear();
            cavityInteriorTriangles.Clear();
            cavityContactTriangles.Clear();
            CavityVisibleColumnCount = 0;
            CavityMaximumOpenHeight = 0f;
            int firstOpen = -1;
            int lastOpen = -1;
            float lowestFront = float.MaxValue;

            for (int column = 0; column < LongitudinalSegments; column++)
            {
                float x0 = Mathf.Lerp(
                    -PackHalfWidth,
                    PackHalfWidth,
                    column / (float)LongitudinalSegments);
                float x1 = Mathf.Lerp(
                    -PackHalfWidth,
                    PackHalfWidth,
                    (column + 1) / (float)LongitudinalSegments);
                float release = ReleaseAtX(sample, (x0 + x1) * 0.5f);
                if (release <= 0.012f)
                {
                    continue;
                }

                float y0 = FrontTopAtX(sample, x0);
                float y1 = FrontTopAtX(sample, x1);
                CavityVisibleColumnCount++;
                firstOpen = firstOpen < 0 ? column : firstOpen;
                lastOpen = column + 1;
                lowestFront = Mathf.Min(lowestFront, y0, y1);
                CavityMaximumOpenHeight = Mathf.Max(
                    CavityMaximumOpenHeight,
                    RearRimTopY - Mathf.Min(y0, y1));

                AddCavityQuad(
                    new Vector3(x0, y0, 0f),
                    new Vector3(x1, y1, 0f),
                    new Vector3(x1, y1 - 0.004f, InnerLipDepth),
                    new Vector3(x0, y0 - 0.004f, InnerLipDepth),
                    cavityInteriorTriangles);
                AddCavityQuad(
                    new Vector3(x0, y0 - 0.0015f, InnerLipDepth * 0.38f),
                    new Vector3(x1, y1 - 0.0015f, InnerLipDepth * 0.38f),
                    new Vector3(x1, y1 + 0.010f, InnerLipDepth * 0.62f),
                    new Vector3(x0, y0 + 0.010f, InnerLipDepth * 0.62f),
                    cavityContactTriangles);
            }

            if (firstOpen >= 0 && lastOpen > firstOpen)
            {
                float openLeft = Mathf.Lerp(
                    -PackHalfWidth,
                    PackHalfWidth,
                    firstOpen / (float)LongitudinalSegments);
                float openRight = Mathf.Lerp(
                    -PackHalfWidth,
                    PackHalfWidth,
                    lastOpen / (float)LongitudinalSegments);
                float leftFront = FrontTopAtX(sample, openLeft);
                float rightFront = FrontTopAtX(sample, openRight);
                float backTop = RearRimTopY + 0.005f;
                float backBottom = lowestFront - 0.008f;
                AddCavityQuad(
                    new Vector3(openLeft, backBottom, cavityBackWallLocalZ),
                    new Vector3(openRight, backBottom, cavityBackWallLocalZ),
                    new Vector3(openRight, backTop, cavityBackWallLocalZ),
                    new Vector3(openLeft, backTop, cavityBackWallLocalZ),
                    cavityInteriorTriangles);
                AddCavityQuad(
                    new Vector3(openLeft, leftFront, 0f),
                    new Vector3(openLeft, backBottom, cavityBackWallLocalZ),
                    new Vector3(openLeft, backTop, cavityBackWallLocalZ),
                    new Vector3(openLeft, RearRimTopY, RearRimDepth),
                    cavityInteriorTriangles);
                AddCavityQuad(
                    new Vector3(openRight, rightFront, 0f),
                    new Vector3(openRight, RearRimTopY, RearRimDepth),
                    new Vector3(openRight, backTop, cavityBackWallLocalZ),
                    new Vector3(openRight, backBottom, cavityBackWallLocalZ),
                    cavityInteriorTriangles);
            }

            cavityMesh.Clear(false);
            cavityMesh.SetVertices(cavityVertices);
            cavityMesh.SetUVs(0, cavityUvs);
            cavityMesh.subMeshCount = 2;
            cavityMesh.SetTriangles(cavityInteriorTriangles, 0);
            cavityMesh.SetTriangles(cavityContactTriangles, 1);
            cavityMesh.RecalculateNormals();
            cavityMesh.RecalculateBounds();
        }

        private void UpdateTearStrip(PackOpeningGate04R012Sample sample)
        {
            stripFrontTriangles.Clear();
            stripUndersideTriangles.Clear();
            stripEdgeTriangles.Clear();
            FoilMaximumCrossCurl = 0f;
            float releaseLength = Mathf.Max(
                0f,
                PackHalfWidth - TearFrontXLocal);
            for (int column = 0; column <= LongitudinalSegments; column++)
            {
                float x = Mathf.Lerp(
                    -PackHalfWidth,
                    PackHalfWidth,
                    column / (float)LongitudinalSegments);
                float normalized = releaseLength <= 0.0001f
                    ? 0f
                    : Mathf.Clamp01((x - TearFrontXLocal) / releaseLength);
                Vector3 spine = EvaluateStripSpine(normalized, sample);
                Vector3 tangent = EvaluateStripTangent(normalized, sample);
                Vector3 widthDirection = Vector3.Lerp(
                    Vector3.up,
                    new Vector3(0f, -0.35f, 0.94f),
                    Smooth01(normalized));
                widthDirection = Vector3.ProjectOnPlane(
                    widthDirection,
                    tangent).normalized;
                if (widthDirection.sqrMagnitude < 0.1f)
                {
                    widthDirection = Vector3.up;
                }
                Vector3 normal = Vector3.Cross(tangent, widthDirection).normalized;
                if (normal.sqrMagnitude < 0.1f)
                {
                    normal = Vector3.forward;
                }
                for (int row = 0; row <= StripRows; row++)
                {
                    float row01 = row / (float)StripRows;
                    float cross = row01 - 0.5f;
                    float crease = Mathf.Sin(row01 * Mathf.PI)
                        * Mathf.Sin(normalized * Mathf.PI * 3f)
                        * (0.0012f + 0.0008f * sample.TearProgress);
                    Vector3 point = spine
                        + widthDirection * (cross * FoilStripWidth)
                        + normal * crease;
                    int front = StripIndex(column, row, 0);
                    int underside = StripIndex(column, row, 1);
                    stripVertices[front] =
                        point - normal * (FoilStripThickness * 0.5f);
                    stripVertices[underside] =
                        point + normal * (FoilStripThickness * 0.5f);
                    Vector2 uv = new Vector2(
                        normalized,
                        Mathf.Lerp(FlapUvMin, FlapUvMax, row01));
                    stripUvs[front] = uv;
                    stripUvs[underside] = uv;
                }
            }

            for (int column = 0; column < LongitudinalSegments; column++)
            {
                float x0 = Mathf.Lerp(
                    -PackHalfWidth,
                    PackHalfWidth,
                    column / (float)LongitudinalSegments);
                float x1 = Mathf.Lerp(
                    -PackHalfWidth,
                    PackHalfWidth,
                    (column + 1) / (float)LongitudinalSegments);
                if (ReleaseAtX(sample, (x0 + x1) * 0.5f) <= 0.012f)
                {
                    continue;
                }
                for (int row = 0; row < StripRows; row++)
                {
                    int frontLower = StripIndex(column, row, 0);
                    int frontUpper = StripIndex(column, row + 1, 0);
                    int frontNextLower = StripIndex(column + 1, row, 0);
                    int frontNextUpper = StripIndex(column + 1, row + 1, 0);
                    stripFrontTriangles.Add(frontLower);
                    stripFrontTriangles.Add(frontUpper);
                    stripFrontTriangles.Add(frontNextLower);
                    stripFrontTriangles.Add(frontNextLower);
                    stripFrontTriangles.Add(frontUpper);
                    stripFrontTriangles.Add(frontNextUpper);
                    int backLower = StripIndex(column, row, 1);
                    int backUpper = StripIndex(column, row + 1, 1);
                    int backNextLower = StripIndex(column + 1, row, 1);
                    int backNextUpper = StripIndex(column + 1, row + 1, 1);
                    stripUndersideTriangles.Add(backLower);
                    stripUndersideTriangles.Add(backNextLower);
                    stripUndersideTriangles.Add(backUpper);
                    stripUndersideTriangles.Add(backNextLower);
                    stripUndersideTriangles.Add(backNextUpper);
                    stripUndersideTriangles.Add(backUpper);
                }
                AddStripEdge(column, column + 1, 0);
                AddStripEdge(column + 1, column, StripRows);
            }

            stripMesh.Clear(false);
            stripMesh.vertices = stripVertices;
            stripMesh.uv = stripUvs;
            stripMesh.subMeshCount = 3;
            stripMesh.SetTriangles(stripFrontTriangles, 0);
            stripMesh.SetTriangles(stripUndersideTriangles, 1);
            stripMesh.SetTriangles(stripEdgeTriangles, 2);
            stripMesh.RecalculateNormals();
            stripMesh.RecalculateBounds();
            FoilMaximumCrossCurl = MeasureFoilTailCurvature();
        }

        private void UpdatePullTab(PackOpeningGate04R012Sample sample)
        {
            Vector3 tab = EvaluateStripSpine(1f, sample);
            pullTab.localPosition = tab;
            pullTab.localScale = Vector3.one
                * Mathf.Lerp(0.64f, 0.76f, sample.TabLift);
            pullTab.localRotation = Quaternion.Euler(
                -22f * sample.TabLift,
                10f * sample.TabLift,
                -7f * sample.TabLift);
        }

        private void ApplyCase(PackOpeningGate04R012Sample sample)
        {
            Vector3 hero = new Vector3(
                caseBasePosition.x,
                -0.015f,
                caseBasePosition.z - 0.300f);
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
            bool labelsVisible = sample.CaseTravel >= 0.70f;
            foreach (Renderer renderer in caseTextRenderers)
            {
                if (renderer != null)
                {
                    renderer.enabled = labelsVisible;
                }
            }
            float strength = sample.CaseSheen > 0f
                ? Mathf.Sin(sample.CaseSheen * Mathf.PI) * 0.16f
                : 0f;
            foreach (Renderer renderer in casePresentation.EffectRenderers)
            {
                if (renderer == null)
                {
                    continue;
                }
                renderer.GetPropertyBlock(caseProperties);
                caseProperties.SetFloat(
                    SheenCenterId,
                    Mathf.Lerp(-0.12f, 1.12f, sample.CaseSheen));
                caseProperties.SetFloat(SheenWidthId, 0.065f);
                caseProperties.SetFloat(SheenStrengthId, strength);
                caseProperties.SetFloat(SheenFalloffId, 0.32f);
                renderer.SetPropertyBlock(caseProperties);
            }
        }

        private void ApplySourceEffects(PackOpeningGate04R012Sample sample)
        {
            sourceEffectsRoot.localPosition = new Vector3(
                TearFrontXLocal,
                FrontTopAtX(sample, TearFrontXLocal) + 0.012f,
                0.006f);
            sourceEffectsRoot.localRotation = Quaternion.identity;
            float age = Mathf.Max(0f, ElapsedSeconds - 0.94f);
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
                float localAge = index == 0 ? age : Mathf.Max(0f, age - 0.56f);
                system.Simulate(localAge, true, true, true);
                system.Pause(true);
                ParticleSystemRenderer renderer =
                    system.GetComponent<ParticleSystemRenderer>();
                if (renderer == null)
                {
                    continue;
                }
                renderer.GetPropertyBlock(sourceProperties);
                sourceProperties.SetFloat(
                    ProgressId,
                    Mathf.Clamp01(localAge / 1.2f));
                renderer.SetPropertyBlock(sourceProperties);
            }
        }

        private void ApplyCamera(PackOpeningGate04R012Sample sample)
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
                - sample.CameraPush * 4.5f;
        }

        private float FrontTopAtX(
            PackOpeningGate04R012Sample sample,
            float x)
        {
            float release = ReleaseAtX(sample, x);
            return SealedRimY
                - MouthMaximumHeight * sample.ApertureProgress * release
                + TearOffsetAtX(x) * release;
        }

        private static float ReleaseAtX(
            PackOpeningGate04R012Sample sample,
            float x)
        {
            if (sample.TearProgress <= 0.0001f)
            {
                return 0f;
            }
            float front = Mathf.Lerp(
                PackHalfWidth,
                -PackHalfWidth,
                sample.TearProgress);
            return Smooth01(Mathf.InverseLerp(
                -0.0015f,
                OpeningTransitionMeters,
                x - front));
        }

        private Vector3 EvaluateStripSpine(
            float normalized,
            PackOpeningGate04R012Sample sample)
        {
            float left = TearFrontXLocal;
            float right = PackHalfWidth;
            float length = Mathf.Max(0.001f, right - left);
            Vector3 start = new Vector3(
                left,
                FrontTopAtX(sample, left),
                0.0015f);
            float pull = sample.TabLift;
            Vector3 end = new Vector3(
                right - 0.004f + pull * 0.010f,
                RearRimTopY - 0.006f + pull * 0.012f,
                pull * 0.046f);
            Vector3 controlOne = start + new Vector3(
                length * 0.24f,
                0.026f + sample.TearProgress * 0.028f,
                0.016f + sample.TearProgress * 0.052f);
            Vector3 controlTwo = end + new Vector3(
                -length * 0.20f,
                -0.024f,
                0.038f);
            return CubicBezier(start, controlOne, controlTwo, end, normalized);
        }

        private Vector3 EvaluateStripTangent(
            float normalized,
            PackOpeningGate04R012Sample sample)
        {
            float left = TearFrontXLocal;
            float right = PackHalfWidth;
            float length = Mathf.Max(0.001f, right - left);
            Vector3 start = new Vector3(
                left,
                FrontTopAtX(sample, left),
                0.0015f);
            float pull = sample.TabLift;
            Vector3 end = new Vector3(
                right - 0.004f + pull * 0.010f,
                RearRimTopY - 0.006f + pull * 0.012f,
                pull * 0.046f);
            Vector3 controlOne = start + new Vector3(
                length * 0.24f,
                0.026f + sample.TearProgress * 0.028f,
                0.016f + sample.TearProgress * 0.052f);
            Vector3 controlTwo = end + new Vector3(
                -length * 0.20f,
                -0.024f,
                0.038f);
            Vector3 tangent = CubicBezierTangent(
                start,
                controlOne,
                controlTwo,
                end,
                normalized);
            return tangent.sqrMagnitude < 0.000001f
                ? Vector3.right
                : tangent.normalized;
        }

        private float ResolveCavityBackWallLocalZ()
        {
            if (!TryGetWorldBounds(caseRenderers, out Bounds caseBounds))
            {
                return 0.340f;
            }
            float rearLocalZ = packRoot.InverseTransformPoint(
                new Vector3(0f, 0f, caseBounds.max.z)).z;
            return Mathf.Max(0.160f, rearLocalZ + CavityBackClearance);
        }

        private void GenerateTearContour()
        {
            const int anchorStride = 4;
            for (int index = 0; index < tearOffsets.Length; index++)
            {
                int anchor = index / anchorStride;
                float local = (index % anchorStride) / (float)anchorStride;
                float a = HashSigned(anchor * 47 + 11);
                float b = HashSigned((anchor + 1) * 47 + 11);
                float c = HashSigned((anchor + 2) * 47 + 11);
                float d = HashSigned((anchor - 1) * 47 + 11);
                float smooth = Smooth01(local);
                float value = Mathf.Lerp(
                    Mathf.Lerp(d, a, 0.5f),
                    Mathf.Lerp(b, c, 0.5f),
                    smooth);
                value += HashSigned(index * 131 + 29) * 0.12f;
                tearOffsets[index] = Mathf.Clamp(value, -1f, 1f)
                    * TearContourMaximumAmplitude;
            }
            tearOffsets[0] *= 0.35f;
            tearOffsets[tearOffsets.Length - 1] *= 0.35f;
        }

        private float TearOffsetAtX(float x)
        {
            float scaled = Mathf.InverseLerp(
                -PackHalfWidth,
                PackHalfWidth,
                x) * LongitudinalSegments;
            int lower = Mathf.Clamp(
                Mathf.FloorToInt(scaled),
                0,
                LongitudinalSegments);
            int upper = Mathf.Min(LongitudinalSegments, lower + 1);
            return Mathf.Lerp(
                tearOffsets[lower],
                tearOffsets[upper],
                scaled - lower);
        }

        private void AddCavityQuad(
            Vector3 a,
            Vector3 b,
            Vector3 c,
            Vector3 d,
            List<int> triangles)
        {
            int index = cavityVertices.Count;
            cavityVertices.Add(a);
            cavityVertices.Add(b);
            cavityVertices.Add(c);
            cavityVertices.Add(d);
            cavityUvs.Add(new Vector2(0f, 0f));
            cavityUvs.Add(new Vector2(1f, 0f));
            cavityUvs.Add(new Vector2(1f, 1f));
            cavityUvs.Add(new Vector2(0f, 1f));
            triangles.Add(index);
            triangles.Add(index + 2);
            triangles.Add(index + 1);
            triangles.Add(index);
            triangles.Add(index + 3);
            triangles.Add(index + 2);
        }

        private void AddStripEdge(int firstColumn, int secondColumn, int row)
        {
            int firstFront = StripIndex(firstColumn, row, 0);
            int firstBack = StripIndex(firstColumn, row, 1);
            int secondFront = StripIndex(secondColumn, row, 0);
            int secondBack = StripIndex(secondColumn, row, 1);
            stripEdgeTriangles.Add(firstFront);
            stripEdgeTriangles.Add(secondFront);
            stripEdgeTriangles.Add(firstBack);
            stripEdgeTriangles.Add(firstBack);
            stripEdgeTriangles.Add(secondFront);
            stripEdgeTriangles.Add(secondBack);
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
            if (float.IsInfinity(minX) || float.IsInfinity(minY)
                || float.IsInfinity(maxX) || float.IsInfinity(maxY))
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
                if (renderer == null)
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
            builder.Append(frontLayerRenderer.enabled ? '1' : '0');
            builder.Append(sealedBackLayerRenderer.enabled ? '1' : '0');
            builder.Append(rearRimRenderer.enabled ? '1' : '0');
            builder.Append(stripRenderer.enabled ? '1' : '0');
            builder.Append(cavityRenderer.enabled ? '1' : '0');
            builder.Append(pullTabRenderer.enabled ? '1' : '0');
            foreach (Vector3 vertex in frontVertices)
            {
                AppendVector(builder, vertex);
            }
            foreach (Vector3 vertex in stripVertices)
            {
                AppendVector(builder, vertex);
            }
            return builder.ToString();
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

        private static float HashSigned(int value)
        {
            unchecked
            {
                uint hash = (uint)value;
                hash ^= hash >> 16;
                hash *= 0x7FEB352Du;
                hash ^= hash >> 15;
                hash *= 0x846CA68Bu;
                hash ^= hash >> 16;
                return (hash & 0x00FFFFFFu) / 8388607.5f - 1f;
            }
        }

        private static float Smooth01(float value)
        {
            float clamped = Mathf.Clamp01(value);
            return clamped * clamped * (3f - 2f * clamped);
        }

        private static int BodyIndex(int column, int row)
        {
            return column * (BodyRows + 1) + row;
        }

        private static int RearRimIndex(int column, int row)
        {
            return column * 2 + row;
        }

        private static int StripIndex(int column, int row, int side)
        {
            return (column * (StripRows + 1) + row) * 2 + side;
        }

        private static void AppendVector(StringBuilder builder, Vector3 value)
        {
            builder.Append(value.x.ToString("R")).Append('|')
                .Append(value.y.ToString("R")).Append('|')
                .Append(value.z.ToString("R")).Append('|');
        }

        private static int FirstMismatch(string expected, string actual)
        {
            int shared = Mathf.Min(expected.Length, actual.Length);
            for (int index = 0; index < shared; index++)
            {
                if (expected[index] != actual[index])
                {
                    return index;
                }
            }
            return shared;
        }

        private static string FingerprintWindow(string value, int index)
        {
            int start = Mathf.Max(0, index - 16);
            int length = Mathf.Min(48, value.Length - start);
            return value.Substring(start, length);
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
