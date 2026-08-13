using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
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
    /// Renders a visual-approval-only cyberpunk plate through the shipping
    /// blue-spinner scene. The preview texture lives under Assets/Editor so it
    /// cannot enter a player build, and the shipping environment catalog is
    /// never modified by this capture.
    /// </summary>
    public static class CyberpunkEnvironmentPreviewCapture
    {
        private const string PreviewTextureAssetPath =
            "Assets/Editor/CyberpunkPreviewAssets/"
            + "cyber-neon-parallax-depth-v13.png";
        private const string PreviewPaletteKey =
            "EditorPreview/cyber-neon-parallax-depth-v13";
        private const string ModelId = "pointed-three-blade";
        private const int Width = 900;
        private const int Height = 1600;
        private const float PreviewSaturation = 0.82f;
        private const float SupportTopViewportY = 0.376f;
        private const float ProductHoverPixels = 4f;

        private readonly struct PreviewView
        {
            public PreviewView(
                string fileName,
                bool shippingPose,
                float pitch,
                float yaw)
            {
                FileName = fileName;
                ShippingPose = shippingPose;
                Pitch = pitch;
                Yaw = yaw;
            }

            public string FileName { get; }
            public bool ShippingPose { get; }
            public float Pitch { get; }
            public float Yaw { get; }
        }

        [MenuItem("Fidgeting/Product/Capture Cyberpunk Environment Preview")]
        public static void Capture()
        {
            ConfigurePreviewTexture();
            Texture2D previewTexture = AssetDatabase.LoadAssetAtPath<Texture2D>(
                PreviewTextureAssetPath);
            if (previewTexture == null)
            {
                throw new FileNotFoundException(
                    "Cyberpunk preview texture is missing.",
                    PreviewTextureAssetPath);
            }

            SpinnerEnvironmentProfile profile =
                SpinnerEnvironmentCatalog.Profiles.First(candidate =>
                    string.Equals(candidate.ModelId, ModelId, StringComparison.Ordinal));
            EditorSceneManager.OpenScene(profile.ScenePath, OpenSceneMode.Single);
            Camera camera = Camera.main ?? UnityEngine.Object.FindAnyObjectByType<Camera>();
            if (camera == null)
            {
                throw new MissingReferenceException(
                    $"Shipping preview camera is missing: {profile.ScenePath}");
            }

            float previousAspect = camera.aspect;
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            camera.aspect = (float)Width / Height;

            SpinnerEnvironmentPresenter presenter =
                SpinnerEnvironmentPresenter.Install(profile.ScenePath);
            if (presenter == null
                || presenter.BackgroundRenderer == null
                || presenter.GroundingStage == null)
            {
                throw new InvalidDataException(
                    $"Shipping environment setup failed: {profile.ScenePath}");
            }

            presenter.SetLibraryPreviewActive(true, true);
            ApplyShippingLibraryFraming(camera);
            AlignCameraToSupport(
                camera,
                presenter.GroundingStage.ModelRenderers,
                presenter.GroundingStage.ModelBounds);
            ApplyPreviewPlate(presenter, profile, previewTexture);
            presenter.RefreshLayout();
            presenter.ImageBasedLighting?.SetViewResponse(
                Vector2.zero,
                false,
                0f,
                0f,
                0.32f);

            Vector3 shippingPosition = camera.transform.position;
            Quaternion shippingRotation = camera.transform.rotation;
            Matrix4x4 shippingProjection = camera.projectionMatrix;
            Bounds modelBounds = presenter.GroundingStage.ModelBounds;
            float cameraDistance = Mathf.Max(
                Vector3.Distance(shippingPosition, modelBounds.center),
                modelBounds.extents.magnitude * 2.8f);

            string outputFolder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../Artifacts/CyberpunkEnvironmentUnityPreviewV13"));
            Directory.CreateDirectory(outputFolder);

            var views = new[]
            {
                new PreviewView("01-library-hero.png", true, 0f, 0f),
                new PreviewView("02-authored-hero-42.png", false, 42f, 32f),
                new PreviewView("03-top-89.png", false, 89f, 0f),
                new PreviewView("04-left-oblique-35.png", false, 35f, -48f),
                new PreviewView("05-right-oblique-35.png", false, 35f, 112f),
                new PreviewView("06-low-angle-15.png", false, 15f, 32f)
            };

            var target = new RenderTexture(
                Width,
                Height,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB)
            {
                antiAliasing = 4,
                name = "CyberpunkEnvironmentShippingScenePreview"
            };
            var readback = new Texture2D(
                Width,
                Height,
                TextureFormat.RGB24,
                false,
                false);
            var contactSheet = new Texture2D(
                Width * 3,
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

                for (int index = 0; index < views.Length; index++)
                {
                    PreviewView view = views[index];
                    if (view.ShippingPose)
                    {
                        camera.transform.SetPositionAndRotation(
                            shippingPosition,
                            shippingRotation);
                    }
                    else
                    {
                        Quaternion orbit = Quaternion.Euler(
                            view.Pitch,
                            view.Yaw,
                            0f);
                        camera.transform.position = modelBounds.center
                            + orbit * (Vector3.back * cameraDistance);
                        camera.transform.LookAt(modelBounds.center, Vector3.up);
                        AlignCameraToSupport(
                            camera,
                            presenter.GroundingStage.ModelRenderers,
                            modelBounds);
                    }

                    camera.projectionMatrix = shippingProjection;
                    presenter.RefreshLayout();
                    presenter.ImageBasedLighting?.SetViewResponse(
                        Vector2.zero,
                        false,
                        0f,
                        0f,
                        0.32f);

                    // Warm up the camera-attached plate and generated reflection
                    // before the approval frame is read back.
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
                        Path.Combine(outputFolder, view.FileName),
                        readback.EncodeToPNG());

                    int column = index % 3;
                    int row = index / 3;
                    contactSheet.SetPixels(
                        column * Width,
                        (1 - row) * Height,
                        Width,
                        Height,
                        readback.GetPixels());
                }

                contactSheet.Apply(false, false);
                File.WriteAllBytes(
                    Path.Combine(outputFolder, "cyber-pointed-spinner-contact-sheet.png"),
                    contactSheet.EncodeToPNG());
                File.WriteAllText(
                    Path.Combine(outputFolder, "README.txt"),
                    "Shipping scene: Assets/Scenes/FidgetSpinnerDemo.unity\n"
                    + "Preview-only plate: " + PreviewTextureAssetPath + "\n"
                    + "Preview product: pointed-three-blade, camera-framed 4 px above the measured center contact plane of the raised docking surface.\n"
                    + "Product transforms and physics are unchanged.\n"
                    + "Top row: shipping library hero, authored hero 42°, top 89°.\n"
                    + "Bottom row: left oblique 35°, right oblique 35°, low 15°.\n"
                    + "The shipping environment catalog and player resources are unchanged.\n");
            }
            finally
            {
                camera.transform.SetPositionAndRotation(
                    shippingPosition,
                    shippingRotation);
                camera.projectionMatrix = shippingProjection;
                camera.aspect = previousAspect;
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                UnityEngine.Object.DestroyImmediate(contactSheet);
                UnityEngine.Object.DestroyImmediate(readback);
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
            }

            Debug.Log(
                $"[FidgetingApp] Captured shipping-scene cyberpunk previews: "
                + outputFolder);
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
        }

        private static void AlignCameraToSupport(
            Camera camera,
            IReadOnlyList<Renderer> modelRenderers,
            Bounds modelBounds)
        {
            float projectedBottom = float.PositiveInfinity;
            for (int rendererIndex = 0;
                rendererIndex < modelRenderers.Count;
                rendererIndex++)
            {
                Renderer renderer = modelRenderers[rendererIndex];
                if (renderer == null || !renderer.enabled)
                {
                    continue;
                }

                Bounds rendererBounds = renderer.bounds;
                Vector3 minimum = rendererBounds.min;
                Vector3 maximum = rendererBounds.max;
                for (int x = 0; x < 2; x++)
                {
                    for (int y = 0; y < 2; y++)
                    {
                        for (int z = 0; z < 2; z++)
                        {
                            Vector3 corner = new Vector3(
                                x == 0 ? minimum.x : maximum.x,
                                y == 0 ? minimum.y : maximum.y,
                                z == 0 ? minimum.z : maximum.z);
                            Vector3 viewport = camera.WorldToViewportPoint(corner);
                            if (viewport.z > 0f)
                            {
                                projectedBottom = Mathf.Min(
                                    projectedBottom,
                                    viewport.y);
                            }
                        }
                    }
                }
            }

            if (float.IsInfinity(projectedBottom))
            {
                throw new InvalidOperationException(
                    "The shipping product is behind the preview camera.");
            }

            float targetBottom = SupportTopViewportY
                + ProductHoverPixels / Height;
            float viewportDelta = targetBottom - projectedBottom;
            Vector3 centerViewport = camera.WorldToViewportPoint(modelBounds.center);
            Vector3 currentCenter = camera.ViewportToWorldPoint(centerViewport);
            centerViewport.y += viewportDelta;
            Vector3 targetCenter = camera.ViewportToWorldPoint(centerViewport);
            // Moving the camera opposite to the desired apparent product shift
            // preserves every Rigidbody and product transform. The background
            // is camera-attached, so the locked support height stays fixed.
            Vector3 cameraShift = currentCenter - targetCenter;
            Vector3 previousPosition = camera.transform.position;
            camera.transform.position += cameraShift;
            Debug.Log(
                "[FidgetingApp] Cyber preview camera alignment: "
                + $"projectedBottom={projectedBottom:0.0000}, "
                + $"targetBottom={targetBottom:0.0000}, "
                + $"viewportDelta={viewportDelta:0.0000}, "
                + $"cameraShift={cameraShift}, "
                + $"camera={previousPosition}->{camera.transform.position}.");
        }

        private static void ApplyPreviewPlate(
            SpinnerEnvironmentPresenter presenter,
            SpinnerEnvironmentProfile shippingProfile,
            Texture2D previewTexture)
        {
            var properties = new MaterialPropertyBlock();
            presenter.BackgroundRenderer.GetPropertyBlock(properties);
            properties.SetTexture("_BaseMap", previewTexture);
            properties.SetTexture("_MainTex", previewTexture);
            properties.SetColor("_BaseColor", Color.white);
            properties.SetFloat("_Saturation", PreviewSaturation);
            presenter.BackgroundRenderer.SetPropertyBlock(properties);

            SetLayerActive(presenter.DeepStarfieldRenderer, false);
            SetLayerActive(presenter.NearStarfieldRenderer, false);
            SetLayerActive(presenter.RightForegroundRenderer, false);
            SetLayerActive(presenter.LeftForegroundRenderer, false);

            SpinnerEnvironmentProfile previewProfile = CloneForPreview(
                shippingProfile,
                previewTexture.width,
                previewTexture.height);
            presenter.ImageBasedLighting?.Configure(
                previewTexture,
                previewProfile,
                presenter.GroundingStage);
            presenter.SetLibraryPreviewActive(true, true);
        }

        private static SpinnerEnvironmentProfile CloneForPreview(
            SpinnerEnvironmentProfile source,
            int sourceWidth,
            int sourceHeight)
        {
            return new SpinnerEnvironmentProfile(
                source.ModelId,
                source.ScenePath,
                PreviewPaletteKey,
                sourceWidth,
                sourceHeight,
                2048,
                source.CoverOverscan,
                PreviewSaturation,
                false,
                source.AmbientSky,
                source.AmbientEquator,
                source.AmbientGround,
                source.ReflectionIntensity,
                source.LibraryLightScale,
                source.LibraryReflectionScale,
                source.StageShape,
                source.StageScale,
                source.StageThicknessRatio,
                true,
                source.LegacyBackdropObjectName,
                source.Lights.ToArray());
        }

        private static void SetLayerActive(Renderer renderer, bool active)
        {
            if (renderer != null)
            {
                renderer.gameObject.SetActive(active);
            }
        }

        private static void ConfigurePreviewTexture()
        {
            AssetDatabase.ImportAsset(
                PreviewTextureAssetPath,
                ImportAssetOptions.ForceSynchronousImport);
            TextureImporter importer =
                AssetImporter.GetAtPath(PreviewTextureAssetPath) as TextureImporter;
            if (importer == null)
            {
                throw new InvalidDataException(
                    $"Preview texture importer is missing: {PreviewTextureAssetPath}");
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
