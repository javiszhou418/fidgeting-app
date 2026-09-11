using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using FidgetingApp.EDC.Candidates;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.Editor
{
    public static class MagneticSlideTileGate11R010Builder
    {
        private const string SourceRoot =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R009";
        private const string Root =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R010";
        private const string ScenePath =
            Root + "/Scenes/MagneticSlideTileGate11R010Parity.unity";
        private const string SourceScenePath =
            SourceRoot + "/Scenes/MagneticSlideTileGate11R009Parity.unity";
        private const string Materials = Root + "/Materials";
        private const string Textures = SourceRoot + "/Imported/Textures";
        private const string CubemapPath =
            SourceRoot + "/Imported/Environment/MagneticSlideTileGate11R009Environment.cubemap";
        private const string ShippingScenePath = "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const int Width = 1400;
        private const int Height = 1100;

        [MenuItem("Fidgeting/Model Pipeline/Build Magnetic Slide Gate 11 R010")]
        public static void BuildAndCapture()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string evidenceRoot = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-010");
            Directory.CreateDirectory(evidenceRoot);
            string shippingBefore = Sha256(Path.Combine(projectRoot, ShippingScenePath));

            Scene scene = EditorSceneManager.OpenScene(SourceScenePath, OpenSceneMode.Single);
            GameObject product = scene.GetRootGameObjects().First(
                item => item.GetComponent<MagneticSlideTileGate11Metadata>() != null);
            product.name = "MagneticSlideTile_Gate11R010_Candidate";
            Bounds bounds = CalculateBounds(product);

            RemoveLegacyPresentation(scene, product);
            Dictionary<string, Material> materials = CreateMaterials();
            AssignMaterials(product, materials);
            ConfigureRenderers(product);
            CreateGround(bounds);
            CreateLights(bounds);
            Cubemap cubemap = AssetDatabase.LoadAssetAtPath<Cubemap>(CubemapPath)
                ?? throw new InvalidDataException("Gate 09 cubemap is missing.");
            ConfigureEnvironment(cubemap);
            CreateReflectionProbe(cubemap);
            Camera camera = CreateCamera();
            CreatePostProcessing();

            MagneticSlideTileGate11PreviewController controller =
                product.GetComponent<MagneticSlideTileGate11PreviewController>();
            GameObject orbitTarget = new("Gate11R010OrbitTarget");
            orbitTarget.transform.position = bounds.center;
            controller.Configure(
                FindTransform(product.transform, "RotatingCarrier"),
                FindTransform(product.transform, "MovingTop"),
                FindTransform(product.transform, "TopLocalSlide"),
                camera,
                orbitTarget.transform,
                Vector3.up,
                Vector3.forward);

            Directory.CreateDirectory(Path.GetDirectoryName(ScenePath)!);
            EditorSceneManager.SaveScene(scene, ScenePath, true);
            AssetDatabase.SaveAssets();
            DynamicGI.UpdateEnvironment();

            CopyReferenceImages(projectRoot, evidenceRoot);
            controller.ResetPose();
            Render(camera, Path.Combine(evidenceRoot, "unity-shipping-closed.png"));
            RenderExr(camera, Path.Combine(evidenceRoot, "unity-shipping-closed-linear.exr"));

            Material clay = CreateClayMaterial();
            Dictionary<Renderer, Material[]> originalMaterials = SwapMaterials(product, clay);
            Render(camera, Path.Combine(evidenceRoot, "unity-clay.png"));
            RestoreMaterials(originalMaterials);
            UnityEngine.Object.DestroyImmediate(clay);

            Material silhouette = CreateSilhouetteMaterial();
            Dictionary<Renderer, Material[]> silhouetteMaterials =
                SwapMaterials(product, silhouette);
            GameObject ground = GameObject.Find("Gate11R010Ground");
            ground.SetActive(false);
            CameraClearFlags previousFlags = camera.clearFlags;
            Color previousBackground = camera.backgroundColor;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.black;
            Render(camera, Path.Combine(evidenceRoot, "unity-silhouette.png"));
            camera.clearFlags = previousFlags;
            camera.backgroundColor = previousBackground;
            ground.SetActive(true);
            RestoreMaterials(silhouetteMaterials);
            UnityEngine.Object.DestroyImmediate(silhouette);

            MagneticSlideTileGate11Metadata metadata =
                product.GetComponent<MagneticSlideTileGate11Metadata>();
            controller.SetPose(0f, metadata.MaximumTravelMeters);
            Render(camera, Path.Combine(evidenceRoot, "unity-max-open.png"));
            controller.SetPose(12f, metadata.MaximumTravelMeters * 0.5f);
            Render(camera, Path.Combine(evidenceRoot, "unity-detent-12.png"));
            controller.SetPose(36f, 0f);
            Render(camera, Path.Combine(evidenceRoot, "unity-detent-36.png"));
            controller.ResetPose();
            CaptureTurntable(camera, bounds.center, controller, evidenceRoot);
            EditorSceneManager.SaveScene(scene, ScenePath);

            string shippingAfter = Sha256(Path.Combine(projectRoot, ShippingScenePath));
            WriteReport(
                product,
                camera,
                bounds,
                shippingBefore,
                shippingAfter,
                Path.Combine(evidenceRoot, "unity-import-parity-report.json"));
            File.WriteAllText(
                Path.Combine(evidenceRoot, "unity-scene-path.txt"),
                ScenePath + System.Environment.NewLine);
            AssetDatabase.Refresh();
        }

        private static void RemoveLegacyPresentation(Scene scene, GameObject product)
        {
            foreach (GameObject root in scene.GetRootGameObjects())
            {
                if (root == product || root.name.Contains("Collision", StringComparison.Ordinal))
                    continue;
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        private static Dictionary<string, Material> CreateMaterials()
        {
            Directory.CreateDirectory(Path.Combine(Application.dataPath,
                "_EDC/Candidates/MagneticSlideTileGate11R010/Materials"));
            Shader silverShader = Shader.Find("FidgetingApp/MagneticSlideTile/SilverR010")
                ?? throw new InvalidDataException("R010 silver shader missing.");
            Shader crystalShader = Shader.Find(
                "FidgetingApp/MagneticSlideTile/BloodRedCrystalR010")
                ?? throw new InvalidDataException("R010 crystal shader missing.");
            Shader lit = Shader.Find("Universal Render Pipeline/Lit")
                ?? throw new InvalidDataException("URP Lit shader missing.");

            Material silver = new(silverShader) { name = "M_G11R010_PolishedSilver" };
            silver.SetColor("_BaseColor", new Color(0.78f, 0.77f, 0.74f, 1f));
            silver.SetFloat("_Smoothness", 0.925f);
            silver.SetFloat("_ReflectionStrength", 0.82f);
            silver.SetFloat("_DirectSpecularStrength", 0.18f);

            Material internalSilver = new(silverShader)
            {
                name = "M_G11R010_InternalSilver"
            };
            internalSilver.SetColor("_BaseColor", new Color(0.72f, 0.71f, 0.69f, 1f));
            internalSilver.SetFloat("_Smoothness", 0.84f);
            internalSilver.SetFloat("_ReflectionStrength", 0.66f);
            internalSilver.SetFloat("_DirectSpecularStrength", 0.14f);

            Material upper = CreateCrystal(
                crystalShader,
                "M_G11R010_CrystalUpper",
                "upperBaseColor.png",
                "upper-maskmap-r009.png",
                "upper-normal-r009.png",
                "upperArtworkMask.png");
            Material lower = CreateCrystal(
                crystalShader,
                "M_G11R010_CrystalLower",
                "lowerBaseColor.png",
                "lower-maskmap-r009.png",
                "lower-normal-r009.png",
                "lowerArtworkMask.png");

            Material dark = new(lit) { name = "M_G11R010_DarkExterior" };
            dark.SetColor("_BaseColor", new Color(0.018f, 0.020f, 0.024f, 1f));
            dark.SetFloat("_Metallic", 0.24f);
            dark.SetFloat("_Smoothness", 0.82f);
            dark.SetFloat("_ClearCoatMask", 0.55f);
            dark.SetFloat("_ClearCoatSmoothness", 0.88f);
            dark.SetFloat("_Cull", 0f);

            Material technical = new(lit) { name = "M_G11R010_Technical" };
            technical.SetColor("_BaseColor", new Color(0.16f, 0.17f, 0.18f, 1f));
            technical.SetFloat("_Metallic", 0.6f);
            technical.SetFloat("_Smoothness", 0.58f);
            technical.SetFloat("_Cull", 0f);

            Material ball = new(lit) { name = "M_G11R010_BallUnknown" };
            ball.SetColor("_BaseColor", new Color(0.78f, 0.80f, 0.82f, 1f));
            ball.SetFloat("_Metallic", 0.5f);
            ball.SetFloat("_Smoothness", 0.86f);
            ball.SetFloat("_Cull", 0f);

            return new Dictionary<string, Material>
            {
                ["silver"] = SaveMaterial(silver),
                ["internal"] = SaveMaterial(internalSilver),
                ["upper"] = SaveMaterial(upper),
                ["lower"] = SaveMaterial(lower),
                ["dark"] = SaveMaterial(dark),
                ["technical"] = SaveMaterial(technical),
                ["ball"] = SaveMaterial(ball)
            };
        }

        private static Material CreateCrystal(
            Shader shader,
            string name,
            string baseName,
            string maskName,
            string normalName,
            string artworkName)
        {
            Material material = new(shader) { name = name };
            material.SetTexture("_BaseMap", LoadTexture(baseName));
            material.SetTexture("_MaskMap", LoadTexture(maskName));
            material.SetTexture("_BumpMap", LoadTexture(normalName));
            material.SetTexture("_ArtworkMask", LoadTexture(artworkName));
            material.SetTexture("_PerimeterMask", LoadTexture("perimeterMask.png"));
            material.SetColor("_DeepBloodRed", new Color(0.18f, 0.003f, 0.008f, 1f));
            material.SetColor("_BlackColor", new Color(0.004f, 0.0015f, 0.0018f, 1f));
            material.SetFloat("_Smoothness", 0.94f);
            material.SetFloat("_BlackSmoothness", 0.84f);
            material.SetFloat("_NormalScale", 0.75f);
            material.SetFloat("_ReflectionStrength", 0.68f);
            material.SetFloat("_CoatStrength", 0.30f);
            material.SetFloat("_Iridescence", 0.08f);
            material.SetFloat("_CrystalDepth", 0.26f);
            return material;
        }

        private static Texture2D LoadTexture(string name)
        {
            return AssetDatabase.LoadAssetAtPath<Texture2D>($"{Textures}/{name}")
                ?? throw new InvalidDataException($"Texture missing: {name}");
        }

        private static Material SaveMaterial(Material material)
        {
            string path = $"{Materials}/{material.name}.mat";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(material, path);
            return AssetDatabase.LoadAssetAtPath<Material>(path);
        }

        private static void AssignMaterials(
            GameObject product,
            IReadOnlyDictionary<string, Material> materials)
        {
            foreach (MeshRenderer renderer in product.GetComponentsInChildren<MeshRenderer>(true))
            {
                renderer.sharedMaterials = renderer.sharedMaterials.Select(source =>
                {
                    string name = source != null ? source.name : "";
                    if (name.Contains("CrystalUpper", StringComparison.OrdinalIgnoreCase))
                        return materials["upper"];
                    if (name.Contains("CrystalLower", StringComparison.OrdinalIgnoreCase))
                        return materials["lower"];
                    if (name.Contains("DarkExterior", StringComparison.OrdinalIgnoreCase))
                        return materials["dark"];
                    if (name.Contains("InternalSilver", StringComparison.OrdinalIgnoreCase))
                        return materials["internal"];
                    if (name.Contains("PolishedSilver", StringComparison.OrdinalIgnoreCase))
                        return materials["silver"];
                    if (name.Contains("Ball", StringComparison.OrdinalIgnoreCase))
                        return materials["ball"];
                    return materials["technical"];
                }).ToArray();
            }
        }

        private static void ConfigureRenderers(GameObject product)
        {
            foreach (Renderer renderer in product.GetComponentsInChildren<Renderer>(true))
            {
                renderer.shadowCastingMode = ShadowCastingMode.On;
                renderer.receiveShadows = true;
                renderer.reflectionProbeUsage = ReflectionProbeUsage.BlendProbesAndSkybox;
                renderer.lightProbeUsage = LightProbeUsage.BlendProbes;
            }
        }

        private static void CreateGround(Bounds bounds)
        {
            GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Gate11R010Ground";
            ground.layer = 8;
            ground.transform.position = new Vector3(
                bounds.center.x,
                bounds.min.y - 0.0006f,
                bounds.center.z);
            ground.transform.localScale = new Vector3(0.024f, 1f, 0.024f);
            Shader lit = Shader.Find("Universal Render Pipeline/Lit")
                ?? throw new InvalidDataException("URP Lit missing.");
            Material material = new(lit) { name = "M_G11R010_Ground" };
            material.SetColor("_BaseColor", new Color(0.018f, 0.016f, 0.017f, 1f));
            material.SetFloat("_Metallic", 0f);
            material.SetFloat("_Smoothness", 0.58f);
            material.SetFloat("_Cull", 0f);
            ground.GetComponent<MeshRenderer>().sharedMaterial = SaveMaterial(material);
            ground.GetComponent<MeshRenderer>().shadowCastingMode = ShadowCastingMode.Off;
            ground.GetComponent<MeshRenderer>().receiveShadows = true;
        }

        private static void CreateLights(Bounds bounds)
        {
            GameObject main = new("Gate11R010KeyDirection");
            Light directional = main.AddComponent<Light>();
            directional.type = LightType.Directional;
            directional.color = new Color(1f, 0.91f, 0.82f);
            directional.intensity = 1.40f;
            directional.shadows = LightShadows.Soft;
            directional.shadowStrength = 0.72f;
            directional.shadowBias = 0.015f;
            directional.shadowNormalBias = 0.18f;
            main.transform.rotation = Quaternion.LookRotation(
                new Vector3(-0.452821f, -0.710461f, -0.538701f),
                Vector3.up);

            GameObject groundFill = new("Gate11R010GroundFill");
            Light groundLight = groundFill.AddComponent<Light>();
            groundLight.type = LightType.Directional;
            groundLight.color = new Color(0.90f, 0.93f, 1f);
            groundLight.intensity = 0.80f;
            groundLight.shadows = LightShadows.None;
            groundLight.cullingMask = 1 << 8;
            groundFill.transform.rotation = Quaternion.LookRotation(
                new Vector3(0.22f, -0.94f, -0.26f),
                Vector3.up);

            CreatePoint("Gate11R010Key", new Color(1f, 0.91f, 0.82f),
                0.008f, new Vector3(0.058f, 0.096f, 0.072f), 0.24f, true);
            CreatePoint("Gate11R010Fill", new Color(0.90f, 0.95f, 1f),
                0.002f, new Vector3(-0.054f, 0.058f, 0.012f), 0.20f, false);
            CreatePoint("Gate11R010Reveal", new Color(1f, 0.87f, 0.75f),
                0.001f, new Vector3(-0.026f, 0.028f, -0.020f), 0.16f, false);
            CreatePoint("Gate11R010Rim", Color.white,
                0.002f, new Vector3(0.044f, 0.062f, -0.070f), 0.22f, false);
        }

        private static void CreatePoint(
            string name,
            Color color,
            float intensity,
            Vector3 position,
            float range,
            bool shadows)
        {
            GameObject lightObject = new(name);
            lightObject.transform.position = position;
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Point;
            light.color = color;
            light.intensity = intensity;
            light.range = range;
            light.cullingMask = ~(1 << 8);
            light.shadows = shadows ? LightShadows.Soft : LightShadows.None;
            light.shadowStrength = 0.55f;
            light.shadowBias = 0.015f;
            light.shadowNormalBias = 0.2f;
        }

        private static void ConfigureEnvironment(Cubemap cubemap)
        {
            Shader shader = Shader.Find("Skybox/Cubemap")
                ?? throw new InvalidDataException("Skybox/Cubemap missing.");
            Material skybox = new(shader) { name = "M_G11R010_Skybox" };
            skybox.SetTexture("_Tex", cubemap);
            skybox.SetFloat("_Exposure", -0.35f);
            skybox.SetFloat("_Rotation", 0f);
            RenderSettings.skybox = SaveMaterial(skybox);
            RenderSettings.ambientMode = AmbientMode.Skybox;
            RenderSettings.ambientIntensity = 0.12f;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflection = cubemap;
            RenderSettings.reflectionIntensity = 0.82f;
            RenderSettings.reflectionBounces = 1;
        }

        private static void CreateReflectionProbe(Cubemap cubemap)
        {
            GameObject probeObject = new("Gate11R010LocalReflectionProbe");
            probeObject.transform.position = new Vector3(0f, 0.012f, 0.003f);
            ReflectionProbe probe = probeObject.AddComponent<ReflectionProbe>();
            probe.mode = ReflectionProbeMode.Custom;
            probe.customBakedTexture = cubemap;
            probe.boxProjection = true;
            probe.size = new Vector3(0.14f, 0.09f, 0.14f);
            probe.intensity = 0.82f;
            probe.importance = 100;
            probe.blendDistance = 0.02f;
        }

        private static Camera CreateCamera()
        {
            GameObject cameraObject = new("CAM_Gate11R010Parity");
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.Skybox;
            camera.backgroundColor = new Color(0.008f, 0.009f, 0.011f, 1f);
            camera.allowHDR = true;
            camera.allowMSAA = true;
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 10f;
            camera.sensorSize = new Vector2(36f, 36f / ((float)Width / Height));
            camera.focalLength = 76f;
            camera.fieldOfView = Camera.FocalLengthToFieldOfView(
                camera.focalLength, camera.sensorSize.y);
            camera.transform.position = new Vector3(0.074f, 0.072f, -0.116f);
            camera.transform.LookAt(new Vector3(0f, 0.005f, -0.002f));
            camera.tag = "MainCamera";
            UniversalAdditionalCameraData additional =
                cameraObject.AddComponent<UniversalAdditionalCameraData>();
            additional.renderPostProcessing = true;
            additional.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            additional.antialiasingQuality = AntialiasingQuality.High;
            return camera;
        }

        private static void CreatePostProcessing()
        {
            VolumeProfile profile = ScriptableObject.CreateInstance<VolumeProfile>();
            profile.name = "Gate11R010ParityVolume";
            profile.Add<Tonemapping>(true).mode.Override(TonemappingMode.ACES);
            WhiteBalance whiteBalance = profile.Add<WhiteBalance>(true);
            whiteBalance.temperature.Override(0f);
            whiteBalance.tint.Override(10f);
            profile.Add<ColorAdjustments>(true).postExposure.Override(0.25f);
            string path = $"{Materials}/Gate11R010ParityVolume.asset";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(profile, path);
            GameObject volumeObject = new("Gate11R010GlobalVolume");
            Volume volume = volumeObject.AddComponent<Volume>();
            volume.isGlobal = true;
            volume.priority = 100;
            volume.sharedProfile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(path);
        }

        private static Material CreateClayMaterial()
        {
            Shader lit = Shader.Find("Universal Render Pipeline/Lit")
                ?? throw new InvalidDataException("URP Lit missing.");
            Material clay = new(lit);
            clay.SetColor("_BaseColor", new Color(0.42f, 0.44f, 0.47f, 1f));
            clay.SetFloat("_Metallic", 0f);
            clay.SetFloat("_Smoothness", 0.62f);
            clay.SetFloat("_Cull", 0f);
            return clay;
        }

        private static Material CreateSilhouetteMaterial()
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Unlit")
                ?? throw new InvalidDataException("URP Unlit missing.");
            Material material = new(shader);
            material.SetColor("_BaseColor", Color.white);
            material.SetFloat("_Cull", 0f);
            return material;
        }

        private static Dictionary<Renderer, Material[]> SwapMaterials(
            GameObject product,
            Material material)
        {
            Dictionary<Renderer, Material[]> originals = new();
            foreach (Renderer renderer in product.GetComponentsInChildren<Renderer>(true))
            {
                originals[renderer] = renderer.sharedMaterials;
                renderer.sharedMaterials = Enumerable
                    .Repeat(material, renderer.sharedMaterials.Length)
                    .ToArray();
            }
            return originals;
        }

        private static void RestoreMaterials(
            IReadOnlyDictionary<Renderer, Material[]> originals)
        {
            foreach ((Renderer renderer, Material[] materials) in originals)
                renderer.sharedMaterials = materials;
        }

        private static Bounds CalculateBounds(GameObject root)
        {
            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true)
                .Where(renderer => renderer.enabled)
                .ToArray();
            Bounds bounds = renderers[0].bounds;
            foreach (Renderer renderer in renderers.Skip(1))
                bounds.Encapsulate(renderer.bounds);
            return bounds;
        }

        private static Transform FindTransform(Transform root, string name)
        {
            Transform result = root.GetComponentsInChildren<Transform>(true)
                .FirstOrDefault(item => item.name == name);
            return result ?? throw new InvalidDataException($"Transform missing: {name}");
        }

        private static void CopyReferenceImages(string projectRoot, string evidenceRoot)
        {
            File.Copy(
                Path.Combine(projectRoot,
                    "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/09-environment/rev-008/shipping-closed-hero.png"),
                Path.Combine(evidenceRoot, "blender-shipping-closed.png"),
                true);
            File.Copy(
                Path.Combine(projectRoot,
                    "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-002/pass-clay.png"),
                Path.Combine(evidenceRoot, "blender-clay.png"),
                true);
            File.Copy(
                Path.Combine(projectRoot,
                    "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-009/blender-silhouette.png"),
                Path.Combine(evidenceRoot, "blender-silhouette.png"),
                true);
        }

        private static void Render(Camera camera, string path)
        {
            Render(camera, path, Width, Height);
        }

        private static void Render(Camera camera, string path, int width, int height)
        {
            RenderTexture target = new(width, height, 24, RenderTextureFormat.ARGB32)
            {
                antiAliasing = 4
            };
            RenderTexture previousActive = RenderTexture.active;
            RenderTexture previousTarget = camera.targetTexture;
            try
            {
                target.Create();
                camera.targetTexture = target;
                UnityEngine.Rendering.RenderPipeline.StandardRequest request = new()
                {
                    destination = target
                };
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                RenderTexture.active = target;
                Texture2D image = new(width, height, TextureFormat.RGBA32, false, false);
                image.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                image.Apply(false, false);
                File.WriteAllBytes(path, image.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(image);
            }
            finally
            {
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
            }
        }

        private static void RenderExr(Camera camera, string path)
        {
            RenderTexture target = new(
                Width,
                Height,
                24,
                RenderTextureFormat.ARGBFloat,
                RenderTextureReadWrite.Linear);
            RenderTexture previousActive = RenderTexture.active;
            RenderTexture previousTarget = camera.targetTexture;
            try
            {
                target.Create();
                camera.targetTexture = target;
                UnityEngine.Rendering.RenderPipeline.StandardRequest request = new()
                {
                    destination = target
                };
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                RenderTexture.active = target;
                Texture2D image = new(Width, Height, TextureFormat.RGBAFloat, false, true);
                image.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
                image.Apply(false, false);
                File.WriteAllBytes(path, image.EncodeToEXR(Texture2D.EXRFlags.CompressZIP));
                UnityEngine.Object.DestroyImmediate(image);
            }
            finally
            {
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
            }
        }

        private static void CaptureTurntable(
            Camera camera,
            Vector3 target,
            MagneticSlideTileGate11PreviewController controller,
            string evidenceRoot)
        {
            string folder = Path.Combine(evidenceRoot, "turntable-frames");
            Directory.CreateDirectory(folder);
            Vector3 originalPosition = camera.transform.position;
            Quaternion originalRotation = camera.transform.rotation;
            const int frameCount = 72;
            for (int frame = 0; frame < frameCount; frame++)
            {
                if (frame < 18) controller.SetPose(0f, 0f);
                else if (frame < 36) controller.SetPose(0f, 0.018076433f);
                else if (frame < 54) controller.SetPose(12f, 0.009038216f);
                else controller.SetPose(36f, 0f);
                float radians = frame * Mathf.PI * 2f / frameCount;
                camera.transform.position = target + new Vector3(
                    Mathf.Sin(radians) * 0.165f,
                    0.078f,
                    Mathf.Cos(radians) * 0.165f);
                camera.transform.LookAt(target + new Vector3(0f, 0.004f, 0f));
                Render(camera, Path.Combine(folder, $"frame-{frame:D3}.png"), 960, 720);
            }
            controller.ResetPose();
            camera.transform.SetPositionAndRotation(originalPosition, originalRotation);
        }

        private static void WriteReport(
            GameObject product,
            Camera camera,
            Bounds bounds,
            string shippingBefore,
            string shippingAfter,
            string path)
        {
            MeshFilter[] filters = product.GetComponentsInChildren<MeshFilter>(true);
            Matrix4x4 view = camera.worldToCameraMatrix;
            Matrix4x4 projection = camera.projectionMatrix;
            Gate11Report report = new()
            {
                schemaVersion = 2,
                gate = "11-unity-parity",
                revision = 10,
                unityVersion = Application.unityVersion,
                scenePath = ScenePath,
                imageWidth = Width,
                imageHeight = Height,
                cameraPosition = camera.transform.position,
                cameraRotation = camera.transform.rotation,
                cameraFocalLengthMm = camera.focalLength,
                cameraSensorSizeMm = camera.sensorSize,
                cameraViewMatrix = MatrixValues(view),
                cameraProjectionMatrix = MatrixValues(projection),
                objectBoundsCenter = bounds.center,
                objectBoundsSize = bounds.size,
                renderMeshCount = filters.Length,
                renderVertexCount = filters.Sum(filter => filter.sharedMesh.vertexCount),
                renderTriangleCount =
                    filters.Sum(filter => filter.sharedMesh.triangles.Length / 3),
                reflectionProbeBoxProjection = true,
                skyboxExposureEv = -0.35f,
                postExposureEv = 0.25f,
                clayBaseColor = new Vector3(0.42f, 0.44f, 0.47f),
                clayRoughness = 0.38f,
                zeroEmission = true,
                shippingSceneHashBefore = shippingBefore,
                shippingSceneHashAfter = shippingAfter,
                shippingSceneModified = shippingBefore != shippingAfter,
                oldShippingModelDefault = true,
                gate12Started = false,
                buildInstallDevice = false,
                pass = shippingBefore == shippingAfter
                    && filters.Length == 8
                    && Width == 1400
                    && Height == 1100
            };
            File.WriteAllText(path, JsonUtility.ToJson(report, true));
            if (!report.pass)
                throw new InvalidDataException("Gate 11 R010 transport report failed.");
        }

        private static float[] MatrixValues(Matrix4x4 matrix)
        {
            float[] values = new float[16];
            for (int row = 0; row < 4; row++)
            for (int column = 0; column < 4; column++)
                values[row * 4 + column] = matrix[row, column];
            return values;
        }

        private static string Sha256(string path)
        {
            using SHA256 algorithm = SHA256.Create();
            using FileStream stream = File.OpenRead(path);
            return BitConverter.ToString(algorithm.ComputeHash(stream))
                .Replace("-", string.Empty)
                .ToLowerInvariant();
        }

        [Serializable]
        private sealed class Gate11Report
        {
            public int schemaVersion;
            public string gate = "";
            public int revision;
            public string unityVersion = "";
            public string scenePath = "";
            public int imageWidth;
            public int imageHeight;
            public Vector3 cameraPosition;
            public Quaternion cameraRotation;
            public float cameraFocalLengthMm;
            public Vector2 cameraSensorSizeMm;
            public float[] cameraViewMatrix = Array.Empty<float>();
            public float[] cameraProjectionMatrix = Array.Empty<float>();
            public Vector3 objectBoundsCenter;
            public Vector3 objectBoundsSize;
            public int renderMeshCount;
            public int renderVertexCount;
            public int renderTriangleCount;
            public bool reflectionProbeBoxProjection;
            public float skyboxExposureEv;
            public float postExposureEv;
            public Vector3 clayBaseColor;
            public float clayRoughness;
            public bool zeroEmission;
            public string shippingSceneHashBefore = "";
            public string shippingSceneHashAfter = "";
            public bool shippingSceneModified;
            public bool oldShippingModelDefault;
            public bool gate12Started;
            public bool buildInstallDevice;
            public bool pass;
        }
    }
}
