using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FidgetingApp.EDC;
using FidgetingApp.FanCard;
using FidgetingApp.Product;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.FanCard.EditorTools
{
    public static class FanCardSceneBuilder
    {
        private const string RootFolder = "Assets/_FanCard";
        private const string GeneratedFolder = RootFolder + "/Generated";
        private const string MeshFolder = GeneratedFolder + "/Meshes";
        private const string MaterialFolder = GeneratedFolder + "/Materials";
        private const string TextureFolder = GeneratedFolder + "/Textures";
        private const string SceneFolder = RootFolder + "/Scenes";
        private const string FontPath =
            "Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf";
        private const string ThumbnailPath =
            "Assets/Plugins/iOS/Thumbnails/Models/product-thumbnail-magnetic-fan-card.png";

        private const string BodyMeshPath = MeshFolder + "/M_FanCardBody.asset";
        private const string FaceMeshPath = MeshFolder + "/M_FanCardFace.asset";
        private const string BorderMeshPath = MeshFolder + "/M_FanCardInsetBorder.asset";
        private const string TrackShellMeshPath = MeshFolder + "/M_FanCardTrackShell.asset";
        private const string TrackMeshPath = MeshFolder + "/M_FanCardTrackMesh.asset";
        private const string SpadeMeshPath = MeshFolder + "/M_FanCardSpade.asset";
        private const string SpadeStripeMeshPath = MeshFolder + "/M_FanCardSpadeSlots.asset";

        private const string GunmetalMaterialPath = MaterialFolder + "/M_FanCardGunmetal.mat";
        private const string SilverMaterialPath = MaterialFolder + "/M_FanCardWarmSilver.mat";
        private const string EtchingMaterialPath = MaterialFolder + "/M_FanCardEtching.mat";
        private const string GrooveMaterialPath = MaterialFolder + "/M_FanCardGroove.mat";
        private const string GoldMeshMaterialPath = MaterialFolder + "/M_FanCardGoldMesh.mat";
        private const string ChromeMaterialPath = MaterialFolder + "/M_FanCardChrome.mat";
        private const string GrainNormalPath = TextureFolder + "/T_FanCardBeadBlastNormal.png";
        private const string WovenTexturePath = TextureFolder + "/T_FanCardGoldWoven.png";
        private const string ReflectionPath = TextureFolder + "/C_FanCardSoftStudio.asset";

        [MenuItem("Tools/Codex/Fan Card/1 Build Magnetic Fan Card Scene")]
        public static void BuildScene()
        {
            EnsureFolders();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);

            FanCardDetentProfile profile = CreateOrUpdateProfile();
            Texture2D grainNormal = CreateOrUpdateGrainNormal();
            Texture2D woven = CreateOrUpdateWovenTexture();
            Cubemap reflection = CreateOrUpdateReflection();

            Material gunmetal = CreateOrUpdateLitMaterial(
                GunmetalMaterialPath,
                "M_FanCardGunmetal",
                FanCardSpecifications.GunmetalColor,
                FanCardSpecifications.GunmetalMetallic,
                FanCardSpecifications.GunmetalSmoothness,
                grainNormal,
                FanCardSpecifications.GrainBumpScale,
                new Vector2(46f, 46f));
            Material silver = CreateOrUpdateLitMaterial(
                SilverMaterialPath,
                "M_FanCardWarmSilver",
                FanCardSpecifications.WarmSilverColor,
                FanCardSpecifications.SilverMetallic,
                FanCardSpecifications.SilverSmoothness,
                grainNormal,
                0.095f,
                new Vector2(72f, 72f));
            Material etching = CreateOrUpdateLitMaterial(
                EtchingMaterialPath,
                "M_FanCardEtching",
                FanCardSpecifications.EtchingColor,
                0.76f,
                0.23f,
                grainNormal,
                0.07f,
                new Vector2(74f, 74f));
            Material groove = CreateOrUpdateLitMaterial(
                GrooveMaterialPath,
                "M_FanCardGroove",
                FanCardSpecifications.GrooveColor,
                0.64f,
                0.16f,
                grainNormal,
                0.08f,
                new Vector2(80f, 80f));
            Material goldMesh = CreateOrUpdateLitMaterial(
                GoldMeshMaterialPath,
                "M_FanCardGoldMesh",
                FanCardSpecifications.MagnetGoldColor,
                0.92f,
                0.36f,
                grainNormal,
                0.08f,
                new Vector2(92f, 92f));
            goldMesh.SetTexture("_BaseMap", woven);
            goldMesh.SetTextureScale("_BaseMap", new Vector2(8f, 2f));
            EditorUtility.SetDirty(goldMesh);
            Material chrome = CreateOrUpdateLitMaterial(
                ChromeMaterialPath,
                "M_FanCardChrome",
                new Color(0.86f, 0.89f, 0.93f, 1f),
                1f,
                FanCardSpecifications.ChromeSmoothness,
                null,
                0f,
                Vector2.one);

            Mesh bodyMesh = SaveMesh(
                CreateRoundedBoxMesh(
                    "M_FanCardBody",
                    FanCardSpecifications.CardWidth,
                    FanCardSpecifications.CardHeight,
                    FanCardSpecifications.CardThickness,
                    FanCardSpecifications.CardCornerRadius,
                    FanCardSpecifications.EdgeBevel,
                    8),
                BodyMeshPath);
            Mesh faceMesh = SaveMesh(
                CreateRoundedBoxMesh(
                    "M_FanCardFace",
                    FanCardSpecifications.FaceWidth,
                    FanCardSpecifications.FaceHeight,
                    FanCardSpecifications.FaceThickness,
                    FanCardSpecifications.FaceCornerRadius,
                    0.00022f,
                    8),
                FaceMeshPath);
            Mesh borderMesh = SaveMesh(
                CreateRoundedRingMesh(
                    "M_FanCardInsetBorder",
                    FanCardSpecifications.FaceWidth - 0.0014f,
                    FanCardSpecifications.FaceHeight - 0.0014f,
                    FanCardSpecifications.FaceCornerRadius - 0.0007f,
                    0.00045f,
                    8),
                BorderMeshPath);
            Mesh trackShellMesh = SaveMesh(
                CreateArcRibbonMesh(
                    "M_FanCardTrackShell",
                    FanCardSpecifications.FollowerFromPivot,
                    -profile.MaximumRelativeAngleDegrees,
                    FanCardSpecifications.TrackShellWidth,
                    32),
                TrackShellMeshPath);
            Mesh trackMesh = SaveMesh(
                CreateArcRibbonMesh(
                    "M_FanCardTrackMesh",
                    FanCardSpecifications.FollowerFromPivot,
                    -profile.MaximumRelativeAngleDegrees,
                    FanCardSpecifications.TrackMeshWidth,
                    32),
                TrackMeshPath);
            List<Vector2> spadePolygon = CreateDownwardSpadePolygon();
            Mesh spadeMesh = SaveMesh(
                CreatePlanarPolygonMesh("M_FanCardSpade", spadePolygon),
                SpadeMeshPath);
            Mesh spadeStripeMesh = SaveMesh(
                CreateVerticalStripeMesh(
                    "M_FanCardSpadeSlots",
                    spadePolygon,
                    0.00125f,
                    0.00058f,
                    0.00072f),
                SpadeStripeMeshPath);

            Font oxanium = AssetDatabase.LoadAssetAtPath<Font>(FontPath);
            if (oxanium == null)
            {
                throw new FileNotFoundException(
                    "The canonical Oxanium product font is missing.",
                    FontPath);
            }

            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            var root = new GameObject("MagneticFanCard_Root");
            root.transform.localRotation = Quaternion.Euler(
                0f,
                FanCardSpecifications.PresentationRotationDegrees,
                0f);
            GameObject bottom = CreateCardLayer(
                "BottomCard",
                root.transform,
                0,
                bodyMesh,
                faceMesh,
                borderMesh,
                spadeMesh,
                spadeStripeMesh,
                trackShellMesh,
                trackMesh,
                gunmetal,
                silver,
                etching,
                groove,
                goldMesh,
                chrome,
                oxanium,
                hasTrack: true,
                hasFollower: false,
                profile);
            GameObject middle = CreateCardLayer(
                "MiddleCard",
                root.transform,
                1,
                bodyMesh,
                faceMesh,
                borderMesh,
                spadeMesh,
                spadeStripeMesh,
                trackShellMesh,
                trackMesh,
                gunmetal,
                silver,
                etching,
                groove,
                goldMesh,
                chrome,
                oxanium,
                hasTrack: true,
                hasFollower: true,
                profile);
            GameObject top = CreateCardLayer(
                "TopCard",
                root.transform,
                2,
                bodyMesh,
                faceMesh,
                borderMesh,
                spadeMesh,
                spadeStripeMesh,
                trackShellMesh,
                trackMesh,
                gunmetal,
                silver,
                etching,
                groove,
                goldMesh,
                chrome,
                oxanium,
                hasTrack: false,
                hasFollower: true,
                profile);
            _ = bottom;

            CreateAxisAssembly(root.transform, chrome, groove);

            BoxCollider interaction = top.AddComponent<BoxCollider>();
            interaction.center = FanCardSpecifications.CardCenterFromPivot;
            interaction.size = new Vector3(
                FanCardSpecifications.CardWidth
                    + FanCardSpecifications.InteractionPadding,
                FanCardSpecifications.LayerPitch * 3.2f,
                FanCardSpecifications.CardHeight
                    + FanCardSpecifications.InteractionPadding);

            Camera camera = CreateStudio(root.transform, reflection);
            EdcPortraitCameraFramer framer =
                camera.gameObject.AddComponent<EdcPortraitCameraFramer>();
            framer.Configure(root.transform);
            FanCardCameraProjectionGuard projectionGuard =
                camera.gameObject.AddComponent<FanCardCameraProjectionGuard>();
            projectionGuard.ApplyNow();
            SharedPresentationGestureController presentation =
                camera.gameObject.AddComponent<SharedPresentationGestureController>();
            presentation.Configure(framer, camera, interaction);

            FanCardController controller = root.AddComponent<FanCardController>();
            controller.Configure(
                middle.transform,
                top.transform,
                camera,
                interaction,
                profile);
            controller.ResetClosed();

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, FanCardSpecifications.ScenePath, true);
            SetProductBuildScenes();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log(
                "[FanCard] Built portrait three-layer magnetic fan card; "
                + $"detents={profile.DetentCount}; adjacent="
                + $"{profile.MaximumRelativeAngleDegrees:F0}deg; total="
                + $"{profile.MaximumTotalAngleDegrees:F0}deg; scene="
                + FanCardSpecifications.ScenePath);
        }

        [MenuItem("Tools/Codex/Fan Card/2 Build and Capture Material Previews")]
        public static void BuildAndCapturePreviews()
        {
            BuildScene();
            Scene scene = EditorSceneManager.OpenScene(
                FanCardSpecifications.ScenePath,
                OpenSceneMode.Single);
            GameObject root = scene.GetRootGameObjects()
                .Single(candidate => candidate.name == "MagneticFanCard_Root");
            FanCardController controller = root.GetComponent<FanCardController>();
            Camera camera = Camera.main ?? UnityEngine.Object.FindAnyObjectByType<Camera>();
            EdcPortraitCameraFramer framer = camera.GetComponent<EdcPortraitCameraFramer>();
            framer.enabled = false;
            controller.enabled = false;
            controller.SetFanProgress(1f);

            SpinnerEnvironmentPresenter environment =
                SpinnerEnvironmentPresenter.Install(FanCardSpecifications.ScenePath);
            environment.SetLibraryPreviewActive(false, true);
            environment.ImageBasedLighting?.SetViewResponse(
                Vector2.zero,
                false,
                0f,
                0f,
                0f);

            string outputFolder = Path.GetFullPath(Path.Combine(
                Directory.GetParent(Application.dataPath).FullName,
                "../../Artifacts/FanCardMaterialPreview"));
            Directory.CreateDirectory(outputFolder);
            Bounds bounds = ResolveBounds(root.transform);
            CaptureView(
                camera,
                environment,
                bounds,
                new Vector3(0f, 1f, -0.08f).normalized,
                Vector3.forward,
                Path.Combine(outputFolder, "fan-card-top.png"),
                900,
                1600);
            CaptureView(
                camera,
                environment,
                bounds,
                EdcPortraitCameraFramer.DefaultDetailFramingBackward,
                Vector3.up,
                Path.Combine(outputFolder, "fan-card-hero.png"),
                900,
                1600);
            CaptureView(
                camera,
                environment,
                bounds,
                new Vector3(-0.58f, 0.48f, -0.66f).normalized,
                Vector3.up,
                Path.Combine(outputFolder, "fan-card-left.png"),
                900,
                1600);
            CaptureView(
                camera,
                environment,
                bounds,
                new Vector3(0.58f, 0.48f, -0.66f).normalized,
                Vector3.up,
                Path.Combine(outputFolder, "fan-card-right.png"),
                900,
                1600);
            CaptureView(
                camera,
                environment,
                bounds,
                new Vector3(0.18f, 0.20f, -0.96f).normalized,
                Vector3.up,
                Path.Combine(outputFolder, "fan-card-low.png"),
                900,
                1600);

            // Repeat the overhead render after the first URP/IBL frames have
            // initialized so the open metal faces are not captured before
            // their environment response is ready.
            CaptureView(
                camera,
                environment,
                bounds,
                new Vector3(0f, 1f, -0.08f).normalized,
                Vector3.forward,
                Path.Combine(outputFolder, "fan-card-top.png"),
                900,
                1600);

            controller.SetFanProgress(0f);
            bounds = ResolveBounds(root.transform);
            CaptureView(
                camera,
                environment,
                bounds,
                new Vector3(0f, 1f, -0.08f).normalized,
                Vector3.forward,
                Path.Combine(outputFolder, "fan-card-front-closed.png"),
                900,
                1600);

            controller.SetFanProgress(2f / 3f);
            bounds = ResolveBounds(root.transform);
            CaptureView(
                camera,
                environment,
                bounds,
                EdcPortraitCameraFramer.DefaultDetailFramingBackward,
                Vector3.up,
                Path.GetFullPath(Path.Combine(
                    Directory.GetParent(Application.dataPath).FullName,
                    ThumbnailPath)),
                512,
                512);
            AssetDatabase.ImportAsset(
                ThumbnailPath,
                ImportAssetOptions.ForceSynchronousImport);
            ConfigureThumbnailImporter();
            controller.ResetClosed();
            Debug.Log($"[FanCard] Six Unity material previews: {outputFolder}");
        }

        private static GameObject CreateCardLayer(
            string name,
            Transform parent,
            int level,
            Mesh bodyMesh,
            Mesh faceMesh,
            Mesh borderMesh,
            Mesh spadeMesh,
            Mesh spadeStripeMesh,
            Mesh trackShellMesh,
            Mesh trackMesh,
            Material gunmetal,
            Material silver,
            Material etching,
            Material groove,
            Material goldMesh,
            Material chrome,
            Font font,
            bool hasTrack,
            bool hasFollower,
            FanCardDetentProfile profile)
        {
            var layer = new GameObject(name);
            layer.transform.SetParent(parent, false);
            layer.transform.localPosition = Vector3.up
                * (level * FanCardSpecifications.LayerPitch);

            CreateMeshObject(
                "GunmetalFrame",
                layer.transform,
                bodyMesh,
                gunmetal,
                FanCardSpecifications.CardCenterFromPivot);
            float faceY = FanCardSpecifications.CardThickness * 0.5f
                + FanCardSpecifications.FaceThickness * 0.5f
                - 0.00006f;
            CreateMeshObject(
                "WarmSilverFace",
                layer.transform,
                faceMesh,
                silver,
                FanCardSpecifications.CardCenterFromPivot + Vector3.up * faceY);
            CreateMeshObject(
                "InsetBorder_ThinLine",
                layer.transform,
                borderMesh,
                etching,
                FanCardSpecifications.CardCenterFromPivot
                    + Vector3.up * (faceY + FanCardSpecifications.FaceThickness * 0.52f));

            AddFaceArtwork(
                layer.transform,
                faceY + FanCardSpecifications.FaceThickness * 0.56f,
                spadeMesh,
                spadeStripeMesh,
                etching,
                silver,
                font);
            CreateBearingSeat(layer.transform, groove, chrome, faceY);

            if (hasTrack)
            {
                CreateMeshObject(
                    "CurvedTrack_Undercut",
                    layer.transform,
                    trackShellMesh,
                    groove,
                    Vector3.up * FanCardSpecifications.TrackSurfaceHeight);
                CreateMeshObject(
                    "CurvedTrack_GoldWoven",
                    layer.transform,
                    trackMesh,
                    goldMesh,
                    Vector3.up * (FanCardSpecifications.TrackSurfaceHeight + 0.00005f));
                for (int detent = 1; detent < profile.DetentCount; detent++)
                {
                    float t = detent / (float)profile.DetentIntervals;
                    Vector2 point = Rotate2D(
                        FanCardSpecifications.FollowerFromPivot,
                        -profile.MaximumRelativeAngleDegrees * t);
                    CreateCylinder(
                        $"Magnet_{detent:D2}",
                        layer.transform,
                        new Vector3(
                            point.x,
                            FanCardSpecifications.TrackSurfaceHeight + 0.00013f,
                            point.y),
                        FanCardSpecifications.MagnetRadius,
                        0.00016f,
                        goldMesh,
                        24);
                }
            }

            if (hasFollower)
            {
                GameObject follower = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                follower.name = "FollowerBearing_Chrome";
                follower.transform.SetParent(layer.transform, false);
                follower.transform.localPosition = new Vector3(
                    FanCardSpecifications.FollowerFromPivot.x,
                    -FanCardSpecifications.CardThickness * 0.5f
                        - 0.00030f,
                    FanCardSpecifications.FollowerFromPivot.y);
                follower.transform.localScale = Vector3.one
                    * (FanCardSpecifications.FollowerBallRadius * 2f);
                follower.GetComponent<MeshRenderer>().sharedMaterial = chrome;
                UnityEngine.Object.DestroyImmediate(follower.GetComponent<Collider>());
            }

            return layer;
        }

        private static void AddFaceArtwork(
            Transform layer,
            float y,
            Mesh spadeMesh,
            Mesh stripeMesh,
            Material etching,
            Material silver,
            Font font)
        {
            Vector3 center = FanCardSpecifications.CardCenterFromPivot;
            Vector3 heroPosition = center + new Vector3(0.003f, y, -0.0035f);
            CreateMeshObject(
                "Spade_Etched",
                layer,
                spadeMesh,
                etching,
                heroPosition,
                new Vector3(1.10f, 1f, 1.10f));
            CreateMeshObject(
                "Spade_VerticalSlots",
                layer,
                stripeMesh,
                silver,
                heroPosition + Vector3.up * 0.000035f,
                new Vector3(1.10f, 1f, 1.10f));

            Vector3 acePosition = center + new Vector3(-0.0172f, y + 0.00018f, 0.0250f);
            CreateAceText("Ace_A_Oxanium", layer, font, acePosition, 180f, 0.00062f);
            GameObject smallSpade = CreateMeshObject(
                "CornerSpade_Down",
                layer,
                spadeMesh,
                etching,
                center + new Vector3(-0.0146f, y + 0.000025f, 0.0169f),
                Vector3.one * 0.245f);
            smallSpade.transform.localRotation = Quaternion.identity;

            CreateAceText(
                "Ace_A_Oxanium_Reverse",
                layer,
                font,
                center + new Vector3(0.0172f, y + 0.00018f, -0.0250f),
                0f,
                0.00055f);
            GameObject reverseSpade = CreateMeshObject(
                "CornerSpade_Down_Reverse",
                layer,
                spadeMesh,
                etching,
                center + new Vector3(0.0146f, y + 0.000025f, -0.0169f),
                Vector3.one * 0.215f);
            reverseSpade.transform.localRotation = Quaternion.Euler(0f, 180f, 0f);

            Vector2[] dots =
            {
                new(-0.0160f, -0.0204f),
                new(-0.0107f, -0.0173f),
                new(-0.0100f, -0.0231f)
            };
            for (int index = 0; index < dots.Length; index++)
            {
                CreateCylinder(
                    $"EtchedDot_{index + 1:D2}",
                    layer,
                    center + new Vector3(dots[index].x, y + 0.00002f, dots[index].y),
                    0.00118f,
                    0.00010f,
                    etching,
                    20);
            }
        }

        private static void CreateAceText(
            string name,
            Transform parent,
            Font font,
            Vector3 position,
            float rotationY,
            float characterSize)
        {
            var owner = new GameObject(name);
            owner.transform.SetParent(parent, false);
            owner.transform.localPosition = position;
            owner.transform.localRotation = Quaternion.Euler(-90f, rotationY, 0f);
            TextMesh text = owner.AddComponent<TextMesh>();
            text.text = "A";
            text.font = font;
            text.fontSize = 96;
            text.characterSize = characterSize;
            // The bundled variable face already supplies the app's authored
            // Oxanium outline. Legacy TextMesh synthetic bold creates offset
            // copies at this millimetre scale, which reads as clipped bars.
            text.fontStyle = FontStyle.Normal;
            text.anchor = TextAnchor.MiddleCenter;
            text.alignment = TextAlignment.Center;
            text.color = FanCardSpecifications.EtchingColor;
            text.richText = false;
            MeshRenderer renderer = owner.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = font.material;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
        }

        private static void CreateBearingSeat(
            Transform layer,
            Material groove,
            Material chrome,
            float faceY)
        {
            CreateCylinder(
                "AxisSeat_Gunmetal",
                layer,
                new Vector3(0f, faceY + 0.00026f, 0f),
                FanCardSpecifications.AxisOuterRadius,
                0.00048f,
                groove,
                36);
            CreateCylinder(
                "AxisSeat_Inner",
                layer,
                new Vector3(0f, faceY + 0.00052f, 0f),
                FanCardSpecifications.AxisInnerRadius,
                0.00020f,
                chrome,
                36);
        }

        private static void CreateAxisAssembly(
            Transform root,
            Material chrome,
            Material groove)
        {
            float totalHeight = FanCardSpecifications.LayerPitch * 2f
                + FanCardSpecifications.CardThickness;
            CreateCylinder(
                "CommonAxis_ShadowSleeve",
                root,
                new Vector3(0f, totalHeight * 0.5f - 0.0008f, 0f),
                FanCardSpecifications.AxisInnerRadius * 0.76f,
                totalHeight,
                groove,
                36);
            CreateCylinder(
                "CommonAxis_ChromePin",
                root,
                new Vector3(0f, totalHeight + 0.00022f, 0f),
                FanCardSpecifications.AxisInnerRadius * 0.70f,
                0.00125f,
                chrome,
                36);

            GameObject ballSeat = CreateCylinder(
                "CommonAxis_BallSeat",
                root,
                new Vector3(0f, totalHeight + 0.00008f, 0f),
                FanCardSpecifications.AxisBallRadius * 1.18f,
                0.00072f,
                groove,
                36);
            ballSeat.GetComponent<MeshRenderer>().shadowCastingMode =
                ShadowCastingMode.On;

            GameObject axisBall = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            axisBall.name = "CommonAxis_ChromeBall";
            axisBall.transform.SetParent(root, false);
            axisBall.transform.localPosition = new Vector3(
                0f,
                totalHeight + 0.00072f,
                0f);
            axisBall.transform.localScale = Vector3.one
                * (FanCardSpecifications.AxisBallRadius * 2f);
            MeshRenderer ballRenderer = axisBall.GetComponent<MeshRenderer>();
            ballRenderer.sharedMaterial = chrome;
            ballRenderer.shadowCastingMode = ShadowCastingMode.On;
            ballRenderer.receiveShadows = true;
            UnityEngine.Object.DestroyImmediate(axisBall.GetComponent<Collider>());
        }

        private static Camera CreateStudio(Transform target, Cubemap reflection)
        {
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.28f, 0.27f, 0.25f);
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflectionTexture = reflection;
            RenderSettings.reflectionIntensity = 0.78f;

            var cameraObject = new GameObject("MainCamera");
            cameraObject.tag = "MainCamera";
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.black;
            camera.nearClipPlane = 0.005f;
            camera.farClipPlane = 20f;
            camera.allowHDR = true;
            camera.allowMSAA = true;
            cameraObject.AddComponent<AudioListener>();

            var keyObject = new GameObject("LargeSoftKey_UpperLeft");
            Light key = keyObject.AddComponent<Light>();
            key.type = LightType.Directional;
            key.color = new Color(1.0f, 0.90f, 0.80f);
            key.intensity = 0.76f;
            key.shadows = LightShadows.Soft;
            keyObject.transform.rotation = Quaternion.Euler(48f, -34f, 0f);

            var fillObject = new GameObject("CoolBroadFill");
            Light fill = fillObject.AddComponent<Light>();
            fill.type = LightType.Directional;
            fill.color = new Color(0.62f, 0.72f, 0.82f);
            fill.intensity = 0.40f;
            fill.shadows = LightShadows.None;
            fillObject.transform.rotation = Quaternion.Euler(62f, 146f, 0f);

            // A low-energy frontal softbox keeps the bead-blasted metal
            // readable in left/right and low-angle product views without
            // creating a second hard highlight.
            var frontObject = new GameObject("SoftFrontLift");
            Light front = frontObject.AddComponent<Light>();
            front.type = LightType.Directional;
            front.color = new Color(0.90f, 0.87f, 0.82f);
            front.intensity = 0.28f;
            front.shadows = LightShadows.None;
            frontObject.transform.rotation = Quaternion.Euler(18f, 8f, 0f);
            return camera;
        }

        private static FanCardDetentProfile CreateOrUpdateProfile()
        {
            FanCardDetentProfile profile =
                AssetDatabase.LoadAssetAtPath<FanCardDetentProfile>(
                    FanCardSpecifications.ProfilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<FanCardDetentProfile>();
                profile.name = "FanCardDetentProfile";
                AssetDatabase.CreateAsset(profile, FanCardSpecifications.ProfilePath);
            }
            profile.ApplyReferenceDefaults();
            EditorUtility.SetDirty(profile);
            return profile;
        }

        private static Material CreateOrUpdateLitMaterial(
            string path,
            string name,
            Color color,
            float metallic,
            float smoothness,
            Texture2D normal,
            float bumpScale,
            Vector2 normalScale)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null)
            {
                throw new MissingReferenceException("URP Lit shader is unavailable.");
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
            material.SetColor("_BaseColor", color);
            material.SetColor("_Color", color);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Smoothness", smoothness);
            material.SetFloat("_SpecularHighlights", 1f);
            material.SetFloat("_EnvironmentReflections", 1f);
            material.SetFloat("_Surface", 0f);
            material.SetFloat("_Cull", 0f);
            material.doubleSidedGI = true;
            if (normal != null)
            {
                material.SetTexture("_BumpMap", normal);
                material.SetTextureScale("_BumpMap", normalScale);
                material.SetFloat("_BumpScale", bumpScale);
                material.EnableKeyword("_NORMALMAP");
            }
            else
            {
                material.SetTexture("_BumpMap", null);
                material.DisableKeyword("_NORMALMAP");
            }
            material.enableInstancing = true;
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Texture2D CreateOrUpdateGrainNormal()
        {
            const int size = 128;
            var random = new System.Random(0xFA4CA2D);
            var heights = new float[size, size];
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    heights[x, y] = (float)random.NextDouble();
                }
            }
            // One blur pass retains a fine isotropic bead-blast grain. Two
            // passes made the normal field too smooth to read on the frame.
            for (int pass = 0; pass < 1; pass++)
            {
                var blurred = new float[size, size];
                for (int y = 0; y < size; y++)
                {
                    for (int x = 0; x < size; x++)
                    {
                        float sum = 0f;
                        for (int oy = -1; oy <= 1; oy++)
                        {
                            for (int ox = -1; ox <= 1; ox++)
                            {
                                sum += heights[
                                    (x + ox + size) % size,
                                    (y + oy + size) % size];
                            }
                        }
                        blurred[x, y] = sum / 9f;
                    }
                }
                heights = blurred;
            }

            var texture = new Texture2D(size, size, TextureFormat.RGBA32, false, true);
            var pixels = new Color[size * size];
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    float left = heights[(x - 1 + size) % size, y];
                    float right = heights[(x + 1) % size, y];
                    float down = heights[x, (y - 1 + size) % size];
                    float up = heights[x, (y + 1) % size];
                    Vector3 normal = new Vector3(left - right, down - up, 1f).normalized;
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
            TextureImporter importer = (TextureImporter)AssetImporter.GetAtPath(GrainNormalPath);
            importer.textureType = TextureImporterType.NormalMap;
            importer.sRGBTexture = false;
            importer.wrapMode = TextureWrapMode.Repeat;
            importer.filterMode = FilterMode.Trilinear;
            importer.mipmapEnabled = true;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(GrainNormalPath);
        }

        private static Texture2D CreateOrUpdateWovenTexture()
        {
            const int size = 128;
            var texture = new Texture2D(size, size, TextureFormat.RGB24, false, false);
            var pixels = new Color[size * size];
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    int diagonalA = (x + y) % 12;
                    int diagonalB = (x - y + size * 2) % 12;
                    bool wire = diagonalA <= 2 || diagonalB <= 2;
                    float glint = ((x + y * 3) & 7) / 7f;
                    Color baseColor = wire
                        ? new Color(0.72f, 0.46f, 0.15f)
                        : new Color(0.105f, 0.070f, 0.032f);
                    pixels[y * size + x] = baseColor
                        * Mathf.Lerp(0.78f, 1.18f, glint);
                }
            }
            texture.SetPixels(pixels);
            texture.Apply(false, false);
            WriteTexturePng(texture, WovenTexturePath);
            UnityEngine.Object.DestroyImmediate(texture);
            AssetDatabase.ImportAsset(WovenTexturePath, ImportAssetOptions.ForceSynchronousImport);
            TextureImporter importer = (TextureImporter)AssetImporter.GetAtPath(WovenTexturePath);
            importer.textureType = TextureImporterType.Default;
            importer.sRGBTexture = true;
            importer.wrapMode = TextureWrapMode.Repeat;
            importer.filterMode = FilterMode.Trilinear;
            importer.mipmapEnabled = true;
            importer.textureCompression = TextureImporterCompression.Compressed;
            importer.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(WovenTexturePath);
        }

        private static Cubemap CreateOrUpdateReflection()
        {
            const int size = 32;
            Cubemap cubemap = AssetDatabase.LoadAssetAtPath<Cubemap>(ReflectionPath);
            if (cubemap == null)
            {
                cubemap = new Cubemap(size, TextureFormat.RGBA32, true)
                {
                    name = "C_FanCardSoftStudio"
                };
                AssetDatabase.CreateAsset(cubemap, ReflectionPath);
            }
            Color[] faces =
            {
                new(0.62f, 0.58f, 0.52f),
                new(0.10f, 0.12f, 0.15f),
                new(0.82f, 0.79f, 0.73f),
                new(0.018f, 0.016f, 0.015f),
                new(0.30f, 0.34f, 0.39f),
                new(0.38f, 0.28f, 0.20f)
            };
            for (int face = 0; face < 6; face++)
            {
                var pixels = new Color[size * size];
                for (int y = 0; y < size; y++)
                {
                    float v = y / (float)(size - 1);
                    for (int x = 0; x < size; x++)
                    {
                        float u = x / (float)(size - 1);
                        float panel = Mathf.Exp(-(
                            Mathf.Pow(u - 0.28f, 2f)
                            + Mathf.Pow(v - 0.74f, 2f)) / 0.20f);
                        pixels[y * size + x] = faces[face]
                            * Mathf.Lerp(0.72f, 1.25f, panel);
                    }
                }
                cubemap.SetPixels(pixels, (CubemapFace)face, 0);
            }
            cubemap.Apply(true, false);
            EditorUtility.SetDirty(cubemap);
            return cubemap;
        }

        private static Mesh CreateRoundedBoxMesh(
            string name,
            float width,
            float height,
            float thickness,
            float radius,
            float bevel,
            int cornerSegments)
        {
            float halfY = thickness * 0.5f;
            float safeBevel = Mathf.Min(bevel, Mathf.Min(radius * 0.55f, halfY));
            List<Vector2>[] rings =
            {
                RoundedRectPoints(width, height, radius, safeBevel, cornerSegments),
                RoundedRectPoints(width, height, radius, 0f, cornerSegments),
                RoundedRectPoints(width, height, radius, 0f, cornerSegments),
                RoundedRectPoints(width, height, radius, safeBevel, cornerSegments)
            };
            float[] ys = { -halfY, -halfY + safeBevel, halfY - safeBevel, halfY };
            var vertices = new List<Vector3>();
            var triangles = new List<int>();
            for (int ring = 0; ring < rings.Length; ring++)
            {
                foreach (Vector2 point in rings[ring])
                {
                    vertices.Add(new Vector3(point.x, ys[ring], point.y));
                }
            }
            int count = rings[0].Count;
            for (int ring = 0; ring < rings.Length - 1; ring++)
            {
                int start = ring * count;
                int next = (ring + 1) * count;
                for (int i = 0; i < count; i++)
                {
                    int j = (i + 1) % count;
                    triangles.Add(start + i);
                    triangles.Add(next + i);
                    triangles.Add(next + j);
                    triangles.Add(start + i);
                    triangles.Add(next + j);
                    triangles.Add(start + j);
                }
            }
            int bottomCenter = vertices.Count;
            vertices.Add(new Vector3(0f, -halfY, 0f));
            int topCenter = vertices.Count;
            vertices.Add(new Vector3(0f, halfY, 0f));
            int topStart = (rings.Length - 1) * count;
            for (int i = 0; i < count; i++)
            {
                int j = (i + 1) % count;
                triangles.Add(bottomCenter);
                triangles.Add(j);
                triangles.Add(i);
                triangles.Add(topCenter);
                triangles.Add(topStart + i);
                triangles.Add(topStart + j);
            }
            return FinalizeMesh(name, vertices, triangles);
        }

        private static Mesh CreateRoundedRingMesh(
            string name,
            float width,
            float height,
            float radius,
            float ringWidth,
            int cornerSegments)
        {
            List<Vector2> outer = RoundedRectPoints(
                width,
                height,
                radius,
                0f,
                cornerSegments);
            List<Vector2> inner = RoundedRectPoints(
                width - ringWidth * 2f,
                height - ringWidth * 2f,
                Mathf.Max(0.0001f, radius - ringWidth),
                0f,
                cornerSegments);
            var vertices = new List<Vector3>(outer.Count * 2);
            var triangles = new List<int>(outer.Count * 6);
            vertices.AddRange(outer.Select(point => new Vector3(point.x, 0f, point.y)));
            vertices.AddRange(inner.Select(point => new Vector3(point.x, 0f, point.y)));
            int count = outer.Count;
            for (int i = 0; i < count; i++)
            {
                int j = (i + 1) % count;
                triangles.Add(i);
                triangles.Add(j);
                triangles.Add(count + j);
                triangles.Add(i);
                triangles.Add(count + j);
                triangles.Add(count + i);
            }
            return FinalizeMesh(name, vertices, triangles);
        }

        private static Mesh CreateArcRibbonMesh(
            string name,
            Vector2 startPoint,
            float sweepDegrees,
            float width,
            int segments)
        {
            float radius = startPoint.magnitude;
            float startAngle = Mathf.Atan2(startPoint.y, startPoint.x) * Mathf.Rad2Deg;
            var vertices = new List<Vector3>((segments + 1) * 2);
            var triangles = new List<int>(segments * 6);
            for (int i = 0; i <= segments; i++)
            {
                float angle = (startAngle + sweepDegrees * i / segments) * Mathf.Deg2Rad;
                Vector2 radial = new(Mathf.Cos(angle), Mathf.Sin(angle));
                Vector2 outer = radial * (radius + width * 0.5f);
                Vector2 inner = radial * (radius - width * 0.5f);
                vertices.Add(new Vector3(outer.x, 0f, outer.y));
                vertices.Add(new Vector3(inner.x, 0f, inner.y));
            }
            for (int i = 0; i < segments; i++)
            {
                int a = i * 2;
                int b = a + 1;
                int c = a + 2;
                int d = a + 3;
                triangles.Add(a);
                triangles.Add(c);
                triangles.Add(d);
                triangles.Add(a);
                triangles.Add(d);
                triangles.Add(b);
            }
            return FinalizeMesh(name, vertices, triangles);
        }

        private static List<Vector2> CreateDownwardSpadePolygon()
        {
            const float s = 0.001f;
            return new List<Vector2>
            {
                new(0f, -13.0f * s),
                new(-2.5f * s, -10.2f * s),
                new(-5.4f * s, -7.4f * s),
                new(-8.2f * s, -4.8f * s),
                new(-10.0f * s, -1.2f * s),
                new(-10.1f * s, 2.0f * s),
                new(-9.0f * s, 4.8f * s),
                new(-6.8f * s, 6.6f * s),
                new(-4.5f * s, 7.2f * s),
                new(-2.2f * s, 6.3f * s),
                new(-1.6f * s, 8.4f * s),
                new(-4.0f * s, 11.5f * s),
                new(-4.0f * s, 13.0f * s),
                new(4.0f * s, 13.0f * s),
                new(4.0f * s, 11.5f * s),
                new(1.6f * s, 8.4f * s),
                new(2.2f * s, 6.3f * s),
                new(4.5f * s, 7.2f * s),
                new(6.8f * s, 6.6f * s),
                new(9.0f * s, 4.8f * s),
                new(10.1f * s, 2.0f * s),
                new(10.0f * s, -1.2f * s),
                new(8.2f * s, -4.8f * s),
                new(5.4f * s, -7.4f * s),
                new(2.5f * s, -10.2f * s)
            };
        }

        private static Mesh CreatePlanarPolygonMesh(
            string name,
            IReadOnlyList<Vector2> polygon)
        {
            List<int> triangles = TriangulatePolygon(polygon);
            EnsurePositiveYFacing(polygon, triangles);
            return FinalizeMesh(
                name,
                polygon.Select(point => new Vector3(point.x, 0f, point.y)).ToList(),
                triangles);
        }

        private static void EnsurePositiveYFacing(
            IReadOnlyList<Vector2> polygon,
            List<int> triangles)
        {
            if (triangles.Count < 3)
            {
                return;
            }
            Vector3 a = new(polygon[triangles[0]].x, 0f, polygon[triangles[0]].y);
            Vector3 b = new(polygon[triangles[1]].x, 0f, polygon[triangles[1]].y);
            Vector3 c = new(polygon[triangles[2]].x, 0f, polygon[triangles[2]].y);
            if (Vector3.Cross(b - a, c - a).y >= 0f)
            {
                return;
            }
            for (int index = 0; index < triangles.Count; index += 3)
            {
                (triangles[index + 1], triangles[index + 2]) =
                    (triangles[index + 2], triangles[index + 1]);
            }
        }

        private static Mesh CreateVerticalStripeMesh(
            string name,
            IReadOnlyList<Vector2> polygon,
            float spacing,
            float stripeWidth,
            float inset)
        {
            float minX = polygon.Min(point => point.x) + inset;
            float maxX = polygon.Max(point => point.x) - inset;
            var vertices = new List<Vector3>();
            var triangles = new List<int>();
            for (float x = minX; x <= maxX; x += spacing)
            {
                if (!TryVerticalRange(polygon, x, out float minZ, out float maxZ))
                {
                    continue;
                }
                minZ += inset;
                maxZ -= inset;
                if (maxZ <= minZ)
                {
                    continue;
                }
                int start = vertices.Count;
                float half = stripeWidth * 0.5f;
                vertices.Add(new Vector3(x - half, 0f, minZ));
                vertices.Add(new Vector3(x - half, 0f, maxZ));
                vertices.Add(new Vector3(x + half, 0f, maxZ));
                vertices.Add(new Vector3(x + half, 0f, minZ));
                triangles.Add(start);
                triangles.Add(start + 1);
                triangles.Add(start + 2);
                triangles.Add(start);
                triangles.Add(start + 2);
                triangles.Add(start + 3);
            }
            return FinalizeMesh(name, vertices, triangles);
        }

        private static bool TryVerticalRange(
            IReadOnlyList<Vector2> polygon,
            float x,
            out float minZ,
            out float maxZ)
        {
            var intersections = new List<float>();
            for (int i = 0; i < polygon.Count; i++)
            {
                Vector2 a = polygon[i];
                Vector2 b = polygon[(i + 1) % polygon.Count];
                if ((x < Mathf.Min(a.x, b.x)) || (x > Mathf.Max(a.x, b.x)))
                {
                    continue;
                }
                float dx = b.x - a.x;
                if (Mathf.Abs(dx) < 0.0000001f)
                {
                    continue;
                }
                float t = (x - a.x) / dx;
                if (t >= 0f && t < 1f)
                {
                    intersections.Add(Mathf.Lerp(a.y, b.y, t));
                }
            }
            if (intersections.Count < 2)
            {
                minZ = maxZ = 0f;
                return false;
            }
            intersections.Sort();
            minZ = intersections[0];
            maxZ = intersections[^1];
            return true;
        }

        private static List<int> TriangulatePolygon(IReadOnlyList<Vector2> polygon)
        {
            var indices = Enumerable.Range(0, polygon.Count).ToList();
            if (SignedArea(polygon) > 0f)
            {
                indices.Reverse();
            }
            var triangles = new List<int>();
            int guard = polygon.Count * polygon.Count;
            while (indices.Count > 2 && guard-- > 0)
            {
                bool clipped = false;
                for (int i = 0; i < indices.Count; i++)
                {
                    int previous = indices[(i - 1 + indices.Count) % indices.Count];
                    int current = indices[i];
                    int next = indices[(i + 1) % indices.Count];
                    Vector2 a = polygon[previous];
                    Vector2 b = polygon[current];
                    Vector2 c = polygon[next];
                    if (Cross(b - a, c - b) >= 0f)
                    {
                        continue;
                    }
                    bool contains = false;
                    for (int testIndex = 0; testIndex < indices.Count; testIndex++)
                    {
                        int test = indices[testIndex];
                        if (test == previous || test == current || test == next)
                        {
                            continue;
                        }
                        if (PointInTriangle(polygon[test], a, b, c))
                        {
                            contains = true;
                            break;
                        }
                    }
                    if (contains)
                    {
                        continue;
                    }
                    triangles.Add(previous);
                    triangles.Add(current);
                    triangles.Add(next);
                    indices.RemoveAt(i);
                    clipped = true;
                    break;
                }
                if (!clipped)
                {
                    break;
                }
            }
            return triangles;
        }

        private static float SignedArea(IReadOnlyList<Vector2> polygon)
        {
            float area = 0f;
            for (int i = 0; i < polygon.Count; i++)
            {
                Vector2 a = polygon[i];
                Vector2 b = polygon[(i + 1) % polygon.Count];
                area += a.x * b.y - b.x * a.y;
            }
            return area * 0.5f;
        }

        private static float Cross(Vector2 a, Vector2 b)
        {
            return a.x * b.y - a.y * b.x;
        }

        private static bool PointInTriangle(
            Vector2 point,
            Vector2 a,
            Vector2 b,
            Vector2 c)
        {
            float c1 = Cross(b - a, point - a);
            float c2 = Cross(c - b, point - b);
            float c3 = Cross(a - c, point - c);
            bool hasNegative = c1 < 0f || c2 < 0f || c3 < 0f;
            bool hasPositive = c1 > 0f || c2 > 0f || c3 > 0f;
            return !(hasNegative && hasPositive);
        }

        private static List<Vector2> RoundedRectPoints(
            float width,
            float height,
            float radius,
            float inset,
            int segments)
        {
            float halfWidth = width * 0.5f - inset;
            float halfHeight = height * 0.5f - inset;
            float r = Mathf.Max(0.0001f, radius - inset);
            float centerX = halfWidth - r;
            float centerZ = halfHeight - r;
            var points = new List<Vector2>(segments * 4);
            AddArc(points, centerX, centerZ, r, 90f, 0f, segments);
            AddArc(points, centerX, -centerZ, r, 0f, -90f, segments);
            AddArc(points, -centerX, -centerZ, r, -90f, -180f, segments);
            AddArc(points, -centerX, centerZ, r, 180f, 90f, segments);
            return points;
        }

        private static void AddArc(
            List<Vector2> points,
            float centerX,
            float centerZ,
            float radius,
            float startDegrees,
            float endDegrees,
            int segments)
        {
            for (int i = 0; i < segments; i++)
            {
                float t = i / (float)segments;
                float angle = Mathf.Lerp(startDegrees, endDegrees, t) * Mathf.Deg2Rad;
                points.Add(new Vector2(
                    centerX + Mathf.Cos(angle) * radius,
                    centerZ + Mathf.Sin(angle) * radius));
            }
        }

        private static Mesh FinalizeMesh(
            string name,
            List<Vector3> vertices,
            List<int> triangles)
        {
            var mesh = new Mesh { name = name };
            mesh.SetVertices(vertices);
            mesh.SetTriangles(triangles, 0, true);
            var uvs = vertices.Select(vertex => new Vector2(
                vertex.x * 18f + 0.5f,
                vertex.z * 18f + 0.5f)).ToList();
            mesh.SetUVs(0, uvs);
            mesh.RecalculateNormals();
            mesh.RecalculateTangents();
            mesh.RecalculateBounds();
            return mesh;
        }

        private static GameObject CreateMeshObject(
            string name,
            Transform parent,
            Mesh mesh,
            Material material,
            Vector3 localPosition,
            Vector3? localScale = null)
        {
            var owner = new GameObject(name);
            owner.transform.SetParent(parent, false);
            owner.transform.localPosition = localPosition;
            owner.transform.localScale = localScale ?? Vector3.one;
            owner.AddComponent<MeshFilter>().sharedMesh = mesh;
            MeshRenderer renderer = owner.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.On;
            renderer.receiveShadows = true;
            return owner;
        }

        private static GameObject CreateCylinder(
            string name,
            Transform parent,
            Vector3 localPosition,
            float radius,
            float height,
            Material material,
            int unusedSegments)
        {
            _ = unusedSegments;
            GameObject cylinder = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            cylinder.name = name;
            cylinder.transform.SetParent(parent, false);
            cylinder.transform.localPosition = localPosition;
            cylinder.transform.localScale = new Vector3(radius, height * 0.5f, radius);
            cylinder.GetComponent<MeshRenderer>().sharedMaterial = material;
            UnityEngine.Object.DestroyImmediate(cylinder.GetComponent<Collider>());
            return cylinder;
        }

        private static Vector2 Rotate2D(Vector2 point, float degrees)
        {
            float radians = degrees * Mathf.Deg2Rad;
            float cosine = Mathf.Cos(radians);
            float sine = Mathf.Sin(radians);
            return new Vector2(
                point.x * cosine - point.y * sine,
                point.x * sine + point.y * cosine);
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

        private static Bounds ResolveBounds(Transform root)
        {
            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            if (renderers.Length == 0)
            {
                throw new InvalidDataException("Fan card has no renderers.");
            }
            Bounds bounds = renderers[0].bounds;
            for (int index = 1; index < renderers.Length; index++)
            {
                bounds.Encapsulate(renderers[index].bounds);
            }
            return bounds;
        }

        private static void CaptureView(
            Camera camera,
            SpinnerEnvironmentPresenter environment,
            Bounds bounds,
            Vector3 backward,
            Vector3 up,
            string path,
            int width,
            int height)
        {
            float previousAspect = camera.aspect;
            camera.aspect = width / (float)height;
            camera.ResetProjectionMatrix();
            float distance = RequiredPreviewDistance(
                camera,
                bounds,
                backward,
                up,
                0.88f,
                0.82f,
                0.07f,
                0.004f);
            camera.transform.position = bounds.center + backward.normalized * distance;
            camera.transform.rotation = Quaternion.LookRotation(
                bounds.center - camera.transform.position,
                up);
            environment.RefreshLayout();
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            RenderCameraToPng(camera, path, width, height);
            camera.aspect = previousAspect;
            camera.ResetProjectionMatrix();
        }

        private static float RequiredPreviewDistance(
            Camera camera,
            Bounds bounds,
            Vector3 backward,
            Vector3 requestedUp,
            float widthFraction,
            float heightFraction,
            float minimumDistance,
            float padding)
        {
            Vector3 viewBackward = backward.sqrMagnitude > 0.0001f
                ? backward.normalized
                : Vector3.back;
            Vector3 viewForward = -viewBackward;
            Vector3 safeUp = Vector3.ProjectOnPlane(requestedUp, viewForward);
            if (safeUp.sqrMagnitude < 0.0001f)
            {
                safeUp = Vector3.ProjectOnPlane(Vector3.up, viewForward);
            }
            safeUp.Normalize();
            Vector3 viewRight = Vector3.Cross(safeUp, viewForward).normalized;
            Vector3 viewUp = Vector3.Cross(viewForward, viewRight).normalized;
            Matrix4x4 projection = camera.projectionMatrix;
            float horizontalTangent = 1f
                / Mathf.Max(Mathf.Abs(projection.m00), 0.0001f);
            float verticalTangent = 1f
                / Mathf.Max(Mathf.Abs(projection.m11), 0.0001f);
            float usableWidth = Mathf.Clamp(widthFraction, 0.30f, 0.92f);
            float usableHeight = Mathf.Clamp(heightFraction, 0.30f, 0.92f);
            float required = Mathf.Max(0.01f, minimumDistance);
            Vector3 extents = bounds.extents;

            for (int x = -1; x <= 1; x += 2)
            {
                for (int y = -1; y <= 1; y += 2)
                {
                    for (int z = -1; z <= 1; z += 2)
                    {
                        Vector3 offset = bounds.center + new Vector3(
                            extents.x * x,
                            extents.y * y,
                            extents.z * z) - bounds.center;
                        float viewX = Vector3.Dot(offset, viewRight);
                        float viewY = Vector3.Dot(offset, viewUp);
                        float viewZ = Vector3.Dot(offset, viewForward);
                        required = Mathf.Max(
                            required,
                            Mathf.Abs(viewX) / (horizontalTangent * usableWidth) - viewZ,
                            Mathf.Abs(viewY) / (verticalTangent * usableHeight) - viewZ);
                    }
                }
            }
            return required + Mathf.Max(0f, padding);
        }

        private static void RenderCameraToPng(
            Camera camera,
            string path,
            int width,
            int height)
        {
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            var target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32)
            {
                antiAliasing = 4
            };
            var image = new Texture2D(width, height, TextureFormat.RGBA32, false, false);
            try
            {
                target.Create();
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
                RenderTexture.active = previousActive;
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
                UnityEngine.Object.DestroyImmediate(image);
            }
        }

        private static void ConfigureThumbnailImporter()
        {
            TextureImporter importer = AssetImporter.GetAtPath(ThumbnailPath)
                as TextureImporter;
            if (importer == null)
            {
                return;
            }
            importer.textureType = TextureImporterType.Default;
            importer.sRGBTexture = true;
            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            importer.alphaIsTransparency = true;
            importer.mipmapEnabled = false;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.maxTextureSize = 512;
            importer.SaveAndReimport();
        }

        private static void WriteTexturePng(Texture2D texture, string assetPath)
        {
            string projectFolder = Directory.GetParent(Application.dataPath).FullName;
            File.WriteAllBytes(
                Path.Combine(projectFolder, assetPath),
                texture.EncodeToPNG());
        }

        private static void EnsureFolders()
        {
            EnsureAssetFolder(RootFolder);
            EnsureAssetFolder(GeneratedFolder);
            EnsureAssetFolder(MeshFolder);
            EnsureAssetFolder(MaterialFolder);
            EnsureAssetFolder(TextureFolder);
            EnsureAssetFolder(SceneFolder);
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
                throw new InvalidDataException($"Invalid asset folder: {path}");
            }
            EnsureAssetFolder(parent);
            AssetDatabase.CreateFolder(parent, child);
        }

        private static void SetProductBuildScenes()
        {
            EditorBuildSettings.scenes = new[]
            {
                new EditorBuildSettingsScene(SpinnerEnvironmentCatalog.MetalScenePath, true),
                new EditorBuildSettingsScene(SpinnerEnvironmentCatalog.BlueScenePath, true),
                new EditorBuildSettingsScene(SpinnerEnvironmentCatalog.ImportedScenePath, true),
                new EditorBuildSettingsScene(SpinnerEnvironmentCatalog.TwoLobeScenePath, true),
                new EditorBuildSettingsScene(SpinnerEnvironmentCatalog.EdcScenePath, true),
                new EditorBuildSettingsScene(FanCardSpecifications.ScenePath, true)
            };
        }
    }
}
