using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.FanCard.EditorTools
{
    public static class FanCardVisualModelIntegrator
    {
        public const string VisualModelPath =
            "Assets/_FanCard/Models/MagneticFanCardVisual.fbx";

        [MenuItem("Tools/Codex/Fan Card/Import Authoritative Visual FBX")]
        public static void IntegrateMenu()
        {
            Integrate();
        }

        public static void IntegrateBatch()
        {
            Integrate();
        }

        public static void AuditGeneratedBatch()
        {
            Mesh mesh = AssetDatabase.LoadAssetAtPath<Mesh>(
                "Assets/_FanCard/Generated/Meshes/M_FanCardBody.asset");
            if (mesh == null)
            {
                throw new MissingReferenceException("Generated Fan Card body is missing.");
            }
            foreach (Vector2 point in new[]
            {
                Vector2.zero,
                new Vector2(
                    FanCardSpecifications.PivotX,
                    FanCardSpecifications.PivotZ),
                new Vector2(
                    -FanCardSpecifications.PivotX,
                    -FanCardSpecifications.PivotZ)
            })
            {
                bool topContains = CapContainsPoint(
                    mesh,
                    point,
                    FanCardSpecifications.CardThickness * 0.5f);
                Debug.Log(
                    $"[FanCardVisualHole] point={point}; "
                    + $"topContains={topContains}");
            }
        }

        private static bool CapContainsPoint(Mesh mesh, Vector2 point, float y)
        {
            Vector3[] vertices = mesh.vertices;
            int[] triangles = mesh.triangles;
            for (int index = 0; index < triangles.Length; index += 3)
            {
                Vector3 a = vertices[triangles[index]];
                Vector3 b = vertices[triangles[index + 1]];
                Vector3 c = vertices[triangles[index + 2]];
                if (Mathf.Abs(a.y - y) > 0.00001f
                    || Mathf.Abs(b.y - y) > 0.00001f
                    || Mathf.Abs(c.y - y) > 0.00001f)
                {
                    continue;
                }
                float d1 = Cross(point, new Vector2(a.x, a.z), new Vector2(b.x, b.z));
                float d2 = Cross(point, new Vector2(b.x, b.z), new Vector2(c.x, c.z));
                float d3 = Cross(point, new Vector2(c.x, c.z), new Vector2(a.x, a.z));
                bool hasNegative = d1 < -0.0000001f
                    || d2 < -0.0000001f
                    || d3 < -0.0000001f;
                bool hasPositive = d1 > 0.0000001f
                    || d2 > 0.0000001f
                    || d3 > 0.0000001f;
                if (!(hasNegative && hasPositive))
                {
                    return true;
                }
            }
            return false;
        }

        private static float Cross(Vector2 point, Vector2 a, Vector2 b)
        {
            return (point.x - b.x) * (a.y - b.y)
                - (a.x - b.x) * (point.y - b.y);
        }

        private static void Integrate()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string source = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-fan-card/evidence/"
                    + "10-export/rev-003/magnetic-fan-card.fbx");
            string destination = Path.Combine(projectRoot, VisualModelPath);
            if (!File.Exists(source))
            {
                throw new FileNotFoundException(
                    "The authoritative smooth-normal Fan Card FBX is missing.",
                    source);
            }
            Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
            File.Copy(source, destination, true);
            AssetDatabase.ImportAsset(
                VisualModelPath,
                ImportAssetOptions.ForceSynchronousImport
                    | ImportAssetOptions.ForceUpdate);
            ModelImporter importer =
                AssetImporter.GetAtPath(VisualModelPath) as ModelImporter;
            if (importer == null)
            {
                throw new InvalidDataException(
                    $"No ModelImporter for {VisualModelPath}.");
            }
            importer.globalScale = 1f;
            importer.useFileScale = true;
            importer.bakeAxisConversion = true;
            importer.preserveHierarchy = true;
            importer.importCameras = false;
            importer.importLights = false;
            importer.importAnimation = false;
            importer.animationType = ModelImporterAnimationType.None;
            importer.importBlendShapes = false;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            importer.importNormals = ModelImporterNormals.Import;
            importer.importTangents = ModelImporterTangents.CalculateMikk;
            importer.isReadable = true;
            importer.optimizeMeshPolygons = false;
            importer.optimizeMeshVertices = false;
            importer.SaveAndReimport();

            Mesh[] meshes = AssetDatabase.LoadAllAssetsAtPath(VisualModelPath)
                .OfType<Mesh>()
                .ToArray();
            string[] required =
            {
                "BottomCard_GunmetalFrame",
                "BottomCard_GoldTrim",
                "BottomCard_WarmSilverFace"
            };
            foreach (string name in required)
            {
                Mesh mesh = meshes.FirstOrDefault(candidate =>
                    candidate.name == name || candidate.name == name + "_Mesh");
                if (mesh == null)
                {
                    throw new InvalidDataException(
                        $"Authoritative visual mesh is missing: {name}.");
                }
                Debug.Log(
                    $"[FanCardVisualModel] {mesh.name}: "
                    + $"verts={mesh.vertexCount}, bounds={mesh.bounds}");
            }
            Debug.Log(
                $"[FanCardVisualModel] Imported {meshes.Length} meshes from "
                + $"{VisualModelPath}; normals=Import, preserveHierarchy=true.");
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                VisualModelPath);
            GameObject instance = UnityEngine.Object.Instantiate(prefab);
            try
            {
                foreach (Transform item in instance.GetComponentsInChildren<Transform>(
                    true).Where(item =>
                        item.name == instance.name
                        || item.name == "MagneticFanCard_Root"
                        || item.name == "BottomCard"
                        || item.name == "BottomCard_GunmetalFrame"
                        || item.name == "BottomCard_WarmSilverFace"))
                {
                    Debug.Log(
                        $"[FanCardVisualTransform] {item.name}: "
                        + $"localPosition={item.localPosition}; "
                        + $"localRotation={item.localEulerAngles}; "
                        + $"localScale={item.localScale}; "
                        + $"lossyScale={item.lossyScale}");
                }
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance);
            }
        }
    }
}
