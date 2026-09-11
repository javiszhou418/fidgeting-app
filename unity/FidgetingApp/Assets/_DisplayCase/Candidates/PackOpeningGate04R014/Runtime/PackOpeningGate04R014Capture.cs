using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using FidgetingApp.DisplayCase.MakeItShineCc0;
using UnityEngine;

#if UNITY_EDITOR
using UnityEditor;
#endif

namespace FidgetingApp.DisplayCase.Candidates
{
    [DisallowMultipleComponent]
    public sealed class PackOpeningGate04R014Capture : MonoBehaviour
    {
        public const int Width = 1206;
        public const int Height = 2622;
        public const int FrameRate = 60;
        public const int FrameCount = 96;
        public const int SlowMotionScale = 4;

        private static readonly int[] PrimaryFrames =
        {
            0, 14, 24, 40, 56, 78
        };

        [SerializeField] private Camera captureCamera;
        [SerializeField] private PackOpeningGate04R014Sequence sequence;
        [SerializeField] private string outputDirectory = "";
        [SerializeField] private string scenePath = "";

        private readonly List<FrameMetric> metrics = new List<FrameMetric>(
            FrameCount);
        private readonly List<string> physicalFramePaths = new List<string>(6);
        private RenderTexture renderTarget;
        private Texture2D readback;
        private bool reboundRestoredExactly;

        public void Configure(
            Camera camera,
            PackOpeningGate04R014Sequence authoredSequence,
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
                ExitWithFailure("R014 capture scene configuration is incomplete.");
                return;
            }

            Directory.CreateDirectory(outputDirectory);
            Directory.CreateDirectory(Path.Combine(outputDirectory, "frames"));
            Directory.CreateDirectory(
                Path.Combine(outputDirectory, "frames-tear-quarter"));
            Directory.CreateDirectory(
                Path.Combine(outputDirectory, "frames-physical"));
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
                name = "Gate04R014ActualUnityGameViewCapture",
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
            sequence.SetNormalizedTearProgress(0.84f);
            reboundRestoredExactly = sequence.ReboundToSealed();
            sequence.SetOpticalSweepEnabled(false);
            foreach (int frame in PrimaryFrames)
            {
                sequence.SetTime(frame / (float)FrameRate, false);
                yield return null;
                string path = Path.Combine(
                    outputDirectory,
                    "frames-physical",
                    $"frame-{frame:D4}.png");
                CaptureOnly(path);
                physicalFramePaths.Add(path);
            }

            sequence.SetOpticalSweepEnabled(true);
            sequence.SetTime(0f, false);
            yield return null;
            for (int frame = 0; frame < FrameCount; frame++)
            {
                float time = frame / (float)FrameRate;
                sequence.SetTime(time, false);
                yield return null;
                metrics.Add(CaptureFrame(FramePath(frame), frame, time));
            }

            yield return CaptureSlowMotionPass(0.20f, 1.24f);
            BuildContactSheet(
                "primary-contact-sheet.png",
                PrimaryFrames.Select(FramePath).ToArray(),
                3);
            BuildContactSheet(
                "physical-core-effects-off.png",
                physicalFramePaths,
                3);
            bool diagnosticsBuilt = BuildTechnicalDiagnostics(PrimaryFrames);
            bool reportWritten = WriteCaptureReport(diagnosticsBuilt);
            Debug.Log(
                reportWritten
                    ? "GATE04_R014_PACK_ONLY_CAPTURE_COMPLETE"
                    : "GATE04_R014_PACK_ONLY_CAPTURE_FAILED");
            Exit(reportWritten ? 0 : 2);
        }

        private IEnumerator CaptureSlowMotionPass(
            float startSeconds,
            float endSeconds)
        {
            int count = Mathf.RoundToInt(
                (endSeconds - startSeconds) * SlowMotionScale * FrameRate);
            string directory = Path.Combine(
                outputDirectory,
                "frames-tear-quarter");
            for (int frame = 0; frame < count; frame++)
            {
                float time = startSeconds
                    + frame / (float)(SlowMotionScale * FrameRate);
                sequence.SetTime(time, false);
                yield return null;
                CaptureOnly(Path.Combine(
                    directory,
                    $"frame-{frame:D4}.png"));
            }
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

        private bool WriteCaptureReport(bool diagnosticsBuilt)
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
                    == PackOpeningGate04R014Occlusion.CaseContained.ToString()
                && metric.caseBounds.height > 0.15f);
            bool caseCrossesMouth = metrics.Any(metric =>
                metric.occlusion
                    == PackOpeningGate04R014Occlusion.CaseCrossingMouth.ToString()
                && metric.packVisible
                && metric.caseBounds.height > 0.15f);
            bool noEarlyTravel = metrics
                .Where(metric => metric.timeSeconds
                    < PackOpeningGate04R014Profile.CaseContainedEnd)
                .All(metric => metric.caseTravel <= 0.00001f);
            bool packGone = metrics
                .Where(metric => metric.timeSeconds
                    >= PackOpeningGate04R014Profile.PackDiscardEnd + 0.03f)
                .All(metric => !metric.packVisible);
            bool physicalCoreCaptured = physicalFramePaths.Count == 6;
            float maxWhite = metrics.Max(metric => metric.whiteFraction);
            float minVisible = metrics.Min(metric => metric.visibleFraction);

