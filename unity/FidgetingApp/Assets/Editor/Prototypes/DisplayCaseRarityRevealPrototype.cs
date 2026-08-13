using System;
using System.Collections.Generic;
using System.IO;
using FidgetingApp.DisplayCase;
using FidgetingApp.Product.Gacha;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.Editor.Prototypes
{
    /// <summary>
    /// Deletable, Editor-only visual study for rarity-colored display cases and
    /// a single-draw reveal. It instantiates the shipping prefab read-only and
    /// applies per-renderer MaterialPropertyBlocks to the temporary instance.
    /// No prefab, scene, shared material, runtime component, or prize asset is
    /// saved by this tool.
    /// </summary>
    public static class DisplayCaseRarityRevealPrototype
    {
        public const float TotalDurationSeconds = 6f;
        public const int FramesPerSecond = 30;

        private const string DisplayCasePrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCase.prefab";
        private const string PrizePrefabPath =
            "Assets/Resources/Gacha/ThreeBladeDisplayPrize.prefab";
        private const int StillWidth = 900;
        private const int StillHeight = 1200;
        private const int VideoWidth = 720;
        private const int VideoHeight = 960;
        private const float SimulatorExplodeProgress = 0.50f;
        private const float SimulatorExplodedScale = 0.72f;
        private const float SimulatorExplodedCenterOffsetX = 0.0263f;
        private const float SimulatorPrizeScale = 1.58f;
        private const float SimulatorSheenPeak = 3.40f;

        private static readonly int BaseColorId = Shader.PropertyToID("_BaseColor");
        private static readonly int ColorId = Shader.PropertyToID("_Color");
        private static readonly int RimColorId = Shader.PropertyToID("_RimColor");
        private static readonly int EmissionColorId =
            Shader.PropertyToID("_EmissionColor");

        private static readonly PrototypePalette[] palettes =
        {
            new PrototypePalette(
                GachaRarity.Standard,
                "standard-blue",
                "STANDARD / BLUE",
                new Color(0.20f, 0.60f, 1.00f),
                new Color(0.035f, 0.095f, 0.16f)),
            new PrototypePalette(
                GachaRarity.Refined,
                "refined-green",
                "REFINED / GREEN",
                new Color(0.20f, 0.88f, 0.58f),
                new Color(0.025f, 0.13f, 0.085f)),
            new PrototypePalette(
                GachaRarity.Signature,
                "signature-purple",
                "SIGNATURE / PURPLE",
                new Color(0.64f, 0.36f, 1.00f),
                new Color(0.105f, 0.045f, 0.18f)),
            new PrototypePalette(
                GachaRarity.Heirloom,
                "heirloom-gold",
                "HEIRLOOM / GOLD",
                new Color(1.00f, 0.63f, 0.16f),
                new Color(0.17f, 0.085f, 0.018f))
        };

        public static IReadOnlyList<string> PaletteIds => Array.ConvertAll(
            palettes,
            palette => palette.Id);

        [MenuItem("Fidgeting/Prototype/Display Case Rarity/Generate All")]
        public static void GenerateAll()
        {
            string outputRoot = OutputRoot;
            string stillRoot = Path.Combine(outputRoot, "stills");
            string storyboardRoot = Path.Combine(outputRoot, "storyboard");
            string frameRoot = Path.Combine(outputRoot, "frames-heirloom-gold");
            Directory.CreateDirectory(outputRoot);
            Directory.CreateDirectory(stillRoot);
            Directory.CreateDirectory(storyboardRoot);
            Directory.CreateDirectory(frameRoot);
            DeletePngFiles(stillRoot);
            DeletePngFiles(storyboardRoot);
            DeletePngFiles(frameRoot);

            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            Camera camera = CreatePreviewEnvironment(scene);

            PrototypeRig defaultRig = CreateRig(null);
            Capture(
                camera,
                Path.Combine(stillRoot, "00-default-case.png"),
                StillWidth,
                StillHeight);
            DestroyRig(defaultRig);

            for (int index = 0; index < palettes.Length; index++)
            {
                PrototypeRig rig = CreateRig(palettes[index]);
                Capture(
                    camera,
                    Path.Combine(
                        stillRoot,
                        $"{index + 1:00}-{palettes[index].Id}.png"),
                    StillWidth,
                    StillHeight);
                DestroyRig(rig);
            }

            PrototypePalette revealPalette = palettes[palettes.Length - 1];
            PrototypeRig revealRig = CreateRig(revealPalette);
            CaptureStoryboard(camera, revealRig, storyboardRoot);
            CaptureVideoFrames(camera, revealRig, frameRoot);
            DestroyRig(revealRig);

            WriteAudit(outputRoot);
            AssetDatabase.Refresh();
            Debug.Log(
                $"[DisplayCaseRarityRevealPrototype] Generated isolated demo: "
                + outputRoot);
        }

        [MenuItem(
            "Fidgeting/Prototype/Display Case Rarity/Generate Neutral Simulator Media")]
        public static void GenerateNeutralSimulatorMedia()
        {
            string outputRoot = OutputRoot;
            string storyboardRoot = Path.Combine(
                outputRoot,
                "storyboard-neutral-simulator");
            string frameRoot = Path.Combine(
                outputRoot,
                "frames-neutral-simulator");
            Directory.CreateDirectory(outputRoot);
            Directory.CreateDirectory(storyboardRoot);
            Directory.CreateDirectory(frameRoot);
            DeletePngFiles(storyboardRoot);
            DeletePngFiles(frameRoot);

            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            Camera camera = CreatePreviewEnvironment(scene);
            PrototypeRig neutralRig = CreateRig(null);
            CaptureStoryboard(camera, neutralRig, storyboardRoot);
            CaptureVideoFrames(camera, neutralRig, frameRoot);
            DestroyRig(neutralRig);

            AssetDatabase.Refresh();
            Debug.Log(
                "[DisplayCaseRarityRevealPrototype] Generated neutral 3:4 "
                + "Simulator media: "
                + outputRoot);
        }

        public static PrototypePhase SamplePhase(float seconds)
        {
            float time = Mathf.Clamp(seconds, 0f, TotalDurationSeconds);
            if (time < 0.80f)
            {
                return PrototypePhase.BackFacing;
            }
            if (time < 1.80f)
            {
                return PrototypePhase.FlipToFront;
            }
            if (time < 2.70f)
            {
                return PrototypePhase.PrizeReadable;
            }
            if (time < 4.10f)
            {
                return PrototypePhase.PartsExplode;
            }
            if (time < 4.45f)
            {
                return PrototypePhase.ExplodedHold;
            }
            if (time < 5.75f)
            {
                return PrototypePhase.PrizeOnlyLightPass;
            }
            return PrototypePhase.Complete;
        }

        private static string OutputRoot => Path.GetFullPath(Path.Combine(
            Application.dataPath,
            "../Artifacts/DisplayCaseRarityRevealPrototype"));

        private static PrototypeRig CreateRig(PrototypePalette? palette)
        {
            PremiumDisplayCase prefab = AssetDatabase.LoadAssetAtPath<
                PremiumDisplayCase>(DisplayCasePrefabPath);
            GameObject prizePrefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                PrizePrefabPath);
            if (prefab == null || prizePrefab == null)
            {
                throw new MissingReferenceException(
                    "The prototype requires the existing display-case and "
                    + "three-blade prize prefabs.");
            }

            PremiumDisplayCase displayCase = (PremiumDisplayCase)PrefabUtility
                .InstantiatePrefab(prefab);
            displayCase.name = "PrototypeDisplayCase_NotForShipping";
            displayCase.transform.SetPositionAndRotation(
                Vector3.zero,
                Quaternion.identity);
            displayCase.setCapsulePreset(
                PremiumDisplayCaseCapsulePreset.RoundedSquareDeep);
            displayCase.SetIdentification(
                palette.HasValue ? palette.Value.Label : "DEFAULT CASE",
                42);
            displayCase.ClearFeaturedBadge();

            GameObject prize = (GameObject)PrefabUtility.InstantiatePrefab(prizePrefab);
            prize.name = "PrototypePrize_ExistingThreeBladeReference";
            displayCase.setContent(
                prize.transform,
                ThreeBladeDisplayPrizeFactory.ContentOptions);
            displayCase.SetRevealProgressForPreview(1f);

            PremiumDisplayCaseInteractionController interaction = displayCase
                .GetComponent<PremiumDisplayCaseInteractionController>();
            if (interaction == null)
            {
                throw new MissingComponentException(
                    "Display-case interaction controller is unavailable.");
            }
            interaction.SetExplodedProgressForPreview(0f);
            interaction.SetOrbitDegrees(0f, 0f);

            var caseRenderers = new List<Renderer>();
            foreach (Renderer renderer in displayCase.GetComponentsInChildren<
                         Renderer>(true))
            {
                if (!renderer.transform.IsChildOf(prize.transform))
                {
                    caseRenderers.Add(renderer);
                }
            }

            Light accent = CreateAccentLight(
                displayCase.transform,
                palette.HasValue
                    ? palette.Value.Accent
                    : new Color(0.72f, 0.82f, 1f));
            Light sheen = CreateSheenLight(
                palette.HasValue
                    ? palette.Value.Accent
                    : Color.white);
            var rig = new PrototypeRig(
                displayCase,
                interaction,
                prize.transform,
                caseRenderers.ToArray(),
                accent,
                sheen,
                palette);
            ResetRig(rig);
            return rig;
        }

        private static void ResetRig(PrototypeRig rig)
        {
            rig.DisplayCase.transform.position = Vector3.zero;
            rig.DisplayCase.transform.rotation = Quaternion.identity;
            rig.DisplayCase.transform.localScale = Vector3.one;
            rig.DisplayCase.SetRevealProgressForPreview(1f);
            rig.Interaction.SetExplodedProgressForPreview(0f);
            rig.Interaction.SetOrbitDegrees(0f, 0f);
            SetCaseRenderersVisible(rig, true);
            rig.Prize.gameObject.SetActive(true);
            rig.AccentLight.intensity = rig.Palette.HasValue ? 0.38f : 0.30f;
            rig.SheenLight.intensity = 0f;
            ApplyPalette(rig);
        }

        private static void ApplyTimeline(PrototypeRig rig, float seconds)
        {
            float time = Mathf.Clamp(seconds, 0f, TotalDurationSeconds);
            ResetRig(rig);

            float flip = Smooth01(Mathf.InverseLerp(0.80f, 1.80f, time));
            float yaw = Mathf.Lerp(180f, 0f, flip);
            rig.DisplayCase.transform.rotation = Quaternion.Euler(0f, yaw, 0f);

            float exploded = Smooth01(Mathf.InverseLerp(2.70f, 4.10f, time))
                * SimulatorExplodeProgress;
            rig.Interaction.SetExplodedProgressForPreview(exploded);
            float explodedUnit = exploded / SimulatorExplodeProgress;
            rig.DisplayCase.transform.position = Vector3.right
                * (SimulatorExplodedCenterOffsetX * explodedUnit);

            bool prizeOnly = time >= 4.45f;
            if (!prizeOnly)
            {
                rig.DisplayCase.transform.localScale = Vector3.one
                    * Mathf.Lerp(
                        1f,
                        SimulatorExplodedScale,
                        exploded / SimulatorExplodeProgress);
            }
            else
            {
                float recenter = Smooth01(Mathf.InverseLerp(4.45f, 4.82f, time));
                rig.DisplayCase.transform.position = Vector3.right
                    * Mathf.Lerp(
                        SimulatorExplodedCenterOffsetX,
                        0f,
                        recenter);
                rig.Interaction.SetExplodedProgressForPreview(
                    SimulatorExplodeProgress * (1f - recenter));
                rig.DisplayCase.transform.localScale = Vector3.one
                    * Mathf.Lerp(
                        SimulatorExplodedScale,
                        SimulatorPrizeScale,
                        recenter);
            }
            SetCaseRenderersVisible(rig, !prizeOnly);
            float accentIntensity = rig.Palette.HasValue ? 0.32f : 0.21f;
            rig.AccentLight.intensity = prizeOnly
                ? accentIntensity * 0.42f
                : accentIntensity;

            if (time >= 4.45f)
            {
                float pass = Mathf.InverseLerp(4.45f, 5.75f, time);
                float travel = Mathf.SmoothStep(-0.17f, 0.17f, pass);
                rig.SheenLight.transform.position =
                    new Vector3(travel, 0.035f, -0.18f);
                rig.SheenLight.transform.LookAt(
                    rig.Prize.position + new Vector3(0f, 0.02f, 0f));
                rig.SheenLight.intensity =
                    Mathf.Sin(Mathf.Clamp01(pass) * Mathf.PI)
                    * SimulatorSheenPeak;
            }

            ApplyPalette(rig);
        }

        private static void ApplyPalette(PrototypeRig rig)
        {
            if (!rig.Palette.HasValue)
            {
                foreach (Renderer renderer in rig.CaseRenderers)
                {
                    renderer.SetPropertyBlock(null);
                }
                return;
            }

            PrototypePalette palette = rig.Palette.Value;
            foreach (Renderer renderer in rig.CaseRenderers)
            {
                if (renderer == null)
                {
                    continue;
                }

                string name = renderer.gameObject.name;
                var properties = new MaterialPropertyBlock();
                renderer.GetPropertyBlock(properties);
                if (name.StartsWith("Fastener_", StringComparison.Ordinal))
                {
                    Color cap = Color.Lerp(
                        new Color(0.18f, 0.20f, 0.24f),
                        palette.Accent,
                        0.48f);
                    SetLitColor(properties, cap);
                }
                else if (name.StartsWith("ChromeCollar_", StringComparison.Ordinal)
                    || name == "Capsule_EdgeHighlight"
                    || name == "RoundedEdgeLight")
                {
                    Color metal = Color.Lerp(
                        new Color(0.48f, 0.52f, 0.58f),
                        palette.Accent,
                        0.34f);
                    SetLitColor(properties, metal);
                    properties.SetColor(
                        EmissionColorId,
                        palette.Accent * 0.018f);
                }
                else if (name.StartsWith("Graphite_", StringComparison.Ordinal)
                    || name.Contains("Velvet", StringComparison.Ordinal))
                {
                    SetLitColor(properties, palette.DarkLining);
                }
                else if (name.StartsWith("RoundedRecess", StringComparison.Ordinal)
                    || name.StartsWith("Capsule_", StringComparison.Ordinal))
                {
                    SetLitColor(
                        properties,
                        Color.Lerp(palette.DarkLining, palette.Accent, 0.18f));
                    properties.SetColor(RimColorId, palette.Accent);
                }
                else if (name.StartsWith("Acrylic_", StringComparison.Ordinal))
                {
                    properties.SetColor(
                        BaseColorId,
                        Color.Lerp(
                            new Color(0.68f, 0.82f, 0.90f),
                            palette.Accent,
                            0.08f));
                    properties.SetColor(
                        RimColorId,
                        Color.Lerp(Color.white, palette.Accent, 0.38f));
                }
                else
                {
                    continue;
                }
                renderer.SetPropertyBlock(properties);
            }
        }

        private static void SetLitColor(
            MaterialPropertyBlock properties,
            Color color)
        {
            properties.SetColor(BaseColorId, color);
            properties.SetColor(ColorId, color);
        }

        private static Light CreateAccentLight(Transform parent, Color color)
        {
            var lightObject = new GameObject("PrototypeRarityAccentLight");
            lightObject.transform.SetParent(parent, false);
            lightObject.transform.localPosition = new Vector3(0f, 0.03f, -0.16f);
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Point;
            light.color = color;
            light.range = 0.55f;
            light.intensity = 0.38f;
            light.shadows = LightShadows.None;
            return light;
        }

        private static Light CreateSheenLight(Color color)
        {
            var lightObject = new GameObject("PrototypePrizeLightPass");
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Spot;
            light.color = Color.Lerp(Color.white, color, 0.28f);
            light.range = 0.70f;
            light.spotAngle = 19f;
            light.innerSpotAngle = 7f;
            light.shadows = LightShadows.None;
            light.intensity = 0f;
            return light;
        }

        private static Camera CreatePreviewEnvironment(Scene scene)
        {
            var cameraObject = new GameObject("PrototypeCamera");
            SceneManager.MoveGameObjectToScene(cameraObject, scene);
            cameraObject.tag = "MainCamera";
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.009f, 0.012f, 0.024f, 1f);
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.allowHDR = true;
            camera.allowMSAA = false;
            camera.transform.position =
                PremiumDisplayCaseCameraRules.FrontCameraPosition;
            camera.transform.LookAt(PremiumDisplayCaseCameraRules.FrontLookAt);
            camera.fieldOfView = PremiumDisplayCaseCameraRules
                .ResolveVerticalFieldOfView(StillWidth / (float)StillHeight);

            var keyObject = new GameObject("PrototypeNeutralKey");
            SceneManager.MoveGameObjectToScene(keyObject, scene);
            Light key = keyObject.AddComponent<Light>();
            key.type = LightType.Directional;
            key.color = new Color(0.80f, 0.87f, 1.00f);
            key.intensity = 0.18f;
            key.shadows = LightShadows.Soft;
            keyObject.transform.rotation = Quaternion.Euler(38f, -32f, 0f);

            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.026f, 0.031f, 0.050f);
            RenderSettings.fog = false;
            return camera;
        }

        private static void CaptureStoryboard(
            Camera camera,
            PrototypeRig rig,
            string outputDirectory)
        {
            float[] moments = { 0.30f, 1.28f, 2.25f, 3.95f, 4.90f, 5.38f };
            string[] names =
            {
                "01-back-facing",
                "02-flip-to-front",
                "03-prize-readable",
                "04-parts-exploded",
                "05-prize-only",
                "06-light-pass-complete"
            };
            for (int index = 0; index < moments.Length; index++)
            {
                ApplyTimeline(rig, moments[index]);
                Capture(
                    camera,
                    Path.Combine(outputDirectory, names[index] + ".png"),
                    StillWidth,
                    StillHeight);
            }
        }

        private static void CaptureVideoFrames(
            Camera camera,
            PrototypeRig rig,
            string outputDirectory)
        {
            int frameCount = Mathf.RoundToInt(
                TotalDurationSeconds * FramesPerSecond);
            for (int frame = 0; frame < frameCount; frame++)
            {
                float time = frame / (float)FramesPerSecond;
                ApplyTimeline(rig, time);
                Capture(
                    camera,
                    Path.Combine(outputDirectory, $"frame-{frame:0000}.png"),
                    VideoWidth,
                    VideoHeight);
            }
        }

        private static void Capture(
            Camera camera,
            string outputPath,
            int width,
            int height)
        {
            camera.aspect = width / (float)height;
            camera.fieldOfView = PremiumDisplayCaseCameraRules
                .ResolveVerticalFieldOfView(camera.aspect);
            var renderTexture = new RenderTexture(
                width,
                height,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB)
            {
                antiAliasing = 1,
                name = "DisplayCaseRarityPrototypeRT"
            };
            renderTexture.Create();
            RenderTexture previousActive = RenderTexture.active;
            RenderTexture previousTarget = camera.targetTexture;
            camera.targetTexture = renderTexture;
            RenderTexture.active = renderTexture;
            camera.Render();

            var texture = new Texture2D(
                width,
                height,
                TextureFormat.RGBA32,
                false,
                false);
            texture.ReadPixels(new Rect(0f, 0f, width, height), 0, 0);
            texture.Apply(false, false);
            File.WriteAllBytes(outputPath, texture.EncodeToPNG());

            camera.targetTexture = previousTarget;
            RenderTexture.active = previousActive;
            renderTexture.Release();
            UnityEngine.Object.DestroyImmediate(texture);
            UnityEngine.Object.DestroyImmediate(renderTexture);
        }

        private static void SetCaseRenderersVisible(
            PrototypeRig rig,
            bool visible)
        {
            foreach (Renderer renderer in rig.CaseRenderers)
            {
                if (renderer != null)
                {
                    renderer.enabled = visible;
                }
            }
        }

        private static void DestroyRig(PrototypeRig rig)
        {
            if (rig.SheenLight != null)
            {
                UnityEngine.Object.DestroyImmediate(rig.SheenLight.gameObject);
            }
            if (rig.DisplayCase != null)
            {
                rig.DisplayCase.setContent((Transform)null);
                UnityEngine.Object.DestroyImmediate(rig.DisplayCase.gameObject);
            }
            if (rig.Prize != null)
            {
                UnityEngine.Object.DestroyImmediate(rig.Prize.gameObject);
            }
        }

        private static float Smooth01(float value)
        {
            float t = Mathf.Clamp01(value);
            return t * t * (3f - 2f * t);
        }

        private static void DeletePngFiles(string directory)
        {
            foreach (string path in Directory.GetFiles(directory, "*.png"))
            {
                File.Delete(path);
            }
        }

        private static void WriteAudit(string outputRoot)
        {
            string json =
                "{\n"
                + "  \"prototypeOnly\": true,\n"
                + "  \"shippingAssetsModified\": false,\n"
                + "  \"sourcePrefab\": \"Assets/Resources/Gacha/PremiumDisplayCase.prefab\",\n"
                + "  \"sourcePrize\": \"Assets/Resources/Gacha/ThreeBladeDisplayPrize.prefab\",\n"
                + "  \"rarityMapping\": [\n"
                + "    {\"rarity\":\"Standard\",\"color\":\"blue\",\"hex\":\"#3399FF\"},\n"
                + "    {\"rarity\":\"Refined\",\"color\":\"green\",\"hex\":\"#33E094\"},\n"
                + "    {\"rarity\":\"Signature\",\"color\":\"purple\",\"hex\":\"#A35CFF\"},\n"
                + "    {\"rarity\":\"Heirloom\",\"color\":\"gold\",\"hex\":\"#FFA329\"}\n"
                + "  ],\n"
                + "  \"customizationBoundaries\": {\n"
                + "    \"screws\": [\"Fastener_*\", \"ChromeCollar_*\"],\n"
                + "    \"background\": [\"Graphite_Insert\", \"Graphite_InnerTray\", \"*Velvet*\"],\n"
                + "    \"innerPlasticCapsule\": [\"RoundedRecess*\", \"RoundedEdgeLight\", \"Capsule_*\"],\n"
                + "    \"acrylic\": \"weak BaseColor/RimColor tint only; preserve transparency\",\n"
                + "    \"lighting\": \"prototype-owned accent and light-pass lights\"\n"
                + "  },\n"
                + "  \"timeline\": [\"back-facing\",\"flip-to-front\",\"prize-readable\",\"parts-explode\",\"prize-only\",\"light-pass-complete\"],\n"
                + "  \"promotionInterfaces\": [\n"
                + "    \"RarityVisualProfile Resolve(GachaRarity)\",\n"
                + "    \"PremiumDisplayCase.ApplyRarityVisual(profile)\",\n"
                + "    \"GachaRevealDirector.Begin(outcome, prizeNode)\",\n"
                + "    \"GachaRevealDirector phase/progress callback to native UI\",\n"
                + "    \"MaterialPropertyBlock bindings for screw/background/capsule/acrylic roles\"\n"
                + "  ]\n"
                + "}\n";
            File.WriteAllText(
                Path.Combine(outputRoot, "material-boundary-audit.json"),
                json);
        }

        private readonly struct PrototypePalette
        {
            public PrototypePalette(
                GachaRarity rarity,
                string id,
                string label,
                Color accent,
                Color darkLining)
            {
                Rarity = rarity;
                Id = id;
                Label = label;
                Accent = accent;
                DarkLining = darkLining;
            }

            public GachaRarity Rarity { get; }
            public string Id { get; }
            public string Label { get; }
            public Color Accent { get; }
            public Color DarkLining { get; }
        }

        private readonly struct PrototypeRig
        {
            public PrototypeRig(
                PremiumDisplayCase displayCase,
                PremiumDisplayCaseInteractionController interaction,
                Transform prize,
                Renderer[] caseRenderers,
                Light accentLight,
                Light sheenLight,
                PrototypePalette? palette)
            {
                DisplayCase = displayCase;
                Interaction = interaction;
                Prize = prize;
                CaseRenderers = caseRenderers;
                AccentLight = accentLight;
                SheenLight = sheenLight;
                Palette = palette;
            }

            public PremiumDisplayCase DisplayCase { get; }
            public PremiumDisplayCaseInteractionController Interaction { get; }
            public Transform Prize { get; }
            public Renderer[] CaseRenderers { get; }
            public Light AccentLight { get; }
            public Light SheenLight { get; }
            public PrototypePalette? Palette { get; }
        }
    }

    public enum PrototypePhase
    {
        BackFacing = 0,
        FlipToFront = 1,
        PrizeReadable = 2,
        PartsExplode = 3,
        ExplodedHold = 4,
        PrizeOnlyLightPass = 5,
        Complete = 6
    }
}
