using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using UnityEngine;
using UnityEngine.Playables;

#if UNITY_EDITOR
using UnityEditor;
#endif

namespace FidgetingApp.DisplayCase.Candidates
{
    [DisallowMultipleComponent]
    public sealed class PackOpeningGate04R011Capture : MonoBehaviour
    {
        public const int Width = 1206;
        public const int Height = 2622;
        public const int FrameRate = 60;
        public const int FrameCount = 207;
        public const int SlowMotionScale = 4;

        private static readonly SourceMatch[] SourceMatches =
        {
            new SourceMatch(5.80f, "source-05.800s.png"),
            new SourceMatch(5.95f, "source-05.950s.png"),
            new SourceMatch(6.15f, "source-06.150s.png"),
            new SourceMatch(6.45f, "source-06.450s.png"),
            new SourceMatch(6.74f, "source-06.740s.png"),
            new SourceMatch(7.00f, "source-07.000s.png")
        };

        [SerializeField] private Camera captureCamera;
        [SerializeField] private PackOpeningGate04R011Controller controller;
        [SerializeField] private PlayableDirector director;
        [SerializeField] private string outputDirectory = "";
        [SerializeField] private string sourceCaptureDirectory = "";
        [SerializeField] private string scenePath =
            "Assets/_DisplayCase/Candidates/PackOpeningGate04R011/Scenes/PackOpeningGate04R011.unity";

        private readonly List<FrameMetric> metrics =
            new List<FrameMetric>(FrameCount);
        private RenderTexture renderTarget;
        private Texture2D readback;
        private bool reboundRestoredExactly;

        public void Configure(
            Camera camera,
            PackOpeningGate04R011Controller sequenceController,
            PlayableDirector timelineDirector,
            string output,
            string authoredScenePath,
            string sourceCaptures)
        {
            captureCamera = camera;
            controller = sequenceController;
            director = timelineDirector;
            outputDirectory = output;
            scenePath = authoredScenePath;
            sourceCaptureDirectory = sourceCaptures;
        }

        private void Start()
        {
            if (
                captureCamera == null
                || controller == null
                || director == null
                || string.IsNullOrWhiteSpace(outputDirectory)
                || string.IsNullOrWhiteSpace(sourceCaptureDirectory)
            )
            {
                ExitWithFailure("Capture scene configuration is incomplete.");
                return;
            }
            if (!controller.HasRequiredBindings)
            {
                ExitWithFailure("Rev 11 sequence bindings are incomplete.");
                return;
            }
            Directory.CreateDirectory(outputDirectory);
            Directory.CreateDirectory(Path.Combine(outputDirectory, "frames"));
            ConfigureCapture();
            StartCoroutine(CaptureSequence());
        }

        private void OnDestroy()
        {
            if (captureCamera != null)
            {
                captureCamera.targetTexture = null;
            }
            if (readback != null)
            {
                Destroy(readback);
            }
            if (renderTarget != null)
            {
                renderTarget.Release();
                Destroy(renderTarget);
            }
        }

        private void ConfigureCapture()
        {
            Time.captureFramerate = FrameRate;
            QualitySettings.vSyncCount = 0;
            Application.targetFrameRate = FrameRate;
            captureCamera.aspect = Width / (float)Height;
            renderTarget = new RenderTexture(
                Width,
                Height,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB)
            {
                name = "Gate04R011RealUnityShippingPortraitCapture",
                antiAliasing = 1,
                useMipMap = false,
                autoGenerateMips = false
            };
            renderTarget.Create();
            readback = new Texture2D(
                Width,
                Height,
                TextureFormat.RGB24,
                false,
                false);
            captureCamera.targetTexture = renderTarget;
        }

