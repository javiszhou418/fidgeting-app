using System;

namespace FidgetingApp.ImportedSpinner.EditorTools
{
    /// <summary>
    /// Compatibility tombstone for the retired Dragon Scale migration tool.
    /// MIRROR QUAD now ships as its true four-wing asset; rebuilding this slot
    /// requires a dedicated four-wing authoring task and may never fall back to
    /// the old three-wing replacement.
    /// </summary>
    public static class ImportedSpinnerSceneBuilder
    {
        public const string ScenePath =
            "Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity";
        public const string RuntimeModelPath =
            "Assets/_ImportedSpinner/Models/ImportedSpinner_Runtime.obj";
        public const bool IsRetiredLegacyBuilder = true;

        public static void BuildPresentation()
        {
            throw RetiredBuilderException();
        }

        public static void BuildAndCapturePreview()
        {
            throw RetiredBuilderException();
        }

        private static NotSupportedException RetiredBuilderException()
        {
            return new NotSupportedException(
                "Retired: do not overwrite the restored four-wing MIRROR QUAD "
                + "shipping scene. A dedicated four-wing builder is required.");
        }
    }
}
