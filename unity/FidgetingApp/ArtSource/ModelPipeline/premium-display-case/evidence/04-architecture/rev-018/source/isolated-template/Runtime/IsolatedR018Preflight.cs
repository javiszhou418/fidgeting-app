using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R018
{
    public static class IsolatedR018Preflight
    {
        private const int Width = 1206;
        private const int Height = 2622;
        private const float ArchiveArtworkV = 0.735f;
        private const float StandardArtworkV = 0.215f;
        private const float PhysicalTopArtworkV = 0.815f;
        private const float BottomCrimpArtworkV = 0.060f;
        private const float MinimumTopDropMeters = 0.005f;
        private const int MinimumMouthCasePixels = 256;
        private const int MinimumOccludedCasePixels = 16;

        public static IEnumerator Run(
            Camera camera,
            IsolatedR018ProofSequence sequence,
            SkinnedMeshRenderer r017MirrorControlFront,
            string outputRoot,
            string scenePath)
        {
            if (Directory.Exists(outputRoot))
            {
                throw new InvalidOperationException(
                    $"R018 preflight output already exists: {outputRoot}");
            }
            Directory.CreateDirectory(outputRoot);
            Directory.CreateDirectory(Path.Combine(outputRoot, "diagnostics"));

            var report = new Report
            {
                schema = "premium-display-case-gate04-r018-preflight.v1",
                source = "actual isolated Unity 6000.5.6f1 URP 17.5 Play Mode frames",
                scene = scenePath,
                width = Width,
                height = Height,
                visualEffectsIntensity = 0f
            };
            var checks = new List<Check>();
            var ledger = new FrameLedger();
            var sealedMesh = new Mesh { name = "R018_Preflight_Sealed" };
            var formedMesh = new Mesh { name = "R018_Preflight_Formed" };
            var render = new RenderSession(camera);
            try
            {
                report.orientationCalibration =
                    new IsolatedR018OrientationCalibration.Result();
                yield return IsolatedR018OrientationCalibration.Capture(
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

                var formedFrame = new FrameCapture();
                yield return CaptureFrame(
                    render,
                    sequence,
                    0.70f,
                    Path.Combine(outputRoot, "formed-mouth-070.png"),
                    formedFrame,
                    ledger);
                sequence.BakeFrontFoil(formedMesh);
                report.formedMouth = MeasureFormedMouth(
                    sequence,
                    sealedMesh,
                    formedMesh);

                var containedFrame = new FrameCapture();
                yield return CaptureFrame(
                    render,
                    sequence,
                    0.90f,
                    Path.Combine(outputRoot, "case-contained-090.png"),
                    containedFrame,
                    ledger);
                report.caseContainment = new CaseContainmentReport
                {
                    packVisible = sequence.PackVisible,
                    packDissolve = sequence.CurrentSample.PackDissolve,
                    caseRootId = sequence.CaseRootId.ToString(),
                    caseRendererIds = sequence.CaseRendererIds
                        .Select(item => item.ToString())
                        .ToArray(),
                    upperMouthRegion = RectData.From(
                        MeasureUpperMouthRegion(sequence))
                };
                yield return CaptureCaseOcclusion(
                    render,
                    sequence,
                    report.caseContainment.upperMouthRegion.ToRect(),
                    outputRoot,
                    report.caseContainment,
                    ledger);

                report.frameBarrierCaptureCount = ledger.captureCount;
                report.frameBarrierAdvancedCount = ledger.advancedCount;
                report.visualEffectsIntensity = CurrentEffectIntensity(sequence);

                checks.Add(new Check(
                    "r017-mirror-regression-is-observed",
                    report.orientationCalibration.r017MirrorRegressionObserved,
                    "The immutable R017 control must select horizontal-flip."));
                checks.Add(new Check(
                    "r018-artwork-identity-wins-calibration",
                    report.orientationCalibration.r018.identityWins,
                    $"margin={report.orientationCalibration.r018.identityMargin:F6}"));
                checks.Add(new Check(
                    "front-winding-faces-calibration-camera",
                    report.orientationCalibration.r018.frontFaceCameraFacing,
                    "R018 front material rendered with Cull Back."));
                checks.Add(new Check(
                    "sealed-artwork-maps-archive-above-standard",
                    report.sealedState.archiveY
                        > report.sealedState.standardY + 0.10f,
                    report.sealedState.Summary()));
                checks.Add(new Check(
                    "sealed-top-crimp-is-above-fidget-archive",
                    report.sealedState.topCrimpMinY
                        > report.sealedState.archiveY,
                    report.sealedState.Summary()));
                checks.Add(new Check(
                    "sealed-bottom-crimp-is-below-standard",
                    report.sealedState.bottomCrimpY
                        < report.sealedState.standardY,
                    report.sealedState.Summary()));
                checks.Add(new Check(
                    "formed-mouth-bounds-stay-in-upper-third",
                    report.formedMouth.allMouthBoundsInUpperThird,
                    report.formedMouth.Summary()));
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
                        && report.caseContainment.occludedCasePixelsByFront
                            >= MinimumOccludedCasePixels,
                    report.caseContainment.Summary()));
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
                    Path.Combine(outputRoot, "r018-preflight-report.json"),
                    report);
                WriteXml(
                    Path.Combine(outputRoot, "r018-preflight-results.xml"),
                    "IsolatedR018Preflight",
                    checks);
                if (!report.passed)
                {
                    throw new InvalidOperationException(
                        "R018 preflight failed. See emitted result XML.");
                }
            }
            finally
            {
                render.Dispose();
                UnityEngine.Object.Destroy(sealedMesh);
                UnityEngine.Object.Destroy(formedMesh);
            }
        }

        private static IEnumerator CaptureFrame(
            RenderSession render,
            IsolatedR018ProofSequence sequence,
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

        private static SealedReport MeasureSealed(
            IsolatedR018ProofSequence sequence,
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

        private static FormedMouthReport MeasureFormedMouth(
            IsolatedR018ProofSequence sequence,
            Mesh sealedMesh,
            Mesh formedMesh)
        {
            if (!sequence.TryGetPackBodyViewportBounds(out Rect packBounds))
            {
                throw new InvalidOperationException(
                    "R018 cannot project Pack body bounds.");
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
                        $"R018 cannot project mouth renderer: {renderer.name}");
                }
                mouthBounds.Add(new NamedRect(renderer.name, bounds));
            }

            Rect upperMouth = Union(
                mouthBounds.Where(item =>
                    item.name == "Pack_InnerFoilMouth"
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
            float horizontalGap = Mathf.Max(
                0f,
                Mathf.Max(tab.rect.xMin - strip.rect.xMax,
                    strip.rect.xMin - tab.rect.xMax));
            float verticalGap = Mathf.Max(
                0f,
                Mathf.Max(tab.rect.yMin - strip.rect.yMax,
                    strip.rect.yMin - tab.rect.yMax));
            float topDrop = ObjectYAtArtworkV(
                sealedMesh,
                PhysicalTopArtworkV)
                - ObjectYAtArtworkV(formedMesh, PhysicalTopArtworkV);
            bool allUpper = mouthBounds.All(
                item => item.rect.yMin >= upperThirdStart);
            bool compactStrip = strip.rect.xMin
                    >= packBounds.xMin + packBounds.width * 0.55f
                && strip.rect.yMin >= upperThirdStart
                && strip.rect.width <= packBounds.width * 0.34f
                && strip.rect.height <= packBounds.height * 0.30f
                && Mathf.Sqrt(horizontalGap * horizontalGap
                    + verticalGap * verticalGap)
                    <= packBounds.width * 0.20f;
            return new FormedMouthReport
            {
                timeSeconds = 0.70f,
                packBounds = RectData.From(packBounds),
                upperThirdStart = upperThirdStart,
                lowerThirdEnd = lowerThirdEnd,
                mouthComponentBounds = mouthBounds.ToArray(),
                upperMouthRegion = RectData.From(upperMouth),
                allMouthBoundsInUpperThird = allUpper,
                frontTopDropMeters = topDrop,
                releasedSealBounds = RectData.From(strip.rect),
                pullTabBounds = RectData.From(tab.rect),
                releasedSealIsCompactTopRight = compactStrip
            };
        }

        private static Rect MeasureUpperMouthRegion(
            IsolatedR018ProofSequence sequence)
        {
            if (!sequence.TryGetPackBodyViewportBounds(out Rect packBounds))
            {
                throw new InvalidOperationException(
                    "R018 cannot project Pack body bounds.");
            }
            float upperThirdStart = packBounds.yMin + packBounds.height * 2f / 3f;
            var components = new[]
            {
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
                        $"R018 cannot project mouth renderer: {renderer.name}");
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
            IsolatedR018ProofSequence sequence,
            Rect upperMouth,
            string outputRoot,
            CaseContainmentReport report,
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
                "R018LiveCaseId",
                new Color(1f, 0.02f, 1f, 1f));
            Material frontId = CreateIdMaterial(
                "R018FrontLipAndSidewallId",
                new Color(1f, 0.85f, 0.02f, 1f));
            try
            {
                foreach (SkinnedMeshRenderer renderer in packRenderers)
                {
                    renderer.enabled = false;
                }
                for (int index = 0; index < caseRenderers.Length; index++)
                {
                    int count = Mathf.Max(1, caseMaterials[index].Length);
                    caseRenderers[index].sharedMaterials = Enumerable.Repeat(
                        caseId,
                        count).ToArray();
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
                    occluded,
                    upperMouth,
                    report);
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
            IReadOnlyList<Color32> occluded,
            Rect upperMouth,
            CaseContainmentReport result)
        {
            int visibleInside = 0;
            int coveredByFront = 0;
            int unoccludedInside = 0;
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
                        }
                    }
                    if (IsCaseId(occluded[index]) && insideMouth)
                    {
                        visibleInside++;
                    }
                }
            }
            result.unoccludedCasePixelsInUpperMouth = unoccludedInside;
            result.visibleCasePixelsInUpperMouth = visibleInside;
            result.occludedCasePixelsByFront = coveredByFront;
        }

        private static Material CreateIdMaterial(string name, Color color)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Unlit");
            if (shader == null)
            {
                throw new MissingReferenceException(
                    "URP Unlit shader is unavailable for R018 diagnostics.");
            }
            var material = new Material(shader)
            {
                name = name,
                renderQueue = 2475
            };
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Cull", 0f);
            return material;
        }

        private static bool IsCaseId(Color32 color)
        {
            return color.r > 180 && color.g < 100 && color.b > 180;
        }

        private static bool IsFrontId(Color32 color)
        {
            return color.r > 180 && color.g > 130 && color.b < 100;
        }

        private static float CurrentEffectIntensity(
            IsolatedR018ProofSequence sequence)
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
                    "R018 front foil has no one-to-one artwork UVs.");
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
                    "R018 cannot map artwork V to the front foil.");
            }
            return total / count;
        }

        private static Rect Union(IReadOnlyList<Rect> rectangles)
        {
            if (rectangles.Count == 0)
            {
                throw new InvalidOperationException(
                    "R018 physical upper-mouth bounds are empty.");
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
            public IsolatedR018OrientationCalibration.Result orientationCalibration;
            public SealedReport sealedState;
            public FormedMouthReport formedMouth;
            public CaseContainmentReport caseContainment;
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
            public RectData releasedSealBounds;
            public RectData pullTabBounds;
            public bool releasedSealIsCompactTopRight;

            public string Summary()
            {
                return $"upperStart={upperThirdStart:F4}, drop={frontTopDropMeters:F6}, strip={releasedSealBounds.Summary()}";
            }
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
            public int occludedCasePixelsByFront;
            public int unoccludedStateSetFrame;
            public int unoccludedRenderedAfterFrame;
            public int occludedStateSetFrame;
            public int occludedRenderedAfterFrame;

            public string Summary()
            {
                return $"visible={visibleCasePixelsInUpperMouth}, occluded={occludedCasePixelsByFront}, pack={packVisible}, dissolve={packDissolve:F6}";
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
