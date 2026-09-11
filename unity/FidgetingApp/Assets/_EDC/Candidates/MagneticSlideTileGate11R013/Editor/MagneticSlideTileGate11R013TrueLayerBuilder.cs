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
    public static class MagneticSlideTileGate11R013TrueLayerBuilder
    {
        private const string ShippingScene = "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const string Root =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R013";
        private const string Materials = Root + "/Materials";
        private const string Generated = Root + "/Generated";
        private const string Source =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R011/Imported";
        private const string SourceFbx =
            Source + "/magnetic-slide-tile-render-r011.fbx";
        private const string OutputRelative =
            "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/"
            + "11-unity-parity/rev-013-true-layers";

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
            new("front", new Vector3(0f, 0.004f, -0.130f),
                new Vector3(0f, 0.004f, 0f), 25f, Pose.Closed),
            new("grazing-15", GrazingPosition(15f),
                new Vector3(0f, 0.004f, 0f), 24f, Pose.Closed),
            new("grazing-30", GrazingPosition(30f),
                new Vector3(0f, 0.004f, 0f), 24f, Pose.Closed),
            new("grazing-60", GrazingPosition(60f),
                new Vector3(0f, 0.004f, 0f), 24f, Pose.Closed),
            new("hero-closed", new Vector3(0.074f, 0.072f, -0.116f),
                new Vector3(0f, 0.005f, -0.002f), 19f, Pose.Closed),
            new("hero-max-open", new Vector3(0.074f, 0.072f, -0.116f),
                new Vector3(0f, 0.005f, 0.006f), 20f, Pose.MaximumOpen),
            new("lower-artwork-max-open",
                new Vector3(-0.060f, 0.060f, -0.100f),
                new Vector3(0f, 0.002f, 0.008f), 22f, Pose.MaximumOpen),
            new("side-macro", new Vector3(0.068f, 0.006f, -0.018f),
                new Vector3(0.018f, 0.004f, 0f), 14f, Pose.Closed),
            new("phone-closed", new Vector3(0.030f, 0.030f, -0.050f),
                Vector3.zero, 38f, Pose.Closed, 1290, 2796),
        };

        [MenuItem("Fidgeting/Model Pipeline/Capture Magnetic Slide True Layers R013")]
        public static void Capture()
        {
            Scene scene = EditorSceneManager.OpenScene(
                ShippingScene, OpenSceneMode.Single);
            string projectRoot =
                Directory.GetParent(Application.dataPath)!.FullName;
            string output = Path.Combine(projectRoot, OutputRelative);
            string onePassDirectory = Path.Combine(output, "A-one-pass-r012");
            string trueLayerDirectory = Path.Combine(output, "B-true-layers-r013");
            string frameDirectory = Path.Combine(output, "reflection-motion-frames");
            Directory.CreateDirectory(onePassDirectory);
            Directory.CreateDirectory(trueLayerDirectory);
            Directory.CreateDirectory(frameDirectory);

            Dictionary<string, string> protectedBefore =
                HashProtectedSources(projectRoot);
            string[] colliderBefore = ColliderIdentities();
            MagneticSlideTileShippingCoordinator coordinator =
                FindCoordinator();
            Camera shippingCamera = Camera.main
                ?? throw new InvalidDataException("Shipping camera missing.");
            MagneticSlideShippingLightingController lighting =
                shippingCamera.GetComponent<
                    MagneticSlideShippingLightingController>()
                ?? throw new InvalidDataException(
                    "Approved lighting controller missing.");
            lighting.ApplyVariant(MagneticSlideLightingVariant.BalancedBrighter);
            coordinator.SetPreviewActive(true);
            coordinator.ResetShippingPose(false);
            Camera camera = CreateCaptureCamera();

            ConfigureOnePassR012(coordinator.CandidateModel);
            Debug.Log(
                $"R013 capture camera={camera.name} "
                + $"mask={camera.cullingMask} "
                + $"candidateActive={coordinator.CandidateModel.activeInHierarchy}");
            foreach (MeshRenderer renderer in ProductRenderers(
                         coordinator.CandidateModel))
            {
                Debug.Log(
                    $"R013 renderer={renderer.name} enabled={renderer.enabled} "
                    + $"active={renderer.gameObject.activeInHierarchy} "
                    + $"layer={renderer.gameObject.layer} "
                    + $"bounds={renderer.bounds}");
            }
            Bounds baselineBounds = ProductBounds(
                coordinator.CandidateModel, includeTrueLayers: false);
            foreach (ViewRecipe view in Views.Where(
                         view => view.Id != "phone-closed"))
            {
                ApplyPose(coordinator, view.Pose);
                Render(camera, onePassDirectory, view);
            }

            LayerMaterials materials = CreateMaterials();
            InstallTrueLayers(coordinator.CandidateModel, materials);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ShippingScene, false);
            AssetDatabase.SaveAssets();

            foreach (ViewRecipe view in Views)
            {
                ApplyPose(coordinator, view.Pose);
                Render(camera, trueLayerDirectory, view);
            }
            float parallaxPixels = MeasureParallaxPixels(
                camera, coordinator.CandidateModel);
            CaptureReflectionMotion(
                camera, coordinator, frameDirectory);

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

            Bounds trueLayerBounds = ProductBounds(
                coordinator.CandidateModel, includeTrueLayers: true);
            Dictionary<string, string> protectedAfter =
                HashProtectedSources(projectRoot);
            string[] colliderAfter = ColliderIdentities();
            MagneticSlideTrueLayerAssembly[] assemblies =
                coordinator.CandidateModel
                    .GetComponentsInChildren<
                        MagneticSlideTrueLayerAssembly>(true);
            Shader[] shaders =
            {
                Shader.Find(
                    "FidgetingApp/MagneticSlideTile/TrueSubstrateR013"),
                Shader.Find(
                    "FidgetingApp/MagneticSlideTile/TrueMotifR013"),
                Shader.Find(
                    "FidgetingApp/MagneticSlideTile/TrueCrystalCapR013"),
            };
            int errors = shaders
                .Where(shader => shader != null)
                .Sum(shader => ShaderUtil.GetShaderMessages(shader)
                    .Count(message =>
                        message.severity
                        == ShaderCompilerMessageSeverity.Error));
            int warnings = shaders
                .Where(shader => shader != null)
                .Sum(shader => ShaderUtil.GetShaderMessages(shader)
                    .Count(message =>
                        message.severity
                        == ShaderCompilerMessageSeverity.Warning));
            bool protectedUnchanged = protectedBefore.All(
                pair => protectedAfter.TryGetValue(
                    pair.Key, out string value)
                    && value == pair.Value);
            float boundsCenterDelta = Vector3.Distance(
                baselineBounds.center, trueLayerBounds.center);
            float boundsSizeDelta = Vector3.Distance(
                baselineBounds.size, trueLayerBounds.size);
            TrueLayerReport report = new()
            {
                schemaVersion = 1,
                gate = "11-unity-parity",
                evidenceRevision = 13,
                sourceScene = ShippingScene,
                userFeedback = "我还是没看出层次感",
                rootCause =
                    "Rev12 remained one opaque surface. Its UV parallax, "
                    + "Fresnel and BRDF mixing had no spatially separated "
                    + "substrate, motif or crystal renderer.",
                architecture =
                    "Two cap assemblies. Each uses a cap-only substrate mesh, "
                    + "an alpha-tested motif mesh and a transparent crystal "
                    + "mesh nested inside the existing exterior boundary.",
                opticalDimensionsAuthority =
                    "user-authorized visual estimates; not measured production dimensions",
                substrateInsetMeters =
                    MagneticSlideTrueLayerAssembly.SubstrateInsetMeters,
                motifInsetMeters =
                    MagneticSlideTrueLayerAssembly.MotifInsetMeters,
                crystalCapThicknessMeters =
                    MagneticSlideTrueLayerAssembly.CrystalCapThicknessMeters,
                motifPhysicalThicknessMeters =
                    MagneticSlideTrueLayerAssembly.MotifPhysicalThicknessMeters,
                motifToSubstrateSeparationMeters =
                    MagneticSlideTrueLayerAssembly.SubstrateInsetMeters
                    - MagneticSlideTrueLayerAssembly.MotifInsetMeters,
                capToMotifSeparationMeters =
                    MagneticSlideTrueLayerAssembly.MotifInsetMeters,
                crystalIor = MagneticSlideTrueLayerAssembly.CrystalIor,
                measuredScreenParallaxPixelsAt15Degrees = parallaxPixels,
                layerAssemblyCount = assemblies.Length,
                addedRenderers = assemblies.Sum(
                    assembly => new[]
                    {
                        assembly.Substrate,
                        assembly.Motif,
                        assembly.CrystalCap,
                    }.Count(renderer => renderer != null && renderer.enabled)),
                estimatedAddedDrawCalls = 4,
                transparentLayerDraws = 2,
                transparentOverdrawLayers = 1,
                shaderTarget = "3.5",
                shaderErrorCount = errors,
                shaderWarningCount = warnings,
                shadersSupported =
                    shaders.All(shader => shader != null && shader.isSupported),
                srpBatcherLayout =
                    "Each shader uses one UnityPerMaterial CBUFFER.",
                estimatedMobileCost =
                    "Per visible face: substrate 3 texture + 1 cubemap "
                    + "sample, motif 2 texture + 1 cubemap sample on black "
                    + "pixels, crystal 1 opaque-color + 1 cubemap sample. "
                    + "Rev13 adds about 4 draw calls and one transparent "
                    + "cap overdraw layer versus rev12; no device GPU timing.",
                transparentSorting =
                    "Opaque substrate queue 2020; alpha-tested motif queue "
                    + "2480 with ZWrite; crystal queue 3090 with DepthOnly "
                    + "prepass and transparent forward pass.",
                minimumPhysicalLayerGapMeters =
                    MagneticSlideTrueLayerAssembly.MotifInsetMeters,
                estimatedDepthPrecisionMeters = 0.00001f,
                zFightingSafetyRatio =
                    MagneticSlideTrueLayerAssembly.MotifInsetMeters
                    / 0.00001f,
                boundsCenterDeltaMeters = boundsCenterDelta,
                boundsSizeDeltaMeters = boundsSizeDelta,
                boundsWithinExistingExterior =
                    boundsCenterDelta < 0.000001f
                    && boundsSizeDelta < 0.000001f,
                colliderIdentitiesUnchanged =
                    colliderBefore.SequenceEqual(colliderAfter),
                protectedRuntimeUnchanged = protectedUnchanged,
                endpointInterlockLegal =
                    coordinator.Mechanism.IsPoseLegal(),
                upperLowerMasksIndependent =
                    materials.UpperMotif.GetTexture("_MotifMask")
                    != materials.LowerMotif.GetTexture("_MotifMask"),
                artworkMeshesAreCapOnly = assemblies.All(
                    assembly =>
                        assembly.Motif.GetComponent<MeshFilter>()
                            .sharedMesh.subMeshCount == 1),
                emission = 0f,
                build42VisualAcceptance = "failed",
                build44InstallAuthorized = false,
                visualApproval = "pending",
            };
            report.pass =
                report.layerAssemblyCount == 2
                && report.addedRenderers == 6
                && report.measuredScreenParallaxPixelsAt15Degrees >= 1f
                && report.shadersSupported
                && report.shaderErrorCount == 0
                && report.boundsWithinExistingExterior
                && report.colliderIdentitiesUnchanged
                && report.protectedRuntimeUnchanged
                && report.endpointInterlockLegal
                && report.upperLowerMasksIndependent
                && report.artworkMeshesAreCapOnly
                && !report.build44InstallAuthorized;
            Directory.CreateDirectory(output);
            File.WriteAllText(
                Path.Combine(output, "unity-true-layer-report.json"),
                JsonUtility.ToJson(report, true) + Environment.NewLine);
            if (!report.pass)
                throw new InvalidDataException(
                    "True-layer material review failed.");
        }

        private static void ConfigureOnePassR012(GameObject product)
        {
            foreach (MagneticSlideTrueLayerAssembly assembly
                     in product.GetComponentsInChildren<
                         MagneticSlideTrueLayerAssembly>(true))
                UnityEngine.Object.DestroyImmediate(assembly.gameObject);
            Material upper = LoadMaterial(
                "Assets/_EDC/Candidates/MagneticSlideTileGate11R012/"
                + "Materials/M_G11R012_UpperLayeredTop.mat");
            Material lower = LoadMaterial(
                "Assets/_EDC/Candidates/MagneticSlideTileGate11R012/"
                + "Materials/M_G11R012_LowerLayeredTop.mat");
            foreach (MeshRenderer renderer in ProductRenderers(product))
            {
                renderer.GetComponent<MeshFilter>().sharedMesh =
                    LoadSourceMesh(renderer.name);
                renderer.sharedMaterials = MapSourceMaterials(
                    renderer.name,
                    renderer.name == "MovingTopBody" ? upper : lower);
            }
        }

        private static void InstallTrueLayers(
            GameObject product,
            LayerMaterials materials)
        {
            EnsureFolder(Root);
            EnsureFolder(Materials);
            EnsureFolder(Generated);
            foreach (MeshRenderer body in ProductRenderers(product))
            {
                Mesh sourceMesh = LoadSourceMesh(body.name);
                int topSubmesh = FindTopSubmesh(body.name);
                Mesh bodyMesh = UnityEngine.Object.Instantiate(sourceMesh);
                bodyMesh.name = body.name + "_TrueLayerBody_R013";
                bodyMesh.SetTriangles(
                    Array.Empty<int>(), topSubmesh, false);
                bodyMesh.bounds = sourceMesh.bounds;
                body.GetComponent<MeshFilter>().sharedMesh = SaveMesh(
                    bodyMesh, $"{Generated}/{bodyMesh.name}.asset");

                int[] topTriangles =
                    sourceMesh.GetTriangles(topSubmesh);
                Mesh capMesh = CreateCompactCapMesh(
                    sourceMesh,
                    topTriangles,
                    body.name + "_CapOnly_R013");
                capMesh = SaveMesh(
                    capMesh, $"{Generated}/{capMesh.name}.asset");
                Vector3 importedNormal = AverageOutwardNormal(
                    sourceMesh, topTriangles);
                Vector3 inward = ChooseInwardDirection(
                    sourceMesh.bounds,
                    capMesh.bounds,
                    importedNormal);
                Vector3 outward = -inward;
                bool upper = body.name == "MovingTopBody";
                Material substrate =
                    upper ? materials.UpperSubstrate : materials.LowerSubstrate;
                Material motif =
                    upper ? materials.UpperMotif : materials.LowerMotif;
                Material crystal =
                    upper ? materials.UpperCrystal : materials.LowerCrystal;
                body.sharedMaterials = MapSourceMaterials(
                    body.name, substrate);
                GameObject assemblyObject = new(
                    (upper ? "Upper" : "Lower")
                    + "_TrueLayerAssembly_R013");
                assemblyObject.transform.SetParent(body.transform, false);
                assemblyObject.layer = body.gameObject.layer;
                MagneticSlideTrueLayerAssembly assembly =
                    assemblyObject.AddComponent<
                        MagneticSlideTrueLayerAssembly>();
                MeshRenderer substrateRenderer = CreateLayerRenderer(
                    assemblyObject.transform,
                    (upper ? "Upper" : "Lower")
                    + "_SubstrateInlay_R013",
                    capMesh,
                    substrate,
                    inward
                    * MagneticSlideTrueLayerAssembly.SubstrateInsetMeters,
                    10);
                MeshRenderer motifRenderer = CreateLayerRenderer(
                    assemblyObject.transform,
                    (upper ? "Upper" : "Lower")
                    + "_EtchedMotif_R013",
                    capMesh,
                    motif,
                    inward
                    * MagneticSlideTrueLayerAssembly.MotifInsetMeters,
                    20);
                MeshRenderer capRenderer = CreateLayerRenderer(
                    assemblyObject.transform,
                    (upper ? "Upper" : "Lower")
                    + "_CrystalCap_R013",
                    capMesh,
                    crystal,
                    Vector3.zero,
                    30);
                assembly.Configure(
                    upper ? "upper" : "lower",
                    outward,
                    substrateRenderer,
                    motifRenderer,
                    capRenderer);
            }
        }

        private static LayerMaterials CreateMaterials()
        {
            EnsureFolder(Root);
            EnsureFolder(Materials);
            Cubemap environment = AssetDatabase.LoadAssetAtPath<Cubemap>(
                Source
                + "/Environment/MagneticSlideTileGate11R011Environment.cubemap")
                ?? throw new InvalidDataException("Approved cubemap missing.");
            Texture2D perimeter = LoadTexture("top-perimeter-mask.png");
            return new LayerMaterials(
                CreateSubstrate("Upper", "upper-albedo.png",
                    "upper-roughness.png", "upper-transport-normal-r011.png",
                    environment),
                CreateSubstrate("Lower", "lower-albedo.png",
                    "lower-roughness.png", "lower-transport-normal-r011.png",
                    environment),
                CreateMotif("Upper", "upper-artwork-mask.png",
                    perimeter, environment),
                CreateMotif("Lower", "lower-artwork-mask.png",
                    perimeter, environment),
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
                "FidgetingApp/MagneticSlideTile/TrueSubstrateR013")
                ?? throw new InvalidDataException(
                    "True substrate shader missing.");
            Material material = GetOrCreateMaterial(
                $"M_G11R013_{face}BloodRedSubstrate", shader);
            material.SetTexture("_BaseMap", LoadTexture(baseName));
            material.SetTexture(
                "_RoughnessMap", LoadTexture(roughnessName));
            material.SetTexture("_NormalMap", LoadTexture(normalName));
            material.SetTexture("_SharedEnvironment", environment);
            material.SetColor(
                "_BloodRed", new Color(0.56f, 0.012f, 0.026f, 1f));
            return SaveMaterial(material);
        }

        private static Material CreateMotif(
            string face,
            string maskName,
            Texture2D perimeter,
            Cubemap environment)
        {
            Shader shader = Shader.Find(
                "FidgetingApp/MagneticSlideTile/TrueMotifR013")
                ?? throw new InvalidDataException(
                    "True motif shader missing.");
            Material material = GetOrCreateMaterial(
                $"M_G11R013_{face}EtchedBlackMotif", shader);
            material.SetTexture("_MotifMask", LoadTexture(maskName));
            material.SetTexture("_PerimeterMask", perimeter);
            material.SetTexture("_SharedEnvironment", environment);
            material.SetColor(
                "_MotifColor",
                new Color(0.010f, 0.012f, 0.016f, 1f));
            material.SetFloat("_Roughness", 0.16f);
            material.SetFloat("_Metallic", 0.18f);
            return SaveMaterial(material);
        }

        private static Material CreateCrystal(
            string face,
            Cubemap environment)
        {
            Shader shader = Shader.Find(
                "FidgetingApp/MagneticSlideTile/TrueCrystalCapR013")
                ?? throw new InvalidDataException(
                    "True crystal shader missing.");
            Material material = GetOrCreateMaterial(
                $"M_G11R013_{face}CrystalCap", shader);
            material.SetTexture("_SharedEnvironment", environment);
            material.SetFloat("_Ior", 1.52f);
            material.SetFloat("_Roughness", 0.018f);
            material.SetFloat(
                "_ThicknessMeters",
                MagneticSlideTrueLayerAssembly.CrystalCapThicknessMeters);
            material.SetFloat("_Transmission", 0.92f);
            material.SetFloat("_ReflectionStrength", 0.86f);
            material.SetFloat("_RefractionPixels", 2.8f);
            material.renderQueue = 3090;
            return SaveMaterial(material);
        }

        private static MeshRenderer CreateLayerRenderer(
            Transform parent,
            string name,
            Mesh mesh,
            Material material,
            Vector3 localPosition,
            int sortingOrder)
        {
            GameObject layer = new(name);
            layer.transform.SetParent(parent, false);
            layer.transform.localPosition = localPosition;
            layer.layer = parent.gameObject.layer;
            MeshFilter filter = layer.AddComponent<MeshFilter>();
            filter.sharedMesh = mesh;
            MeshRenderer renderer = layer.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            renderer.lightProbeUsage = LightProbeUsage.Off;
            renderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
            renderer.motionVectorGenerationMode =
                MotionVectorGenerationMode.ForceNoMotion;
            renderer.sortingOrder = sortingOrder;
            return renderer;
        }

        private static Mesh LoadSourceMesh(string name)
        {
            return AssetDatabase.LoadAllAssetsAtPath(SourceFbx)
                .OfType<Mesh>()
                .Single(mesh => mesh.name == name);
        }

        private static int FindTopSubmesh(string rendererName)
        {
            Material[] sourceMaterials =
                SourceRenderer(rendererName).sharedMaterials;
            int index = Array.FindIndex(
                sourceMaterials,
                material => material != null
                    && material.name.Contains(
                        "TopArtwork",
                        StringComparison.OrdinalIgnoreCase));
            if (index < 0)
            {
                throw new InvalidDataException(
                    $"Top artwork submesh missing on {rendererName}.");
            }
            return index;
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
                    {
                        return LoadMaterial(
                            "Assets/_EDC/Candidates/"
                            + "MagneticSlideTileGate11R011/Materials/"
                            + "M_G11R011_SolidDarkSide.mat");
                    }
                    if (name.Contains(
                            "PolishedBrightSilverRim",
                            StringComparison.OrdinalIgnoreCase))
                    {
                        return LoadMaterial(
                            "Assets/_EDC/Candidates/"
                            + "MagneticSlideTileGate11R011/Materials/"
                            + "M_G11R011_PolishedBrightSilverRim.mat");
                    }
                    if (name.Contains(
                            "NeutralUnderside",
                            StringComparison.OrdinalIgnoreCase))
                    {
                        return LoadMaterial(
                            "Assets/_EDC/Candidates/"
                            + "MagneticSlideTileGate11R011/Materials/"
                            + "M_G11R011_NeutralUnderside.mat");
                    }
                    throw new InvalidDataException(
                        $"Unknown source material {name} "
                        + $"on {rendererName}.");
                })
                .ToArray();
        }

        private static MeshRenderer SourceRenderer(
            string rendererName)
        {
            GameObject source =
                AssetDatabase.LoadAssetAtPath<GameObject>(SourceFbx)
                ?? throw new InvalidDataException(
                    "Source FBX prefab missing.");
            return source.GetComponentsInChildren<MeshRenderer>(true)
                .Single(renderer => renderer.name == rendererName);
        }

        private static Vector3 AverageOutwardNormal(
            Mesh mesh,
            IReadOnlyList<int> triangles)
        {
            Vector3 sum = Vector3.zero;
            Vector3[] normals = mesh.normals;
            foreach (int index in triangles)
                sum += normals[index];
            if (sum.sqrMagnitude < 0.01f)
                throw new InvalidDataException(
                    $"Top cap normal is ambiguous on {mesh.name}.");
            return sum.normalized;
        }

        private static Mesh CreateCompactCapMesh(
            Mesh source,
            IReadOnlyList<int> sourceTriangles,
            string name)
        {
            int[] sourceIndices = sourceTriangles
                .Distinct()
                .OrderBy(index => index)
                .ToArray();
            Dictionary<int, int> remap = sourceIndices
                .Select((sourceIndex, compactIndex) =>
                    new { sourceIndex, compactIndex })
                .ToDictionary(
                    item => item.sourceIndex,
                    item => item.compactIndex);
            Vector3[] sourceVertices = source.vertices;
            Vector3[] sourceNormals = source.normals;
            Vector4[] sourceTangents = source.tangents;
            Vector2[] sourceUv = source.uv;
            Vector2[] sourceUv2 = source.uv2;
            Color[] sourceColors = source.colors;
            Mesh mesh = new()
            {
                name = name,
                indexFormat = source.indexFormat,
                vertices = sourceIndices
                    .Select(index => sourceVertices[index])
                    .ToArray(),
                normals = sourceIndices
                    .Select(index => sourceNormals[index])
                    .ToArray(),
                tangents = sourceIndices
                    .Select(index => sourceTangents[index])
                    .ToArray(),
                uv = sourceIndices
                    .Select(index => sourceUv[index])
                    .ToArray(),
            };
            if (sourceUv2.Length == source.vertexCount)
            {
                mesh.uv2 = sourceIndices
                    .Select(index => sourceUv2[index])
                    .ToArray();
            }
            if (sourceColors.Length == source.vertexCount)
            {
                mesh.colors = sourceIndices
                    .Select(index => sourceColors[index])
                    .ToArray();
            }
            mesh.SetTriangles(
                sourceTriangles.Select(index => remap[index]).ToArray(),
                0,
                true);
            mesh.RecalculateBounds();
            return mesh;
        }

        private static Vector3 ChooseInwardDirection(
            Bounds bodyBounds,
            Bounds capBounds,
            Vector3 importedNormal)
        {
            float inset =
                MagneticSlideTrueLayerAssembly.SubstrateInsetMeters;
            float alongImported = BoundsExpansion(
                bodyBounds, ShiftBounds(
                    capBounds, importedNormal * inset));
            float againstImported = BoundsExpansion(
                bodyBounds, ShiftBounds(
                    capBounds, -importedNormal * inset));
            return alongImported <= againstImported
                ? importedNormal
                : -importedNormal;
        }

        private static Bounds ShiftBounds(
            Bounds bounds,
            Vector3 offset)
        {
            bounds.center += offset;
            return bounds;
        }

        private static float BoundsExpansion(
            Bounds body,
            Bounds candidate)
        {
            Vector3 minimum = Vector3.Min(body.min, candidate.min);
            Vector3 maximum = Vector3.Max(body.max, candidate.max);
            return ((maximum - minimum) - body.size)
                .magnitude;
        }

        private static float MeasureParallaxPixels(
            Camera camera,
            GameObject product)
        {
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
            camera.usePhysicalProperties = false;
            camera.fieldOfView = 14f;
            camera.aspect = 1280f / 960f;
            MagneticSlideTrueLayerAssembly upper = product
                .GetComponentsInChildren<
                    MagneticSlideTrueLayerAssembly>(true)
                .Single(assembly => assembly.FaceId == "upper");
            Mesh capMesh =
                upper.CrystalCap.GetComponent<MeshFilter>().sharedMesh;
            Vector3 center = capMesh.bounds.center;
            Vector3 substrateWorld = upper.transform.TransformPoint(
                center - upper.LocalOutwardNormal
                * MagneticSlideTrueLayerAssembly.SubstrateInsetMeters);
            Vector3 motifWorld = upper.transform.TransformPoint(
                center - upper.LocalOutwardNormal
                * MagneticSlideTrueLayerAssembly.MotifInsetMeters);
            Vector3 substrateScreen =
                camera.WorldToScreenPoint(substrateWorld);
            Vector3 motifScreen = camera.WorldToScreenPoint(motifWorld);
            return Vector2.Distance(substrateScreen, motifScreen);
        }

        private static void CaptureReflectionMotion(
            Camera camera,
            MagneticSlideTileShippingCoordinator coordinator,
            string directory)
        {
            coordinator.ResetShippingPose(false);
            Vector3 target = new(0f, 0.004f, 0f);
            const int frameCount = 240;
            for (int frame = 0; frame < frameCount; frame++)
            {
                float phase = frame / (float)(frameCount - 1);
                float angle =
                    Mathf.Lerp(-68f, 68f, phase) * Mathf.Deg2Rad;
                float elevation =
                    Mathf.Lerp(16f, 52f,
                        0.5f - 0.5f
                        * Mathf.Cos(phase * Mathf.PI * 2f))
                    * Mathf.Deg2Rad;
                const float radius = 0.105f;
                Vector3 position = new(
                    Mathf.Sin(angle) * Mathf.Cos(elevation) * radius,
                    Mathf.Sin(elevation) * radius,
                    -Mathf.Cos(angle) * Mathf.Cos(elevation) * radius);
                camera.transform.SetPositionAndRotation(
                    position,
                    Quaternion.LookRotation(
                        target - position, Vector3.up));
                camera.usePhysicalProperties = false;
                camera.fieldOfView = 25f;
                RenderCurrent(
                    camera,
                    Path.Combine(
                        directory, $"frame-{frame:D4}.png"),
                    1280,
                    720);
            }
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
            Pose pose)
        {
            coordinator.ResetShippingPose(false);
            if (pose == Pose.MaximumOpen)
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
            camera.usePhysicalProperties = false;
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
                "CAM_Gate11R013_TrueLayerCapture")
            {
                hideFlags = HideFlags.HideAndDontSave,
            };
            Camera camera = cameraObject.AddComponent<Camera>();
            cameraObject.AddComponent<UniversalAdditionalCameraData>();
            UniversalAdditionalCameraData data =
                camera.GetUniversalAdditionalCameraData();
            data.cameraStack.Clear();
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

        private static MagneticSlideTileShippingCoordinator FindCoordinator()
        {
            return UnityEngine.Object.FindFirstObjectByType<
                       MagneticSlideTileShippingCoordinator>(
                       FindObjectsInactive.Include)
                   ?? throw new InvalidDataException(
                       "Shipping coordinator missing.");
        }

        private static MeshRenderer[] ProductRenderers(GameObject product)
        {
            return product.GetComponentsInChildren<MeshRenderer>(true)
                .Where(renderer =>
                    renderer.name == "MovingTopBody"
                    || renderer.name == "BottomExterior")
                .ToArray();
        }

        private static Bounds ProductBounds(
            GameObject product,
            bool includeTrueLayers)
        {
            MeshRenderer[] renderers = product
                .GetComponentsInChildren<MeshRenderer>(true)
                .Where(renderer => renderer.enabled
                    && (includeTrueLayers
                        || renderer.GetComponentInParent<
                            MagneticSlideTrueLayerAssembly>() == null))
                .ToArray();
            Bounds bounds = renderers[0].bounds;
            foreach (MeshRenderer renderer in renderers.Skip(1))
                bounds.Encapsulate(renderer.bounds);
            return bounds;
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
                    + $"{collider.bounds.size:R}|"
                    + $"{ColliderMeshIdentity(collider)}")
                .OrderBy(value => value, StringComparer.Ordinal)
                .ToArray();
        }

        private static string ColliderMeshIdentity(Collider collider)
        {
            if (collider is not MeshCollider meshCollider
                || meshCollider.sharedMesh == null)
                return "none";
            Mesh mesh = meshCollider.sharedMesh;
            return $"{AssetDatabase.GetAssetPath(mesh)}|"
                + $"{mesh.name}|{mesh.vertexCount}";
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

        private static Mesh SaveMesh(Mesh mesh, string path)
        {
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(mesh, path);
            return AssetDatabase.LoadAssetAtPath<Mesh>(path);
        }

        private static void EnsureFolder(string path)
        {
            string parent = Path.GetDirectoryName(path)!
                .Replace('\\', '/');
            string name = Path.GetFileName(path);
            if (!AssetDatabase.IsValidFolder(path))
                AssetDatabase.CreateFolder(parent, name);
        }

        private enum Pose
        {
            Closed,
            MaximumOpen,
        }

        private readonly struct ViewRecipe
        {
            public ViewRecipe(
                string id,
                Vector3 position,
                Vector3 lookAt,
                float fieldOfView,
                Pose pose,
                int width = 1280,
                int height = 960)
            {
                Id = id;
                Position = position;
                LookAt = lookAt;
                FieldOfView = fieldOfView;
                Pose = pose;
                Width = width;
                Height = height;
            }

            public string Id { get; }
            public Vector3 Position { get; }
            public Vector3 LookAt { get; }
            public float FieldOfView { get; }
            public Pose Pose { get; }
            public int Width { get; }
            public int Height { get; }
        }

        private sealed class LayerMaterials
        {
            public LayerMaterials(
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
        private sealed class TrueLayerReport
        {
            public int schemaVersion;
            public string gate;
            public int evidenceRevision;
            public string sourceScene;
            public string userFeedback;
            public string rootCause;
            public string architecture;
            public string opticalDimensionsAuthority;
            public float substrateInsetMeters;
            public float motifInsetMeters;
            public float crystalCapThicknessMeters;
            public float motifPhysicalThicknessMeters;
            public float motifToSubstrateSeparationMeters;
            public float capToMotifSeparationMeters;
            public float crystalIor;
            public float measuredScreenParallaxPixelsAt15Degrees;
            public int layerAssemblyCount;
            public int addedRenderers;
            public int estimatedAddedDrawCalls;
            public int transparentLayerDraws;
            public int transparentOverdrawLayers;
            public string shaderTarget;
            public int shaderErrorCount;
            public int shaderWarningCount;
            public bool shadersSupported;
            public string srpBatcherLayout;
            public string estimatedMobileCost;
            public string transparentSorting;
            public float minimumPhysicalLayerGapMeters;
            public float estimatedDepthPrecisionMeters;
            public float zFightingSafetyRatio;
            public float boundsCenterDeltaMeters;
            public float boundsSizeDeltaMeters;
            public bool boundsWithinExistingExterior;
            public bool colliderIdentitiesUnchanged;
            public bool protectedRuntimeUnchanged;
            public bool endpointInterlockLegal;
            public bool upperLowerMasksIndependent;
            public bool artworkMeshesAreCapOnly;
            public float emission;
            public string build42VisualAcceptance;
            public bool build44InstallAuthorized;
            public string visualApproval;
            public bool pass;
        }
    }
}
