using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using FidgetingApp.Product.Gacha;

namespace FidgetingApp.DisplayCase.Editor
{
    /// <summary>
    /// Gate 12 R009: tri-spinner-slab-v3-cmf shipping candidate. Wraps the
    /// approved Gate 11 rev-004 prefab (URP zone materials, studio cubemap)
    /// with the shipping presentation contract (PresentationRoot > case
    /// assembly > PIVOT_PDC_CONTENT_SLOT > ContentFit, receipt-driven header
    /// label, reveal profile) and renders the real shipping-scene preview with
    /// the contract's beauty post (bloom / tonemap / vignette).
    /// Candidate only: PremiumDisplayCaseShippingFactory.ResourcesPath keeps
    /// pointing at R004 until the user approves this preview.
    /// </summary>
    public static class PremiumDisplayCaseGate12R009Builder
    {
        public const string ResourcesFolder = "Assets/Resources/Gacha/PremiumDisplayCaseGate12R009";
        public const string PrefabPath = ResourcesFolder + "/PresentationRoot.prefab";
        public const string ResourcesPath = "Gacha/PremiumDisplayCaseGate12R009/PresentationRoot";
        public const string VolumeProfilePath = ResourcesFolder + "/Gate12R009BeautyVolume.asset";
        public const string RuleMaterialPath = ResourcesFolder + "/M_PDC_HeaderLabelInk.mat";
        public const string ScenePath = "Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R009.unity";
        public const string ProfilePath = "Assets/Resources/Gacha/PremiumDisplayCaseGate12R004Profile.asset";
        public const string FontPath = "Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf";
        // "rev-009" is a legacy premium-display-case Gate 12 round; the V3
        // variant's stage revision 9 evidence lives under v3-rev-009.
        public const string EvidenceRelativeRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/v3-rev-009";
        public const string LabelTextMaterialPath = ResourcesFolder + "/M_PDC_HeaderLabelText.mat";
        public const string LabelTextShaderName = "FidgetingApp/DisplayCase/LabelTextDepthTested";
        public const string AppScenePath = "Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity";

        public const string RootName = "PresentationRoot";
        public const string CaseAssemblyName = "ROOT_PDC_CASE_ASSEMBLY";
        public const string ContentSlotName = "PIVOT_PDC_CONTENT_SLOT";
        public const string ContentFitName = "ContentFit";
        public const string ContentOrientName = "CONTENT_ORIENT_XZ_TO_FRONT";
        public static readonly Vector3 ContentOrientEuler = new Vector3(-90f, 0f, 0f);
        public const string HeaderPlaneName = "GEO_PDC_HEADER_GRAPHITE_PLANE";
        public const string PlaceholderDecalName = "DECAL_PDC_HEADER_LABEL";
        public const string HeaderLabelRootName = "HEADER_LABEL_RUNTIME";
        public const int ExpectedCaseMeshCount = 38;

        // Contract unity_urp.post_processing_beauty_start (rev-013).
        public const float BloomThreshold = 1.25f;      // 1.1–1.4
        public const float BloomIntensity = 0.08f;      // 0.05–0.12
        public const float BloomScatter = 0.50f;        // 0.45–0.55
        public const float BloomClamp = 10f;            // 8–12
        public const float VignetteIntensity = 0.10f;   // 0.08–0.12
        public const float VignetteSmoothness = 0.30f;  // 0.25–0.35

        // Pocket well Ø67.4 mm minus 1.0 mm clearance each side; design toy
        // thickness 14.5 mm centred on PIVOT_PDC_CONTENT_SLOT (contract
        // main.pocket_well_diameter_mm, spinner.max_thickness_mm).
        public static readonly Vector3 ContentFitAvailableSize = new Vector3(0.0654f, 0.0654f, 0.0145f);
        public const float ContentFitDepthOffsetMeters = 0f;
        public const float PocketWellDiameterMeters = 0.0674f;

        // Header label layout from evidence/10-export/rev-003/header-label-decal.json
        // (plate 81.48 x 40.43 mm, margin 6, title 7.4, series 3.6, rule y 22, spec 2.6).
        public const float LabelMarginMm = 6.0f;
        public const float TitleCapMm = 7.4f;
        public const float SeriesCapMm = 3.6f;
        public const float SpecCapMm = 2.6f;
        public const float RuleYMm = 22.0f;
        public const float RuleWidthMm = 0.18f;
        public const float LabelLiftMeters = 0.00005f;
        // Decal ink sRGB (222,226,230) dimmed to sit in the lit graphite plate
        // (TextMesh is unlit).
        public static readonly Color LabelInk = new Color(222f / 255f * 0.62f, 226f / 255f * 0.62f, 230f / 255f * 0.62f, 1f);

        public const int TurntableFrames = 72;
        public const int PhoneWidth = 1179;
        public const int PhoneHeight = 2556;
        public const float PhoneFocalLengthMm = 50f;
        public const float PhoneCaseWidthFraction = 0.60f; // GachaShippingRevealChoreography.RestCaseViewportWidthFraction

        public static string EvidenceRoot =>
            Path.GetFullPath(Path.Combine(Application.dataPath, "..", EvidenceRelativeRoot));

