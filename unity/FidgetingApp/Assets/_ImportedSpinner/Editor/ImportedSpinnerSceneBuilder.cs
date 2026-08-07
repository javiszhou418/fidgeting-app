using System.IO;
using FidgetingApp.Product;
using ThreeBladeEDC.Interaction;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.ImportedSpinner.EditorTools
{
    /// <summary>
    /// Builds the supplied one-piece FBX into the third product scene. The
    /// original 1.5M-triangle FBX remains an unreferenced source asset; the
    /// shipping scene references only the mobile runtime mesh.
    /// </summary>
    public static class ImportedSpinnerSceneBuilder
    {
        public const string ScenePath =
            "Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity";
        public const string RuntimeModelPath =
            "Assets/_ImportedSpinner/Models/ImportedSpinner_Runtime.obj";
        public const string SourceModelPath =
            "Assets/_ImportedSpinner/Models/ImportedSpinner.fbx";

        private const string BaseScenePath =
            "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity";
        private const string BlueScenePath =
            "Assets/Scenes/FidgetSpinnerDemo.unity";
        private const string TwoLobeScenePath =
            "Assets/_TwoLobeBar/Scenes/TwoLobeBar.unity";
        private const string EdcScenePath =
            "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const string MaterialFolder =
            "Assets/_ImportedSpinner/Materials";
        private const string MaterialPath =
            MaterialFolder + "/M_ImportedSpinnerMirrorSteel.mat";
        private const string MirrorReflectionPath =
            MaterialFolder + "/C_ImportedSpinnerMirrorStudio.asset";
        private const float MirrorSteelMetallic = 1f;
        private const float MirrorSteelSmoothness = 0.95f;
        private const float TargetPlanarDiameter = 0.122f;
        private const float TargetThickness = 0.014f;

        [MenuItem("Tools/Codex/Build Imported Spinner Third Model")]
        public static void BuildPresentation()
        {
            ConfigureRuntimeModelImporter();
            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(RuntimeModelPath);
            if (model == null)
            {
                throw new FileNotFoundException(
                    "Generate the mobile runtime OBJ before building the third spinner scene.",
                    RuntimeModelPath);
            }

            EnsureAssetFolder("Assets/_ImportedSpinner/Scenes");
            Material material = CreateOrUpdateMaterial();

            Scene scene = EditorSceneManager.OpenScene(BaseScenePath, OpenSceneMode.Single);
            GameObject root = GameObject.Find("ThreeBladeEDC_Root");
            if (root == null)
            {
                throw new InvalidDataException(
                    "The canonical metal scene no longer contains ThreeBladeEDC_Root.");
            }

            root.name = "ImportedSpinner_Root";
            Transform rotor = root.transform.Find("RotorDynamic");
            Transform hub = root.transform.Find("HubStatic");
            if (rotor == null || hub == null)
            {
                throw new InvalidDataException("The canonical rotor/hub scene contract changed.");
            }

            ClearChildren(rotor);
            DestroyChild(root.transform, "BearingVisual");
            DestroyChild(root.transform, "RatchetAudio");
            DestroyComponent<MetalGlintController>(root);
            DestroyComponent<ExplodedViewController>(root);
            DestroyComponent<SpinnerVariantSwitcher>(root);

            foreach (Collider collider in rotor.GetComponents<Collider>())
            {
                Object.DestroyImmediate(collider);
            }

            GameObject visual = (GameObject)PrefabUtility.InstantiatePrefab(model, scene);
            visual.name = "ImportedSpinnerVisual";
            visual.transform.SetParent(rotor, false);
            visual.transform.localPosition = Vector3.zero;
            visual.transform.localRotation = Quaternion.identity;
            visual.transform.localScale = Vector3.one;

            FitVisualToRotor(visual, rotor, material);

            BoxCollider touchCollider = rotor.gameObject.AddComponent<BoxCollider>();
            touchCollider.center = Vector3.zero;
            touchCollider.size = new Vector3(
                TargetPlanarDiameter * 1.08f,
                TargetThickness * 1.8f,
                TargetPlanarDiameter * 1.08f);

            // This FBX is one welded textured mesh, including its own center.
            // Hide the inherited generic hub so it cannot cover the supplied
            // model with an unrelated grey cap.
            hub.gameObject.SetActive(false);

            RotorRigidbodyController controller =
                rotor.GetComponent<RotorRigidbodyController>();
            if (controller == null || root.GetComponent<MobileGestureController>() == null)
            {
                throw new InvalidDataException(
                    "The imported scene must retain the canonical rotor and gesture pipeline.");
            }
            controller.CaptureInitialPose();

            OrbitPresentationCamera orbit =
                Object.FindAnyObjectByType<OrbitPresentationCamera>();
            if (orbit == null)
            {
                throw new InvalidDataException("The third spinner scene has no orbit camera.");
            }
            orbit.ConfigureFraming(ProductFramingCatalog.Resolve(ScenePath));

            foreach (Light light in root.GetComponentsInChildren<Light>(true))
            {
                light.useColorTemperature = false;
                switch (light.name)
                {
                    case "Key_5000K":
                        light.color = new Color(0.96f, 0.98f, 1f, 1f);
                        light.intensity = 0.72f;
                        break;
                    case "WarmRim_3200K":
                        light.color = new Color(0.88f, 0.93f, 1f, 1f);
                        light.intensity = 0.34f;
                        break;
                    case "CoolFill_6500K":
                        light.color = new Color(0.78f, 0.86f, 1f, 1f);
                        light.intensity = 0.42f;
                        break;
                }
            }
            ConfigureMirrorSteelStudio(root);

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ScenePath, true);
            SetProductBuildScenes();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log(
                $"[ImportedSpinner] Third model scene built: {ScenePath}; "
                + $"runtime={RuntimeModelPath}; source={SourceModelPath}");
        }

        private static void ConfigureRuntimeModelImporter()
        {
            AssetDatabase.ImportAsset(RuntimeModelPath, ImportAssetOptions.ForceSynchronousImport);
            ModelImporter importer = AssetImporter.GetAtPath(RuntimeModelPath) as ModelImporter;
            if (importer == null)
            {
                throw new FileNotFoundException("Runtime OBJ importer is missing.", RuntimeModelPath);
            }

            importer.globalScale = 1f;
            importer.useFileScale = false;
            importer.importAnimation = false;
            importer.importBlendShapes = false;
            importer.importCameras = false;
            importer.importLights = false;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            // Mirror reflections expose even tiny vertex/normal quantization.
            // Keep the optimized triangle count, but do not compress this one
            // hero mesh or the broad steel faces become visibly rippled.
            importer.meshCompression = ModelImporterMeshCompression.Off;
            importer.optimizeMeshPolygons = true;
            importer.optimizeMeshVertices = true;
            importer.weldVertices = true;
            importer.isReadable = false;
            importer.importNormals = ModelImporterNormals.Calculate;
            importer.normalCalculationMode = ModelImporterNormalCalculationMode.AreaAndAngleWeighted;
            importer.normalSmoothingSource = ModelImporterNormalSmoothingSource.FromAngle;
            importer.normalSmoothingAngle = 60f;
            importer.importTangents = ModelImporterTangents.CalculateMikk;
            importer.SaveAndReimport();
        }

        private static void FitVisualToRotor(
            GameObject visual,
            Transform rotor,
            Material material)
        {
            Renderer[] renderers = visual.GetComponentsInChildren<Renderer>(true);
            if (renderers.Length == 0)
            {
                throw new InvalidDataException("The mobile runtime model has no renderers.");
            }

            Bounds bounds = CombinedBounds(renderers);
            float planarSize = Mathf.Max(bounds.size.x, bounds.size.z);
            if (planarSize <= 0f || bounds.size.y <= 0f)
            {
                throw new InvalidDataException("The mobile runtime model has invalid bounds.");
            }

            float planarScale = TargetPlanarDiameter / planarSize;
            float verticalScale = Mathf.Min(planarScale, TargetThickness / bounds.size.y);
            visual.transform.localScale = new Vector3(planarScale, verticalScale, planarScale);

            bounds = CombinedBounds(renderers);
            visual.transform.position += rotor.position - bounds.center;

            foreach (Renderer renderer in renderers)
            {
                Material[] materials = new Material[renderer.sharedMaterials.Length];
                for (int index = 0; index < materials.Length; index++)
                {
                    materials[index] = material;
                }
                renderer.sharedMaterials = materials;
                renderer.shadowCastingMode = ShadowCastingMode.On;
                renderer.receiveShadows = true;
                renderer.lightProbeUsage = LightProbeUsage.Off;
                renderer.reflectionProbeUsage = ReflectionProbeUsage.BlendProbes;
                renderer.motionVectorGenerationMode = MotionVectorGenerationMode.ForceNoMotion;
            }
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

        private static Material CreateOrUpdateMaterial()
        {
            EnsureAssetFolder(MaterialFolder);
            Material material = AssetDatabase.LoadAssetAtPath<Material>(MaterialPath);
            if (material == null)
            {
                Shader shader = Shader.Find("Universal Render Pipeline/Lit");
                if (shader == null)
                {
                    throw new InvalidDataException("URP Lit shader is unavailable.");
                }
                material = new Material(shader) { name = "M_ImportedSpinnerMirrorSteel" };
                AssetDatabase.CreateAsset(material, MaterialPath);
            }

            // Mirror-polished stainless steel: deliberately texture-free so
            // there is no baked grain, scratch, noise or roughness variation.
            Color steel = new Color(0.76f, 0.78f, 0.81f, 1f);
            material.name = "M_ImportedSpinnerMirrorSteel";
            material.SetTexture("_BaseMap", null);
            material.SetTexture("_MainTex", null);
            material.SetTexture("_BumpMap", null);
            material.SetTexture("_MetallicGlossMap", null);
            material.SetTexture("_DetailAlbedoMap", null);
            material.SetTexture("_DetailNormalMap", null);
            material.SetColor("_BaseColor", steel);
            material.SetColor("_Color", steel);
            material.SetFloat("_BumpScale", 0f);
            material.SetFloat("_Metallic", MirrorSteelMetallic);
            material.SetFloat("_Smoothness", MirrorSteelSmoothness);
            material.SetFloat("_GlossMapScale", MirrorSteelSmoothness);
            material.SetFloat("_WorkflowMode", 1f);
            material.SetFloat("_ClearCoatMask", 0f);
            material.DisableKeyword("_NORMALMAP");
            material.DisableKeyword("_DETAIL_MULX2");
            material.DisableKeyword("_METALLICSPECGLOSSMAP");
            material.SetFloat("_EnvironmentReflections", 1f);
            material.SetFloat("_SpecularHighlights", 1f);
            EditorUtility.SetDirty(material);
            return material;
        }

        private static void ConfigureMirrorSteelStudio(GameObject root)
        {
            Cubemap reflection = CreateOrUpdateMirrorReflection();
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

        private static Cubemap CreateOrUpdateMirrorReflection()
        {
            const int size = 256;
            Cubemap reflection = AssetDatabase.LoadAssetAtPath<Cubemap>(MirrorReflectionPath);
            if (reflection == null)
            {
                reflection = new Cubemap(size, TextureFormat.RGBA32, true)
                {
                    name = "C_ImportedSpinnerMirrorStudio",
                    filterMode = FilterMode.Trilinear,
                    wrapMode = TextureWrapMode.Clamp
                };
                AssetDatabase.CreateAsset(reflection, MirrorReflectionPath);
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

                        // Continuous world-space studio cards. Unlike a
                        // face-local pattern, these do not repeat six times or
                        // break at cubemap seams when reflected by the steel.
                        float keyPanel = SoftRectangle(
                            azimuth,
                            elevation,
                            -0.82f,
                            0.08f,
                            0.20f,
                            0.72f);
                        float rimPanel = SoftRectangle(
                            azimuth,
                            elevation,
                            1.22f,
                            0.02f,
                            0.15f,
                            0.58f);
                        float overheadPanel = SoftRectangle(
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

                        Color baseColor = new Color(0.17f, 0.18f, 0.20f)
                            + new Color(0.06f, 0.07f, 0.085f) * horizon;
                        Color key = new Color(0.78f, 0.83f, 0.90f) * keyPanel * 0.72f;
                        Color rim = new Color(0.55f, 0.64f, 0.76f) * rimPanel * 0.44f;
                        Color overhead = new Color(0.70f, 0.75f, 0.84f)
                            * overheadPanel
                            * 0.34f;
                        pixels[y * size + x] = baseColor + key + rim + overhead;
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
            EditorBuildSettings.scenes = new[]
            {
                new EditorBuildSettingsScene(BlueScenePath, true),
                new EditorBuildSettingsScene(BaseScenePath, true),
                new EditorBuildSettingsScene(ScenePath, true),
                new EditorBuildSettingsScene(TwoLobeScenePath, true),
                new EditorBuildSettingsScene(EdcScenePath, true)
            };
        }

        private static void ClearChildren(Transform parent)
        {
            for (int index = parent.childCount - 1; index >= 0; index--)
            {
                Object.DestroyImmediate(parent.GetChild(index).gameObject);
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

        private static void DestroyComponent<T>(GameObject gameObject) where T : Component
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

        [MenuItem("Tools/Codex/Capture Imported Spinner Preview")]
        public static void CapturePreview()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            Camera camera = Camera.main;
            if (camera == null)
            {
                throw new InvalidDataException("The third spinner scene has no MainCamera.");
            }

            const int width = 900;
            const int height = 1600;
            string folder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../../../Artifacts/ImportedSpinner"));
            Directory.CreateDirectory(folder);
            string path = Path.Combine(folder, "imported-spinner-hero.png");

            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            var target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
            var image = new Texture2D(width, height, TextureFormat.RGBA32, false, false);
            try
            {
                camera.aspect = (float)width / height;
                camera.targetTexture = target;
                camera.Render();
                RenderTexture.active = target;
                image.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                image.Apply(false, false);
                File.WriteAllBytes(path, image.EncodeToPNG());
            }
            finally
            {
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                Object.DestroyImmediate(image);
                target.Release();
                Object.DestroyImmediate(target);
            }

            Debug.Log($"[ImportedSpinner] Preview written: {path}");
        }
    }
}
