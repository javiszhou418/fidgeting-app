using System;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Candidates
{
    [DisallowMultipleComponent]
    public sealed class PackOpeningGate04R009Controller : MonoBehaviour
    {
        private static readonly int OpeningId = Shader.PropertyToID("_Opening");
        private static readonly int RetreatId = Shader.PropertyToID("_Retreat");
        private static readonly int TearEdgeId = Shader.PropertyToID("_TearEdge");
        private static readonly int FoilSweepId = Shader.PropertyToID("_FoilSweep");
        private static readonly int BaseColorId = Shader.PropertyToID("_BaseColor");
        private static readonly int SheenCenterId = Shader.PropertyToID("_SheenCenter");
        private static readonly int SheenWidthId = Shader.PropertyToID("_SheenWidth");
        private static readonly int SheenStrengthId = Shader.PropertyToID("_SheenStrength");
        private static readonly int SheenFalloffId = Shader.PropertyToID("_SheenFalloff");

        private const int FlapSegmentCount = 18;
        private const int FlapRows = 5;
        private const int OpeningSegments = 48;
        private const float PackWidth = 0.145f;
        private const float PackHeight = PackWidth * 4f / 3f;
        private const float FlapVisibleWidth = PackWidth * 0.94f;
        private const float FlapVisibleHeight = PackHeight * 0.236f;
        private const float FlapSeamY = PackHeight * 0.215f;

        [SerializeField] private PackOpeningGate04R009Profile profile;
        [SerializeField] private Camera captureCamera;
        [SerializeField] private Renderer packBodyRenderer;
        [SerializeField] private MeshFilter flapMeshFilter;
        [SerializeField] private Renderer flapRenderer;
        [SerializeField] private MeshFilter openingRimMeshFilter;
        [SerializeField] private Renderer openingRimRenderer;
        [SerializeField] private Transform caseMotionRoot;
        [SerializeField] private PremiumDisplayCaseShippingPresentation casePresentation;
        [SerializeField] private Transform localizedFlash;
        [SerializeField] private Renderer localizedFlashRenderer;
        [SerializeField] private Transform shockwave;
        [SerializeField] private Renderer shockwaveRenderer;
        [SerializeField] private ParticleSystem foilShards;
        [SerializeField] private ParticleSystem glints;
        [SerializeField] private ParticleSystem directionalStreaks;
        [SerializeField] private Light openingLight;

        private readonly Vector3[] flapVertices =
            new Vector3[(FlapSegmentCount + 1) * FlapRows];
        private readonly Vector2[] flapUvs =
            new Vector2[(FlapSegmentCount + 1) * FlapRows];
        private readonly Color[] flapColors =
            new Color[(FlapSegmentCount + 1) * FlapRows];
        private readonly int[] flapTriangles =
            new int[FlapSegmentCount * (FlapRows - 1) * 6];
        private readonly Vector3[] openingVertices =
            new Vector3[OpeningSegments * 2];
        private readonly Vector2[] openingUvs =
            new Vector2[OpeningSegments * 2];
        private readonly int[] openingTriangles =
            new int[(OpeningSegments - 1) * 6];

        private Mesh flapMesh;
        private Mesh openingRimMesh;
        private MaterialPropertyBlock packProperties;
        private MaterialPropertyBlock accentProperties;
        private MaterialPropertyBlock caseProperties;
        private Vector3 cameraBasePosition;
        private Quaternion cameraBaseRotation;
        private float cameraBaseFov;
        private bool initialized;

        public PackOpeningGate04R009Profile Profile => profile;
        public PremiumDisplayCaseShippingPresentation CasePresentation =>
            casePresentation;
        public float ElapsedSeconds { get; private set; }
        public bool ReduceMotion { get; private set; }
        public PackOpeningGate04R009Sample CurrentSample { get; private set; }

        public bool HasRequiredBindings =>
            profile != null
            && captureCamera != null
            && packBodyRenderer != null
            && flapMeshFilter != null
            && flapRenderer != null
            && openingRimMeshFilter != null
            && openingRimRenderer != null
            && caseMotionRoot != null
            && casePresentation != null
            && localizedFlash != null
            && localizedFlashRenderer != null
            && shockwave != null
            && shockwaveRenderer != null
            && foilShards != null
            && glints != null
            && directionalStreaks != null
            && openingLight != null;

        public void Configure(
            PackOpeningGate04R009Profile authoredProfile,
            Camera authoredCamera,
            Renderer authoredPackBodyRenderer,
            MeshFilter authoredFlapMeshFilter,
            Renderer authoredFlapRenderer,
            MeshFilter authoredOpeningRimMeshFilter,
            Renderer authoredOpeningRimRenderer,
            Transform authoredCaseMotionRoot,
            PremiumDisplayCaseShippingPresentation authoredCasePresentation,
            Transform authoredLocalizedFlash,
            Renderer authoredLocalizedFlashRenderer,
            Transform authoredShockwave,
            Renderer authoredShockwaveRenderer,
            ParticleSystem authoredFoilShards,
            ParticleSystem authoredGlints,
            ParticleSystem authoredDirectionalStreaks,
            Light authoredOpeningLight)
        {
            profile = authoredProfile;
            captureCamera = authoredCamera;
            packBodyRenderer = authoredPackBodyRenderer;
            flapMeshFilter = authoredFlapMeshFilter;
            flapRenderer = authoredFlapRenderer;
            openingRimMeshFilter = authoredOpeningRimMeshFilter;
            openingRimRenderer = authoredOpeningRimRenderer;
            caseMotionRoot = authoredCaseMotionRoot;
            casePresentation = authoredCasePresentation;
            localizedFlash = authoredLocalizedFlash;
            localizedFlashRenderer = authoredLocalizedFlashRenderer;
            shockwave = authoredShockwave;
            shockwaveRenderer = authoredShockwaveRenderer;
            foilShards = authoredFoilShards;
            glints = authoredGlints;
            directionalStreaks = authoredDirectionalStreaks;
            openingLight = authoredOpeningLight;
            Initialize();
            SetTime(0f, false);
        }

        private void Awake()
        {
            Initialize();
        }

        private void OnDestroy()
        {
            DestroyOwned(flapMesh);
            DestroyOwned(openingRimMesh);
        }

        public void SetTime(float elapsedSeconds, bool reduceMotion)
        {
            Initialize();
            if (!HasRequiredBindings)
            {
                throw new MissingReferenceException(
                    "Gate 04 rev 9 controller bindings are incomplete.");
            }

            ElapsedSeconds = Mathf.Clamp(
                elapsedSeconds,
                0f,
                PackOpeningGate04R009Profile.TotalSeconds);
            ReduceMotion = reduceMotion;
            CurrentSample = profile.Evaluate(ElapsedSeconds, reduceMotion);

            ApplyPack(CurrentSample);
            ApplyCase(CurrentSample);
            ApplyImpact(CurrentSample);
            ApplyCamera(CurrentSample);
        }

        private void Initialize()
        {
            if (initialized || !HasRequiredBindings)
            {
                return;
            }

            cameraBasePosition = captureCamera.transform.position;
            cameraBaseRotation = captureCamera.transform.rotation;
            cameraBaseFov = captureCamera.fieldOfView;
            packProperties = new MaterialPropertyBlock();
            accentProperties = new MaterialPropertyBlock();
            caseProperties = new MaterialPropertyBlock();
            BuildFlapMesh();
            BuildOpeningRimMesh();
            StopParticles(foilShards);
            StopParticles(glints);
            StopParticles(directionalStreaks);
            casePresentation.SetTimeForPreview(
                casePresentation.RevealProfile.TotalDurationSeconds);
            initialized = true;
        }

        private void ApplyPack(PackOpeningGate04R009Sample sample)
        {
            bool packVisible = sample.PackRetreat < 0.999f;
            packBodyRenderer.enabled = packVisible;
            flapRenderer.enabled = packVisible;
            openingRimRenderer.enabled =
                packVisible && sample.OpeningProgress > 0.005f;

            packBodyRenderer.GetPropertyBlock(packProperties);
            packProperties.SetFloat(OpeningId, sample.OpeningProgress);
            packProperties.SetFloat(RetreatId, sample.PackRetreat);
            packProperties.SetFloat(
                TearEdgeId,
                Mathf.SmoothStep(0.22f, 1f, sample.TearProgress));
            packProperties.SetFloat(
                FoilSweepId,
                Mathf.Lerp(-0.15f, 1.15f, sample.TearProgress));
            packBodyRenderer.SetPropertyBlock(packProperties);

            UpdateFlapMesh(sample);
            UpdateOpeningRim(sample);
        }

        private void ApplyCase(PackOpeningGate04R009Sample sample)
        {
            bool caseVisible = sample.CaseEntry > 0.006f;
            caseMotionRoot.gameObject.SetActive(caseVisible);
            if (!caseVisible)
            {
                return;
            }

            float entry = sample.CaseEntry;
            caseMotionRoot.localPosition = Vector3.Lerp(
                new Vector3(0f, FlapSeamY + 0.010f, 0.080f),
                new Vector3(0f, -0.014f, 0f),
                entry);
            caseMotionRoot.localRotation = Quaternion.Euler(
                0f,
                sample.CaseRotationDegrees,
                0f);
            float scale = Mathf.Lerp(0.22f, 0.82f, entry);
            caseMotionRoot.localScale = Vector3.one * scale;

            float sheenStrength = sample.CaseSweep <= 0f
                ? 0f
                : Mathf.Sin(sample.CaseSweep * Mathf.PI) * 0.26f;
            foreach (Renderer renderer in casePresentation.EffectRenderers)
            {
                if (renderer == null)
                {
                    continue;
                }
                renderer.GetPropertyBlock(caseProperties);
                caseProperties.SetFloat(
                    SheenCenterId,
                    Mathf.Lerp(-0.14f, 1.14f, sample.CaseSweep));
                caseProperties.SetFloat(SheenWidthId, 0.070f);
                caseProperties.SetFloat(SheenStrengthId, sheenStrength);
                caseProperties.SetFloat(SheenFalloffId, 0.34f);
                renderer.SetPropertyBlock(caseProperties);
            }
        }

        private void ApplyImpact(PackOpeningGate04R009Sample sample)
        {
            bool flashVisible = sample.LocalizedFlash > 0.001f;
            localizedFlash.gameObject.SetActive(flashVisible);
            if (flashVisible)
            {
                localizedFlash.localScale = Vector3.one
                    * Mathf.Lerp(0.034f, 0.068f, sample.LocalizedFlash);
                SetAccentColor(
                    localizedFlashRenderer,
                    new Color(
                        1f,
                        0.985f,
                        0.94f,
                        Mathf.Lerp(0.18f, 0.96f, sample.LocalizedFlash)));
            }

            bool shockwaveVisible = sample.ShockwaveProgress > 0.001f;
            shockwave.gameObject.SetActive(shockwaveVisible);
            if (shockwaveVisible)
            {
                float progress = sample.ShockwaveProgress;
                float scale = Mathf.Lerp(
                    0.035f,
                    0.125f,
                    EaseOutQuart(progress));
                shockwave.localScale = new Vector3(
                    scale,
                    scale * 0.56f,
                    scale);
                SetAccentColor(
                    shockwaveRenderer,
                    new Color(
                        0.38f,
                        0.27f,
                        0.54f,
                        Mathf.Sin(progress * Mathf.PI) * 0.11f));
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

            float openingEnergy = Mathf.Clamp01(
                sample.OpeningProgress * (1f - sample.PackRetreat) * 0.24f
                + sample.LocalizedFlash * 1.8f
                + Mathf.Sin(sample.ShockwaveProgress * Mathf.PI) * 0.46f);
            openingLight.intensity = ReduceMotion
                ? openingEnergy * 0.22f
                : openingEnergy * 1.25f;
            openingLight.color = new Color(0.96f, 0.84f, 0.70f);
        }

        private void ApplyCamera(PackOpeningGate04R009Sample sample)
        {
            captureCamera.transform.position =
                cameraBasePosition
                + cameraBaseRotation * Vector3.forward * sample.CameraPush
                + cameraBaseRotation
                    * new Vector3(
                        sample.CameraKick.x,
                        sample.CameraKick.y,
                        0f);
            captureCamera.transform.rotation = cameraBaseRotation;
            captureCamera.fieldOfView = cameraBaseFov
                - sample.CameraPush * 7.5f
                + Mathf.Abs(sample.CameraKick.x) * 52f;
        }

        private void BuildFlapMesh()
        {
            flapMesh = new Mesh { name = "Gate04R009DeformingFoilFlap" };
            flapMesh.MarkDynamic();
            int triangle = 0;
            for (int segment = 0; segment < FlapSegmentCount; segment++)
            {
                for (int row = 0; row < FlapRows - 1; row++)
                {
                    int lower = segment * FlapRows + row;
                    int upper = lower + 1;
                    int nextLower = (segment + 1) * FlapRows + row;
                    int nextUpper = nextLower + 1;
                    flapTriangles[triangle++] = lower;
                    flapTriangles[triangle++] = upper;
                    flapTriangles[triangle++] = nextLower;
                    flapTriangles[triangle++] = nextLower;
                    flapTriangles[triangle++] = upper;
                    flapTriangles[triangle++] = nextUpper;
                }
            }
            flapMesh.vertices = flapVertices;
            flapMesh.uv = flapUvs;
            flapMesh.colors = flapColors;
            flapMesh.triangles = flapTriangles;
            flapMeshFilter.sharedMesh = flapMesh;
        }

        private void UpdateFlapMesh(PackOpeningGate04R009Sample sample)
        {
            const float uMin = 12f / 384f;
            const float uMax = 372f / 384f;
            const float vMin = 1f - 145f / 512f;
            const float vMax = 1f - 24f / 512f;
            float retreat = Mathf.SmoothStep(
                0f,
                1f,
                Mathf.InverseLerp(1.42f, 2.00f, ElapsedSeconds));

            for (int column = 0; column <= FlapSegmentCount; column++)
            {
                float columnU = column / (float)FlapSegmentCount;
                float threshold =
                    1f
                    - columnU
                    + 0.012f * Mathf.Sin(column * 1.83f + 0.8f);
                threshold = Mathf.Clamp01(threshold);
                float released = Mathf.SmoothStep(
                    0f,
                    1f,
                    Mathf.InverseLerp(
                        threshold - 0.035f,
                        threshold + 0.080f,
                        sample.TearProgress));
                float segmentVariation = 0.88f
                    + 0.12f * Mathf.Sin(column * 1.37f + 0.4f);

                for (int row = 0; row < FlapRows; row++)
                {
                    float row01 = row / (float)(FlapRows - 1);
                    float curlRadians =
                        row01
                        * released
                        * Mathf.Lerp(82f, 154f, row01)
                        * segmentVariation
                        * Mathf.Deg2Rad;
                    float radius = FlapVisibleHeight * 0.44f;
                    float curledY = Mathf.Sin(curlRadians) * radius;
                    float curledZ = -(1f - Mathf.Cos(curlRadians)) * radius;
                    float releaseLift =
                        released
                        * (
                            0.008f
                            + 0.021f * columnU
                            + 0.010f * row01
                        );
                    float stagger =
                        released
                        * 0.0018f
                        * Mathf.Sin(column * 1.6f + row01 * 1.7f);
                    float exitLift = retreat
                        * (0.016f + 0.072f * columnU)
                        * released;
                    float exitSide = retreat
                        * (0.032f + 0.096f * columnU)
                        * released;

                    int index = column * FlapRows + row;
                    float x = Mathf.Lerp(
                        -FlapVisibleWidth * 0.5f,
                        FlapVisibleWidth * 0.5f,
                        columnU);
                    flapVertices[index] = new Vector3(
                        x
                            + released * (0.006f + 0.012f * columnU)
                            + exitSide
                            + stagger,
                        FlapSeamY
                            + row01 * FlapVisibleHeight
                            + curledY
                            + releaseLift
                            + exitLift,
                        -0.003f
                            + curledZ
                            - released
                                * 0.013f
                                * Mathf.Sin(columnU * Mathf.PI * 2f)
                            - released * 0.006f
                            - retreat * 0.014f);
                    flapUvs[index] = new Vector2(
                        Mathf.Lerp(uMin, uMax, columnU),
                        Mathf.Lerp(vMin, vMax, row01));
                    float frontEdge = Mathf.Clamp01(
                        1f
                        - Mathf.Abs(sample.TearProgress - threshold) / 0.075f);
                    flapColors[index] = new Color(
                        released,
                        frontEdge,
                        0f,
                        1f);
                }
            }

            flapMesh.vertices = flapVertices;
            flapMesh.uv = flapUvs;
            flapMesh.colors = flapColors;
            flapMesh.RecalculateNormals();
            flapMesh.RecalculateBounds();
        }

        private void BuildOpeningRimMesh()
        {
            openingRimMesh = new Mesh
            {
                name = "Gate04R009IrregularTornFoilThickness"
            };
            openingRimMesh.MarkDynamic();
            int triangle = 0;
            for (int index = 0; index < OpeningSegments - 1; index++)
            {
                int next = index + 1;
                int outer = index * 2;
                int inner = outer + 1;
                int nextOuter = next * 2;
                int nextInner = nextOuter + 1;
                openingTriangles[triangle++] = outer;
                openingTriangles[triangle++] = nextOuter;
                openingTriangles[triangle++] = inner;
                openingTriangles[triangle++] = inner;
                openingTriangles[triangle++] = nextOuter;
                openingTriangles[triangle++] = nextInner;
            }
            openingRimMesh.vertices = openingVertices;
            openingRimMesh.uv = openingUvs;
            openingRimMesh.triangles = openingTriangles;
            openingRimMeshFilter.sharedMesh = openingRimMesh;
        }

        private void UpdateOpeningRim(PackOpeningGate04R009Sample sample)
        {
            float opening = Mathf.Max(0.001f, sample.OpeningProgress);
            float rightEdge = PackWidth * 0.465f;
            float leftEdge = PackWidth * -0.445f;
            float tearFront = Mathf.Lerp(rightEdge, leftEdge, opening);
            float thickness = Mathf.Lerp(0.00045f, 0.00125f, opening);
            for (int index = 0; index < OpeningSegments; index++)
            {
                float progress = index / (float)(OpeningSegments - 1);
                float x = Mathf.Lerp(tearFront, rightEdge, progress);
                float normalizedU = x / PackWidth + 0.5f;
                float depthEnvelope = Mathf.SmoothStep(
                    0f,
                    1f,
                    Mathf.InverseLerp(0f, 0.18f, progress));
                float bottomUv =
                    0.715f
                    + (1f - depthEnvelope) * 0.090f
                    - opening * 0.105f * depthEnvelope
                    + opening
                        * depthEnvelope
                        * (
                            0.016f * Mathf.Sin(normalizedU * 31f + 0.7f)
                            + 0.009f * Mathf.Sin(normalizedU * 67f + 2.1f)
                            + 0.004f * Mathf.Sin(normalizedU * 137f + 0.3f)
                        );
                float y = (bottomUv - 0.5f) * PackHeight;
                float fold = thickness
                    * (0.72f + 0.28f * Mathf.Sin(index * 2.4f + 0.5f));
                openingVertices[index * 2] = new Vector3(
                    x,
                    y + fold,
                    0f);
                openingVertices[index * 2 + 1] = new Vector3(
                    x,
                    y - fold,
                    -0.0008f);
                openingUvs[index * 2] = new Vector2(progress, 1f);
                openingUvs[index * 2 + 1] = new Vector2(progress, 0f);
            }
            openingRimMesh.vertices = openingVertices;
            openingRimMesh.uv = openingUvs;
            openingRimMesh.RecalculateNormals();
            openingRimMesh.RecalculateBounds();

            openingRimRenderer.GetPropertyBlock(accentProperties);
            accentProperties.SetColor(
                BaseColorId,
                Color.Lerp(
                    new Color(0.76f, 0.71f, 0.62f, 0.82f),
                    new Color(0.67f, 0.59f, 0.69f, 0.76f),
                    Mathf.Clamp01(sample.TearProgress - 0.72f) * 0.12f));
            openingRimRenderer.SetPropertyBlock(accentProperties);
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

        private static float EaseOutQuart(float value)
        {
            float clamped = Mathf.Clamp01(value);
            return 1f - Mathf.Pow(1f - clamped, 4f);
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
