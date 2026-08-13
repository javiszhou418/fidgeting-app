using System;
using System.IO;
using CodexUnityLab;
using FidgetingApp.Product;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.Editor
{
    /// <summary>
    /// Builds the native wallpaper-picker plates from the shipping Unity scenes.
    /// Both themes for a model are rendered from one frozen camera, projection,
    /// model pose and library framing state so changing themes cannot resize the
    /// product in the picker.
    /// </summary>
    public static class EnvironmentWallpaperAssetCapture
    {
        public const string AssetFolder =
            "Assets/Plugins/iOS/SceneWallpapers";
        public const int Width = 900;
        public const int Height = 1600;

        [MenuItem("Fidgeting/Product/Capture Matched Environment Wallpapers")]
        public static void CaptureAll()
        {
            string outputFolder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "Plugins/iOS/SceneWallpapers"));
            Directory.CreateDirectory(outputFolder);

            foreach (SpinnerEnvironmentProfile profile in
                     SpinnerEnvironmentCatalog.Profiles)
            {
                CaptureThemePair(profile, outputFolder);
            }

            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            ConfigureImporters();
            AssetDatabase.SaveAssets();
            Debug.Log(
                "[FidgetingApp] Captured matched canyon/cyberpunk wallpaper "
                + $"pairs for {SpinnerEnvironmentCatalog.Profiles.Count} "
                + $"shipping products: {outputFolder}");
        }

        private static void CaptureThemePair(
            SpinnerEnvironmentProfile profile,
            string outputFolder)
        {
            EditorSceneManager.OpenScene(profile.ScenePath, OpenSceneMode.Single);
            Camera camera = Camera.main ?? UnityEngine.Object.FindAnyObjectByType<Camera>();
            if (camera == null)
            {
                throw new MissingReferenceException(
                    $"Wallpaper camera is missing: {profile.ScenePath}");
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
                    $"Wallpaper environment setup failed: {profile.ScenePath}");
            }

            presenter.SetLibraryPreviewActive(true, true);
            ApplyShippingLibraryFraming(camera);
            presenter.RefreshLayout();
            presenter.ImageBasedLighting?.SetViewResponse(
                Vector2.zero,
                false,
                0f,
                0f,
                0.32f);

            Vector3 matchedPosition = camera.transform.position;
            Quaternion matchedRotation = camera.transform.rotation;
            Matrix4x4 matchedProjection = camera.projectionMatrix;

            var target = new RenderTexture(
                Width,
                Height,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB)
            {
                antiAliasing = 4,
                name = $"EnvironmentWallpaper-{profile.ModelId}"
            };
            var readback = new Texture2D(
                Width,
                Height,
                TextureFormat.RGB24,
                false,
                false);

            try
            {
                target.Create();
                camera.targetTexture = target;
                camera.allowHDR = false;
                camera.allowMSAA = true;

                foreach (SpinnerEnvironmentThemeProfile theme in
                         SpinnerEnvironmentThemeCatalog.Profiles)
                {
                    camera.transform.SetPositionAndRotation(
                        matchedPosition,
                        matchedRotation);
                    camera.projectionMatrix = matchedProjection;

                    if (!presenter.ApplyTheme(theme.Id))
                    {
                        throw new InvalidDataException(
                            $"Wallpaper theme could not be applied: {theme.Id}");
                    }

                    // Theme application may rebuild environment layers, but it
                    // must never become a second source of product framing.
                    camera.transform.SetPositionAndRotation(
                        matchedPosition,
                        matchedRotation);
                    camera.projectionMatrix = matchedProjection;
                    presenter.SetLibraryPreviewActive(true, true);
                    presenter.RefreshLayout();
                    presenter.ImageBasedLighting?.SetViewResponse(
                        Vector2.zero,
                        false,
                        0f,
                        0f,
                        0.32f);

                    Render(camera, target);
                    Render(camera, target);
                    RenderTexture.active = target;
                    readback.ReadPixels(
                        new Rect(0f, 0f, Width, Height),
                        0,
                        0,
                        false);
                    readback.Apply(false, false);

                    string fileName =
                        $"scene-wallpaper-{theme.Id}-{profile.ModelId}.png";
                    File.WriteAllBytes(
                        Path.Combine(outputFolder, fileName),
                        readback.EncodeToPNG());
                }
            }
            finally
            {
                camera.transform.SetPositionAndRotation(
                    matchedPosition,
                    matchedRotation);
                camera.projectionMatrix = matchedProjection;
                camera.aspect = previousAspect;
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                UnityEngine.Object.DestroyImmediate(readback);
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
            }
        }

        private static void ApplyShippingLibraryFraming(Camera camera)
        {
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
                orbitCamera.FrameNow();
            }

            FidgetingApp.EDC.EdcPortraitCameraFramer edcFramer =
                camera.GetComponent<FidgetingApp.EDC.EdcPortraitCameraFramer>();
            if (edcFramer != null)
            {
                edcFramer.SetLibraryPreviewActive(true, true);
                edcFramer.FrameNow();
            }
        }

        private static void ConfigureImporters()
        {
            foreach (SpinnerEnvironmentProfile profile in
                     SpinnerEnvironmentCatalog.Profiles)
            {
                foreach (SpinnerEnvironmentThemeProfile theme in
                         SpinnerEnvironmentThemeCatalog.Profiles)
                {
                    string path =
                        $"{AssetFolder}/scene-wallpaper-{theme.Id}-{profile.ModelId}.png";
                    TextureImporter importer =
                        AssetImporter.GetAtPath(path) as TextureImporter;
                    if (importer == null)
                    {
                        throw new InvalidDataException(
                            $"Wallpaper importer is missing: {path}");
                    }

                    importer.textureType = TextureImporterType.Default;
                    importer.sRGBTexture = true;
                    importer.alphaSource = TextureImporterAlphaSource.None;
                    importer.mipmapEnabled = false;
                    importer.wrapMode = TextureWrapMode.Clamp;
                    importer.filterMode = FilterMode.Bilinear;
                    importer.npotScale = TextureImporterNPOTScale.None;
                    importer.maxTextureSize = 2048;
                    importer.textureCompression = TextureImporterCompression.Uncompressed;
                    importer.SaveAndReimport();
                }
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
