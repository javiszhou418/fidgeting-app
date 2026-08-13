using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FidgetingApp.Product;
using FidgetingApp.TwoLobeBar.Geometry;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EditorTools
{
    public static class SpinnerAxisTrimPreviewCapture
    {
        private const int Width = 720;
        private const int Height = 1280;

        private readonly struct ProductDefinition
        {
            public ProductDefinition(string modelId, string scenePath, string rootName)
            {
                ModelId = modelId;
                ScenePath = scenePath;
                RootName = rootName;
            }

            public string ModelId { get; }
            public string ScenePath { get; }
            public string RootName { get; }
        }

        private readonly struct PreviewPose
        {
            public PreviewPose(string fileName, float yaw, float pitch)
            {
                FileName = fileName;
                Yaw = yaw;
                Pitch = pitch;
            }

            public string FileName { get; }
            public float Yaw { get; }
            public float Pitch { get; }
        }

        [MenuItem("Tools/Codex/Capture Spinner Axis Trim Approval Views")]
        public static void Capture()
        {
            var products = new[]
            {
                new ProductDefinition(
                    ProductCatalog.PointedThreeBladeModelId,
                    SpinnerEnvironmentCatalog.PointedScenePath,
                    "ThreeBladeEDC_Root"),
                new ProductDefinition(
                    ProductCatalog.MetalThreeBladeModelId,
                    SpinnerEnvironmentCatalog.MetalScenePath,
                    "ThreeBladeEDC_Root"),
                new ProductDefinition(
                    ProductCatalog.GoldFourWingModelId,
                    SpinnerEnvironmentCatalog.ImportedScenePath,
                    "ImportedSpinner_Root"),
                new ProductDefinition(
                    ProductCatalog.GraphiteTwoLobeModelId,
                    TwoLobeBarSpecifications.ScenePath,
                    "TwoLobeBar_Root")
            };
            var poses = new[]
            {
                new PreviewPose("01-authored-hero-42.png", 32f, 42f),
                new PreviewPose("02-top-89.png", 0f, 89f),
                new PreviewPose("03-left-oblique-35.png", -48f, 35f),
                new PreviewPose("04-right-oblique-35.png", 112f, 35f),
                new PreviewPose("05-low-angle-15.png", 32f, 15f)
            };

            string rootFolder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../Artifacts/SpinnerAxisTrimRemovalPreview"));
            Directory.CreateDirectory(rootFolder);
            SceneSetup[] previousSetup = EditorSceneManager.GetSceneManagerSetup();
            try
            {
                foreach (ProductDefinition product in products)
                {
                    CaptureProduct(product, poses, rootFolder);
                }
            }
            finally
            {
                if (previousSetup != null && previousSetup.Any(setup => setup.isLoaded))
                {
                    EditorSceneManager.RestoreSceneManagerSetup(previousSetup);
                }
                else
                {
                    EditorSceneManager.NewScene(
                        NewSceneSetup.EmptyScene,
                        NewSceneMode.Single);
                }
            }

            File.WriteAllText(
                Path.Combine(rootFolder, "README.txt"),
                "Source: four saved shipping Unity scenes\n"
                + "Views per product: authored hero, top, left/right oblique, low angle\n"
                + "Removed: decorative axis trims/bezel/shadow collars only\n"
                + "Preserved: finger caps, axle, bearing races, washers, collision and interaction\n"
                + "Device installation: blocked pending explicit visual approval\n");
            Debug.Log($"[SpinnerAxisTrim] Approval views written: {rootFolder}");
        }

        private static void CaptureProduct(
            ProductDefinition product,
            IReadOnlyList<PreviewPose> poses,
            string rootFolder)
        {
            Scene scene = EditorSceneManager.OpenScene(
                product.ScenePath,
                OpenSceneMode.Single);
            Transform root = scene.GetRootGameObjects()
                .Single(candidate => candidate.name == product.RootName)
                .transform;
            Camera camera = Camera.main ?? UnityEngine.Object.FindAnyObjectByType<Camera>();
            OrbitPresentationCamera orbit =
                UnityEngine.Object.FindAnyObjectByType<OrbitPresentationCamera>();
            if (camera == null || orbit == null)
            {
                throw new InvalidDataException(
                    $"{product.ScenePath} has no shipping camera/orbit.");
            }
            if (!ProductCameraFraming.TryGetProductBounds(root, out Bounds bounds))
            {
                throw new InvalidDataException(
                    $"{product.ScenePath} has no visible product bounds.");
            }

            ProductFramingProfile framing = ProductFramingCatalog.Resolve(
                product.ScenePath);
            Vector3 focusPoint = orbit.FocusPoint;
            string folder = Path.Combine(rootFolder, product.ModelId);
            Directory.CreateDirectory(folder);

            Vector3 previousPosition = camera.transform.position;
            Quaternion previousRotation = camera.transform.rotation;
            float previousAspect = camera.aspect;
            CameraClearFlags previousClearFlags = camera.clearFlags;
            Color previousBackground = camera.backgroundColor;
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
                name = $"SpinnerAxisTrim_{product.ModelId}"
            };
            var image = new Texture2D(
                Width,
                Height,
                TextureFormat.RGB24,
                false,
                false);

            try
            {
                if (!target.Create())
                {
                    throw new InvalidDataException(
                        $"Could not create preview target for {product.ModelId}.");
                }
                camera.aspect = (float)Width / Height;
                camera.targetTexture = target;
                camera.clearFlags = CameraClearFlags.SolidColor;
                camera.backgroundColor = product.ModelId
                    == ProductCatalog.GraphiteTwoLobeModelId
                    ? new Color(0.12f, 0.10f, 0.09f, 1f)
                    : Color.black;
                camera.allowHDR = false;
                camera.allowMSAA = true;

                foreach (PreviewPose pose in poses)
                {
                    Quaternion rotation = Quaternion.Euler(pose.Pitch, pose.Yaw, 0f);
                    Vector3 backward = rotation * Vector3.back;
                    float distance = ProductCameraFraming.RequiredDistance(
                        camera,
                        bounds,
                        backward,
                        framing.DetailWidthFraction,
                        framing.DetailHeightFraction,
                        focusPoint: focusPoint);
                    camera.transform.position = focusPoint + backward * distance;
                    camera.transform.LookAt(focusPoint, Vector3.up);
                    Render(camera, target, image, Path.Combine(folder, pose.FileName));
                }
            }
            finally
            {
                camera.transform.SetPositionAndRotation(previousPosition, previousRotation);
                camera.aspect = previousAspect;
                camera.clearFlags = previousClearFlags;
                camera.backgroundColor = previousBackground;
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                UnityEngine.Object.DestroyImmediate(image);
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
            }
        }

        private static void Render(
            Camera camera,
            RenderTexture target,
            Texture2D image,
            string path)
        {
            RenderTexture.active = target;
            GL.Clear(true, true, camera.backgroundColor);
            var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest
            {
                destination = target
            };
            UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
            RenderTexture.active = target;
            image.ReadPixels(new Rect(0f, 0f, Width, Height), 0, 0, false);
            image.Apply(false, false);
            File.WriteAllBytes(path, image.EncodeToPNG());
        }
    }
}
