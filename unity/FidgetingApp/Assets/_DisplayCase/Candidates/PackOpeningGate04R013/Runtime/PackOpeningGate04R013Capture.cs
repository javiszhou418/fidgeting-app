using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using UnityEngine;

#if UNITY_EDITOR
using UnityEditor;
#endif

namespace FidgetingApp.DisplayCase.Candidates
{
    [DisallowMultipleComponent]
    public sealed class PackOpeningGate04R013Capture : MonoBehaviour
    {
        public const int Width = 1206;
        public const int Height = 2622;
        public const int FrameRate = 60;
        public const int FrameCount = 210;
        public const int SlowMotionScale = 4;

        private static readonly SourceMatch[] SourceMatches =
        {
            new SourceMatch(5.80f, 0.70f, "source-05.800s.png"),
            new SourceMatch(5.95f, 0.90f, "source-05.950s.png"),
            new SourceMatch(6.15f, 1.10f, "source-06.150s.png"),
            new SourceMatch(6.45f, 1.45f, "source-06.450s.png"),
            new SourceMatch(6.74f, 1.70f, "source-06.740s.png"),
            new SourceMatch(7.00f, 2.00f, "source-07.000s.png")
        };

        [SerializeField] private Camera captureCamera;
        [SerializeField] private PackOpeningGate04R013Sequence sequence;
        [SerializeField] private string outputDirectory = "";
        [SerializeField] private string scenePath = "";

        private readonly List<FrameMetric> metrics = new List<FrameMetric>(
            FrameCount);
        private RenderTexture renderTarget;
        private Texture2D readback;
        private bool reboundRestoredExactly;

        public void Configure(
            Camera camera,
            PackOpeningGate04R013Sequence authoredSequence,
            string output,
            string authoredScenePath)
        {
            captureCamera = camera;
            sequence = authoredSequence;
            outputDirectory = output;
            scenePath = authoredScenePath;
        }

        private void Start()
        {
            if (captureCamera == null
                || sequence == null
                || string.IsNullOrWhiteSpace(outputDirectory)
                || !sequence.HasRequiredBindings)
            {
                ExitWithFailure("R013 capture scene configuration is incomplete.");
                return;
            }

            Directory.CreateDirectory(outputDirectory);
            Directory.CreateDirectory(Path.Combine(outputDirectory, "frames"));
            Directory.CreateDirectory(
                Path.Combine(outputDirectory, "frames-tear-quarter"));
            Directory.CreateDirectory(
                Path.Combine(outputDirectory, "frames-impact-quarter"));
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
                name = "Gate04R013ActualUnityPortraitCapture",
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
            sequence.SetNormalizedDragProgress(0.72f);
            reboundRestoredExactly = sequence.ReboundToSealed();
            sequence.SetTime(0f, false);
            yield return null;

            for (int frame = 0; frame < FrameCount; frame++)
            {
                float time = frame / (float)FrameRate;
                sequence.SetTime(time, false);
                yield return null;
                metrics.Add(CaptureFrame(FramePath(frame), frame, time));
            }

            yield return CaptureSlowMotionPass(
                "frames-tear-quarter",
                0.58f,
                1.68f,
                new Vector3(0f, 0.018f, 0.145f),
                0.72f);
            yield return CaptureSlowMotionPass(
                "frames-impact-quarter",
                1.54f,
                2.46f,
                Vector3.zero,
                0.90f);

            int[] primaryFrames =
            {
                0,
                FrameForTearProgress(0.15f),
                FrameForTearProgress(0.35f),
                FrameForTearProgress(0.55f),
                FrameForTearProgress(0.75f),
                FrameForTearProgress(1.0f),
                FrameForTime(2.82f)
            };
            BuildContactSheet("primary-contact-sheet.png", primaryFrames, 3);
            BuildContactSheet(
                "continuity-contact-sheet.png",
                new[]
                {
                    FrameForTearProgress(0.35f),
                    FrameForTearProgress(0.55f),
                    FrameForTearProgress(0.75f),
                    FrameForTearProgress(1.0f),
                    FrameForTime(1.92f),
                    FrameForTime(2.20f),
                    FrameForTime(2.48f),
                    FrameForTime(2.82f)
                },
                4);
            bool diagnosticsBuilt = BuildTechnicalDiagnostics(primaryFrames);
            bool sourceComparisonBuilt = BuildSourceComparison();
            bool footprintBuilt = WriteRuntimeFootprint();
            bool passed = WriteCaptureReport(
                sourceComparisonBuilt,
                diagnosticsBuilt,
                footprintBuilt);
            Debug.Log(
                passed
                    ? "GATE04_R013_PACK_ONLY_BLENDER_CAPTURE_COMPLETE"
                    : "GATE04_R013_PACK_ONLY_BLENDER_CAPTURE_FAILED");
            Exit(passed ? 0 : 2);
        }

