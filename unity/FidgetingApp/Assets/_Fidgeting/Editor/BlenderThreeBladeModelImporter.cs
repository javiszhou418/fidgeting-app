using UnityEditor;

namespace ThreeBladeEDC.EditorTools
{
    /// <summary>
    /// Keeps Blender's meter-scale hierarchy intact and prevents render-only
    /// DCC data from entering the mobile player through the FBX importer.
    /// </summary>
    public sealed class BlenderThreeBladeModelImporter : AssetPostprocessor
    {
        public const string ModelFolder =
            "Assets/_Fidgeting/Models/BlenderThreeBlade/";

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
            importer.isReadable = false;
            importer.meshCompression = ModelImporterMeshCompression.Off;
        }

    }
}
