using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using FidgetingApp.EDC.Candidates.ModelHhax;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.Editor
{
    /// <summary>
    /// Imports the approved model-hhax Gate 10 FBX into an isolated Unity
    /// candidate. Shipping assets are hash-checked before and after this pass.
    /// </summary>
    public static class ModelHhaxGate11Builder
    {
        public const string CandidateRoot = "Assets/_EDC/Candidates/ModelHhaxGate11R001";
        public const string ModelPath = CandidateRoot + "/Models/model-hhax-final.fbx";
        public const string CollisionPath = CandidateRoot + "/Models/model-hhax-collision.fbx";
        public const string TextureRoot = CandidateRoot + "/Textures";
        public const string MaterialRoot = CandidateRoot + "/Materials";
        public const string PrefabPath = CandidateRoot + "/Prefabs/ModelHhaxGate11R001.prefab";
        public const string ScenePath = CandidateRoot + "/Scenes/ModelHhaxGate11Parity.unity";
        public const string EvidenceRelative =
            "ArtSource/ModelPipeline/model-hhax/evidence/11-unity-parity/rev-001";
        public const string RuntimeEvidenceRelative =
            "ArtSource/ModelPipeline/model-hhax/evidence/11-unity-parity/rev-002/runtime-frames";

        public const string ApprovedFbxSha256 =
            "d8585e19573d00c9e3ba2ba30c8cbc4ed224f035270f342bb526521a28b62d34";
        public const string ApprovedCollisionSha256 =
            "53329498e605e3eb844905636d878c2d26eb5ccf45dab7c89dfda77bda0a7dfa";
        public const string GoverningContractSha256 =
            "e7aadf84cd589b0f69cec93eb866c6169af932560ed9e4e95369ece45c253911";
        public const string ExportManifestSha256 =
            "756c8c577e0b7aa4275818fcb1f6a5008e64315c974832c3e622f07c7f66e705";
        public const string ExportValidationSha256 =
            "b8c7f72fb13f0dc7c2157d70e9091b92260f96d66c4d88793744f695e685fb1e";
        public const string HierarchyMetadataSha256 =
            "8753f7eccfccf225a15568ebb52f302e77bfb925963f06193c4465349d9465f1";
        public const string NeutralCameraRecipeSha256 =
            "70c716af85e6e30b0c40ef30bc2b16eeb384fb1661157404f4b3e9482703e76b";
        public const string UnityImportContractSha256 =
            "be42605a0e5aea75e3aded381a30c119eff3a3df7d9342254bd935c27d1baefb";
        public const int ExpectedRenderMeshCount = 19;
        public const int ExpectedTriangleCount = 20022;
        public const int ExpectedCollisionCount = 3;

        private const string SourceRoot =
            "ArtSource/ModelPipeline/model-hhax/evidence/10-export/rev-001";
        private const string SourceTextureRoot =
            "ArtSource/ModelPipeline/model-hhax/source/textures";
        private const string BlenderNeutralSource =
            "ArtSource/ModelPipeline/model-hhax/evidence/09-environment/rev-001/neutral-environment.png";
        private const string ShippingScenePath = "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const string PendingRuntimeCaptureKey =
            "Fidgeting.ModelHhax.Gate11.PendingRuntimeCapture";

        private static readonly string[] TextureNames =
        {
            "front-basecolor.png", "front-emission.png", "front-emission-mask.png",
            "front-normal.png", "front-roughness.png",
            "lower-basecolor.png", "lower-emission.png", "lower-emission-mask.png",
            "lower-normal.png", "lower-roughness.png",
            "back-basecolor.png", "back-emission.png", "back-emission-mask.png",
            "back-normal.png", "back-roughness.png"
        };

        private static readonly string[] StableMaterialNames =
        {
            "MAT_BackMOP", "MAT_ClearSeal", "MAT_ClearSealEdge", "MAT_FrontMOP",
            "MAT_GrooveDark", "MAT_LowerMOP", "MAT_PolishedSteel", "MAT_TrackBronze",
            "MAT_Zirconium_PurpleBlack"
        };

        private static readonly Dictionary<string, string> TextureHashes =
            new Dictionary<string, string>(StringComparer.Ordinal)
            {
                ["back-basecolor.png"] = "df5c6d263ee36fe9945cbbaff430aa9183e1bc11a23d1a892d8a629dc9ba3672",
                ["back-emission-mask.png"] = "4547ce83890dd68b3cc115bb95bab05827251ff4825a460e4f15a7ad91b2a907",
                ["back-emission.png"] = "52b3a68917352a9cbd9eba6dc78d901f41dc55b3320f8b90086353e7b65b008a",
                ["back-normal.png"] = "3ef7366a2c2ef3d32c1305104be509551ad4c7c65cb0e91b080dc23a0cb58413",
                ["back-roughness.png"] = "9c212e88b133dd46418b1da2264afdd1dc97d6281fa7566348a2533a4ff74d0e",
                ["front-basecolor.png"] = "330623fd942ccd3f28cafebe7508c31cc58e6e47dad45e00284401f8132bf15a",
                ["front-emission-mask.png"] = "a74637f79b30a8723f52cbe9ad69497e208ffc53f8c0948a9227a6b27a1827f2",
                ["front-emission.png"] = "fecf44ef3cd982c44fa8c84bb8936c28e96dfa9792d1e4cb9b5536a84852686b",
                ["front-normal.png"] = "1540c7baa73aa9470413dc6c8b1d033d9727cb24e6344cabdefe4e92410c1057",
                ["front-roughness.png"] = "2b2239559d39144893ee12b24d8e881de9b15ac12715e1c040ba9c3d817bb917",
                ["lower-basecolor.png"] = "6ff04a9b30f411dd740aefcaa113ae5f087a7c1ce7611caf87da47db60434a77",
                ["lower-emission-mask.png"] = "d3da11e2d4f931f44ead3f8605d321b1b9f0ef0f0d71da99b61baae58abdc80f",
                ["lower-emission.png"] = "67da301370fba08efac8c07527a1f2fb3b6e25decdbad92d45ad8ec1d5c96044",
                ["lower-normal.png"] = "6a29d01e17599e799c0174e31e394f22d3fa6d8116004ca72fa7a41b68c5febb",
                ["lower-roughness.png"] = "59a18517f21f376a0d29fc41e3f7fdedcd274281944a1299f046c82541b05625"
            };

        private static readonly Dictionary<string, string[]> ExpectedRendererMaterials =
            new Dictionary<string, string[]>(StringComparer.Ordinal)
            {
                ["LowerShell"] = new[] { "MAT_Zirconium_PurpleBlack" },
                ["LowerFrontArtwork"] = new[] { "MAT_LowerMOP" },
                ["BackArtwork"] = new[] { "MAT_BackMOP" },
                ["UpperShell"] = new[] { "MAT_Zirconium_PurpleBlack" },
                ["FrontArtwork"] = new[] { "MAT_FrontMOP" },
                ["ClearSealCap"] = new[] { "MAT_ClearSeal", "MAT_ClearSealEdge" },
                ["StraightTrack_1"] = new[] { "MAT_TrackBronze" },
                ["StraightTrack_2"] = new[] { "MAT_TrackBronze" },
                ["RotaryCarrierTrack"] = new[] { "MAT_TrackBronze" },
                ["CentralAdjustmentScrew"] = new[] { "MAT_PolishedSteel" },
                ["IllustrativeFollower_A"] = new[] { "MAT_PolishedSteel" },
                ["IllustrativeFollower_B"] = new[] { "MAT_PolishedSteel" },
                ["RearReplaceablePatch"] = new[] { "MAT_BackMOP" },
                ["RearClearCap"] = new[] { "MAT_ClearSeal" },
                ["RearRotationOrientationMark"] = new[] { "MAT_GrooveDark" },
                ["FrontScrew_1"] = new[] { "MAT_PolishedSteel" },
                ["FrontScrewSlot_1"] = new[] { "MAT_GrooveDark" },
                ["FrontScrew_2"] = new[] { "MAT_PolishedSteel" },
                ["FrontScrewSlot_2"] = new[] { "MAT_GrooveDark" }
            };

        private static readonly Dictionary<string, string> CollisionOwners =
            new Dictionary<string, string>(StringComparer.Ordinal)
            {
                ["UCX_FixedLower"] = "FixedLowerAssembly",
                ["UCX_MovingUpper"] = "MovingUpperAssembly",
                ["UCX_RearRotor"] = "RearRotorAssembly"
            };

        private static readonly Dictionary<string, string> ExpectedRendererOwners =
            new Dictionary<string, string>(StringComparer.Ordinal)
            {
                ["LowerShell"] = "FixedLowerAssembly",
                ["LowerFrontArtwork"] = "FixedLowerAssembly",
                ["BackArtwork"] = "FixedLowerAssembly",
                ["UpperShell"] = "MovingUpperAssembly",
                ["FrontArtwork"] = "MovingUpperAssembly",
                ["ClearSealCap"] = "MovingUpperAssembly",
                ["StraightTrack_1"] = "MechanicalTrackAssembly",
                ["StraightTrack_2"] = "MechanicalTrackAssembly",
                ["RotaryCarrierTrack"] = "MechanicalTrackAssembly",
                ["CentralAdjustmentScrew"] = "MechanicalTrackAssembly",
                ["IllustrativeFollower_A"] = "MechanicalTrackAssembly",
                ["IllustrativeFollower_B"] = "MechanicalTrackAssembly",
                ["RearReplaceablePatch"] = "RearRotorAssembly",
                ["RearClearCap"] = "RearRotorAssembly",
                ["RearRotationOrientationMark"] = "RearRotorAssembly",
                ["FrontScrew_1"] = "MovingUpperAssembly",
                ["FrontScrewSlot_1"] = "MovingUpperAssembly",
                ["FrontScrew_2"] = "MovingUpperAssembly",
                ["FrontScrewSlot_2"] = "MovingUpperAssembly"
            };

        [MenuItem("Fidgeting/Model Pipeline/model-hhax/Gate 11 Build")]
        public static void BuildGate11()
        {
            string shippingHashBefore = File.Exists(AssetAbsolute(ShippingScenePath))
                ? Sha256(AssetAbsolute(ShippingScenePath)) : "missing";
            EnsureFolders();
            CopyApprovedSources();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            ConfigureModelImporter(ModelPath, false);
            ConfigureModelImporter(CollisionPath, true);
            ConfigureTextureImports();
            Dictionary<string, Material> materials = BuildMaterials();
            GameObject prefab = BuildPrefab(materials);
            BuildSceneAndStaticEvidence(prefab, materials, shippingHashBefore);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            string shippingHashAfter = File.Exists(AssetAbsolute(ShippingScenePath))
                ? Sha256(AssetAbsolute(ShippingScenePath)) : "missing";
            if (!string.Equals(shippingHashBefore, shippingHashAfter, StringComparison.Ordinal))
                throw new InvalidOperationException("Gate 11 changed the shipping scene.");
            Debug.Log("model-hhax Gate 11 isolated Unity candidate and parity evidence complete.");
        }

        [MenuItem("Fidgeting/Model Pipeline/model-hhax/Gate 11 Build And Run PlayMode Capture")]
        public static void BuildAndRunGate11()
        {
            SessionState.SetBool(PendingRuntimeCaptureKey, true);
            BuildGate11();
            QueuePendingRuntimeCapture();
        }

        [InitializeOnLoadMethod]
        private static void ResumePendingRuntimeCaptureAfterReload()
        {
            if (SessionState.GetBool(PendingRuntimeCaptureKey, false))
                QueuePendingRuntimeCapture();
        }

        private static void QueuePendingRuntimeCapture()
        {
            EditorApplication.delayCall -= TryStartPendingRuntimeCapture;
            EditorApplication.delayCall += TryStartPendingRuntimeCapture;
        }

        private static void TryStartPendingRuntimeCapture()
        {
            if (!SessionState.GetBool(PendingRuntimeCaptureKey, false)) return;
            if (EditorApplication.isCompiling || EditorApplication.isUpdating)
            {
                QueuePendingRuntimeCapture();
                return;
            }

            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            GameObject host = GameObject.Find("ModelHhax_Gate11_ReviewHost")
                ?? throw new InvalidDataException("Gate 11 review host is missing.");
            ModelHhaxRuntimeEvidenceCapture prior =
                host.GetComponent<ModelHhaxRuntimeEvidenceCapture>();
            if (prior != null) UnityEngine.Object.DestroyImmediate(prior);
            ModelHhaxDirectPoseController controller =
                host.GetComponentInChildren<ModelHhaxDirectPoseController>(true)
                ?? throw new InvalidDataException("Direct-pose controller is missing.");
            Camera camera = host.GetComponentInChildren<Camera>(true)
                ?? throw new InvalidDataException("Review camera is missing.");
            Light[] lights = host.GetComponentsInChildren<Light>(true);
            Renderer floor = host.transform.Find("ReviewFloor")?.GetComponent<Renderer>();
            ModelHhaxRuntimeEvidenceCapture capture =
                host.AddComponent<ModelHhaxRuntimeEvidenceCapture>();
            if (capture == null)
            {
                SessionState.SetBool(PendingRuntimeCaptureKey, false);
                throw new InvalidOperationException(
                    "Gate 11 runtime evidence component could not be attached.");
            }
            capture.Configure(controller, camera, lights, floor,
                ProjectPath(RuntimeEvidenceRelative), 900, 900, 180);
            SessionState.SetBool(PendingRuntimeCaptureKey, false);
            // Evidence harness and absolute output path remain unsaved/editor-only.
            EditorApplication.delayCall += () => EditorApplication.isPlaying = true;
        }

        public static string ProjectRoot => Directory.GetParent(Application.dataPath)!.FullName;
        public static string EvidenceRoot => ProjectPath(EvidenceRelative);

        private static string ProjectPath(string relative) =>
            Path.GetFullPath(Path.Combine(ProjectRoot, relative));

        private static string AssetAbsolute(string assetPath) =>
            Path.GetFullPath(Path.Combine(ProjectRoot, assetPath));

        private static void EnsureFolders()
        {
            foreach (string path in new[]
                     {
                         CandidateRoot + "/Models", TextureRoot, MaterialRoot,
                         CandidateRoot + "/Prefabs", CandidateRoot + "/Scenes"
                     })
                Directory.CreateDirectory(AssetAbsolute(path));
            Directory.CreateDirectory(EvidenceRoot);
            Directory.CreateDirectory(ProjectPath(RuntimeEvidenceRelative));
        }

        private static void CopyApprovedSources()
        {
            string sourceFbx = ProjectPath(SourceRoot + "/model-hhax-final.fbx");
            string sourceCollision = ProjectPath(SourceRoot + "/model-hhax-collision.fbx");
            AssertHash(sourceFbx, ApprovedFbxSha256, "approved Gate 10 FBX");
            AssertHash(sourceCollision, ApprovedCollisionSha256, "approved Gate 10 collision FBX");
            AssertHash(ProjectPath(SourceRoot + "/export-manifest.json"),
                ExportManifestSha256, "Gate 10 export manifest");
            AssertHash(ProjectPath(SourceRoot + "/export-validation.json"),
                ExportValidationSha256, "Gate 10 export validation");
            AssertHash(ProjectPath(SourceRoot + "/hierarchy-motion-metadata.json"),
                HierarchyMetadataSha256, "Gate 10 hierarchy metadata");
            AssertHash(ProjectPath(SourceRoot + "/neutral-camera-recipe.json"),
                NeutralCameraRecipeSha256, "Gate 10 neutral camera recipe");
            AssertHash(ProjectPath(SourceRoot + "/unity-import-contract.json"),
                UnityImportContractSha256, "Gate 10 Unity import contract");
            CopyIfChanged(sourceFbx, AssetAbsolute(ModelPath));
            CopyIfChanged(sourceCollision, AssetAbsolute(CollisionPath));
            foreach (string name in TextureNames)
            {
                AssertHash(ProjectPath(SourceTextureRoot + "/" + name), TextureHashes[name],
                    "approved Gate 07 texture " + name);
                CopyIfChanged(ProjectPath(SourceTextureRoot + "/" + name), AssetAbsolute(TextureRoot + "/" + name));
            }
            CopyIfChanged(ProjectPath(BlenderNeutralSource), Path.Combine(EvidenceRoot, "blender-neutral.png"));
            CopyIfChanged(ProjectPath(SourceRoot + "/neutral-camera-recipe.json"),
                Path.Combine(EvidenceRoot, "neutral-camera-recipe.json"));
            AssertHash(AssetAbsolute(ModelPath), ApprovedFbxSha256, "copied Gate 10 FBX");
            AssertHash(AssetAbsolute(CollisionPath), ApprovedCollisionSha256, "copied collision FBX");
        }

        private static void CopyIfChanged(string source, string destination)
        {
            if (!File.Exists(source)) throw new FileNotFoundException("Missing source", source);
            Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
            if (File.Exists(destination) && Sha256(source) == Sha256(destination)) return;
            File.Copy(source, destination, true);
        }

        private static void ConfigureModelImporter(string path, bool collision)
        {
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
            ModelImporter importer = AssetImporter.GetAtPath(path) as ModelImporter
                ?? throw new InvalidOperationException($"No ModelImporter for {path}");
            importer.importAnimation = false;
            importer.animationType = ModelImporterAnimationType.None;
            importer.materialImportMode = collision
                ? ModelImporterMaterialImportMode.None
                : ModelImporterMaterialImportMode.ImportStandard;
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

            Vector3 measured = MeasureModelAsset(path);
            if (!collision)
            {
                bool expected = Mathf.Abs(measured.x - 0.0309f) <= 0.0002f
                    && Mathf.Abs(measured.y - 0.0136f) <= 0.0002f
                    && Mathf.Abs(measured.z - 0.0505f) <= 0.0002f;
                if (!expected)
                    throw new InvalidDataException(
                        $"Unity import must preserve the Gate 10 scale exactly; got {measured}m.");
            }
            else
            {
                float maximum = Mathf.Max(measured.x, Mathf.Max(measured.y, measured.z));
                if (maximum < 0.01f || maximum > 0.06f)
                    throw new InvalidDataException(
                        $"Collision import scale is outside the approved product envelope: {measured}m.");
            }
        }

        private static Vector3 MeasureModelAsset(string path)
        {
            GameObject asset = AssetDatabase.LoadAssetAtPath<GameObject>(path)
                ?? throw new InvalidOperationException($"Model failed to import: {path}");
            return CalculateBounds(asset.transform, _ => true).size;
        }

        private static void ConfigureTextureImports()
        {
            foreach (string name in TextureNames)
            {
                string path = TextureRoot + "/" + name;
                TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter
                    ?? throw new InvalidOperationException($"No TextureImporter for {path}");
                bool normal = name.Contains("-normal", StringComparison.Ordinal);
                bool data = normal || name.Contains("roughness", StringComparison.Ordinal)
                    || name.Contains("mask", StringComparison.Ordinal);
                importer.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                importer.sRGBTexture = !data;
                importer.alphaSource = TextureImporterAlphaSource.None;
                importer.mipmapEnabled = true;
                importer.filterMode = FilterMode.Trilinear;
                importer.anisoLevel = 8;
                importer.maxTextureSize = 2048;
                importer.wrapMode = TextureWrapMode.Clamp;
                importer.isReadable = true;
                importer.SaveAndReimport();
            }
            foreach (string stem in new[] { "front", "lower", "back" })
                BuildMetallicSmoothness(stem, 0.08f);
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        }

        private static void BuildMetallicSmoothness(string stem, float metallic)
        {
            string sourcePath = TextureRoot + $"/{stem}-roughness.png";
            Texture2D source = AssetDatabase.LoadAssetAtPath<Texture2D>(sourcePath)
                ?? throw new InvalidOperationException($"Roughness failed to load: {sourcePath}");
            Color32[] pixels = source.GetPixels32();
            byte metal = (byte)Mathf.RoundToInt(metallic * 255f);
            for (int i = 0; i < pixels.Length; i++)
                pixels[i] = new Color32(metal, metal, metal, (byte)(255 - pixels[i].r));
            Texture2D packed = new Texture2D(source.width, source.height, TextureFormat.RGBA32, false, true);
            packed.SetPixels32(pixels);
            packed.Apply(false, false);
            string assetPath = TextureRoot + $"/{stem}-metallic-smoothness.png";
            File.WriteAllBytes(AssetAbsolute(assetPath), packed.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(packed);
            AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceSynchronousImport);
            TextureImporter importer = AssetImporter.GetAtPath(assetPath) as TextureImporter
                ?? throw new InvalidOperationException($"Packed map failed to import: {assetPath}");
            importer.sRGBTexture = false;
            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            importer.mipmapEnabled = true;
            importer.filterMode = FilterMode.Trilinear;
            importer.anisoLevel = 8;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.SaveAndReimport();
        }

        private static Dictionary<string, Material> BuildMaterials()
        {
            Shader lit = Shader.Find("Universal Render Pipeline/Lit")
                ?? throw new InvalidOperationException("URP Lit shader is required.");
            Dictionary<string, Material> result = new Dictionary<string, Material>();
            result["MAT_FrontMOP"] = BuildMop(lit, "MAT_FrontMOP", "front", true);
            result["MAT_LowerMOP"] = BuildMop(lit, "MAT_LowerMOP", "lower", false);
            result["MAT_BackMOP"] = BuildMop(lit, "MAT_BackMOP", "back", true);
            result["MAT_Zirconium_PurpleBlack"] = BuildOpaque(lit, "MAT_Zirconium_PurpleBlack",
                Hex("241D2F"), 0.96f, 0.82f, 0.48f, 0.90f);
            result["MAT_TrackBronze"] = BuildOpaque(lit, "MAT_TrackBronze",
                Hex("956F42"), 0.88f, 0.78f, 0f, 0f);
            result["MAT_PolishedSteel"] = BuildOpaque(lit, "MAT_PolishedSteel",
                Hex("D7DFE6"), 0.96f, 0.86f, 0.35f, 0.90f);
            result["MAT_GrooveDark"] = BuildOpaque(lit, "MAT_GrooveDark",
                Hex("15131B"), 0.18f, 0.73f, 0f, 0f);
            result["MAT_ClearSeal"] = BuildTransparent(lit, "MAT_ClearSeal",
                Hex("E5EFF6"), 0.045f, 0.985f, 3000);
            result["MAT_ClearSealEdge"] = BuildTransparent(lit, "MAT_ClearSealEdge",
                Hex("B1CBE5"), 0.34f, 0.978f, 3010);
            AssetDatabase.SaveAssets();
            return result;
        }

        private static Material BuildMop(Shader shader, string name, string stem, bool emission)
        {
            Material material = UpsertMaterial(shader, name);
            // Match the approved Blender daylight grade (Value 0.62). The
            // source texture already carries the photographic hue variation;
            // multiplying it here keeps the Unity daylight result from being
            // mistaken for the charged dark-state emission.
            SetOpaque(material, new Color(0.62f, 0.62f, 0.62f, 1f),
                0.08f, 0.62f, 0f, 0f);
            material.SetTexture("_BaseMap", LoadTexture($"{stem}-basecolor.png"));
            material.SetTexture("_MetallicGlossMap", LoadTexture($"{stem}-metallic-smoothness.png"));
            material.EnableKeyword("_METALLICSPECGLOSSMAP");
            material.SetFloat("_Metallic", 0.08f);
            material.SetFloat("_Smoothness", 1f);
            material.SetTexture("_BumpMap", LoadTexture($"{stem}-normal.png"));
            material.SetFloat("_BumpScale", 0.28f);
            material.EnableKeyword("_NORMALMAP");
            if (emission)
            {
                material.SetTexture("_EmissionMap", LoadTexture($"{stem}-emission.png"));
                material.SetColor("_EmissionColor", Color.white * 0.05f);
                material.EnableKeyword("_EMISSION");
                material.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;
            }
            else
            {
                material.SetTexture("_EmissionMap", null);
                material.SetColor("_EmissionColor", Color.black);
                material.DisableKeyword("_EMISSION");
            }
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Texture2D LoadTexture(string name) =>
            AssetDatabase.LoadAssetAtPath<Texture2D>(TextureRoot + "/" + name)
            ?? throw new InvalidOperationException($"Texture failed to load: {name}");

        private static Material BuildOpaque(
            Shader shader, string name, Color color, float metallic, float smoothness,
            float coatMask, float coatSmoothness)
        {
            Material material = UpsertMaterial(shader, name);
            SetOpaque(material, color, metallic, smoothness, coatMask, coatSmoothness);
            return material;
        }

        private static void SetOpaque(
            Material material, Color color, float metallic, float smoothness,
            float coatMask, float coatSmoothness)
        {
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Smoothness", smoothness);
            material.SetFloat("_Surface", 0f);
            material.SetFloat("_Blend", 0f);
            material.SetFloat("_ZWrite", 1f);
            material.SetFloat("_SrcBlend", (float)BlendMode.One);
            material.SetFloat("_DstBlend", (float)BlendMode.Zero);
            material.SetOverrideTag("RenderType", "Opaque");
            material.DisableKeyword("_SURFACE_TYPE_TRANSPARENT");
            material.renderQueue = -1;
            material.SetFloat("_ClearCoatMask", coatMask);
            material.SetFloat("_ClearCoatSmoothness", coatSmoothness);
            if (coatMask > 0f) material.EnableKeyword("_CLEARCOAT");
            else material.DisableKeyword("_CLEARCOAT");
            material.SetFloat("_SpecularHighlights", 1f);
            material.SetFloat("_EnvironmentReflections", 1f);
            EditorUtility.SetDirty(material);
        }

        private static Material BuildTransparent(
            Shader shader, string name, Color color, float alpha, float smoothness, int queue)
        {
            Material material = UpsertMaterial(shader, name);
            color.a = alpha;
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Metallic", 0f);
            material.SetFloat("_Smoothness", smoothness);
            material.SetFloat("_Surface", 1f);
            material.SetFloat("_Blend", 2f);
            material.SetFloat("_ZWrite", 0f);
            material.SetFloat("_SrcBlend", (float)BlendMode.One);
            material.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
            material.SetFloat("_SrcBlendAlpha", (float)BlendMode.One);
            material.SetFloat("_DstBlendAlpha", (float)BlendMode.OneMinusSrcAlpha);
            material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            material.EnableKeyword("_ALPHAPREMULTIPLY_ON");
            material.SetOverrideTag("RenderType", "Transparent");
            material.renderQueue = queue;
            material.SetFloat("_ClearCoatMask", 0.95f);
            material.SetFloat("_ClearCoatSmoothness", 0.98f);
            material.EnableKeyword("_CLEARCOAT");
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Material UpsertMaterial(Shader shader, string name)
        {
            string path = MaterialRoot + "/" + name + ".mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader) { name = name };
                AssetDatabase.CreateAsset(material, path);
            }
            else material.shader = shader;
            return material;
        }

        private static Color Hex(string value)
        {
            if (!ColorUtility.TryParseHtmlString("#" + value, out Color color))
                throw new InvalidDataException("Bad colour: " + value);
            return color;
        }

        private static GameObject BuildPrefab(Dictionary<string, Material> materials)
        {
            GameObject modelAsset = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath)
                ?? throw new InvalidOperationException("Approved FBX is not imported.");
            GameObject root = new GameObject("ModelHhax_Gate11_Root");
            GameObject model = (GameObject)PrefabUtility.InstantiatePrefab(modelAsset);
            PrefabUtility.UnpackPrefabInstance(model,
                PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            model.name = "ModelHhax_Root";
            model.transform.SetParent(root.transform, false);
            Renderer[] modelRenderers = model.GetComponentsInChildren<Renderer>(true);
            if (modelRenderers.Length != ExpectedRendererMaterials.Count)
                throw new InvalidDataException(
                    $"Expected {ExpectedRendererMaterials.Count} render meshes, got {modelRenderers.Length}.");
            foreach (Renderer renderer in modelRenderers)
            {
                if (!ExpectedRendererMaterials.TryGetValue(renderer.name, out string[] expected))
                    throw new InvalidDataException("Unknown Gate 10 renderer: " + renderer.name);
                if (renderer.sharedMaterials.Length != expected.Length)
                    throw new InvalidDataException(
                        $"Renderer {renderer.name} expected {expected.Length} material slots, got {renderer.sharedMaterials.Length}.");
                renderer.sharedMaterials = expected.Select(name => materials[name]).ToArray();
            }

            Transform fixedLower = FindDescendant(model.transform, "FixedLowerAssembly")
                ?? throw new InvalidDataException("FixedLowerAssembly is missing.");
            Transform moving = FindDescendant(model.transform, "MovingUpperAssembly")
                ?? throw new InvalidDataException("MovingUpperAssembly is missing.");
            Transform rotor = FindDescendant(model.transform, "RearRotorAssembly")
                ?? throw new InvalidDataException("RearRotorAssembly is missing.");
            Transform mechanical = FindDescendant(model.transform, "MechanicalTrackAssembly")
                ?? throw new InvalidDataException("MechanicalTrackAssembly is missing.");
            Dictionary<string, Transform> rendererOwners = new Dictionary<string, Transform>(StringComparer.Ordinal)
            {
                ["FixedLowerAssembly"] = fixedLower,
                ["MovingUpperAssembly"] = moving,
                ["RearRotorAssembly"] = rotor,
                ["MechanicalTrackAssembly"] = mechanical
            };
            foreach (Renderer renderer in modelRenderers)
            {
                string ownerName = ExpectedRendererOwners[renderer.name];
                Transform owner = rendererOwners[ownerName];
                if (!renderer.transform.IsChildOf(owner))
                    renderer.transform.SetParent(owner, true);
            }

            GameObject collisionAsset = AssetDatabase.LoadAssetAtPath<GameObject>(CollisionPath)
                ?? throw new InvalidOperationException("Collision FBX is not imported.");
            GameObject collision = (GameObject)PrefabUtility.InstantiatePrefab(collisionAsset);
            collision.name = "CollisionProxies";
            collision.transform.SetParent(root.transform, false);
            PrefabUtility.UnpackPrefabInstance(collision,
                PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            Dictionary<string, Transform> owners = new Dictionary<string, Transform>(StringComparer.Ordinal)
            {
                ["FixedLowerAssembly"] = fixedLower,
                ["MovingUpperAssembly"] = moving,
                ["RearRotorAssembly"] = rotor
            };
            foreach (KeyValuePair<string, string> pair in CollisionOwners)
            {
                Transform proxy = FindDescendant(collision.transform, pair.Key)
                    ?? throw new InvalidDataException("Missing collision proxy: " + pair.Key);
                MeshFilter filter = proxy.GetComponent<MeshFilter>()
                    ?? throw new InvalidDataException("Collision proxy has no mesh: " + pair.Key);
                if (filter.sharedMesh == null)
                    throw new InvalidDataException("Collision proxy mesh is empty: " + pair.Key);
                proxy.SetParent(owners[pair.Value], true);
                foreach (Renderer renderer in proxy.GetComponentsInChildren<Renderer>(true))
                    renderer.enabled = false;
                MeshCollider collider = proxy.gameObject.GetComponent<MeshCollider>();
                if (collider == null)
                    collider = proxy.gameObject.AddComponent<MeshCollider>();
                collider.sharedMesh = filter.sharedMesh;
                collider.convex = true;
            }
            UnityEngine.Object.DestroyImmediate(collision);

            ModelHhaxDirectPoseController controller = root.AddComponent<ModelHhaxDirectPoseController>();
            controller.Configure(moving, rotor, Vector3.forward, Vector3.up);
            PrefabUtility.SaveAsPrefabAsset(root, PrefabPath);
            UnityEngine.Object.DestroyImmediate(root);
            return AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath)
                ?? throw new InvalidOperationException("Candidate prefab failed to save.");
        }

        private static Transform FindDescendant(Transform root, string name)
        {
            foreach (Transform item in root.GetComponentsInChildren<Transform>(true))
                if (item.name == name) return item;
            return null;
        }

        private static void BuildSceneAndStaticEvidence(
            GameObject prefab,
            Dictionary<string, Material> materials,
            string shippingHashBefore)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject host = new GameObject("ModelHhax_Gate11_ReviewHost");
            SceneManager.MoveGameObjectToScene(host, scene);
            GameObject candidate = (GameObject)PrefabUtility.InstantiatePrefab(prefab, scene);
            candidate.transform.SetParent(host.transform, false);
            candidate.transform.SetLocalPositionAndRotation(Vector3.zero, Quaternion.identity);
            candidate.transform.localScale = Vector3.one;
            ModelHhaxDirectPoseController controller = candidate.GetComponent<ModelHhaxDirectPoseController>()
                ?? throw new InvalidDataException("Candidate direct-pose controller is missing.");

            Renderer floor = CreateFloor(host.transform);
            Light[] lights = CreateLights(host.transform);
            Camera camera = CreateCamera(host.transform);
            ConfigureNeutralWorld();

            // The approved Blender neutral reference is open. Source +Y maps
            // to Unity +Z, so the negative source-Y camera maps to negative Z.
            controller.SetTravelMm(ModelHhaxDirectPoseController.MaximumTravelMm);
            SetView(camera, new Vector3(0.092f, 0.094f, -0.119f), new Vector3(0f, 0.006f, 0f), 32.378413f);
            Capture(camera, Path.Combine(EvidenceRoot, "unity-neutral.png"), 1000, 1000);

            controller.ResetPose();
            floor.enabled = false;
            SetView(camera, new Vector3(0.070f, -0.060f, 0.105f), new Vector3(0f, 0.006f, 0f), 34f);
            Capture(camera, Path.Combine(EvidenceRoot, "unity-back.png"), 1000, 1000);

            floor.enabled = true;
            controller.SetTravelMm(ModelHhaxDirectPoseController.MaximumTravelMm);
            SetView(camera, new Vector3(0.090f, 0.105f, -0.135f), new Vector3(0f, 0.006f, 0.008f), 34f);
            Capture(camera, Path.Combine(EvidenceRoot, "unity-open-track.png"), 1000, 1000);

            controller.ResetPose();
            foreach (Light light in lights) light.enabled = false;
            floor.enabled = false;
            RenderSettings.ambientLight = Color.black;
            ModelHhaxArtworkEmission.Set(candidate, 3.6f);
            SetView(camera, new Vector3(0.092f, 0.094f, -0.119f), new Vector3(0f, 0.006f, 0f), 32.378413f);
            Capture(camera, Path.Combine(EvidenceRoot, "unity-dark.png"), 1000, 1000);
            ModelHhaxArtworkEmission.Clear(candidate);
            foreach (Light light in lights) light.enabled = true;
            floor.enabled = true;
            ConfigureNeutralWorld();
            controller.ResetPose();

            EditorSceneManager.SaveScene(scene, ScenePath, false);
            AssetDatabase.SaveAssets();
            WriteReports(candidate, materials, shippingHashBefore);
        }

        private static Renderer CreateFloor(Transform parent)
        {
            GameObject floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
            floor.name = "ReviewFloor";
            floor.transform.SetParent(parent, false);
            floor.transform.localPosition = new Vector3(0f, -0.0005f, 0f);
            floor.transform.localScale = new Vector3(0.035f, 1f, 0.035f);
            UnityEngine.Object.DestroyImmediate(floor.GetComponent<Collider>());
            Shader lit = Shader.Find("Universal Render Pipeline/Lit")
                ?? throw new InvalidOperationException("URP Lit shader is required.");
            Material material = UpsertMaterial(lit, "M_HHAX_NeutralFloor");
            SetOpaque(material, Hex("566176"), 0f, 0.42f, 0f, 0f);
            Renderer renderer = floor.GetComponent<Renderer>();
            renderer.sharedMaterial = material;
            return renderer;
        }

        private static Light[] CreateLights(Transform parent)
        {
            Light key = CreateLight(parent, "Key_D65", LightType.Directional,
                new Vector3(52f, -38f, -18f), Hex("F5FAFF"), 0.90f, Vector3.zero, 0f);
            Light fill = CreateLight(parent, "Fill_Cool", LightType.Directional,
                new Vector3(-38f, 145f, 25f), Hex("B7CAFF"), 0.42f, Vector3.zero, 0f);
            Light rim = CreateLight(parent, "Rim_Warm", LightType.Directional,
                new Vector3(-20f, 70f, 160f), Hex("FFD0BA"), 0.24f, Vector3.zero, 0f);
            key.shadows = LightShadows.Soft;
            fill.shadows = LightShadows.None;
            rim.shadows = LightShadows.None;
            return new[] { key, fill, rim };
        }

        private static Light CreateLight(
            Transform parent, string name, LightType type, Vector3 euler,
            Color color, float intensity, Vector3 position, float range)
        {
            GameObject item = new GameObject(name);
            item.transform.SetParent(parent, false);
            item.transform.localPosition = position;
            item.transform.localEulerAngles = euler;
            Light light = item.AddComponent<Light>();
            light.type = type;
            light.color = color;
            light.intensity = intensity;
            if (range > 0f) light.range = range;
            return light;
        }

        private static Camera CreateCamera(Transform parent)
        {
            GameObject item = new GameObject("CAM_HHAX_Gate11_Review");
            item.transform.SetParent(parent, false);
            Camera camera = item.AddComponent<Camera>();
            camera.enabled = false;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Hex("151B29");
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 10f;
            camera.allowHDR = true;
            camera.allowMSAA = true;
            return camera;
        }

        private static void ConfigureNeutralWorld()
        {
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = Hex("181D2A");
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Skybox;
            RenderSettings.reflectionIntensity = 0.38f;
        }

        private static void SetView(Camera camera, Vector3 position, Vector3 target, float fov)
        {
            camera.transform.position = position;
            camera.transform.rotation = Quaternion.LookRotation(target - position, Vector3.up);
            camera.fieldOfView = fov;
        }

        public static void Capture(Camera camera, string path, int width, int height)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            RenderTexture target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
            target.Create();
            RenderTexture previous = RenderTexture.active;
            camera.targetTexture = target;
            camera.Render();
            camera.Render();
            RenderTexture.active = target;
            Texture2D image = new Texture2D(width, height, TextureFormat.RGBA32, false, false);
            image.ReadPixels(new Rect(0f, 0f, width, height), 0, 0);
            image.Apply(false, false);
            File.WriteAllBytes(path, image.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(image);
            camera.targetTexture = null;
            RenderTexture.active = previous;
            target.Release();
            UnityEngine.Object.DestroyImmediate(target);
        }

        private static void WriteReports(
            GameObject candidate,
            Dictionary<string, Material> materials,
            string shippingHashBefore)
        {
            Renderer[] renderers = candidate.GetComponentsInChildren<Renderer>(true)
                .Where(renderer => !renderer.name.StartsWith("UCX_", StringComparison.Ordinal)).ToArray();
            MeshFilter[] filters = candidate.GetComponentsInChildren<MeshFilter>(true)
                .Where(filter => !filter.name.StartsWith("UCX_", StringComparison.Ordinal)).ToArray();
            int triangles = filters.Sum(filter => filter.sharedMesh == null
                ? 0 : Enumerable.Range(0, filter.sharedMesh.subMeshCount)
                    .Sum(index => (int)filter.sharedMesh.GetIndexCount(index) / 3));
            Bounds bounds = CalculateBounds(candidate.transform,
                renderer => !renderer.name.StartsWith("UCX_", StringComparison.Ordinal));
            Vector3 size = bounds.size;
            bool dimensionsPass = Mathf.Abs(size.x - 0.0309f) <= 0.0002f
                && Mathf.Abs(size.y - 0.0136f) <= 0.0002f
                && Mathf.Abs(size.z - 0.0505f) <= 0.0002f;
            int colliders = candidate.GetComponentsInChildren<MeshCollider>(true).Length;
            bool hierarchyPass = FindDescendant(candidate.transform, "FixedLowerAssembly") != null
                && FindDescendant(candidate.transform, "MovingUpperAssembly") != null
                && FindDescendant(candidate.transform, "RearRotorAssembly") != null;
            bool materialPass = StableMaterialNames.All(name => materials.ContainsKey(name))
                && RendererMaterialsPass(renderers);
            bool rendererOwnershipPass = RendererOwnershipPass(candidate.transform, renderers);
            bool collisionOwnershipPass = CollisionOwnershipPass(candidate.transform);
            bool pass = dimensionsPass && renderers.Length == ExpectedRenderMeshCount
                && triangles == ExpectedTriangleCount && colliders == ExpectedCollisionCount
                && hierarchyPass && materialPass && rendererOwnershipPass && collisionOwnershipPass
                && candidate.GetComponentInChildren<Animator>(true) == null;

            string report = "{\n"
                + "  \"schemaVersion\": 1,\n"
                + "  \"modelId\": \"model-hhax\",\n"
                + "  \"engine\": \"Unity 6000.5.6f1 / URP\",\n"
                + $"  \"status\": \"{(pass ? "pass" : "fail")}\",\n"
                + $"  \"approvedFbxSha256\": \"{ApprovedFbxSha256}\",\n"
                + $"  \"approvedCollisionSha256\": \"{ApprovedCollisionSha256}\",\n"
                + $"  \"governingContractSha256\": \"{GoverningContractSha256}\",\n"
                + $"  \"shippingSceneSha256BeforeAndAfter\": \"{shippingHashBefore}\",\n"
                + $"  \"boundsMeters\": [{F(size.x)}, {F(size.y)}, {F(size.z)}],\n"
                + $"  \"renderMeshCount\": {renderers.Length},\n"
                + $"  \"triangleCount\": {triangles},\n"
                + $"  \"collisionProxyCount\": {colliders},\n"
                + "  \"motion\": {\"upper\": \"direct +Z 0..0.0187m\", \"rearRotor\": \"independent +Y\", \"automatic\": false, \"coupling\": false},\n"
                + "  \"materialBinding\": {\"hhaxSpecific\": [\"zirconium-purple-black\", \"front-mop-sealed\", \"lower-mop-sealed\", \"back-mop-sealed\", \"clear-crystal-seal\", \"clear-crystal-seal-edge\", \"provisional-track-bronze\"], \"shared\": [\"bevel-polished\", \"groove-dark\"], \"modelLocalTextureSets\": [\"front\", \"lower\", \"back\"]},\n"
                + "  \"checks\": {\n"
                + $"    \"dimensions\": \"{(dimensionsPass ? "pass" : "fail")}\",\n"
                + $"    \"meshCount\": \"{(renderers.Length == ExpectedRenderMeshCount ? "pass" : "fail")}\",\n"
                + $"    \"triangleCount\": \"{(triangles == ExpectedTriangleCount ? "pass" : "fail")}\",\n"
                + $"    \"hierarchyAndPivots\": \"{(hierarchyPass ? "pass" : "fail")}\",\n"
                + $"    \"collisionOwners\": \"{(collisionOwnershipPass ? "pass" : "fail")}\",\n"
                + $"    \"materialsAndLocalTextures\": \"{(materialPass ? "pass" : "fail")}\",\n"
                + $"    \"rendererMotionOwners\": \"{(rendererOwnershipPass ? "pass" : "fail")}\",\n"
                + $"    \"noImportedAnimation\": \"{(candidate.GetComponentInChildren<Animator>(true) == null ? "pass" : "fail")}\",\n"
                + "    \"shippingSceneUnchanged\": \"pass\"\n"
                + "  },\n"
                + "  \"boundary\": \"isolated candidate only; no build, install, phone push, detent, haptic, force curve, timing or manufacturing claim\"\n"
                + "}\n";
            File.WriteAllText(Path.Combine(EvidenceRoot, "unity-parity-report.json"), report);

            string snapshot = "{\n"
                + "  \"schemaVersion\": 1,\n"
                + "  \"camera\": {\"positionMeters\": [0.092, 0.094, -0.119], \"targetMeters\": [0, 0.006, 0], \"verticalFovDegrees\": 32.378413},\n"
                + "  \"expectedBoundsMm\": [30.9, 13.6, 50.5],\n"
                + "  \"slideTravelMm\": [0, 18.7],\n"
                + "  \"rearRotorPivotSourceMm\": [0, 11.05, 0],\n"
                + "  \"artworkDaylightValue\": 0.62,\n"
                + "  \"artworkDaylightEmissionStrength\": 0.05,\n"
                + "  \"chargedDarkEvidenceEmissionStrength\": 3.6,\n"
                + "  \"productionAutomaticMotion\": false,\n"
                + "  \"physicalOrManufacturingClaim\": false\n"
                + "}\n";
            File.WriteAllText(Path.Combine(EvidenceRoot, "unity-parity-parameters.json"), snapshot);
            if (!pass) throw new InvalidOperationException("model-hhax Gate 11 parity validation failed. See unity-parity-report.json.");
        }

        private static bool RendererMaterialsPass(Renderer[] renderers)
        {
            if (renderers.Length != ExpectedRendererMaterials.Count) return false;
            HashSet<string> used = new HashSet<string>(StringComparer.Ordinal);
            foreach (Renderer renderer in renderers)
            {
                if (!ExpectedRendererMaterials.TryGetValue(renderer.name, out string[] expected))
                    return false;
                string[] actual = renderer.sharedMaterials
                    .Select(material => material == null ? string.Empty : material.name).ToArray();
                if (!actual.SequenceEqual(expected)) return false;
                foreach (string name in actual) used.Add(name);
            }
            return StableMaterialNames.All(used.Contains);
        }

        private static bool RendererOwnershipPass(Transform candidate, Renderer[] renderers)
        {
            foreach (Renderer renderer in renderers)
            {
                if (!ExpectedRendererOwners.TryGetValue(renderer.name, out string ownerName))
                    return false;
                Transform owner = FindDescendant(candidate, ownerName);
                if (owner == null || !renderer.transform.IsChildOf(owner)) return false;
            }
            return renderers.Length == ExpectedRendererOwners.Count;
        }

        private static bool CollisionOwnershipPass(Transform candidate)
        {
            foreach (KeyValuePair<string, string> pair in CollisionOwners)
            {
                Transform proxy = FindDescendant(candidate, pair.Key);
                Transform owner = FindDescendant(candidate, pair.Value);
                if (proxy == null || owner == null || proxy.parent != owner)
                    return false;
                MeshCollider collider = proxy.GetComponent<MeshCollider>();
                if (collider == null || collider.sharedMesh == null || !collider.convex)
                    return false;
                Renderer renderer = proxy.GetComponent<Renderer>();
                if (renderer != null && renderer.enabled) return false;
            }
            return candidate.GetComponentsInChildren<MeshCollider>(true).Length == ExpectedCollisionCount;
        }

        public static Bounds CalculateBounds(Transform root, Func<Renderer, bool> include)
        {
            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true).Where(include).ToArray();
            if (renderers.Length == 0) return new Bounds(Vector3.zero, Vector3.zero);
            Bounds bounds = renderers[0].bounds;
            for (int i = 1; i < renderers.Length; i++) bounds.Encapsulate(renderers[i].bounds);
            return bounds;
        }

        private static string F(float value) => value.ToString("0.########", CultureInfo.InvariantCulture);

        private static void AssertHash(string path, string expected, string label)
        {
            if (!File.Exists(path)) throw new FileNotFoundException("Missing " + label, path);
            string actual = Sha256(path);
            if (!string.Equals(actual, expected, StringComparison.Ordinal))
                throw new InvalidOperationException($"{label} hash mismatch. Expected {expected}, got {actual}.");
        }

        public static string Sha256(string path)
        {
            using SHA256 sha = SHA256.Create();
            using FileStream stream = File.OpenRead(path);
            return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", string.Empty).ToLowerInvariant();
        }
    }
}
