using System.IO;
using System.Linq;
using FidgetingApp.EDC.Candidates;
using FidgetingApp.EDC.Runtime;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.Editor
{
    public static class MagneticSlideTileUnityOnlyPlayModeCaptureBuilder
    {
        private const string SourceScene =
            "Assets/_EDC/Candidates/MagneticSlideTileGate08R004NeutralParity/Scenes/MagneticSlideTileNeutralParityR004.unity";
        private const string CaptureScene =
            "Assets/_EDC/Candidates/MagneticSlideTileGate08R004NeutralParity/Scenes/MagneticSlideTileUnityOnlyPlayModePreview.unity";

        [MenuItem("Fidgeting/Model Pipeline/Capture Gate 08 R004 Unity PlayMode")]
        public static void BuildAndRun()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
                throw new System.InvalidOperationException(
                    "Unity is already entering or running PlayMode.");

            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string output = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-004/unity-playmode-preview");
            Directory.CreateDirectory(output);
            foreach (string oldFrame in Directory.GetFiles(output, "frame-*.png"))
                File.Delete(oldFrame);
            string oldReport = Path.Combine(output, "unity-playmode-capture-report.json");
            if (File.Exists(oldReport))
                File.Delete(oldReport);

            Scene scene = EditorSceneManager.OpenScene(SourceScene, OpenSceneMode.Single);
            MagneticSlideTileGate11Metadata metadata = scene
                .GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<MagneticSlideTileGate11Metadata>(true))
                .Single();
            GameObject product = metadata.gameObject;
            MagneticSlideTileGate11PreviewController controller =
                product.GetComponent<MagneticSlideTileGate11PreviewController>();
            Camera camera = scene
                .GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<Camera>(true))
                .Single(item => item.name == "CAM_Gate08R004NeutralParity");
            controller.Configure(
                controller.RotatingCarrier,
                controller.MovingTop,
                controller.TopLocalSlide,
                camera,
                null,
                Vector3.up,
                Vector3.forward);
            controller.ResetPose();
            controller.enabled = false;

            GameObject host = new("UnityOnlyPlayModeCaptureHost");
            MagneticSlideTileUnityOnlyPlayModeCapture capture =
                host.AddComponent<MagneticSlideTileUnityOnlyPlayModeCapture>();
            capture.Configure(camera, product, controller, metadata, output);

            Directory.CreateDirectory(Path.GetDirectoryName(CaptureScene)!);
            EditorSceneManager.SaveScene(scene, CaptureScene, false);
            AssetDatabase.SaveAssets();
            Debug.Log(
                "UNITY_ONLY_PLAYMODE_CAPTURE_READY "
                + $"scene={CaptureScene} output={output}");
            EditorApplication.isPlaying = true;
        }
    }
}
