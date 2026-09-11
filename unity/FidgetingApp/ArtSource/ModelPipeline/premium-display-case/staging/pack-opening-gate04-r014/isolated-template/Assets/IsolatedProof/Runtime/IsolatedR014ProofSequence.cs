using System;
using System.Linq;
using FidgetingApp.DisplayCase.Candidates;
using UnityEngine;

namespace FidgetingApp.DisplayCase.IsolatedCandidate
{
    public sealed class IsolatedR014ProofSequence
    {
        public const float PackWidthMeters = 0.255f;
        public const float PackHeightMeters = 0.340f;
        public const float MouthDepthMeters = 0.070f;
        public const float FoilThicknessMeters = 0.00075f;
        public const float TopSealHeightFraction = 0.06470588f;

        private static readonly string[] PoseKeys =
        {
            "Pose_TabCatch",
            "Pose_NarrowPeel",
            "Pose_TearAdvance",
            "Pose_FormedMouth",
            "Pose_CaseContained",
            "Pose_ContinuousRise"
        };

        private readonly PackOpeningGate04R014Profile profile;
        private readonly Camera camera;
        private readonly Transform packRoot;
        private readonly SkinnedMeshRenderer[] packRenderers;
        private readonly SkinnedMeshRenderer frontFoil;
        private readonly SkinnedMeshRenderer topSeal;
        private readonly SkinnedMeshRenderer innerMouth;
        private readonly SkinnedMeshRenderer innerBackRim;
        private readonly SkinnedMeshRenderer rolledCrimpLip;
        private readonly SkinnedMeshRenderer tornContourRim;
        private readonly SkinnedMeshRenderer tornSealStrip;
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

        public IsolatedR014ProofSequence(
            PackOpeningGate04R014Profile profile,
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
            frontFoil = RequireRenderer("Pack_FrontFoil");
            topSeal = RequireRenderer("Pack_TopSealRemaining");
            innerMouth = RequireRenderer("Pack_InnerFoilMouth");
            innerBackRim = RequireRenderer("Pack_InnerBackFoilRim");
            rolledCrimpLip = RequireRenderer("Pack_RolledCrimpLip");
            tornContourRim = RequireRenderer("Pack_TornContourRim");
            tornSealStrip = RequireRenderer("Pack_TornSealStrip");
            pullTab = RequireRenderer("Pack_TopRightPullTab");
            caseRenderers = caseMotionRoot.GetComponentsInChildren<Renderer>(true);
            packBasePosition = packRoot.localPosition;
            caseBasePosition = caseMotionRoot.localPosition;
            caseBaseRotation = caseMotionRoot.localRotation;
            caseBaseScale = caseMotionRoot.localScale;
            ValidateBindings();
        }

        public PackOpeningGate04R014Sample CurrentSample { get; private set; }
        public EntityId CaseEntityId => caseMotionRoot.GetEntityId();

        public void SetTime(float seconds, bool effectsEnabled)
        {
            CurrentSample = profile.Evaluate(seconds);
            ApplyBlendShapeProgress(CurrentSample.TearProgress);
            ApplyPack(CurrentSample);
            ApplyCase(CurrentSample);
            ApplyContourSweep(CurrentSample, effectsEnabled);
        }

        public bool IsCaseContainedInMouth()
        {
            float depth = caseMotionRoot.position.z - packRoot.position.z;
            return CurrentSample.Occlusion == PackOpeningGate04R014Occlusion.CaseContained
                && depth >= 0.020f
                && depth <= MouthDepthMeters + 0.006f;
        }

        public Rect GetCaseViewportBounds()
        {
            return GetViewportBounds(caseRenderers);
        }

        private void ValidateBindings()
        {
            if (profile == null || camera == null || packRenderers.Length != 10
                || caseRenderers.Length == 0)
            {
                throw new InvalidOperationException("Isolated R014 bindings are incomplete.");
            }
            foreach (SkinnedMeshRenderer renderer in packRenderers)
            {
                if (renderer.sharedMesh == null
                    || renderer.sharedMesh.blendShapeCount != PoseKeys.Length)
                {
                    throw new InvalidOperationException(
                        $"Rig mesh {renderer.name} does not contain six R014 blend shapes.");
                }
            }
        }

