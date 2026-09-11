using System.Collections.Generic;
using System.IO;
using CodexUnityLab;
using FidgetingApp.Product;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FidgetingApp.Editor
{
    /// <summary>
    /// Renders hub finger-cap size and matte-material candidates for the rotor
    /// products so the user can pick a diameter before any source change.
    /// Cameras are placed explicitly here instead of using the authored
    /// framers, so every variant of a model shares one comparable framing.
    /// This capture never saves a scene, mesh, or material asset.
    /// </summary>
    public static class HubCapSizePreviewCapture
    {
        private const int Width = 1000;
        private const int Height = 1000;
        private const string RevisionFolderName = "hub-cap-facets-r005";
        private const int AuthoredWidth = 900;
        private const int AuthoredHeight = 1600;
        private const float FieldOfView = 30f;

        /// <summary>Renderers excluded when measuring the product bounds.</summary>
        private static readonly string[] EnvironmentNameFragments =
        {
            "Environment",
            "Background",
            "Backdrop",
            "Starfield",
            "Foreground",
            "Midground",
            "GroundingStage",
            "CenterSupport",
            "Plate",
            "Shadow",
            "Glow"
        };

        private readonly struct CapModel
        {
            public CapModel(
                string modelId,
                string scenePath,
                string[] capAssemblyNames,
                string[] capFaceNames,
                string[] hubRingNames,
                float referenceSpanMeters,
                float currentCapDiameterMeters,
                CapVariant[] variants)
            {
                ModelId = modelId;
                ScenePath = scenePath;
                CapAssemblyNames = capAssemblyNames;
                CapFaceNames = capFaceNames;
                HubRingNames = hubRingNames;
                ReferenceSpanMeters = referenceSpanMeters;
                CurrentCapDiameterMeters = currentCapDiameterMeters;
                Variants = variants;
            }

            public string ModelId { get; }
            public string ScenePath { get; }

            /// <summary>Transforms scaled on X/Z so cap thickness is preserved.</summary>
            public string[] CapAssemblyNames { get; }

            /// <summary>Renderers that receive the matte candidate override.</summary>
            public string[] CapFaceNames { get; }

            /// <summary>
            /// Rotor core, races, shields, balls, and washers. These keep their
            /// own diameter, so a smaller cap exposes them as a chrome ring.
            /// </summary>
            public string[] HubRingNames { get; }

            public float ReferenceSpanMeters { get; }
            public float CurrentCapDiameterMeters { get; }
            public CapVariant[] Variants { get; }
        }

        private readonly struct CapVariant
        {
            public CapVariant(
                string label,
                float spanFraction,
                bool matteCap,
                bool matteRings,
                bool dimHighlights)
            {
                Label = label;
                SpanFraction = spanFraction;
                MatteCap = matteCap;
                MatteRings = matteRings;
                DimHighlights = dimHighlights;
            }

            public string Label { get; }

            /// <summary>Target cap diameter as a fraction of the model span.</summary>
            public float SpanFraction { get; }

            public bool MatteCap { get; }
            public bool MatteRings { get; }
            public bool DimHighlights { get; }
        }

        private static readonly CapVariant[] MetalVariants =
        {
            new CapVariant("a-current", 0f, false, false, false),
            new CapVariant("b-facet-restore", 0f, false, false, true)
        };

        private static readonly CapVariant[] TwoLobeVariants =
        {
            new CapVariant("a-current", 0f, false, false, false),
            new CapVariant("b-highlight-dimmed", 0f, false, false, true)
        };

        private static readonly string[] SharedRingNames =
        {
            "RotorCore",
            "BearingOuterRace",
            "BearingInnerRace",
            "BearingVisual",
            "BearingBalls",
            "BearingShield_Top",
            "BearingShield_Bottom",
            "TopWasher",
            "BottomWasher",
            "BearingBall_01",
            "BearingBall_02",
            "BearingBall_03",
            "BearingBall_04",
            "BearingBall_05",
            "BearingBall_06",
            "BearingBall_07",
            "BearingBall_08",
            "BearingBall_09",
            "BearingBall_10"
        };

        private static readonly CapModel[] Models =
        {
            new CapModel(
                "gold-four-wing",
                SpinnerEnvironmentCatalog.ImportedScenePath,
                new[] { "TopCap_Root", "BottomCap_Root" },
                new[]
                {
                    "FingerCapTop_RadialFace",
                    "FingerCapBottom_RadialFace",
                    "FingerCap_Top",
                    "FingerCap_Bottom"
                },
                SharedRingNames,
                0.085f,
                0.0442f,
                MetalVariants),
            new CapModel(
                "metal-three-blade",
                SpinnerEnvironmentCatalog.MetalScenePath,
                new[] { "TopCap_Root", "BottomCap_Root" },
                new[]
                {
                    "FingerCapTop_BrushedFace",
                    "FingerCapBottom_BrushedFace",
                    "FingerCap_Top",
                    "FingerCap_Bottom"
                },
                SharedRingNames,
                0.085f,
                0.0442f,
                MetalVariants),
            new CapModel(
                "pointed-three-blade",
                SpinnerEnvironmentCatalog.PointedScenePath,
                new[] { "TopCap", "BottomCap" },
                new[] { "TopCap", "BottomCap" },
                SharedRingNames,
                0.085f,
                0.0344f,
                MetalVariants),
            new CapModel(
                "graphite-two-lobe",
                SpinnerEnvironmentCatalog.TwoLobeScenePath,
                new[] { "TopButton", "BottomButton" },
                new[] { "TopButton", "BottomButton" },
                SharedRingNames,
                0.050f,
                0.0240f,
                TwoLobeVariants)
        };

        private static readonly string[] ViewNames =
        {
            "authored",
            "top",
            "hub",
            "oblique"
        };

        [MenuItem("Fidgeting/Product/Capture Hub Cap Size Comparison")]
        public static void CaptureAll()
        {
            string folder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../../../Artifacts/EnvironmentIntegration",
                RevisionFolderName));
            Directory.CreateDirectory(folder);

            foreach (CapModel model in Models)
            {
                foreach (CapVariant variant in model.Variants)
                {
                    CaptureVariant(model, variant, folder);
                }

                foreach (string view in ViewNames)
                {
                    ComposeModelSheet(model, view, folder);
                }
            }

            Debug.Log(
                "[FidgetingApp] Captured hub cap size comparison previews: " + folder);
        }

        private static void CaptureVariant(
            CapModel model,
            CapVariant variant,
            string folder)
        {
            EditorSceneManager.OpenScene(model.ScenePath, OpenSceneMode.Single);
            Camera camera = Camera.main ?? Object.FindAnyObjectByType<Camera>();
            if (camera == null)
            {
                throw new InvalidDataException(
                    "Hub cap preview camera missing: " + model.ScenePath);
            }

            // Measure before the presenter adds backdrop and stage renderers.
            if (!TryMeasureProduct(out Bounds product))
            {
                throw new InvalidDataException(
                    "Hub cap preview could not measure product: " + model.ScenePath);
            }

            ApplyCapScale(model, variant);

            SpinnerEnvironmentPresenter presenter =
                SpinnerEnvironmentPresenter.Install(model.ScenePath);
            if (presenter == null)
            {
                throw new InvalidDataException(
                    "Hub cap preview presenter failed: " + model.ScenePath);
            }

            // Library lighting is where the user saw the blown-out hub.
            presenter.SetLibraryPreviewActive(true, true);
            presenter.ImageBasedLighting?.SetViewResponse(
                Vector2.zero,
                false,
                0f,
                0f,
                0f);

            // Applied after Install so the shared soft-metal property block
            // cannot re-brighten the hub.
            if (variant.MatteCap)
            {
                ApplyMatteOverride(model.CapFaceNames);
            }

            if (variant.MatteRings)
            {
                ApplyMatteOverride(model.HubRingNames);
            }

            if (variant.DimHighlights)
            {
                DimHighlights();
            }

            float authoredFieldOfView = camera.fieldOfView;
            try
            {
                // The authored library pose is the one the user judges in the
                // app, and the only pose where two-lobe shows its hot specular.
                camera.aspect = (float)AuthoredWidth / AuthoredHeight;
                FrameAuthoredLibraryPose(camera);
                Render(
                    camera,
                    Path.Combine(folder, $"{model.ModelId}-{variant.Label}-authored.png"),
                    AuthoredWidth,
                    AuthoredHeight,
                    true);

                DisableAuthoredFramers(camera);
                camera.aspect = 1f;
                camera.fieldOfView = FieldOfView;
                camera.ResetProjectionMatrix();

                PlaceCamera(camera, product.center, 90f, model.ReferenceSpanMeters * 0.62f);
                Render(
                    camera,
                    Path.Combine(folder, $"{model.ModelId}-{variant.Label}-top.png"),
                    Width,
                    Height,
                    true);

                PlaceCamera(camera, product.center, 90f, model.ReferenceSpanMeters * 0.30f);
                Render(
                    camera,
                    Path.Combine(folder, $"{model.ModelId}-{variant.Label}-hub.png"),
                    Width,
                    Height,
                    false);

                PlaceCamera(camera, product.center, 35f, model.ReferenceSpanMeters * 0.62f);
                Render(
                    camera,
                    Path.Combine(folder, $"{model.ModelId}-{variant.Label}-oblique.png"),
                    Width,
                    Height,
                    false);
            }
            finally
            {
                camera.fieldOfView = authoredFieldOfView;
                camera.ResetProjectionMatrix();
            }
        }

        private static void FrameAuthoredLibraryPose(Camera camera)
        {
            PortraitCameraFramer portraitFramer =
                camera.GetComponent<PortraitCameraFramer>();
            if (portraitFramer != null)
            {
                portraitFramer.SetLibraryPreviewActive(true, true);
                portraitFramer.FrameNow();
            }

            OrbitPresentationCamera orbitCamera =
                camera.GetComponent<OrbitPresentationCamera>();
            if (orbitCamera != null)
            {
                orbitCamera.SetLibraryPreviewActive(true, true);
            }

            FidgetingApp.EDC.EdcPortraitCameraFramer edcFramer =
                camera.GetComponent<FidgetingApp.EDC.EdcPortraitCameraFramer>();
            if (edcFramer != null)
            {
                edcFramer.SetLibraryPreviewActive(true, true);
                edcFramer.FrameNow();
            }
        }

        private static bool TryMeasureProduct(out Bounds bounds)
        {
            bounds = default;
            bool hasBounds = false;
            MeshRenderer[] renderers = Object.FindObjectsByType<MeshRenderer>(
                FindObjectsInactive.Exclude,
                FindObjectsSortMode.None);
            foreach (MeshRenderer renderer in renderers)
            {
                if (IsEnvironmentRenderer(renderer))
                {
                    continue;
                }

                Bounds candidate = renderer.bounds;
                // Environment plates are far larger than any handheld product.
                if (candidate.extents.magnitude > 0.5f)
                {
                    continue;
                }

                if (!hasBounds)
                {
                    bounds = candidate;
                    hasBounds = true;
                }
                else
                {
                    bounds.Encapsulate(candidate);
                }
            }

            return hasBounds;
        }

        private static bool IsEnvironmentRenderer(MeshRenderer renderer)
        {
            string name = renderer.gameObject.name;
            foreach (string fragment in EnvironmentNameFragments)
            {
                if (name.IndexOf(fragment, System.StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    return true;
                }
            }

            return false;
        }

        private static void ApplyCapScale(CapModel model, CapVariant variant)
        {
            if (variant.SpanFraction <= 0f)
            {
                return;
            }

            float targetDiameter = model.ReferenceSpanMeters * variant.SpanFraction;
            float factor = targetDiameter / model.CurrentCapDiameterMeters;
            foreach (Transform candidate in FindByNames(model.CapAssemblyNames))
            {
                Vector3 scale = candidate.localScale;
                candidate.localScale = new Vector3(
                    scale.x * factor,
                    scale.y,
                    scale.z * factor);
            }
        }

        /// <summary>
        /// Approximates the candidate finish without recompiling shader
        /// variants, which batch-mode rendering would otherwise draw magenta.
        /// </summary>
        private static void ApplyMatteOverride(string[] names)
        {
            var block = new MaterialPropertyBlock();
            var matte = new Color(0.17f, 0.175f, 0.18f, 1f);
            block.SetColor("_BaseColor", matte);
            block.SetColor("_Color", matte);
            block.SetFloat("_Metallic", 0f);
            block.SetFloat("_Smoothness", 0.20f);
            block.SetFloat("_Glossiness", 0.20f);
            block.SetFloat("_SpecularHighlights", 0f);
            block.SetFloat("_EnvironmentReflections", 0f);

            foreach (Transform candidate in FindByNames(names))
            {
                var renderer = candidate.GetComponent<MeshRenderer>();
                if (renderer == null)
                {
                    continue;
                }

                renderer.SetPropertyBlock(block);
                for (int index = 0; index < renderer.sharedMaterials.Length; index++)
                {
                    renderer.SetPropertyBlock(block, index);
                }
            }
        }

        /// <summary>
        /// Two-lobe reads white from specular response, not from cap albedo or
        /// cap diameter, so its candidate only trims highlight energy.
        /// </summary>
        private static void DimHighlights()
        {
            RenderSettings.reflectionIntensity *= 0.45f;
            Light[] lights = Object.FindObjectsByType<Light>(
                FindObjectsInactive.Exclude,
                FindObjectsSortMode.None);
            foreach (Light light in lights)
            {
                if (light.gameObject.name.IndexOf(
                        "ViewResponsiveHighlight",
                        System.StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    light.enabled = false;
                    continue;
                }

                light.intensity *= 0.7f;
            }
        }

        private static List<Transform> FindByNames(string[] names)
        {
            var matches = new List<Transform>();
            Transform[] all = Object.FindObjectsByType<Transform>(
                FindObjectsInactive.Include,
                FindObjectsSortMode.None);
            foreach (Transform candidate in all)
            {
                foreach (string name in names)
                {
                    if (string.Equals(
                            candidate.gameObject.name,
                            name,
                            System.StringComparison.Ordinal))
                    {
                        matches.Add(candidate);
                        break;
                    }
                }
            }

            return matches;
        }

        private static void DisableAuthoredFramers(Camera camera)
        {
            foreach (MonoBehaviour behaviour in
                camera.GetComponents<MonoBehaviour>())
            {
                if (behaviour == null)
                {
                    continue;
                }

                string type = behaviour.GetType().Name;
                if (type.IndexOf("Framer", System.StringComparison.Ordinal) >= 0
                    || type.IndexOf("Orbit", System.StringComparison.Ordinal) >= 0)
                {
                    behaviour.enabled = false;
                }
            }
        }

        private static void PlaceCamera(
            Camera camera,
            Vector3 target,
            float elevationDegrees,
            float fitRadius)
        {
            float distance = fitRadius
                / Mathf.Tan(FieldOfView * 0.5f * Mathf.Deg2Rad);
            float elevation = elevationDegrees * Mathf.Deg2Rad;
            var direction = new Vector3(
                0f,
                Mathf.Sin(elevation),
                -Mathf.Cos(elevation));
            camera.transform.position = target + direction.normalized * distance;
            Vector3 up = elevationDegrees >= 89f ? Vector3.forward : Vector3.up;
            camera.transform.rotation = Quaternion.LookRotation(
                (target - camera.transform.position).normalized,
                up);
            camera.nearClipPlane = Mathf.Max(0.001f, distance * 0.05f);
            camera.farClipPlane = distance * 40f;
        }

        private static void ComposeModelSheet(
            CapModel model,
            string view,
            string folder)
        {
            var paths = new string[model.Variants.Length];
            for (int index = 0; index < model.Variants.Length; index++)
            {
                paths[index] = Path.Combine(
                    folder,
                    $"{model.ModelId}-{model.Variants[index].Label}-{view}.png");
            }

            bool authored = string.Equals(view, "authored", System.StringComparison.Ordinal);
            int cellWidth = authored ? 288 : 460;
            int cellHeight = authored ? 512 : 460;
            const int gutter = 10;
            int columns = model.Variants.Length;
            var sheet = new Texture2D(
                columns * cellWidth + (columns + 1) * gutter,
                cellHeight + 2 * gutter,
                TextureFormat.RGB24,
                false);
            var clear = new Color[sheet.width * sheet.height];
            for (int index = 0; index < clear.Length; index++)
            {
                clear[index] = new Color(0.06f, 0.06f, 0.07f, 1f);
            }

            sheet.SetPixels(clear);
            for (int index = 0; index < paths.Length; index++)
            {
                if (!File.Exists(paths[index]))
                {
                    continue;
                }

                var source = new Texture2D(2, 2, TextureFormat.RGBA32, false);
                source.LoadImage(File.ReadAllBytes(paths[index]), false);
                int originX = gutter + index * (cellWidth + gutter);
                for (int y = 0; y < cellHeight; y++)
                {
                    for (int x = 0; x < cellWidth; x++)
                    {
                        Color pixel = source.GetPixelBilinear(
                            (x + 0.5f) / cellWidth,
                            (y + 0.5f) / cellHeight);
                        sheet.SetPixel(originX + x, gutter + y, pixel);
                    }
                }

                Object.DestroyImmediate(source);
            }

            sheet.Apply(false, false);
            File.WriteAllBytes(
                Path.Combine(folder, $"{model.ModelId}-sheet-{view}.png"),
                sheet.EncodeToPNG());
            Object.DestroyImmediate(sheet);
        }

        private static void Render(
            Camera camera,
            string outputPath,
            int width,
            int height,
            bool warmup)
        {
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            var target = new RenderTexture(
                width,
                height,
                24,
                RenderTextureFormat.ARGB32);
            var image = new Texture2D(
                width,
                height,
                TextureFormat.RGBA32,
                false,
                false);
            try
            {
                target.Create();
                camera.targetTexture = target;
                var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest
                {
                    destination = target
                };
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                if (warmup)
                {
                    UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                }

                RenderTexture.active = target;
                image.ReadPixels(new Rect(0f, 0f, width, height), 0, 0);
                image.Apply(false, false);
                File.WriteAllBytes(outputPath, image.EncodeToPNG());
            }
            finally
            {
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                target.Release();
                Object.DestroyImmediate(target);
                Object.DestroyImmediate(image);
            }
        }
    }
}
