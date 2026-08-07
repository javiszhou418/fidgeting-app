using System;
using System.IO;
using FidgetingApp.Product;
using FidgetingApp.TwoLobeBar.Geometry;
using ThreeBladeEDC.Interaction;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.TwoLobeBar.EditorTools
{
    public static class TwoLobeBarSceneBuilder
    {
        private const string BaseScenePath =
            "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity";
        private const string BlueScenePath =
            "Assets/Scenes/FidgetSpinnerDemo.unity";
        private const string ImportedScenePath =
            "Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity";
        private const string EdcScenePath =
            "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const string MeshFolder =
            "Assets/_TwoLobeBar/Generated/Meshes";
        private const string MaterialFolder =
            "Assets/_TwoLobeBar/Generated/Materials";
        private const string TextureFolder =
            "Assets/_TwoLobeBar/Generated/Textures";
        private const string BodyMaterialPath =
            MaterialFolder + "/M_TwoLobeGraphite.mat";
        private const string ButtonMaterialPath =
            MaterialFolder + "/M_TwoLobeButton.mat";
        private const string ShadowGapMaterialPath =
            MaterialFolder + "/M_TwoLobeShadowGap.mat";
        private const string BackdropMaterialPath =
            MaterialFolder + "/M_WarmDefocusedBackdrop.mat";
        private const string GrainNormalPath =
            TextureFolder + "/N_IsotropicBeadBlast.png";
        private const string BackdropTexturePath =
            TextureFolder + "/T_WarmDefocusedBackdrop.png";
        private const string ButtonOcclusionPath =
            TextureFolder + "/O_ButtonDishAO.png";
        private const string StudioReflectionPath =
            TextureFolder + "/C_MatteZirconiumStudio.asset";
        private const string BodyMeshPath =
            MeshFolder + "/M_TwoLobeBarBody.asset";
        private const string ButtonMeshPath =
            MeshFolder + "/M_TwoLobeConcaveButton.asset";
        private const string ShadowGapMeshPath =
            MeshFolder + "/M_TwoLobeUndercutShadowCollar.asset";

        [MenuItem("Tools/Codex/Build Graphite Two-Lobe Spinner")]
        public static void BuildPresentation()
        {
            EnsureFolders();
            Texture2D grainNormal = CreateOrUpdateGrainNormal();
            Texture2D backdropTexture = CreateOrUpdateBackdropTexture();
            Texture2D buttonOcclusion = CreateOrUpdateButtonOcclusion();
            Cubemap studioReflection = CreateOrUpdateStudioReflection();
            Material bodyMaterial = CreateOrUpdateBodyMaterial(grainNormal);
            Material buttonMaterial = CreateOrUpdateButtonMaterial(
                grainNormal,
                buttonOcclusion);
            Material shadowGapMaterial = CreateOrUpdateShadowGapMaterial();
            Material backdropMaterial = CreateOrUpdateBackdropMaterial(backdropTexture);
            Mesh bodyMesh = SaveMesh(
                TwoLobeBarMeshFactory.CreateBody(),
                BodyMeshPath);
            Mesh buttonMesh = SaveMesh(
                TwoLobeBarMeshFactory.CreateConcaveButton(),
                ButtonMeshPath);
            Mesh shadowGapMesh = SaveMesh(
                TwoLobeBarMeshFactory.CreateUndercutShadowCollar(),
                ShadowGapMeshPath);

            Scene scene = EditorSceneManager.OpenScene(
                BaseScenePath,
                OpenSceneMode.Single);
            GameObject root = GameObject.Find("ThreeBladeEDC_Root");
            if (root == null)
            {
                throw new InvalidDataException(
                    "The canonical metal scene no longer contains ThreeBladeEDC_Root.");
            }

            root.name = "TwoLobeBar_Root";
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
            DestroyChild(root.transform, "RatchetAudio");
            DestroyChild(root.transform, "MobileCanvas");
            DestroyChild(root.transform, "EventSystem");
            DestroyComponent<MetalGlintController>(root);
            DestroyComponent<ExplodedViewController>(root);
            DestroyComponent<SpinnerVariantSwitcher>(root);

            foreach (Collider collider in rotor.GetComponents<Collider>())
            {
                UnityEngine.Object.DestroyImmediate(collider);
            }

            GameObject body = CreateBody(
                rotor,
                bodyMesh,
                bodyMaterial);

            GameObject axle = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            axle.name = "Axle";
            axle.transform.SetParent(hub, false);
            axle.transform.localScale = new Vector3(
                0.0045f,
                TwoLobeBarSpecifications.BodyThickness * 0.5f,
                0.0045f);
            axle.GetComponent<MeshRenderer>().sharedMaterial = bodyMaterial;
            UnityEngine.Object.DestroyImmediate(axle.GetComponent<Collider>());

            GameObject topButton = CreateButton(
                "TopButton",
                hub,
                buttonMesh,
                buttonMaterial,
                false);
            CreateMeshObject(
                "UndercutShadowGap",
                topButton.transform,
                shadowGapMesh,
                shadowGapMaterial);
            topButton.transform.localPosition = Vector3.up
                * (TwoLobeBarSpecifications.BodyThickness * 0.5f
                    - TwoLobeBarSpecifications.ButtonUndercutSink);
            topButton.AddComponent<SpinnerTouchSurface>();
            AddButtonTouchCollider(topButton);

            GameObject bottomButton = CreateButton(
                "BottomButton",
                hub,
                buttonMesh,
                buttonMaterial,
                true);
            CreateMeshObject(
                "UndercutShadowGap",
                bottomButton.transform,
                shadowGapMesh,
                shadowGapMaterial);
            bottomButton.transform.localPosition = Vector3.down
                * (TwoLobeBarSpecifications.BodyThickness * 0.5f
                    - TwoLobeBarSpecifications.ButtonUndercutSink);

            Rigidbody rotorBody = rotor.GetComponent<Rigidbody>();
            RotorRigidbodyController rotorController =
                rotor.GetComponent<RotorRigidbodyController>();
            MobileGestureController gestures =
                root.GetComponent<MobileGestureController>();
            if (rotorBody == null || rotorController == null || gestures == null)
            {
                throw new InvalidDataException(
                    "The two-lobe scene must retain the canonical interaction pipeline.");
            }

            rotorBody.mass = 0.095f;
            rotorBody.angularVelocity = Vector3.zero;
            rotorBody.linearVelocity = Vector3.zero;

            ExplodedViewController exploded =
                root.AddComponent<ExplodedViewController>();
            exploded.Configure(
                rotorBody,
                new[]
                {
                    Part(topButton.transform, new Vector3(0f, 0.032f, 0f)),
                    Part(rotor, new Vector3(0f, 0.013f, 0f)),
                    Part(bottomButton.transform, new Vector3(0f, -0.032f, 0f))
                });

            ConfigureStudio(
                root,
                backdropMaterial,
                studioReflection,
                out Camera camera);
            OrbitPresentationCamera orbit =
                camera.GetComponent<OrbitPresentationCamera>();
            if (orbit == null)
            {
                orbit = camera.gameObject.AddComponent<OrbitPresentationCamera>();
            }
            orbit.Target = root.transform;
            orbit.ConfigureFraming(ProductFramingCatalog.Resolve(
                TwoLobeBarSpecifications.ScenePath));
            orbit.SetDesktopInputEnabled(false);
            gestures.Configure(rotorController, camera, orbit);

            rotorController.CaptureInitialPose();
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(
                scene,
                TwoLobeBarSpecifications.ScenePath,
                true);
            SetProductBuildScenes();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log(
                "[TwoLobeBar] Built 50 x 18 x 13 mm graphite spinner; "
                + $"body={body.name}; crownExponent="
                + $"{TwoLobeBarSpecifications.BodyCrownExponent:F1}; "
                + $"scene={TwoLobeBarSpecifications.ScenePath}");
        }

        [MenuItem("Tools/Codex/Build and Capture Graphite Two-Lobe Spinner")]
        public static void BuildAndRenderPreview()
        {
            BuildPresentation();
            Scene scene = EditorSceneManager.OpenScene(
                TwoLobeBarSpecifications.ScenePath,
                OpenSceneMode.Single);
            Camera camera = Camera.main;
            if (camera == null)
            {
                throw new MissingReferenceException(
                    "The graphite two-lobe scene has no Main Camera.");
            }

            string outputFolder = Path.GetFullPath(Path.Combine(
                Directory.GetParent(Application.dataPath).FullName,
                "../../Artifacts/TwoLobeBar"));
            try
            {
                Directory.CreateDirectory(outputFolder);
            }
            catch (UnauthorizedAccessException)
            {
                outputFolder = Path.Combine(
                    Directory.GetParent(Application.dataPath).FullName,
                    "Artifacts/TwoLobeBar");
                Directory.CreateDirectory(outputFolder);
            }
            string outputPath = Path.Combine(outputFolder, "two-lobe-bar-hero.png");
            RenderCameraToPng(camera, outputPath);
            Debug.Log($"[TwoLobeBar] Hero preview written: {outputPath}; scene={scene.path}");
        }

        [MenuItem("Tools/Codex/Capture Graphite Two-Lobe Exploded View")]
        public static void BuildAndRenderExplodedPreview()
        {
            BuildPresentation();
            Scene scene = EditorSceneManager.OpenScene(
                TwoLobeBarSpecifications.ScenePath,
                OpenSceneMode.Single);
            GameObject root = GameObject.Find("TwoLobeBar_Root");
            Camera camera = Camera.main;
            if (root == null || camera == null)
            {
                throw new MissingReferenceException(
                    "The graphite two-lobe scene is missing its root or Main Camera.");
            }

            Transform rotor = root.transform.Find("RotorDynamic");
            Transform hub = root.transform.Find("HubStatic");
            Transform body = rotor?.Find("Body");
            Transform axle = hub?.Find("Axle");
            Transform topButton = hub?.Find("TopButton");
            Transform bottomButton = hub?.Find("BottomButton");
            if (body == null || axle == null
                || topButton == null || bottomButton == null)
            {
                throw new MissingReferenceException(
                    "The graphite two-lobe exploded view requires its one-piece body, axle and buttons.");
            }

            // Keep the rotor as one indivisible bar. Only the stationary caps
            // separate along the bearing axis in this exterior-only diagram.
            body.localPosition = Vector3.zero;
            axle.localPosition = Vector3.zero;
            topButton.localPosition = Vector3.up * 0.055f;
            bottomButton.localPosition = Vector3.down * 0.055f;

            OrbitPresentationCamera orbit = camera.GetComponent<OrbitPresentationCamera>();
            if (orbit != null)
            {
                orbit.enabled = false;
            }
            Vector3 target = root.transform.position;
            camera.usePhysicalProperties = false;
            camera.orthographic = true;
            camera.orthographicSize = 0.080f;
            camera.transform.position = target + new Vector3(0.14f, 0.095f, -0.17f);
            camera.transform.LookAt(target);

            string outputFolder = Path.GetFullPath(Path.Combine(
                Directory.GetParent(Application.dataPath).FullName,
                "../../Artifacts/TwoLobeBar"));
            try
            {
                Directory.CreateDirectory(outputFolder);
            }
            catch (UnauthorizedAccessException)
            {
                outputFolder = Path.Combine(
                    Directory.GetParent(Application.dataPath).FullName,
                    "Artifacts/TwoLobeBar");
                Directory.CreateDirectory(outputFolder);
            }
            string outputPath = Path.Combine(
                outputFolder,
                "two-lobe-bar-exploded.png");
            RenderCameraToPng(camera, outputPath);
            Debug.Log(
                $"[TwoLobeBar] Exploded preview written: {outputPath}; scene={scene.path}");
        }

        [MenuItem("Tools/Codex/Capture Two-Lobe Crown Calibration")]
        public static void BuildAndRenderCrownCalibration()
        {
            BuildPresentation();
            Scene scene = EditorSceneManager.OpenScene(
                TwoLobeBarSpecifications.ScenePath,
                OpenSceneMode.Single);
            GameObject root = GameObject.Find("TwoLobeBar_Root");
            Camera camera = Camera.main;
            if (root == null || camera == null)
            {
                throw new MissingReferenceException(
                    "The graphite two-lobe scene is missing its root or Main Camera.");
            }

            OrbitPresentationCamera orbit = camera.GetComponent<OrbitPresentationCamera>();
            if (orbit != null)
            {
                orbit.enabled = false;
            }

            string outputFolder = Path.GetFullPath(Path.Combine(
                Directory.GetParent(Application.dataPath).FullName,
                "../../Artifacts/TwoLobeBar/CurveCalibration"));
            try
            {
                Directory.CreateDirectory(outputFolder);
            }
            catch (UnauthorizedAccessException)
            {
                outputFolder = Path.Combine(
                    Directory.GetParent(Application.dataPath).FullName,
                    "Artifacts/TwoLobeBar/CurveCalibration");
                Directory.CreateDirectory(outputFolder);
            }

            Vector3 target = root.transform.position;
            camera.usePhysicalProperties = false;
            camera.orthographic = true;
            camera.orthographicSize = 0.034f;

            camera.transform.position = target + Vector3.up * 0.20f;
            camera.transform.rotation = Quaternion.LookRotation(
                Vector3.down,
                Vector3.forward);
            RenderCameraToPng(
                camera,
                Path.Combine(outputFolder, "01-crowned-face.png"));

            camera.transform.position = target + Vector3.right * 0.20f;
            camera.transform.rotation = Quaternion.LookRotation(
                Vector3.left,
                Vector3.up);
            RenderCameraToPng(
                camera,
                Path.Combine(outputFolder, "02-crowned-side.png"));

            // Stay predominantly above the object. The former low/end-on
            // camera foreshortened the 50 mm bar and made it look stubby.
            camera.transform.position = target + new Vector3(0.070f, 0.180f, -0.045f);
            camera.transform.LookAt(target);
            camera.orthographicSize = 0.035f;
            RenderCameraToPng(
                camera,
                Path.Combine(outputFolder, "03-crowned-three-quarter.png"));

            // Low close-up dedicated to the physical undercut. This angle
            // exposes the recessed neck and the real shadow under the disc.
            camera.transform.position = target + new Vector3(0.055f, 0.058f, -0.040f);
            camera.transform.LookAt(target + Vector3.up * 0.005f);
            camera.orthographicSize = 0.025f;
            RenderCameraToPng(
                camera,
                Path.Combine(outputFolder, "04-undercut-closeup.png"));

            Debug.Log(
                $"[TwoLobeBar] Crown calibration written: {outputFolder}; scene={scene.path}");
        }

        private static GameObject CreateBody(
            Transform rotor,
            Mesh mesh,
            Material material)
        {
            GameObject body = CreateMeshObject("Body", rotor, mesh, material);
            BoxCollider collider = body.AddComponent<BoxCollider>();
            collider.center = Vector3.zero;
            collider.size = new Vector3(
                TwoLobeBarSpecifications.BodyWidth,
                TwoLobeBarSpecifications.BodyThickness,
                TwoLobeBarSpecifications.BodyLength);
            return body;
        }

        private static GameObject CreateButton(
            string name,
            Transform hub,
            Mesh mesh,
            Material material,
            bool flipped)
        {
            GameObject button = CreateMeshObject(name, hub, mesh, material);
            if (flipped)
            {
                button.transform.localRotation = Quaternion.Euler(180f, 0f, 0f);
            }
            return button;
        }

        private static void AddButtonTouchCollider(GameObject button)
        {
            BoxCollider collider = button.AddComponent<BoxCollider>();
            collider.center = Vector3.up
                * (TwoLobeBarSpecifications.ButtonProudHeight * 0.5f);
            collider.size = new Vector3(
                TwoLobeBarSpecifications.ButtonDiameter,
                TwoLobeBarSpecifications.ButtonProudHeight,
                TwoLobeBarSpecifications.ButtonDiameter);
        }

        private static GameObject CreateMeshObject(
            string name,
            Transform parent,
            Mesh mesh,
            Material material)
        {
            GameObject gameObject = new GameObject(name);
            gameObject.transform.SetParent(parent, false);
            gameObject.AddComponent<MeshFilter>().sharedMesh = mesh;
            MeshRenderer renderer = gameObject.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.On;
            renderer.receiveShadows = true;
            renderer.lightProbeUsage = LightProbeUsage.Off;
            return gameObject;
        }

        private static void ConfigureStudio(
            GameObject root,
            Material backdropMaterial,
            Cubemap studioReflection,
            out Camera camera)
        {
            Transform studio = root.transform.Find("Studio");
            if (studio == null)
            {
                GameObject studioObject = new GameObject("Studio");
                studioObject.transform.SetParent(root.transform, false);
                studio = studioObject.transform;
            }

            foreach (Light light in studio.GetComponentsInChildren<Light>(true))
            {
                UnityEngine.Object.DestroyImmediate(light.gameObject);
            }
            DestroyChild(studio, "StudioFloor");
            DestroyChild(studio, "StudioReflectionProbe");

            camera = studio.GetComponentInChildren<Camera>(true);
            if (camera == null)
            {
                camera = new GameObject("HeroCamera").AddComponent<Camera>();
                camera.transform.SetParent(studio, false);
                camera.tag = "MainCamera";
            }

            Vector3 target = root.transform.position;
            camera.transform.position = target + new Vector3(0.050f, 0.145f, -0.040f);
            camera.transform.LookAt(target);
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.22f, 0.17f, 0.13f, 1f);
            camera.allowHDR = false;
            camera.allowMSAA = true;
            camera.usePhysicalProperties = true;
            camera.focalLength = 75f;
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 10f;

            Transform existingBackdrop = camera.transform.Find("WarmDefocusedBackdrop");
            if (existingBackdrop != null)
            {
                UnityEngine.Object.DestroyImmediate(existingBackdrop.gameObject);
            }

            GameObject backdrop = GameObject.CreatePrimitive(PrimitiveType.Quad);
            backdrop.name = "WarmDefocusedBackdrop";
            backdrop.transform.SetParent(camera.transform, false);
            backdrop.transform.localPosition = new Vector3(0f, 0f, 2f);
            backdrop.transform.localRotation = Quaternion.identity;
            backdrop.transform.localScale = new Vector3(4f, 2.5f, 1f);
            UnityEngine.Object.DestroyImmediate(backdrop.GetComponent<Collider>());
            MeshRenderer backdropRenderer = backdrop.GetComponent<MeshRenderer>();
            backdropRenderer.sharedMaterial = backdropMaterial;
            backdropRenderer.shadowCastingMode = ShadowCastingMode.Off;
            backdropRenderer.receiveShadows = false;
            backdropRenderer.lightProbeUsage = LightProbeUsage.Off;
            backdropRenderer.reflectionProbeUsage = ReflectionProbeUsage.Off;

            Light key = new GameObject("LargeSoftAreaKey_UpperLeft").AddComponent<Light>();
            key.transform.SetParent(studio, true);
            key.transform.position = target + new Vector3(-0.18f, 0.23f, -0.16f);
            key.transform.LookAt(target);
            // URP does not render realtime rectangular area lights. A broad
            // soft-shadow spot is the realtime mobile equivalent.
            key.type = LightType.Spot;
            key.useColorTemperature = true;
            key.colorTemperature = 5100f;
            key.intensity = 0.82f;
            key.range = 1.4f;
            key.spotAngle = 82f;
            key.innerSpotAngle = 62f;
            key.shadows = LightShadows.Soft;
            key.shadowStrength = 0.52f;
            key.shadowBias = 0.025f;
            key.shadowNormalBias = 0.22f;

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.18f, 0.20f, 0.22f);
            RenderSettings.ambientEquatorColor = new Color(0.085f, 0.090f, 0.098f);
            RenderSettings.ambientGroundColor = new Color(0.030f, 0.026f, 0.023f);
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflection = studioReflection;
            RenderSettings.reflectionIntensity = 0.62f;
        }

        private static Material CreateOrUpdateBodyMaterial(Texture2D grainNormal)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null)
            {
                throw new MissingReferenceException("URP Lit shader is unavailable.");
            }

            Material material = AssetDatabase.LoadAssetAtPath<Material>(BodyMaterialPath);
            if (material == null)
            {
                material = new Material(shader) { name = "M_TwoLobeGraphite" };
                AssetDatabase.CreateAsset(material, BodyMaterialPath);
            }
            else
            {
                material.shader = shader;
            }

            ConfigureGraphiteMaterial(material, grainNormal);
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Material CreateOrUpdateButtonMaterial(
            Texture2D grainNormal,
            Texture2D occlusion)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null)
            {
                throw new MissingReferenceException("URP Lit shader is unavailable.");
            }

            Material material = AssetDatabase.LoadAssetAtPath<Material>(ButtonMaterialPath);
            if (material == null)
            {
                material = new Material(shader) { name = "M_TwoLobeButton" };
                AssetDatabase.CreateAsset(material, ButtonMaterialPath);
            }
            else
            {
                material.shader = shader;
            }

            ConfigureGraphiteMaterial(material, grainNormal);
            material.SetTexture("_OcclusionMap", occlusion);
            material.SetFloat("_OcclusionStrength", 1f);
            material.EnableKeyword("_OCCLUSIONMAP");
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Material CreateOrUpdateShadowGapMaterial()
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null)
            {
                throw new MissingReferenceException("URP Lit shader is unavailable.");
            }

            Material material = AssetDatabase.LoadAssetAtPath<Material>(
                ShadowGapMaterialPath);
            if (material == null)
            {
                material = new Material(shader) { name = "M_TwoLobeShadowGap" };
                AssetDatabase.CreateAsset(material, ShadowGapMaterialPath);
            }
            else
            {
                material.shader = shader;
            }

            Color shadowColor = new Color32(0x10, 0x12, 0x13, 0xFF);
            material.SetColor("_BaseColor", shadowColor);
            material.SetColor("_Color", shadowColor);
            material.SetFloat("_Metallic", 0.72f);
            material.SetFloat("_Smoothness", 0.12f);
            material.SetFloat("_SpecularHighlights", 0.35f);
            material.SetFloat("_EnvironmentReflections", 0.35f);
            material.enableInstancing = true;
            EditorUtility.SetDirty(material);
            return material;
        }

        private static void ConfigureGraphiteMaterial(
            Material material,
            Texture2D grainNormal)
        {
            material.SetColor("_BaseColor", TwoLobeBarSpecifications.BodyBaseColor);
            material.SetColor("_Color", TwoLobeBarSpecifications.BodyBaseColor);
            material.SetFloat("_Metallic", TwoLobeBarSpecifications.Metallic);
            material.SetFloat("_Smoothness", TwoLobeBarSpecifications.Smoothness);
            material.SetFloat("_SpecularHighlights", 1f);
            material.SetFloat("_EnvironmentReflections", 1f);
            material.SetTexture("_BumpMap", grainNormal);
            material.SetTextureScale("_BumpMap", new Vector2(54f, 54f));
            material.SetFloat("_BumpScale", 0.14f);
            material.EnableKeyword("_NORMALMAP");
            material.enableInstancing = true;
        }

        private static Material CreateOrUpdateBackdropMaterial(Texture2D texture)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Unlit");
            if (shader == null)
            {
                throw new MissingReferenceException("URP Unlit shader is unavailable.");
            }

            Material material = AssetDatabase.LoadAssetAtPath<Material>(BackdropMaterialPath);
            if (material == null)
            {
                material = new Material(shader) { name = "M_WarmDefocusedBackdrop" };
                AssetDatabase.CreateAsset(material, BackdropMaterialPath);
            }
            else
            {
                material.shader = shader;
            }

            material.SetColor("_BaseColor", Color.white);
            material.SetTexture("_BaseMap", texture);
            material.SetFloat("_Surface", 0f);
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Texture2D CreateOrUpdateGrainNormal()
        {
            int size = TwoLobeBarSpecifications.GrainTextureSize;
            var random = new System.Random(0x2B10BE);
            float[,] heights = new float[size, size];
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    heights[x, y] = (float)random.NextDouble();
                }
            }

            for (int pass = 0; pass < 2; pass++)
            {
                float[,] blurred = new float[size, size];
                for (int y = 0; y < size; y++)
                {
                    for (int x = 0; x < size; x++)
                    {
                        float sum = 0f;
                        for (int oy = -1; oy <= 1; oy++)
                        {
                            for (int ox = -1; ox <= 1; ox++)
                            {
                                int sx = (x + ox + size) % size;
                                int sy = (y + oy + size) % size;
                                sum += heights[sx, sy];
                            }
                        }
                        blurred[x, y] = sum / 9f;
                    }
                }
                heights = blurred;
            }

            var texture = new Texture2D(size, size, TextureFormat.RGBA32, false, true);
            var pixels = new Color[size * size];
            const float normalStrength = 1.0f;
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    float left = heights[(x - 1 + size) % size, y];
                    float right = heights[(x + 1) % size, y];
                    float down = heights[x, (y - 1 + size) % size];
                    float up = heights[x, (y + 1) % size];
                    Vector3 normal = new Vector3(
                        (left - right) * normalStrength,
                        (down - up) * normalStrength,
                        1f).normalized;
                    pixels[y * size + x] = new Color(
                        normal.x * 0.5f + 0.5f,
                        normal.y * 0.5f + 0.5f,
                        normal.z * 0.5f + 0.5f,
                        1f);
                }
            }
            texture.SetPixels(pixels);
            texture.Apply(false, false);
            WriteTexturePng(texture, GrainNormalPath);
            UnityEngine.Object.DestroyImmediate(texture);

            AssetDatabase.ImportAsset(GrainNormalPath, ImportAssetOptions.ForceSynchronousImport);
            TextureImporter importer = AssetImporter.GetAtPath(GrainNormalPath) as TextureImporter;
            if (importer == null)
            {
                throw new FileNotFoundException("Generated bead-blast normal failed to import.");
            }
            importer.textureType = TextureImporterType.NormalMap;
            importer.sRGBTexture = false;
            importer.wrapMode = TextureWrapMode.Repeat;
            importer.filterMode = FilterMode.Trilinear;
            importer.mipmapEnabled = true;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.maxTextureSize = size;
            importer.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(GrainNormalPath);
        }

        private static Texture2D CreateOrUpdateBackdropTexture()
        {
            const int width = 512;
            const int height = 320;
            var texture = new Texture2D(width, height, TextureFormat.RGB24, false, false);
            var pixels = new Color[width * height];
            Color top = new Color(0.28f, 0.23f, 0.19f);
            Color bottom = new Color(0.11f, 0.085f, 0.070f);
            for (int y = 0; y < height; y++)
            {
                float v = y / (float)(height - 1);
                for (int x = 0; x < width; x++)
                {
                    float u = x / (float)(width - 1);
                    Color color = Color.Lerp(bottom, top, Mathf.SmoothStep(0f, 1f, v));
                    float warmWindow = Gaussian(u, v, 0.28f, 0.69f, 0.24f);
                    float amberBlur = Gaussian(u, v, 0.76f, 0.42f, 0.33f);
                    float coolEdge = Gaussian(u, v, 0.06f, 0.48f, 0.22f);
                    color += new Color(0.24f, 0.15f, 0.075f) * warmWindow;
                    color += new Color(0.12f, 0.075f, 0.040f) * amberBlur;
                    color += new Color(0.035f, 0.045f, 0.052f) * coolEdge;
                    pixels[y * width + x] = color;
                }
            }
            texture.SetPixels(pixels);
            texture.Apply(false, false);
            WriteTexturePng(texture, BackdropTexturePath);
            UnityEngine.Object.DestroyImmediate(texture);

            AssetDatabase.ImportAsset(
                BackdropTexturePath,
                ImportAssetOptions.ForceSynchronousImport);
            TextureImporter importer =
                AssetImporter.GetAtPath(BackdropTexturePath) as TextureImporter;
            if (importer == null)
            {
                throw new FileNotFoundException("Generated warm backdrop failed to import.");
            }
            importer.textureType = TextureImporterType.Default;
            importer.sRGBTexture = true;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.filterMode = FilterMode.Bilinear;
            importer.mipmapEnabled = false;
            importer.textureCompression = TextureImporterCompression.Compressed;
            importer.maxTextureSize = width;
            importer.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(BackdropTexturePath);
        }

        private static Cubemap CreateOrUpdateStudioReflection()
        {
            const int size = 32;
            Cubemap cubemap = AssetDatabase.LoadAssetAtPath<Cubemap>(
                StudioReflectionPath);
            if (cubemap == null)
            {
                cubemap = new Cubemap(size, TextureFormat.RGBA32, true)
                {
                    name = "C_MatteZirconiumStudio"
                };
                AssetDatabase.CreateAsset(cubemap, StudioReflectionPath);
            }

            Color[] faceColors =
            {
                new Color(0.40f, 0.39f, 0.37f),
                new Color(0.26f, 0.29f, 0.32f),
                new Color(0.48f, 0.50f, 0.51f),
                new Color(0.055f, 0.050f, 0.047f),
                new Color(0.19f, 0.20f, 0.21f),
                new Color(0.31f, 0.27f, 0.23f)
            };
            for (int faceIndex = 0; faceIndex < 6; faceIndex++)
            {
                var pixels = new Color[size * size];
                for (int y = 0; y < size; y++)
                {
                    float v = y / (float)(size - 1);
                    for (int x = 0; x < size; x++)
                    {
                        float u = x / (float)(size - 1);
                        float softPanel = Gaussian(
                            u,
                            v,
                            0.28f,
                            0.74f,
                            0.48f);
                        pixels[y * size + x] = faceColors[faceIndex]
                            * Mathf.Lerp(0.70f, 1.18f, softPanel);
                    }
                }
                cubemap.SetPixels(pixels, (CubemapFace)faceIndex, 0);
            }
            cubemap.Apply(true, false);
            EditorUtility.SetDirty(cubemap);
            return cubemap;
        }

        private static Texture2D CreateOrUpdateButtonOcclusion()
        {
            const int size = 128;
            var texture = new Texture2D(size, size, TextureFormat.RGB24, false, true);
            var pixels = new Color[size * size];
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    float nx = (x + 0.5f) / size * 2f - 1f;
                    float ny = (y + 0.5f) / size * 2f - 1f;
                    float radius = Mathf.Sqrt(nx * nx + ny * ny);
                    float dish = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(radius / 0.90f));
                    float value = Mathf.Lerp(0.58f, 1f, dish);
                    pixels[y * size + x] = new Color(value, value, value, 1f);
                }
            }
            texture.SetPixels(pixels);
            texture.Apply(false, false);
            WriteTexturePng(texture, ButtonOcclusionPath);
            UnityEngine.Object.DestroyImmediate(texture);

            AssetDatabase.ImportAsset(
                ButtonOcclusionPath,
                ImportAssetOptions.ForceSynchronousImport);
            TextureImporter importer =
                AssetImporter.GetAtPath(ButtonOcclusionPath) as TextureImporter;
            if (importer == null)
            {
                throw new FileNotFoundException("Generated button AO failed to import.");
            }
            importer.textureType = TextureImporterType.Default;
            importer.sRGBTexture = false;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.filterMode = FilterMode.Bilinear;
            importer.mipmapEnabled = true;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.maxTextureSize = size;
            importer.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(ButtonOcclusionPath);
        }

        private static float Gaussian(
            float x,
            float y,
            float centerX,
            float centerY,
            float radius)
        {
            float dx = x - centerX;
            float dy = y - centerY;
            return Mathf.Exp(-(dx * dx + dy * dy) / (radius * radius));
        }

        private static void WriteTexturePng(Texture2D texture, string assetPath)
        {
            string projectFolder = Directory.GetParent(Application.dataPath).FullName;
            string fullPath = Path.Combine(projectFolder, assetPath);
            File.WriteAllBytes(fullPath, texture.EncodeToPNG());
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

        private static Mesh SaveMesh(Mesh generated, string path)
        {
            Mesh existing = AssetDatabase.LoadAssetAtPath<Mesh>(path);
            if (existing == null)
            {
                AssetDatabase.CreateAsset(generated, path);
                return generated;
            }

            EditorUtility.CopySerialized(generated, existing);
            UnityEngine.Object.DestroyImmediate(generated);
            EditorUtility.SetDirty(existing);
            return existing;
        }

        private static void EnsureFolders()
        {
            EnsureAssetFolder("Assets/_TwoLobeBar");
            EnsureAssetFolder("Assets/_TwoLobeBar/Generated");
            EnsureAssetFolder(MeshFolder);
            EnsureAssetFolder(MaterialFolder);
            EnsureAssetFolder(TextureFolder);
            EnsureAssetFolder("Assets/_TwoLobeBar/Scenes");
        }

        private static void EnsureAssetFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path))
            {
                return;
            }

            string parent = Path.GetDirectoryName(path)?.Replace('\\', '/');
            string child = Path.GetFileName(path);
            if (string.IsNullOrEmpty(parent) || string.IsNullOrEmpty(child))
            {
                throw new InvalidDataException($"Invalid asset folder path: {path}");
            }
            EnsureAssetFolder(parent);
            AssetDatabase.CreateFolder(parent, child);
        }

        private static void ClearChildren(Transform parent)
        {
            for (int index = parent.childCount - 1; index >= 0; index--)
            {
                UnityEngine.Object.DestroyImmediate(parent.GetChild(index).gameObject);
            }
        }

        private static void DestroyChild(Transform parent, string childName)
        {
            Transform child = parent.Find(childName);
            if (child != null)
            {
                UnityEngine.Object.DestroyImmediate(child.gameObject);
            }
        }

        private static void DestroyComponent<T>(GameObject owner) where T : Component
        {
            T component = owner.GetComponent<T>();
            if (component != null)
            {
                UnityEngine.Object.DestroyImmediate(component);
            }
        }

        private static void SetProductBuildScenes()
        {
            EditorBuildSettings.scenes = new[]
            {
                new EditorBuildSettingsScene(BlueScenePath, true),
                new EditorBuildSettingsScene(BaseScenePath, true),
                new EditorBuildSettingsScene(ImportedScenePath, true),
                new EditorBuildSettingsScene(TwoLobeBarSpecifications.ScenePath, true),
                new EditorBuildSettingsScene(EdcScenePath, true)
            };
        }

        private static void RenderCameraToPng(Camera camera, string path)
        {
            const int width = 1200;
            const int height = 1200;
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            float previousAspect = camera.aspect;
            var target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32)
            {
                antiAliasing = 4
            };
            var image = new Texture2D(width, height, TextureFormat.RGB24, false);
            try
            {
                target.Create();
                camera.aspect = 1f;
                camera.targetTexture = target;
                camera.Render();
                RenderTexture.active = target;
                image.ReadPixels(new Rect(0f, 0f, width, height), 0, 0);
                image.Apply(false, false);
                File.WriteAllBytes(path, image.EncodeToPNG());
            }
            finally
            {
                camera.targetTexture = previousTarget;
                camera.aspect = previousAspect;
                RenderTexture.active = previousActive;
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
                UnityEngine.Object.DestroyImmediate(image);
            }
        }
    }
}