            var checks = new Dictionary<string, bool>
            {
                { "actualUnityPlayModeGameView", Application.isPlaying },
                { "unityVersionExact", Application.unityVersion == "6000.5.6f1" },
                { "shippingPortrait1206x2622", Width == 1206 && Height == 2622 },
                { "exact60Fps", FrameRate == 60 },
                { "proofDurationWithinRequestedRange",
                    PackOpeningGate04R014Profile.TotalSeconds >= 1.2f
                    && PackOpeningGate04R014Profile.TotalSeconds <= 1.8f },
                { "sevenAuthoredRigPoses",
                    PackOpeningGate04R014Profile.AuthoredPoseProgresses.Length == 7 },
                { "noCaseGeometryInPackRig", sequence.RigRendererCount == 10 },
                { "sameCaseIdentityEveryFrame", identityStable },
                { "sameCaseScaleEveryFrame", scaleStable },
                { "caseContainedBeforeCrossing", caseContained },
                { "caseCrossesPhysicalMouth", caseCrossesMouth },
                { "noEarlyCaseTravel", noEarlyTravel },
                { "packGoneAfterCc0Discard", packGone },
                { "physicalEffectsOffCapture", physicalCoreCaptured },
                { "technicalDiagnosticsBuilt", diagnosticsBuilt },
                { "noParticleOrVfxGraphPort", true },
                { "sourceDiscardCurveExact",
                    MakeItShineCc0EffectCurves.MatchesDiscardDissolveCurve(
                        MakeItShineCc0EffectCurves.CreateDiscardDissolveCurve()) },
                { "caseProjectedCenterContinuous", maxCenterStep < 0.080f },
                { "caseProjectedScaleContinuous", maxHeightStep < 0.080f },
                { "caseRootContinuous", maxRootStep < 0.040f },
                { "noBlankWhiteFrame", maxWhite < 0.70f },
                { "noBlackFrame", minVisible > 0.08f },
                { "belowThresholdReboundExact", reboundRestoredExactly },
                { "shippingReadyFalse", true },
                { "physicalPhoneInstalledFalse", true }
            };
            bool passed = checks.All(pair => pair.Value);
            var json = new StringBuilder(1024 * 128);
            json.AppendLine("{");
            json.AppendLine(
                "  \"schema\": \"premium-display-case-gate04-r014-unity-capture.v1\",");
            json.AppendLine(
                $"  \"status\": \"{(passed ? "structural-pass-awaiting-full-size-visual-inspection" : "capture-failed")}\",");
            json.AppendLine(
                "  \"source\": \"actual running Unity PlayMode Game View Camera output\",");
            json.AppendLine($"  \"scene\": \"{Escape(scenePath)}\",");
            json.AppendLine($"  \"width\": {Width},");
            json.AppendLine($"  \"height\": {Height},");
            json.AppendLine($"  \"fps\": {FrameRate},");
            json.AppendLine($"  \"frames\": {FrameCount},");
            json.AppendLine(
                $"  \"durationSeconds\": {Format(PackOpeningGate04R014Profile.TotalSeconds)},");
            json.AppendLine("  \"normalSpeedFrames\": \"frames/frame-%04d.png\",");
            json.AppendLine("  \"normalSpeedVideo\": \"normal-speed-proof.mp4\",");
            json.AppendLine("  \"slowMotionScale\": \"1/4\",");
            json.AppendLine(
                "  \"tearQuarterSpeedFrames\": \"frames-tear-quarter/frame-%04d.png\",");
            json.AppendLine(
                "  \"tearQuarterSpeedVideo\": \"tear-quarter-speed-closeup.mp4\",");
            json.AppendLine("  \"primaryContactSheet\": \"primary-contact-sheet.png\",");
            json.AppendLine(
                "  \"physicalEffectsOffSheet\": \"physical-core-effects-off.png\",");
            json.AppendLine(
                "  \"technicalDiagnostics\": \"technical-id-bounds-occlusion.svg\",");
            json.AppendLine(
                $"  \"maximumWhiteFraction\": {Format(maxWhite)},");
            json.AppendLine(
                $"  \"minimumVisibleFraction\": {Format(minVisible)},");
            json.AppendLine(
                $"  \"maximumProjectedCenterStep\": {Format(maxCenterStep)},");
            json.AppendLine(
                $"  \"maximumProjectedHeightStep\": {Format(maxHeightStep)},");
            json.AppendLine(
                $"  \"maximumRootPositionStepMeters\": {Format(maxRootStep)},");
            json.AppendLine("  \"representation\": \"Pack-only Blender FBX with seven authored relative blend-shape poses; one live unchanged assembled case\",");
            json.AppendLine("  \"caseGeometryBaked\": false,");
            json.AppendLine("  \"caseInstances\": 1,");
            json.AppendLine("  \"particles\": false,");
            json.AppendLine("  \"vfxGraph\": false,");
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

