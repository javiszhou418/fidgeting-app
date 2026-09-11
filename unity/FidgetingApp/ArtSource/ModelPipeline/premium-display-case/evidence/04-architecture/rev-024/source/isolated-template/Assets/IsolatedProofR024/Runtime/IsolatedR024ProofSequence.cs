using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using UnityEngine;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R024
{
    public sealed class IsolatedR024ProofSequence
    {
        public const int ExpectedRendererCount = 11;
        public const int ExpectedBlendShapeCount = 6;
        public const float MouthDepthMeters = 0.107f;
        public const float LinerDepthMeters = 0.0055f;
        public const float FoilThicknessMeters = 0.00075f;
        public const float TopSealHeightFraction = 0.020f;
        public const float ReleasedStripHeightFraction = 0.048f;

        private static readonly string[] PoseKeys =
        {
            "Pose_TabCatch",
            "Pose_Resistance",
            "Pose_TearAdvance",
            "Pose_FormedMouth",
            "Pose_CaseContained",
            "Pose_ContinuousRise"
        };
        private static readonly float[] TearFrontByPose =
        {
            0f, 0f, 0.125f, 0.375f, 0.6875f, 0.9166667f, 1f
        };

        private readonly IsolatedR024Profile profile;
        private readonly Camera camera;
        private readonly Transform packRoot;
        private readonly SkinnedMeshRenderer[] packRenderers;
        private readonly SkinnedMeshRenderer frontFoil;
        private readonly SkinnedMeshRenderer rearFoil;
        private readonly SkinnedMeshRenderer topSeal;
        private readonly SkinnedMeshRenderer innerMouth;
        private readonly SkinnedMeshRenderer innerBackRim;
        private readonly SkinnedMeshRenderer rolledCrimpLip;
        private readonly SkinnedMeshRenderer tornContour;
        private readonly SkinnedMeshRenderer tearFrontSidewall;
        private readonly SkinnedMeshRenderer tabSidewall;
        private readonly SkinnedMeshRenderer releasedSealStrip;
        private readonly SkinnedMeshRenderer pullTab;
        private readonly Transform caseMotionRoot;
        private readonly Renderer[] caseRenderers;
        private readonly MaterialPropertyBlock packProperties = new();
        private readonly MaterialPropertyBlock contourProperties = new();
        private readonly Vector3 packBasePosition;
        private readonly Vector3 caseBasePosition;
        private readonly Quaternion caseBaseRotation;
        private readonly Vector3 caseBaseScale;
        private readonly int dissolveId = Shader.PropertyToID("_Dissolve");
        private readonly int edgeStrengthId = Shader.PropertyToID("_EdgeStrength");
        private readonly int sweepProgressId = Shader.PropertyToID("_SweepProgress");
        private readonly int intensityId = Shader.PropertyToID("_Intensity");

        public IsolatedR024ProofSequence(
            IsolatedR024Profile profile,
            Camera camera,
            Transform packRoot,
            SkinnedMeshRenderer[] packRenderers,
            Transform caseMotionRoot)
        {
            this.profile = profile;
            this.camera = camera;
            this.packRoot = packRoot;
            this.packRenderers = packRenderers;
            this.caseMotionRoot = caseMotionRoot;
            frontFoil = RequireRenderer("Pack_FrontPrintedFoil");
            rearFoil = RequireRenderer("Pack_RearInnerFoil");
            topSeal = RequireRenderer("Pack_TopSealRemaining");
            innerMouth = RequireRenderer("Pack_InnerFoilMouth");
            innerBackRim = RequireRenderer("Pack_InnerBackFoilRim");
            rolledCrimpLip = RequireRenderer("Pack_RolledCrimpLip");
            tornContour = RequireRenderer("Pack_TornContourSweepCarrier");
            tearFrontSidewall = RequireRenderer("Pack_TearFrontSidewall");
            tabSidewall = RequireRenderer("Pack_TabSidewall");
            releasedSealStrip = RequireRenderer("Pack_ReleasedSealStrip");
            pullTab = RequireRenderer("Pack_TopRightPullTab");
            caseRenderers = caseMotionRoot.GetComponentsInChildren<Renderer>(true);
            packBasePosition = packRoot.localPosition;
            caseBasePosition = caseMotionRoot.localPosition;
            caseBaseRotation = caseMotionRoot.localRotation;
            caseBaseScale = caseMotionRoot.localScale;
            ValidateBindings();
        }

        public IsolatedR024Sample CurrentSample { get; private set; }
        public float NormalizedTearProgress { get; private set; }
        public float NormalizedTearFront { get; private set; }
        public bool PackVisible => frontFoil.enabled;
        public bool EffectsEnabled { get; private set; }
        public bool MouthContactOcclusionActive =>
            rolledCrimpLip.enabled && NormalizedTearProgress >= 0.50f;
        public EntityId CaseRootId => caseMotionRoot.GetEntityId();
        public IReadOnlyList<EntityId> CaseRendererIds =>
            caseRenderers.Select(renderer => renderer.GetEntityId()).ToArray();
        public IReadOnlyList<EntityId> PackRendererIds =>
            packRenderers.Select(renderer => renderer.GetEntityId()).ToArray();
        public IReadOnlyList<Renderer> LiveCaseRenderers => caseRenderers;
        public IReadOnlyList<SkinnedMeshRenderer> PackRenderers => packRenderers;
        public IReadOnlyList<SkinnedMeshRenderer> PhysicalMouthRenderers =>
            new[]
            {
                rearFoil,
                innerMouth,
                innerBackRim,
                rolledCrimpLip,
                tearFrontSidewall,
                tabSidewall,
                releasedSealStrip,
                pullTab
            };
        public SkinnedMeshRenderer FrontFoil => frontFoil;
        public SkinnedMeshRenderer TopSeal => topSeal;
        public SkinnedMeshRenderer InnerMouth => innerMouth;
        public SkinnedMeshRenderer InnerBackRim => innerBackRim;
        public SkinnedMeshRenderer RolledCrimpLip => rolledCrimpLip;
        public SkinnedMeshRenderer TearFrontSidewall => tearFrontSidewall;
        public SkinnedMeshRenderer TabSidewall => tabSidewall;
        public SkinnedMeshRenderer ReleasedSealStrip => releasedSealStrip;
        public SkinnedMeshRenderer PullTab => pullTab;
        public SkinnedMeshRenderer TornContour => tornContour;
        public Quaternion PackRootLocalRotation => packRoot.localRotation;
        public Vector3 CaseAuthoredScale => caseBaseScale;
        public Vector3 CaseMotionRootPosition => caseMotionRoot.localPosition;
        public Vector3 CaseMotionRootScale => caseMotionRoot.localScale;
        public string SealedStateFingerprint { get; private set; } = string.Empty;
        public string CurrentStateFingerprint => BuildStateFingerprint();

        public void InitializeSealedState()
        {
            SetTime(0f, false);
            SealedStateFingerprint = BuildStateFingerprint();
        }

        public void SetTime(float elapsedSeconds, bool effectsEnabled)
        {
            CurrentSample = profile.Evaluate(elapsedSeconds, effectsEnabled);
            NormalizedTearProgress = CurrentSample.TearProgress;
            NormalizedTearFront = ResolveTearFront(NormalizedTearProgress);
            EffectsEnabled = effectsEnabled;
            ApplyBlendShapeProgress(NormalizedTearProgress);
            ApplyPack(CurrentSample);
            ApplyCase(CurrentSample);
            ApplyContourSweep(CurrentSample);
        }

        public void SetNormalizedTearProgress(float progress)
        {
            NormalizedTearProgress = Mathf.Clamp01(progress);
            NormalizedTearFront = ResolveTearFront(NormalizedTearProgress);
            CurrentSample = new IsolatedR024Sample(
                IsolatedR024Phase.FormedMouth,
                IsolatedR024Occlusion.MouthOpening,
                NormalizedTearProgress,
                0f,
                0f,
                0f);
            EffectsEnabled = false;
            ApplyBlendShapeProgress(NormalizedTearProgress);
            ApplyPack(CurrentSample);
            ApplyCase(CurrentSample);
            ApplyContourSweep(CurrentSample);
        }

        public bool ReboundToSealed()
        {
            SetNormalizedTearProgress(0f);
            SetTime(0f, false);
            return string.Equals(
                SealedStateFingerprint,
                BuildStateFingerprint(),
                StringComparison.Ordinal);
        }

        public bool IsCaseContainedInMouth()
        {
            float depth = caseMotionRoot.position.z - packRoot.position.z;
            return CurrentSample.Occlusion == IsolatedR024Occlusion.CaseContained
                && depth >= 0.040f
                && depth <= MouthDepthMeters + 0.010f
                && MouthContactOcclusionActive;
        }

        public bool TryGetCaseViewportBounds(out Rect bounds)
        {
            return TryGetViewportBounds(caseRenderers, out bounds);
        }

        public bool TryGetPackViewportBounds(out Rect bounds)
        {
            return TryGetViewportBounds(
                packRenderers.Cast<Renderer>().ToArray(),
                out bounds);
        }

        public bool TryGetPackBodyViewportBounds(out Rect bounds)
        {
            return TryGetViewportBounds(
                new Renderer[] { frontFoil },
                out bounds);
        }

        public bool TryGetRendererViewportBounds(
            Renderer renderer,
            out Rect bounds)
        {
            return TryGetViewportBounds(new[] { renderer }, out bounds);
        }

        public bool TryGetRendererVertexViewportPoint(
            SkinnedMeshRenderer renderer,
            int vertexIndex,
            out Vector2 point)
        {
            point = default;
            if (renderer == null || !renderer.enabled || vertexIndex < 0)
            {
                return false;
            }

            var baked = new Mesh { name = "R024_VertexViewportProbe" };
            try
            {
                renderer.BakeMesh(baked);
                if (vertexIndex >= baked.vertexCount)
                {
                    return false;
                }
                Vector3 viewport = camera.WorldToViewportPoint(
                    renderer.transform.TransformPoint(baked.vertices[vertexIndex]));
                if (viewport.z <= 0f)
                {
                    return false;
                }
                point = new Vector2(viewport.x, viewport.y);
                return true;
            }
            finally
            {
                UnityEngine.Object.Destroy(baked);
            }
        }

        public bool TryGetTopSealPhysicalEdgeViewportPoints(
            out Vector2 physicalUZero,
            out Vector2 physicalUOne)
        {
            physicalUZero = default;
            physicalUOne = default;
            if (topSeal.sharedMesh == null
                || topSeal.sharedMesh.vertexCount < 4)
            {
                return false;
            }
            return TryGetRendererVertexViewportPoint(
                       topSeal,
                       0,
                       out physicalUZero)
                && TryGetRendererVertexViewportPoint(
                    topSeal,
                    topSeal.sharedMesh.vertexCount - 2,
                    out physicalUOne);
        }

        public bool TryGetMouthViewportBounds(out Rect bounds)
        {
            return TryGetViewportBounds(
                new Renderer[]
                {
                    rearFoil,
                    rolledCrimpLip,
                    innerMouth,
                    innerBackRim
                },
                out bounds);
        }

        public void BakeFrontFoil(Mesh destination)
        {
            if (destination == null)
            {
                throw new ArgumentNullException(nameof(destination));
            }
            frontFoil.BakeMesh(destination);
        }

        private void ValidateBindings()
        {
            if (profile == null
                || camera == null
                || packRoot == null
                || caseMotionRoot == null
                || packRenderers.Length != ExpectedRendererCount
                || caseRenderers.Length == 0)
            {
                throw new InvalidOperationException(
                    "R024 isolated Pack-only bindings are incomplete.");
            }

            foreach (SkinnedMeshRenderer renderer in packRenderers)
            {
                if (renderer == null
                    || renderer.sharedMesh == null
                    || renderer.sharedMesh.blendShapeCount != ExpectedBlendShapeCount)
                {
                    throw new InvalidOperationException(
                        "Every R024 Pack-only mesh must expose six authored poses.");
                }
            }
        }

        private SkinnedMeshRenderer RequireRenderer(string name)
        {
            SkinnedMeshRenderer renderer = packRenderers.SingleOrDefault(
                item => string.Equals(item.name, name, StringComparison.Ordinal));
            if (renderer == null)
            {
                throw new InvalidOperationException(
                    $"Missing R024 Pack-only renderer: {name}");
            }
            return renderer;
        }

        private void ApplyBlendShapeProgress(float progress)
        {
            float[] samples = IsolatedR024Profile.AuthoredPoseProgresses;
            int lower = 0;
            int upper = samples.Length - 1;
            for (int index = 1; index < samples.Length; index++)
            {
                if (progress <= samples[index])
                {
                    lower = index - 1;
                    upper = index;
                    break;
                }
            }
            if (progress >= samples[^1])
            {
                lower = samples.Length - 1;
                upper = lower;
            }

            float blend = lower == upper
                ? 0f
                : Mathf.InverseLerp(samples[lower], samples[upper], progress);
            foreach (SkinnedMeshRenderer renderer in packRenderers)
            {
                Mesh mesh = renderer.sharedMesh;
                for (int index = 0; index < PoseKeys.Length; index++)
                {
                    renderer.SetBlendShapeWeight(
                        mesh.GetBlendShapeIndex(PoseKeys[index]),
                        0f);
                }
                if (lower > 0)
                {
                    renderer.SetBlendShapeWeight(
                        mesh.GetBlendShapeIndex(PoseKeys[lower - 1]),
                        upper == lower ? 100f : (1f - blend) * 100f);
                }
                if (upper > 0 && upper != lower)
                {
                    renderer.SetBlendShapeWeight(
                        mesh.GetBlendShapeIndex(PoseKeys[upper - 1]),
                        blend * 100f);
                }
            }
        }

        private void ApplyPack(IsolatedR024Sample sample)
        {
            bool visible = sample.PackDissolve < 0.9995f;
            frontFoil.enabled = visible;
            rearFoil.enabled = visible;
            topSeal.enabled = visible;
            innerMouth.enabled = visible && sample.TearProgress > 0.025f;
            innerBackRim.enabled = visible && sample.TearProgress > 0.035f;
            rolledCrimpLip.enabled = visible && sample.TearProgress > 0.040f;
            tornContour.enabled = visible
                && EffectsEnabled
                && sample.ContourSweep > 0.0001f;
            tearFrontSidewall.enabled = visible && sample.TearProgress > 0.170f;
            tabSidewall.enabled = visible && sample.TearProgress > 0.075f;
            releasedSealStrip.enabled = visible && sample.TearProgress > 0.110f;
            pullTab.enabled = visible && sample.TearProgress > 0.004f;
            packRoot.localPosition = packBasePosition + new Vector3(
                0f,
                -0.012f * sample.PackDissolve,
                0.002f * sample.PackDissolve);
            ApplyDiscardProperties(frontFoil, sample.PackDissolve);
        }

        private void ApplyDiscardProperties(
            Renderer renderer,
            float dissolve)
        {
            renderer.GetPropertyBlock(packProperties);
            packProperties.SetFloat(dissolveId, dissolve);
            packProperties.SetFloat(edgeStrengthId, 0f);
            renderer.SetPropertyBlock(packProperties);
        }

        private void ApplyCase(IsolatedR024Sample sample)
        {
            caseMotionRoot.localPosition = caseBasePosition + new Vector3(
                0f,
                0.148f * sample.CaseTravel,
                0f);
            caseMotionRoot.localRotation = caseBaseRotation;
            caseMotionRoot.localScale = caseBaseScale;
        }

        private void ApplyContourSweep(IsolatedR024Sample sample)
        {
            tornContour.GetPropertyBlock(contourProperties);
            contourProperties.SetFloat(
                sweepProgressId,
                sample.TearProgress);
            contourProperties.SetFloat(
                intensityId,
                sample.ContourSweep);
            tornContour.SetPropertyBlock(contourProperties);
        }

        private bool TryGetViewportBounds(
            IReadOnlyList<Renderer> renderers,
            out Rect viewportBounds)
        {
            viewportBounds = default;
            if (!TryGetWorldBounds(renderers, out Bounds bounds))
            {
                return false;
            }

            float minX = float.PositiveInfinity;
            float minY = float.PositiveInfinity;
            float maxX = float.NegativeInfinity;
            float maxY = float.NegativeInfinity;
            Vector3 center = bounds.center;
            Vector3 extents = bounds.extents;
            for (int x = -1; x <= 1; x += 2)
            {
                for (int y = -1; y <= 1; y += 2)
                {
                    for (int z = -1; z <= 1; z += 2)
                    {
                        Vector3 point = camera.WorldToViewportPoint(
                            center + Vector3.Scale(
                                extents,
                                new Vector3(x, y, z)));
                        if (point.z <= 0f)
                        {
                            continue;
                        }
                        minX = Mathf.Min(minX, point.x);
                        minY = Mathf.Min(minY, point.y);
                        maxX = Mathf.Max(maxX, point.x);
                        maxY = Mathf.Max(maxY, point.y);
                    }
                }
            }

            if (float.IsInfinity(minX)
                || float.IsInfinity(minY)
                || float.IsInfinity(maxX)
                || float.IsInfinity(maxY))
            {
                return false;
            }
            viewportBounds = Rect.MinMaxRect(minX, minY, maxX, maxY);
            return true;
        }

        private static bool TryGetWorldBounds(
            IReadOnlyList<Renderer> renderers,
            out Bounds bounds)
        {
            bounds = default;
            bool found = false;
            foreach (Renderer renderer in renderers)
            {
                if (renderer == null || !renderer.enabled)
                {
                    continue;
                }
                if (!found)
                {
                    bounds = renderer.bounds;
                    found = true;
                }
                else
                {
                    bounds.Encapsulate(renderer.bounds);
                }
            }
            return found;
        }

        private static float ResolveTearFront(float progress)
        {
            float[] samples = IsolatedR024Profile.AuthoredPoseProgresses;
            float clamped = Mathf.Clamp01(progress);
            for (int index = 1; index < samples.Length; index++)
            {
                if (clamped <= samples[index])
                {
                    float blend = Mathf.InverseLerp(
                        samples[index - 1],
                        samples[index],
                        clamped);
                    return Mathf.Lerp(
                        TearFrontByPose[index - 1],
                        TearFrontByPose[index],
                        blend);
                }
            }
            return TearFrontByPose[^1];
        }

        private string BuildStateFingerprint()
        {
            var builder = new StringBuilder(1024);
            AppendVector(builder, packRoot.localPosition);
            AppendQuaternion(builder, packRoot.localRotation);
            builder.Append(NormalizedTearFront.ToString("R")).Append('|');
            AppendVector(builder, caseMotionRoot.localPosition);
            AppendQuaternion(builder, caseMotionRoot.localRotation);
            foreach (SkinnedMeshRenderer renderer in packRenderers)
            {
                builder.Append(renderer.enabled ? '1' : '0');
                Mesh mesh = renderer.sharedMesh;
                foreach (string key in PoseKeys)
                {
                    builder.Append(renderer.GetBlendShapeWeight(
                        mesh.GetBlendShapeIndex(key)).ToString("R"))
                        .Append('|');
                }
            }
            return builder.ToString();
        }

        private static void AppendVector(StringBuilder builder, Vector3 value)
        {
            builder.Append(value.x.ToString("R")).Append('|')
                .Append(value.y.ToString("R")).Append('|')
                .Append(value.z.ToString("R")).Append('|');
        }

        private static void AppendQuaternion(
            StringBuilder builder,
            Quaternion value)
        {
            builder.Append(value.x.ToString("R")).Append('|')
                .Append(value.y.ToString("R")).Append('|')
                .Append(value.z.ToString("R")).Append('|')
                .Append(value.w.ToString("R")).Append('|');
        }
    }
}
