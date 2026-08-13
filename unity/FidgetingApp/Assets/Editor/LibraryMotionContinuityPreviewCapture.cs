using System.IO;
using FidgetingApp.Product;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FidgetingApp.Editor
{
    /// <summary>
    /// Captures the actual shipping scenes at deterministic model-page and
    /// device-motion checkpoints. Row one proves a left swipe moves the old
    /// model left and brings the next model in from the right. Row two crosses the 90-degree
    /// top-view pole and must retain one continuous screen-up orientation.
    /// </summary>
    public static class LibraryMotionContinuityPreviewCapture
    {
        private const int Width = 450;
        private const int Height = 800;
        private const string PointedScene =
            "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity";
        private const string MetalScene =
            "Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity";

        [MenuItem("Fidgeting/Product/Capture Library Motion Continuity")]
        public static void Capture()
        {
            string outputFolder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../Artifacts/LibraryMotionContinuityPreview"));
            Directory.CreateDirectory(outputFolder);

            Color[] pointedCenter = CaptureFrame(
                PointedScene,
                0f,
                Vector2.zero,
                "01-pointed-center.png",
                outputFolder);
            Color[] pointedExit = CaptureFrame(
                PointedScene,
                -0.32f,
                Vector2.zero,
                "02-pointed-exit-left.png",
                outputFolder);
            Color[] metalEntrance = CaptureFrame(
                MetalScene,
                0.32f,
                Vector2.zero,
                "03-metal-enter-right.png",
                outputFolder);
            Color[] metalCenter = CaptureFrame(
                MetalScene,
                0f,
                Vector2.zero,
                "04-metal-center.png",
                outputFolder);
            Color[] beforePole = CaptureFrame(
                MetalScene,
                0f,
                new Vector2(0f, -0.12f),
                "05-gyro-before-pole.png",
                outputFolder);
            Color[] afterPole = CaptureFrame(
                MetalScene,
                0f,
                new Vector2(0f, -0.18f),
                "06-gyro-after-pole.png",
                outputFolder);

            var contactSheet = new Texture2D(
                Width * 4,
                Height * 2,
                TextureFormat.RGB24,
                false,
                false);
            Color[] black = new Color[Width * Height];
            for (int index = 0; index < black.Length; index++)
            {
                black[index] = Color.black;
            }
            for (int column = 0; column < 4; column++)
            {
                contactSheet.SetPixels(column * Width, 0, Width, Height, black);
                contactSheet.SetPixels(column * Width, Height, Width, Height, black);
            }
            contactSheet.SetPixels(0, Height, Width, Height, pointedCenter);
            contactSheet.SetPixels(Width, Height, Width, Height, pointedExit);
            contactSheet.SetPixels(Width * 2, Height, Width, Height, metalEntrance);
            contactSheet.SetPixels(Width * 3, Height, Width, Height, metalCenter);
            contactSheet.SetPixels(Width, 0, Width, Height, beforePole);
            contactSheet.SetPixels(Width * 2, 0, Width, Height, afterPole);
            contactSheet.Apply(false, false);
            File.WriteAllBytes(
                Path.Combine(outputFolder, "library-motion-contact-sheet.png"),
                contactSheet.EncodeToPNG());
            Object.DestroyImmediate(contactSheet);
            AssetDatabase.Refresh();
            Debug.Log(
                "[FidgetingApp] Captured Library motion continuity: "
                + outputFolder);
        }

        private static Color[] CaptureFrame(
            string scenePath,
            float pageOffset,
            Vector2 motionTilt,
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
                name = "LibraryMotionContinuityPreview"
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
                        "Library motion preview needs a graphics device; "
                        + "do not run this visual gate with -nographics.");
                }
                camera.targetTexture = target;
                camera.allowHDR = false;
                camera.allowMSAA = true;

                SpinnerEnvironmentPresenter presenter =
                    SpinnerEnvironmentPresenter.Install(scenePath);
                presenter.ApplyTheme(SpinnerEnvironmentThemeCatalog.CanyonId);
                presenter.SetLibraryPreviewActive(true, true);
                presenter.RefreshLayout();
                presenter.ParallaxController?.SetLibraryPageOffsetForPreview(
                    pageOffset);

                OrbitPresentationCamera orbitCamera =
                    camera.GetComponent<OrbitPresentationCamera>();
                if (orbitCamera != null)
                {
                    orbitCamera.SetLibraryPreviewActive(true, true);
                    orbitCamera.SetMotionTilt(motionTilt, 6.5f);
                    orbitCamera.FrameNow();
                }

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
