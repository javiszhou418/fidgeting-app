using System.IO;
using CodexUnityLab;
using FidgetingApp.Product;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FidgetingApp.Editor
{
    public static class SpinnerEnvironmentPreviewCapture
    {
        private const int Width = 900;
        private const int Height = 1600;

        [MenuItem("Fidgeting/Product/Capture Environment Integration Previews")]
        public static void CaptureAll()
        {
            string folder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../../../Artifacts/EnvironmentIntegration"));
            Directory.CreateDirectory(folder);

            foreach (SpinnerEnvironmentProfile profile in SpinnerEnvironmentCatalog.Profiles)
            {
                EditorSceneManager.OpenScene(profile.ScenePath, OpenSceneMode.Single);
                Camera camera = Camera.main ?? Object.FindAnyObjectByType<Camera>();
                if (camera == null)
                {
                    throw new InvalidDataException(
                        $"Environment preview camera missing: {profile.ScenePath}");
                }

                float previousAspect = camera.aspect;
                camera.aspect = (float)Width / Height;
                SpinnerEnvironmentPresenter presenter =
                    SpinnerEnvironmentPresenter.Install(profile.ScenePath);
                if (presenter == null || presenter.BackgroundTexture == null)
                {
                    throw new InvalidDataException(
                        $"Environment preview setup failed: {profile.ScenePath}");
                }
                presenter.SetLibraryPreviewActive(true, true);

                // Match the camera pose used by the shipping library screen.
                // Editor batch rendering does not execute the runtime LateUpdate
                // that normally applies these framing components.
                PortraitCameraFramer portraitFramer =
                    camera.GetComponent<PortraitCameraFramer>();
                if (portraitFramer != null)
                {
                    portraitFramer.SetLibraryPreviewActive(true, true);
                    portraitFramer.FrameNow();
                }
                OrbitPresentationCamera orbitCamera =
                    camera.GetComponent<OrbitPresentationCamera>();
                if (orbitCamera != null)
                {
                    orbitCamera.SetLibraryPreviewActive(true, true);
                }
                FidgetingApp.EDC.EdcPortraitCameraFramer edcFramer =
                    camera.GetComponent<FidgetingApp.EDC.EdcPortraitCameraFramer>();
                if (edcFramer != null)
                {
                    edcFramer.SetLibraryPreviewActive(true, true);
                    edcFramer.FrameNow();
                }
                presenter.ImageBasedLighting?.SetViewResponse(
                    Vector2.zero,
                    false,
                    0f,
                    0f,
                    0f);

                string outputPath = Path.Combine(folder, $"{profile.ModelId}-unity.png");
                try
                {
                    Render(camera, outputPath);
                    ApplyPreviewParallax(
                        camera,
                        presenter,
                        new Vector2(0.72f, -0.46f));
                    Render(
                        camera,
                        Path.Combine(folder, $"{profile.ModelId}-parallax-unity.png"));
                }
                finally
                {
                    camera.ResetProjectionMatrix();
                    presenter.SetLayeredParallaxTilt(Vector2.zero, 0f);
                    presenter.ImageBasedLighting?.SetViewResponse(
                        Vector2.zero,
                        false,
                        0f,
                        0f,
                        0f);
                    camera.aspect = previousAspect;
                }
            }

            Debug.Log(
                $"[FidgetingApp] Captured six neutral and six parallax previews: {folder}");
        }

        private static void ApplyPreviewParallax(
            Camera camera,
            SpinnerEnvironmentPresenter presenter,
            Vector2 normalizedTilt)
        {
            camera.projectionMatrix = SpinnerSceneParallaxController.OffsetProjection(
                camera.projectionMatrix,
                camera.orthographic,
                normalizedTilt * SpinnerSceneParallaxController.AnchorLayerPixels,
                new Vector2(Width, Height));
            presenter.RefreshLayout();
            presenter.SetLayeredParallaxTilt(
                normalizedTilt,
                SpinnerSceneParallaxController.AnchorLayerPixels);
            presenter.ImageBasedLighting?.SetViewResponse(
                normalizedTilt,
                false,
                0f,
                0f,
                0f);
        }

        private static void Render(Camera camera, string outputPath)
        {
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
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
                target.Create();
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
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                Object.DestroyImmediate(image);
                target.Release();
                Object.DestroyImmediate(target);
            }
        }
    }
}
