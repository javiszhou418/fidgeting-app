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
        private const string ThumbnailPath =
            "Assets/Plugins/iOS/Thumbnails/Models/product-thumbnail-magnetic-fan-card.png";

        private const string BodyMeshPath = MeshFolder + "/M_FanCardBody.asset";
        private const string FaceMeshPath = MeshFolder + "/M_FanCardFace.asset";
        private const string BackFaceMeshPath =
            MeshFolder + "/M_FanCardBackFace.asset";
        private const string GoldTrimMeshPath = MeshFolder + "/M_FanCardGoldTrim.asset";
        private const string BackGoldTrimMeshPath =
            MeshFolder + "/M_FanCardBackGoldTrim.asset";
        private const string SpadeMeshPath = MeshFolder + "/M_FanCardSpade.asset";
        private const string SpadeStripeMeshPath = MeshFolder + "/M_FanCardSpadeSlots.asset";

        private const string GunmetalMaterialPath = MaterialFolder + "/M_FanCardGunmetal.mat";
        private const string SilverMaterialPath = MaterialFolder + "/M_FanCardWarmSilver.mat";
        private const string EtchingMaterialPath = MaterialFolder + "/M_FanCardEtching.mat";
        private const string GrooveMaterialPath = MaterialFolder + "/M_FanCardGroove.mat";
        private const string GoldMeshMaterialPath = MaterialFolder + "/M_FanCardGoldMesh.mat";
        private const string ChromeMaterialPath = MaterialFolder + "/M_FanCardChrome.mat";
        private const string GrainNormalPath = TextureFolder + "/T_FanCardBeadBlastNormal.png";
        private const string GunmetalGrainPath = TextureFolder + "/T_FanCardGunmetalGrain.png";
        private const string WovenTexturePath = TextureFolder + "/T_FanCardGoldWoven.png";
        private const string ReflectionPath = TextureFolder + "/C_FanCardSoftStudio.asset";
        private static readonly string[] MetalClickPaths =
        {
            "Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_01.wav",
            "Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_02.wav",
            "Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_03.wav",
            "Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_04.wav",
            "Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_05.wav"
        };

        [MenuItem("Tools/Codex/Fan Card/1 Build Magnetic Fan Card Scene")]
        public static void BuildScene()
        {
            EnsureFolders();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            FanCardVisualModelIntegrator.IntegrateBatch();
            ConfigureBackMechanismModelImporter();

            FanCardDetentProfile profile = CreateOrUpdateProfile();
            Texture2D grainNormal = CreateOrUpdateGrainNormal();
            Texture2D gunmetalGrain = CreateOrUpdateGunmetalGrain();
            Cubemap reflection = CreateOrUpdateReflection();

            Material gunmetal = CreateOrUpdateGunmetalMaterial(
                grainNormal,
                gunmetalGrain);
            Material silver = CreateOrUpdateSilverMaterial(grainNormal);
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
                FanCardSpecifications.GoldMetallic,
                FanCardSpecifications.GoldSmoothness,
                grainNormal,
                0.10f,
                new Vector2(92f, 92f));
            // This is deliberately an opaque metal material on genuinely
            // open geometry. A textured ribbon would hide the magnets and
            // collapse to a brown strip at oblique angles.
            goldMesh.SetTexture("_BaseMap", null);
            goldMesh.SetTexture("_MainTex", null);
            goldMesh.SetTextureScale("_BaseMap", Vector2.one);
            EditorUtility.SetDirty(goldMesh);
            Material chrome = CreateOrUpdateChromeMaterial();

            VisualMeshSource sourceBody = LoadVisualModelPart(
                "BottomCard",
                "BottomCard_GunmetalFrame");
            VisualMeshSource sourceFace = LoadVisualModelPart(
                "BottomCard",
                "BottomCard_WarmSilverFace");
            VisualMeshSource sourceGoldTrim = LoadVisualModelPart(
                "BottomCard",
                "BottomCard_GoldTrim");
            Bounds transformedBodyBounds = TransformBounds(
                sourceBody.Mesh.bounds,
                sourceBody.ObjectToCard);
            float visualYOffset = -transformedBodyBounds.center.y;
            Bounds transformedFaceBounds = TransformBounds(
                sourceFace.Mesh.bounds,
                sourceFace.ObjectToCard);
            float authoritativeFaceY =
                transformedFaceBounds.max.y + visualYOffset;
            Mesh bodyMesh = SaveMesh(
                ConvertAuthoritativeVisualMesh(
                    sourceBody,
                    "M_FanCardBody",
                    visualYOffset,
                    flattenSurface: false,
                    mirrorY: false),
                BodyMeshPath);
            Mesh faceMesh = SaveMesh(
                ConvertAuthoritativeVisualMesh(
                    sourceFace,
                    "M_FanCardFace",
                    visualYOffset,
                    flattenSurface: true,
                    mirrorY: false),
                FaceMeshPath);
            Mesh backFaceMesh = SaveMesh(
                ConvertAuthoritativeVisualMesh(
                    sourceFace,
                    "M_FanCardBackFace",
                    visualYOffset,
                    flattenSurface: true,
                    mirrorY: false),
                BackFaceMeshPath);
            Mesh goldTrimMesh = SaveMesh(
                ConvertAuthoritativeVisualMesh(
                    sourceGoldTrim,
                    "M_FanCardGoldTrim",
                    visualYOffset,
                    flattenSurface: false,
                    mirrorY: false),
                GoldTrimMeshPath);
            Mesh backGoldTrimMesh = SaveMesh(
                ConvertAuthoritativeVisualMesh(
                    sourceGoldTrim,
                    "M_FanCardBackGoldTrim",
                    visualYOffset,
                    flattenSurface: false,
                    mirrorY: true),
                BackGoldTrimMeshPath);
            Mesh trackShellMesh = LoadBackMechanismMesh("Track_Undercut");
            Mesh trackMesh = LoadBackMechanismMesh("Track_Grille");
            Mesh[] trackMagnetMeshes = Enumerable.Range(1, 3)
                .Select(index => LoadBackMechanismMesh($"Magnet_{index:D2}"))
                .ToArray();
            Mesh aceMesh = LoadBackMechanismMesh("Ace_A_Oxanium");
            Mesh queenMesh = LoadBackMechanismMesh("Queen_Q_Oxanium");
            Mesh kingMesh = LoadBackMechanismMesh("King_K_Oxanium");
            Mesh bearingCapMesh = LoadBackMechanismMesh(
                "Axis_BearingCap_Chrome");
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
                backFaceMesh,
                goldTrimMesh,
                backGoldTrimMesh,
                authoritativeFaceY,
                spadeMesh,
                spadeStripeMesh,
                trackShellMesh,
                trackMesh,
                trackMagnetMeshes,
                gunmetal,
                silver,
                etching,
                groove,
                goldMesh,
                chrome,
                aceMesh,
                hasTrack: false,
                hasFollower: true,
                profile);
            GameObject middle = CreateCardLayer(
                "MiddleCard",
                root.transform,
                1,
                bodyMesh,
                faceMesh,
                backFaceMesh,
                goldTrimMesh,
                backGoldTrimMesh,
                authoritativeFaceY,
                spadeMesh,
                spadeStripeMesh,
                trackShellMesh,
                trackMesh,
                trackMagnetMeshes,
                gunmetal,
                silver,
                etching,
                groove,
                goldMesh,
                chrome,
                aceMesh,
                hasTrack: true,
                hasFollower: true,
                profile);
            GameObject top = CreateCardLayer(
                "TopCard",
                root.transform,
                2,
                bodyMesh,
                faceMesh,
                backFaceMesh,
                goldTrimMesh,
                backGoldTrimMesh,
                authoritativeFaceY,
                spadeMesh,
                spadeStripeMesh,
                trackShellMesh,
                trackMesh,
                trackMagnetMeshes,
                gunmetal,
                silver,
                etching,
                groove,
                goldMesh,
                chrome,
                aceMesh,
                hasTrack: true,
                hasFollower: false,
                profile);
            _ = bottom;

            CreateAxisAssembly(
                root.transform,
                bearingCapMesh,
                gunmetal,
                chrome);

            FanCardFaceRankPresenter rankPresenter =
                root.AddComponent<FanCardFaceRankPresenter>();
            rankPresenter.Configure(
                aceMesh,
                queenMesh,
                kingMesh,
                new[]
                {
                    CreateRankLayerBinding(bottom.transform),
                    CreateRankLayerBinding(middle.transform),
                    CreateRankLayerBinding(top.transform)
                });

            Bounds interactionBounds =
                FanCardSpecifications.InteractionSweepBounds;
            BoxCollider interaction = root.AddComponent<BoxCollider>();
            interaction.center = interactionBounds.center;
            interaction.size = interactionBounds.size;

            var presentationFocusObject = new GameObject(
                "FanCardPresentationCenter");
            presentationFocusObject.transform.SetParent(root.transform, false);
            presentationFocusObject.transform.localPosition =
                FanCardController.ResolveFanCentroidLocal(0f);

            Camera camera = CreateStudio(root.transform, reflection);
            EdcPortraitCameraFramer framer =
                camera.gameObject.AddComponent<EdcPortraitCameraFramer>();
            framer.Configure(root.transform);
            framer.ConfigureFocusTarget(presentationFocusObject.transform);
            framer.ConfigureStableLocalBounds(
                FanCardSpecifications.CameraSweepBounds);
            framer.ConfigureFraming(ProductFramingCatalog.Resolve(
                FanCardSpecifications.ScenePath));
            framer.ConfigureLibraryPresentation(
                FanCardSpecifications.LibraryPreviewRollDegrees);
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
                profile,
                presentationFocusObject.transform);
            controller.ResetClosed();
            CreateMetalDetentAudio(root.transform, controller);

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
            FanCardFaceRankPresenter rankPresenter =
                root.GetComponent<FanCardFaceRankPresenter>();
            rankPresenter.ApplyPattern(FanCardRankPattern.QueenKingAce);
            Camera camera = Camera.main ?? UnityEngine.Object.FindAnyObjectByType<Camera>();
            EdcPortraitCameraFramer framer = camera.GetComponent<EdcPortraitCameraFramer>();
            framer.enabled = false;
            controller.enabled = false;
            controller.SetFanProgress(
                FanCardSpecifications.LibraryPreviewProgress);

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
                1200,
                900);
            CaptureView(
                camera,
                environment,
                bounds,
                new Vector3(0.08f, -1f, -0.14f).normalized,
                Vector3.forward,
                Path.Combine(outputFolder, "fan-card-back.png"),
                900,
                1600);
            // The rear mechanism is authored only on the top and middle
            // cards. Capture the top-card underside explicitly so the preview
            // gate can never silently fall back to a forbidden bottom track.
            Transform topLayer = root.transform.Find("TopCard");
            Transform middleLayer = root.transform.Find("MiddleCard");
            Transform bottomLayer = root.transform.Find("BottomCard");
            Renderer grilleRenderer = topLayer
                .Find("CurvedTrack_GoldGrille")
                .GetComponent<Renderer>();
            Bounds backTrackDetailBounds = grilleRenderer.bounds;
            foreach (Renderer magnetRenderer in topLayer
                .Cast<Transform>()
                .Where(child => child.name.StartsWith("Magnet_"))
                .Select(child => child.GetComponent<Renderer>()))
            {
                backTrackDetailBounds.Encapsulate(magnetRenderer.bounds);
            }
            backTrackDetailBounds.Expand(0.007f);
            bool middleWasActive = middleLayer.gameObject.activeSelf;
            bool bottomWasActive = bottomLayer.gameObject.activeSelf;
            middleLayer.gameObject.SetActive(false);
            bottomLayer.gameObject.SetActive(false);
            CaptureView(
                camera,
                environment,
                backTrackDetailBounds,
                new Vector3(0.16f, -0.94f, -0.30f).normalized,
                Vector3.forward,
                Path.Combine(outputFolder, "fan-card-back-track-closeup.png"),
                1200,
                900);
            middleLayer.gameObject.SetActive(middleWasActive);
            bottomLayer.gameObject.SetActive(bottomWasActive);

            Renderer aceRenderer = topLayer
                .Find("RankGlyph_TopLeft")
                .GetComponent<Renderer>();
            Renderer cornerSpadeRenderer = topLayer
                .Find("CornerSpade_TopLeft")
                .GetComponent<Renderer>();
            Bounds aceDetailBounds = aceRenderer.bounds;
            aceDetailBounds.Encapsulate(cornerSpadeRenderer.bounds);
            aceDetailBounds.Expand(0.006f);
            CaptureView(
                camera,
                environment,
                aceDetailBounds,
                new Vector3(0f, 1f, -0.04f).normalized,
                Vector3.forward,
                Path.Combine(outputFolder, "fan-card-ace-closeup.png"),
                1000,
                1000);

            Renderer oppositeAceRenderer = topLayer
                .Find("RankGlyph_BottomRight")
                .GetComponent<Renderer>();
            Renderer oppositeSpadeRenderer = topLayer
                .Find("CornerSpade_BottomRight")
                .GetComponent<Renderer>();
            Bounds oppositeIndexBounds = oppositeAceRenderer.bounds;
            oppositeIndexBounds.Encapsulate(oppositeSpadeRenderer.bounds);
            oppositeIndexBounds.Expand(0.006f);
            CaptureView(
                camera,
                environment,
                oppositeIndexBounds,
                new Vector3(0f, 1f, -0.04f).normalized,
                Vector3.forward,
                Path.Combine(
                    outputFolder,
                    "fan-card-corner-index-bottom-right-closeup.png"),
                1000,
                1000);

            Vector3 cardInterior = topLayer.TransformPoint(
                FanCardSpecifications.CardCenterFromPivot);
            var materialDetailBounds = new Bounds(
                Vector3.Lerp(root.transform.position, cardInterior, 0.17f),
                new Vector3(0.026f, 0.014f, 0.022f));
            CaptureView(
                camera,
                environment,
                materialDetailBounds,
                new Vector3(0.28f, 0.78f, -0.56f).normalized,
                Vector3.forward,
                Path.Combine(outputFolder, "fan-card-bearing-closeup.png"),
                1200,
                800);

            Renderer recessedSpindleRenderer = root.transform
                .Find("CommonAxis_RecessedMatteSpindle")
                .GetComponent<Renderer>();
            Bounds axisDetailBounds = recessedSpindleRenderer.bounds;
            axisDetailBounds.Encapsulate(root.transform
                .Find("CommonAxis_BearingCap_Chrome")
                .GetComponent<Renderer>()
                .bounds);
            axisDetailBounds.Expand(0.011f);
            CaptureView(
                camera,
                environment,
                axisDetailBounds,
                new Vector3(0.06f, 1f, -0.10f).normalized,
                Vector3.forward,
                Path.Combine(outputFolder, "fan-card-axis-closeup.png"),
                1000,
                1000);

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

            // Both allowed whole-set states are captured from the shipping
            // scene. This is deterministic editor evidence; runtime still
            // selects one state at each detail entry.
            rankPresenter.ApplyPattern(FanCardRankPattern.TripleAce);
            controller.SetFanProgress(FanCardSpecifications.LibraryPreviewProgress);
            bounds = ResolveBounds(root.transform);
            CaptureView(
                camera,
                environment,
                bounds,
                EdcPortraitCameraFramer.DefaultDetailFramingBackward,
                Vector3.up,
                Path.Combine(outputFolder, "fan-card-aaa-hero.png"),
                900,
                1600);
            CaptureView(
                camera,
                environment,
                bounds,
                new Vector3(0f, 1f, -0.08f).normalized,
                Vector3.forward,
                Path.Combine(outputFolder, "fan-card-aaa-top.png"),
                900,
                1600);
            rankPresenter.ApplyPattern(FanCardRankPattern.QueenKingAce);
            CaptureView(
                camera,
                environment,
                bounds,
                EdcPortraitCameraFramer.DefaultDetailFramingBackward,
                Vector3.up,
                Path.Combine(outputFolder, "fan-card-qka-hero.png"),
                900,
                1600);
            CaptureView(
                camera,
                environment,
                bounds,
                new Vector3(0f, 1f, -0.08f).normalized,
                Vector3.forward,
                Path.Combine(outputFolder, "fan-card-qka-top.png"),
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
            CaptureView(
                camera,
                environment,
                bounds,
                new Vector3(0.02f, 0.08f, -1f).normalized,
                Vector3.up,
                Path.Combine(outputFolder, "fan-card-side-profile.png"),
                1200,
                800);
            CaptureLibraryPreview(
                controller,
                framer,
                camera,
                environment,
                outputFolder);

            CaptureMotionFrame(
                controller,
                root.transform,
                camera,
                environment,
                outputFolder,
                1f,
                "fan-card-motion-90.png");
            CaptureMotionFrame(
                controller,
                root.transform,
                camera,
                environment,
                outputFolder,
                2f / 3f,
                "fan-card-motion-60.png");
            CaptureMotionFrame(
                controller,
                root.transform,
                camera,
                environment,
                outputFolder,
                1f / 3f,
                "fan-card-motion-30.png");
            CaptureMotionFrame(
                controller,
                root.transform,
                camera,
                environment,
                outputFolder,
                0f,
                "fan-card-motion-00.png");

            controller.SetFanProgress(
                FanCardSpecifications.LibraryPreviewProgress);
            bounds = ResolveBounds(root.transform);
            Vector3 thumbnailBackward =
                EdcPortraitCameraFramer.DefaultDetailFramingBackward;
            CaptureView(
                camera,
                environment,
                bounds,
                thumbnailBackward,
                ResolveRolledUp(
                    thumbnailBackward,
                    FanCardSpecifications.LibraryPreviewRollDegrees),
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
            rankPresenter.ApplyPattern(FanCardRankPattern.TripleAce);
            Debug.Log($"[FanCard] Unity material and AAA/QKA previews: {outputFolder}");
        }

        private static void CaptureMotionFrame(
            FanCardController controller,
            Transform root,
            Camera camera,
            SpinnerEnvironmentPresenter environment,
            string outputFolder,
            float progress,
            string fileName)
        {
            controller.SetFanProgress(progress);
            Bounds bounds = TransformLocalBounds(
                root,
                FanCardSpecifications.CameraSweepBounds);
            CaptureView(
                camera,
                environment,
                bounds,
                EdcPortraitCameraFramer.DefaultDetailFramingBackward,
                Vector3.up,
                Path.Combine(outputFolder, fileName),
                900,
                1600,
                ProductFramingCatalog.FanCardDetailWidthFraction,
                ProductFramingCatalog.FanCardDetailHeightFraction);
        }

        private static void CaptureLibraryPreview(
            FanCardController controller,
            EdcPortraitCameraFramer framer,
            Camera camera,
            SpinnerEnvironmentPresenter environment,
            string outputFolder)
        {
            controller.SetFanProgress(0f);
            controller.SetLibraryPreviewActive(true);
            float previousAspect = camera.aspect;
            camera.aspect = 900f / 1600f;
            camera.ResetProjectionMatrix();
            framer.SetLibraryPreviewActive(true, true);
            environment.SetLibraryPreviewActive(true, true);
            environment.RefreshLayout();
            RenderCameraToPng(
                camera,
                Path.Combine(outputFolder, "fan-card-library-centered.png"),
                900,
                1600);
            framer.SetLibraryPreviewActive(false, true);
            controller.SetLibraryPreviewActive(false);
            environment.SetLibraryPreviewActive(false, true);
            camera.aspect = previousAspect;
            camera.ResetProjectionMatrix();
        }

        private static Vector3 ResolveRolledUp(
            Vector3 backward,
            float rollDegrees)
        {
            Vector3 forward = -backward.normalized;
            Vector3 baseUp = Vector3.ProjectOnPlane(Vector3.up, forward);
            if (baseUp.sqrMagnitude < 0.0001f)
            {
                baseUp = Vector3.ProjectOnPlane(Vector3.forward, forward);
            }
            return Quaternion.AngleAxis(rollDegrees, forward)
                * baseUp.normalized;
        }

        private static GameObject CreateCardLayer(
            string name,
            Transform parent,
            int level,
            Mesh bodyMesh,
            Mesh faceMesh,
            Mesh backFaceMesh,
            Mesh goldTrimMesh,
            Mesh backGoldTrimMesh,
            float authoritativeFaceY,
            Mesh spadeMesh,
            Mesh spadeStripeMesh,
            Mesh trackShellMesh,
            Mesh trackMesh,
            IReadOnlyList<Mesh> trackMagnetMeshes,
            Material gunmetal,
            Material silver,
            Material etching,
            Material groove,
            Material goldMesh,
            Material chrome,
            Mesh rankMesh,
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
            float bodyTop = bodyMesh.bounds.max.y;
            float bodyBottom = bodyMesh.bounds.min.y;
            CreateMeshObject(
                "WarmGoldTrim",
                layer.transform,
                goldTrimMesh,
                goldMesh,
                FanCardSpecifications.CardCenterFromPivot);
            CreateMeshObject(
                "WarmGoldBackTrim",
                layer.transform,
                backGoldTrimMesh,
                goldMesh,
                FanCardSpecifications.CardCenterFromPivot);

            // The authoritative FBX defines the face outline and elevation.
            // Unity flattens only its manufacturing-thin cap for rank swapping;
            // it never regenerates the visible rounded contour or normals.
            float faceY = authoritativeFaceY;
            CreateMeshObject(
                "WarmSilverFace",
                layer.transform,
                faceMesh,
                silver,
                FanCardSpecifications.CardCenterFromPivot
                    + Vector3.up * faceY);
            float backFaceY = -authoritativeFaceY;
            GameObject backFace = CreateMeshObject(
                "WarmSilverBackFace",
                layer.transform,
                backFaceMesh,
                silver,
                FanCardSpecifications.CardCenterFromPivot
                    + Vector3.up * backFaceY);
            backFace.transform.localRotation = Quaternion.Euler(180f, 0f, 0f);
            float artworkY = faceY + 0.000075f;
            AddFaceArtwork(
                layer.transform,
                artworkY,
                spadeMesh,
                spadeStripeMesh,
                etching,
                silver,
                rankMesh,
                FanCardSpecifications.CardCenterFromPivot,
                string.Empty);
            if (hasTrack)
            {
                GameObject trackUndercut = CreateMeshObject(
                    "CurvedTrack_Undercut",
                    layer.transform,
                    trackShellMesh,
                    groove,
                    Vector3.up * (backFaceY
                        - FanCardSpecifications.BackTrackUndercutOffset));
                GameObject trackInlay = CreateMeshObject(
                    "CurvedTrack_GoldGrille",
                    layer.transform,
                    trackMesh,
                    goldMesh,
                    Vector3.up * (backFaceY
                        - FanCardSpecifications.BackTrackInlayOffset));
                if (trackMagnetMeshes.Count != profile.DetentIntervals)
                {
                    throw new InvalidDataException(
                        "The Blender back mechanism must provide one magnet "
                        + "mesh for each interval in the four-detent profile.");
                }
                for (int detent = 1; detent < profile.DetentCount; detent++)
                {
                    CreateMeshObject(
                        $"Magnet_{detent:D2}",
                        layer.transform,
                        trackMagnetMeshes[detent - 1],
                        goldMesh,
                        Vector3.up * (backFaceY
                            - FanCardSpecifications.BackMagnetCenterOffset));
                }
            }

            if (hasFollower)
            {
                // A rear track on the card above runs over a shallow follower
                // cap seated in the front of the card below. Keeping the cap
                // inside the one-millimetre air gap prevents it from punching
                // through a face or appearing as unrelated front artwork.
                CreateCylinder(
                    "FollowerSeat_Undercut",
                    layer.transform,
                    new Vector3(
                        FanCardSpecifications.FollowerFromPivot.x,
                        bodyTop
                            + FanCardSpecifications.FollowerSeatHeight * 0.5f,
                        FanCardSpecifications.FollowerFromPivot.y),
                    FanCardSpecifications.FollowerSeatRadius,
                    FanCardSpecifications.FollowerSeatHeight,
                    groove,
                    36);
                GameObject follower = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                follower.name = "FollowerBearing_Chrome";
                follower.transform.SetParent(layer.transform, false);
                follower.transform.localPosition = new Vector3(
                    FanCardSpecifications.FollowerFromPivot.x,
                    bodyTop
                        + FanCardSpecifications.FollowerBallProtrusion
                        - FanCardSpecifications.FollowerBallRadius,
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
            Mesh rankMesh,
            Vector3 center,
            string suffix)
        {
            Vector3 heroPosition = center + new Vector3(0.003f, y, -0.0035f);
            CreateMeshObject(
                "Spade_Etched" + suffix,
                layer,
                spadeMesh,
                etching,
                heroPosition,
                new Vector3(1.10f, 1f, 1.10f));
            CreateMeshObject(
                "Spade_VerticalSlots" + suffix,
                layer,
                stripeMesh,
                silver,
                heroPosition + Vector3.up * 0.000035f,
                new Vector3(1.10f, 1f, 1.10f));

            CreateCornerIndex(
                layer,
                y,
                spadeMesh,
                etching,
                rankMesh,
                center,
                FanCardSpecifications.CornerTopLeftRankOffset,
                FanCardSpecifications.CornerTopLeftSpadeOffset,
                FanCardSpecifications.CornerTopLeftRotationDegrees,
                "TopLeft" + suffix);
            CreateCornerIndex(
                layer,
                y,
                spadeMesh,
                etching,
                rankMesh,
                center,
                FanCardSpecifications.CornerBottomRightRankOffset,
                FanCardSpecifications.CornerBottomRightSpadeOffset,
                FanCardSpecifications.CornerBottomRightRotationDegrees,
                "BottomRight" + suffix);

            if (FanCardSpecifications.DecorativeDotCountPerFront != 0)
            {
                throw new InvalidDataException(
                    "The approved Fan Card face has no decorative dot motif.");
            }
        }

        private static void CreateCornerIndex(
            Transform layer,
            float y,
            Mesh spadeMesh,
            Material etching,
            Mesh rankMesh,
            Vector3 center,
            Vector2 rankOffset,
            Vector2 spadeOffset,
            float rotationDegrees,
            string cornerName)
        {
            Quaternion indexRotation = Quaternion.Euler(
                0f,
                rotationDegrees,
                0f);
            GameObject rank = CreateMeshObject(
                "RankGlyph_" + cornerName,
                layer,
                rankMesh,
                etching,
                center + new Vector3(
                    rankOffset.x,
                    y + 0.000040f,
                    rankOffset.y),
                Vector3.one);
            rank.transform.localRotation = indexRotation;

            GameObject smallSpade = CreateMeshObject(
                "CornerSpade_" + cornerName,
                layer,
                spadeMesh,
                etching,
                center + new Vector3(
                    spadeOffset.x,
                    y + 0.000025f,
                    spadeOffset.y),
                Vector3.one * FanCardSpecifications.CornerSpadeScale);
            smallSpade.transform.localRotation = indexRotation;
        }

        private static FanCardRankLayerBinding CreateRankLayerBinding(
            Transform layer)
        {
            var binding = new FanCardRankLayerBinding();
            binding.Configure(
                layer.Find("RankGlyph_TopLeft").GetComponent<MeshFilter>(),
                layer.Find("RankGlyph_BottomRight").GetComponent<MeshFilter>());
            return binding;
        }

        private static void CreateAxisAssembly(
            Transform root,
            Mesh bearingCapMesh,
            Material spindleMaterial,
            Material chrome)
        {
            float totalHeight = FanCardSpecifications.LayerPitch * 2f
                + FanCardSpecifications.CardThickness;
            // Keep a non-rendered spindle marker for structural validation and
            // future joint authoring. The previous flush annulus read as an
            // unexplained floating ring. The shipping part below is instead a
            // narrower matte shaft recessed from both outer faces.
            var spindleMarker = new GameObject("CommonAxis_ShadowSleeve");
            spindleMarker.transform.SetParent(root, false);
            spindleMarker.transform.localPosition = new Vector3(
                0f,
                totalHeight * 0.5f - 0.0008f,
                0f);

            float bottomFace = -FanCardSpecifications.CardThickness * 0.5f;
            float topFace = FanCardSpecifications.LayerPitch * 2f
                + FanCardSpecifications.CardThickness * 0.5f;
            float spindleBottom = bottomFace
                + FanCardSpecifications.RecessedSpindleTopInset;
            float spindleTop = topFace
                - FanCardSpecifications.RecessedSpindleTopInset;
            CreateCylinder(
                "CommonAxis_RecessedMatteSpindle",
                root,
                new Vector3(0f, (spindleBottom + spindleTop) * 0.5f, 0f),
                FanCardSpecifications.RecessedSpindleRadius,
                spindleTop - spindleBottom,
                spindleMaterial,
                48);

            // One Blender-authored oblate cap covers the layered aperture
            // crescents and makes the shared pivot read as actual bearing
            // hardware. It is neither a ring nor a decorative free-floating
            // ball, and its lower half stays inside the real spindle hole.
            CreateMeshObject(
                "CommonAxis_BearingCap_Chrome",
                root,
                bearingCapMesh,
                chrome,
                Vector3.up * topFace);
        }

        private static Camera CreateStudio(Transform target, Cubemap reflection)
        {
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.22f, 0.205f, 0.185f);
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflectionTexture = reflection;
            RenderSettings.reflectionIntensity = 0.28f;

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
            key.intensity = 0.92f;
            key.shadows = LightShadows.Soft;
            keyObject.transform.rotation = Quaternion.Euler(48f, -34f, 0f);

            var fillObject = new GameObject("CoolBroadFill");
            Light fill = fillObject.AddComponent<Light>();
            fill.type = LightType.Directional;
            fill.color = new Color(0.62f, 0.72f, 0.82f);
            fill.intensity = 0.28f;
            fill.shadows = LightShadows.None;
            fillObject.transform.rotation = Quaternion.Euler(62f, 146f, 0f);

            // A low-energy frontal softbox keeps the bead-blasted metal
            // readable in left/right and low-angle product views without
            // creating a second hard highlight.
            var frontObject = new GameObject("SoftFrontLift");
            Light front = frontObject.AddComponent<Light>();
            front.type = LightType.Directional;
            front.color = new Color(0.90f, 0.87f, 0.82f);
            front.intensity = 0.10f;
            front.shadows = LightShadows.None;
            frontObject.transform.rotation = Quaternion.Euler(18f, 8f, 0f);

            var sideObject = new GameObject("CoolSideWallRim");
            Light side = sideObject.AddComponent<Light>();
            side.type = LightType.Directional;
            side.color = new Color(0.48f, 0.61f, 0.74f);
            side.intensity = 0.12f;
            side.shadows = LightShadows.None;
            sideObject.transform.rotation = Quaternion.Euler(12f, 112f, 0f);
            return camera;
        }

        private static FanCardMetalDetentAudio CreateMetalDetentAudio(
            Transform root,
            FanCardController controller)
        {
            var audioObject = new GameObject("FanCardMetalAudio");
            audioObject.transform.SetParent(root, false);
            var voices = new AudioSource[FanCardMetalAudioModel.VoiceCount];
            for (int index = 0; index < voices.Length; index++)
            {
                var voiceObject = new GameObject($"Voice_{index:00}");
                voiceObject.transform.SetParent(audioObject.transform, false);
                voices[index] = voiceObject.AddComponent<AudioSource>();
            }

            AudioClip[] variants = MetalClickPaths
                .Select(path => AssetDatabase.LoadAssetAtPath<AudioClip>(path))
                .ToArray();
            if (variants.Any(clip => clip == null))
            {
                throw new FileNotFoundException(
                    "One or more canonical metal detent click assets are missing.");
            }

            FanCardMetalDetentAudio audio =
                audioObject.AddComponent<FanCardMetalDetentAudio>();
            audio.Configure(
                controller,
                variants,
                voices,
                FanCardMetalAudioModel.DefaultMasterVolume);
            return audio;
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

        private static void ConfigureBackMechanismModelImporter()
        {
            AssetDatabase.ImportAsset(
                FanCardSpecifications.BackMechanismModelPath,
                ImportAssetOptions.ForceSynchronousImport);
            ModelImporter importer = AssetImporter.GetAtPath(
                FanCardSpecifications.BackMechanismModelPath) as ModelImporter;
            if (importer == null)
            {
                throw new FileNotFoundException(
                    "The Blender-authored Fan Card back mechanism is missing.",
                    FanCardSpecifications.BackMechanismModelPath);
            }
            bool requiresReimport = importer.globalScale != 1f
                || !importer.useFileScale
                || !importer.bakeAxisConversion
                || importer.importCameras
                || importer.importLights
                || importer.materialImportMode
                    != ModelImporterMaterialImportMode.None
                || !importer.isReadable
                || importer.meshCompression != ModelImporterMeshCompression.Off;
            if (!requiresReimport)
            {
                return;
            }
            importer.globalScale = 1f;
            importer.useFileScale = true;
            importer.bakeAxisConversion = true;
            importer.importCameras = false;
            importer.importLights = false;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            importer.isReadable = true;
            importer.meshCompression = ModelImporterMeshCompression.Off;
            importer.SaveAndReimport();
        }

        private static Mesh LoadBackMechanismMesh(string objectName)
        {
            Mesh mesh = AssetDatabase.LoadAllAssetsAtPath(
                    FanCardSpecifications.BackMechanismModelPath)
                .OfType<Mesh>()
                .FirstOrDefault(candidate => candidate.name == objectName
                    || candidate.name == objectName + "_Mesh");
            if (mesh == null)
            {
                throw new MissingReferenceException(
                    $"Blender FBX does not contain mesh '{objectName}'.");
            }
            return mesh;
        }

        private static VisualMeshSource LoadVisualModelPart(
            string cardName,
            string objectName)
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                FanCardVisualModelIntegrator.VisualModelPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(
                    "The authoritative visual FBX prefab is unavailable.");
            }
            GameObject instance = UnityEngine.Object.Instantiate(prefab);
            try
            {
                Transform modelRoot = instance.GetComponentsInChildren<Transform>(true)
                    .FirstOrDefault(item => item.name == "MagneticFanCard_Root")
                    ?? instance.transform;
                Transform card = modelRoot.GetComponentsInChildren<Transform>(true)
                    .FirstOrDefault(item => item.name == cardName);
                Transform part = card?.GetComponentsInChildren<Transform>(true)
                    .FirstOrDefault(item => item.name == objectName);
                Mesh mesh = part?.GetComponent<MeshFilter>()?.sharedMesh;
                if (card == null || part == null || mesh == null)
                {
                    throw new MissingReferenceException(
                        $"Authoritative visual FBX does not contain "
                        + $"{cardName}/{objectName}.");
                }
                var blenderToRuntime = Matrix4x4.zero;
                blenderToRuntime.m00 = 1f;
                blenderToRuntime.m12 = -1f;
                blenderToRuntime.m21 = 1f;
                blenderToRuntime.m33 = 1f;
                return new VisualMeshSource(mesh, blenderToRuntime);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance);
            }
        }

        private static Bounds TransformBounds(Bounds source, Matrix4x4 matrix)
        {
            Vector3 minimum = Vector3.positiveInfinity;
            Vector3 maximum = Vector3.negativeInfinity;
            Vector3 center = source.center;
            Vector3 extents = source.extents;
            for (int x = -1; x <= 1; x += 2)
            {
                for (int y = -1; y <= 1; y += 2)
                {
                    for (int z = -1; z <= 1; z += 2)
                    {
                        Vector3 point = matrix.MultiplyPoint3x4(
                            center + Vector3.Scale(
                                extents,
                                new Vector3(x, y, z)));
                        minimum = Vector3.Min(minimum, point);
                        maximum = Vector3.Max(maximum, point);
                    }
                }
            }
            return new Bounds(
                (minimum + maximum) * 0.5f,
                maximum - minimum);
        }

        private static Mesh ConvertAuthoritativeVisualMesh(
            VisualMeshSource source,
            string name,
            float yOffset,
            bool flattenSurface,
            bool mirrorY)
        {
            Vector3[] sourceVertices = source.Mesh.vertices;
            Vector3[] sourceNormals = source.Mesh.normals;
            Vector4[] sourceTangents = source.Mesh.tangents;
            Vector2[] sourceUvs = source.Mesh.uv;
            int[] sourceTriangles = source.Mesh.triangles;
            var cardVertices = sourceVertices
                .Select(vertex => source.ObjectToCard.MultiplyPoint3x4(vertex))
                .ToArray();
            float frontSurface = cardVertices.Max(vertex => vertex.y);
            var selectedTriangles = new List<int>(sourceTriangles.Length);
            for (int index = 0; index < sourceTriangles.Length; index += 3)
            {
                int a = sourceTriangles[index];
                int b = sourceTriangles[index + 1];
                int c = sourceTriangles[index + 2];
                if (flattenSurface
                    && (Mathf.Abs(cardVertices[a].y - frontSurface) > 0.000001f
                        || Mathf.Abs(cardVertices[b].y - frontSurface) > 0.000001f
                        || Mathf.Abs(cardVertices[c].y - frontSurface) > 0.000001f))
                {
                    continue;
                }
                selectedTriangles.Add(a);
                selectedTriangles.Add(b);
                selectedTriangles.Add(c);
            }

            int[] sourceIndices = flattenSurface
                ? selectedTriangles.Distinct().OrderBy(index => index).ToArray()
                : Enumerable.Range(0, sourceVertices.Length).ToArray();
            var remap = sourceIndices
                .Select((sourceIndex, outputIndex) => (sourceIndex, outputIndex))
                .ToDictionary(pair => pair.sourceIndex, pair => pair.outputIndex);
            var vertices = new Vector3[sourceIndices.Length];
            var normals = new Vector3[sourceIndices.Length];
            var tangents = new Vector4[sourceIndices.Length];
            var uvs = new Vector2[sourceIndices.Length];
            Matrix4x4 normalMatrix = source.ObjectToCard.inverse.transpose;
            for (int outputIndex = 0; outputIndex < sourceIndices.Length; outputIndex++)
            {
                int sourceIndex = sourceIndices[outputIndex];
                Vector3 vertex = cardVertices[sourceIndex];
                vertex.y += yOffset;
                vertex.x -= FanCardSpecifications.CardCenterFromPivot.x;
                vertex.z -= FanCardSpecifications.CardCenterFromPivot.z;
                if (flattenSurface)
                {
                    vertex.y = 0f;
                }
                if (mirrorY)
                {
                    vertex.y = -vertex.y;
                }
                vertices[outputIndex] = vertex;

                Vector3 normal = flattenSurface
                    ? Vector3.up
                    : normalMatrix.MultiplyVector(
                        sourceNormals[sourceIndex]).normalized;
                if (mirrorY)
                {
                    normal.y = -normal.y;
                }
                normals[outputIndex] = normal;

                Vector4 sourceTangent =
                    sourceTangents.Length == sourceVertices.Length
                        ? sourceTangents[sourceIndex]
                        : new Vector4(1f, 0f, 0f, 1f);
                Vector3 tangentDirection = source.ObjectToCard.MultiplyVector(
                    new Vector3(
                        sourceTangent.x,
                        sourceTangent.y,
                        sourceTangent.z)).normalized;
                if (mirrorY)
                {
                    tangentDirection.y = -tangentDirection.y;
                }
                tangents[outputIndex] = new Vector4(
                    tangentDirection.x,
                    tangentDirection.y,
                    tangentDirection.z,
                    sourceTangent.w);
                uvs[outputIndex] = sourceUvs.Length == sourceVertices.Length
                    ? sourceUvs[sourceIndex]
                    : Vector2.zero;
            }

            int[] triangles = selectedTriangles
                .Select(index => remap[index])
                .ToArray();
            for (int index = 0; index < triangles.Length; index += 3)
            {
                Vector3 a = vertices[triangles[index]];
                Vector3 b = vertices[triangles[index + 1]];
                Vector3 c = vertices[triangles[index + 2]];
                Vector3 geometricNormal = Vector3.Cross(b - a, c - a);
                Vector3 expectedNormal = (
                    normals[triangles[index]]
                    + normals[triangles[index + 1]]
                    + normals[triangles[index + 2]]).normalized;
                if (Vector3.Dot(geometricNormal, expectedNormal) < 0f)
                {
                    (triangles[index + 1], triangles[index + 2]) =
                        (triangles[index + 2], triangles[index + 1]);
                }
            }
            triangles = Enumerable.Range(0, triangles.Length / 3)
                .SelectMany(triangle =>
                {
                    int offset = triangle * 3;
                    int a = triangles[offset];
                    int b = triangles[offset + 1];
                    int c = triangles[offset + 2];
                    Vector3 ab = vertices[b] - vertices[a];
                    Vector3 bc = vertices[c] - vertices[b];
                    Vector3 ca = vertices[a] - vertices[c];
                    Vector3 cross = Vector3.Cross(ab, vertices[c] - vertices[a]);
                    bool collapsedEdge = ab.sqrMagnitude < 0.0000000000000001f
                        || bc.sqrMagnitude < 0.0000000000000001f
                        || ca.sqrMagnitude < 0.0000000000000001f;
                    bool flatDegenerate = flattenSurface
                        && cross.sqrMagnitude < 0.00000000000000000001f;
                    bool coversAxis = flattenSurface
                        && PointInTriangleXZ(
                            new Vector2(
                                FanCardSpecifications.PivotX,
                                FanCardSpecifications.PivotZ),
                            vertices[a],
                            vertices[b],
                            vertices[c]);
                    return collapsedEdge || flatDegenerate || coversAxis
                        ? Array.Empty<int>()
                        : new[] { a, b, c };
                })
                .ToArray();
            var mesh = new Mesh
            {
                name = name,
                indexFormat = source.Mesh.indexFormat,
                vertices = vertices,
                normals = normals,
                tangents = tangents,
                uv = uvs,
                triangles = triangles
            };
            mesh.RecalculateBounds();
            return mesh;
        }

        private static bool PointInTriangleXZ(
            Vector2 point,
            Vector3 a,
            Vector3 b,
            Vector3 c)
        {
            float d1 = Cross2D(
                point,
                new Vector2(a.x, a.z),
                new Vector2(b.x, b.z));
            float d2 = Cross2D(
                point,
                new Vector2(b.x, b.z),
                new Vector2(c.x, c.z));
            float d3 = Cross2D(
                point,
                new Vector2(c.x, c.z),
                new Vector2(a.x, a.z));
            bool hasNegative = d1 < -0.0000001f
                || d2 < -0.0000001f
                || d3 < -0.0000001f;
            bool hasPositive = d1 > 0.0000001f
                || d2 > 0.0000001f
                || d3 > 0.0000001f;
            return !(hasNegative && hasPositive);
        }

        private static float Cross2D(Vector2 point, Vector2 a, Vector2 b)
        {
            return (point.x - b.x) * (a.y - b.y)
                - (a.x - b.x) * (point.y - b.y);
        }

        private sealed class VisualMeshSource
        {
            public VisualMeshSource(Mesh mesh, Matrix4x4 objectToCard)
            {
                Mesh = mesh;
                ObjectToCard = objectToCard;
            }

            public Mesh Mesh { get; }
            public Matrix4x4 ObjectToCard { get; }
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

        private static Material CreateOrUpdateChromeMaterial()
        {
            Shader shader = Shader.Find("FidgetingApp/FanCardChrome");
            if (shader == null)
            {
                throw new MissingReferenceException(
                    "The fan-card chrome shader is unavailable.");
            }
            Material material = AssetDatabase.LoadAssetAtPath<Material>(
                ChromeMaterialPath);
            if (material == null)
            {
                material = new Material(shader) { name = "M_FanCardChrome" };
                AssetDatabase.CreateAsset(material, ChromeMaterialPath);
            }
            else
            {
                material.shader = shader;
                material.name = "M_FanCardChrome";
            }
            material.SetColor("_BaseColor", new Color(0.93f, 0.95f, 0.98f, 1f));
            material.SetFloat("_Smoothness", FanCardSpecifications.ChromeSmoothness);
            material.enableInstancing = true;
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Material CreateOrUpdateGunmetalMaterial(
            Texture2D grainNormal,
            Texture2D grainColor)
        {
            Shader shader = Shader.Find("FidgetingApp/FanCardGunmetal");
            if (shader == null)
            {
                throw new MissingReferenceException(
                    "The fan-card gunmetal shader is unavailable.");
            }
            Material material = AssetDatabase.LoadAssetAtPath<Material>(
                GunmetalMaterialPath);
            if (material == null)
            {
                material = new Material(shader) { name = "M_FanCardGunmetal" };
                AssetDatabase.CreateAsset(material, GunmetalMaterialPath);
            }
            else
            {
                material.shader = shader;
                material.name = "M_FanCardGunmetal";
            }
            material.SetColor("_BaseColor", FanCardSpecifications.GunmetalColor);
            material.SetFloat("_Metallic", FanCardSpecifications.GunmetalMetallic);
            material.SetFloat("_Smoothness", FanCardSpecifications.GunmetalSmoothness);
            material.SetTexture("_BaseMap", grainColor);
            material.SetTextureScale("_BaseMap", new Vector2(6f, 6f));
            material.SetTexture("_BumpMap", grainNormal);
            material.SetTextureScale("_BumpMap", new Vector2(10f, 10f));
            material.SetFloat("_BumpScale", FanCardSpecifications.GrainBumpScale);
            material.enableInstancing = true;
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Material CreateOrUpdateSilverMaterial(Texture2D grainNormal)
        {
            Shader shader = Shader.Find("FidgetingApp/FanCardSatinSilver");
            if (shader == null)
            {
                throw new MissingReferenceException(
                    "The fan-card satin-silver shader is unavailable.");
            }
            Material material = AssetDatabase.LoadAssetAtPath<Material>(
                SilverMaterialPath);
            if (material == null)
            {
                material = new Material(shader) { name = "M_FanCardWarmSilver" };
                AssetDatabase.CreateAsset(material, SilverMaterialPath);
            }
            else
            {
                material.shader = shader;
                material.name = "M_FanCardWarmSilver";
            }
            material.SetColor("_BaseColor", FanCardSpecifications.WarmSilverColor);
            material.SetFloat("_Metallic", FanCardSpecifications.SilverMetallic);
            material.SetFloat("_Smoothness", FanCardSpecifications.SilverSmoothness);
            material.SetTexture("_BumpMap", grainNormal);
            material.SetTextureScale("_BumpMap", new Vector2(18f, 18f));
            material.SetFloat("_BumpScale", FanCardSpecifications.SilverBumpScale);
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

        private static Texture2D CreateOrUpdateGunmetalGrain()
        {
            const int size = 128;
            var random = new System.Random(0xB34D5A7);
            var texture = new Texture2D(size, size, TextureFormat.RGB24, false, false);
            var pixels = new Color[size * size];
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    float fine = (float)random.NextDouble();
                    float neighboring = (float)random.NextDouble();
                    float value = Mathf.Lerp(0.84f, 1.0f, fine * 0.72f + neighboring * 0.28f);
                    pixels[y * size + x] = new Color(value, value, value, 1f);
                }
            }
            texture.SetPixels(pixels);
            texture.Apply(false, false);
            WriteTexturePng(texture, GunmetalGrainPath);
            UnityEngine.Object.DestroyImmediate(texture);
            AssetDatabase.ImportAsset(
                GunmetalGrainPath,
                ImportAssetOptions.ForceSynchronousImport);
            TextureImporter importer =
                (TextureImporter)AssetImporter.GetAtPath(GunmetalGrainPath);
            importer.textureType = TextureImporterType.Default;
            importer.sRGBTexture = true;
            importer.wrapMode = TextureWrapMode.Repeat;
            importer.filterMode = FilterMode.Trilinear;
            importer.mipmapEnabled = true;
            importer.textureCompression = TextureImporterCompression.Compressed;
            importer.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(GunmetalGrainPath);
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
                            * Mathf.Lerp(0.90f, 1.06f, panel);
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
            int cornerSegments,
            Vector2? holeCenter = null,
            float holeRadius = 0f,
            float holeBevel = 0f)
        {
            float halfY = thickness * 0.5f;
            float safeBevel = Mathf.Min(bevel, Mathf.Min(radius * 0.55f, halfY));
            int radialSegments = Mathf.Max(
                96,
                cornerSegments * 4);
            Vector2 radialCenter = holeCenter ?? Vector2.zero;
            List<Vector2>[] rings =
            {
                RadialRoundedRectPoints(
                    width,
                    height,
                    radius,
                    safeBevel,
                    cornerSegments,
                    radialCenter,
                    radialSegments),
                RadialRoundedRectPoints(
                    width,
                    height,
                    radius,
                    0f,
                    cornerSegments,
                    radialCenter,
                    radialSegments),
                RadialRoundedRectPoints(
                    width,
                    height,
                    radius,
                    0f,
                    cornerSegments,
                    radialCenter,
                    radialSegments),
                RadialRoundedRectPoints(
                    width,
                    height,
                    radius,
                    safeBevel,
                    cornerSegments,
                    radialCenter,
                    radialSegments)
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
            if (holeCenter.HasValue && holeRadius > 0f)
            {
                float safeHoleBevel = Mathf.Min(
                    Mathf.Max(0f, holeBevel),
                    Mathf.Max(0f, halfY * 0.45f));
                AppendMatchedPerforatedCap(
                    vertices,
                    triangles,
                    rings[0],
                    holeCenter.Value,
                    holeRadius + safeHoleBevel,
                    -halfY,
                    false);
                AppendMatchedPerforatedCap(
                    vertices,
                    triangles,
                    rings[^1],
                    holeCenter.Value,
                    holeRadius + safeHoleBevel,
                    halfY,
                    true);
                AppendHoleWall(
                    vertices,
                    triangles,
                    holeCenter.Value,
                    holeRadius,
                    safeHoleBevel,
                    halfY,
                    radialSegments);
            }
            else
            {
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
            }
            return FinalizeMesh(name, vertices, triangles);
        }

        private static Mesh CreateRoundedSurfaceMesh(
            string name,
            float width,
            float height,
            float radius,
            int cornerSegments,
            Vector2 holeCenter,
            float holeRadius)
        {
            List<Vector2> outer = RoundedRectPoints(
                width,
                height,
                radius,
                0f,
                Mathf.Max(16, cornerSegments * 2));
            if (CircleIsInsideRoundedRect(
                holeCenter,
                holeRadius,
                width,
                height,
                radius))
            {
                int radialSegments = Mathf.Max(
                    96,
                    cornerSegments * 4);
                List<Vector2> matchedOuter = RadialRoundedRectPoints(
                    width,
                    height,
                    radius,
                    0f,
                    cornerSegments,
                    holeCenter,
                    radialSegments);
                var perforatedVertices = new List<Vector3>(radialSegments * 2);
                var perforatedTriangles = new List<int>(radialSegments * 6);
                AppendMatchedPerforatedCap(
                    perforatedVertices,
                    perforatedTriangles,
                    matchedOuter,
                    holeCenter,
                    holeRadius,
                    0f,
                    true);
                return FinalizeMesh(
                    name,
                    perforatedVertices,
                    perforatedTriangles);
            }
            List<Vector2> notched = SubtractCircularCornerNotch(
                outer,
                holeCenter,
                holeRadius,
                48);
            List<int> triangles = TriangulatePolygon(notched);
            EnsurePositiveYFacing(notched, triangles);
            return FinalizeMesh(
                name,
                notched.Select(point => new Vector3(point.x, 0f, point.y)).ToList(),
                triangles);
        }

        private static bool CircleIsInsideRoundedRect(
            Vector2 center,
            float circleRadius,
            float width,
            float height,
            float cornerRadius)
        {
            const int samples = 96;
            for (int index = 0; index < samples; index++)
            {
                float angle = index * Mathf.PI * 2f / samples;
                Vector2 point = center + new Vector2(
                    Mathf.Cos(angle),
                    Mathf.Sin(angle)) * circleRadius;
                if (!PointIsInsideRoundedRect(
                    point,
                    width,
                    height,
                    cornerRadius))
                {
                    return false;
                }
            }
            return true;
        }

        private static bool PointIsInsideRoundedRect(
            Vector2 point,
            float width,
            float height,
            float cornerRadius)
        {
            float x = Mathf.Abs(point.x);
            float z = Mathf.Abs(point.y);
            float halfWidth = width * 0.5f;
            float halfHeight = height * 0.5f;
            if (x > halfWidth || z > halfHeight)
            {
                return false;
            }
            float cornerX = halfWidth - cornerRadius;
            float cornerZ = halfHeight - cornerRadius;
            if (x <= cornerX || z <= cornerZ)
            {
                return true;
            }
            Vector2 delta = new(x - cornerX, z - cornerZ);
            return delta.sqrMagnitude <= cornerRadius * cornerRadius;
        }

        private static List<Vector2> RadialRoundedRectPoints(
            float width,
            float height,
            float radius,
            float inset,
            int cornerSegments,
            Vector2 origin,
            int radialSegments)
        {
            List<Vector2> boundary = RoundedRectPoints(
                width,
                height,
                radius,
                inset,
                Mathf.Max(16, cornerSegments * 2));
            var points = new List<Vector2>(radialSegments);
            for (int index = 0; index < radialSegments; index++)
            {
                float angle = index * Mathf.PI * 2f / radialSegments;
                Vector2 direction = new(Mathf.Cos(angle), Mathf.Sin(angle));
                points.Add(origin + direction
                    * RayToPolygonBoundary(origin, direction, boundary));
            }
            return points;
        }

        private static void AppendMatchedPerforatedCap(
            List<Vector3> vertices,
            List<int> triangles,
            IReadOnlyList<Vector2> outer,
            Vector2 center,
            float innerRadius,
            float y,
            bool top)
        {
            int start = vertices.Count;
            int count = outer.Count;
            for (int index = 0; index < count; index++)
            {
                float angle = index * Mathf.PI * 2f / count;
                Vector2 inner = center + new Vector2(
                    Mathf.Cos(angle),
                    Mathf.Sin(angle)) * innerRadius;
                vertices.Add(new Vector3(inner.x, y, inner.y));
                vertices.Add(new Vector3(outer[index].x, y, outer[index].y));
            }

            for (int index = 0; index < count; index++)
            {
                int next = (index + 1) % count;
                int inner = start + index * 2;
                int outerIndex = inner + 1;
                int nextInner = start + next * 2;
                int nextOuter = nextInner + 1;
                if (top)
                {
                    triangles.Add(inner);
                    triangles.Add(nextOuter);
                    triangles.Add(outerIndex);
                    triangles.Add(inner);
                    triangles.Add(nextInner);
                    triangles.Add(nextOuter);
                }
                else
                {
                    triangles.Add(inner);
                    triangles.Add(outerIndex);
                    triangles.Add(nextOuter);
                    triangles.Add(inner);
                    triangles.Add(nextOuter);
                    triangles.Add(nextInner);
                }
            }
        }

        private static List<Vector2> SubtractCircularCornerNotch(
            IReadOnlyList<Vector2> outer,
            Vector2 center,
            float radius,
            int arcSegments)
        {
            int entrySegment = -1;
            int exitSegment = -1;
            for (int index = 0; index < outer.Count; index++)
            {
                int next = (index + 1) % outer.Count;
                bool currentInside = IsInsideCircle(outer[index], center, radius);
                bool nextInside = IsInsideCircle(outer[next], center, radius);
                if (!currentInside && nextInside)
                {
                    entrySegment = index;
                }
                else if (currentInside && !nextInside)
                {
                    exitSegment = index;
                }
            }

            if (entrySegment < 0 || exitSegment < 0)
            {
                throw new InvalidDataException(
                    "The fan-card face cutout must intersect its rounded corner exactly twice.");
            }

            Vector2 entry = SegmentCircleIntersection(
                outer[entrySegment],
                outer[(entrySegment + 1) % outer.Count],
                center,
                radius);
            Vector2 exit = SegmentCircleIntersection(
                outer[exitSegment],
                outer[(exitSegment + 1) % outer.Count],
                center,
                radius);

            var polygon = new List<Vector2>(outer.Count + arcSegments);
            polygon.Add(exit);
            int cursor = (exitSegment + 1) % outer.Count;
            int entryOutside = entrySegment;
            while (true)
            {
                polygon.Add(outer[cursor]);
                if (cursor == entryOutside)
                {
                    break;
                }
                cursor = (cursor + 1) % outer.Count;
            }
            polygon.Add(entry);

            float entryAngle = Mathf.Atan2(
                entry.y - center.y,
                entry.x - center.x);
            float exitAngle = Mathf.Atan2(
                exit.y - center.y,
                exit.x - center.x);
            float counterClockwise = Mathf.Repeat(
                exitAngle - entryAngle,
                Mathf.PI * 2f);
            float clockwise = counterClockwise - Mathf.PI * 2f;
            float sweep = ArcMidpointIsInsideRoundedRect(
                center,
                radius,
                entryAngle,
                counterClockwise,
                FanCardSpecifications.FaceWidth,
                FanCardSpecifications.FaceHeight,
                FanCardSpecifications.FaceCornerRadius)
                ? counterClockwise
                : clockwise;
            int steps = Mathf.Max(8, Mathf.CeilToInt(
                Mathf.Abs(sweep) / (Mathf.PI * 2f) * arcSegments));
            for (int step = 1; step < steps; step++)
            {
                float angle = entryAngle + sweep * step / steps;
                polygon.Add(center + new Vector2(
                    Mathf.Cos(angle),
                    Mathf.Sin(angle)) * radius);
            }
            return polygon;
        }

        private static bool IsInsideCircle(
            Vector2 point,
            Vector2 center,
            float radius)
        {
            return (point - center).sqrMagnitude < radius * radius;
        }

        private static Vector2 SegmentCircleIntersection(
            Vector2 start,
            Vector2 end,
            Vector2 center,
            float radius)
        {
            Vector2 direction = end - start;
            Vector2 offset = start - center;
            float a = Vector2.Dot(direction, direction);
            float b = 2f * Vector2.Dot(offset, direction);
            float c = Vector2.Dot(offset, offset) - radius * radius;
            float discriminant = Mathf.Max(0f, b * b - 4f * a * c);
            float root = Mathf.Sqrt(discriminant);
            float first = (-b - root) / (2f * a);
            float second = (-b + root) / (2f * a);
            if (first >= -0.0001f && first <= 1.0001f)
            {
                return Vector2.LerpUnclamped(start, end, first);
            }
            if (second >= -0.0001f && second <= 1.0001f)
            {
                return Vector2.LerpUnclamped(start, end, second);
            }
            throw new InvalidDataException(
                "Could not resolve the fan-card face/circular-notch intersection.");
        }

        private static bool ArcMidpointIsInsideRoundedRect(
            Vector2 center,
            float radius,
            float startAngle,
            float sweep,
            float width,
            float height,
            float cornerRadius)
        {
            float angle = startAngle + sweep * 0.5f;
            Vector2 point = center + new Vector2(
                Mathf.Cos(angle),
                Mathf.Sin(angle)) * radius;
            float x = Mathf.Abs(point.x);
            float z = Mathf.Abs(point.y);
            float halfWidth = width * 0.5f;
            float halfHeight = height * 0.5f;
            if (x > halfWidth || z > halfHeight)
            {
                return false;
            }
            float cornerX = halfWidth - cornerRadius;
            float cornerZ = halfHeight - cornerRadius;
            if (x <= cornerX || z <= cornerZ)
            {
                return true;
            }
            return new Vector2(x - cornerX, z - cornerZ).sqrMagnitude
                <= cornerRadius * cornerRadius;
        }

        private static void AppendPerforatedCap(
            List<Vector3> vertices,
            List<int> triangles,
            IReadOnlyList<Vector2> outerPolygon,
            Vector2 center,
            float innerRadius,
            float y,
            bool top,
            int segments)
        {
            int start = vertices.Count;
            for (int index = 0; index < segments; index++)
            {
                float angle = index * Mathf.PI * 2f / segments;
                Vector2 direction = new(Mathf.Cos(angle), Mathf.Sin(angle));
                Vector2 inner = center + direction * innerRadius;
                Vector2 outer = center + direction
                    * RayToPolygonBoundary(center, direction, outerPolygon);
                vertices.Add(new Vector3(inner.x, y, inner.y));
                vertices.Add(new Vector3(outer.x, y, outer.y));
            }

            for (int index = 0; index < segments; index++)
            {
                int next = (index + 1) % segments;
                int inner = start + index * 2;
                int outer = inner + 1;
                int nextInner = start + next * 2;
                int nextOuter = nextInner + 1;
                if (top)
                {
                    triangles.Add(inner);
                    triangles.Add(nextOuter);
                    triangles.Add(outer);
                    triangles.Add(inner);
                    triangles.Add(nextInner);
                    triangles.Add(nextOuter);
                }
                else
                {
                    triangles.Add(inner);
                    triangles.Add(outer);
                    triangles.Add(nextOuter);
                    triangles.Add(inner);
                    triangles.Add(nextOuter);
                    triangles.Add(nextInner);
                }
            }
        }

        private static void AppendHoleWall(
            List<Vector3> vertices,
            List<int> triangles,
            Vector2 center,
            float radius,
            float bevel,
            float halfY,
            int segments)
        {
            float[] radii =
            {
                radius + bevel,
                radius,
                radius,
                radius + bevel
            };
            float[] heights =
            {
                -halfY,
                -halfY + bevel,
                halfY - bevel,
                halfY
            };
            int start = vertices.Count;
            for (int ring = 0; ring < radii.Length; ring++)
            {
                for (int index = 0; index < segments; index++)
                {
                    float angle = index * Mathf.PI * 2f / segments;
                    vertices.Add(new Vector3(
                        center.x + Mathf.Cos(angle) * radii[ring],
                        heights[ring],
                        center.y + Mathf.Sin(angle) * radii[ring]));
                }
            }

            for (int ring = 0; ring < radii.Length - 1; ring++)
            {
                int currentStart = start + ring * segments;
                int nextStart = currentStart + segments;
                for (int index = 0; index < segments; index++)
                {
                    int next = (index + 1) % segments;
                    triangles.Add(currentStart + index);
                    triangles.Add(nextStart + next);
                    triangles.Add(nextStart + index);
                    triangles.Add(currentStart + index);
                    triangles.Add(currentStart + next);
                    triangles.Add(nextStart + next);
                }
            }
        }

        private static float RayToPolygonBoundary(
            Vector2 origin,
            Vector2 direction,
            IReadOnlyList<Vector2> polygon)
        {
            float nearest = float.PositiveInfinity;
            for (int index = 0; index < polygon.Count; index++)
            {
                Vector2 a = polygon[index];
                Vector2 edge = polygon[(index + 1) % polygon.Count] - a;
                float denominator = Cross(direction, edge);
                if (Mathf.Abs(denominator) < 0.0000001f)
                {
                    continue;
                }
                Vector2 offset = a - origin;
                float distance = Cross(offset, edge) / denominator;
                float edgePosition = Cross(offset, direction) / denominator;
                if (distance >= 0f
                    && edgePosition >= -0.0001f
                    && edgePosition <= 1.0001f)
                {
                    nearest = Mathf.Min(nearest, distance);
                }
            }
            if (!float.IsFinite(nearest))
            {
                throw new InvalidDataException(
                    "Could not intersect the fan-card cap boundary.");
            }
            return nearest;
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
            int segments,
            bool faceDown)
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
                bool useDefaultWinding = faceDown
                    ? sweepDegrees > 0f
                    : sweepDegrees < 0f;
                if (!useDefaultWinding)
                {
                    triangles.Add(a);
                    triangles.Add(d);
                    triangles.Add(c);
                    triangles.Add(a);
                    triangles.Add(b);
                    triangles.Add(d);
                }
                else
                {
                    triangles.Add(a);
                    triangles.Add(c);
                    triangles.Add(d);
                    triangles.Add(a);
                    triangles.Add(d);
                    triangles.Add(b);
                }
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

        private static Bounds TransformLocalBounds(
            Transform root,
            Bounds localBounds)
        {
            Vector3 localExtents = localBounds.extents;
            Vector3 worldCenter = root.TransformPoint(localBounds.center);
            Vector3 worldX = root.TransformVector(
                new Vector3(localExtents.x, 0f, 0f));
            Vector3 worldY = root.TransformVector(
                new Vector3(0f, localExtents.y, 0f));
            Vector3 worldZ = root.TransformVector(
                new Vector3(0f, 0f, localExtents.z));
            Vector3 worldExtents = new(
                Mathf.Abs(worldX.x) + Mathf.Abs(worldY.x) + Mathf.Abs(worldZ.x),
                Mathf.Abs(worldX.y) + Mathf.Abs(worldY.y) + Mathf.Abs(worldZ.y),
                Mathf.Abs(worldX.z) + Mathf.Abs(worldY.z) + Mathf.Abs(worldZ.z));
            return new Bounds(worldCenter, worldExtents * 2f);
        }

        private static void CaptureView(
            Camera camera,
            SpinnerEnvironmentPresenter environment,
            Bounds bounds,
            Vector3 backward,
            Vector3 up,
            string path,
            int width,
            int height,
            float widthFraction = 0.86f,
            float heightFraction = 0.82f)
        {
            float previousAspect = camera.aspect;
            camera.aspect = width / (float)height;
            camera.ResetProjectionMatrix();
            float distance = RequiredPreviewDistance(
                camera,
                bounds,
                backward,
                up,
                widthFraction,
                heightFraction,
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
            EditorBuildSettings.scenes = ProductCatalog.ShippingScenePaths()
                .Select(path => new EditorBuildSettingsScene(path, true))
                .ToArray();
        }
    }
}
