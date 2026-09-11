using System.Globalization;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Editor
{
    /// <summary>
    /// Gate 12 R007: R006-A (flocking) with the rarity block re-cut as a
    /// die-struck sandblasted foil badge, after the user's enamel-pin
    /// reference. Emblem and tier word become raised polished relief; the
    /// field carries bead-blast grain and a warm-to-deep gradient. Two
    /// variants for A/B: A sets the relief on its own foil plaque, B cuts
    /// the relief straight into the holographic plate.
    /// </summary>
    public static class PremiumDisplayCaseGate12R007Builder
    {
        public const string PlaquePrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R007/PresentationRoot.prefab";
        public const string ReliefPrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R007Relief/PresentationRoot.prefab";
        public const string PlaqueScenePath =
            "Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R007.unity";
        public const string ReliefScenePath =
            "Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R007Relief.unity";
        public const string EvidenceRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/rev-020";
        public const string ShaderName = "FidgetingApp/Gate12R007SandblastFoil";
        public const string PlaqueName = "RarityBadgePlaque";
        private const string GeneratedRoot = "Assets/_DisplayCase/Generated/Gate12R007";
        private const string MaterialRoot = GeneratedRoot + "/Materials";
        private const string TextureRoot = GeneratedRoot + "/Textures";

        // Plate-local units: 1 mm = 1e-5 (case assembly scaled 100).
        private const float Mm = 0.00001f;
        private const float RightBlockX = 63f * Mm;
        /// <summary>Plaque face, 0.6 µm (0.06 mm world) in front of the plate.</summary>
        private const float PlaqueFront = -0.0000186f;
        private const float EmblemFront = -0.0000192f;
        public const float PlaqueSizeMm = 40f;
        public const float PlaqueCornerMm = 4f;
        /// <summary>Mask margin so the recess shadow has room outside the plaque.</summary>
        private const float PlaqueMarginMm = 0.5f;
        public const float EmblemSizeMm = 22f;
        public const float EmblemZMm = -6f;
        public const float TierZMm = 14f;
        /// <summary>R005 authored 0.0000085; struck lettering is cut a little larger.</summary>
        public const float TierCharacterSize = 0.0000105f;

        [MenuItem("Fidgeting/Display Case/Gate 12/R007 Build Candidates (A plaque, B relief)")]
        public static void BuildCandidates()
        {
            PremiumDisplayCaseGate12R006Builder.BuildCandidates();
            EnsureDirectories();
            Texture2D grain = BuildGrainTexture();
            Texture2D mask = BuildPlaqueMask();
            Shader shader = PremiumDisplayCaseGate12R005Builder.RequireShader(ShaderName);
            // Field: fine bead-blast (30 tiles/m = 0.07 mm texels, ~0.2 mm
            // dimples), gentle tilt so it reads as grain, not hammering.
            Material plaque = Badge("Gate12R007BadgePlaque", shader, grain, mask,
                grainTilt: 0.5f, speckle: 0.22f, bevelWidth: 0.0005f, bevelTilt: 1.5f,
                edgeGain: 3f, recess: 0.55f, recessReach: 2f, faceGloss: 0f, gradientScale: 1f,
                gradientOffset: 0f, gradientStrength: 1f, tilesPerMeter: 30f, queue: 3001);
            // Relief: polished face, wider bevel, dark recess so it stands
            // off the field.
            Material emblem = Badge("Gate12R007BadgeEmblem", shader, grain, null,
                grainTilt: 0.10f, speckle: 0.05f, bevelWidth: 0.00032f, bevelTilt: 2.6f,
                edgeGain: 3.5f, recess: 0.9f, recessReach: 2f, faceGloss: 1f, gradientScale: 1f,
                gradientOffset: 0.20f, gradientStrength: 0.5f, tilesPerMeter: 30f, queue: 3002);
            // Glyphs sit 1 texel apart in the dynamic atlas (about 0.1 mm on
            // the plate), so the word's taps stay inside that: one bevel
            // width of 0.12 mm and no far recess ring.
            Material tier = Badge("Gate12R007BadgeTier", shader, grain, null,
                grainTilt: 0.10f, speckle: 0.05f, bevelWidth: 0.00012f, bevelTilt: 3.0f,
                edgeGain: 5f, recess: 0.9f, recessReach: 1f, faceGloss: 1f, gradientScale: 0f,
                gradientOffset: 0.20f, gradientStrength: 1f, tilesPerMeter: 30f, queue: 3003);
            BuildVariant(PlaquePrefabPath, PlaqueScenePath, plaque, emblem, tier, withPlaque: true);
            BuildVariant(ReliefPrefabPath, ReliefScenePath, plaque, emblem, tier, withPlaque: false);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("Premium Display Case Gate 12 R007 candidates built.");
        }

        [MenuItem("Fidgeting/Display Case/Gate 12/R007 Capture Standard Views")]
        public static void CaptureStandardViews()
        {
            BuildCandidates();
            CaptureVariant(PlaqueScenePath, PlaquePrefabPath, "a-plaque");
            CaptureVariant(ReliefScenePath, ReliefPrefabPath, "b-relief");
            AssetDatabase.Refresh();
        }

        /// <summary>
        /// Material-gate turntable: camera swings ±26° yaw with a little
        /// pitch around the badge while the R053 tilt driver gets matching
        /// gravity. Frames go to Logs/gate12-r007-turntable/&lt;variant&gt;.
        /// </summary>
        [MenuItem("Fidgeting/Display Case/Gate 12/R007 Capture Turntable Frames")]
        public static void CaptureTurntableFrames()
        {
            CaptureTurntable(PlaqueScenePath, "a-plaque");
            CaptureTurntable(ReliefScenePath, "b-relief");
        }

        public static void CaptureAll()
        {
            CaptureStandardViews();
            CaptureTurntableFrames();
        }

        private static void CaptureVariant(string scenePath, string prefabPath, string folder)
        {
            Scene scene = EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
            GameObject[] roots = scene.GetRootGameObjects();
            Camera camera = roots.SelectMany(r => r.GetComponentsInChildren<Camera>(true)).Single();
            PremiumDisplayCaseShippingPresentation presentation = roots
                .SelectMany(r => r.GetComponentsInChildren<PremiumDisplayCaseShippingPresentation>(true))
                .Single();
            MeshRenderer[] renderers = roots
                .SelectMany(r => r.GetComponentsInChildren<MeshRenderer>(true)).ToArray();
            MeshRenderer label = renderers.Single(r => r.name == "PhysicalLabel");
            presentation.SetLabel(PremiumDisplayCaseGate12R005Builder.BuildAuthoritativeReviewLabel());
            presentation.SetTimeForPreview(presentation.RevealProfile.TotalDurationSeconds);
            string output = Path.GetFullPath(Path.Combine(
                Application.dataPath, "..", EvidenceRoot, folder));
            Directory.CreateDirectory(output);

            Vector3 focus = new Vector3(0f, 0.008f, 0f);
            Shot(camera, output, "hero.png", new Vector3(0.33f, 0.185f, -0.69f), focus, 28.5f);
            Shot(camera, output, "top.png", new Vector3(0f, 0.64f, -0.05f), Vector3.zero, 31f, Vector3.forward);
            Shot(camera, output, "left-oblique.png", new Vector3(-0.36f, 0.12f, -0.64f), focus, 29f);
            Shot(camera, output, "right-oblique.png", new Vector3(0.36f, 0.12f, -0.64f), focus, 29f);
            Shot(camera, output, "low.png", new Vector3(0.27f, -0.22f, -0.64f), new Vector3(0f, 0.012f, 0f), 29f);
            Shot(camera, output, "front.png", new Vector3(0f, 0.008f, -0.78f), focus, 27f);

            Bounds plate = label.bounds;
            float aspect = 1640f / 2000f;
            float halfHeight = Mathf.Max(plate.extents.y, plate.extents.x / aspect) * 1.30f;
            float distance = halfHeight / Mathf.Tan(13f * Mathf.Deg2Rad);
            Macro(camera, output, "label-macro.png",
                plate.center + new Vector3(0.10f, 0.18f, -1f).normalized * distance, plate.center,
                1640, 2000);

            // Badge macro: the rarity block alone, square, from the same
            // upper-right key side so the bevel reads.
            Bounds badge = BadgeBounds(renderers);
            float badgeHalf = Mathf.Max(badge.extents.x, badge.extents.y) * 1.25f;
            float badgeDistance = badgeHalf / Mathf.Tan(13f * Mathf.Deg2Rad);
            Macro(camera, output, "badge-macro.png",
                badge.center + new Vector3(0.12f, 0.20f, -1f).normalized * badgeDistance, badge.center,
                1600, 1600);
            Macro(camera, output, "badge-macro-low.png",
                badge.center + new Vector3(-0.30f, -0.22f, -1f).normalized * badgeDistance, badge.center,
                1600, 1600);

            WriteReport(output, scenePath, prefabPath, presentation);
            Debug.Log($"Gate 12 R007 {folder} captured at {output}.");
        }

        private static void CaptureTurntable(string scenePath, string folder)
        {
            const int frameCount = 120;
            const float seconds = 4f;
            Scene scene = EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
            GameObject[] roots = scene.GetRootGameObjects();
            Camera camera = roots.SelectMany(r => r.GetComponentsInChildren<Camera>(true)).Single();
            PremiumDisplayCaseShippingPresentation presentation = roots
                .SelectMany(r => r.GetComponentsInChildren<PremiumDisplayCaseShippingPresentation>(true))
                .Single();
            MeshRenderer[] renderers = roots
                .SelectMany(r => r.GetComponentsInChildren<MeshRenderer>(true)).ToArray();
            PremiumDisplayCaseLabelFoil tilt = presentation.GetComponent<PremiumDisplayCaseLabelFoil>();
            presentation.SetLabel(PremiumDisplayCaseGate12R005Builder.BuildAuthoritativeReviewLabel());
            presentation.SetTimeForPreview(presentation.RevealProfile.TotalDurationSeconds);
            string output = Path.GetFullPath(Path.Combine(
                Application.dataPath, "..", "Logs", "gate12-r007-turntable", folder));
            if (Directory.Exists(output))
            {
                Directory.Delete(output, true);
            }
            Directory.CreateDirectory(output);

            // Frame the whole label so the badge is seen against the plate.
            Bounds plate = renderers.Single(r => r.name == "PhysicalLabel").bounds;
            const float aspect = 1400f / 1000f;
            float halfHeight = Mathf.Max(plate.extents.y, plate.extents.x / aspect) * 1.18f;
            float distance = halfHeight / Mathf.Tan(13f * Mathf.Deg2Rad);
            Vector3 lookAt = plate.center;
            float delta = seconds / frameCount;
            for (int frame = 0; frame < frameCount; frame++)
            {
                float t = (float)frame / frameCount;
                float yaw = Mathf.Sin(t * Mathf.PI * 2f) * 26f;
                float pitch = 10f + Mathf.Sin(t * Mathf.PI * 4f) * 6f;
                Quaternion orbit = Quaternion.Euler(pitch, yaw, 0f);
                Vector3 position = lookAt + orbit * new Vector3(0f, 0f, -distance);
                if (tilt != null)
                {
                    tilt.Step(delta, true, new Vector3(
                        Mathf.Sin(yaw * Mathf.Deg2Rad),
                        -Mathf.Cos(pitch * Mathf.Deg2Rad),
                        0f));
                }
                PremiumDisplayCaseGate12R005Builder.Capture(
                    camera, output, $"frame-{frame:D3}.png", position, lookAt, Vector3.up, 26f, 1400, 1000);
            }
            Debug.Log($"Gate 12 R007 {folder} turntable frames captured at {output}.");
        }

        private static Bounds BadgeBounds(MeshRenderer[] renderers)
        {
            MeshRenderer plaque = renderers.FirstOrDefault(r => r.name == PlaqueName);
            if (plaque != null)
            {
                return plaque.bounds;
            }
            Bounds bounds = renderers.Single(r => r.name == "RarityEmblem").bounds;
            bounds.Encapsulate(renderers.Single(r => r.name == "AuthoritativeRarityLevel").bounds);
            // Match the plaque footprint so A and B macros frame alike.
            float half = PlaqueSizeMm * 0.5f * 0.001f;
            bounds.Encapsulate(bounds.center + new Vector3(half, half, 0f));
            bounds.Encapsulate(bounds.center + new Vector3(-half, -half, 0f));
            return bounds;
        }

        private static void Shot(
            Camera camera, string output, string file, Vector3 from, Vector3 at, float fov)
        {
            Shot(camera, output, file, from, at, fov, Vector3.up);
        }

        private static void Shot(
            Camera camera, string output, string file, Vector3 from, Vector3 at, float fov, Vector3 up)
        {
            PremiumDisplayCaseGate12R005Builder.Capture(camera, output, file, from, at, up, fov, 820, 1000);
        }

        private static void Macro(
            Camera camera, string output, string file, Vector3 from, Vector3 at, int width, int height)
        {
            PremiumDisplayCaseGate12R005Builder.Capture(
                camera, output, file, from, at, Vector3.up, 26f, width, height);
        }

        private static void EnsureDirectories()
        {
            string project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            foreach (string path in new[]
                     {
                         "Assets/Resources/Gacha/PremiumDisplayCaseGate12R007",
                         "Assets/Resources/Gacha/PremiumDisplayCaseGate12R007Relief",
                         MaterialRoot, TextureRoot, EvidenceRoot
                     })
            {
                Directory.CreateDirectory(Path.Combine(project, path));
            }
            AssetDatabase.Refresh();
        }

        private static void BuildVariant(
            string prefabPath, string scenePath,
            Material plaqueMaterial, Material emblemMaterial, Material tierMaterial,
            bool withPlaque)
        {
            GameObject r006 = AssetDatabase.LoadAssetAtPath<GameObject>(
                PremiumDisplayCaseGate12R006Builder.FlockingPrefabPath);
            GameObject root = PrefabUtility.InstantiatePrefab(r006) as GameObject;
            try
            {
                root.name = "PresentationRoot";
                root.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
                Transform[] transforms = root.GetComponentsInChildren<Transform>(true);
                Transform label = transforms.Single(t => t.name == "PhysicalLabel");
                Transform emblem = transforms.Single(t => t.name == "RarityEmblem");
                TextMesh tier = root.GetComponentsInChildren<TextMesh>(true)
                    .Single(t => t.name == "AuthoritativeRarityLevel");
                PremiumDisplayCaseLabelPlate plate = label.GetComponent<PremiumDisplayCaseLabelPlate>();

                // Relief layout inside a 40 mm square block: emblem above,
                // tier word below, both centred on the block axis.
                emblem.localPosition = new Vector3(RightBlockX, EmblemFront, EmblemZMm * Mm);
                emblem.localScale = new Vector3(EmblemSizeMm * Mm, EmblemSizeMm * Mm, 1f);
                emblem.GetComponent<MeshRenderer>().sharedMaterial = emblemMaterial;

                Vector3 tierPosition = tier.transform.localPosition;
                tier.transform.localPosition = new Vector3(RightBlockX, tierPosition.y, TierZMm * Mm);
                // Struck lettering needs stroke width for its bevel; the plate
                // still shrinks any word wider than TierMaxWidth (38 mm).
                tier.characterSize = TierCharacterSize;
                MeshRenderer tierRenderer = tier.GetComponent<MeshRenderer>();
                tierRenderer.sharedMaterial = tierMaterial;
                plate.AddFoilRenderer(tierRenderer);

                Transform existing = label.Find(PlaqueName);
                if (existing != null)
                {
                    Object.DestroyImmediate(existing.gameObject);
                }
                if (withPlaque)
                {
                    float size = (PlaqueSizeMm + PlaqueMarginMm * 2f) * Mm;
                    MeshRenderer plaque = PremiumDisplayCaseGate12R005Builder.Quad(label, PlaqueName,
                        new Vector3(RightBlockX, PlaqueFront, 0f),
                        new Vector3(size, size, 1f), plaqueMaterial);
                    plate.AddFoilRenderer(plaque);
                }
                PrefabUtility.SaveAsPrefabAsset(root, prefabPath);
            }
            finally
            {
                Object.DestroyImmediate(root);
            }
            BuildScene(prefabPath, scenePath);
        }

        private static Material Badge(
            string name, Shader shader, Texture2D grain, Texture2D mask,
            float grainTilt, float speckle, float bevelWidth, float bevelTilt,
            float edgeGain, float recess, float recessReach, float faceGloss, float gradientScale,
            float gradientOffset, float gradientStrength, float tilesPerMeter, int queue)
        {
            string path = MaterialRoot + "/" + name + ".mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader) { name = name };
                AssetDatabase.CreateAsset(material, path);
            }
            material.shader = shader;
            material.SetTexture("_MainTex", mask);
            material.SetTexture("_GrainTex", grain);
            material.SetColor("_FoilColor", new Color(0.96f, 0.78f, 0.38f, 1f));
            material.SetFloat("_GrainTilesPerMeter", tilesPerMeter);
            material.SetFloat("_GrainStrength", grainTilt);
            material.SetFloat("_SpeckleStrength", speckle);
            material.SetFloat("_BevelWidth", bevelWidth);
            material.SetFloat("_BevelHeight", bevelTilt);
            material.SetFloat("_EdgeGain", edgeGain);
            material.SetFloat("_EdgeDarken", recess);
            material.SetFloat("_RecessReach", recessReach);
            material.SetFloat("_FaceGloss", faceGloss);
            material.SetFloat("_GradientScale", gradientScale);
            material.SetFloat("_GradientOffset", gradientOffset);
            material.SetFloat("_GradientStrength", gradientStrength);
            material.SetFloat("_Cutoff", 0.5f);
            material.renderQueue = queue;
            EditorUtility.SetDirty(material);
            return material;
        }

        /// <summary>
        /// Tileable bead-blast grain: white noise blurred with wrap into
        /// ~3-texel dimples, then differentiated into a tilt map (RG) with a
        /// separate speckle channel (B). 512 texels per 62.5 mm tile gives
        /// 0.12 mm grains, about what glass-bead blasting leaves on brass.
        /// </summary>
        private static Texture2D BuildGrainTexture()
        {
            const int size = 512;
            var random = new System.Random(0x2707);
            float[] height = new float[size * size];
            float[] speckle = new float[size * size];
            for (int i = 0; i < height.Length; i++)
            {
                height[i] = (float)random.NextDouble();
                speckle[i] = (float)random.NextDouble();
            }
            height = BlurWrap(BlurWrap(height, size), size);
            speckle = BlurWrap(speckle, size);

            var pixels = new Color32[size * size];
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    float hl = height[y * size + (x + size - 1) % size];
                    float hr = height[y * size + (x + 1) % size];
                    float hd = height[((y + size - 1) % size) * size + x];
                    float hu = height[((y + 1) % size) * size + x];
                    // Blur leaves a ±0.08 range; scale so a dimple wall tilts ~30°.
                    float tx = Mathf.Clamp((hr - hl) * 6f, -1f, 1f);
                    float ty = Mathf.Clamp((hu - hd) * 6f, -1f, 1f);
                    float s = Mathf.Clamp01(0.5f + (speckle[y * size + x] - 0.5f) * 2.4f);
                    pixels[y * size + x] = new Color32(
                        (byte)Mathf.RoundToInt((tx * 0.5f + 0.5f) * 255f),
                        (byte)Mathf.RoundToInt((ty * 0.5f + 0.5f) * 255f),
                        (byte)Mathf.RoundToInt(s * 255f),
                        255);
                }
            }
            return SaveTexture(TextureRoot + "/Gate12R007SandblastGrain.png", size, size, pixels,
                srgb: false, wrap: TextureWrapMode.Repeat, alphaIsTransparency: false);
        }

        private static float[] BlurWrap(float[] source, int size)
        {
            var result = new float[source.Length];
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    float sum = 0f;
                    for (int dy = -1; dy <= 1; dy++)
                    {
                        int sy = (y + dy + size) % size;
                        for (int dx = -1; dx <= 1; dx++)
                        {
                            sum += source[sy * size + (x + dx + size) % size];
                        }
                    }
                    result[y * size + x] = sum / 9f;
                }
            }
            return result;
        }

        /// <summary>Rounded-square relief mask with a clear margin for the recess.</summary>
        private static Texture2D BuildPlaqueMask()
        {
            const float pixelsPerMm = 12f;
            int size = Mathf.RoundToInt((PlaqueSizeMm + PlaqueMarginMm * 2f) * pixelsPerMm);
            float half = PlaqueSizeMm * 0.5f * pixelsPerMm;
            float radius = PlaqueCornerMm * pixelsPerMm;
            var pixels = new Color32[size * size];
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    float px = x + 0.5f - size * 0.5f;
                    float py = y + 0.5f - size * 0.5f;
                    float qx = Mathf.Abs(px) - (half - radius);
                    float qy = Mathf.Abs(py) - (half - radius);
                    float outside = new Vector2(Mathf.Max(qx, 0f), Mathf.Max(qy, 0f)).magnitude;
                    float inside = Mathf.Min(Mathf.Max(qx, qy), 0f);
                    float distance = outside + inside - radius;
                    float alpha = Mathf.Clamp01(0.5f - distance);
                    byte a = (byte)Mathf.RoundToInt(alpha * 255f);
                    pixels[y * size + x] = new Color32(255, 255, 255, a);
                }
            }
            return SaveTexture(TextureRoot + "/Gate12R007PlaqueMask.png", size, size, pixels,
                srgb: true, wrap: TextureWrapMode.Clamp, alphaIsTransparency: true);
        }

        private static Texture2D SaveTexture(
            string assetPath, int width, int height, Color32[] pixels,
            bool srgb, TextureWrapMode wrap, bool alphaIsTransparency)
        {
            var texture = new Texture2D(width, height, TextureFormat.RGBA32, false, !srgb);
            texture.SetPixels32(pixels);
            texture.Apply(false, false);
            File.WriteAllBytes(
                Path.GetFullPath(Path.Combine(Application.dataPath, "..", assetPath)),
                texture.EncodeToPNG());
            Object.DestroyImmediate(texture);
            AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceUpdate);
            var importer = (TextureImporter)AssetImporter.GetAtPath(assetPath);
            importer.sRGBTexture = srgb;
            importer.alphaIsTransparency = alphaIsTransparency;
            importer.mipmapEnabled = true;
            importer.wrapMode = wrap;
            importer.filterMode = FilterMode.Trilinear;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(assetPath);
        }

        private static void BuildScene(string prefabPath, string scenePath)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
            PremiumDisplayCaseShippingPresentation presentation =
                (PrefabUtility.InstantiatePrefab(prefab) as GameObject)
                    .GetComponent<PremiumDisplayCaseShippingPresentation>();
            presentation.transform.position = Vector3.zero;
            presentation.SetLabel(PremiumDisplayCaseGate12R005Builder.BuildAuthoritativeReviewLabel());
            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            prize.name = "AuthoritativeThreeBladePrize";
            presentation.AttachContent(prize.transform, PremiumDisplayCaseShippingFactory.ThreeBladeContentEuler);
            presentation.SetTimeForPreview(presentation.RevealProfile.TotalDurationSeconds);

            PremiumDisplayCaseGate12R005Builder.DirectionalLight("CaseKey", Quaternion.Euler(42f, -34f, 0f), new Color(0.96f, 0.97f, 1f), 2.10f);
            PremiumDisplayCaseGate12R005Builder.DirectionalLight("CaseFill", Quaternion.Euler(58f, 132f, 0f), new Color(0.72f, 0.80f, 0.90f), 0.92f);
            PremiumDisplayCaseGate12R005Builder.DirectionalLight("CaseRim", Quaternion.Euler(18f, 204f, 0f), new Color(0.92f, 0.95f, 1f), 1.24f);
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.28f, 0.30f, 0.34f);

            var cameraObject = new GameObject("Gate12ShippingCamera") { tag = "MainCamera" };
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.008f, 0.010f, 0.014f, 1f);
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.fieldOfView = 27f;
            camera.transform.position = new Vector3(0f, 0.008f, -0.78f);
            camera.transform.LookAt(new Vector3(0f, 0.008f, 0f));
            EditorSceneManager.SaveScene(scene, scenePath);
        }

        private static void WriteReport(
            string output, string scenePath, string prefabPath,
            PremiumDisplayCaseShippingPresentation presentation)
        {
            PremiumDisplayCaseLabelPlate plate =
                presentation.GetComponentInChildren<PremiumDisplayCaseLabelPlate>(true);
            bool atlasBound = plate != null && plate.TierWordAtlas != null;
            File.WriteAllText(
                Path.Combine(output, "shipping-capture-report.json"),
                "{\n"
                + "  \"source\":\"canonical unity/FidgetingApp\",\n"
                + $"  \"scene\":\"{scenePath}\",\n"
                + $"  \"prefab\":\"{prefabPath}\",\n"
                + "  \"basedOn\":\"" + PremiumDisplayCaseGate12R006Builder.FlockingPrefabPath + "\",\n"
                + "  \"shader\":\"" + ShaderName + "\",\n"
                + "  \"shippingFactoryPointsAtR007\":false,\n"
                + "  \"wholeAssembledCaseOnly\":true,\n"
                + "  \"toyCallerOwned\":true,\n"
                + $"  \"plateWired\":{(plate != null && plate.IsWired ? "true" : "false")},\n"
                + $"  \"plateTier\":\"{(plate != null ? plate.Tier.ToString() : "none")}\",\n"
                + $"  \"tierWordUsesFoil\":{(plate != null && plate.TierWordUsesFoil ? "true" : "false")},\n"
                + $"  \"tierWordAtlasBound\":{(atlasBound ? "true" : "false")},\n"
                + $"  \"foilRendererCount\":{(plate != null ? plate.FoilRendererCount : 0)},\n"
                + $"  \"plaqueSizeMm\":{PlaqueSizeMm.ToString("F1", CultureInfo.InvariantCulture)},\n"
                + $"  \"emblemSizeMm\":{EmblemSizeMm.ToString("F1", CultureInfo.InvariantCulture)},\n"
                + "  \"designApproved\":false,\n"
                + "  \"physicalPhoneInstalled\":false\n"
                + "}\n");
        }
    }
}
