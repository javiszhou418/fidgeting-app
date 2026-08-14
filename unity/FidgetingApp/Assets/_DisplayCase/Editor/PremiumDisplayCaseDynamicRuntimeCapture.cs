using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using FidgetingApp.Product;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Editor
{
    public static class PremiumDisplayCaseDynamicRuntimeCapture
    {
        private const string PrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCase.prefab";
        private const string OutputFolder =
            "../Artifacts/PremiumDisplayCaseDynamicRuntimeValidation";
        private const int FrameWidth = 480;
        private const int FrameHeight = 640;
        private const float FrameStep = 1f / 15f;

        [Serializable]
        private sealed class ProductValidation
        {
            public string modelId;
            public string scenePath;
            public string sourceRoot;
            public string capsule;
            public string initialEuler;
            public float idlePeriodSeconds;
            public int sourceRendererCount;
            public int snapshotRendererCount;
            public string[] snapshotRendererNames;
            public string fitScale;
            public string fitOffset;
            public float frontAngleErrorDegrees;
            public float frontImageLuminanceRange;
            public float restoredLayerErrorMeters;
            public bool rendererSetClean;
            public bool entranceFrontReadable;
            public bool explodeCompleted;
            public bool replayRestored;
            public bool passed;
        }

        [Serializable]
        private sealed class ValidationReport
        {
            public string generatedUtc;
            public string captureContract;
            public ProductValidation[] products;
            public bool passed;
        }

        [MenuItem("Fidgeting/Display Case/Capture Dynamic Shipping Runtime Gate")]
        public static void CaptureAll()
        {
            CaptureProducts(
                ProductCatalog.ShippingEntries,
                OutputFolder);
        }

        [MenuItem("Fidgeting/Display Case/Capture Corrected Three Products")]
        public static void CaptureCorrectedThree()
        {
            string[] correctedModelIds =
            {
                ProductCatalog.MetalThreeBladeModelId,
                ProductCatalog.GoldFourWingModelId,
                ProductCatalog.MagneticFanCardModelId
            };
            CaptureProducts(
                ProductCatalog.ShippingEntries.Where(entry =>
                    correctedModelIds.Contains(entry.ModelId)),
                "../Artifacts/PremiumDisplayCaseThreeProductCorrection");
        }

        private static void CaptureProducts(
            IEnumerable<ProductCatalogEntry> products,
            string outputFolder)
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(
                    $"Missing shipping display-case prefab: {PrefabPath}");
            }

            string outputRoot = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                outputFolder));
            Directory.CreateDirectory(outputRoot);
            var validations = new List<ProductValidation>();

            foreach (ProductCatalogEntry product in products)
            {
                validations.Add(CaptureProduct(prefab, product, outputRoot));
            }

            var report = new ValidationReport
            {
                generatedUtc = DateTime.UtcNow.ToString("O", CultureInfo.InvariantCulture),
                captureContract =
                    "shipping scene root -> renderer-only canonical rest snapshot -> "
                    + "shipping PremiumDisplayCase prefab -> play/front/flip/orbit/"
                    + "explode/replay/dismiss lifecycle",
                products = validations.ToArray(),
                passed = validations.All(validation => validation.passed)
            };
            File.WriteAllText(
                Path.Combine(outputRoot, "dynamic-validation.json"),
                JsonUtility.ToJson(report, true));
            EditorSceneManager.OpenScene(
                "Assets/_DisplayCase/Scenes/PremiumDisplayCase.unity",
                OpenSceneMode.Single);
            Debug.Log(
                $"Premium display-case dynamic runtime gate: {outputRoot}; "
                + $"passed={report.passed}");
            if (!report.passed)
            {
                throw new InvalidOperationException(
                    "One or more shipping display-case dynamic sessions failed.");
            }
        }

        private static ProductValidation CaptureProduct(
            GameObject prefab,
            ProductCatalogEntry product,
            string outputRoot)
        {
            Scene scene = EditorSceneManager.OpenScene(
                product.ScenePath,
                OpenSceneMode.Single);
            PremiumDisplayCaseProductProfile profile =
                PremiumDisplayCaseProductProfiles.Resolve(product.ModelId);
            Transform sourceRoot = scene.GetRootGameObjects()
                .Select(root => root.transform)
                .Single(root => root.name == profile.SceneRootName);
            Renderer[] sourceRenderers = sourceRoot.GetComponentsInChildren<Renderer>(
                false);
            GameObject canonical = PremiumDisplayCaseProductSnapshot.Capture(
                product.ModelId,
                sourceRoot);
            Renderer[] snapshotRenderers = canonical.GetComponentsInChildren<Renderer>(
                true);
            string[] snapshotNames = snapshotRenderers
                .Select(renderer => renderer.gameObject.name)
                .ToArray();
            bool rendererSetClean = snapshotNames.All(name =>
                    !name.Contains("Camera", StringComparison.OrdinalIgnoreCase)
                    && !name.Contains("Studio", StringComparison.OrdinalIgnoreCase)
                    && !name.Contains("Ground", StringComparison.OrdinalIgnoreCase)
                    && !name.Contains("Particle", StringComparison.OrdinalIgnoreCase))
                && canonical.GetComponentsInChildren<Camera>(true).Length == 0
                && canonical.GetComponentsInChildren<ParticleSystem>(true).Length == 0
                && canonical.GetComponentsInChildren<Collider>(true).Length == 0
                && canonical.GetComponentsInChildren<Rigidbody>(true).Length == 0;

            foreach (GameObject root in scene.GetRootGameObjects())
            {
                if (root != canonical)
                {
                    root.SetActive(false);
                }
            }

            GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(
                prefab,
                scene);
            PremiumDisplayCase displayCase = instance.GetComponent<
                PremiumDisplayCase>();
            PremiumDisplayCaseInteractionController interaction = instance
                .GetComponent<PremiumDisplayCaseInteractionController>();
            if (displayCase == null || interaction == null)
            {
                throw new MissingReferenceException(
                    $"Shipping display-case runtime is incomplete for {product.ModelId}.");
            }
            displayCase.name = $"PremiumDisplayCase_{product.ModelId}";
            displayCase.SetIdentification(profile.EnglishDisplayName, 50);
            displayCase.setCapsuleDimensions(profile.CapsuleDimensions);
            displayCase.SetProductPresentationOffset(profile.PresentationOffset);
            displayCase.setContent(canonical.transform, profile.ContentOptions);
            displayCase.SetLightingPreset(PremiumDisplayCaseLightingCatalog.DefaultId);
            displayCase.SetParallaxForPreview(Vector2.zero);
            CreateEnvironment();
            Camera camera = UnityEngine.Object.FindObjectsByType<Camera>()
                .Single(item => item.name == "DynamicDisplayCaseCamera");
            camera.transform.position = PremiumDisplayCaseCameraRules.FrontCameraPosition;
            camera.transform.LookAt(PremiumDisplayCaseCameraRules.FrontLookAt);
            camera.fieldOfView = PremiumDisplayCaseCameraRules
                .ReferenceVerticalFieldOfView;

            string productOutput = Path.Combine(outputRoot, product.ModelId);
            string framesOutput = Path.Combine(productOutput, "frames");
            string keysOutput = Path.Combine(productOutput, "keyframes");
            Directory.CreateDirectory(framesOutput);
            Directory.CreateDirectory(keysOutput);
            using var recorder = new FrameRecorder(camera, framesOutput);

            Transform[] layers = DisplayLayers(displayCase);
            interaction.SetExplodedProgress(0f);
            Vector3[] assembled = layers.Select(layer => layer.localPosition).ToArray();
            interaction.SetExplodedProgress(1f);
            displayCase.play();
            interaction.PlayAssembly();
            recorder.Keyframe(keysOutput, "00_present.png");
            Run(recorder, PremiumDisplayCaseRevealMotion.DurationSeconds,
                delta =>
                {
                    displayCase.AdvanceAnimation(delta);
                    interaction.AdvanceAnimation(delta);
                });
            float frontError = Quaternion.Angle(
                Quaternion.identity,
                displayCase.ContentOrbitRotation);
            float frontImageRange = recorder.Keyframe(
                keysOutput,
                "01_front_readable.png");

            Run(recorder, PremiumDisplayCase.FrontReadableHoldSeconds,
                displayCase.AdvanceAnimation);
            Run(recorder, profile.ContentOptions.IdleRotationPeriodSeconds * 0.5f,
                displayCase.AdvanceAnimation);
            recorder.Keyframe(keysOutput, "02_flip_back.png");
            Run(recorder, profile.ContentOptions.IdleRotationPeriodSeconds * 0.5f,
                displayCase.AdvanceAnimation);
            recorder.Keyframe(keysOutput, "03_flip_front_restored.png");

            RunOrbit(recorder, interaction, true, keysOutput);
            RunOrbit(recorder, interaction, false, keysOutput);
            interaction.ResetInteraction();

            interaction.PlayExplode();
            Run(recorder, PremiumDisplayCaseExplodedLayout.AssemblyDurationSeconds,
                interaction.AdvanceAnimation);
            bool explodeCompleted = Mathf.Abs(interaction.ExplodedProgress - 1f)
                < 0.0001f;
            recorder.Keyframe(keysOutput, "08_exploded.png");

            displayCase.play();
            interaction.PlayAssembly();
            Run(recorder, PremiumDisplayCaseRevealMotion.DurationSeconds,
                delta =>
                {
                    displayCase.AdvanceAnimation(delta);
                    interaction.AdvanceAnimation(delta);
                });
            float restoredError = 0f;
            for (int index = 0; index < layers.Length; index++)
            {
                restoredError = Mathf.Max(restoredError, Vector3.Distance(
                    layers[index].localPosition,
                    assembled[index]));
            }
            bool replayRestored = Mathf.Abs(interaction.ExplodedProgress) < 0.0001f
                && restoredError < 0.00001f;
            recorder.Keyframe(keysOutput, "09_replay_restored.png");

            var validation = new ProductValidation
            {
                modelId = product.ModelId,
                scenePath = product.ScenePath,
                sourceRoot = profile.SceneRootName,
                capsule = profile.CapsulePreset.ToString(),
                initialEuler = Format(profile.ContentOptions.InitialEulerAngles),
                idlePeriodSeconds = profile.ContentOptions.IdleRotationPeriodSeconds,
                sourceRendererCount = sourceRenderers.Length,
                snapshotRendererCount = snapshotRenderers.Length,
                snapshotRendererNames = snapshotNames,
                fitScale = Format(displayCase.ContentFitScale),
                fitOffset = Format(displayCase.ContentFitPosition),
                frontAngleErrorDegrees = frontError,
                frontImageLuminanceRange = frontImageRange,
                restoredLayerErrorMeters = restoredError,
                rendererSetClean = rendererSetClean,
                entranceFrontReadable = frontError < 0.1f,
                explodeCompleted = explodeCompleted,
                replayRestored = replayRestored
            };
            validation.passed = validation.snapshotRendererCount > 0
                && validation.rendererSetClean
                && validation.entranceFrontReadable
                && validation.frontImageLuminanceRange > 0.10f
                && validation.explodeCompleted
                && validation.replayRestored
                && displayCase.ContentFitScale.x > 0f
                && float.IsFinite(displayCase.ContentFitScale.x);

            displayCase.setContent((Transform)null);
            bool dismissRestored = canonical.transform.parent == null
                && !canonical.activeSelf;
            validation.passed &= dismissRestored;
            File.WriteAllText(
                Path.Combine(productOutput, "validation.json"),
                JsonUtility.ToJson(validation, true));
            UnityEngine.Object.DestroyImmediate(displayCase.gameObject);
            UnityEngine.Object.DestroyImmediate(canonical);
            Debug.Log(
                $"Dynamic display-case capture {product.ModelId}: "
                + $"passed={validation.passed}, frames={recorder.FrameCount}");
            return validation;
        }

        private static void RunOrbit(
            FrameRecorder recorder,
            PremiumDisplayCaseInteractionController interaction,
            bool horizontal,
            string keysOutput)
        {
            float positive = horizontal ? 28f : 16f;
            float negative = -positive;
            AnimateOrbit(recorder, interaction, horizontal, 0f, positive, 0.45f);
            recorder.Keyframe(keysOutput,
                horizontal ? "04_drag_horizontal_right.png" : "06_drag_vertical_down.png");
            AnimateOrbit(recorder, interaction, horizontal, positive, negative, 0.90f);
            recorder.Keyframe(keysOutput,
                horizontal ? "05_drag_horizontal_left.png" : "07_drag_vertical_up.png");
            AnimateOrbit(recorder, interaction, horizontal, negative, 0f, 0.45f);
        }

        private static void AnimateOrbit(
            FrameRecorder recorder,
            PremiumDisplayCaseInteractionController interaction,
            bool horizontal,
            float from,
            float to,
            float seconds)
        {
            Run(recorder, seconds, (delta, normalized) =>
            {
                float value = Mathf.Lerp(from, to, normalized);
                interaction.SetOrbitDegrees(
                    horizontal ? value : 0f,
                    horizontal ? 0f : value);
            });
        }

        private static void Run(
            FrameRecorder recorder,
            float seconds,
            Action<float> advance)
        {
            Run(recorder, seconds, (delta, normalized) => advance(delta));
        }

        private static void Run(
            FrameRecorder recorder,
            float seconds,
            Action<float, float> advance)
        {
            float elapsed = 0f;
            while (elapsed < seconds - 0.000001f)
            {
                float delta = Mathf.Min(FrameStep, seconds - elapsed);
                elapsed += delta;
                advance(delta, Mathf.Clamp01(elapsed / seconds));
                recorder.Frame();
            }
        }

        private static Transform[] DisplayLayers(PremiumDisplayCase displayCase)
        {
            string[] names =
            {
                "Layer_01_FrontPlate",
                "Layer_02_Fasteners",
                "Layer_03_SpacerFrame",
                "Layer_04_Capsule",
                "Layer_05_VelvetInsert",
                "Layer_06_RearPlate",
                "Layer_07_OuterTray",
                "Layer_08_BoxLid"
            };
            Transform[] transforms = displayCase.GetComponentsInChildren<Transform>(
                true);
            return names.Select(name => transforms.Single(item => item.name == name))
                .ToArray();
        }

        private static void CreateEnvironment()
        {
            GameObject root = new GameObject("DynamicCaptureEnvironment");
            GameObject cameraObject = new GameObject("DynamicDisplayCaseCamera");
            cameraObject.transform.SetParent(root.transform, false);
            cameraObject.tag = "MainCamera";
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.34f, 0.045f, 0.17f, 1f);
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.allowHDR = true;
            camera.allowMSAA = false;

            GameObject ambient = new GameObject("DynamicAmbientLight");
            ambient.transform.SetParent(root.transform, false);
            Light light = ambient.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = new Color(0.88f, 0.48f, 0.70f);
            light.intensity = 0.10f;
            ambient.transform.rotation = Quaternion.Euler(42f, -28f, 0f);
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.055f, 0.020f, 0.045f);
            RenderSettings.fog = false;
        }

        private static string Format(Vector3 value)
        {
            return string.Format(
                CultureInfo.InvariantCulture,
                "({0:F6},{1:F6},{2:F6})",
                value.x,
                value.y,
                value.z);
        }

        private sealed class FrameRecorder : IDisposable
        {
            private readonly Camera camera;
            private readonly string output;
            private readonly RenderTexture target;
            private readonly Texture2D texture;
            private readonly RenderTexture previousTarget;
            private readonly RenderTexture previousActive;

            public FrameRecorder(Camera camera, string output)
            {
                this.camera = camera;
                this.output = output;
                previousTarget = camera.targetTexture;
                previousActive = RenderTexture.active;
                target = new RenderTexture(
                    FrameWidth,
                    FrameHeight,
                    24,
                    RenderTextureFormat.ARGB32,
                    RenderTextureReadWrite.sRGB)
                {
                    antiAliasing = 1,
                    name = "DisplayCaseDynamicCaptureRT"
                };
                target.Create();
                texture = new Texture2D(
                    FrameWidth,
                    FrameHeight,
                    TextureFormat.RGBA32,
                    false,
                    false);
                camera.targetTexture = target;
                RenderTexture.active = target;
            }

            public int FrameCount { get; private set; }

            public void Frame()
            {
                Write(Path.Combine(output, $"frame-{FrameCount:0000}.png"));
                FrameCount++;
            }

            public float Keyframe(string directory, string filename)
            {
                return Write(Path.Combine(directory, filename));
            }

            private float Write(string path)
            {
                camera.Render();
                RenderTexture.active = target;
                texture.ReadPixels(
                    new Rect(0, 0, FrameWidth, FrameHeight),
                    0,
                    0);
                texture.Apply(false, false);
                File.WriteAllBytes(path, texture.EncodeToPNG());
                Color32[] pixels = texture.GetPixels32();
                float minimum = 1f;
                float maximum = 0f;
                for (int index = 0; index < pixels.Length; index += 64)
                {
                    Color32 pixel = pixels[index];
                    float luminance = (0.2126f * pixel.r
                            + 0.7152f * pixel.g
                            + 0.0722f * pixel.b)
                        / 255f;
                    minimum = Mathf.Min(minimum, luminance);
                    maximum = Mathf.Max(maximum, luminance);
                }
                return maximum - minimum;
            }

            public void Dispose()
            {
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                target.Release();
                UnityEngine.Object.DestroyImmediate(texture);
                UnityEngine.Object.DestroyImmediate(target);
            }
        }
    }
}
