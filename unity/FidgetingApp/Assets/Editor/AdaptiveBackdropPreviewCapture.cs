using System.IO;
using FidgetingApp.Product;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FidgetingApp.Editor
{
    /// <summary>
    /// Captures shipping-scene checkpoints for the model-reactive background.
    /// The first five frames keep the metal scene loaded while its page and
    /// hue field travel left; the final frame proves the incoming gold hue is
    /// continuous once the next shipping scene becomes current.
    /// </summary>
    public static class AdaptiveBackdropPreviewCapture
    {
        private const int Width = 450;
        private const int Height = 800;
        private const string MetalScene = SpinnerEnvironmentCatalog.MetalScenePath;
        private const string GoldScene = SpinnerEnvironmentCatalog.ImportedScenePath;

        [MenuItem("Fidgeting/Product/Capture Adaptive Backdrop Transition")]
        public static void Capture()
        {
            string outputFolder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../Artifacts/AdaptiveBackdropPreview/Transition"));
            Directory.CreateDirectory(outputFolder);

            Color[][] frames =
            {
                CaptureFrame(MetalScene, 0f, false, "01-metal-stable.png", outputFolder),
                CaptureFrame(MetalScene, -0.25f, false, "02-drag-25.png", outputFolder),
                CaptureFrame(MetalScene, -0.50f, false, "03-drag-50.png", outputFolder),
                CaptureFrame(MetalScene, -0.75f, false, "04-drag-75.png", outputFolder),
                CaptureFrame(MetalScene, -1f, false, "05-gold-hue-arrived.png", outputFolder),
                CaptureFrame(GoldScene, 0.35f, true, "06-gold-enters-with-stable-hue.png", outputFolder)
            };

            var sheet = new Texture2D(
                Width * 3,
                Height * 2,
                TextureFormat.RGB24,
                false,
                false);
            for (int index = 0; index < frames.Length; index++)
            {
                int column = index % 3;
                int row = index < 3 ? 1 : 0;
                sheet.SetPixels(
                    column * Width,
                    row * Height,
                    Width,
                    Height,
                    frames[index]);
            }
            sheet.Apply(false, false);
            File.WriteAllBytes(
                Path.Combine(outputFolder, "adaptive-transition-contact-sheet.png"),
                sheet.EncodeToPNG());
            Object.DestroyImmediate(sheet);
            Debug.Log(
                "[FidgetingApp] Captured adaptive backdrop transition: "
                + outputFolder);
        }

        private static Color[] CaptureFrame(
            string scenePath,
            float pageOffset,
            bool entrance,
            string fileName,
            string outputFolder)
        {
            EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
            Camera camera = Camera.main ?? Object.FindAnyObjectByType<Camera>();
            if (camera == null)
            {
                throw new MissingReferenceException(
                    "Shipping preview camera is missing: " + scenePath);
            }

            float previousAspect = camera.aspect;
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            var target = new RenderTexture(
                Width,
                Height,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB)
            {
                antiAliasing = 4,
                name = "AdaptiveBackdropTransitionPreview"
            };
            var readback = new Texture2D(
                Width,
                Height,
                TextureFormat.RGB24,
                false,
                false);

            try
            {
                camera.aspect = (float)Width / Height;
                if (!target.Create())
                {
                    throw new InvalidDataException(
                        "Adaptive preview needs a graphics device; "
                        + "do not run this visual gate with -nographics.");
                }
                camera.targetTexture = target;
                camera.allowHDR = false;
                camera.allowMSAA = true;

                SpinnerEnvironmentPresenter presenter =
                    SpinnerEnvironmentPresenter.Install(scenePath);
                presenter.ApplyTheme(SpinnerEnvironmentThemeCatalog.AdaptiveId);
                presenter.SetLibraryPreviewActive(true, true);
                presenter.RefreshLayout();
                presenter.ParallaxController?.SetLibraryPageOffsetForPreview(
                    pageOffset,
                    entrance);

                OrbitPresentationCamera orbitCamera =
                    camera.GetComponent<OrbitPresentationCamera>();
                if (orbitCamera != null)
                {
                    orbitCamera.SetLibraryPreviewActive(true, true);
                    orbitCamera.FrameNow();
                }
                presenter.ImageBasedLighting?.SetViewResponse(
                    Vector2.zero,
                    false,
                    0f,
                    0f,
                    0f);

                Render(camera, target);
                Render(camera, target);
                RenderTexture.active = target;
                readback.ReadPixels(
                    new Rect(0f, 0f, Width, Height),
                    0,
                    0,
                    false);
                readback.Apply(false, false);
                File.WriteAllBytes(
                    Path.Combine(outputFolder, fileName),
                    readback.EncodeToPNG());
                return readback.GetPixels();
            }
            finally
            {
                camera.aspect = previousAspect;
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                Object.DestroyImmediate(readback);
                target.Release();
                Object.DestroyImmediate(target);
            }
        }

        private static void Render(Camera camera, RenderTexture target)
        {
            var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest
            {
                destination = target
            };
            UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
        }
    }
}