        private IEnumerator CaptureSequence()
        {
            yield return null;
            Evaluate(0.76f, false);
            reboundRestoredExactly = controller.ReboundToSealed();
            Evaluate(0f, false);
            yield return null;

            for (int frame = 0; frame < FrameCount; frame++)
            {
                float time = frame / (float)FrameRate;
                Evaluate(time, false);
                yield return null;
                string path = FramePath(frame);
                metrics.Add(CaptureFrame(path, frame, time));
            }

            yield return CaptureSlowMotionPass(
                "frames-tear-quarter",
                0.80f,
                1.62f,
                new Vector3(0f, 0.030f, 0.235f),
                0.60f);
            yield return CaptureSlowMotionPass(
                "frames-impact-quarter",
                1.56f,
                2.34f,
                Vector3.zero,
                1f);

            BuildContactSheet(
                "tear-contact-sheet.png",
                new[] { 33, 51, 54, 60, 72, 84, 95, 102 });
            BuildContactSheet(
                "source-impact-contact-sheet.png",
                new[] { 94, 96, 99, 102, 105, 112, 120, 132 });
            BuildContactSheet(
                "continuity-contact-sheet.png",
                new[] { 96, 102, 112, 126, 140, 151, 168, 186 });
            bool technicalDiagnosticsBuilt = BuildTechnicalDiagnosticsSheet(
                new[] { 96, 102, 112, 126, 140, 151, 168, 186 });
            bool sourceComparisonBuilt = BuildSourceComparison();
            bool passed = WriteCaptureReport(
                sourceComparisonBuilt,
                technicalDiagnosticsBuilt);
            Debug.Log(
                passed
                    ? "GATE04_R011_CC0_REUSE_CAPTURE_COMPLETE"
                    : "GATE04_R011_CC0_REUSE_CAPTURE_SELF_REJECTED");
            Exit(passed ? 0 : 2);
        }

        /// Writes a 0.25x pass over one window. Playback stays 60 fps, so a
        /// window of N seconds produces N * 4 * 60 real rendered frames rather
        /// than resampling the normal-speed pass.
        private IEnumerator CaptureSlowMotionPass(
            string folder,
            float startSeconds,
            float endSeconds,
            Vector3 framingOffset,
            float fieldOfViewScale)
        {
            string directory = Path.Combine(outputDirectory, folder);
            Directory.CreateDirectory(directory);
            if (framingOffset != Vector3.zero || fieldOfViewScale != 1f)
            {
                controller.ApplyCaptureFraming(framingOffset, fieldOfViewScale);
            }

            int frames = Mathf.RoundToInt(
                (endSeconds - startSeconds) * SlowMotionScale * FrameRate);
            for (int frame = 0; frame < frames; frame++)
            {
                float time =
                    startSeconds
                    + frame / (float)(SlowMotionScale * FrameRate);
                Evaluate(time, false);
                yield return null;
                RenderTexture previous = RenderTexture.active;
                try
                {
                    RenderTexture.active = renderTarget;
                    captureCamera.Render();
                    readback.ReadPixels(
                        new Rect(0, 0, Width, Height),
                        0,
                        0,
                        false);
                    readback.Apply(false, false);
                    File.WriteAllBytes(
                        Path.Combine(
                            directory,
                            $"frame-{frame:D4}.png"),
                        readback.EncodeToPNG());
                }
                finally
                {
                    RenderTexture.active = previous;
                }
            }

            controller.ResetCaptureFraming();
            Debug.Log(
                $"GATE04_R011_SLOWMO_PASS {folder} frames={frames} "
                + $"window={startSeconds:F2}-{endSeconds:F2}s "
                + $"scale=1/{SlowMotionScale}");
        }

        private void Evaluate(float time, bool reduceMotion)
        {
            director.time = Mathf.Clamp(
                time,
                0f,
                PackOpeningGate04R011Profile.TotalSeconds);
            director.Evaluate();
            controller.SetTime(time, reduceMotion);
        }

        private FrameMetric CaptureFrame(
            string path,
            int frame,
            float time)
        {
            RenderTexture previous = RenderTexture.active;
            try
            {
                RenderTexture.active = renderTarget;
                captureCamera.Render();
                readback.ReadPixels(
                    new Rect(0, 0, Width, Height),
                    0,
                    0,
                    false);
                readback.Apply(false, false);
                Color32[] pixels = readback.GetPixels32();
                File.WriteAllBytes(path, readback.EncodeToPNG());
                controller.TryGetCaseViewportBounds(out Rect caseBounds);
                controller.TryGetPackViewportBounds(out Rect packBounds);
                return FrameMetric.Measure(
                    frame,
                    time,
                    controller,
                    caseBounds,
                    packBounds,
                    pixels);
            }
            finally
            {
                RenderTexture.active = previous;
            }
        }

