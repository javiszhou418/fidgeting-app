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
    public sealed class PackOpeningGate04R011Controller : MonoBehaviour
    {
        private static readonly int BaseMapId = Shader.PropertyToID("_BaseMap");
        private static readonly int BaseColorId = Shader.PropertyToID("_BaseColor");
        private static readonly int SaturationId = Shader.PropertyToID("_Saturation");
        private static readonly int OpacityId = Shader.PropertyToID("_Opacity");
        private static readonly int DissolveId = Shader.PropertyToID("_Dissolve");
        private static readonly int ProgressId = Shader.PropertyToID("_Progress");
        private static readonly int RevealId = Shader.PropertyToID("_Reveal");
        private static readonly int IntensityId = Shader.PropertyToID("_Intensity");
        private static readonly int SheenCenterId = Shader.PropertyToID("_SheenCenter");
        private static readonly int SheenWidthId = Shader.PropertyToID("_SheenWidth");
        private static readonly int SheenStrengthId = Shader.PropertyToID("_SheenStrength");
        private static readonly int SheenFalloffId = Shader.PropertyToID("_SheenFalloff");
        private static readonly int TearSweepId = Shader.PropertyToID("_TearSweep");

        public const int StripSegments = 64;
        public const int StripRows = 8;
        public const int BodyRows = 12;
        public const float PackWidth = 0.255f;
        public const float PackHeight = 0.340f;
        public const float TearSeamY = PackHeight * 0.320f;
        public const float StripHeight = 0.022f;
        public const float StripThickness = 0.00075f;
        public const float StripEdgeIrregularity = 0.16f;
        public const float MaximumTearAmplitude = 0.00190f;
        public const float CaseScale = 1.02f;

        public const float SealedFoilTwistDegrees = 6f;
        public const float FreedFoilTwistDegrees = 34f;

        /// The audited discard curve removes the Pack. Large translation made it
        /// read as a panel sliding away from a separate object.
        public const float MaximumPackRetreatTravelMeters = 0.045f;

        private const float PackHalfWidth = PackWidth * 0.47f;
        private const float PackBottomY = -PackHeight * 0.5f;
        private const float PackPlaneZ = 0f;
        private const float ApertureDepth = 0.026f;
        private const float ReleasedFoilRampMeters = 0.044f;
        private const float InteriorSideWallDepth = 0.034f;
        // The bag needs a real interior or the receding front face reveals
        // nothing and the opening reads as the top being sliced off.
        //
        // Iteration 10 hard-coded this to pack-local 0.082 and claimed it sat
        // "behind the concealed case (z 0.060)". That mixed two spaces: the pack
        // root is at world z -0.180, so local 0.082 is world -0.098, while the
        // case root is at world +0.060. The camera is at world z -1.35 looking
        // toward +z, so the wall was between the camera and the case and hid it.
        // The mouth rendered as an empty slab and the case could only appear
        // after it passed the torn edge. The depth is now measured from the
        // concealed case bounds in the cavity's own space, so the wall can never
        // again be placed in front of the thing it is supposed to reveal.
        public const float InteriorBackWallFallbackZ = 0.082f;
        public const float InteriorBackWallClearance = 0.026f;
        public const float TornEdgeLipDepth = 0.0115f;
        public const float TornEdgeLipDrop = 0.0042f;
        // Reference depth for torn-contour space. The emissive edge band is
        // measured against this, so it is constant in object space and can never
        // stretch into a full-width horizontal band.
        public const float ContourBandReference = 0.052f;
        public const float InteriorRimTilt = 0.018f;
        private const float TearFrontGlowHalfWidth = 0.055f;
        private const float FlapUvMin = 1f - 96f / 512f;
        private const float FlapUvMax = 1f - 57f / 512f;

        [SerializeField] private PackOpeningGate04R011Profile profile;
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
        [SerializeField] private ParticleSystem sourceActivationGlow;
        [SerializeField] private ParticleSystem sourceLightningStrips;
        [SerializeField] private ParticleSystem sourceLightningSparks;
        [SerializeField] private ParticleSystem sourceExplosionDust;
        [SerializeField] private ParticleSystem sourceExplosionFlares;

        private readonly float[] tearOffsets = new float[StripSegments + 1];
        private readonly Vector3[] bodyVertices =
            new Vector3[(StripSegments + 1) * (BodyRows + 1)];
        private readonly Vector2[] bodyUvs =
            new Vector2[(StripSegments + 1) * (BodyRows + 1)];
        // uv2 carries torn-contour space so the emissive edge can hug the tear
        // instead of the horizontal dissolve sweep line: x = normalized depth
        // below this column's torn top edge, y = proximity to the tear front.
        private readonly Vector2[] bodyContourUvs =
            new Vector2[(StripSegments + 1) * (BodyRows + 1)];
        // uv3 carries per-column jitter so the dissolve boundary is irregular
        // rather than a clean full-width horizontal rectangle.
        private readonly Vector2[] bodyJitterUvs =
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
        // The interior is assembled from a variable number of surfaces (back
        // wall, tear-front cross wall, right side wall, torn-edge lip), so it
        // cannot use a fixed stride like the front face does.
        private readonly List<Vector3> cavityVertices =
            new List<Vector3>((StripSegments + 1) * 8);
        private readonly List<Vector2> cavityUvs =
            new List<Vector2>((StripSegments + 1) * 8);
        // Submesh 0 is the lit interior, submesh 1 is the occlusion contact band
        // under the torn lip. A single flat-lit surface cannot express the
        // darkening where the front face meets the interior.
        private readonly List<int> cavityTriangles =
            new List<int>(StripSegments * 36);
        private readonly List<int> cavityContactTriangles =
            new List<int>(StripSegments * 12);
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
        private MaterialPropertyBlock packProperties;
        private MaterialPropertyBlock sourceEffectProperties;
        private MaterialPropertyBlock caseProperties;
        private Vector3 cameraBasePosition;
        private Quaternion cameraBaseRotation;
        private float cameraBaseFov;
        private Vector3 cameraAuthoredPosition;
        private float cameraAuthoredFov;
        private Vector3 packBasePosition;
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
        private float interiorBackWallZ = InteriorBackWallFallbackZ;
        private int interiorWallBottomRow;
        private int interiorRowSpan;

        public PackOpeningGate04R011Profile Profile => profile;
        public PremiumDisplayCaseShippingPresentation CasePresentation =>
            casePresentation;
        public Transform CaseMotionRoot => caseMotionRoot;
        /// <summary>
        /// Resolved depth of the bag's back panel in the cavity's local space.
        /// Exposed so tests can assert the wall really is behind the concealed
        /// case instead of trusting a hard-coded constant.
        /// </summary>
        public float InteriorBackWallLocalZ => interiorBackWallZ;
        /// <summary>
        /// The back panel in world space, so callers and tests compare it against
        /// the case in one space. Iteration 10 compared a cavity-local constant
        /// against a world-space case position and concluded the wall was behind
        /// the case when it was in front of it.
        /// </summary>
        public float InteriorBackWallWorldZ =>
            cavityMeshFilter == null
                ? interiorBackWallZ
                : cavityMeshFilter.transform.TransformPoint(
                    new Vector3(0f, 0f, interiorBackWallZ)).z;
        /// <summary>
        /// The Pack's front face in world space.
        /// </summary>
        public float PackFrontFaceWorldZ =>
            cavityMeshFilter == null
                ? PackPlaneZ
                : cavityMeshFilter.transform.TransformPoint(
                    new Vector3(0f, 0f, PackPlaneZ)).z;
        /// <summary>
        /// Rear-most world z of the assembled case at its current pose.
        /// </summary>
        public float CaseRearWorldZ
        {
            get
            {
                bool found = false;
                Bounds bounds = default;
                for (int index = 0; index < caseRenderers.Length; index++)
                {
                    Renderer renderer = caseRenderers[index];
                    if (renderer == null)
                    {
                        continue;
                    }
                    if (!found)
                    {
                        bounds = renderer.bounds;
                        found = true;
                        continue;
                    }
                    bounds.Encapsulate(renderer.bounds);
                }
                return found ? bounds.max.z : float.NaN;
            }
        }
        public float ElapsedSeconds { get; private set; }
        public bool ReduceMotion { get; private set; }
        public PackOpeningGate04R011Sample CurrentSample { get; private set; }
        public float TearFrontXLocal { get; private set; } = PackHalfWidth;
        /// <summary>
        /// Columns whose front face has receded far enough to expose interior.
        /// Zero while sealed; must be non-zero once the tear is under way or the
        /// Pack is not visibly open.
        /// </summary>
        public int CavityVisibleColumnCount { get; private set; }
        /// <summary>
        /// Tallest gap between the original rim and the receded front edge, in
        /// object-space metres. This is the opening that must read in silhouette.
        /// </summary>
        public float CavityMaximumOpenHeight { get; private set; }
        /// <summary>
        /// Largest angle between neighbouring interior back-panel normals. The
        /// iteration-10 interior emitted one unwelded quad per column; the
        /// jittered contour made each quad non-planar, so neighbouring columns
        /// disagreed by several degrees and the mouth rendered as a 48-stripe
        /// vertical comb. Welded rows keep this near zero.
        /// </summary>
        public float CavityInteriorMaxAdjacentNormalAngleDegrees { get; private set; }
        public float FoilMaximumCrossCurl { get; private set; }
        public Vector3 TearFrontWorldPosition =>
            packRoot != null
                ? packRoot.TransformPoint(new Vector3(
                    TearFrontXLocal,
                    TearSeamY + TearOffsetAtX(TearFrontXLocal),
                    PackPlaneZ))
                : Vector3.zero;
        public IReadOnlyList<float> SharedTearOffsets => tearOffsets;
        public float PackRetreatTravelMeters =>
            packRoot != null
                ? Vector3.Distance(packRoot.localPosition, packBasePosition)
                : 0f;
        public float MaximumAheadOfFrontSeparation =>
            maximumAheadOfFrontSeparation;
        public EntityId CaseRootEntityId =>
            caseMotionRoot != null
                ? caseMotionRoot.GetEntityId()
                : EntityId.None;
        public IReadOnlyList<EntityId> CaseRendererEntityIds =>
            caseRendererEntityIds;
        public IReadOnlyList<ParticleSystem> SourceEffectSystems =>
            new[]
            {
                sourceActivationGlow,
                sourceLightningStrips,
                sourceLightningSparks,
                sourceExplosionDust,
                sourceExplosionFlares
            };
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
            && sourceActivationGlow != null
            && sourceLightningStrips != null
            && sourceLightningSparks != null
            && sourceExplosionDust != null
            && sourceExplosionFlares != null;

        public void Configure(
            PackOpeningGate04R011Profile authoredProfile,
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
            ParticleSystem authoredSourceActivationGlow,
            ParticleSystem authoredSourceLightningStrips,
            ParticleSystem authoredSourceLightningSparks,
            ParticleSystem authoredSourceExplosionDust,
            ParticleSystem authoredSourceExplosionFlares)
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
            sourceActivationGlow = authoredSourceActivationGlow;
            sourceLightningStrips = authoredSourceLightningStrips;
            sourceLightningSparks = authoredSourceLightningSparks;
            sourceExplosionDust = authoredSourceExplosionDust;
            sourceExplosionFlares = authoredSourceExplosionFlares;
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
                    "Gate 04 rev 11 controller bindings are incomplete.");
            }

            ElapsedSeconds = Mathf.Clamp(
                elapsedSeconds,
                0f,
                PackOpeningGate04R011Profile.TotalSeconds);
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

        /// Reframes the shipping portrait camera for a close-up evidence pass.
        /// The authored shipping composition is restored by
        /// <see cref="ResetCaptureFraming"/>; it is never changed permanently.
        public void ApplyCaptureFraming(
            Vector3 localOffset,
            float fieldOfViewScale)
        {
            Initialize();
            cameraBasePosition = cameraAuthoredPosition
                + cameraBaseRotation * localOffset;
            cameraBaseFov = cameraAuthoredFov * fieldOfViewScale;
        }

        public void ResetCaptureFraming()
        {
            cameraBasePosition = cameraAuthoredPosition;
            cameraBaseFov = cameraAuthoredFov;
        }

        public bool ReboundToSealed()
        {
            SetTime(0f, false);
            StopSourceEffects();
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
            float anchorX = Mathf.Lerp(
                TearFrontXLocal,
                PackHalfWidth,
                0.70f);
            float release = ReleaseFractionAtX(CurrentSample, anchorX);
            if (release <= 0.001f)
            {
                return 0f;
            }
            EvaluateFoilFrame(
                anchorX,
                release,
                CurrentSample,
                out Vector3 anchor,
                out Vector3 tangent,
                out Vector3 widthDirection,
                out Vector3 surfaceNormal);
            float width = StripHeight * (1f + FoilGrain(anchorX) * StripEdgeIrregularity);
            Vector3 a = EvaluateFoilPoint(
                anchor,
                tangent,
                widthDirection,
                surfaceNormal,
                0.25f,
                release,
                width,
                FoilGrain(anchorX));
            Vector3 b = EvaluateFoilPoint(
                anchor,
                tangent,
                widthDirection,
                surfaceNormal,
                0.50f,
                release,
                width,
                FoilGrain(anchorX));
            Vector3 c = EvaluateFoilPoint(
                anchor,
                tangent,
                widthDirection,
                surfaceNormal,
                0.75f,
                release,
                width,
                FoilGrain(anchorX));
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
            cameraAuthoredPosition = cameraBasePosition;
            cameraAuthoredFov = cameraBaseFov;
            packBasePosition = packRoot.localPosition;
            packBaseScale = packRoot.localScale;
            caseBasePosition = caseMotionRoot.localPosition;
            caseBaseRotation = caseMotionRoot.localRotation;
            caseBaseScale = caseMotionRoot.localScale;
            environmentProperties = new MaterialPropertyBlock();
            packProperties = new MaterialPropertyBlock();
            sourceEffectProperties = new MaterialPropertyBlock();
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
            interiorBackWallZ = ResolveInteriorBackWallZ();
            StopSourceEffects();
            initialized = true;
        }

        /// <summary>
        /// Places the bag's back panel behind the concealed case, measured in the
        /// cavity mesh's own space. The case is still at its concealed pose here,
        /// so this fixes the panel where a real bag's back would be: behind the
        /// thing the mouth is supposed to reveal.
        /// </summary>
        private float ResolveInteriorBackWallZ()
        {
            if (cavityMeshFilter == null)
            {
                return InteriorBackWallFallbackZ;
            }
            bool found = false;
            Bounds worldBounds = default;
            for (int index = 0; index < caseRenderers.Length; index++)
            {
                Renderer renderer = caseRenderers[index];
                if (renderer == null)
                {
                    continue;
                }
                if (!found)
                {
                    worldBounds = renderer.bounds;
                    found = true;
                    continue;
                }
                worldBounds.Encapsulate(renderer.bounds);
            }
            if (!found)
            {
                return InteriorBackWallFallbackZ;
            }
            // Use the bounding sphere, not the current AABB. The case is rotated
            // about -25 degrees during the concealed phase, so an AABB measured
            // at one pose understates the rear by a few millimetres and the wall
            // slides back in front of the case mid-animation. A sphere radius is
            // rotation-invariant, so the panel stays behind the case at every
            // pose. Overshooting only makes the hidden interior deeper.
            Transform cavityTransform = cavityMeshFilter.transform;
            float centreLocalZ = cavityTransform
                .InverseTransformPoint(worldBounds.center).z;
            float radius = worldBounds.extents.magnitude;
            return Mathf.Max(
                InteriorBackWallFallbackZ,
                centreLocalZ + radius + InteriorBackWallClearance);
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

        private void ApplyPack(PackOpeningGate04R011Sample sample)
        {
            // The discard curve, not the retreat settle, is what removes the
            // Pack. Gating on retreat let the renderer switch off while the
            // dissolve was still at 0.9984.
            bool bodyVisible = sample.PackDissolve < 0.99995f;
            bool stripVisible = bodyVisible && sample.PackRetreat < 0.52f;
            packBodyRenderer.enabled = bodyVisible;
            tearStripRenderer.enabled = stripVisible;
            cavityRenderer.enabled =
                bodyVisible
                && sample.ApertureProgress > 0.006f
                && sample.PackRetreat < 0.44f;
            contactShadowRenderer.enabled =
                stripVisible
                && sample.TearProgress > 0.008f
                && sample.TearProgress < 0.995f
                && sample.PackRetreat < 0.20f;
            specularRenderer.enabled =
                stripVisible
                && sample.TearProgress > 0.10f
                && sample.PackRetreat < 0.34f;
            packBodyRenderer.GetPropertyBlock(packProperties);
            packProperties.SetFloat(DissolveId, sample.PackDissolve);
            // The audited edge sweep is the identity of this transition, so it
            // must be driven by the tear itself. Keying it off PackDissolve left
            // it absent for the entire tear, which is when it has to be seen.
            packProperties.SetFloat(TearSweepId, TearSweepStrength(sample));
            packBodyRenderer.SetPropertyBlock(packProperties);
            // The audited discard curve removes the Pack. A large translation
            // here made it read as a flat panel sliding away from a separate
            // object instead of dissolving from its own torn edge.
            packRoot.localPosition = packBasePosition + new Vector3(
                -0.030f * sample.PackRetreat,
                -0.026f * sample.PackRetreat,
                -0.016f * sample.PackRetreat);
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

        private void ApplyCase(PackOpeningGate04R011Sample sample)
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

        private void ApplyImpact(PackOpeningGate04R011Sample sample)
        {
            SimulateSourceSystem(
                sourceActivationGlow,
                sample.ActivationEnabled,
                sample.ActivationAge,
                2.20f);
            SimulateSourceSystem(
                sourceLightningStrips,
                sample.LightningEnabled,
                sample.LightningAge,
                1.46f);
            SimulateSourceSystem(
                sourceLightningSparks,
                sample.LightningEnabled,
                sample.LightningAge,
                1.46f);
            SimulateSourceSystem(
                sourceExplosionDust,
                sample.ExplosionEnabled,
                sample.ExplosionAge,
                1.20f);
            SimulateSourceSystem(
                sourceExplosionFlares,
                sample.ExplosionEnabled,
                sample.ExplosionAge,
                1.20f);
        }

        private void ApplyCamera(PackOpeningGate04R011Sample sample)
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

        /// <summary>
        /// Intensity of the audited discard edge sweep. It rises with the tear
        /// so the source identity is visible while the Pack is still opaque, and
        /// stays lit through the dissolve rather than starting there.
        /// </summary>
        public static float TearSweepStrength(PackOpeningGate04R011Sample sample)
        {
            float tearDriven = Smooth01(
                Mathf.InverseLerp(0.010f, 0.34f, sample.TearProgress));
            return Mathf.Clamp01(Mathf.Max(tearDriven, sample.PackDissolve));
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
                // One sine term at 0.38 weight outweighed the smoothed random
                // component and read as a regular machine-cut wave. Two
                // incommensurate terms at lower weight keep the edge continuous
                // without repeating.
                float lowFrequency =
                    Mathf.Sin(index * 0.73f + 0.45f) * 0.17f
                    + Mathf.Sin(index * 0.271f + 2.11f) * 0.13f;
                // The 3-tap smoothing that keeps the edge continuous also
                // removes every per-column feature, which is what made the tear
                // resolve as a machine-cut scallop. The unsmoothed micro term
                // restores fibre-scale reversals without breaking continuity.
                float micro = current * 0.30f;
                tearOffsets[index] = Mathf.Clamp(
                    (previous + current * 2f + next) * 0.170f
                    + lowFrequency
                    + micro,
                    -1f,
                    1f) * MaximumTearAmplitude;
            }
            tearOffsets[0] *= 0.45f;
            tearOffsets[tearOffsets.Length - 1] *= 0.45f;
        }

        private void BuildBodyMesh()
        {
            bodyMesh = new Mesh { name = "Gate04R011PhysicalPackOccluder" };
            bodyMesh.MarkDynamic();
            bodyMesh.vertices = bodyVertices;
            bodyMesh.uv = bodyUvs;
            bodyMesh.triangles = Array.Empty<int>();
            packBodyMeshFilter.sharedMesh = bodyMesh;
        }

        private void UpdateBodyMesh(PackOpeningGate04R011Sample sample)
        {
            bodyTriangles.Clear();
            for (int column = 0; column <= StripSegments; column++)
            {
                float column01 = column / (float)StripSegments;
                float x = Mathf.Lerp(-PackHalfWidth, PackHalfWidth, column01);
                float openedBehindFront = OpeningFractionAtX(sample, x);
                float originalTop = TearSeamY;
                float tornTop = TornTopAtX(sample, x);
                // The tear front is the hot spot of the audited sweep. Distance
                // is measured in object space so the highlight travels with the
                // front instead of sitting on a fixed screen row.
                float frontHeat = sample.TearProgress > 0.0001f
                    ? Mathf.Clamp01(
                        1f
                        - Mathf.Abs(x - TearFrontXLocal)
                            / TearFrontGlowHalfWidth)
                    : 0f;
                float columnJitter = tearOffsets[column] / MaximumTearAmplitude;
                for (int row = 0; row <= BodyRows; row++)
                {
                    float row01 = row / (float)BodyRows;
                    float topInfluence = Mathf.Pow(row01, 6f);
                    float y = Mathf.Lerp(PackBottomY, originalTop, row01)
                        + (tornTop - originalTop) * topInfluence;
                    int index = BodyIndex(column, row);
                    bodyVertices[index] = new Vector3(
                        x,
                        y,
                        PackPlaneZ);
                    bodyUvs[index] = new Vector2(
                        column01,
                        Mathf.Clamp01(
                            Mathf.Lerp(
                                0f,
                                originalTop / PackHeight + 0.5f,
                                row01)));
                    bodyContourUvs[index] = new Vector2(
                        Mathf.Clamp01((tornTop - y) / ContourBandReference),
                        frontHeat);
                    bodyJitterUvs[index] = new Vector2(
                        columnJitter,
                        openedBehindFront);
                }
            }

            for (int column = 0; column < StripSegments; column++)
            {
                for (int row = 0; row < BodyRows; row++)
                {
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
            bodyMesh.uv2 = bodyContourUvs;
            bodyMesh.uv3 = bodyJitterUvs;
            bodyMesh.SetTriangles(bodyTriangles, 0);
            bodyMesh.RecalculateNormals();
            bodyMesh.RecalculateBounds();
        }

        private void BuildStripMesh()
        {
            stripMesh = new Mesh
            {
                name = "Gate04R011SubdividedDeformableFoilStrip",
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

        private void UpdateStripMesh(PackOpeningGate04R011Sample sample)
        {
            maximumAheadOfFrontSeparation = 0f;
            FoilMaximumCrossCurl = 0f;
            for (int column = 0; column <= StripSegments; column++)
            {
                float column01 = column / (float)StripSegments;
                float originalX = Mathf.Lerp(
                    -PackHalfWidth,
                    PackHalfWidth,
                    column01);
                float release = ReleaseFractionAtX(sample, originalX);
                bool released = release > 0.0001f;
                Vector3 anchor;
                Vector3 tangent;
                Vector3 widthDirection;
                Vector3 surfaceNormal;
                if (!released)
                {
                    anchor = new Vector3(
                        originalX,
                        TearSeamY,
                        PackPlaneZ);
                    tangent = Vector3.right;
                    widthDirection = Vector3.up;
                    surfaceNormal = Vector3.forward;
                }
                else
                {
                    EvaluateFoilFrame(
                        originalX,
                        release,
                        sample,
                        out anchor,
                        out tangent,
                        out widthDirection,
                        out surfaceNormal);
                }

                float grain = FoilGrain(originalX);
                float width = StripHeight
                    * (1f + grain * StripEdgeIrregularity);
                for (int row = 0; row <= StripRows; row++)
                {
                    float row01 = row / (float)StripRows;
                    Vector3 centerAtRow = released
                        ? EvaluateFoilPoint(
                            anchor,
                            tangent,
                            widthDirection,
                            surfaceNormal,
                            row01,
                            release,
                            width,
                            grain)
                        : anchor + widthDirection * (StripHeight * row01);
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

                if (released)
                {
                    Vector3 a = EvaluateFoilPoint(
                        anchor,
                        tangent,
                        widthDirection,
                        surfaceNormal,
                        0.25f,
                        release,
                        width,
                        grain);
                    Vector3 b = EvaluateFoilPoint(
                        anchor,
                        tangent,
                        widthDirection,
                        surfaceNormal,
                        0.50f,
                        release,
                        width,
                        grain);
                    Vector3 c = EvaluateFoilPoint(
                        anchor,
                        tangent,
                        widthDirection,
                        surfaceNormal,
                        0.75f,
                        release,
                        width,
                        grain);
                    FoilMaximumCrossCurl = Mathf.Max(
                        FoilMaximumCrossCurl,
                        (a - 2f * b + c).magnitude);
                }
                else
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

        private void EvaluateFoilFrame(
            float anchorX,
            float release,
            PackOpeningGate04R011Sample sample,
            out Vector3 anchor,
            out Vector3 tangent,
            out Vector3 widthDirection,
            out Vector3 surfaceNormal)
        {
            float peeled = Smooth01(release);
            float normalizedX = Mathf.InverseLerp(
                -PackHalfWidth,
                PackHalfWidth,
                anchorX);
            anchor = new Vector3(
                anchorX,
                TornTopAtX(sample, anchorX),
                PackPlaneZ);
            tangent = new Vector3(
                1f,
                Mathf.Sin(normalizedX * 13.7f + 0.4f) * peeled * 0.014f,
                Mathf.Cos(normalizedX * 11.3f + 0.9f) * peeled * 0.022f)
                .normalized;
            float twistDegrees = -Mathf.Lerp(
                SealedFoilTwistDegrees,
                FreedFoilTwistDegrees,
                peeled);
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

        private static Vector3 EvaluateFoilPoint(
            Vector3 anchor,
            Vector3 tangent,
            Vector3 widthDirection,
            Vector3 surfaceNormal,
            float row01,
            float release,
            float width,
            float grain)
        {
            float peeled = Smooth01(release);
            float middleCurl = Mathf.Sin(row01 * Mathf.PI)
                * peeled
                * (0.0034f + Mathf.Abs(grain) * 0.0008f);
            float edgeCurl = row01 * row01 * peeled * 0.0058f;
            float fibreShift = grain * row01 * peeled * 0.0008f;
            return anchor
                + widthDirection * (row01 * width)
                - surfaceNormal * (middleCurl + edgeCurl)
                + tangent * fibreShift;
        }

        private static float FoilGrain(float x)
        {
            float normalized = Mathf.InverseLerp(
                -PackHalfWidth,
                PackHalfWidth,
                x);
            return Mathf.Sin(normalized * 71.9f + 0.31f) * 0.48f
                + Mathf.Sin(normalized * 129.7f + 1.87f) * 0.30f
                + Mathf.Sin(normalized * 191.3f + 4.02f) * 0.14f;
        }

        private void BuildCavityMesh()
        {
            cavityMesh = new Mesh
            {
                name = "Gate04R011ShapedParallaxCavity",
                subMeshCount = 2
            };
            cavityMesh.MarkDynamic();
            cavityMesh.triangles = Array.Empty<int>();
            cavityMeshFilter.sharedMesh = cavityMesh;
        }

        /// <summary>
        /// Builds the bag interior that the receding front face uncovers.
        /// Iteration 09 only drew a thin ribbon hugging the receding edge, so the
        /// vacated region showed background and the Pack read as being sliced
        /// short rather than opened. The interior now keeps the bag's original
        /// rim: a back wall behind the concealed case, a cross wall at the tear
        /// front, a side wall at the released end, and a lip that gives the torn
        /// front edge visible foil thickness.
        /// </summary>
        private void UpdateCavityMesh(PackOpeningGate04R011Sample sample)
        {
            cavityVertices.Clear();
            cavityUvs.Clear();
            cavityTriangles.Clear();
            cavityContactTriangles.Clear();
            CavityVisibleColumnCount = 0;
            CavityMaximumOpenHeight = 0f;
            interiorRowSpan = 0;
            interiorWallBottomRow = 0;

            bool fullyTorn = sample.TearProgress >= 0.999f;
            int firstOpenBoundary = -1;
            int lastOpenBoundary = -1;
            for (int column = 0; column < StripSegments; column++)
            {
                float leftX = Mathf.Lerp(
                    -PackHalfWidth,
                    PackHalfWidth,
                    column / (float)StripSegments);
                float rightX = Mathf.Lerp(
                    -PackHalfWidth,
                    PackHalfWidth,
                    (column + 1) / (float)StripSegments);
                if (!fullyTorn && rightX <= TearFrontXLocal)
                {
                    continue;
                }

                EvaluateColumnOpening(
                    sample,
                    column,
                    out float leftTornTop,
                    out float leftOriginalTop);
                EvaluateColumnOpening(
                    sample,
                    column + 1,
                    out float rightTornTop,
                    out float rightOriginalTop);
                float openHeight = Mathf.Max(
                    leftOriginalTop - leftTornTop,
                    rightOriginalTop - rightTornTop);
                if (openHeight <= 0.0004f)
                {
                    continue;
                }
                CavityVisibleColumnCount++;
                CavityMaximumOpenHeight = Mathf.Max(
                    CavityMaximumOpenHeight,
                    openHeight);
                if (firstOpenBoundary < 0)
                {
                    firstOpenBoundary = column;
                }
                lastOpenBoundary = column + 1;

                // Torn front-edge lip stays per column: it is the foil's cut
                // thickness and has to keep the high-frequency irregularity of
                // the contour. The interior behind it is welded instead.
                AddCavityQuad(
                    new Vector3(leftX, leftTornTop, PackPlaneZ + 0.0004f),
                    new Vector3(rightX, rightTornTop, PackPlaneZ + 0.0004f),
                    new Vector3(
                        rightX,
                        rightTornTop - TornEdgeLipDrop,
                        PackPlaneZ + TornEdgeLipDepth),
                    new Vector3(
                        leftX,
                        leftTornTop - TornEdgeLipDrop,
                        PackPlaneZ + TornEdgeLipDepth),
                    0.98f,
                    0.62f);
            }

            if (firstOpenBoundary >= 0)
            {
                AddWeldedInterior(sample, firstOpenBoundary, lastOpenBoundary);
            }

            float shallowWallZ = Mathf.Min(
                interiorBackWallZ,
                PackPlaneZ + InteriorSideWallDepth);
            // Cross wall at the tear front closes the opened region against the
            // still-sealed region, so the mouth never leaks background.
            if (!fullyTorn && TearFrontXLocal < PackHalfWidth)
            {
                EvaluateColumnOpeningAtX(
                    sample,
                    TearFrontXLocal,
                    out float frontTornTop,
                    out float frontOriginalTop);
                if (frontOriginalTop - frontTornTop > 0.0004f)
                {
                    AddCavityQuad(
                        new Vector3(
                            TearFrontXLocal,
                            frontTornTop - 0.004f,
                            PackPlaneZ),
                        new Vector3(
                            TearFrontXLocal,
                            frontTornTop - 0.004f,
                            shallowWallZ),
                        new Vector3(
                            TearFrontXLocal,
                            frontOriginalTop,
                            shallowWallZ),
                        new Vector3(
                            TearFrontXLocal,
                            frontOriginalTop,
                            PackPlaneZ),
                        0.10f,
                        0.80f);
                }
            }

            // Side wall at the released end keeps the rim reading as a bag mouth
            // instead of an open-ended trough.
            EvaluateColumnOpening(
                sample,
                StripSegments,
                out float endTornTop,
                out float endOriginalTop);
            if (endOriginalTop - endTornTop > 0.0004f)
            {
                float sideWallX = PackHalfWidth - 0.0035f;
                AddCavityQuad(
                    new Vector3(sideWallX, endTornTop - 0.004f, shallowWallZ),
                    new Vector3(sideWallX, endTornTop - 0.004f, PackPlaneZ),
                    new Vector3(sideWallX, endOriginalTop, PackPlaneZ),
                    new Vector3(sideWallX, endOriginalTop, shallowWallZ),
                    0.10f,
                    0.80f);
            }

            cavityMesh.Clear(false);
            cavityMesh.SetVertices(cavityVertices);
            cavityMesh.SetUVs(0, cavityUvs);
            cavityMesh.subMeshCount = 2;
            cavityMesh.SetTriangles(cavityTriangles, 0);
            cavityMesh.SetTriangles(cavityContactTriangles, 1);
            cavityMesh.RecalculateNormals();
            cavityMesh.RecalculateBounds();
            MeasureInteriorNormalContinuity();
        }

        /// <summary>
        /// Reports the worst normal disagreement between neighbouring interior
        /// columns so the comb regression cannot come back unnoticed.
        /// </summary>
        private void MeasureInteriorNormalContinuity()
        {
            CavityInteriorMaxAdjacentNormalAngleDegrees = 0f;
            if (interiorRowSpan < 2)
            {
                return;
            }
            Vector3[] normals = cavityMesh.normals;
            if (normals == null
                || interiorWallBottomRow + interiorRowSpan > normals.Length)
            {
                return;
            }
            for (int index = 0; index < interiorRowSpan - 1; index++)
            {
                float angle = Vector3.Angle(
                    normals[interiorWallBottomRow + index],
                    normals[interiorWallBottomRow + index + 1]);
                CavityInteriorMaxAdjacentNormalAngleDegrees = Mathf.Max(
                    CavityInteriorMaxAdjacentNormalAngleDegrees,
                    angle);
            }
        }

        /// <summary>
        /// Builds the bag interior as one welded strip across the opened span.
        /// Neighbouring columns share vertices, so <c>RecalculateNormals</c>
        /// averages along x and the wall reads as a continuous surface.
        ///
        /// Iteration 10 emitted an independent quad per column. Because the
        /// jittered contour gave each quad a different top and bottom edge, no
        /// quad was planar, every column ended up with its own normal, and the
        /// interior rendered as a vertical comb of 48 stripes.
        /// </summary>
        private void AddWeldedInterior(
            PackOpeningGate04R011Sample sample,
            int firstBoundary,
            int lastBoundary)
        {
            int span = lastBoundary - firstBoundary + 1;
            if (span < 2)
            {
                return;
            }
            interiorRowSpan = span;

            float lowestTornTop = float.MaxValue;
            float highestOriginalTop = float.MinValue;
            for (int boundary = firstBoundary; boundary <= lastBoundary; boundary++)
            {
                EvaluateColumnOpening(
                    sample,
                    boundary,
                    out float tornTop,
                    out float originalTop);
                lowestTornTop = Mathf.Min(lowestTornTop, tornTop);
                highestOriginalTop = Mathf.Max(highestOriginalTop, originalTop);
            }
            float bottomY = lowestTornTop - 0.0035f;
            float topY = highestOriginalTop + 0.0015f;
            float contactY = Mathf.Min(
                topY - 0.0015f,
                bottomY + 0.0065f);

            // Four rows: contact-band bottom, contact-band top, wall bottom and
            // wall top. The two middle rows are co-located but separate so the
            // crease between the occluded band and the lit wall stays crisp
            // while both remain welded along x.
            int bottomRow = cavityVertices.Count;
            int contactTopRow = bottomRow + span;
            int wallBottomRow = contactTopRow + span;
            int topRow = wallBottomRow + span;
            interiorWallBottomRow = wallBottomRow;
            for (int row = 0; row < 4; row++)
            {
                for (int boundary = firstBoundary;
                    boundary <= lastBoundary;
                    boundary++)
                {
                    float x = Mathf.Lerp(
                        -PackHalfWidth,
                        PackHalfWidth,
                        boundary / (float)StripSegments);
                    float u = (boundary - firstBoundary) / (float)(span - 1);
                    if (row == 0)
                    {
                        cavityVertices.Add(new Vector3(
                            x,
                            bottomY,
                            interiorBackWallZ));
                        cavityUvs.Add(new Vector2(u, 0f));
                    }
                    else if (row == 3)
                    {
                        cavityVertices.Add(new Vector3(
                            x,
                            topY,
                            interiorBackWallZ - InteriorRimTilt));
                        cavityUvs.Add(new Vector2(u, 1f));
                    }
                    else
                    {
                        cavityVertices.Add(new Vector3(
                            x,
                            contactY,
                            interiorBackWallZ));
                        cavityUvs.Add(new Vector2(u, 0.35f));
                    }
                }
            }

            AddWeldedBand(bottomRow, contactTopRow, span, cavityContactTriangles);
            AddWeldedBand(wallBottomRow, topRow, span, cavityTriangles);
        }

        private static void AddWeldedBand(
            int lowerRow,
            int upperRow,
            int span,
            List<int> target)
        {
            for (int index = 0; index < span - 1; index++)
            {
                int lowerLeft = lowerRow + index;
                int lowerRight = lowerRow + index + 1;
                int upperLeft = upperRow + index;
                int upperRight = upperRow + index + 1;
                target.Add(lowerLeft);
                target.Add(upperRight);
                target.Add(lowerRight);
                target.Add(lowerLeft);
                target.Add(upperLeft);
                target.Add(upperRight);
            }
        }

        private void EvaluateColumnOpening(
            PackOpeningGate04R011Sample sample,
            int column,
            out float tornTop,
            out float originalTop)
        {
            float x = Mathf.Lerp(
                -PackHalfWidth,
                PackHalfWidth,
                column / (float)StripSegments);
            originalTop = TearSeamY;
            tornTop = TornTopAtX(sample, x);
        }

        private void EvaluateColumnOpeningAtX(
            PackOpeningGate04R011Sample sample,
            float x,
            out float tornTop,
            out float originalTop)
        {
            originalTop = TearSeamY;
            tornTop = TornTopAtX(sample, x);
        }

        private float OpeningFractionAtX(
            PackOpeningGate04R011Sample sample,
            float x)
        {
            float front = TearFrontXFor(sample);
            if (sample.TearProgress <= 0.0001f || x <= front)
            {
                return 0f;
            }
            return Smooth01(Mathf.InverseLerp(
                0f,
                ReleasedFoilRampMeters,
                x - front));
        }

        private static float ReleaseFractionAtX(
            PackOpeningGate04R011Sample sample,
            float x)
        {
            float front = TearFrontXFor(sample);
            if (sample.TearProgress <= 0.0001f || x <= front)
            {
                return 0f;
            }
            return Smooth01(Mathf.InverseLerp(
                0f,
                ReleasedFoilRampMeters,
                x - front));
        }

        private static float TearFrontXFor(PackOpeningGate04R011Sample sample)
        {
            return Mathf.Lerp(
                PackHalfWidth,
                -PackHalfWidth,
                sample.TearProgress);
        }

        private float TornTopAtX(
            PackOpeningGate04R011Sample sample,
            float x)
        {
            float opened = OpeningFractionAtX(sample, x);
            return TearSeamY
                + TearOffsetAtX(x) * opened
                - ApertureDepth * sample.ApertureProgress * opened;
        }

        private void AddCavityQuad(
            Vector3 a,
            Vector3 b,
            Vector3 c,
            Vector3 d,
            float bottomV,
            float topV,
            bool contactBand = false)
        {
            List<int> target = contactBand
                ? cavityContactTriangles
                : cavityTriangles;
            int baseIndex = cavityVertices.Count;
            cavityVertices.Add(a);
            cavityVertices.Add(b);
            cavityVertices.Add(c);
            cavityVertices.Add(d);
            cavityUvs.Add(new Vector2(0f, bottomV));
            cavityUvs.Add(new Vector2(1f, bottomV));
            cavityUvs.Add(new Vector2(1f, topV));
            cavityUvs.Add(new Vector2(0f, topV));
            target.Add(baseIndex);
            target.Add(baseIndex + 2);
            target.Add(baseIndex + 1);
            target.Add(baseIndex);
            target.Add(baseIndex + 3);
            target.Add(baseIndex + 2);
        }

        private void BuildContactShadowMesh()
        {
            contactShadowMesh = new Mesh
            {
                name = "Gate04R011RestrainedContactShadow"
            };
            contactShadowMesh.vertices = contactShadowVertices;
            contactShadowMesh.uv = contactShadowUvs;
            contactShadowMesh.triangles = contactShadowTriangles;
            contactShadowMeshFilter.sharedMesh = contactShadowMesh;
        }

        private void UpdateContactShadow(PackOpeningGate04R011Sample sample)
        {
            float front = TearFrontXLocal;
            float x0 = Mathf.Max(-PackHalfWidth, front - 0.012f);
            float x1 = Mathf.Min(PackHalfWidth, front + 0.038f);
            float y = TornTopAtX(sample, front) - 0.0045f;
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
                name = "Gate04R011MovingNarrowFoilSpecular"
            };
            specularMesh.vertices = specularVertices;
            specularMesh.uv = specularUvs;
            specularMesh.triangles = specularTriangles;
            specularMeshFilter.sharedMesh = specularMesh;
        }

        private void UpdateSpecularHighlight(PackOpeningGate04R011Sample sample)
        {
            float span = Mathf.Max(0f, PackHalfWidth - TearFrontXLocal);
            float center = Mathf.Lerp(0.30f, 0.76f, sample.TearProgress);
            float s0 = Mathf.Clamp01(center - 0.080f);
            float s1 = Mathf.Clamp01(center + 0.080f);
            float x0 = TearFrontXLocal + span * s0;
            float x1 = TearFrontXLocal + span * s1;
            float release0 = ReleaseFractionAtX(sample, x0);
            float release1 = ReleaseFractionAtX(sample, x1);
            EvaluateFoilFrame(
                x0,
                release0,
                sample,
                out Vector3 anchor0,
                out Vector3 tangent0,
                out Vector3 width0,
                out Vector3 normal0);
            EvaluateFoilFrame(
                x1,
                release1,
                sample,
                out Vector3 anchor1,
                out Vector3 tangent1,
                out Vector3 width1,
                out Vector3 normal1);
            Vector3 center0 = EvaluateFoilPoint(
                anchor0,
                tangent0,
                width0,
                normal0,
                0.55f,
                release0,
                StripHeight,
                FoilGrain(x0));
            Vector3 center1 = EvaluateFoilPoint(
                anchor1,
                tangent1,
                width1,
                normal1,
                0.55f,
                release1,
                StripHeight,
                FoilGrain(x1));
            float halfWidth = StripHeight * 0.050f;
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
            AppendVector(builder, packRoot.localPosition);
            AppendVector(builder, packRoot.localScale);
            AppendVector(builder, caseMotionRoot.localPosition);
            AppendQuaternion(builder, caseMotionRoot.localRotation);
            AppendVector(builder, caseMotionRoot.localScale);
            builder.Append(packBodyRenderer.enabled ? '1' : '0');
            builder.Append(tearStripRenderer.enabled ? '1' : '0');
            builder.Append(cavityRenderer.enabled ? '1' : '0');
            builder.Append(contactShadowRenderer.enabled ? '1' : '0');
            builder.Append(specularRenderer.enabled ? '1' : '0');
            foreach (ParticleSystem system in SourceEffectSystems)
            {
                builder.Append(system != null ? system.particleCount : -1)
                    .Append('|');
            }
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
                packBodyRenderer,
                includeTexture: true);
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
            AppendFloat(builder, properties.GetFloat(DissolveId));
            AppendFloat(builder, properties.GetFloat(ProgressId));
            AppendFloat(builder, properties.GetFloat(RevealId));
            AppendFloat(builder, properties.GetFloat(IntensityId));
            if (includeTexture)
            {
                Texture texture = properties.GetTexture(BaseMapId);
                builder.Append(texture != null ? texture.name : "null")
                    .Append('|');
            }
        }

        private static void AppendVertices(
            StringBuilder builder,
            IReadOnlyList<Vector3> vertices)
        {
            for (int index = 0; index < vertices.Count; index++)
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

        private void SimulateSourceSystem(
            ParticleSystem system,
            bool enabled,
            float age,
            float authoredDuration)
        {
            if (system == null)
            {
                return;
            }
            system.Stop(
                true,
                ParticleSystemStopBehavior.StopEmittingAndClear);
            if (!enabled || age < 0f)
            {
                return;
            }
            float clampedAge = Mathf.Min(age, authoredDuration);
            system.Simulate(clampedAge, true, true, true);
            system.Pause(true);
            ParticleSystemRenderer renderer =
                system.GetComponent<ParticleSystemRenderer>();
            if (renderer == null)
            {
                return;
            }
            renderer.GetPropertyBlock(sourceEffectProperties);
            sourceEffectProperties.SetFloat(
                ProgressId,
                Mathf.Clamp01(clampedAge / authoredDuration));
            sourceEffectProperties.SetFloat(RevealId, 1f);
            sourceEffectProperties.SetFloat(IntensityId, 1f);
            renderer.SetPropertyBlock(sourceEffectProperties);
        }

        private void StopSourceEffects()
        {
            StopParticles(sourceActivationGlow);
            StopParticles(sourceLightningStrips);
            StopParticles(sourceLightningSparks);
            StopParticles(sourceExplosionDust);
            StopParticles(sourceExplosionFlares);
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
