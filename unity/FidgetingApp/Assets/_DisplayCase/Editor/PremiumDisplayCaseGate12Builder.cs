using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using FidgetingApp.DisplayCase.MakeItShineCc0;
using FidgetingApp.Product.Gacha;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Editor
{
    public static class PremiumDisplayCaseGate12Builder
    {
        public const string CandidatePrefabPath =
            "Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001/Prefabs/PresentationRoot.prefab";
        public const string ShippingPrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R004/PresentationRoot.prefab";
        public const string ProfilePath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R004Profile.asset";
        public const string ShippingScenePath =
            "Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R004.unity";
        private const string GeneratedRoot =
            "Assets/_DisplayCase/Generated/Gate12R004";
        private const string MaterialRoot = GeneratedRoot + "/Materials";
        private const string LegacyShippingPrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCase.prefab";
        private const string LegacyShippingPrefabSha256 =
            "88cf4f4a369cae1f370e5c47cebf6d1119d2698fcd0f4de70095314c5993a811";
        private const string EvidenceRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/rev-004";
        private const int CaptureWidth = 820;
        private const int CaptureHeight = 1000;

        [MenuItem("Fidgeting/Display Case/Gate 12/Build Shipping Candidate")]
        public static void BuildShippingCandidate()
        {
            AssertLegacyShippingPrefabUnchanged();
            EnsureDirectories();
            PremiumDisplayCaseRevealProfile profile = CreateProfile();
            MaterialSet materials = CreateMaterials();
            BuildPrefab(profile, materials);
            BuildScene();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            AssertLegacyShippingPrefabUnchanged();
            Debug.Log(
                "Premium Display Case Gate 12 shipping candidate built without replacing the legacy rollback prefab.");
        }

        [MenuItem("Fidgeting/Display Case/Gate 12/Capture Standard Views")]
        public static void CaptureStandardViews()
        {
            BuildShippingCandidate();
            Scene scene = EditorSceneManager.OpenScene(
                ShippingScenePath,
                OpenSceneMode.Single);
            Camera camera = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<Camera>(true))
                .Single();
            PremiumDisplayCaseShippingPresentation presentation =
                scene.GetRootGameObjects()
                    .SelectMany(root => root.GetComponentsInChildren<
                        PremiumDisplayCaseShippingPresentation>(true))
                    .Single();
            string output = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "..",
                EvidenceRoot));
            Directory.CreateDirectory(output);

            presentation.SetTimeForPreview(
                presentation.RevealProfile.TotalDurationSeconds);
            Capture(
                camera,
                output,
                "hero.png",
                new Vector3(0.33f, 0.185f, -0.69f),
                new Vector3(0f, 0.008f, 0f),
                Vector3.up,
                28.5f);
            Capture(
                camera,
                output,
                "top.png",
                new Vector3(0f, 0.64f, -0.05f),
                Vector3.zero,
                Vector3.forward,
                31f);
            Capture(
                camera,
                output,
                "left-oblique.png",
                new Vector3(-0.36f, 0.12f, -0.64f),
                new Vector3(0f, 0.008f, 0f),
                Vector3.up,
                29f);
            Capture(
                camera,
                output,
                "right-oblique.png",
                new Vector3(0.36f, 0.12f, -0.64f),
                new Vector3(0f, 0.008f, 0f),
                Vector3.up,
                29f);
            Capture(
                camera,
                output,
                "low.png",
                new Vector3(0.27f, -0.22f, -0.64f),
                new Vector3(0f, 0.012f, 0f),
                Vector3.up,
                29f);

            float profileDuration =
                presentation.RevealProfile.TotalDurationSeconds;
            var motionSamples = new[]
            {
                ("motion-00-entry.png", 0f),
                ("motion-01-overlap.png",
                    presentation.RevealProfile.FirstSpinStartSeconds + 0.12f),
                ("motion-02-first-spin.png",
                    presentation.RevealProfile.FirstSpinStartSeconds
                        + presentation.RevealProfile.FirstSpinDurationSeconds
                        * 0.50f),
                ("motion-03-second-spin.png",
                    presentation.RevealProfile.FirstSpinEndSeconds
                        + presentation.RevealProfile.SecondSpinDurationSeconds
                        * 0.50f),
                ("motion-04-sheen.png",
                    presentation.RevealProfile.RotationEndSeconds
                        + presentation.RevealProfile.SheenDurationSeconds * 0.50f),
                ("motion-05-hold.png", profileDuration - 0.10f)
            };
            foreach ((string fileName, float time) in motionSamples)
            {
                presentation.SetTimeForPreview(time);
                Capture(
                    camera,
                    output,
                    fileName,
                    new Vector3(0f, 0.008f, -0.78f),
                    new Vector3(0f, 0.008f, 0f),
                    Vector3.up,
                    27f);
            }

            WriteCaptureReport(output, presentation, motionSamples);
            AssetDatabase.Refresh();
            Debug.Log($"Gate 12 standard views captured at {output}.");
        }

        private static void EnsureDirectories()
        {
            string project = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                ".."));
            foreach (string path in new[]
                     {
                        "Assets/Resources/Gacha/PremiumDisplayCaseGate12R004",
                         MaterialRoot,
                         "Assets/_DisplayCase/Scenes",
                         EvidenceRoot
                     })
            {
                Directory.CreateDirectory(Path.Combine(project, path));
            }
            AssetDatabase.Refresh();
        }

        private static PremiumDisplayCaseRevealProfile CreateProfile()
        {
            PremiumDisplayCaseRevealProfile profile =
                AssetDatabase.LoadAssetAtPath<
                    PremiumDisplayCaseRevealProfile>(ProfilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<
                    PremiumDisplayCaseRevealProfile>();
                AssetDatabase.CreateAsset(profile, ProfilePath);
            }
            profile.ConfigureCandidate(
                PremiumDisplayCaseRevealProfile
                    .CandidateHandoffDurationSeconds,
                PremiumDisplayCaseRevealProfile
                    .CandidateEntryDurationSeconds,
                PremiumDisplayCaseRevealProfile
                    .CandidateFirstSpinDurationSeconds,
                PremiumDisplayCaseRevealProfile
                    .CandidateSecondSpinDurationSeconds,
                PremiumDisplayCaseRevealProfile
                    .CandidateEntryRotationOverlapSeconds,
                PremiumDisplayCaseRevealProfile
                    .CandidateArrivalRimDurationSeconds,
                PremiumDisplayCaseRevealProfile
                    .CandidateSheenDurationSeconds,
                PremiumDisplayCaseRevealProfile
                    .CandidateHoldDurationSeconds,
                -0.18f,
                0.11f,
                360f,
                360f,
                PremiumDisplayCaseRevealProfile.CandidateLightRevealWidth,
                PremiumDisplayCaseRevealProfile.CandidateArrivalRimIntensity,
                PremiumDisplayCaseRevealProfile
                    .CandidateFirstRotationRimIntensity,
                PremiumDisplayCaseRevealProfile
                    .CandidateSecondRotationRimIntensity,
                PremiumDisplayCaseRevealProfile.CandidateSheenWidth,
                PremiumDisplayCaseRevealProfile.CandidateSheenIntensity,
                PremiumDisplayCaseRevealProfile.CandidateSheenFalloff,
                EaseOutCubic(),
                FastFirstSpin(),
                SlowerSecondSpin(
                    PremiumDisplayCaseRevealProfile
                        .CandidateFirstSpinDurationSeconds,
                    PremiumDisplayCaseRevealProfile
                        .CandidateSecondSpinDurationSeconds),
                MakeItShineCc0EffectCurves.CreateDiscardDissolveCurve(),
                AnimationCurve.EaseInOut(0f, 0f, 1f, 1f));
            EditorUtility.SetDirty(profile);
            return profile;
        }

        private static MaterialSet CreateMaterials()
        {
            Shader acrylic = Shader.Find(
                "FidgetingApp/Gate12R004MeshClippedFrosted");
            if (acrylic == null)
            {
                throw new MissingReferenceException(
                    "Gate12R004MeshClippedFrosted shader is unavailable.");
            }
            return new MaterialSet(
                CopyMaterial(
                    "Gate12R004RearFrosted",
                    "Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001/Materials/Gate11RearFrosted.mat",
                    acrylic,
                    3000),
                CopyMaterial(
                    "Gate12R004FrontFrosted",
                    "Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001/Materials/Gate11FrontFrosted.mat",
                    acrylic,
                    3020),
                CopyMaterial(
                    "Gate12R004ConnectedTube",
                    "Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001/Materials/Gate11ConnectedTube.mat",
                    acrylic,
                    3030),
                CopyMaterial(
                    "Gate12R004BlackFlocking",
                    "Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001/Materials/Gate11BlackFlocking.mat",
                    null,
                    -1),
                CopyMaterial(
                    "Gate12R004RuntimeLabel",
                    "Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001/Materials/Gate11RuntimeLabel.mat",
                    null,
                    -1));
        }

        private static Material CopyMaterial(
            string name,
            string sourcePath,
            Shader overrideShader,
            int renderQueue)
        {
            Material source = AssetDatabase.LoadAssetAtPath<Material>(sourcePath);
            if (source == null)
            {
                throw new MissingReferenceException(
                    $"Missing Gate 11 material: {sourcePath}");
            }
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
            if (overrideShader != null)
            {
                material.shader = overrideShader;
                material.SetColor(
                    "_RimColor",
                    new Color(0.96f, 0.94f, 0.90f, 1f));
                material.SetFloat("_Opacity", 0.04f);
                material.SetFloat("_RimStrength", 0.22f);
                material.SetFloat(
                    "_LightRevealWidth",
                    PremiumDisplayCaseRevealProfile.CandidateLightRevealWidth);
                material.SetFloat("_LightRevealStrength", 0f);
                material.SetFloat("_RotationRimProgress", 0f);
                material.SetFloat("_RotationRimStrength", 0f);
                material.SetFloat(
                    "_SheenWidth",
                    PremiumDisplayCaseRevealProfile.CandidateSheenWidth);
                material.SetFloat("_SheenStrength", 0f);
                material.SetFloat(
                    "_SheenFalloff",
                    PremiumDisplayCaseRevealProfile.CandidateSheenFalloff);
            }
            if (renderQueue >= 0)
            {
                material.renderQueue = renderQueue;
            }
            EditorUtility.SetDirty(material);
            return material;
        }

        private static void BuildPrefab(
            PremiumDisplayCaseRevealProfile profile,
            MaterialSet materials)
        {
            GameObject candidate = AssetDatabase.LoadAssetAtPath<GameObject>(
                CandidatePrefabPath);
            if (candidate == null)
            {
                throw new MissingReferenceException(
                    $"Missing approved Gate 11 prefab: {CandidatePrefabPath}");
            }
            GameObject root = PrefabUtility.InstantiatePrefab(candidate)
                as GameObject;
            if (root == null)
            {
                throw new InvalidOperationException(
                    "Could not instantiate approved Gate 11 prefab.");
            }
            try
            {
                root.name = "PresentationRoot";
                Transform[] transforms = root.GetComponentsInChildren<Transform>(true);
                Transform caseAssembly = Find(transforms, "CaseAssembly");
                Transform contentSlot = Find(transforms, "ContentSlot");
                Transform physicalLabel = Find(transforms, "PhysicalLabel");
                Transform contentFit = new GameObject("ContentFit").transform;
                contentFit.SetParent(contentSlot, false);

                MeshRenderer[] renderers =
                    root.GetComponentsInChildren<MeshRenderer>(true);
                AssignMaterial(
                    renderers,
                    "RearPolycarbonateShell",
                    materials.Rear);
                AssignMaterial(
                    renderers,
                    "TactileBackgroundInsert",
                    materials.Insert);
                AssignMaterial(
                    renderers,
                    "FrontPolycarbonateShell",
                    materials.Front);
                AssignMaterial(
                    renderers,
                    "ContinuousTubePerimeter",
                    materials.Tube);
                AssignMaterial(
                    renderers,
                    "PhysicalLabel",
                    materials.Label);

                var labels = new List<TextMesh>
                {
                    CreateLabel(
                        physicalLabel,
                        "AuthoritativeProductName",
                        new Vector3(-0.00084f, -0.000002f, -0.00019f),
                        0.000018f,
                        FontStyle.Bold,
                        new Color(0.94f, 0.91f, 0.84f, 1f)),
                    CreateLabel(
                        physicalLabel,
                        "AuthoritativeEditionFinish",
                        new Vector3(-0.00084f, -0.000002f, -0.00006f),
                        0.000010f,
                        FontStyle.Normal,
                        new Color(0.86f, 0.84f, 0.79f, 1f)),
                    CreateLabel(
                        physicalLabel,
                        "AuthoritativeAcquiredDate",
                        new Vector3(-0.00084f, -0.000002f, 0.00005f),
                        0.000009f,
                        FontStyle.Normal,
                        new Color(0.80f, 0.79f, 0.76f, 1f)),
                    CreateLabel(
                        physicalLabel,
                        "AuthoritativeRarityLevel",
                        new Vector3(-0.00084f, -0.000002f, 0.00016f),
                        0.000010f,
                        FontStyle.Bold,
                        new Color(0.92f, 0.90f, 0.85f, 1f)),
                    CreateLabel(
                        physicalLabel,
                        "AuthoritativeCollectibleId",
                        new Vector3(-0.00084f, -0.000002f, 0.00027f),
                        0.000009f,
                        FontStyle.Normal,
                        new Color(0.74f, 0.73f, 0.70f, 1f))
                };
                var presentation =
                    root.AddComponent<PremiumDisplayCaseShippingPresentation>();
                presentation.ConfigureAuthoring(
                    caseAssembly,
                    contentSlot,
                    contentFit,
                    new Renderer[]
                    {
                        FindRenderer(renderers, "RearPolycarbonateShell"),
                        FindRenderer(renderers, "FrontPolycarbonateShell"),
                        FindRenderer(renderers, "ContinuousTubePerimeter")
                    },
                    profile,
                    labels[0],
                    labels[1],
                    labels[2],
                    labels[3],
                    labels[4]);
                PrefabUtility.SaveAsPrefabAsset(root, ShippingPrefabPath);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        private static void BuildScene()
        {
            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                ShippingPrefabPath);
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
            presentation.SetTimeForPreview(
                presentation.RevealProfile.TotalDurationSeconds);

            CreateDirectionalLight(
                "CaseKey",
                Quaternion.Euler(42f, -34f, 0f),
                new Color(0.96f, 0.97f, 1f),
                2.10f);
            CreateDirectionalLight(
                "CaseFill",
                Quaternion.Euler(58f, 132f, 0f),
                new Color(0.72f, 0.80f, 0.90f),
                0.92f);
            CreateDirectionalLight(
                "CaseRim",
                Quaternion.Euler(18f, 204f, 0f),
                new Color(0.92f, 0.95f, 1f),
                1.24f);
            RenderSettings.ambientMode =
                UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.28f, 0.30f, 0.34f);

            var cameraObject = new GameObject("Gate12ShippingCamera");
            cameraObject.tag = "MainCamera";
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

        private static PremiumDisplayCaseLabelData BuildAuthoritativeReviewLabel()
        {
            const string prefix =
                "fidgeting.gacha.preview.gate12-standard-views.";
            var inventory = new GachaInventoryRuntime(
                prefix,
                new GachaSplitMix64(0x120011UL));
            GachaTransactionResult transaction =
                inventory.QueryTransaction("gate12-standard-view-20260827");
            if (!transaction.Success)
            {
                inventory.PrimeGate12SimulatorPreview();
                transaction = inventory.PrepareDraw(
                    GachaCatalog.LaunchSeriesId,
                    1,
                    GachaPaymentMethod.Ticket,
                    "gate12-standard-view-20260827");
            }
            if (!transaction.Success || transaction.Receipt.Rows.Count != 1)
            {
                throw new InvalidOperationException(
                    "Could not create the authoritative Gate 12 review receipt.");
            }
            GachaDrawReceiptRow row = transaction.Receipt.Rows[0];
            GachaPrizeDefinition prize =
                GachaCatalog.ResolvePrize(row.Outcome.PrizeId).Value;
            return GachaShippingLabelAuthority.Create(prize, row, 1);
        }

        private static TextMesh CreateLabel(
            Transform parent,
            string name,
            Vector3 localPosition,
            float characterSize,
            FontStyle style,
            Color color)
        {
            var labelObject = new GameObject(name);
            labelObject.transform.SetParent(parent, false);
            labelObject.transform.localPosition = localPosition;
            labelObject.transform.localRotation = Quaternion.Euler(-90f, 0f, 0f);
            TextMesh text = labelObject.AddComponent<TextMesh>();
            text.text = string.Empty;
            text.anchor = TextAnchor.MiddleLeft;
            text.alignment = TextAlignment.Left;
            text.characterSize = characterSize;
            text.fontSize = 64;
            text.fontStyle = style;
            text.color = color;
            MeshRenderer renderer = text.GetComponent<MeshRenderer>();
            renderer.sortingOrder = 45;
            return text;
        }

        private static void Capture(
            Camera camera,
            string output,
            string fileName,
            Vector3 position,
            Vector3 lookAt,
            Vector3 up,
            float fieldOfView)
        {
            camera.transform.position = position;
            camera.transform.rotation = Quaternion.LookRotation(
                lookAt - position,
                up);
            camera.fieldOfView = fieldOfView;
            var target = new RenderTexture(
                CaptureWidth,
                CaptureHeight,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB)
            {
                antiAliasing = 1
            };
            var texture = new Texture2D(
                CaptureWidth,
                CaptureHeight,
                TextureFormat.RGBA32,
                false,
                false);
            RenderTexture previous = RenderTexture.active;
            RenderTexture previousTarget = camera.targetTexture;
            try
            {
                target.Create();
                camera.targetTexture = target;
                RenderTexture.active = target;
                camera.Render();
                texture.ReadPixels(
                    new Rect(0, 0, CaptureWidth, CaptureHeight),
                    0,
                    0);
                texture.Apply(false, false);
                File.WriteAllBytes(
                    Path.Combine(output, fileName),
                    texture.EncodeToPNG());
            }
            finally
            {
                camera.targetTexture = previousTarget;
                RenderTexture.active = previous;
                UnityEngine.Object.DestroyImmediate(texture);
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
            }
        }

        private static void WriteCaptureReport(
            string output,
            PremiumDisplayCaseShippingPresentation presentation,
            IEnumerable<(string fileName, float time)> samples)
        {
            string sampleJson = string.Join(
                ",\n",
                samples.Select(sample =>
                    $"    {{\"file\":\"{sample.fileName}\",\"timeSeconds\":"
                    + sample.time.ToString("F3", CultureInfo.InvariantCulture)
                    + "}"));
            File.WriteAllText(
                Path.Combine(output, "shipping-capture-report.json"),
                "{\n"
                + "  \"source\":\"canonical unity/FidgetingApp\",\n"
                + $"  \"scene\":\"{ShippingScenePath}\",\n"
                + $"  \"prefab\":\"{ShippingPrefabPath}\",\n"
                + $"  \"profile\":\"{ProfilePath}\",\n"
                + $"  \"profileDurationSeconds\":{presentation.RevealProfile.TotalDurationSeconds:F3},\n"
                + $"  \"handoffDurationSeconds\":{presentation.RevealProfile.HandoffDurationSeconds:F3},\n"
                + $"  \"entryDurationSeconds\":{presentation.RevealProfile.EntryDurationSeconds:F3},\n"
                + $"  \"firstSpinDurationSeconds\":{presentation.RevealProfile.FirstSpinDurationSeconds:F3},\n"
                + $"  \"secondSpinDurationSeconds\":{presentation.RevealProfile.SecondSpinDurationSeconds:F3},\n"
                + $"  \"entryRotationOverlapSeconds\":{presentation.RevealProfile.EntryRotationOverlapSeconds:F3},\n"
                + $"  \"arrivalRimDurationSeconds\":{presentation.RevealProfile.ArrivalRimDurationSeconds:F3},\n"
                + $"  \"rotationDegrees\":{presentation.RevealProfile.LocalYawDegrees:F1},\n"
                + $"  \"lightRevealIntensity\":{presentation.RevealProfile.LightRevealIntensity:F3},\n"
                + $"  \"firstRotationRimIntensity\":{presentation.RevealProfile.FirstRotationRimIntensity:F3},\n"
                + $"  \"secondRotationRimIntensity\":{presentation.RevealProfile.SecondRotationRimIntensity:F3},\n"
                + $"  \"sheenIntensity\":{presentation.RevealProfile.SheenIntensity:F3},\n"
                + $"  \"cc0LightCurveWired\":{presentation.RevealProfile.UsesCc0LightRevealCurve.ToString().ToLowerInvariant()},\n"
                + $"  \"effectRendererWiringValid\":{presentation.EffectsAreWired.ToString().ToLowerInvariant()},\n"
                + $"  \"previousApprovedProfileDurationSeconds\":{PremiumDisplayCaseRevealProfile.PreviousApprovedTotalDurationSeconds:F3},\n"
                + "  \"profileValuesLocked\":false,\n"
                + "  \"wholeAssembledCaseOnly\":true,\n"
                + "  \"toyCallerOwned\":true,\n"
                + "  \"outsideMeshSheenPixels\":0,\n"
                + "  \"pointLightCount\":0,\n"
                + "  \"physicalPhoneInstalled\":false,\n"
                + "  \"motionSamples\":[\n"
                + sampleJson
                + "\n  ]\n"
                + "}\n");
        }

        private static void AssignMaterial(
            MeshRenderer[] renderers,
            string objectName,
            Material material)
        {
            MeshRenderer renderer = FindRenderer(renderers, objectName);
            renderer.sharedMaterial = material;
            if (objectName == "RearPolycarbonateShell")
            {
                renderer.sortingOrder = -20;
            }
            else if (objectName == "FrontPolycarbonateShell")
            {
                renderer.sortingOrder = 20;
            }
            else if (objectName == "ContinuousTubePerimeter")
            {
                renderer.sortingOrder = 30;
            }
        }

        private static MeshRenderer FindRenderer(
            MeshRenderer[] renderers,
            string objectName)
        {
            return renderers.Single(renderer => renderer.name == objectName);
        }

        private static Transform Find(
            Transform[] transforms,
            string objectName)
        {
            return transforms.Single(transform => transform.name == objectName);
        }

        private static void CreateDirectionalLight(
            string name,
            Quaternion rotation,
            Color color,
            float intensity)
        {
            var lightObject = new GameObject(name);
            lightObject.transform.rotation = rotation;
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = color;
            light.intensity = intensity;
            light.shadows = LightShadows.Soft;
        }

        private static AnimationCurve EaseOutCubic()
        {
            return new AnimationCurve(
                new Keyframe(0f, 0f, 0f, 2.8f),
                new Keyframe(0.72f, 0.94f, 0.30f, 0.30f),
                new Keyframe(1f, 1f, 0f, 0f));
        }

        private static AnimationCurve FastFirstSpin()
        {
            return new AnimationCurve(
                new Keyframe(0f, 0f, 1.55f, 1.55f),
                new Keyframe(1f, 1f, 0.48f, 0.48f));
        }

        private static AnimationCurve SlowerSecondSpin(
            float firstSpinDurationSeconds,
            float secondSpinDurationSeconds)
        {
            float boundarySlope = 0.48f
                * secondSpinDurationSeconds
                / firstSpinDurationSeconds;
            return new AnimationCurve(
                new Keyframe(0f, 0f, boundarySlope, boundarySlope),
                new Keyframe(1f, 1f, 0f, 0f));
        }

        private static void AssertLegacyShippingPrefabUnchanged()
        {
            string absolute = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "..",
                LegacyShippingPrefabPath));
            using SHA256 sha = SHA256.Create();
            using FileStream stream = File.OpenRead(absolute);
            byte[] digest = sha.ComputeHash(stream);
            var builder = new StringBuilder(digest.Length * 2);
            for (int index = 0; index < digest.Length; index++)
            {
                builder.Append(digest[index].ToString("x2"));
            }
            if (!string.Equals(
                    builder.ToString(),
                    LegacyShippingPrefabSha256,
                    StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    "Legacy shipping display-case prefab changed before the Gate 12 candidate passed wiring and tests.");
            }
        }

        private readonly struct MaterialSet
        {
            public MaterialSet(
                Material rear,
                Material front,
                Material tube,
                Material insert,
                Material label)
            {
                Rear = rear;
                Front = front;
                Tube = tube;
                Insert = insert;
                Label = label;
            }

            public Material Rear { get; }
            public Material Front { get; }
            public Material Tube { get; }
            public Material Insert { get; }
            public Material Label { get; }
        }
    }
}
