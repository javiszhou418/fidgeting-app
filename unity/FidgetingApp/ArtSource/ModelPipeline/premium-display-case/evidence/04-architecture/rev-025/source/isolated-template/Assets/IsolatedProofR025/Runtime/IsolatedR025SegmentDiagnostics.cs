using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R025
{
    internal static class IsolatedR025SegmentDiagnostics
    {
        private const int Width = IsolatedR025ProofCapture.Width;
        private const int Height = IsolatedR025ProofCapture.Height;
        private const int SegmentCount = 48;
        private const float PackLeftMeters = -0.1275f;
        private const float PackWidthMeters = 0.255f;
        private const float SegmentWidthMeters = PackWidthMeters / SegmentCount;
        private const float DegenerateTriangleAreaSquared = 0.000000000001f;
        private const float LocalSegmentAllowanceMeters = 0.00002f;
        private const float ProjectionAllowance = 0.0015f;
        private static readonly float[] StaticSampleSeconds =
        {
            0.50f, 0.70f, 0.90f
        };

        private static readonly ComponentSpec[] Components =
        {
            new(
                "top-seal",
                sequence => sequence.TopSeal,
                new Color32(255, 199, 10, 255),
                true),
            new(
                "inner-liner",
                sequence => sequence.InnerMouth,
                new Color32(8, 209, 255, 255),
                false),
            new(
                "cavity-back",
                sequence => sequence.PackRenderers.Single(
                    renderer => renderer.name == "Pack_RearInnerFoil"),
                new Color32(255, 20, 8, 255),
                false)
        };

        private static readonly Color32 PackColor =
            new(5, 235, 36, 255);

        public static IEnumerator Capture(
            IsolatedR025PortraitRenderSession render,
            IsolatedR025ProofSequence sequence,
            string outputRoot,
            Action<int, int> recordCapture,
            TargetPortraitProjectionReport report)
        {
            if (render == null)
            {
                throw new ArgumentNullException(nameof(render));
            }
            if (sequence == null)
            {
                throw new ArgumentNullException(nameof(sequence));
            }
            if (recordCapture == null)
            {
                throw new ArgumentNullException(nameof(recordCapture));
            }
            if (report == null)
            {
                throw new ArgumentNullException(nameof(report));
            }

            render.PrepareForMeasurement();
            sequence.SetTime(0f, false);
            yield return null;
            render.PrepareForMeasurement();
            if (!sequence.TryGetTopSealPhysicalEdgeViewportPoints(
                    out Vector2 physicalUZero,
                    out Vector2 physicalUOne))
            {
                throw new InvalidOperationException(
                    "R025 cannot project the physical top-seal edges.");
            }

            report.width = render.Width;
            report.height = render.Height;
            report.targetAspect = render.TargetAspect;
            report.cameraAspectBeforeSession = render.OriginalAspect;
            report.cameraAspect = render.Camera.aspect;
            report.cameraAspectExactlyTarget =
                render.AspectExactlyMatchesTarget;
            report.targetTextureExactlySession =
                render.TargetExactlyMatchesSession;
            report.transitionAllowance = ProjectionAllowance;
            report.physicalUZeroScreenX = physicalUZero.x;
            report.physicalUOneScreenX = physicalUOne.x;
            report.directionPassed = physicalUZero.x
                > physicalUOne.x + 0.010f;

            var states = new List<StaticSegmentState>(
                StaticSampleSeconds.Length);
            Renderer[] caseRenderers = sequence.LiveCaseRenderers.ToArray();
            bool[] caseEnabled = caseRenderers
                .Select(renderer => renderer.enabled)
                .ToArray();
            var packEnvelope = new PackEnvelope();
            try
            {
                foreach (Renderer renderer in caseRenderers)
                {
                    renderer.enabled = false;
                }
                yield return CapturePackEnvelope(
                    render,
                    sequence,
                    outputRoot,
                    packEnvelope,
                    recordCapture);
                foreach (float seconds in StaticSampleSeconds)
                {
                    var state = new StaticSegmentState
                    {
                        timeSeconds = seconds,
                        expectedSealedSegments = ExpectedSegments(seconds, true),
                        expectedOpenedSegments = ExpectedSegments(seconds, false),
                        packMask = packEnvelope.mask
                    };
                    yield return CaptureState(
                        render,
                        sequence,
                        outputRoot,
                        state,
                        packEnvelope.coverage,
                        recordCapture);
                    states.Add(state);
                }
            }
            finally
            {
                for (int index = 0; index < caseRenderers.Length; index++)
                {
                    caseRenderers[index].enabled = caseEnabled[index];
                }
            }

            report.physicalPackEnvelope = packEnvelope.mask;
            report.physicalPackEnvelopePath = packEnvelope.path;
            report.physicalPackEnvelopeStateSetFrame =
                packEnvelope.stateSetFrame;
            report.physicalPackEnvelopeRenderedAfterFrame =
                packEnvelope.renderedAfterFrame;
            report.states = states.ToArray();
            report.maximumExactIdBoundsDelta = report.states
                .SelectMany(state => state.components)
                .DefaultIfEmpty()
                .Max(component => component == null
                    ? float.PositiveInfinity
                    : component.exactIdBoundsDelta);
            report.bakedBoundsMatchExactIdMasks = report.states.All(state =>
                state.components.All(component =>
                    component.exactIdBoundsMatch));
            report.logicalSegmentRangesMatch = report.states.All(state =>
                state.components.All(component =>
                    component.expectedSegmentRangeMatches));
            report.masksStayInsidePack = report.states.All(state =>
                state.masksStayInsidePack);
            report.noFullWidthBridge = report.states.All(state =>
                state.noFullWidthBridge);
            report.passed = report.cameraAspectExactlyTarget
                && report.targetTextureExactlySession
                && report.directionPassed
                && report.bakedBoundsMatchExactIdMasks
                && report.logicalSegmentRangesMatch
                && report.masksStayInsidePack
                && report.noFullWidthBridge;
        }

        private static IEnumerator CapturePackEnvelope(
            IsolatedR025PortraitRenderSession render,
            IsolatedR025ProofSequence sequence,
            string outputRoot,
            PackEnvelope result,
            Action<int, int> recordCapture)
        {
            sequence.SetTime(0f, false);
            yield return null;
            render.PrepareForMeasurement();
            SkinnedMeshRenderer[] packRenderers = sequence.PackRenderers
                .ToArray();
            bool[] originalEnabled = packRenderers
                .Select(renderer => renderer.enabled)
                .ToArray();
            Material[][] originalMaterials = packRenderers
                .Select(renderer => renderer.sharedMaterials)
                .ToArray();
            Material envelopeId = CreateIdMaterial(
                "R025PhysicalPackEnvelopeId",
                PackColor,
                2460);
            try
            {
                Disable(packRenderers);
                foreach (SkinnedMeshRenderer renderer in new[]
                         {
                             sequence.FrontFoil,
                             sequence.TopSeal
                         })
                {
                    renderer.enabled = true;
                    renderer.sharedMaterials = Enumerable.Repeat(
                        envelopeId,
                        Mathf.Max(1, renderer.sharedMaterials.Length))
                        .ToArray();
                }
                result.stateSetFrame = Time.frameCount;
                yield return null;
                result.renderedAfterFrame = Time.frameCount;
                Color32[] pixels = render.Capture(Path.Combine(
                    outputRoot,
                    "diagnostics/physical-pack-envelope-id.png"));
                recordCapture(result.stateSetFrame, result.renderedAfterFrame);
                MaskMetrics mask = MeasureExactMask(pixels, PackColor);
                result.mask = new MaskState
                {
                    pixels = mask.count,
                    bounds = ViewportRect.From(mask.bounds)
                };
                result.coverage = BuildExactMask(pixels, PackColor);
                result.path = "diagnostics/physical-pack-envelope-id.png";
            }
            finally
            {
                for (int index = 0; index < packRenderers.Length; index++)
                {
                    packRenderers[index].enabled = originalEnabled[index];
                    packRenderers[index].sharedMaterials =
                        originalMaterials[index];
                }
                UnityEngine.Object.Destroy(envelopeId);
            }
        }

        private static IEnumerator CaptureState(
            IsolatedR025PortraitRenderSession render,
            IsolatedR025ProofSequence sequence,
            string outputRoot,
            StaticSegmentState state,
            IReadOnlyList<bool> packCoverage,
            Action<int, int> recordCapture)
        {
            sequence.SetTime(state.timeSeconds, false);
            yield return null;
            render.PrepareForMeasurement();
            state.cameraAspect = render.Camera.aspect;
            state.cameraAspectExactlyTarget =
                render.AspectExactlyMatchesTarget;

            SkinnedMeshRenderer[] packRenderers = sequence.PackRenderers
                .ToArray();
            bool[] originalEnabled = packRenderers
                .Select(renderer => renderer.enabled)
                .ToArray();
            Material[][] originalMaterials = packRenderers
                .Select(renderer => renderer.sharedMaterials)
                .ToArray();
            try
            {
                var components = new List<SegmentComponentState>(
                    Components.Length);
                foreach (ComponentSpec spec in Components)
                {
                    Disable(packRenderers);
                    SkinnedMeshRenderer renderer = spec.resolve(sequence);
                    renderer.enabled = true;
                    Material componentId = CreateIdMaterial(
                        $"R025{spec.role}Id{state.timeSeconds:0.000}",
                        spec.color,
                        spec.role == "top-seal" ? 2490 : 2470);
                    try
                    {
                        renderer.sharedMaterials = Enumerable.Repeat(
                            componentId,
                            Mathf.Max(1, renderer.sharedMaterials.Length))
                            .ToArray();
                        int stateSetFrame = Time.frameCount;
                        yield return null;
                        int renderedAfterFrame = Time.frameCount;
                        Color32[] componentPixels = render.Capture(Path.Combine(
                            outputRoot,
                            $"diagnostics/{spec.role}-id-{state.timeSeconds:0.000}.png"));
                        recordCapture(stateSetFrame, renderedAfterFrame);
                        BakedAnalysis analysis = Analyze(
                            render,
                            renderer,
                            state.timeSeconds,
                            spec.sealedComponent);
                        try
                        {
                            renderer.enabled = false;
                            var component = BuildComponentState(
                                spec,
                                state,
                                componentPixels,
                                packCoverage,
                                analysis,
                                stateSetFrame,
                                renderedAfterFrame);
                            yield return CaptureSegmentLabels(
                                render,
                                outputRoot,
                                component,
                                analysis,
                                packCoverage,
                                recordCapture);
                            components.Add(component);
                        }
                        finally
                        {
                            analysis.Dispose();
                        }
                    }
                    finally
                    {
                        UnityEngine.Object.Destroy(componentId);
                    }
                }

                state.components = components.ToArray();
                state.masksStayInsidePack = state.components.All(component =>
                    component.masksStayInsidePack);
                state.noFullWidthBridge = state.components.All(component =>
                    component.noSegmentBridge);
                state.bakedBoundsMatchExactIdMasks = state.components.All(
                    component => component.exactIdBoundsMatch);
                state.logicalSegmentRangesMatch = state.components.All(
                    component => component.expectedSegmentRangeMatches);
                state.passed = state.cameraAspectExactlyTarget
                    && state.masksStayInsidePack
                    && state.noFullWidthBridge
                    && state.bakedBoundsMatchExactIdMasks
                    && state.logicalSegmentRangesMatch;
            }
            finally
            {
                for (int index = 0; index < packRenderers.Length; index++)
                {
                    packRenderers[index].enabled = originalEnabled[index];
                    packRenderers[index].sharedMaterials =
                        originalMaterials[index];
                }
            }
        }

        private static IEnumerator CaptureSegmentLabels(
            IsolatedR025PortraitRenderSession render,
            string outputRoot,
            SegmentComponentState component,
            BakedAnalysis analysis,
            IReadOnlyList<bool> packCoverage,
            Action<int, int> recordCapture)
        {
            var labels = new SegmentLabelRender(analysis);
            try
            {
                int stateSetFrame = Time.frameCount;
                yield return null;
                int renderedAfterFrame = Time.frameCount;
                Color32[] pixels = render.Capture(Path.Combine(
                    outputRoot,
                    $"diagnostics/{component.role}-segment-labels-{component.timeSeconds:0.000}.png"));
                recordCapture(stateSetFrame, renderedAfterFrame);
                component.segmentMaskStateSetFrame = stateSetFrame;
                component.segmentMaskRenderedAfterFrame = renderedAfterFrame;
                component.segmentLabelPath =
                    $"diagnostics/{component.role}-segment-labels-{component.timeSeconds:0.000}.png";
                PopulateSegmentMasks(component, analysis, pixels, packCoverage);
                MatchExactIdBoundsToBakedTriangleMask(component);
            }
            finally
            {
                labels.Dispose();
            }
        }

        private static SegmentComponentState BuildComponentState(
            ComponentSpec spec,
            StaticSegmentState state,
            IReadOnlyList<Color32> pixels,
            IReadOnlyList<bool> packCoverage,
            BakedAnalysis analysis,
            int stateSetFrame,
            int renderedAfterFrame)
        {
            MaskMetrics mask = MeasureExactMask(pixels, spec.color);
            Rect analyticBounds = ClipToViewport(analysis.projectedBounds);
            int outsidePack = CountOutsidePack(
                pixels,
                spec.color,
                packCoverage);
            int[] expected = spec.sealedComponent
                ? state.expectedSealedSegments
                : state.expectedOpenedSegments;
            int[] active = analysis.segments
                .Select(segment => segment.physicalSegment)
                .OrderBy(segment => segment)
                .ToArray();
            return new SegmentComponentState
            {
                role = spec.role,
                timeSeconds = state.timeSeconds,
                expectedSegments = expected,
                activeNonDegenerateSegments = active,
                activeTriangleCount = analysis.activeTriangleCount,
                degenerateTriangleCount = analysis.degenerateTriangleCount,
                exactIdPixels = mask.count,
                exactIdBounds = ViewportRect.From(mask.bounds),
                analyticTargetAspectBakedBounds =
                    ViewportRect.From(analyticBounds),
                exactIdOutsidePackPixels = outsidePack,
                masksStayInsidePack = outsidePack == 0,
                expectedSegmentRangeMatches = expected.SequenceEqual(active),
                allActiveTrianglesFitOneSegment = analysis.segments.All(
                    segment => segment.trianglesFitOneSegment),
                originalIdPath =
                    $"diagnostics/{spec.role}-id-{state.timeSeconds:0.000}.png",
                originalIdStateSetFrame = stateSetFrame,
                originalIdRenderedAfterFrame = renderedAfterFrame
            };
        }

        private static void PopulateSegmentMasks(
            SegmentComponentState component,
            BakedAnalysis analysis,
            IReadOnlyList<Color32> pixels,
            IReadOnlyList<bool> packCoverage)
        {
            var byColor = analysis.segments.ToDictionary(
                segment => ColorKey(SegmentColor(segment.physicalSegment)),
                segment => segment);
            foreach (SegmentGeometry segment in analysis.segments)
            {
                segment.mask = new MaskAccumulator();
            }

            for (int y = 0; y < Height; y++)
            {
                float normalizedY = y / (float)(Height - 1);
                for (int x = 0; x < Width; x++)
                {
                    int index = y * Width + x;
                    if (!byColor.TryGetValue(
                            ColorKey(pixels[index]),
                            out SegmentGeometry segment))
                    {
                        continue;
                    }
                    segment.mask.Add(
                        x / (float)(Width - 1),
                        normalizedY,
                        !packCoverage[index]);
                }
            }

            component.segments = analysis.segments.Select(segment =>
            {
                Rect visibleExpected = ClipToViewport(segment.projectedBounds);
                MaskMetrics mask = segment.mask.ToMetrics();
                bool expectedVisible = visibleExpected.width > 0.00001f
                    && visibleExpected.height > 0.00001f;
                float maskWidth = mask.bounds.width;
                bool maskFits = !expectedVisible
                    ? mask.count == 0
                    : mask.count > 0
                        && maskWidth
                            <= segment.expectedProjectedWidth
                                + ProjectionAllowance;
                return new PerSegmentMaskState
                {
                    physicalSegment = segment.physicalSegment,
                    activeTriangleCount = segment.triangleCount,
                    bakedBounds = ViewportRect.From(visibleExpected),
                    maskBounds = ViewportRect.From(mask.bounds),
                    visibleMaskPixels = mask.count,
                    outsidePackPixels = segment.mask.outsidePackPixels,
                    expectedProjectedWidth =
                        segment.expectedProjectedWidth,
                    maximumTriangleProjectedWidth =
                        segment.maximumTriangleProjectedWidth,
                    maximumTriangleLocalWidth =
                        segment.maximumTriangleLocalWidth,
                    bakedMaskBoundsDelta = RectDelta(
                        visibleExpected,
                        mask.bounds),
                    trianglesFitOneSegment =
                        segment.trianglesFitOneSegment,
                    maskFitsOneSegment = maskFits,
                    maskStaysInsidePack =
                        segment.mask.outsidePackPixels == 0,
                    passed = segment.trianglesFitOneSegment
                        && maskFits
                        && segment.mask.outsidePackPixels == 0
                };
            }).ToArray();
            component.segmentMaskOutsidePackPixels = component.segments.Sum(
                segment => segment.outsidePackPixels);
            component.noSegmentBridge =
                component.allActiveTrianglesFitOneSegment
                && component.segments.All(segment =>
                    segment.trianglesFitOneSegment
                    && segment.maskFitsOneSegment);
            component.masksStayInsidePack =
                component.masksStayInsidePack
                && component.segmentMaskOutsidePackPixels == 0;
            component.passed = component.exactIdBoundsMatch
                && component.expectedSegmentRangeMatches
                && component.noSegmentBridge
                && component.masksStayInsidePack;
        }

        private static void MatchExactIdBoundsToBakedTriangleMask(
            SegmentComponentState component)
        {
            PerSegmentMaskState[] visible = component.segments
                .Where(segment => segment.visibleMaskPixels > 0)
                .ToArray();
            int pixels = visible.Sum(segment => segment.visibleMaskPixels);
            Rect bounds = visible.Length == 0
                ? Rect.zero
                : visible.Select(segment => segment.maskBounds.ToRect())
                    .Aggregate(Union);
            component.bakedTriangleMaskPixels = pixels;
            component.targetAspectBakedBounds = ViewportRect.From(bounds);
            component.exactIdBoundsDelta = RectDelta(
                component.exactIdBounds.ToRect(),
                bounds);
            component.exactIdBoundsMatch = component.exactIdPixels > 0
                && pixels > 0
                && component.exactIdBoundsDelta <= ProjectionAllowance;
            component.passed = component.exactIdBoundsMatch
                && component.expectedSegmentRangeMatches
                && component.noSegmentBridge
                && component.masksStayInsidePack;
        }

        private static BakedAnalysis Analyze(
            IsolatedR025PortraitRenderSession render,
            SkinnedMeshRenderer renderer,
            float seconds,
            bool sealedComponent)
        {
            render.PrepareForMeasurement();
            var baked = new Mesh { name = $"{renderer.name}_R025Baked" };
            renderer.BakeMesh(baked);
            Vector3[] vertices = baked.vertices;
            int[] triangles = baked.triangles;
            var segments = new Dictionary<int, SegmentGeometry>();
            int degenerate = 0;
            for (int index = 0; index < triangles.Length; index += 3)
            {
                int first = triangles[index];
                int second = triangles[index + 1];
                int third = triangles[index + 2];
                Vector3 a = vertices[first];
                Vector3 b = vertices[second];
                Vector3 c = vertices[third];
                if (Vector3.Cross(b - a, c - a).sqrMagnitude
                    <= DegenerateTriangleAreaSquared)
                {
                    degenerate++;
                    continue;
                }

                int localSegment = LocalSegmentIndex(
                    (a.x + b.x + c.x) / 3f);
                int segmentIndex = SegmentCount - 1 - localSegment;
                if (!segments.TryGetValue(
                        segmentIndex,
                        out SegmentGeometry segment))
                {
                    segment = new SegmentGeometry(
                        segmentIndex,
                        localSegment);
                    segments.Add(segmentIndex, segment);
                }
                segment.AddTriangle(
                    first,
                    second,
                    third,
                    a,
                    b,
                    c,
                    renderer.transform,
                    render.Camera);
            }

            int[] expected = ExpectedSegments(seconds, sealedComponent);
            return new BakedAnalysis(
                baked,
                renderer.transform,
                segments.Values.OrderBy(item => item.physicalSegment).ToArray(),
                degenerate,
                expected);
        }

        private static int[] ExpectedSegments(
            float seconds,
            bool sealedComponent) =>
            seconds switch
            {
                <= 0.501f => SegmentRange(
                    sealedComponent ? 7 : 0,
                    sealedComponent ? 47 : 6),
                <= 0.701f => SegmentRange(
                    sealedComponent ? 19 : 0,
                    sealedComponent ? 47 : 33),
                _ => SegmentRange(
                    sealedComponent ? 34 : 0,
                    sealedComponent ? 47 : 44)
            };

        private static int[] SegmentRange(int first, int last) =>
            Enumerable.Range(first, last - first + 1).ToArray();

        private static int LocalSegmentIndex(float x) => Mathf.Clamp(
            Mathf.FloorToInt((x - PackLeftMeters) / SegmentWidthMeters),
            0,
            SegmentCount - 1);

        private static void Disable(
            IEnumerable<SkinnedMeshRenderer> renderers)
        {
            foreach (SkinnedMeshRenderer renderer in renderers)
            {
                renderer.enabled = false;
            }
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

        private static bool[] BuildExactMask(
            IReadOnlyList<Color32> pixels,
            Color32 color)
        {
            var mask = new bool[Width * Height];
            for (int index = 0; index < mask.Length; index++)
            {
                mask[index] = pixels[index].Equals(color);
            }
            return mask;
        }

        private static MaskMetrics MeasureExactMask(
            IReadOnlyList<Color32> pixels,
            Color32 color)
        {
            var accumulator = new MaskAccumulator();
            for (int y = 0; y < Height; y++)
            {
                float normalizedY = y / (float)(Height - 1);
                for (int x = 0; x < Width; x++)
                {
                    if (pixels[y * Width + x].Equals(color))
                    {
                        accumulator.Add(
                            x / (float)(Width - 1),
                            normalizedY,
                            false);
                    }
                }
            }
            return accumulator.ToMetrics();
        }

        private static int CountOutsidePack(
            IReadOnlyList<Color32> pixels,
            Color32 color,
            IReadOnlyList<bool> packCoverage)
        {
            int outside = 0;
            for (int index = 0; index < pixels.Count; index++)
            {
                if (pixels[index].Equals(color) && !packCoverage[index])
                {
                    outside++;
                }
            }
            return outside;
        }

        private static Rect ClipToViewport(Rect bounds) =>
            Rect.MinMaxRect(
                Mathf.Clamp01(bounds.xMin),
                Mathf.Clamp01(bounds.yMin),
                Mathf.Clamp01(bounds.xMax),
                Mathf.Clamp01(bounds.yMax));

        private static float RectDelta(Rect left, Rect right) =>
            Mathf.Max(
                Mathf.Abs(left.xMin - right.xMin),
                Mathf.Abs(left.xMax - right.xMax),
                Mathf.Abs(left.yMin - right.yMin),
                Mathf.Abs(left.yMax - right.yMax));

        private static uint ColorKey(Color32 color) =>
            ((uint)color.r << 16) | ((uint)color.g << 8) | color.b;

        private static Color32 SegmentColor(int segment)
        {
            int red = segment % 4;
            int green = segment / 4 % 4;
            int blue = segment / 16;
            return new Color32(
                (byte)(32 + red * 64),
                (byte)(32 + green * 64),
                (byte)(32 + blue * 64),
                255);
        }

        private sealed class ComponentSpec
        {
            public ComponentSpec(
                string role,
                Func<IsolatedR025ProofSequence, SkinnedMeshRenderer> resolve,
                Color32 color,
                bool sealedComponent)
            {
                this.role = role;
                this.resolve = resolve;
                this.color = color;
                this.sealedComponent = sealedComponent;
            }

            public string role { get; }
            public Func<IsolatedR025ProofSequence, SkinnedMeshRenderer> resolve { get; }
            public Color32 color { get; }
            public bool sealedComponent { get; }
        }

        private sealed class PackEnvelope
        {
            public bool[] coverage = Array.Empty<bool>();
            public MaskState mask;
            public string path;
            public int stateSetFrame;
            public int renderedAfterFrame;
        }

        private sealed class BakedAnalysis : IDisposable
        {
            public BakedAnalysis(
                Mesh baked,
                Transform sourceTransform,
                SegmentGeometry[] segments,
                int degenerateTriangleCount,
                int[] expectedSegments)
            {
                this.baked = baked;
                this.sourceTransform = sourceTransform;
                this.segments = segments;
                this.degenerateTriangleCount = degenerateTriangleCount;
                this.expectedSegments = expectedSegments;
                projectedBounds = segments.Length == 0
                    ? Rect.zero
                    : Union(segments.Select(segment =>
                        segment.projectedBounds).ToArray());
            }

            public Mesh baked { get; }
            public Transform sourceTransform { get; }
            public SegmentGeometry[] segments { get; }
            public int degenerateTriangleCount { get; }
            public int[] expectedSegments { get; }
            public Rect projectedBounds { get; }
            public int activeTriangleCount => segments.Sum(
                segment => segment.triangleCount);

            public void Dispose()
            {
                UnityEngine.Object.Destroy(baked);
            }
        }

        private sealed class SegmentGeometry
        {
            private readonly List<int> triangles = new();
            private Rect bounds;
            private bool hasBounds;

            public SegmentGeometry(int physicalSegment, int localSegment)
            {
                this.physicalSegment = physicalSegment;
                this.localSegment = localSegment;
            }

            public int physicalSegment { get; }
            public int localSegment { get; }
            public IReadOnlyList<int> triangleIndices => triangles;
            public int triangleCount => triangles.Count / 3;
            public float expectedProjectedWidth { get; private set; }
            public float maximumTriangleProjectedWidth { get; private set; }
            public float maximumTriangleLocalWidth { get; private set; }
            public bool trianglesFitOneSegment { get; private set; } = true;
            public Rect projectedBounds => hasBounds ? bounds : Rect.zero;
            public MaskAccumulator mask { get; set; }

            public void AddTriangle(
                int first,
                int second,
                int third,
                Vector3 a,
                Vector3 b,
                Vector3 c,
                Transform transform,
                Camera camera)
            {
                triangles.Add(first);
                triangles.Add(second);
                triangles.Add(third);
                float localWidth = Mathf.Max(a.x, b.x, c.x)
                    - Mathf.Min(a.x, b.x, c.x);
                Vector3 worldA = transform.TransformPoint(a);
                Vector3 worldB = transform.TransformPoint(b);
                Vector3 worldC = transform.TransformPoint(c);
                Vector3 viewportA = camera.WorldToViewportPoint(worldA);
                Vector3 viewportB = camera.WorldToViewportPoint(worldB);
                Vector3 viewportC = camera.WorldToViewportPoint(worldC);
                if (viewportA.z <= 0f || viewportB.z <= 0f || viewportC.z <= 0f)
                {
                    trianglesFitOneSegment = false;
                    return;
                }
                Rect triangleBounds = Rect.MinMaxRect(
                    Mathf.Min(viewportA.x, viewportB.x, viewportC.x),
                    Mathf.Min(viewportA.y, viewportB.y, viewportC.y),
                    Mathf.Max(viewportA.x, viewportB.x, viewportC.x),
                    Mathf.Max(viewportA.y, viewportB.y, viewportC.y));
                bounds = hasBounds ? Union(bounds, triangleBounds) : triangleBounds;
                hasBounds = true;
                float minimumX = PackLeftMeters
                    + localSegment * SegmentWidthMeters;
                float expectedMinimum = float.PositiveInfinity;
                float expectedMaximum = float.NegativeInfinity;
                foreach (Vector3 vertex in new[] { a, b, c })
                {
                    Vector3 left = transform.TransformPoint(
                        new Vector3(minimumX, vertex.y, vertex.z));
                    Vector3 right = transform.TransformPoint(
                        new Vector3(
                            minimumX + SegmentWidthMeters,
                            vertex.y,
                            vertex.z));
                    expectedMinimum = Mathf.Min(
                        expectedMinimum,
                        camera.WorldToViewportPoint(left).x);
                    expectedMaximum = Mathf.Max(
                        expectedMaximum,
                        camera.WorldToViewportPoint(right).x);
                }
                float expectedWidth = expectedMaximum - expectedMinimum;
                float projectedWidth = triangleBounds.width;
                expectedProjectedWidth = Mathf.Max(
                    expectedProjectedWidth,
                    expectedWidth);
                maximumTriangleProjectedWidth = Mathf.Max(
                    maximumTriangleProjectedWidth,
                    projectedWidth);
                maximumTriangleLocalWidth = Mathf.Max(
                    maximumTriangleLocalWidth,
                    localWidth);
                trianglesFitOneSegment = trianglesFitOneSegment
                    && localWidth <= SegmentWidthMeters
                        + LocalSegmentAllowanceMeters
                    && projectedWidth <= expectedWidth + ProjectionAllowance;
            }
        }

        private sealed class SegmentLabelRender : IDisposable
        {
            private readonly List<GameObject> objects = new();
            private readonly List<Mesh> meshes = new();
            private readonly List<Material> materials = new();

            public SegmentLabelRender(BakedAnalysis analysis)
            {
                Vector3[] sourceVertices = analysis.baked.vertices;
                Vector3[] sourceNormals = analysis.baked.normals;
                foreach (SegmentGeometry segment in analysis.segments)
                {
                    var remapped = new Dictionary<int, int>();
                    var vertices = new List<Vector3>();
                    var normals = new List<Vector3>();
                    var triangles = new List<int>();
                    foreach (int sourceIndex in segment.triangleIndices)
                    {
                        if (!remapped.TryGetValue(
                                sourceIndex,
                                out int destinationIndex))
                        {
                            destinationIndex = vertices.Count;
                            remapped.Add(sourceIndex, destinationIndex);
                            vertices.Add(analysis.sourceTransform.TransformPoint(
                                sourceVertices[sourceIndex]));
                            normals.Add(analysis.sourceTransform
                                .TransformDirection(sourceNormals.Length
                                > sourceIndex
                                ? sourceNormals[sourceIndex]
                                : Vector3.back)
                                .normalized);
                        }
                        triangles.Add(destinationIndex);
                    }
                    var mesh = new Mesh
                    {
                        name = $"R025_{segment.physicalSegment:D2}_SegmentMask"
                    };
                    mesh.SetVertices(vertices);
                    mesh.SetNormals(normals);
                    mesh.SetTriangles(triangles, 0, true);
                    mesh.RecalculateBounds();
                    var item = new GameObject(mesh.name);
                    MeshFilter filter = item.AddComponent<MeshFilter>();
                    MeshRenderer renderer = item.AddComponent<MeshRenderer>();
                    Material material = CreateIdMaterial(
                        $"{mesh.name}_Material",
                        SegmentColor(segment.physicalSegment),
                        2500);
                    filter.sharedMesh = mesh;
                    renderer.sharedMaterial = material;
                    renderer.shadowCastingMode = ShadowCastingMode.Off;
                    renderer.receiveShadows = false;
                    objects.Add(item);
                    meshes.Add(mesh);
                    materials.Add(material);
                }
            }

            public void Dispose()
            {
                foreach (GameObject item in objects)
                {
                    UnityEngine.Object.Destroy(item);
                }
                foreach (Mesh mesh in meshes)
                {
                    UnityEngine.Object.Destroy(mesh);
                }
                foreach (Material material in materials)
                {
                    UnityEngine.Object.Destroy(material);
                }
            }
        }

        private sealed class MaskAccumulator
        {
            private float minX = float.PositiveInfinity;
            private float minY = float.PositiveInfinity;
            private float maxX = float.NegativeInfinity;
            private float maxY = float.NegativeInfinity;

            public int count { get; private set; }
            public int outsidePackPixels { get; private set; }

            public void Add(float x, float y, bool outsidePack)
            {
                count++;
                minX = Mathf.Min(minX, x);
                minY = Mathf.Min(minY, y);
                maxX = Mathf.Max(maxX, x);
                maxY = Mathf.Max(maxY, y);
                if (outsidePack)
                {
                    outsidePackPixels++;
                }
            }

            public MaskMetrics ToMetrics() => count == 0
                ? new MaskMetrics(0, Rect.zero)
                : new MaskMetrics(
                    count,
                    Rect.MinMaxRect(minX, minY, maxX, maxY));
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

        private static Rect Union(IReadOnlyList<Rect> rectangles)
        {
            Rect result = rectangles[0];
            for (int index = 1; index < rectangles.Count; index++)
            {
                result = Union(result, rectangles[index]);
            }
            return result;
        }

        private static Rect Union(Rect first, Rect second) => Rect.MinMaxRect(
            Mathf.Min(first.xMin, second.xMin),
            Mathf.Min(first.yMin, second.yMin),
            Mathf.Max(first.xMax, second.xMax),
            Mathf.Max(first.yMax, second.yMax));

        [Serializable]
        public sealed class TargetPortraitProjectionReport
        {
            public int width;
            public int height;
            public float targetAspect;
            public float cameraAspectBeforeSession;
            public float cameraAspect;
            public bool cameraAspectExactlyTarget;
            public bool targetTextureExactlySession;
            public float transitionAllowance;
            public float physicalUZeroScreenX;
            public float physicalUOneScreenX;
            public bool directionPassed;
            public MaskState physicalPackEnvelope;
            public string physicalPackEnvelopePath;
            public int physicalPackEnvelopeStateSetFrame;
            public int physicalPackEnvelopeRenderedAfterFrame;
            public StaticSegmentState[] states;
            public float maximumExactIdBoundsDelta;
            public bool bakedBoundsMatchExactIdMasks;
            public bool logicalSegmentRangesMatch;
            public bool masksStayInsidePack;
            public bool noFullWidthBridge;
            public bool passed;

            public StaticSegmentState At(float seconds)
            {
                StaticSegmentState result = states?.SingleOrDefault(state =>
                    Mathf.Abs(state.timeSeconds - seconds) < 0.0001f);
                if (result == null)
                {
                    throw new InvalidOperationException(
                        $"R025 lacks projection evidence at t={seconds:F3}.");
                }
                return result;
            }

            public string Summary() =>
                $"aspect={cameraAspect:F7}/{targetAspect:F7}, delta={maximumExactIdBoundsDelta:F6}, ranges={logicalSegmentRangesMatch}, inside={masksStayInsidePack}, bridge={noFullWidthBridge}";
        }

        [Serializable]
        public sealed class StaticSegmentState
        {
            public float timeSeconds;
            public float cameraAspect;
            public bool cameraAspectExactlyTarget;
            public int packMaskStateSetFrame;
            public int packMaskRenderedAfterFrame;
            public MaskState packMask;
            public int[] expectedSealedSegments;
            public int[] expectedOpenedSegments;
            public SegmentComponentState[] components;
            public bool bakedBoundsMatchExactIdMasks;
            public bool logicalSegmentRangesMatch;
            public bool masksStayInsidePack;
            public bool noFullWidthBridge;
            public bool passed;

            public SegmentComponentState Component(string role)
            {
                SegmentComponentState result = components?.SingleOrDefault(
                    component => component.role == role);
                if (result == null)
                {
                    throw new InvalidOperationException(
                        $"R025 lacks {role} segment evidence.");
                }
                return result;
            }
        }

        [Serializable]
        public sealed class SegmentComponentState
        {
            public string role;
            public float timeSeconds;
            public int[] expectedSegments;
            public int[] activeNonDegenerateSegments;
            public int activeTriangleCount;
            public int degenerateTriangleCount;
            public int exactIdPixels;
            public ViewportRect exactIdBounds;
            public ViewportRect analyticTargetAspectBakedBounds;
            public ViewportRect targetAspectBakedBounds;
            public int bakedTriangleMaskPixels;
            public float exactIdBoundsDelta;
            public bool exactIdBoundsMatch;
            public int exactIdOutsidePackPixels;
            public string originalIdPath;
            public int originalIdStateSetFrame;
            public int originalIdRenderedAfterFrame;
            public string segmentLabelPath;
            public int segmentMaskStateSetFrame;
            public int segmentMaskRenderedAfterFrame;
            public PerSegmentMaskState[] segments;
            public int segmentMaskOutsidePackPixels;
            public bool expectedSegmentRangeMatches;
            public bool allActiveTrianglesFitOneSegment;
            public bool masksStayInsidePack;
            public bool noSegmentBridge;
            public bool passed;
        }

        [Serializable]
        public sealed class PerSegmentMaskState
        {
            public int physicalSegment;
            public int activeTriangleCount;
            public ViewportRect bakedBounds;
            public ViewportRect maskBounds;
            public int visibleMaskPixels;
            public int outsidePackPixels;
            public float expectedProjectedWidth;
            public float maximumTriangleProjectedWidth;
            public float maximumTriangleLocalWidth;
            public float bakedMaskBoundsDelta;
            public bool trianglesFitOneSegment;
            public bool maskFitsOneSegment;
            public bool maskStaysInsidePack;
            public bool passed;
        }

        [Serializable]
        public struct MaskState
        {
            public int pixels;
            public ViewportRect bounds;
        }

        [Serializable]
        public struct ViewportRect
        {
            public float x;
            public float y;
            public float width;
            public float height;

            public static ViewportRect From(Rect source) => new()
            {
                x = source.x,
                y = source.y,
                width = source.width,
                height = source.height
            };

            public Rect ToRect() => new(x, y, width, height);
        }
    }
}
