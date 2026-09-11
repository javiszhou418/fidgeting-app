using System;
using System.Collections.Generic;
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
    /// Renders label and backplate finish candidates for the shipping
    /// collector slab so a direction can be chosen before Gate 07 materials
    /// change. The approved Gate 12 R004 scene is opened read-only: this
    /// capture never calls the Gate 12 builder, never saves the scene, and
    /// never writes a material asset, so the shipping material set cannot
    /// drift while options are being compared.
    /// </summary>
    public static class SlabLabelBackplatePreviewCapture
    {
        private const string RevisionFolderName = "slab-label-backplate-r001";
        private const int CaptureWidth = 820;
        private const int CaptureHeight = 1000;

        /// <summary>The macro view is where the finish is actually judged, so
        /// it is rendered at twice the standard size.</summary>
        private const int MacroWidth = 1640;
        private const int MacroHeight = 2000;
        private const string LabelObjectName = "PhysicalLabel";
        private const string InsertObjectName = "TactileBackgroundInsert";

        private static readonly string[] LabelTextObjectNames =
        {
            "AuthoritativeProductName",
            "AuthoritativeEditionFinish",
            "AuthoritativeAcquiredDate",
            "AuthoritativeRarityLevel",
            "AuthoritativeCollectibleId"
        };

        /// <summary>Ink for a dark label, matching the authored hierarchy.</summary>
        private static readonly Color[] LightInk =
        {
            new Color(0.94f, 0.91f, 0.84f, 1f),
            new Color(0.86f, 0.84f, 0.79f, 1f),
            new Color(0.80f, 0.79f, 0.76f, 1f),
            new Color(0.92f, 0.90f, 0.85f, 1f),
            new Color(0.74f, 0.73f, 0.70f, 1f)
        };

        /// <summary>Ink for a light label, keeping the same field hierarchy.</summary>
        private static readonly Color[] DarkInk =
        {
            new Color(0.11f, 0.10f, 0.09f, 1f),
            new Color(0.22f, 0.21f, 0.19f, 1f),
            new Color(0.30f, 0.29f, 0.26f, 1f),
            new Color(0.13f, 0.12f, 0.11f, 1f),
            new Color(0.36f, 0.35f, 0.32f, 1f)
        };

        private enum LabelPattern
        {
            None,
            StoneSpeckle,
            NarrowFoilBand
        }

        private readonly struct View
        {
            public View(
                string fileName,
                Vector3 position,
                Vector3 lookAt,
                Vector3 up,
                float fieldOfView)
            {
                FileName = fileName;
                Position = position;
                LookAt = lookAt;
                Up = up;
                FieldOfView = fieldOfView;
            }

            public string FileName { get; }
            public Vector3 Position { get; }
            public Vector3 LookAt { get; }
            public Vector3 Up { get; }
            public float FieldOfView { get; }
        }

        /// <summary>Gate 12 R004 standard views, copied so every candidate
        /// shares the framing the approved evidence already uses. The label
        /// macro view is computed from the label bounds instead, so it frames
        /// the strip itself rather than a hand-guessed point.</summary>
        private const string LabelMacroViewName = "label-macro";

        private static readonly View[] Views =
        {
            new View(
                "hero",
                new Vector3(0.33f, 0.185f, -0.69f),
                new Vector3(0f, 0.008f, 0f),
                Vector3.up,
                28.5f),
            new View(
                "top",
                new Vector3(0f, 0.64f, -0.05f),
                Vector3.zero,
                Vector3.forward,
                31f),
            new View(
                "left-oblique",
                new Vector3(-0.36f, 0.12f, -0.64f),
                new Vector3(0f, 0.008f, 0f),
                Vector3.up,
                29f),
            new View(
                "right-oblique",
                new Vector3(0.36f, 0.12f, -0.64f),
                new Vector3(0f, 0.008f, 0f),
                Vector3.up,
                29f),
            new View(
                "low",
                new Vector3(0.27f, -0.22f, -0.64f),
                new Vector3(0f, 0.012f, 0f),
                Vector3.up,
                29f)
        };

        private static readonly string[] SheetViewNames =
            Views.Select(view => view.FileName)
                .Concat(new[] { LabelMacroViewName })
                .ToArray();

        private readonly struct Finish
        {
            public Finish(
                string id,
                bool shippingBaseline,
                bool labelReceivesLight,
                Color labelColor,
                float labelMetallic,
                float labelSmoothness,
                LabelPattern labelPattern,
                bool darkInk,
                Color insertColor,
                float insertSmoothness)
            {
                Id = id;
                ShippingBaseline = shippingBaseline;
                LabelReceivesLight = labelReceivesLight;
                LabelColor = labelColor;
                LabelMetallic = labelMetallic;
                LabelSmoothness = labelSmoothness;
                LabelPattern = labelPattern;
                DarkInk = darkInk;
                InsertColor = insertColor;
                InsertSmoothness = insertSmoothness;
            }

            public string Id { get; }

            /// <summary>Captured with no override at all, as the control.</summary>
            public bool ShippingBaseline { get; }

            /// <summary>
            /// The shipping label is URP Unlit, which renders a matte paper
            /// at exactly its authored value. Only a candidate whose look
            /// depends on sheen or metal moves to URP Lit, where this scene's
            /// key light pushes a paper value near white.
            /// </summary>
            public bool LabelReceivesLight { get; }

            public Color LabelColor { get; }
            public float LabelMetallic { get; }
            public float LabelSmoothness { get; }
            public LabelPattern LabelPattern { get; }
            public bool DarkInk { get; }
            public Color InsertColor { get; }
            public float InsertSmoothness { get; }
        }

        private static readonly Finish[] Finishes =
        {
            new Finish(
                "00-current",
                true,
                false,
                default,
                0f,
                0f,
                LabelPattern.None,
                false,
                default,
                0f),
            new Finish(
                "a-archive-paper-flocking",
                false,
                false,
                Hex(0xBD, 0xB8, 0xAD),
                0f,
                0.27f,
                LabelPattern.None,
                true,
                Hex(0x05, 0x06, 0x09),
                0.14f),
            new Finish(
                "b-graphite-deboss-microsuede",
                false,
                true,
                Hex(0x0E, 0x0F, 0x11),
                0f,
                0.48f,
                LabelPattern.None,
                false,
                Hex(0x0E, 0x11, 0x14),
                0.12f),
            new Finish(
                "c-narrow-foil-ink-flocking",
                false,
                false,
                Hex(0xBD, 0xB8, 0xAD),
                0f,
                0.27f,
                LabelPattern.NarrowFoilBand,
                true,
                Hex(0x04, 0x06, 0x0B),
                0.10f),
            new Finish(
                "d-stone-paper-graphite-felt",
                false,
                false,
                Hex(0xE4, 0xE0, 0xD8),
                0f,
                0.20f,
                LabelPattern.StoneSpeckle,
                true,
                Hex(0x16, 0x17, 0x1A),
                0.07f),
            new Finish(
                "e-anodized-plate-velvet",
                false,
                true,
                Hex(0x6E, 0x73, 0x78),
                0.90f,
                0.62f,
                LabelPattern.None,
                false,
                Hex(0x0B, 0x15, 0x12),
                0.14f)
        };

        [MenuItem("Fidgeting/Display Case/Gate 12/Capture Slab Label And Backplate Options")]
        public static void CaptureAll()
        {
            string folder = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../../../Artifacts/DisplayCaseSlabMaterials",
                RevisionFolderName));
            Directory.CreateDirectory(folder);

            var diagnostics = new List<string>();
            foreach (Finish finish in Finishes)
            {
                diagnostics.Add(CaptureFinish(finish, folder));
            }

            foreach (string view in SheetViewNames)
            {
                ComposeSheet(view, folder);
            }

            WriteReport(folder, diagnostics);
            AssetDatabase.Refresh();
            Debug.Log(
                "[FidgetingApp] Captured slab label and backplate options: " + folder);
        }

        private static string CaptureFinish(Finish finish, string folder)
        {
            // Reopened per candidate so no material or ink override can bleed
            // into the next one. The scene is never saved.
            Scene scene = EditorSceneManager.OpenScene(
                PremiumDisplayCaseGate12Builder.ShippingScenePath,
                OpenSceneMode.Single);
            GameObject[] roots = scene.GetRootGameObjects();
            Camera camera = roots
                .SelectMany(root => root.GetComponentsInChildren<Camera>(true))
                .Single();
            PremiumDisplayCaseShippingPresentation presentation = roots
                .SelectMany(root => root
                    .GetComponentsInChildren<PremiumDisplayCaseShippingPresentation>(true))
                .Single();
            MeshRenderer[] renderers = roots
                .SelectMany(root => root.GetComponentsInChildren<MeshRenderer>(true))
                .ToArray();
            MeshRenderer label = Renderer(renderers, LabelObjectName);
            MeshRenderer insert = Renderer(renderers, InsertObjectName);

            presentation.SetTimeForPreview(
                presentation.RevealProfile.TotalDurationSeconds);
            if (!finish.ShippingBaseline)
            {
                label.sharedMaterial = BuildLabelMaterial(finish, label.sharedMaterial);
                insert.sharedMaterial = BuildInsertMaterial(finish, insert.sharedMaterial);
                ApplyInk(roots, finish);
            }

            foreach (View view in Views)
            {
                Capture(
                    camera,
                    view,
                    Path.Combine(folder, $"{finish.Id}-{view.FileName}.png"),
                    CaptureWidth,
                    CaptureHeight);
            }

            Capture(
                camera,
                LabelMacroView(label),
                Path.Combine(folder, $"{finish.Id}-{LabelMacroViewName}.png"),
                MacroWidth,
                MacroHeight);

            return Describe(finish, label, insert);
        }

        /// <summary>
        /// Frames the label strip from its own world bounds, so the macro
        /// view stays correct if the label ever moves or resizes.
        /// </summary>
        private static View LabelMacroView(MeshRenderer label)
        {
            const float fieldOfView = 26f;
            const float margin = 1.30f;
            Bounds bounds = label.bounds;
            float aspect = (float)CaptureWidth / CaptureHeight;
            float fitHalfHeight = Mathf.Max(
                bounds.extents.y,
                bounds.extents.x / aspect) * margin;
            float distance = fitHalfHeight
                / Mathf.Tan(fieldOfView * 0.5f * Mathf.Deg2Rad);
            // Slightly above and right of the label so a foil band or a
            // brushed plate shows its sweep instead of a flat fill.
            Vector3 direction = new Vector3(0.10f, 0.18f, -1f).normalized;
            return new View(
                LabelMacroViewName,
                bounds.center + direction * distance,
                bounds.center,
                Vector3.up,
                fieldOfView);
        }

        private static Material BuildLabelMaterial(Finish finish, Material shipping)
        {
            Shader shader = finish.LabelReceivesLight
                ? RequireShader("Universal Render Pipeline/Lit")
                : shipping.shader;
            var material = new Material(shader)
            {
                name = "SlabLabelPreview_" + finish.Id
            };
            if (shader == shipping.shader)
            {
                material.CopyPropertiesFromMaterial(shipping);
            }

            material.SetColor("_BaseColor", finish.LabelColor);
            material.SetColor("_Color", finish.LabelColor);
            material.SetColor("_EmissionColor", Color.black);
            material.SetFloat("_Metallic", finish.LabelMetallic);
            material.SetFloat("_Smoothness", finish.LabelSmoothness);
            material.SetFloat("_Glossiness", finish.LabelSmoothness);
            material.renderQueue = shipping.renderQueue;
            Texture2D pattern = BuildPattern(finish);
            if (pattern != null)
            {
                material.SetTexture("_BaseMap", pattern);
                material.SetTexture("_MainTex", pattern);
            }

            return material;
        }

        private static Material BuildInsertMaterial(Finish finish, Material shipping)
        {
            var material = new Material(shipping.shader)
            {
                name = "SlabInsertPreview_" + finish.Id
            };
            material.CopyPropertiesFromMaterial(shipping);
            material.SetColor("_BaseColor", finish.InsertColor);
            material.SetColor("_Color", finish.InsertColor);
            material.SetFloat("_Smoothness", finish.InsertSmoothness);
            material.SetFloat("_Glossiness", finish.InsertSmoothness);
            material.SetFloat("_Metallic", 0f);
            material.renderQueue = shipping.renderQueue;
            return material;
        }

        /// <summary>
        /// Approximates a candidate's print pattern in albedo only. Real
        /// speckle relief and a real foil band need an authored base and
        /// normal map at Gate 07; these previews only judge value and hue.
        /// </summary>
        private static Texture2D BuildPattern(Finish finish)
        {
            if (finish.LabelPattern == LabelPattern.None)
            {
                return null;
            }

            const int size = 512;
            var texture = new Texture2D(size, size, TextureFormat.RGBA32, false, false)
            {
                name = "SlabLabelPattern_" + finish.Id,
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Bilinear
            };
            var pixels = new Color[size * size];
            var random = new System.Random(0x51AB);
            for (int index = 0; index < pixels.Length; index++)
            {
                pixels[index] = Color.white;
            }

            if (finish.LabelPattern == LabelPattern.StoneSpeckle)
            {
                // Roughly 0.4 mm flecks across the 184 mm strip. Coarser or
                // darker than this and the paper reads as dust, not stone.
                int flecks = size * size / 260;
                for (int fleck = 0; fleck < flecks; fleck++)
                {
                    int x = random.Next(size);
                    int y = random.Next(size);
                    int radius = 1 + random.Next(2);
                    float shade = 0.62f + (float)random.NextDouble() * 0.26f;
                    var tint = new Color(shade, shade * 0.96f, shade * 0.88f, 1f);
                    Blot(pixels, size, x, y, radius, tint);
                }
            }
            else
            {
                // A 6 mm band on a 58 mm label strip, centred low so the
                // printed fields stay above it.
                const float bandCentre = 0.66f;
                const float bandHalf = 6f / 58f * 0.5f;
                for (int y = 0; y < size; y++)
                {
                    float v = (y + 0.5f) / size;
                    if (Mathf.Abs(v - bandCentre) > bandHalf)
                    {
                        continue;
                    }

                    for (int x = 0; x < size; x++)
                    {
                        // Broad sweep standing in for brushed anisotropy.
                        float u = (x + 0.5f) / size;
                        float sweep = 0.52f + 0.46f * Mathf.Pow(
                            Mathf.Cos((u - 0.34f) * Mathf.PI * 1.05f),
                            2f);
                        pixels[y * size + x] = new Color(
                            sweep,
                            sweep * 1.01f,
                            sweep * 1.04f,
                            1f);
                    }
                }
            }

            texture.SetPixels(pixels);
            texture.Apply(false, false);
            return texture;
        }

        private static void Blot(
            Color[] pixels,
            int size,
            int centreX,
            int centreY,
            int radius,
            Color tint)
        {
            for (int y = centreY - radius; y <= centreY + radius; y++)
            {
                for (int x = centreX - radius; x <= centreX + radius; x++)
                {
                    if (x < 0 || y < 0 || x >= size || y >= size)
                    {
                        continue;
                    }

                    int dx = x - centreX;
                    int dy = y - centreY;
                    if (dx * dx + dy * dy > radius * radius)
                    {
                        continue;
                    }

                    pixels[y * size + x] = tint;
                }
            }
        }

        /// <summary>
        /// Ink follows the label value, otherwise a light label would render
        /// the approved light text unreadable and hide the real trade-off.
        /// </summary>
        private static void ApplyInk(GameObject[] roots, Finish finish)
        {
            Color[] ink = finish.DarkInk ? DarkInk : LightInk;
            TextMesh[] texts = roots
                .SelectMany(root => root.GetComponentsInChildren<TextMesh>(true))
                .ToArray();
            for (int index = 0; index < LabelTextObjectNames.Length; index++)
            {
                TextMesh text = texts.SingleOrDefault(
                    candidate => candidate.name == LabelTextObjectNames[index]);
                if (text == null)
                {
                    continue;
                }

                text.color = ink[index];
            }
        }

        private static string Describe(
            Finish finish,
            MeshRenderer label,
            MeshRenderer insert)
        {
            Mesh labelMesh = label.GetComponent<MeshFilter>()?.sharedMesh;
            Vector2 uvMin = Vector2.zero;
            Vector2 uvMax = Vector2.zero;
            int uvCount = 0;
            if (labelMesh != null && labelMesh.uv != null && labelMesh.uv.Length > 0)
            {
                Vector2[] uv = labelMesh.uv;
                uvCount = uv.Length;
                uvMin = uv[0];
                uvMax = uv[0];
                foreach (Vector2 coordinate in uv)
                {
                    uvMin = Vector2.Min(uvMin, coordinate);
                    uvMax = Vector2.Max(uvMax, coordinate);
                }
            }

            // Read back from the materials actually rendered, so the report
            // cannot claim a value the capture did not use.
            Material labelMaterial = label.sharedMaterial;
            Material insertMaterial = insert.sharedMaterial;
            string labelMetallic = Number(Property(labelMaterial, "_Metallic"));
            string labelSmoothness = Number(Property(labelMaterial, "_Smoothness"));
            string labelBaseMap = Bool(labelMaterial.GetTexture("_BaseMap") != null);
            string insertSmoothness = Number(Property(insertMaterial, "_Smoothness"));
            return "    {"
                + $"\"id\":\"{finish.Id}\","
                + $"\"shippingBaseline\":{Bool(finish.ShippingBaseline)},"
                + $"\"labelShader\":\"{labelMaterial.shader.name}\","
                + $"\"labelReceivesLight\":{Bool(finish.LabelReceivesLight)},"
                + $"\"labelColor\":\"{Hex(labelMaterial)}\","
                + $"\"labelMetallic\":{labelMetallic},"
                + $"\"labelSmoothness\":{labelSmoothness},"
                + $"\"labelPattern\":\"{finish.LabelPattern}\","
                + $"\"labelBaseMap\":{labelBaseMap},"
                + $"\"labelUvCount\":{uvCount},"
                + $"\"labelUvMin\":[{Number(uvMin.x)},{Number(uvMin.y)}],"
                + $"\"labelUvMax\":[{Number(uvMax.x)},{Number(uvMax.y)}],"
                + $"\"insertShader\":\"{insertMaterial.shader.name}\","
                + $"\"insertColor\":\"{Hex(insertMaterial)}\","
                + $"\"insertSmoothness\":{insertSmoothness}"
                + "}";
        }

        private static void WriteReport(string folder, IEnumerable<string> diagnostics)
        {
            File.WriteAllText(
                Path.Combine(folder, "slab-material-options-report.json"),
                "{\n"
                + "  \"source\":\"canonical unity/FidgetingApp\",\n"
                + $"  \"scene\":\"{PremiumDisplayCaseGate12Builder.ShippingScenePath}\",\n"
                + $"  \"prefab\":\"{PremiumDisplayCaseGate12Builder.ShippingPrefabPath}\",\n"
                + "  \"builderExecuted\":false,\n"
                + "  \"sceneSaved\":false,\n"
                + "  \"materialAssetsWritten\":false,\n"
                + "  \"wholeAssembledCaseOnly\":true,\n"
                + "  \"toyCallerOwned\":true,\n"
                + "  \"patternApproximatedInAlbedoOnly\":true,\n"
                + "  \"designApproved\":false,\n"
                + "  \"physicalPhoneInstalled\":false,\n"
                + "  \"candidates\":[\n"
                + string.Join(",\n", diagnostics)
                + "\n  ]\n"
                + "}\n");
        }

        private static void ComposeSheet(string view, string folder)
        {
            const int gutter = 10;
            int cellWidth = 280;
            int cellHeight = 341;
            int columns = Finishes.Length;
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
            for (int index = 0; index < Finishes.Length; index++)
            {
                string path = Path.Combine(
                    folder,
                    $"{Finishes[index].Id}-{view}.png");
                if (!File.Exists(path))
                {
                    continue;
                }

                var source = new Texture2D(2, 2, TextureFormat.RGBA32, false);
                source.LoadImage(File.ReadAllBytes(path), false);
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

                UnityEngine.Object.DestroyImmediate(source);
            }

            sheet.Apply(false, false);
            File.WriteAllBytes(
                Path.Combine(folder, $"sheet-{view}.png"),
                sheet.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(sheet);
        }

        private static void Capture(
            Camera camera,
            View view,
            string outputPath,
            int width,
            int height)
        {
            camera.transform.position = view.Position;
            camera.transform.rotation = Quaternion.LookRotation(
                view.LookAt - view.Position,
                view.Up);
            camera.fieldOfView = view.FieldOfView;
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            var target = new RenderTexture(
                width,
                height,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB);
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
                // Submitted twice so the first frame's uninitialised shadow
                // and reflection state cannot land in the saved image.
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
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
                UnityEngine.Object.DestroyImmediate(target);
                UnityEngine.Object.DestroyImmediate(image);
            }
        }

        private static MeshRenderer Renderer(MeshRenderer[] renderers, string objectName)
        {
            MeshRenderer match = renderers.SingleOrDefault(
                renderer => renderer.name == objectName);
            if (match == null)
            {
                throw new InvalidDataException(
                    "Slab preview could not find renderer: " + objectName);
            }

            return match;
        }

        private static Shader RequireShader(string name)
        {
            Shader shader = Shader.Find(name);
            if (shader == null)
            {
                throw new MissingReferenceException("Shader unavailable: " + name);
            }

            return shader;
        }

        private static Color Hex(int red, int green, int blue)
        {
            return new Color(red / 255f, green / 255f, blue / 255f, 1f);
        }

        private static string Hex(Material material)
        {
            return ColorUtility.ToHtmlStringRGB(material.GetColor("_BaseColor"));
        }

        private static float Property(Material material, string name)
        {
            return material.HasProperty(name) ? material.GetFloat(name) : 0f;
        }

        private static string Bool(bool value)
        {
            return value ? "true" : "false";
        }

        private static string Number(float value)
        {
            return value.ToString("0.###", CultureInfo.InvariantCulture);
        }
    }
}
