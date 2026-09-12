using System.IO;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Editor
{
    public static class PremiumDisplayCaseGate12R012RuntimeCapture
    {
        public const string EvidenceRelativeRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/v3-rev-012";

        public static string EvidenceRoot =>
            Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "..",
                EvidenceRelativeRoot));

        [MenuItem(
            "Fidgeting/Display Case/Gate 12/R012 Capture Corrected Runtime")]
        public static void Capture()
        {
            if (Directory.Exists(EvidenceRoot))
            {
                throw new IOException(
                    "R012 already exists. Preserve it and use a new revision.");
            }
            if (Resources.Load<PremiumDisplayCaseGachaLightingProfile>(
                    PremiumDisplayCaseGachaLightingContract.ResourcesPath) == null)
            {
                throw new MissingReferenceException(
                    "The R011 runtime lighting profile is missing.");
            }

            Directory.CreateDirectory(EvidenceRoot);
            Directory.CreateDirectory(Path.Combine(
                EvidenceRoot,
                "runtime-frames"));
            PremiumDisplayCaseGate12R011IntegrationBuilder
                .CaptureRuntimeFrames(EvidenceRoot);
            AssetDatabase.Refresh();
            Debug.Log("Gate 12 R012 corrected runtime capture complete.");
        }
    }
}
