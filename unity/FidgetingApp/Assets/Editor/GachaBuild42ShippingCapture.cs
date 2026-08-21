using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.Product.Gacha.Editor
{
    /// <summary>
    /// Reproducible Build 42 evidence capture. This deliberately instantiates
    /// the shipping resolver, reveal director, Resources display-case prefab
    /// and camera lease; it contains no parallel preview implementation.
    /// </summary>
    public static class GachaBuild42ShippingCapture
    {
        public const int FrameWidth = 480;
        public const int FrameHeight = 640;
        public const int FramesPerSecond = 30;
        public const string OutputArgument = "-gachaRevealOutput";
        public const string DefaultOutputParent =
            "../Artifacts/GachaBuild42ShippingReveal";

        private const int ContactCellWidth = 120;
        private const int ContactCellHeight = 160;
        private const int VisiblePixelChannelTolerance = 1;
        private const int VisiblePixelEdgeGuardPixels = 3;
        private const float Epsilon = 0.00001f;
        private static readonly int RevealVisibilityId =
            Shader.PropertyToID("_RevealVisibility");

        public static readonly GachaRevealPhase[] VisiblePhaseOrder =
        {
            GachaRevealPhase.Back,
            GachaRevealPhase.Front,
            GachaRevealPhase.Readable
        };

        [Serializable]
        public sealed class ViewportEvidence
        {
            public string measurementMethod;
            public bool measured;
            public float xMin;
            public float yMin;
            public float xMax;
            public float yMax;
            public float nearestDepth;
            public int foregroundPixelCount;
            public int edgeContactPixelCount;
            public int edgeGuardPixels;
            public string backgroundRgba;
            public bool withinShippingCropTolerance;
        }

        [Serializable]
        public sealed class RendererViewportEvidence
        {
            public string path;
            public string rendererType;
            public bool enabled;
            public bool activeInHierarchy;
            public bool transientBoxLid;
            public bool usesRevealVisibility;
            public float materialRevealVisibility;
            public float propertyBlockRevealVisibility;
            public bool measured;
            public float xMin;
            public float yMin;
            public float xMax;
            public float yMax;
            public float nearestDepth;
            public float overflow;
        }

        [Serializable]
        public sealed class PhaseEvidence
        {
            public string phase;
            public float sampleTimeSeconds;
            public float phaseProgress;
            public string keyframe;
            public float luminanceRange;
            public ViewportEvidence visibleContentViewport;
            public ViewportEvidence aggregateGeometryViewport;
            public RendererViewportEvidence[] rendererBoundsDiagnostics;
            public bool shellVisibilityCorrect;
            public bool prizeVisible;
            public bool passed;
        }

        [Serializable]
        public sealed class PrizeEvidence
        {
            public string prizeId;
            public string displayName;
            public string rarity;
            public string prizeKind;
            public string contentReference;
            public string presentationKind;
            public bool usesThreeBladeDisplayModel;
            public bool isPhysicalArtwork;
            public int rendererCount;
            public string[] componentTypes;
            public bool rendererOnly;
            public bool noPhysics;
            public bool noHapticComponents;
            public bool idleRotationEnabled;
            public float idleRotationPeriodErrorDegrees;
            public string caseResource;
            public string caseHierarchySignature;
            public string capsulePreset;
            public string capsuleDimensions;
            public string contentFitScale;
            public string contentFitOffset;
            public bool uniformFiniteFit;
            public string cameraSignature;
            public bool cameraStableAfterTwoFrames;
            public string cameraFailureReason;
            public string[] emittedPhases;
            public bool exactPhaseOrder;
            public int completionCount;
            public int frameCount;
            public string framePattern;
            public bool sequenceCropFree;
            public int sequenceCroppedFrameCount;
            public int sequenceFirstCroppedFrame;
            public int sequenceMaximumEdgeContactPixels;
            public PhaseEvidence[] phases;
            public bool dismissedCaseAndPrize;
            public bool passed;
        }

        [Serializable]
        public sealed class ContactSheetInput
        {
            public int row;
            public int column;
            public string prizeId;
            public string phase;
            public string image;
        }

        [Serializable]
        public sealed class ContactSheetManifest
        {
            public int rows;
            public int columns;
            public int cellWidth;
            public int cellHeight;
            public string output;
            public ContactSheetInput[] inputs;
        }

        [Serializable]
        public sealed class ShippingReport
        {
            public string generatedUtc;
            public string build;
            public string seriesId;
            public string runtimeContract;
            public string cropContract;
            public int frameWidth;
            public int frameHeight;
            public int framesPerSecond;
            public float revealDurationSeconds;
            public string ffmpegInputPattern;
            public int expectedPrizeCount;
            public int capturedPrizeCount;
            public bool allContentReferencesMapped;
            public bool sharedCase;
            public bool sharedCapsule;
            public bool sharedCamera;
            public PrizeEvidence[] prizes;
            public ContactSheetManifest contactSheet;
            public bool passed;
        }

        private readonly struct PhaseSample
        {
            public PhaseSample(GachaRevealPhase phase, float time)
            {
                Phase = phase;
                Time = time;
            }

            public GachaRevealPhase Phase { get; }
            public float Time { get; }
        }

        private sealed class CaptureEnvironment
        {
            public GameObject Root;
            public Camera Camera;
        }

        private sealed class CapturedImage
        {
            public byte[] Png;
            public float LuminanceRange;
            public ViewportEvidence VisiblePixelViewport;
            public int EdgeContactPixelCount;
        }

        [MenuItem("Fidgeting/Gacha/Capture Build 42 Shipping Reveal Gate")]
        public static void CaptureAll()
        {
            if (!Application.isBatchMode
                && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
            {
                return;
            }

            string outputRoot = ResolveOutputRoot(
                Environment.GetCommandLineArgs(),
                DateTime.UtcNow);
            CaptureAll(outputRoot);
        }

        /// <summary>Stable -executeMethod entry point for CI and release gates.</summary>
        public static void CaptureAllForCommandLine()
        {
            CaptureAll();
        }

        public static void CaptureAll(string outputRoot)
        {
            if (string.IsNullOrWhiteSpace(outputRoot))
            {
                throw new ArgumentException("Capture output is required.", nameof(outputRoot));
            }

            SceneSetup[] previousSetup = EditorSceneManager.GetSceneManagerSetup();
            Directory.CreateDirectory(outputRoot);
            var results = new List<PrizeEvidence>();
            var contactInputs = new List<ContactSheetInput>();

            try
            {
                EditorSceneManager.NewScene(
                    NewSceneSetup.EmptyScene,
                    NewSceneMode.Single);
                CaptureEnvironment environment = CreateEnvironment();
                GachaSeriesDefinition series = GachaCatalog.ResolveSeries(
                    GachaCatalog.LaunchSeriesId);
                if (series == null)
                {
                    throw new InvalidOperationException("Launch gacha series is missing.");
                }

                for (int index = 0; index < series.Prizes.Count; index++)
                {
                    PrizeEvidence result = CapturePrize(
                        series.Prizes[index],
                        index,
                        environment.Camera,
                        outputRoot,
                        contactInputs);
                    results.Add(result);
                }

                ContactSheetManifest contactSheet = BuildContactSheet(
                    outputRoot,
                    series.Prizes.Count,
                    contactInputs);
                ShippingReport report = BuildReport(
                    series,
                    results,
                    contactSheet);
                WriteJson(
                    Path.Combine(outputRoot, "shipping-validation.json"),
                    report);
                WriteJson(
                    Path.Combine(outputRoot, "contact-sheet-inputs.json"),
                    contactSheet);

                Debug.Log(
                    $"Build 42 shipping gacha capture: {outputRoot}; "
                    + $"passed={report.passed}");
                if (!report.passed)
                {
                    throw new InvalidOperationException(
                        "Build 42 gacha shipping reveal validation failed. "
                        + "Inspect shipping-validation.json.");
                }
            }
            finally
            {
                if (previousSetup != null
                    && previousSetup.Any(item => !string.IsNullOrEmpty(item.path)))
                {
                    EditorSceneManager.RestoreSceneManagerSetup(previousSetup);
                }
                else
                {
                    EditorSceneManager.NewScene(
                        NewSceneSetup.EmptyScene,
                        NewSceneMode.Single);
                }
            }
        }

        public static float PhaseMidpoint(GachaRevealPhase phase)
        {
            return phase switch
            {
                GachaRevealPhase.Back => GachaRevealTimeline.BackEnd * 0.5f,
                GachaRevealPhase.Front => (GachaRevealTimeline.BackEnd
                    + GachaRevealTimeline.FrontEnd) * 0.5f,
                GachaRevealPhase.Readable => (GachaRevealTimeline.FrontEnd
                    + GachaRevealTimeline.ReadableEnd) * 0.5f,
                _ => throw new ArgumentOutOfRangeException(nameof(phase), phase, null)
            };
        }

        public static string ResolveOutputRoot(string[] arguments, DateTime utcNow)
        {
            string[] args = arguments ?? Array.Empty<string>();
            for (int index = 0; index < args.Length - 1; index++)
            {
                if (string.Equals(args[index], OutputArgument,
                        StringComparison.Ordinal))
                {
                    return Path.GetFullPath(args[index + 1]);
                }
            }

            string runId = utcNow.ToUniversalTime().ToString(
                "yyyyMMdd'T'HHmmss'Z'",
                CultureInfo.InvariantCulture);
            return Path.GetFullPath(Path.Combine(
                Application.dataPath,
                DefaultOutputParent,
                runId));
        }

        private static PrizeEvidence CapturePrize(
            GachaPrizeDefinition prize,
            int row,
            Camera camera,
            string outputRoot,
            List<ContactSheetInput> contactInputs)
        {
            string prizeOutput = Path.Combine(outputRoot, prize.Id);
            string frameOutput = Path.Combine(prizeOutput, "frames");
            string phaseOutput = Path.Combine(prizeOutput, "phases");
            Directory.CreateDirectory(frameOutput);
            Directory.CreateDirectory(phaseOutput);

            var host = new GameObject("GachaBuild42CaptureHost_" + prize.Id);
            var director = host.AddComponent<GachaRevealDirector>();
            var emitted = new List<GachaRevealPhase>();
            int completions = 0;
            director.phaseChanged += emitted.Add;
            director.revealCompleted += () => completions++;
            PremiumDisplayCaseCameraLease lease = null;
            GameObject caseObject = null;
            GameObject prizeObject = null;

            try
            {
                lease = PremiumDisplayCaseCameraLease.Acquire(camera);
                if (!director.Prepare(prize))
                {
                    throw new InvalidOperationException(
                        $"{prize.Id}: {director.FailureReason}");
                }
                if (!director.StartReveal())
                {
                    throw new InvalidOperationException(
                        $"{prize.Id}: {director.FailureReason}");
                }

                caseObject = director.ActiveCase.gameObject;
                prizeObject = director.ActivePrize.gameObject;
                Renderer[] prizeRenderers = prizeObject.GetComponentsInChildren<Renderer>(
                    true);
                // Layer_08_BoxLid is excluded here too: gacha explicitly
                // disables it once retracted (see IsTransientBoxLid below),
                // so it is not part of the settled shell this gate verifies.
                Renderer[] shellRenderers = caseObject
                    .GetComponentsInChildren<Renderer>(true)
                    .Where(renderer => !renderer.transform.IsChildOf(
                        prizeObject.transform)
                        && !IsTransientBoxLid(renderer.transform, caseObject.transform))
                    .ToArray();

                bool rendererOnly = GachaPrizePresentationResolver.IsRendererOnly(
                    prizeObject);
                bool noPhysics = HasNoPhysics(prizeObject);
                string[] componentTypes = prizeObject
                    .GetComponentsInChildren<Component>(true)
                    .Where(component => component != null)
                    .Select(component => component.GetType().FullName)
                    .Distinct()
                    .OrderBy(value => value, StringComparer.Ordinal)
                    .ToArray();
                bool noHaptics = componentTypes.All(value =>
                    value.IndexOf("Haptic", StringComparison.OrdinalIgnoreCase) < 0);
                bool idleRotationEnabled = GachaPrizePresentationResolver
                    .SharedContentOptions.IdleRotationEnabled;
                bool uniformFiniteFit = IsUniformFinitePositive(
                    director.ActiveCase.ContentFitScale);
                string hierarchySignature = StableSignature(shellRenderers
                    .Select(renderer => RelativePath(
                        renderer.transform,
                        caseObject.transform))
                    .OrderBy(value => value, StringComparer.Ordinal));
                string cameraSignature = CameraSignature(camera);

                var phases = new List<PhaseEvidence>();
                using (var recorder = new FrameRecorder(camera))
                {
                    // Two real renders mirror the coordinator's two-frame
                    // camera-stability gate before native starts trusting it.
                    recorder.Render();
                    recorder.Render();
                    bool cameraStable = lease.IsPresentationStable(
                        caseObject.transform,
                        out string cameraFailure);

                    float elapsed = 0f;
                    int frameCount = 0;
                    int croppedFrameCount = 0;
                    int firstCroppedFrame = -1;
                    int maximumEdgeContactPixels = 0;
                    var phaseSamples = VisiblePhaseOrder
                        .Select(phase => new PhaseSample(
                            phase,
                            PhaseMidpoint(phase)))
                        .ToArray();
                    int phaseIndex = 0;
                    int maximumFrame = Mathf.CeilToInt(
                        GachaRevealTimeline.TotalSeconds * FramesPerSecond);

                    for (int frame = 0; frame <= maximumFrame; frame++)
                    {
                        float frameTime = Mathf.Min(
                            GachaRevealTimeline.TotalSeconds,
                            frame / (float)FramesPerSecond);
                        CaptureSamplesBefore(
                            phaseSamples,
                            ref phaseIndex,
                            frameTime,
                            ref elapsed,
                            director,
                            recorder,
                            phaseOutput,
                            prize,
                            row,
                            shellRenderers,
                            prizeRenderers,
                            phases,
                            contactInputs);
                        AdvanceTo(director, ref elapsed, frameTime);
                        CapturedImage image = recorder.Render(
                            measureEdgeContact: true);
                        if (image.EdgeContactPixelCount > 0)
                        {
                            if (firstCroppedFrame < 0)
                            {
                                firstCroppedFrame = frameCount;
                            }
                            croppedFrameCount++;
                            maximumEdgeContactPixels = Mathf.Max(
                                maximumEdgeContactPixels,
                                image.EdgeContactPixelCount);
                        }
                        File.WriteAllBytes(
                            Path.Combine(frameOutput, $"frame-{frameCount:0000}.png"),
                            image.Png);
                        frameCount++;
                    }

                    CaptureSamplesBefore(
                        phaseSamples,
                        ref phaseIndex,
                        float.PositiveInfinity,
                        ref elapsed,
                        director,
                        recorder,
                        phaseOutput,
                        prize,
                        row,
                        shellRenderers,
                        prizeRenderers,
                        phases,
                        contactInputs);
                    AdvanceTo(
                        director,
                        ref elapsed,
                        GachaRevealTimeline.TotalSeconds);

                    director.ActiveCase.AdvanceAnimation(
                        PremiumDisplayCaseRevealMotion.DurationSeconds + 0.1f);
                    Quaternion idleBefore = director.ActiveCase
                        .ContentOrbitRotation;
                    director.ActiveCase.AdvanceAnimation(
                        GachaPrizePresentationResolver.SharedContentOptions
                            .IdleRotationPeriodSeconds * 2f);
                    float idleRotationPeriodError = Quaternion.Angle(
                        idleBefore,
                        director.ActiveCase.ContentOrbitRotation);

                    GachaPrizePresentationResolver.TryResolveDescriptor(
                        prize.ContentReference,
                        out GachaPrizePresentationDescriptor descriptor);
                    var result = new PrizeEvidence
                    {
                        prizeId = prize.Id,
                        displayName = prize.DisplayName,
                        rarity = prize.Rarity.ToString(),
                        prizeKind = prize.Kind.ToString(),
                        contentReference = prize.ContentReference,
                        presentationKind = descriptor.Kind.ToString(),
                        usesThreeBladeDisplayModel =
                            descriptor.UsesThreeBladeDisplayModel,
                        isPhysicalArtwork = descriptor.IsPhysicalArtwork,
                        rendererCount = prizeRenderers.Length,
                        componentTypes = componentTypes,
                        rendererOnly = rendererOnly,
                        noPhysics = noPhysics,
                        noHapticComponents = noHaptics,
                        idleRotationEnabled = idleRotationEnabled,
                        idleRotationPeriodErrorDegrees = idleRotationPeriodError,
                        caseResource = PremiumDisplayCaseFactory.ResourcesPath,
                        caseHierarchySignature = hierarchySignature,
                        capsulePreset = director.ActiveCase.CapsulePreset.ToString(),
                        capsuleDimensions = Format(
                            director.ActiveCase.CapsuleDimensions.InnerSize),
                        contentFitScale = Format(
                            director.ActiveCase.ContentFitScale),
                        contentFitOffset = Format(
                            director.ActiveCase.ContentFitPosition),
                        uniformFiniteFit = uniformFiniteFit,
                        cameraSignature = cameraSignature,
                        cameraStableAfterTwoFrames = cameraStable,
                        cameraFailureReason = cameraFailure,
                        emittedPhases = emitted.Select(item => item.ToString())
                            .ToArray(),
                        exactPhaseOrder = emitted.SequenceEqual(
                            VisiblePhaseOrder.Concat(new[]
                            {
                                GachaRevealPhase.Complete
                            })),
                        completionCount = completions,
                        frameCount = frameCount,
                        framePattern = prize.Id + "/frames/frame-%04d.png",
                        sequenceCropFree = croppedFrameCount == 0,
                        sequenceCroppedFrameCount = croppedFrameCount,
                        sequenceFirstCroppedFrame = firstCroppedFrame,
                        sequenceMaximumEdgeContactPixels =
                            maximumEdgeContactPixels,
                        phases = phases.ToArray()
                    };
                    result.passed = result.rendererCount > 0
                        && result.rendererOnly
                        && result.noPhysics
                        && result.noHapticComponents
                        && result.idleRotationEnabled
                        && result.idleRotationPeriodErrorDegrees < 0.001f
                        && result.capsulePreset == PremiumDisplayCaseCapsulePreset
                            .CollectorSlabCompact.ToString()
                        && result.uniformFiniteFit
                        && result.cameraStableAfterTwoFrames
                        && result.exactPhaseOrder
                        && result.completionCount == 1
                        && result.sequenceCropFree
                        && result.phases.Length == VisiblePhaseOrder.Length
                        && result.phases.All(item => item.passed);

                    director.Dismiss();
                    result.dismissedCaseAndPrize = caseObject == null
                        && prizeObject == null;
                    result.passed &= result.dismissedCaseAndPrize;
                    WriteJson(
                        Path.Combine(prizeOutput, "validation.json"),
                        result);
                    return result;
                }
            }
            finally
            {
                director.Dismiss();
                lease?.Dispose();
                UnityEngine.Object.DestroyImmediate(host);
            }
        }

        private static void CaptureSamplesBefore(
            PhaseSample[] samples,
            ref int sampleIndex,
            float beforeOrAt,
            ref float elapsed,
            GachaRevealDirector director,
            FrameRecorder recorder,
            string phaseOutput,
            GachaPrizeDefinition prize,
            int row,
            Renderer[] shellRenderers,
            Renderer[] prizeRenderers,
            List<PhaseEvidence> phases,
            List<ContactSheetInput> contactInputs)
        {
            while (sampleIndex < samples.Length
                && samples[sampleIndex].Time <= beforeOrAt + Epsilon)
            {
                PhaseSample sample = samples[sampleIndex];
                AdvanceTo(director, ref elapsed, sample.Time);
                string filename = $"{sampleIndex + 1:00}_{PhaseToken(sample.Phase)}.png";
                string path = Path.Combine(phaseOutput, filename);
                CapturedImage image = recorder.Render(measureVisiblePixels: true);
                File.WriteAllBytes(path, image.Png);
                bool shellVisibility;
                if (sample.Phase == GachaRevealPhase.Back)
                {
                    Renderer[] identification = shellRenderers
                        .Where(IsFrontIdentificationRenderer)
                        .ToArray();
                    shellVisibility = identification.Length > 0
                        && identification.All(renderer => !renderer.enabled)
                        && shellRenderers
                            .Where(renderer => !IsFrontIdentificationRenderer(renderer))
                            .All(renderer => renderer.enabled);
                }
                else
                {
                    shellVisibility = shellRenderers.Length > 0
                        && shellRenderers.All(renderer => renderer.enabled);
                }
                bool prizeVisible = prizeRenderers.Length > 0
                    && prizeRenderers.All(renderer => renderer.enabled);
                ViewportEvidence aggregateGeometryViewport = MeasureViewport(
                    recorder.Camera,
                    director.ActiveCase.transform);
                ViewportEvidence viewport = image.VisiblePixelViewport;
                var evidence = new PhaseEvidence
                {
                    phase = sample.Phase.ToString(),
                    sampleTimeSeconds = sample.Time,
                    phaseProgress = director.PhaseProgress,
                    keyframe = prize.Id + "/phases/" + filename,
                    luminanceRange = image.LuminanceRange,
                    visibleContentViewport = viewport,
                    aggregateGeometryViewport = aggregateGeometryViewport,
                    rendererBoundsDiagnostics = MeasureRendererDiagnostics(
                        recorder.Camera,
                        director.ActiveCase.transform),
                    shellVisibilityCorrect = shellVisibility,
                    prizeVisible = prizeVisible
                };
                evidence.passed = director.Phase == sample.Phase
                    && Mathf.Abs(director.PhaseProgress - 0.5f) < 0.001f
                    && evidence.shellVisibilityCorrect
                    && evidence.prizeVisible
                    && evidence.luminanceRange > 0.05f
                    && viewport.measured
                    && viewport.withinShippingCropTolerance;
                phases.Add(evidence);
                contactInputs.Add(new ContactSheetInput
                {
                    row = row,
                    column = sampleIndex,
                    prizeId = prize.Id,
                    phase = sample.Phase.ToString(),
                    image = evidence.keyframe
                });
                sampleIndex++;
            }
        }

        private static void AdvanceTo(
            GachaRevealDirector director,
            ref float elapsed,
            float target)
        {
            float delta = Mathf.Max(0f, target - elapsed);
            if (delta > 0f)
            {
                director.Tick(delta);
                elapsed = target;
            }
        }

        private static bool IsFrontIdentificationRenderer(Renderer renderer)
        {
            if (renderer == null)
            {
                return false;
            }
            string name = renderer.name ?? string.Empty;
            return name == "LaserLevelMark"
                || name == "LaserProductName"
                || name == "FeaturedBadgeArtwork"
                || name == "FeaturedBadgeToken"
                || name == "FeaturedBadgeShortName"
                || name == "CollectorTierAndLevel"
                || name == "CollectorProductName"
                || name == "CollectorEdition"
                || name == "CollectorAcquiredDate"
                || name == "CollectorStableId"
                || name == "Collector_LabelPaper"
                || name == "Collector_RarityFoilBand"
                || name.StartsWith(
                    "Collector_LabelFoil_",
                    StringComparison.Ordinal);
        }

        private static ShippingReport BuildReport(
            GachaSeriesDefinition series,
            List<PrizeEvidence> results,
            ContactSheetManifest contactSheet)
        {
            bool allMapped = series.Prizes.All(prize =>
                GachaPrizePresentationResolver.TryResolveDescriptor(
                    prize.ContentReference,
                    out _));
            bool sharedCase = results.Select(item => item.caseResource)
                    .Distinct().Count() == 1
                && results.Select(item => item.caseHierarchySignature)
                    .Distinct().Count() == 1;
            bool sharedCapsule = results.Select(item => item.capsulePreset)
                    .Distinct().Count() == 1
                && results.Select(item => item.capsuleDimensions)
                    .Distinct().Count() == 1;
            bool sharedCamera = results.Select(item => item.cameraSignature)
                .Distinct().Count() == 1;
            var report = new ShippingReport
            {
                generatedUtc = DateTime.UtcNow.ToString(
                    "O", CultureInfo.InvariantCulture),
                build = "42",
                seriesId = series.Id,
                runtimeContract =
                    "GachaCatalog -> GachaPrizePresentationResolver -> "
                    + "GachaRevealDirector/GachaRevealSession -> "
                    + "Resources/Gacha/PremiumDisplayCase -> "
                    + "PremiumDisplayCaseCameraLease",
                cropContract =
                    "six midpoint rendered-visible-pixel bounds + every "
                    + "recorded frame three-pixel edge guard; aggregate and "
                    + "per-renderer bounds are diagnostic-only",
                frameWidth = FrameWidth,
                frameHeight = FrameHeight,
                framesPerSecond = FramesPerSecond,
                revealDurationSeconds = GachaRevealTimeline.TotalSeconds,
                ffmpegInputPattern =
                    "ffmpeg -framerate 30 -i <prize>/frames/frame-%04d.png "
                    + "-c:v libx264 -pix_fmt yuv420p <prize>.mp4",
                expectedPrizeCount = 8,
                capturedPrizeCount = results.Count,
                allContentReferencesMapped = allMapped,
                sharedCase = sharedCase,
                sharedCapsule = sharedCapsule,
                sharedCamera = sharedCamera,
                prizes = results.ToArray(),
                contactSheet = contactSheet
            };
            report.passed = report.capturedPrizeCount == report.expectedPrizeCount
                && report.allContentReferencesMapped
                && report.sharedCase
                && report.sharedCapsule
                && report.sharedCamera
                && report.prizes.All(item => item.passed);
            return report;
        }

        private static ContactSheetManifest BuildContactSheet(
            string outputRoot,
            int rowCount,
            List<ContactSheetInput> inputs)
        {
            int columns = VisiblePhaseOrder.Length;
            var contact = new Texture2D(
                columns * ContactCellWidth,
                rowCount * ContactCellHeight,
                TextureFormat.RGBA32,
                false,
                false);
            Color32 background = new Color32(8, 8, 10, 255);
            Color32[] contactPixels = Enumerable.Repeat(
                background,
                contact.width * contact.height).ToArray();

            foreach (ContactSheetInput input in inputs)
            {
                string sourcePath = Path.Combine(outputRoot, input.image);
                var source = new Texture2D(2, 2, TextureFormat.RGBA32, false, false);
                try
                {
                    if (!source.LoadImage(File.ReadAllBytes(sourcePath), false))
                    {
                        throw new InvalidOperationException(
                            "Could not decode contact-sheet input: " + sourcePath);
                    }
                    int targetY = (rowCount - input.row - 1) * ContactCellHeight;
                    for (int y = 0; y < ContactCellHeight; y++)
                    {
                        float v = (y + 0.5f) / ContactCellHeight;
                        for (int x = 0; x < ContactCellWidth; x++)
                        {
                            float u = (x + 0.5f) / ContactCellWidth;
                            int targetX = input.column * ContactCellWidth + x;
                            contactPixels[(targetY + y) * contact.width + targetX] =
                                source.GetPixelBilinear(u, v);
                        }
                    }
                }
                finally
                {
                    UnityEngine.Object.DestroyImmediate(source);
                }
            }

            contact.SetPixels32(contactPixels);
            contact.Apply(false, false);
            string outputName = "contact-sheet-8x6.png";
            File.WriteAllBytes(
                Path.Combine(outputRoot, outputName),
                contact.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(contact);
            return new ContactSheetManifest
            {
                rows = rowCount,
                columns = columns,
                cellWidth = ContactCellWidth,
                cellHeight = ContactCellHeight,
                output = outputName,
                inputs = inputs.ToArray()
            };
        }

        private static CaptureEnvironment CreateEnvironment()
        {
            var root = new GameObject("GachaBuild42ShippingCaptureEnvironment");
            var cameraObject = new GameObject("GachaBuild42ShippingCamera");
            cameraObject.transform.SetParent(root.transform, false);
            cameraObject.tag = "MainCamera";
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.aspect = FrameWidth / (float)FrameHeight;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.012f, 0.014f, 0.018f, 1f);
            camera.allowHDR = true;
            camera.allowMSAA = false;

            CreateDirectionalLight(
                root.transform,
                "GachaCaptureKey",
                new Color(0.84f, 0.89f, 1f),
                0.76f,
                Quaternion.Euler(36f, -32f, 0f));
            CreateDirectionalLight(
                root.transform,
                "GachaCaptureFill",
                new Color(1f, 0.62f, 0.38f),
                0.28f,
                Quaternion.Euler(54f, 142f, 0f));
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.08f, 0.085f, 0.095f);
            RenderSettings.fog = false;
            return new CaptureEnvironment { Root = root, Camera = camera };
        }

        private static void CreateDirectionalLight(
            Transform parent,
            string name,
            Color color,
            float intensity,
            Quaternion rotation)
        {
            var lightObject = new GameObject(name);
            lightObject.transform.SetParent(parent, false);
            lightObject.transform.rotation = rotation;
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = color;
            light.intensity = intensity;
            light.shadows = LightShadows.Soft;
        }

        private static ViewportEvidence MeasureViewport(
            Camera camera,
            Transform root)
        {
            bool measured = PremiumDisplayCaseCameraRules.TryMeasureCaseViewport(
                camera,
                root,
                out Rect viewport,
                out float nearestDepth);
            bool within = measured
                && nearestDepth > camera.nearClipPlane
                && viewport.xMin >= -PremiumDisplayCaseCameraRules
                    .MaximumCaseViewportOverflow
                && viewport.yMin >= -PremiumDisplayCaseCameraRules
                    .MaximumCaseViewportOverflow
                && viewport.xMax <= 1f + PremiumDisplayCaseCameraRules
                    .MaximumCaseViewportOverflow
                && viewport.yMax <= 1f + PremiumDisplayCaseCameraRules
                    .MaximumCaseViewportOverflow;
            return new ViewportEvidence
            {
                measurementMethod = "aggregate-renderer-world-aabb-diagnostic",
                measured = measured,
                xMin = viewport.xMin,
                yMin = viewport.yMin,
                xMax = viewport.xMax,
                yMax = viewport.yMax,
                nearestDepth = measured ? nearestDepth : 0f,
                withinShippingCropTolerance = within
            };
        }

        /// <summary>
        /// Measures the shipping render itself rather than enabled Renderer
        /// bounds. PremiumDisplayCase deliberately keeps acrylic renderers
        /// enabled while _RevealVisibility makes them transparent, and moves
        /// Layer_08_BoxLid outside the shot during the authored opening. Those
        /// objects must remain diagnosable, but they are not cropped visible
        /// content. Any actually rendered pixel inside the edge guard still
        /// fails closed, so genuine clipping cannot pass this gate.
        /// </summary>
        public static ViewportEvidence MeasureVisiblePixelViewport(
            Color32[] pixels,
            int width,
            int height,
            Color32 background,
            int edgeGuardPixels = VisiblePixelEdgeGuardPixels,
            int channelTolerance = VisiblePixelChannelTolerance)
        {
            int safeGuard = Mathf.Max(1, edgeGuardPixels);
            int safeTolerance = Mathf.Clamp(channelTolerance, 0, byte.MaxValue);
            var evidence = new ViewportEvidence
            {
                measurementMethod = "rendered-visible-pixels",
                edgeGuardPixels = safeGuard,
                backgroundRgba = string.Format(
                    CultureInfo.InvariantCulture,
                    "({0},{1},{2},{3})",
                    background.r,
                    background.g,
                    background.b,
                    background.a)
            };
            if (pixels == null
                || width <= 0
                || height <= 0
                || pixels.Length < width * height)
            {
                return evidence;
            }

            int minimumX = width;
            int minimumY = height;
            int maximumX = -1;
            int maximumY = -1;
            int foregroundCount = 0;
            int edgeContactCount = 0;
            for (int y = 0; y < height; y++)
            {
                int row = y * width;
                for (int x = 0; x < width; x++)
                {
                    if (!IsVisiblePixel(
                            pixels[row + x],
                            background,
                            safeTolerance))
                    {
                        continue;
                    }

                    foregroundCount++;
                    minimumX = Mathf.Min(minimumX, x);
                    minimumY = Mathf.Min(minimumY, y);
                    maximumX = Mathf.Max(maximumX, x);
                    maximumY = Mathf.Max(maximumY, y);
                    if (x < safeGuard
                        || x >= width - safeGuard
                        || y < safeGuard
                        || y >= height - safeGuard)
                    {
                        edgeContactCount++;
                    }
                }
            }

            evidence.foregroundPixelCount = foregroundCount;
            evidence.edgeContactPixelCount = edgeContactCount;
            if (foregroundCount <= 0)
            {
                return evidence;
            }

            evidence.measured = true;
            evidence.xMin = minimumX / (float)width;
            evidence.yMin = minimumY / (float)height;
            evidence.xMax = (maximumX + 1) / (float)width;
            evidence.yMax = (maximumY + 1) / (float)height;
            evidence.withinShippingCropTolerance = edgeContactCount == 0;
            return evidence;
        }

        public static int CountVisibleEdgeContactPixels(
            Color32[] pixels,
            int width,
            int height,
            Color32 background,
            int edgeGuardPixels = VisiblePixelEdgeGuardPixels,
            int channelTolerance = VisiblePixelChannelTolerance)
        {
            if (pixels == null
                || width <= 0
                || height <= 0
                || pixels.Length < width * height)
            {
                return 0;
            }

            int guard = Mathf.Clamp(
                edgeGuardPixels,
                1,
                Mathf.Max(1, Mathf.Min(width, height) / 2));
            int tolerance = Mathf.Clamp(channelTolerance, 0, byte.MaxValue);
            int count = 0;
            for (int y = 0; y < guard; y++)
            {
                count += CountVisibleRow(
                    pixels,
                    width,
                    y,
                    0,
                    width,
                    background,
                    tolerance);
            }
            for (int y = height - guard; y < height; y++)
            {
                count += CountVisibleRow(
                    pixels,
                    width,
                    y,
                    0,
                    width,
                    background,
                    tolerance);
            }
            for (int y = guard; y < height - guard; y++)
            {
                count += CountVisibleRow(
                    pixels,
                    width,
                    y,
                    0,
                    guard,
                    background,
                    tolerance);
                count += CountVisibleRow(
                    pixels,
                    width,
                    y,
                    width - guard,
                    width,
                    background,
                    tolerance);
            }
            return count;
        }

        private static int CountVisibleRow(
            Color32[] pixels,
            int width,
            int y,
            int startX,
            int endX,
            Color32 background,
            int tolerance)
        {
            int count = 0;
            int row = y * width;
            for (int x = startX; x < endX; x++)
            {
                if (IsVisiblePixel(pixels[row + x], background, tolerance))
                {
                    count++;
                }
            }
            return count;
        }

        private static bool IsVisiblePixel(
            Color32 pixel,
            Color32 background,
            int tolerance)
        {
            int difference = Mathf.Max(
                Mathf.Abs(pixel.r - background.r),
                Mathf.Max(
                    Mathf.Abs(pixel.g - background.g),
                    Mathf.Abs(pixel.b - background.b)));
            return difference > tolerance;
        }

        private static RendererViewportEvidence[] MeasureRendererDiagnostics(
            Camera camera,
            Transform root)
        {
            if (camera == null || root == null)
            {
                return Array.Empty<RendererViewportEvidence>();
            }

            return root.GetComponentsInChildren<Renderer>(false)
                .Where(renderer => renderer != null)
                .Select(renderer => MeasureRendererDiagnostic(
                    camera,
                    root,
                    renderer))
                .OrderByDescending(item => item.overflow)
                .ThenBy(item => item.path, StringComparer.Ordinal)
                .ToArray();
        }

        private static RendererViewportEvidence MeasureRendererDiagnostic(
            Camera camera,
            Transform root,
            Renderer renderer)
        {
            bool usesRevealVisibility = renderer.sharedMaterials.Any(material =>
                material != null && material.HasProperty(RevealVisibilityId));
            float materialRevealVisibility = usesRevealVisibility
                ? renderer.sharedMaterials
                    .First(material => material != null
                        && material.HasProperty(RevealVisibilityId))
                    .GetFloat(RevealVisibilityId)
                : 0f;
            float propertyBlockRevealVisibility = 0f;
            if (usesRevealVisibility)
            {
                var properties = new MaterialPropertyBlock();
                renderer.GetPropertyBlock(properties);
                propertyBlockRevealVisibility = properties.GetFloat(
                    RevealVisibilityId);
            }

            bool measured = TryProjectWorldBounds(
                camera,
                renderer.bounds,
                out Rect viewport,
                out float nearestDepth);
            float overflow = measured
                ? Mathf.Max(
                    0f,
                    Mathf.Max(
                        Mathf.Max(-viewport.xMin, viewport.xMax - 1f),
                        Mathf.Max(-viewport.yMin, viewport.yMax - 1f)))
                : -1f;
            return new RendererViewportEvidence
            {
                path = RelativePath(renderer.transform, root),
                rendererType = renderer.GetType().FullName,
                enabled = renderer.enabled,
                activeInHierarchy = renderer.gameObject.activeInHierarchy,
                transientBoxLid = IsTransientBoxLid(renderer.transform, root),
                usesRevealVisibility = usesRevealVisibility,
                materialRevealVisibility = materialRevealVisibility,
                propertyBlockRevealVisibility = propertyBlockRevealVisibility,
                measured = measured,
                xMin = viewport.xMin,
                yMin = viewport.yMin,
                xMax = viewport.xMax,
                yMax = viewport.yMax,
                nearestDepth = measured ? nearestDepth : 0f,
                overflow = overflow
            };
        }

        private static bool IsTransientBoxLid(Transform item, Transform root)
        {
            Transform cursor = item;
            while (cursor != null && cursor != root)
            {
                if (string.Equals(cursor.name, "BoxLidRoot",
                        StringComparison.Ordinal)
                    || string.Equals(cursor.name, "Layer_08_BoxLid",
                        StringComparison.Ordinal))
                {
                    return true;
                }
                cursor = cursor.parent;
            }
            return false;
        }

        private static bool TryProjectWorldBounds(
            Camera camera,
            Bounds bounds,
            out Rect viewport,
            out float nearestDepth)
        {
            viewport = default;
            nearestDepth = float.PositiveInfinity;
            if (camera == null || !IsFinite(bounds))
            {
                return false;
            }

            float minimumX = float.PositiveInfinity;
            float maximumX = float.NegativeInfinity;
            float minimumY = float.PositiveInfinity;
            float maximumY = float.NegativeInfinity;
            Vector3 extents = bounds.extents;
            for (int x = -1; x <= 1; x += 2)
            {
                for (int y = -1; y <= 1; y += 2)
                {
                    for (int z = -1; z <= 1; z += 2)
                    {
                        Vector3 corner = bounds.center + new Vector3(
                            extents.x * x,
                            extents.y * y,
                            extents.z * z);
                        Vector3 projected = camera.WorldToViewportPoint(corner);
                        if (!IsFinite(projected))
                        {
                            return false;
                        }
                        minimumX = Mathf.Min(minimumX, projected.x);
                        maximumX = Mathf.Max(maximumX, projected.x);
                        minimumY = Mathf.Min(minimumY, projected.y);
                        maximumY = Mathf.Max(maximumY, projected.y);
                        nearestDepth = Mathf.Min(nearestDepth, projected.z);
                    }
                }
            }

            viewport = Rect.MinMaxRect(
                minimumX,
                minimumY,
                maximumX,
                maximumY);
            return IsFinite(viewport.xMin)
                && IsFinite(viewport.yMin)
                && IsFinite(viewport.xMax)
                && IsFinite(viewport.yMax)
                && IsFinite(nearestDepth);
        }

        private static bool HasNoPhysics(GameObject root)
        {
            return root.GetComponentsInChildren<Rigidbody>(true).Length == 0
                && root.GetComponentsInChildren<Rigidbody2D>(true).Length == 0
                && root.GetComponentsInChildren<Collider>(true).Length == 0
                && root.GetComponentsInChildren<Collider2D>(true).Length == 0
                && root.GetComponentsInChildren<ArticulationBody>(true).Length == 0;
        }

        private static bool IsUniformFinitePositive(Vector3 value)
        {
            return IsFinite(value.x)
                && IsFinite(value.y)
                && IsFinite(value.z)
                && value.x > 0f
                && Mathf.Abs(value.x - value.y) < Epsilon
                && Mathf.Abs(value.x - value.z) < Epsilon;
        }

        private static bool IsFinite(float value)
        {
            return !float.IsNaN(value) && !float.IsInfinity(value);
        }

        private static bool IsFinite(Vector3 value)
        {
            return IsFinite(value.x) && IsFinite(value.y) && IsFinite(value.z);
        }

        private static bool IsFinite(Bounds value)
        {
            return IsFinite(value.center) && IsFinite(value.extents);
        }

        private static string CameraSignature(Camera camera)
        {
            return string.Join("|",
                Format(camera.transform.position),
                Format(camera.transform.rotation.eulerAngles),
                camera.fieldOfView.ToString("F6", CultureInfo.InvariantCulture),
                camera.aspect.ToString("F6", CultureInfo.InvariantCulture),
                camera.nearClipPlane.ToString("F6", CultureInfo.InvariantCulture),
                camera.farClipPlane.ToString("F6", CultureInfo.InvariantCulture));
        }

        private static string RelativePath(Transform item, Transform root)
        {
            var names = new Stack<string>();
            Transform cursor = item;
            while (cursor != null && cursor != root)
            {
                names.Push(cursor.name);
                cursor = cursor.parent;
            }
            return string.Join("/", names);
        }

        private static string StableSignature(IEnumerable<string> values)
        {
            unchecked
            {
                const ulong offset = 14695981039346656037UL;
                const ulong prime = 1099511628211UL;
                ulong hash = offset;
                string joined = string.Join("\n", values);
                for (int index = 0; index < joined.Length; index++)
                {
                    hash ^= joined[index];
                    hash *= prime;
                }
                return hash.ToString("x16", CultureInfo.InvariantCulture);
            }
        }

        private static string PhaseToken(GachaRevealPhase phase)
        {
            return char.ToLowerInvariant(phase.ToString()[0])
                + phase.ToString().Substring(1);
        }

        private static string Format(Vector3 value)
        {
            return string.Format(
                CultureInfo.InvariantCulture,
                "({0:F6},{1:F6},{2:F6})",
                value.x,
                value.y,
                value.z);
        }

        private static void WriteJson(string path, object value)
        {
            File.WriteAllText(path, JsonUtility.ToJson(value, true));
        }

        private sealed class FrameRecorder : IDisposable
        {
            private readonly Camera camera;
            private readonly RenderTexture target;
            private readonly Texture2D texture;
            private readonly RenderTexture previousTarget;
            private readonly RenderTexture previousActive;
            private readonly Color32 clearPixel;

            public FrameRecorder(Camera camera)
            {
                this.camera = camera;
                previousTarget = camera.targetTexture;
                previousActive = RenderTexture.active;
                target = new RenderTexture(
                    FrameWidth,
                    FrameHeight,
                    24,
                    RenderTextureFormat.ARGB32,
                    RenderTextureReadWrite.sRGB)
                {
                    antiAliasing = 1,
                    name = "GachaBuild42ShippingCaptureRT"
                };
                target.Create();
                texture = new Texture2D(
                    FrameWidth,
                    FrameHeight,
                    TextureFormat.RGBA32,
                    false,
                    false);
                camera.targetTexture = target;
                RenderTexture.active = target;
                clearPixel = CaptureClearPixel();
            }

            public Camera Camera => camera;

            public CapturedImage Render(
                bool measureVisiblePixels = false,
                bool measureEdgeContact = false)
            {
                camera.Render();
                RenderTexture.active = target;
                texture.ReadPixels(
                    new Rect(0, 0, FrameWidth, FrameHeight),
                    0,
                    0);
                texture.Apply(false, false);
                Color32[] pixels = texture.GetPixels32();
                float minimum = 1f;
                float maximum = 0f;
                for (int index = 0; index < pixels.Length; index += 64)
                {
                    Color32 pixel = pixels[index];
                    float luminance = (0.2126f * pixel.r
                            + 0.7152f * pixel.g
                            + 0.0722f * pixel.b)
                        / 255f;
                    minimum = Mathf.Min(minimum, luminance);
                    maximum = Mathf.Max(maximum, luminance);
                }
                ViewportEvidence visibleViewport = measureVisiblePixels
                    ? MeasureVisiblePixelViewport(
                        pixels,
                        FrameWidth,
                        FrameHeight,
                        clearPixel)
                    : null;
                return new CapturedImage
                {
                    Png = texture.EncodeToPNG(),
                    LuminanceRange = maximum - minimum,
                    VisiblePixelViewport = visibleViewport,
                    EdgeContactPixelCount = visibleViewport != null
                        ? visibleViewport.edgeContactPixelCount
                        : measureEdgeContact
                            ? CountVisibleEdgeContactPixels(
                            pixels,
                            FrameWidth,
                            FrameHeight,
                            clearPixel)
                            : 0
                };
            }

            private Color32 CaptureClearPixel()
            {
                int previousCullingMask = camera.cullingMask;
                var sample = new Texture2D(
                    1,
                    1,
                    TextureFormat.RGBA32,
                    false,
                    false);
                try
                {
                    camera.cullingMask = 0;
                    camera.Render();
                    RenderTexture.active = target;
                    sample.ReadPixels(new Rect(0, 0, 1, 1), 0, 0);
                    sample.Apply(false, false);
                    return sample.GetPixels32()[0];
                }
                finally
                {
                    camera.cullingMask = previousCullingMask;
                    UnityEngine.Object.DestroyImmediate(sample);
                }
            }

            public void Dispose()
            {
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                target.Release();
                UnityEngine.Object.DestroyImmediate(texture);
                UnityEngine.Object.DestroyImmediate(target);
            }
        }
    }
}