        private bool WriteCaptureReport(
            bool sourceComparisonBuilt,
            bool technicalDiagnosticsBuilt)
        {
            EntityId expectedRootId = controller.CaseRootEntityId;
            EntityId[] expectedRendererIds = controller.CaseRendererEntityIds
                .ToArray();
            float maximumProjectedCenterStep = 0f;
            float maximumProjectedHeightStep = 0f;
            float maximumRootPositionStep = 0f;
            for (int index = 1; index < metrics.Count; index++)
            {
                FrameMetric previous = metrics[index - 1];
                FrameMetric current = metrics[index];
                maximumProjectedCenterStep = Mathf.Max(
                    maximumProjectedCenterStep,
                    Vector2.Distance(
                        previous.caseBounds.center,
                        current.caseBounds.center));
                maximumProjectedHeightStep = Mathf.Max(
                    maximumProjectedHeightStep,
                    Mathf.Abs(current.caseBounds.height - previous.caseBounds.height));
                maximumRootPositionStep = Mathf.Max(
                    maximumRootPositionStep,
                    Vector3.Distance(
                        previous.caseRootPosition,
                        current.caseRootPosition));
            }

            bool caseIdentityStable = metrics.All(value =>
                value.caseRootId.Equals(expectedRootId)
                && value.caseRendererIds.SequenceEqual(expectedRendererIds));
            bool caseScaleStable = metrics.All(value =>
                Vector3.Distance(
                    value.caseRootScale,
                    controller.CaseAuthoredScale) < 0.000001f);
            bool sameCaseVisibleThroughAperture = metrics.Any(value =>
                value.occlusion == PackOpeningGate04R011Occlusion
                    .AperturePartial.ToString()
                && value.tearProgress >= 0.30f
                && value.caseBounds.height > 0.20f);
            bool sameCaseCrossesOccluder = metrics.Any(value =>
                value.occlusion == PackOpeningGate04R011Occlusion
                    .CrossingOccluder.ToString()
                && value.packVisible
                && value.caseBounds.height > 0.20f);
            bool packGoneAfterHandoff = metrics
                .Where(value =>
                    value.timeSeconds
                    >= PackOpeningGate04R011Profile.TargetProxyResultOff + 0.02f)
                .All(value => !value.packVisible);
            bool noEarlyRarity = metrics
                .Where(value =>
                    value.timeSeconds
                    < PackOpeningGate04R011Profile.TargetRealResultStart)
                .All(value => value.rarityReveal <= 0.00001f);
            bool sourceCountsExact = controller.SourceEffectSystems
                .Select(value => value.main.maxParticles)
                .SequenceEqual(new[] { 3, 25, 512, 512, 16 });
            bool sourceEffectVisible = metrics
                .Where(value => value.timeSeconds >= 1.60f
                    && value.timeSeconds <= 2.45f)
                .Max(value => value.sourceParticleCount) >= 512;
            float maximumWhiteFraction = metrics.Max(value => value.whiteFraction);
            float minimumVisibleFraction = metrics.Min(value => value.visibleFraction);
            float maximumAheadSeparation = metrics.Max(
                value => value.maximumAheadSeparation);
            FrameMetric settled = metrics[metrics.Count - 1];
            Transform[] transforms = controller.gameObject.scene
                .GetRootGameObjects()
                .SelectMany(root =>
                    root.GetComponentsInChildren<Transform>(true))
                .ToArray();
            bool noPlaceholderLanguage = transforms.All(value =>
                !value.name.Contains(
                    "EnergyRing",
                    StringComparison.OrdinalIgnoreCase)
                && !value.name.Contains("Concentric", StringComparison.OrdinalIgnoreCase)
                && !value.name.Contains("PurpleWash", StringComparison.OrdinalIgnoreCase)
                && !value.name.Contains("Opening_Booster", StringComparison.Ordinal)
                && !value.name.Contains("Card_v", StringComparison.Ordinal));
            PackOpeningGate04R011Sample reduced =
                controller.Profile.Evaluate(1.93f, true);
            bool reduceMotionCausal =
                reduced.Occlusion
                    == PackOpeningGate04R011Occlusion.CrossingOccluder
                && !reduced.ActivationEnabled
                && !reduced.LightningEnabled
                && !reduced.ExplosionEnabled
                && reduced.CameraKick == Vector2.zero
                && reduced.CameraPush == 0f;
            var checks = new Dictionary<string, bool>
            {
                { "realUnityPlayModeCapture", Application.isPlaying },
                { "unityVersionExact", Application.unityVersion == "6000.5.6f1" },
                { "shippingPortrait1206x2622", Width == 1206 && Height == 2622 },
                { "exact60Fps", FrameRate == 60 },
                { "sourceComparisonBuilt", sourceComparisonBuilt },
                { "technicalDiagnosticsBuilt", technicalDiagnosticsBuilt },
                { "sameCaseIdentityEveryFrame", caseIdentityStable },
                { "sameCaseScaleEveryFrame", caseScaleStable },
                { "sameCaseVisibleThroughAperture", sameCaseVisibleThroughAperture },
                { "sameCaseCrossesPhysicalPack", sameCaseCrossesOccluder },
                { "packGoneAfterSourceMappedHandoff", packGoneAfterHandoff },
                { "caseProjectedCenterContinuous", maximumProjectedCenterStep < 0.060f },
                { "caseProjectedScaleContinuous", maximumProjectedHeightStep < 0.065f },
                { "caseRootPositionContinuous", maximumRootPositionStep < 0.045f },
                { "sourceShurikenCapacitiesExact", sourceCountsExact },
                { "sourceEffectParticlesVisible", sourceEffectVisible },
                { "sourceDiscardCurveDrivesPack",
                    metrics.Any(value => value.packDissolve > 0.20f
                        && value.packDissolve < 0.95f) },
                { "noReceiptRarityLeak", noEarlyRarity },
                { "noBlankWhiteFrame", maximumWhiteFraction < 0.58f },
                { "noBlackFrame", minimumVisibleFraction > 0.10f },
                { "aheadOfTearFrontRemainsWelded",
                    maximumAheadSeparation < 0.000001f },
                { "settledCaseReadable",
                    settled.caseBounds.height >= 0.48f
                    && settled.caseBounds.height <= 0.62f },
                { "noPlaceholderRingWashOrSampleEntity", noPlaceholderLanguage },
                { "belowThresholdReboundExact", reboundRestoredExactly },
                { "reduceMotionPreservesCausality", reduceMotionCausal },
                { "shippingReadyFalse", true },
                { "physicalPhoneInstalledFalse", true }
            };
            bool passed = checks.All(pair => pair.Value);

            var json = new StringBuilder(1024 * 512);
            json.AppendLine("{");
            json.AppendLine("  \"schema\": \"premium-display-case-gate04-r011-unity-capture.v1\",");
            json.AppendLine($"  \"status\": \"{(passed ? "pass" : "self-rejected")}\",");
            json.AppendLine("  \"source\": \"actual running Unity PlayMode scene and Camera output\",");
            json.AppendLine($"  \"scene\": \"{Escape(scenePath)}\",");
            json.AppendLine($"  \"width\": {Width},");
            json.AppendLine($"  \"height\": {Height},");
            json.AppendLine($"  \"fps\": {FrameRate},");
            json.AppendLine($"  \"frames\": {FrameCount},");
            json.AppendLine("  \"durationSeconds\": 3.45,");
            json.AppendLine("  \"normalSpeedFrames\": \"frames/frame-%04d.png\",");
            json.AppendLine($"  \"slowMotionScale\": \"1/{SlowMotionScale}\",");
            json.AppendLine("  \"tearQuarterSpeedFrames\": \"frames-tear-quarter/frame-%04d.png\",");
            json.AppendLine("  \"impactQuarterSpeedFrames\": \"frames-impact-quarter/frame-%04d.png\",");
            json.AppendLine("  \"sourceComparison\": \"source-target-side-by-side.png\",");
            json.AppendLine("  \"tearContactSheet\": \"tear-contact-sheet.png\",");
            json.AppendLine("  \"impactContactSheet\": \"source-impact-contact-sheet.png\",");
            json.AppendLine("  \"continuityContactSheet\": \"continuity-contact-sheet.png\",");
            json.AppendLine("  \"technicalDiagnosticsSheet\": \"technical-continuity-sheet.svg\",");
            json.AppendLine($"  \"maximumWhiteFraction\": {Format(maximumWhiteFraction)},");
            json.AppendLine($"  \"minimumVisibleFraction\": {Format(minimumVisibleFraction)},");
            json.AppendLine($"  \"maximumProjectedCenterStep\": {Format(maximumProjectedCenterStep)},");
            json.AppendLine($"  \"maximumProjectedHeightStep\": {Format(maximumProjectedHeightStep)},");
            json.AppendLine($"  \"maximumRootPositionStepMeters\": {Format(maximumRootPositionStep)},");
            json.AppendLine($"  \"maximumAheadSeparationMeters\": {Format(maximumAheadSeparation)},");
            json.AppendLine("  \"candidateOnly\": true,");
            json.AppendLine("  \"shippingRuntimeWired\": false,");
            json.AppendLine("  \"shippingReady\": false,");
            json.AppendLine("  \"physicalPhoneInstalled\": false,");
            json.AppendLine("  \"checks\": {");
            json.AppendLine(string.Join(
                ",\n",
                checks.Select(pair =>
                    $"    \"{pair.Key}\": {pair.Value.ToString().ToLowerInvariant()}")));
            json.AppendLine("  },");
            json.AppendLine("  \"frameMetrics\": [");
            json.AppendLine(string.Join(
                ",\n",
                metrics.Select(value => value.ToJson())));
            json.AppendLine("  ]");
            json.AppendLine("}");
            File.WriteAllText(
                Path.Combine(outputDirectory, "unity-capture-report.json"),
                json.ToString());
            return passed;
        }

