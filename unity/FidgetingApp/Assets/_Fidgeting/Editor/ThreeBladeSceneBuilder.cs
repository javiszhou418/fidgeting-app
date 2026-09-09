using System.Collections.Generic;
using System.IO;
using FidgetingApp.Product;
using ThreeBladeEDC.Geometry;
using ThreeBladeEDC.Interaction;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace ThreeBladeEDC.EditorTools
{
    public static class ThreeBladeSceneBuilder
    {
        public const string ScenePath = "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity";
        public const string OriginalMetalScenePath =
            "Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity";
        private const string ImportedScenePath =
            "Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity";
        private const string TwoLobeScenePath =
            "Assets/_TwoLobeBar/Scenes/TwoLobeBar.unity";
        private const string EdcScenePath =
            "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const string MeshFolder = "Assets/_Fidgeting/Generated/Meshes";
        private const string DragonScaleRollbackModelPath =
            "Assets/_Fidgeting/Models/BlenderDragonScale/DragonScaleEDC.fbx";
        // GEEONE 龙鳞三叶: ModelPipeline metal-three-blade Gate 10 rev-002 export (two kinematic groups:
        // Rotor_Root spins about local +Y, Fixed_Root = Cap_Top + Cap_Bottom + Hub_Core stays with the fingers).
        public const string GeeoneModelPath =
            "Assets/_Fidgeting/Models/GeeoneTriSpinner/GeeoneTriSpinner.fbx";
        private const int RatchetAudioVoiceCount = 12;
        private static readonly string[] RatchetClickPaths =
        {
            "Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_01.wav",
            "Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_02.wav",
            "Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_03.wav",
            "Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_04.wav",
            "Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_05.wav"
        };

        [MenuItem("Fidgeting/Three-Blade/Rebuild Pointed Presentation")]
        public static void BuildPresentation()
        {
            BuildPresentation(ScenePath, installDragonScaleVisuals: false);
        }

        [MenuItem("Fidgeting/Three-Blade/Rebuild Original Metal Presentation")]
        public static void BuildOriginalMetalPresentation()
        {
            BuildPresentation(OriginalMetalScenePath, installDragonScaleVisuals: true);
        }

        private static void BuildPresentation(
            string outputScenePath,
            bool installDragonScaleVisuals)
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            AudioClip[] ratchetClickVariants = LoadRatchetClickVariants();
            ThreeBladeMaterialFactory.MaterialSet materials =
                ThreeBladeMaterialFactory.CreateOrUpdate();
            Mesh bladeSector = ProceduralMeshFactory.CreateBlade();
            Mesh bladeMesh = SaveMesh(
                ProceduralMeshFactory.CreateRadialCopies(
                    bladeSector,
                    "M_ThreeBladeFrame"),
                MeshFolder + "/M_ThreeBladeFrame.asset");
            UnityEngine.Object.DestroyImmediate(bladeSector);
            Mesh bladeInsetSector = ProceduralMeshFactory.CreateBladeInset();
            Mesh bladeInsetMesh = SaveMesh(
                ProceduralMeshFactory.CreateRadialCopies(
                    bladeInsetSector,
                    "M_ThreeBladeInsets"),
                MeshFolder + "/M_ThreeBladeInsets.asset");
            UnityEngine.Object.DestroyImmediate(bladeInsetSector);
            Mesh bladeCollisionMesh = SaveMesh(
                ProceduralMeshFactory.CreateBladeCollision(),
                MeshFolder + "/M_BladeCollision.asset");
            Mesh bearingBallCageMesh = SaveMesh(
                ProceduralMeshFactory.CreateBearingBallCage(),
                MeshFolder + "/M_BearingBallCage.asset");
            Mesh capMesh = SaveMesh(
                ProceduralMeshFactory.CreateScallopedDisc(
                    "M_ScallopedTopCap",
                    0.0172f,
                    0.0032f,
                    24,
                    6,
                    0.00012f,
                    0.00072f),
                MeshFolder + "/M_FacetedTopCap.asset");
            Mesh capCollisionMesh = SaveMesh(
                ProceduralMeshFactory.CreateFacetedDisc(
                    "M_TopCapCollision", 0.0172f, 0.0032f, 32, 0.00072f),
                MeshFolder + "/M_TopCapCollision.asset");
            Mesh bottomCapMesh = SaveMesh(
                ProceduralMeshFactory.CreateFacetedDisc(
                    "M_FacetedBottomCap", 0.0148f, 0.0028f, 96, 0.00062f),
                MeshFolder + "/M_FacetedBottomCap.asset");
            Mesh rotorCoreMesh = SaveMesh(
                ProceduralMeshFactory.CreateRing(
                    "M_RotorCore", 0.0168f, 0.0117f, 0.0056f, 128),
                MeshFolder + "/M_RotorCore.asset");
            Mesh outerRaceMesh = SaveMesh(
                ProceduralMeshFactory.CreateRing(
                    "M_BearingOuterRace", 0.0115f, 0.0090f, 0.0060f, 128),
                MeshFolder + "/M_BearingOuterRace.asset");
            Mesh innerRaceMesh = SaveMesh(
                ProceduralMeshFactory.CreateRing(
                    "M_BearingInnerRace", 0.0088f, 0.0042f, 0.0060f, 128),
                MeshFolder + "/M_BearingInnerRace.asset");
            Mesh washerMesh = SaveMesh(
                ProceduralMeshFactory.CreateRing(
                    "M_BearingWasher", 0.0110f, 0.0043f, 0.0006f, 96),
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
            rotorBody.angularDamping = 0f;
            rotorBody.maxAngularVelocity =
                global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultMaximumAngularSpeed;
            rotorBody.interpolation = RigidbodyInterpolation.Interpolate;
            rotorBody.collisionDetectionMode = CollisionDetectionMode.Discrete;
            rotorBody.constraints = RigidbodyConstraints.FreezePosition
                | RigidbodyConstraints.FreezeRotationX
                | RigidbodyConstraints.FreezeRotationZ;

            RotorRigidbodyController rotorController =
                rotor.AddComponent<RotorRigidbodyController>();
            rotor.AddComponent<SpinnerTouchSurface>();

            CreateMeshObject(
                "RotorCore",
                rotor.transform,
                rotorCoreMesh,
                new[] { materials.blade });
            CreateMeshObject(
                "BearingOuterRace",
                rotor.transform,
                outerRaceMesh,
                new[] { materials.bearing });

            GameObject frameVisual = CreateMeshObject(
                "ThreeBladeFrame",
                rotor.transform,
                bladeMesh,
                new[] { materials.blade, materials.bevel });
            GameObject insetVisual = CreateMeshObject(
                "ThreeBladeInsets",
                rotor.transform,
                bladeInsetMesh,
                new[] { materials.inset });
            insetVisual.transform.localPosition = new Vector3(0f, 0.00316f, 0f);
            // Keep three independent convex colliders for touch hit testing,
            // while the visible 120-degree array is one batched renderer.
            for (int i = 0; i < 3; i++)
            {
                GameObject blade = new GameObject($"Blade_{i:00}");
                blade.transform.SetParent(rotor.transform, false);
                blade.transform.localRotation = Quaternion.Euler(0f, i * 120f, 0f);

                MeshCollider collider = blade.AddComponent<MeshCollider>();
                collider.sharedMesh = bladeCollisionMesh;
                collider.convex = true;
            }

            GameObject axle = CreatePrimitive(
                PrimitiveType.Cylinder,
                "Axle",
                hub.transform,
                materials.bearing,
                new Vector3(0.0078f, 0.0035f, 0.0078f));
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
            topWasher.transform.localPosition = new Vector3(0f, 0.00355f, 0f);

            GameObject bottomWasher = CreateMeshObject(
                "BottomWasher",
                hub.transform,
                washerMesh,
                new[] { materials.darkRing });
            bottomWasher.transform.localPosition = new Vector3(0f, -0.00355f, 0f);

            GameObject topCap = CreateMeshObject(
                "TopCap",
                hub.transform,
                capMesh,
                new[] { materials.cap, materials.bevel });
            topCap.transform.localPosition = new Vector3(0f, 0.0056f, 0f);
            topCap.AddComponent<SpinnerTouchSurface>();
            MeshCollider topCapCollider = topCap.AddComponent<MeshCollider>();
            // The scalloped visual is intentionally decoupled from physics:
            // touch hit-testing only needs a coarse convex disc, not all 144
            // visual perimeter samples.
            topCapCollider.sharedMesh = capCollisionMesh;
            topCapCollider.convex = true;

            GameObject bottomCap = CreateMeshObject(
                "BottomCap",
                hub.transform,
                bottomCapMesh,
                new[] { materials.darkRing, materials.bevel });
            bottomCap.transform.localPosition = new Vector3(0f, -0.0054f, 0f);

            GameObject bearingVisual = new GameObject("BearingVisual");
            bearingVisual.transform.SetParent(root.transform, false);
            GameObject cage = new GameObject("BallCage");
            cage.transform.SetParent(bearingVisual.transform, false);
            cage.transform.localPosition = new Vector3(0f, -0.0004f, 0f);
            CreateMeshObject(
                "BearingBalls",
                cage.transform,
                bearingBallCageMesh,
                new[] { materials.bearing });

            Renderer[] presentationRenderers = installDragonScaleVisuals
                ? InstallGeeoneVisuals(
                    scene,
                    materials,
                    root.transform,
                    rotor.transform,
                    hub.transform,
                    cage.transform,
                    topCap.transform,
                    bottomCap.transform)
                : root.GetComponentsInChildren<Renderer>(true);

            BearingCageVisualSync cageSync =
                bearingVisual.AddComponent<BearingCageVisualSync>();
            cageSync.Configure(rotorController, cage.transform, 0.5f);

            MetalGlintController glint = root.AddComponent<MetalGlintController>();
            glint.Configure(rotorController, presentationRenderers);

            GameObject studio = new GameObject("Studio");
            studio.transform.SetParent(root.transform, false);
            CreateStudio(
                studio.transform,
                root.transform.position,
                materials.floor,
                materials.studioReflection,
                out Camera camera);
            camera.gameObject.AddComponent<AudioListener>();

            GameObject ratchetAudioObject = new GameObject("RatchetAudio");
            ratchetAudioObject.transform.SetParent(root.transform, false);
            AudioSource[] ratchetVoices = new AudioSource[RatchetAudioVoiceCount];
            for (int index = 0; index < ratchetVoices.Length; index++)
            {
                GameObject voiceObject = new GameObject($"Voice_{index:00}");
                voiceObject.transform.SetParent(ratchetAudioObject.transform, false);
                ratchetVoices[index] = voiceObject.AddComponent<AudioSource>();
            }
            MetalRatchetDetentAudio ratchetAudio =
                ratchetAudioObject.AddComponent<MetalRatchetDetentAudio>();
            ratchetAudio.Configure(
                rotorController,
                ratchetClickVariants,
                ratchetVoices,
                0.82f);

            GameObject windAudioObject = new GameObject("RotorWindAudio");
            windAudioObject.transform.SetParent(root.transform, false);
            RotorWindAudio windAudio =
                windAudioObject.AddComponent<RotorWindAudio>();
            windAudio.Configure(
                rotorController,
                3,
                RotorWindAudioModel.DefaultMasterVolume);

            OrbitPresentationCamera orbit =
                camera.gameObject.AddComponent<OrbitPresentationCamera>();
            orbit.Target = root.transform;
            orbit.FocusTarget = installDragonScaleVisuals
                ? RequireDescendant(topCap.transform, "Cap_Top")
                : topCap.transform;
            orbit.ConfigureFraming(ProductFramingCatalog.Resolve(outputScenePath));
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
                    Part(topWasher.transform, new Vector3(0f, 0.024f, 0f)),
                    Part(bearingVisual.transform, new Vector3(0f, 0.010f, 0f)),
                    Part(rotor.transform, Vector3.zero),
                    Part(bottomWasher.transform, new Vector3(0f, -0.016f, 0f)),
                    Part(bottomCap.transform, new Vector3(0f, -0.036f, 0f))
                });

            MobileRuntimeBootstrap runtime =
                root.AddComponent<MobileRuntimeBootstrap>();
            runtime.Configure(rotorController, gestures);

            rotorController.CaptureInitialPose();
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, outputScenePath);
            SetBuildScene();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log($"Three-Blade EDC presentation rebuilt: {outputScenePath}");
        }

        public static void BuildAndRenderPreview()
        {
            BuildPresentation();
            RenderCurrentPresentationPreview();
        }

        public static void RenderCurrentPresentationPreview()
        {
            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            Camera camera = Camera.main;
            if (camera == null)
            {
                throw new MissingReferenceException("Presentation camera tagged MainCamera was not found.");
            }

            string projectParent = Directory.GetParent(Application.dataPath).FullName;
            string artifactFolder = Path.GetFullPath(Path.Combine(projectParent, "../../Artifacts"));
            Directory.CreateDirectory(artifactFolder);
            GameObject root = scene.GetRootGameObjects()[0];
            Vector3 heroPosition = camera.transform.position;
            Quaternion heroRotation = camera.transform.rotation;
            string assembledPath = Path.Combine(artifactFolder, "three-blade-edc-preview.png");
            RenderCameraToPng(camera, assembledPath);

            camera.transform.position = root.transform.position + Vector3.up * 0.46f;
            camera.transform.LookAt(root.transform.position, Vector3.forward);
            string topPath = Path.Combine(artifactFolder, "three-blade-edc-top.png");
            RenderCameraToPng(camera, topPath);

            camera.transform.position = root.transform.position
                + new Vector3(-0.16f, 0.12f, -0.30f);
            camera.transform.LookAt(root.transform.position);
            string leftObliquePath = Path.Combine(
                artifactFolder,
                "three-blade-edc-left-oblique.png");
            RenderCameraToPng(camera, leftObliquePath);

            camera.transform.position = root.transform.position
                + new Vector3(0.16f, 0.12f, -0.30f);
            camera.transform.LookAt(root.transform.position);
            string rightObliquePath = Path.Combine(
                artifactFolder,
                "three-blade-edc-right-oblique.png");
            RenderCameraToPng(camera, rightObliquePath);

            camera.transform.position = root.transform.position
                + new Vector3(0f, 0.012f, -0.32f);
            camera.transform.LookAt(root.transform.position);
            string sidePath = Path.Combine(artifactFolder, "three-blade-edc-side.png");
            RenderCameraToPng(camera, sidePath);

            camera.transform.position = heroPosition;
            camera.transform.rotation = heroRotation;
            OffsetLocal(root.transform.Find("HubStatic/TopCap"), 0.043f);
            OffsetLocal(root.transform.Find("HubStatic/TopWasher"), 0.024f);
            OffsetLocal(root.transform.Find("BearingVisual"), 0.010f);
            OffsetLocal(root.transform.Find("HubStatic/BottomWasher"), -0.016f);
            OffsetLocal(root.transform.Find("HubStatic/BottomCap"), -0.036f);
            camera.transform.position = root.transform.position + new Vector3(0.18f, 0.14f, -0.48f);
            camera.transform.LookAt(root.transform.position);
            string explodedPath = Path.Combine(artifactFolder, "three-blade-edc-exploded.png");
            RenderCameraToPng(camera, explodedPath);

            // Reload the saved assembled scene so preview-only offsets are
            // never persisted into the interactive deliverable.
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            Debug.Log(
                $"Three-Blade EDC previews written: {assembledPath} | {topPath} | "
                + $"{leftObliquePath} | {rightObliquePath} | {sidePath} | {explodedPath}");
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

        private static Renderer[] InstallGeeoneVisuals(
            Scene scene,
            ThreeBladeMaterialFactory.MaterialSet materials,
            Transform productRoot,
            Transform rotor,
            Transform hub,
            Transform bearingCage,
            Transform topCap,
            Transform bottomCap)
        {
            ConfigureGeeoneImporter(GeeoneModelPath);
            GameObject modelAsset = AssetDatabase.LoadAssetAtPath<GameObject>(GeeoneModelPath);
            if (modelAsset == null)
            {
                throw new FileNotFoundException(
                    "The GEEONE tri-spinner FBX is missing.",
                    GeeoneModelPath);
            }

            DisableRenderer(rotor, "RotorCore");
            DisableRenderer(rotor, "BearingOuterRace");
            DisableRenderer(rotor, "ThreeBladeFrame");
            DisableRenderer(rotor, "ThreeBladeInsets");
            DisableRenderer(rotor, "RotorCoreTopTrim");
            DisableRenderer(hub, "Axle");
            DisableRenderer(hub, "BearingInnerRace");
            DisableRenderer(hub, "TopWasher");
            DisableRenderer(hub, "BottomWasher");
            DisableRenderer(hub, "TopCap");
            DisableRenderer(hub, "BottomCap");
            // No bearing is visible on the GEEONE design (D09: no bright bearing ring anywhere);
            // the static Hub_Core is the only thing between cap lip and rotor face.
            DisableRenderer(bearingCage, "BearingBalls");

            GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(
                modelAsset,
                scene);
            instance.name = "GeeoneTriSpinner_Source";
            instance.transform.SetParent(productRoot, false);
            // Blender +Y (blade at twelve o'clock in the authored top view) maps to Unity -Z through
            // FBX conversion; rotate about the +Y spin axis so one blade points at +Z / twelve o'clock.
            instance.transform.localRotation = Quaternion.Euler(0f, 180f, 0f);
            PrefabUtility.UnpackPrefabInstance(
                instance,
                PrefabUnpackMode.Completely,
                InteractionMode.AutomatedAction);

            Transform rotorRoot = RequireDescendant(instance.transform, "Rotor_Root");
            Transform capTop = RequireDescendant(instance.transform, "Cap_Top");
            Transform capBottom = RequireDescendant(instance.transform, "Cap_Bottom");
            Transform hubCore = RequireDescendant(instance.transform, "Hub_Core");
            RequireDescendant(instance.transform, "Rotor_Body");

            // Kinematics: Rotor_Root (blades + connecting ring) under the Rigidbody rotor; the caps ride the
            // exploded-view cap transforms; the hub core stays with the static hub.
            ReparentPreservingWorld(rotorRoot, rotor);
            ReparentPreservingWorld(capTop, topCap);
            ReparentPreservingWorld(capBottom, bottomCap);
            ReparentPreservingWorld(hubCore, hub);

            var renderers = new List<Renderer>();
            AddGeeoneRenderers(rotorRoot, materials, renderers);
            AddGeeoneRenderers(capTop, materials, renderers);
            AddGeeoneRenderers(capBottom, materials, renderers);
            AddGeeoneRenderers(hubCore, materials, renderers);

            UnityEngine.Object.DestroyImmediate(instance);
            return renderers.ToArray();
        }

        private static void ConfigureGeeoneImporter(string assetPath)
        {
            AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceSynchronousImport);
            ModelImporter importer = AssetImporter.GetAtPath(assetPath) as ModelImporter;
            if (importer == null)
            {
                throw new FileNotFoundException("GEEONE model importer is missing.", assetPath);
            }

            importer.globalScale = 1f;
            importer.useFileScale = true;
            importer.preserveHierarchy = true;
            importer.importAnimation = false;
            importer.importBlendShapes = false;
            importer.importCameras = false;
            importer.importLights = false;
            importer.importVisibility = false;
            importer.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
            importer.meshCompression = ModelImporterMeshCompression.Off;
            importer.optimizeMeshPolygons = true;
            importer.optimizeMeshVertices = true;
            importer.weldVertices = true;
            importer.isReadable = true;
            importer.importNormals = ModelImporterNormals.Import;
            importer.importTangents = ModelImporterTangents.CalculateMikk;
            importer.SaveAndReimport();
        }

        private static void AddGeeoneRenderers(
            Transform root,
            ThreeBladeMaterialFactory.MaterialSet materials,
            List<Renderer> destination)
        {
            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            for (int index = 0; index < renderers.Length; index++)
            {
                renderers[index].enabled = true;
                Material[] assigned = renderers[index].sharedMaterials;
                for (int materialIndex = 0; materialIndex < assigned.Length; materialIndex++)
                {
                    string name = assigned[materialIndex] != null ? assigned[materialIndex].name : string.Empty;
                    assigned[materialIndex] = name.Contains("DiscTurned")
                        ? materials.geeoneDisc
                        : name.Contains("HubDark")
                            ? materials.geeoneHubDark
                            : materials.geeoneSatin;
                }
                renderers[index].sharedMaterials = assigned;
                destination.Add(renderers[index]);
            }
        }

        private static Renderer[] InstallDragonScaleRollbackVisuals(
            Scene scene,
            ThreeBladeMaterialFactory.MaterialSet materials,
            Transform productRoot,
            Transform rotor,
            Transform hub,
            Transform bearingVisual,
            Transform bearingCage,
            Transform topCap,
            Transform topWasher,
            Transform bottomWasher,
            Transform bottomCap)
        {
            GameObject modelAsset = AssetDatabase.LoadAssetAtPath<GameObject>(
                DragonScaleRollbackModelPath);
            if (modelAsset == null)
            {
                throw new FileNotFoundException(
                    "The selected Dragon Scale rollback FBX is missing.",
                    DragonScaleRollbackModelPath);
            }

            DisableRenderer(rotor, "RotorCore");
            DisableRenderer(rotor, "BearingOuterRace");
            DisableRenderer(rotor, "ThreeBladeFrame");
            DisableRenderer(rotor, "ThreeBladeInsets");
            DisableRenderer(rotor, "RotorCoreTopTrim");
            DisableRenderer(hub, "Axle");
            DisableRenderer(hub, "BearingInnerRace");
            DisableRenderer(hub, "TopWasher");
            DisableRenderer(hub, "BottomWasher");
            DisableRenderer(hub, "TopCap");
            DisableRenderer(hub, "BottomCap");
            DisableRenderer(bearingCage, "BearingBalls");

            GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(
                modelAsset,
                scene);
            instance.name = "DragonScaleRollback_Source";
            instance.transform.SetParent(productRoot, false);
            // Blender's +Y reference-facing blade maps to Unity -Z through
            // FBX conversion. Rotate about the shipping +Y spin axis so the
            // authored composition keeps one blade at twelve o'clock, as in
            // the supplied front-view reference.
            instance.transform.localRotation = Quaternion.Euler(0f, 180f, 0f);
            PrefabUtility.UnpackPrefabInstance(
                instance,
                PrefabUnpackMode.Completely,
                InteractionMode.AutomatedAction);

            Transform rotorRoot = RequireDescendant(instance.transform, "Rotor_Root");
            Transform fixedRoot = RequireDescendant(instance.transform, "Fixed_Root");
            Transform importedBearing = RequireDescendant(
                instance.transform,
                "BearingAssembly_Root");
            Transform importedCage = RequireDescendant(
                instance.transform,
                "BearingCage_Root");
            Transform topCapRoot = RequireDescendant(instance.transform, "TopCap_Root");
            Transform topWasherRoot = RequireDescendant(
                instance.transform,
                "TopWasher_Root");
            Transform bottomWasherRoot = RequireDescendant(
                instance.transform,
                "BottomWasher_Root");
            Transform bottomCapRoot = RequireDescendant(
                instance.transform,
                "BottomCap_Root");

            ReparentPreservingWorld(rotorRoot, rotor);
            ReparentPreservingWorld(importedBearing, bearingVisual);
            ReparentPreservingWorld(topCapRoot, topCap);
            ReparentPreservingWorld(topWasherRoot, topWasher);
            ReparentPreservingWorld(bottomWasherRoot, bottomWasher);
            ReparentPreservingWorld(bottomCapRoot, bottomCap);
            ReparentPreservingWorld(fixedRoot, hub);

            var renderers = new List<Renderer>();
            AddRenderers(rotorRoot, materials, renderers);
            AddRenderers(importedBearing, materials, renderers);
            AddRenderers(topCapRoot, materials, renderers);
            AddRenderers(topWasherRoot, materials, renderers);
            AddRenderers(bottomWasherRoot, materials, renderers);
            AddRenderers(bottomCapRoot, materials, renderers);
            AddRenderers(fixedRoot, materials, renderers);

            UnityEngine.Object.DestroyImmediate(importedCage.gameObject);
            SetNamedRendererEnabled(topCapRoot, "FingerCapTop_AccentLine", false);
            SetNamedRendererEnabled(bottomCapRoot, "FingerCapBottom_AccentLine", false);
            SetNamedRendererEnabled(bearingCage, "BearingBalls", true);

            UnityEngine.Object.DestroyImmediate(instance);
            return renderers.ToArray();
        }

        private static void DisableRenderer(Transform parent, string childName)
        {
            Transform child = parent != null ? parent.Find(childName) : null;
            Renderer renderer = child != null ? child.GetComponent<Renderer>() : null;
            if (renderer != null)
            {
                renderer.enabled = false;
            }
        }

        private static void SetNamedRendererEnabled(
            Transform parent,
            string objectName,
            bool enabled)
        {
            Transform child = FindDescendant(parent, objectName);
            Renderer renderer = child != null ? child.GetComponent<Renderer>() : null;
            if (renderer != null)
            {
                renderer.enabled = enabled;
            }
        }

        private static Transform RequireDescendant(Transform root, string objectName)
        {
            Transform result = FindDescendant(root, objectName);
            if (result != null)
            {
                return result;
            }

            throw new MissingReferenceException(
                $"The imported metal model under {root.name} is missing {objectName}.");
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

        private static void AddRenderers(
            Transform root,
            ThreeBladeMaterialFactory.MaterialSet materials,
            List<Renderer> destination)
        {
            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            for (int index = 0; index < renderers.Length; index++)
            {
                renderers[index].enabled = true;
                Material[] assigned = renderers[index].sharedMaterials;
                for (int materialIndex = 0; materialIndex < assigned.Length; materialIndex++)
                {
                    assigned[materialIndex] = ResolveRollbackMaterial(
                        assigned[materialIndex],
                        materials);
                }
                renderers[index].sharedMaterials = assigned;
                destination.Add(renderers[index]);
            }
        }

        private static Material ResolveRollbackMaterial(
            Material imported,
            ThreeBladeMaterialFactory.MaterialSet materials)
        {
            if (imported == null)
            {
                return materials.blade;
            }

            string name = imported.name;
            if (name.Contains("Recess") || name.Contains("Black_POM"))
            {
                return name.Contains("POM") ? materials.darkRing : materials.inset;
            }
            if (name.Contains("Bearing"))
            {
                return materials.bearing;
            }
            if (name.Contains("Cap_Radial"))
            {
                return materials.cap;
            }
            if (name.Contains("Polished") || name.Contains("Gold"))
            {
                return materials.bevel;
            }
            return materials.blade;
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
            // The shipping product uses a pure-black Unity stage beneath the
            // native Liquid Glass shell. Keep the floor authored for optional
            // inspection, but do not spend fill-rate or tint the hero render.
            floor.SetActive(false);

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
                0.24f,
                74f);

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.16f, 0.18f, 0.22f);
            RenderSettings.ambientEquatorColor = new Color(0.075f, 0.085f, 0.10f);
            RenderSettings.ambientGroundColor = new Color(0.028f, 0.030f, 0.036f);
            RenderSettings.reflectionIntensity = 0.48f;
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
            color.postExposure.Override(0.75f);
            color.contrast.Override(4f);
            color.saturation.Override(-2f);

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

        private static AudioClip[] LoadRatchetClickVariants()
        {
            AudioClip[] clips = new AudioClip[RatchetClickPaths.Length];
            for (int index = 0; index < RatchetClickPaths.Length; index++)
            {
                string path = RatchetClickPaths[index];
                AudioImporter importer = AssetImporter.GetAtPath(path) as AudioImporter;
                if (importer == null)
                {
                    throw new FileNotFoundException(
                        "Missing atomic ratchet click variant.",
                        path);
                }

                AudioImporterSampleSettings settings = importer.defaultSampleSettings;
                settings.loadType = AudioClipLoadType.DecompressOnLoad;
                settings.compressionFormat = AudioCompressionFormat.PCM;
                settings.sampleRateSetting = AudioSampleRateSetting.PreserveSampleRate;
                settings.preloadAudioData = true;
                importer.defaultSampleSettings = settings;
                // The authored files are already mono. Avoid importer downmix
                // normalization so their small EQ/level differences survive.
                importer.forceToMono = false;
                importer.loadInBackground = false;
                importer.ambisonic = false;
                importer.SaveAndReimport();

                clips[index] = AssetDatabase.LoadAssetAtPath<AudioClip>(path);
                if (clips[index] == null
                    || clips[index].channels != 1
                    || clips[index].length < 0.03f
                    || clips[index].length > 0.08f)
                {
                    throw new InvalidDataException(
                        $"Ratchet click must be mono and 30–80 ms: {path}");
                }
            }

            return clips;
        }

        private static void SetBuildScene()
        {
            EditorBuildSettings.scenes = new[]
            {
                new EditorBuildSettingsScene(ScenePath, true),
                new EditorBuildSettingsScene(OriginalMetalScenePath, true),
                new EditorBuildSettingsScene(ImportedScenePath, true),
                new EditorBuildSettingsScene(TwoLobeScenePath, true),
                new EditorBuildSettingsScene(EdcScenePath, true)
            };
        }
    }
}
