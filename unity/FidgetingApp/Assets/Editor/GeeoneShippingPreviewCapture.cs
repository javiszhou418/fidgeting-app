using System.Collections.Generic;
using System.IO;
using System.Linq;
using CodexUnityLab;
using FidgetingApp.Product;
using ThreeBladeEDC.Interaction;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace FidgetingApp.Editor
{
    /// <summary>
    /// GEEONE 龙鳞三叶 (ModelPipeline metal-three-blade) Gate 11 / Gate 12 evidence from the real shipping scene.
    /// Gate 12: top / authored hero / left+right oblique / low / phone composition + the library thumbnail.
    /// Gate 11: neutral captures with a fixed camera recipe (orthographic top, 2.3 R wide; hero) and a
    /// hierarchy / bounds / material report, compared offline against the Blender GLB round-trip renders.
    /// Batch: -executeMethod FidgetingApp.Editor.GeeoneShippingPreviewCapture.CaptureAll
    /// </summary>
    public static class GeeoneShippingPreviewCapture
    {
        private const int Width = 720;
        private const int Height = 1280;
        private const int SquareSize = 1200;
        private const int ThumbnailSize = 512;
        private const float RadiusM = 0.0425f;

        private sealed class ShippingLightingState
        {
            public Dictionary<Light, float> LightIntensities { get; } = new();
            public Color AmbientSky { get; set; }
            public Color AmbientEquator { get; set; }
            public Color AmbientGround { get; set; }
            public float ReflectionIntensity { get; set; }
            public bool CameraHdr { get; set; }
            public bool CameraPostProcessing { get; set; }
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

        [MenuItem("Tools/Codex/Capture GEEONE Shipping + Parity Views")]
        public static void CaptureAll()
        {
            string evidenceRoot = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../ArtSource/ModelPipeline/metal-three-blade/evidence"));
            string shippingFolder = Path.Combine(evidenceRoot, "12-shipping/rev-007");
            string parityFolder = Path.Combine(evidenceRoot, "11-unity-parity/rev-002");
            Directory.CreateDirectory(shippingFolder);
            Directory.CreateDirectory(parityFolder);

            SceneSetup[] previousSetup = EditorSceneManager.GetSceneManagerSetup();
            try
            {
                Scene scene = EditorSceneManager.OpenScene(
                    SpinnerEnvironmentCatalog.MetalScenePath,
                    OpenSceneMode.Single);
                Transform root = scene.GetRootGameObjects()
                    .Single(candidate => candidate.name == "ThreeBladeEDC_Root")
                    .transform;
                WriteParityReport(root, parityFolder);
                CaptureNeutral(root, parityFolder);
                CaptureShipping(root, shippingFolder);
            }
            finally
            {
                if (previousSetup != null && previousSetup.Any(setup => setup.isLoaded))
                {
                    EditorSceneManager.RestoreSceneManagerSetup(previousSetup);
                }
                else
                {
                    EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                }
            }

            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            Debug.Log($"[Geeone] shipping previews -> {shippingFolder}; parity -> {parityFolder}");
        }

        // ------------------------------------------------------------------ Gate 12
        private static void CaptureShipping(Transform root, string folder)
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

            ProductFramingProfile framing = ProductFramingCatalog.Resolve(SpinnerEnvironmentCatalog.MetalScenePath);
            Vector3 focus = orbit.FocusPoint;
            ShippingLightingState lightingState = ApplyShippingLightingBoost(camera, presenter);
            var poses = new[]
            {
                new PreviewPose("shipping-hero.png", 32f, 42f),
                new PreviewPose("shipping-top.png", 0f, 89f),
                new PreviewPose("shipping-left-oblique.png", -48f, 35f),
                new PreviewPose("shipping-right-oblique.png", 112f, 35f),
                new PreviewPose("shipping-low.png", 32f, 15f)
            };

            Vector3 previousPosition = camera.transform.position;
            Quaternion previousRotation = camera.transform.rotation;
            float previousAspect = camera.aspect;
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            var target = NewTarget(Width, Height, "GeeoneShipping");
            var image = new Texture2D(Width, Height, TextureFormat.RGB24, false, false);
            try
            {
                camera.aspect = (float)Width / Height;
                camera.targetTexture = target;
                camera.allowHDR = true;
                camera.allowMSAA = true;

                // SpinnerSceneParallaxController (installed by the presenter) pins an explicit projection matrix captured at
                // batchmode's 4:3 aspect; rendering that into a portrait target stretches the product (the same bug made the
                // RecoveryApprovalV22 previews tall). Reset to the portrait projection before every render, as
                // SpinnerEnvironmentPreviewCapture does.
                PortraitProjection(camera, (float)Width / Height);
                // phone composition = the shipping camera exactly as the app opens the scene (no pose change)
                presenter.ImageBasedLighting?.SetViewResponse(
                    Vector2.zero,
                    false,
                    0f,
                    0f,
                    0f);
                presenter.RefreshLayout();
                Render(camera, target, image, Path.Combine(folder, "shipping-phone.png"), true);

                foreach (PreviewPose pose in poses)
                {
                    PortraitProjection(camera, (float)Width / Height);
                    ApplyPose(camera, bounds, focus, pose, framing.DetailWidthFraction, framing.DetailHeightFraction);
                    presenter.ImageBasedLighting?.SetViewResponse(
                        Vector2.zero,
                        false,
                        0f,
                        0f,
                        0f);
                    presenter.RefreshLayout();
                    Render(camera, target, image, Path.Combine(folder, pose.FileName), true);
                }

                // library thumbnail: square top view like RecoveryApprovalPreviewCapture.WriteThumbnail, written both to the
                // evidence folder and to the shipping SwiftUI asset (product-thumbnail-metal-three-blade.png)
                var square = NewTarget(ThumbnailSize, ThumbnailSize, "GeeoneThumbnail");
                var squareImage = new Texture2D(ThumbnailSize, ThumbnailSize, TextureFormat.RGB24, false, false);
                try
                {
                    camera.targetTexture = square;
                    PortraitProjection(camera, 1f);
                    ApplyPose(camera, bounds, focus, new PreviewPose("library", 0f, 89f), framing.LibraryWidthFraction, framing.LibraryHeightFraction);
                    presenter.ImageBasedLighting?.SetViewResponse(
                        Vector2.zero,
                        false,
                        0f,
                        0f,
                        0f);
                    presenter.RefreshLayout();
                    Render(camera, square, squareImage, Path.Combine(folder, "shipping-library.png"), true);
                    File.WriteAllBytes(
                        Path.Combine(Application.dataPath, "Plugins/iOS/Thumbnails/Models", "product-thumbnail-metal-three-blade.png"),
                        squareImage.EncodeToPNG());
                }
                finally
                {
                    Object.DestroyImmediate(squareImage);
                    square.Release();
                    Object.DestroyImmediate(square);
                }
            }
            finally
            {
                RestoreShippingLighting(camera, lightingState);
                camera.transform.SetPositionAndRotation(previousPosition, previousRotation);
                camera.ResetProjectionMatrix();
                camera.aspect = previousAspect;
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                Object.DestroyImmediate(image);
                target.Release();
                Object.DestroyImmediate(target);
            }
        }

        private static ShippingLightingState ApplyShippingLightingBoost(
            Camera camera,
            SpinnerEnvironmentPresenter presenter)
        {
            var state = new ShippingLightingState
            {
                AmbientSky = RenderSettings.ambientSkyColor,
                AmbientEquator = RenderSettings.ambientEquatorColor,
                AmbientGround = RenderSettings.ambientGroundColor,
                ReflectionIntensity = RenderSettings.reflectionIntensity,
            };
            UniversalAdditionalCameraData cameraData =
                camera.GetUniversalAdditionalCameraData();
            state.CameraHdr = camera.allowHDR;
            state.CameraPostProcessing = cameraData.renderPostProcessing;

            presenter.SetLibraryPreviewActive(false, true);
            presenter.ImageBasedLighting?.SetViewResponse(
                Vector2.zero,
                false,
                0f,
                0f,
                0f);

            // Lighting comes only from the runtime recipe applied by
            // SpinnerImageBasedLightingController.SetLibraryPreviewActive above.
            // rev-007 previews hard-coded a third, brighter set here and did not
            // match the phone; the capture must show what ships.
            foreach (Light light in Object.FindObjectsByType<Light>(FindObjectsInactive.Exclude))
            {
                state.LightIntensities[light] = light.intensity;
            }

            camera.allowHDR = true;
            cameraData.renderPostProcessing = true;
            return state;
        }

        private static void RestoreShippingLighting(
            Camera camera,
            ShippingLightingState state)
        {
            if (state == null)
            {
                return;
            }

            foreach (KeyValuePair<Light, float> entry in state.LightIntensities)
            {
                if (entry.Key != null)
                {
                    entry.Key.intensity = entry.Value;
                }
            }

            RenderSettings.ambientSkyColor = state.AmbientSky;
            RenderSettings.ambientEquatorColor = state.AmbientEquator;
            RenderSettings.ambientGroundColor = state.AmbientGround;
            RenderSettings.reflectionIntensity = state.ReflectionIntensity;
            camera.allowHDR = state.CameraHdr;
            camera.GetUniversalAdditionalCameraData().renderPostProcessing =
                state.CameraPostProcessing;
        }

        // ------------------------------------------------------------------ Gate 11
        private static void CaptureNeutral(Transform root, string folder)
        {
            // A temporary neutral camera (no environment presenter, black background) with the same recipe as the
            // Blender GLB round-trip renders: orthographic top view 2.3 R wide, and the hero from (1.2R, -1.6R, 1.5R)
            // in Blender axes. FBX maps Blender (x, y, z) -> Unity (x, z, -y); the builder then yaws the model 180°
            // about Y, so the same view point is Unity (-1.2R, 1.5R, -1.6R).
            var go = new GameObject("GeeoneNeutralCamera");
            Camera camera = go.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.black;
            camera.allowHDR = false;
            camera.allowMSAA = true;
            camera.nearClipPlane = 0.001f;
            camera.farClipPlane = 5f;
            var target = NewTarget(SquareSize, SquareSize, "GeeoneNeutral");
            var image = new Texture2D(SquareSize, SquareSize, TextureFormat.RGB24, false, false);
            RenderTexture previousActive = RenderTexture.active;
            Transform body = root.Find("RotorDynamic/Rotor_Root/Rotor_Body");
            if (body == null)
            {
                throw new InvalidDataException("Rotor_Body is missing from the metal scene.");
            }
            // The product sits above the studio floor; the Blender recipe is centred on the rotor's mid-plane at the axis.
            Vector3 centre = body.GetComponent<Renderer>().bounds.center;
            centre.x = body.position.x;
            centre.z = body.position.z;
            // Silhouette capture: the four GEEONE parts in flat unlit white, everything else hidden, so the mask
            // compares geometry only (lighting differs from Blender by design).
            Renderer[] parts = new[] { "RotorDynamic/Rotor_Root/Rotor_Body", "HubStatic/TopCap/Cap_Top", "HubStatic/BottomCap/Cap_Bottom", "HubStatic/Hub_Core" }
                .Select(path => root.Find(path))
                .Where(t => t != null)
                .Select(t => t.GetComponent<Renderer>())
                .Where(r => r != null)
                .ToArray();
            Renderer[] allRenderers = Object.FindObjectsByType<Renderer>(FindObjectsInactive.Exclude, FindObjectsSortMode.None);
            var hidden = new List<Renderer>();
            var savedMaterials = new Dictionary<Renderer, Material[]>();
            Shader unlitShader = Shader.Find("Universal Render Pipeline/Unlit");
            var unlit = new Material(unlitShader) { color = Color.white, name = "GeeoneSilhouetteUnlit" };
            foreach (Renderer r in allRenderers)
            {
                if (parts.Contains(r))
                {
                    savedMaterials[r] = r.sharedMaterials;
                    r.sharedMaterials = r.sharedMaterials.Select(_ => unlit).ToArray();
                }
                else if (r.enabled)
                {
                    r.enabled = false;
                    hidden.Add(r);
                }
            }
            try
            {
                camera.targetTexture = target;
                camera.aspect = 1f;
                camera.orthographic = true;
                camera.orthographicSize = 2.3f * RadiusM / 2f;
                camera.transform.position = centre + Vector3.up * 1f;
                camera.transform.rotation = Quaternion.LookRotation(Vector3.down, Vector3.forward);
                Render(camera, target, image, Path.Combine(folder, "unity-neutral-top-ortho.png"));

                camera.orthographic = false;
                camera.fieldOfView = Camera.FocalLengthToFieldOfView(50f, 36f);
                camera.transform.position = centre + new Vector3(-1.2f * RadiusM, 1.5f * RadiusM, -1.6f * RadiusM);
                camera.transform.LookAt(centre + Vector3.up * 0.3f * 0.085f * RadiusM, Vector3.up);
                Render(camera, target, image, Path.Combine(folder, "unity-neutral-hero.png"));
            }
            finally
            {
                foreach (KeyValuePair<Renderer, Material[]> entry in savedMaterials)
                {
                    entry.Key.sharedMaterials = entry.Value;
                }
                foreach (Renderer r in hidden)
                {
                    r.enabled = true;
                }
                Object.DestroyImmediate(unlit);
                RenderTexture.active = previousActive;
                Object.DestroyImmediate(image);
                target.Release();
                Object.DestroyImmediate(target);
                Object.DestroyImmediate(go);
            }
        }

        private static void WriteParityReport(Transform root, string folder)
        {
            Transform rotor = root.Find("RotorDynamic");
            Transform body = root.Find("RotorDynamic/Rotor_Root/Rotor_Body");
            Transform capTop = root.Find("HubStatic/TopCap/Cap_Top");
            Transform capBottom = root.Find("HubStatic/BottomCap/Cap_Bottom");
            Transform hubCore = root.Find("HubStatic/Hub_Core");
            var lines = new List<string> { "{", "  \"gate\": \"11-unity-parity\",", "  \"revision\": 2,", "  \"scene\": \"" + SpinnerEnvironmentCatalog.MetalScenePath + "\"," };
            void Part(string label, Transform t, bool last)
            {
                if (t == null)
                {
                    lines.Add($"  \"{label}\": null{(last ? string.Empty : ",")}");
                    return;
                }
                MeshRenderer renderer = t.GetComponent<MeshRenderer>();
                MeshFilter filter = t.GetComponent<MeshFilter>();
                Bounds b = renderer != null ? renderer.bounds : new Bounds(t.position, Vector3.zero);
                string materials = renderer != null ? string.Join(",", renderer.sharedMaterials.Select(m => "\"" + (m != null ? m.name : "null") + "\"")) : string.Empty;
                string mesh = filter != null && filter.sharedMesh != null ? AssetDatabase.GetAssetPath(filter.sharedMesh) : string.Empty;
                int tris = filter != null && filter.sharedMesh != null ? filter.sharedMesh.triangles.Length / 3 : 0;
                lines.Add($"  \"{label}\": {{\"path\": \"{HierarchyPath(t, root)}\", \"rotates\": {(t.IsChildOf(rotor) ? "true" : "false")}, \"rendererEnabled\": {(renderer != null && renderer.enabled ? "true" : "false")}, \"materials\": [{materials}], \"mesh\": \"{mesh}\", \"triangles\": {tris}, \"worldBoundsMin\": [{b.min.x:F5}, {b.min.y:F5}, {b.min.z:F5}], \"worldBoundsMax\": [{b.max.x:F5}, {b.max.y:F5}, {b.max.z:F5}], \"localPosition\": [{t.localPosition.x:F5}, {t.localPosition.y:F5}, {t.localPosition.z:F5}]}}{(last ? string.Empty : ",")}");
            }
            Part("rotorBody", body, false);
            Part("capTop", capTop, false);
            Part("capBottom", capBottom, false);
            Part("hubCore", hubCore, false);
            RotorRigidbodyController controller = rotor != null ? rotor.GetComponent<RotorRigidbodyController>() : null;
            Rigidbody rigidbody = rotor != null ? rotor.GetComponent<Rigidbody>() : null;
            lines.Add($"  \"rotorController\": {(controller != null ? "true" : "false")},");
            lines.Add($"  \"rotorAngularVelocityAtLoad\": {(rigidbody != null ? rigidbody.angularVelocity.magnitude : -1f):F6},");
            lines.Add($"  \"rotorYaw180Applied\": {(body != null && Mathf.Abs(Mathf.DeltaAngle(body.parent.localEulerAngles.y, 180f)) < 0.5f ? "true" : "false")},");
            lines.Add($"  \"rotorBoundsSizeM\": [{(body != null ? body.GetComponent<MeshRenderer>().bounds.size.x : 0f):F5}, {(body != null ? body.GetComponent<MeshRenderer>().bounds.size.y : 0f):F5}, {(body != null ? body.GetComponent<MeshRenderer>().bounds.size.z : 0f):F5}],");
            lines.Add($"  \"neutralCamera\": {{\"topOrthoWidthM\": {2.3f * RadiusM:F5}, \"heroPositionM\": [{-1.2f * RadiusM:F5}, {1.5f * RadiusM:F5}, {-1.6f * RadiusM:F5}], \"heroFocalLengthMm\": 50, \"blenderHeroPositionR\": [1.2, -1.6, 1.5]}}");
            lines.Add("}");
            File.WriteAllText(Path.Combine(folder, "unity-import-parity-report.json"), string.Join("\n", lines) + "\n");
        }

        private static string HierarchyPath(Transform t, Transform root)
        {
            var parts = new List<string>();
            while (t != null && t != root)
            {
                parts.Insert(0, t.name);
                t = t.parent;
            }
            return string.Join("/", parts);
        }

        // ------------------------------------------------------------------ helpers
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

        private static void ApplyPose(Camera camera, Bounds bounds, Vector3 focus, PreviewPose pose, float widthFraction, float heightFraction)
        {
            Vector3 backward = Quaternion.Euler(pose.Pitch, pose.Yaw, 0f) * Vector3.back;
            float distance = ProductCameraFraming.RequiredDistance(camera, bounds, backward, widthFraction, heightFraction, focusPoint: focus);
            camera.transform.position = focus + backward * distance;
            camera.transform.LookAt(focus, Vector3.up);
        }

        private static void Render(Camera camera, RenderTexture target, Texture2D image, string path, bool warmup = false)
        {
            RenderTexture.active = target;
            GL.Clear(true, true, camera.backgroundColor);
            var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest { destination = target };
            UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
            if (warmup)
            {
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
            }
            RenderTexture.active = target;
            image.ReadPixels(new Rect(0f, 0f, image.width, image.height), 0, 0, false);
            image.Apply(false, false);
            File.WriteAllBytes(path, image.EncodeToPNG());
        }
    }
}