        private void BuildContactSheet(string name, IReadOnlyList<int> frames)
        {
            const int columns = 4;
            const int cellWidth = 603;
            const int cellHeight = 1311;
            int rows = Mathf.CeilToInt(frames.Count / (float)columns);
            var sheet = new Texture2D(
                columns * cellWidth,
                rows * cellHeight,
                TextureFormat.RGB24,
                false);
            Color32[] pixels = Enumerable
                .Repeat(new Color32(4, 5, 7, 255), sheet.width * sheet.height)
                .ToArray();
            for (int index = 0; index < frames.Count; index++)
            {
                using LoadedTexture loaded = LoadedTexture.Open(
                    FramePath(frames[index]));
                BlitFit(
                    loaded.Texture,
                    pixels,
                    sheet.width,
                    index % columns * cellWidth,
                    (rows - 1 - index / columns) * cellHeight,
                    cellWidth,
                    cellHeight);
            }
            sheet.SetPixels32(pixels);
            sheet.Apply(false, false);
            File.WriteAllBytes(
                Path.Combine(outputDirectory, name),
                sheet.EncodeToPNG());
            Destroy(sheet);
        }

        private bool BuildTechnicalDiagnosticsSheet(
            IReadOnlyList<int> frames)
        {
            try
            {
                const int columns = 4;
                const float cellWidth = 301.5f;
                const float frameHeight = 655.5f;
                const float detailHeight = 96f;
                int rows = Mathf.CeilToInt(frames.Count / (float)columns);
                var svg = new StringBuilder(16384);
                svg.AppendLine(
                    $"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{Format(columns * cellWidth)}\" height=\"{Format(rows * (frameHeight + detailHeight))}\" viewBox=\"0 0 {Format(columns * cellWidth)} {Format(rows * (frameHeight + detailHeight))}\">");
                svg.AppendLine("<rect width=\"100%\" height=\"100%\" fill=\"#040507\"/>");
                for (int index = 0; index < frames.Count; index++)
                {
                    FrameMetric metric = metrics.Single(
                        value => value.frame == frames[index]);
                    int column = index % columns;
                    int row = index / columns;
                    float x = column * cellWidth;
                    float y = row * (frameHeight + detailHeight);
                    float boxX = x + metric.caseBounds.x * cellWidth;
                    float boxY = y + (1f - metric.caseBounds.y
                        - metric.caseBounds.height) * frameHeight;
                    float boxWidth = metric.caseBounds.width * cellWidth;
                    float boxHeight = metric.caseBounds.height * frameHeight;
                    svg.AppendLine(
                        $"<image href=\"frames/frame-{metric.frame:D4}.png\" x=\"{Format(x)}\" y=\"{Format(y)}\" width=\"{Format(cellWidth)}\" height=\"{Format(frameHeight)}\" preserveAspectRatio=\"xMidYMid meet\"/>");
                    svg.AppendLine(
                        $"<rect x=\"{Format(boxX)}\" y=\"{Format(boxY)}\" width=\"{Format(boxWidth)}\" height=\"{Format(boxHeight)}\" fill=\"none\" stroke=\"#f0df9c\" stroke-width=\"2\"/>");
                    svg.AppendLine(
                        $"<rect x=\"{Format(x)}\" y=\"{Format(y + frameHeight)}\" width=\"{Format(cellWidth)}\" height=\"{Format(detailHeight)}\" fill=\"#101216\"/>");
                    svg.AppendLine(
                        $"<text x=\"{Format(x + 10f)}\" y=\"{Format(y + frameHeight + 20f)}\" fill=\"#f3f0e8\" font-family=\"monospace\" font-size=\"11\">frame {metric.frame:D4} · {EscapeXml(metric.occlusion)}</text>");
                    svg.AppendLine(
                        $"<text x=\"{Format(x + 10f)}\" y=\"{Format(y + frameHeight + 38f)}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"10\">case {EscapeXml(metric.caseRootId.ToString())}</text>");
                    svg.AppendLine(
                        $"<text x=\"{Format(x + 10f)}\" y=\"{Format(y + frameHeight + 56f)}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"10\">bounds {Format(metric.caseBounds.x)},{Format(metric.caseBounds.y)} {Format(metric.caseBounds.width)}×{Format(metric.caseBounds.height)}</text>");
                    svg.AppendLine(
                        $"<text x=\"{Format(x + 10f)}\" y=\"{Format(y + frameHeight + 74f)}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"10\">tear {Format(metric.tearProgress)} · dissolve {Format(metric.packDissolve)}</text>");
                }
                svg.AppendLine("</svg>");
                File.WriteAllText(
                    Path.Combine(outputDirectory, "technical-continuity-sheet.svg"),
                    svg.ToString());
                return true;
            }
            catch (Exception exception)
            {
                Debug.LogWarning(
                    $"Could not write technical diagnostics: {exception.Message}");
                return false;
            }
        }

