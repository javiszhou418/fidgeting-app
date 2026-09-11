using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using FidgetingApp.Product.Gacha;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Editor
{
    /// <summary>
    /// Gate 12 R005 candidate: the approved R004 case with a bead-blast
    /// frost on the shell and rim, a holographic graphite plate laid out as
    /// left text column + right rarity block, rarity foil tiers, an inner
    /// chamber bezel line, and an embossed brand mark on the bottom rim.
    /// Built as a variant of the R004 prefab so R004 stays the rollback and
    /// the shipping factory keeps pointing at it until approval.
    /// </summary>
    public static class PremiumDisplayCaseGate12R005Builder
    {
        public const string ShippingPrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R005/PresentationRoot.prefab";
        public const string ShippingScenePath =
            "Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R005.unity";
        public const string EvidenceRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/rev-016";
        private const string GeneratedRoot = "Assets/_DisplayCase/Generated/Gate12R005";
        private const string MaterialRoot = GeneratedRoot + "/Materials";
        private const string TextureRoot = GeneratedRoot + "/Textures";
        private const string R004MaterialRoot =
            "Assets/_DisplayCase/Generated/Gate12R004/Materials";
        private const string EmblemRoot = "Assets/Plugins/iOS/GachaPacks";
        private const string FrostedShaderName = "FidgetingApp/Gate12R005MeshClippedFrosted";
        private const string FoilShaderName = "FidgetingApp/Gate12R005FoilLabel";
        private const int CaptureWidth = 820;
        private const int CaptureHeight = 1000;
        private const int MacroWidth = 1640;
        private const int MacroHeight = 2000;

        // Plate-local units: the case assembly is scaled 100, so 1 mm = 1e-5.
        private const float Mm = 0.00001f;
        private const float PlateFront = -0.000018f;
        private const float PlateTextFront = -0.000020f;
        private const float LeftColumnX = -84f * Mm;
        private const float DividerX = 40f * Mm;
        private const float RightBlockX = 63f * Mm;
        public const float LeftColumnMaxWidth = 116f * Mm;
        public const float TierMaxWidth = 38f * Mm;

        /// <summary>Rarity block emblem by foil tier: steel, copper, silver, gold.</summary>
        private static readonly string[] EmblemFilesByTier =
        {
            "gacha-pack-standard-emblem.png",
            "gacha-pack-refined-emblem.png",
            "gacha-pack-signature-emblem.png",
            "gacha-pack-grail-emblem.png"
        };

        public const string BrandMark = "F I D G E T I N G";

        [MenuItem("Fidgeting/Display Case/Gate 12/R005 Build Candidate")]
        public static void BuildCandidate()
        {
            EnsureDirectories();
            Texture2D guilloche = BuildGuillocheTexture();
            MaterialSet materials = CreateMaterials(guilloche);
            BuildPrefab(materials);
            BuildScene();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("Premium Display Case Gate 12 R005 candidate built.");
        }

        [MenuItem("Fidgeting/Display Case/Gate 12/R005 Capture Standard Views")]
        public static void CaptureStandardViews()
        {
            BuildCandidate();
            Scene scene = EditorSceneManager.OpenScene(ShippingScenePath, OpenSceneMode.Single);
            GameObject[] roots = scene.GetRootGameObjects();
            Camera camera = roots
                .SelectMany(root => root.GetComponentsInChildren<Camera>(true))
                .Single();
            PremiumDisplayCaseShippingPresentation presentation = roots
                .SelectMany(root => root
                    .GetComponentsInChildren<PremiumDisplayCaseShippingPresentation>(true))
                .Single();
            MeshRenderer label = roots
                .SelectMany(root => root.GetComponentsInChildren<MeshRenderer>(true))
                .Single(renderer => renderer.name == "PhysicalLabel");
            string output = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "..",
                EvidenceRoot));
            Directory.CreateDirectory(output);
            // Same path the shipping factory takes at spawn: SetLabel writes
            // the strings, then the plate fits them and tints the foil.
            presentation.SetLabel(BuildAuthoritativeReviewLabel());
            presentation.SetTimeForPreview(presentation.RevealProfile.TotalDurationSeconds);

            Capture(camera, output, "hero.png",
                new Vector3(0.33f, 0.185f, -0.69f), new Vector3(0f, 0.008f, 0f),
                Vector3.up, 28.5f, CaptureWidth, CaptureHeight);
            Capture(camera, output, "top.png",
                new Vector3(0f, 0.64f, -0.05f), Vector3.zero,
                Vector3.forward, 31f, CaptureWidth, CaptureHeight);
            Capture(camera, output, "left-oblique.png",
                new Vector3(-0.36f, 0.12f, -0.64f), new Vector3(0f, 0.008f, 0f),
                Vector3.up, 29f, CaptureWidth, CaptureHeight);
            Capture(camera, output, "right-oblique.png",
                new Vector3(0.36f, 0.12f, -0.64f), new Vector3(0f, 0.008f, 0f),
                Vector3.up, 29f, CaptureWidth, CaptureHeight);
            Capture(camera, output, "low.png",
                new Vector3(0.27f, -0.22f, -0.64f), new Vector3(0f, 0.012f, 0f),
                Vector3.up, 29f, CaptureWidth, CaptureHeight);
            Capture(camera, output, "front.png",
                new Vector3(0f, 0.008f, -0.78f), new Vector3(0f, 0.008f, 0f),
                Vector3.up, 27f, CaptureWidth, CaptureHeight);

            Bounds plate = label.bounds;
            float aspect = (float)MacroWidth / MacroHeight;
            float fitHalfHeight = Mathf.Max(plate.extents.y, plate.extents.x / aspect) * 1.30f;
            float distance = fitHalfHeight / Mathf.Tan(26f * 0.5f * Mathf.Deg2Rad);
            Vector3 macroDirection = new Vector3(0.10f, 0.18f, -1f).normalized;
            Capture(camera, output, "label-macro.png",
                plate.center + macroDirection * distance, plate.center,
                Vector3.up, 26f, MacroWidth, MacroHeight);
            Vector3 macroLeft = new Vector3(-0.42f, 0.12f, -1f).normalized;
            Capture(camera, output, "label-macro-left.png",
                plate.center + macroLeft * distance, plate.center,
                Vector3.up, 26f, MacroWidth, MacroHeight);

            // Bottom rim mark.
            Vector3 markCenter = new Vector3(0f, -0.147f, -0.030f);
            Capture(camera, output, "brand-mark-macro.png",
                markCenter + new Vector3(0.05f, -0.16f, -1f).normalized * 0.34f,
                markCenter, Vector3.up, 26f, MacroWidth, MacroHeight);

            WriteReport(output, presentation);
            AssetDatabase.Refresh();
            Debug.Log($"Gate 12 R005 standard views captured at {output}.");
        }

        /// <summary>
        /// Turntable for the material gate: the camera swings ±26° yaw and
        /// a little pitch while the R053 tilt driver is fed matching gravity,
        /// so the frames show both view-dependent and tilt-driven holo.
        /// Frames land in Logs/gate12-r005-turntable; ffmpeg assembles them.
        /// </summary>
        [MenuItem("Fidgeting/Display Case/Gate 12/R005 Capture Turntable Frames")]
        public static void CaptureTurntableFrames()
        {
            const int frameCount = 120;
            const float seconds = 4f;
            Scene scene = EditorSceneManager.OpenScene(ShippingScenePath, OpenSceneMode.Single);
            GameObject[] roots = scene.GetRootGameObjects();
            Camera camera = roots
                .SelectMany(root => root.GetComponentsInChildren<Camera>(true))
                .Single();
            PremiumDisplayCaseShippingPresentation presentation = roots
                .SelectMany(root => root
                    .GetComponentsInChildren<PremiumDisplayCaseShippingPresentation>(true))
                .Single();
            PremiumDisplayCaseLabelFoil tilt =
                presentation.GetComponent<PremiumDisplayCaseLabelFoil>();
            presentation.SetLabel(BuildAuthoritativeReviewLabel());
            presentation.SetTimeForPreview(presentation.RevealProfile.TotalDurationSeconds);
            string output = Path.GetFullPath(Path.Combine(
                Application.dataPath, "..", "Logs", "gate12-r005-turntable"));
            if (Directory.Exists(output))
            {
                Directory.Delete(output, true);
            }
            Directory.CreateDirectory(output);
            Vector3 lookAt = new Vector3(0f, 0.008f, 0f);
            float delta = seconds / frameCount;
            for (int frame = 0; frame < frameCount; frame++)
            {
                float t = (float)frame / frameCount;
                float yaw = Mathf.Sin(t * Mathf.PI * 2f) * 26f;
                float pitch = 12f + Mathf.Sin(t * Mathf.PI * 4f) * 5f;
                Quaternion orbit = Quaternion.Euler(pitch, yaw, 0f);
                Vector3 position = lookAt + orbit * new Vector3(0f, 0f, -0.74f);
                if (tilt != null)
                {
                    tilt.Step(delta, true, new Vector3(
                        Mathf.Sin(yaw * Mathf.Deg2Rad),
                        -Mathf.Cos(pitch * Mathf.Deg2Rad),
                        0f));
                }
                Capture(camera, output, $"frame-{frame:D3}.png",
                    position, lookAt, Vector3.up, 28.5f, CaptureWidth, CaptureHeight);
            }
            Debug.Log($"Gate 12 R005 turntable frames captured at {output}.");
        }

        private static void EnsureDirectories()
        {
            string project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            foreach (string path in new[]
                     {
                         "Assets/Resources/Gacha/PremiumDisplayCaseGate12R005",
                         MaterialRoot,
                         TextureRoot,
                         "Assets/_DisplayCase/Scenes",
                         EvidenceRoot
                     })
            {
                Directory.CreateDirectory(Path.Combine(project, path));
            }
            AssetDatabase.Refresh();
        }

        /// <summary>
        /// Print under the plate: fine 45° hairlines with a set of faint
        /// arcs centred on the rarity block, so the plate has structure the
        /// eye can hold before it reads the text.
        /// </summary>
        private static Texture2D BuildGuillocheTexture()
        {
            const int width = 1024;
            const int height = 324;
            var pixels = new Color32[width * height];
            // Rarity block centre in plate UV; UV x runs left→right,
            // v = 0 at the bottom edge of the plate.
            float arcCenterU = (RightBlockX / Mm + 92f) / 184f;
            float arcCenterV = 1f - (-9f + 29f) / 58f;
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    float u = (x + 0.5f) / width;
                    float v = (y + 0.5f) / height;
                    float diagonal = Mathf.Repeat((x + y) / 7.0f, 1f);
                    float hairline = Mathf.SmoothStep(0f, 1f, Mathf.Abs(diagonal - 0.5f) * 2f);
                    float value = 0.5f + (hairline - 0.5f) * 0.22f;
                    float du = (u - arcCenterU) * 184f;
                    float dv = (v - arcCenterV) * 58f;
                    float radiusMm = Mathf.Sqrt(du * du + dv * dv);
                    float ring = Mathf.Repeat(radiusMm / 5.5f, 1f);
                    float arc = Mathf.Exp(-Mathf.Pow((ring - 0.5f) / 0.09f, 2f));
                    float arcFade = Mathf.Clamp01(1f - (radiusMm - 14f) / 70f)
                        * Mathf.Clamp01((radiusMm - 12f) / 6f);
                    value += arc * arcFade * 0.20f;
                    // Reserve a clean field where the tier word and emblem sit.
                    float clean = Mathf.Clamp01((radiusMm - 13.5f) / 1.5f);
                    value = Mathf.Lerp(0.5f, value, clean);
                    byte gray = (byte)Mathf.RoundToInt(Mathf.Clamp01(value) * 255f);
                    pixels[y * width + x] = new Color32(gray, gray, gray, 255);
                }
            }
            var texture = new Texture2D(width, height, TextureFormat.RGBA32, false, true);
            texture.SetPixels32(pixels);
            texture.Apply(false, false);
            string assetPath = TextureRoot + "/Gate12R005LabelGuilloche.png";
            File.WriteAllBytes(
                Path.GetFullPath(Path.Combine(Application.dataPath, "..", assetPath)),
                texture.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(texture);
            AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceUpdate);
            var importer = (TextureImporter)AssetImporter.GetAtPath(assetPath);
            importer.sRGBTexture = false;
            importer.mipmapEnabled = true;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.filterMode = FilterMode.Trilinear;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(assetPath);
        }

        private static MaterialSet CreateMaterials(Texture2D guilloche)
        {
            Shader frosted = RequireShader(FrostedShaderName);
            Shader foil = RequireShader(FoilShaderName);
            return new MaterialSet(
                Frosted("Gate12R005RearFrosted", "Gate12R004RearFrosted", frosted, 3000,
                    frost: 0.22f, opacity: 0.05f, rim: 0.22f),
                Frosted("Gate12R005FrontFrosted", "Gate12R004FrontFrosted", frosted, 3020,
                    frost: 0.035f, opacity: 0.04f, rim: 0.22f),
                Frosted("Gate12R005ConnectedTube", "Gate12R004ConnectedTube", frosted, 3030,
                    frost: 0.55f, opacity: 0.06f, rim: 0.30f),
                Frosted("Gate12R005ChamberBezel", "Gate12R004ConnectedTube", frosted, 3010,
                    frost: 0.62f, opacity: 0.10f, rim: 0f),
                Plate("Gate12R005HoloPlate", foil, guilloche, metalness: 0.35f,
                    holo: 0.60f, brush: 0.9f, printStrength: 0.35f, clip: false),
                Plate("Gate12R005Foil", foil, null, metalness: 1f,
                    holo: 0.25f, brush: 1.2f, printStrength: 0f, clip: false),
                Plate("Gate12R005FoilEmblem", foil, null, metalness: 1f,
                    holo: 0.25f, brush: 1.2f, printStrength: 0f, clip: true),
                Load(R004MaterialRoot + "/Gate12R004BlackFlocking.mat"));
        }

        internal static Material Frosted(
            string name,
            string sourceName,
            Shader shader,
            int renderQueue,
            float frost,
            float opacity,
            float rim)
        {
            Material source = Load(R004MaterialRoot + "/" + sourceName + ".mat");
            Material material = Upsert(name, source);
            material.shader = shader;
            material.SetFloat("_Frost", frost);
            material.SetFloat("_Opacity", opacity);
            material.SetFloat("_RimStrength", rim);
            material.SetColor("_FrostColor", new Color(0.86f, 0.89f, 0.93f, 1f));
            material.renderQueue = renderQueue;
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Material Plate(
            string name,
            Shader shader,
            Texture2D pattern,
            float metalness,
            float holo,
            float brush,
            float printStrength,
            bool clip)
        {
            string path = MaterialRoot + "/" + name + ".mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader) { name = name };
                AssetDatabase.CreateAsset(material, path);
            }
            material.shader = shader;
            material.SetColor("_BaseColor", new Color(0.09f, 0.10f, 0.12f, 1f));
            material.SetColor("_FoilColor", new Color(0.82f, 0.84f, 0.88f, 1f));
            material.SetFloat("_Metalness", metalness);
            material.SetFloat("_HoloStrength", holo);
            material.SetFloat("_BrushStrength", brush);
            material.SetFloat("_PatternStrength", printStrength);
            material.SetFloat("_AlphaClip", clip ? 1f : 0f);
            material.SetTexture("_PatternTex", pattern);
            material.renderQueue = clip ? 2450 : 2000;
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Material Upsert(string name, Material source)
        {
            string path = MaterialRoot + "/" + name + ".mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(source) { name = name };
                AssetDatabase.CreateAsset(material, path);
            }
            else
            {
                material.CopyPropertiesFromMaterial(source);
                material.name = name;
            }
            return material;
        }

        private static void BuildPrefab(MaterialSet materials)
        {
            GameObject r004 = AssetDatabase.LoadAssetAtPath<GameObject>(
                PremiumDisplayCaseGate12Builder.ShippingPrefabPath);
            if (r004 == null)
            {
                throw new MissingReferenceException("Missing approved Gate 12 R004 prefab.");
            }
            GameObject root = PrefabUtility.InstantiatePrefab(r004) as GameObject;
            try
            {
                root.name = "PresentationRoot";
                root.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
                Transform[] transforms = root.GetComponentsInChildren<Transform>(true);
                MeshRenderer[] renderers = root.GetComponentsInChildren<MeshRenderer>(true);
                Transform caseAssembly = Find(transforms, "CaseAssembly");
                Transform physicalLabel = Find(transforms, "PhysicalLabel");

                Renderer(renderers, "RearPolycarbonateShell").sharedMaterial = materials.Rear;
                Renderer(renderers, "FrontPolycarbonateShell").sharedMaterial = materials.Front;
                Renderer(renderers, "ContinuousTubePerimeter").sharedMaterial = materials.Tube;
                Renderer(renderers, "TactileBackgroundInsert").sharedMaterial = materials.Insert;
                Renderer(renderers, "PhysicalLabel").sharedMaterial = materials.HoloPlate;

                BuildPlate(root, physicalLabel, materials);
                BuildChamberBezel(caseAssembly, materials.ChamberBezel);
                BuildBrandMark(root.transform);

                PrefabUtility.SaveAsPrefabAsset(root, ShippingPrefabPath);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        /// <summary>
        /// Left column: name / edition / acquired. Right block: emblem over
        /// tier word, foil-tinted. Collectible id stays off the plate (R053).
        /// </summary>
        private static void BuildPlate(GameObject root, Transform label, MaterialSet materials)
        {
            TextMesh[] texts = root.GetComponentsInChildren<TextMesh>(true);
            TextMesh name = Text(texts, "AuthoritativeProductName");
            TextMesh edition = Text(texts, "AuthoritativeEditionFinish");
            TextMesh acquired = Text(texts, "AuthoritativeAcquiredDate");
            TextMesh tier = Text(texts, "AuthoritativeRarityLevel");
            TextMesh id = Text(texts, "AuthoritativeCollectibleId");

            LayoutLeft(name, -13f, 0.000019f, FontStyle.Bold, new Color(0.93f, 0.91f, 0.86f, 1f));
            LayoutLeft(edition, 3f, 0.0000100f, FontStyle.Normal, new Color(0.78f, 0.79f, 0.82f, 1f));
            LayoutLeft(acquired, 15f, 0.0000088f, FontStyle.Normal, new Color(0.66f, 0.68f, 0.72f, 1f));
            tier.transform.localPosition = new Vector3(RightBlockX, PlateTextFront, 17f * Mm);
            tier.characterSize = 0.0000085f;
            tier.fontStyle = FontStyle.Bold;
            tier.anchor = TextAnchor.MiddleCenter;
            tier.alignment = TextAlignment.Center;
            id.transform.localPosition = new Vector3(LeftColumnX, PlateTextFront, 26f * Mm);
            id.characterSize = 0.0000060f;

            var foils = new List<MeshRenderer>
            {
                Line(label, "PlateFrameTop", 0f, -25.5f, 177f, 0.7f, materials.Foil),
                Line(label, "PlateFrameBottom", 0f, 25.5f, 177f, 0.7f, materials.Foil),
                Line(label, "PlateFrameLeft", -88.5f, 0f, 0.7f, 51.7f, materials.Foil),
                Line(label, "PlateFrameRight", 88.5f, 0f, 0.7f, 51.7f, materials.Foil),
                Line(label, "PlateDivider", DividerX / Mm, 0f, 0.6f, 40f, materials.Foil)
            };
            MeshRenderer emblem = Quad(label, "RarityEmblem",
                new Vector3(RightBlockX, -0.000019f, -8f * Mm),
                new Vector3(26f * Mm, 26f * Mm, 1f),
                materials.FoilEmblem);

            var emblems = new Texture2D[EmblemFilesByTier.Length];
            for (int index = 0; index < emblems.Length; index++)
            {
                emblems[index] = AssetDatabase.LoadAssetAtPath<Texture2D>(
                    EmblemRoot + "/" + EmblemFilesByTier[index]);
                if (emblems[index] == null)
                {
                    throw new MissingReferenceException(
                        "Missing pack emblem: " + EmblemFilesByTier[index]);
                }
            }

            PremiumDisplayCaseLabelPlate plate =
                label.GetComponent<PremiumDisplayCaseLabelPlate>()
                ?? label.gameObject.AddComponent<PremiumDisplayCaseLabelPlate>();
            plate.ConfigureAuthoring(
                label,
                new[] { name, edition, acquired },
                tier,
                emblem,
                foils.ToArray(),
                emblems,
                LeftColumnMaxWidth,
                TierMaxWidth);
        }

        private static void LayoutLeft(
            TextMesh text,
            float zMm,
            float characterSize,
            FontStyle style,
            Color ink)
        {
            text.transform.localPosition = new Vector3(LeftColumnX, PlateTextFront, zMm * Mm);
            text.characterSize = characterSize;
            text.fontStyle = style;
            text.anchor = TextAnchor.MiddleLeft;
            text.alignment = TextAlignment.Left;
            text.color = ink;
        }

        private static MeshRenderer Line(
            Transform label,
            string name,
            float xMm,
            float zMm,
            float lengthMm,
            float widthMm,
            Material material)
        {
            return Quad(label, name,
                new Vector3(xMm * Mm, PlateFront, zMm * Mm),
                new Vector3(lengthMm * Mm, widthMm * Mm, 1f),
                material);
        }

        internal static MeshRenderer Quad(
            Transform parent,
            string name,
            Vector3 localPosition,
            Vector3 localScale,
            Material material)
        {
            Transform existing = parent.Find(name);
            if (existing != null)
            {
                UnityEngine.Object.DestroyImmediate(existing.gameObject);
            }
            GameObject quad = GameObject.CreatePrimitive(PrimitiveType.Quad);
            quad.name = name;
            UnityEngine.Object.DestroyImmediate(quad.GetComponent<Collider>());
            quad.transform.SetParent(parent, false);
            quad.transform.localPosition = localPosition;
            // Same facing as the plate text: quad -Z becomes plate -Y (front).
            quad.transform.localRotation = Quaternion.Euler(-90f, 0f, 0f);
            quad.transform.localScale = localScale;
            var renderer = quad.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            return renderer;
        }

        /// <summary>
        /// Rounded bezel line 2 mm inside the flocking insert edge, floating
        /// 0.8 mm in front of it, so the chamber reads as a set-in tray
        /// instead of a flat dark field.
        /// </summary>
        private static void BuildChamberBezel(Transform caseAssembly, Material material)
        {
            Transform existing = caseAssembly.Find("ChamberBezel");
            if (existing != null)
            {
                UnityEngine.Object.DestroyImmediate(existing.gameObject);
            }
            var bezel = new GameObject("ChamberBezel");
            bezel.transform.position = new Vector3(0f, -0.042f, -0.0013f);
            bezel.transform.rotation = Quaternion.identity;
            bezel.transform.SetParent(caseAssembly, true);
            Mesh mesh = RoundedRectRing(0.093f, 0.103f, 0.018f, 0.0012f, 10);
            mesh.name = "ChamberBezelRing";
            bezel.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = bezel.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.sortingOrder = 10;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            AssetDatabase.CreateAsset(mesh, GeneratedRoot + "/ChamberBezelRing.asset");
        }

        /// <summary>Flat ring in the XY plane, normal -Z (toward the viewer).</summary>
        internal static Mesh RoundedRectRing(
            float halfWidth,
            float halfHeight,
            float radius,
            float lineWidth,
            int cornerSegments)
        {
            var path = new List<Vector2>();
            Vector2[] corners =
            {
                new Vector2(halfWidth - radius, halfHeight - radius),
                new Vector2(-halfWidth + radius, halfHeight - radius),
                new Vector2(-halfWidth + radius, -halfHeight + radius),
                new Vector2(halfWidth - radius, -halfHeight + radius)
            };
            for (int corner = 0; corner < 4; corner++)
            {
                float start = 90f * corner;
                for (int segment = 0; segment <= cornerSegments; segment++)
                {
                    float angle = (start + 90f * segment / cornerSegments) * Mathf.Deg2Rad;
                    path.Add(corners[corner] + new Vector2(Mathf.Cos(angle), Mathf.Sin(angle)) * radius);
                }
            }
            int count = path.Count;
            var vertices = new Vector3[count * 2];
            var normals = new Vector3[count * 2];
            var uv = new Vector2[count * 2];
            var triangles = new int[count * 6];
            for (int index = 0; index < count; index++)
            {
                Vector2 previous = path[(index - 1 + count) % count];
                Vector2 next = path[(index + 1) % count];
                Vector2 tangent = (next - previous).normalized;
                Vector2 outward = new Vector2(tangent.y, -tangent.x);
                Vector2 point = path[index];
                vertices[index * 2] = point + outward * (lineWidth * 0.5f);
                vertices[index * 2 + 1] = point - outward * (lineWidth * 0.5f);
                normals[index * 2] = Vector3.back;
                normals[index * 2 + 1] = Vector3.back;
                uv[index * 2] = new Vector2((float)index / count, 0f);
                uv[index * 2 + 1] = new Vector2((float)index / count, 1f);
                int nextIndex = (index + 1) % count;
                int t = index * 6;
                // Wound so the face points -Z.
                triangles[t] = index * 2;
                triangles[t + 1] = index * 2 + 1;
                triangles[t + 2] = nextIndex * 2;
                triangles[t + 3] = index * 2 + 1;
                triangles[t + 4] = nextIndex * 2 + 1;
                triangles[t + 5] = nextIndex * 2;
            }
            var mesh = new Mesh
            {
                vertices = vertices,
                normals = normals,
                uv = uv,
                triangles = triangles
            };
            mesh.RecalculateBounds();
            return mesh;
        }

        /// <summary>
        /// Brand mark on the bottom rim: a light face over a dark offset
        /// copy so the letters read as raised frost, not printed ink.
        /// </summary>
        private static void BuildBrandMark(Transform root)
        {
            foreach (string name in new[] { "BrandMarkShadow", "BrandMarkFace" })
            {
                Transform existing = root.Find(name);
                if (existing != null)
                {
                    UnityEngine.Object.DestroyImmediate(existing.gameObject);
                }
            }
            CreateMark(root, "BrandMarkShadow",
                new Vector3(0.00025f, -0.14735f, -0.02975f),
                new Color(0.01f, 0.015f, 0.025f, 0.70f), 48);
            CreateMark(root, "BrandMarkFace",
                new Vector3(0f, -0.1470f, -0.0300f),
                new Color(0.90f, 0.93f, 0.97f, 0.82f), 50);
        }

        internal static void CreateMark(
            Transform root,
            string name,
            Vector3 localPosition,
            Color color,
            int sortingOrder)
        {
            var mark = new GameObject(name);
            mark.transform.SetParent(root, false);
            mark.transform.localPosition = localPosition;
            mark.transform.localRotation = Quaternion.identity;
            TextMesh text = mark.AddComponent<TextMesh>();
            text.text = BrandMark;
            text.anchor = TextAnchor.MiddleCenter;
            text.alignment = TextAlignment.Center;
            text.fontSize = 64;
            text.fontStyle = FontStyle.Bold;
            // 5 mm tall letters on a 10 mm rim.
            text.characterSize = 0.00078f;
            text.color = color;
            MeshRenderer renderer = text.GetComponent<MeshRenderer>();
            renderer.sortingOrder = sortingOrder;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        }

        private static void BuildScene()
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(ShippingPrefabPath);
            PremiumDisplayCaseShippingPresentation presentation =
                (PrefabUtility.InstantiatePrefab(prefab) as GameObject)
                    .GetComponent<PremiumDisplayCaseShippingPresentation>();
            presentation.transform.position = Vector3.zero;
            presentation.SetLabel(BuildAuthoritativeReviewLabel());
            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            prize.name = "AuthoritativeThreeBladePrize";
            presentation.AttachContent(
                prize.transform,
                PremiumDisplayCaseShippingFactory.ThreeBladeContentEuler);
            presentation.SetTimeForPreview(presentation.RevealProfile.TotalDurationSeconds);

            // Lighting and camera are the approved Gate 12 R004 rig.
            DirectionalLight("CaseKey", Quaternion.Euler(42f, -34f, 0f), new Color(0.96f, 0.97f, 1f), 2.10f);
            DirectionalLight("CaseFill", Quaternion.Euler(58f, 132f, 0f), new Color(0.72f, 0.80f, 0.90f), 0.92f);
            DirectionalLight("CaseRim", Quaternion.Euler(18f, 204f, 0f), new Color(0.92f, 0.95f, 1f), 1.24f);
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
            EditorSceneManager.SaveScene(scene, ShippingScenePath);
        }

        internal static PremiumDisplayCaseLabelData BuildAuthoritativeReviewLabel()
        {
            const string prefix = "fidgeting.gacha.preview.gate12-r005-standard-views.";
            var inventory = new GachaInventoryRuntime(prefix, new GachaSplitMix64(0x120055UL));
            GachaTransactionResult transaction =
                inventory.QueryTransaction("gate12-r005-standard-view-20260909");
            if (!transaction.Success)
            {
                inventory.PrimeGate12SimulatorPreview();
                transaction = inventory.PrepareDraw(
                    GachaCatalog.LaunchSeriesId,
                    1,
                    GachaPaymentMethod.Ticket,
                    "gate12-r005-standard-view-20260909");
            }
            if (!transaction.Success || transaction.Receipt.Rows.Count != 1)
            {
                throw new InvalidOperationException(
                    "Could not create the authoritative Gate 12 R005 review receipt.");
            }
            GachaDrawReceiptRow row = transaction.Receipt.Rows[0];
            GachaPrizeDefinition prize = GachaCatalog.ResolvePrize(row.Outcome.PrizeId).Value;
            return GachaShippingLabelAuthority.Create(prize, row, 1);
        }

        internal static void Capture(
            Camera camera,
            string output,
            string fileName,
            Vector3 position,
            Vector3 lookAt,
            Vector3 up,
            float fieldOfView,
            int width,
            int height)
        {
            camera.transform.position = position;
            camera.transform.rotation = Quaternion.LookRotation(lookAt - position, up);
            camera.fieldOfView = fieldOfView;
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            var target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB);
            var image = new Texture2D(width, height, TextureFormat.RGBA32, false, false);
            try
            {
                target.Create();
                camera.targetTexture = target;
                var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest
                {
                    destination = target
                };
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                RenderTexture.active = target;
                image.ReadPixels(new Rect(0f, 0f, width, height), 0, 0);
                image.Apply(false, false);
                File.WriteAllBytes(Path.Combine(output, fileName), image.EncodeToPNG());
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

        private static void WriteReport(
            string output,
            PremiumDisplayCaseShippingPresentation presentation)
        {
            PremiumDisplayCaseLabelPlate plate =
                presentation.GetComponentInChildren<PremiumDisplayCaseLabelPlate>(true);
            File.WriteAllText(
                Path.Combine(output, "shipping-capture-report.json"),
                "{\n"
                + "  \"source\":\"canonical unity/FidgetingApp\",\n"
                + $"  \"scene\":\"{ShippingScenePath}\",\n"
                + $"  \"prefab\":\"{ShippingPrefabPath}\",\n"
                + "  \"basedOn\":\"" + PremiumDisplayCaseGate12Builder.ShippingPrefabPath + "\",\n"
                + "  \"shippingFactoryPointsAtR005\":false,\n"
                + "  \"wholeAssembledCaseOnly\":true,\n"
                + "  \"toyCallerOwned\":true,\n"
                + $"  \"plateWired\":{(plate != null && plate.IsWired ? "true" : "false")},\n"
                + $"  \"plateTier\":\"{(plate != null ? plate.Tier.ToString() : "none")}\",\n"
                + $"  \"leftColumnMaxWidthMm\":{(LeftColumnMaxWidth / Mm).ToString("F1", CultureInfo.InvariantCulture)},\n"
                + $"  \"tierMaxWidthMm\":{(TierMaxWidth / Mm).ToString("F1", CultureInfo.InvariantCulture)},\n"
                + $"  \"brandMark\":\"{BrandMark}\",\n"
                + "  \"designApproved\":false,\n"
                + "  \"physicalPhoneInstalled\":false\n"
                + "}\n");
        }

        internal static void DirectionalLight(string name, Quaternion rotation, Color color, float intensity)
        {
            var lightObject = new GameObject(name);
            lightObject.transform.rotation = rotation;
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = color;
            light.intensity = intensity;
            light.shadows = LightShadows.Soft;
        }

        internal static Material Load(string path)
        {
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                throw new MissingReferenceException("Missing material: " + path);
            }
            return material;
        }

        internal static Shader RequireShader(string name)
        {
            Shader shader = Shader.Find(name);
            if (shader == null)
            {
                throw new MissingReferenceException("Shader unavailable: " + name);
            }
            return shader;
        }

        private static Transform Find(Transform[] transforms, string name)
        {
            return transforms.Single(transform => transform.name == name);
        }

        private static MeshRenderer Renderer(MeshRenderer[] renderers, string name)
        {
            return renderers.Single(renderer => renderer.name == name);
        }

        private static TextMesh Text(TextMesh[] texts, string name)
        {
            return texts.Single(text => text.name == name);
        }

        private readonly struct MaterialSet
        {
            public MaterialSet(
                Material rear,
                Material front,
                Material tube,
                Material chamberBezel,
                Material holoPlate,
                Material foil,
                Material foilEmblem,
                Material insert)
            {
                Rear = rear;
                Front = front;
                Tube = tube;
                ChamberBezel = chamberBezel;
                HoloPlate = holoPlate;
                Foil = foil;
                FoilEmblem = foilEmblem;
                Insert = insert;
            }

            public Material Rear { get; }
            public Material Front { get; }
            public Material Tube { get; }
            public Material ChamberBezel { get; }
            public Material HoloPlate { get; }
            public Material Foil { get; }
            public Material FoilEmblem { get; }
            public Material Insert { get; }
        }
    }
}
