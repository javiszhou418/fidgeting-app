using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EditorTools
{
    public static class MagneticSlideTileGate05R012PreviewBuilder
    {
        private const string ModelPath =
            "Assets/_EDC/Candidates/MagneticSlideTileGate05R012Geometry/Imported/magnetic-slide-tile-fixed-axis-r012.fbx";
        private const string ScenePath =
            "Assets/_EDC/Candidates/MagneticSlideTileGate05R012Geometry/MagneticSlideTileGate05R012Preview.unity";
        private const int Width = 960;
        private const int Height = 720;
        private const int Frames = 300;
        private const float MaximumTravel = 0.0180764331f;

        public static void BuildAndCapture()
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject source = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (source == null)
                throw new InvalidOperationException($"Missing corrected FBX: {ModelPath}");
            GameObject product = PrefabUtility.InstantiatePrefab(source) as GameObject;
            product.name = "MagneticSlideTile_G05_R012_UnityPreview";

            Transform bottom = Find(product.transform, "BottomExterior");
            Transform fixedAxis = Find(product.transform, "FixedAxis");
            Transform carrier = Find(product.transform, "RotatingCarrier");
            Transform top = Find(product.transform, "MovingTopBody");
            if (new[] { bottom, fixedAxis, carrier, top }.Any(item => item == null))
                throw new InvalidOperationException("Corrected hierarchy is incomplete.");

            Shader lit = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
            Shader unlit = Shader.Find("Universal Render Pipeline/Unlit") ?? Shader.Find("Unlit/Color");
            Material clay = new Material(lit) { name = "G05R012_UnityClay" };
            clay.color = new Color(0.69f, 0.72f, 0.77f, 1f);
            clay.SetFloat("_Smoothness", 0.28f);
            HashSet<string> whitelist = new HashSet<string> { "BottomExterior", "MovingTopBody" };
            foreach (Renderer renderer in product.GetComponentsInChildren<Renderer>(true))
            {
                renderer.enabled = whitelist.Contains(renderer.name);
                if (renderer.enabled)
                    renderer.sharedMaterial = clay;
            }
            string[] activeRenderers = product.GetComponentsInChildren<Renderer>(true)
                .Where(renderer => renderer.enabled)
                .Select(renderer => renderer.name)
                .OrderBy(name => name)
                .ToArray();
            if (!activeRenderers.SequenceEqual(whitelist.OrderBy(name => name)))
                throw new InvalidOperationException("Unity product renderer whitelist drifted.");

            Vector3 pivot = fixedAxis.position;
            Vector3 pivotReference = pivot;
            Quaternion carrierBaseline = carrier.rotation;
            Quaternion topBaseline = top.rotation;
            Vector3 q0 = top.InverseTransformPoint(pivot);
            Vector3 horizontalQ = new Vector3(q0.x, q0.y, 0f);
            Vector3 slideAxis = -horizontalQ.normalized;
            if (Mathf.Abs(horizontalQ.magnitude - 0.009f) > 0.00001f)
                throw new InvalidOperationException($"Unexpected closed slot point: {q0}");

            GameObject axisOverlay = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            axisOverlay.name = "Technical_FixedWorldAxisOverlay";
            axisOverlay.transform.position = pivot + Vector3.up * 0.012f;
            axisOverlay.transform.localScale = new Vector3(0.00022f, 0.017f, 0.00022f);
            UnityEngine.Object.DestroyImmediate(axisOverlay.GetComponent<Collider>());
            Material red = new Material(unlit) { name = "G05R012_AxisOverlay" };
            red.color = new Color(1f, 0.04f, 0.01f, 1f);
            axisOverlay.GetComponent<Renderer>().sharedMaterial = red;

            Camera camera = new GameObject("CAM_G05R012_UnityGeometry").AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.018f, 0.022f, 0.03f, 1f);
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 1f;
            camera.fieldOfView = 32f;
            camera.transform.position = new Vector3(0.075f, 0.067f, -0.112f);
            camera.transform.LookAt(new Vector3(0f, 0.006f, -0.004f), Vector3.up);

            Light key = new GameObject("Key").AddComponent<Light>();
            key.type = LightType.Directional;
            key.intensity = 1.35f;
            key.color = new Color(1f, 0.96f, 0.91f);
            key.transform.rotation = Quaternion.Euler(48f, -28f, 0f);
            Light fill = new GameObject("Fill").AddComponent<Light>();
            fill.type = LightType.Directional;
            fill.intensity = 0.55f;
            fill.color = new Color(0.72f, 0.82f, 1f);
            fill.transform.rotation = Quaternion.Euler(55f, 145f, 0f);
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.19f, 0.21f, 0.25f);

            EditorSceneManager.SaveScene(scene, ScenePath);
            string output = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/unity-preview"));
            string frames = Path.Combine(output, "frames");
            Directory.CreateDirectory(frames);
            foreach (string oldFrame in Directory.GetFiles(frames, "*.png"))
                File.Delete(oldFrame);

            RenderTexture target = new RenderTexture(Width, Height, 24, RenderTextureFormat.ARGB32);
            Texture2D readback = new Texture2D(Width, Height, TextureFormat.RGB24, false);
            camera.targetTexture = target;
            float maxPivotVariance = 0f;
            float maxResidual = 0f;
            float maxPitchRoll = 0f;
            List<PoseRecord> keyPoses = new List<PoseRecord>();
            for (int frame = 0; frame < Frames; frame++)
            {
                GetPose(frame, out float slide, out float angle);
                Quaternion yaw = Quaternion.AngleAxis(-angle, Vector3.up);
                Vector3 q = q0 + slideAxis * slide;
                top.rotation = yaw * topBaseline;
                top.position = pivot - top.rotation * q;
                carrier.rotation = yaw * carrierBaseline;
                maxPivotVariance = Mathf.Max(maxPivotVariance, Vector3.Distance(fixedAxis.position, pivotReference));
                maxResidual = Mathf.Max(maxResidual, Vector3.Distance(top.TransformPoint(q), pivot));
                maxPitchRoll = Mathf.Max(
                    maxPitchRoll,
                    Vector3.Angle(top.forward, yaw * (topBaseline * Vector3.forward)));
                if (frame is 0 or 59 or 119 or 179 or 239 or 299)
                    keyPoses.Add(new PoseRecord(frame, slide, angle, fixedAxis.position, top.TransformPoint(q)));
                camera.Render();
                RenderTexture.active = target;
                readback.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
                readback.Apply(false);
                File.WriteAllBytes(Path.Combine(frames, $"frame-{frame:D4}.png"), readback.EncodeToPNG());
            }
            camera.targetTexture = null;
            RenderTexture.active = null;
            UnityEngine.Object.DestroyImmediate(target);
            UnityEngine.Object.DestroyImmediate(readback);

            Report report = new Report
            {
                schemaVersion = 1,
                unityVersion = Application.unityVersion,
                scenePath = ScenePath,
                modelPath = ModelPath,
                frames = Frames,
                fps = 30,
                fixedPivotMeters = new[] { pivot.x, pivot.y, pivot.z },
                q0LocalMeters = new[] { q0.x, q0.y, q0.z },
                transform = "M_top(s,theta)=T(P)*R_worldUp(theta)*T(-q(s))",
                maxPivotVarianceMeters = maxPivotVariance,
                maxConstraintResidualMeters = maxResidual,
                maxPitchRollDegrees = maxPitchRoll,
                rendererWhitelist = activeRenderers,
                keyPoses = keyPoses.ToArray(),
                build = false,
                install = false,
                phone = false,
                pass = maxPivotVariance <= 1e-9f
                    && maxResidual <= 1e-7f
                    && maxPitchRoll <= 0.0001f
                    && activeRenderers.Length == 2,
            };
            File.WriteAllText(Path.Combine(output, "unity-motion-validation.json"), JsonUtility.ToJson(report, true));
            AssetDatabase.SaveAssets();
            if (!report.pass)
                throw new InvalidOperationException(JsonUtility.ToJson(report, true));
            Debug.Log($"GATE05_R012_CAPTURE_PASS frames={Frames} residual={maxResidual:R}");
        }

        private static void GetPose(int frame, out float slide, out float angle)
        {
            if (frame < 60) { slide = 0f; angle = 0f; return; }
            if (frame < 120) { slide = MaximumTravel * ((frame - 60) / 59f); angle = 0f; return; }
            if (frame < 180) { slide = MaximumTravel; angle = 36f * ((frame - 120) / 59f); return; }
            if (frame < 240)
            {
                float t = (frame - 180) / 59f;
                slide = Mathf.Lerp(MaximumTravel, MaximumTravel * 0.45f, t);
                angle = Mathf.Lerp(36f, 12f, t);
                return;
            }
            float close = (frame - 240) / 59f;
            slide = Mathf.Lerp(MaximumTravel * 0.45f, 0f, close);
            angle = Mathf.Lerp(12f, 0f, close);
        }

        private static Transform Find(Transform root, string name)
        {
            if (root.name == name) return root;
            foreach (Transform child in root)
            {
                Transform found = Find(child, name);
                if (found != null) return found;
            }
            return null;
        }

        [Serializable]
        private sealed class Report
        {
            public int schemaVersion;
            public string unityVersion;
            public string scenePath;
            public string modelPath;
            public int frames;
            public int fps;
            public float[] fixedPivotMeters;
            public float[] q0LocalMeters;
            public string transform;
            public float maxPivotVarianceMeters;
            public float maxConstraintResidualMeters;
            public float maxPitchRollDegrees;
            public string[] rendererWhitelist;
            public PoseRecord[] keyPoses;
            public bool build;
            public bool install;
            public bool phone;
            public bool pass;
        }

        [Serializable]
        private sealed class PoseRecord
        {
            public int frame;
            public float slideMeters;
            public float angleDegrees;
            public float[] pivot;
            public float[] lockedSlotPoint;

            public PoseRecord(int frame, float slide, float angle, Vector3 pivot, Vector3 locked)
            {
                this.frame = frame;
                slideMeters = slide;
                angleDegrees = angle;
                this.pivot = new[] { pivot.x, pivot.y, pivot.z };
                lockedSlotPoint = new[] { locked.x, locked.y, locked.z };
            }
        }
    }
}

