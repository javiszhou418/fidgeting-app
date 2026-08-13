using System;
using System.Collections.Generic;
using FidgetingApp.Product;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.DisplayCase
{
    public readonly struct PremiumDisplayCaseProductProfile
    {
        public PremiumDisplayCaseProductProfile(
            string modelId,
            string englishDisplayName,
            string sceneRootName,
            PremiumDisplayCaseCapsulePreset capsulePreset,
            PremiumDisplayCaseContentOptions contentOptions)
        {
            ModelId = modelId ?? string.Empty;
            EnglishDisplayName = englishDisplayName ?? string.Empty;
            SceneRootName = sceneRootName ?? string.Empty;
            CapsulePreset = capsulePreset;
            ContentOptions = contentOptions;
        }

        public string ModelId { get; }
        public string EnglishDisplayName { get; }
        public string SceneRootName { get; }
        public PremiumDisplayCaseCapsulePreset CapsulePreset { get; }
        public PremiumDisplayCaseContentOptions ContentOptions { get; }
    }

    /// <summary>
    /// Product-specific packaging presentation. The outer acrylic collector case
    /// stays authored at its approved physical dimensions; the neutral capsule,
    /// content plane and idle turn are selected from the current shipping model.
    /// </summary>
    public static class PremiumDisplayCaseProductProfiles
    {
        private const PremiumDisplayCaseCapsulePreset MagneticSlideBaselineCapsule =
            PremiumDisplayCaseCapsulePreset.RoundedSquareDeep;
        private static readonly PremiumDisplayCaseContentOptions
            MagneticSlideBaselineContent = FacingOptions(90f, -8f, 6f);

        private static readonly PremiumDisplayCaseProductProfile[] profiles =
        {
            BaselineProfile(
                ProductCatalog.PointedThreeBladeModelId,
                "EDGE TRIAD",
                "ThreeBladeEDC_Root"),
            BaselineProfile(
                ProductCatalog.MetalThreeBladeModelId,
                "MAGNETIC TRINITY",
                "ThreeBladeEDC_Root"),
            BaselineProfile(
                ProductCatalog.GoldFourWingModelId,
                "MIRROR QUAD",
                "ImportedSpinner_Root"),
            BaselineProfile(
                ProductCatalog.GraphiteTwoLobeModelId,
                "GRAPHITE DUO",
                "TwoLobeBar_Root"),
            BaselineProfile(
                ProductCatalog.MagneticSlideTileModelId,
                "MAGNETIC SLIDE",
                "EDC_Root"),
            Profile(
                ProductCatalog.MagneticFanCardModelId,
                "MAGNETIC FAN",
                "MagneticFanCard_Root",
                // Card faces point up in the authored XZ plane. The other
                // products use +90 degrees, but that exposes the fan's plain
                // rear face to the display-case camera. Use the mirrored plane
                // conversion so the A/Q/K artwork remains visible.
                FacingOptions(-90f, -8f, 6f))
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

            return BaselineProfile(
                string.IsNullOrEmpty(modelId)
                    ? ProductCatalog.MetalThreeBladeModelId
                    : modelId,
                "COLLECTOR EDITION",
                "ThreeBladeEDC_Root");
        }

        private static PremiumDisplayCaseProductProfile BaselineProfile(
            string modelId,
            string englishDisplayName,
            string sceneRootName)
        {
            return Profile(
                modelId,
                englishDisplayName,
                sceneRootName,
                MagneticSlideBaselineContent);
        }

        private static PremiumDisplayCaseProductProfile Profile(
            string modelId,
            string englishDisplayName,
            string sceneRootName,
            PremiumDisplayCaseContentOptions contentOptions)
        {
            return new PremiumDisplayCaseProductProfile(
                modelId,
                englishDisplayName,
                sceneRootName,
                MagneticSlideBaselineCapsule,
                contentOptions);
        }

        private static PremiumDisplayCaseContentOptions FacingOptions(
            float pitchDegrees,
            float yawDegrees,
            float idlePeriodSeconds)
        {
            return new PremiumDisplayCaseContentOptions(
                true,
                idlePeriodSeconds,
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

            Renderer[] sourceRenderers = sourceRoot.GetComponentsInChildren<Renderer>(
                false);
            var snapshot = new GameObject(
                $"DisplayCasePrize_{NormalizeName(modelId)}");
            snapshot.SetActive(false);
            PremiumDisplayCaseRuntimeMeshOwner meshOwner =
                snapshot.AddComponent<PremiumDisplayCaseRuntimeMeshOwner>();

            int capturedCount = 0;
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
                ApplySourceRelativeTransform(
                    visual.transform,
                    sourceRoot,
                    source.transform);

                MeshFilter filter = visual.AddComponent<MeshFilter>();
                filter.sharedMesh = mesh;
                MeshRenderer target = visual.AddComponent<MeshRenderer>();
                CopyRenderer(source, target);
                capturedCount++;
            }

            if (capturedCount == 0)
            {
                UnityEngine.Object.DestroyImmediate(snapshot);
                throw new MissingReferenceException(
                    $"No visible product renderers were available for {modelId}.");
            }

            return snapshot;
        }

        private static void ApplySourceRelativeTransform(
            Transform target,
            Transform sourceRoot,
            Transform source)
        {
            // The shipping product may already be translated, scaled or orbited
            // by the detail/library presentation when the case is opened. Those
            // presentation transforms must not become prize geometry. Preserve
            // only the renderer pose relative to the authoritative product root.
            Matrix4x4 relative = sourceRoot.worldToLocalMatrix
                * source.localToWorldMatrix;
            target.localPosition = relative.GetPosition();
            target.localRotation = relative.rotation;
            target.localScale = relative.lossyScale;
        }

        private static bool ShouldCapture(Renderer renderer)
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
