using System;
using System.Collections.Generic;
using FidgetingApp.FanCard;
using FidgetingApp.Product;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.DisplayCase
{
    /// <summary>
    /// Prize-only conversion from a product's authored front to the one shared
    /// magnetic-slide case presentation. This rotation is baked into the
    /// renderer-only snapshot; it never changes the case, camera or animation.
    /// </summary>
    public readonly struct PremiumDisplayCasePrizeNormalization
    {
        public PremiumDisplayCasePrizeNormalization(
            Vector3 canonicalFrontEulerAngles)
        {
            CanonicalFrontEulerAngles = canonicalFrontEulerAngles;
        }

        public Vector3 CanonicalFrontEulerAngles { get; }

        public Quaternion SnapshotLocalRotation
        {
            get
            {
                Quaternion sharedCaseRotation = Quaternion.Euler(
                    PremiumDisplayCaseProductProfiles.SharedContentOptions
                        .InitialEulerAngles);
                Quaternion canonicalFrontRotation = Quaternion.Euler(
                    CanonicalFrontEulerAngles);
                return Quaternion.Inverse(sharedCaseRotation)
                    * canonicalFrontRotation;
            }
        }

        public Matrix4x4 SnapshotLocalMatrix =>
            Matrix4x4.Rotate(SnapshotLocalRotation);
    }

    public readonly struct PremiumDisplayCaseProductProfile
    {
        public PremiumDisplayCaseProductProfile(
            string modelId,
            string englishDisplayName,
            string sceneRootName,
            PremiumDisplayCasePrizeNormalization prizeNormalization)
        {
            ModelId = modelId ?? string.Empty;
            EnglishDisplayName = englishDisplayName ?? string.Empty;
            SceneRootName = sceneRootName ?? string.Empty;
            PrizeNormalization = prizeNormalization;
        }

        public string ModelId { get; }
        public string EnglishDisplayName { get; }
        public string SceneRootName { get; }
        public PremiumDisplayCasePrizeNormalization PrizeNormalization { get; }
        public PremiumDisplayCaseCapsulePreset CapsulePreset =>
            PremiumDisplayCaseProductProfiles.SharedCapsulePreset;
        public PremiumDisplayCaseCapsuleDimensions CapsuleDimensions =>
            PremiumDisplayCaseProductProfiles.SharedCapsuleDimensions;
        public Vector3 PresentationOffset =>
            PremiumDisplayCaseProductProfiles.SharedPresentationOffset;
        public PremiumDisplayCaseContentOptions ContentOptions =>
            PremiumDisplayCaseProductProfiles.ResolveContentOptions(ModelId);
    }

    /// <summary>
    /// All products use the approved magnetic-slide collector presentation.
    /// Profiles only identify the prize source and normalize its authored front
    /// inside the renderer-only snapshot. The case, capsule, camera, offset,
    /// reveal and assembly never vary by product. The one-sided fan-card prize
    /// alone holds its readable front instead of idling onto its blank back.
    /// </summary>
    public static class PremiumDisplayCaseProductProfiles
    {
        public const PremiumDisplayCaseCapsulePreset SharedCapsulePreset =
            PremiumDisplayCaseCapsulePreset.RoundedSquareDeep;

        private static readonly PremiumDisplayCaseCapsuleDimensions
            sharedCapsuleDimensions = PremiumDisplayCaseCapsulePresets.Resolve(
                SharedCapsulePreset);
        private static readonly PremiumDisplayCaseContentOptions
            sharedContentOptions = new PremiumDisplayCaseContentOptions(
                true,
                6f,
                new Vector3(90f, -8f, 0f));
        private static readonly PremiumDisplayCaseContentOptions
            readableFrontContentOptions = new PremiumDisplayCaseContentOptions(
                false,
                sharedContentOptions.IdleRotationPeriodSeconds,
                sharedContentOptions.InitialEulerAngles);

        public static PremiumDisplayCaseCapsuleDimensions SharedCapsuleDimensions =>
            sharedCapsuleDimensions;
        public static PremiumDisplayCaseContentOptions SharedContentOptions =>
            sharedContentOptions;
        public static Vector3 SharedPresentationOffset => Vector3.zero;

        /// <summary>
        /// The case, camera, capsule, initial pose, reveal and assembly stay
        /// identical for every product. The fan-card prize is the sole
        /// one-sided mechanical object: turning the shared content orbit by
        /// 180 degrees exposes an intentionally blank back. Keep that
        /// renderer-only snapshot on its composed Q/K/A front after reveal.
        /// </summary>
        public static PremiumDisplayCaseContentOptions ResolveContentOptions(
            string modelId)
        {
            return string.Equals(
                    modelId,
                    ProductCatalog.MagneticFanCardModelId,
                    StringComparison.Ordinal)
                ? readableFrontContentOptions
                : sharedContentOptions;
        }

        private static readonly PremiumDisplayCaseProductProfile[] profiles =
        {
            Profile(
                ProductCatalog.PointedThreeBladeModelId,
                "EDGE TRIAD",
                "ThreeBladeEDC_Root",
                NormalizeAuthoredFront(90f, -18f)),
            Profile(
                ProductCatalog.MetalThreeBladeModelId,
                "MAGNETIC TRINITY",
                "ThreeBladeEDC_Root",
                NormalizeAuthoredFront(-90f, -8f)),
            Profile(
                ProductCatalog.GoldFourWingModelId,
                "MIRROR QUAD",
                "ImportedSpinner_Root",
                NormalizeAuthoredFront(90f, -12f)),
            Profile(
                ProductCatalog.GraphiteTwoLobeModelId,
                "GRAPHITE DUO",
                "TwoLobeBar_Root",
                NormalizeAuthoredFront(90f, -10f)),
            Profile(
                ProductCatalog.MagneticSlideTileModelId,
                "MAGNETIC SLIDE",
                "EDC_Root",
                NormalizeAuthoredFront(90f, -8f)),
            Profile(
                ProductCatalog.MagneticFanCardModelId,
                "MAGNETIC FAN",
                "MagneticFanCard_Root",
                NormalizeAuthoredFront(-90f, 0f))
        };

        public static IReadOnlyList<PremiumDisplayCaseProductProfile> Profiles =>
            profiles;

        public static PremiumDisplayCaseProductProfile Resolve(string modelId)
        {
            for (int index = 0; index < profiles.Length; index++)
            {
                if (string.Equals(
                        profiles[index].ModelId,
                        modelId,
                        StringComparison.Ordinal))
                {
                    return profiles[index];
                }
            }

            return Profile(
                string.IsNullOrEmpty(modelId)
                    ? ProductCatalog.MetalThreeBladeModelId
                    : modelId,
                "COLLECTOR EDITION",
                "ThreeBladeEDC_Root",
                NormalizeAuthoredFront(-90f, -8f));
        }

        private static PremiumDisplayCaseProductProfile Profile(
            string modelId,
            string englishDisplayName,
            string sceneRootName,
            PremiumDisplayCasePrizeNormalization prizeNormalization)
        {
            return new PremiumDisplayCaseProductProfile(
                modelId,
                englishDisplayName,
                sceneRootName,
                prizeNormalization);
        }

        private static PremiumDisplayCasePrizeNormalization NormalizeAuthoredFront(
            float pitchDegrees,
            float yawDegrees)
        {
            return new PremiumDisplayCasePrizeNormalization(
                new Vector3(pitchDegrees, yawDegrees, 0f));
        }
    }

    /// <summary>
    /// Produces a renderer-only snapshot of the current product. Runtime scripts,
    /// colliders, rigidbodies, cameras, audio and input never enter the case.
    /// Shared meshes/materials and renderer property blocks are preserved so the
    /// snapshot matches the selected product's current skin and sticker state.
    /// </summary>
    public static class PremiumDisplayCaseProductSnapshot
    {
        public static GameObject Capture(string modelId, Transform sourceRoot)
        {
            if (sourceRoot == null)
            {
                throw new ArgumentNullException(nameof(sourceRoot));
            }

            FanCardFaceRankPresenter fanRankPresenter = null;
            FanCardRankPattern previousFanRankPattern = default;
            bool restoreFanRankPattern = false;
            if (string.Equals(modelId, ProductCatalog.MagneticFanCardModelId,
                    StringComparison.Ordinal))
            {
                // The collector card is deliberately a readable product pose,
                // not the current live detent. Temporarily select the approved
                // whole-set Q/K/A face state only while copying meshes, then
                // restore the active detail/library state unchanged.
                fanRankPresenter = sourceRoot.GetComponent<FanCardFaceRankPresenter>();
                if (fanRankPresenter != null)
                {
                    previousFanRankPattern = fanRankPresenter.CurrentPattern;
                    fanRankPresenter.ApplyPattern(FanCardRankPattern.QueenKingAce);
                    restoreFanRankPattern = true;
                }
            }

            Renderer[] sourceRenderers = sourceRoot.GetComponentsInChildren<Renderer>(
                false);
            var snapshot = new GameObject(
                $"DisplayCasePrize_{NormalizeName(modelId)}");
            snapshot.SetActive(false);
            PremiumDisplayCaseRuntimeMeshOwner meshOwner =
                snapshot.AddComponent<PremiumDisplayCaseRuntimeMeshOwner>();

            int capturedCount = 0;
            try
            {
                for (int index = 0; index < sourceRenderers.Length; index++)
                {
                    Renderer source = sourceRenderers[index];
                    if (!ShouldCapture(source))
                    {
                        continue;
                    }

                    Mesh mesh = ResolveMesh(source, meshOwner);
                    if (mesh == null)
                    {
                        continue;
                    }

                    GameObject visual = new GameObject(
                        $"Visual_{capturedCount:00}_{source.gameObject.name}");
                    visual.layer = source.gameObject.layer;
                    visual.transform.SetParent(snapshot.transform, false);
                    Matrix4x4 finalPose = ResolveCollectorPose(
                        modelId,
                        sourceRoot,
                        source.transform);
                    ApplySourceRelativeTransform(
                        visual.transform,
                        sourceRoot,
                        source.transform,
                        finalPose);

                    MeshFilter filter = visual.AddComponent<MeshFilter>();
                    filter.sharedMesh = mesh;
                    MeshRenderer target = visual.AddComponent<MeshRenderer>();
                    CopyRenderer(source, target);
                    capturedCount++;
                }
            }
            finally
            {
                if (restoreFanRankPattern)
                {
                    fanRankPresenter.ApplyPattern(previousFanRankPattern);
                }
            }

            if (capturedCount == 0)
            {
                UnityEngine.Object.DestroyImmediate(snapshot);
                throw new MissingReferenceException(
                    $"No visible product renderers were available for {modelId}.");
            }

            return snapshot;
        }

        /// <summary>
        /// Refreshes only materials and renderer property blocks on an already
        /// captured canonical prize. Geometry transforms intentionally remain
        /// untouched so a skin/sticker change cannot bake live spin, slide or
        /// fan state into the collector presentation.
        /// </summary>
        public static bool RefreshAppearance(
            GameObject snapshot,
            Transform sourceRoot)
        {
            if (snapshot == null || sourceRoot == null)
            {
                return false;
            }

            Renderer[] targets = snapshot.GetComponentsInChildren<Renderer>(true);
            Renderer[] sources = sourceRoot.GetComponentsInChildren<Renderer>(false);
            var capturedSources = new List<Renderer>();
            for (int index = 0; index < sources.Length; index++)
            {
                if (ShouldCapture(sources[index]) && HasRenderableMesh(sources[index]))
                {
                    capturedSources.Add(sources[index]);
                }
            }
            if (targets.Length != capturedSources.Count)
            {
                return false;
            }

            for (int index = 0; index < targets.Length; index++)
            {
                CopyRenderer(capturedSources[index], (MeshRenderer)targets[index]);
            }
            return true;
        }

        private static void ApplySourceRelativeTransform(
            Transform target,
            Transform sourceRoot,
            Transform source,
            Matrix4x4 collectorPose)
        {
            // The shipping product may already be translated, scaled or orbited
            // by the detail/library presentation when the case is opened. Those
            // presentation transforms must not become prize geometry. Preserve
            // only the renderer pose relative to the authoritative product root.
            Matrix4x4 relative = collectorPose * (sourceRoot.worldToLocalMatrix
                * source.localToWorldMatrix);
            target.localPosition = relative.GetPosition();
            target.localRotation = relative.rotation;
            target.localScale = relative.lossyScale;
        }

        private static Matrix4x4 ResolveCollectorPose(
            string modelId,
            Transform sourceRoot,
            Transform source)
        {
            Matrix4x4 normalization = PremiumDisplayCaseProductProfiles
                .Resolve(modelId)
                .PrizeNormalization
                .SnapshotLocalMatrix;
            if (!string.Equals(modelId, ProductCatalog.MagneticFanCardModelId,
                    StringComparison.Ordinal))
            {
                return normalization;
            }

            Transform middle = sourceRoot.Find("MiddleCard");
            Transform top = sourceRoot.Find("TopCard");
            if (middle != null && source.IsChildOf(middle))
            {
                return normalization
                    * FanLayerCorrection(sourceRoot, middle, 45f);
            }
            if (top != null && source.IsChildOf(top))
            {
                return normalization
                    * FanLayerCorrection(sourceRoot, top, 90f);
            }
            return normalization;
        }

        private static Matrix4x4 FanLayerCorrection(
            Transform sourceRoot,
            Transform layer,
            float targetDegrees)
        {
            // Apply the renderer-only equivalent of SetFanProgress(1): bottom
            // remains fixed, middle is +45°, top is +90°. The live controller,
            // detents, colliders and Haptic state are never touched.
            Matrix4x4 current = sourceRoot.worldToLocalMatrix
                * layer.localToWorldMatrix;
            Matrix4x4 canonical = Matrix4x4.TRS(
                current.GetPosition(),
                Quaternion.Euler(0f, targetDegrees, 0f),
                current.lossyScale);
            return canonical * current.inverse;
        }

        /// <summary>
        /// Defines the exact renderer set represented by a display-case
        /// snapshot. Shipping presentation uses this same predicate when it
        /// hides the live product, so scene cameras, studios, grounding and
        /// particle/line effects always remain active.
        /// </summary>
        public static bool ShouldCapture(Renderer renderer)
        {
            return renderer != null
                && renderer.enabled
                && renderer.gameObject.activeInHierarchy
                && !(renderer is ParticleSystemRenderer)
                && !(renderer is LineRenderer)
                && renderer.GetComponentInParent<Camera>() == null
                && renderer.GetComponentInParent<SpinnerGroundingStage>() == null;
        }

        private static Mesh ResolveMesh(
            Renderer source,
            PremiumDisplayCaseRuntimeMeshOwner meshOwner)
        {
            if (source is MeshRenderer)
            {
                MeshFilter filter = source.GetComponent<MeshFilter>();
                return filter != null ? filter.sharedMesh : null;
            }

            if (source is SkinnedMeshRenderer skinned && skinned.sharedMesh != null)
            {
                var baked = new Mesh
                {
                    name = $"{skinned.sharedMesh.name}_DisplayCaseSnapshot"
                };
                skinned.BakeMesh(baked, true);
                meshOwner.Add(baked);
                return baked;
            }

            return null;
        }

        private static bool HasRenderableMesh(Renderer source)
        {
            if (source is MeshRenderer)
            {
                MeshFilter filter = source.GetComponent<MeshFilter>();
                return filter != null && filter.sharedMesh != null;
            }
            return source is SkinnedMeshRenderer skinned
                && skinned.sharedMesh != null;
        }

        private static void CopyRenderer(Renderer source, MeshRenderer target)
        {
            target.sharedMaterials = source.sharedMaterials;
            target.shadowCastingMode = source.shadowCastingMode;
            target.receiveShadows = source.receiveShadows;
            target.motionVectorGenerationMode = MotionVectorGenerationMode.ForceNoMotion;
            target.lightProbeUsage = LightProbeUsage.Off;
            target.reflectionProbeUsage = source.reflectionProbeUsage;
            target.allowOcclusionWhenDynamic = source.allowOcclusionWhenDynamic;
            target.renderingLayerMask = source.renderingLayerMask;
            target.sortingLayerID = source.sortingLayerID;
            target.sortingOrder = source.sortingOrder;

            var properties = new MaterialPropertyBlock();
            source.GetPropertyBlock(properties);
            target.SetPropertyBlock(properties);
            for (int materialIndex = 0;
                 materialIndex < source.sharedMaterials.Length;
                 materialIndex++)
            {
                properties.Clear();
                source.GetPropertyBlock(properties, materialIndex);
                target.SetPropertyBlock(properties, materialIndex);
            }
        }

        private static string NormalizeName(string modelId)
        {
            return string.IsNullOrWhiteSpace(modelId)
                ? "CurrentProduct"
                : modelId.Replace('-', '_');
        }
    }

    [DisallowMultipleComponent]
    public sealed class PremiumDisplayCaseRuntimeMeshOwner : MonoBehaviour
    {
        private readonly List<Mesh> meshes = new List<Mesh>();

        public void Add(Mesh mesh)
        {
            if (mesh != null)
            {
                meshes.Add(mesh);
            }
        }

        private void OnDestroy()
        {
            for (int index = 0; index < meshes.Count; index++)
            {
                if (meshes[index] == null)
                {
                    continue;
                }
                if (Application.isPlaying)
                {
                    UnityEngine.Object.Destroy(meshes[index]);
                }
                else
                {
                    UnityEngine.Object.DestroyImmediate(meshes[index]);
                }
            }
            meshes.Clear();
        }
    }
}
