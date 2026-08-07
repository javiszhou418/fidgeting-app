using System.Collections.Generic;
using System.IO;
using CodexUnityLab;
using FidgetingApp.EDC;
using FidgetingApp.Product;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.Editor
{
    public static class RecoveryApprovalPreviewCapture
    {
        private const int Width = 540;
        private const int Height = 960;
        private const int ThumbnailSize = 512;
        private const string OutputFolderName = "RecoveryApprovalV22";

        private readonly struct PreviewPose
        {
            public PreviewPose(string name, float yaw, float pitch)
            {
                Name = name;
                Yaw = yaw;
                Pitch = pitch;
            }

            public string Name { get; }
            public float Yaw { get; }
            public float Pitch { get; }
        }

        [MenuItem("Tools/Codex/Capture Recovery Approval Previews")]
        public static void Capture()
        {
            string outputFolder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../../../Artifacts",
                OutputFolderName));
            Directory.CreateDirectory(outputFolder);

            var poses = new[]
            {
                new PreviewPose("top", 0f, 89f),
                new PreviewPose("hero", 32f, 42f),
                new PreviewPose("left", -48f, 35f),
                new PreviewPose("right", 112f, 35f),
                new PreviewPose("low", 32f, 15f)
            };
            var heroImages = new List<Texture2D>();

            try
            {
                foreach (ProductCatalogEntry product in ProductCatalog.ShippingEntries)
                {
                    Scene scene = EditorSceneManager.OpenScene(
                        product.ScenePath,
                        OpenSceneMode.Single);
                    Camera camera = Camera.main ?? Object.FindAnyObjectByType<Camera>();
                    if (camera == null)
                    {
                        throw new InvalidDataException(
                            $"Shipping preview camera missing: {product.ScenePath}");
                    }

                    SpinnerEnvironmentPresenter presenter =
                        SpinnerEnvironmentPresenter.Install(product.ScenePath);
                    presenter.SetLibraryPreviewActive(false, true);
                    Transform target = ResolveTarget(camera);
                    if (target == null
                        || !ProductCameraFraming.TryGetProductBounds(target, out Bounds bounds))
                    {
                        throw new InvalidDataException(
                            $"Visible product bounds missing: {product.ScenePath}");
                    }

                    ProductFramingProfile framing = ProductFramingCatalog.Resolve(
                        product.ScenePath);
                    Vector3 focus = ResolveFocus(camera, bounds);
                    float previousAspect = camera.aspect;
                    RenderTexture previousTarget = camera.targetTexture;
                    RenderTexture previousActive = RenderTexture.active;
                    var targetTexture = new RenderTexture(
                        Width,
                        Height,
                        24,
                        RenderTextureFormat.ARGB32,
                        RenderTextureReadWrite.sRGB)
                    {
                        antiAliasing = 4,
                        name = "RecoveryApprovalPreview"
                    };
                    var readback = new Texture2D(
                        Width,
                        Height,
                        TextureFormat.RGB24,
                        false,
                        false);
                    var contactSheet = new Texture2D(
                        Width * poses.Length,
                        Height,
                        TextureFormat.RGB24,
                        false,
                        false);

                    try
                    {
                        targetTexture.Create();
                        camera.aspect = (float)Width / Height;
                        camera.targetTexture = targetTexture;
                        camera.allowHDR = false;
                        camera.allowMSAA = true;

                        for (int index = 0; index < poses.Length; index++)
                        {
                            ApplyPose(
                                camera,
                                bounds,
                                focus,
                                poses[index],
                                framing.DetailWidthFraction,
                                framing.DetailHeightFraction);
                            presenter.RefreshLayout();
                            Capture(camera, targetTexture, readback);
                            File.WriteAllBytes(
                                Path.Combine(
                                    outputFolder,
                                    $"{product.ModelId}-{poses[index].Name}.png"),
                                readback.EncodeToPNG());
                            contactSheet.SetPixels(
                                index * Width,
                                0,
                                Width,
                                Height,
                                readback.GetPixels());
                            if (poses[index].Name == "hero")
                            {
                                heroImages.Add(Clone(readback));
                            }
                        }

                        contactSheet.Apply(false, false);
                        File.WriteAllBytes(
                            Path.Combine(
                                outputFolder,
                                product.ModelId + "-five-angle-contact.png"),
                            contactSheet.EncodeToPNG());

                        if (product.ModelId == ProductCatalog.PointedThreeBladeModelId
                            || product.ModelId == ProductCatalog.MetalThreeBladeModelId)
                        {
                            WriteThumbnail(
                                camera,
                                targetTexture,
                                readback,
                                presenter,
                                bounds,
                                focus,
                                product,
                                framing);
                        }
                    }
                    finally
                    {
                        camera.aspect = previousAspect;
                        camera.targetTexture = previousTarget;
                        RenderTexture.active = previousActive;
                        Object.DestroyImmediate(readback);
                        Object.DestroyImmediate(contactSheet);
                        targetTexture.Release();
                        Object.DestroyImmediate(targetTexture);
                    }
                }

                WriteHeroContactSheet(outputFolder, heroImages);
                AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
                Debug.Log(
                    $"[Codex] Recovery approval previews captured from five shipping scenes: {outputFolder}");
            }
            finally
            {
                foreach (Texture2D hero in heroImages)
                {
                    Object.DestroyImmediate(hero);
                }
            }
        }

        private static Transform ResolveTarget(Camera camera)
        {
            OrbitPresentationCamera orbit = camera.GetComponent<OrbitPresentationCamera>();
            if (orbit != null)
            {
                return orbit.Target;
            }

            PortraitCameraFramer portrait = camera.GetComponent<PortraitCameraFramer>();
            if (portrait != null)
            {
                return portrait.Target;
            }

            EdcPortraitCameraFramer edc = camera.GetComponent<EdcPortraitCameraFramer>();
            return edc != null ? edc.Target : null;
        }

        private static Vector3 ResolveFocus(Camera camera, Bounds bounds)
        {
            OrbitPresentationCamera orbit = camera.GetComponent<OrbitPresentationCamera>();
            return orbit != null ? orbit.FocusPoint : bounds.center;
        }

        private static void ApplyPose(
            Camera camera,
            Bounds bounds,
            Vector3 focus,
            PreviewPose pose,
            float widthFraction,
            float heightFraction)
        {
            Vector3 backward = Quaternion.Euler(pose.Pitch, pose.Yaw, 0f)
                * Vector3.back;
            float distance = ProductCameraFraming.RequiredDistance(
                camera,
                bounds,
                backward,
                widthFraction,
                heightFraction,
                focusPoint: focus);
            camera.transform.position = focus + backward * distance;
            camera.transform.LookAt(focus, Vector3.up);
        }

        private static void Capture(
            Camera camera,
            RenderTexture target,
            Texture2D readback)
        {
            RenderTexture.active = target;
            GL.Clear(true, true, Color.black);
            var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest
            {
                destination = target
            };
            UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
            RenderTexture.active = target;
            readback.ReadPixels(
                new Rect(0f, 0f, readback.width, readback.height),
                0,
                0,
                false);
            readback.Apply(false, false);
        }

        private static Texture2D Clone(Texture2D source)
        {
            var clone = new Texture2D(
                source.width,
                source.height,
                TextureFormat.RGB24,
                false,
                false)
            {
                // Opening the next shipping scene triggers an unused-resource sweep.
                // Keep these five transient hero frames alive until the final contact
                // sheet is assembled, then destroy them explicitly in Capture().
                hideFlags = HideFlags.HideAndDontSave
            };
            clone.SetPixels(source.GetPixels());
            clone.Apply(false, false);
            return clone;
        }

        private static void WriteThumbnail(
            Camera camera,
            RenderTexture portraitTarget,
            Texture2D portraitReadback,
            SpinnerEnvironmentPresenter presenter,
            Bounds bounds,
            Vector3 focus,
            ProductCatalogEntry product,
            ProductFramingProfile framing)
        {
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            float previousAspect = camera.aspect;
            var squareTarget = new RenderTexture(
                ThumbnailSize,
                ThumbnailSize,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB)
            {
                antiAliasing = 4,
                name = "RecoveryProductThumbnail"
            };
            var squareImage = new Texture2D(
                ThumbnailSize,
                ThumbnailSize,
                TextureFormat.RGB24,
                false,
                false);
            try
            {
                squareTarget.Create();
                camera.aspect = 1f;
                camera.targetTexture = squareTarget;
                ApplyPose(
                    camera,
                    bounds,
                    focus,
                    new PreviewPose("library", 0f, 89f),
                    framing.LibraryWidthFraction,
                    framing.LibraryHeightFraction);
                presenter.RefreshLayout();
                Capture(camera, squareTarget, squareImage);
                string path = Path.Combine(
                    Application.dataPath,
                    "Plugins/iOS/Thumbnails/Models",
                    "product-thumbnail-" + product.ModelId + ".png");
                File.WriteAllBytes(path, squareImage.EncodeToPNG());
            }
            finally
            {
                camera.aspect = previousAspect;
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                Object.DestroyImmediate(squareImage);
                squareTarget.Release();
                Object.DestroyImmediate(squareTarget);
            }
        }

        private static void WriteHeroContactSheet(
            string outputFolder,
            IReadOnlyList<Texture2D> heroes)
        {
            var contact = new Texture2D(
                Width * heroes.Count,
                Height,
                TextureFormat.RGB24,
                false,
                false);
            try
            {
                for (int index = 0; index < heroes.Count; index++)
                {
                    contact.SetPixels(
                        index * Width,
                        0,
                        Width,
                        Height,
                        heroes[index].GetPixels());
                }
                contact.Apply(false, false);
                File.WriteAllBytes(
                    Path.Combine(outputFolder, "shipping-five-hero-contact.png"),
                    contact.EncodeToPNG());
            }
            finally
            {
                Object.DestroyImmediate(contact);
            }
        }
    }
}
