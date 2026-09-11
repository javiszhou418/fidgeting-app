using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R020
{
    public static class IsolatedR020Preflight
    {
        private const int Width = 1206;
        private const int Height = 2622;
        private const float ArchiveArtworkV = 0.735f;
        private const float ArchiveTitleBandMinV = 0.710f;
        private const float ArchiveTitleBandMaxV = 0.770f;
        private const float StandardArtworkV = 0.215f;
        private const float PhysicalTopArtworkV = 0.815f;
        private const float BottomCrimpArtworkV = 0.060f;
        private const float MinimumTopDropMeters = 0.005f;
        private const int MinimumMouthCasePixels = 10000;
        private const int MinimumOccludedCasePixels = 4054;
        private const int MinimumContiguousOcclusionPixels = 4054;
        private const int MinimumVisibleLinerPixels = 384;
        private const int MinimumVisibleCavityPixels = 512;
        private const int MinimumContiguousCavityPixels = 384;
        private const float MinimumLinerCavityLuminanceDelta = 0.050f;
        private const float MinimumLinerOuterLuminanceDelta = 0.035f;
        private const float MinimumCavityBackgroundLuminanceDelta = 0.015f;
        private const float MinimumCaseBoundsWidth = 0.060f;
        private const float MinimumCaseBoundsHeight = 0.035f;
        private const float MinimumCaseBoundaryContrast = 0.040f;
        private static readonly float[] TearFrontProgressSamples =
        {
            0.35f, 0.70f, 0.90f
        };

        public static IEnumerator Run(
            Camera camera,
            IsolatedR020ProofSequence sequence,
            SkinnedMeshRenderer r017MirrorControlFront,
            string outputRoot,
            string scenePath)
        {
            if (Directory.Exists(outputRoot))
            {
                throw new InvalidOperationException(
                    $"R020 preflight output already exists: {outputRoot}");
            }
            Directory.CreateDirectory(outputRoot);
            Directory.CreateDirectory(Path.Combine(outputRoot, "diagnostics"));

            var report = new Report
            {
                schema = "premium-display-case-gate04-r020-preflight.v1",
                source = "actual isolated Unity 6000.5.6f1 URP 17.5 Play Mode frames",
                scene = scenePath,
                width = Width,
                height = Height,
                visualEffectsIntensity = 0f
            };
            var checks = new List<Check>();
            var ledger = new FrameLedger();
            var sealedMesh = new Mesh { name = "R020_Preflight_Sealed" };
            var formedMesh = new Mesh { name = "R020_Preflight_Formed" };
            var containedMesh = new Mesh { name = "R020_Preflight_Contained" };
            var render = new RenderSession(camera);
            try
            {
                report.orientationCalibration =
                    new IsolatedR020OrientationCalibration.Result();
                yield return IsolatedR020OrientationCalibration.Capture(
                    sequence,
                    r017MirrorControlFront,
                    outputRoot,
                    report.orientationCalibration);

                var sealedFrame = new FrameCapture();
                yield return CaptureFrame(
                    render,
                    sequence,
                    0f,
                    Path.Combine(outputRoot, "sealed-state.png"),
                    sealedFrame,
                    ledger);
                sequence.BakeFrontFoil(sealedMesh);
                report.sealedState = MeasureSealed(sequence, sealedMesh);
            report.sealedRender = new RenderedCrimpReport();
            yield return CaptureRenderedCrimpAndTitle(
                render,
                sequence,
                outputRoot,
                report.sealedRender,
                ledger);
                report.tearFrontDirection = new TearFrontDirectionReport();
                yield return CaptureTearFrontDirection(
                    render,
                    sequence,
                    outputRoot,
                    report.tearFrontDirection,
                    ledger);

                var tearFrontFrame = new FrameCapture();
                yield return CaptureFrame(
                    render,
                    sequence,
                    0.50f,
                    Path.Combine(outputRoot, "tear-front-050.png"),
                    tearFrontFrame,
                    ledger);
                var formedFrame = new FrameCapture();
                yield return CaptureFrame(
                    render,
                    sequence,
                    0.70f,
                    Path.Combine(outputRoot, "formed-mouth-070.png"),
                    formedFrame,
                    ledger);
                sequence.BakeFrontFoil(formedMesh);
            report.formedMouth = MeasureMouth(
                    sequence,
                    sealedMesh,
                formedMesh,
                0.70f);
            report.formedMouthMaterials = new MouthMaterialReport();
            yield return CaptureMouthMaterialSeparation(
                render,
                sequence,
                formedFrame.pixels,
                report.formedMouth.upperMouthRegion.ToRect(),
                0.70f,
                outputRoot,
                report.formedMouthMaterials,
                ledger);

                var containedFrame = new FrameCapture();
                yield return CaptureFrame(
                    render,
                    sequence,
                    0.90f,
                    Path.Combine(outputRoot, "case-contained-090.png"),
                    containedFrame,
                    ledger);
            sequence.BakeFrontFoil(containedMesh);
            report.containedMouth = MeasureMouth(
                sequence,
                sealedMesh,
                containedMesh,
                0.90f);
            report.containedMouthMaterials = new MouthMaterialReport();
            yield return CaptureMouthMaterialSeparation(
                render,
                sequence,
                containedFrame.pixels,
                report.containedMouth.upperMouthRegion.ToRect(),
                0.90f,
                outputRoot,
                report.containedMouthMaterials,
                ledger);
                report.primaryStaticSheet = "primary-static-sheet.png";
                BuildPrimaryStaticSheet(
                    Path.Combine(outputRoot, report.primaryStaticSheet),
                    sealedFrame.pixels,
                    tearFrontFrame.pixels,
                    formedFrame.pixels,
                    containedFrame.pixels);
                report.caseContainment = new CaseContainmentReport
                {
                    packVisible = sequence.PackVisible,
                    packDissolve = sequence.CurrentSample.PackDissolve,
                    caseRootId = sequence.CaseRootId.ToString(),
                    caseRendererIds = sequence.CaseRendererIds
                        .Select(item => item.ToString())
                        .ToArray(),
                    upperMouthRegion = RectData.From(
                        report.containedMouth.upperMouthRegion.ToRect())
                };
                report.caseLegibility = new CaseLegibilityReport();
                yield return CaptureCaseOcclusion(
                    render,
                    sequence,
                    report.caseContainment.upperMouthRegion.ToRect(),
                    containedFrame.pixels,
                    outputRoot,
                    report.caseContainment,
                    report.caseLegibility,
                    ledger);

                report.frameBarrierCaptureCount = ledger.captureCount;
                report.frameBarrierAdvancedCount = ledger.advancedCount;
                report.visualEffectsIntensity = CurrentEffectIntensity(sequence);

                checks.Add(new Check(
                    "r017-mirror-regression-is-observed",
                    report.orientationCalibration.r017MirrorRegressionObserved,
                    "The immutable R017 control must select horizontal-flip."));
                checks.Add(new Check(
                    "r020-artwork-identity-wins-calibration",
                    report.orientationCalibration.r020.identityWins,
                    $"margin={report.orientationCalibration.r020.identityMargin:F6}"));
                checks.Add(new Check(
                    "front-winding-faces-calibration-camera",
                    report.orientationCalibration.r020.frontFaceCameraFacing,
                    "R020 front material rendered with Cull Back."));
                checks.Add(new Check(
                    "sealed-artwork-maps-archive-above-standard",
                    report.sealedState.archiveY
                        > report.sealedState.standardY + 0.10f,
                    report.sealedState.Summary()));
                checks.Add(new Check(
                    "sealed-top-crimp-rendered-above-fidget-archive",
                    report.sealedRender.topCrimpPixels >= 64
                        && report.sealedRender.titleBandPixels >= 64
                        && report.sealedRender.topCrimpLowestViewportY
                            > report.sealedRender.archiveTitleTopViewportY,
                    report.sealedRender.Summary()));
                checks.Add(new Check(
                    "sealed-bottom-crimp-is-below-standard",
                    report.sealedState.bottomCrimpY
                        < report.sealedState.standardY,
                    report.sealedState.Summary()));
                checks.Add(new Check(
                    "tear-front-opens-from-screen-right",
                    report.tearFrontDirection.passed,
                    report.tearFrontDirection.Summary()));
                checks.Add(new Check(
                    "formed-mouth-bounds-stay-in-upper-third",
                    report.formedMouth.allMouthBoundsInUpperThird,
                    report.formedMouth.Summary()));
                checks.Add(new Check(
                    "contained-mouth-bounds-stay-in-upper-third",
                    report.containedMouth.allMouthBoundsInUpperThird,
                    report.containedMouth.Summary()));
                checks.Add(new Check(
                    "formed-mouth-liner-and-cavity-separate",
                    report.formedMouthMaterials.passed,
                    report.formedMouthMaterials.Summary()));
                checks.Add(new Check(
                    "contained-mouth-liner-and-cavity-separate",
                    report.containedMouthMaterials.passed,
                    report.containedMouthMaterials.Summary()));
                checks.Add(new Check(
                    "physical-top-front-edge-moves-downward",
                    report.formedMouth.frontTopDropMeters >= MinimumTopDropMeters,
                    report.formedMouth.Summary()));
                checks.Add(new Check(
                    "released-seal-is-compact-top-right-strip",
                    report.formedMouth.releasedSealIsCompactTopRight,
                    report.formedMouth.Summary()));
                checks.Add(new Check(
                    "contained-case-renders-inside-upper-mouth",
                    report.caseContainment.packVisible
                        && report.caseContainment.packDissolve <= 0.000001f
                        && report.caseContainment.visibleCasePixelsInUpperMouth
                            >= MinimumMouthCasePixels
                        && report.caseContainment.visibleCasePixelsWithPackInUpperMouth
                            >= MinimumMouthCasePixels
                        && report.caseContainment.occludedCasePixelsByFront
                            >= MinimumOccludedCasePixels
                        && report.caseContainment.largestFrontOcclusionClusterPixels
                            >= MinimumContiguousOcclusionPixels
                        && report.caseContainment.frontLipCaseProjectedOverlapPixels
                            >= MinimumContiguousOcclusionPixels,
                    report.caseContainment.Summary()));
                checks.Add(new Check(
                    "contained-case-has-readable-contrast-and-bounds",
                    report.caseLegibility.passed,
                    report.caseLegibility.Summary()));
                checks.Add(new Check(
                    "primary-static-sheet-emits-four-unity-frames",
                    File.Exists(Path.Combine(outputRoot, report.primaryStaticSheet)),
                    report.primaryStaticSheet));
                checks.Add(new Check(
                    "preflight-effects-remain-zero",
                    report.visualEffectsIntensity <= 0.000001f,
                    report.visualEffectsIntensity.ToString("F6")));
                checks.Add(new Check(
                    "every-capture-follows-a-unity-frame",
                    ledger.AllFramesAdvanced,
                    $"captures={ledger.captureCount}, advanced={ledger.advancedCount}"));

                report.checks = checks.ToArray();
                report.passed = checks.All(check => check.passed);
                WriteJson(
                    Path.Combine(outputRoot, "r020-preflight-report.json"),
                    report);
                WriteXml(
                    Path.Combine(outputRoot, "r020-preflight-results.xml"),
                    "IsolatedR020Preflight",
                    checks);
                if (!report.passed)
                {
                    throw new InvalidOperationException(
                        "R020 preflight failed. See emitted result XML.");
                }
            }
            finally
            {
                render.Dispose();
                UnityEngine.Object.Destroy(sealedMesh);
                UnityEngine.Object.Destroy(formedMesh);
                UnityEngine.Object.Destroy(containedMesh);
            }
        }

        private static IEnumerator CaptureFrame(
            RenderSession render,
            IsolatedR020ProofSequence sequence,
            float seconds,
            string path,
            FrameCapture result,
            FrameLedger ledger)
        {
            result.timeSeconds = seconds;
            result.stateSetFrame = Time.frameCount;
            sequence.SetTime(seconds, false);
            yield return null;
            result.renderedAfterFrame = Time.frameCount;
            result.pixels = render.Capture(path);
            ledger.Record(result.stateSetFrame, result.renderedAfterFrame);
        }

        private static IEnumerator CaptureTearFrontDirection(
            RenderSession render,
            IsolatedR020ProofSequence sequence,
            string outputRoot,
            TearFrontDirectionReport report,
            FrameLedger ledger)
        {
            SkinnedMeshRenderer[] packRenderers = sequence.PackRenderers.ToArray();
            bool[] enabled = packRenderers.Select(item => item.enabled).ToArray();
            Material[][] materials = packRenderers
                .Select(item => item.sharedMaterials)
                .ToArray();
            var states = new List<TearFrontState>(
                TearFrontProgressSamples.Length);
            try
            {
                sequence.SetNormalizedTearProgress(0f);
                yield return null;
                if (!sequence.TryGetTopSealUvEdgeViewportPoints(
                        out Vector2 physicalUZero,
                        out Vector2 physicalUOne))
                {
                    throw new InvalidOperationException(
                        "R020 cannot project the top-seal physical-U edges.");
                }
                report.physicalUZeroScreenX = physicalUZero.x;
                report.physicalUOneScreenX = physicalUOne.x;
                foreach (float progress in TearFrontProgressSamples)
                {
                    sequence.SetNormalizedTearProgress(progress);
                    yield return null;
                    if (!sequence.TryGetPackBodyViewportBounds(
                            out Rect packBounds))
                    {
                        throw new InvalidOperationException(
                            "R020 cannot project Pack bounds for tear direction.");
                    }
                    foreach (SkinnedMeshRenderer renderer in packRenderers)
                    {
                        renderer.enabled = false;
                    }
                    Material sealId = CreateTopSealIdMaterial(
                        $"R020TopSealDirectionId{progress:0.000}",
                        new Color(1f, 0.78f, 0.04f, 1f),
                        sequence.NormalizedTearFront);
                    try
                    {
                        sequence.TopSeal.enabled = true;
                        sequence.TopSeal.sharedMaterials = Enumerable.Repeat(
                            sealId,
                            Mathf.Max(
                                1,
                                sequence.TopSeal.sharedMaterials.Length))
                            .ToArray();
                        int stateSetFrame = Time.frameCount;
                        yield return null;
                        int renderedAfterFrame = Time.frameCount;
                        Color32[] pixels = render.Capture(Path.Combine(
                            outputRoot,
                            $"diagnostics/tear-front-seal-id-{progress:0.000}.png"));
                        ledger.Record(stateSetFrame, renderedAfterFrame);
                        states.Add(MeasureTearFrontState(
                            progress,
                            sequence.NormalizedTearFront,
                            packBounds,
                            pixels,
                            stateSetFrame,
                            renderedAfterFrame));
                    }
                    finally
                    {
                        UnityEngine.Object.Destroy(sealId);
                    }
                }
            }
            finally
            {
                for (int index = 0; index < packRenderers.Length; index++)
                {
                    packRenderers[index].sharedMaterials = materials[index];
                    packRenderers[index].enabled = enabled[index];
                }
            }
            report.states = states.ToArray();
            report.passed = report.physicalUZeroScreenX
                > report.physicalUOneScreenX + 0.010f
                && report.states.Length == TearFrontProgressSamples.Length
                && report.states.All(item => item.openedSideIsScreenRight);
        }

        private static TearFrontState MeasureTearFrontState(
            float progress,
            float tearFront,
            Rect packBounds,
            IReadOnlyList<Color32> pixels,
            int stateSetFrame,
            int renderedAfterFrame)
        {
            float edgeBand = packBounds.width * 0.25f;
            float leftLimit = packBounds.xMin + edgeBand;
            float rightLimit = packBounds.xMax - edgeBand;
            int left = 0;
            int right = 0;
            for (int y = 0; y < Height; y++)
            {
                for (int x = 0; x < Width; x++)
                {
                    if (!IsTopCrimpId(pixels[y * Width + x]))
                    {
                        continue;
                    }
                    float normalizedX = x / (float)(Width - 1);
                    if (normalizedX <= leftLimit)
                    {
                        left++;
                    }
                    else if (normalizedX >= rightLimit)
                    {
                        right++;
                    }
                }
            }
            return new TearFrontState
            {
                normalizedTearProgress = progress,
                normalizedTearFront = tearFront,
                leftEdgeSealPixels = left,
                rightEdgeSealPixels = right,
                openedSideIsScreenRight = left >= 128 && right * 3 <= left,
                stateSetFrame = stateSetFrame,
                renderedAfterFrame = renderedAfterFrame
            };
        }

        private static void BuildPrimaryStaticSheet(
            string path,
            params IReadOnlyList<Color32>[] frames)
        {
            if (frames.Length != 4 || frames.Any(frame =>
                    frame == null || frame.Count != Width * Height))
            {
                throw new InvalidOperationException(
                    "R020 primary sheet requires four full Unity frames.");
            }
            int cellWidth = Width / 2;
            int cellHeight = Height / 2;
            var pixels = new Color32[Width * Height];
            for (int index = 0; index < frames.Length; index++)
            {
                IReadOnlyList<Color32> source = frames[index];
                int cellX = index % 2 * cellWidth;
                int cellY = (1 - index / 2) * cellHeight;
                for (int y = 0; y < cellHeight; y++)
                {
                    int sourceY = y * Height / cellHeight;
                    for (int x = 0; x < cellWidth; x++)
                    {
                        int sourceX = x * Width / cellWidth;
                        pixels[(cellY + y) * Width + cellX + x] =
                            source[sourceY * Width + sourceX];
                    }
                }
            }
            var sheet = new Texture2D(
                Width,
                Height,
                TextureFormat.RGB24,
                false,
                false);
            try
            {
                sheet.SetPixels32(pixels);
                sheet.Apply(false, false);
                File.WriteAllBytes(path, sheet.EncodeToPNG());
            }
            finally
            {
                UnityEngine.Object.Destroy(sheet);
            }
        }

        private static IEnumerator CaptureRenderedCrimpAndTitle(
            RenderSession render,
            IsolatedR020ProofSequence sequence,
            string outputRoot,
            RenderedCrimpReport report,
            FrameLedger ledger)
        {
            SkinnedMeshRenderer[] packRenderers = sequence.PackRenderers.ToArray();
            bool[] enabled = packRenderers.Select(item => item.enabled).ToArray();
            Material[][] materials = packRenderers
                .Select(item => item.sharedMaterials)
                .ToArray();
            Texture artwork = sequence.FrontFoil.sharedMaterial.GetTexture(
                "_BaseMap");
            Material crimpId = CreateIdMaterial(
                "R020TopCrimpId",
                new Color(1f, 0.78f, 0.04f, 1f),
                2490);
            Material titleBand = CreateTitleBandMaterial(artwork);
            try
            {
                foreach (SkinnedMeshRenderer renderer in packRenderers)
                {
                    renderer.enabled = false;
                }
                sequence.TopSeal.enabled = true;
                sequence.TopSeal.sharedMaterials = Enumerable.Repeat(
                    crimpId,
                    Mathf.Max(1, sequence.TopSeal.sharedMaterials.Length))
                    .ToArray();
                int crimpStateSetFrame = Time.frameCount;
                yield return null;
                int crimpRenderedAfterFrame = Time.frameCount;
                Color32[] crimpPixels = render.Capture(Path.Combine(
                    outputRoot,
                    "diagnostics/top-crimp-id.png"));
                ledger.Record(crimpStateSetFrame, crimpRenderedAfterFrame);
                MaskMetrics crimp = MeasureMask(crimpPixels, IsTopCrimpId);

                sequence.TopSeal.enabled = false;
                sequence.FrontFoil.enabled = true;
                sequence.FrontFoil.sharedMaterials = Enumerable.Repeat(
                    titleBand,
                    Mathf.Max(1, sequence.FrontFoil.sharedMaterials.Length))
                    .ToArray();
                int titleStateSetFrame = Time.frameCount;
                yield return null;
                int titleRenderedAfterFrame = Time.frameCount;
                Color32[] titlePixels = render.Capture(Path.Combine(
                    outputRoot,
                    "diagnostics/archive-title-band-id.png"));
                ledger.Record(titleStateSetFrame, titleRenderedAfterFrame);
                MaskMetrics title = MeasureMask(titlePixels, IsTitleBandId);

                report.topCrimpPixels = crimp.count;
                report.topCrimpBounds = RectData.From(crimp.bounds);
                report.topCrimpLowestViewportY = crimp.bounds.yMin;
                report.titleBandPixels = title.count;
                report.titleBandBounds = RectData.From(title.bounds);
                report.archiveTitleTopViewportY = title.bounds.yMax;
                report.topCrimpStateSetFrame = crimpStateSetFrame;
                report.topCrimpRenderedAfterFrame = crimpRenderedAfterFrame;
                report.titleBandStateSetFrame = titleStateSetFrame;
                report.titleBandRenderedAfterFrame = titleRenderedAfterFrame;
            }
            finally
            {
                for (int index = 0; index < packRenderers.Length; index++)
                {
                    packRenderers[index].sharedMaterials = materials[index];
                    packRenderers[index].enabled = enabled[index];
                }
                UnityEngine.Object.Destroy(crimpId);
                UnityEngine.Object.Destroy(titleBand);
            }
        }

        private static IEnumerator CaptureMouthMaterialSeparation(
            RenderSession render,
            IsolatedR020ProofSequence sequence,
            IReadOnlyList<Color32> beautyPixels,
            Rect upperMouth,
            float seconds,
            string outputRoot,
            MouthMaterialReport report,
            FrameLedger ledger)
        {
            SkinnedMeshRenderer[] packRenderers = sequence.PackRenderers.ToArray();
            Material[][] materials = packRenderers
                .Select(item => item.sharedMaterials)
                .ToArray();
            Material outerId = CreateIdMaterial(
                "R020OuterPackId",
                new Color(0.02f, 0.92f, 0.14f, 1f),
                2460);
            Material topSealId = CreateTopSealIdMaterial(
                "R020TopSealMouthId",
                new Color(0.02f, 0.92f, 0.14f, 1f),
                sequence.NormalizedTearFront);
            Material linerId = CreateIdMaterial(
                "R020InnerLinerId",
                new Color(0.03f, 0.82f, 1f, 1f),
                2470);
            Material cavityId = CreateIdMaterial(
                "R020CavityId",
                new Color(1f, 0.08f, 0.03f, 1f),
                2470);
            Material lipId = CreateIdMaterial(
                "R020LipId",
                new Color(1f, 0.78f, 0.04f, 1f),
                2480);
            try
            {
                for (int index = 0; index < packRenderers.Length; index++)
                {
                    SkinnedMeshRenderer renderer = packRenderers[index];
                    Material replacement = renderer == sequence.TopSeal
                        ? topSealId
                        : renderer == sequence.FrontFoil
                            ? outerId
                        : renderer.name == "Pack_RearInnerFoil"
                            ? cavityId
                            : renderer == sequence.InnerMouth
                                || renderer == sequence.InnerBackRim
                                || renderer == sequence.TearFrontSidewall
                                || renderer == sequence.TabSidewall
                                ? linerId
                                : lipId;
                    renderer.sharedMaterials = Enumerable.Repeat(
                        replacement,
                        Mathf.Max(1, materials[index].Length)).ToArray();
                }
                int stateSetFrame = Time.frameCount;
                yield return null;
                int renderedAfterFrame = Time.frameCount;
                Color32[] ids = render.Capture(Path.Combine(
                    outputRoot,
                    $"diagnostics/mouth-material-id-{seconds:0.000}.png"));
                ledger.Record(stateSetFrame, renderedAfterFrame);
                MeasureMouthMaterialSeparation(
                    beautyPixels,
                    ids,
                    upperMouth,
                    seconds,
                    report);
                report.stateSetFrame = stateSetFrame;
                report.renderedAfterFrame = renderedAfterFrame;
            }
            finally
            {
                for (int index = 0; index < packRenderers.Length; index++)
                {
                    packRenderers[index].sharedMaterials = materials[index];
                }
                UnityEngine.Object.Destroy(outerId);
                UnityEngine.Object.Destroy(topSealId);
                UnityEngine.Object.Destroy(linerId);
                UnityEngine.Object.Destroy(cavityId);
                UnityEngine.Object.Destroy(lipId);
            }
        }

        private static SealedReport MeasureSealed(
            IsolatedR020ProofSequence sequence,
            Mesh sealedMesh)
        {
            Bounds topCrimp = sequence.TopSeal.bounds;
            return new SealedReport
            {
                archiveY = ObjectYAtArtworkV(sealedMesh, ArchiveArtworkV),
                standardY = ObjectYAtArtworkV(sealedMesh, StandardArtworkV),
                bottomCrimpY = ObjectYAtArtworkV(
                    sealedMesh,
                    BottomCrimpArtworkV),
                topCrimpMinY = topCrimp.min.y,
                topCrimpMaxY = topCrimp.max.y
            };
        }

        private static FormedMouthReport MeasureMouth(
            IsolatedR020ProofSequence sequence,
            Mesh sealedMesh,
            Mesh openedMesh,
            float seconds)
        {
            if (!sequence.TryGetPackBodyViewportBounds(out Rect packBounds))
            {
                throw new InvalidOperationException(
                    "R020 cannot project Pack body bounds.");
            }
            float upperThirdStart = packBounds.yMin + packBounds.height * 2f / 3f;
            float lowerThirdEnd = packBounds.yMin + packBounds.height / 3f;
            var mouthBounds = new List<NamedRect>();
            foreach (SkinnedMeshRenderer renderer in sequence.PhysicalMouthRenderers)
            {
                if (!renderer.enabled
                    || !sequence.TryGetRendererViewportBounds(renderer, out Rect bounds))
                {
                    throw new InvalidOperationException(
                        $"R020 cannot project mouth renderer: {renderer.name}");
                }
                mouthBounds.Add(new NamedRect(renderer.name, bounds));
            }

            Rect upperMouth = Union(
                mouthBounds.Where(item =>
                    item.name == "Pack_RearInnerFoil"
                    || item.name == "Pack_InnerFoilMouth"
                    || item.name == "Pack_InnerBackFoilRim"
                    || item.name == "Pack_RolledCrimpLip"
                    || item.name == "Pack_TearFrontSidewall"
                    || item.name == "Pack_TabSidewall")
                    .Select(item => item.rect)
                    .ToArray());
            upperMouth = Rect.MinMaxRect(
                Mathf.Max(packBounds.xMin, upperMouth.xMin - 0.006f),
                Mathf.Max(upperThirdStart, upperMouth.yMin - 0.004f),
                Mathf.Min(packBounds.xMax, upperMouth.xMax + 0.006f),
                Mathf.Min(packBounds.yMax, upperMouth.yMax + 0.006f));

            NamedRect strip = mouthBounds.Single(
                item => item.name == "Pack_ReleasedSealStrip");
            NamedRect tab = mouthBounds.Single(
                item => item.name == "Pack_TopRightPullTab");
            NamedRect seam = mouthBounds.Single(
                item => item.name == "Pack_TopSealRemaining");
            if (!sequence.TryGetRendererVertexViewportPoint(
                    sequence.ReleasedSealStrip,
                    0,
                    out Vector2 stripRoot))
            {
                throw new InvalidOperationException(
                    "R020 cannot project the released strip root.");
            }
            float topDrop = ObjectYAtArtworkV(
                sealedMesh,
                PhysicalTopArtworkV)
                - ObjectYAtArtworkV(openedMesh, PhysicalTopArtworkV);
            bool allUpper = mouthBounds.All(
                item => item.rect.yMin >= upperThirdStart);
            bool compactStrip = MeetsTopRightStripBoundsForTesting(
                packBounds,
                seam.rect,
                strip.rect,
                tab.rect,
                stripRoot);
            return new FormedMouthReport
            {
                timeSeconds = seconds,
                packBounds = RectData.From(packBounds),
                upperThirdStart = upperThirdStart,
                lowerThirdEnd = lowerThirdEnd,
                mouthComponentBounds = mouthBounds.ToArray(),
                upperMouthRegion = RectData.From(upperMouth),
                allMouthBoundsInUpperThird = allUpper,
                frontTopDropMeters = topDrop,
                seamBounds = RectData.From(seam.rect),
                releasedSealBounds = RectData.From(strip.rect),
                pullTabBounds = RectData.From(tab.rect),
                releasedSealRootViewport = Vector2Data.From(stripRoot),
                releasedSealIsCompactTopRight = compactStrip
            };
        }

        public static bool MeetsTopRightStripBoundsForTesting(
            Rect packBounds,
            Rect seamBounds,
            Rect stripBounds,
            Rect tabBounds,
            Vector2 stripRoot)
        {
            float rightBandMin = packBounds.xMin + packBounds.width * 0.80f;
            float rightBandMax = packBounds.xMin + packBounds.width * 0.88f;
            float curlMin = packBounds.xMin + packBounds.width * 0.79f;
            float curlMax = packBounds.xMax + packBounds.width * 0.02f;
            float verticalLimit = packBounds.height * 0.15f;
            return stripRoot.x >= rightBandMin
                && stripRoot.x <= rightBandMax
                && stripBounds.xMin >= curlMin
                && stripBounds.xMax <= curlMax
                && stripBounds.width <= packBounds.width * 0.20f
                && stripBounds.yMin >= seamBounds.yMin - verticalLimit
                && stripBounds.yMax <= seamBounds.yMax + verticalLimit
                && tabBounds.xMin >= curlMin
                && tabBounds.xMax <= curlMax
                && tabBounds.width <= packBounds.width * 0.20f
                && tabBounds.height <= packBounds.height * 0.15f;
        }

        private static Rect MeasureUpperMouthRegion(
            IsolatedR020ProofSequence sequence)
        {
            if (!sequence.TryGetPackBodyViewportBounds(out Rect packBounds))
            {
                throw new InvalidOperationException(
                    "R020 cannot project Pack body bounds.");
            }
            float upperThirdStart = packBounds.yMin + packBounds.height * 2f / 3f;
            var components = new[]
            {
                sequence.PackRenderers.Single(
                    item => item.name == "Pack_RearInnerFoil"),
                sequence.InnerMouth,
                sequence.InnerBackRim,
                sequence.RolledCrimpLip,
                sequence.TearFrontSidewall,
                sequence.TabSidewall
            };
            Rect region = Union(components.Select(renderer =>
            {
                if (!renderer.enabled
                    || !sequence.TryGetRendererViewportBounds(
                        renderer,
                        out Rect bounds))
                {
                    throw new InvalidOperationException(
                        $"R020 cannot project mouth renderer: {renderer.name}");
                }
                return bounds;
            }).ToArray());
            return Rect.MinMaxRect(
                Mathf.Max(packBounds.xMin, region.xMin - 0.006f),
                Mathf.Max(upperThirdStart, region.yMin - 0.004f),
                Mathf.Min(packBounds.xMax, region.xMax + 0.006f),
                Mathf.Min(packBounds.yMax, region.yMax + 0.006f));
        }

        private static IEnumerator CaptureCaseOcclusion(
            RenderSession render,
            IsolatedR020ProofSequence sequence,
            Rect upperMouth,
            IReadOnlyList<Color32> beautyPixels,
            string outputRoot,
            CaseContainmentReport report,
            CaseLegibilityReport legibility,
            FrameLedger ledger)
        {
            Renderer[] caseRenderers = sequence.LiveCaseRenderers.ToArray();
            SkinnedMeshRenderer[] packRenderers = sequence.PackRenderers.ToArray();
            SkinnedMeshRenderer[] frontOccluders =
            {
                sequence.RolledCrimpLip,
                sequence.TearFrontSidewall,
                sequence.TabSidewall
            };
            bool[] packEnabled = packRenderers
                .Select(renderer => renderer.enabled)
                .ToArray();
            Material[][] caseMaterials = caseRenderers
                .Select(renderer => renderer.sharedMaterials)
                .ToArray();
            Material[][] occluderMaterials = frontOccluders
                .Select(renderer => renderer.sharedMaterials)
                .ToArray();
            Material caseId = CreateIdMaterial(
                "R020LiveCaseId",
                new Color(1f, 0.02f, 1f, 1f),
                2475);
            Material frontId = CreateIdMaterial(
                "R020FrontLipAndSidewallId",
                new Color(1f, 0.85f, 0.02f, 1f),
                2480);
            try
            {
                for (int index = 0; index < caseRenderers.Length; index++)
                {
                    int count = Mathf.Max(1, caseMaterials[index].Length);
                    caseRenderers[index].sharedMaterials = Enumerable.Repeat(
                        caseId,
                        count).ToArray();
                }

                int visibleWithPackStateSetFrame = Time.frameCount;
                yield return null;
                int visibleWithPackRenderedAfterFrame = Time.frameCount;
                Color32[] visibleWithPack = render.Capture(Path.Combine(
                    outputRoot,
                    "diagnostics/case-visible-id-090.png"));
                ledger.Record(
                    visibleWithPackStateSetFrame,
                    visibleWithPackRenderedAfterFrame);

                foreach (SkinnedMeshRenderer renderer in packRenderers)
                {
                    renderer.enabled = false;
                }
                int unoccludedStateSetFrame = Time.frameCount;
                yield return null;
                int unoccludedRenderedAfterFrame = Time.frameCount;
                Color32[] unoccluded = render.Capture(Path.Combine(
                    outputRoot,
                    "diagnostics/case-unoccluded-id-090.png"));
                ledger.Record(
                    unoccludedStateSetFrame,
                    unoccludedRenderedAfterFrame);

                foreach (SkinnedMeshRenderer renderer in frontOccluders)
                {
                    renderer.enabled = true;
                    int materialCount = Mathf.Max(
                        1,
                        renderer.sharedMaterials.Length);
                    renderer.sharedMaterials = Enumerable.Repeat(
                        frontId,
                        materialCount).ToArray();
                }
                int occludedStateSetFrame = Time.frameCount;
                yield return null;
                int occludedRenderedAfterFrame = Time.frameCount;
                Color32[] occluded = render.Capture(Path.Combine(
                    outputRoot,
                    "diagnostics/case-front-occlusion-id-090.png"));
                ledger.Record(
                    occludedStateSetFrame,
                    occludedRenderedAfterFrame);

                MeasureCaseOcclusion(
                    unoccluded,
                    visibleWithPack,
                    occluded,
                    upperMouth,
                    report);
                MeasureCaseLegibility(
                    beautyPixels,
                    visibleWithPack,
                    upperMouth,
                    legibility);
                if (!sequence.TryGetCaseViewportBounds(
                        out Rect caseProjectedBounds)
                    || !sequence.TryGetRendererViewportBounds(
                        sequence.RolledCrimpLip,
                        out Rect lipProjectedBounds))
                {
                    throw new InvalidOperationException(
                        "R020 cannot project the case and front lip.");
                }
                report.caseProjectedBounds = RectData.From(caseProjectedBounds);
                report.frontLipProjectedBounds = RectData.From(lipProjectedBounds);
                report.frontLipCaseProjectedOverlapPixels =
                    OverlapPixels(caseProjectedBounds, lipProjectedBounds);
                report.visibleWithPackStateSetFrame =
                    visibleWithPackStateSetFrame;
                report.visibleWithPackRenderedAfterFrame =
                    visibleWithPackRenderedAfterFrame;
                report.unoccludedStateSetFrame = unoccludedStateSetFrame;
                report.unoccludedRenderedAfterFrame =
                    unoccludedRenderedAfterFrame;
                report.occludedStateSetFrame = occludedStateSetFrame;
                report.occludedRenderedAfterFrame = occludedRenderedAfterFrame;
            }
            finally
            {
                for (int index = 0; index < caseRenderers.Length; index++)
                {
                    caseRenderers[index].sharedMaterials = caseMaterials[index];
                }
                for (int index = 0; index < frontOccluders.Length; index++)
                {
                    frontOccluders[index].sharedMaterials =
                        occluderMaterials[index];
                }
                for (int index = 0; index < packRenderers.Length; index++)
                {
                    packRenderers[index].enabled = packEnabled[index];
                }
                UnityEngine.Object.Destroy(caseId);
                UnityEngine.Object.Destroy(frontId);
            }
        }

        private static void MeasureCaseOcclusion(
            IReadOnlyList<Color32> unoccluded,
            IReadOnlyList<Color32> visibleWithPack,
            IReadOnlyList<Color32> occluded,
            Rect upperMouth,
            CaseContainmentReport result)
        {
            int visibleInside = 0;
            int visibleWithPackInside = 0;
            int coveredByFront = 0;
            int unoccludedInside = 0;
            var frontCoverage = new bool[Width * Height];
            for (int y = 0; y < Height; y++)
            {
                float normalizedY = y / (float)(Height - 1);
                for (int x = 0; x < Width; x++)
                {
                    int index = y * Width + x;
                    float normalizedX = x / (float)(Width - 1);
                    bool insideMouth = upperMouth.Contains(
                        new Vector2(normalizedX, normalizedY));
                    if (IsCaseId(unoccluded[index]) && insideMouth)
                    {
                        unoccludedInside++;
                        if (IsFrontId(occluded[index]))
                        {
                            coveredByFront++;
                            frontCoverage[index] = true;
                        }
                    }
                    if (IsCaseId(visibleWithPack[index]) && insideMouth)
                    {
                        visibleWithPackInside++;
                    }
                    if (IsCaseId(occluded[index]) && insideMouth)
                    {
                        visibleInside++;
                    }
                }
            }
            result.unoccludedCasePixelsInUpperMouth = unoccludedInside;
            result.visibleCasePixelsInUpperMouth = visibleInside;
            result.visibleCasePixelsWithPackInUpperMouth = visibleWithPackInside;
            result.occludedCasePixelsByFront = coveredByFront;
            result.largestFrontOcclusionClusterPixels =
                LargestNearContiguousPixelCluster(frontCoverage);
        }

        private static void MeasureCaseLegibility(
            IReadOnlyList<Color32> beauty,
            IReadOnlyList<Color32> caseIds,
            Rect upperMouth,
            CaseLegibilityReport result)
        {
            var mask = new bool[Width * Height];
            int count = 0;
            float minX = float.PositiveInfinity;
            float minY = float.PositiveInfinity;
            float maxX = float.NegativeInfinity;
            float maxY = float.NegativeInfinity;
            for (int y = 0; y < Height; y++)
            {
                float normalizedY = y / (float)(Height - 1);
                for (int x = 0; x < Width; x++)
                {
                    int index = y * Width + x;
                    float normalizedX = x / (float)(Width - 1);
                    if (!IsCaseId(caseIds[index])
                        || !upperMouth.Contains(
                            new Vector2(normalizedX, normalizedY)))
                    {
                        continue;
                    }
                    mask[index] = true;
                    count++;
                    minX = Mathf.Min(minX, normalizedX);
                    minY = Mathf.Min(minY, normalizedY);
                    maxX = Mathf.Max(maxX, normalizedX);
                    maxY = Mathf.Max(maxY, normalizedY);
                }
            }
            float contrastTotal = 0f;
            int contrastCount = 0;
            for (int y = 1; y < Height - 1; y++)
            {
                for (int x = 1; x < Width - 1; x++)
                {
                    int index = y * Width + x;
                    if (!mask[index])
                    {
                        continue;
                    }
                    float current = Luminance(beauty[index]);
                    foreach (int neighbor in new[]
                             {
                                 index - 1,
                                 index + 1,
                                 index - Width,
                                 index + Width
                             })
                    {
                        if (mask[neighbor])
                        {
                            continue;
                        }
                        contrastTotal += Mathf.Abs(
                            current - Luminance(beauty[neighbor]));
                        contrastCount++;
                    }
                }
            }
            result.visibleCasePixels = count;
            result.visibleCaseBounds = count == 0
                ? RectData.From(Rect.zero)
                : RectData.From(Rect.MinMaxRect(minX, minY, maxX, maxY));
            result.averageBoundaryContrast = contrastCount == 0
                ? 0f
                : contrastTotal / contrastCount;
            result.passed = count >= MinimumMouthCasePixels
                && result.visibleCaseBounds.width >= MinimumCaseBoundsWidth
                && result.visibleCaseBounds.height >= MinimumCaseBoundsHeight
                && result.averageBoundaryContrast >= MinimumCaseBoundaryContrast;
        }

        private static int LargestNearContiguousPixelCluster(bool[] mask)
        {
            var visited = new bool[mask.Length];
            var queue = new Queue<int>();
            int largest = 0;
            for (int start = 0; start < mask.Length; start++)
            {
                if (!mask[start] || visited[start])
                {
                    continue;
                }
                int count = 0;
                queue.Enqueue(start);
                visited[start] = true;
                while (queue.Count > 0)
                {
                    int current = queue.Dequeue();
                    count++;
                    int x = current % Width;
                    int y = current / Width;
                    for (int offsetY = -1; offsetY <= 1; offsetY++)
                    {
                        int neighborY = y + offsetY;
                        if (neighborY < 0 || neighborY >= Height)
                        {
                            continue;
                        }
                        for (int offsetX = -1; offsetX <= 1; offsetX++)
                        {
                            int neighborX = x + offsetX;
                            if (offsetX == 0 && offsetY == 0
                                || neighborX < 0 || neighborX >= Width)
                            {
                                continue;
                            }
                            int neighbor = neighborY * Width + neighborX;
                            if (!mask[neighbor] || visited[neighbor])
                            {
                                continue;
                            }
                            visited[neighbor] = true;
                            queue.Enqueue(neighbor);
                        }
                    }
                }
                largest = Mathf.Max(largest, count);
            }
            return largest;
        }

        private static int OverlapPixels(Rect first, Rect second)
        {
            float width = Mathf.Max(
                0f,
                Mathf.Min(first.xMax, second.xMax)
                    - Mathf.Max(first.xMin, second.xMin));
            float height = Mathf.Max(
                0f,
                Mathf.Min(first.yMax, second.yMax)
                    - Mathf.Max(first.yMin, second.yMin));
            return Mathf.RoundToInt(width * Width * height * Height);
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
                    "URP Unlit shader is unavailable for R020 diagnostics.");
            }
            var material = new Material(shader)
            {
                name = name,
                renderQueue = renderQueue
            };
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Cull", 0f);
            return material;
        }

        private static Material CreateTopSealIdMaterial(
            string name,
            Color color,
            float tearFront)
        {
            Shader shader = Shader.Find(
                "FidgetingApp/Isolated/R020/TopSealTearClip");
            if (shader == null)
            {
                throw new MissingReferenceException(
                    "R020 top-seal clip shader is unavailable.");
            }
            var material = new Material(shader)
            {
                name = name,
                renderQueue = 2490
            };
            material.SetTexture("_BaseMap", Texture2D.whiteTexture);
            material.SetColor("_BaseColor", color);
            material.SetFloat("_TearFront", tearFront);
            material.SetFloat("_Cutoff", 0f);
            return material;
        }

        private static Material CreateTitleBandMaterial(Texture artwork)
        {
            if (artwork == null)
            {
                throw new MissingReferenceException(
                    "R020 cannot create the rendered title-band diagnostic.");
            }
            Shader shader = Shader.Find(
                "FidgetingApp/Isolated/R020/RenderedBandMaskUnlit");
            if (shader == null)
            {
                throw new MissingReferenceException(
                    "R020 rendered title-band shader is unavailable.");
            }
            var material = new Material(shader)
            {
                name = "R020ArchiveTitleBandId",
                renderQueue = 2490
            };
            material.SetTexture("_BaseMap", artwork);
            material.SetFloat("_BandMin", ArchiveTitleBandMinV);
            material.SetFloat("_BandMax", ArchiveTitleBandMaxV);
            material.SetColor("_MaskColor", new Color(0.04f, 0.10f, 1f, 1f));
            return material;
        }

        private static void MeasureMouthMaterialSeparation(
            IReadOnlyList<Color32> beauty,
            IReadOnlyList<Color32> ids,
            Rect upperMouth,
            float seconds,
            MouthMaterialReport report)
        {
            LuminanceSample liner = SampleLuminance(
                beauty,
                ids,
                upperMouth,
                IsLinerId,
                true);
            LuminanceSample cavity = SampleLuminance(
                beauty,
                ids,
                upperMouth,
                IsCavityId,
                true);
            LuminanceSample outer = SampleLuminance(
                beauty,
                ids,
                upperMouth,
                IsOuterPackId,
                false);
            bool[] cavityMask = BuildRegionMask(
                ids,
                upperMouth,
                IsCavityId);
            float background = SampleBackgroundLuminance(beauty);
            report.timeSeconds = seconds;
            report.visibleInnerLinerPixels = liner.count;
            report.visibleCavityPixels = cavity.count;
            report.largestCavityClusterPixels =
                LargestNearContiguousPixelCluster(cavityMask);
            report.innerLinerLuminance = liner.average;
            report.recessedCavityLuminance = cavity.average;
            report.outerPackLuminance = outer.average;
            report.backgroundLuminance = background;
            report.linerCavityLuminanceDelta = Mathf.Abs(
                liner.average - cavity.average);
            report.linerOuterLuminanceDelta = Mathf.Abs(
                liner.average - outer.average);
            report.cavityBackgroundLuminanceDelta = Mathf.Abs(
                cavity.average - background);
            report.passed = liner.count >= MinimumVisibleLinerPixels
                && cavity.count >= MinimumVisibleCavityPixels
                && report.largestCavityClusterPixels
                    >= MinimumContiguousCavityPixels
                && report.linerCavityLuminanceDelta
                    >= MinimumLinerCavityLuminanceDelta
                && report.linerOuterLuminanceDelta
                    >= MinimumLinerOuterLuminanceDelta
                && report.cavityBackgroundLuminanceDelta
                    >= MinimumCavityBackgroundLuminanceDelta;
        }

        private static LuminanceSample SampleLuminance(
            IReadOnlyList<Color32> beauty,
            IReadOnlyList<Color32> ids,
            Rect region,
            Func<Color32, bool> matcher,
            bool constrainToRegion)
        {
            int count = 0;
            float total = 0f;
            for (int y = 0; y < Height; y++)
            {
                float normalizedY = y / (float)(Height - 1);
                for (int x = 0; x < Width; x++)
                {
                    int index = y * Width + x;
                    if (!matcher(ids[index]))
                    {
                        continue;
                    }
                    if (constrainToRegion
                        && !region.Contains(new Vector2(
                            x / (float)(Width - 1),
                            normalizedY)))
                    {
                        continue;
                    }
                    count++;
                    total += Luminance(beauty[index]);
                }
            }
            return new LuminanceSample(
                count,
                count == 0 ? 0f : total / count);
        }

        private static bool[] BuildRegionMask(
            IReadOnlyList<Color32> pixels,
            Rect region,
            Func<Color32, bool> matcher)
        {
            var mask = new bool[Width * Height];
            for (int y = 0; y < Height; y++)
            {
                float normalizedY = y / (float)(Height - 1);
                for (int x = 0; x < Width; x++)
                {
                    int index = y * Width + x;
                    mask[index] = matcher(pixels[index])
                        && region.Contains(new Vector2(
                            x / (float)(Width - 1),
                            normalizedY));
                }
            }
            return mask;
        }

        private static float SampleBackgroundLuminance(
            IReadOnlyList<Color32> pixels)
        {
            int count = 0;
            float total = 0f;
            int sideWidth = Mathf.CeilToInt(Width * 0.08f);
            for (int y = 0; y < Height; y += 8)
            {
                for (int x = 0; x < Width; x += 8)
                {
                    if (x >= sideWidth && x < Width - sideWidth)
                    {
                        continue;
                    }
                    count++;
                    total += Luminance(pixels[y * Width + x]);
                }
            }
            return count == 0 ? 0f : total / count;
        }

        private static MaskMetrics MeasureMask(
            IReadOnlyList<Color32> pixels,
            Func<Color32, bool> matcher)
        {
            int count = 0;
            float minX = float.PositiveInfinity;
            float minY = float.PositiveInfinity;
            float maxX = float.NegativeInfinity;
            float maxY = float.NegativeInfinity;
            for (int y = 0; y < Height; y++)
            {
                float normalizedY = y / (float)(Height - 1);
                for (int x = 0; x < Width; x++)
                {
                    Color32 pixel = pixels[y * Width + x];
                    if (!matcher(pixel))
                    {
                        continue;
                    }
                    float normalizedX = x / (float)(Width - 1);
                    count++;
                    minX = Mathf.Min(minX, normalizedX);
                    minY = Mathf.Min(minY, normalizedY);
                    maxX = Mathf.Max(maxX, normalizedX);
                    maxY = Mathf.Max(maxY, normalizedY);
                }
            }
            return count == 0
                ? new MaskMetrics(0, Rect.zero)
                : new MaskMetrics(
                    count,
                    Rect.MinMaxRect(minX, minY, maxX, maxY));
        }

        private static bool IsCaseId(Color32 color)
        {
            return color.r > 180 && color.g < 100 && color.b > 180;
        }

        private static bool IsFrontId(Color32 color)
        {
            return color.r > 180 && color.g > 130 && color.b < 100;
        }

        private static bool IsTopCrimpId(Color32 color)
        {
            return color.r > 180 && color.g > 130 && color.b < 100;
        }

        private static bool IsTitleBandId(Color32 color)
        {
            return color.r < 100 && color.g < 140 && color.b > 180;
        }

        private static bool IsOuterPackId(Color32 color)
        {
            return color.r < 100 && color.g > 150 && color.b < 100;
        }

        private static bool IsLinerId(Color32 color)
        {
            return color.r < 100 && color.g > 120 && color.b > 180;
        }

        private static bool IsCavityId(Color32 color)
        {
            return color.r > 180 && color.g < 120 && color.b < 100;
        }

        private static float Luminance(Color32 color)
        {
            return (color.r * 0.2126f
                + color.g * 0.7152f
                + color.b * 0.0722f) / 255f;
        }

        private static float CurrentEffectIntensity(
            IsolatedR020ProofSequence sequence)
        {
            var block = new MaterialPropertyBlock();
            sequence.TornContour.GetPropertyBlock(block);
            return Mathf.Max(
                sequence.CurrentSample.ContourSweep,
                block.GetFloat(Shader.PropertyToID("_Intensity")));
        }

        private static float ObjectYAtArtworkV(Mesh mesh, float targetV)
        {
            Vector2[] uvs = mesh.uv;
            Vector3[] vertices = mesh.vertices;
            if (uvs.Length != vertices.Length || uvs.Length == 0)
            {
                throw new InvalidOperationException(
                    "R020 front foil has no one-to-one artwork UVs.");
            }
            float nearest = float.PositiveInfinity;
            for (int index = 0; index < uvs.Length; index++)
            {
                nearest = Mathf.Min(nearest, Mathf.Abs(uvs[index].y - targetV));
            }
            float total = 0f;
            int count = 0;
            for (int index = 0; index < uvs.Length; index++)
            {
                if (Mathf.Abs(uvs[index].y - targetV) <= nearest + 0.00001f)
                {
                    total += vertices[index].y;
                    count++;
                }
            }
            if (count == 0)
            {
                throw new InvalidOperationException(
                    "R020 cannot map artwork V to the front foil.");
            }
            return total / count;
        }

        private static Rect Union(IReadOnlyList<Rect> rectangles)
        {
            if (rectangles.Count == 0)
            {
                throw new InvalidOperationException(
                    "R020 physical upper-mouth bounds are empty.");
            }
            Rect result = rectangles[0];
            for (int index = 1; index < rectangles.Count; index++)
            {
                Rect next = rectangles[index];
                result = Rect.MinMaxRect(
                    Mathf.Min(result.xMin, next.xMin),
                    Mathf.Min(result.yMin, next.yMin),
                    Mathf.Max(result.xMax, next.xMax),
                    Mathf.Max(result.yMax, next.yMax));
            }
            return result;
        }

        private static void WriteJson(string path, object value)
        {
            File.WriteAllText(path, JsonUtility.ToJson(value, true) + "\n");
        }

        private static void WriteXml(
            string path,
            string suite,
            IReadOnlyList<Check> checks)
        {
            int failures = checks.Count(check => !check.passed);
            var output = new System.Text.StringBuilder();
            output.AppendLine("<?xml version=\"1.0\" encoding=\"utf-8\"?>");
            output.AppendLine(
                $"<testsuite name=\"{Escape(suite)}\" tests=\"{checks.Count}\" failures=\"{failures}\" errors=\"0\">");
            foreach (Check check in checks)
            {
                output.AppendLine(check.passed
                    ? $"  <testcase name=\"{Escape(check.id)}\" />"
                    : $"  <testcase name=\"{Escape(check.id)}\"><failure message=\"{Escape(check.evidence)}\" /></testcase>");
            }
            output.AppendLine("</testsuite>");
            File.WriteAllText(path, output.ToString());
        }

        private static string Escape(string value)
        {
            return (value ?? string.Empty)
                .Replace("&", "&amp;")
                .Replace("\"", "&quot;")
                .Replace("<", "&lt;")
                .Replace(">", "&gt;");
        }

        [Serializable]
        private sealed class Report
        {
            public string schema;
            public string source;
            public string scene;
            public int width;
            public int height;
            public float visualEffectsIntensity;
            public IsolatedR020OrientationCalibration.Result orientationCalibration;
            public SealedReport sealedState;
            public RenderedCrimpReport sealedRender;
            public TearFrontDirectionReport tearFrontDirection;
            public FormedMouthReport formedMouth;
            public MouthMaterialReport formedMouthMaterials;
            public FormedMouthReport containedMouth;
            public MouthMaterialReport containedMouthMaterials;
            public CaseContainmentReport caseContainment;
            public CaseLegibilityReport caseLegibility;
            public string primaryStaticSheet;
            public int frameBarrierCaptureCount;
            public int frameBarrierAdvancedCount;
            public Check[] checks;
            public bool passed;
        }

        [Serializable]
        private sealed class SealedReport
        {
            public float archiveY;
            public float standardY;
            public float bottomCrimpY;
            public float topCrimpMinY;
            public float topCrimpMaxY;

            public string Summary()
            {
                return $"archive={archiveY:F6}, standard={standardY:F6}, topCrimp={topCrimpMinY:F6}, bottomCrimp={bottomCrimpY:F6}";
            }
        }

        [Serializable]
        private sealed class FormedMouthReport
        {
            public float timeSeconds;
            public RectData packBounds;
            public float upperThirdStart;
            public float lowerThirdEnd;
            public NamedRect[] mouthComponentBounds;
            public RectData upperMouthRegion;
            public bool allMouthBoundsInUpperThird;
            public float frontTopDropMeters;
            public RectData seamBounds;
            public RectData releasedSealBounds;
            public RectData pullTabBounds;
            public Vector2Data releasedSealRootViewport;
            public bool releasedSealIsCompactTopRight;

            public string Summary()
            {
                return $"upperStart={upperThirdStart:F4}, drop={frontTopDropMeters:F6}, strip={releasedSealBounds.Summary()}, root={releasedSealRootViewport.Summary()}";
            }
        }

        [Serializable]
        private sealed class RenderedCrimpReport
        {
            public int topCrimpPixels;
            public RectData topCrimpBounds;
            public float topCrimpLowestViewportY;
            public int titleBandPixels;
            public RectData titleBandBounds;
            public float archiveTitleTopViewportY;
            public int topCrimpStateSetFrame;
            public int topCrimpRenderedAfterFrame;
            public int titleBandStateSetFrame;
            public int titleBandRenderedAfterFrame;

            public string Summary()
            {
                return $"crimpPixels={topCrimpPixels}, titlePixels={titleBandPixels}, crimpBottom={topCrimpLowestViewportY:F5}, titleTop={archiveTitleTopViewportY:F5}";
            }
        }

        [Serializable]
        private sealed class MouthMaterialReport
        {
            public float timeSeconds;
            public int visibleInnerLinerPixels;
            public int visibleCavityPixels;
            public int largestCavityClusterPixels;
            public float innerLinerLuminance;
            public float recessedCavityLuminance;
            public float outerPackLuminance;
            public float backgroundLuminance;
            public float linerCavityLuminanceDelta;
            public float linerOuterLuminanceDelta;
            public float cavityBackgroundLuminanceDelta;
            public int stateSetFrame;
            public int renderedAfterFrame;
            public bool passed;

            public string Summary()
            {
                return $"liner={visibleInnerLinerPixels}, cavity={visibleCavityPixels}, cluster={largestCavityClusterPixels}, liner-cavity={linerCavityLuminanceDelta:F4}, liner-outer={linerOuterLuminanceDelta:F4}, cavity-background={cavityBackgroundLuminanceDelta:F4}";
            }
        }

        [Serializable]
        private sealed class TearFrontDirectionReport
        {
            public float physicalUZeroScreenX;
            public float physicalUOneScreenX;
            public TearFrontState[] states;
            public bool passed;

            public string Summary()
            {
                return $"u0={physicalUZeroScreenX:F4}, u1={physicalUOneScreenX:F4}, states={states?.Length ?? 0}, pass={passed}";
            }
        }

        [Serializable]
        private sealed class TearFrontState
        {
            public float normalizedTearProgress;
            public float normalizedTearFront;
            public int leftEdgeSealPixels;
            public int rightEdgeSealPixels;
            public bool openedSideIsScreenRight;
            public int stateSetFrame;
            public int renderedAfterFrame;
        }

        [Serializable]
        private sealed class CaseContainmentReport
        {
            public bool packVisible;
            public float packDissolve;
            public string caseRootId;
            public string[] caseRendererIds;
            public RectData upperMouthRegion;
            public int unoccludedCasePixelsInUpperMouth;
            public int visibleCasePixelsInUpperMouth;
            public int visibleCasePixelsWithPackInUpperMouth;
            public int occludedCasePixelsByFront;
            public int largestFrontOcclusionClusterPixels;
            public RectData caseProjectedBounds;
            public RectData frontLipProjectedBounds;
            public int frontLipCaseProjectedOverlapPixels;
            public int visibleWithPackStateSetFrame;
            public int visibleWithPackRenderedAfterFrame;
            public int unoccludedStateSetFrame;
            public int unoccludedRenderedAfterFrame;
            public int occludedStateSetFrame;
            public int occludedRenderedAfterFrame;

            public string Summary()
            {
                return $"visible={visibleCasePixelsWithPackInUpperMouth}, lipOcclusion={occludedCasePixelsByFront}, contiguous={largestFrontOcclusionClusterPixels}, projected={frontLipCaseProjectedOverlapPixels}, pack={packVisible}, dissolve={packDissolve:F6}";
            }
        }

        [Serializable]
        private sealed class CaseLegibilityReport
        {
            public int visibleCasePixels;
            public RectData visibleCaseBounds;
            public float averageBoundaryContrast;
            public bool passed;

            public string Summary()
            {
                return $"pixels={visibleCasePixels}, bounds={visibleCaseBounds.Summary()}, contrast={averageBoundaryContrast:F4}";
            }
        }

        [Serializable]
        private sealed class Check
        {
            public Check(string id, bool passed, string evidence)
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
        private sealed class NamedRect
        {
            public NamedRect(string name, Rect rect)
            {
                this.name = name;
                this.rect = rect;
                bounds = RectData.From(rect);
            }

            public string name;
            [NonSerialized] public Rect rect;
            public RectData bounds;
        }

        [Serializable]
        private sealed class FrameCapture
        {
            public float timeSeconds;
            public int stateSetFrame;
            public int renderedAfterFrame;
            [NonSerialized] public Color32[] pixels;
        }

        [Serializable]
        private struct RectData
        {
            public float x;
            public float y;
            public float width;
            public float height;

            public static RectData From(Rect rect)
            {
                return new RectData
                {
                    x = rect.x,
                    y = rect.y,
                    width = rect.width,
                    height = rect.height
                };
            }

            public Rect ToRect()
            {
                return new Rect(x, y, width, height);
            }

            public string Summary()
            {
                return $"{x:F4},{y:F4} {width:F4}x{height:F4}";
            }
        }

        [Serializable]
        private struct Vector2Data
        {
            public float x;
            public float y;

            public static Vector2Data From(Vector2 point)
            {
                return new Vector2Data { x = point.x, y = point.y };
            }

            public string Summary()
            {
                return $"{x:F4},{y:F4}";
            }
        }

        private readonly struct LuminanceSample
        {
            public LuminanceSample(int count, float average)
            {
                this.count = count;
                this.average = average;
            }

            public int count { get; }
            public float average { get; }
        }

        private readonly struct MaskMetrics
        {
            public MaskMetrics(int count, Rect bounds)
            {
                this.count = count;
                this.bounds = bounds;
            }

            public int count { get; }
            public Rect bounds { get; }
        }

        private sealed class FrameLedger
        {
            public int captureCount { get; private set; }
            public int advancedCount { get; private set; }
            public bool AllFramesAdvanced => captureCount > 0
                && captureCount == advancedCount;

            public void Record(int stateSetFrame, int renderedAfterFrame)
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

            public Color32[] Capture(string path)
            {
                RenderPipeline.SubmitRenderRequest(
                    camera,
                    new RenderPipeline.StandardRequest { destination = target });
                RenderTexture previous = RenderTexture.active;
                try
                {
                    RenderTexture.active = target;
                    readback.ReadPixels(
                        new Rect(0f, 0f, Width, Height),
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
    }
}