        private bool BuildSourceComparison()
        {
            const int rowWidth = 1206;
            const int rowHeight = 520;
            var sheet = new Texture2D(
                rowWidth,
                rowHeight * SourceMatches.Length,
                TextureFormat.RGB24,
                false);
            Color32[] pixels = Enumerable
                .Repeat(
                    new Color32(4, 5, 7, 255),
                    sheet.width * sheet.height)
                .ToArray();
            var manifest = new StringBuilder(4096);
            manifest.AppendLine("{");
            manifest.AppendLine("  \"schema\": \"make-it-shine-matched-timestamps.v1\",");
            manifest.AppendLine("  \"pairs\": [");
            for (int index = 0; index < SourceMatches.Length; index++)
            {
                SourceMatch match = SourceMatches[index];
                string sourcePath = Path.Combine(
                    sourceCaptureDirectory,
                    match.FileName);
                if (!File.Exists(sourcePath))
                {
                    Destroy(sheet);
                    return false;
                }
                float targetTime =
                    match.SourceTime - PackOpeningGate04R011Profile.SourceTimeOffset;
                int targetFrame = Mathf.Clamp(
                    Mathf.RoundToInt(targetTime * FrameRate),
                    0,
                    FrameCount - 1);
                int y = (SourceMatches.Length - 1 - index) * rowHeight;
                using (LoadedTexture source = LoadedTexture.Open(sourcePath))
                {
                    BlitFit(
                        source.Texture,
                        pixels,
                        sheet.width,
                        0,
                        y,
                        760,
                        rowHeight);
                }
                using (LoadedTexture target = LoadedTexture.Open(
                    FramePath(targetFrame)))
                {
                    BlitFit(
                        target.Texture,
                        pixels,
                        sheet.width,
                        786,
                        y,
                        420,
                        rowHeight);
                }
                manifest.AppendLine("    {");
                manifest.AppendLine(
                    $"      \"sourceTimeSeconds\": {Format(match.SourceTime)},");
                manifest.AppendLine(
                    $"      \"sourceFrame\": \"{match.FileName}\",");
                manifest.AppendLine(
                    $"      \"targetTimeSeconds\": {Format(targetTime)},");
                manifest.AppendLine(
                    $"      \"targetFrame\": {targetFrame}");
                manifest.AppendLine(
                    index == SourceMatches.Length - 1 ? "    }" : "    },");
            }
            manifest.AppendLine("  ]");
            manifest.AppendLine("}");
            sheet.SetPixels32(pixels);
            sheet.Apply(false, false);
            File.WriteAllBytes(
                Path.Combine(outputDirectory, "source-target-side-by-side.png"),
                sheet.EncodeToPNG());
            File.WriteAllText(
                Path.Combine(outputDirectory, "matched-timestamps.json"),
                manifest.ToString());
            Destroy(sheet);
            return true;
        }

