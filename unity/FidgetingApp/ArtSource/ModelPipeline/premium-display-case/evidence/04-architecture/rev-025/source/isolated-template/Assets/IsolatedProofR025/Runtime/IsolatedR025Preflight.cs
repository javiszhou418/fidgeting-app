using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R025
{
    public static class IsolatedR025Preflight
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
        private const int MinimumMouthCasePixels = 2048;
        private const int MinimumOccludedCasePixels = 4054;
        private const int MinimumContiguousOcclusionPixels = 4054;
        private const int MinimumVisibleLinerPixels = 384;
        private const int MinimumVisibleCavityPixels = 128;
        private const int MinimumContiguousCavityPixels = 128;
        private const float MinimumLinerCavityLuminanceDelta = 0.050f;
        private const float MinimumLinerOuterLuminanceDelta = 0.035f;
        private const float MinimumCavityBackgroundLuminanceDelta = 0.015f;
        private const float MinimumCaseBoundsWidth = 0.060f;
        private const float MinimumCaseBoundsHeight = 0.035f;
        private const float MinimumCaseBoundaryContrast = 0.040f;
        private const float TargetCountToleranceFraction = 0.15f;
        private const int Expected070LinerPixels = 2912;
        private const int Expected070CavityPixels = 21791;
        private const int Expected090LinerPixels = 3051;
        private const int Expected090CavityPixels = 35001;
        private const float ExpectedFullMaskCaseContrast = 0.174388f;
        private const float FullMaskContrastTolerance = 0.060f;
        private const float TopSealTransitionAllowanceFraction = 0.045f;
        private static readonly float[] StaticSampleSeconds =
        {
            0.50f, 0.70f, 0.90f
        };

        public static IEnumerator Run(
            Camera camera,
            IsolatedR025ProofSequence sequence,
            SkinnedMeshRenderer r017MirrorControlFront,
            string outputRoot,
            string scenePath)
        {
            if (Directory.Exists(outputRoot))
            {
                throw new InvalidOperationException(
                    $"R025 preflight output already exists: {outputRoot}");
            }
            Directory.CreateDirectory(outputRoot);
            Directory.CreateDirectory(Path.Combine(outputRoot, "diagnostics"));

            var report = new Report
            {
                schema = "premium-display-case-gate04-r025-preflight.v1",
                source = "actual isolated Unity 6000.5.6f1 URP 17.5 Play Mode frames",
                scene = scenePath,
                width = Width,
                height = Height,
                visualEffectsIntensity = 0f
            };
            var checks = new List<Check>();
            var ledger = new FrameLedger();
            var sealedMesh = new Mesh { name = "R025_Preflight_Sealed" };
            var formedMesh = new Mesh { name = "R025_Preflight_Formed" };
            var containedMesh = new Mesh { name = "R025_Preflight_Contained" };
            var render = new IsolatedR025PortraitRenderSession(
                camera,
                Width,
                Height);
            report.accounting = new PreflightAccounting
            {
                sourceTopology = MeasureSourceTopology(sequence),
                targetPortraitProjection =
                    new IsolatedR025SegmentDiagnostics.TargetPortraitProjectionReport(),
                beautyFullSizeReview = new BeautyFullSizeReviewAccounting
                {
                    state = "pending-native-size-inspection",
                    width = Width,
                    height = Height,
                    automaticPass = false
                }
            };
            try
            {
                report.orientationCalibration =
                    new IsolatedR025OrientationCalibration.Result();
                yield return IsolatedR025OrientationCalibration.Capture(
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
                yield return IsolatedR025SegmentDiagnostics.Capture(
                    render,
                    sequence,
                    outputRoot,
                    ledger.Record,
                    report.accounting.targetPortraitProjection);

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
                    render,
                    sequence,
                    sealedMesh,
                    formedMesh,
                    0.70f,
                    report.accounting.targetPortraitProjection.At(0.70f));
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
                render,
                sequence,
                sealedMesh,
                containedMesh,
                0.90f,
                report.accounting.targetPortraitProjection.At(0.90f));
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
                    "r025-artwork-identity-wins-calibration",
                    report.orientationCalibration.r025.identityWins,
                    $"margin={report.orientationCalibration.r025.identityMargin:F6}"));
                checks.Add(new Check(
                    "front-winding-faces-calibration-camera",
                    report.orientationCalibration.r025.frontFaceCameraFacing,
                    "R025 front material rendered with Cull Back."));
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
                    "source-topology-is-accounted-separately",
                    report.accounting.sourceTopology.passed,
                    report.accounting.sourceTopology.Summary()));
                checks.Add(new Check(
                    "target-portrait-projection-is-exact",
                    report.accounting.targetPortraitProjection
                        .cameraAspectExactlyTarget
                    && report.accounting.targetPortraitProjection
                        .targetTextureExactlySession,
                    report.accounting.targetPortraitProjection.Summary()));
                checks.Add(new Check(
                    "tear-front-opens-from-screen-right",
                    report.accounting.targetPortraitProjection.directionPassed,
                    report.accounting.targetPortraitProjection.Summary()));
                checks.Add(new Check(
                    "target-aspect-baked-bounds-match-exact-id-masks",
                    report.accounting.targetPortraitProjection
                        .bakedBoundsMatchExactIdMasks,
                    report.accounting.targetPortraitProjection.Summary()));
                checks.Add(new Check(
                    "logical-segment-ranges-match-target-projection",
                    report.accounting.targetPortraitProjection
                        .logicalSegmentRangesMatch,
                    report.accounting.targetPortraitProjection.Summary()));
                checks.Add(new Check(
                    "per-segment-masks-stay-inside-pack-without-bridges",
                    report.accounting.targetPortraitProjection
                        .masksStayInsidePack
                    && report.accounting.targetPortraitProjection
                        .noFullWidthBridge,
                    report.accounting.targetPortraitProjection.Summary()));
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
                    Path.Combine(outputRoot, "r025-preflight-report.json"),
                    report);
                WriteXml(
                    Path.Combine(outputRoot, "r025-preflight-results.xml"),
                    "IsolatedR025Preflight",
                    checks);
                if (!report.passed)
                {
                    throw new InvalidOperationException(
                        "R025 preflight failed. See emitted result XML.");
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
            IsolatedR025PortraitRenderSession render,
            IsolatedR025ProofSequence sequence,
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

        private static IEnumerator CaptureTopSealMasks(
            IsolatedR025PortraitRenderSession render,
            IsolatedR025ProofSequence sequence,
            string outputRoot,
            TopSealMaskReport report,
            FrameLedger ledger)
        {
            SkinnedMeshRenderer[] packRenderers = sequence.PackRenderers.ToArray();
            bool[] enabled = packRenderers.Select(item => item.enabled).ToArray();
            Material[][] materials = packRenderers
                .Select(item => item.sharedMaterials)
                .ToArray();
            var states = new List<TopSealMaskState>(
                StaticSampleSeconds.Length);
            try
            {
                sequence.SetTime(0f, false);
                yield return null;
                if (!sequence.TryGetTopSealPhysicalEdgeViewportPoints(
                        out Vector2 physicalUZero,
                        out Vector2 physicalUOne))
                {
                    throw new InvalidOperationException(
                        "R025 cannot project the top-seal physical-U edges.");
                }
                report.physicalUZeroScreenX = physicalUZero.x;
                report.physicalUOneScreenX = physicalUOne.x;
                foreach (float seconds in StaticSampleSeconds)
                {
                    sequence.SetTime(seconds, false);
                    yield return null;
                    if (!sequence.TryGetPackBodyViewportBounds(
                            out Rect packBounds))
                    {
                        throw new InvalidOperationException(
                            "R025 cannot project Pack bounds for tear direction.");
                    }
                    foreach (SkinnedMeshRenderer renderer in packRenderers)
                    {
                        renderer.enabled = false;
                    }
                    Material sealId = CreateIdMaterial(
                        $"R025TopSealMaskId{seconds:0.000}",
                        new Color(1f, 0.78f, 0.04f, 1f),
                        2490);
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
                            $"diagnostics/top-seal-id-{seconds:0.000}.png"));
                        ledger.Record(stateSetFrame, renderedAfterFrame);
                        states.Add(MeasureTopSealMaskState(
                            seconds,
                            sequence.NormalizedTearProgress,
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
            report.directionPassed = report.physicalUZeroScreenX
                > report.physicalUOneScreenX + 0.010f
                && report.states.Length == StaticSampleSeconds.Length
                && report.states.All(item => item.openedSideIsScreenRight);
            report.sealedSegmentsOnly = report.states.Length
                == StaticSampleSeconds.Length
                && report.states.All(item => item.boundedToSealedSegment);
            report.passed = report.directionPassed
                && report.sealedSegmentsOnly;
        }

        private static TopSealMaskState MeasureTopSealMaskState(
            float seconds,
            float tearProgress,
            float tearFront,
            Rect packBounds,
            IReadOnlyList<Color32> pixels,
            int stateSetFrame,
            int renderedAfterFrame)
        {
            MaskMetrics mask = MeasureMask(pixels, IsTopCrimpId);
            float expectedSealedWidth = packBounds.width * (1f - tearFront);
            float transitionAllowance = packBounds.width
                * TopSealTransitionAllowanceFraction;
            float maximumRight = packBounds.xMax
                - Mathf.Max(0f, tearFront * packBounds.width
                    - transitionAllowance);
            int residualOpenedSidePixels = 0;
            for (int y = 0; y < Height; y++)
            {
                for (int x = 0; x < Width; x++)
                {
                    if (!IsTopCrimpId(pixels[y * Width + x]))
                    {
                        continue;
                    }
                    float normalizedX = x / (float)(Width - 1);
                    if (normalizedX > maximumRight)
                    {
                        residualOpenedSidePixels++;
                    }
                }
            }
            bool hasMask = mask.count >= 64;
            bool noFullWidthBand = hasMask
                && mask.bounds.width < packBounds.width * 0.97f;
            bool boundsFollowSealedSegment = hasMask
                && mask.bounds.xMin <= packBounds.xMin + transitionAllowance
                && mask.bounds.width
                    <= expectedSealedWidth + transitionAllowance;
            bool openedSideIsScreenRight = boundsFollowSealedSegment
                && mask.bounds.xMax <= maximumRight
                && residualOpenedSidePixels == 0;
            return new TopSealMaskState
            {
                timeSeconds = seconds,
                normalizedTearProgress = tearProgress,
                normalizedTearFront = tearFront,
                packBounds = RectData.From(packBounds),
                bounds = RectData.From(mask.bounds),
                occupiedPixels = mask.count,
                occupiedViewportArea = mask.bounds.width * mask.bounds.height,
                expectedSealedWidth = expectedSealedWidth,
                transitionAllowance = transitionAllowance,
                residualOpenedSidePixels = residualOpenedSidePixels,
                noFullWidthBand = noFullWidthBand,
                boundedToSealedSegment = boundsFollowSealedSegment
                    && noFullWidthBand,
                openedSideIsScreenRight = openedSideIsScreenRight,
                stateSetFrame = stateSetFrame,
                renderedAfterFrame = renderedAfterFrame
            };
        }

        private static IEnumerator CaptureComponentSegments(
            IsolatedR025PortraitRenderSession render,
            IsolatedR025ProofSequence sequence,
            string outputRoot,
            TopSealMaskReport topSeal,
            ComponentSegmentReport report,
            FrameLedger ledger)
        {
            SkinnedMeshRenderer[] packRenderers = sequence.PackRenderers.ToArray();
            Renderer[] caseRenderers = sequence.LiveCaseRenderers.ToArray();
            bool[] packEnabled = packRenderers.Select(item => item.enabled).ToArray();
            bool[] caseEnabled = caseRenderers.Select(item => item.enabled).ToArray();
            Material[] topMaterials = sequence.TopSeal.sharedMaterials;
            Material[] linerMaterials = sequence.InnerMouth.sharedMaterials;
            Material[] cavityMaterials = sequence.PackRenderers.Single(
                item => item.name == "Pack_RearInnerFoil").sharedMaterials;
            var states = new List<ComponentSegmentState>(
                StaticSampleSeconds.Length);
            try
            {
                foreach (float seconds in StaticSampleSeconds)
                {
                    sequence.SetTime(seconds, false);
                    yield return null;
                    if (!sequence.TryGetPackBodyViewportBounds(out Rect packBounds))
                    {
                        throw new InvalidOperationException(
                            "R025 cannot project Pack bounds for component diagnostics.");
                    }
                    foreach (SkinnedMeshRenderer renderer in packRenderers)
                    {
                        renderer.enabled = false;
                    }
                    foreach (Renderer renderer in caseRenderers)
                    {
                        renderer.enabled = false;
                    }

                    Material topId = CreateIdMaterial(
                        $"R025TopSealSegmentsId{seconds:0.000}",
                        new Color(1f, 0.78f, 0.04f, 1f),
                        2490);
                    Material linerId = CreateIdMaterial(
                        $"R025InnerLinerSegmentsId{seconds:0.000}",
                        new Color(0.03f, 0.82f, 1f, 1f),
                        2470);
                    Material cavityId = CreateIdMaterial(
                        $"R025CavitySegmentsId{seconds:0.000}",
                        new Color(1f, 0.08f, 0.03f, 1f),
                        2470);
                    try
                    {
                        sequence.TopSeal.enabled = true;
                        sequence.TopSeal.sharedMaterials = Enumerable.Repeat(
                            topId,
                            Mathf.Max(1, topMaterials.Length)).ToArray();
                        int topStateSetFrame = Time.frameCount;
                        yield return null;
                        int topRenderedAfterFrame = Time.frameCount;
                        Color32[] topPixels = render.Capture(Path.Combine(
                            outputRoot,
                            $"diagnostics/top-seal-segments-id-{seconds:0.000}.png"));
                        ledger.Record(topStateSetFrame, topRenderedAfterFrame);
                        MaskMetrics topMask = MeasureMask(topPixels, IsTopCrimpId);

                        sequence.TopSeal.enabled = false;
                        sequence.InnerMouth.enabled = true;
                        sequence.InnerMouth.sharedMaterials = Enumerable.Repeat(
                            linerId,
                            Mathf.Max(1, linerMaterials.Length)).ToArray();
                        int linerStateSetFrame = Time.frameCount;
                        yield return null;
                        int linerRenderedAfterFrame = Time.frameCount;
                        Color32[] linerPixels = render.Capture(Path.Combine(
                            outputRoot,
                            $"diagnostics/inner-liner-segments-id-{seconds:0.000}.png"));
                        ledger.Record(linerStateSetFrame, linerRenderedAfterFrame);
                        MaskMetrics linerMask = MeasureMask(linerPixels, IsLinerId);

                        sequence.InnerMouth.enabled = false;
                        SkinnedMeshRenderer cavity = sequence.PackRenderers.Single(
                            item => item.name == "Pack_RearInnerFoil");
                        cavity.enabled = true;
                        cavity.sharedMaterials = Enumerable.Repeat(
                            cavityId,
                            Mathf.Max(1, cavityMaterials.Length)).ToArray();
                        int cavityStateSetFrame = Time.frameCount;
                        yield return null;
                        int cavityRenderedAfterFrame = Time.frameCount;
                        Color32[] cavityPixels = render.Capture(Path.Combine(
                            outputRoot,
                            $"diagnostics/cavity-back-segments-id-{seconds:0.000}.png"));
                        ledger.Record(cavityStateSetFrame, cavityRenderedAfterFrame);
                        MaskMetrics cavityMask = MeasureMask(cavityPixels, IsCavityId);

                        states.Add(MeasureComponentSegmentState(
                            seconds,
                            sequence.NormalizedTearProgress,
                            sequence.NormalizedTearFront,
                            packBounds,
                            topSeal.physicalUZeroScreenX,
                            topSeal.physicalUOneScreenX,
                            topMask,
                            linerMask,
                            cavityMask,
                            topPixels,
                            linerPixels,
                            cavityPixels,
                            topRenderedAfterFrame,
                            linerRenderedAfterFrame,
                            cavityRenderedAfterFrame));
                    }
                    finally
                    {
                        UnityEngine.Object.Destroy(topId);
                        UnityEngine.Object.Destroy(linerId);
                        UnityEngine.Object.Destroy(cavityId);
                    }
                }
            }
            finally
            {
                sequence.TopSeal.sharedMaterials = topMaterials;
                sequence.InnerMouth.sharedMaterials = linerMaterials;
                sequence.PackRenderers.Single(
                    item => item.name == "Pack_RearInnerFoil").sharedMaterials =
                    cavityMaterials;
                for (int index = 0; index < packRenderers.Length; index++)
                {
                    packRenderers[index].enabled = packEnabled[index];
                }
                for (int index = 0; index < caseRenderers.Length; index++)
                {
                    caseRenderers[index].enabled = caseEnabled[index];
                }
            }
            report.states = states.ToArray();
            report.passed = report.states.Length == StaticSampleSeconds.Length
                && report.states.All(item => item.passed);
        }

        private static ComponentSegmentState MeasureComponentSegmentState(
            float seconds,
            float tearProgress,
            float tearFront,
            Rect packBounds,
            float physicalUZeroScreenX,
            float physicalUOneScreenX,
            MaskMetrics topSeal,
            MaskMetrics liner,
            MaskMetrics cavity,
            IReadOnlyList<Color32> topPixels,
            IReadOnlyList<Color32> linerPixels,
            IReadOnlyList<Color32> cavityPixels,
            int topRenderedAfterFrame,
            int linerRenderedAfterFrame,
            int cavityRenderedAfterFrame)
        {
            float transitionAllowance = packBounds.width
                * TopSealTransitionAllowanceFraction;
            float tearFrontScreenX = Mathf.Lerp(
                physicalUZeroScreenX,
                physicalUOneScreenX,
                tearFront);
            float topExpectedWidth = packBounds.width * (1f - tearFront)
                + transitionAllowance;
            float openedExpectedWidth = packBounds.width * tearFront
                + transitionAllowance;
            int topOpenedPixels = CountMaskPixels(
                topPixels,
                IsTopCrimpId,
                viewportX => viewportX > tearFrontScreenX + transitionAllowance);
            int linerSealedPixels = CountMaskPixels(
                linerPixels,
                IsLinerId,
                viewportX => viewportX < tearFrontScreenX - transitionAllowance);
            int cavitySealedPixels = CountMaskPixels(
                cavityPixels,
                IsCavityId,
                viewportX => viewportX < tearFrontScreenX - transitionAllowance);
            bool topBounded = topSeal.count >= 32
                && topSeal.bounds.xMin >= packBounds.xMin - 0.004f
                && topSeal.bounds.xMax <= tearFrontScreenX + transitionAllowance
                && topSeal.bounds.width <= topExpectedWidth;
            bool linerBounded = liner.count >= 32
                && liner.bounds.xMin >= tearFrontScreenX - transitionAllowance
                && liner.bounds.xMax <= packBounds.xMax + 0.004f
                && liner.bounds.width <= openedExpectedWidth;
            bool cavityBounded = cavity.count >= 64
                && cavity.bounds.xMin >= tearFrontScreenX - transitionAllowance
                && cavity.bounds.xMax <= packBounds.xMax + 0.004f
                && cavity.bounds.width <= openedExpectedWidth;
            bool masksStayInsidePack = topSeal.bounds.xMin
                >= packBounds.xMin - 0.004f
                && topSeal.bounds.xMax <= packBounds.xMax + 0.004f
                && liner.bounds.xMin >= packBounds.xMin - 0.004f
                && liner.bounds.xMax <= packBounds.xMax + 0.004f
                && cavity.bounds.xMin >= packBounds.xMin - 0.004f
                && cavity.bounds.xMax <= packBounds.xMax + 0.004f;
            bool noFullWidthBridge = topSeal.bounds.width
                < packBounds.width * 0.97f
                && liner.bounds.width < packBounds.width * 0.97f
                && cavity.bounds.width < packBounds.width * 0.97f;
            return new ComponentSegmentState
            {
                timeSeconds = seconds,
                normalizedTearProgress = tearProgress,
                normalizedTearFront = tearFront,
                tearFrontScreenX = tearFrontScreenX,
                packBounds = RectData.From(packBounds),
                topSealBounds = RectData.From(topSeal.bounds),
                innerLinerBounds = RectData.From(liner.bounds),
                cavityBackBounds = RectData.From(cavity.bounds),
                topSealPixels = topSeal.count,
                innerLinerPixels = liner.count,
                cavityBackPixels = cavity.count,
                topSealOpenedSidePixels = topOpenedPixels,
                innerLinerSealedSidePixels = linerSealedPixels,
                cavityBackSealedSidePixels = cavitySealedPixels,
                topSealBoundedToSealedSegments = topBounded
                    && topOpenedPixels == 0,
                innerLinerBoundedToOpenedSegments = linerBounded
                    && linerSealedPixels == 0,
                cavityBackBoundedToOpenedSegments = cavityBounded
                    && cavitySealedPixels == 0,
                masksStayInsidePack = masksStayInsidePack,
                noFullWidthBridge = noFullWidthBridge,
                topSealRenderedAfterFrame = topRenderedAfterFrame,
                innerLinerRenderedAfterFrame = linerRenderedAfterFrame,
                cavityBackRenderedAfterFrame = cavityRenderedAfterFrame,
                passed = topBounded
                    && linerBounded
                    && cavityBounded
                    && masksStayInsidePack
                    && noFullWidthBridge
                    && topOpenedPixels == 0
                    && linerSealedPixels == 0
                    && cavitySealedPixels == 0
            };
        }

        private static int CountMaskPixels(
            IReadOnlyList<Color32> pixels,
            Func<Color32, bool> matcher,
            Func<float, bool> matchesX)
        {
            int count = 0;
            for (int y = 0; y < Height; y++)
            {
                for (int x = 0; x < Width; x++)
                {
                    if (matcher(pixels[y * Width + x])
                        && matchesX(x / (float)(Width - 1)))
                    {
                        count++;
                    }
                }
            }
            return count;
        }

        private static void BuildPrimaryStaticSheet(
            string path,
            params IReadOnlyList<Color32>[] frames)
        {
            if (frames.Length != 4 || frames.Any(frame =>
                    frame == null || frame.Count != Width * Height))
            {
                throw new InvalidOperationException(
                    "R025 primary sheet requires four full Unity frames.");
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
            IsolatedR025PortraitRenderSession render,
            IsolatedR025ProofSequence sequence,
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
                "R025TopCrimpId",
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
            IsolatedR025PortraitRenderSession render,
            IsolatedR025ProofSequence sequence,
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
                "R025OuterPackId",
                new Color(0.02f, 0.92f, 0.14f, 1f),
                2460);
            Material topSealId = CreateIdMaterial(
                "R025TopSealMouthId",
                new Color(0.02f, 0.92f, 0.14f, 1f),
                2460);
            Material linerId = CreateIdMaterial(
                "R025InnerLinerId",
                new Color(0.03f, 0.82f, 1f, 1f),
                2470);
            Material cavityId = CreateIdMaterial(
                "R025CavityId",
                new Color(1f, 0.08f, 0.03f, 1f),
                2470);
            Material lipId = CreateIdMaterial(
                "R025LipId",
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
            IsolatedR025ProofSequence sequence,
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

        private static SourceTopologyAccounting MeasureSourceTopology(
            IsolatedR025ProofSequence sequence)
        {
            SkinnedMeshRenderer[] renderers = sequence.PackRenderers.ToArray();
            bool identityLocalTransforms = renderers.All(renderer =>
                renderer.transform.localPosition.sqrMagnitude <= 0.0000000001f
                && Quaternion.Angle(
                    renderer.transform.localRotation,
                    Quaternion.identity) <= 0.0001f
                && (renderer.transform.localScale - Vector3.one).sqrMagnitude
                    <= 0.0000000001f);
            bool noArmatureOrBindPoses = renderers.All(renderer =>
                renderer.rootBone == null
                && renderer.bones.Length == 0
                && renderer.sharedMesh.bindposes.Length == 0);
            bool correctShapeCount = renderers.All(renderer =>
                renderer.sharedMesh.blendShapeCount
                    == IsolatedR025ProofSequence.ExpectedBlendShapeCount);
            return new SourceTopologyAccounting
            {
                sourceRigPath =
                    "Assets/Source/R024/PackOpeningGate04R024PackOnlyRig.fbx",
                expectedSegmentCount = 48,
                rendererCount = renderers.Length,
                identityLocalTransforms = identityLocalTransforms,
                noArmatureOrBindPoses = noArmatureOrBindPoses,
                correctShapeCount = correctShapeCount,
                passed = renderers.Length
                    == IsolatedR025ProofSequence.ExpectedRendererCount
                    && identityLocalTransforms
                    && noArmatureOrBindPoses
                    && correctShapeCount
            };
        }

        private static FormedMouthReport MeasureMouth(
            IsolatedR025PortraitRenderSession render,
            IsolatedR025ProofSequence sequence,
            Mesh sealedMesh,
            Mesh openedMesh,
            float seconds,
            IsolatedR025SegmentDiagnostics.StaticSegmentState
                targetPortraitState)
        {
            render.PrepareForMeasurement();
            if (!sequence.TryGetPackBodyViewportBounds(out Rect packBounds))
            {
                throw new InvalidOperationException(
                    "R025 cannot project Pack body bounds.");
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
                        $"R025 cannot project mouth renderer: {renderer.name}");
                }
                mouthBounds.Add(new NamedRect(renderer.name, bounds));
            }
            mouthBounds.Add(new NamedRect(
                "Pack_TopSealRemaining",
                targetPortraitState.Component("top-seal")
                    .exactIdBounds.ToRect()));
            NamedRect strip = mouthBounds.Single(
                item => item.name == "Pack_ReleasedSealStrip");
            NamedRect tab = mouthBounds.Single(
                item => item.name == "Pack_TopRightPullTab");

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
                Mathf.Min(
                    1f,
                    Mathf.Max(
                        upperMouth.yMax,
                        strip.rect.yMax,
                        tab.rect.yMax) + 0.006f));

            NamedRect seam = mouthBounds.Single(
                item => item.name == "Pack_TopSealRemaining");
            if (!sequence.TryGetRendererVertexViewportPoint(
                    sequence.ReleasedSealStrip,
                    0,
                    out Vector2 stripRoot))
            {
                throw new InvalidOperationException(
                    "R025 cannot project the released strip root.");
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
            IsolatedR025ProofSequence sequence)
        {
            if (!sequence.TryGetPackBodyViewportBounds(out Rect packBounds))
            {
                throw new InvalidOperationException(
                    "R025 cannot project Pack body bounds.");
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
                        $"R025 cannot project mouth renderer: {renderer.name}");
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
            IsolatedR025PortraitRenderSession render,
            IsolatedR025ProofSequence sequence,
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
            Material[][] caseIds = caseMaterials
                .Select((materials, rendererIndex) =>
                    CreateQueueConsistentCaseIds(
                        materials,
                        rendererIndex))
                .ToArray();
            Material frontId = CreateIdMaterial(
                "R025FrontLipAndSidewallId",
                new Color(1f, 0.85f, 0.02f, 1f),
                2480);
            try
            {
                for (int index = 0; index < caseRenderers.Length; index++)
                {
                    caseRenderers[index].sharedMaterials = caseIds[index];
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
                    caseIds.SelectMany(materials =>
                        materials.Select(material => material.renderQueue))
                        .Distinct()
                        .OrderBy(queue => queue)
                        .ToArray(),
                    legibility);
                render.PrepareForMeasurement();
                if (!sequence.TryGetCaseViewportBounds(
                        out Rect caseProjectedBounds)
                    || !sequence.TryGetRendererViewportBounds(
                        sequence.RolledCrimpLip,
                        out Rect lipProjectedBounds))
                {
                    throw new InvalidOperationException(
                        "R025 cannot project the case and front lip.");
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
                foreach (Material material in caseIds.SelectMany(
                    materials => materials))
                {
                    UnityEngine.Object.Destroy(material);
                }
                UnityEngine.Object.Destroy(frontId);
            }
        }

        private static Material[] CreateQueueConsistentCaseIds(
            IReadOnlyList<Material> source,
            int rendererIndex)
        {
            if (source.Count == 0)
            {
                return new[]
                {
                    CreateIdMaterial(
                        $"R025LiveCaseId{rendererIndex:D2}Fallback",
                        new Color(1f, 0.02f, 1f, 1f),
                        3000)
                };
            }
            return source.Select((material, materialIndex) =>
                CreateIdMaterial(
                    $"R025LiveCaseId{rendererIndex:D2}_{materialIndex:D2}",
                    new Color(1f, 0.02f, 1f, 1f),
                    material == null || material.renderQueue < 0
                        ? 3000
                        : material.renderQueue)).ToArray();
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
            IReadOnlyList<int> queueConsistentMaskQueues,
            CaseLegibilityReport result)
        {
            CaseMaskMeasurement targetMouth = MeasureCaseMask(
                beauty,
                caseIds,
                upperMouth);
            CaseMaskMeasurement fullTarget = MeasureCaseMask(
                beauty,
                caseIds,
                new Rect(0f, 0f, 1f, 1f));
            result.targetSpaceMouthRegion = RectData.From(upperMouth);
            result.queueConsistentMaskQueues =
                queueConsistentMaskQueues.ToArray();
            result.queueConsistentMask = result.queueConsistentMaskQueues
                .Contains(3000)
                && result.queueConsistentMaskQueues
                    .Any(queue => queue >= 3020);
            result.visibleCasePixels = targetMouth.count;
            result.visibleCaseBounds = RectData.From(targetMouth.bounds);
            result.averageBoundaryContrast = targetMouth.averageBoundaryContrast;
            result.fullTargetMaskPixels = fullTarget.count;
            result.fullTargetMaskBounds = RectData.From(fullTarget.bounds);
            result.fullTargetMaskContrast = fullTarget.averageBoundaryContrast;
            result.targetMouthContainsEntireLiveMask =
                targetMouth.count == fullTarget.count;
            result.fullTargetMaskMatchesExpectedContrast =
                Mathf.Abs(fullTarget.averageBoundaryContrast
                    - ExpectedFullMaskCaseContrast)
                <= FullMaskContrastTolerance;
            result.passed = targetMouth.count >= MinimumMouthCasePixels
                && targetMouth.bounds.width >= MinimumCaseBoundsWidth
                && targetMouth.bounds.height >= MinimumCaseBoundsHeight
                && targetMouth.averageBoundaryContrast
                    >= MinimumCaseBoundaryContrast
                && result.targetMouthContainsEntireLiveMask
                && result.queueConsistentMask
                && result.fullTargetMaskMatchesExpectedContrast;
        }

        private static CaseMaskMeasurement MeasureCaseMask(
            IReadOnlyList<Color32> beauty,
            IReadOnlyList<Color32> caseIds,
            Rect region)
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
                        || !region.Contains(
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
                    if (!mask[index - 1])
                    {
                        contrastTotal += Mathf.Abs(
                            current - Luminance(beauty[index - 1]));
                        contrastCount++;
                    }
                    if (!mask[index + 1])
                    {
                        contrastTotal += Mathf.Abs(
                            current - Luminance(beauty[index + 1]));
                        contrastCount++;
                    }
                    if (!mask[index - Width])
                    {
                        contrastTotal += Mathf.Abs(
                            current - Luminance(beauty[index - Width]));
                        contrastCount++;
                    }
                    if (!mask[index + Width])
                    {
                        contrastTotal += Mathf.Abs(
                            current - Luminance(beauty[index + Width]));
                        contrastCount++;
                    }
                }
            }
            return new CaseMaskMeasurement(
                count,
                count == 0
                    ? Rect.zero
                    : Rect.MinMaxRect(minX, minY, maxX, maxY),
                contrastCount == 0 ? 0f : contrastTotal / contrastCount);
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
                    "URP Unlit shader is unavailable for R025 diagnostics.");
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

        private static Material CreateTitleBandMaterial(Texture artwork)
        {
            if (artwork == null)
            {
                throw new MissingReferenceException(
                    "R025 cannot create the rendered title-band diagnostic.");
            }
            Shader shader = Shader.Find(
                "FidgetingApp/Isolated/R025/RenderedBandMaskUnlit");
            if (shader == null)
            {
                throw new MissingReferenceException(
                    "R025 rendered title-band shader is unavailable.");
            }
            var material = new Material(shader)
            {
                name = "R025ArchiveTitleBandId",
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
            (int expectedLiner, int expectedCavity) = seconds < 0.80f
                ? (Expected070LinerPixels, Expected070CavityPixels)
                : (Expected090LinerPixels, Expected090CavityPixels);
            report.expectedLinerPixels = expectedLiner;
            report.expectedCavityPixels = expectedCavity;
            report.targetCountsApproximatelyMatch = WithinFraction(
                liner.count,
                expectedLiner,
                TargetCountToleranceFraction)
                && WithinFraction(
                    cavity.count,
                    expectedCavity,
                    TargetCountToleranceFraction);
            report.passed = liner.count >= MinimumVisibleLinerPixels
                && cavity.count >= MinimumVisibleCavityPixels
                && report.largestCavityClusterPixels
                    >= MinimumContiguousCavityPixels
                && report.linerCavityLuminanceDelta
                    >= MinimumLinerCavityLuminanceDelta
                && report.linerOuterLuminanceDelta
                    >= MinimumLinerOuterLuminanceDelta
                && report.cavityBackgroundLuminanceDelta
                    >= MinimumCavityBackgroundLuminanceDelta
                && report.targetCountsApproximatelyMatch;
        }

        private static bool WithinFraction(
            int actual,
            int expected,
            float fraction) =>
            Mathf.Abs(actual - expected) <= Mathf.CeilToInt(expected * fraction);

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
            IsolatedR025ProofSequence sequence)
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
                    "R025 front foil has no one-to-one artwork UVs.");
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
                    "R025 cannot map artwork V to the front foil.");
            }
            return total / count;
        }

        private static Rect Union(IReadOnlyList<Rect> rectangles)
        {
            if (rectangles.Count == 0)
            {
                throw new InvalidOperationException(
                    "R025 physical upper-mouth bounds are empty.");
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
            public PreflightAccounting accounting;
            public IsolatedR025OrientationCalibration.Result orientationCalibration;
            public SealedReport sealedState;
            public RenderedCrimpReport sealedRender;
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
        private sealed class PreflightAccounting
        {
            public SourceTopologyAccounting sourceTopology;
            public IsolatedR025SegmentDiagnostics.TargetPortraitProjectionReport
                targetPortraitProjection;
            public BeautyFullSizeReviewAccounting beautyFullSizeReview;
        }

        [Serializable]
        private sealed class SourceTopologyAccounting
        {
            public string sourceRigPath;
            public int expectedSegmentCount;
            public int rendererCount;
            public bool identityLocalTransforms;
            public bool noArmatureOrBindPoses;
            public bool correctShapeCount;
            public bool passed;

            public string Summary() =>
                $"segments={expectedSegmentCount}, renderers={rendererCount}, identity={identityLocalTransforms}, noRig={noArmatureOrBindPoses}, shapes={correctShapeCount}";
        }

        [Serializable]
        private sealed class BeautyFullSizeReviewAccounting
        {
            public string state;
            public int width;
            public int height;
            public bool automaticPass;
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
            public int expectedLinerPixels;
            public int expectedCavityPixels;
            public bool targetCountsApproximatelyMatch;
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
                return $"liner={visibleInnerLinerPixels}/{expectedLinerPixels}, cavity={visibleCavityPixels}/{expectedCavityPixels}, counts={targetCountsApproximatelyMatch}, cluster={largestCavityClusterPixels}, liner-cavity={linerCavityLuminanceDelta:F4}, liner-outer={linerOuterLuminanceDelta:F4}, cavity-background={cavityBackgroundLuminanceDelta:F4}";
            }
        }

        [Serializable]
        private sealed class TopSealMaskReport
        {
            public float physicalUZeroScreenX;
            public float physicalUOneScreenX;
            public TopSealMaskState[] states;
            public bool directionPassed;
            public bool sealedSegmentsOnly;
            public bool passed;

            public TopSealMaskState At(float seconds)
            {
                TopSealMaskState result = states?.SingleOrDefault(
                    item => Mathf.Abs(item.timeSeconds - seconds) < 0.0001f);
                if (result == null)
                {
                    throw new InvalidOperationException(
                        $"R025 lacks a top-seal mask at t={seconds:F3}.");
                }
                return result;
            }

            public string Summary()
            {
                return $"u0={physicalUZeroScreenX:F4}, u1={physicalUOneScreenX:F4}, states={states?.Length ?? 0}, direction={directionPassed}, sealed={sealedSegmentsOnly}";
            }
        }

        [Serializable]
        private sealed class TopSealMaskState
        {
            public float timeSeconds;
            public float normalizedTearProgress;
            public float normalizedTearFront;
            public RectData packBounds;
            public RectData bounds;
            public int occupiedPixels;
            public float occupiedViewportArea;
            public float expectedSealedWidth;
            public float transitionAllowance;
            public int residualOpenedSidePixels;
            public bool noFullWidthBand;
            public bool boundedToSealedSegment;
            public bool openedSideIsScreenRight;
            public int stateSetFrame;
            public int renderedAfterFrame;
        }

        [Serializable]
        private sealed class ComponentSegmentReport
        {
            public ComponentSegmentState[] states;
            public bool passed;

            public string Summary()
            {
                return $"states={states?.Length ?? 0}, pass={passed}";
            }
        }

        [Serializable]
        private sealed class ComponentSegmentState
        {
            public float timeSeconds;
            public float normalizedTearProgress;
            public float normalizedTearFront;
            public float tearFrontScreenX;
            public RectData packBounds;
            public RectData topSealBounds;
            public RectData innerLinerBounds;
            public RectData cavityBackBounds;
            public int topSealPixels;
            public int innerLinerPixels;
            public int cavityBackPixels;
            public int topSealOpenedSidePixels;
            public int innerLinerSealedSidePixels;
            public int cavityBackSealedSidePixels;
            public bool topSealBoundedToSealedSegments;
            public bool innerLinerBoundedToOpenedSegments;
            public bool cavityBackBoundedToOpenedSegments;
            public bool masksStayInsidePack;
            public bool noFullWidthBridge;
            public int topSealRenderedAfterFrame;
            public int innerLinerRenderedAfterFrame;
            public int cavityBackRenderedAfterFrame;
            public bool passed;
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
            public RectData targetSpaceMouthRegion;
            public int[] queueConsistentMaskQueues;
            public bool queueConsistentMask;
            public int visibleCasePixels;
            public RectData visibleCaseBounds;
            public float averageBoundaryContrast;
            public int fullTargetMaskPixels;
            public RectData fullTargetMaskBounds;
            public float fullTargetMaskContrast;
            public bool targetMouthContainsEntireLiveMask;
            public bool fullTargetMaskMatchesExpectedContrast;
            public bool passed;

            public string Summary()
            {
                return $"pixels={visibleCasePixels}/{fullTargetMaskPixels}, mouth={targetMouthContainsEntireLiveMask}, queues={string.Join(",", queueConsistentMaskQueues ?? Array.Empty<int>())}, contrast={averageBoundaryContrast:F6}/{fullTargetMaskContrast:F6}, expected={ExpectedFullMaskCaseContrast:F6}";
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

        private readonly struct CaseMaskMeasurement
        {
            public CaseMaskMeasurement(
                int count,
                Rect bounds,
                float averageBoundaryContrast)
            {
                this.count = count;
                this.bounds = bounds;
                this.averageBoundaryContrast = averageBoundaryContrast;
            }

            public int count { get; }
            public Rect bounds { get; }
            public float averageBoundaryContrast { get; }
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

    }
}