        private IEnumerator CaptureSlowMotionPass(
            string folder,
            float startSeconds,
            float endSeconds,
            Vector3 framingOffset,
            float fieldOfViewScale)
        {
            string directory = Path.Combine(outputDirectory, folder);
            Vector3 authoredPosition = captureCamera.transform.position;
            float authoredFov = captureCamera.fieldOfView;
            captureCamera.transform.position +=
                captureCamera.transform.rotation * framingOffset;
            captureCamera.fieldOfView *= fieldOfViewScale;
            int frames = Mathf.RoundToInt(
                (endSeconds - startSeconds) * SlowMotionScale * FrameRate);
            for (int frame = 0; frame < frames; frame++)
            {
                float time = startSeconds
                    + frame / (float)(SlowMotionScale * FrameRate);
                sequence.SetTime(time, false);
                yield return null;
                CaptureOnly(Path.Combine(directory, $"frame-{frame:D4}.png"));
            }
            captureCamera.transform.position = authoredPosition;
            captureCamera.fieldOfView = authoredFov;
            sequence.SetTime(endSeconds, false);
        }

        private FrameMetric CaptureFrame(string path, int frame, float time)
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
                sequence.TryGetCaseViewportBounds(out Rect caseBounds);
                sequence.TryGetPackViewportBounds(out Rect packBounds);
                return FrameMetric.Measure(
                    frame,
                    time,
                    sequence,
                    caseBounds,
                    packBounds,
                    pixels);
            }
            finally
            {
                RenderTexture.active = previous;
            }
        }

        private void CaptureOnly(string path)
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
                File.WriteAllBytes(path, readback.EncodeToPNG());
            }
            finally
            {
                RenderTexture.active = previous;
            }
        }

        private bool WriteCaptureReport(
            bool sourceComparisonBuilt,
            bool diagnosticsBuilt,
            bool footprintBuilt)
        {
            EntityId rootId = sequence.CaseRootEntityId;
            EntityId[] rendererIds = sequence.CaseRendererIds.ToArray();
            float maxCenterStep = 0f;
            float maxHeightStep = 0f;
            float maxRootStep = 0f;
            for (int index = 1; index < metrics.Count; index++)
            {
                FrameMetric previous = metrics[index - 1];
                FrameMetric current = metrics[index];
                maxCenterStep = Mathf.Max(
                    maxCenterStep,
                    Vector2.Distance(
                        previous.caseBounds.center,
                        current.caseBounds.center));
                maxHeightStep = Mathf.Max(
                    maxHeightStep,
                    Mathf.Abs(
                        current.caseBounds.height - previous.caseBounds.height));
                maxRootStep = Mathf.Max(
                    maxRootStep,
                    Vector3.Distance(
                        previous.caseRootPosition,
                        current.caseRootPosition));
            }

            bool identityStable = metrics.All(metric =>
                metric.caseRootId.Equals(rootId)
                && metric.caseRendererIds.SequenceEqual(rendererIds));
            bool scaleStable = metrics.All(metric =>
                Vector3.Distance(
                    metric.caseRootScale,
                    sequence.CaseAuthoredScale) < 0.000001f);
            bool caseContained = metrics.Any(metric =>
                metric.occlusion
                    == PackOpeningGate04R013Occlusion.CaseContained.ToString()
                && metric.tearProgress >= 0.35f
                && metric.caseBounds.height > 0.20f);
            bool caseCrossesMouth = metrics.Any(metric =>
                metric.occlusion
                    == PackOpeningGate04R013Occlusion.CaseCrossingMouth.ToString()
                && metric.packVisible
                && metric.caseBounds.height > 0.20f);
            bool packGone = metrics
                .Where(metric => metric.timeSeconds
                    >= PackOpeningGate04R013Profile.PackDiscardEnd + 0.03f)
                .All(metric => !metric.packVisible);
            bool sourceVisible = metrics
                .Where(metric => metric.timeSeconds >= 0.80f
                    && metric.timeSeconds <= 1.90f)
                .Any(metric => metric.sourceParticleCount > 0);
            float maxWhite = metrics.Max(metric => metric.whiteFraction);
            float minVisible = metrics.Min(metric => metric.visibleFraction);
            FrameMetric settled = metrics[metrics.Count - 1];
            sequence.SetTime(
                PackOpeningGate04R013Profile.TearEnd,
                false);
            bool fullTearContainsCase = sequence.IsCaseContainedInMouth();
            sequence.SetTime(
                PackOpeningGate04R013Profile.CaseTravelStart - 0.01f,
                false);
            bool noEarlyReveal = sequence.CurrentSample.CaseTravel == 0f;

            var checks = new Dictionary<string, bool>
            {
                { "realUnityPlayModeCapture", Application.isPlaying },
                { "unityVersionExact", Application.unityVersion == "6000.5.6f1" },
                { "shippingPortrait1206x2622", Width == 1206 && Height == 2622 },
                { "exact60Fps", FrameRate == 60 },
                { "blenderPackOnlyRigImported",
                    sequence.RigRendererCount == 10
                    && sequence.RigBlendShapeCount == 50
                    && sequence.RigVertexCount >= 10000 },
                { "fineTearColumns",
                    PackOpeningGate04R013Sequence.LongitudinalTearColumns >= 48 },
                { "sourceComparisonBuilt", sourceComparisonBuilt },
                { "technicalDiagnosticsBuilt", diagnosticsBuilt },
                { "runtimeFootprintBuilt", footprintBuilt },
                { "sameCaseIdentityEveryFrame", identityStable },
                { "sameCaseScaleEveryFrame", scaleStable },
                { "caseContainedBeforeCrossing", caseContained && fullTearContainsCase },
                { "caseCrossesPhysicalMouth", caseCrossesMouth },
                { "noEarlyCaseTravel", noEarlyReveal },
                { "packGoneAfterCc0Discard", packGone },
                { "caseProjectedCenterContinuous", maxCenterStep < 0.060f },
                { "caseProjectedScaleContinuous", maxHeightStep < 0.065f },
                { "caseRootContinuous", maxRootStep < 0.045f },
                { "physicalContactLipActive",
                    metrics.Any(metric => metric.mouthContactOcclusion) },
                { "noBlankWhiteFrame", maxWhite < 0.58f },
                { "noBlackFrame", minVisible > 0.10f },
                { "settledCaseReadable",
                    settled.caseBounds.height >= 0.48f
                    && settled.caseBounds.height <= 0.62f },
                { "belowThresholdReboundExact", reboundRestoredExactly },
                { "shippingReadyFalse", true },
                { "physicalPhoneInstalledFalse", true }
            };
            bool passed = checks.All(pair => pair.Value);
            var json = new StringBuilder(1024 * 512);
            json.AppendLine("{");
            json.AppendLine(
                "  \"schema\": \"premium-display-case-gate04-r013-unity-capture.v1\",");
            json.AppendLine(
                $"  \"status\": \"{(passed ? "structural-pass-awaiting-full-size-review" : "capture-failed")}\",");
            json.AppendLine(
                "  \"source\": \"actual running Unity PlayMode scene and Camera output\",");
            json.AppendLine($"  \"scene\": \"{Escape(scenePath)}\",");
            json.AppendLine($"  \"width\": {Width},");
            json.AppendLine($"  \"height\": {Height},");
            json.AppendLine($"  \"fps\": {FrameRate},");
            json.AppendLine($"  \"frames\": {FrameCount},");
            json.AppendLine(
                $"  \"durationSeconds\": {Format(PackOpeningGate04R013Profile.TotalSeconds)},");
            json.AppendLine("  \"normalSpeedFrames\": \"frames/frame-%04d.png\",");
            json.AppendLine($"  \"slowMotionScale\": \"1/{SlowMotionScale}\",");
            json.AppendLine(
                "  \"tearQuarterSpeedFrames\": \"frames-tear-quarter/frame-%04d.png\",");
            json.AppendLine(
                "  \"impactQuarterSpeedFrames\": \"frames-impact-quarter/frame-%04d.png\",");
            json.AppendLine("  \"primaryContactSheet\": \"primary-contact-sheet.png\",");
            json.AppendLine(
                "  \"technicalDiagnostics\": \"technical-continuity-sheet.svg\",");
            json.AppendLine(
                "  \"sourceComparison\": \"source-target-side-by-side.png\",");
            json.AppendLine(
                "  \"runtimeFootprint\": \"runtime-footprint-editor-estimate.json\",");
            json.AppendLine($"  \"maximumWhiteFraction\": {Format(maxWhite)},");
            json.AppendLine($"  \"minimumVisibleFraction\": {Format(minVisible)},");
            json.AppendLine(
                $"  \"maximumProjectedCenterStep\": {Format(maxCenterStep)},");
            json.AppendLine(
                $"  \"maximumProjectedHeightStep\": {Format(maxHeightStep)},");
            json.AppendLine(
                $"  \"maximumRootPositionStepMeters\": {Format(maxRootStep)},");
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
                metrics.Select(metric => metric.ToJson())));
            json.AppendLine("  ]");
            json.AppendLine("}");
            File.WriteAllText(
                Path.Combine(outputDirectory, "unity-capture-report.json"),
                json.ToString());
            return passed;
        }

        private bool WriteRuntimeFootprint()
        {
            try
            {
                const int float3Bytes = 12;
                int vertices = sequence.RigVertexCount;
                int blendShapes = sequence.RigBlendShapeCount;
                long estimatedBlendDeltaBytes =
                    (long)vertices * float3Bytes * (blendShapes / 10);
                int activePackDrawCalls = sequence.RigRendererCount;
                var json = new StringBuilder(1024);
                json.AppendLine("{");
                json.AppendLine(
                    "  \"schema\": \"premium-display-case-gate04-r013-runtime-footprint.v1\",");
                json.AppendLine("  \"evidenceType\": \"Unity Editor estimate; not device evidence\",");
                json.AppendLine("  \"representation\": \"10 SkinnedMeshRenderers with 5 relative blend shapes each\",");
                json.AppendLine($"  \"packRigRendererCount\": {sequence.RigRendererCount},");
                json.AppendLine($"  \"packRigVertexCount\": {vertices},");
                json.AppendLine($"  \"packRigBlendShapeCount\": {blendShapes},");
                json.AppendLine(
                    $"  \"estimatedPositionDeltaBytes\": {estimatedBlendDeltaBytes},");
                json.AppendLine($"  \"activePackDrawCallUpperBound\": {activePackDrawCalls},");
                json.AppendLine("  \"newPackTextureBytes\": 0,");
                json.AppendLine(
                    "  \"textureReuse\": \"existing 384x512 body/flap and CC0 flare atlas; no baked case texture or video\"");
                json.AppendLine("}");
                File.WriteAllText(
                    Path.Combine(
                        outputDirectory,
                        "runtime-footprint-editor-estimate.json"),
                    json.ToString());
                return true;
            }
            catch (Exception exception)
            {
                Debug.LogWarning(
                    $"Could not write R013 runtime estimate: {exception.Message}");
                return false;
            }
        }

        private void BuildContactSheet(
            string name,
            IReadOnlyList<int> frames,
            int columns)
        {
            int cellWidth = Width / columns;
            int cellHeight = Height / columns;
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

        private bool BuildTechnicalDiagnostics(IReadOnlyList<int> frames)
        {
            try
            {
                const int columns = 4;
                const float cellWidth = 301.5f;
                const float imageHeight = 655.5f;
                const float detailsHeight = 110f;
                int rows = Mathf.CeilToInt(frames.Count / (float)columns);
                var svg = new StringBuilder(16384);
                svg.AppendLine(
                    $"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{Format(columns * cellWidth)}\" height=\"{Format(rows * (imageHeight + detailsHeight))}\" viewBox=\"0 0 {Format(columns * cellWidth)} {Format(rows * (imageHeight + detailsHeight))}\">");
                svg.AppendLine("<rect width=\"100%\" height=\"100%\" fill=\"#040507\"/>");
                for (int index = 0; index < frames.Count; index++)
                {
                    FrameMetric metric = metrics.Single(
                        value => value.frame == frames[index]);
                    int column = index % columns;
                    int row = index / columns;
                    float x = column * cellWidth;
                    float y = row * (imageHeight + detailsHeight);
                    float boxX = x + metric.caseBounds.x * cellWidth;
                    float boxY = y + (1f - metric.caseBounds.y
                        - metric.caseBounds.height) * imageHeight;
                    float boxWidth = metric.caseBounds.width * cellWidth;
                    float boxHeight = metric.caseBounds.height * imageHeight;
                    svg.AppendLine(
                        $"<image href=\"frames/frame-{metric.frame:D4}.png\" x=\"{Format(x)}\" y=\"{Format(y)}\" width=\"{Format(cellWidth)}\" height=\"{Format(imageHeight)}\" preserveAspectRatio=\"xMidYMid meet\"/>");
                    svg.AppendLine(
                        $"<rect x=\"{Format(boxX)}\" y=\"{Format(boxY)}\" width=\"{Format(boxWidth)}\" height=\"{Format(boxHeight)}\" fill=\"none\" stroke=\"#f0df9c\" stroke-width=\"2\"/>");
                    svg.AppendLine(
                        $"<rect x=\"{Format(x)}\" y=\"{Format(y + imageHeight)}\" width=\"{Format(cellWidth)}\" height=\"{Format(detailsHeight)}\" fill=\"#101216\"/>");
                    svg.AppendLine(
                        $"<text x=\"{Format(x + 9f)}\" y=\"{Format(y + imageHeight + 19f)}\" fill=\"#f3f0e8\" font-family=\"monospace\" font-size=\"11\">frame {metric.frame:D4} · {EscapeXml(metric.occlusion)}</text>");
                    svg.AppendLine(
                        $"<text x=\"{Format(x + 9f)}\" y=\"{Format(y + imageHeight + 37f)}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"10\">case {EscapeXml(metric.caseRootId.ToString())}</text>");
                    svg.AppendLine(
                        $"<text x=\"{Format(x + 9f)}\" y=\"{Format(y + imageHeight + 55f)}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"10\">bounds {Format(metric.caseBounds.x)},{Format(metric.caseBounds.y)} {Format(metric.caseBounds.width)}×{Format(metric.caseBounds.height)}</text>");
                    svg.AppendLine(
                        $"<text x=\"{Format(x + 9f)}\" y=\"{Format(y + imageHeight + 73f)}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"10\">tear {Format(metric.tearProgress)} · dissolve {Format(metric.packDissolve)} · lip {metric.mouthContactOcclusion}</text>");
                    svg.AppendLine(
                        $"<text x=\"{Format(x + 9f)}\" y=\"{Format(y + imageHeight + 91f)}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"10\">pack IDs {metric.packRendererIds.Length} · case IDs {metric.caseRendererIds.Length}</text>");
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
                    $"Could not write R013 diagnostics: {exception.Message}");
                return false;
            }
        }

        private bool BuildSourceComparison()
        {
            string sourceDirectory = Path.Combine(
                outputDirectory,
                "source-reference");
            if (!SourceMatches.All(match => File.Exists(
                    Path.Combine(sourceDirectory, match.fileName))))
            {
                return false;
            }

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
            manifest.AppendLine(
                "  \"schema\": \"make-it-shine-matched-timestamps.v3\",");
            manifest.AppendLine("  \"pairs\": [");
            for (int index = 0; index < SourceMatches.Length; index++)
            {
                SourceMatch match = SourceMatches[index];
                int targetFrame = FrameForTime(match.targetTimeSeconds);
                int y = (SourceMatches.Length - 1 - index) * rowHeight;
                using (LoadedTexture source = LoadedTexture.Open(
                    Path.Combine(sourceDirectory, match.fileName)))
                {
                    BlitFit(source.Texture, pixels, sheet.width, 0, y, 760, rowHeight);
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
                    $"      \"sourceTimeSeconds\": {Format(match.sourceTimeSeconds)},");
                manifest.AppendLine(
                    $"      \"sourceFrame\": \"source-reference/{match.fileName}\",");
                manifest.AppendLine(
                    $"      \"targetTimeSeconds\": {Format(match.targetTimeSeconds)},");
                manifest.AppendLine($"      \"targetFrame\": {targetFrame}");
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

        private int FrameForTearProgress(float progress)
        {
            return metrics.OrderBy(metric =>
                Mathf.Abs(metric.tearProgress - progress)).First().frame;
        }

        private static int FrameForTime(float time)
        {
            return Mathf.Clamp(
                Mathf.RoundToInt(time * FrameRate),
                0,
                FrameCount - 1);
        }

        private string FramePath(int frame)
        {
            return Path.Combine(
                outputDirectory,
                "frames",
                $"frame-{frame:D4}.png");
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
                for (int targetX = 0; targetX < drawWidth; targetX++)
                {
                    int sourceX = Mathf.Min(
                        source.width - 1,
                        targetX * source.width / drawWidth);
                    int sourceY = Mathf.Min(
                        source.height - 1,
                        targetY * source.height / drawHeight);
                    destination[
                        (offsetY + targetY) * destinationWidth
                        + offsetX
                        + targetX] =
                        sourcePixels[sourceY * source.width + sourceX];
                }
            }
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
            public SourceMatch(
                float sourceTime,
                float targetTime,
                string sourceFileName)
            {
                sourceTimeSeconds = sourceTime;
                targetTimeSeconds = targetTime;
                fileName = sourceFileName;
            }

            public readonly float sourceTimeSeconds;
            public readonly float targetTimeSeconds;
            public readonly string fileName;
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
                int captureFrame,
                float time,
                PackOpeningGate04R013Sequence source,
                Rect caseViewportBounds,
                Rect packViewportBounds,
                float visible,
                float white)
            {
                frame = captureFrame;
                timeSeconds = time;
                phase = source.CurrentSample.Phase.ToString();
                occlusion = source.CurrentSample.Occlusion.ToString();
                tearProgress = source.NormalizedDragProgress;
                packDissolve = source.CurrentSample.PackDissolve;
                caseTravel = source.CurrentSample.CaseTravel;
                sourceParticleCount = source.SourceEffectSystems.Sum(
                    system => system == null ? 0 : system.particleCount);
                mouthContactOcclusion = source.MouthContactOcclusionActive;
                caseRootId = source.CaseRootEntityId;
                caseRendererIds = source.CaseRendererIds.ToArray();
                packRendererIds = source.PackRendererIds.ToArray();
                caseRootPosition = source.CaseMotionRoot.localPosition;
                caseRootScale = source.CaseMotionRoot.localScale;
                caseBounds = caseViewportBounds;
                packBounds = packViewportBounds;
                packVisible = source.PackVisible;
                visibleFraction = visible;
                whiteFraction = white;
            }

            public readonly int frame;
            public readonly float timeSeconds;
            public readonly string phase;
            public readonly string occlusion;
            public readonly float tearProgress;
            public readonly float packDissolve;
            public readonly float caseTravel;
            public readonly int sourceParticleCount;
            public readonly bool mouthContactOcclusion;
            public readonly EntityId caseRootId;
            public readonly EntityId[] caseRendererIds;
            public readonly EntityId[] packRendererIds;
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
                PackOpeningGate04R013Sequence source,
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
                        sampled++;
                        if (luma > 0.018f)
                        {
                            visible++;
                        }
                        if (r > 0.94f && g > 0.94f && b > 0.90f)
                        {
                            white++;
                        }
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
                return "    {"
                    + $"\"frame\":{frame},"
                    + $"\"timeSeconds\":{Format(timeSeconds)},"
                    + $"\"phase\":\"{phase}\","
                    + $"\"occlusion\":\"{occlusion}\","
                    + $"\"tearProgress\":{Format(tearProgress)},"
                    + $"\"packDissolve\":{Format(packDissolve)},"
                    + $"\"caseTravel\":{Format(caseTravel)},"
                    + $"\"sourceParticleCount\":{sourceParticleCount},"
                    + $"\"mouthContactOcclusion\":{mouthContactOcclusion.ToString().ToLowerInvariant()},"
                    + $"\"caseRootId\":\"{Escape(caseRootId.ToString())}\","
                    + "\"caseRendererIds\":["
                    + string.Join(
                        ",",
                        caseRendererIds.Select(
                            id => $"\"{Escape(id.ToString())}\""))
                    + "],"
                    + "\"packRendererIds\":["
                    + string.Join(
                        ",",
                        packRendererIds.Select(
                            id => $"\"{Escape(id.ToString())}\""))
                    + "],"
                    + "\"caseRootPosition\":" + VectorJson(caseRootPosition)
                    + ",\"caseRootScale\":" + VectorJson(caseRootScale)
                    + ",\"caseBounds\":" + RectJson(caseBounds)
                    + ",\"packBounds\":" + RectJson(packBounds)
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
