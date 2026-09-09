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
                    presenter.SetLibraryPreviewActive(false, true);
                    presenter.ImageBasedLighting?.SetViewResponse(
                        Vector2.zero,
                        false,
                        0f,
                        0f,
                        0f);
                    Render(
                        camera,
                        Path.Combine(folder, $"{profile.ModelId}-detail-unity.png"));
                    ApplyPreviewParallax(
                        camera,
                        presenter,
                        new Vector2(0.72f, -0.46f));
                    Render(
                        camera,
                        Path.Combine(
                            folder,
                            $"{profile.ModelId}-detail-parallax-unity.png"));
                }
                finally
                {
                    camera.ResetProjectionMatrix();
                    presenter.SetLayeredParallaxTilt(Vector2.zero, 0f);
                    presenter.SetLibraryPreviewActive(true, true);
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
                "[FidgetingApp] Captured library, parallax, detail, and detail-parallax previews: "
                + folder);
        }

        [MenuItem("Fidgeting/Product/Capture Fan Card App Scene Lighting")]
        public static void CaptureFanCardAppScene()
        {
            SpinnerEnvironmentProfile profile = default;
            bool found = false;
            foreach (SpinnerEnvironmentProfile candidate in SpinnerEnvironmentCatalog.Profiles)
            {
                if (string.Equals(
                        candidate.ModelId,
                        ProductCatalog.MagneticFanCardModelId,
                        System.StringComparison.Ordinal))
                {
                    profile = candidate;
                    found = true;
                    break;
                }
            }
            if (!found)
            {
                throw new InvalidDataException("Fan card environment profile missing.");
            }

            string folder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../../../Artifacts/EnvironmentIntegration"));
            Directory.CreateDirectory(folder);
            EditorSceneManager.OpenScene(profile.ScenePath, OpenSceneMode.Single);
            Camera camera = Camera.main ?? Object.FindAnyObjectByType<Camera>();
            float previousAspect = camera.aspect;
            camera.aspect = (float)Width / Height;
            SpinnerEnvironmentPresenter presenter =
                SpinnerEnvironmentPresenter.Install(profile.ScenePath);
            FidgetingApp.EDC.EdcPortraitCameraFramer edcFramer =
                camera.GetComponent<FidgetingApp.EDC.EdcPortraitCameraFramer>();
            try
            {
                CaptureFanCardTheme(
                    camera,
                    presenter,
                    edcFramer,
                    SpinnerEnvironmentThemeCatalog.CanyonId,
                    folder);
                CaptureFanCardTheme(
                    camera,
                    presenter,
                    edcFramer,
                    SpinnerEnvironmentThemeCatalog.CyberpunkId,
                    folder);
            }
            finally
            {
                camera.ResetProjectionMatrix();
                presenter.SetLayeredParallaxTilt(Vector2.zero, 0f);
                presenter.SetLibraryPreviewActive(true, true);
                presenter.ImageBasedLighting?.SetViewResponse(
                    Vector2.zero,
                    false,
                    0f,
                    0f,
                    0f);
                camera.aspect = previousAspect;
            }

            ComposeFanCardShippingSceneSheet(folder);
            Debug.Log("[FidgetingApp] Captured fan card canyon/cyberpunk app scenes: " + folder);
        }

        [MenuItem("Fidgeting/Product/Capture Fan Card Canyon Lighting Audit")]
        public static void CaptureFanCardCanyonLightingAudit()
        {
            SpinnerEnvironmentProfile profile = default;
            bool found = false;
            foreach (SpinnerEnvironmentProfile candidate in SpinnerEnvironmentCatalog.Profiles)
            {
                if (string.Equals(
                        candidate.ModelId,
                        ProductCatalog.MagneticFanCardModelId,
                        System.StringComparison.Ordinal))
                {
                    profile = candidate;
                    found = true;
                    break;
                }
            }
            if (!found)
            {
                throw new InvalidDataException("Fan card environment profile missing.");
            }

            string folder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../../../Artifacts/EnvironmentIntegration"));
            Directory.CreateDirectory(folder);
            string prefix = Path.Combine(
                folder,
                "magnetic-fan-card-canyon-toplight-audit-r008");
            EditorSceneManager.OpenScene(profile.ScenePath, OpenSceneMode.Single);
            Camera camera = Camera.main ?? Object.FindAnyObjectByType<Camera>();
            float previousAspect = camera.aspect;
            camera.aspect = (float)Width / Height;
            SpinnerEnvironmentPresenter presenter =
                SpinnerEnvironmentPresenter.Install(profile.ScenePath);
            FidgetingApp.EDC.EdcPortraitCameraFramer edcFramer =
                camera.GetComponent<FidgetingApp.EDC.EdcPortraitCameraFramer>();
            try
            {
                CaptureFanCardTheme(
                    camera,
                    presenter,
                    edcFramer,
                    SpinnerEnvironmentThemeCatalog.CanyonId,
                    folder,
                    prefix);
            }
            finally
            {
                camera.ResetProjectionMatrix();
                presenter.SetLayeredParallaxTilt(Vector2.zero, 0f);
                presenter.SetLibraryPreviewActive(true, true);
                presenter.ImageBasedLighting?.SetViewResponse(
                    Vector2.zero,
                    false,
                    0f,
                    0f,
                    0f);
                camera.aspect = previousAspect;
            }

            ComposeFanCardCanyonLightingAuditSheet(prefix);
            Debug.Log(
                "[FidgetingApp] Captured fan card Canyon top-light audit: "
                + prefix);
        }

        [MenuItem("Fidgeting/Product/Capture Fan Card Canyon Light Isolation")]
        public static void CaptureFanCardCanyonLightIsolation()
        {
            SpinnerEnvironmentProfile profile = ResolveFanCardProfile();
            string folder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../../../Artifacts/EnvironmentIntegration"));
            Directory.CreateDirectory(folder);
            const string prefixName =
                "magnetic-fan-card-canyon-toplight-audit-r001";
            string prefix = Path.Combine(folder, prefixName);
            EditorSceneManager.OpenScene(profile.ScenePath, OpenSceneMode.Single);
            Camera camera = Camera.main ?? Object.FindAnyObjectByType<Camera>();
            float previousAspect = camera.aspect;
            camera.aspect = (float)Width / Height;
            SpinnerEnvironmentPresenter presenter =
                SpinnerEnvironmentPresenter.Install(profile.ScenePath);
            FidgetingApp.EDC.EdcPortraitCameraFramer framer =
                camera.GetComponent<FidgetingApp.EDC.EdcPortraitCameraFramer>();
            if (!presenter.ApplyTheme(SpinnerEnvironmentThemeCatalog.CanyonId))
            {
                throw new InvalidDataException("Fan card Canyon theme failed.");
            }

            Light topKey = FindLight(
                SpinnerEnvironmentCatalog.FanCardTopKeyName);
            if (topKey == null)
            {
                throw new InvalidDataException("Fan card top key is missing.");
            }

            bool keyWasEnabled = topKey.enabled;
            float reflectionIntensity = RenderSettings.reflectionIntensity;
            try
            {
                presenter.SetLibraryPreviewActive(false, true);
                framer.SetLibraryPreviewActive(false, true);
                framer.FrameNow();
                presenter.RefreshLayout();
                presenter.ImageBasedLighting?.SetViewResponse(
                    Vector2.zero,
                    false,
                    0f,
                    0f,
                    0f);

                topKey.enabled = false;
                Render(camera, prefix + "-detail-key-off.png", true);

                topKey.enabled = keyWasEnabled;
                RenderSettings.reflectionIntensity = 0f;
                Render(camera, prefix + "-detail-reflection-off.png", true);

                topKey.enabled = false;
                Render(camera, prefix + "-detail-key-reflection-off.png", true);

                topKey.enabled = keyWasEnabled;
                RenderSettings.reflectionIntensity = reflectionIntensity;
                Light rockBounce = FindLight(
                    SpinnerEnvironmentCatalog.FanCardRockBounceName);
                bool bounceWasEnabled = rockBounce != null && rockBounce.enabled;
                if (rockBounce != null)
                {
                    rockBounce.enabled = false;
                }
                Render(camera, prefix + "-detail-rock-bounce-off.png", true);
                if (rockBounce != null)
                {
                    rockBounce.enabled = bounceWasEnabled;
                }

                Light modelBounce = presenter.ImageBasedLighting?.ModelBounceLight;
                bool modelBounceWasEnabled =
                    modelBounce != null && modelBounce.enabled;
                if (modelBounce != null)
                {
                    modelBounce.enabled = false;
                }
                Render(camera, prefix + "-detail-model-bounce-off.png", true);
                if (modelBounce != null)
                {
                    modelBounce.enabled = modelBounceWasEnabled;
                }

                Light[] lights = Object.FindObjectsByType<Light>(
                    FindObjectsInactive.Include);
                var lightStates = new bool[lights.Length];
                for (int index = 0; index < lights.Length; index++)
                {
                    Debug.Log(
                        "[FidgetingApp] Fan light isolation: "
                        + $"name={lights[index].name}; "
                        + $"type={lights[index].type}; "
                        + $"enabled={lights[index].enabled}; "
                        + $"intensity={lights[index].intensity:F4}; "
                        + $"forward={lights[index].transform.forward}.");
                    lightStates[index] = lights[index].enabled;
                    lights[index].enabled = false;
                }
                Render(camera, prefix + "-detail-all-lights-off.png", true);
                Render(camera, prefix + "-detail-reflection-only.png", true);
                RenderSettings.reflectionIntensity = 4f;
                Render(
                    camera,
                    prefix + "-detail-reflection-amplified.png",
                    true);

                RenderSettings.reflectionIntensity = 0f;
                topKey.enabled = true;
                Render(camera, prefix + "-detail-top-key-only.png", true);
                float topKeyIntensity = topKey.intensity;
                topKey.intensity = 4f;
                Render(camera, prefix + "-detail-top-key-amplified.png", true);
                topKey.intensity = topKeyIntensity;
                topKey.enabled = false;

                if (rockBounce != null)
                {
                    rockBounce.enabled = true;
                    Render(camera, prefix + "-detail-rock-bounce-only.png", true);
                    rockBounce.enabled = false;
                }

                Light skyFill = FindLight(
                    SpinnerEnvironmentCatalog.FanCardSkyFillName);
                if (skyFill != null)
                {
                    float skyFillIntensity = skyFill.intensity;
                    skyFill.enabled = true;
                    Render(camera, prefix + "-detail-sky-fill-only.png", true);
                    skyFill.intensity = 4f;
                    Render(camera, prefix + "-detail-sky-fill-amplified.png", true);
                    skyFill.intensity = skyFillIntensity;
                    skyFill.enabled = false;
                }

                Light apertureTop = FindLight(
                    SpinnerEnvironmentCatalog.FanCardApertureTopLightName);
                if (apertureTop != null)
                {
                    float apertureIntensity = apertureTop.intensity;
                    apertureTop.enabled = true;
                    apertureTop.intensity = 0.04f;
                    Render(
                        camera,
                        prefix + "-detail-aperture-004.png",
                        true);
                    apertureTop.intensity = 0.08f;
                    Render(
                        camera,
                        prefix + "-detail-aperture-008.png",
                        true);
                    apertureTop.intensity = 0.12f;
                    Render(
                        camera,
                        prefix + "-detail-aperture-012.png",
                        true);
                    apertureTop.intensity = apertureIntensity;
                    apertureTop.enabled = false;
                }

                if (modelBounce != null)
                {
                    modelBounce.enabled = true;
                    Render(camera, prefix + "-detail-model-bounce-only.png", true);
                    modelBounce.enabled = false;
                }

                RenderSettings.reflectionIntensity = reflectionIntensity;
                for (int index = 0; index < lights.Length; index++)
                {
                    lights[index].enabled = lightStates[index];
                }

                MeshRenderer[] environmentLayers =
                {
                    presenter.BackgroundRenderer,
                    presenter.MidgroundRenderer,
                    presenter.LeftForegroundRenderer,
                    presenter.RightForegroundRenderer
                };
                var environmentStates = new bool[environmentLayers.Length];
                for (int index = 0; index < environmentLayers.Length; index++)
                {
                    if (environmentLayers[index] == null)
                    {
                        continue;
                    }
                    environmentStates[index] = environmentLayers[index].enabled;
                    environmentLayers[index].enabled = false;
                }
                Render(camera, prefix + "-detail-environment-off.png", true);
                for (int index = 0; index < environmentLayers.Length; index++)
                {
                    if (environmentLayers[index] != null)
                    {
                        environmentLayers[index].enabled = environmentStates[index];
                    }
                }
            }
            finally
            {
                topKey.enabled = keyWasEnabled;
                RenderSettings.reflectionIntensity = reflectionIntensity;
                camera.ResetProjectionMatrix();
                presenter.SetLayeredParallaxTilt(Vector2.zero, 0f);
                presenter.SetLibraryPreviewActive(true, true);
                presenter.ImageBasedLighting?.SetViewResponse(
                    Vector2.zero,
                    false,
                    0f,
                    0f,
                    0f);
                camera.aspect = previousAspect;
            }
        }

        private static void ComposeFanCardShippingSceneSheet(string folder)
        {
            string[] paths =
            {
                Path.Combine(folder, "magnetic-fan-card-canyon-library.png"),
                Path.Combine(folder, "magnetic-fan-card-canyon-library-ibl-left.png"),
                Path.Combine(folder, "magnetic-fan-card-canyon-library-ibl-right.png"),
                Path.Combine(folder, "magnetic-fan-card-canyon-detail.png"),
                Path.Combine(folder, "magnetic-fan-card-canyon-detail-ibl-left.png"),
                Path.Combine(folder, "magnetic-fan-card-cyberpunk-library.png"),
                Path.Combine(folder, "magnetic-fan-card-cyberpunk-detail.png")
            };
            ComposeFanCardSceneSheet(
                Path.Combine(folder, "magnetic-fan-card-shipping-scene-sheet.png"),
                paths);
        }

        private static void ComposeFanCardCanyonLightingAuditSheet(string prefix)
        {
            ComposeFanCardSceneSheet(
                prefix + "-sheet.png",
                new[]
                {
                    prefix + "-library.png",
                    prefix + "-library-ibl-left.png",
                    prefix + "-library-ibl-right.png",
                    prefix + "-detail.png",
                    prefix + "-detail-ibl-left.png"
                });
        }

        private static void ComposeFanCardSceneSheet(
            string outputPath,
            string[] paths)
        {
            const int cellWidth = 360;
            const int cellHeight = 640;
            const int gutter = 12;
            const int columns = 4;
            int rows = 2;
            var sheet = new Texture2D(
                columns * cellWidth + (columns + 1) * gutter,
                rows * cellHeight + (rows + 1) * gutter,
                TextureFormat.RGB24,
                false);
            Color[] clear = new Color[sheet.width * sheet.height];
            for (int index = 0; index < clear.Length; index++)
            {
                clear[index] = new Color(0.06f, 0.06f, 0.07f, 1f);
            }
            sheet.SetPixels(clear);
            for (int index = 0; index < paths.Length; index++)
            {
                if (!File.Exists(paths[index]))
                {
                    continue;
                }

                byte[] bytes = File.ReadAllBytes(paths[index]);
                var source = new Texture2D(2, 2, TextureFormat.RGBA32, false);
                source.LoadImage(bytes, false);
                int column = index % columns;
                int row = index / columns;
                int destX = gutter + column * (cellWidth + gutter);
                int destY = sheet.height - gutter - (row + 1) * cellHeight - row * gutter;
                Color[] scaled = ScalePixels(source, cellWidth, cellHeight);
                sheet.SetPixels(destX, destY, cellWidth, cellHeight, scaled);
                Object.DestroyImmediate(source);
            }

            File.WriteAllBytes(
                outputPath,
                sheet.EncodeToPNG());
            Object.DestroyImmediate(sheet);
        }

        private static Color[] ScalePixels(Texture2D source, int width, int height)
        {
            var scaled = new Color[width * height];
            for (int y = 0; y < height; y++)
            {
                float v = (y + 0.5f) / height;
                for (int x = 0; x < width; x++)
                {
                    float u = (x + 0.5f) / width;
                    scaled[y * width + x] = source.GetPixelBilinear(u, v);
                }
            }

            return scaled;
        }

        private static SpinnerEnvironmentProfile ResolveFanCardProfile()
        {
            foreach (SpinnerEnvironmentProfile candidate in SpinnerEnvironmentCatalog.Profiles)
            {
                if (string.Equals(
                        candidate.ModelId,
                        ProductCatalog.MagneticFanCardModelId,
                        System.StringComparison.Ordinal))
                {
                    return candidate;
                }
            }

            throw new InvalidDataException("Fan card environment profile missing.");
        }

        private static Light FindLight(string objectName)
        {
            foreach (Light light in Object.FindObjectsByType<Light>(
                FindObjectsInactive.Include))
            {
                if (string.Equals(
                        light.name,
                        objectName,
                        System.StringComparison.Ordinal))
                {
                    return light;
                }
            }

            return null;
        }

        private static void CaptureFanCardTheme(
            Camera camera,
            SpinnerEnvironmentPresenter presenter,
            FidgetingApp.EDC.EdcPortraitCameraFramer edcFramer,
            string themeId,
            string folder,
            string outputPrefix = null)
        {
            if (!presenter.ApplyTheme(themeId))
            {
                throw new InvalidDataException("Fan card theme failed: " + themeId);
            }

            string prefix = string.IsNullOrEmpty(outputPrefix)
                ? Path.Combine(folder, "magnetic-fan-card-" + themeId)
                : outputPrefix;
            presenter.SetLibraryPreviewActive(true, true);
            edcFramer.SetLibraryPreviewActive(true, true);
            edcFramer.FrameNow();
            presenter.RefreshLayout();
            presenter.ImageBasedLighting?.SetViewResponse(
                Vector2.zero,
                false,
                0f,
                0f,
                0f);
            Render(camera, prefix + "-library.png", true);
            presenter.ImageBasedLighting?.SetViewResponse(
                new Vector2(0.85f, 0.12f),
                false,
                0f,
                0f,
                0f);
            presenter.RefreshLayout();
            Render(camera, prefix + "-library-ibl-left.png", true);
            presenter.ImageBasedLighting?.SetViewResponse(
                new Vector2(-0.85f, -0.12f),
                false,
                0f,
                0f,
                0f);
            presenter.RefreshLayout();
            Render(camera, prefix + "-library-ibl-right.png", true);
            presenter.ImageBasedLighting?.SetViewResponse(
                Vector2.zero,
                false,
                0f,
                0f,
                0f);
            camera.ResetProjectionMatrix();
            camera.aspect = (float)Width / Height;
            presenter.SetLayeredParallaxTilt(Vector2.zero, 0f);
            presenter.SetLibraryPreviewActive(false, true);
            edcFramer.SetLibraryPreviewActive(false, true);
            edcFramer.FrameNow();
            presenter.RefreshLayout();
            Render(camera, prefix + "-detail.png", true);
            presenter.ImageBasedLighting?.SetViewResponse(
                new Vector2(0.85f, 0.12f),
                false,
                0f,
                0f,
                0f);
            presenter.RefreshLayout();
            Render(camera, prefix + "-detail-ibl-left.png", true);
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
            Render(camera, outputPath, false);
        }

        private static void Render(Camera camera, string outputPath, bool warmup)
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
                if (warmup)
                {
                    UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                }
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
