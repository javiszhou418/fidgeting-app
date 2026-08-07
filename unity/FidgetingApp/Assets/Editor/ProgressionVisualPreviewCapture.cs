using System.IO;
using FidgetingApp.Product;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace CodexUnityLabEditor
{
    public static class ProgressionVisualPreviewCapture
    {
        private readonly struct PreviewModel
        {
            public PreviewModel(string scenePath, string rotorName, string modelId)
            {
                ScenePath = scenePath;
                RotorName = rotorName;
                ModelId = modelId;
            }

            public string ScenePath { get; }
            public string RotorName { get; }
            public string ModelId { get; }
        }

        private static readonly PreviewModel[] Models =
        {
            new PreviewModel(
                "Assets/Scenes/FidgetSpinnerDemo.unity",
                "FidgetSpinner",
                "blue-classic"),
            new PreviewModel(
                "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity",
                "RotorDynamic",
                "metal-three-blade"),
            new PreviewModel(
                "Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity",
                "RotorDynamic",
                "gold-four-wing"),
            new PreviewModel(
                "Assets/_TwoLobeBar/Scenes/TwoLobeBar.unity",
                "RotorDynamic",
                "graphite-two-lobe")
        };

        private static readonly int[] Levels = { 1, 20, 50, 75, 100 };

        [MenuItem("Tools/Codex/Capture Progression Visual Stages")]
        public static void CaptureAll()
        {
            string folder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../../../Artifacts/ProgressionVisuals"));
            Directory.CreateDirectory(folder);

            for (int modelIndex = 0; modelIndex < Models.Length; modelIndex++)
            {
                PreviewModel model = Models[modelIndex];
                Scene scene = EditorSceneManager.OpenScene(model.ScenePath, OpenSceneMode.Single);
                GameObject rotor = FindGameObject(scene, model.RotorName);
                Camera camera = Camera.main;
                if (rotor == null || camera == null)
                {
                    throw new InvalidDataException(
                        $"Progression preview prerequisites missing: {model.ScenePath}");
                }

                bool usesIntegratedMetalSkins =
                    model.ModelId == ThreeBladeMetalSkinCatalog.ModelId;
                SpinnerProgressionVisuals visuals = null;
                ThreeBladeMetalSkinProgression metalSkins = null;
                if (usesIntegratedMetalSkins)
                {
                    metalSkins = rotor.GetComponent<ThreeBladeMetalSkinProgression>()
                        ?? rotor.AddComponent<ThreeBladeMetalSkinProgression>();
                }
                else
                {
                    visuals = rotor.GetComponent<SpinnerProgressionVisuals>()
                        ?? rotor.AddComponent<SpinnerProgressionVisuals>();
                }

                for (int levelIndex = 0; levelIndex < Levels.Length; levelIndex++)
                {
                    int level = Levels[levelIndex];
                    if (usesIntegratedMetalSkins)
                    {
                        metalSkins.Apply(
                            level,
                            ThreeBladeMetalSkinCatalog.AutomaticSelectionId);
                    }
                    else
                    {
                        visuals.Apply(model.ModelId, level);
                    }
                    string outputPath = Path.Combine(
                        folder,
                        $"{model.ModelId}-lv{level:000}.png");
                    Render(camera, outputPath);
                }
            }

            Debug.Log($"[ProgressionVisuals] Captured {Models.Length * Levels.Length} previews: {folder}");
        }

        private static GameObject FindGameObject(Scene scene, string objectName)
        {
            GameObject[] roots = scene.GetRootGameObjects();
            for (int index = 0; index < roots.Length; index++)
            {
                Transform[] transforms = roots[index].GetComponentsInChildren<Transform>(true);
                for (int transformIndex = 0; transformIndex < transforms.Length; transformIndex++)
                {
                    if (transforms[transformIndex].name == objectName)
                    {
                        return transforms[transformIndex].gameObject;
                    }
                }
            }

            return null;
        }

        private static void Render(Camera camera, string outputPath)
        {
            const int width = 900;
            const int height = 1600;
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            float previousAspect = camera.aspect;
            var target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
            var image = new Texture2D(width, height, TextureFormat.RGBA32, false, false);
            try
            {
                target.Create();
                camera.aspect = (float)width / height;
                camera.targetTexture = target;
                var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest
                {
                    destination = target
                };
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                RenderTexture.active = target;
                image.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                image.Apply(false, false);
                File.WriteAllBytes(outputPath, image.EncodeToPNG());
            }
            finally
            {
                camera.aspect = previousAspect;
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                Object.DestroyImmediate(image);
                target.Release();
                Object.DestroyImmediate(target);
            }
        }
    }
}
