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
    public sealed class PackOpeningGate04R010Capture : MonoBehaviour
    {
        public const int Width = 1206;
        public const int Height = 2622;
        public const int FrameRate = 60;
        public const int FrameCount = 186;

        [SerializeField] private Camera captureCamera;
        [SerializeField] private PackOpeningGate04R010Controller controller;
        [SerializeField] private string outputDirectory = "";
        [SerializeField] private string scenePath =
            "Assets/_DisplayCase/Candidates/PackOpeningGate04R010/Scenes/PackOpeningGate04R010.unity";

        private readonly List<FrameMetric> metrics =
            new List<FrameMetric>(FrameCount);
        private RenderTexture renderTarget;
        private Texture2D readback;
        private bool reboundRestoredExactly;

        public void Configure(
            Camera camera,
            PackOpeningGate04R010Controller sequenceController,
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
                ExitWithFailure("Rev 10 sequence bindings are incomplete.");
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
                name = "Gate04R010RealUnityShippingPortraitCapture",
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
            controller.SetTime(0.76f, false);
            reboundRestoredExactly = controller.ReboundToSealed();
            yield return null;

            for (int frame = 0; frame < FrameCount; frame++)
            {
                float time = frame / (float)FrameRate;
                controller.SetTime(time, false);
                yield return null;
                string path = Path.Combine(
                    outputDirectory,
                    "frames",
                    $"frame-{frame:D4}.png");
                metrics.Add(CaptureFrame(path, frame, time));
            }

            bool passed = WriteCaptureReport();
            Debug.Log(
                passed
                    ? "GATE04_R010_REAL_UNITY_CAPTURE_COMPLETE"
                    : "GATE04_R010_REAL_UNITY_CAPTURE_SELF_REJECTED");
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
                controller.TryGetCaseViewportBounds(out Rect caseBounds);
                controller.TryGetPackViewportBounds(out Rect packBounds);
                float tearFrontViewportX = captureCamera.WorldToViewportPoint(
                    controller.TearFrontWorldPosition).x;
                return FrameMetric.Measure(
                    frame,
                    time,
                    controller,
                    caseBounds,
                    packBounds,
                    tearFrontViewportX,
                    pixels,
                    Width,
                    Height);
            }
            finally
            {
                RenderTexture.active = previous;
            }
        }

        private bool WriteCaptureReport()
        {
            EntityId[] expectedRendererIds = controller.CaseRendererEntityIds
                .ToArray();
            EntityId expectedRootId = controller.CaseRootEntityId;
            int flashFrameCount = metrics.Count(
                value => value.localizedFlash > 0.001f);
            float maximumWhiteFraction = metrics.Max(
                value => value.whiteFraction);
            float minimumVisibleFraction = metrics.Min(
                value => value.visibleFraction);
            float flashSilhouetteFraction = metrics
                .Where(value => value.localizedFlash > 0.001f)
                .Select(value => value.caseDarkSilhouetteFraction)
                .DefaultIfEmpty(0f)
                .Min();
            float maximumAheadSeparation = metrics.Max(
                value => value.maximumAheadSeparation);
            float maximumScaleDeviation = metrics.Max(value =>
                Vector3.Distance(
                    value.caseRootScale,
                    controller.CaseAuthoredScale));
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
                        previous.caseProjectedBounds.center,
                        current.caseProjectedBounds.center));
                maximumProjectedHeightStep = Mathf.Max(
                    maximumProjectedHeightStep,
                    Mathf.Abs(
                        current.caseProjectedBounds.height
                        - previous.caseProjectedBounds.height));
                maximumRootPositionStep = Mathf.Max(
                    maximumRootPositionStep,
                    Vector3.Distance(
                        previous.caseRootPosition,
                        current.caseRootPosition));
            }

            FrameMetric intact = metrics[18];
            FrameMetric final = metrics[metrics.Count - 1];
            bool caseRootIdentityStable = metrics.All(
                value => value.caseRootEntityId.Equals(expectedRootId));
            bool caseRendererIdentityStable = metrics.All(value =>
                value.caseRendererEntityIds.SequenceEqual(
                    expectedRendererIds));
            bool packGoneByImpactEnd = metrics
                .Where(value =>
                    value.timeSeconds
                    >= PackOpeningGate04R010Profile.ImpactEnd + 0.0001f)
                .All(value => !value.packVisible);
            bool sameCaseVisibleThroughAperture = metrics.Any(value =>
                value.occlusionState
                    == PackOpeningGate04R010Occlusion.AperturePartial.ToString()
                && value.tearProgress >= 0.30f
                && value.caseRootEntityId.Equals(expectedRootId)
                && value.caseProjectedBounds.height > 0.20f);
            bool sameCaseCrossesOccluder = metrics.Any(value =>
                value.occlusionState
                    == PackOpeningGate04R010Occlusion.CrossingOccluder.ToString()
                && value.packVisible
                && value.caseRootEntityId.Equals(expectedRootId));
            float curvature20 = controller.MeasureFreedTailCurvature(0.20f);
            float curvature50 = controller.MeasureFreedTailCurvature(0.50f);
            float curvature80 = controller.MeasureFreedTailCurvature(0.80f);
            float maximumOffset = controller.SharedTearOffsets
                .Max(value => Mathf.Abs(value));
            float maximumAdjacentOffsetDelta = 0f;
            for (
                int index = 1;
                index < controller.SharedTearOffsets.Count;
                index++)
            {
                maximumAdjacentOffsetDelta = Mathf.Max(
                    maximumAdjacentOffsetDelta,
                    Mathf.Abs(
                        controller.SharedTearOffsets[index]
                        - controller.SharedTearOffsets[index - 1]));
            }

            var checks = new Dictionary<string, bool>
            {
                { "realUnityPlayModeCapture", Application.isPlaying },
                { "unityVersionExact", Application.unityVersion == "6000.5.6f1" },
                { "shippingPortrait1206x2622", Width == 1206 && Height == 2622 },
                { "exact60FpsTimeline", FrameCount == 186 && FrameRate == 60 },
                { "singleLocalizedFlashFrame", flashFrameCount == 1 },
                { "noBlankWhiteFrame", maximumWhiteFraction < 0.58f },
                { "flashRetainsDarkHeroSilhouette", flashSilhouetteFraction > 0.16f },
                { "noBlackFrame", minimumVisibleFraction > 0.10f },
                { "caseRootIdentityStableEveryFrame", caseRootIdentityStable },
                { "caseRendererIdentityStableEveryFrame", caseRendererIdentityStable },
                { "caseRootScaleConstantEveryFrame", maximumScaleDeviation < 0.000001f },
                { "caseProjectedCenterContinuous", maximumProjectedCenterStep < 0.060f },
                { "caseProjectedScaleContinuous", maximumProjectedHeightStep < 0.065f },
                { "caseRootPositionContinuous", maximumRootPositionStep < 0.045f },
                { "sameCaseVisibleThroughAperture", sameCaseVisibleThroughAperture },
                { "sameCaseCrossesPackOccluder", sameCaseCrossesOccluder },
                { "packGoneByImpactHandoffEnd", packGoneByImpactEnd },
                { "intactPackHeightTarget", intact.packProjectedBounds.height >= 0.45f
                    && intact.packProjectedBounds.height <= 0.55f },
                { "settledCaseHeightTarget", final.caseProjectedBounds.height >= 0.48f
                    && final.caseProjectedBounds.height <= 0.62f },
                { "settledCaseOpticallyCentered", final.caseProjectedBounds.center.x >= 0.42f
                    && final.caseProjectedBounds.center.x <= 0.58f
                    && final.caseProjectedBounds.center.y >= 0.38f
                    && final.caseProjectedBounds.center.y <= 0.62f },
                { "aheadOfTearFrontRemainsWelded", maximumAheadSeparation < 0.000001f },
                { "tearEdgeLowAmplitude", maximumOffset <=
                    PackOpeningGate04R010Controller.MaximumTearAmplitude + 0.000001f },
                { "tearEdgeHasNoLargeSawTeeth", maximumAdjacentOffsetDelta < 0.0011f },
                { "tailCurvatureChanges", curvature20 > 0.0001f
                    && Mathf.Abs(curvature50 - curvature20) > 0.0001f
                    && Mathf.Abs(curvature80 - curvature50) > 0.0001f },
                { "belowThresholdReboundExact", reboundRestoredExactly },
                { "reduceMotionPreservesCausalOrder",
                    controller.Profile.Evaluate(1.68f, true).Occlusion
                        == PackOpeningGate04R010Occlusion.CrossingOccluder
                    && controller.Profile.Evaluate(1.68f, true)
                        .EnergyRingProgress == 0f
                    && !controller.Profile.Evaluate(1.68f, true)
                        .ImpactParticlesEnabled },
                { "shippingReadyIsFalse", true },
                { "physicalPhoneInstalledIsFalse", true }
            };
            bool passed = checks.All(pair => pair.Value);

            var json = new StringBuilder(1024 * 512);
            json.Append("{\n");
            json.Append("  \"schema\": \"premium-display-case-gate04-r010-unity-capture.v1\",\n");
            json.Append($"  \"status\": \"{(passed ? "pass" : "self-rejected")}\",\n");
            json.Append("  \"source\": \"actual running Unity PlayMode scene and Camera output\",\n");
            json.Append($"  \"unity\": \"{Application.unityVersion}\",\n");
            json.Append("  \"urp\": \"17.5.0\",\n");
            json.Append($"  \"scene\": \"{Escape(scenePath)}\",\n");
            json.Append($"  \"width\": {Width},\n");
            json.Append($"  \"height\": {Height},\n");
            json.Append($"  \"fps\": {FrameRate},\n");
            json.Append($"  \"frames\": {FrameCount},\n");
            json.Append("  \"durationSeconds\": 3.10,\n");
            json.Append("  \"normalSpeedFrames\": \"frames/frame-%04d.png\",\n");
            json.Append(
                $"  \"caseRootEntityId\": \"{Escape(expectedRootId.ToString())}\",\n");
            json.Append("  \"caseRendererEntityIds\": [");
            json.Append(string.Join(
                ",",
                expectedRendererIds.Select(
                    value => $"\"{Escape(value.ToString())}\"")));
            json.Append("],\n");
            json.Append($"  \"flashFrameCount\": {flashFrameCount},\n");
            json.Append($"  \"maximumWhiteFraction\": {Format(maximumWhiteFraction)},\n");
            json.Append($"  \"minimumVisibleFraction\": {Format(minimumVisibleFraction)},\n");
            json.Append($"  \"flashDarkSilhouetteFraction\": {Format(flashSilhouetteFraction)},\n");
            json.Append($"  \"maximumAheadOfFrontSeparationMeters\": {Format(maximumAheadSeparation)},\n");
            json.Append($"  \"maximumCaseScaleDeviation\": {Format(maximumScaleDeviation)},\n");
            json.Append($"  \"maximumProjectedCenterStep\": {Format(maximumProjectedCenterStep)},\n");
            json.Append($"  \"maximumProjectedHeightStep\": {Format(maximumProjectedHeightStep)},\n");
            json.Append($"  \"maximumRootPositionStepMeters\": {Format(maximumRootPositionStep)},\n");
            json.Append($"  \"maximumTearOffsetMeters\": {Format(maximumOffset)},\n");
            json.Append($"  \"maximumAdjacentTearOffsetDeltaMeters\": {Format(maximumAdjacentOffsetDelta)},\n");
            json.Append("  \"tailCurvature\": {\n");
            json.Append($"    \"tear20\": {Format(curvature20)},\n");
            json.Append($"    \"tear50\": {Format(curvature50)},\n");
            json.Append($"    \"tear80\": {Format(curvature80)}\n");
            json.Append("  },\n");
            json.Append("  \"candidateOnly\": true,\n");
            json.Append("  \"shippingRuntimeWired\": false,\n");
            json.Append("  \"nativeUiWired\": false,\n");
            json.Append("  \"shippingReady\": false,\n");
            json.Append("  \"physicalPhoneInstalled\": false,\n");
            json.Append("  \"checks\": {\n");
            json.Append(string.Join(
                ",\n",
                checks.Select(pair =>
                    $"    \"{pair.Key}\": {pair.Value.ToString().ToLowerInvariant()}")));
            json.Append("\n  },\n");
            json.Append("  \"frameMetrics\": [\n");
            json.Append(string.Join(
                ",\n",
                metrics.Select(value => value.ToJson())));
            json.Append("\n  ]\n");
            json.Append("}\n");
            File.WriteAllText(
                Path.Combine(outputDirectory, "unity-capture-report.json"),
                json.ToString());
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
            private FrameMetric(
                int frame,
                float time,
                PackOpeningGate04R010Controller source,
                Rect caseBounds,
                Rect packBounds,
                float tearFrontViewportX,
                float visibleFraction,
                float whiteFraction,
                float darkSilhouetteFraction)
            {
                this.frame = frame;
                timeSeconds = time;
                phase = source.CurrentSample.Phase.ToString();
                occlusionState = source.CurrentSample.Occlusion.ToString();
                tearProgress = source.CurrentSample.TearProgress;
                apertureProgress = source.CurrentSample.ApertureProgress;
                packRetreat = source.CurrentSample.PackRetreat;
                caseTravel = source.CurrentSample.CaseTravel;
                caseRotationDegrees =
                    source.CurrentSample.CaseRotationDegrees;
                localizedFlash = source.CurrentSample.LocalizedFlash;
                energyRingProgress =
                    source.CurrentSample.EnergyRingProgress;
                this.tearFrontViewportX = tearFrontViewportX;
                maximumAheadSeparation =
                    source.MaximumAheadOfFrontSeparation;
                caseRootEntityId = source.CaseRootEntityId;
                caseRendererEntityIds = source.CaseRendererEntityIds
                    .ToArray();
                caseRootPosition = source.CaseMotionRoot.localPosition;
                caseRootScale = source.CaseMotionRoot.localScale;
                caseProjectedBounds = caseBounds;
                packProjectedBounds = packBounds;
                packVisible = source.PackVisible;
                cavityVisible = source.CavityVisible;
                caseActive = source.CaseMotionRoot.gameObject.activeInHierarchy;
                this.visibleFraction = visibleFraction;
                this.whiteFraction = whiteFraction;
                caseDarkSilhouetteFraction = darkSilhouetteFraction;
            }

            public readonly int frame;
            public readonly float timeSeconds;
            public readonly string phase;
            public readonly string occlusionState;
            public readonly float tearProgress;
            public readonly float apertureProgress;
            public readonly float packRetreat;
            public readonly float caseTravel;
            public readonly float caseRotationDegrees;
            public readonly float localizedFlash;
            public readonly float energyRingProgress;
            public readonly float tearFrontViewportX;
            public readonly float maximumAheadSeparation;
            public readonly EntityId caseRootEntityId;
            public readonly EntityId[] caseRendererEntityIds;
            public readonly Vector3 caseRootPosition;
            public readonly Vector3 caseRootScale;
            public readonly Rect caseProjectedBounds;
            public readonly Rect packProjectedBounds;
            public readonly bool packVisible;
            public readonly bool cavityVisible;
            public readonly bool caseActive;
            public readonly float visibleFraction;
            public readonly float whiteFraction;
            public readonly float caseDarkSilhouetteFraction;

            public static FrameMetric Measure(
                int frame,
                float time,
                PackOpeningGate04R010Controller source,
                Rect caseBounds,
                Rect packBounds,
                float tearFrontViewportX,
                IReadOnlyList<Color32> pixels,
                int width,
                int height)
            {
                int sampled = 0;
                int visible = 0;
                int white = 0;
                int caseSampled = 0;
                int darkSilhouette = 0;
                const int stride = 8;
                int minCaseX = Mathf.Clamp(
                    Mathf.FloorToInt(caseBounds.xMin * width),
                    0,
                    width - 1);
                int maxCaseX = Mathf.Clamp(
                    Mathf.CeilToInt(caseBounds.xMax * width),
                    0,
                    width - 1);
                int minCaseY = Mathf.Clamp(
                    Mathf.FloorToInt(caseBounds.yMin * height),
                    0,
                    height - 1);
                int maxCaseY = Mathf.Clamp(
                    Mathf.CeilToInt(caseBounds.yMax * height),
                    0,
                    height - 1);
                for (int y = 0; y < height; y += stride)
                {
                    for (int x = 0; x < width; x += stride)
                    {
                        Color32 pixel = pixels[y * width + x];
                        float r = pixel.r / 255f;
                        float g = pixel.g / 255f;
                        float b = pixel.b / 255f;
                        float luma =
                            r * 0.2126f + g * 0.7152f + b * 0.0722f;
                        sampled += 1;
                        if (luma > 0.018f) visible += 1;
                        if (r > 0.94f && g > 0.94f && b > 0.90f) white += 1;
                        if (
                            x >= minCaseX
                            && x <= maxCaseX
                            && y >= minCaseY
                            && y <= maxCaseY
                        )
                        {
                            caseSampled += 1;
                            if (luma > 0.018f && luma < 0.56f)
                            {
                                darkSilhouette += 1;
                            }
                        }
                    }
                }

                return new FrameMetric(
                    frame,
                    time,
                    source,
                    caseBounds,
                    packBounds,
                    tearFrontViewportX,
                    visible / (float)Mathf.Max(1, sampled),
                    white / (float)Mathf.Max(1, sampled),
                    darkSilhouette / (float)Mathf.Max(1, caseSampled));
            }

            public string ToJson()
            {
                return
                    "    {"
                    + $"\"frame\":{frame},"
                    + $"\"timeSeconds\":{Format(timeSeconds)},"
                    + $"\"phase\":\"{phase}\","
                    + $"\"occlusionState\":\"{occlusionState}\","
                    + $"\"tearProgress\":{Format(tearProgress)},"
                    + $"\"apertureProgress\":{Format(apertureProgress)},"
                    + $"\"packRetreat\":{Format(packRetreat)},"
                    + $"\"caseTravel\":{Format(caseTravel)},"
                    + $"\"caseRotationDegrees\":{Format(caseRotationDegrees)},"
                    + $"\"localizedFlash\":{Format(localizedFlash)},"
                    + $"\"energyRingProgress\":{Format(energyRingProgress)},"
                    + $"\"tearFrontViewportX\":{Format(tearFrontViewportX)},"
                    + $"\"maximumAheadSeparationMeters\":{Format(maximumAheadSeparation)},"
                    + $"\"caseRootEntityId\":\"{Escape(caseRootEntityId.ToString())}\","
                    + "\"caseRendererEntityIds\":["
                    + string.Join(
                        ",",
                        caseRendererEntityIds.Select(
                            value => $"\"{Escape(value.ToString())}\""))
                    + "],"
                    + "\"caseRootPosition\":"
                    + VectorJson(caseRootPosition)
                    + ",\"caseRootScale\":"
                    + VectorJson(caseRootScale)
                    + ",\"caseProjectedBounds\":"
                    + RectJson(caseProjectedBounds)
                    + ",\"packProjectedBounds\":"
                    + RectJson(packProjectedBounds)
                    + $",\"packVisible\":{packVisible.ToString().ToLowerInvariant()}"
                    + $",\"cavityVisible\":{cavityVisible.ToString().ToLowerInvariant()}"
                    + $",\"caseActive\":{caseActive.ToString().ToLowerInvariant()}"
                    + $",\"visibleFraction\":{Format(visibleFraction)}"
                    + $",\"whiteFraction\":{Format(whiteFraction)}"
                    + $",\"caseDarkSilhouetteFraction\":{Format(caseDarkSilhouetteFraction)}"
                    + "}";
            }

            private static string VectorJson(Vector3 value)
            {
                return
                    "{"
                    + $"\"x\":{Format(value.x)},"
                    + $"\"y\":{Format(value.y)},"
                    + $"\"z\":{Format(value.z)}"
                    + "}";
            }

            private static string RectJson(Rect value)
            {
                return
                    "{"
                    + $"\"x\":{Format(value.x)},"
                    + $"\"y\":{Format(value.y)},"
                    + $"\"width\":{Format(value.width)},"
                    + $"\"height\":{Format(value.height)}"
                    + "}";
            }
        }
    }
}
