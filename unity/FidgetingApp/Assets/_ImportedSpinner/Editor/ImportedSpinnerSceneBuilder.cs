using System;
using System.Collections.Generic;
using System.IO;
using FidgetingApp.Product;
using ThreeBladeEDC.Interaction;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace FidgetingApp.ImportedSpinner.EditorTools
{
    /// <summary>
    /// Rebuilds only the legacy gold-four-wing product slot with the approved
    /// 85 mm Dragon Scale CLI asset. The two authored three-blade scenes are
    /// source templates/read-only inputs and are never saved by this builder.
    /// </summary>
    public static class ImportedSpinnerSceneBuilder
    {
        public const string ScenePath =
            "Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity";
        public const string RuntimeModelPath =
            "Assets/_ImportedSpinner/Models/DragonScaleCLI/"
            + "DragonScaleEDC_CLI_85mm.fbx";
        public const string CollisionModelPath =
            "Assets/_ImportedSpinner/Models/DragonScaleCLI/"
            + "DragonScaleEDC_CLI_85mm_Collision.fbx";
        public const string DccSourcePath =
            "ArtSource/DragonScaleEDC/CLIAnything/DragonScaleEDC_CLI_85mm.blend";

        private const string BaseScenePath =
            "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity";
        private const string MaterialFolder =
            "Assets/_ImportedSpinner/Materials/DragonScaleCLI";
        private const string ReflectionPath =
            MaterialFolder + "/C_DragonScaleCLIStudio.asset";
        private const string SandblastNormalPath =
            "Assets/_Fidgeting/Generated/Textures/N_Sandblast.asset";
        private const string RadialTexturePath =
            "Assets/_Fidgeting/Generated/Textures/T_RadialBrush.asset";
        private const string RadialNormalPath =
            "Assets/_Fidgeting/Generated/Textures/N_RadialBrush.asset";
        private const float TargetPlanarWidth =
            ProductFramingCatalog.CircularReferencePlanarDiameterMeters;
        private const float TargetThickness = 0.017f;
        private const int RotorBladeCount = 3;

        private sealed class DragonScaleMaterials
        {
            public Material body;
            public Material bodyDark;
            public Material polished;
            public Material radialA;
            public Material radialB;
            public Material recess;
            public Material bearing;
            public Material pom;
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

        [MenuItem("Tools/Codex/Build Dragon Scale In Imported Spinner Slot")]
        public static void BuildPresentation()
        {
            if (!Application.isBatchMode
                && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
            {
                throw new OperationCanceledException(
                    "Dragon Scale build cancelled so the open Unity scene was not discarded.");
            }

            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            ConfigureModelImporter(RuntimeModelPath, importMaterials: true);
            ConfigureModelImporter(CollisionModelPath, importMaterials: false);

            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(RuntimeModelPath);
            if (model == null)
            {
                throw new FileNotFoundException(
                    "The Dragon Scale CLI runtime FBX is missing.",
                    RuntimeModelPath);
            }

            EnsureAssetFolder("Assets/_ImportedSpinner/Scenes");
            DragonScaleMaterials materials = CreateOrUpdateMaterials();

            // Open the saved pointed-three-blade scene only as the canonical
            // interaction template. Save exclusively to ScenePath below.
            Scene scene = EditorSceneManager.OpenScene(BaseScenePath, OpenSceneMode.Single);
            GameObject root = GameObject.Find("ThreeBladeEDC_Root");
            if (root == null)
            {
                throw new InvalidDataException(
                    "The canonical rotor scene no longer contains ThreeBladeEDC_Root.");
            }

            root.name = "ImportedSpinner_Root";
            Transform rotor = root.transform.Find("RotorDynamic");
            Transform hub = root.transform.Find("HubStatic");
            if (rotor == null || hub == null)
            {
                throw new InvalidDataException(
                    "The canonical rotor/hub scene contract changed.");
            }

            ClearChildren(rotor);
            ClearChildren(hub);
            DestroyChild(root.transform, "BearingVisual");
            DestroyComponent<MetalGlintController>(root);
            DestroyComponent<SpinnerVariantSwitcher>(root);
            DestroyColliders(rotor);
            DestroyColliders(hub);
            hub.gameObject.SetActive(true);

            RotorRigidbodyController controller =
                rotor.GetComponent<RotorRigidbodyController>();
            Rigidbody rotorBody = rotor.GetComponent<Rigidbody>();
            if (controller == null
                || rotorBody == null
                || root.GetComponent<MobileGestureController>() == null)
            {
                throw new InvalidDataException(
                    "The imported slot must retain the canonical rotor and gesture pipeline.");
            }

            GameObject source = (GameObject)PrefabUtility.InstantiatePrefab(model, scene);
            source.name = "DragonScaleCLI_Source";
            source.transform.SetParent(root.transform, false);
            source.transform.localPosition = Vector3.zero;
            // Blender +Z becomes Unity +Y. This authored rotation keeps the
            // reference blade at twelve o'clock in the shipping hero view.
            source.transform.localRotation = Quaternion.Euler(0f, 180f, 0f);
            source.transform.localScale = Vector3.one;

            Renderer[] importedRenderers = ScaleVisualToReference(source, rotor);
            AssignMaterials(importedRenderers, materials);
            PrefabUtility.UnpackPrefabInstance(
                source,
                PrefabUnpackMode.Completely,
                InteractionMode.AutomatedAction);

            Transform rotorRoot = RequireDescendant(source.transform, "Rotor_Root");
            Transform fixedRoot = RequireDescendant(source.transform, "Fixed_Root");
            Transform bearingRoot = RequireDescendant(
                source.transform,
                "BearingAssembly_Root");
            Transform cageRoot = RequireDescendant(source.transform, "BearingCage_Root");
            Transform topCapRoot = RequireDescendant(source.transform, "TopCap_Root");
            Transform topWasherRoot = RequireDescendant(source.transform, "TopWasher_Root");
            Transform bottomWasherRoot = RequireDescendant(
                source.transform,
                "BottomWasher_Root");
            Transform bottomCapRoot = RequireDescendant(source.transform, "BottomCap_Root");
            Transform outerRace = RequireDescendant(source.transform, "BearingOuterRace");
            Transform innerRace = RequireDescendant(source.transform, "BearingInnerRace");
            Transform topShield = RequireDescendant(source.transform, "BearingShield_Top");
            Transform bottomShield = RequireDescendant(
                source.transform,
                "BearingShield_Bottom");

            GameObject bearingVisualObject = new GameObject("BearingVisual");
            bearingVisualObject.transform.SetParent(root.transform, false);
            GameObject cageObject = new GameObject("BallCage");
            cageObject.transform.SetParent(bearingVisualObject.transform, false);

            ReparentPreservingWorld(rotorRoot, rotor);
            ReparentPreservingWorld(fixedRoot, hub);
            // The outer race and shields rotate with the chassis. The inner
            // race, axle and finger caps stay fixed; the cage follows half the
            // real rotor angle for a mechanically legible bearing animation.
            ReparentPreservingWorld(outerRace, rotor);
            ReparentPreservingWorld(topShield, rotor);
            ReparentPreservingWorld(bottomShield, rotor);
            ReparentPreservingWorld(innerRace, hub);
            ReparentPreservingWorld(cageRoot, cageObject.transform);
            Object.DestroyImmediate(bearingRoot.gameObject);
            Object.DestroyImmediate(source);

            var touchCollider = rotor.gameObject.AddComponent<BoxCollider>();
            touchCollider.center = Vector3.zero;
            touchCollider.size = new Vector3(
                TargetPlanarWidth * 1.08f,
                TargetThickness * 1.8f,
                TargetPlanarWidth * 1.08f);

            var capCollider = hub.gameObject.AddComponent<CapsuleCollider>();
            capCollider.direction = 1;
            capCollider.center = Vector3.zero;
            capCollider.radius = 0.0221f;
            capCollider.height = TargetThickness;
            if (hub.GetComponent<SpinnerTouchSurface>() == null)
            {
                hub.gameObject.AddComponent<SpinnerTouchSurface>();
            }

            BearingCageVisualSync cageSync =
                bearingVisualObject.AddComponent<BearingCageVisualSync>();
            cageSync.Configure(controller, cageObject.transform, 0.5f);

            ExplodedViewController exploded =
                root.GetComponent<ExplodedViewController>()
                ?? root.AddComponent<ExplodedViewController>();
            exploded.Configure(
                rotorBody,
                new[]
                {
                    Part(topCapRoot, new Vector3(0f, 0.043f, 0f)),
                    Part(topWasherRoot, new Vector3(0f, 0.024f, 0f)),
                    Part(outerRace, new Vector3(0f, 0.010f, 0f)),
                    Part(innerRace, new Vector3(0f, 0.010f, 0f)),
                    Part(topShield, new Vector3(0f, 0.010f, 0f)),
                    Part(bottomShield, new Vector3(0f, 0.010f, 0f)),
                    Part(cageObject.transform, new Vector3(0f, 0.010f, 0f)),
                    Part(bottomWasherRoot, new Vector3(0f, -0.016f, 0f)),
                    Part(bottomCapRoot, new Vector3(0f, -0.036f, 0f))
                });

            RotorWindAudio windAudio =
                root.GetComponentInChildren<RotorWindAudio>(true);
            MetalRatchetDetentAudio ratchetAudio =
                root.GetComponentInChildren<MetalRatchetDetentAudio>(true);
            if (windAudio == null || ratchetAudio == null)
            {
                throw new InvalidDataException(
                    "The imported slot must retain wind and ratchet audio layers.");
            }
            windAudio.Configure(
                controller,
                RotorBladeCount,
                RotorWindAudioModel.DefaultMasterVolume);

            OrbitPresentationCamera orbit =
                Object.FindAnyObjectByType<OrbitPresentationCamera>();
            if (orbit == null)
            {
                throw new InvalidDataException(
                    "The imported slot has no authored orbit camera.");
            }
            orbit.Target = root.transform;
            orbit.FocusTarget = FindDescendant(
                    topCapRoot,
                    "FingerCapTop_RadialFace")
                ?? topCapRoot;
            orbit.ConfigureFraming(ProductFramingCatalog.Resolve(ScenePath));
            orbit.ResetHero();

            ConfigureLights(root);
            ConfigureDragonScaleStudio(root);
            rotorBody.linearVelocity = Vector3.zero;
            rotorBody.angularVelocity = Vector3.zero;
            rotorBody.Sleep();
            controller.CaptureInitialPose();

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ScenePath, true);
            SetProductBuildScenes();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log(
                $"[ImportedSpinner] Dragon Scale CLI scene built: {ScenePath}; "
                + $"runtime={RuntimeModelPath}; dcc={DccSourcePath}; "
                + "pointed/metal three-blade scenes were not saved");
        }

        [MenuItem("Tools/Codex/Build And Capture Dragon Scale Shipping Preview")]
        public static void BuildAndCapturePreview()
        {
            BuildPresentation();
            CapturePreview();
        }

        private static void ConfigureModelImporter(
            string assetPath,
            bool importMaterials)
        {
            AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceSynchronousImport);
            ModelImporter importer = AssetImporter.GetAtPath(assetPath) as ModelImporter;
            if (importer == null)
            {
                throw new FileNotFoundException("Model importer is missing.", assetPath);
            }

            importer.globalScale = 1f;
            importer.useFileScale = true;
            importer.preserveHierarchy = true;
            importer.importAnimation = false;
            importer.importBlendShapes = false;
            importer.importCameras = false;
            importer.importLights = false;
            importer.importVisibility = false;
            importer.materialImportMode = importMaterials
                ? ModelImporterMaterialImportMode.ImportStandard
                : ModelImporterMaterialImportMode.None;
            importer.meshCompression = ModelImporterMeshCompression.Off;
            importer.optimizeMeshPolygons = true;
            importer.optimizeMeshVertices = true;
            importer.weldVertices = true;
            importer.isReadable = false;
            importer.importNormals = ModelImporterNormals.Import;
            importer.importTangents = ModelImporterTangents.CalculateMikk;
            importer.SaveAndReimport();
        }

        private static Renderer[] ScaleVisualToReference(
            GameObject source,
            Transform rotor)
        {
            Renderer[] renderers = source.GetComponentsInChildren<Renderer>(true);
            if (renderers.Length == 0)
            {
                throw new InvalidDataException(
                    "The Dragon Scale CLI model has no renderers.");
            }

            Bounds bounds = CombinedBounds(renderers);
            float planarSize = Mathf.Max(bounds.size.x, bounds.size.z);
            if (planarSize <= 0f || bounds.size.y <= 0f)
            {
                throw new InvalidDataException(
                    "The Dragon Scale CLI model has invalid bounds.");
            }

            float uniformScale = TargetPlanarWidth / planarSize;
            source.transform.localScale = Vector3.one * uniformScale;
            // The authored FBX origin is the mechanical bearing axis. A
            // three-blade silhouette has an asymmetric world AABB (one tip is
            // opposite two tips), so aligning the AABB center to RotorDynamic
            // moves the real bearing axis off the Rigidbody pivot. Keep the
            // authored origin on the runtime axis and use bounds only for
            // dimensional validation.
            source.transform.position = rotor.position;
            bounds = CombinedBounds(renderers);
            if (Mathf.Abs(bounds.size.x > bounds.size.z
                    ? bounds.size.x - TargetPlanarWidth
                    : bounds.size.z - TargetPlanarWidth) > 0.0002f
                || Mathf.Abs(bounds.size.y - TargetThickness) > 0.00025f)
            {
                throw new InvalidDataException(
                    $"Dragon Scale dimensions drifted after import: "
                    + $"bounds={bounds.size}, expected width={TargetPlanarWidth} "
                    + $"and thickness={TargetThickness}.");
            }
            Vector3 originOffset = source.transform.position - rotor.position;
            if (new Vector2(originOffset.x, originOffset.z).magnitude > 0.00001f)
            {
                throw new InvalidDataException(
                    $"Dragon Scale mechanical origin drifted from RotorDynamic: "
                    + $"offset={originOffset}.");
            }
            return renderers;
        }

        private static Bounds CombinedBounds(Renderer[] renderers)
        {
            Bounds bounds = renderers[0].bounds;
            for (int index = 1; index < renderers.Length; index++)
            {
                bounds.Encapsulate(renderers[index].bounds);
            }
            return bounds;
        }

        private static DragonScaleMaterials CreateOrUpdateMaterials()
        {
            EnsureAssetFolder(MaterialFolder);
            Texture2D sandblastNormal =
                AssetDatabase.LoadAssetAtPath<Texture2D>(SandblastNormalPath);
            Texture2D radialTexture =
                AssetDatabase.LoadAssetAtPath<Texture2D>(RadialTexturePath);
            Texture2D radialNormal =
                AssetDatabase.LoadAssetAtPath<Texture2D>(RadialNormalPath);
            if (sandblastNormal == null || radialTexture == null || radialNormal == null)
            {
                throw new FileNotFoundException(
                    "The shared machined-metal textures are missing; rebuild the canonical material assets first.");
            }

            return new DragonScaleMaterials
            {
                body = CreateOrUpdateMaterial(
                    "M_DragonScale_BlastedTitanium",
                    "Universal Render Pipeline/Lit",
                    new Color32(0xAE, 0xB3, 0xB6, 0xFF),
                    1f,
                    0.72f,
                    null,
                    sandblastNormal,
                    0.12f),
                bodyDark = CreateOrUpdateMaterial(
                    "M_DragonScale_BlastedTitaniumDark",
                    "Universal Render Pipeline/Lit",
                    new Color32(0x72, 0x79, 0x81, 0xFF),
                    1f,
                    0.69f,
                    null,
                    sandblastNormal,
                    0.08f),
                polished = CreateOrUpdateMaterial(
                    "M_DragonScale_PolishedEdge",
                    "Universal Render Pipeline/Lit",
                    new Color32(0xD6, 0xDA, 0xDD, 0xFF),
                    1f,
                    0.90f,
                    null,
                    null,
                    0f),
                radialA = CreateOrUpdateMaterial(
                    "M_DragonScale_RadialBrushedA",
                    "ThreeBlade/RadialBrushedMetal",
                    new Color32(0xE6, 0xEA, 0xEC, 0xFF),
                    1f,
                    0.81f,
                    radialTexture,
                    radialNormal,
                    0.10f,
                    0.08f),
                radialB = CreateOrUpdateMaterial(
                    "M_DragonScale_RadialBrushedB",
                    "ThreeBlade/RadialBrushedMetal",
                    new Color32(0xBF, 0xC5, 0xC8, 0xFF),
                    1f,
                    0.77f,
                    radialTexture,
                    radialNormal,
                    0.10f,
                    0.08f),
                recess = CreateOrUpdateMaterial(
                    "M_DragonScale_RecessedGunmetal",
                    "Universal Render Pipeline/Lit",
                    new Color32(0x11, 0x15, 0x1A, 0xFF),
                    0.35f,
                    0.52f,
                    null,
                    sandblastNormal,
                    0.07f),
                bearing = CreateOrUpdateMaterial(
                    "M_DragonScale_BearingSteel",
                    "Universal Render Pipeline/Lit",
                    new Color32(0x68, 0x70, 0x77, 0xFF),
                    1f,
                    0.84f,
                    null,
                    null,
                    0f),
                pom = CreateOrUpdateMaterial(
                    "M_DragonScale_BlackPOM",
                    "Universal Render Pipeline/Lit",
                    new Color32(0x0B, 0x0D, 0x10, 0xFF),
                    0f,
                    0.58f,
                    null,
                    null,
                    0f)
            };
        }

        private static Material CreateOrUpdateMaterial(
            string name,
            string shaderName,
            Color color,
            float metallic,
            float smoothness,
            Texture2D baseTexture,
            Texture2D normalTexture,
            float normalStrength,
            float radialContrast = 0f)
        {
            string path = MaterialFolder + "/" + name + ".mat";
            Shader shader = Shader.Find(shaderName);
            if (shader == null)
            {
                throw new MissingReferenceException(
                    $"Required Dragon Scale shader is unavailable: {shaderName}");
            }

            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
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

            SetIfPresent(material, "_BaseColor", color);
            SetIfPresent(material, "_Color", color);
            SetIfPresent(material, "_Metallic", metallic);
            SetIfPresent(material, "_Smoothness", smoothness);
            SetIfPresent(material, "_GlossMapScale", smoothness);
            SetTextureIfPresent(material, "_BaseMap", baseTexture);
            SetTextureIfPresent(material, "_MainTex", baseTexture);
            SetTextureIfPresent(material, "_BumpMap", normalTexture);
            SetIfPresent(material, "_BumpScale", normalStrength);
            SetIfPresent(material, "_RadialContrast", radialContrast);
            SetIfPresent(material, "_EnvironmentReflections", 1f);
            SetIfPresent(material, "_SpecularHighlights", 1f);
            if (normalTexture != null)
            {
                material.EnableKeyword("_NORMALMAP");
            }
            else
            {
                material.DisableKeyword("_NORMALMAP");
            }
            material.DisableKeyword("_METALLICSPECGLOSSMAP");
            EditorUtility.SetDirty(material);
            return material;
        }

        private static void SetIfPresent(Material material, string property, float value)
        {
            if (material.HasProperty(property))
            {
                material.SetFloat(property, value);
            }
        }

        private static void SetIfPresent(Material material, string property, Color value)
        {
            if (material.HasProperty(property))
            {
                material.SetColor(property, value);
            }
        }

        private static void SetTextureIfPresent(
            Material material,
            string property,
            Texture texture)
        {
            if (material.HasProperty(property))
            {
                material.SetTexture(property, texture);
            }
        }

        private static void AssignMaterials(
            Renderer[] renderers,
            DragonScaleMaterials materials)
        {
            foreach (Renderer renderer in renderers)
            {
                Material[] assigned = renderer.sharedMaterials;
                for (int index = 0; index < assigned.Length; index++)
                {
                    assigned[index] = ResolveMaterial(assigned[index], materials);
                }
                renderer.sharedMaterials = assigned;
                renderer.enabled = true;
                renderer.shadowCastingMode = ShadowCastingMode.On;
                renderer.receiveShadows = true;
                renderer.lightProbeUsage = LightProbeUsage.Off;
                renderer.reflectionProbeUsage = ReflectionProbeUsage.BlendProbes;
                renderer.motionVectorGenerationMode =
                    MotionVectorGenerationMode.ForceNoMotion;
            }
        }

        private static Material ResolveMaterial(
            Material imported,
            DragonScaleMaterials materials)
        {
            string name = imported != null ? imported.name : string.Empty;
            if (name.Contains("BlastedTitaniumDark"))
            {
                return materials.bodyDark;
            }
            if (name.Contains("BlastedTitanium"))
            {
                return materials.body;
            }
            if (name.Contains("PolishedEdge"))
            {
                return materials.polished;
            }
            if (name.Contains("RadialBrushedA"))
            {
                return materials.radialA;
            }
            if (name.Contains("RadialBrushedB"))
            {
                return materials.radialB;
            }
            if (name.Contains("RecessedGunmetal"))
            {
                return materials.recess;
            }
            if (name.Contains("BearingSteel"))
            {
                return materials.bearing;
            }
            if (name.Contains("BlackPOM"))
            {
                return materials.pom;
            }
            return materials.body;
        }

        private static void ConfigureLights(GameObject root)
        {
            foreach (Light light in root.GetComponentsInChildren<Light>(true))
            {
                light.useColorTemperature = false;
                switch (light.name)
                {
                    case "Key_5000K":
                        light.color = new Color(0.96f, 0.98f, 1f, 1f);
                        light.intensity = 0.48f;
                        break;
                    case "WarmRim_3200K":
                        light.color = new Color(1f, 0.56f, 0.38f, 1f);
                        light.intensity = 0.22f;
                        break;
                    case "CoolFill_6500K":
                        light.color = new Color(0.66f, 0.78f, 1f, 1f);
                        light.intensity = 0.26f;
                        break;
                }
            }
        }

        private static void ConfigureDragonScaleStudio(GameObject root)
        {
            Cubemap reflection = CreateOrUpdateReflection();
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.23f, 0.25f, 0.29f, 1f);
            RenderSettings.ambientEquatorColor = new Color(0.14f, 0.15f, 0.18f, 1f);
            RenderSettings.ambientGroundColor = new Color(0.055f, 0.06f, 0.075f, 1f);
            RenderSettings.reflectionIntensity = 0.9f;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflectionTexture = reflection;

            ReflectionProbe probe = root.GetComponentInChildren<ReflectionProbe>(true);
            if (probe != null)
            {
                probe.mode = ReflectionProbeMode.Custom;
                probe.customBakedTexture = reflection;
                probe.intensity = 1f;
                probe.boxProjection = false;
            }
        }

        private static Cubemap CreateOrUpdateReflection()
        {
            const int size = 256;
            Cubemap reflection = AssetDatabase.LoadAssetAtPath<Cubemap>(ReflectionPath);
            if (reflection == null)
            {
                reflection = new Cubemap(size, TextureFormat.RGBA32, true)
                {
                    name = "C_DragonScaleCLIStudio",
                    filterMode = FilterMode.Trilinear,
                    wrapMode = TextureWrapMode.Clamp
                };
                AssetDatabase.CreateAsset(reflection, ReflectionPath);
            }

            foreach (CubemapFace face in new[]
                     {
                         CubemapFace.PositiveX,
                         CubemapFace.NegativeX,
                         CubemapFace.PositiveY,
                         CubemapFace.NegativeY,
                         CubemapFace.PositiveZ,
                         CubemapFace.NegativeZ
                     })
            {
                var pixels = new Color[size * size];
                for (int y = 0; y < size; y++)
                {
                    for (int x = 0; x < size; x++)
                    {
                        float u = (x + 0.5f) / size * 2f - 1f;
                        float v = (y + 0.5f) / size * 2f - 1f;
                        Vector3 direction = CubemapDirection(face, u, v);
                        float azimuth = Mathf.Atan2(direction.x, direction.z);
                        float elevation = Mathf.Asin(direction.y);
                        float key = SoftRectangle(
                            azimuth,
                            elevation,
                            -0.82f,
                            0.08f,
                            0.20f,
                            0.72f);
                        float rim = SoftRectangle(
                            azimuth,
                            elevation,
                            1.22f,
                            0.02f,
                            0.15f,
                            0.58f);
                        float overhead = SoftRectangle(
                            azimuth,
                            elevation,
                            0.25f,
                            1.02f,
                            0.95f,
                            0.18f);
                        float horizon = Mathf.SmoothStep(
                            0.055f,
                            0.15f,
                            Mathf.InverseLerp(-0.75f, 0.65f, direction.y));
                        pixels[y * size + x] =
                            new Color(0.17f, 0.18f, 0.20f)
                            + new Color(0.06f, 0.07f, 0.085f) * horizon
                            + new Color(0.78f, 0.83f, 0.90f) * key * 0.72f
                            + new Color(0.64f, 0.36f, 0.22f) * rim * 0.34f
                            + new Color(0.70f, 0.75f, 0.84f) * overhead * 0.34f;
                    }
                }
                reflection.SetPixels(pixels, face);
            }
            reflection.Apply(true, false);
            EditorUtility.SetDirty(reflection);
            return reflection;
        }

        private static Vector3 CubemapDirection(CubemapFace face, float u, float v)
        {
            Vector3 direction = face switch
            {
                CubemapFace.PositiveX => new Vector3(1f, -v, -u),
                CubemapFace.NegativeX => new Vector3(-1f, -v, u),
                CubemapFace.PositiveY => new Vector3(u, 1f, v),
                CubemapFace.NegativeY => new Vector3(u, -1f, -v),
                CubemapFace.PositiveZ => new Vector3(u, -v, 1f),
                CubemapFace.NegativeZ => new Vector3(-u, -v, -1f),
                _ => Vector3.forward
            };
            return direction.normalized;
        }

        private static float SoftRectangle(
            float azimuth,
            float elevation,
            float centerAzimuth,
            float centerElevation,
            float halfWidth,
            float halfHeight)
        {
            float horizontal = Mathf.DeltaAngle(
                centerAzimuth * Mathf.Rad2Deg,
                azimuth * Mathf.Rad2Deg) * Mathf.Deg2Rad;
            float x = Mathf.Abs(horizontal) / Mathf.Max(0.001f, halfWidth);
            float y = Mathf.Abs(elevation - centerElevation)
                / Mathf.Max(0.001f, halfHeight);
            return Mathf.Exp(-(Mathf.Pow(x, 6f) + Mathf.Pow(y, 6f)));
        }

        private static void SetProductBuildScenes()
        {
            string[] paths = ProductCatalog.ShippingScenePaths();
            var scenes = new EditorBuildSettingsScene[paths.Length];
            for (int index = 0; index < paths.Length; index++)
            {
                scenes[index] = new EditorBuildSettingsScene(paths[index], true);
            }
            EditorBuildSettings.scenes = scenes;
        }

        private static ExplodedViewController.ExplodedPart Part(
            Transform transform,
            Vector3 offset)
        {
            return new ExplodedViewController.ExplodedPart
            {
                transform = transform,
                localOffset = offset
            };
        }

        private static Transform RequireDescendant(Transform root, string objectName)
        {
            Transform result = FindDescendant(root, objectName);
            if (result != null)
            {
                return result;
            }
            throw new MissingReferenceException(
                $"{RuntimeModelPath} is missing {objectName}.");
        }

        private static Transform FindDescendant(Transform root, string objectName)
        {
            Transform[] descendants = root.GetComponentsInChildren<Transform>(true);
            for (int index = 0; index < descendants.Length; index++)
            {
                if (descendants[index].name == objectName)
                {
                    return descendants[index];
                }
            }
            return null;
        }

        private static void ReparentPreservingWorld(Transform child, Transform parent)
        {
            child.SetParent(parent, true);
        }

        private static void ClearChildren(Transform parent)
        {
            for (int index = parent.childCount - 1; index >= 0; index--)
            {
                Object.DestroyImmediate(parent.GetChild(index).gameObject);
            }
        }

        private static void DestroyColliders(Transform parent)
        {
            foreach (Collider collider in parent.GetComponents<Collider>())
            {
                Object.DestroyImmediate(collider);
            }
        }

        private static void DestroyChild(Transform parent, string childName)
        {
            Transform child = parent.Find(childName);
            if (child != null)
            {
                Object.DestroyImmediate(child.gameObject);
            }
        }

        private static void DestroyComponent<T>(GameObject gameObject)
            where T : Component
        {
            T component = gameObject.GetComponent<T>();
            if (component != null)
            {
                Object.DestroyImmediate(component);
            }
        }

        private static void EnsureAssetFolder(string path)
        {
            string[] parts = path.Split('/');
            string current = parts[0];
            for (int index = 1; index < parts.Length; index++)
            {
                string next = current + "/" + parts[index];
                if (!AssetDatabase.IsValidFolder(next))
                {
                    AssetDatabase.CreateFolder(current, parts[index]);
                }
                current = next;
            }
        }

        [MenuItem("Tools/Codex/Capture Dragon Scale Shipping Preview")]
        public static void CapturePreview()
        {
            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            GameObject root = GameObject.Find("ImportedSpinner_Root");
            Camera camera = Camera.main ?? Object.FindAnyObjectByType<Camera>();
            OrbitPresentationCamera orbit =
                Object.FindAnyObjectByType<OrbitPresentationCamera>();
            if (root == null || camera == null || orbit == null)
            {
                throw new InvalidDataException(
                    "The shipping Dragon Scale scene is missing its root or camera.");
            }
            if (!ProductCameraFraming.TryGetProductBounds(root.transform, out Bounds bounds))
            {
                throw new InvalidDataException(
                    "The shipping Dragon Scale scene has no visible product bounds.");
            }

            const int width = 720;
            const int height = 1280;
            string folder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../Artifacts/DragonScaleCLIShippingPreview"));
            Directory.CreateDirectory(folder);
            var poses = new[]
            {
                new PreviewPose("01-authored-hero-42.png", 32f, 42f),
                new PreviewPose("02-top-89.png", 0f, 89f),
                new PreviewPose("03-left-oblique-35.png", -48f, 35f),
                new PreviewPose("04-right-oblique-35.png", 112f, 35f),
                new PreviewPose("05-low-angle-15.png", 32f, 15f)
            };
            ProductFramingProfile framing = ProductFramingCatalog.Resolve(ScenePath);
            Vector3 focusPoint = orbit.FocusPoint;
            Vector3 originalPosition = camera.transform.position;
            Quaternion originalRotation = camera.transform.rotation;
            float originalAspect = camera.aspect;
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            var target = new RenderTexture(
                width,
                height,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB)
            {
                antiAliasing = 4,
                name = "DragonScaleCLIShippingPreview"
            };
            var image = new Texture2D(
                width,
                height,
                TextureFormat.RGB24,
                false,
                false);

            try
            {
                target.Create();
                camera.aspect = (float)width / height;
                camera.targetTexture = target;
                camera.clearFlags = CameraClearFlags.SolidColor;
                camera.backgroundColor = Color.black;
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

                File.WriteAllText(
                    Path.Combine(folder, "README.txt"),
                    "Shipping scene: " + ScenePath + "\n"
                    + "Replaced slot: gold-four-wing only\n"
                    + "Protected products: pointed-three-blade, metal-three-blade\n"
                    + "Views: authored hero, top, left/right oblique, low angle\n"
                    + "Device installation: blocked pending explicit visual approval\n");
            }
            finally
            {
                camera.transform.SetPositionAndRotation(originalPosition, originalRotation);
                camera.aspect = originalAspect;
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                Object.DestroyImmediate(image);
                target.Release();
                Object.DestroyImmediate(target);
            }

            Debug.Log($"[ImportedSpinner] Shipping previews written: {folder}");
        }

        private static void Render(
            Camera camera,
            RenderTexture target,
            Texture2D image,
            string path)
        {
            RenderTexture.active = target;
            GL.Clear(true, true, Color.black);
            var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest
            {
                destination = target
            };
            UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
            RenderTexture.active = target;
            image.ReadPixels(new Rect(0f, 0f, image.width, image.height), 0, 0, false);
            image.Apply(false, false);
            File.WriteAllBytes(path, image.EncodeToPNG());
        }
    }
}