        private static void BlitFit(
            Texture2D source,
            Color32[] destination,
            int destinationWidth,
            int x,
            int y,
            int width,
            int height)
        {
            float scale = Mathf.Min(
                width / (float)source.width,
                height / (float)source.height);
            int drawWidth = Mathf.Max(1, Mathf.RoundToInt(source.width * scale));
            int drawHeight = Mathf.Max(1, Mathf.RoundToInt(source.height * scale));
            int offsetX = x + (width - drawWidth) / 2;
            int offsetY = y + (height - drawHeight) / 2;
            Color32[] sourcePixels = source.GetPixels32();
            for (int targetY = 0; targetY < drawHeight; targetY++)
            {
                int sourceY = Mathf.Min(
                    source.height - 1,
                    targetY * source.height / drawHeight);
                for (int targetX = 0; targetX < drawWidth; targetX++)
                {
                    int sourceX = Mathf.Min(
                        source.width - 1,
                        targetX * source.width / drawWidth);
                    destination[
                        (offsetY + targetY) * destinationWidth
                        + offsetX
                        + targetX] =
                        sourcePixels[sourceY * source.width + sourceX];
                }
            }
        }

        private string FramePath(int frame)
        {
            return Path.Combine(
                outputDirectory,
                "frames",
                $"frame-{frame:D4}.png");
        }

