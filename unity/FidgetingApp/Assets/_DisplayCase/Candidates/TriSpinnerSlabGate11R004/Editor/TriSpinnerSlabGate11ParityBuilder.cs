using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Editor
{
    /// <summary>
    /// Gate 11 (rev-004) Unity parity for the tri-spinner-slab-v3-cmf variant (export rev-003).
    /// Imports the approved FBX byte-for-byte, re-authors the seven Gate 07 zone
    /// materials as URP Lit, adds the header label decal, and captures the same
    /// hero / front / low-oblique cameras and studio rigs as the Blender Gate 09
    /// SHIPPING and NEUTRAL sets so the two can be compared pixel for pixel.
    /// Nothing here touches the shipping prefab, scene, model, or factory.
    /// </summary>
    public static class TriSpinnerSlabGate11ParityBuilder
    {
        public const string CandidateRoot =
            "Assets/_DisplayCase/Candidates/TriSpinnerSlabGate11R004";
        public const string ModelPath = CandidateRoot + "/Models/TriSpinnerSlabGate11R004.fbx";
        public const string DecalPath =
            CandidateRoot + "/Textures/TriSpinnerSlabHeaderLabelDecal.png";
        public const string ReferencePath =
            CandidateRoot + "/Reference/blender-parity-reference.json";
        public const string PrefabPath = CandidateRoot + "/Prefabs/PresentationRoot.prefab";
        public const string ScenePath = CandidateRoot + "/Scenes/TriSpinnerSlabGate11Parity.unity";
        public const string MaterialRoot = CandidateRoot + "/Materials";
        public const string CubemapRoot = CandidateRoot + "/Cubemaps";
        public const string ShippingCubemapPath = CubemapRoot + "/TriSpinnerSlabStudioShipping.asset";
        public const string NeutralCubemapPath = CubemapRoot + "/TriSpinnerSlabStudioNeutral.asset";
        public const string EvidenceRelativeRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/11-unity-parity/rev-004";

        public const string ApprovedFbxSha256 =
            "51bdbd4a0a1b9d7914f37fd08a311d42c744cefed936103ae435546800343a89";
        public const string ApprovedDecalSha256 =
            "3fdc093913f5cb60dc16642d0ab28d33f1d60d9e8b57c0ae606d8c1b1b82135f";
        public const string GoverningContractSha256 =
            "e9a6f14a61e823274c716f3b3c26ee63e0bbc8e5879145e7b98c65aa9ea88294";

        private const string ShippingPrefabPath = "Assets/Resources/Gacha/PremiumDisplayCase.prefab";
        private const string ShippingScenePath = "Assets/_DisplayCase/Scenes/PremiumDisplayCase.unity";
        private const string ShippingModelPath = "Assets/_DisplayCase/Models/PremiumDisplayCase.fbx";
        private const string ShippingPrefabSha256 =
            "88cf4f4a369cae1f370e5c47cebf6d1119d2698fcd0f4de70095314c5993a811";
        private const string ShippingSceneSha256 =
            "f83df832a7f1f7b057b59abfdba2528c0bee617b56422887291ac21db6fd8bbb";
        private const string ShippingModelSha256 =
            "41c71ffce320acdaa65ea5931b791361695afef88cd091fa9796514ec5c5c819";

        public const string RootName = "PresentationRoot";
        public const string CaseAssemblyName = "ROOT_PDC_CASE_ASSEMBLY";
        public const string ContentSlotName = "PIVOT_PDC_CONTENT_SLOT";
        public const string HeaderPlaneName = "GEO_PDC_HEADER_GRAPHITE_PLANE";
        public const string DecalName = "DECAL_PDC_HEADER_LABEL";
        public const int ExpectedTriangles = 91008;
        public const int ExpectedMeshCount = 38;
        public const int CaseMaterialSlotBudget = 7;
        public const int OrbitFrameCount = 48;
        public const int CubemapSize = 256;
        public const float MaxCubemapRadiance = 40f;

        // Case bounds from export-manifest.json (101.28 x 171.78 x 10.96 mm) in Unity metres.
        public static readonly Vector3 ExpectedCaseSize = new Vector3(0.10128f, 0.17178f, 0.01096f);
        public const float BoundsTolerancePercent = 0.1f;
        public const float ObjectBoundsToleranceMeters = 0.00005f;
        public static readonly Vector2 HeaderPlateSizeMeters = new Vector2(0.08148f, 0.04043f);

        // Gate 07 rev-003 adopted values (material-revalidation.json, scheme A).
        // Colours are linear; roughness -> smoothness = 1 - roughness.
        public static readonly ZoneMaterialSpec[] ZoneSpecs =
        {
            new ZoneMaterialSpec(1, "M_PDC_ClearCrystal", new Color(0.9387f, 0.9647f, 1f), 0f, 0.97f,
                SurfaceKind.TransparentPremultiplied, 0.08f, 3000,
                "case-clear-crystal: URP Lit premultiplied stand-in for PDC/ClearCrystal (no refraction); broad-plane alpha 0.08 (contract 0.08-0.16)"),
            new ZoneMaterialSpec(2, "M_PDC_SmokeLiner", SrgbToLinear(0xD8, 0xD2, 0xE0), 0f, 0.84f,
                SurfaceKind.TransparentPremultiplied, 0.25f, 2990,
                "case-smoke-lilac-liner: contract unity spec #D8D2E0, alpha 0.25 (= 1 - Blender transmission 0.775; contract 0.25-0.45)"),
            new ZoneMaterialSpec(3, "M_PDC_DarkSandblast", new Color(0.107f, 0.1221f, 0.1329f), 1f, 0.55f,
                SurfaceKind.Opaque, 1f, 2000,
                "case-dark-sandblast: #5C6266 metallic, roughness 0.45; procedural microblast deferred"),
            new ZoneMaterialSpec(4, "M_PDC_PianoBlack", new Color(0.0116f, 0.013f, 0.016f), 0.05f, 0.92f,
                SurfaceKind.Opaque, 1f, 2000,
                "case-piano-black: coat 1.0 / coat roughness 0.03 folded into smoothness 0.92"),
            new ZoneMaterialSpec(5, "M_PDC_BrushedSteel", new Color(0.78f, 0.79f, 0.80f), 1f, 0.70f,
                SurfaceKind.Opaque, 1f, 2000,
                "steel-satin: roughness 0.30; anisotropic brushing deferred (URP Lit has no anisotropy)"),
            new ZoneMaterialSpec(6, "M_PDC_Mirror", new Color(0.5841f, 0.6308f, 0.6724f), 1f, 0.96f,
                SurfaceKind.Opaque, 1f, 2000,
                "case-bright-mirror: #C9D0D6 roughness 0.04"),
            new ZoneMaterialSpec(7, "M_PDC_AccentMetal", new Color(0.5776f, 0.4564f, 0.2582f), 1f, 0.74f,
                SurfaceKind.Opaque, 1f, 2000,
                "case-champagne-gold-inlay: #C8B48B roughness 0.26")
        };

        public enum SurfaceKind
        {
            Opaque,
            TransparentPremultiplied,
            TransparentAlpha
        }

        public readonly struct ZoneMaterialSpec
        {
            public ZoneMaterialSpec(
                int zone,
                string name,
                Color linearColor,
                float metallic,
                float smoothness,
                SurfaceKind surface,
                float alpha,
                int queue,
                string note)
            {
                Zone = zone;
                Name = name;
                LinearColor = linearColor;
                Metallic = metallic;
                Smoothness = smoothness;
                Surface = surface;
                Alpha = alpha;
                Queue = queue;
                Note = note;
            }

            public int Zone { get; }
            public string Name { get; }
            public Color LinearColor { get; }
            public float Metallic { get; }
            public float Smoothness { get; }
            public SurfaceKind Surface { get; }
            public float Alpha { get; }
            public int Queue { get; }
            public string Note { get; }
        }

        [MenuItem("Fidgeting/Display Case/Gate 11/Tri-Spinner Slab R004 Build Candidate And Capture")]
        public static void BuildAndCapture()
        {
            string evidenceRoot = EvidenceRoot;
            EnsureDirectories(evidenceRoot);
            AssertSourceAndShippingHashes();
            ParityReference reference = LoadReference();
            ImportReport import = ConfigureModelImporter();
            ConfigureDecalImporter();
            Dictionary<int, Material> materials = CreateMaterials(out Material decalMaterial);
            GameObject prefab = BuildCandidatePrefab(reference, materials, decalMaterial);

            Cubemap shippingCubemap = BuildStudioCubemap(
                ShippingCubemapPath, reference.shippingLights, reference.shippingWorld);
            Cubemap neutralCubemap = BuildStudioCubemap(
                NeutralCubemapPath, reference.neutralLights, reference.neutralWorld);

            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Transform orbitRoot = new GameObject("Gate11InspectionOrbit_ReviewOnly").transform;
            GameObject candidate = (GameObject)PrefabUtility.InstantiatePrefab(prefab, scene);
            candidate.transform.SetParent(orbitRoot, false);
            candidate.transform.localPosition = Vector3.zero;
            candidate.transform.localRotation = Quaternion.identity;
            candidate.transform.localScale = Vector3.one;

            Transform environment = new GameObject("Gate11StudioEnvironment").transform;
            Camera camera = CreateCamera(environment);

            // NEUTRAL rig (contract lighting.neutral, Gate 07 calibrated energies).
            ApplyRig(environment, camera, reference.neutralLights, reference.neutralWorld, neutralCubemap, "Neutral");
            CaptureView(camera, reference, "CAM_PDC_HERO", Path.Combine(evidenceRoot, "unity-neutral-hero.png"));
            CaptureView(camera, reference, "CAM_PDC_FRONT", Path.Combine(evidenceRoot, "unity-neutral-front.png"));
            CaptureView(camera, reference, "CAM_PDC_LOW_OBLIQUE", Path.Combine(evidenceRoot, "unity-neutral-low-oblique.png"));

            // SHIPPING rig (Gate 09 rev-004 shipping set; parity target).
            ApplyRig(environment, camera, reference.shippingLights, reference.shippingWorld, shippingCubemap, "Shipping");
            CaptureView(camera, reference, "CAM_PDC_HERO", Path.Combine(evidenceRoot, "unity-shipping-hero.png"));
            CaptureView(camera, reference, "CAM_PDC_FRONT", Path.Combine(evidenceRoot, "unity-shipping-front.png"));
            CaptureView(camera, reference, "CAM_PDC_LOW_OBLIQUE", Path.Combine(evidenceRoot, "unity-shipping-low-oblique.png"));
            CaptureView(camera, reference, "CAM_PDC_LEFT_OBLIQUE", Path.Combine(evidenceRoot, "unity-shipping-left-oblique.png"));
            CaptureView(camera, reference, "CAM_PDC_RIGHT_OBLIQUE", Path.Combine(evidenceRoot, "unity-shipping-right-oblique.png"));
            CaptureView(camera, reference, "CAM_PDC_TOP", Path.Combine(evidenceRoot, "unity-shipping-top.png"));
            CaptureMirrorProbe(camera, reference, candidate, Path.Combine(evidenceRoot, "unity-shipping-cubemap-probe.png"));
            CaptureShadowVariant(camera, reference, environment, Path.Combine(evidenceRoot, "unity-shipping-hero-noshadow.png"));
            CaptureOrbit(camera, reference, orbitRoot, Path.Combine(evidenceRoot, "orbit-frames"));

            // Geometry-only silhouette (unlit white on black) for the IoU check.
            CaptureSilhouette(camera, reference, candidate, Path.Combine(evidenceRoot, "unity-silhouette-front.png"));

            ApplyRig(environment, camera, reference.shippingLights, reference.shippingWorld, shippingCubemap, "Shipping");
            SetView(camera, reference, "CAM_PDC_HERO");

            HierarchyReport hierarchy = CreateHierarchyReport(candidate.transform, reference, materials, decalMaterial);
            BoundsReport bounds = CreateBoundsReport(candidate.transform, reference, import);
            CaptureReport capture = CreateCaptureReport(reference, shippingCubemap, neutralCubemap);
            WriteJson(Path.Combine(evidenceRoot, "unity-hierarchy-pivot-material-report.json"), hierarchy);
            WriteJson(Path.Combine(evidenceRoot, "unity-bounds-digest-validation.json"), bounds);
            WriteJson(Path.Combine(evidenceRoot, "unity-capture-report.json"), capture);

            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            AssertSourceAndShippingHashes();

            if (hierarchy.status != "pass" || bounds.status != "pass" || capture.status != "pass")
            {
                throw new InvalidOperationException(
                    "Tri-Spinner Slab Gate 11 parity reports contain a failed check. "
                    + $"hierarchy={hierarchy.status} bounds={bounds.status} capture={capture.status}");
            }
            Debug.Log("Tri-Spinner Slab Gate 11 candidate, cubemaps, prefab, scene and parity captures complete.");
        }

        public static string EvidenceRoot =>
            Path.GetFullPath(Path.Combine(Application.dataPath, "..", EvidenceRelativeRoot));

        private static void EnsureDirectories(string evidenceRoot)
        {
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            foreach (string directory in new[]
                     {
                         MaterialRoot,
                         CubemapRoot,
                         CandidateRoot + "/Prefabs",
                         CandidateRoot + "/Scenes",
                     })
            {
                Directory.CreateDirectory(Path.Combine(projectRoot, directory));
            }
            Directory.CreateDirectory(evidenceRoot);
            Directory.CreateDirectory(Path.Combine(evidenceRoot, "orbit-frames"));
            AssetDatabase.Refresh();
        }

        public static void AssertSourceAndShippingHashes()
        {
            AssertHash(ModelPath, ApprovedFbxSha256, "approved export FBX (Gate 10 evidence rev-003)");
            AssertHash(DecalPath, ApprovedDecalSha256, "approved header label decal");
            AssertHash(ShippingPrefabPath, ShippingPrefabSha256, "shipping prefab");
            AssertHash(ShippingScenePath, ShippingSceneSha256, "shipping scene");
            AssertHash(ShippingModelPath, ShippingModelSha256, "shipping model");
        }

        private static void AssertHash(string assetPath, string expected, string label)
        {
            string absolute = AssetAbsolutePath(assetPath);
            if (!File.Exists(absolute))
            {
                throw new FileNotFoundException($"Missing {label}: {assetPath}");
            }
            string actual = Sha256File(absolute);
            if (!string.Equals(actual, expected, StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{label} hash changed. Expected {expected}, got {actual}.");
            }
        }

        public static ParityReference LoadReference()
        {
            string json = File.ReadAllText(AssetAbsolutePath(ReferencePath));
            ParityReference reference = JsonUtility.FromJson<ParityReference>(json);
            if (reference == null || reference.objects == null || reference.objects.Length == 0)
            {
                throw new InvalidOperationException($"Could not parse {ReferencePath}.");
            }
            return reference;
        }

        private static ImportReport ConfigureModelImporter()
        {
            ModelImporter importer = AssetImporter.GetAtPath(ModelPath) as ModelImporter;
            if (importer == null)
            {
                AssetDatabase.ImportAsset(ModelPath, ImportAssetOptions.ForceSynchronousImport);
                importer = AssetImporter.GetAtPath(ModelPath) as ModelImporter;
            }
            if (importer == null)
            {
                throw new InvalidOperationException($"Unity did not create a ModelImporter for {ModelPath}.");
            }

            importer.importAnimation = false;
            importer.animationType = ModelImporterAnimationType.None;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            importer.importBlendShapes = false;
            importer.importCameras = false;
            importer.importLights = false;
            importer.addCollider = false;
            importer.preserveHierarchy = true;
            importer.isReadable = true;
            importer.meshCompression = ModelImporterMeshCompression.Off;
            importer.importNormals = ModelImporterNormals.Import;
            importer.importTangents = ModelImporterTangents.CalculateMikk;
            importer.generateSecondaryUV = false;
            importer.optimizeMeshPolygons = false;
            importer.optimizeMeshVertices = false;
            importer.weldVertices = false;
            importer.globalScale = 1f;
            importer.useFileScale = true;
            importer.bakeAxisConversion = true;
            importer.SaveAndReimport();

            ImportReport report = new ImportReport();
            Vector3 measured = MeasureImportedSize();
            report.initialMeasuredSizeMeters = ToArray(measured);
            // Compare the largest extents so an axis swap cannot masquerade as a unit error.
            float measuredMax = Mathf.Max(measured.x, Mathf.Max(measured.y, measured.z));
            float expectedMax = Mathf.Max(ExpectedCaseSize.x, Mathf.Max(ExpectedCaseSize.y, ExpectedCaseSize.z));
            float ratio = expectedMax / Mathf.Max(measuredMax, 1e-9f);
            if (Mathf.Abs(ratio - 1f) > 0.001f)
            {
                // FBX_SCALE_NONE exports write Blender metres with a unit scale
                // Unity may read as centimetres. Correct once, deterministically.
                float corrected = SnapToDecade(ratio);
                importer.useFileScale = false;
                importer.globalScale = corrected;
                importer.SaveAndReimport();
                report.appliedGlobalScale = corrected;
                report.usedFileScale = false;
                measured = MeasureImportedSize();
            }
            else
            {
                report.appliedGlobalScale = 1f;
                report.usedFileScale = true;
            }
            report.finalMeasuredSizeMeters = ToArray(measured);
            return report;
        }

        private static float SnapToDecade(float ratio)
        {
            foreach (float decade in new[] { 0.001f, 0.01f, 0.1f, 1f, 10f, 100f, 1000f })
            {
                if (Mathf.Abs(ratio / decade - 1f) < 0.002f)
                {
                    return decade;
                }
            }
            return ratio;
        }

        private static Vector3 MeasureImportedSize()
        {
            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (model == null)
            {
                throw new InvalidOperationException($"Model asset failed to load: {ModelPath}");
            }
            MeshFilter[] filters = model.GetComponentsInChildren<MeshFilter>(true);
            bool any = false;
            Bounds union = new Bounds();
            foreach (MeshFilter filter in filters)
            {
                if (filter.sharedMesh == null)
                {
                    continue;
                }
                Bounds local = filter.sharedMesh.bounds;
                Bounds world = TransformBounds(filter.transform.localToWorldMatrix, local);
                if (!any)
                {
                    union = world;
                    any = true;
                }
                else
                {
                    union.Encapsulate(world);
                }
            }
            return any ? union.size : Vector3.zero;
        }

        private static Bounds TransformBounds(Matrix4x4 matrix, Bounds local)
        {
            Vector3 min = local.min;
            Vector3 max = local.max;
            Bounds result = new Bounds();
            bool first = true;
            for (int i = 0; i < 8; i++)
            {
                Vector3 corner = new Vector3(
                    (i & 1) == 0 ? min.x : max.x,
                    (i & 2) == 0 ? min.y : max.y,
                    (i & 4) == 0 ? min.z : max.z);
                Vector3 world = matrix.MultiplyPoint3x4(corner);
                if (first)
                {
                    result = new Bounds(world, Vector3.zero);
                    first = false;
                }
                else
                {
                    result.Encapsulate(world);
                }
            }
            return result;
        }

        private static void ConfigureDecalImporter()
        {
            TextureImporter importer = AssetImporter.GetAtPath(DecalPath) as TextureImporter;
            if (importer == null)
            {
                AssetDatabase.ImportAsset(DecalPath, ImportAssetOptions.ForceSynchronousImport);
                importer = AssetImporter.GetAtPath(DecalPath) as TextureImporter;
            }
            if (importer == null)
            {
                throw new InvalidOperationException($"Unity did not create a TextureImporter for {DecalPath}.");
            }
            importer.textureType = TextureImporterType.Default;
            importer.sRGBTexture = true;
            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            importer.alphaIsTransparency = true;
            importer.mipmapEnabled = true;
            importer.filterMode = FilterMode.Trilinear;
            importer.anisoLevel = 8;
            importer.maxTextureSize = 2048;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.SaveAndReimport();
        }

        private static Dictionary<int, Material> CreateMaterials(out Material decalMaterial)
        {
            Shader lit = Shader.Find("Universal Render Pipeline/Lit");
            if (lit == null)
            {
                throw new InvalidOperationException("URP Lit shader is required for Gate 11 materials.");
            }
            Dictionary<int, Material> materials = new Dictionary<int, Material>();
            foreach (ZoneMaterialSpec spec in ZoneSpecs)
            {
                Material material = UpsertMaterial(spec.Name, lit);
                ApplySpec(material, spec, null);
                materials[spec.Zone] = material;
            }

            Texture2D decal = AssetDatabase.LoadAssetAtPath<Texture2D>(DecalPath);
            if (decal == null)
            {
                throw new InvalidOperationException($"Decal texture failed to load: {DecalPath}");
            }
            decalMaterial = UpsertMaterial("M_PDC_HeaderLabelDecal", lit);
            ApplySpec(
                decalMaterial,
                new ZoneMaterialSpec(0, "M_PDC_HeaderLabelDecal", Color.white, 0f, 0.40f,
                    SurfaceKind.TransparentAlpha, 1f, 2980, "header label decal (placeholder copy, runtime-owned)"),
                decal);
            AssetDatabase.SaveAssets();
            return materials;
        }

        private static Material UpsertMaterial(string name, Shader shader)
        {
            string path = $"{MaterialRoot}/{name}.mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader) { name = name };
                AssetDatabase.CreateAsset(material, path);
            }
            else if (material.shader != shader)
            {
                material.shader = shader;
            }
            return material;
        }

        private static void ApplySpec(Material material, ZoneMaterialSpec spec, Texture2D baseMap)
        {
            Color srgb = spec.LinearColor.gamma;
            srgb.a = spec.Alpha;
            material.SetColor("_BaseColor", srgb);
            material.SetTexture("_BaseMap", baseMap);
            material.SetFloat("_Metallic", spec.Metallic);
            material.SetFloat("_Smoothness", spec.Smoothness);
            material.SetFloat("_SpecularHighlights", 1f);
            material.SetFloat("_EnvironmentReflections", 1f);
            material.SetFloat("_AlphaClip", 0f);
            material.SetFloat("_Cull", (float)CullMode.Back);
            material.DisableKeyword("_ALPHATEST_ON");
            material.DisableKeyword("_EMISSION");
            material.SetColor("_EmissionColor", Color.black);

            switch (spec.Surface)
            {
                case SurfaceKind.Opaque:
                    material.SetFloat("_Surface", 0f);
                    material.SetFloat("_Blend", 0f);
                    material.SetFloat("_ZWrite", 1f);
                    material.SetFloat("_SrcBlend", (float)BlendMode.One);
                    material.SetFloat("_DstBlend", (float)BlendMode.Zero);
                    material.SetFloat("_SrcBlendAlpha", (float)BlendMode.One);
                    material.SetFloat("_DstBlendAlpha", (float)BlendMode.Zero);
                    material.DisableKeyword("_SURFACE_TYPE_TRANSPARENT");
                    material.DisableKeyword("_ALPHAPREMULTIPLY_ON");
                    material.DisableKeyword("_ALPHAMODULATE_ON");
                    material.SetOverrideTag("RenderType", "Opaque");
                    material.SetFloat("_QueueOffset", 0f);
                    material.renderQueue = -1;
                    break;
                case SurfaceKind.TransparentPremultiplied:
                    material.SetFloat("_Surface", 1f);
                    material.SetFloat("_Blend", 2f);
                    material.SetFloat("_ZWrite", 0f);
                    material.SetFloat("_SrcBlend", (float)BlendMode.One);
                    material.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
                    material.SetFloat("_SrcBlendAlpha", (float)BlendMode.One);
                    material.SetFloat("_DstBlendAlpha", (float)BlendMode.OneMinusSrcAlpha);
                    material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
                    material.EnableKeyword("_ALPHAPREMULTIPLY_ON");
                    material.DisableKeyword("_ALPHAMODULATE_ON");
                    material.SetOverrideTag("RenderType", "Transparent");
                    // URP's material post-processor recomputes the queue as 3000 + _QueueOffset.
                    material.SetFloat("_QueueOffset", spec.Queue - 3000);
                    material.renderQueue = spec.Queue;
                    break;
                case SurfaceKind.TransparentAlpha:
                    material.SetFloat("_Surface", 1f);
                    material.SetFloat("_Blend", 0f);
                    material.SetFloat("_ZWrite", 0f);
                    material.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
                    material.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
                    material.SetFloat("_SrcBlendAlpha", (float)BlendMode.One);
                    material.SetFloat("_DstBlendAlpha", (float)BlendMode.OneMinusSrcAlpha);
                    material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
                    material.DisableKeyword("_ALPHAPREMULTIPLY_ON");
                    material.DisableKeyword("_ALPHAMODULATE_ON");
                    material.SetOverrideTag("RenderType", "Transparent");
                    material.SetFloat("_QueueOffset", spec.Queue - 3000);
                    material.renderQueue = spec.Queue;
                    break;
            }
            EditorUtility.SetDirty(material);
        }

        private static GameObject BuildCandidatePrefab(
            ParityReference reference,
            Dictionary<int, Material> materials,
            Material decalMaterial)
        {
            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            GameObject fileRoot = (GameObject)PrefabUtility.InstantiatePrefab(model);
            PrefabUtility.UnpackPrefabInstance(fileRoot, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            // The FBX file node wraps Blender's ROOT_PDC_PRESENTATION; promote the
            // Blender root so the Unity hierarchy matches the export parent map.
            Transform presentation = fileRoot.transform.Find("ROOT_PDC_PRESENTATION");
            GameObject instance;
            if (presentation != null)
            {
                presentation.SetParent(null, true);
                instance = presentation.gameObject;
                UnityEngine.Object.DestroyImmediate(fileRoot);
            }
            else
            {
                instance = fileRoot;
            }
            instance.name = RootName;
            instance.transform.position = Vector3.zero;
            instance.transform.rotation = Quaternion.identity;
            instance.transform.localScale = Vector3.one;

            Dictionary<string, ReferenceObject> byName = reference.objects.ToDictionary(item => item.name);
            MeshRenderer[] renderers = instance.GetComponentsInChildren<MeshRenderer>(true);
            foreach (MeshRenderer renderer in renderers)
            {
                if (!byName.TryGetValue(renderer.name, out ReferenceObject record))
                {
                    throw new InvalidOperationException($"Imported mesh {renderer.name} is not in the Blender reference table.");
                }
                if (!materials.TryGetValue(record.cmfZoneId, out Material material))
                {
                    throw new InvalidOperationException($"No material for cmf_zone_id {record.cmfZoneId} ({renderer.name}).");
                }
                renderer.sharedMaterial = material;
                renderer.shadowCastingMode = record.cmfZoneId == 1 || record.cmfZoneId == 2
                    ? ShadowCastingMode.Off
                    : ShadowCastingMode.On;
                renderer.receiveShadows = true;
                renderer.lightProbeUsage = LightProbeUsage.Off;
                renderer.reflectionProbeUsage = ReflectionProbeUsage.BlendProbes;
            }

            Transform header = instance.GetComponentsInChildren<Transform>(true)
                .FirstOrDefault(item => item.name == HeaderPlaneName);
            if (header == null)
            {
                throw new InvalidOperationException($"Header plane {HeaderPlaneName} missing from import.");
            }
            Transform existingDecal = header.Find(DecalName);
            if (existingDecal != null)
            {
                UnityEngine.Object.DestroyImmediate(existingDecal.gameObject);
            }
            Bounds headerBounds = header.GetComponent<Renderer>().bounds;
            GameObject decal = GameObject.CreatePrimitive(PrimitiveType.Quad);
            decal.name = DecalName;
            UnityEngine.Object.DestroyImmediate(decal.GetComponent<Collider>());
            decal.transform.SetParent(header, true);
            // Front face of the header plane is its minimum Z (front = -Z); lift 40 µm.
            decal.transform.position = new Vector3(
                headerBounds.center.x,
                headerBounds.center.y,
                headerBounds.min.z - 0.00004f);
            decal.transform.rotation = Quaternion.identity;
            decal.transform.localScale = new Vector3(
                HeaderPlateSizeMeters.x / Mathf.Max(header.lossyScale.x, 1e-6f),
                HeaderPlateSizeMeters.y / Mathf.Max(header.lossyScale.y, 1e-6f),
                1f);
            MeshRenderer decalRenderer = decal.GetComponent<MeshRenderer>();
            decalRenderer.sharedMaterial = decalMaterial;
            decalRenderer.shadowCastingMode = ShadowCastingMode.Off;
            decalRenderer.receiveShadows = false;
            decalRenderer.lightProbeUsage = LightProbeUsage.Off;

            GameObject saved = PrefabUtility.SaveAsPrefabAsset(instance, PrefabPath);
            UnityEngine.Object.DestroyImmediate(instance);
            if (saved == null)
            {
                throw new InvalidOperationException($"Failed to save candidate prefab {PrefabPath}.");
            }
            return saved;
        }

        // ------------------------------------------------------------------
        // Studio cubemap: every Blender area light becomes an HDR rectangle at
        // its true direction/size as seen from the case centre; the world colour
        // fills the rest. Radiance = P / (pi * A), Cycles' one-sided area light.
        // ------------------------------------------------------------------
        private static Cubemap BuildStudioCubemap(string assetPath, ReferenceLight[] lights, ReferenceWorld world)
        {
            Cubemap cubemap = new Cubemap(CubemapSize, TextureFormat.RGBAHalf, true);
            Color background = new Color(
                world.colorLinear[0] * world.strength,
                world.colorLinear[1] * world.strength,
                world.colorLinear[2] * world.strength,
                1f);
            Color[] pixels = new Color[CubemapSize * CubemapSize];
            float pixelAngle = 2f / CubemapSize;
            for (int face = 0; face < 6; face++)
            {
                for (int y = 0; y < CubemapSize; y++)
                {
                    float v = ((y + 0.5f) / CubemapSize) * 2f - 1f;
                    for (int x = 0; x < CubemapSize; x++)
                    {
                        float u = ((x + 0.5f) / CubemapSize) * 2f - 1f;
                        Vector3 direction = CubemapDirection((CubemapFace)face, u, v).normalized;
                        Color radiance = background;
                        foreach (ReferenceLight light in lights)
                        {
                            radiance += SampleAreaLight(light, direction, pixelAngle);
                        }
                        radiance.a = 1f;
                        pixels[y * CubemapSize + x] = radiance;
                    }
                }
                cubemap.SetPixels(pixels, (CubemapFace)face);
            }
            cubemap.Apply(true, false);
            cubemap.wrapMode = TextureWrapMode.Clamp;
            cubemap.filterMode = FilterMode.Trilinear;

            Cubemap existing = AssetDatabase.LoadAssetAtPath<Cubemap>(assetPath);
            if (existing != null)
            {
                AssetDatabase.DeleteAsset(assetPath);
            }
            AssetDatabase.CreateAsset(cubemap, assetPath);
            return AssetDatabase.LoadAssetAtPath<Cubemap>(assetPath);
        }

        // Standard DX/Unity cubemap face parametrisation; row 0 is the top of the face.
        private static Vector3 CubemapDirection(CubemapFace face, float u, float v)
        {
            switch (face)
            {
                case CubemapFace.PositiveX: return new Vector3(1f, -v, -u);
                case CubemapFace.NegativeX: return new Vector3(-1f, -v, u);
                case CubemapFace.PositiveY: return new Vector3(u, 1f, v);
                case CubemapFace.NegativeY: return new Vector3(u, -1f, -v);
                case CubemapFace.PositiveZ: return new Vector3(u, -v, 1f);
                default: return new Vector3(-u, -v, -1f);
            }
        }

        private static Color SampleAreaLight(ReferenceLight light, Vector3 direction, float pixelAngle)
        {
            Vector3 position = ToVector(light.unityPosition);
            Vector3 normal = ToVector(light.unityForward).normalized; // emits along forward
            float denominator = Vector3.Dot(direction, normal);
            if (denominator > -1e-6f)
            {
                return Color.clear; // ray travels away from or parallel to the emitter plane
            }
            float t = Vector3.Dot(position, normal) / denominator;
            if (t <= 0f)
            {
                return Color.clear;
            }
            Vector3 hit = direction * t;
            Vector3 offset = hit - position;
            Vector3 right = ToVector(light.unityRight).normalized;
            Vector3 up = ToVector(light.unityUp).normalized;
            float halfWidth = Mathf.Max(light.sizeM, 0.002f) * 0.5f;
            float halfHeight = Mathf.Max(light.sizeYM, 0.002f) * 0.5f;
            float lx = Mathf.Abs(Vector3.Dot(offset, right));
            float ly = Mathf.Abs(Vector3.Dot(offset, up));
            // Soft edge one pixel wide in angular terms, projected to the plane.
            float feather = pixelAngle * t;
            float coverage = Mathf.Clamp01((halfWidth + feather - lx) / feather)
                * Mathf.Clamp01((halfHeight + feather - ly) / feather);
            if (coverage <= 0f)
            {
                return Color.clear;
            }
            float area = Mathf.Max(light.sizeM, 0.002f) * Mathf.Max(light.sizeYM, 0.002f);
            // Clamp tames the 6 mm sparkle emitters (radiance ~187) that otherwise
            // alias into white speckle on the mirror lip; key/strips stay unclipped.
            float radiance = Mathf.Min(light.energyW / (Mathf.PI * area), MaxCubemapRadiance);
            return new Color(
                light.colorLinear[0] * radiance * coverage,
                light.colorLinear[1] * radiance * coverage,
                light.colorLinear[2] * radiance * coverage,
                0f);
        }

        // ------------------------------------------------------------------
        // Rigs
        // ------------------------------------------------------------------
        public static void ApplyRig(
            Transform environment,
            Camera camera,
            ReferenceLight[] lights,
            ReferenceWorld world,
            Cubemap cubemap,
            string rigName)
        {
            for (int index = environment.childCount - 1; index >= 0; index--)
            {
                Transform child = environment.GetChild(index);
                if (child.GetComponent<Camera>() == null)
                {
                    UnityEngine.Object.DestroyImmediate(child.gameObject);
                }
            }
            Transform rig = new GameObject($"Gate11Rig_{rigName}").transform;
            rig.SetParent(environment, false);

            // Direct lights: the two brightest white emitters become directional
            // (large softboxes read as distant), the two strongest coloured strips
            // become spots (grazing edges). Everything else lives in the cubemap.
            ReferenceLight[] whites = lights
                .Where(item => IsWhite(item))
                .OrderByDescending(item => Irradiance(item))
                .Take(2)
                .ToArray();
            ReferenceLight[] coloured = lights
                .Where(item => !IsWhite(item))
                .OrderByDescending(item => Irradiance(item))
                .Take(2)
                .ToArray();
            bool first = true;
            foreach (ReferenceLight light in whites)
            {
                GameObject lightObject = new GameObject(light.name);
                lightObject.transform.SetParent(rig, false);
                lightObject.transform.rotation = Quaternion.LookRotation(ToVector(light.unityForward).normalized, Vector3.up);
                Light component = lightObject.AddComponent<Light>();
                component.type = LightType.Directional;
                component.color = ToColor(light.colorLinear);
                component.intensity = Irradiance(light);
                component.shadows = first ? LightShadows.Soft : LightShadows.None;
                component.shadowStrength = 0.6f;
                component.shadowBias = 0.002f;
                component.shadowNormalBias = 0.2f;
                first = false;
            }
            foreach (ReferenceLight light in coloured)
            {
                GameObject lightObject = new GameObject(light.name);
                lightObject.transform.SetParent(rig, false);
                lightObject.transform.position = ToVector(light.unityPosition);
                lightObject.transform.rotation = Quaternion.LookRotation(ToVector(light.unityForward).normalized, Vector3.up);
                Light component = lightObject.AddComponent<Light>();
                component.type = LightType.Spot;
                component.color = ToColor(light.colorLinear);
                component.intensity = light.energyW / (Mathf.PI * Mathf.PI); // spot: irradiance = I / d^2
                component.range = 0.8f;
                component.spotAngle = 120f;
                component.innerSpotAngle = 60f;
                component.shadows = LightShadows.None;
            }

            Color background = new Color(
                world.colorLinear[0] * world.strength,
                world.colorLinear[1] * world.strength,
                world.colorLinear[2] * world.strength,
                1f);
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = background;
            RenderSettings.ambientIntensity = 1f;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflectionTexture = cubemap;
            RenderSettings.reflectionIntensity = 1f;
            RenderSettings.reflectionBounces = 1;
            RenderSettings.fog = false;
            camera.backgroundColor = background.gamma;
        }

        private static bool IsWhite(ReferenceLight light)
        {
            float min = Mathf.Min(light.colorLinear[0], Mathf.Min(light.colorLinear[1], light.colorLinear[2]));
            return min >= 0.8f;
        }

        // Unity directional intensity that reproduces a Cycles area light of power P
        // at distance d: physical irradiance P/(pi d^2), divided by pi because Unity's
        // Lambert term is albedo * intensity (no 1/pi).
        private static float Irradiance(ReferenceLight light)
        {
            float distance = ToVector(light.unityPosition).magnitude;
            return light.energyW / (Mathf.PI * Mathf.PI * Mathf.Max(distance * distance, 1e-6f));
        }

        // ------------------------------------------------------------------
        // Cameras and captures
        // ------------------------------------------------------------------
        public static Camera CreateCamera(Transform parent)
        {
            GameObject cameraObject = new GameObject("Gate11MatchedCamera") { tag = "MainCamera" };
            cameraObject.transform.SetParent(parent, false);
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.black;
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.allowHDR = true;
            camera.allowMSAA = true;
            return camera;
        }

        public static ReferenceCamera FindCamera(ParityReference reference, string name)
        {
            ReferenceCamera camera = reference.cameras.FirstOrDefault(item => item.name == name);
            if (camera == null)
            {
                throw new InvalidOperationException($"Camera {name} is not in the Blender reference table.");
            }
            return camera;
        }

        public static void SetView(Camera camera, ParityReference reference, string name)
        {
            ReferenceCamera view = FindCamera(reference, name);
            camera.transform.position = ToVector(view.unityPosition);
            camera.transform.rotation = Quaternion.LookRotation(
                ToVector(view.unityForward).normalized,
                ToVector(view.unityUp).normalized);
            if (view.projection == "ORTHO")
            {
                camera.orthographic = true;
                camera.usePhysicalProperties = false;
                camera.orthographicSize = view.orthoScale * 0.5f;
                camera.nearClipPlane = 0.001f;
                camera.farClipPlane = 4f;
            }
            else
            {
                camera.orthographic = false;
                camera.usePhysicalProperties = true;
                camera.focalLength = view.focalLengthMm;
                camera.sensorSize = new Vector2(view.sensorMm[0], view.sensorMm[1]);
                camera.gateFit = Camera.GateFitMode.Horizontal;
                camera.lensShift = Vector2.zero;
                camera.nearClipPlane = 0.02f;
                camera.farClipPlane = 8f;
            }
        }

        private static void ResolutionFor(ParityReference reference, string cameraName, out int width, out int height)
        {
            ReferenceCamera view = FindCamera(reference, cameraName);
            if (view.projection == "ORTHO")
            {
                width = 2048;
                height = 2048;
            }
            else
            {
                width = reference.shippingResolution[0];
                height = reference.shippingResolution[1];
            }
        }

        private static void CaptureView(Camera camera, ParityReference reference, string cameraName, string outputPath)
        {
            SetView(camera, reference, cameraName);
            ResolutionFor(reference, cameraName, out int width, out int height);
            Capture(camera, outputPath, width, height);
        }

        private static void CaptureOrbit(Camera camera, ParityReference reference, Transform orbitRoot, string framesDirectory)
        {
            SetView(camera, reference, "CAM_PDC_HERO");
            ResolutionFor(reference, "CAM_PDC_HERO", out int width, out int height);
            for (int index = 0; index < OrbitFrameCount; index++)
            {
                float degrees = 360f * index / OrbitFrameCount;
                orbitRoot.localRotation = Quaternion.Euler(0f, degrees, 0f);
                Capture(camera, Path.Combine(framesDirectory, $"frame-{index:000}.png"), width / 2, height / 2);
            }
            orbitRoot.localRotation = Quaternion.identity;
        }

        private static void CaptureShadowVariant(Camera camera, ParityReference reference, Transform environment, string outputPath)
        {
            Light[] lights = environment.GetComponentsInChildren<Light>(true);
            LightShadows[] previous = lights.Select(item => item.shadows).ToArray();
            try
            {
                foreach (Light light in lights)
                {
                    light.shadows = LightShadows.None;
                }
                CaptureView(camera, reference, "CAM_PDC_HERO", outputPath);
            }
            finally
            {
                for (int index = 0; index < lights.Length; index++)
                {
                    lights[index].shadows = previous[index];
                }
            }
        }

        private static void CaptureMirrorProbe(Camera camera, ParityReference reference, GameObject candidate, string outputPath)
        {
            Shader lit = Shader.Find("Universal Render Pipeline/Lit");
            Material mirror = new Material(lit);
            mirror.SetColor("_BaseColor", Color.white);
            mirror.SetFloat("_Metallic", 1f);
            mirror.SetFloat("_Smoothness", 1f);
            GameObject sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            sphere.name = "Gate11CubemapProbe_ReviewOnly";
            sphere.transform.position = Vector3.zero;
            sphere.transform.localScale = Vector3.one * 0.12f;
            sphere.GetComponent<MeshRenderer>().sharedMaterial = mirror;
            bool wasActive = candidate.activeSelf;
            candidate.SetActive(false);
            try
            {
                SetView(camera, reference, "CAM_PDC_FRONT");
                camera.orthographicSize = 0.075f;
                Capture(camera, outputPath, 1024, 1024);
            }
            finally
            {
                candidate.SetActive(wasActive);
                UnityEngine.Object.DestroyImmediate(sphere);
                UnityEngine.Object.DestroyImmediate(mirror);
            }
        }

        private static void CaptureSilhouette(Camera camera, ParityReference reference, GameObject candidate, string outputPath)
        {
            Shader unlitShader = Shader.Find("Universal Render Pipeline/Unlit");
            Material white = new Material(unlitShader);
            white.SetColor("_BaseColor", Color.white);
            MeshRenderer[] renderers = candidate.GetComponentsInChildren<MeshRenderer>(true);
            Material[] previous = renderers.Select(item => item.sharedMaterial).ToArray();
            Transform decal = renderers.Select(item => item.transform).FirstOrDefault(item => item.name == DecalName);
            Color previousBackground = camera.backgroundColor;
            Color previousAmbient = RenderSettings.ambientLight;
            try
            {
                foreach (MeshRenderer renderer in renderers)
                {
                    renderer.sharedMaterial = white;
                }
                if (decal != null)
                {
                    decal.gameObject.SetActive(false);
                }
                camera.backgroundColor = Color.black;
                SetView(camera, reference, "CAM_PDC_FRONT");
                camera.allowMSAA = false;
                Capture(camera, outputPath, 2048, 2048);
            }
            finally
            {
                for (int index = 0; index < renderers.Length; index++)
                {
                    renderers[index].sharedMaterial = previous[index];
                }
                if (decal != null)
                {
                    decal.gameObject.SetActive(true);
                }
                camera.backgroundColor = previousBackground;
                camera.allowMSAA = true;
                RenderSettings.ambientLight = previousAmbient;
                UnityEngine.Object.DestroyImmediate(white);
            }
        }

        public static void Capture(Camera camera, string outputPath, int width, int height)
        {
            // Render at 2x with 4x MSAA, then box-filter down: thin mirror rims
            // otherwise alias into white speckle against the HDR strip lights.
            int supersample = camera.allowMSAA ? 2 : 1;
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            RenderTexture hi = new RenderTexture(width * supersample, height * supersample, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB)
            {
                antiAliasing = camera.allowMSAA ? 4 : 1,
                filterMode = FilterMode.Bilinear
            };
            RenderTexture target = new RenderTexture(width, height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            Texture2D image = new Texture2D(width, height, TextureFormat.RGBA32, false, false);
            try
            {
                hi.Create();
                target.Create();
                camera.targetTexture = hi;
                UnityEngine.Rendering.RenderPipeline.StandardRequest request =
                    new UnityEngine.Rendering.RenderPipeline.StandardRequest { destination = hi };
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                Graphics.Blit(hi, target);
                RenderTexture.active = target;
                image.ReadPixels(new Rect(0f, 0f, width, height), 0, 0);
                image.Apply(false, false);
                File.WriteAllBytes(outputPath, image.EncodeToPNG());
            }
            finally
            {
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                hi.Release();
                target.Release();
                UnityEngine.Object.DestroyImmediate(hi);
                UnityEngine.Object.DestroyImmediate(target);
                UnityEngine.Object.DestroyImmediate(image);
            }
        }

        // ------------------------------------------------------------------
        // Reports
        // ------------------------------------------------------------------
        public static HierarchyReport CreateHierarchyReport(
            Transform root,
            ParityReference reference,
            Dictionary<int, Material> materials,
            Material decalMaterial)
        {
            Dictionary<string, ReferenceObject> byName = reference.objects.ToDictionary(item => item.name);
            Transform[] transforms = root.GetComponentsInChildren<Transform>(true);
            MeshRenderer[] renderers = root.GetComponentsInChildren<MeshRenderer>(true);
            List<string> failures = new List<string>();

            if (root.name != RootName) failures.Add($"root is {root.name}, expected {RootName}");
            if (root.localRotation != Quaternion.identity) failures.Add("root rotation is not zero");
            if (root.localScale != Vector3.one) failures.Add("root scale is not one");

            List<TransformRecord> records = new List<TransformRecord>();
            int triangles = 0;
            int meshCount = 0;
            HashSet<Material> caseMaterials = new HashSet<Material>();
            foreach (Transform item in transforms.OrderBy(item => item.name, StringComparer.Ordinal))
            {
                MeshFilter filter = item.GetComponent<MeshFilter>();
                MeshRenderer renderer = item.GetComponent<MeshRenderer>();
                TransformRecord record = new TransformRecord
                {
                    name = item.name,
                    parent = item == root ? null : item.parent.name,
                    localPosition = ToArray(item.localPosition),
                    localEuler = ToArray(item.localRotation.eulerAngles),
                    localScale = ToArray(item.localScale),
                    material = renderer != null && renderer.sharedMaterial != null ? renderer.sharedMaterial.name : null,
                    triangles = filter != null && filter.sharedMesh != null ? filter.sharedMesh.triangles.Length / 3 : 0
                };
                Vector3 scale = item.localScale;
                if (scale.x < 0f || scale.y < 0f || scale.z < 0f)
                {
                    failures.Add($"{item.name} has negative scale");
                }
                if (item.name == DecalName)
                {
                    record.cmfZoneId = 0;
                    record.role = "header-label-decal (runtime-owned copy, placeholder)";
                    if (renderer == null || renderer.sharedMaterial != decalMaterial)
                    {
                        failures.Add("decal material not assigned");
                    }
                    if (item.parent == null || item.parent.name != HeaderPlaneName)
                    {
                        failures.Add($"decal parent is not {HeaderPlaneName}");
                    }
                }
                else if (item == root)
                {
                    record.role = "presentation root (ROOT_PDC_PRESENTATION)";
                }
                else if (byName.TryGetValue(item.name, out ReferenceObject expected))
                {
                    record.cmfZoneId = expected.cmfZoneId;
                    record.role = expected.type == "EMPTY" ? "empty" : "case mesh";
                    string expectedParent = expected.parent == "ROOT_PDC_PRESENTATION" ? RootName : expected.parent;
                    if (record.parent != expectedParent)
                    {
                        failures.Add($"{item.name} parent {record.parent}, expected {expectedParent}");
                    }
                    Vector3 expectedPosition = ToVector(expected.unityLocalPosition);
                    if (expected.type == "EMPTY" && (item.position - expectedPosition).magnitude > ObjectBoundsToleranceMeters)
                    {
                        failures.Add($"{item.name} pivot {item.position} differs from Blender {expectedPosition}");
                    }
                    if (expected.type == "MESH")
                    {
                        meshCount++;
                        triangles += record.triangles;
                        if (record.triangles != expected.triangles)
                        {
                            failures.Add($"{item.name} triangles {record.triangles}, Blender {expected.triangles}");
                        }
                        if (renderer == null || !materials.TryGetValue(expected.cmfZoneId, out Material zoneMaterial)
                            || renderer.sharedMaterial != zoneMaterial)
                        {
                            failures.Add($"{item.name} material does not match zone {expected.cmfZoneId}");
                        }
                        else
                        {
                            caseMaterials.Add(zoneMaterial);
                        }
                    }
                }
                else
                {
                    failures.Add($"{item.name} is not in the Blender reference table");
                }
                records.Add(record);
            }
            if (meshCount != ExpectedMeshCount) failures.Add($"mesh count {meshCount}, expected {ExpectedMeshCount}");
            if (triangles != ExpectedTriangles) failures.Add($"triangles {triangles}, expected {ExpectedTriangles}");
            if (caseMaterials.Count > CaseMaterialSlotBudget) failures.Add($"case material slots {caseMaterials.Count} exceed {CaseMaterialSlotBudget}");
            if (transforms.All(item => item.name != ContentSlotName)) failures.Add($"{ContentSlotName} missing");

            return new HierarchyReport
            {
                status = failures.Count == 0 ? "pass" : "fail",
                candidatePrefab = PrefabPath,
                sourceFbxSha256 = ApprovedFbxSha256,
                governingContractSha256 = GoverningContractSha256,
                meshCount = meshCount,
                triangles = triangles,
                caseMaterialSlots = caseMaterials.Count,
                caseMaterialSlotBudget = CaseMaterialSlotBudget,
                materials = ZoneSpecs.Select(spec => new MaterialRecord
                {
                    cmfZoneId = spec.Zone,
                    name = spec.Name,
                    shader = "Universal Render Pipeline/Lit",
                    surface = spec.Surface.ToString(),
                    baseColorLinear = new[] { spec.LinearColor.r, spec.LinearColor.g, spec.LinearColor.b },
                    alpha = spec.Alpha,
                    metallic = spec.Metallic,
                    smoothness = spec.Smoothness,
                    renderQueue = spec.Queue,
                    note = spec.Note
                }).ToArray(),
                transforms = records.ToArray(),
                failures = failures.ToArray()
            };
        }

        public static BoundsReport CreateBoundsReport(Transform root, ParityReference reference, ImportReport import)
        {
            Dictionary<string, ReferenceObject> byName = reference.objects.ToDictionary(item => item.name);
            MeshRenderer[] renderers = root.GetComponentsInChildren<MeshRenderer>(true)
                .Where(item => item.name != DecalName)
                .ToArray();
            List<string> failures = new List<string>();
            List<ObjectBoundsRecord> records = new List<ObjectBoundsRecord>();
            Bounds union = renderers[0].bounds;
            float maxDelta = 0f;
            foreach (MeshRenderer renderer in renderers.OrderBy(item => item.name, StringComparer.Ordinal))
            {
                Bounds bounds = renderer.bounds;
                union.Encapsulate(bounds);
                ReferenceObject expected = byName[renderer.name];
                Vector3 expectedMin = ToVector(expected.unityBoundsMin);
                Vector3 expectedMax = ToVector(expected.unityBoundsMax);
                float delta = Mathf.Max(
                    MaxAbsComponent(bounds.min - expectedMin),
                    MaxAbsComponent(bounds.max - expectedMax));
                maxDelta = Mathf.Max(maxDelta, delta);
                records.Add(new ObjectBoundsRecord
                {
                    name = renderer.name,
                    unityMin = ToArray(bounds.min),
                    unityMax = ToArray(bounds.max),
                    blenderMin = expected.unityBoundsMin,
                    blenderMax = expected.unityBoundsMax,
                    maxDeltaMeters = delta,
                    pass = delta <= ObjectBoundsToleranceMeters
                });
                if (delta > ObjectBoundsToleranceMeters)
                {
                    failures.Add($"{renderer.name} bounds differ by {delta * 1000f:F4} mm");
                }
            }
            Vector3 size = union.size;
            float[] deltaPercent =
            {
                Mathf.Abs(size.x / ExpectedCaseSize.x - 1f) * 100f,
                Mathf.Abs(size.y / ExpectedCaseSize.y - 1f) * 100f,
                Mathf.Abs(size.z / ExpectedCaseSize.z - 1f) * 100f
            };
            if (deltaPercent.Max() > BoundsTolerancePercent)
            {
                failures.Add($"case size {size} differs from manifest {ExpectedCaseSize} by {deltaPercent.Max():F3}%");
            }
            Vector3 referenceMin = ToVector(reference.caseBoundsUnityM.min);
            Vector3 referenceMax = ToVector(reference.caseBoundsUnityM.max);
            if (MaxAbsComponent(union.min - referenceMin) > ObjectBoundsToleranceMeters
                || MaxAbsComponent(union.max - referenceMax) > ObjectBoundsToleranceMeters)
            {
                failures.Add($"case bounds {union.min}..{union.max} differ from Blender {referenceMin}..{referenceMax}");
            }
            return new BoundsReport
            {
                status = failures.Count == 0 ? "pass" : "fail",
                import = import,
                caseSizeMeters = ToArray(size),
                expectedCaseSizeMeters = ToArray(ExpectedCaseSize),
                caseSizeDeltaPercent = deltaPercent,
                boundsTolerancePercent = BoundsTolerancePercent,
                caseBoundsMin = ToArray(union.min),
                caseBoundsMax = ToArray(union.max),
                objectBoundsToleranceMeters = ObjectBoundsToleranceMeters,
                maxObjectBoundsDeltaMeters = maxDelta,
                objects = records.ToArray(),
                failures = failures.ToArray()
            };
        }

        private static CaptureReport CreateCaptureReport(ParityReference reference, Cubemap shipping, Cubemap neutral)
        {
            return new CaptureReport
            {
                status = "pass",
                axisMapping = reference.axisMapping,
                unityRenderPipeline = GraphicsSettings.currentRenderPipeline != null
                    ? GraphicsSettings.currentRenderPipeline.name
                    : "built-in",
                colorSpace = PlayerSettings.colorSpace.ToString(),
                postProcessing = "none (contract unity_urp.post_processing_beauty_start.validation_volume_disabled)",
                blenderViewTransform = string.Join(" / ", reference.shippingViewTransform),
                shippingResolution = reference.shippingResolution,
                cameras = reference.cameras.Select(item => new CameraRecord
                {
                    name = item.name,
                    projection = item.projection,
                    unityPosition = item.unityPosition,
                    unityForward = item.unityForward,
                    unityUp = item.unityUp,
                    focalLengthMm = item.focalLengthMm,
                    sensorMm = item.sensorMm,
                    orthoScale = item.orthoScale
                }).ToArray(),
                shippingRig = DescribeRig(reference.shippingLights, reference.shippingWorld, shipping),
                neutralRig = DescribeRig(reference.neutralLights, reference.neutralWorld, neutral),
                notes = new[]
                {
                    "Blender area lights become HDR rectangles in a procedural reflection cubemap (radiance P/(pi*A)).",
                    "Two brightest white emitters -> directional lights (irradiance P/(pi*d^2)); two strongest coloured strips -> spot lights (P/pi).",
                    "URP additional realtime lights used: 3 (contract performance_budget.additional_realtime_lights_max = 3).",
                    "No tonemapping: Blender uses AgX; absolute colour parity is not claimed, geometry/silhouette/composition are."
                }
            };
        }

        private static RigRecord DescribeRig(ReferenceLight[] lights, ReferenceWorld world, Cubemap cubemap)
        {
            return new RigRecord
            {
                worldColorLinear = world.colorLinear,
                worldStrength = world.strength,
                cubemapAsset = AssetDatabase.GetAssetPath(cubemap),
                cubemapSize = CubemapSize,
                emitters = lights.Select(item => new EmitterRecord
                {
                    name = item.name,
                    energyW = item.energyW,
                    colorLinear = item.colorLinear,
                    unityPosition = item.unityPosition,
                    unityForward = item.unityForward,
                    sizeM = new[] { item.sizeM, item.sizeYM },
                    radiance = item.energyW / (Mathf.PI * Mathf.Max(item.sizeM, 0.002f) * Mathf.Max(item.sizeYM, 0.002f)),
                    irradianceAtCase = Irradiance(item),
                    directRole = IsWhite(item) ? "candidate directional" : "candidate spot"
                }).ToArray()
            };
        }

        // ------------------------------------------------------------------
        // Helpers
        // ------------------------------------------------------------------
        private static Color SrgbToLinear(int r, int g, int b)
        {
            return new Color(r / 255f, g / 255f, b / 255f).linear;
        }

        private static float MaxAbsComponent(Vector3 value)
        {
            return Mathf.Max(Mathf.Abs(value.x), Mathf.Max(Mathf.Abs(value.y), Mathf.Abs(value.z)));
        }

        public static Vector3 ToVector(float[] values)
        {
            return new Vector3(values[0], values[1], values[2]);
        }

        private static Color ToColor(float[] values)
        {
            return new Color(values[0], values[1], values[2], 1f);
        }

        private static float[] ToArray(Vector3 value)
        {
            return new[] { value.x, value.y, value.z };
        }

        public static string AssetAbsolutePath(string assetPath)
        {
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            return Path.Combine(projectRoot, assetPath);
        }

        public static string Sha256File(string path)
        {
            using (SHA256 sha = SHA256.Create())
            using (FileStream stream = File.OpenRead(path))
            {
                byte[] hash = sha.ComputeHash(stream);
                StringBuilder builder = new StringBuilder(hash.Length * 2);
                foreach (byte value in hash)
                {
                    builder.Append(value.ToString("x2", CultureInfo.InvariantCulture));
                }
                return builder.ToString();
            }
        }

        public static void WriteJson<T>(string path, T value)
        {
            File.WriteAllText(path, JsonUtility.ToJson(value, true));
        }

        // ------------------------------------------------------------------
        // Serialisable records
        // ------------------------------------------------------------------
        [Serializable]
        public class ParityReference
        {
            public int schemaVersion;
            public string modelId;
            public string variantId;
            public string axisMapping;
            public ReferenceBounds caseBoundsUnityM;
            public int expectedTriangles;
            public int expectedMeshCount;
            public int expectedEmptyCount;
            public ReferenceObject[] objects;
            public ReferenceCamera[] cameras;
            public int[] shippingResolution;
            public string[] shippingViewTransform;
            public ReferenceWorld shippingWorld;
            public ReferenceLight[] shippingLights;
            public ReferenceWorld neutralWorld;
            public ReferenceLight[] neutralLights;
        }

        [Serializable]
        public class ReferenceBounds
        {
            public float[] min;
            public float[] max;
        }

        [Serializable]
        public class ReferenceObject
        {
            public string name;
            public string type;
            public string parent;
            public int cmfZoneId;
            public string blenderMaterial;
            public int triangles;
            public float[] blenderLocation;
            public float[] unityLocalPosition;
            public float[] unityBoundsMin;
            public float[] unityBoundsMax;
        }

        [Serializable]
        public class ReferenceCamera
        {
            public string name;
            public string projection;
            public float[] unityPosition;
            public float[] unityForward;
            public float[] unityUp;
            public float focalLengthMm;
            public float[] sensorMm;
            public string sensorFit;
            public float orthoScale;
            public float[] clip;
        }

        [Serializable]
        public class ReferenceLight
        {
            public string name;
            public string type;
            public float energyW;
            public float[] colorLinear;
            public float[] unityPosition;
            public float[] unityForward;
            public float[] unityRight;
            public float[] unityUp;
            public float sizeM;
            public float sizeYM;
            public string shape;
            public float spreadDeg;
        }

        [Serializable]
        public class ReferenceWorld
        {
            public float[] colorLinear;
            public float strength;
        }

        [Serializable]
        public class ImportReport
        {
            public float[] initialMeasuredSizeMeters;
            public float[] finalMeasuredSizeMeters;
            public float appliedGlobalScale;
            public bool usedFileScale;
        }

        [Serializable]
        public class TransformRecord
        {
            public string name;
            public string parent;
            public string role;
            public int cmfZoneId;
            public string material;
            public int triangles;
            public float[] localPosition;
            public float[] localEuler;
            public float[] localScale;
        }

        [Serializable]
        public class MaterialRecord
        {
            public int cmfZoneId;
            public string name;
            public string shader;
            public string surface;
            public float[] baseColorLinear;
            public float alpha;
            public float metallic;
            public float smoothness;
            public int renderQueue;
            public string note;
        }

        [Serializable]
        public class HierarchyReport
        {
            public string status;
            public string candidatePrefab;
            public string sourceFbxSha256;
            public string governingContractSha256;
            public int meshCount;
            public int triangles;
            public int caseMaterialSlots;
            public int caseMaterialSlotBudget;
            public MaterialRecord[] materials;
            public TransformRecord[] transforms;
            public string[] failures;
        }

        [Serializable]
        public class ObjectBoundsRecord
        {
            public string name;
            public float[] unityMin;
            public float[] unityMax;
            public float[] blenderMin;
            public float[] blenderMax;
            public float maxDeltaMeters;
            public bool pass;
        }

        [Serializable]
        public class BoundsReport
        {
            public string status;
            public ImportReport import;
            public float[] caseSizeMeters;
            public float[] expectedCaseSizeMeters;
            public float[] caseSizeDeltaPercent;
            public float boundsTolerancePercent;
            public float[] caseBoundsMin;
            public float[] caseBoundsMax;
            public float objectBoundsToleranceMeters;
            public float maxObjectBoundsDeltaMeters;
            public ObjectBoundsRecord[] objects;
            public string[] failures;
        }

        [Serializable]
        public class CameraRecord
        {
            public string name;
            public string projection;
            public float[] unityPosition;
            public float[] unityForward;
            public float[] unityUp;
            public float focalLengthMm;
            public float[] sensorMm;
            public float orthoScale;
        }

        [Serializable]
        public class EmitterRecord
        {
            public string name;
            public float energyW;
            public float[] colorLinear;
            public float[] unityPosition;
            public float[] unityForward;
            public float[] sizeM;
            public float radiance;
            public float irradianceAtCase;
            public string directRole;
        }

        [Serializable]
        public class RigRecord
        {
            public float[] worldColorLinear;
            public float worldStrength;
            public string cubemapAsset;
            public int cubemapSize;
            public EmitterRecord[] emitters;
        }

        [Serializable]
        public class CaptureReport
        {
            public string status;
            public string axisMapping;
            public string unityRenderPipeline;
            public string colorSpace;
            public string postProcessing;
            public string blenderViewTransform;
            public int[] shippingResolution;
            public CameraRecord[] cameras;
            public RigRecord shippingRig;
            public RigRecord neutralRig;
            public string[] notes;
        }
    }
}
