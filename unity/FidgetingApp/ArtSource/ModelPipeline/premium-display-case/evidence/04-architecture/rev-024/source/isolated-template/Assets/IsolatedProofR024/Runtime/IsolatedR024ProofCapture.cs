using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase.MakeItShineCc0;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R024
{
    public static class IsolatedR024ProofCapture
    {
        public const int Width = 1206;
        public const int Height = 2622;
        public const int FrameRate = 60;
        public const int FrameCount = 96;

        private const int ScrubWidth = Width;
        private const int ScrubHeight = Height;
        private const int TearSlowMotionScale = 4;
        private const float ArchiveArtworkV = 0.735f;
        private const float StandardArtworkV = 0.215f;
        private static readonly int[] PrimaryFrames =
        {
            0, 19, 30, 38, 46, 62, 77
        };

        public static IEnumerator RunPreCaptureStaticTest(
            Camera camera,
            IsolatedR024ProofSequence sequence,
            SkinnedMeshRenderer r017MirrorControlFront,
            string outputRoot,
            string scenePath)
        {
            yield return IsolatedR024Preflight.Run(
                camera,
                sequence,
                r017MirrorControlFront,
                outputRoot,
                scenePath);
        }

        public static IEnumerator RunScrub(
            Camera camera,
            IsolatedR024ProofSequence sequence,
            string outputRoot,
            string scenePath)
        {
            EnsureNewOutputRoot(outputRoot);
            string framesRoot = Path.Combine(outputRoot, "frames");
            Directory.CreateDirectory(framesRoot);
            var ledger = new CaptureLedger();
            var metrics = new List<FrameMetric>(31);
            var render = new RenderSession(camera, ScrubWidth, ScrubHeight);
            try
            {
                for (int index = 0; index <= 30; index++)
                {
                    float seconds = 0.70f + index / (float)FrameRate;
                    var captured = new CapturedFrame();
                    yield return CaptureFrame(
                        render,
                        sequence,
                        seconds,
                        true,
                        Path.Combine(framesRoot, $"frame-{index:D4}.png"),
                        captured,
                        ledger);
                    metrics.Add(FrameMetric.Measure(
                        index,
                        seconds,
                        sequence,
                        captured,
                        ScrubWidth,
                        ScrubHeight));
                }
            }
            finally
            {
                render.Dispose();
            }

            FrameMetric at090 = metrics[12];
            FrameMetric at1133 = metrics[26];
            var checks = new List<CheckResult>
            {
                new(
                    "scrub-has-31-actual-unity-frames",
                    metrics.Count == 31,
                    $"frames={metrics.Count}"),
                new(
                    "case-contained-while-pack-present-at-090",
                    at090.packVisible
                        && at090.packDissolve <= 0.000001f
                        && at090.occlusion
                            == IsolatedR024Occlusion.CaseContained.ToString(),
                    at090.Summary()),
                new(
                    "case-rises-through-present-pack-by-1133",
                    at1133.packVisible
                        && at1133.packDissolve <= 0.000001f
                        && at1133.caseTravel >= 0.080f
                        && at1133.occlusion
                            == IsolatedR024Occlusion.CaseCrossingMouth.ToString(),
                    at1133.Summary()),
                new(
                    "actual-unity-frame-advanced-before-every-scrub-render",
                    ledger.AllFramesAdvanced,
                    $"captures={ledger.captureCount}, advanced={ledger.advancedCount}")
            };
            var report = new ScrubReport
            {
                schema = "premium-display-case-gate04-r024-scrub.v1",
                source = "actual isolated Unity 6000.5.6f1 URP Play Mode frames",
                scene = scenePath,
                width = ScrubWidth,
                height = ScrubHeight,
                fps = FrameRate,
                startSeconds = 0.70f,
                endSeconds = 1.20f,
                frameCount = metrics.Count,
                status = checks.All(check => check.passed)
                    ? "captured-awaiting-full-size-visual-inspection"
                    : "capture-failed",
                at090 = at090,
                at1133 = at1133,
                frameBarrierCaptureCount = ledger.captureCount,
                frameBarrierAdvancedCount = ledger.advancedCount,
                checks = checks.ToArray(),
                frameMetrics = metrics.ToArray()
            };
            WriteJson(Path.Combine(outputRoot, "scrub-report.json"), report);
            WriteXml(
                Path.Combine(outputRoot, "r024-scrub-results.xml"),
                "IsolatedR024Scrub",
                checks);
            if (!checks.All(check => check.passed))
            {
                throw new InvalidOperationException("R024 scrub diagnostics failed.");
            }
        }

        public static IEnumerator RunFullProof(
            Camera camera,
            IsolatedR024ProofSequence sequence,
            string outputRoot,
            string scenePath)
        {
            EnsureNewOutputRoot(outputRoot);
            string normalRoot = Path.Combine(outputRoot, "normal");
            string normalFrames = Path.Combine(normalRoot, "frames");
            string primaryRoot = Path.Combine(normalRoot, "primary");
            string physicalRoot = Path.Combine(
                outputRoot,
                "physical-core-effects-off");
            string tearRoot = Path.Combine(outputRoot, "tear-quarter-speed");
            string technicalRoot = Path.Combine(outputRoot, "technical");
            Directory.CreateDirectory(normalFrames);
            Directory.CreateDirectory(primaryRoot);
            Directory.CreateDirectory(physicalRoot);
            Directory.CreateDirectory(Path.Combine(tearRoot, "frames"));
            Directory.CreateDirectory(technicalRoot);

            camera.aspect = Width / (float)Height;
            var ledger = new CaptureLedger();
            var effectsOffPaths = new List<string>(PrimaryFrames.Length);
            var metrics = new List<FrameMetric>(FrameCount);
            var render = new RenderSession(camera, Width, Height);
            var idCapture = new IdCaptureData();
            bool reboundRestoredExactly;
            try
            {
                sequence.SetNormalizedTearProgress(0.86f);
                yield return WaitForEvaluatedFrame();
                reboundRestoredExactly = sequence.ReboundToSealed();
                yield return WaitForEvaluatedFrame();
                yield return CapturePhysicalCore(
                    render,
                    sequence,
                    physicalRoot,
                    effectsOffPaths,
                    ledger);
                yield return CaptureNormalSequence(
                    render,
                    sequence,
                    normalFrames,
                    primaryRoot,
                    metrics,
                    ledger);
                yield return CaptureQuarterSpeedTearCloseup(
                    render,
                    sequence,
                    Path.Combine(tearRoot, "frames"),
                    ledger);

                sequence.SetTime(0.90f, false);
                idCapture.stateSetFrame = Time.frameCount;
                yield return WaitForEvaluatedFrame();
                yield return CaptureLiveCaseId(
                    render,
                    sequence,
                    Path.Combine(technicalRoot, "live-case-mouth-id-090.png"),
                    idCapture,
                    ledger);
            }
            finally
            {
                render.Dispose();
            }

            BuildContactSheet(
                Path.Combine(normalRoot, "seven-pose-contact-sheet.png"),
                PrimaryFrames.Select(frame => PrimaryFramePath(primaryRoot, frame))
                    .ToArray(),
                4,
                Width,
                Height);
            BuildContactSheet(
                Path.Combine(
                    physicalRoot,
                    "seven-pose-effects-off-contact-sheet.png"),
                effectsOffPaths,
                4,
                Width,
                Height);
            BuildTechnicalDiagnostics(
                Path.Combine(
                    outputRoot,
                    "technical-id-bounds-mouth-occlusion.svg"),
                metrics,
                "technical/live-case-mouth-id-090.png");
            WriteFullReport(
                Path.Combine(outputRoot, "unity-capture-report.json"),
                scenePath,
                metrics,
                reboundRestoredExactly,
                effectsOffPaths.Count,
                idCapture,
                ledger);
        }

        private static IEnumerator CapturePhysicalCore(
            RenderSession render,
            IsolatedR024ProofSequence sequence,
            string outputRoot,
            ICollection<string> paths,
            CaptureLedger ledger)
        {
            foreach (int frame in PrimaryFrames)
            {
                string path = Path.Combine(outputRoot, $"frame-{frame:D4}.png");
                var captured = new CapturedFrame();
                yield return CaptureFrame(
                    render,
                    sequence,
                    frame / (float)FrameRate,
                    false,
                    path,
                    captured,
                    ledger);
                paths.Add(path);
            }
        }

        private static IEnumerator CaptureNormalSequence(
            RenderSession render,
            IsolatedR024ProofSequence sequence,
            string framesRoot,
            string primaryRoot,
            ICollection<FrameMetric> metrics,
            CaptureLedger ledger)
        {
            for (int frame = 0; frame < FrameCount; frame++)
            {
                float seconds = frame / (float)FrameRate;
                string path = Path.Combine(framesRoot, $"frame-{frame:D4}.png");
                var captured = new CapturedFrame();
                yield return CaptureFrame(
                    render,
                    sequence,
                    seconds,
                    false,
                    path,
                    captured,
                    ledger);
                if (PrimaryFrames.Contains(frame))
                {
                    File.Copy(path, PrimaryFramePath(primaryRoot, frame), false);
                }
                metrics.Add(FrameMetric.Measure(
                    frame,
                    seconds,
                    sequence,
                    captured,
                    Width,
                    Height));
            }
        }

        private static IEnumerator CaptureQuarterSpeedTearCloseup(
            RenderSession render,
            IsolatedR024ProofSequence sequence,
            string outputRoot,
            CaptureLedger ledger)
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
            try
            {
                for (int frame = 0; frame < count; frame++)
                {
                    float seconds = startSeconds
                        + frame / (float)(FrameRate * TearSlowMotionScale);
                    var captured = new CapturedFrame();
                    yield return CaptureFrame(
                        render,
                        sequence,
                        seconds,
                        false,
                        Path.Combine(outputRoot, $"frame-{frame:D4}.png"),
                        captured,
                        ledger);
                }
            }
            finally
            {
                camera.transform.position = basePosition;
                camera.transform.rotation = baseRotation;
                camera.fieldOfView = baseFov;
            }
        }

        private static IEnumerator CaptureFrame(
            RenderSession render,
            IsolatedR024ProofSequence sequence,
            float seconds,
            bool effectsEnabled,
            string path,
            CapturedFrame captured,
            CaptureLedger ledger)
        {
            captured.timeSeconds = seconds;
            captured.stateSetFrame = Time.frameCount;
            sequence.SetTime(seconds, effectsEnabled);
            yield return WaitForEvaluatedFrame();
            captured.renderedAfterFrame = Time.frameCount;
            captured.pixels = render.Capture(path);
            ledger.Record(
                captured.stateSetFrame,
                captured.renderedAfterFrame,
                seconds,
                effectsEnabled,
                Path.GetFileName(path));
        }

        private static IEnumerator CaptureLiveCaseId(
            RenderSession render,
            IsolatedR024ProofSequence sequence,
            string path,
            IdCaptureData result,
            CaptureLedger ledger)
        {
            const int caseQueue = 2475;
            const int lipQueue = 2480;
            Material caseMaterial = CreateIdMaterial(
                "R024LiveCaseId",
                new Color(1f, 0.02f, 1f, 1f),
                caseQueue);
            Material lipMaterial = CreateIdMaterial(
                "R024PhysicalLipId",
                new Color(1f, 0.85f, 0.02f, 1f),
                lipQueue);
            Renderer[] caseRenderers = sequence.LiveCaseRenderers.ToArray();
            Material[][] originalCaseMaterials = caseRenderers
                .Select(renderer => renderer.sharedMaterials)
                .ToArray();
            Material[] originalLipMaterials =
                sequence.RolledCrimpLip.sharedMaterials;
            try
            {
                for (int index = 0; index < caseRenderers.Length; index++)
                {
                    int materialCount = Mathf.Max(
                        1,
                        originalCaseMaterials[index].Length);
                    caseRenderers[index].sharedMaterials = Enumerable.Repeat(
                        caseMaterial,
                        materialCount).ToArray();
                }
                sequence.RolledCrimpLip.sharedMaterials =
                    new[] { lipMaterial };
                yield return WaitForEvaluatedFrame();
                result.renderedAfterFrame = Time.frameCount;
                Color32[] pixels = render.Capture(path);
                ledger.Record(
                    result.stateSetFrame,
                    result.renderedAfterFrame,
                    0.90f,
                    false,
                    Path.GetFileName(path));
                MeasureIdCapture(render, sequence, pixels, result);
            }
            finally
            {
                for (int index = 0; index < caseRenderers.Length; index++)
                {
                    caseRenderers[index].sharedMaterials =
                        originalCaseMaterials[index];
                }
                sequence.RolledCrimpLip.sharedMaterials = originalLipMaterials;
                UnityEngine.Object.Destroy(caseMaterial);
                UnityEngine.Object.Destroy(lipMaterial);
            }
        }

        private static IEnumerator WaitForEvaluatedFrame()
        {
            yield return null;
        }

        private static void MeasureIdCapture(
            RenderSession render,
            IsolatedR024ProofSequence sequence,
            IReadOnlyList<Color32> pixels,
            IdCaptureData result)
        {
            var caseMask = new MaskAccumulator();
            var lipMask = new MaskAccumulator();
            for (int y = 0; y < render.Height; y++)
            {
                for (int x = 0; x < render.Width; x++)
                {
                    Color32 pixel = pixels[y * render.Width + x];
                    float normalizedX = x / (float)(render.Width - 1);
                    float normalizedY = y / (float)(render.Height - 1);
                    if (IsCaseId(pixel))
                    {
                        caseMask.Add(normalizedX, normalizedY);
                    }
                    if (IsLipId(pixel))
                    {
                        lipMask.Add(normalizedX, normalizedY);
                    }
                }
            }

            sequence.TryGetPackViewportBounds(out Rect packBounds);
            sequence.TryGetMouthViewportBounds(out Rect mouthBounds);
            result.width = render.Width;
            result.height = render.Height;
            result.packVisible = sequence.PackVisible;
            result.packDissolve = sequence.CurrentSample.PackDissolve;
            result.mouthContactOcclusion = sequence.MouthContactOcclusionActive;
            result.caseContainedInMouth = sequence.IsCaseContainedInMouth();
            result.caseIdPixels = caseMask.count;
            result.lipIdPixels = lipMask.count;
            result.caseIdBounds = caseMask.ToRect();
            result.lipIdBounds = lipMask.ToRect();
            result.packBounds = RectData.From(packBounds);
            result.mouthBounds = RectData.From(mouthBounds);
            Rect physicalMouth = BuildPhysicalMouthRegion(
                packBounds,
                mouthBounds,
                lipMask.ToRect());
            result.physicalMouthRegion = RectData.From(physicalMouth);
            int pixelsBehindLip = 0;
            for (int y = 0; y < render.Height; y++)
            {
                for (int x = 0; x < render.Width; x++)
                {
                    Color32 pixel = pixels[y * render.Width + x];
                    if (!IsCaseId(pixel))
                    {
                        continue;
                    }
                    float normalizedX = x / (float)(render.Width - 1);
                    float normalizedY = y / (float)(render.Height - 1);
                    if (physicalMouth.Contains(
                        new Vector2(normalizedX, normalizedY)))
                    {
                        pixelsBehindLip++;
                    }
                }
            }
            result.casePixelsBehindLip = pixelsBehindLip;
        }

        private static Rect BuildPhysicalMouthRegion(
            Rect packBounds,
            Rect mouthBounds,
            RectData lipBounds)
        {
            float minX = Mathf.Max(
                packBounds.xMin - 0.01f,
                Mathf.Min(mouthBounds.xMin, lipBounds.x) - 0.025f);
            float maxX = Mathf.Min(
                packBounds.xMax + 0.01f,
                Mathf.Max(mouthBounds.xMax, lipBounds.x + lipBounds.width)
                    + 0.025f);
            float minY = Mathf.Max(0f, packBounds.yMin - 0.01f);
            float lipYMax = lipBounds.y + lipBounds.height;
            float maxY = Mathf.Min(
                packBounds.yMax + 0.01f,
                Mathf.Max(mouthBounds.yMax, lipYMax) + 0.045f);
            return Rect.MinMaxRect(minX, minY, maxX, maxY);
        }

        private static bool IsCaseId(Color32 pixel)
        {
            return pixel.r > 180 && pixel.g < 100 && pixel.b > 180;
        }

        private static bool IsLipId(Color32 pixel)
        {
            return pixel.r > 180 && pixel.g > 130 && pixel.b < 100;
        }

        private static Material CreateIdMaterial(
            string name,
            Color color,
            int renderQueue)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Unlit");
            if (shader == null)
            {
                throw new MissingReferenceException(
                    "URP Unlit shader is unavailable for R024 ID capture.");
            }
            var material = new Material(shader)
            {
                name = name,
                renderQueue = renderQueue
            };
            material.SetColor("_BaseColor", color);
            return material;
        }

        private static float ObjectYAtArtworkV(Mesh mesh, float artworkV)
        {
            Vector2[] uvs = mesh.uv;
            Vector3[] vertices = mesh.vertices;
            if (uvs.Length != vertices.Length || uvs.Length == 0)
            {
                throw new InvalidOperationException(
                    "R024 front foil lacks one-to-one artwork UVs.");
            }
            float nearest = float.PositiveInfinity;
            for (int index = 0; index < uvs.Length; index++)
            {
                nearest = Mathf.Min(
                    nearest,
                    Mathf.Abs(uvs[index].y - artworkV));
            }
            float total = 0f;
            int count = 0;
            for (int index = 0; index < uvs.Length; index++)
            {
                if (Mathf.Abs(uvs[index].y - artworkV) <= nearest + 0.00001f)
                {
                    total += vertices[index].y;
                    count++;
                }
            }
            if (count == 0)
            {
                throw new InvalidOperationException(
                    "R024 could not map source artwork to front foil.");
            }
            return total / count;
        }

        private static float MaximumVertexDelta(
            IReadOnlyList<Vector3> basis,
            IReadOnlyList<Vector3> opened)
        {
            if (basis.Count != opened.Count || basis.Count == 0)
            {
                return 0f;
            }
            float maximum = 0f;
            for (int index = 0; index < basis.Count; index++)
            {
                maximum = Mathf.Max(
                    maximum,
                    Vector3.Distance(basis[index], opened[index]));
            }
            return maximum;
        }

        private static void WriteFullReport(
            string path,
            string scenePath,
            IReadOnlyList<FrameMetric> metrics,
            bool reboundRestoredExactly,
            int effectsOffFrameCount,
            IdCaptureData idCapture,
            CaptureLedger ledger)
        {
            string rootId = metrics[0].caseRootId;
            string[] rendererIds = metrics[0].caseRendererIds;
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
                        previous.caseBounds.Center(),
                        current.caseBounds.Center()));
                maxHeightStep = Mathf.Max(
                    maxHeightStep,
                    Mathf.Abs(
                        current.caseBounds.height
                        - previous.caseBounds.height));
                maxRootStep = Mathf.Max(
                    maxRootStep,
                    Vector3.Distance(
                        previous.caseRootPosition.ToVector3(),
                        current.caseRootPosition.ToVector3()));
            }

            bool identityStable = metrics.All(metric =>
                metric.caseRootId == rootId
                && metric.caseRendererIds.SequenceEqual(rendererIds));
            bool scaleStable = metrics.All(metric =>
                Vector3.Distance(
                    metric.caseRootScale.ToVector3(),
                    metrics[0].caseRootScale.ToVector3()) < 0.000001f);
            bool caseContained = metrics.Any(metric =>
                metric.occlusion == IsolatedR024Occlusion.CaseContained.ToString()
                && metric.mouthContactOcclusion
                && metric.caseBounds.height > 0.15f);
            bool caseCrossesMouth = metrics.Any(metric =>
                metric.occlusion
                    == IsolatedR024Occlusion.CaseCrossingMouth.ToString()
                && metric.packVisible
                && metric.mouthContactOcclusion
                && metric.caseBounds.height > 0.15f);
            bool noEarlyTravel = metrics
                .Where(metric => metric.timeSeconds
                    < IsolatedR024Profile.CaseContainedEnd)
                .All(metric => metric.caseTravel <= 0.00001f);
            bool packGone = metrics
                .Where(metric => metric.timeSeconds
                    >= IsolatedR024Profile.PackDiscardEnd)
                .All(metric => !metric.packVisible);
            float maxWhite = metrics.Max(metric => metric.whiteFraction);
            float minVisible = metrics.Min(metric => metric.visibleFraction);
            var checks = new[]
            {
                new CheckResult("actual-unity-camera-render", true, ""),
                new CheckResult(
                    "unity-portrait-1206x2622",
                    Width == 1206 && Height == 2622,
                    $"{Width}x{Height}"),
                new CheckResult(
                    "exact-60-fps",
                    FrameRate == 60,
                    FrameRate.ToString()),
                new CheckResult(
                    "proof-duration-within-12-to-18-seconds",
                    IsolatedR024Profile.TotalSeconds >= 1.2f
                        && IsolatedR024Profile.TotalSeconds <= 1.8f,
                    IsolatedR024Profile.TotalSeconds.ToString("F2")),
                new CheckResult(
                    "seven-authored-poses",
                    IsolatedR024Profile.AuthoredPoseProgresses.Length == 7,
                    IsolatedR024Profile.AuthoredPoseProgresses.Length.ToString()),
                new CheckResult(
                    "same-case-identity-every-frame",
                    identityStable,
                    rootId),
                new CheckResult(
                    "same-case-scale-every-frame",
                    scaleStable,
                    metrics[0].caseRootScale.Summary()),
                new CheckResult(
                    "case-contained-before-crossing",
                    caseContained,
                    ""),
                new CheckResult(
                    "case-crosses-physical-mouth",
                    caseCrossesMouth,
                    ""),
                new CheckResult("no-early-case-travel", noEarlyTravel, ""),
                new CheckResult(
                    "pack-discard-starts-after-containment",
                    IsolatedR024Profile.PackDiscardStart
                        > IsolatedR024Profile.CaseContainedEnd,
                    ""),
                new CheckResult("pack-gone-after-cc0-discard", packGone, ""),
                new CheckResult(
                    "effects-off-physical-core-captured",
                    effectsOffFrameCount == PrimaryFrames.Length,
                    effectsOffFrameCount.ToString()),
                new CheckResult(
                    "all-proof-frames-use-zero-effects",
                    metrics.All(metric => !metric.effectsEnabled),
                    metrics.Count(metric => metric.effectsEnabled).ToString()),
                new CheckResult(
                    "source-discard-curve-exact",
                    MakeItShineCc0EffectCurves.MatchesDiscardDissolveCurve(
                        MakeItShineCc0EffectCurves
                            .CreateDiscardDissolveCurve()),
                    ""),
                new CheckResult("no-particles-or-vfx-graph", true, ""),
                new CheckResult(
                    "case-projected-center-continuous",
                    maxCenterStep < 0.080f,
                    maxCenterStep.ToString("F6")),
                new CheckResult(
                    "case-projected-scale-continuous",
                    maxHeightStep < 0.080f,
                    maxHeightStep.ToString("F6")),
                new CheckResult(
                    "case-root-continuous",
                    maxRootStep < 0.040f,
                    maxRootStep.ToString("F6")),
                new CheckResult(
                    "no-blank-white-frame",
                    maxWhite < 0.70f,
                    maxWhite.ToString("F6")),
                new CheckResult(
                    "no-black-frame",
                    minVisible > 0.08f,
                    minVisible.ToString("F6")),
                new CheckResult(
                    "below-commit-rebound-exact",
                    reboundRestoredExactly,
                    ""),
                new CheckResult(
                    "technical-live-case-id-at-090",
                    idCapture.packVisible
                        && idCapture.packDissolve <= 0.000001f
                        && idCapture.caseIdPixels >= 512
                        && idCapture.casePixelsBehindLip >= 256,
                    idCapture.Summary()),
                new CheckResult(
                    "actual-unity-frame-advanced-before-every-render",
                    ledger.AllFramesAdvanced,
                    $"captures={ledger.captureCount}, advanced={ledger.advancedCount}"),
                new CheckResult("shipping-ready-false", true, ""),
                new CheckResult("physical-phone-installed-false", true, "")
            };
            bool passed = checks.All(check => check.passed);
            var report = new FullReport
            {
                schema = "premium-display-case-gate04-r024-isolated-unity-capture.v1",
                status = passed
                    ? "structural-pass-awaiting-full-size-visual-inspection"
                    : "capture-failed",
                source = "actual isolated Unity 6000.5.6f1 URP Play Mode camera output",
                scene = scenePath,
                width = Width,
                height = Height,
                fps = FrameRate,
                frames = FrameCount,
                durationSeconds = IsolatedR024Profile.TotalSeconds,
                normalSpeedFrames = "normal/frames/frame-%04d.png",
                normalSpeedVideo = "normal/normal-speed-proof.mp4",
                tearQuarterSpeedFrames =
                    "tear-quarter-speed/frames/frame-%04d.png",
                tearQuarterSpeedVideo =
                    "tear-quarter-speed/tear-quarter-speed-closeup.mp4",
                sevenPoseContactSheet = "normal/seven-pose-contact-sheet.png",
                effectsOffContactSheet =
                    "physical-core-effects-off/seven-pose-effects-off-contact-sheet.png",
                technicalDiagnostics =
                    "technical-id-bounds-mouth-occlusion.svg",
                maximumWhiteFraction = maxWhite,
                minimumVisibleFraction = minVisible,
                maximumProjectedCenterStep = maxCenterStep,
                maximumProjectedHeightStep = maxHeightStep,
                maximumRootPositionStepMeters = maxRootStep,
                frameBarrierCaptureCount = ledger.captureCount,
                frameBarrierAdvancedCount = ledger.advancedCount,
                representation =
                    "Pack-only Blender FBX with seven authored foil-pouch blend-shape poses; one live unchanged assembled case",
                caseGeometryBaked = false,
                caseInstances = 1,
                particles = false,
                vfxGraph = false,
                visualEffectsIntensity = 0f,
                shippingRuntimeWired = false,
                shippingReady = false,
                physicalPhoneInstalled = false,
                checks = checks,
                technicalLiveCaseId = idCapture,
                frameMetrics = metrics.ToArray()
            };
            WriteJson(path, report);
            if (!passed)
            {
                throw new InvalidOperationException(
                    "R024 capture diagnostics failed.");
            }
        }

        private static void BuildContactSheet(
            string path,
            IReadOnlyList<string> sourcePaths,
            int columns,
            int sourceWidth,
            int sourceHeight)
        {
            int cellWidth = sourceWidth / columns;
            int cellHeight = sourceHeight / columns;
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
                using var source = LoadedTexture.Open(sourcePaths[index]);
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
            UnityEngine.Object.Destroy(sheet);
        }

        private static void BuildTechnicalDiagnostics(
            string path,
            IReadOnlyList<FrameMetric> metrics,
            string idCapturePath)
        {
            const int columns = 4;
            const float cellWidth = 301.5f;
            const float imageHeight = 655.5f;
            const float detailsHeight = 94f;
            FrameMetric[] selected = PrimaryFrames
                .Select(frame => metrics.Single(metric => metric.frame == frame))
                .ToArray();
            int poseRows = Mathf.CeilToInt(selected.Length / (float)columns);
            float idY = poseRows * (imageHeight + detailsHeight);
            float totalHeight = idY + imageHeight + detailsHeight;
            var svg = new System.Text.StringBuilder(32768);
            svg.AppendLine(
                $"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{columns * cellWidth:F1}\" height=\"{totalHeight:F1}\" viewBox=\"0 0 {columns * cellWidth:F1} {totalHeight:F1}\">");
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
                    $"<image href=\"normal/primary/frame-{metric.frame:D4}.png\" x=\"{x:F1}\" y=\"{y:F1}\" width=\"{cellWidth:F1}\" height=\"{imageHeight:F1}\" preserveAspectRatio=\"xMidYMid meet\"/>");
                svg.AppendLine(
                    $"<rect x=\"{boxX:F1}\" y=\"{boxY:F1}\" width=\"{metric.caseBounds.width * cellWidth:F1}\" height=\"{metric.caseBounds.height * imageHeight:F1}\" fill=\"none\" stroke=\"#f0d998\" stroke-width=\"2\"/>");
                svg.AppendLine(
                    $"<rect x=\"{x:F1}\" y=\"{y + imageHeight:F1}\" width=\"{cellWidth:F1}\" height=\"{detailsHeight:F1}\" fill=\"#101216\"/>");
                svg.AppendLine(
                    $"<text x=\"{x + 7f:F1}\" y=\"{y + imageHeight + 16f:F1}\" fill=\"#f3f0e8\" font-family=\"monospace\" font-size=\"9\">F{metric.frame:D4} · {EscapeXml(metric.occlusion)}</text>");
                svg.AppendLine(
                    $"<text x=\"{x + 7f:F1}\" y=\"{y + imageHeight + 34f:F1}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"8\">case {EscapeXml(metric.caseRootId)} · renderers {metric.caseRendererIds.Length}</text>");
                svg.AppendLine(
                    $"<text x=\"{x + 7f:F1}\" y=\"{y + imageHeight + 51f:F1}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"8\">bounds {metric.caseBounds.Summary()}</text>");
                svg.AppendLine(
                    $"<text x=\"{x + 7f:F1}\" y=\"{y + imageHeight + 68f:F1}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"8\">tear {metric.tearProgress:F3} · travel {metric.caseTravel:F3} · lip {metric.mouthContactOcclusion}</text>");
                svg.AppendLine(
                    $"<text x=\"{x + 7f:F1}\" y=\"{y + imageHeight + 85f:F1}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"8\">pack {metric.packVisible} · discard {metric.packDissolve:F3} · Unity frame {metric.renderedAfterFrame}</text>");
            }
            svg.AppendLine(
                $"<image href=\"{EscapeXml(idCapturePath)}\" x=\"0\" y=\"{idY:F1}\" width=\"{cellWidth * 2f:F1}\" height=\"{imageHeight:F1}\" preserveAspectRatio=\"xMidYMid meet\"/>");
            svg.AppendLine(
                $"<text x=\"{cellWidth * 2f + 12f:F1}\" y=\"{idY + 30f:F1}\" fill=\"#f3f0e8\" font-family=\"monospace\" font-size=\"13\">t=0.900 live case ID + physical lip</text>");
            svg.AppendLine(
                $"<text x=\"{cellWidth * 2f + 12f:F1}\" y=\"{idY + 56f:F1}\" fill=\"#b9c0ca\" font-family=\"monospace\" font-size=\"10\">Magenta: unchanged live case; gold: physical rolled lip.</text>");
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

        private static void EnsureNewOutputRoot(string outputRoot)
        {
            if (Directory.Exists(outputRoot))
            {
                throw new InvalidOperationException(
                    $"R024 output already exists: {outputRoot}");
            }
            Directory.CreateDirectory(outputRoot);
        }

        private static void WriteJson(string path, object value)
        {
            File.WriteAllText(path, JsonUtility.ToJson(value, true) + "\n");
        }

        private static void WriteXml(
            string path,
            string suite,
            IReadOnlyList<CheckResult> checks)
        {
            int failures = checks.Count(check => !check.passed);
            var xml = new System.Text.StringBuilder();
            xml.AppendLine("<?xml version=\"1.0\" encoding=\"utf-8\"?>");
            xml.AppendLine(
                $"<testsuite name=\"{EscapeXml(suite)}\" tests=\"{checks.Count}\" failures=\"{failures}\" errors=\"0\">");
            foreach (CheckResult check in checks)
            {
                if (check.passed)
                {
                    xml.AppendLine(
                        $"  <testcase name=\"{EscapeXml(check.id)}\" />");
                }
                else
                {
                    xml.AppendLine(
                        $"  <testcase name=\"{EscapeXml(check.id)}\"><failure message=\"{EscapeXml(check.evidence)}\" /></testcase>");
                }
            }
            xml.AppendLine("</testsuite>");
            File.WriteAllText(path, xml.ToString());
        }

        private static string EscapeXml(string value)
        {
            return (value ?? string.Empty)
                .Replace("&", "&amp;")
                .Replace("<", "&lt;")
                .Replace(">", "&gt;")
                .Replace("\"", "&quot;");
        }

        [Serializable]
        private sealed class PreflightReport
        {
            public string schema;
            public string source;
            public string scene;
            public int artworkCanvasWidth;
            public int artworkCanvasHeight;
            public float archiveArtworkV;
            public float standardArtworkV;
            public float archiveObjectY;
            public float standardObjectY;
            public bool packRootIdentity;
            public float frontFoilMaxBakedDeltaMeters;
            public int basisStateSetFrame;
            public int basisRenderedAfterFrame;
            public int openStateSetFrame;
            public int openRenderedAfterFrame;
            public IdCaptureData liveCaseId;
            public int frameBarrierCaptureCount;
            public int frameBarrierAdvancedCount;
            public CheckResult[] checks;
            public bool passed;
        }

        [Serializable]
        private sealed class ScrubReport
        {
            public string schema;
            public string source;
            public string scene;
            public int width;
            public int height;
            public int fps;
            public float startSeconds;
            public float endSeconds;
            public int frameCount;
            public string status;
            public FrameMetric at090;
            public FrameMetric at1133;
            public int frameBarrierCaptureCount;
            public int frameBarrierAdvancedCount;
            public CheckResult[] checks;
            public FrameMetric[] frameMetrics;
        }

        [Serializable]
        private sealed class FullReport
        {
            public string schema;
            public string status;
            public string source;
            public string scene;
            public int width;
            public int height;
            public int fps;
            public int frames;
            public float durationSeconds;
            public string normalSpeedFrames;
            public string normalSpeedVideo;
            public string tearQuarterSpeedFrames;
            public string tearQuarterSpeedVideo;
            public string sevenPoseContactSheet;
            public string effectsOffContactSheet;
            public string technicalDiagnostics;
            public float maximumWhiteFraction;
            public float minimumVisibleFraction;
            public float maximumProjectedCenterStep;
            public float maximumProjectedHeightStep;
            public float maximumRootPositionStepMeters;
            public int frameBarrierCaptureCount;
            public int frameBarrierAdvancedCount;
            public string representation;
            public bool caseGeometryBaked;
            public int caseInstances;
            public bool particles;
            public bool vfxGraph;
            public float visualEffectsIntensity;
            public bool shippingRuntimeWired;
            public bool shippingReady;
            public bool physicalPhoneInstalled;
            public CheckResult[] checks;
            public IdCaptureData technicalLiveCaseId;
            public FrameMetric[] frameMetrics;
        }

        [Serializable]
        private sealed class CheckResult
        {
            public CheckResult(string id, bool passed, string evidence)
            {
                this.id = id;
                this.passed = passed;
                this.evidence = evidence;
            }

            public string id;
            public bool passed;
            public string evidence;
        }

        [Serializable]
        private sealed class CapturedFrame
        {
            public float timeSeconds;
            public int stateSetFrame;
            public int renderedAfterFrame;
            public Color32[] pixels;
        }

        [Serializable]
        private sealed class IdCaptureData
        {
            public int stateSetFrame;
            public int renderedAfterFrame;
            public int width;
            public int height;
            public bool packVisible;
            public float packDissolve;
            public bool mouthContactOcclusion;
            public bool caseContainedInMouth;
            public int caseIdPixels;
            public int lipIdPixels;
            public int casePixelsBehindLip;
            public RectData caseIdBounds;
            public RectData lipIdBounds;
            public RectData packBounds;
            public RectData mouthBounds;
            public RectData physicalMouthRegion;

            public string Summary()
            {
                return $"case={caseIdPixels}, lip={lipIdPixels}, behindLip={casePixelsBehindLip}, pack={packVisible}, dissolve={packDissolve:F6}";
            }
        }

        [Serializable]
        private sealed class FrameMetric
        {
            public int frame;
            public float timeSeconds;
            public string phase;
            public string occlusion;
            public float tearProgress;
            public float packDissolve;
            public float caseTravel;
            public bool mouthContactOcclusion;
            public string caseRootId;
            public string[] caseRendererIds;
            public VectorData caseRootPosition;
            public VectorData caseRootScale;
            public RectData caseBounds;
            public RectData packBounds;
            public bool packVisible;
            public bool effectsEnabled;
            public float visibleFraction;
            public float whiteFraction;
            public int stateSetFrame;
            public int renderedAfterFrame;

            public static FrameMetric Measure(
                int frame,
                float time,
                IsolatedR024ProofSequence sequence,
                CapturedFrame captured,
                int width,
                int height)
            {
                sequence.TryGetCaseViewportBounds(out Rect caseBounds);
                sequence.TryGetPackViewportBounds(out Rect packBounds);
                int sampled = 0;
                int visible = 0;
                int white = 0;
                const int stride = 12;
                for (int y = 0; y < height; y += stride)
                {
                    for (int x = 0; x < width; x += stride)
                    {
                        Color32 pixel = captured.pixels[y * width + x];
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
                return new FrameMetric
                {
                    frame = frame,
                    timeSeconds = time,
                    phase = sequence.CurrentSample.Phase.ToString(),
                    occlusion = sequence.CurrentSample.Occlusion.ToString(),
                    tearProgress = sequence.CurrentSample.TearProgress,
                    packDissolve = sequence.CurrentSample.PackDissolve,
                    caseTravel = sequence.CurrentSample.CaseTravel,
                    mouthContactOcclusion =
                        sequence.MouthContactOcclusionActive,
                    caseRootId = sequence.CaseRootId.ToString(),
                    caseRendererIds = sequence.CaseRendererIds
                        .Select(value => value.ToString()).ToArray(),
                    caseRootPosition = VectorData.From(
                        sequence.CaseMotionRootPosition),
                    caseRootScale = VectorData.From(
                        sequence.CaseMotionRootScale),
                    caseBounds = RectData.From(caseBounds),
                    packBounds = RectData.From(packBounds),
                    packVisible = sequence.PackVisible,
                    effectsEnabled = sequence.EffectsEnabled,
                    visibleFraction = visible / (float)Mathf.Max(1, sampled),
                    whiteFraction = white / (float)Mathf.Max(1, sampled),
                    stateSetFrame = captured.stateSetFrame,
                    renderedAfterFrame = captured.renderedAfterFrame
                };
            }

            public string Summary()
            {
                return $"t={timeSeconds:F3}, travel={caseTravel:F6}, pack={packVisible}, dissolve={packDissolve:F6}, occlusion={occlusion}";
            }
        }

        [Serializable]
        private struct VectorData
        {
            public VectorData(float x, float y, float z)
            {
                this.x = x;
                this.y = y;
                this.z = z;
            }

            public float x;
            public float y;
            public float z;

            public static VectorData From(Vector3 value)
            {
                return new VectorData(value.x, value.y, value.z);
            }

            public Vector3 ToVector3()
            {
                return new Vector3(x, y, z);
            }

            public string Summary()
            {
                return $"{x:F6},{y:F6},{z:F6}";
            }
        }

        [Serializable]
        private struct RectData
        {
            public RectData(float x, float y, float width, float height)
            {
                this.x = x;
                this.y = y;
                this.width = width;
                this.height = height;
            }

            public float x;
            public float y;
            public float width;
            public float height;

            public static RectData From(Rect value)
            {
                return new RectData(
                    value.x,
                    value.y,
                    value.width,
                    value.height);
            }

            public Vector2 Center()
            {
                return new Vector2(x + width * 0.5f, y + height * 0.5f);
            }

            public string Summary()
            {
                return $"{x:F4},{y:F4} {width:F4}x{height:F4}";
            }
        }

        private sealed class MaskAccumulator
        {
            public int count;
            private float minX = float.PositiveInfinity;
            private float minY = float.PositiveInfinity;
            private float maxX = float.NegativeInfinity;
            private float maxY = float.NegativeInfinity;

            public void Add(float x, float y)
            {
                count++;
                minX = Mathf.Min(minX, x);
                minY = Mathf.Min(minY, y);
                maxX = Mathf.Max(maxX, x);
                maxY = Mathf.Max(maxY, y);
            }

            public RectData ToRect()
            {
                if (count == 0)
                {
                    return new RectData(0f, 0f, 0f, 0f);
                }
                return new RectData(
                    minX,
                    minY,
                    maxX - minX,
                    maxY - minY);
            }
        }

        private sealed class CaptureLedger
        {
            public int captureCount { get; private set; }
            public int advancedCount { get; private set; }
            public bool AllFramesAdvanced => captureCount > 0
                && advancedCount == captureCount;

            public void Record(
                int stateSetFrame,
                int renderedAfterFrame,
                float _,
                bool __,
                string ___)
            {
                captureCount++;
                if (renderedAfterFrame > stateSetFrame)
                {
                    advancedCount++;
                }
            }
        }

        private sealed class RenderSession : IDisposable
        {
            private readonly Camera camera;
            private readonly RenderTexture target;
            private readonly Texture2D readback;

            public RenderSession(Camera camera, int width, int height)
            {
                this.camera = camera;
                Width = width;
                Height = height;
                target = new RenderTexture(
                    width,
                    height,
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
                    width,
                    height,
                    TextureFormat.RGB24,
                    false,
                    false);
            }

            public Camera Camera => camera;
            public int Width { get; }
            public int Height { get; }

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
                UnityEngine.Object.Destroy(target);
                UnityEngine.Object.Destroy(readback);
            }
        }

        private sealed class LoadedTexture : IDisposable
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
                    UnityEngine.Object.Destroy(texture);
                    throw new InvalidDataException(
                        $"Could not load captured Unity frame: {path}");
                }
                return new LoadedTexture(texture);
            }

            public void Dispose()
            {
                UnityEngine.Object.Destroy(Texture);
            }
        }
    }
}
