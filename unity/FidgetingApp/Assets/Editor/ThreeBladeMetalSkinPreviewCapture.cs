using System.IO;
using FidgetingApp.Product;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FidgetingApp.Editor
{
    public static class ThreeBladeMetalSkinPreviewCapture
    {
        private const string ScenePath =
            "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity";
        private const int Width = 900;
        private const int Height = 1600;

        [MenuItem("Fidgeting/Product/Capture Three-Blade Metal Skins")]
        public static void CaptureAll()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            GameObject rotor = GameObject.Find("RotorDynamic");
            Camera camera = Camera.main ?? Object.FindAnyObjectByType<Camera>();
            if (rotor == null || camera == null)
            {
                throw new InvalidDataException(
                    "Three-blade metal skin preview prerequisites are missing.");
            }

            ThreeBladeMetalSkinProgression skins =
                rotor.GetComponent<ThreeBladeMetalSkinProgression>()
                ?? rotor.AddComponent<ThreeBladeMetalSkinProgression>();
            string folder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../../../Artifacts/ThreeBladeMetalSkins"));
            Directory.CreateDirectory(folder);

            foreach (ThreeBladeMetalSkinDefinition skin in
                ThreeBladeMetalSkinCatalog.Skins)
            {
                skins.Apply(skin.Level, skin.Id);
                Render(
                    camera,
                    Path.Combine(
                        folder,
                        $"lv{skin.Level:000}-{skin.Id}.png"));
            }

            Debug.Log(
                $"[ThreeBladeMetalSkins] Captured "
                + $"{ThreeBladeMetalSkinCatalog.Skins.Count} previews: {folder}");
        }

        private static void Render(Camera camera, string outputPath)
        {
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            float previousAspect = camera.aspect;
            var target = new RenderTexture(
                Width,
                Height,
                24,
                RenderTextureFormat.ARGB32);
            var image = new Texture2D(
                Width,
                Height,
                TextureFormat.RGBA32,
                false,
                false);
            try
            {
                if (!target.Create())
                {
                    throw new InvalidDataException(
                        "Unity could not create the metal skin preview render target.");
                }
                camera.aspect = (float)Width / Height;
                camera.targetTexture = target;
                var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest
                {
                    destination = target
                };
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                RenderTexture.active = target;
                image.ReadPixels(new Rect(0f, 0f, Width, Height), 0, 0);
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
