using System.IO;
using System.Linq;
using FidgetingApp.Product;
using FidgetingApp.Product.Gacha;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Editor
{
    /// <summary>
    /// Gate 12 R006: R005 plus the physical slab details read off a PSA
    /// case. Label sits in its own light well with a frosted bridge bar to
    /// the chamber; the rim gets an outer edge highlight and a weld seam;
    /// the chamber gets a dark gap and an inner well shadow; a frost-etched
    /// micro-mark sits in the lower corner; the plate gets a tier keyline.
    /// Two insert variants are built for A/B: black flocking (A) and an
    /// off-white printed certificate card laid on the flocking (B).
    /// </summary>
    public static class PremiumDisplayCaseGate12R006Builder
    {
        public const string FlockingPrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R006/PresentationRoot.prefab";
        public const string PaperPrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R006Paper/PresentationRoot.prefab";
        public const string FlockingScenePath =
            "Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R006.unity";
        public const string PaperScenePath =
            "Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R006Paper.unity";
        // rev-018 belongs to the parallel R007 badge round; traits land in 019.
        public const string EvidenceRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/rev-019";
        private const string GeneratedRoot = "Assets/_DisplayCase/Generated/Gate12R006";
        private const string MaterialRoot = GeneratedRoot + "/Materials";
        private const string TextureRoot = GeneratedRoot + "/Textures";
        private const string R005MaterialRoot = "Assets/_DisplayCase/Generated/Gate12R005/Materials";
        private const string ProductFontPath = "Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf";
        private const string FrostedShaderName = "FidgetingApp/Gate12R005MeshClippedFrosted";
        private const string SpriteShaderName = "Universal Render Pipeline/2D/Sprite-Unlit-Default";

        // Approved R004 world geometry (metres). Tube 228x304 front face
        // z -0.0295; front shell z -0.023..-0.017; insert 190x210 centred at
        // y -0.042, front face z -0.0005; label 184x58 centred at y 0.099.
        private const float TubeHalfWidth = 0.114f;
        private const float TubeHalfHeight = 0.152f;
        private const float TubeCornerRadius = 0.0205f;
        private const float TubeFrontZ = -0.0295f;
        private const float FrontShellFrontZ = -0.023f;
        private const float FrontShellBackZ = -0.017f;
        private const float InsertHalfWidth = 0.095f;
        private const float InsertHalfHeight = 0.105f;
        private const float InsertCenterY = -0.042f;
        private const float InsertCornerRadius = 0.020f;
        private const float InsertFrontZ = -0.0005f;
        private const float LabelCenterY = 0.099f;

        public const string CornerMark = "FIDGETING · SLAB";
        public const string CertificateBand = "CONGRATULATIONS!";
        public const string TraitHeading = "TRAIT PROFILE";

        /// <summary>The prize this preview seals, so traits match the toy inside.</summary>
        public const string PreviewPrizeId = "canyon-heir-metal-three-blade";

        // Trait block, card-relative. Rows sit between the certificate band
        // and the bottom keyline at y −0.098.
        private const float TraitHeadingY = -0.0692f;
        private const float TraitRuleY = -0.0733f;
        private const float TraitFirstRowY = -0.0790f;
        private const float TraitRowPitch = 0.0075f;
        private const float TraitLabelX = -0.080f;
        private const float TraitValueX = 0.080f;
        private const float TraitTrackLeftX = -0.050f;
        private const float TraitTrackWidth = 0.112f;
        private const float TraitTrackHeight = 0.0030f;

        private static readonly Color Ink = new Color(0.06f, 0.055f, 0.05f, 1f);
        private static readonly Color GoldInk = new Color(0.78f, 0.60f, 0.26f, 1f);

        /// <summary>Empty part of a trait bar: a light press into the stock.</summary>
        private static readonly Color TroughInk = new Color(0.62f, 0.60f, 0.55f, 1f);

        [MenuItem("Fidgeting/Display Case/Gate 12/R006 Build Candidates (A flocking, B paper)")]
        public static void BuildCandidates()
        {
            PremiumDisplayCaseGate12R005Builder.BuildCandidate();
            EnsureDirectories();
            BuildVariant(FlockingPrefabPath, FlockingScenePath, paperCard: false);
            BuildVariant(PaperPrefabPath, PaperScenePath, paperCard: true);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("Premium Display Case Gate 12 R006 candidates built.");
        }

        [MenuItem("Fidgeting/Display Case/Gate 12/R006 Capture Standard Views")]
        public static void CaptureStandardViews()
        {
            BuildCandidates();
            CaptureVariant(FlockingScenePath, "a-flocking");
            CaptureVariant(PaperScenePath, "b-paper");
            AssetDatabase.Refresh();
        }

        private static void CaptureVariant(string scenePath, string folder)
        {
            Scene scene = EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
            GameObject[] roots = scene.GetRootGameObjects();
            Camera camera = roots.SelectMany(r => r.GetComponentsInChildren<Camera>(true)).Single();
            PremiumDisplayCaseShippingPresentation presentation = roots
                .SelectMany(r => r.GetComponentsInChildren<PremiumDisplayCaseShippingPresentation>(true))
                .Single();
            MeshRenderer label = roots
                .SelectMany(r => r.GetComponentsInChildren<MeshRenderer>(true))
                .Single(r => r.name == "PhysicalLabel");
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
                plate.center + new Vector3(0.10f, 0.18f, -1f).normalized * distance, plate.center);
            // Label well, bridge bar, and the top of the chamber in one frame.
            Vector3 bridge = new Vector3(0f, 0.066f, -0.01f);
            Macro(camera, output, "bridge-macro.png",
                bridge + new Vector3(-0.30f, 0.22f, -1f).normalized * 0.26f, bridge);
            // Lower chamber: certificate band, fine print, corner mark, rim seam.
            Vector3 lower = new Vector3(0.02f, -0.118f, -0.003f);
            Macro(camera, output, "lower-chamber-macro.png",
                lower + new Vector3(0.22f, -0.18f, -1f).normalized * 0.30f, lower);
            // Whole trait block, band to bottom keyline, with room for the
            // axis words and numbers at both ends.
            Vector3 traits = new Vector3(0f, -0.122f, -0.003f);
            PremiumDisplayCaseGate12R005Builder.Capture(
                camera, output, "trait-macro.png",
                traits + new Vector3(0.10f, -0.08f, -1f).normalized * 0.45f,
                traits, Vector3.up, 26f, 1640, 1200);
            Vector3 corner = new Vector3(0.095f, -0.138f, -0.02f);
            Macro(camera, output, "corner-macro.png",
                corner + new Vector3(0.35f, -0.25f, -1f).normalized * 0.16f, corner);
            Debug.Log($"Gate 12 R006 {folder} captured at {output}.");
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

        private static void Macro(Camera camera, string output, string file, Vector3 from, Vector3 at)
        {
            PremiumDisplayCaseGate12R005Builder.Capture(
                camera, output, file, from, at, Vector3.up, 26f, 1640, 2000);
        }

        private static void EnsureDirectories()
        {
            string project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            foreach (string path in new[]
                     {
                         "Assets/Resources/Gacha/PremiumDisplayCaseGate12R006",
                         "Assets/Resources/Gacha/PremiumDisplayCaseGate12R006Paper",
                         MaterialRoot, TextureRoot, EvidenceRoot
                     })
            {
                Directory.CreateDirectory(Path.Combine(project, path));
            }
            AssetDatabase.Refresh();
        }

        private static void BuildVariant(string prefabPath, string scenePath, bool paperCard)
        {
            GameObject r005 = AssetDatabase.LoadAssetAtPath<GameObject>(
                PremiumDisplayCaseGate12R005Builder.ShippingPrefabPath);
            GameObject root = PrefabUtility.InstantiatePrefab(r005) as GameObject;
            try
            {
                root.name = "PresentationRoot";
                root.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
                Transform[] transforms = root.GetComponentsInChildren<Transform>(true);
                Transform caseAssembly = transforms.Single(t => t.name == "CaseAssembly");
                Transform label = transforms.Single(t => t.name == "PhysicalLabel");
                Shader frosted = PremiumDisplayCaseGate12R005Builder.RequireShader(FrostedShaderName);
                Shader sprite = PremiumDisplayCaseGate12R005Builder.RequireShader(SpriteShaderName);

                BuildLabelWell(caseAssembly, frosted);
                BuildRim(caseAssembly, sprite);
                BuildChamberWell(caseAssembly, sprite);
                BuildCornerMark(root.transform);
                BuildTierKeyline(label);
                if (paperCard)
                {
                    BuildCertificateCard(caseAssembly, sprite);
                }
                PrefabUtility.SaveAsPrefabAsset(root, prefabPath);
            }
            finally
            {
                Object.DestroyImmediate(root);
            }
            BuildScene(prefabPath, scenePath);
        }

        /// <summary>
        /// Light frosted floor behind the label margin and a frosted bar
        /// between label well and chamber, so the label reads as set in its
        /// own window rather than stuck on the flocking.
        /// </summary>
        private static void BuildLabelWell(Transform caseAssembly, Shader frosted)
        {
            Material floor = FrostedMaterial("Gate12R006LabelWellFloor", "Gate12R005ChamberBezel",
                frosted, frost: 0.62f, opacity: 0.42f, rim: 0f, queue: 3005,
                tint: new Color(0.80f, 0.84f, 0.89f, 1f));
            Material bar = FrostedMaterial("Gate12R006BridgeBar", "Gate12R005ConnectedTube",
                frosted, frost: 0.62f, opacity: 0.55f, rim: 0.20f, queue: 3015,
                tint: new Color(0.86f, 0.89f, 0.93f, 1f));

            WorldQuad(caseAssembly, "LabelWellFloor",
                new Vector3(0f, LabelCenterY, FrontShellBackZ + 0.0004f),
                new Vector2(0.200f, 0.070f), floor, 5);

            Transform existing = caseAssembly.Find("BridgeBar");
            if (existing != null)
            {
                Object.DestroyImmediate(existing.gameObject);
            }
            GameObject box = GameObject.CreatePrimitive(PrimitiveType.Cube);
            box.name = "BridgeBar";
            Object.DestroyImmediate(box.GetComponent<Collider>());
            box.transform.position = new Vector3(0f, 0.0665f, -0.009f);
            box.transform.rotation = Quaternion.identity;
            box.transform.localScale = new Vector3(0.204f, 0.009f, 0.015f);
            box.transform.SetParent(caseAssembly, true);
            var renderer = box.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = bar;
            renderer.sortingOrder = 12;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        }

        /// <summary>Outer edge highlight and a sonic-weld seam 4 mm in.</summary>
        private static void BuildRim(Transform caseAssembly, Shader sprite)
        {
            Material lines = SpriteMaterial("Gate12R006RimLines", sprite);
            Ring(caseAssembly, "RimEdgeHighlight", lines,
                TubeHalfWidth - 0.0005f, TubeHalfHeight - 0.0005f, TubeCornerRadius, 0.0007f,
                new Vector3(0f, 0f, TubeFrontZ - 0.0003f),
                new Color(1f, 1f, 1f, 0.55f), new Color(1f, 1f, 1f, 0.55f), 52);
            Ring(caseAssembly, "WeldSeam", lines,
                TubeHalfWidth - 0.004f, TubeHalfHeight - 0.004f, TubeCornerRadius - 0.0035f, 0.0004f,
                new Vector3(0f, 0f, TubeFrontZ - 0.0003f),
                new Color(0.04f, 0.05f, 0.07f, 0.55f), new Color(0.04f, 0.05f, 0.07f, 0.55f), 52);
        }

        /// <summary>
        /// Dark gap just outside the insert edge and a shadow that fades in
        /// from the well wall, so the chamber reads as a recessed tray.
        /// </summary>
        private static void BuildChamberWell(Transform caseAssembly, Shader sprite)
        {
            Material lines = SpriteMaterial("Gate12R006ChamberShade", sprite);
            Ring(caseAssembly, "ChamberGap", lines,
                InsertHalfWidth + 0.0015f, InsertHalfHeight + 0.0015f, InsertCornerRadius + 0.0015f, 0.003f,
                new Vector3(0f, InsertCenterY, InsertFrontZ - 0.0004f),
                new Color(0f, 0f, 0f, 0.85f), new Color(0f, 0f, 0f, 0.85f), 6);
            Ring(caseAssembly, "ChamberWellShadow", lines,
                InsertHalfWidth - 0.0035f, InsertHalfHeight - 0.0035f, InsertCornerRadius - 0.0035f, 0.007f,
                new Vector3(0f, InsertCenterY, InsertFrontZ - 0.0004f),
                new Color(0f, 0f, 0f, 0.55f), new Color(0f, 0f, 0f, 0f), 6);
        }

        /// <summary>Frost-etched micro-mark on the front shell, lower right.</summary>
        private static void BuildCornerMark(Transform root)
        {
            Transform existing = root.Find("CornerMark");
            if (existing != null)
            {
                Object.DestroyImmediate(existing.gameObject);
            }
            var mark = new GameObject("CornerMark");
            mark.transform.SetParent(root, false);
            mark.transform.localPosition = new Vector3(0.0865f, -0.1375f, FrontShellFrontZ - 0.0004f);
            TextMesh text = mark.AddComponent<TextMesh>();
            Font font = AssetDatabase.LoadAssetAtPath<Font>(ProductFontPath);
            text.font = font;
            text.text = CornerMark;
            text.fontSize = 64;
            text.fontStyle = FontStyle.Bold;
            text.anchor = TextAnchor.MiddleRight;
            text.alignment = TextAlignment.Right;
            text.characterSize = 0.00027f;
            text.richText = false;
            text.color = new Color(0.86f, 0.89f, 0.93f, 0.42f);
            MeshRenderer renderer = text.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = font.material;
            renderer.sortingOrder = 46;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        }

        /// <summary>PSA-style brand rule: one thicker line along the top edge, in tier foil.</summary>
        private static void BuildTierKeyline(Transform label)
        {
            Material foil = PremiumDisplayCaseGate12R005Builder.Load(R005MaterialRoot + "/Gate12R005Foil.mat");
            MeshRenderer keyline = PremiumDisplayCaseGate12R005Builder.Quad(label, "PlateTierKeyline",
                new Vector3(0f, -0.0000185f, -0.000236f),
                new Vector3(0.00174f, 0.000014f, 1f), foil);
            label.GetComponent<PremiumDisplayCaseLabelPlate>().AddFoilRenderer(keyline);
        }

        /// <summary>
        /// Variant B: an off-white certificate card laid on the flocking,
        /// 3 mm smaller than the insert so the black shows as a gap. Printed
        /// content is static series copy, never per-draw data (R053 keeps
        /// the collectible id off every plate).
        /// </summary>
        private static void BuildCertificateCard(Transform caseAssembly, Shader sprite)
        {
            Transform existing = caseAssembly.Find("CertificateCard");
            if (existing != null)
            {
                Object.DestroyImmediate(existing.gameObject);
            }
            var card = new GameObject("CertificateCard");
            card.transform.position = new Vector3(0f, InsertCenterY, 0f);
            card.transform.rotation = Quaternion.identity;
            card.transform.SetParent(caseAssembly, true);
            Transform parent = card.transform;

            Material paper = PaperMaterial();
            Material inkFill = UnlitMaterial("Gate12R006Ink", Ink);
            Material shadow = SpriteMaterial("Gate12R006ContactShadow", sprite);
            shadow.SetTexture("_MainTex", RadialShadowTexture());
            Font font = AssetDatabase.LoadAssetAtPath<Font>(ProductFontPath);

            const float z = InsertFrontZ - 0.0002f;
            const float print = z - 0.0001f;
            WorldQuad(parent, "Paper", new Vector3(0f, InsertCenterY, z), new Vector2(0.184f, 0.204f), paper, 0);
            // Keyline 4 mm in from the card edge, 0.6 mm wide.
            WorldQuad(parent, "KeylineTop", new Vector3(0f, InsertCenterY + 0.098f, print), new Vector2(0.176f, 0.0006f), inkFill, 1);
            WorldQuad(parent, "KeylineBottom", new Vector3(0f, InsertCenterY - 0.098f, print), new Vector2(0.176f, 0.0006f), inkFill, 1);
            WorldQuad(parent, "KeylineLeft", new Vector3(-0.088f, InsertCenterY, print), new Vector2(0.0006f, 0.1966f), inkFill, 1);
            WorldQuad(parent, "KeylineRight", new Vector3(0.088f, InsertCenterY, print), new Vector2(0.0006f, 0.1966f), inkFill, 1);

            // Card-relative y offsets (card spans ±0.102; toy spans about ±0.055).
            Print(parent, font, "SeriesStamp", "SERIES 01", new Vector3(-0.082f, 0.092f, print), 0.00046f, FontStyle.Bold, GoldInk, TextAnchor.MiddleLeft, TextAlignment.Left);
            Print(parent, font, "EditionCode", "LAUNCH", new Vector3(0.082f, 0.092f, print), 0.00046f, FontStyle.Normal, Ink, TextAnchor.MiddleRight, TextAlignment.Right);
            WorldQuad(parent, "RuleTop", new Vector3(0f, InsertCenterY + 0.084f, print), new Vector2(0.150f, 0.0003f), inkFill, 1);
            Print(parent, font, "Title", "FIDGETING COLLECTIBLE", new Vector3(0f, 0.075f, print), 0.00062f, FontStyle.Bold, Ink, TextAnchor.MiddleCenter, TextAlignment.Center);
            Print(parent, font, "Subtitle", "SEALED DISPLAY CASE", new Vector3(0f, 0.066f, print), 0.00044f, FontStyle.Normal, Ink, TextAnchor.MiddleCenter, TextAlignment.Center);
            WorldQuad(parent, "RuleMid", new Vector3(0f, InsertCenterY + 0.059f, print), new Vector2(0.110f, 0.0003f), inkFill, 1);

            WorldQuad(parent, "Band", new Vector3(0f, InsertCenterY - 0.060f, print), new Vector2(0.176f, 0.010f), inkFill, 1);
            Print(parent, font, "BandText", CertificateBand, new Vector3(0f, -0.060f, print - 0.0001f), 0.00090f, FontStyle.Bold, new Color(0.97f, 0.96f, 0.93f, 1f), TextAnchor.MiddleCenter, TextAlignment.Center);
            BuildTraitBlock(parent, font, inkFill, print);

            // Toy contact shadow: paper does not hide a floating object.
            MeshRenderer contact = WorldQuad(parent, "ToyContactShadow",
                new Vector3(0f, InsertCenterY, print - 0.0001f), new Vector2(0.130f, 0.130f), shadow, 2);
            Mesh mesh = Object.Instantiate(contact.GetComponent<MeshFilter>().sharedMesh);
            mesh.colors = Enumerable.Repeat(new Color(0f, 0f, 0f, 0.62f), mesh.vertexCount).ToArray();
            mesh.name = "ToyContactShadowQuad";
            AssetDatabase.CreateAsset(mesh, GeneratedRoot + "/ToyContactShadowQuad.asset");
            contact.GetComponent<MeshFilter>().sharedMesh = mesh;
        }

        /// <summary>
        /// Three printed trait bars where the unreadable fine print used to
        /// be. Values come from <see cref="ToyTalentCatalog"/> and are innate
        /// to the toy, so the card never prints per-draw data (R053). The
        /// filled part is tier foil and joins the plate's foil set, which
        /// keeps rarity to the narrow metallic accents `FDB-DSP-014` allows.
        /// </summary>
        private static void BuildTraitBlock(
            Transform parent, Font font, Material inkFill, float print)
        {
            Material foil = PremiumDisplayCaseGate12R005Builder.Load(
                R005MaterialRoot + "/Gate12R005Foil.mat");
            Material trough = UnlitMaterial("Gate12R006TraitTrough", TroughInk);

            ToyTalentProfile profile = ToyTalentCatalog.ResolveFromContentReference(
                GachaCatalog.ResolvePrize(PreviewPrizeId).Value.ContentReference);

            Print(parent, font, "TraitHeading", TraitHeading,
                new Vector3(TraitLabelX, TraitHeadingY, print), 0.00048f,
                FontStyle.Bold, Ink, TextAnchor.MiddleLeft, TextAlignment.Left);
            TextMesh budget = Print(parent, font, "TraitBudget", "000 / 000",
                new Vector3(TraitValueX, TraitHeadingY, print), 0.00048f,
                FontStyle.Normal, Ink, TextAnchor.MiddleRight, TextAlignment.Right);
            WorldQuad(parent, "TraitRule",
                new Vector3(0f, InsertCenterY + TraitRuleY, print),
                new Vector2(0.160f, 0.0003f), inkFill, 1);

            var fills = new Transform[ToyTalentCatalog.AxisCount];
            var values = new TextMesh[ToyTalentCatalog.AxisCount];
            for (int index = 0; index < ToyTalentCatalog.AxisCount; index++)
            {
                var axis = (ToyTalentAxis)index;
                string label = ToyTalentCatalog.Label(axis);
                float y = TraitFirstRowY - TraitRowPitch * index;
                Print(parent, font, "Trait" + label + "Label", label,
                    new Vector3(TraitLabelX, y, print), 0.00062f,
                    FontStyle.Normal, Ink, TextAnchor.MiddleLeft, TextAlignment.Left);
                values[index] = Print(parent, font, "Trait" + label + "Value", "00",
                    new Vector3(TraitValueX, y, print), 0.00068f,
                    FontStyle.Bold, Ink, TextAnchor.MiddleRight, TextAlignment.Right);

                WorldQuad(parent, "Trait" + label + "Trough",
                    new Vector3(TraitTrackLeftX + TraitTrackWidth * 0.5f, InsertCenterY + y, print),
                    new Vector2(TraitTrackWidth, TraitTrackHeight), trough, 1);
                // Quarter ticks read as a printed scale and stay visible past
                // the fill edge, so a bar can be judged without the number.
                for (int tick = 1; tick <= 3; tick++)
                {
                    WorldQuad(parent, "Trait" + label + "Tick" + tick,
                        new Vector3(
                            TraitTrackLeftX + TraitTrackWidth * 0.25f * tick,
                            InsertCenterY + y,
                            print - 0.00005f),
                        new Vector2(0.0003f, TraitTrackHeight), inkFill, 2);
                }
                // Authored at 100%; the trait block shortens it to the value.
                fills[index] = WorldQuad(parent, "Trait" + label + "Fill",
                    new Vector3(TraitTrackLeftX + TraitTrackWidth * 0.5f, InsertCenterY + y, print - 0.0001f),
                    new Vector2(TraitTrackWidth, TraitTrackHeight), foil, 3).transform;
            }

            var block = parent.gameObject.AddComponent<PremiumDisplayCaseTraitBlock>();
            block.ConfigureAuthoring(fills, values, budget);
            block.Apply(profile);

            PremiumDisplayCaseLabelPlate plate =
                parent.root.GetComponentInChildren<PremiumDisplayCaseLabelPlate>(true);
            for (int index = 0; index < fills.Length; index++)
            {
                plate.AddFoilRenderer(fills[index].GetComponent<MeshRenderer>());
            }
        }

        private static TextMesh Print(
            Transform parent, Font font, string name, string copy, Vector3 position,
            float characterSize, FontStyle style, Color ink, TextAnchor anchor, TextAlignment alignment)
        {
            var go = new GameObject(name);
            go.transform.position = new Vector3(position.x, InsertCenterY + position.y, position.z);
            go.transform.rotation = Quaternion.identity;
            go.transform.SetParent(parent, true);
            TextMesh text = go.AddComponent<TextMesh>();
            text.font = font;
            text.text = copy;
            // Render glyphs at 128 px and halve the size: sharper small print.
            text.fontSize = 128;
            text.fontStyle = style;
            text.characterSize = characterSize * 0.5f;
            text.anchor = anchor;
            text.alignment = alignment;
            text.richText = false;
            text.color = ink;
            MeshRenderer renderer = text.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = font.material;
            renderer.sortingOrder = 3;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            return text;
        }

        private static MeshRenderer WorldQuad(
            Transform parent, string name, Vector3 position, Vector2 size, Material material, int order)
        {
            Transform existing = parent.Find(name);
            if (existing != null)
            {
                Object.DestroyImmediate(existing.gameObject);
            }
            GameObject quad = GameObject.CreatePrimitive(PrimitiveType.Quad);
            quad.name = name;
            Object.DestroyImmediate(quad.GetComponent<Collider>());
            // Quad faces -Z natively, which is the viewer side of the case.
            quad.transform.position = position;
            quad.transform.rotation = Quaternion.identity;
            quad.transform.localScale = new Vector3(size.x, size.y, 1f);
            quad.transform.SetParent(parent, true);
            var renderer = quad.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.sortingOrder = order;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            return renderer;
        }

        private static void Ring(
            Transform caseAssembly, string name, Material material,
            float halfWidth, float halfHeight, float radius, float width,
            Vector3 position, Color outer, Color inner, int order)
        {
            Transform existing = caseAssembly.Find(name);
            if (existing != null)
            {
                Object.DestroyImmediate(existing.gameObject);
            }
            Mesh mesh = PremiumDisplayCaseGate12R005Builder.RoundedRectRing(halfWidth, halfHeight, radius, width, 10);
            // Even vertices are the outward edge, odd the inward edge.
            var colors = new Color[mesh.vertexCount];
            for (int i = 0; i < colors.Length; i++)
            {
                colors[i] = (i & 1) == 0 ? outer : inner;
            }
            mesh.colors = colors;
            mesh.name = name + "Ring";
            AssetDatabase.CreateAsset(mesh, GeneratedRoot + "/" + name + "Ring.asset");
            var go = new GameObject(name);
            go.transform.position = position;
            go.transform.rotation = Quaternion.identity;
            go.transform.SetParent(caseAssembly, true);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = go.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.sortingOrder = order;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            renderer.receiveShadows = false;
        }

        private static Material FrostedMaterial(
            string name, string r005Source, Shader shader,
            float frost, float opacity, float rim, int queue, Color tint)
        {
            Material source = PremiumDisplayCaseGate12R005Builder.Load(R005MaterialRoot + "/" + r005Source + ".mat");
            Material material = Upsert(name, source);
            material.shader = shader;
            material.SetFloat("_Frost", frost);
            material.SetFloat("_Opacity", opacity);
            material.SetFloat("_RimStrength", rim);
            material.SetColor("_FrostColor", tint);
            material.renderQueue = queue;
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Material SpriteMaterial(string name, Shader shader)
        {
            string path = MaterialRoot + "/" + name + ".mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader) { name = name };
                AssetDatabase.CreateAsset(material, path);
            }
            material.shader = shader;
            material.SetTexture("_MainTex", null);
            material.renderQueue = 3000;
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Material UnlitMaterial(string name, Color color)
        {
            Shader shader = PremiumDisplayCaseGate12R005Builder.RequireShader("Universal Render Pipeline/Unlit");
            string path = MaterialRoot + "/" + name + ".mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader) { name = name };
                AssetDatabase.CreateAsset(material, path);
            }
            material.shader = shader;
            material.SetColor("_BaseColor", color);
            EditorUtility.SetDirty(material);
            return material;
        }

        /// <summary>Warm off-white stock with fibre grain, lit so it takes the key light falloff.</summary>
        private static Material PaperMaterial()
        {
            Shader shader = PremiumDisplayCaseGate12R005Builder.RequireShader("Universal Render Pipeline/Lit");
            string path = MaterialRoot + "/Gate12R006CertificatePaper.mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader) { name = "Gate12R006CertificatePaper" };
                AssetDatabase.CreateAsset(material, path);
            }
            material.shader = shader;
            material.SetTexture("_BaseMap", PaperGrainTexture());
            material.SetColor("_BaseColor", new Color(0.80f, 0.77f, 0.70f, 1f));
            material.SetFloat("_Metallic", 0f);
            material.SetFloat("_Smoothness", 0.18f);
            material.SetFloat("_SpecularHighlights", 1f);
            material.SetFloat("_EnvironmentReflections", 0f);
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Texture2D PaperGrainTexture()
        {
            const int size = 512;
            var random = new System.Random(0x2606);
            var pixels = new Color32[size * size];
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    float grain = (float)random.NextDouble() - 0.5f;
                    // Fibre streaks run along the card's long axis.
                    float fibre = Mathf.PerlinNoise(x * 0.012f, y * 0.11f) - 0.5f;
                    float mottle = Mathf.PerlinNoise(x * 0.05f + 17f, y * 0.05f + 3f) - 0.5f;
                    float value = 1f + grain * 0.045f + fibre * 0.06f + mottle * 0.05f;
                    byte v = (byte)Mathf.RoundToInt(Mathf.Clamp01(value) * 255f);
                    // A touch less blue keeps it stock-white, not screen-white.
                    pixels[y * size + x] = new Color32(v, (byte)(v * 0.985f), (byte)(v * 0.955f), 255);
                }
            }
            return SaveTexture(TextureRoot + "/Gate12R006PaperGrain.png", size, size, pixels, srgb: true, wrap: TextureWrapMode.Repeat);
        }

        private static Texture2D RadialShadowTexture()
        {
            const int size = 256;
            var pixels = new Color32[size * size];
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    float dx = (x + 0.5f) / size - 0.5f;
                    float dy = (y + 0.5f) / size - 0.5f;
                    float r = Mathf.Sqrt(dx * dx + dy * dy) * 2f;
                    float alpha = Mathf.SmoothStep(1f, 0f, Mathf.Clamp01((r - 0.35f) / 0.65f));
                    pixels[y * size + x] = new Color32(255, 255, 255, (byte)Mathf.RoundToInt(alpha * 255f));
                }
            }
            return SaveTexture(TextureRoot + "/Gate12R006RadialShadow.png", size, size, pixels, srgb: false, wrap: TextureWrapMode.Clamp);
        }

        private static Texture2D SaveTexture(
            string assetPath, int width, int height, Color32[] pixels, bool srgb, TextureWrapMode wrap)
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
            importer.alphaIsTransparency = !srgb;
            importer.mipmapEnabled = true;
            importer.wrapMode = wrap;
            importer.filterMode = FilterMode.Trilinear;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(assetPath);
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
            }
            return material;
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
    }
}