        private static string Format(float value)
        {
            return value.ToString("0.000000", CultureInfo.InvariantCulture);
        }

        private static string Escape(string value)
        {
            return (value ?? string.Empty)
                .Replace("\\", "\\\\")
                .Replace("\"", "\\\"");
        }

        private static string EscapeXml(string value)
        {
            return (value ?? string.Empty)
                .Replace("&", "&amp;")
                .Replace("<", "&lt;")
                .Replace(">", "&gt;")
                .Replace("\"", "&quot;");
        }

        private void ExitWithFailure(string message)
        {
            Debug.LogError(message);
            Exit(1);
        }

        private static void Exit(int code)
        {
#if UNITY_EDITOR
            EditorApplication.Exit(code);
#else
            Application.Quit(code);
#endif
        }

        private readonly struct SourceMatch
        {
            public SourceMatch(float sourceTime, string fileName)
            {
                SourceTime = sourceTime;
                FileName = fileName;
            }

            public float SourceTime { get; }
            public string FileName { get; }
        }

        private readonly struct LoadedTexture : IDisposable
        {
            private LoadedTexture(Texture2D texture)
            {
                Texture = texture;
            }

            public Texture2D Texture { get; }

            public static LoadedTexture Open(string path)
            {
                var texture = new Texture2D(2, 2, TextureFormat.RGBA32, false);
                if (!texture.LoadImage(File.ReadAllBytes(path), false))
                {
                    DestroyImmediate(texture);
                    throw new InvalidDataException($"Could not load {path}");
                }
                return new LoadedTexture(texture);
            }

            public void Dispose()
            {
                if (Texture != null)
                {
                    DestroyImmediate(Texture);
                }
            }
        }

