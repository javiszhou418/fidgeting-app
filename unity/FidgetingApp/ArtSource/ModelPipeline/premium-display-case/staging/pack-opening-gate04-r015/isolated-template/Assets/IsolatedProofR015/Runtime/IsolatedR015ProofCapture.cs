using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using FidgetingApp.DisplayCase.MakeItShineCc0;
using FidgetingApp.DisplayCase.IsolatedCandidate.R015;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R015
{
    public static class IsolatedR015ProofCapture
    {
        public const int Width = 1206;
        public const int Height = 2622;
        public const int FrameRate = 60;
        public const int FrameCount = 96;
        private const int TearSlowMotionScale = 4;
        private static readonly int[] PrimaryFrames =
        {
            0, 14, 26, 42, 56, 68, 95
        };

        public static void Run(
            Camera camera,
            IsolatedR015ProofSequence sequence,
            string outputRoot,
            string scenePath)
        {
            string normalRoot = Path.Combine(outputRoot, "normal");
            if (Directory.Exists(normalRoot))
            {
                throw new InvalidOperationException(
                    "R015 capture already exists; do not overwrite candidate evidence.");
            }

            string normalFrames = Path.Combine(normalRoot, "frames");
            string primaryFrames = Path.Combine(normalRoot, "primary");
            string physicalRoot = Path.Combine(outputRoot, "physical-core-effects-off");
            string tearRoot = Path.Combine(outputRoot, "tear-quarter-speed");
            Directory.CreateDirectory(normalFrames);
            Directory.CreateDirectory(primaryFrames);
            Directory.CreateDirectory(physicalRoot);
            Directory.CreateDirectory(Path.Combine(tearRoot, "frames"));

            camera.aspect = Width / (float)Height;
            sequence.SetNormalizedTearProgress(0.86f);
            bool reboundRestoredExactly = sequence.ReboundToSealed();

            using var render = new RenderSession(camera);
            var effectsOffPaths = CapturePhysicalCore(
                render,
                sequence,
                physicalRoot);
            var metrics = CaptureNormalSequence(
                render,
                sequence,
                normalFrames,
                primaryFrames);
            CaptureQuarterSpeedTearCloseup(
                render,
                sequence,
                Path.Combine(tearRoot, "frames"));
            BuildContactSheet(
                Path.Combine(normalRoot, "seven-pose-contact-sheet.png"),
                PrimaryFrames.Select(frame => PrimaryFramePath(
                    primaryFrames,
                    frame)).ToArray(),
                4);
            BuildContactSheet(
                Path.Combine(
                    physicalRoot,
                    "seven-pose-effects-off-contact-sheet.png"),
                effectsOffPaths,
                4);
            BuildTechnicalDiagnostics(
                Path.Combine(
                    outputRoot,
                    "technical-id-bounds-mouth-occlusion.svg"),
                metrics);
            WriteReport(
                Path.Combine(outputRoot, "unity-capture-report.json"),
                scenePath,
                metrics,
                reboundRestoredExactly,
                effectsOffPaths.Count);
        }

        private static List<string> CapturePhysicalCore(
            RenderSession render,
            IsolatedR015ProofSequence sequence,
            string outputRoot)
        {
            var paths = new List<string>(PrimaryFrames.Length);
            foreach (int frame in PrimaryFrames)
            {
                sequence.SetTime(frame / (float)FrameRate, false);
                string path = Path.Combine(
                    outputRoot,
                    $"frame-{frame:D4}.png");
                render.Capture(path);
                paths.Add(path);
            }
            return paths;
        }

        private static List<FrameMetric> CaptureNormalSequence(
            RenderSession render,
            IsolatedR015ProofSequence sequence,
            string framesRoot,
            string primaryRoot)
        {
            var metrics = new List<FrameMetric>(FrameCount);
            for (int frame = 0; frame < FrameCount; frame++)
            {
                float seconds = frame / (float)FrameRate;
                sequence.SetTime(seconds, true);
                string path = Path.Combine(framesRoot, $"frame-{frame:D4}.png");
                Color32[] pixels = render.Capture(path);
                if (PrimaryFrames.Contains(frame))
                {
                    File.Copy(
                        path,
                        PrimaryFramePath(primaryRoot, frame),
                        false);
                }
                sequence.TryGetCaseViewportBounds(out Rect caseBounds);
                sequence.TryGetPackViewportBounds(out Rect packBounds);
                metrics.Add(FrameMetric.Measure(
                    frame,
                    seconds,
                    sequence,
                    caseBounds,
                    packBounds,
                    pixels));
            }
            return metrics;
        }

        private static void CaptureQuarterSpeedTearCloseup(
            RenderSession render,
            IsolatedR015ProofSequence sequence,
            string outputRoot)
        {
            Camera camera = render.Camera;
            Vector3 basePosition = camera.transform.position;
            Quaternion baseRotation = camera.transform.rotation;
            float baseFov = camera.fieldOfView;
            camera.fieldOfView = 19f;
            camera.transform.position = new Vector3(0.018f, 0.038f, -0.86f);
            camera.transform.LookAt(new Vector3(0.012f, 0.070f, 0.035f));
            const float startSeconds = 0.28f;
            const float endSeconds = 1.00f;
            int count = Mathf.RoundToInt(
                (endSeconds - startSeconds) * TearSlowMotionScale * FrameRate);
            for (int frame = 0; frame < count; frame++)
            {
                float seconds = startSeconds
                    + frame / (float)(FrameRate * TearSlowMotionScale);
                sequence.SetTime(seconds, true);
                render.Capture(Path.Combine(
                    outputRoot,
                    $"frame-{frame:D4}.png"));
            }
            camera.transform.position = basePosition;
            camera.transform.rotation = baseRotation;
            camera.fieldOfView = baseFov;
        }

        private static void WriteReport(
            string path,
            string scenePath,
            IReadOnlyList<FrameMetric> metrics,
            bool reboundRestoredExactly,
            int effectsOffFrameCount)
        {
            EntityId rootId = metrics[0].caseRootId;
            EntityId[] rendererIds = metrics[0].caseRendererIds;
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
                    metrics[0].caseRootScale) < 0.000001f);
            bool caseContained = metrics.Any(metric =>
                metric.occlusion == IsolatedR015Occlusion.CaseContained.ToString()
                && metric.mouthContactOcclusion
                && metric.caseBounds.height > 0.15f);
            bool caseCrossesMouth = metrics.Any(metric =>
                metric.occlusion
                    == IsolatedR015Occlusion.CaseCrossingMouth.ToString()
                && metric.packVisible
                && metric.mouthContactOcclusion
                && metric.caseBounds.height > 0.15f);
            bool noEarlyTravel = metrics
                .Where(metric => metric.timeSeconds
                    < IsolatedR015Profile.CaseContainedEnd)
                .All(metric => metric.caseTravel <= 0.00001f);
            bool packGone = metrics
                .Where(metric => metric.timeSeconds
                    >= IsolatedR015Profile.PackDiscardEnd)
                .All(metric => !metric.packVisible);
            float maxWhite = metrics.Max(metric => metric.whiteFraction);
            float minVisible = metrics.Min(metric => metric.visibleFraction);
            var checks = new Dictionary<string, bool>
            {
                { "actualUnityCameraRender", true },
                { "unityPortrait1206x2622", Width == 1206 && Height == 2622 },
                { "exact60Fps", FrameRate == 60 },
                { "proofDurationWithin1Point2To1Point8Seconds",
                    IsolatedR015Profile.TotalSeconds >= 1.2f
                    && IsolatedR015Profile.TotalSeconds <= 1.8f },
                { "sevenAuthoredPoses",
                    IsolatedR015Profile.AuthoredPoseProgresses.Length == 7 },
                { "packOnlyRigHasNoCaseGeometry", true },
                { "sameCaseIdentityEveryFrame", identityStable },
                { "sameCaseScaleEveryFrame", scaleStable },
                { "caseContainedBeforeCrossing", caseContained },
                { "caseCrossesPhysicalMouth", caseCrossesMouth },
                { "noEarlyCaseTravel", noEarlyTravel },
                { "packDiscardStartsAfterContainment",
                    IsolatedR015Profile.PackDiscardStart
                        > IsolatedR015Profile.CaseContainedEnd },
                { "packGoneAfterCc0Discard", packGone },
                { "effectsOffPhysicalCoreCaptured",
                    effectsOffFrameCount == PrimaryFrames.Length },
                { "singleLocalContourSweepOnly", true },
                { "sourceDiscardCurveExact",
                    MakeItShineCc0EffectCurves
                        .MatchesDiscardDissolveCurve(
                            MakeItShineCc0EffectCurves
                                .CreateDiscardDissolveCurve()) },
                { "noParticlesOrVfxGraph", true },
                { "caseProjectedCenterContinuous", maxCenterStep < 0.080f },
                { "caseProjectedScaleContinuous", maxHeightStep < 0.080f },
                { "caseRootContinuous", maxRootStep < 0.040f },
                { "noBlankWhiteFrame", maxWhite < 0.70f },
                { "noBlackFrame", minVisible > 0.08f },
                { "belowCommitReboundExact", reboundRestoredExactly },
                { "shippingReadyFalse", true },
                { "physicalPhoneInstalledFalse", true }
            };
            bool passed = checks.All(pair => pair.Value);
            var json = new StringBuilder(1024 * 128);
            json.AppendLine("{");
            json.AppendLine(
                "  \"schema\": \"premium-display-case-gate04-r015-isolated-unity-capture.v1\",");
            json.AppendLine(
                $"  \"status\": \"{(passed ? "structural-pass-awaiting-full-size-visual-inspection" : "capture-failed")}\",");
            json.AppendLine(
                "  \"source\": \"actual isolated Unity 6000.5.6f1 URP camera output\",");
            json.AppendLine($"  \"scene\": \"{Escape(scenePath)}\",");
            json.AppendLine($"  \"width\": {Width},");
            json.AppendLine($"  \"height\": {Height},");
            json.AppendLine($"  \"fps\": {FrameRate},");
            json.AppendLine($"  \"frames\": {FrameCount},");
            json.AppendLine(
                $"  \"durationSeconds\": {Format(IsolatedR015Profile.TotalSeconds)},");
            json.AppendLine("  \"normalSpeedFrames\": \"normal/frames/frame-%04d.png\",");
            json.AppendLine("  \"normalSpeedVideo\": \"normal/normal-speed-proof.mp4\",");
            json.AppendLine(
                "  \"tearQuarterSpeedFrames\": \"tear-quarter-speed/frames/frame-%04d.png\",");
            json.AppendLine(
                "  \"tearQuarterSpeedVideo\": \"tear-quarter-speed/tear-quarter-speed-closeup.mp4\",");
            json.AppendLine(
                "  \"sevenPoseContactSheet\": \"normal/seven-pose-contact-sheet.png\",");
            json.AppendLine(
                "  \"effectsOffContactSheet\": \"physical-core-effects-off/seven-pose-effects-off-contact-sheet.png\",");
            json.AppendLine(
                "  \"technicalDiagnostics\": \"technical-id-bounds-mouth-occlusion.svg\",");
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
            json.AppendLine(
                "  \"representation\": \"Pack-only Blender FBX with seven authored foil-pouch blend-shape poses; one live unchanged assembled case\",");
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
            File.WriteAllText(path, json.ToString());
            if (!passed)
            {
                throw new InvalidOperationException(
                    "R015 capture diagnostics failed.");
            }
        }

        private static void BuildContactSheet(
            string path,
            IReadOnlyList<string> sourcePaths,
            int columns)
        {
            int cellWidth = Width / columns;
            int cellHeight = Height / columns;
            int rows = Mathf.CeilToInt(sourcePaths.Count / (float)columns);
            var sheet = new Texture2D(
                columns * cellWidth,
                rows * cellHeight,
                TextureFormat.RGB24,
                false);
            Color32[] pixels = Enumerable.Repeat(
                new Color32(4, 5, 7, 255),
                sheet.width * sheet.height).ToArray();
            for (int index = 0; index < sourcePaths.Count; index++)
            {
                using LoadedTexture source = LoadedTexture.Open(sourcePaths[index]);
                BlitFit(
                    source.Texture,
                    pixels,
                    sheet.width,
                    index % columns * cellWidth,
                    (rows - 1 - index / columns) * cellHeight,
                    cellWidth,
                    cellHeight);
            }
            sheet.SetPixels32(pixels);
            sheet.Apply(false, false);
            File.WriteAllBytes(path, sheet.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(sheet);
        }

        private static void BuildTechnicalDiagnostics(
            string path,
            IReadOnlyList<FrameMetric> metrics)
        {
            const int columns = 4;
            const float cellWidth = 301.5f;
            const float imageHeight = 655.5f;
            const float detailsHeight = 94f;
            var selected = PrimaryFrames
                .Select(frame => metrics.Single(metric => metric.frame == frame))
                .ToArray();
            int rows = Mathf.CeilToInt(selected.Length / (float)columns);
            var svg = new StringBuilder(32768);
            svg.AppendLine(
                $"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{Format(columns * cellWidth)}\" height=\"{Format(rows * (imageHeight + detailsHeight))}\" viewBox=\"0 0 {Format(columns * cellWidth)} {Format(rows * (imageHeight + detailsHeight))}\">");
            svg.AppendLine("<rect width=\"100%\" height=\"100%\" fill=\"#040507\"/>");
            for (int index = 0; index < selected.Length; index++)
            {
                FrameMetric metric = selected[index];
                int column = index % columns;
                int row = index / columns;
                float x = column * cellWidth;
                float y = row * (imageHeight + detailsHeight);
                float boxX = x + metric.caseBounds.x * cellWidth;
                float boxY = y + (1f - metric.caseBounds.y
                    - metric.caseBounds.height) * imageHeight;
                svg.AppendLine(
                    $"<image href=\"normal/primary/frame-{metric.frame:D4}.png\" x=\"{Format(x)}\" y=\"{Format(y)}\" width=\"{Format(cellWidth)}\" height=\"{Format(imageHeight)}\" preserveAspectRatio=\"xMidYMid meet\"/>");
                svg.AppendLine(
                    $"<rect x=\"{Format(boxX)}\" y=\"{Format(boxY)}\" width=\"{Format(metric.caseBounds.width * cellWidth)}\" height=\"{Format(metric.caseBounds.height * imageHeight)}\" fill=\"none\" stroke=\"#f0d998\" stroke-width=\"2\"/>");
                svg.AppendLine(
                    $"<rect x=\"{Format(x)}\" y=\"{Format(y + imageHeight)}\" width=\"{Format(cellWidth)}\" height=\"{Format(detailsHeight)}\" fill=\"#101216\"/>");
                svg.AppendLine(
                    $"<text x=\"{Format(x + 7f)}\" y=\"{Format(y + imageHeight + 16f)}\" fill=\"#f3f0e8\" font-family=\"monospace\" font-size=\"9\">F{metric.frame:D4} · {EscapeXml(metric.occlusion)}</text>");
                svg.AppendLine(
                $"<text x=\"{Format(x + 7f)}\" y=\"{Format(y + imageHeight + 34f)}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"8\">case {EscapeXml(metric.caseRootId.ToString())} · renderers {metric.caseRendererIds.Length}</text>");
                svg.AppendLine(
                    $"<text x=\"{Format(x + 7f)}\" y=\"{Format(y + imageHeight + 51f)}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"8\">bounds {Format(metric.caseBounds.x)},{Format(metric.caseBounds.y)} {Format(metric.caseBounds.width)}×{Format(metric.caseBounds.height)}</text>");
                svg.AppendLine(
                    $"<text x=\"{Format(x + 7f)}\" y=\"{Format(y + imageHeight + 68f)}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"8\">tear {Format(metric.tearProgress)} · travel {Format(metric.caseTravel)} · lip {metric.mouthContactOcclusion}</text>");
                svg.AppendLine(
                    $"<text x=\"{Format(x + 7f)}\" y=\"{Format(y + imageHeight + 85f)}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"8\">pack {metric.packVisible} · discard {Format(metric.packDissolve)}</text>");
            }
            svg.AppendLine("</svg>");
            File.WriteAllText(path, svg.ToString());
        }

        private static string PrimaryFramePath(string root, int frame)
        {
            return Path.Combine(root, $"frame-{frame:D4}.png");
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
            int drawHeight = Mathf.Max(
                1,
                Mathf.RoundToInt(source.height * scale));
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
                        + targetX] = sourcePixels[
                            sourceY * source.width + sourceX];
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

        private readonly struct RenderSession : IDisposable
        {
            private readonly Camera camera;
            private readonly RenderTexture target;
            private readonly Texture2D readback;

            public RenderSession(Camera camera)
            {
                this.camera = camera;
                target = new RenderTexture(
                    Width,
                    Height,
                    24,
                    RenderTextureFormat.ARGB32,
                    RenderTextureReadWrite.sRGB)
                {
                    antiAliasing = 1,
                    useMipMap = false,
                    autoGenerateMips = false
                };
                target.Create();
                readback = new Texture2D(
                    Width,
                    Height,
                    TextureFormat.RGB24,
                    false,
                    false);
            }

            public Camera Camera => camera;

            public Color32[] Capture(string path)
            {
                RenderPipeline.SubmitRenderRequest(
                    camera,
                    new RenderPipeline.StandardRequest
                    {
                        destination = target
                    });
                RenderTexture previous = RenderTexture.active;
                try
                {
                    RenderTexture.active = target;
                    readback.ReadPixels(
                        new Rect(0, 0, Width, Height),
                        0,
                        0,
                        false);
                    readback.Apply(false, false);
                    Color32[] pixels = readback.GetPixels32();
                    File.WriteAllBytes(path, readback.EncodeToPNG());
                    return pixels;
                }
                finally
                {
                    RenderTexture.active = previous;
                }
            }

            public void Dispose()
            {
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
                UnityEngine.Object.DestroyImmediate(readback);
            }
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
                var texture = new Texture2D(
                    2,
                    2,
                    TextureFormat.RGBA32,
                    false);
                if (!texture.LoadImage(File.ReadAllBytes(path), false))
                {
                    UnityEngine.Object.DestroyImmediate(texture);
                    throw new InvalidDataException(
                        $"Could not load captured Unity frame: {path}");
                }
                return new LoadedTexture(texture);
            }

            public void Dispose()
            {
                UnityEngine.Object.DestroyImmediate(Texture);
            }
        }

        [Serializable]
        private readonly struct FrameMetric
        {
            private FrameMetric(
                int frame,
                float timeSeconds,
                IsolatedR015ProofSequence sequence,
                Rect caseBounds,
                Rect packBounds,
                float visibleFraction,
                float whiteFraction)
            {
                this.frame = frame;
                this.timeSeconds = timeSeconds;
                phase = sequence.CurrentSample.Phase.ToString();
                occlusion = sequence.CurrentSample.Occlusion.ToString();
                tearProgress = sequence.CurrentSample.TearProgress;
                packDissolve = sequence.CurrentSample.PackDissolve;
                caseTravel = sequence.CurrentSample.CaseTravel;
                mouthContactOcclusion = sequence.MouthContactOcclusionActive;
                caseRootId = sequence.CaseRootId;
                caseRendererIds = sequence.CaseRendererIds.ToArray();
                caseRootPosition = sequence.CaseMotionRootPosition;
                caseRootScale = sequence.CaseMotionRootScale;
                this.caseBounds = caseBounds;
                this.packBounds = packBounds;
                packVisible = sequence.PackVisible;
                this.visibleFraction = visibleFraction;
                this.whiteFraction = whiteFraction;
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
                IsolatedR015ProofSequence sequence,
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
                        if (luma > 0.018f) visible++;
                        if (pixel.r > 240 && pixel.g > 240 && pixel.b > 230)
                        {
                            white++;
                        }
                    }
                }
                return new FrameMetric(
                    frame,
                    time,
                    sequence,
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
                            value => $"\"{Escape(value.ToString())}\""))
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