        private SkinnedMeshRenderer RequireRenderer(string name)
        {
            SkinnedMeshRenderer renderer = packRenderers.SingleOrDefault(
                item => string.Equals(item.name, name, StringComparison.Ordinal));
            if (renderer == null)
            {
                throw new InvalidOperationException($"Missing rig renderer: {name}");
            }
            return renderer;
        }

        private void ApplyBlendShapeProgress(float progress)
        {
            float[] samples = PackOpeningGate04R014Profile.AuthoredPoseProgresses;
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
            if (progress >= samples[samples.Length - 1])
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
                    renderer.SetBlendShapeWeight(mesh.GetBlendShapeIndex(PoseKeys[index]), 0f);
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
                        mesh.GetBlendShapeIndex(PoseKeys[upper - 1]), blend * 100f);
                }
            }
        }

        private void ApplyPack(PackOpeningGate04R014Sample sample)
        {
            bool visible = sample.PackDissolve < 0.9995f;
            frontFoil.enabled = visible;
            topSeal.enabled = visible;
            innerMouth.enabled = visible && sample.TearProgress > 0.01f;
            innerBackRim.enabled = visible && sample.TearProgress > 0.01f;
            rolledCrimpLip.enabled = visible && sample.TearProgress > 0.04f;
            tornContourRim.enabled = visible && sample.TearProgress > 0.10f;
            tornSealStrip.enabled = visible
                && sample.TearProgress > 0.18f
                && sample.PackDissolve < 0.84f;
            pullTab.enabled = visible && sample.PackDissolve < 0.92f;
            packRoot.localPosition = packBasePosition + new Vector3(
                0f, -0.018f * sample.PackDissolve, 0.002f * sample.PackDissolve);
            ApplyPackProperties(frontFoil, sample.PackDissolve);
            ApplyPackProperties(topSeal, sample.PackDissolve);
        }

        private void ApplyPackProperties(Renderer renderer, float dissolve)
        {
            renderer.GetPropertyBlock(packProperties);
            packProperties.SetFloat(dissolveId, dissolve);
            packProperties.SetFloat(edgeStrengthId, 0.10f);
            renderer.SetPropertyBlock(packProperties);
        }

        private void ApplyCase(PackOpeningGate04R014Sample sample)
        {
            float travel = sample.CaseTravel;
            caseMotionRoot.localPosition = caseBasePosition
                + new Vector3(0f, 0.105f * travel, -0.055f * travel);
            caseMotionRoot.localRotation = caseBaseRotation
                * Quaternion.Euler(0f, -7f * (1f - travel), 0f);
            caseMotionRoot.localScale = caseBaseScale;
        }

        private void ApplyContourSweep(
            PackOpeningGate04R014Sample sample,
            bool effectsEnabled)
        {
            tornContourRim.GetPropertyBlock(contourProperties);
            contourProperties.SetFloat(sweepProgressId, sample.TearProgress);
            contourProperties.SetFloat(
                intensityId, effectsEnabled ? sample.OpticalSweep * 0.26f : 0f);
            tornContourRim.SetPropertyBlock(contourProperties);
        }

        private Rect GetViewportBounds(Renderer[] renderers)
        {
            Bounds bounds = default;
            bool found = false;
            foreach (Renderer renderer in renderers)
            {
                if (renderer == null || !renderer.enabled) continue;
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
            if (!found) return default;

            Vector3 center = bounds.center;
            Vector3 extents = bounds.extents;
            float minX = 1f;
            float minY = 1f;
            float maxX = 0f;
            float maxY = 0f;
            for (int x = -1; x <= 1; x += 2)
            for (int y = -1; y <= 1; y += 2)
            for (int z = -1; z <= 1; z += 2)
            {
                Vector3 point = camera.WorldToViewportPoint(
                    center + Vector3.Scale(extents, new Vector3(x, y, z)));
                if (point.z <= 0f) continue;
                minX = Mathf.Min(minX, point.x);
                minY = Mathf.Min(minY, point.y);
                maxX = Mathf.Max(maxX, point.x);
                maxY = Mathf.Max(maxY, point.y);
            }
            return Rect.MinMaxRect(minX, minY, maxX, maxY);
        }
    }
}
