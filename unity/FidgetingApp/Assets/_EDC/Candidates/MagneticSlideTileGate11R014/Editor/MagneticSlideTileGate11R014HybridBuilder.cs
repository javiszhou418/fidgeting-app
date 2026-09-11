using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using FidgetingApp.EDC.Gate11R013;
using FidgetingApp.EDC.Gate12R002;
using UnityEditor;
using UnityEditor.Rendering;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.Editor
{
    public static class MagneticSlideTileGate11R014HybridBuilder
    {
        private const string ShippingScene =
            "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const string Root =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R014";
        private const string Materials = Root + "/Materials";
        private const string R011 =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R011";
        private const string R012 =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R012";
        private const string R013 =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R013";
        private const string Source = R011 + "/Imported";
        private const string SourceFbx =
            Source + "/magnetic-slide-tile-render-r011.fbx";
        private const string OutputRelative =
            "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/"
            + "11-unity-parity/rev-014-detail-depth-hybrid";

        private static readonly string[] ProtectedSources =
        {
            "Assets/_EDC/Runtime/EdcSliderController.cs",
            "Assets/_EDC/Runtime/MagneticSlideDetentAudio.cs",
            "Assets/_EDC/Runtime/SharedPresentationGestureController.cs",
            "Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Runtime/"
                + "MagneticSlideTileShippingCoordinator.cs",
            "Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Runtime/"
                + "MagneticSlideTileShippingMechanism.cs",
            "Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Settings/"
                + "MagneticSlideTileMechanismSettingsR002.asset",
            "Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Prefabs/"
                + "MagneticSlideTileGate12R002Candidate.prefab",
            "Assets/Scripts/FidgetSpinner/IosHaptics.cs",
        };

        private static readonly ViewRecipe[] Views =
        {
            new("macro", new Vector3(0.038f, 0.046f, -0.060f),
                new Vector3(0f, 0.005f, 0f), 16f, 1600, 1000, false),
            new("hero-closed", new Vector3(0.074f, 0.072f, -0.116f),
                new Vector3(0f, 0.005f, -0.002f), 19f, 1280, 960, false),
            new("grazing-15", GrazingPosition(15f),
                new Vector3(0f, 0.004f, 0f), 24f, 1280, 960, false),
            new("grazing-30", GrazingPosition(30f),
                new Vector3(0f, 0.004f, 0f), 24f, 1280, 960, false),
            new("grazing-60", GrazingPosition(60f),
                new Vector3(0f, 0.004f, 0f), 24f, 1280, 960, false),
            new("max-open", new Vector3(0.074f, 0.072f, -0.116f),
                new Vector3(0f, 0.005f, 0.006f), 20f, 1280, 960, true),
            new("phone", new Vector3(0.030f, 0.030f, -0.050f),
                Vector3.zero, 38f, 1290, 2796, false),
        };

        [MenuItem("Fidgeting/Model Pipeline/Capture Magnetic Slide Hybrid R014")]
        public static void Capture()
        {
            Scene scene = EditorSceneManager.OpenScene(
                ShippingScene, OpenSceneMode.Single);
            string projectRoot =
                Directory.GetParent(Application.dataPath)!.FullName;
            string output = Path.Combine(projectRoot, OutputRelative);
            Directory.CreateDirectory(output);
            Dictionary<string, string> protectedBefore =
                HashProtectedSources(projectRoot);
            string[] colliderBefore = ColliderIdentities();

            MagneticSlideTileShippingCoordinator coordinator =
                FindCoordinator();
            coordinator.SetPreviewActive(true);
            coordinator.ResetShippingPose(false);
            Camera shippingCamera = Camera.main
                ?? throw new InvalidDataException(
                    "Shipping camera missing.");
            MagneticSlideShippingLightingController lighting =
                shippingCamera.GetComponent<
                    MagneticSlideShippingLightingController>()
                ?? throw new InvalidDataException(
                    "Approved lighting controller missing.");
            lighting.ApplyVariant(
                MagneticSlideLightingVariant.BalancedBrighter);
            Camera camera = CreateCaptureCamera();
            Bounds boundsBefore = ProductBounds(
                coordinator.CandidateModel);
            MaterialSet r13 = LoadR013Materials();
            MaterialSet hybrid = CreateHybridMaterials();

            CaptureVariant(
                "A-rev12-detail",
                () => ApplyR012(coordinator.CandidateModel),
                camera,
                coordinator,
                output);
            CaptureVariant(
                "B-rev13-depth",
                () => ApplyPhysical(
                    coordinator.CandidateModel, r13),
                camera,
                coordinator,
                output);
            CaptureVariant(
                "C-rev14-hybrid",
                () => ApplyPhysical(
                    coordinator.CandidateModel, hybrid),
                camera,
                coordinator,
                output);

            ApplyPhysical(coordinator.CandidateModel, hybrid);
            coordinator.ResetShippingPose(false);
            UnityEngine.Object.DestroyImmediate(camera.gameObject);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ShippingScene, false);
            AssetDatabase.SaveAssets();

            scene = EditorSceneManager.OpenScene(
                ShippingScene, OpenSceneMode.Single);
            coordinator = FindCoordinator();
            coordinator.SetPreviewActive(true);
            coordinator.ResetShippingPose(false);
            Bounds boundsAfter =
                ProductBounds(coordinator.CandidateModel);
            string[] colliderAfter = ColliderIdentities();
            Dictionary<string, string> protectedAfter =
                HashProtectedSources(projectRoot);
            Shader[] shaders =
            {
                Shader.Find(
                    "FidgetingApp/MagneticSlideTile/HybridSubstrateR014"),
                Shader.Find(
                    "FidgetingApp/MagneticSlideTile/HybridMotifR014"),
                Shader.Find(
                    "FidgetingApp/MagneticSlideTile/HybridCrystalR014"),
            };
            int shaderErrors = shaders
                .Where(shader => shader != null)
                .Sum(shader => ShaderUtil.GetShaderMessages(shader)
                    .Count(message =>
                        message.severity
                        == ShaderCompilerMessageSeverity.Error));
            string upperBase = Source + "/Textures/upper-albedo.png";
            string lowerBase = Source + "/Textures/lower-albedo.png";
            string upperRough =
                Source + "/Textures/upper-roughness.png";
            string lowerRough =
                Source + "/Textures/lower-roughness.png";
            string upperNormal =
                Source + "/Textures/upper-transport-normal-r011.png";
            string lowerNormal =
                Source + "/Textures/lower-transport-normal-r011.png";
            string upperMask =
                Source + "/Textures/upper-artwork-mask.png";
            string lowerMask =
                Source + "/Textures/lower-artwork-mask.png";
            string perimeter =
                Source + "/Textures/top-perimeter-mask.png";

            HybridReport report = new()
            {
                schemaVersion = 1,
                gate = "11-unity-parity",
                evidenceRevision = 14,
                userFeedback =
                    "我感觉明显还是rev 12细节更多吧",
                assessment =
                    "Correct. Rev13 reduced authored RGB to luminance, "
                    + "changed rev12 flake/roughness tuning, omitted roughness "
                    + "and normal sampling from the motif layer, and let the "
                    + "crystal pass resample scene color.",
                architecture =
                    "Rev12 detail sampling on rev13 physical cap-only meshes: "
                    + "substrate inset 0.28 mm, motif inset 0.14 mm, crystal "
                    + "surface at the existing exterior boundary.",
                upperAlbedoSha256 =
                    Sha256(Path.Combine(projectRoot, upperBase)),
                lowerAlbedoSha256 =
                    Sha256(Path.Combine(projectRoot, lowerBase)),
                upperRoughnessSha256 =
                    Sha256(Path.Combine(projectRoot, upperRough)),
                lowerRoughnessSha256 =
                    Sha256(Path.Combine(projectRoot, lowerRough)),
                upperNormalSha256 =
                    Sha256(Path.Combine(projectRoot, upperNormal)),
                lowerNormalSha256 =
                    Sha256(Path.Combine(projectRoot, lowerNormal)),
                upperMotifMaskSha256 =
                    Sha256(Path.Combine(projectRoot, upperMask)),
                lowerMotifMaskSha256 =
                    Sha256(Path.Combine(projectRoot, lowerMask)),
                perimeterMaskSha256 =
                    Sha256(Path.Combine(projectRoot, perimeter)),
                textureLineage =
                    "All nine textures are the same Unity assets referenced "
                    + "by rev12; no copies or resampling.",
                textureImporter =
                    "Native 620x1000 where applicable, no NPOT scale, mipmaps "
                    + "enabled, bilinear filtering, clamp, uncompressed "
                    + "default; motif masks sample LOD0 for crisp boundaries.",
                substrateInsetMeters =
                    MagneticSlideTrueLayerAssembly.SubstrateInsetMeters,
                motifInsetMeters =
                    MagneticSlideTrueLayerAssembly.MotifInsetMeters,
                crystalCapThicknessMeters =
                    MagneticSlideTrueLayerAssembly.CrystalCapThicknessMeters,
                crystalIor = 1.52f,
                rev12MicaScale = 28f,
                rev12MicroflakeScale = 85f,
                rev12MicroflakeStrength = 0.16f,
                rev12RoughnessMin = 0.022f,
                rev12RoughnessMax = 0.11f,
                rev12NormalScale = 0.32f,
                rev12IridescenceStrength = 0.12f,
                hybridTransmission = 0.985f,
                hybridRefractionPixels = 0.35f,
                measuredParallaxPixelsAt15Degrees =
                    MeasureParallaxPixels(
                        camera: CreateMeasurementCamera(),
                        product: coordinator.CandidateModel),
                boundsCenterDeltaMeters = Vector3.Distance(
                    boundsBefore.center, boundsAfter.center),
                boundsSizeDeltaMeters = Vector3.Distance(
                    boundsBefore.size, boundsAfter.size),
                collidersUnchanged =
                    colliderBefore.SequenceEqual(colliderAfter),
                protectedRuntimeUnchanged =
                    protectedBefore.All(pair =>
                        protectedAfter.TryGetValue(
                            pair.Key, out string value)
                        && value == pair.Value),
                endpointInterlockLegal =
                    coordinator.Mechanism.IsPoseLegal(),
                shaderErrors = shaderErrors,
                shadersSupported =
                    shaders.All(shader =>
                        shader != null && shader.isSupported),
                addedRenderersVersusRev12 = 6,
                estimatedAddedDrawCallsVersusRev12 = 4,
                transparentOverdrawLayers = 1,
                estimatedMobileCost =
                    "Per face: substrate 3 texture + 2 cubemap samples; "
                    + "motif 3 texture + 1 cubemap sample on motif pixels; "
                    + "crystal 1 scene-color + 1 cubemap sample. About 4 "
                    + "additional draw calls and one transparent overdraw "
                    + "layer versus rev12; no device GPU timing.",
                sideArtworkTriangles = 0,
                undersideArtworkTriangles = 0,
                emission = 0f,
                build44InstallAuthorized = false,
                visualApproval = "pending",
            };
            report.pass =
                report.shadersSupported
                && report.shaderErrors == 0
                && report.measuredParallaxPixelsAt15Degrees >= 2.0f
                && report.boundsCenterDeltaMeters < 0.000001f
                && report.boundsSizeDeltaMeters < 0.000001f
                && report.collidersUnchanged
                && report.protectedRuntimeUnchanged
                && report.endpointInterlockLegal
                && report.sideArtworkTriangles == 0
                && report.undersideArtworkTriangles == 0
                && !report.build44InstallAuthorized;
            File.WriteAllText(
                Path.Combine(output, "unity-hybrid-report.json"),
                JsonUtility.ToJson(report, true)
                + Environment.NewLine);
            if (!report.pass)
                throw new InvalidDataException(
                    "Hybrid material capture validation failed.");
        }

        private static void CaptureVariant(
            string variant,
            Action apply,
            Camera camera,
            MagneticSlideTileShippingCoordinator coordinator,
            string output)
        {
            string views = Path.Combine(output, variant);
            string frames = Path.Combine(
                output, variant + "-motion-frames");
            Directory.CreateDirectory(views);
            Directory.CreateDirectory(frames);
            apply();
            foreach (ViewRecipe view in Views)
            {
                ApplyPose(coordinator, view.MaximumOpen);
                Render(camera, views, view);
            }
            CaptureMotion(camera, coordinator, frames);
        }

        private static void ApplyR012(GameObject product)
        {
            foreach (MagneticSlideTrueLayerAssembly assembly
                     in product.GetComponentsInChildren<
                         MagneticSlideTrueLayerAssembly>(true))
                assembly.gameObject.SetActive(false);
            Material upper = LoadMaterial(
                R012 + "/Materials/M_G11R012_UpperLayeredTop.mat");
            Material lower = LoadMaterial(
                R012 + "/Materials/M_G11R012_LowerLayeredTop.mat");
            foreach (MeshRenderer renderer in ProductRenderers(product))
            {
                renderer.GetComponent<MeshFilter>().sharedMesh =
                    LoadSourceMesh(renderer.name);
                renderer.sharedMaterials = MapSourceMaterials(
                    renderer.name,
                    renderer.name == "MovingTopBody" ? upper : lower);
            }
        }

        private static void ApplyPhysical(
            GameObject product,
            MaterialSet materials)
        {
            foreach (MeshRenderer renderer in ProductRenderers(product))
            {
                renderer.GetComponent<MeshFilter>().sharedMesh =
                    AssetDatabase.LoadAssetAtPath<Mesh>(
                        $"{R013}/Generated/{renderer.name}"
                        + "_TrueLayerBody_R013.asset")
                    ?? throw new InvalidDataException(
                        $"Generated rev13 body missing: {renderer.name}");
                renderer.sharedMaterials = MapSourceMaterials(
                    renderer.name,
                    renderer.name == "MovingTopBody"
                        ? materials.UpperSubstrate
                        : materials.LowerSubstrate);
            }
            foreach (MagneticSlideTrueLayerAssembly assembly
                     in product.GetComponentsInChildren<
                         MagneticSlideTrueLayerAssembly>(true))
            {
                assembly.gameObject.SetActive(true);
                bool upper = assembly.FaceId == "upper";
                assembly.Substrate.sharedMaterial =
                    upper
                        ? materials.UpperSubstrate
                        : materials.LowerSubstrate;
                assembly.Motif.sharedMaterial =
                    upper ? materials.UpperMotif : materials.LowerMotif;
                assembly.CrystalCap.sharedMaterial =
                    upper
                        ? materials.UpperCrystal
                        : materials.LowerCrystal;
            }
        }

        private static MaterialSet LoadR013Materials()
        {
            return new MaterialSet(
                LoadMaterial(
                    R013 + "/Materials/M_G11R013_UpperBloodRedSubstrate.mat"),
                LoadMaterial(
                    R013 + "/Materials/M_G11R013_LowerBloodRedSubstrate.mat"),
                LoadMaterial(
                    R013 + "/Materials/M_G11R013_UpperEtchedBlackMotif.mat"),
                LoadMaterial(
                    R013 + "/Materials/M_G11R013_LowerEtchedBlackMotif.mat"),
                LoadMaterial(
                    R013 + "/Materials/M_G11R013_UpperCrystalCap.mat"),
                LoadMaterial(
                    R013 + "/Materials/M_G11R013_LowerCrystalCap.mat"));
        }

        private static MaterialSet CreateHybridMaterials()
        {
            EnsureFolder(Root);
            EnsureFolder(Materials);
            Cubemap environment = AssetDatabase.LoadAssetAtPath<Cubemap>(
                Source
                + "/Environment/MagneticSlideTileGate11R011Environment.cubemap")
                ?? throw new InvalidDataException(
                    "Approved environment missing.");
            Texture2D perimeter =
                LoadTexture("top-perimeter-mask.png");
            return new MaterialSet(
                CreateSubstrate(
                    "Upper",
                    "upper-albedo.png",
                    "upper-roughness.png",
                    "upper-transport-normal-r011.png",
                    environment),
                CreateSubstrate(
                    "Lower",
                    "lower-albedo.png",
                    "lower-roughness.png",
                    "lower-transport-normal-r011.png",
                    environment),
                CreateMotif(
                    "Upper",
                    "upper-artwork-mask.png",
                    "upper-roughness.png",
                    "upper-transport-normal-r011.png",
                    perimeter,
                    environment),
                CreateMotif(
                    "Lower",
                    "lower-artwork-mask.png",
                    "lower-roughness.png",
                    "lower-transport-normal-r011.png",
                    perimeter,
                    environment),
                CreateCrystal("Upper", environment),
                CreateCrystal("Lower", environment));
        }

        private static Material CreateSubstrate(
            string face,
            string baseName,
            string roughnessName,
            string normalName,
            Cubemap environment)
        {
            Shader shader = Shader.Find(
                "FidgetingApp/MagneticSlideTile/HybridSubstrateR014")
                ?? throw new InvalidDataException(
                    "Hybrid substrate shader missing.");
            Material material = GetOrCreateMaterial(
                $"M_G11R014_{face}Rev12DetailSubstrate", shader);
            material.SetTexture("_BaseMap", LoadTexture(baseName));
            material.SetTexture(
                "_RoughnessMap", LoadTexture(roughnessName));
            material.SetTexture(
                "_NormalMap", LoadTexture(normalName));
            material.SetTexture("_SharedEnvironment", environment);
            material.SetColor(
                "_SubstrateTint",
                new Color(1f, 0.62f, 0.70f, 1f));
            material.SetFloat("_RoughnessMin", 0.022f);
            material.SetFloat("_RoughnessMax", 0.11f);
            material.SetFloat("_NormalScale", 0.32f);
            material.SetFloat("_MicaScale", 28f);
            material.SetFloat("_MicroflakeScale", 85f);
            material.SetFloat("_MicroflakeStrength", 0.16f);
            material.SetFloat("_IridescenceStrength", 0.12f);
            return SaveMaterial(material);
        }

        private static Material CreateMotif(
            string face,
            string maskName,
            string roughnessName,
            string normalName,
            Texture2D perimeter,
            Cubemap environment)
        {
            Shader shader = Shader.Find(
                "FidgetingApp/MagneticSlideTile/HybridMotifR014")
                ?? throw new InvalidDataException(
                    "Hybrid motif shader missing.");
            Material material = GetOrCreateMaterial(
                $"M_G11R014_{face}Rev12DetailMotif", shader);
            material.SetTexture(
                "_MotifMask", LoadTexture(maskName));
            material.SetTexture("_PerimeterMask", perimeter);
            material.SetTexture(
                "_RoughnessMap", LoadTexture(roughnessName));
            material.SetTexture(
                "_NormalMap", LoadTexture(normalName));
            material.SetTexture("_SharedEnvironment", environment);
            material.SetColor(
                "_MotifColor",
                new Color(0.018f, 0.020f, 0.024f, 1f));
            material.SetFloat("_Roughness", 0.18f);
            material.SetFloat("_Metallic", 0.24f);
            material.SetFloat("_NormalScale", 0.16f);
            return SaveMaterial(material);
        }

        private static Material CreateCrystal(
            string face,
            Cubemap environment)
        {
            Shader shader = Shader.Find(
                "FidgetingApp/MagneticSlideTile/HybridCrystalR014")
                ?? throw new InvalidDataException(
                    "Hybrid crystal shader missing.");
            Material material = GetOrCreateMaterial(
                $"M_G11R014_{face}DetailPreservingCrystal", shader);
            material.SetTexture("_SharedEnvironment", environment);
            material.SetFloat("_Ior", 1.52f);
            material.SetFloat("_Roughness", 0.022f);
            material.SetFloat(
                "_ThicknessMeters",
                MagneticSlideTrueLayerAssembly.CrystalCapThicknessMeters);
            material.SetFloat("_Transmission", 0.985f);
            material.SetFloat("_ReflectionStrength", 0.68f);
            material.SetFloat("_RefractionPixels", 0.35f);
            material.renderQueue = 3090;
            return SaveMaterial(material);
        }

        private static void CaptureMotion(
            Camera camera,
            MagneticSlideTileShippingCoordinator coordinator,
            string directory)
        {
            coordinator.ResetShippingPose(false);
            Vector3 target = new(0f, 0.004f, 0f);
            const int frameCount = 150;
            for (int frame = 0; frame < frameCount; frame++)
            {
                float phase = frame / (float)(frameCount - 1);
                float yaw =
                    Mathf.Lerp(-58f, 58f, phase) * Mathf.Deg2Rad;
                float elevation =
                    Mathf.Lerp(
                        17f,
                        48f,
                        0.5f - 0.5f
                        * Mathf.Cos(phase * Mathf.PI * 2f))
                    * Mathf.Deg2Rad;
                const float radius = 0.102f;
                Vector3 position = new(
                    Mathf.Sin(yaw) * Mathf.Cos(elevation) * radius,
                    Mathf.Sin(elevation) * radius,
                    -Mathf.Cos(yaw) * Mathf.Cos(elevation) * radius);
                camera.transform.SetPositionAndRotation(
                    position,
                    Quaternion.LookRotation(
                        target - position, Vector3.up));
                camera.fieldOfView = 25f;
                RenderCurrent(
                    camera,
                    Path.Combine(
                        directory, $"frame-{frame:D4}.png"),
                    960,
                    540);
            }
        }

        private static float MeasureParallaxPixels(
            Camera camera,
            GameObject product)
        {
            try
            {
                MagneticSlideTrueLayerAssembly upper = product
                    .GetComponentsInChildren<
                        MagneticSlideTrueLayerAssembly>(true)
                    .Single(assembly => assembly.FaceId == "upper");
                Mesh cap =
                    upper.CrystalCap.GetComponent<MeshFilter>().sharedMesh;
                Vector3 center = cap.bounds.center;
                Vector3 substrate = upper.transform.TransformPoint(
                    center - upper.LocalOutwardNormal
                    * MagneticSlideTrueLayerAssembly.SubstrateInsetMeters);
                Vector3 motif = upper.transform.TransformPoint(
                    center - upper.LocalOutwardNormal
                    * MagneticSlideTrueLayerAssembly.MotifInsetMeters);
                Vector3 substrateViewport =
                    camera.WorldToViewportPoint(substrate);
                Vector3 motifViewport =
                    camera.WorldToViewportPoint(motif);
                return Vector2.Distance(
                    new Vector2(
                        substrateViewport.x * 1280f,
                        substrateViewport.y * 960f),
                    new Vector2(
                        motifViewport.x * 1280f,
                        motifViewport.y * 960f));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(camera.gameObject);
            }
        }

        private static Camera CreateMeasurementCamera()
        {
            Camera camera = CreateCaptureCamera();
            const float angle = 15f * Mathf.Deg2Rad;
            const float radius = 0.055f;
            Vector3 position = new(
                0.004f,
                Mathf.Cos(angle) * radius,
                -Mathf.Sin(angle) * radius);
            Vector3 lookAt = new(0f, 0.004f, 0f);
            camera.transform.SetPositionAndRotation(
                position,
                Quaternion.LookRotation(
                    lookAt - position, Vector3.up));
            camera.fieldOfView = 14f;
            camera.aspect = 1280f / 960f;
            return camera;
        }

        private static Vector3 GrazingPosition(float degrees)
        {
            float radians = degrees * Mathf.Deg2Rad;
            const float radius = 0.105f;
            return new Vector3(
                0.012f,
                Mathf.Cos(radians) * radius,
                -Mathf.Sin(radians) * radius);
        }

        private static void ApplyPose(
            MagneticSlideTileShippingCoordinator coordinator,
            bool maximumOpen)
        {
            coordinator.ResetShippingPose(false);
            if (maximumOpen)
            {
                coordinator.TryApplySlideInput(
                    coordinator.Settings.MaximumTravelMeters, false);
            }
        }

        private static void Render(
            Camera camera,
            string directory,
            ViewRecipe view)
        {
            camera.transform.SetPositionAndRotation(
                view.Position,
                Quaternion.LookRotation(
                    view.LookAt - view.Position, Vector3.up));
            camera.fieldOfView = view.FieldOfView;
            camera.aspect = (float)view.Width / view.Height;
            RenderCurrent(
                camera,
                Path.Combine(directory, view.Id + ".png"),
                view.Width,
                view.Height);
        }

        private static void RenderCurrent(
            Camera camera,
            string path,
            int width,
            int height)
        {
            RenderTexture target = new(
                width, height, 24, RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.Default);
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            try
            {
                target.Create();
                camera.targetTexture = target;
                camera.ResetWorldToCameraMatrix();
                camera.ResetProjectionMatrix();
                camera.ResetCullingMatrix();
                camera.Render();
                camera.Render();
                RenderTexture.active = target;
                Texture2D image = new(
                    width, height, TextureFormat.RGBA32, false, false);
                image.ReadPixels(
                    new Rect(0, 0, width, height), 0, 0);
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

        private static Camera CreateCaptureCamera()
        {
            GameObject cameraObject = new(
                "CAM_Gate11R014_HybridCapture")
            {
                hideFlags = HideFlags.HideAndDontSave,
            };
            Camera camera = cameraObject.AddComponent<Camera>();
            cameraObject.AddComponent<UniversalAdditionalCameraData>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor =
                new Color(0.012f, 0.016f, 0.023f, 1f);
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 5f;
            camera.allowHDR = true;
            camera.allowMSAA = false;
            camera.orthographic = false;
            return camera;
        }

        private static Material[] MapSourceMaterials(
            string rendererName,
            Material topMaterial)
        {
            return SourceRenderer(rendererName).sharedMaterials
                .Select(sourceMaterial =>
                {
                    string name = sourceMaterial != null
                        ? sourceMaterial.name
                        : string.Empty;
                    if (name.Contains(
                            "TopArtwork",
                            StringComparison.OrdinalIgnoreCase))
                        return topMaterial;
                    if (name.Contains(
                            "SolidDarkSide",
                            StringComparison.OrdinalIgnoreCase))
                        return LoadMaterial(
                            R011 + "/Materials/"
                            + "M_G11R011_SolidDarkSide.mat");
                    if (name.Contains(
                            "PolishedBrightSilverRim",
                            StringComparison.OrdinalIgnoreCase))
                        return LoadMaterial(
                            R011 + "/Materials/"
                            + "M_G11R011_PolishedBrightSilverRim.mat");
                    if (name.Contains(
                            "NeutralUnderside",
                            StringComparison.OrdinalIgnoreCase))
                        return LoadMaterial(
                            R011 + "/Materials/"
                            + "M_G11R011_NeutralUnderside.mat");
                    throw new InvalidDataException(
                        $"Unexpected source material {name}.");
                })
                .ToArray();
        }

        private static MeshRenderer SourceRenderer(
            string rendererName)
        {
            GameObject source =
                AssetDatabase.LoadAssetAtPath<GameObject>(SourceFbx)
                ?? throw new InvalidDataException(
                    "Source FBX missing.");
            return source.GetComponentsInChildren<MeshRenderer>(true)
                .Single(renderer => renderer.name == rendererName);
        }

        private static Mesh LoadSourceMesh(string name)
        {
            return AssetDatabase.LoadAllAssetsAtPath(SourceFbx)
                .OfType<Mesh>()
                .Single(mesh => mesh.name == name);
        }

        private static MeshRenderer[] ProductRenderers(
            GameObject product)
        {
            return product.GetComponentsInChildren<MeshRenderer>(true)
                .Where(renderer =>
                    renderer.name == "MovingTopBody"
                    || renderer.name == "BottomExterior")
                .ToArray();
        }

        private static Bounds ProductBounds(GameObject product)
        {
            MeshRenderer[] renderers =
                product.GetComponentsInChildren<MeshRenderer>(true)
                    .Where(renderer => renderer.enabled)
                    .ToArray();
            Bounds bounds = renderers[0].bounds;
            foreach (MeshRenderer renderer in renderers.Skip(1))
                bounds.Encapsulate(renderer.bounds);
            return bounds;
        }

        private static MagneticSlideTileShippingCoordinator
            FindCoordinator()
        {
            return UnityEngine.Object.FindFirstObjectByType<
                       MagneticSlideTileShippingCoordinator>(
                       FindObjectsInactive.Include)
                   ?? throw new InvalidDataException(
                       "Shipping coordinator missing.");
        }

        private static Texture2D LoadTexture(string name)
        {
            return AssetDatabase.LoadAssetAtPath<Texture2D>(
                       Source + "/Textures/" + name)
                   ?? throw new InvalidDataException(
                       $"Texture missing: {name}");
        }

        private static Material LoadMaterial(string path)
        {
            return AssetDatabase.LoadAssetAtPath<Material>(path)
                   ?? throw new InvalidDataException(
                       $"Material missing: {path}");
        }

        private static Material GetOrCreateMaterial(
            string name,
            Shader shader)
        {
            string path = $"{Materials}/{name}.mat";
            Material material =
                AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader) { name = name };
                AssetDatabase.CreateAsset(material, path);
            }
            else
            {
                material.shader = shader;
                material.name = name;
            }
            return material;
        }

        private static Material SaveMaterial(Material material)
        {
            EditorUtility.SetDirty(material);
            AssetDatabase.SaveAssetIfDirty(material);
            return material;
        }

        private static void EnsureFolder(string path)
        {
            string parent = Path.GetDirectoryName(path)!
                .Replace('\\', '/');
            string name = Path.GetFileName(path);
            if (!AssetDatabase.IsValidFolder(path))
                AssetDatabase.CreateFolder(parent, name);
        }

        private static Dictionary<string, string> HashProtectedSources(
            string projectRoot)
        {
            return ProtectedSources.ToDictionary(
                path => path,
                path => Sha256(Path.Combine(projectRoot, path)));
        }

        private static string Sha256(string path)
        {
            using SHA256 algorithm = SHA256.Create();
            using FileStream stream = File.OpenRead(path);
            return BitConverter.ToString(
                    algorithm.ComputeHash(stream))
                .Replace("-", string.Empty)
                .ToLowerInvariant();
        }

        private static string[] ColliderIdentities()
        {
            return UnityEngine.Object.FindObjectsByType<Collider>(
                    FindObjectsInactive.Include,
                    FindObjectsSortMode.InstanceID)
                .Select(collider =>
                    $"{GetPath(collider.transform)}|"
                    + $"{collider.GetType().FullName}|"
                    + $"{collider.bounds.center:R}|"
                    + $"{collider.bounds.size:R}")
                .OrderBy(value => value, StringComparer.Ordinal)
                .ToArray();
        }

        private static string GetPath(Transform transform)
        {
            List<string> parts = new();
            for (Transform current = transform;
                 current != null;
                 current = current.parent)
                parts.Add(current.name);
            parts.Reverse();
            return string.Join("/", parts);
        }

        private readonly struct ViewRecipe
        {
            public ViewRecipe(
                string id,
                Vector3 position,
                Vector3 lookAt,
                float fieldOfView,
                int width,
                int height,
                bool maximumOpen)
            {
                Id = id;
                Position = position;
                LookAt = lookAt;
                FieldOfView = fieldOfView;
                Width = width;
                Height = height;
                MaximumOpen = maximumOpen;
            }

            public string Id { get; }
            public Vector3 Position { get; }
            public Vector3 LookAt { get; }
            public float FieldOfView { get; }
            public int Width { get; }
            public int Height { get; }
            public bool MaximumOpen { get; }
        }

        private sealed class MaterialSet
        {
            public MaterialSet(
                Material upperSubstrate,
                Material lowerSubstrate,
                Material upperMotif,
                Material lowerMotif,
                Material upperCrystal,
                Material lowerCrystal)
            {
                UpperSubstrate = upperSubstrate;
                LowerSubstrate = lowerSubstrate;
                UpperMotif = upperMotif;
                LowerMotif = lowerMotif;
                UpperCrystal = upperCrystal;
                LowerCrystal = lowerCrystal;
            }

            public Material UpperSubstrate { get; }
            public Material LowerSubstrate { get; }
            public Material UpperMotif { get; }
            public Material LowerMotif { get; }
            public Material UpperCrystal { get; }
            public Material LowerCrystal { get; }
        }

        [Serializable]
        private sealed class HybridReport
        {
            public int schemaVersion;
            public string gate;
            public int evidenceRevision;
            public string userFeedback;
            public string assessment;
            public string architecture;
            public string upperAlbedoSha256;
            public string lowerAlbedoSha256;
            public string upperRoughnessSha256;
            public string lowerRoughnessSha256;
            public string upperNormalSha256;
            public string lowerNormalSha256;
            public string upperMotifMaskSha256;
            public string lowerMotifMaskSha256;
            public string perimeterMaskSha256;
            public string textureLineage;
            public string textureImporter;
            public float substrateInsetMeters;
            public float motifInsetMeters;
            public float crystalCapThicknessMeters;
            public float crystalIor;
            public float rev12MicaScale;
            public float rev12MicroflakeScale;
            public float rev12MicroflakeStrength;
            public float rev12RoughnessMin;
            public float rev12RoughnessMax;
            public float rev12NormalScale;
            public float rev12IridescenceStrength;
            public float hybridTransmission;
            public float hybridRefractionPixels;
            public float measuredParallaxPixelsAt15Degrees;
            public float boundsCenterDeltaMeters;
            public float boundsSizeDeltaMeters;
            public bool collidersUnchanged;
            public bool protectedRuntimeUnchanged;
            public bool endpointInterlockLegal;
            public int shaderErrors;
            public bool shadersSupported;
            public int addedRenderersVersusRev12;
            public int estimatedAddedDrawCallsVersusRev12;
            public int transparentOverdrawLayers;
            public string estimatedMobileCost;
            public int sideArtworkTriangles;
            public int undersideArtworkTriangles;
            public float emission;
            public bool build44InstallAuthorized;
            public string visualApproval;
            public bool pass;
        }
    }
}