        [MenuItem("Fidgeting/Display Case/Gate 12/Tri-Spinner Slab R009 Build Candidate And Capture")]
        public static void BuildAndCapture()
        {
            string rejectionRecord = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "..",
                EvidenceRelativeRoot,
                "rejected-20260911T222500+0800",
                "user-rejection.md"));
            if (File.Exists(rejectionRecord))
            {
                throw new InvalidOperationException(
                    "Gate 12 R009 was rejected. Preserve its evidence and use R010 or later.");
            }
            TriSpinnerSlabGate11ParityBuilder.AssertSourceAndShippingHashes();
            EnsureDirectories();
            labelTextMaterial = null;
            var report = new Report
            {
                candidatePrefab = PrefabPath,
                candidateResourcesPath = ResourcesPath,
                shippingFactoryResourcesPath = PremiumDisplayCaseShippingFactory.ResourcesPath,
                sourceGate11Prefab = TriSpinnerSlabGate11ParityBuilder.PrefabPath,
                sourceFbxSha256 = TriSpinnerSlabGate11ParityBuilder.ApprovedFbxSha256
            };
            BuildPrefab(report);
            BuildSceneAndCapture(report);
            CaptureAppScenePreview(report);
            report.status = report.failures.Count == 0 ? "pass" : "fail";
            TriSpinnerSlabGate11ParityBuilder.WriteJson(Path.Combine(EvidenceRoot, "gate12-r009-report.json"), report);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            TriSpinnerSlabGate11ParityBuilder.AssertSourceAndShippingHashes();
            if (report.status != "pass")
            {
                throw new InvalidOperationException(
                    "Gate 12 R009 report failed: " + string.Join("; ", report.failures));
            }
            Debug.Log("Tri-Spinner Slab Gate 12 R009 candidate, scene and shipping previews complete.");
        }

        private static void EnsureDirectories()
        {
            string project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            foreach (string path in new[] { ResourcesFolder, "Assets/_DisplayCase/Scenes", EvidenceRelativeRoot, EvidenceRelativeRoot + "/turntable-frames", EvidenceRelativeRoot + "/app-turntable-frames" })
            {
                Directory.CreateDirectory(Path.Combine(project, path));
            }
            AssetDatabase.Refresh();
        }

        // ------------------------------------------------------------------
        // Prefab
        // ------------------------------------------------------------------
        public static void BuildPrefab(Report report)
        {
            GameObject source = AssetDatabase.LoadAssetAtPath<GameObject>(TriSpinnerSlabGate11ParityBuilder.PrefabPath);
            if (source == null)
            {
                throw new InvalidOperationException("Gate 11 rev-004 prefab missing: " + TriSpinnerSlabGate11ParityBuilder.PrefabPath);
            }
            GameObject root = (GameObject)PrefabUtility.InstantiatePrefab(source);
            try
            {
                PrefabUtility.UnpackPrefabInstance(root, PrefabUnpackMode.OutermostRoot, InteractionMode.AutomatedAction);
                root.name = RootName;
                root.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
                root.transform.localScale = Vector3.one;

                Transform caseAssembly = Require(root.transform, CaseAssemblyName);
                Transform contentSlot = Require(root.transform, ContentSlotName);
                Transform headerPlane = Require(root.transform, HeaderPlaneName);
                Transform decal = root.transform.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == PlaceholderDecalName);
                if (decal != null)
                {
                    // The Gate 10 decal is placeholder copy; the receipt owns the label.
                    decal.gameObject.SetActive(false);
                }

                // Toys present in their XZ plane (top = +Y); the slab's slot
                // faces -Z. The orient node carries that mapping because
                // RestoreContent resets ContentFit to identity on every attach.
                Transform orient = contentSlot.Find(ContentOrientName);
                if (orient == null)
                {
                    orient = new GameObject(ContentOrientName).transform;
                    orient.SetParent(contentSlot, false);
                }
                orient.localPosition = Vector3.zero;
                orient.localRotation = Quaternion.Euler(ContentOrientEuler);
                orient.localScale = Vector3.one;
                Transform contentFit = orient.Find(ContentFitName) ?? contentSlot.Find(ContentFitName);
                if (contentFit == null)
                {
                    contentFit = new GameObject(ContentFitName).transform;
                }
                contentFit.SetParent(orient, false);
                contentFit.localPosition = Vector3.zero;
                contentFit.localRotation = Quaternion.identity;
                contentFit.localScale = Vector3.one;

                Transform oldLabel = root.transform.Find(HeaderLabelRootName);
                if (oldLabel != null)
                {
                    UnityEngine.Object.DestroyImmediate(oldLabel.gameObject);
                }
                Labels labels = BuildHeaderLabels(root.transform, headerPlane, report);

                var presentation = root.GetComponent<PremiumDisplayCaseShippingPresentation>()
                                   ?? root.AddComponent<PremiumDisplayCaseShippingPresentation>();
                var profile = AssetDatabase.LoadAssetAtPath<PremiumDisplayCaseRevealProfile>(ProfilePath);
                if (profile == null)
                {
                    throw new InvalidOperationException("Reveal profile missing: " + ProfilePath);
                }
                presentation.ConfigureAuthoring(
                    caseAssembly, contentSlot, contentFit, Array.Empty<Renderer>(), profile,
                    labels.Title, labels.Edition, labels.Acquired, labels.Rarity, labels.CollectibleId);
                presentation.ConfigureContentFit(ContentFitAvailableSize, ContentFitDepthOffsetMeters);

                int meshCount = caseAssembly.GetComponentsInChildren<MeshFilter>(false)
                    .Count(f => f.sharedMesh != null && f.name.StartsWith("GEO_PDC_", StringComparison.Ordinal));
                report.caseMeshCount = meshCount;
                if (meshCount != ExpectedCaseMeshCount)
                {
                    report.failures.Add($"case mesh count {meshCount} != {ExpectedCaseMeshCount}");
                }
                if (root.GetComponentsInChildren<Transform>(true).Any(t =>
                        t.name.IndexOf("explode", StringComparison.OrdinalIgnoreCase) >= 0))
                {
                    report.failures.Add("explode node present in shipping candidate");
                }
                PrefabUtility.SaveAsPrefabAsset(root, PrefabPath);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        private static Transform Require(Transform root, string name)
        {
            Transform found = root.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name);
            if (found == null)
            {
                throw new InvalidOperationException($"{name} missing under {root.name}.");
            }
            return found;
        }

        private struct Labels
        {
            public TextMesh Title;
            public TextMesh Edition;
            public TextMesh Acquired;
            public TextMesh Rarity;
            public TextMesh CollectibleId;
        }

        private static Labels BuildHeaderLabels(Transform root, Transform headerPlane, Report report)
        {
            Renderer plane = headerPlane.GetComponent<Renderer>();
            Bounds bounds = plane.bounds; // root is at identity, so world == prefab space
            var labelRoot = new GameObject(HeaderLabelRootName).transform;
            labelRoot.SetParent(root, false);
            labelRoot.localPosition = Vector3.zero;
            labelRoot.localRotation = Quaternion.identity;
            labelRoot.localScale = Vector3.one;

            Font font = AssetDatabase.LoadAssetAtPath<Font>(FontPath);
            if (font == null)
            {
                report.failures.Add("Oxanium font asset missing: " + FontPath);
                font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            }
            report.labelFont = font != null ? font.name : "none";

            float plateLeft = bounds.min.x;
            float plateTop = bounds.max.y;
            float z = bounds.min.z - LabelLiftMeters;
            float leftMm = LabelMarginMm;
            report.headerPlateSizeMm = new[] { bounds.size.x * 1000f, bounds.size.y * 1000f };

            var labels = new Labels
            {
                Title = CreateLine(labelRoot, font, "LABEL_PRODUCT_NAME", plateLeft, plateTop, z, leftMm, 6.0f, TitleCapMm, FontStyle.Bold, report),
                Edition = CreateLine(labelRoot, font, "LABEL_EDITION_FINISH", plateLeft, plateTop, z, leftMm, 15.6f, SeriesCapMm, FontStyle.Normal, report),
                Acquired = CreateLine(labelRoot, font, "LABEL_ACQUIRED_DATE", plateLeft, plateTop, z, leftMm, 25.4f, SpecCapMm, FontStyle.Normal, report),
                Rarity = CreateLine(labelRoot, font, "LABEL_RARITY", plateLeft, plateTop, z, leftMm + 17.5f, 30.6f, SpecCapMm, FontStyle.Bold, report),
                CollectibleId = CreateLine(labelRoot, font, "LABEL_COLLECTIBLE_ID", plateLeft, plateTop, z, leftMm, 35.2f, SpecCapMm, FontStyle.Normal, report)
            };
            TextMesh caption = CreateLine(labelRoot, font, "LABEL_RARITY_CAPTION", plateLeft, plateTop, z, leftMm, 30.6f, SpecCapMm, FontStyle.Normal, report);
            caption.text = "RARITY";
            BuildRule(labelRoot, plateLeft, plateTop, z, bounds.size.x);
            return labels;
        }

        private static TextMesh CreateLine(
            Transform parent, Font font, string name, float plateLeft, float plateTop, float z,
            float leftMm, float capTopMm, float capHeightMm, FontStyle style, Report report)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.localRotation = Quaternion.identity;
            go.transform.localScale = Vector3.one;
            var text = go.AddComponent<TextMesh>();
            text.font = font;
            text.fontSize = 64;
            text.fontStyle = style;
            text.anchor = TextAnchor.MiddleLeft;
            text.alignment = TextAlignment.Left;
            text.richText = false;
            text.color = LabelInk;
            var renderer = go.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = font.material;
            go.AddComponent<PremiumDisplayCaseLabelTextMaterial>().Configure(LabelTextMaterial());
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            renderer.lightProbeUsage = LightProbeUsage.Off;
            renderer.reflectionProbeUsage = ReflectionProbeUsage.Off;

            float capCenterY = plateTop - (capTopMm + capHeightMm * 0.5f) * 0.001f;
            go.transform.position = new Vector3(plateLeft + leftMm * 0.001f, capCenterY, z);

            // Calibrate characterSize so a capital H is capHeightMm tall, then
            // shift so the cap centre lands on the layout line.
            text.characterSize = 1f;
            text.text = "H";
            float measured = renderer.bounds.size.y;
            if (measured > 1e-6f)
            {
                text.characterSize = capHeightMm * 0.001f / measured;
                text.text = "H";
                Bounds glyph = renderer.bounds;
                go.transform.position += new Vector3(0f, capCenterY - glyph.center.y, 0f);
                go.transform.position += new Vector3(plateLeft + leftMm * 0.001f - glyph.min.x, 0f, 0f);
                report.labelCalibration.Add($"{name}: H@1={measured * 1000f:F2} mm -> characterSize {text.characterSize:F5}, cap {renderer.bounds.size.y * 1000f:F2} mm");
            }
            else
            {
                // TextMesh did not regenerate in this editor context; analytic fallback.
                text.characterSize = capHeightMm * 0.001f / (0.07f * text.fontSize);
                report.labelCalibration.Add($"{name}: measured 0, analytic characterSize {text.characterSize:F5}");
            }
            text.text = string.Empty;
            return text;
        }

        private static Material labelTextMaterial;

        private static Material LabelTextMaterial()
        {
            if (labelTextMaterial != null)
            {
                return labelTextMaterial;
            }
            Shader shader = Shader.Find(LabelTextShaderName);
            if (shader == null)
            {
                throw new InvalidOperationException("Shader missing: " + LabelTextShaderName);
            }
            Material material = AssetDatabase.LoadAssetAtPath<Material>(LabelTextMaterialPath);
            if (material == null)
            {
                material = new Material(shader) { name = "M_PDC_HeaderLabelText" };
                AssetDatabase.CreateAsset(material, LabelTextMaterialPath);
            }
            material.shader = shader;
            material.SetColor("_Color", Color.white);
            EditorUtility.SetDirty(material);
            labelTextMaterial = material;
            return material;
        }

        private static void BuildRule(Transform parent, float plateLeft, float plateTop, float z, float plateWidth)
        {
            Material ink = AssetDatabase.LoadAssetAtPath<Material>(RuleMaterialPath);
            Shader unlit = Shader.Find("Universal Render Pipeline/Unlit");
            if (ink == null)
            {
                ink = new Material(unlit) { name = "M_PDC_HeaderLabelInk" };
                AssetDatabase.CreateAsset(ink, RuleMaterialPath);
            }
            ink.shader = unlit;
            ink.SetColor("_BaseColor", LabelInk);
            EditorUtility.SetDirty(ink);

            var rule = GameObject.CreatePrimitive(PrimitiveType.Quad);
            UnityEngine.Object.DestroyImmediate(rule.GetComponent<Collider>());
            rule.name = "LABEL_RULE";
            rule.transform.SetParent(parent, false);
            float width = plateWidth - 2f * LabelMarginMm * 0.001f;
            // Unity's Quad faces -Z, the side the plate is read from.
            rule.transform.localRotation = Quaternion.identity;
            rule.transform.localScale = new Vector3(width, RuleWidthMm * 0.001f, 1f);
            rule.transform.position = new Vector3(plateLeft + LabelMarginMm * 0.001f + width * 0.5f, plateTop - RuleYMm * 0.001f, z);
            var renderer = rule.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = ink;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
        }

        // ------------------------------------------------------------------
        // Scene + captures
        // ------------------------------------------------------------------
        private static void BuildSceneAndCapture(Report report)
        {
            string evidence = EvidenceRoot;
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
            var presentation = ((GameObject)PrefabUtility.InstantiatePrefab(prefab, scene))
                .GetComponent<PremiumDisplayCaseShippingPresentation>();
            presentation.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
            PremiumDisplayCaseLabelData label = PremiumDisplayCaseGate12R005Builder.BuildAuthoritativeReviewLabel();
            presentation.SetLabel(label);
            report.labelTexts = new[] { label.ProductName, label.EditionFinish, "ACQUIRED " + label.AcquiredDate, label.RarityLevel };

            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            prize.name = "AuthoritativeThreeBladePrize";
            presentation.AttachContent(prize.transform, PremiumDisplayCaseShippingFactory.ThreeBladeContentEuler);
            presentation.SetTimeForPreview(presentation.RevealProfile.TotalDurationSeconds);
            MeasureContentFit(presentation, prize.transform, report);

            // Gate 11 shipping rig (Gate 09 rev-004 emitters -> cubemap + 4 lights).
            TriSpinnerSlabGate11ParityBuilder.ParityReference reference = TriSpinnerSlabGate11ParityBuilder.LoadReference();
            var cubemap = AssetDatabase.LoadAssetAtPath<Cubemap>(TriSpinnerSlabGate11ParityBuilder.ShippingCubemapPath);
            if (cubemap == null)
            {
                throw new InvalidOperationException("Gate 11 shipping cubemap missing.");
            }
            Transform environment = new GameObject("Gate12ShippingEnvironment").transform;
            Camera camera = TriSpinnerSlabGate11ParityBuilder.CreateCamera(environment);
            camera.gameObject.name = "Gate12ShippingCamera";
            TriSpinnerSlabGate11ParityBuilder.ApplyRig(environment, camera, reference.shippingLights, reference.shippingWorld, cubemap, "Shipping");
            // URP: the brightest directional is the main light; every other
            // realtime light counts against additional_realtime_lights_max.
            Light[] lights = environment.GetComponentsInChildren<Light>(true);
            report.mainDirectionalLights = lights.Any(l => l.type == LightType.Directional) ? 1 : 0;
            report.additionalRealtimeLights = lights.Length - report.mainDirectionalLights;
            if (report.additionalRealtimeLights > 3)
            {
                report.failures.Add($"additional realtime lights {report.additionalRealtimeLights} > 3");
            }

            UniversalAdditionalCameraData additional = camera.GetUniversalAdditionalCameraData();
            additional.renderPostProcessing = true;
            additional.antialiasing = AntialiasingMode.None; // MSAA 4 + 2x supersample in Capture
            BuildVolume(report);
            var volumeObject = new GameObject("Gate12R009BeautyVolume");
            Volume volume = volumeObject.AddComponent<Volume>();
            volume.isGlobal = true;
            volume.sharedProfile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(VolumeProfilePath);

            // Parity frame first (validation volume disabled), then beauty.
            additional.renderPostProcessing = false;
            TriSpinnerSlabGate11ParityBuilder.SetView(camera, reference, "CAM_PDC_HERO");
            TriSpinnerSlabGate11ParityBuilder.Capture(camera, Path.Combine(evidence, "shipping-hero-post-off.png"), 2048, 1365);
            additional.renderPostProcessing = true;

            foreach (var view in new[]
                     {
                         ("CAM_PDC_HERO", "shipping-hero.png"), ("CAM_PDC_FRONT", "shipping-front.png"),
                         ("CAM_PDC_LOW_OBLIQUE", "shipping-low-oblique.png"), ("CAM_PDC_LEFT_OBLIQUE", "shipping-left-oblique.png"),
                         ("CAM_PDC_RIGHT_OBLIQUE", "shipping-right-oblique.png"), ("CAM_PDC_TOP", "shipping-top.png")
                     })
            {
                TriSpinnerSlabGate11ParityBuilder.SetView(camera, reference, view.Item1);
                bool ortho = camera.orthographic;
                TriSpinnerSlabGate11ParityBuilder.Capture(camera, Path.Combine(evidence, view.Item2), ortho ? 2048 : 2048, ortho ? 2048 : 1365);
                report.captures.Add(view.Item2);
            }

            // Macros: header label and pocket with the attached toy (85 mm, close).
            CaptureMacro(camera, evidence, "shipping-header-macro.png", new Vector3(0f, 0.0558f, 0f), new Vector3(0.10f, 0.06f, -1f), 0.26f, report);
            CaptureMacro(camera, evidence, "shipping-pocket-macro.png", new Vector3(0f, -0.0207f, -0.004f), new Vector3(0.22f, 0.10f, -1f), 0.30f, report);

            // Phone portrait framing at the choreography's rest width fraction: front and rear.
            CapturePhone(camera, presentation.transform, evidence, "phone-rest-front.png", 0f, report);
            CapturePhone(camera, presentation.transform, evidence, "phone-rest-rear.png", 180f, report);
            CapturePhone(camera, presentation.transform, evidence, "phone-rest-quarter.png", 28f, report);
            presentation.transform.rotation = Quaternion.identity;

            // Turntable: yaw the motion owner a full turn under the hero camera.
            TriSpinnerSlabGate11ParityBuilder.SetView(camera, reference, "CAM_PDC_HERO");
            string frames = Path.Combine(evidence, "turntable-frames");
            for (int frame = 0; frame < TurntableFrames; frame++)
            {
                presentation.transform.rotation = Quaternion.Euler(0f, 360f * frame / TurntableFrames, 0f);
                TriSpinnerSlabGate11ParityBuilder.Capture(camera, Path.Combine(frames, $"frame-{frame:D3}.png"), 1440, 960);
            }
            presentation.transform.rotation = Quaternion.identity;
            report.turntableFrames = TurntableFrames;

            TriSpinnerSlabGate11ParityBuilder.SetView(camera, reference, "CAM_PDC_HERO");
            EditorSceneManager.SaveScene(scene, ScenePath);
        }

        // ------------------------------------------------------------------
        // Real app scene: FidgetAppCoordinator's gacha camera pose, reveal
        // lights and GachaShippingRevealDirector rest framing, phone aspect.
        // Rig A = the lights the app creates today (R004-tuned); rig B = the
        // approved Gate 09 studio rig + contract beauty post (proposal).
        // The app scene is never saved.
        // ------------------------------------------------------------------
        private static void CaptureAppScenePreview(Report report)
        {
            string evidence = EvidenceRoot;
            Scene app = EditorSceneManager.OpenScene(AppScenePath, OpenSceneMode.Single);
            Camera camera = UnityEngine.Object.FindObjectsByType<Camera>(FindObjectsInactive.Include, FindObjectsSortMode.None)
                .FirstOrDefault(c => c.CompareTag("MainCamera"));
            if (camera == null)
            {
                throw new InvalidOperationException("App scene has no MainCamera: " + AppScenePath);
            }
            foreach (Camera other in UnityEngine.Object.FindObjectsByType<Camera>(FindObjectsSortMode.None))
            {
                if (other != camera) other.enabled = false;
            }
            // HideLibraryProductForGacha: the library product is hidden during the reveal.
            foreach (Renderer renderer in UnityEngine.Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
            {
                renderer.enabled = false;
            }
            // FidgetAppCoordinator.AcquireGachaCamera
            camera.gameObject.SetActive(true);
            camera.enabled = true;
            camera.transform.position = new Vector3(0f, 0.008f, -0.78f);
            camera.transform.rotation = Quaternion.LookRotation(new Vector3(0f, 0.008f, 0f) - camera.transform.position, Vector3.up);
            camera.orthographic = false;
            camera.usePhysicalProperties = false;
            camera.fieldOfView = 27f;
            camera.allowHDR = true;
            camera.allowMSAA = true;
            camera.aspect = (float)PhoneWidth / PhoneHeight;
            report.appCameraPostProcessing = camera.GetUniversalAdditionalCameraData().renderPostProcessing;

            var host = new GameObject("GachaShippingRevealHost");
            var presentation = ((GameObject)PrefabUtility.InstantiatePrefab(
                AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath), app)).GetComponent<PremiumDisplayCaseShippingPresentation>();
            presentation.transform.SetParent(host.transform, false);
            (GachaPrizeDefinition prizeDefinition, GachaDrawReceiptRow row) = BuildReviewReceipt();
            presentation.SetLabel(GachaShippingLabelAuthority.Create(prizeDefinition, row, 1));
            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            prize.name = "AuthoritativeThreeBladePrize";
            presentation.AttachContent(prize.transform, PremiumDisplayCaseShippingFactory.ThreeBladeContentEuler);
            presentation.SetTimeForPreview(presentation.RevealProfile.TotalDurationSeconds);
            foreach (Renderer renderer in presentation.GetComponentsInChildren<Renderer>(true))
            {
                renderer.sortingOrder = GachaRevealStageFX.CaseSortingOrder;
            }

            // Director rest framing: centre at viewport y 0.56, width 60 % of the screen.
            Vector3 restCenter = camera.ViewportToWorldPoint(new Vector3(0.5f, GachaShippingRevealChoreography.RestCenterViewportYFraction, 0.78f));
            restCenter.z = 0f;
            presentation.transform.position = restCenter;
            float widthFraction = ProjectedWidthFraction(camera, presentation.CaseAssembly);
            float scale = GachaShippingRevealChoreography.RestCaseViewportWidthFraction / Mathf.Max(widthFraction, 1e-4f);
            presentation.transform.localScale = Vector3.one * scale;
            report.appRestScaleMultiplier = scale;

            GachaRevealRarityStyle style = GachaRevealRarityStyle.For(row.Outcome.Rarity);
            var stageFX = new GachaRevealStageFX(host.transform, camera);
            stageFX.PlaceForCaseDistance(Vector3.Distance(camera.transform.position, presentation.transform.position));
            float complete = GachaShippingRevealChoreography.CompleteSeconds;
            stageFX.SetStageStrength(GachaShippingRevealChoreography.StageDim(complete));
            stageFX.SetFlash(0f, Color.white);
            stageFX.SetHalo(GachaShippingRevealChoreography.HaloOpacityAt(complete), style.Glow,
                0.10128f * scale * GachaShippingRevealChoreography.HaloRadiusCaseWidths * 0.5f, presentation.transform.position);

            // Rig A: the app's current reveal lights (FidgetAppCoordinator.CreateGachaRevealLighting).
            var rigA = new GameObject("GachaRevealLighting_Current").transform;
            rigA.SetParent(host.transform, false);
            AppDirectional(rigA, "GachaCaseKey", Quaternion.Euler(42f, -34f, 0f), new Color(0.96f, 0.97f, 1f), 2.10f);
            AppDirectional(rigA, "GachaCaseFill", Quaternion.Euler(58f, 132f, 0f), new Color(0.72f, 0.80f, 0.90f), 0.92f);
            AppDirectional(rigA, "GachaCaseRim", Quaternion.Euler(18f, 204f, 0f), new Color(0.92f, 0.95f, 1f), 1.24f);
            foreach (float yaw in new[] { 0f, 180f, 28f })
            {
                presentation.transform.rotation = Quaternion.Euler(0f, yaw, 0f);
                string file = $"app-rig-current-yaw{yaw:000}.png";
                TriSpinnerSlabGate11ParityBuilder.Capture(camera, Path.Combine(evidence, file), PhoneWidth, PhoneHeight);
                report.captures.Add(file);
            }

            // Rig B: Gate 09 studio rig (cubemap + 4 lights) + contract beauty post; scene lights muted.
            rigA.gameObject.SetActive(false);
            Light[] sceneLights = UnityEngine.Object.FindObjectsByType<Light>(FindObjectsSortMode.None);
            report.appSceneLightsMutedForRigB = sceneLights.Length;
            foreach (Light light in sceneLights)
            {
                light.enabled = false;
            }
            TriSpinnerSlabGate11ParityBuilder.ParityReference reference = TriSpinnerSlabGate11ParityBuilder.LoadReference();
            var cubemap = AssetDatabase.LoadAssetAtPath<Cubemap>(TriSpinnerSlabGate11ParityBuilder.ShippingCubemapPath);
            var environment = new GameObject("Gate09StudioRig").transform;
            environment.SetParent(host.transform, false);
            TriSpinnerSlabGate11ParityBuilder.ApplyRig(environment, camera, reference.shippingLights, reference.shippingWorld, cubemap, "Shipping");
            UniversalAdditionalCameraData additional = camera.GetUniversalAdditionalCameraData();
            bool previousPost = additional.renderPostProcessing;
            additional.renderPostProcessing = true;
            var volumeObject = new GameObject("Gate12R009BeautyVolume_Preview");
            volumeObject.transform.SetParent(host.transform, false);
            Volume volume = volumeObject.AddComponent<Volume>();
            volume.isGlobal = true;
            volume.priority = 100f;
            volume.sharedProfile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(VolumeProfilePath);
            foreach (float yaw in new[] { 0f, 180f, 28f })
            {
                presentation.transform.rotation = Quaternion.Euler(0f, yaw, 0f);
                string file = $"app-rig-gate09-yaw{yaw:000}.png";
                TriSpinnerSlabGate11ParityBuilder.Capture(camera, Path.Combine(evidence, file), PhoneWidth, PhoneHeight);
                report.captures.Add(file);
            }
            string frames = Path.Combine(evidence, "app-turntable-frames");
            for (int frame = 0; frame < AppTurntableFrames; frame++)
            {
                presentation.transform.rotation = Quaternion.Euler(0f, 360f * frame / AppTurntableFrames, 0f);
                TriSpinnerSlabGate11ParityBuilder.Capture(camera, Path.Combine(frames, $"frame-{frame:D3}.png"), PhoneWidth / 2, PhoneHeight / 2);
            }
            report.appTurntableFrames = AppTurntableFrames;
            additional.renderPostProcessing = previousPost;
            stageFX.Dispose();

            // Discard every app-scene change.
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        }

        public const int AppTurntableFrames = 48;

        private static (GachaPrizeDefinition, GachaDrawReceiptRow) BuildReviewReceipt()
        {
            const string prefix = "fidgeting.gacha.preview.gate12-r009-app-scene.";
            var inventory = new GachaInventoryRuntime(prefix, new GachaSplitMix64(0x120099UL));
            GachaTransactionResult transaction = inventory.QueryTransaction("gate12-r009-app-scene-20260911");
            if (!transaction.Success)
            {
                inventory.PrimeGate12SimulatorPreview();
                transaction = inventory.PrepareDraw(GachaCatalog.LaunchSeriesId, 1, GachaPaymentMethod.Ticket, "gate12-r009-app-scene-20260911");
            }
            if (!transaction.Success || transaction.Receipt.Rows.Count != 1)
            {
                throw new InvalidOperationException("Could not create the Gate 12 R009 review receipt.");
            }
            GachaDrawReceiptRow row = transaction.Receipt.Rows[0];
            return (GachaCatalog.ResolvePrize(row.Outcome.PrizeId).Value, row);
        }

        private static void AppDirectional(Transform parent, string name, Quaternion rotation, Color color, float intensity)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.rotation = rotation;
            Light light = go.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = color;
            light.intensity = intensity;
            light.shadows = LightShadows.Soft;
        }

        private static float ProjectedWidthFraction(Camera camera, Transform caseAssembly)
        {
            Renderer[] renderers = caseAssembly.GetComponentsInChildren<Renderer>(false);
            Bounds bounds = renderers[0].bounds;
            foreach (Renderer renderer in renderers.Skip(1))
            {
                bounds.Encapsulate(renderer.bounds);
            }
            float min = float.MaxValue, max = float.MinValue;
            for (int corner = 0; corner < 8; corner++)
            {
                Vector3 world = new Vector3(
                    (corner & 1) == 0 ? bounds.min.x : bounds.max.x,
                    (corner & 2) == 0 ? bounds.min.y : bounds.max.y,
                    (corner & 4) == 0 ? bounds.min.z : bounds.max.z);
                float x = camera.WorldToViewportPoint(world).x;
                min = Mathf.Min(min, x);
                max = Mathf.Max(max, x);
            }
            return max - min;
        }

        private static void MeasureContentFit(PremiumDisplayCaseShippingPresentation presentation, Transform prize, Report report)
        {
            Renderer[] renderers = prize.GetComponentsInChildren<Renderer>(true).Where(r => r.enabled).ToArray();
            if (renderers.Length == 0)
            {
                report.failures.Add("prize has no renderers");
                return;
            }
            Bounds bounds = renderers[0].bounds;
            foreach (Renderer renderer in renderers.Skip(1))
            {
                bounds.Encapsulate(renderer.bounds);
            }
            Transform slot = presentation.ContentSlot;
            report.contentFitAvailableMm = Scale(presentation.ContentFitAvailableSize);
            report.prizeBoundsMm = Scale(bounds.size);
            Vector3 localCenter = slot.InverseTransformPoint(bounds.center);
            report.prizeCenterOffsetFromSlotMm = Scale(localCenter);
            report.prizeFitScale = presentation.transform.GetComponentsInChildren<Transform>(true)
                .First(t => t.name == ContentFitName).localScale.x;
            float radialExtent = Mathf.Max(bounds.size.x, bounds.size.y);
            report.prizeInsidePocketWell = radialExtent <= PocketWellDiameterMeters
                && Mathf.Abs(localCenter.x) < 0.0005f
                && Mathf.Abs(localCenter.y) < 0.0005f;
            report.prizeFrontProtrusionMm = (-0.002435f - bounds.min.z) * 1000f; // beyond the frame front (z -2.435 mm)
            if (!report.prizeInsidePocketWell)
            {
                report.failures.Add($"prize {radialExtent * 1000f:F1} mm exceeds pocket well {PocketWellDiameterMeters * 1000f:F1} mm or is off-centre");
            }
            if (!presentation.ContentFitHoldsOnlyAttachedContent)
            {
                report.failures.Add("ContentFit holds more than the attached content");
            }
        }

        private static void BuildVolume(Report report)
        {
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(VolumeProfilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>();
                profile.name = "Gate12R009BeautyVolume";
                AssetDatabase.CreateAsset(profile, VolumeProfilePath);
            }
            foreach (VolumeComponent component in profile.components.ToArray())
            {
                if (component == null)
                {
                    profile.components.Remove(component);
                    continue;
                }
                profile.Remove(component.GetType());
                AssetDatabase.RemoveObjectFromAsset(component);
                UnityEngine.Object.DestroyImmediate(component, true);
            }
            Bloom bloom = profile.Add<Bloom>(true);
            bloom.threshold.Override(BloomThreshold);
            bloom.intensity.Override(BloomIntensity);
            bloom.scatter.Override(BloomScatter);
            bloom.clamp.Override(BloomClamp);
            bloom.dirtIntensity.Override(0f);
            Tonemapping tonemapping = profile.Add<Tonemapping>(true);
            tonemapping.mode.Override(TonemappingMode.Neutral);
            Vignette vignette = profile.Add<Vignette>(true);
            vignette.intensity.Override(VignetteIntensity);
            vignette.smoothness.Override(VignetteSmoothness);
            // VolumeProfile.Add only builds in-memory components; without sub-assets the
            // profile reloads with null entries and TryGet<Bloom> fails in a fresh session.
            PersistComponent(profile, bloom);
            PersistComponent(profile, tonemapping);
            PersistComponent(profile, vignette);
            EditorUtility.SetDirty(profile);
            AssetDatabase.SaveAssets();
            report.post = new PostRecord
            {
                bloomThreshold = BloomThreshold, bloomIntensity = BloomIntensity, bloomScatter = BloomScatter, bloomClamp = BloomClamp,
                vignetteIntensity = VignetteIntensity, vignetteSmoothness = VignetteSmoothness, tonemapping = "Neutral",
                chromaticAberration = 0f, filmGrain = 0f, lensDirt = 0f, softFocusRendererFeature = "not implemented (known limitation)"
            };
        }

        private static void PersistComponent(VolumeProfile profile, VolumeComponent component)
        {
            component.name = component.GetType().Name;
            component.hideFlags = HideFlags.HideInInspector | HideFlags.HideInHierarchy;
            AssetDatabase.AddObjectToAsset(component, profile);
        }

        private static void CaptureMacro(Camera camera, string evidence, string file, Vector3 target, Vector3 fromDirection, float distance, Report report)
        {
            camera.orthographic = false;
            camera.usePhysicalProperties = true;
            camera.focalLength = 85f;
            camera.sensorSize = new Vector2(36f, 24f);
            camera.gateFit = Camera.GateFitMode.Horizontal;
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.transform.position = target + fromDirection.normalized * distance;
            camera.transform.rotation = Quaternion.LookRotation(target - camera.transform.position, Vector3.up);
            TriSpinnerSlabGate11ParityBuilder.Capture(camera, Path.Combine(evidence, file), 2048, 1365);
            report.captures.Add(file);
        }

        private static void CapturePhone(Camera camera, Transform root, string evidence, string file, float yawDegrees, Report report)
        {
            root.rotation = Quaternion.Euler(0f, yawDegrees, 0f);
            camera.orthographic = false;
            camera.usePhysicalProperties = true;
            camera.focalLength = PhoneFocalLengthMm;
            camera.sensorSize = new Vector2(36f, 24f);
            camera.gateFit = Camera.GateFitMode.Horizontal;
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            float halfHorizontalFov = Mathf.Atan(18f / PhoneFocalLengthMm);
            float caseWidth = 0.10128f;
            float distance = caseWidth / (2f * PhoneCaseWidthFraction * Mathf.Tan(halfHorizontalFov));
            camera.transform.position = new Vector3(0f, 0f, -distance);
            camera.transform.rotation = Quaternion.identity;
            TriSpinnerSlabGate11ParityBuilder.Capture(camera, Path.Combine(evidence, file), PhoneWidth, PhoneHeight);
            report.captures.Add(file);
            report.phoneCameraDistanceMeters = distance;
        }

        private static float[] Scale(Vector3 value)
        {
            return new[] { value.x * 1000f, value.y * 1000f, value.z * 1000f };
        }

        [Serializable]
        public class PostRecord
        {
            public float bloomThreshold, bloomIntensity, bloomScatter, bloomClamp, vignetteIntensity, vignetteSmoothness, chromaticAberration, filmGrain, lensDirt;
            public string tonemapping;
            public string softFocusRendererFeature;
        }

        [Serializable]
        public class Report
        {
            public string status;
            public string candidatePrefab;
            public string candidateResourcesPath;
            public string shippingFactoryResourcesPath;
            public string sourceGate11Prefab;
            public string sourceFbxSha256;
            public int caseMeshCount;
            public string labelFont;
            public float[] headerPlateSizeMm;
            public List<string> labelCalibration = new List<string>();
            public string[] labelTexts;
            public float[] contentFitAvailableMm;
            public float[] prizeBoundsMm;
            public float[] prizeCenterOffsetFromSlotMm;
            public float prizeFitScale;
            public bool prizeInsidePocketWell;
            public float prizeFrontProtrusionMm;
            public int additionalRealtimeLights;
            public int mainDirectionalLights;
            public PostRecord post;
            public List<string> captures = new List<string>();
            public int turntableFrames;
            public float phoneCameraDistanceMeters;
            public bool appCameraPostProcessing;
            public float appRestScaleMultiplier;
            public int appSceneLightsMutedForRigB;
            public int appTurntableFrames;
            public List<string> failures = new List<string>();
        }
    }
}
