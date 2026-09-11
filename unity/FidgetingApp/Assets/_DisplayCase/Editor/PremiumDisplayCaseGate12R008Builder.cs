using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Editor
{
    /// <summary>
    /// Gate 12 R008: reference-match lookdev (user 2026-09-09 22:01, PSA
    /// turntable render). Built on the R006 flocking variant: glossy clear
    /// acrylic shells with edge dispersion, a silver holographic glitter
    /// backing behind the toy and the label, a frosted glowing rim, HDR +
    /// bloom + ACES, and a 9:16 black-void turntable with a fixed key.
    /// Shipping factory still points at R004. R007 is a separate task
    /// (sandblasted foil badge) and is not touched here.
    /// </summary>
    public static class PremiumDisplayCaseGate12R008Builder
    {
        public const string PrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R008/PresentationRoot.prefab";
        public const string ScenePath =
            "Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R008.unity";
        public const string EvidenceRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/rev-021";
        private const string GeneratedRoot = "Assets/_DisplayCase/Generated/Gate12R008";
        private const string MaterialRoot = GeneratedRoot + "/Materials";
        public const string VolumeProfilePath = GeneratedRoot + "/Gate12R008LookdevVolume.asset";
        public const string AcrylicShaderName = "FidgetingApp/Gate12R008ClearAcrylic";
        public const string GlitterShaderName = "FidgetingApp/Gate12R008GlitterHolo";

        // One key for every custom shader and the scene light, so the toy
        // (URP Lit) and the shells agree on where the light is.
        public static readonly Vector3 KeyDirection = new Vector3(0.45f, 0.55f, -0.70f).normalized;
        public static readonly Vector3 FillDirection = new Vector3(-0.70f, 0.20f, -0.65f).normalized;

        public const int TurntableFrames = 300;
        public const float TurntableSeconds = 10f;
        private const int PortraitWidth = 1080;
        private const int PortraitHeight = 1440; // 3:4 at 1.22 m: slab ~62% of height with black margin for the halo
        private static readonly Vector3 CameraPosition = new Vector3(0f, 0.03f, -1.22f);
        private static readonly Vector3 CameraTarget = new Vector3(0f, 0.008f, 0f);
        private const float CameraFov = 20f;

        [MenuItem("Fidgeting/Display Case/Gate 12/R008 Build Reference-Match Lookdev")]
        public static void Build()
        {
            PremiumDisplayCaseGate12R006Builder.BuildCandidates();
            EnsureDirectories();
            Materials materials = CreateMaterials();
            BuildPrefab(materials);
            BuildScene();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("Premium Display Case Gate 12 R008 lookdev built.");
        }

        [MenuItem("Fidgeting/Display Case/Gate 12/R008 Capture Stills")]
        public static void CaptureStills()
        {
            Run(false);
        }

        [MenuItem("Fidgeting/Display Case/Gate 12/R008 Capture Product Views (existing scene)")]
        public static void CaptureProductViews()
        {
            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            GameObject[] roots = scene.GetRootGameObjects();
            Camera camera = roots.SelectMany(r => r.GetComponentsInChildren<Camera>(true)).Single();
            PremiumDisplayCaseShippingPresentation presentation = roots
                .SelectMany(r => r.GetComponentsInChildren<PremiumDisplayCaseShippingPresentation>(true))
                .Single();
            presentation.SetLabel(PremiumDisplayCaseGate12R005Builder.BuildAuthoritativeReviewLabel());
            presentation.SetTimeForPreview(presentation.RevealProfile.TotalDurationSeconds);
            presentation.transform.rotation = Quaternion.identity;
            string output = Path.GetFullPath(Path.Combine(Application.dataPath, "..", EvidenceRoot));
            Directory.CreateDirectory(output);
            CaptureProductAngles(camera, output);
            AssetDatabase.Refresh();
            Debug.Log($"Gate 12 R008 product views at {output}.");
        }

        [MenuItem("Fidgeting/Display Case/Gate 12/R008 Capture Stills + Turntable")]
        public static void CaptureAll()
        {
            Run(true);
        }

        private static void Run(bool turntable)
        {
            Build();
            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            GameObject[] roots = scene.GetRootGameObjects();
            Camera camera = roots.SelectMany(r => r.GetComponentsInChildren<Camera>(true)).Single();
            PremiumDisplayCaseShippingPresentation presentation = roots
                .SelectMany(r => r.GetComponentsInChildren<PremiumDisplayCaseShippingPresentation>(true))
                .Single();
            presentation.SetLabel(PremiumDisplayCaseGate12R005Builder.BuildAuthoritativeReviewLabel());
            presentation.SetTimeForPreview(presentation.RevealProfile.TotalDurationSeconds);
            Transform root = presentation.transform;
            string output = Path.GetFullPath(Path.Combine(Application.dataPath, "..", EvidenceRoot));
            Directory.CreateDirectory(output);

            // Stills at the reference strip's yaws: front, quarter, edge, back, return.
            foreach (float yaw in new[] { 0f, 25f, 90f, 200f, 335f })
            {
                root.rotation = Quaternion.Euler(0f, yaw, 0f);
                Still(camera, output, $"turntable-yaw-{yaw:000}.png");
            }
            root.rotation = Quaternion.Euler(0f, 18f, 0f);
            Macro(camera, output, "glitter-backing-macro.png",
                new Vector3(0.02f, -0.02f, 0f) + new Vector3(0.25f, 0.20f, -1f).normalized * 0.34f,
                new Vector3(0.02f, -0.02f, 0f));
            Macro(camera, output, "edge-dispersion-macro.png",
                new Vector3(0.105f, 0.06f, -0.02f) + new Vector3(0.55f, 0.10f, -1f).normalized * 0.22f,
                new Vector3(0.105f, 0.06f, -0.02f));
            root.rotation = Quaternion.identity;
            CaptureProductAngles(camera, output);
            if (!turntable)
            {
                AssetDatabase.Refresh();
                Debug.Log($"Gate 12 R008 stills at {output}.");
                return;
            }

            string frames = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "Logs", "gate12-r008-turntable"));
            if (Directory.Exists(frames))
            {
                Directory.Delete(frames, true);
            }
            Directory.CreateDirectory(frames);
            for (int frame = 0; frame < TurntableFrames; frame++)
            {
                float yaw = 360f * frame / TurntableFrames;
                root.rotation = Quaternion.Euler(0f, yaw, 0f);
                Still(camera, frames, $"frame-{frame:D3}.png");
            }
            root.rotation = Quaternion.identity;
            AssetDatabase.Refresh();
            Debug.Log($"Gate 12 R008 stills at {output}; turntable frames at {frames}.");
        }

        private static void CaptureProductAngles(Camera camera, string output)
        {
            PremiumDisplayCaseGate12R005Builder.Capture(camera, output, "hero.png",
                new Vector3(0.42f, 0.22f, -1.05f), CameraTarget, Vector3.up, 22f, PortraitWidth, PortraitHeight);
            PremiumDisplayCaseGate12R005Builder.Capture(camera, output, "top.png",
                new Vector3(0f, 1.05f, 0.02f), Vector3.zero, Vector3.forward, 24f, PortraitWidth, PortraitHeight);
            PremiumDisplayCaseGate12R005Builder.Capture(camera, output, "left-oblique.png",
                new Vector3(-0.48f, 0.16f, -1.02f), CameraTarget, Vector3.up, 22f, PortraitWidth, PortraitHeight);
            PremiumDisplayCaseGate12R005Builder.Capture(camera, output, "right-oblique.png",
                new Vector3(0.48f, 0.16f, -1.02f), CameraTarget, Vector3.up, 22f, PortraitWidth, PortraitHeight);
            PremiumDisplayCaseGate12R005Builder.Capture(camera, output, "low.png",
                new Vector3(0.32f, -0.38f, -1.05f), new Vector3(0f, 0.012f, 0f), Vector3.up, 22f, PortraitWidth, PortraitHeight);
            Still(camera, output, "front.png");
        }

        private static void Still(Camera camera, string output, string file)
        {
            PremiumDisplayCaseGate12R005Builder.Capture(camera, output, file,
                CameraPosition, CameraTarget, Vector3.up, CameraFov, PortraitWidth, PortraitHeight);
        }

        private static void Macro(Camera camera, string output, string file, Vector3 from, Vector3 at)
        {
            PremiumDisplayCaseGate12R005Builder.Capture(camera, output, file,
                from, at, Vector3.up, 24f, PortraitWidth, PortraitHeight);
        }

        private static void EnsureDirectories()
        {
            string project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            foreach (string path in new[]
                     {
                         "Assets/Resources/Gacha/PremiumDisplayCaseGate12R008", MaterialRoot, EvidenceRoot
                     })
            {
                Directory.CreateDirectory(Path.Combine(project, path));
            }
            AssetDatabase.Refresh();
        }

        private static Materials CreateMaterials()
        {
            Shader acrylic = PremiumDisplayCaseGate12R005Builder.RequireShader(AcrylicShaderName);
            Shader glitter = PremiumDisplayCaseGate12R005Builder.RequireShader(GlitterShaderName);
            return new Materials
            {
                FrontShell = Acrylic("Gate12R008FrontShell", acrylic, opacity: 0.05f, frost: 0f,
                    rim: 0.45f, streak: 0.55f, hotspot: 7f, dispersion: 1.3f, edgeGlow: 0f, queue: 3020),
                RearShell = Acrylic("Gate12R008RearShell", acrylic, opacity: 0.05f, frost: 0f,
                    rim: 0.35f, streak: 0.4f, hotspot: 3f, dispersion: 1.1f, edgeGlow: 0f, queue: 3000),
                // The perimeter is a wide front frame, not a bead: wall glow on
                // it paints the whole frame pink. Edge-on glow comes from the skirt.
                Tube = Acrylic("Gate12R008Rim", acrylic, opacity: 0.10f, frost: 0f,
                    rim: 0.9f, streak: 1.8f, hotspot: 3f, dispersion: 2.6f, edgeGlow: 0.25f, queue: 3030),
                Skirt = Acrylic("Gate12R008SideWallSkirt", acrylic, opacity: 0.22f, frost: 0f,
                    rim: 0.35f, streak: 1.6f, hotspot: 2f, dispersion: 0.9f, edgeGlow: 1.4f, queue: 3025),
                BridgeBar = Acrylic("Gate12R008BridgeBar", acrylic, opacity: 0.30f, frost: 0.55f,
                    rim: 0.30f, streak: 0.8f, hotspot: 0f, dispersion: 0.6f, edgeGlow: 0.3f, queue: 3015),
                Backing = Glitter("Gate12R008GlitterBacking", glitter,
                    new Color(0.70f, 0.71f, 0.74f, 1f), density: 800f, intensity: 14f, sheen: 0.16f),
                LabelWell = Glitter("Gate12R008GlitterLabelWell", glitter,
                    new Color(0.58f, 0.59f, 0.62f, 1f), density: 1000f, intensity: 9f, sheen: 0.12f)
            };
        }

        private static Material Acrylic(string name, Shader shader, float opacity, float frost,
            float rim, float streak, float hotspot, float dispersion, float edgeGlow, int queue)
        {
            Material m = Upsert(name, shader);
            m.SetColor("_BaseColor", new Color(0.10f, 0.12f, 0.15f, 1f));
            m.SetFloat("_Opacity", opacity);
            m.SetFloat("_Frost", frost);
            m.SetFloat("_RimStrength", rim);
            m.SetFloat("_SpecularStrength", streak);
            m.SetFloat("_SpecularPower", 40f);
            m.SetFloat("_HotspotStrength", hotspot);
            m.SetFloat("_Dispersion", dispersion);
            m.SetFloat("_EdgeGlow", edgeGlow);
            bool skirt = name.Contains("Skirt");
            m.SetFloat("_WallOverride", skirt ? 1f : 0f);
            // Only the skirt's outer faces: its inner faces seen through the
            // front shell painted the whole frame pink.
            m.SetFloat("_Cull", skirt ? (float)CullMode.Back : (float)CullMode.Off);
            m.SetVector("_KeyDirection", KeyDirection);
            m.SetVector("_FillDirection", FillDirection);
            m.renderQueue = queue;
            EditorUtility.SetDirty(m);
            return m;
        }

        private static Material Glitter(string name, Shader shader, Color stock,
            float density, float intensity, float sheen)
        {
            Material m = Upsert(name, shader);
            m.SetColor("_BaseColor", stock);
            m.SetFloat("_FlakeDensity", density);
            m.SetFloat("_FlakeIntensity", intensity);
            m.SetFloat("_FlakeSharpness", 45f);
            m.SetFloat("_FlakeSpread", 0.6f);
            m.SetFloat("_FlakeSaturation", 0.9f);
            m.SetFloat("_SheenStrength", sheen);
            // Rainbow wash must be a gradient across the sheet, not one hue
            // per view angle, or the whole field turns pink at yaw 0.
            m.SetFloat("_SheenScale", 9f);
            m.SetVector("_KeyDirection", KeyDirection);
            m.SetVector("_FillDirection", FillDirection);
            EditorUtility.SetDirty(m);
            return m;
        }

        private static Material Upsert(string name, Shader shader)
        {
            string path = MaterialRoot + "/" + name + ".mat";
            Material m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null)
            {
                m = new Material(shader) { name = name };
                AssetDatabase.CreateAsset(m, path);
            }
            m.shader = shader;
            return m;
        }

        private static void BuildPrefab(Materials materials)
        {
            GameObject r006 = AssetDatabase.LoadAssetAtPath<GameObject>(
                PremiumDisplayCaseGate12R006Builder.FlockingPrefabPath);
            GameObject root = PrefabUtility.InstantiatePrefab(r006) as GameObject;
            try
            {
                root.name = "PresentationRoot";
                root.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
                MeshRenderer[] renderers = root.GetComponentsInChildren<MeshRenderer>(true);
                Renderer(renderers, "FrontPolycarbonateShell").sharedMaterial = materials.FrontShell;
                Renderer(renderers, "RearPolycarbonateShell").sharedMaterial = materials.RearShell;
                Renderer(renderers, "ContinuousTubePerimeter").sharedMaterial = materials.Tube;
                Renderer(renderers, "BridgeBar").sharedMaterial = materials.BridgeBar;
                Renderer(renderers, "TactileBackgroundInsert").sharedMaterial = materials.Backing;
                Renderer(renderers, "LabelWellFloor").sharedMaterial = materials.LabelWell;
                // The frosted bezel line fights the glitter; the gap and well
                // shadow rings carry the recess on the light backing.
                Renderer(renderers, "ChamberBezel").enabled = false;
                BuildSideWallSkirt(root.transform, renderers, materials.Skirt);
                PrefabUtility.SaveAsPrefabAsset(root, PrefabPath);
            }
            finally
            {
                Object.DestroyImmediate(root);
            }
        }

        /// <summary>
        /// The R004 case is two thin shells plus a rim bead: edge-on there is
        /// open air between them. A solid slab has a continuous side wall, and
        /// the reference glows through it, so R008 closes the gap with a
        /// rounded-rect skirt spanning rear-shell back to front-shell front.
        /// Lookdev candidate only; it is not a change to the approved R004 body.
        /// </summary>
        private static void BuildSideWallSkirt(Transform root, MeshRenderer[] renderers, Material material)
        {
            Transform old = root.Find("SideWallSkirt");
            if (old != null)
            {
                Object.DestroyImmediate(old.gameObject);
            }
            Bounds front = Renderer(renderers, "FrontPolycarbonateShell").bounds;
            Bounds rear = Renderer(renderers, "RearPolycarbonateShell").bounds;
            Bounds outline = front;
            outline.Encapsulate(rear);
            float zFront = front.min.z;
            float zBack = rear.max.z;
            const float cornerRadius = 0.012f;
            const int cornerSegments = 10;
            Mesh mesh = RoundedRectBand(outline.center, outline.size.x * 0.5f - 0.0002f,
                outline.size.y * 0.5f - 0.0002f, cornerRadius, cornerSegments, zBack, zFront);
            mesh.name = "SideWallSkirt";
            AssetDatabase.CreateAsset(mesh, GeneratedRoot + "/SideWallSkirt.asset");

            var skirt = new GameObject("SideWallSkirt");
            skirt.transform.SetParent(root, false);
            skirt.AddComponent<MeshFilter>().sharedMesh = mesh;
            MeshRenderer renderer = skirt.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            renderer.sortingOrder = 25;
            Debug.Log($"R008 skirt: outline {outline.size.x * 1000f:F1} x {outline.size.y * 1000f:F1} mm, depth {(zBack - zFront) * 1000f:F1} mm (z {zFront:F4}..{zBack:F4}).");
        }

        private static Mesh RoundedRectBand(Vector3 center, float halfWidth, float halfHeight,
            float radius, int cornerSegments, float zBack, float zFront)
        {
            var outline = new System.Collections.Generic.List<Vector2>();
            var normals2 = new System.Collections.Generic.List<Vector2>();
            Vector2[] corners =
            {
                new Vector2(halfWidth - radius, halfHeight - radius),
                new Vector2(-(halfWidth - radius), halfHeight - radius),
                new Vector2(-(halfWidth - radius), -(halfHeight - radius)),
                new Vector2(halfWidth - radius, -(halfHeight - radius))
            };
            for (int corner = 0; corner < 4; corner++)
            {
                float start = 90f * corner;
                for (int segment = 0; segment <= cornerSegments; segment++)
                {
                    float angle = Mathf.Deg2Rad * (start + 90f * segment / cornerSegments);
                    var normal = new Vector2(Mathf.Cos(angle), Mathf.Sin(angle));
                    outline.Add(corners[corner] + normal * radius);
                    normals2.Add(normal);
                }
            }
            int count = outline.Count;
            var vertices = new Vector3[count * 2];
            var normals = new Vector3[count * 2];
            var uv = new Vector2[count * 2];
            for (int index = 0; index < count; index++)
            {
                Vector2 p = outline[index];
                vertices[index] = new Vector3(center.x + p.x, center.y + p.y, zBack);
                vertices[index + count] = new Vector3(center.x + p.x, center.y + p.y, zFront);
                var n = new Vector3(normals2[index].x, normals2[index].y, 0f);
                normals[index] = n;
                normals[index + count] = n;
                uv[index] = new Vector2((float)index / count, 0f);
                uv[index + count] = new Vector2((float)index / count, 1f);
            }
            var triangles = new int[count * 6];
            for (int index = 0; index < count; index++)
            {
                int next = (index + 1) % count;
                int t = index * 6;
                triangles[t] = index;
                triangles[t + 1] = index + count;
                triangles[t + 2] = next;
                triangles[t + 3] = next;
                triangles[t + 4] = index + count;
                triangles[t + 5] = next + count;
            }
            var mesh = new Mesh { vertices = vertices, normals = normals, uv = uv, triangles = triangles };
            mesh.RecalculateBounds();
            return mesh;
        }

        private static void BuildScene()
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
            PremiumDisplayCaseShippingPresentation presentation =
                (PrefabUtility.InstantiatePrefab(prefab) as GameObject)
                    .GetComponent<PremiumDisplayCaseShippingPresentation>();
            presentation.transform.position = Vector3.zero;
            presentation.SetLabel(PremiumDisplayCaseGate12R005Builder.BuildAuthoritativeReviewLabel());
            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            prize.name = "AuthoritativeThreeBladePrize";
            presentation.AttachContent(prize.transform, PremiumDisplayCaseShippingFactory.ThreeBladeContentEuler);
            presentation.SetTimeForPreview(presentation.RevealProfile.TotalDurationSeconds);

            // Black void, one warm key from upper right front, cool fill from
            // the left, soft rim from behind. Ambient low so edges read.
            AddLight("LookdevKey", Quaternion.LookRotation(-KeyDirection), new Color(1f, 0.96f, 0.90f), 2.6f, LightShadows.Soft);
            AddLight("LookdevFill", Quaternion.LookRotation(-FillDirection), new Color(0.70f, 0.82f, 1f), 0.55f, LightShadows.None);
            AddLight("LookdevRim", Quaternion.Euler(12f, 195f, 0f), new Color(0.90f, 0.94f, 1f), 0.9f, LightShadows.None);
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.10f, 0.11f, 0.13f);

            var cameraObject = new GameObject("Gate12LookdevCamera") { tag = "MainCamera" };
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.black;
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.fieldOfView = CameraFov;
            camera.allowHDR = true;
            camera.transform.position = CameraPosition;
            camera.transform.LookAt(CameraTarget);
            UniversalAdditionalCameraData additional = camera.GetUniversalAdditionalCameraData();
            additional.renderPostProcessing = true;
            additional.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            additional.antialiasingQuality = AntialiasingQuality.High;

            VolumeProfile profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(VolumeProfilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>();
                profile.name = "Gate12R008LookdevVolume";
                AssetDatabase.CreateAsset(profile, VolumeProfilePath);
            }
            foreach (VolumeComponent component in profile.components.ToArray())
            {
                profile.Remove(component.GetType());
            }
            Bloom bloom = profile.Add<Bloom>(true);
            bloom.threshold.Override(1.0f);
            bloom.intensity.Override(1.0f);
            bloom.scatter.Override(0.76f);
            bloom.tint.Override(new Color(1f, 0.97f, 0.94f));
            Tonemapping tonemapping = profile.Add<Tonemapping>(true);
            tonemapping.mode.Override(TonemappingMode.ACES);
            ColorAdjustments grade = profile.Add<ColorAdjustments>(true);
            grade.postExposure.Override(0.05f);
            grade.saturation.Override(12f);
            grade.contrast.Override(18f);
            Vignette vignette = profile.Add<Vignette>(true);
            vignette.intensity.Override(0.28f);
            vignette.smoothness.Override(0.6f);
            EditorUtility.SetDirty(profile);
            var volumeObject = new GameObject("Gate12R008GlobalVolume");
            Volume volume = volumeObject.AddComponent<Volume>();
            volume.isGlobal = true;
            volume.sharedProfile = profile;

            EditorSceneManager.SaveScene(scene, ScenePath);
        }

        private static void AddLight(string name, Quaternion rotation, Color color,
            float intensity, LightShadows shadows)
        {
            var go = new GameObject(name);
            go.transform.rotation = rotation;
            Light light = go.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = color;
            light.intensity = intensity;
            light.shadows = shadows;
            light.shadowStrength = 0.7f;
        }

        private static MeshRenderer Renderer(MeshRenderer[] renderers, string name)
        {
            return renderers.Single(r => r.name == name);
        }

        private struct Materials
        {
            public Material FrontShell;
            public Material RearShell;
            public Material Tube;
            public Material Skirt;
            public Material BridgeBar;
            public Material Backing;
            public Material LabelWell;
        }
    }
}
