using UnityEditor;

namespace ThreeBladeEDC.EditorTools
{
    /// <summary>
    /// Preserves the meter-scale mechanical hierarchy authored by Blender and
    /// strips DCC-only payloads from the Dragon Scale mobile model assets.
    /// </summary>
    public sealed class BlenderDragonScaleModelImporter : AssetPostprocessor
    {
        public const string ModelFolder =
            "Assets/_Fidgeting/Models/BlenderDragonScale/";

        private void OnPreprocessModel()
        {
            if (!assetPath.StartsWith(ModelFolder))
            {
                return;
            }

            var importer = (ModelImporter)assetImporter;
            importer.globalScale = 1f;
            importer.useFileScale = true;
            importer.preserveHierarchy = true;
            importer.importAnimation = false;
            importer.importBlendShapes = false;
            importer.importCameras = false;
            importer.importLights = false;
            importer.importVisibility = false;
            importer.importNormals = ModelImporterNormals.Import;
            importer.importTangents = ModelImporterTangents.CalculateMikk;
            importer.isReadable = false;
            importer.meshCompression = ModelImporterMeshCompression.Off;
        }
    }
}