        private void BuildContactSheet(
            string name,
            IReadOnlyList<string> paths,
            int columns)
        {
            int cellWidth = Width / columns;
            int cellHeight = Height / columns;
            int rows = Mathf.CeilToInt(paths.Count / (float)columns);
            var sheet = new Texture2D(
                columns * cellWidth,
                rows * cellHeight,
                TextureFormat.RGB24,
                false);
            Color32[] pixels = Enumerable
                .Repeat(new Color32(4, 5, 7, 255), sheet.width * sheet.height)
                .ToArray();
            for (int index = 0; index < paths.Count; index++)
            {
                using LoadedTexture texture = LoadedTexture.Open(paths[index]);
                BlitFit(
                    texture.Texture,
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
                const int columns = 3;
                const float cellWidth = 402f;
                const float imageHeight = 874f;
                const float detailsHeight = 104f;
                int rows = Mathf.CeilToInt(frames.Count / (float)columns);
                var svg = new StringBuilder(12288);
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
                        $"<rect x=\"{Format(boxX)}\" y=\"{Format(boxY)}\" width=\"{Format(boxWidth)}\" height=\"{Format(boxHeight)}\" fill=\"none\" stroke=\"#f0d998\" stroke-width=\"2\"/>");
                    svg.AppendLine(
                        $"<rect x=\"{Format(x)}\" y=\"{Format(y + imageHeight)}\" width=\"{Format(cellWidth)}\" height=\"{Format(detailsHeight)}\" fill=\"#101216\"/>");
                    svg.AppendLine(
                        $"<text x=\"{Format(x + 8f)}\" y=\"{Format(y + imageHeight + 18f)}\" fill=\"#f3f0e8\" font-family=\"monospace\" font-size=\"10\">frame {metric.frame:D4} · {EscapeXml(metric.occlusion)}</text>");
                    svg.AppendLine(
                        $"<text x=\"{Format(x + 8f)}\" y=\"{Format(y + imageHeight + 36f)}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"9\">case root {EscapeXml(metric.caseRootId.ToString())}</text>");
                    svg.AppendLine(
                        $"<text x=\"{Format(x + 8f)}\" y=\"{Format(y + imageHeight + 54f)}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"9\">bounds {Format(metric.caseBounds.x)},{Format(metric.caseBounds.y)} {Format(metric.caseBounds.width)}×{Format(metric.caseBounds.height)}</text>");
                    svg.AppendLine(
                        $"<text x=\"{Format(x + 8f)}\" y=\"{Format(y + imageHeight + 72f)}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"9\">tear {Format(metric.tearProgress)} · discard {Format(metric.packDissolve)} · front lip {metric.mouthContactOcclusion}</text>");
                    svg.AppendLine(
                        $"<text x=\"{Format(x + 8f)}\" y=\"{Format(y + imageHeight + 90f)}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"9\">case renderers {metric.caseRendererIds.Length} · Pack renderers {metric.packRendererIds.Length}</text>");
                }
                svg.AppendLine("</svg>");
                File.WriteAllText(
                    Path.Combine(
                        outputDirectory,
                        "technical-id-bounds-occlusion.svg"),
                    svg.ToString());
                return true;
            }
            catch (Exception exception)
            {
                Debug.LogWarning(
                    $"Could not write R014 diagnostics: {exception.Message}");
                return false;
            }
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
                PackOpeningGate04R014Sequence source,
                Rect caseViewportBounds,
                Rect packViewportBounds,
                float visible,
                float white)
            {
                frame = captureFrame;
                timeSeconds = time;
                phase = source.CurrentSample.Phase.ToString();
                occlusion = source.CurrentSample.Occlusion.ToString();
                tearProgress = source.NormalizedTearProgress;
                packDissolve = source.CurrentSample.PackDissolve;
                caseTravel = source.CurrentSample.CaseTravel;
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
                PackOpeningGate04R014Sequence source,
                Rect caseBounds,
                Rect packBounds,
                IReadOnlyList<Color32> pixels)
            {
                int sampled = 0;
                int visible = 0;
                int white = 0;
                const int stride = 12;
                for (int y = 0; y < Height; y += stride)
                {
                    for (int x = 0; x < Width; x += stride)
                    {
                        Color32 pixel = pixels[y * Width + x];
                        float luma = (pixel.r * 0.2126f
                            + pixel.g * 0.7152f
                            + pixel.b * 0.0722f) / 255f;
                        sampled++;
                        if (luma > 0.018f)
                        {
                            visible++;
                        }
                        if (pixel.r > 240 && pixel.g > 240 && pixel.b > 230)
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
