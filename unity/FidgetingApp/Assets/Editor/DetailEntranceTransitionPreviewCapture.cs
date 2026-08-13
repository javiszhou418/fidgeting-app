using System;
using System.IO;
using System.Linq;
using CodexUnityLab;
using FidgetingApp.Product;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FidgetingApp.Editor
{
    /// <summary>
    /// Captures deterministic checkpoints from the same presentation timeline
    /// used by the shipping library-to-detail transition. The two rows prove
    /// that the camera push and foreground retreat work for both environments.
    /// </summary>
    public static class DetailEntranceTransitionPreviewCapture
    {
        private const string ModelId = "pointed-three-blade";
        private const int Width = 450;
        private const int Height = 800;

        private static readonly float[] ProgressCheckpoints =
        {
            0f,
            0.33f,
            0.67f,
            1f
        };

        [MenuItem("Fidgeting/Product/Capture Detail Entrance Transition Preview")]
        public static void Capture()
        {
            SpinnerEnvironmentProfile profile =
                SpinnerEnvironmentCatalog.Profiles.First(candidate =>
                    string.Equals(
                        candidate.ModelId,
                        ModelId,
                        StringComparison.Ordinal));
            EditorSceneManager.OpenScene(profile.ScenePath, OpenSceneMode.Single);

            Camera camera = Camera.main
                ?? UnityEngine.Object.FindAnyObjectByType<Camera>();
            if (camera == null)
            {
                throw new MissingReferenceException(
                    $"Detail entrance preview camera is missing: {profile.ScenePath}");
            }

            float previousAspect = camera.aspect;
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            camera.aspect = (float)Width / Height;

            SpinnerEnvironmentPresenter presenter =
                SpinnerEnvironmentPresenter.Install(profile.ScenePath);
            if (presenter == null || presenter.BackgroundRenderer == null)
            {
                throw new InvalidDataException(
                    $"Detail entrance environment setup failed: {profile.ScenePath}");
            }

            PortraitCameraFramer portraitFramer =
                camera.GetComponent<PortraitCameraFramer>();
            OrbitPresentationCamera orbitCamera =
                camera.GetComponent<OrbitPresentationCamera>();
            FidgetingApp.EDC.EdcPortraitCameraFramer edcFramer =
                camera.GetComponent<FidgetingApp.EDC.EdcPortraitCameraFramer>();

            string outputFolder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../Artifacts/DetailEntranceTransition"));
            Directory.CreateDirectory(outputFolder);

            var target = new RenderTexture(
                Width,
                Height,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB)
            {
                antiAliasing = 4,
                name = "DetailEntranceTransitionPreview"
            };
            var readback = new Texture2D(
                Width,
                Height,
                TextureFormat.RGB24,
                false,
                false);
            var contactSheet = new Texture2D(
                Width * ProgressCheckpoints.Length,
                Height * 2,
                TextureFormat.RGB24,
                false,
                false);

            try
            {
                target.Create();
                camera.targetTexture = target;
                camera.allowHDR = false;
                camera.allowMSAA = true;

                string[] themes =
                {
                    SpinnerEnvironmentThemeCatalog.CanyonId,
                    SpinnerEnvironmentThemeCatalog.CyberpunkId
                };
                for (int themeIndex = 0; themeIndex < themes.Length; themeIndex++)
                {
                    string themeId = themes[themeIndex];
                    if (!presenter.ApplyTheme(themeId))
                    {
                        throw new InvalidDataException(
                            $"Detail entrance theme could not be applied: {themeId}");
                    }

                    presenter.SetLibraryPreviewActive(true, true);
                    presenter.RefreshLayout();
                    for (int progressIndex = 0;
                         progressIndex < ProgressCheckpoints.Length;
                         progressIndex++)
                    {
                        float progress = ProgressCheckpoints[progressIndex];
                        ApplyProgress(
                            progress,
                            presenter,
                            portraitFramer,
                            orbitCamera,
                            edcFramer);
                        Render(camera, target);
                        Render(camera, target);
                        RenderTexture.active = target;
                        readback.ReadPixels(
                            new Rect(0f, 0f, Width, Height),
                            0,
                            0,
                            false);
                        readback.Apply(false, false);

                        string checkpoint = Mathf.RoundToInt(progress * 100f)
                            .ToString("D3");
                        File.WriteAllBytes(
                            Path.Combine(
                                outputFolder,
                                $"{themeId}-{checkpoint}.png"),
                            readback.EncodeToPNG());

                        int contactY = themeIndex == 0 ? Height : 0;
                        contactSheet.SetPixels(
                            progressIndex * Width,
                            contactY,
                            Width,
                            Height,
                            readback.GetPixels());
                    }
                }

                contactSheet.Apply(false, false);
                File.WriteAllBytes(
                    Path.Combine(outputFolder, "detail-entrance-contact-sheet.png"),
                    contactSheet.EncodeToPNG());
            }
            finally
            {
                camera.aspect = previousAspect;
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                UnityEngine.Object.DestroyImmediate(contactSheet);
                UnityEngine.Object.DestroyImmediate(readback);
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
            }

            AssetDatabase.Refresh();
            Debug.Log(
                "[FidgetingApp] Captured canyon/cyberpunk detail entrance "
                + $"checkpoints: {outputFolder}");
        }

        private static void ApplyProgress(
            float progress,
            SpinnerEnvironmentPresenter presenter,
            PortraitCameraFramer portraitFramer,
            OrbitPresentationCamera orbitCamera,
            FidgetingApp.EDC.EdcPortraitCameraFramer edcFramer)
        {
            presenter.SetLibraryPreviewActive(false, false);
            presenter.RefreshLayout();
            presenter.SetDetailEntranceProgressForPreview(progress);
            presenter.ImageBasedLighting?.SetViewResponse(
                Vector2.zero,
                false,
                0f,
                0f,
                0.32f);

            if (portraitFramer != null)
            {
                portraitFramer.SetDetailEntranceProgressForPreview(progress);
                portraitFramer.FrameNow();
            }
            if (orbitCamera != null)
            {
                orbitCamera.SetDetailEntranceProgressForPreview(progress);
                orbitCamera.FrameNow();
            }
            if (edcFramer != null)
            {
                edcFramer.SetDetailEntranceProgressForPreview(progress);
                edcFramer.FrameNow();
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
