using System.Collections.Generic;
using System.IO;
using ThreeBladeEDC.Geometry;
using ThreeBladeEDC.Interaction;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace ThreeBladeEDC.EditorTools
{
    public static class ThreeBladeSceneBuilder
    {
        public const string ScenePath = "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity";
        private const string MeshFolder = "Assets/_Fidgeting/Generated/Meshes";

        [MenuItem("Fidgeting/Three-Blade/Rebuild Presentation")]
        public static void BuildPresentation()
        {
            ThreeBladeMaterialFactory.MaterialSet materials =
                ThreeBladeMaterialFactory.CreateOrUpdate();
            Mesh bladeMesh = SaveMesh(
                ProceduralMeshFactory.CreateBlade(),
                MeshFolder + "/M_ThreeBladeSector.asset");
            Mesh bladeInsetMesh = SaveMesh(
                ProceduralMeshFactory.CreateBladeInset(),
                MeshFolder + "/M_BladeInset.asset");
            Mesh bladeCollisionMesh = SaveMesh(
                ProceduralMeshFactory.CreateBladeCollision(),
                MeshFolder + "/M_BladeCollision.asset");
            Mesh capMesh = SaveMesh(
                ProceduralMeshFactory.CreateFacetedDisc(
                    "M_FacetedTopCap", 0.0172f, 0.0039f, 64, 0.0009f),
                MeshFolder + "/M_FacetedTopCap.asset");
            Mesh bottomCapMesh = SaveMesh(
                ProceduralMeshFactory.CreateFacetedDisc(
                    "M_FacetedBottomCap", 0.0148f, 0.0034f, 56, 0.00075f),
                MeshFolder + "/M_FacetedBottomCap.asset");
            Mesh rotorCoreMesh = SaveMesh(
                ProceduralMeshFactory.CreateRing(
                    "M_RotorCore", 0.0197f, 0.0117f, 0.0060f, 96),
                MeshFolder + "/M_RotorCore.asset");
            Mesh outerRaceMesh = SaveMesh(
                ProceduralMeshFactory.CreateRing(
                    "M_BearingOuterRace", 0.0115f, 0.0090f, 0.0070f, 96),
                MeshFolder + "/M_BearingOuterRace.asset");
            Mesh innerRaceMesh = SaveMesh(
                ProceduralMeshFactory.CreateRing(
                    "M_BearingInnerRace", 0.0088f, 0.0042f, 0.0070f, 96),
                MeshFolder + "/M_BearingInnerRace.asset");
            Mesh washerMesh = SaveMesh(
                ProceduralMeshFactory.CreateRing(
                    "M_BearingWasher", 0.0110f, 0.0043f, 0.0007f, 64),
                MeshFolder + "/M_BearingWasher.asset");

            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);

            GameObject root = new GameObject("ThreeBladeEDC_Root");
            root.transform.position = new Vector3(0f, 0.052f, 0f);
            root.AddComponent<ConceptModelNotice>();

            GameObject hub = new GameObject("HubStatic");
            hub.transform.SetParent(root.transform, false);
            Rigidbody hubBody = hub.AddComponent<Rigidbody>();
            hubBody.isKinematic = true;
            hubBody.useGravity = false;

            GameObject rotor = new GameObject("RotorDynamic");
            rotor.transform.SetParent(root.transform, false);
            Rigidbody rotorBody = rotor.AddComponent<Rigidbody>();
            rotorBody.mass = 0.105f;
            rotorBody.useGravity = false;
            rotorBody.angularDamping = 0.55f;
            rotorBody.maxAngularVelocity = 24f;
            rotorBody.interpolation = RigidbodyInterpolation.Interpolate;
            rotorBody.collisionDetectionMode = CollisionDetectionMode.ContinuousSpeculative;
            rotorBody.constraints = RigidbodyConstraints.FreezePosition
                | RigidbodyConstraints.FreezeRotationX
                | RigidbodyConstraints.FreezeRotationZ;

            HingeJoint hinge = rotor.AddComponent<HingeJoint>();
            hinge.connectedBody = hubBody;
            hinge.axis = Vector3.up;
            hinge.anchor = Vector3.zero;
            hinge.autoConfigureConnectedAnchor = false;
            hinge.connectedAnchor = Vector3.zero;
            hinge.useMotor = false;

            RotorRigidbodyController rotorController =
                rotor.AddComponent<RotorRigidbodyController>();
            rotor.AddComponent<SpinnerTouchSurface>();

            CreateMeshObject(
                "RotorCore",
                rotor.transform,
                rotorCoreMesh,
                new[] { materials.darkRing });
            CreateMeshObject(
                "BearingOuterRace",
                rotor.transform,
                outerRaceMesh,
                new[] { materials.bearing });

            for (int i = 0; i < 3; i++)
            {
                GameObject blade = new GameObject($"Blade_{i:00}");
                blade.transform.SetParent(rotor.transform, false);
                blade.transform.localRotation = Quaternion.Euler(0f, i * 120f, 0f);

                GameObject shell = CreateMeshObject(
                    "Shell",
                    blade.transform,
                    bladeMesh,
                    new[] { materials.blade, materials.bevel });
                shell.transform.localPosition = new Vector3(0f, 0.0003f, 0f);

                MeshCollider collider = blade.AddComponent<MeshCollider>();
                collider.sharedMesh = bladeCollisionMesh;
                collider.convex = true;

                GameObject inset = CreateMeshObject(
                    "TriangularInset",
                    blade.transform,
                    bladeInsetMesh,
                    new[] { materials.inset, materials.darkRing });
                // The procedural shell is not boolean-cut, so keep the dark
                // insert only 0.075 mm proud of the top face. At product-view
                // distance the polished border reads as a recessed pocket,
                // without z-fighting or the former floating-plate look.
                inset.transform.localPosition = new Vector3(0f, 0.00360f, 0f);
            }

            GameObject axle = CreatePrimitive(
                PrimitiveType.Cylinder,
                "Axle",
                hub.transform,
                materials.bearing,
                new Vector3(0.008f, 0.0085f, 0.008f));
            axle.transform.localPosition = Vector3.zero;

            CreateMeshObject(
                "BearingInnerRace",
                hub.transform,
                innerRaceMesh,
                new[] { materials.bearing });

            GameObject topWasher = CreateMeshObject(
                "TopWasher",
                hub.transform,
                washerMesh,
                new[] { materials.darkRing });
            topWasher.transform.localPosition = new Vector3(0f, 0.0047f, 0f);

            GameObject bottomWasher = CreateMeshObject(
                "BottomWasher",
                hub.transform,
                washerMesh,
                new[] { materials.darkRing });
            bottomWasher.transform.localPosition = new Vector3(0f, -0.0047f, 0f);

            GameObject topCap = CreateMeshObject(
                "TopCap",
                hub.transform,
                capMesh,
                new[] { materials.cap, materials.bevel });
            topCap.transform.localPosition = new Vector3(0f, 0.0081f, 0f);
            topCap.AddComponent<SpinnerTouchSurface>();
            MeshCollider topCapCollider = topCap.AddComponent<MeshCollider>();
            topCapCollider.sharedMesh = capMesh;
            topCapCollider.convex = true;

            GameObject bottomCap = CreateMeshObject(
                "BottomCap",
                hub.transform,
                bottomCapMesh,
                new[] { materials.darkRing, materials.bevel });
            bottomCap.transform.localPosition = new Vector3(0f, -0.0075f, 0f);

            GameObject bearingVisual = new GameObject("BearingVisual");
            bearingVisual.transform.SetParent(root.transform, false);
            GameObject cage = new GameObject("BallCage");
            cage.transform.SetParent(bearingVisual.transform, false);
            cage.transform.localPosition = new Vector3(0f, -0.0004f, 0f);
            for (int i = 0; i < 8; i++)
            {
                float angle = i * Mathf.PI * 0.25f;
                GameObject ball = CreatePrimitive(
                    PrimitiveType.Sphere,
                    $"Ball_{i:00}",
                    cage.transform,
                    materials.bearing,
                    Vector3.one * 0.0031f,
                    false);
                ball.transform.localPosition = new Vector3(
                    Mathf.Cos(angle) * 0.0075f,
                    0f,
                    Mathf.Sin(angle) * 0.0075f);
            }

            BearingCageVisualSync cageSync =
                bearingVisual.AddComponent<BearingCageVisualSync>();
            cageSync.Configure(rotorController, cage.transform, 0.5f);

            GameObject studio = new GameObject("Studio");
            studio.transform.SetParent(root.transform, false);
            CreateStudio(
                studio.transform,
                root.transform.position,
                materials.floor,
                materials.studioReflection,
                out Camera camera);

            OrbitPresentationCamera orbit =
                camera.gameObject.AddComponent<OrbitPresentationCamera>();
            orbit.Target = root.transform;
            orbit.SetDesktopInputEnabled(false);

            MobileGestureController gestures =
                root.AddComponent<MobileGestureController>();
            gestures.Configure(rotorController, camera, orbit);

            ExplodedViewController exploded =
                root.AddComponent<ExplodedViewController>();
            exploded.Configure(
                rotorBody,
                new[]
                {
                    Part(topCap.transform, new Vector3(0f, 0.043f, 0f)),
                    Part(topWasher.transform, new Vector3(0f, 0.029f, 0f)),
                    Part(rotor.transform, new Vector3(0f, 0.014f, 0f)),
                    Part(cage.transform, new Vector3(0f, -0.013f, 0f)),
                    Part(bottomWasher.transform, new Vector3(0f, -0.026f, 0f)),
                    Part(bottomCap.transform, new Vector3(0f, -0.039f, 0f))
                });

            MobileRuntimeBootstrap runtime =
                root.AddComponent<MobileRuntimeBootstrap>();
            runtime.Configure(rotorController, gestures);
            CreateMobileUi(root.transform, rotorController, exploded, orbit);

            rotorController.CaptureInitialPose();
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ScenePath);
            SetBuildScene();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log($"Three-Blade EDC presentation rebuilt: {ScenePath}");
        }

        public static void BuildAndRenderPreview()
        {
            BuildPresentation();
            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            Camera camera = Camera.main;
            if (camera == null)
            {
                throw new MissingReferenceException("Presentation camera tagged MainCamera was not found.");
            }

            string projectParent = Directory.GetParent(Application.dataPath).FullName;
            string artifactFolder = Path.GetFullPath(Path.Combine(projectParent, "../../Artifacts"));
            Directory.CreateDirectory(artifactFolder);
            string assembledPath = Path.Combine(artifactFolder, "three-blade-edc-preview.png");
            RenderCameraToPng(camera, assembledPath);

            GameObject root = scene.GetRootGameObjects()[0];
            OffsetLocal(root.transform.Find("HubStatic/TopCap"), 0.043f);
            OffsetLocal(root.transform.Find("HubStatic/TopWasher"), 0.029f);
            OffsetLocal(root.transform.Find("RotorDynamic"), 0.014f);
            OffsetLocal(root.transform.Find("BearingVisual/BallCage"), -0.013f);
            OffsetLocal(root.transform.Find("HubStatic/BottomWasher"), -0.026f);
            OffsetLocal(root.transform.Find("HubStatic/BottomCap"), -0.039f);
            camera.transform.position = root.transform.position + new Vector3(0.18f, 0.14f, -0.48f);
            camera.transform.LookAt(root.transform.position);
            string explodedPath = Path.Combine(artifactFolder, "three-blade-edc-exploded.png");
            RenderCameraToPng(camera, explodedPath);

            // Reload the saved assembled scene so preview-only offsets are
            // never persisted into the interactive deliverable.
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            Debug.Log($"Three-Blade EDC previews written: {assembledPath} | {explodedPath}");
        }

        private static void RenderCameraToPng(Camera camera, string path)
        {
            RenderTexture renderTexture = new RenderTexture(
                1920,
                1080,
                24,
                RenderTextureFormat.ARGB32)
            {
                antiAliasing = 4
            };
            camera.targetTexture = renderTexture;
            camera.Render();
            RenderTexture previous = RenderTexture.active;
            RenderTexture.active = renderTexture;
            Texture2D preview = new Texture2D(1920, 1080, TextureFormat.RGB24, false);
            preview.ReadPixels(new Rect(0f, 0f, 1920f, 1080f), 0, 0);
            preview.Apply(false, false);
            File.WriteAllBytes(path, preview.EncodeToPNG());
            camera.targetTexture = null;
            RenderTexture.active = previous;
            UnityEngine.Object.DestroyImmediate(preview);
            UnityEngine.Object.DestroyImmediate(renderTexture);
        }

        private static void OffsetLocal(Transform part, float yOffset)
        {
            if (part != null)
            {
                part.localPosition += Vector3.up * yOffset;
            }
        }

        private static void CreateMobileUi(
            Transform parent,
            RotorRigidbodyController rotor,
            ExplodedViewController exploded,
            OrbitPresentationCamera orbit)
        {
            Font font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            GameObject canvasObject = new GameObject(
                "MobileCanvas",
                typeof(RectTransform),
                typeof(Canvas),
                typeof(CanvasScaler),
                typeof(GraphicRaycaster));
            canvasObject.transform.SetParent(parent, false);
            Canvas canvas = canvasObject.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 100;
            CanvasScaler scaler = canvasObject.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920f, 1080f);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
            scaler.matchWidthOrHeight = 0.5f;

            GameObject safeObject = new GameObject(
                "SafeArea",
                typeof(RectTransform),
                typeof(SafeAreaFitter));
            safeObject.transform.SetParent(canvasObject.transform, false);
            RectTransform safeRect = safeObject.GetComponent<RectTransform>();
            safeRect.anchorMin = Vector2.zero;
            safeRect.anchorMax = Vector2.one;
            safeRect.offsetMin = Vector2.zero;
            safeRect.offsetMax = Vector2.zero;

            Text title = CreateLabel(
                "Title",
                safeRect,
                font,
                "THREE-BLADE EDC",
                30,
                TextAnchor.MiddleLeft,
                new Color(0.90f, 0.94f, 0.98f, 0.92f));
            RectTransform titleRect = title.rectTransform;
            titleRect.anchorMin = new Vector2(0f, 1f);
            titleRect.anchorMax = new Vector2(0f, 1f);
            titleRect.pivot = new Vector2(0f, 1f);
            titleRect.anchoredPosition = new Vector2(34f, -26f);
            titleRect.sizeDelta = new Vector2(520f, 58f);

            Text rpm = CreateLabel(
                "Rpm",
                safeRect,
                font,
                "0 RPM",
                28,
                TextAnchor.MiddleRight,
                new Color(1f, 0.46f, 0.16f, 0.96f));
            RectTransform rpmRect = rpm.rectTransform;
            rpmRect.anchorMin = new Vector2(1f, 1f);
            rpmRect.anchorMax = new Vector2(1f, 1f);
            rpmRect.pivot = new Vector2(1f, 1f);
            rpmRect.anchoredPosition = new Vector2(-34f, -26f);
            rpmRect.sizeDelta = new Vector2(300f, 58f);

            GameObject barObject = new GameObject(
                "ControlBar",
                typeof(RectTransform),
                typeof(Image),
                typeof(HorizontalLayoutGroup));
            barObject.transform.SetParent(safeRect, false);
            RectTransform barRect = barObject.GetComponent<RectTransform>();
            barRect.anchorMin = new Vector2(0.5f, 0f);
            barRect.anchorMax = new Vector2(0.5f, 0f);
            barRect.pivot = new Vector2(0.5f, 0f);
            barRect.anchoredPosition = new Vector2(0f, 26f);
            barRect.sizeDelta = new Vector2(940f, 104f);
            Image barImage = barObject.GetComponent<Image>();
            barImage.color = new Color(0.025f, 0.035f, 0.048f, 0.88f);
            HorizontalLayoutGroup layout = barObject.GetComponent<HorizontalLayoutGroup>();
            layout.padding = new RectOffset(20, 20, 18, 18);
            layout.spacing = 18f;
            layout.childAlignment = TextAnchor.MiddleCenter;
            layout.childControlWidth = true;
            layout.childControlHeight = true;
            layout.childForceExpandWidth = true;
            layout.childForceExpandHeight = true;

            Button explodeButton = CreateButton(
                "ExplodeButton", barRect, font, "EXPLODE", out Text explodeLabel);
            Button resetButton = CreateButton(
                "ResetButton", barRect, font, "RESET", out _);
            Button motorButton = CreateButton(
                "MotorButton", barRect, font, "MOTOR", out Text motorLabel);
            Button viewButton = CreateButton(
                "ViewButton", barRect, font, "VIEW", out _);

            MobileViewerUI ui = canvasObject.AddComponent<MobileViewerUI>();
            ui.Configure(
                rotor,
                exploded,
                orbit,
                explodeButton,
                resetButton,
                motorButton,
                viewButton,
                explodeLabel,
                motorLabel,
                rpm);

            GameObject eventSystemObject = new GameObject(
                "EventSystem",
                typeof(EventSystem),
                typeof(InputSystemUIInputModule));
            eventSystemObject.transform.SetParent(parent, false);
            eventSystemObject
                .GetComponent<InputSystemUIInputModule>()
                .AssignDefaultActions();
        }

        private static Text CreateLabel(
            string name,
            Transform parent,
            Font font,
            string value,
            int fontSize,
            TextAnchor alignment,
            Color color)
        {
            GameObject labelObject = new GameObject(
                name,
                typeof(RectTransform),
                typeof(CanvasRenderer),
                typeof(Text));
            labelObject.transform.SetParent(parent, false);
            Text label = labelObject.GetComponent<Text>();
            label.font = font;
            label.text = value;
            label.fontSize = fontSize;
            label.alignment = alignment;
            label.color = color;
            label.raycastTarget = false;
            return label;
        }

        private static Button CreateButton(
            string name,
            Transform parent,
            Font font,
            string labelValue,
            out Text label)
        {
            GameObject buttonObject = new GameObject(
                name,
                typeof(RectTransform),
                typeof(CanvasRenderer),
                typeof(Image),
                typeof(Button),
                typeof(LayoutElement));
            buttonObject.transform.SetParent(parent, false);
            Image image = buttonObject.GetComponent<Image>();
            image.color = new Color(0.10f, 0.13f, 0.17f, 0.96f);
            Button button = buttonObject.GetComponent<Button>();
            ColorBlock colors = button.colors;
            colors.normalColor = Color.white;
            colors.highlightedColor = new Color(1f, 0.72f, 0.52f);
            colors.pressedColor = new Color(1f, 0.46f, 0.16f);
            colors.selectedColor = new Color(1f, 0.66f, 0.40f);
            colors.fadeDuration = 0.08f;
            button.colors = colors;
            LayoutElement layout = buttonObject.GetComponent<LayoutElement>();
            layout.preferredWidth = 205f;
            layout.preferredHeight = 68f;

            label = CreateLabel(
                "Label",
                buttonObject.transform,
                font,
                labelValue,
                25,
                TextAnchor.MiddleCenter,
                new Color(0.94f, 0.96f, 0.98f, 1f));
            RectTransform labelRect = label.rectTransform;
            labelRect.anchorMin = Vector2.zero;
            labelRect.anchorMax = Vector2.one;
            labelRect.offsetMin = Vector2.zero;
            labelRect.offsetMax = Vector2.zero;
            return button;
        }

        private static void CreateStudio(
            Transform parent,
            Vector3 target,
            Material floorMaterial,
            Cubemap studioReflection,
            out Camera camera)
        {
            GameObject floor = CreatePrimitive(
                PrimitiveType.Plane,
                "StudioFloor",
                parent,
                floorMaterial,
                new Vector3(0.045f, 1f, 0.045f));
            floor.transform.position = Vector3.zero;
            floor.SetActive(true);

            camera = new GameObject("HeroCamera").AddComponent<Camera>();
            camera.transform.SetParent(parent, true);
            camera.tag = "MainCamera";
            camera.transform.position = target + new Vector3(0.105f, 0.160f, -0.160f);
            camera.transform.LookAt(target);
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.black;
            camera.allowHDR = true;
            camera.allowMSAA = true;
            camera.usePhysicalProperties = true;
            camera.focalLength = 85f;
            camera.sensorSize = new Vector2(36f, 24f);
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 10f;
            UniversalAdditionalCameraData cameraData =
                camera.gameObject.AddComponent<UniversalAdditionalCameraData>();
            cameraData.renderPostProcessing = true;
            cameraData.renderShadows = true;

            CreateSpotLight(
                "Key_5000K",
                parent,
                target + new Vector3(-0.22f, 0.30f, -0.18f),
                target,
                5000f,
                0.62f,
                58f);
            CreateSpotLight(
                "WarmRim_3200K",
                parent,
                target + new Vector3(0.22f, 0.22f, 0.16f),
                target,
                3200f,
                0.52f,
                46f);
            CreateSpotLight(
                "CoolFill_6500K",
                parent,
                target + new Vector3(-0.18f, 0.14f, 0.14f),
                target,
                6500f,
                0.22f,
                74f);

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.12f, 0.14f, 0.18f);
            RenderSettings.ambientEquatorColor = new Color(0.055f, 0.065f, 0.08f);
            RenderSettings.ambientGroundColor = new Color(0.018f, 0.020f, 0.026f);
            RenderSettings.reflectionIntensity = 0.35f;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflectionTexture = studioReflection;

            GameObject reflectionObject = new GameObject("StudioReflectionProbe");
            reflectionObject.transform.SetParent(parent, false);
            reflectionObject.transform.position = target;
            ReflectionProbe reflectionProbe = reflectionObject.AddComponent<ReflectionProbe>();
            reflectionProbe.mode = ReflectionProbeMode.Custom;
            reflectionProbe.customBakedTexture = studioReflection;
            reflectionProbe.size = Vector3.one * 0.5f;
            reflectionProbe.boxProjection = true;
            reflectionProbe.intensity = 1f;
            reflectionProbe.importance = 100;

            ConfigureVolume(parent);
        }

        private static void ConfigureVolume(Transform parent)
        {
            const string profilePath = "Assets/_Fidgeting/Generated/ThreeBladeVolume.asset";
            VolumeProfile profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(profilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>();
                AssetDatabase.CreateAsset(profile, profilePath);
            }

            if (!profile.TryGet(out Tonemapping tonemapping))
            {
                tonemapping = profile.Add<Tonemapping>(true);
            }
            tonemapping.mode.Override(TonemappingMode.ACES);

            if (!profile.TryGet(out ColorAdjustments color))
            {
                color = profile.Add<ColorAdjustments>(true);
            }
            color.postExposure.Override(-0.3f);
            color.contrast.Override(12f);
            color.saturation.Override(-5f);

            if (!profile.TryGet(out Vignette vignette))
            {
                vignette = profile.Add<Vignette>(true);
            }
            vignette.intensity.Override(0.18f);
            vignette.smoothness.Override(0.72f);

            GameObject volumeObject = new GameObject("GlobalVolume");
            volumeObject.transform.SetParent(parent, false);
            Volume volume = volumeObject.AddComponent<Volume>();
            volume.isGlobal = true;
            volume.priority = 10f;
            volume.sharedProfile = profile;
            EditorUtility.SetDirty(profile);
        }

        private static void CreateSpotLight(
            string name,
            Transform parent,
            Vector3 position,
            Vector3 target,
            float temperature,
            float intensity,
            float spotAngle)
        {
            Light light = new GameObject(name).AddComponent<Light>();
            light.transform.SetParent(parent, true);
            light.transform.position = position;
            light.transform.LookAt(target);
            light.type = LightType.Spot;
            light.useColorTemperature = true;
            light.colorTemperature = temperature;
            light.intensity = intensity;
            light.range = 1.5f;
            light.spotAngle = spotAngle;
            light.innerSpotAngle = spotAngle * 0.58f;
            light.shadows = LightShadows.Soft;
            light.shadowStrength = 0.65f;
        }

        private static GameObject CreateMeshObject(
            string name,
            Transform parent,
            Mesh mesh,
            Material[] materials)
        {
            GameObject gameObject = new GameObject(name);
            gameObject.transform.SetParent(parent, false);
            gameObject.AddComponent<MeshFilter>().sharedMesh = mesh;
            gameObject.AddComponent<MeshRenderer>().sharedMaterials = materials;
            return gameObject;
        }

        private static GameObject CreatePrimitive(
            PrimitiveType type,
            string name,
            Transform parent,
            Material material,
            Vector3 scale,
            bool keepCollider = true)
        {
            GameObject gameObject = GameObject.CreatePrimitive(type);
            gameObject.name = name;
            gameObject.transform.SetParent(parent, false);
            gameObject.transform.localScale = scale;
            gameObject.GetComponent<MeshRenderer>().sharedMaterial = material;
            if (!keepCollider)
            {
                Collider collider = gameObject.GetComponent<Collider>();
                if (collider != null)
                {
                    UnityEngine.Object.DestroyImmediate(collider);
                }
            }
            return gameObject;
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

        private static void SetBuildScene()
        {
            EditorBuildSettings.scenes = new[]
            {
                new EditorBuildSettingsScene(ScenePath, true)
            };
        }
    }
}
