using System;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Candidates.Editor
{
    public static class PackOpeningGate04R013RigProbe
    {
        private const string RigPath =
            "Assets/_DisplayCase/Candidates/PackOpeningGate04R013/Imported/"
            + "PackOpeningGate04R013PackOnlyRig.fbx";

        public static void Validate()
        {
            AssetDatabase.ImportAsset(
                RigPath,
                ImportAssetOptions.ForceSynchronousImport);
            ModelImporter importer = AssetImporter.GetAtPath(RigPath)
                as ModelImporter;
            if (importer == null)
            {
                throw new InvalidOperationException("The Pack-only FBX has no importer.");
            }
            importer.importBlendShapes = true;
            importer.animationType = ModelImporterAnimationType.Generic;
            AssetDatabase.WriteImportSettingsIfDirty(RigPath);
            AssetDatabase.ImportAsset(
                RigPath,
                ImportAssetOptions.ForceSynchronousImport);

            GameObject rig = AssetDatabase.LoadAssetAtPath<GameObject>(RigPath);
            SkinnedMeshRenderer[] renderers = rig == null
                ? Array.Empty<SkinnedMeshRenderer>()
                : rig.GetComponentsInChildren<SkinnedMeshRenderer>(true);
            if (renderers.Length < 8)
            {
                throw new InvalidOperationException(
                    $"Expected Pack-only blend-shape renderers; found {renderers.Length}.");
            }

            string[] expected = { "Tear_015", "Tear_035", "Tear_055", "Tear_075", "Tear_100" };
            Debug.Log(
                $"GATE04_R013_RIG_ROOT rotation={rig.transform.localEulerAngles} "
                + $"scale={rig.transform.localScale}");
            foreach (SkinnedMeshRenderer renderer in renderers)
            {
                if (renderer.sharedMesh == null
                    || renderer.sharedMesh.blendShapeCount != expected.Length
                    || expected.Any(name =>
                        renderer.sharedMesh.GetBlendShapeIndex(name) < 0))
                {
                    throw new InvalidOperationException(
                        $"Invalid blend-shape payload on {renderer.name}.");
                }
                Mesh mesh = renderer.sharedMesh;
                Vector2[] uv = mesh.uv;
                float uvMinY = uv.Length == 0 ? float.NaN : uv.Min(value => value.y);
                float uvMaxY = uv.Length == 0 ? float.NaN : uv.Max(value => value.y);
                Debug.Log(
                    $"GATE04_R013_RIG_MESH name={renderer.name} "
                    + $"bounds={mesh.bounds.size} triangles={mesh.triangles.Length / 3} "
                    + $"uvY={uvMinY:F4}-{uvMaxY:F4} "
                    + $"localRotation={renderer.transform.localEulerAngles}");
            }

            Debug.Log(
                "GATE04_R013_RIG_IMPORT_OK "
                + $"renderers={renderers.Length} "
                + $"vertices={renderers.Sum(item => item.sharedMesh.vertexCount)} "
                + $"blendShapes={renderers.Sum(item => item.sharedMesh.blendShapeCount)}");
        }
    }
}
