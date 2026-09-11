using System;
using System.IO;
using System.Linq;
using System.Text;
using FidgetingApp.Product;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace FidgetingApp.Editor
{
    /// <summary>
    /// Renders GEEONE from the shipping metal scene once per
    /// <see cref="GeeoneLightingPresetCatalog"/> preset so the user can pick a
    /// softer recipe side by side. Camera HDR/post settings are left exactly as
    /// the scene ships; only the lighting preset changes between rows.
    /// Output: Artifacts/GeeoneLighting/&lt;round&gt;/&lt;preset&gt;-&lt;view&gt;.png
    /// </summary>
    public static class GeeoneLightingOptionsPreviewCapture
    {
        private const int Width = 720;
        private const int Height = 1280;
        private const string RoundEnvironmentVariable = "GEEONE_LIGHTING_ROUND";
        private const string DefaultRound = "r001";

        private readonly struct PreviewPose
        {
            public PreviewPose(string name, float yaw, float pitch, bool library, bool shippingCamera = false)
            {
                Name = name;
                Yaw = yaw;
                Pitch = pitch;
                Library = library;
                ShippingCamera = shippingCamera;
            }

            public string Name { get; }
            public float Yaw { get; }
            public float Pitch { get; }
            public bool Library { get; }
            /// <summary>Leave the camera exactly where the app opens the detail scene.</summary>
            public bool ShippingCamera { get; }
        }

        private static readonly PreviewPose[] Poses =
        {
            new PreviewPose("library", 0f, 89f, true),
            new PreviewPose("phone", 0f, 0f, false, shippingCamera: true),
            new PreviewPose("hero", 32f, 42f, false),
            new PreviewPose("low", 32f, 15f, false)
        };

        [MenuItem("Tools/Codex/Capture GEEONE Lighting Options")]
        public static void CaptureAll()
        {
            string round = Environment.GetEnvironmentVariable(RoundEnvironmentVariable);
            if (string.IsNullOrWhiteSpace(round))
            {
                round = DefaultRound;
            }

            string folder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../../../Artifacts/GeeoneLighting",
                round));
            Directory.CreateDirectory(folder);

            SceneSetup[] previousSetup = EditorSceneManager.GetSceneManagerSetup();
            try
            {
                Scene scene = EditorSceneManager.OpenScene(
                    SpinnerEnvironmentCatalog.MetalScenePath,
                    OpenSceneMode.Single);
                Transform root = scene.GetRootGameObjects()
                    .Single(candidate => candidate.name == "ThreeBladeEDC_Root")
                    .transform;
                Capture(root, folder);
            }
            finally
            {
                GeeoneLightingPresetCatalog.ResetActive();
                if (previousSetup != null && previousSetup.Any(setup => setup.isLoaded))
                {
                    EditorSceneManager.RestoreSceneManagerSetup(previousSetup);
                }
                else
                {
                    EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                }
            }

            Debug.Log($"[GeeoneLighting] preset previews -> {folder}");
        }

        private static void Capture(Transform root, string folder)
        {
            Camera camera = Camera.main ?? Object.FindAnyObjectByType<Camera>();
            OrbitPresentationCamera orbit = Object.FindAnyObjectByType<OrbitPresentationCamera>();
            if (camera == null || orbit == null)
            {
                throw new InvalidDataException("The metal scene has no shipping camera/orbit.");
            }

            SpinnerEnvironmentPresenter presenter =
                SpinnerEnvironmentPresenter.Install(SpinnerEnvironmentCatalog.MetalScenePath);
            if (!ProductCameraFraming.TryGetProductBounds(root, out Bounds bounds))
            {
                throw new InvalidDataException("The metal scene has no visible product bounds.");
            }

            ProductFramingProfile framing =
                ProductFramingCatalog.Resolve(SpinnerEnvironmentCatalog.MetalScenePath);
            Vector3 focus = orbit.FocusPoint;

            Vector3 previousPosition = camera.transform.position;
            Quaternion previousRotation = camera.transform.rotation;
            float previousAspect = camera.aspect;
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            var target = NewTarget(Width, Height, "GeeoneLightingOptions");
            var image = new Texture2D(Width, Height, TextureFormat.RGB24, false, false);
            var manifest = new StringBuilder();
            manifest.AppendLine("{");
            manifest.AppendLine($"  \"scene\": \"{SpinnerEnvironmentCatalog.MetalScenePath}\",");
            manifest.AppendLine($"  \"cameraHdr\": {camera.allowHDR.ToString().ToLowerInvariant()},");
            manifest.AppendLine("  \"presets\": [");
            try
            {
                camera.aspect = (float)Width / Height;
                camera.targetTexture = target;

                for (int presetIndex = 0; presetIndex < GeeoneLightingPresetCatalog.All.Count; presetIndex++)
                {
                    GeeoneLightingPreset preset = GeeoneLightingPresetCatalog.All[presetIndex];
                    GeeoneLightingPresetCatalog.SetActiveForPreview(preset);
                    // The environment cubemap is built in Configure; re-install
                    // so the preset's StudioSoftboxIntensity is baked in.
                    presenter = SpinnerEnvironmentPresenter.Install(SpinnerEnvironmentCatalog.MetalScenePath);
                    camera.targetTexture = target;

                    foreach (PreviewPose pose in Poses)
                    {
                        // Re-resolve the recipe for this preset and pose; immediate
                        // so the batch render lands on the final state.
                        presenter.SetLibraryPreviewActive(pose.Library, true);
                        PortraitProjection(camera, (float)Width / Height);
                        if (pose.ShippingCamera)
                        {
                            camera.transform.SetPositionAndRotation(previousPosition, previousRotation);
                        }
                        else
                        {
                            ApplyPose(
                                camera,
                                bounds,
                                focus,
                                pose,
                                pose.Library ? framing.LibraryWidthFraction : framing.DetailWidthFraction,
                                pose.Library ? framing.LibraryHeightFraction : framing.DetailHeightFraction);
                        }
                        presenter.ImageBasedLighting?.SetViewResponse(Vector2.zero, false, 0f, 0f, 0f);
                        presenter.RefreshLayout();
                        Render(camera, target, image, Path.Combine(folder, $"{preset.Id}-{pose.Name}.png"));
                    }

                    SpinnerImageBasedLightingController.PresentationLightingState state =
                        presenter.ImageBasedLighting.ResolvePresentationState(false);
                    manifest.AppendLine("    {");
                    manifest.AppendLine($"      \"id\": \"{preset.Id}\",");
                    manifest.AppendLine($"      \"displayName\": \"{preset.DisplayName}\",");
                    manifest.AppendLine($"      \"directLightBoost\": {preset.DirectLightBoost:F2},");
                    manifest.AppendLine($"      \"reflectionBoost\": {preset.ReflectionBoost:F2},");
                    manifest.AppendLine($"      \"ambientBoost\": {preset.AmbientBoost:F2},");
                    manifest.AppendLine($"      \"visibilityFillIntensity\": {preset.VisibilityFillIntensity:F2},");
                    manifest.AppendLine($"      \"ambientFloorScale\": {preset.AmbientFloorScale:F2},");
                    manifest.AppendLine($"      \"studioSoftboxIntensity\": {preset.StudioSoftboxIntensity:F2},");
                    manifest.AppendLine($"      \"lightFloors\": [{preset.KeyLightFloor:F2}, {preset.WarmRimLightFloor:F2}, {preset.CoolFillLightFloor:F2}],");
                    manifest.AppendLine($"      \"resolvedReflectionIntensity\": {RenderSettings.reflectionIntensity:F3},");
                    manifest.AppendLine($"      \"resolvedAmbientSky\": [{state.AmbientSky.r:F3}, {state.AmbientSky.g:F3}, {state.AmbientSky.b:F3}],");
                    manifest.AppendLine($"      \"resolvedLights\": {{{ResolvedLights()}}}");
                    manifest.Append("    }");
                    manifest.AppendLine(presetIndex + 1 < GeeoneLightingPresetCatalog.All.Count ? "," : string.Empty);
                }
            }
            finally
            {
                GeeoneLightingPresetCatalog.ResetActive();
                presenter = SpinnerEnvironmentPresenter.Install(SpinnerEnvironmentCatalog.MetalScenePath);
                presenter.SetLibraryPreviewActive(true, true);
                camera.transform.SetPositionAndRotation(previousPosition, previousRotation);
                camera.ResetProjectionMatrix();
                camera.aspect = previousAspect;
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                Object.DestroyImmediate(image);
                target.Release();
                Object.DestroyImmediate(target);
            }

            manifest.AppendLine("  ]");
            manifest.AppendLine("}");
            File.WriteAllText(Path.Combine(folder, "presets.json"), manifest.ToString());
        }

        private static string ResolvedLights()
        {
            return string.Join(
                ", ",
                Object.FindObjectsByType<Light>(FindObjectsInactive.Exclude)
                    .OrderBy(light => light.name, StringComparer.Ordinal)
                    .Select(light => $"\"{light.name}\": {light.intensity:F3}"));
        }

        private static void PortraitProjection(Camera camera, float aspect)
        {
            camera.ResetProjectionMatrix();
            camera.aspect = aspect;
        }

        private static RenderTexture NewTarget(int width, int height, string name)
        {
            var target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB)
            {
                antiAliasing = 4,
                name = name
            };
            if (!target.Create())
            {
                throw new InvalidDataException($"Could not create render target {name}.");
            }
            return target;
        }

        private static void ApplyPose(
            Camera camera,
            Bounds bounds,
            Vector3 focus,
            PreviewPose pose,
            float widthFraction,
            float heightFraction)
        {
            Vector3 backward = Quaternion.Euler(pose.Pitch, pose.Yaw, 0f) * Vector3.back;
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

        private static void Render(Camera camera, RenderTexture target, Texture2D image, string path)
        {
            RenderTexture.active = target;
            GL.Clear(true, true, camera.backgroundColor);
            var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest { destination = target };
            // Two submits: the first warms reflection probes/shadows for the new lighting state.
            UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
            UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
            RenderTexture.active = target;
            image.ReadPixels(new Rect(0f, 0f, image.width, image.height), 0, 0, false);
            image.Apply(false, false);
            File.WriteAllBytes(path, image.EncodeToPNG());
        }
    }
}
