using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FidgetingApp.Product;
using FidgetingApp.TwoLobeBar.Geometry;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EditorTools
{
    /// <summary>
    /// Produces a deterministic, machine-readable audit of the shipping product
    /// dimensions, camera occupancy and rotor-to-bearing axis alignment. The
    /// report intentionally uses real saved scenes rather than catalogue art.
    /// </summary>
    public static class SpinnerModelGeometryAudit
    {
        private const float PhoneAspect = 1290f / 2796f;
        private const string OutputFolder = "Artifacts/SpinnerModelGeometryAudit";

        [Serializable]
        private sealed class AuditReport
        {
            public string generatedUtc;
            public List<ProductAudit> products = new List<ProductAudit>();
        }

        [Serializable]
        private sealed class ProductAudit
        {
            public string modelId;
            public string scenePath;
            public string rootName;
            public Vector3 rootWorldScale;
            public Vector3 worldBoundsCenter;
            public Vector3 worldBoundsSize;
            public float planarSizeMillimeters;
            public float thicknessMillimeters;
            public Vector2 detailViewportFraction;
            public Vector2 libraryViewportFraction;
            public Vector3 rotorPivotWorld;
            public Vector3 rotorVisualBoundsCenterWorld;
            public Vector3 rotorBoundsCenterOffsetMillimeters;
            public Vector3 fixedHubCenterWorld;
            public Vector3 rotorToHubOffsetMillimeters;
            public Vector3 rotorRootLocalPosition;
            public Vector3 bearingOuterRaceLocalPosition;
            public Vector3 topCapCenterWorld;
            public Vector3 rotorToTopCapOffsetMillimeters;
            public List<RingAudit> circularRenderers = new List<RingAudit>();
        }

        [Serializable]
        private sealed class RingAudit
        {
            public string path;
            public string material;
            public Vector3 worldSizeMillimeters;
            public Vector3 centerOffsetFromRotorMillimeters;
            public bool rotatesWithRotor;
        }

        private readonly struct ProductDefinition
        {
            public ProductDefinition(string modelId, string scenePath, string rootName)
            {
                ModelId = modelId;
                ScenePath = scenePath;
                RootName = rootName;
            }

            public string ModelId { get; }
            public string ScenePath { get; }
            public string RootName { get; }
        }

        [MenuItem("Tools/Codex/Audit Shipping Spinner Geometry")]
        public static void Capture()
        {
            var definitions = new[]
            {
                new ProductDefinition(
                    ProductCatalog.PointedThreeBladeModelId,
                    SpinnerEnvironmentCatalog.PointedScenePath,
                    "ThreeBladeEDC_Root"),
                new ProductDefinition(
                    ProductCatalog.MetalThreeBladeModelId,
                    SpinnerEnvironmentCatalog.MetalScenePath,
                    "ThreeBladeEDC_Root"),
                new ProductDefinition(
                    ProductCatalog.GoldFourWingModelId,
                    SpinnerEnvironmentCatalog.ImportedScenePath,
                    "ImportedSpinner_Root"),
                new ProductDefinition(
                    ProductCatalog.GraphiteTwoLobeModelId,
                    TwoLobeBarSpecifications.ScenePath,
                    "TwoLobeBar_Root")
            };

            var report = new AuditReport
            {
                generatedUtc = DateTime.UtcNow.ToString("O")
            };
            SceneSetup[] previousSetup = EditorSceneManager.GetSceneManagerSetup();
            try
            {
                foreach (ProductDefinition definition in definitions)
                {
                    report.products.Add(Audit(definition));
                }
            }
            finally
            {
                if (previousSetup.Length > 0)
                {
                    EditorSceneManager.RestoreSceneManagerSetup(previousSetup);
                }
            }

            string projectRoot = Directory.GetParent(Application.dataPath).FullName;
            string outputFolder = Path.Combine(projectRoot, OutputFolder);
            Directory.CreateDirectory(outputFolder);
            string outputPath = Path.Combine(outputFolder, "model-geometry-audit.json");
            File.WriteAllText(outputPath, JsonUtility.ToJson(report, true));
            Debug.Log($"[SpinnerModelGeometryAudit] {outputPath}");
        }

        private static ProductAudit Audit(ProductDefinition definition)
        {
            Scene scene = EditorSceneManager.OpenScene(
                definition.ScenePath,
                OpenSceneMode.Single);
            Transform root = scene.GetRootGameObjects()
                .Select(item => item.transform)
                .Single(item => item.name == definition.RootName);
            OrbitPresentationCamera orbit = UnityEngine.Object.FindAnyObjectByType<
                OrbitPresentationCamera>();
            if (orbit == null)
            {
                throw new InvalidDataException(
                    $"{definition.ScenePath} has no OrbitPresentationCamera.");
            }

            Camera camera = orbit.GetComponent<Camera>();
            camera.aspect = PhoneAspect;
            orbit.Target = root;
            orbit.ConfigureFraming(ProductFramingCatalog.Resolve(definition.ScenePath));
            orbit.ResetHero();
            orbit.FrameNow();

            if (!ProductCameraFraming.TryGetProductBounds(root, out Bounds bounds))
            {
                throw new InvalidDataException(
                    $"{definition.ScenePath} has no product render bounds.");
            }

            Vector2 detailViewport = ProductCameraFraming.ProjectedViewportSize(
                camera,
                bounds);
            orbit.SetLibraryPreviewActive(true, true);
            orbit.FrameNow();
            Vector2 libraryViewport = ProductCameraFraming.ProjectedViewportSize(
                camera,
                bounds);

            Transform rotor = root.Find("RotorDynamic");
            Transform hub = root.Find("HubStatic");
            if (rotor == null || hub == null)
            {
                throw new InvalidDataException(
                    $"{definition.ScenePath} does not expose RotorDynamic/HubStatic.");
            }

            Renderer[] rotorRenderers = rotor.GetComponentsInChildren<Renderer>(true)
                .Where(IsProductRenderer)
                .ToArray();
            Bounds rotorBounds = CombinedBounds(rotorRenderers);
            Transform rotorRoot = FindDescendant(rotor, "Rotor_Root");
            Transform outerRace = FindDescendant(rotor, "BearingOuterRace");
            Transform topCap = FindDescendant(hub, "TopCap_Root")
                ?? FindDescendant(hub, "TopButton")
                ?? FindDescendant(hub, "TopCap");
            Vector3 topCapCenter = topCap != null
                ? CombinedBounds(topCap.GetComponentsInChildren<Renderer>(true)
                    .Where(IsProductRenderer)
                    .ToArray()).center
                : hub.position;

            var product = new ProductAudit
            {
                modelId = definition.ModelId,
                scenePath = definition.ScenePath,
                rootName = definition.RootName,
                rootWorldScale = root.lossyScale,
                worldBoundsCenter = bounds.center,
                worldBoundsSize = bounds.size,
                planarSizeMillimeters = Mathf.Max(bounds.size.x, bounds.size.z) * 1000f,
                thicknessMillimeters = bounds.size.y * 1000f,
                detailViewportFraction = detailViewport,
                libraryViewportFraction = libraryViewport,
                rotorPivotWorld = rotor.position,
                rotorVisualBoundsCenterWorld = rotorBounds.center,
                rotorBoundsCenterOffsetMillimeters =
                    (rotorBounds.center - rotor.position) * 1000f,
                fixedHubCenterWorld = hub.position,
                rotorToHubOffsetMillimeters = (rotor.position - hub.position) * 1000f,
                rotorRootLocalPosition = rotorRoot != null
                    ? rotor.InverseTransformPoint(rotorRoot.position)
                    : Vector3.zero,
                bearingOuterRaceLocalPosition = outerRace != null
                    ? rotor.InverseTransformPoint(outerRace.position)
                    : Vector3.zero,
                topCapCenterWorld = topCapCenter,
                rotorToTopCapOffsetMillimeters =
                    (rotor.position - topCapCenter) * 1000f
            };

            foreach (Renderer renderer in root.GetComponentsInChildren<Renderer>(true)
                         .Where(IsProductRenderer)
                         .Where(IsCircularAxisRenderer)
                         .OrderBy(item => HierarchyPath(item.transform)))
            {
                product.circularRenderers.Add(new RingAudit
                {
                    path = HierarchyPath(renderer.transform),
                    material = renderer.sharedMaterial != null
                        ? renderer.sharedMaterial.name
                        : string.Empty,
                    worldSizeMillimeters = renderer.bounds.size * 1000f,
                    centerOffsetFromRotorMillimeters =
                        (renderer.bounds.center - rotor.position) * 1000f,
                    rotatesWithRotor = renderer.transform.IsChildOf(rotor)
                });
            }

            return product;
        }

        private static bool IsProductRenderer(Renderer renderer)
        {
            return renderer != null
                && renderer.enabled
                && renderer.gameObject.activeInHierarchy
                && renderer.GetComponentInParent<Camera>() == null;
        }

        private static bool IsCircularAxisRenderer(Renderer renderer)
        {
            string name = renderer.name.ToLowerInvariant();
            return name.Contains("bearing")
                || name.Contains("shield")
                || name.Contains("race")
                || name.Contains("ring")
                || name.Contains("washer")
                || name.Contains("bezel")
                || name.Contains("collar")
                || name.Contains("trim")
                || name.Contains("gap")
                || name.Contains("cap")
                || name.Contains("button")
                || name.Contains("axle");
        }

        private static Transform FindDescendant(Transform root, string name)
        {
            return root.GetComponentsInChildren<Transform>(true)
                .FirstOrDefault(item => item.name == name);
        }

        private static Bounds CombinedBounds(Renderer[] renderers)
        {
            if (renderers == null || renderers.Length == 0)
            {
                return new Bounds(Vector3.zero, Vector3.zero);
            }

            Bounds bounds = renderers[0].bounds;
            for (int index = 1; index < renderers.Length; index++)
            {
                bounds.Encapsulate(renderers[index].bounds);
            }
            return bounds;
        }

        private static string HierarchyPath(Transform transform)
        {
            var names = new Stack<string>();
            Transform current = transform;
            while (current != null)
            {
                names.Push(current.name);
                current = current.parent;
            }
            return string.Join("/", names);
        }
    }
}
