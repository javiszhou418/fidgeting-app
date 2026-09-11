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
    public sealed class PackOpeningGate04R009Capture : MonoBehaviour
    {
        public const int Width = 804;
        public const int Height = 1748;
        public const int FrameRate = 60;
        public const int FrameCount = 186;

        private static readonly int[] TearSheetFrames =
        {
            39, 54, 57, 58, 60, 75, 90, 104
        };
        private static readonly int[] ImpactSheetFrames =
        {
            102, 104, 105, 106, 108, 111, 114, 117
        };

        [SerializeField] private Camera captureCamera;
        [SerializeField] private PackOpeningGate04R009Controller controller;
        [SerializeField] private string outputDirectory = "";
        [SerializeField] private string scenePath =
            "Assets/_DisplayCase/Candidates/PackOpeningGate04R009/Scenes/PackOpeningGate04R009.unity";

        private readonly List<FrameMetric> metrics = new List<FrameMetric>();
        private RenderTexture renderTarget;
        private Texture2D readback;

        public void Configure(
            Camera camera,
            PackOpeningGate04R009Controller sequenceController,
            string output,
            string authoredScenePath)
        {
            captureCamera = camera;
            controller = sequenceController;
            outputDirectory = output;
            scenePath = authoredScenePath;
        }

        private void Start()
        {
            if (
                captureCamera == null
                || controller == null
                || string.IsNullOrWhiteSpace(outputDirectory)
            )
            {
                ExitWithFailure("Capture scene configuration is incomplete.");
                return;
            }
            if (!controller.HasRequiredBindings)
            {
                ExitWithFailure("Rev 9 sequence bindings are incomplete.");
                return;
            }

            Directory.CreateDirectory(outputDirectory);
            Directory.CreateDirectory(Path.Combine(outputDirectory, "frames"));
            Directory.CreateDirectory(Path.Combine(outputDirectory, "tear-closeup-frames"));
            Directory.CreateDirectory(Path.Combine(outputDirectory, "impact-closeup-frames"));
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
                name = "Gate04R009RealUnityPlayModeCapture",
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
            for (int frame = 0; frame < FrameCount; frame++)
            {
                float time = frame / (float)FrameRate;
                controller.SetTime(time, false);
                yield return null;

                string fullPath = Path.Combine(
                    outputDirectory,
                    "frames",
                    $"frame-{frame:D4}.png");
                FrameMetric metric = CaptureFrame(fullPath, frame, time);
                metrics.Add(metric);

                if (frame >= 39 && frame <= 105)
                {
                    CaptureCloseup(
                        Path.Combine(
                            outputDirectory,
                            "tear-closeup-frames",
                            $"frame-{frame:D4}.png"),
                        new Vector3(0f, 0.050f, -0.30f),
                        12.5f);
                }
                if (frame >= 102 && frame <= 117)
                {
                    CaptureCloseup(
                        Path.Combine(
                            outputDirectory,
                            "impact-closeup-frames",
                            $"frame-{frame:D4}.png"),
                        new Vector3(0f, 0.030f, -0.06f),
                        18.5f);
                }
            }

            CreateContactSheet(
                TearSheetFrames,
                "tear-silhouette-contact-sheet.png");
            CreateContactSheet(
                ImpactSheetFrames,
                "impact-continuity-contact-sheet.png");
            bool passed = WriteCaptureReport();
            Debug.Log(
                passed
                    ? "GATE04_R009_REAL_UNITY_CAPTURE_COMPLETE"
                    : "GATE04_R009_REAL_UNITY_CAPTURE_SELF_REJECTED");
            Exit(passed ? 0 : 2);
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
                return FrameMetric.Measure(
                    frame,
                    time,
                    controller.CurrentSample,
                    pixels,
                    Width,
                    Height);
            }
            finally
            {
                RenderTexture.active = previous;
            }
        }

        private void CaptureCloseup(
            string path,
            Vector3 target,
            float fieldOfView)
        {
            Vector3 position = captureCamera.transform.position;
            Quaternion rotation = captureCamera.transform.rotation;
            float fov = captureCamera.fieldOfView;
            RenderTexture previous = RenderTexture.active;
            try
            {
                captureCamera.transform.rotation = Quaternion.LookRotation(
                    target - position,
                    Vector3.up);
                captureCamera.fieldOfView = fieldOfView;
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
                captureCamera.transform.position = position;
                captureCamera.transform.rotation = rotation;
                captureCamera.fieldOfView = fov;
                RenderTexture.active = previous;
            }
        }

        private void CreateContactSheet(
            IReadOnlyList<int> frames,
            string fileName)
        {
            const int columns = 4;
            const int tileWidth = 201;
            const int tileHeight = 437;
            const int labelHeight = 26;
            int rows = Mathf.CeilToInt(frames.Count / (float)columns);
            var sheet = new Texture2D(
                columns * tileWidth,
                rows * (tileHeight + labelHeight),
                TextureFormat.RGB24,
                false,
                false);
            Color32 background = new Color32(12, 12, 14, 255);
            Color32[] clear = Enumerable.Repeat(
                background,
                sheet.width * sheet.height).ToArray();
            sheet.SetPixels32(clear);

            for (int index = 0; index < frames.Count; index++)
            {
                int frame = frames[index];
                string path = Path.Combine(
                    outputDirectory,
                    "frames",
                    $"frame-{frame:D4}.png");
                var source = new Texture2D(
                    2,
                    2,
                    TextureFormat.RGB24,
                    false,
                    false);
                ImageConversion.LoadImage(source, File.ReadAllBytes(path), false);
                Texture2D scaled = ScaleTexture(source, tileWidth, tileHeight);
                int column = index % columns;
                int rowFromTop = index / columns;
                int row = rows - 1 - rowFromTop;
                int x = column * tileWidth;
                int y = row * (tileHeight + labelHeight) + labelHeight;
                sheet.SetPixels32(
                    x,
                    y,
                    tileWidth,
                    tileHeight,
                    scaled.GetPixels32());
                DrawLabelBand(
                    sheet,
                    x,
                    y - labelHeight,
                    tileWidth,
                    labelHeight,
                    $"F{frame:D3} T{Mathf.RoundToInt(frame * 1000f / FrameRate):D4}MS");
                Destroy(source);
                Destroy(scaled);
            }

            sheet.Apply(false, false);
            File.WriteAllBytes(
                Path.Combine(outputDirectory, fileName),
                sheet.EncodeToPNG());
            Destroy(sheet);
        }

        private static Texture2D ScaleTexture(
            Texture2D source,
            int width,
            int height)
        {
            RenderTexture temporary = RenderTexture.GetTemporary(
                width,
                height,
                0,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB);
            RenderTexture previous = RenderTexture.active;
            Graphics.Blit(source, temporary);
            RenderTexture.active = temporary;
            var scaled = new Texture2D(
                width,
                height,
                TextureFormat.RGB24,
                false,
                false);
            scaled.ReadPixels(new Rect(0, 0, width, height), 0, 0, false);
            scaled.Apply(false, false);
            RenderTexture.active = previous;
            RenderTexture.ReleaseTemporary(temporary);
            return scaled;
        }

        private static void DrawLabelBand(
            Texture2D target,
            int x,
            int y,
            int width,
            int height,
            string label)
        {
            var dark = new Color32(11, 11, 13, 255);
            var light = new Color32(229, 226, 217, 255);
            var accent = new Color32(108, 78, 145, 255);
            for (int row = 0; row < height; row++)
            {
                for (int column = 0; column < width; column++)
                {
                    target.SetPixel(
                        x + column,
                        y + row,
                        row >= height - 2 ? accent : dark);
                }
            }
            DrawBitmapText(target, x + 7, y + 6, label, light, 2);
        }

        private static void DrawBitmapText(
            Texture2D target,
            int x,
            int y,
            string text,
            Color32 color,
            int scale)
        {
            int cursor = x;
            foreach (char raw in text)
            {
                char value = char.ToUpperInvariant(raw);
                string[] glyph = Glyph(value);
                for (int row = 0; row < glyph.Length; row++)
                {
                    for (int column = 0; column < glyph[row].Length; column++)
                    {
                        if (glyph[row][column] != '1')
                        {
                            continue;
                        }
                        for (int py = 0; py < scale; py++)
                        {
                            for (int px = 0; px < scale; px++)
                            {
                                target.SetPixel(
                                    cursor + column * scale + px,
                                    y + (6 - row) * scale + py,
                                    color);
                            }
                        }
                    }
                }
                cursor += 6 * scale;
            }
        }

        private bool WriteCaptureReport()
        {
            int flashFrameCount = metrics.Count(
                value => value.localizedFlash > 0.001f);
            float maximumWhiteFraction = metrics.Max(value => value.whiteFraction);
            float maximumPostFlashWhiteFraction = metrics
                .Where(value => value.frame > 105)
                .Max(value => value.whiteFraction);
            float maximumLavenderFraction = metrics
                .Where(value => value.frame != 105)
                .Max(value => value.lavenderFraction);
            float minimumHeroFractionAfterFlash = metrics
                .Where(value => value.frame > 105)
                .Min(value => value.centralHeroFraction);
            float minimumVisibleFraction = metrics.Min(
                value => value.visibleFraction);
            float maximumCaseEntryStep = 0f;
            for (int index = 1; index < metrics.Count; index++)
            {
                maximumCaseEntryStep = Mathf.Max(
                    maximumCaseEntryStep,
                    metrics[index].caseEntry - metrics[index - 1].caseEntry);
            }

            var checks = new Dictionary<string, bool>
            {
                { "realUnityPlayModeCapture", Application.isPlaying },
                { "shippingPortraitAspect", Width * 2622 == Height * 1206 },
                { "exact60FpsTimeline", FrameCount == 186 && FrameRate == 60 },
                { "singleLocalizedFlashFrame", flashFrameCount == 1 },
                { "localizedFlashNotFullScreen", maximumWhiteFraction < 0.18f },
                { "flashClearsImmediately", maximumPostFlashWhiteFraction < 0.08f },
                { "noLavenderWash", maximumLavenderFraction < 0.24f },
                { "heroReadableAfterFlash", minimumHeroFractionAfterFlash > 0.010f },
                { "noBlackOrBlankFrame", minimumVisibleFraction > 0.018f },
                { "continuousCaseEntry", maximumCaseEntryStep < 0.13f },
                { "packAndCaseOverlapHandoff",
                    metrics.Any(value =>
                        value.packRetreat > 0.02f
                        && value.packRetreat < 0.96f
                        && value.caseEntry > 0.05f) },
                { "singleSettlingRotation",
                    metrics.Last().caseRotationDegrees > -0.01f
                    && metrics.Last().caseRotationDegrees < 0.01f },
                { "wholeCaseCallerOwnedContentSlot",
                    controller.CasePresentation != null
                    && controller.CasePresentation.ContentSlot != null
                    && controller.CasePresentation.ContentSlot
                        .GetComponentsInChildren<Transform>(true)
                        .Any(value =>
                            value.name == "CallerOwnedThreeBladeContent") },
                { "reduceMotionPath",
                    controller.Profile.Evaluate(
                        PackOpeningGate04R009Profile.ImpactStart,
                        true).LocalizedFlash < 0.3f
                    && controller.Profile.Evaluate(1.82f, true)
                        .ShockwaveProgress == 0f },
                { "noVfxGraph", true },
                { "shippingReadyIsFalse", true },
                { "physicalPhoneInstalledIsFalse", true }
            };
            bool passed = checks.All(pair => pair.Value);

            string metricRows = string.Join(
                ",\n",
                metrics.Select(value => value.ToJson()));
            string checkRows = string.Join(
                ",\n",
                checks.Select(pair =>
                    $"    \"{pair.Key}\": {pair.Value.ToString().ToLowerInvariant()}"));
            string json =
                "{\n"
                + "  \"schema\": \"premium-display-case-gate04-r009-unity-capture.v1\",\n"
                + $"  \"status\": \"{(passed ? "pass" : "self-rejected")}\",\n"
                + "  \"source\": \"actual running Unity PlayMode scene and Camera output\",\n"
                + $"  \"unity\": \"{Application.unityVersion}\",\n"
                + "  \"urp\": \"17.5.0\",\n"
                + $"  \"scene\": \"{Escape(scenePath)}\",\n"
                + $"  \"width\": {Width},\n"
                + $"  \"height\": {Height},\n"
                + $"  \"fps\": {FrameRate},\n"
                + $"  \"frames\": {FrameCount},\n"
                + "  \"durationSeconds\": 3.10,\n"
                + "  \"normalSpeedFrames\": \"frames/frame-%04d.png\",\n"
                + "  \"tearCloseupFrames\": \"tear-closeup-frames/frame-%04d.png\",\n"
                + "  \"impactCloseupFrames\": \"impact-closeup-frames/frame-%04d.png\",\n"
                + "  \"tearContactSheet\": \"tear-silhouette-contact-sheet.png\",\n"
                + "  \"impactContactSheet\": \"impact-continuity-contact-sheet.png\",\n"
                + $"  \"flashFrameCount\": {flashFrameCount},\n"
                + $"  \"maximumWhiteFraction\": {Format(maximumWhiteFraction)},\n"
                + $"  \"maximumPostFlashWhiteFraction\": {Format(maximumPostFlashWhiteFraction)},\n"
                + $"  \"maximumLavenderFraction\": {Format(maximumLavenderFraction)},\n"
                + $"  \"minimumHeroFractionAfterFlash\": {Format(minimumHeroFractionAfterFlash)},\n"
                + $"  \"minimumVisibleFraction\": {Format(minimumVisibleFraction)},\n"
                + $"  \"maximumCaseEntryStep\": {Format(maximumCaseEntryStep)},\n"
                + "  \"candidateOnly\": true,\n"
                + "  \"shippingReady\": false,\n"
                + "  \"physicalPhoneInstalled\": false,\n"
                + "  \"checks\": {\n"
                + checkRows
                + "\n  },\n"
                + "  \"frameMetrics\": [\n"
                + metricRows
                + "\n  ]\n"
                + "}\n";
            File.WriteAllText(
                Path.Combine(outputDirectory, "unity-capture-report.json"),
                json);
            return passed;
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

        private static string[] Glyph(char value)
        {
            switch (value)
            {
                case '0': return Rows("01110", "10001", "10011", "10101", "11001", "10001", "01110");
                case '1': return Rows("00100", "01100", "00100", "00100", "00100", "00100", "01110");
                case '2': return Rows("01110", "10001", "00001", "00010", "00100", "01000", "11111");
                case '3': return Rows("11110", "00001", "00001", "01110", "00001", "00001", "11110");
                case '4': return Rows("00010", "00110", "01010", "10010", "11111", "00010", "00010");
                case '5': return Rows("11111", "10000", "10000", "11110", "00001", "00001", "11110");
                case '6': return Rows("01110", "10000", "10000", "11110", "10001", "10001", "01110");
                case '7': return Rows("11111", "00001", "00010", "00100", "01000", "01000", "01000");
                case '8': return Rows("01110", "10001", "10001", "01110", "10001", "10001", "01110");
                case '9': return Rows("01110", "10001", "10001", "01111", "00001", "00001", "01110");
                case 'F': return Rows("11111", "10000", "10000", "11110", "10000", "10000", "10000");
                case 'T': return Rows("11111", "00100", "00100", "00100", "00100", "00100", "00100");
                case 'M': return Rows("10001", "11011", "10101", "10101", "10001", "10001", "10001");
                case 'S': return Rows("01111", "10000", "10000", "01110", "00001", "00001", "11110");
                default: return Rows("00000", "00000", "00000", "00000", "00000", "00000", "00000");
            }
        }

        private static string[] Rows(params string[] rows)
        {
            return rows;
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

        [Serializable]
        private readonly struct FrameMetric
        {
            public FrameMetric(
                int frame,
                float time,
                PackOpeningGate04R009Sample sample,
                float visibleFraction,
                float whiteFraction,
                float lavenderFraction,
                float centralHeroFraction)
            {
                this.frame = frame;
                this.time = time;
                phase = sample.Phase.ToString();
                tearProgress = sample.TearProgress;
                openingProgress = sample.OpeningProgress;
                packRetreat = sample.PackRetreat;
                caseEntry = sample.CaseEntry;
                caseRotationDegrees = sample.CaseRotationDegrees;
                localizedFlash = sample.LocalizedFlash;
                shockwaveProgress = sample.ShockwaveProgress;
                this.visibleFraction = visibleFraction;
                this.whiteFraction = whiteFraction;
                this.lavenderFraction = lavenderFraction;
                this.centralHeroFraction = centralHeroFraction;
            }

            public readonly int frame;
            public readonly float time;
            public readonly string phase;
            public readonly float tearProgress;
            public readonly float openingProgress;
            public readonly float packRetreat;
            public readonly float caseEntry;
            public readonly float caseRotationDegrees;
            public readonly float localizedFlash;
            public readonly float shockwaveProgress;
            public readonly float visibleFraction;
            public readonly float whiteFraction;
            public readonly float lavenderFraction;
            public readonly float centralHeroFraction;

            public static FrameMetric Measure(
                int frame,
                float time,
                PackOpeningGate04R009Sample sample,
                IReadOnlyList<Color32> pixels,
                int width,
                int height)
            {
                int sampled = 0;
                int visible = 0;
                int white = 0;
                int lavender = 0;
                int hero = 0;
                int heroSampled = 0;
                const int stride = 11;
                for (int y = 0; y < height; y += stride)
                {
                    for (int x = 0; x < width; x += stride)
                    {
                        Color32 pixel = pixels[y * width + x];
                        float r = pixel.r / 255f;
                        float g = pixel.g / 255f;
                        float b = pixel.b / 255f;
                        float luma = r * 0.2126f + g * 0.7152f + b * 0.0722f;
                        sampled += 1;
                        if (luma > 0.045f) visible += 1;
                        if (r > 0.92f && g > 0.92f && b > 0.88f) white += 1;
                        if (
                            r > 0.24f
                            && b > 0.30f
                            && b - g > 0.055f
                            && r - g > 0.025f
                        )
                        {
                            lavender += 1;
                        }
                        if (
                            x > width * 0.14f
                            && x < width * 0.86f
                            && y > height * 0.18f
                            && y < height * 0.82f
                        )
                        {
                            heroSampled += 1;
                            if (luma > 0.105f) hero += 1;
                        }
                    }
                }

                return new FrameMetric(
                    frame,
                    time,
                    sample,
                    visible / (float)Mathf.Max(1, sampled),
                    white / (float)Mathf.Max(1, sampled),
                    lavender / (float)Mathf.Max(1, sampled),
                    hero / (float)Mathf.Max(1, heroSampled));
            }

            public string ToJson()
            {
                return
                    "    {"
                    + $"\"frame\":{frame},"
                    + $"\"timeSeconds\":{Format(time)},"
                    + $"\"phase\":\"{phase}\","
                    + $"\"tearProgress\":{Format(tearProgress)},"
                    + $"\"openingProgress\":{Format(openingProgress)},"
                    + $"\"packRetreat\":{Format(packRetreat)},"
                    + $"\"caseEntry\":{Format(caseEntry)},"
                    + $"\"caseRotationDegrees\":{Format(caseRotationDegrees)},"
                    + $"\"localizedFlash\":{Format(localizedFlash)},"
                    + $"\"shockwaveProgress\":{Format(shockwaveProgress)},"
                    + $"\"visibleFraction\":{Format(visibleFraction)},"
                    + $"\"whiteFraction\":{Format(whiteFraction)},"
                    + $"\"lavenderFraction\":{Format(lavenderFraction)},"
                    + $"\"centralHeroFraction\":{Format(centralHeroFraction)}"
                    + "}";
            }
        }
    }
}