        [Serializable]
        private readonly struct FrameMetric
        {
            private FrameMetric(
                int frame,
                float time,
                PackOpeningGate04R011Controller source,
                Rect caseBounds,
                Rect packBounds,
                float visibleFraction,
                float whiteFraction)
            {
                this.frame = frame;
                timeSeconds = time;
                phase = source.CurrentSample.Phase.ToString();
                occlusion = source.CurrentSample.Occlusion.ToString();
                sourceTimeSeconds = source.CurrentSample.SourceTimeSeconds;
                tearProgress = source.CurrentSample.TearProgress;
                packRetreat = source.CurrentSample.PackRetreat;
                packDissolve = source.CurrentSample.PackDissolve;
                caseTravel = source.CurrentSample.CaseTravel;
                rarityReveal = source.CurrentSample.RarityReveal;
                sourceParticleCount = source.SourceEffectSystems.Sum(
                    value => value.particleCount);
                maximumAheadSeparation = source.MaximumAheadOfFrontSeparation;
                caseRootId = source.CaseRootEntityId;
                caseRendererIds = source.CaseRendererEntityIds.ToArray();
                caseRootPosition = source.CaseMotionRoot.localPosition;
                caseRootScale = source.CaseMotionRoot.localScale;
                this.caseBounds = caseBounds;
                this.packBounds = packBounds;
                packVisible = source.PackVisible;
                this.visibleFraction = visibleFraction;
                this.whiteFraction = whiteFraction;
            }

            public readonly int frame;
            public readonly float timeSeconds;
            public readonly string phase;
            public readonly string occlusion;
            public readonly float sourceTimeSeconds;
            public readonly float tearProgress;
            public readonly float packRetreat;
            public readonly float packDissolve;
            public readonly float caseTravel;
            public readonly float rarityReveal;
            public readonly int sourceParticleCount;
            public readonly float maximumAheadSeparation;
            public readonly EntityId caseRootId;
            public readonly EntityId[] caseRendererIds;
            public readonly Vector3 caseRootPosition;
            public readonly Vector3 caseRootScale;
            public readonly Rect caseBounds;
            public readonly Rect packBounds;
            public readonly bool packVisible;
            public readonly float visibleFraction;
            public readonly float whiteFraction;

            public static FrameMetric Measure(
                int frame,
                float time,
                PackOpeningGate04R011Controller source,
                Rect caseBounds,
                Rect packBounds,
                IReadOnlyList<Color32> pixels)
            {
                int sampled = 0;
                int visible = 0;
                int white = 0;
                const int stride = 8;
                for (int y = 0; y < Height; y += stride)
                {
                    for (int x = 0; x < Width; x += stride)
                    {
                        Color32 pixel = pixels[y * Width + x];
                        float r = pixel.r / 255f;
                        float g = pixel.g / 255f;
                        float b = pixel.b / 255f;
                        float luma =
                            r * 0.2126f + g * 0.7152f + b * 0.0722f;
                        sampled += 1;
                        if (luma > 0.018f) visible += 1;
                        if (r > 0.94f && g > 0.94f && b > 0.90f) white += 1;
                    }
                }
                return new FrameMetric(
                    frame,
                    time,
                    source,
                    caseBounds,
                    packBounds,
                    visible / (float)Mathf.Max(1, sampled),
                    white / (float)Mathf.Max(1, sampled));
            }

            public string ToJson()
            {
                return
                    "    {"
                    + $"\"frame\":{frame},"
                    + $"\"timeSeconds\":{Format(timeSeconds)},"
                    + $"\"sourceTimeSeconds\":{Format(sourceTimeSeconds)},"
                    + $"\"phase\":\"{phase}\","
                    + $"\"occlusion\":\"{occlusion}\","
                    + $"\"tearProgress\":{Format(tearProgress)},"
                    + $"\"packRetreat\":{Format(packRetreat)},"
                    + $"\"packDissolve\":{Format(packDissolve)},"
                    + $"\"caseTravel\":{Format(caseTravel)},"
                    + $"\"rarityReveal\":{Format(rarityReveal)},"
                    + $"\"sourceParticleCount\":{sourceParticleCount},"
                    + $"\"maximumAheadSeparation\":{Format(maximumAheadSeparation)},"
                    + $"\"caseRootId\":\"{Escape(caseRootId.ToString())}\","
                    + "\"caseRendererIds\":["
                    + string.Join(
                        ",",
                        caseRendererIds.Select(
                            value => $"\"{Escape(value.ToString())}\""))
                    + "],"
                    + "\"caseRootPosition\":"
                    + VectorJson(caseRootPosition)
                    + ",\"caseRootScale\":"
                    + VectorJson(caseRootScale)
                    + ",\"caseBounds\":"
                    + RectJson(caseBounds)
                    + ",\"packBounds\":"
                    + RectJson(packBounds)
                    + $",\"packVisible\":{packVisible.ToString().ToLowerInvariant()}"
                    + $",\"visibleFraction\":{Format(visibleFraction)}"
                    + $",\"whiteFraction\":{Format(whiteFraction)}"
                    + "}";
            }

            private static string VectorJson(Vector3 value)
            {
                return "{"
                    + $"\"x\":{Format(value.x)},"
                    + $"\"y\":{Format(value.y)},"
                    + $"\"z\":{Format(value.z)}"
                    + "}";
            }

            private static string RectJson(Rect value)
            {
                return "{"
                    + $"\"x\":{Format(value.x)},"
                    + $"\"y\":{Format(value.y)},"
                    + $"\"width\":{Format(value.width)},"
                    + $"\"height\":{Format(value.height)}"
                    + "}";
            }
        }
    }
}
