using CodexUnityLab;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace CodexUnityLabEditor
{
    public static class FidgetSpinnerBuilder
    {
        private const string ScenePath = "Assets/Scenes/FidgetSpinnerDemo.unity";
        private const string MetalScenePath = "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity";
        private const string ImportedScenePath =
            "Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity";
        private const string TwoLobeScenePath =
            "Assets/_TwoLobeBar/Scenes/TwoLobeBar.unity";
        private const string EdcScenePath =
            "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const string FanCardScenePath =
            "Assets/_FanCard/Scenes/MagneticFanCard.unity";
        private const string PrefabPath = "Assets/Prefabs/FidgetSpinner.prefab";
        private const string MaterialFolder = "Assets/Materials/FidgetSpinner";
        private const string ModelFolder = "Assets/Models/FidgetSpinner";

        [MenuItem("Tools/Codex/Create Fidget Spinner Demo")]
        public static void BuildDemoScene()
        {
            EnsureProjectFolders();

            Material bodyMaterial = CreateMaterial(
                $"{MaterialFolder}/SpinnerBody.mat",
                new Color(0.025f, 0.31f, 0.95f),
                0.42f,
                0.82f);
            Material metalMaterial = CreateMaterial(
                $"{MaterialFolder}/BearingMetal.mat",
                new Color(0.56f, 0.62f, 0.70f),
                0.92f,
                0.94f);
            Material darkMaterial = CreateMaterial(
                $"{MaterialFolder}/BearingShield.mat",
                new Color(0.018f, 0.022f, 0.032f),
                0.55f,
                0.72f);
            Material spatialSkybox = CreateSpatialSkyboxMaterial(
                $"{MaterialFolder}/SpatialSkybox.mat");

            Mesh bodyRingMesh = CreateOrReplaceMeshAsset(
                $"{ModelFolder}/BodyRing.asset",
                CreateTorusMesh("BodyRing", 0.68f, 0.28f, 40, 14));
            Mesh bearingRingMesh = CreateOrReplaceMeshAsset(
                $"{ModelFolder}/BearingRing.asset",
                CreateTorusMesh("BearingRing", 0.34f, 0.11f, 40, 12));

            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            ConfigureEnvironment(spatialSkybox);

            // This is an invisible reference frame only. The spinner is suspended
            // at its origin without any floor, pedestal, tray, or support geometry.
            GameObject motionSpace = new GameObject("GyroAlignedSpace");
            GameObject spinner = CreateSpinner(bodyMaterial, metalMaterial, darkMaterial, bodyRingMesh, bearingRingMesh);
            spinner.transform.SetParent(motionSpace.transform, true);
            CreateCameraAndLights(spinner.transform);

            PrefabUtility.SaveAsPrefabAsset(spinner, PrefabPath);
            EditorSceneManager.SaveScene(scene, ScenePath);
            AddSceneToBuildSettings();

            Selection.activeGameObject = spinner;
            SceneView.lastActiveSceneView?.FrameSelected();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log($"[Codex] Fidget spinner demo created: {ScenePath}");
        }

        private static GameObject CreateSpinner(
            Material bodyMaterial,
            Material metalMaterial,
            Material darkMaterial,
            Mesh bodyRingMesh,
            Mesh bearingRingMesh)
        {
            GameObject root = new GameObject("FidgetSpinner");
            root.transform.position = Vector3.zero;

            Rigidbody rigidbody = root.AddComponent<Rigidbody>();
            rigidbody.mass = 1.4f;
            rigidbody.useGravity = false;
            rigidbody.interpolation = RigidbodyInterpolation.Interpolate;
            rigidbody.collisionDetectionMode = CollisionDetectionMode.ContinuousSpeculative;
            rigidbody.constraints = RigidbodyConstraints.FreezePosition
                | RigidbodyConstraints.FreezeRotationX
                | RigidbodyConstraints.FreezeRotationZ;
            root.AddComponent<FidgetSpinnerController>();

            CreateCylinder("CenterBody", root.transform, Vector3.zero, new Vector3(1.08f, 0.22f, 1.08f), bodyMaterial, true);

            for (int index = 0; index < 3; index++)
            {
                float angle = index * 120f;
                Quaternion aroundCenter = Quaternion.Euler(0f, angle, 0f);
                Vector3 direction = aroundCenter * Vector3.forward;

                GameObject arm = GameObject.CreatePrimitive(PrimitiveType.Capsule);
                arm.name = $"Arm_{index + 1}";
                arm.transform.SetParent(root.transform, false);
                arm.transform.localPosition = direction * 1.28f;
                arm.transform.localRotation = aroundCenter * Quaternion.Euler(90f, 0f, 0f);
                arm.transform.localScale = new Vector3(0.86f, 1.28f, 0.40f);
                arm.GetComponent<MeshRenderer>().sharedMaterial = bodyMaterial;

                Vector3 lobePosition = direction * 2.42f;
                CreateMeshObject($"OuterBodyRing_{index + 1}", root.transform, lobePosition, bodyRingMesh, bodyMaterial);
                CreateMeshObject($"Bearing_{index + 1}", root.transform, lobePosition + Vector3.up * 0.045f, bearingRingMesh, metalMaterial);
                CreateCylinder(
                    $"BearingShield_{index + 1}",
                    root.transform,
                    lobePosition + Vector3.up * 0.045f,
                    new Vector3(0.225f, 0.07f, 0.225f),
                    darkMaterial,
                    false);

                GameObject colliderObject = new GameObject($"LobeCollider_{index + 1}");
                colliderObject.transform.SetParent(root.transform, false);
                colliderObject.transform.localPosition = lobePosition;
                SphereCollider lobeCollider = colliderObject.AddComponent<SphereCollider>();
                lobeCollider.radius = 0.93f;
            }

            CreateMeshObject("CenterBearing", root.transform, Vector3.up * 0.25f, bearingRingMesh, metalMaterial);
            CreateCylinder(
                "CenterBearingCap",
                root.transform,
                Vector3.up * 0.25f,
                new Vector3(0.31f, 0.07f, 0.31f),
                darkMaterial,
                false);

            return root;
        }

        private static GameObject CreateMeshObject(
            string name,
            Transform parent,
            Vector3 localPosition,
            Mesh mesh,
            Material material)
        {
            GameObject gameObject = new GameObject(name);
            gameObject.transform.SetParent(parent, false);
            gameObject.transform.localPosition = localPosition;
            gameObject.AddComponent<MeshFilter>().sharedMesh = mesh;
            gameObject.AddComponent<MeshRenderer>().sharedMaterial = material;
            return gameObject;
        }

        private static GameObject CreateCylinder(
            string name,
            Transform parent,
            Vector3 localPosition,
            Vector3 localScale,
            Material material,
            bool keepCollider)
        {
            GameObject cylinder = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            cylinder.name = name;
            cylinder.transform.SetParent(parent, false);
            cylinder.transform.localPosition = localPosition;
            cylinder.transform.localScale = localScale;
            cylinder.GetComponent<MeshRenderer>().sharedMaterial = material;

            if (!keepCollider)
            {
                Object.DestroyImmediate(cylinder.GetComponent<Collider>());
            }

            return cylinder;
        }

        private static void CreateCameraAndLights(Transform spinnerTarget)
        {
            GameObject cameraRig = new GameObject("GyroCameraRig");
            cameraRig.transform.position = Vector3.zero;

            GameObject cameraObject = new GameObject("Main Camera");
            cameraObject.tag = "MainCamera";
            cameraObject.transform.SetParent(cameraRig.transform, true);
            // A phone resting flat starts from an oblique floating-space view,
            // preserving the spinner's thickness without implying a support plane.
            cameraObject.transform.position = new Vector3(0f, 10.4f, -3.8f);
            cameraObject.transform.LookAt(Vector3.zero);
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.fieldOfView = 39f;
            camera.clearFlags = CameraClearFlags.Skybox;
            camera.backgroundColor = new Color(0.006f, 0.009f, 0.018f);
            camera.nearClipPlane = 0.1f;
            camera.farClipPlane = 100f;
            PortraitCameraFramer framer = cameraObject.AddComponent<PortraitCameraFramer>();
            framer.SetTarget(spinnerTarget);
            cameraObject.AddComponent<DeviceMotionController>();
            cameraObject.AddComponent<IosSwiftUiOverlayController>();

            GameObject keyLightObject = new GameObject("Key Light");
            keyLightObject.transform.rotation = Quaternion.Euler(48f, -32f, 0f);
            Light keyLight = keyLightObject.AddComponent<Light>();
            keyLight.type = LightType.Directional;
            keyLight.color = new Color(0.86f, 0.93f, 1f);
            keyLight.intensity = 2.2f;
            keyLight.shadows = LightShadows.Soft;

            GameObject rimLightObject = new GameObject("Rim Light");
            rimLightObject.transform.position = new Vector3(-3.8f, 5.2f, 2.8f);
            Light rimLight = rimLightObject.AddComponent<Light>();
            rimLight.type = LightType.Point;
            rimLight.color = new Color(0.18f, 0.42f, 1f);
            rimLight.intensity = 18f;
            rimLight.range = 12f;
            rimLight.shadows = LightShadows.Soft;
        }

        private static void ConfigureEnvironment(Material spatialSkybox)
        {
            RenderSettings.skybox = spatialSkybox;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.22f, 0.28f, 0.42f);
            RenderSettings.ambientEquatorColor = new Color(0.045f, 0.060f, 0.11f);
            RenderSettings.ambientGroundColor = new Color(0.009f, 0.012f, 0.024f);
            RenderSettings.reflectionIntensity = 0.92f;
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.ExponentialSquared;
            RenderSettings.fogColor = new Color(0.008f, 0.012f, 0.026f);
            RenderSettings.fogDensity = 0.008f;
        }

        private static Material CreateSpatialSkyboxMaterial(string path)
        {
            Shader shader = Shader.Find("Skybox/Procedural");
            if (shader == null)
            {
                return null;
            }

            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader);
                AssetDatabase.CreateAsset(material, path);
            }
            else
            {
                material.shader = shader;
            }

            material.SetColor("_SkyTint", new Color(0.045f, 0.085f, 0.18f));
            material.SetColor("_GroundColor", new Color(0.004f, 0.006f, 0.014f));
            material.SetFloat("_AtmosphereThickness", 0.22f);
            material.SetFloat("_Exposure", 0.42f);
            material.SetFloat("_SunSize", 0.015f);
            material.SetFloat("_SunSizeConvergence", 8f);
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Material CreateMaterial(string path, Color color, float metallic, float smoothness)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader);
                AssetDatabase.CreateAsset(material, path);
            }
            else
            {
                material.shader = shader;
            }

            if (material.HasProperty("_BaseColor"))
            {
                material.SetColor("_BaseColor", color);
            }
            if (material.HasProperty("_Color"))
            {
                material.SetColor("_Color", color);
            }
            if (material.HasProperty("_Metallic"))
            {
                material.SetFloat("_Metallic", metallic);
            }
            if (material.HasProperty("_Smoothness"))
            {
                material.SetFloat("_Smoothness", smoothness);
            }

            EditorUtility.SetDirty(material);
            return material;
        }

        private static Mesh CreateTorusMesh(string name, float majorRadius, float minorRadius, int majorSegments, int minorSegments)
        {
            Mesh mesh = new Mesh { name = name };
            Vector3[] vertices = new Vector3[majorSegments * minorSegments];
            Vector3[] normals = new Vector3[vertices.Length];
            Vector2[] uv = new Vector2[vertices.Length];
            int[] triangles = new int[majorSegments * minorSegments * 6];

            for (int major = 0; major < majorSegments; major++)
            {
                float u = major / (float)majorSegments;
                float majorAngle = u * Mathf.PI * 2f;
                float majorCos = Mathf.Cos(majorAngle);
                float majorSin = Mathf.Sin(majorAngle);

                for (int minor = 0; minor < minorSegments; minor++)
                {
                    float v = minor / (float)minorSegments;
                    float minorAngle = v * Mathf.PI * 2f;
                    float minorCos = Mathf.Cos(minorAngle);
                    float minorSin = Mathf.Sin(minorAngle);
                    int vertexIndex = major * minorSegments + minor;

                    float radialDistance = majorRadius + minorRadius * minorCos;
                    vertices[vertexIndex] = new Vector3(radialDistance * majorCos, minorRadius * minorSin, radialDistance * majorSin);
                    normals[vertexIndex] = new Vector3(minorCos * majorCos, minorSin, minorCos * majorSin).normalized;
                    uv[vertexIndex] = new Vector2(u, v);
                }
            }

            int triangleIndex = 0;
            for (int major = 0; major < majorSegments; major++)
            {
                int nextMajor = (major + 1) % majorSegments;
                for (int minor = 0; minor < minorSegments; minor++)
                {
                    int nextMinor = (minor + 1) % minorSegments;
                    int current = major * minorSegments + minor;
                    int nextAlongMajor = nextMajor * minorSegments + minor;
                    int nextAlongMinor = major * minorSegments + nextMinor;
                    int diagonal = nextMajor * minorSegments + nextMinor;

                    triangles[triangleIndex++] = current;
                    triangles[triangleIndex++] = nextAlongMinor;
                    triangles[triangleIndex++] = diagonal;
                    triangles[triangleIndex++] = current;
                    triangles[triangleIndex++] = diagonal;
                    triangles[triangleIndex++] = nextAlongMajor;
                }
            }

            mesh.vertices = vertices;
            mesh.normals = normals;
            mesh.uv = uv;
            mesh.triangles = triangles;
            mesh.RecalculateBounds();
            return mesh;
        }

        private static Mesh CreateOrReplaceMeshAsset(string path, Mesh generatedMesh)
        {
            Mesh existingMesh = AssetDatabase.LoadAssetAtPath<Mesh>(path);
            if (existingMesh == null)
            {
                AssetDatabase.CreateAsset(generatedMesh, path);
                return generatedMesh;
            }

            EditorUtility.CopySerialized(generatedMesh, existingMesh);
            Object.DestroyImmediate(generatedMesh);
            EditorUtility.SetDirty(existingMesh);
            return existingMesh;
        }

        private static void EnsureProjectFolders()
        {
            EnsureFolder("Assets", "Prefabs");
            EnsureFolder("Assets", "Materials");
            EnsureFolder("Assets/Materials", "FidgetSpinner");
            EnsureFolder("Assets", "Models");
            EnsureFolder("Assets/Models", "FidgetSpinner");
        }

        private static void EnsureFolder(string parent, string child)
        {
            string path = $"{parent}/{child}";
            if (!AssetDatabase.IsValidFolder(path))
            {
                AssetDatabase.CreateFolder(parent, child);
            }
        }

        private static void AddSceneToBuildSettings()
        {
            EditorBuildSettings.scenes = new[]
            {
                new EditorBuildSettingsScene(ScenePath, true),
                new EditorBuildSettingsScene(MetalScenePath, true),
                new EditorBuildSettingsScene(ImportedScenePath, true),
                new EditorBuildSettingsScene(TwoLobeScenePath, true),
                new EditorBuildSettingsScene(EdcScenePath, true),
                new EditorBuildSettingsScene(FanCardScenePath, true)
            };
        }
    }
}
