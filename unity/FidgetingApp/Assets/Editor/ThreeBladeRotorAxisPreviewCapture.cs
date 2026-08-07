using System.IO;
using System.Linq;
using FidgetingApp.Product;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.Editor
{
    public static class ThreeBladeRotorAxisPreviewCapture
    {
        private const string ScenePath =
            "Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity";
        private const int Width = 720;
        private const int Height = 1280;

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

        [MenuItem("Fidgeting/Three-Blade/Capture Rotor Axis Fix Preview")]
        public static void Capture()
        {
            Scene scene = EditorSceneManager.OpenScene(
                ScenePath,
                OpenSceneMode.Single);
            Transform root = scene.GetRootGameObjects()
                .Single(candidate => candidate.name == "ThreeBladeEDC_Root")
                .transform;
            Transform rotor = root.Find("RotorDynamic");
            Transform visibleTopCap = root.Find(
                "HubStatic/TopCap/TopCap_Root/FingerCapTop_BrushedFace");
            Renderer visibleTopCapRenderer = visibleTopCap != null
                ? visibleTopCap.GetComponent<Renderer>()
                : null;
            Camera camera = Camera.main ?? Object.FindAnyObjectByType<Camera>();
            if (rotor == null || visibleTopCapRenderer == null || camera == null)
            {
                throw new InvalidDataException(
                    "The shipping three-blade scene is missing its rotor or camera.");
            }

            string folder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../Artifacts/ThreeBladeRotorAxisCenterV2"));
            Directory.CreateDirectory(folder);
            ProductFramingProfile framing = ProductFramingCatalog.Resolve(ScenePath);
            var poses = new[]
            {
                new PreviewPose("top-89", 0f, 89f),
                new PreviewPose("hero-42", 32f, 42f),
                new PreviewPose("left-oblique-35", -48f, 35f),
                new PreviewPose("right-oblique-35", 112f, 35f),
                new PreviewPose("low-15", 32f, 15f)
            };

            Quaternion initialRotorRotation = rotor.localRotation;
            Vector3 initialCameraPosition = camera.transform.position;
            Quaternion initialCameraRotation = camera.transform.rotation;
            float initialAspect = camera.aspect;
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
                name = "ThreeBladeRotorAxisFixPreview"
            };
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
                        "Unity could not create the rotor-axis preview target.");
                }

                camera.aspect = (float)Width / Height;
                camera.targetTexture = target;
                camera.clearFlags = CameraClearFlags.SolidColor;
                camera.backgroundColor = Color.black;
                camera.allowHDR = false;
                camera.allowMSAA = true;
                rotor.localRotation = initialRotorRotation;

                foreach (PreviewPose pose in poses)
                {
                    ApplyCameraPose(
                        camera,
                        root,
                        visibleTopCapRenderer.bounds.center,
                        pose,
                        framing);
                    Render(
                        camera,
                        target,
                        image,
                        Path.Combine(folder, $"view-{pose.Name}.png"),
                        false);
                }

                PreviewPose hero = poses[1];
                rotor.localRotation = initialRotorRotation;
                ApplyCameraPose(
                    camera,
                    root,
                    visibleTopCapRenderer.bounds.center,
                    hero,
                    framing);
                foreach (int angle in new[] { 0, 30, 60, 90, 120 })
                {
                    rotor.localRotation = Quaternion.Euler(0f, angle, 0f)
                        * initialRotorRotation;
                    Render(
                        camera,
                        target,
                        image,
                        Path.Combine(folder, $"spin-{angle:000}-axis-overlay.png"),
                        true);
                }
            }
            finally
            {
                rotor.localRotation = initialRotorRotation;
                camera.transform.SetPositionAndRotation(
                    initialCameraPosition,
                    initialCameraRotation);
                camera.aspect = initialAspect;
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                Object.DestroyImmediate(image);
                target.Release();
                Object.DestroyImmediate(target);
            }

            Debug.Log(
                $"[ThreeBladeRotorAxisFix] Captured five approval views and "
                + $"five centered spin frames: {folder}");
        }

        private static void ApplyCameraPose(
            Camera camera,
            Transform root,
            Vector3 visibleAxisPoint,
            PreviewPose pose,
            ProductFramingProfile framing)
        {
            if (!ProductCameraFraming.TryGetProductBounds(root, out Bounds bounds))
            {
                throw new InvalidDataException(
                    "The shipping three-blade scene has no visible product bounds.");
            }

            Quaternion orbit = Quaternion.Euler(pose.Pitch, pose.Yaw, 0f);
            Vector3 backward = orbit * Vector3.back;
            float distance = ProductCameraFraming.RequiredDistance(
                camera,
                bounds,
                backward,
                framing.DetailWidthFraction,
                framing.DetailHeightFraction,
                focusPoint: visibleAxisPoint);
            camera.transform.position = visibleAxisPoint + backward * distance;
            camera.transform.LookAt(visibleAxisPoint, Vector3.up);
        }

        private static void Render(
            Camera camera,
            RenderTexture target,
            Texture2D image,
            string outputPath,
            bool drawAxisOverlay)
        {
            RenderTexture.active = target;
            GL.Clear(true, true, Color.black);
            var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest
            {
                destination = target
            };
            UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
            RenderTexture.active = target;
            image.ReadPixels(new Rect(0f, 0f, Width, Height), 0, 0, false);
            image.Apply(false, false);
            if (drawAxisOverlay)
            {
                DrawAxisOverlay(image);
            }
            File.WriteAllBytes(outputPath, image.EncodeToPNG());
        }

        private static void DrawAxisOverlay(Texture2D image)
        {
            int centerX = image.width / 2;
            int centerY = image.height / 2;
            Color marker = new Color(0.20f, 0.95f, 1f, 1f);
            for (int offset = -14; offset <= 14; offset++)
            {
                image.SetPixel(centerX + offset, centerY, marker);
                image.SetPixel(centerX, centerY + offset, marker);
            }
            image.Apply(false, false);
        }
    }
}
