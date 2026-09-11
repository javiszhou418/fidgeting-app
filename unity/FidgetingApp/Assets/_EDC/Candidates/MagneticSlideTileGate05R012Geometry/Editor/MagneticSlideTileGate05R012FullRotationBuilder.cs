using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace FidgetingApp.EditorTools
{
    public static class MagneticSlideTileGate05R012FullRotationBuilder
    {
        private const string ModelPath =
            "Assets/_EDC/Candidates/MagneticSlideTileGate05R012Geometry/Imported/magnetic-slide-tile-fixed-axis-r012.fbx";
        private const string ScenePath =
            "Assets/_EDC/Candidates/MagneticSlideTileGate05R012Geometry/MagneticSlideTileGate05R012FullRotationPreview.unity";
        private const int Width = 1920;
        private const int Height = 1080;
        private const int Frames = 570;
        private const float MaximumTravel = 0.0180764331f;
        private const float PartialTravel = MaximumTravel * 0.5f;
        private const float DiskRadius = 0.015f;

        public static void BuildAndCapture()
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject source = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (source == null)
                throw new InvalidOperationException($"Missing corrected FBX: {ModelPath}");
            GameObject product = PrefabUtility.InstantiatePrefab(source) as GameObject;
            product.name = "MagneticSlideTile_G05_R012_FullRotationProof";

            Transform bottom = Find(product.transform, "BottomExterior");
            Transform fixedAxis = Find(product.transform, "FixedAxis");
            Transform carrier = Find(product.transform, "RotatingCarrier");
            Transform top = Find(product.transform, "MovingTopBody");
            if (new[] { bottom, fixedAxis, carrier, top }.Any(item => item == null))
                throw new InvalidOperationException("Corrected hierarchy is incomplete.");

            Shader lit = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
            Shader unlit = Shader.Find("Universal Render Pipeline/Unlit") ?? Shader.Find("Unlit/Color");
            Material clay = new Material(lit) { name = "G05R012_FullRotationClay" };
            clay.color = new Color(0.70f, 0.73f, 0.78f, 1f);
            clay.SetFloat("_Smoothness", 0.26f);
            HashSet<string> whitelist = new HashSet<string> { "BottomExterior", "MovingTopBody" };
            foreach (Renderer renderer in product.GetComponentsInChildren<Renderer>(true))
            {
                renderer.enabled = whitelist.Contains(renderer.name);
                if (renderer.enabled) renderer.sharedMaterial = clay;
            }
            string[] activeRenderers = product.GetComponentsInChildren<Renderer>(true)
                .Where(renderer => renderer.enabled)
                .Select(renderer => renderer.name)
                .OrderBy(name => name)
                .ToArray();
            if (!activeRenderers.SequenceEqual(whitelist.OrderBy(name => name)))
                throw new InvalidOperationException("Product renderer whitelist drifted.");
            int pivotCount = product.GetComponentsInChildren<Transform>(true)
                .Count(item => item.name == "FixedAxis");
            if (pivotCount != 1)
                throw new InvalidOperationException($"Expected one FixedAxis, found {pivotCount}.");

            Vector3 pivot = fixedAxis.position;
            Vector3 pivotReference = pivot;
            Vector3 bottomPosition = bottom.position;
            Quaternion bottomRotation = bottom.rotation;
            Vector3 productPosition = product.transform.position;
            Quaternion productRotation = product.transform.rotation;
            Quaternion carrierBaseline = carrier.rotation;
            Quaternion topBaseline = top.rotation;
            Vector3 q0 = top.InverseTransformPoint(pivot);
            Vector3 slideAxis = -new Vector3(q0.x, q0.y, 0f).normalized;
            if (Mathf.Abs(new Vector2(q0.x, q0.y).magnitude - 0.009f) > 0.00001f)
                throw new InvalidOperationException($"Unexpected closed slot point: {q0}");

            GameObject axisOverlay = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            axisOverlay.name = "Technical_FixedWorldAxisOverlay";
            axisOverlay.transform.position = pivot + Vector3.up * 0.014f;
            axisOverlay.transform.localScale = new Vector3(0.00024f, 0.020f, 0.00024f);
            UnityEngine.Object.DestroyImmediate(axisOverlay.GetComponent<Collider>());
            Material red = new Material(unlit) { name = "G05R012_FixedAxisRed" };
            red.color = new Color(1f, 0.035f, 0.01f, 1f);
            axisOverlay.GetComponent<Renderer>().sharedMaterial = red;

            Camera camera = new GameObject("CAM_G05R012_Fixed_FullRotation").AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.015f, 0.019f, 0.027f, 1f);
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 1f;
            camera.fieldOfView = 30f;
            camera.transform.position = new Vector3(0.076f, 0.067f, -0.116f);
            camera.transform.LookAt(new Vector3(0f, 0.006f, -0.005f), Vector3.up);
            Matrix4x4 cameraMatrix = camera.transform.localToWorldMatrix;

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

            Text statusText = BuildStatusOverlay(camera);
            Renderer bottomRenderer = bottom.GetComponent<Renderer>();
            Renderer topRenderer = top.GetComponent<Renderer>();
            MeshCollider topCollider = top.gameObject.AddComponent<MeshCollider>();
            topCollider.sharedMesh = top.GetComponent<MeshFilter>().sharedMesh;

            EditorSceneManager.SaveScene(scene, ScenePath);
            string output = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/unity-preview"));
            string frameDirectory = Path.Combine(output, "frames-full-360");
            Directory.CreateDirectory(frameDirectory);
            foreach (string oldFrame in Directory.GetFiles(frameDirectory, "*.png"))
                File.Delete(oldFrame);

            RenderTexture target = new RenderTexture(Width, Height, 24, RenderTextureFormat.ARGB32);
            Texture2D readback = new Texture2D(Width, Height, TextureFormat.RGB24, false);
            camera.targetTexture = target;
            HashSet<int> detents = new HashSet<int>();
            float maxPivotVariance = 0f;
            float maxResidual = 0f;
            float maxBottomPositionVariance = 0f;
            float maxBottomRotationVariance = 0f;
            float maxProductPositionVariance = 0f;
            float maxProductRotationVariance = 0f;
            float maxTilt = 0f;
            float minimumVerticalGap = float.MaxValue;
            int containmentMisses = 0;
            int illegalSlides = 0;
            int cameraMotionFrames = 0;
            List<PoseRecord> keyPoses = new List<PoseRecord>();
            Quaternion partialStart = Quaternion.identity;
            Quaternion partialEnd = Quaternion.identity;
            Quaternion maximumStart = Quaternion.identity;
            Quaternion maximumEnd = Quaternion.identity;

            for (int frame = 0; frame < Frames; frame++)
            {
                GetPose(frame, out float slide, out float angle, out string phase);
                Quaternion yaw = Quaternion.AngleAxis(-angle, Vector3.up);
                Vector3 q = q0 + slideAxis * slide;
                top.rotation = yaw * topBaseline;
                top.position = pivot - top.rotation * q;
                carrier.rotation = yaw * carrierBaseline;
                Physics.SyncTransforms();

                if (frame == 60) partialStart = top.rotation;
                if (frame == 240) partialEnd = top.rotation;
                if (frame == 270) maximumStart = top.rotation;
                if (frame == 450) maximumEnd = top.rotation;
                if ((frame >= 60 && frame <= 240) || (frame >= 270 && frame <= 450))
                {
                    float nearest = Mathf.Round(angle / 12f);
                    if (Mathf.Abs(angle - nearest * 12f) <= 0.0001f && angle < 360f)
                        detents.Add(((int)nearest) % 30);
                }

                maxPivotVariance = Mathf.Max(maxPivotVariance, Vector3.Distance(fixedAxis.position, pivotReference));
                maxResidual = Mathf.Max(maxResidual, Vector3.Distance(top.TransformPoint(q), pivot));
                maxBottomPositionVariance = Mathf.Max(maxBottomPositionVariance, Vector3.Distance(bottom.position, bottomPosition));
                maxBottomRotationVariance = Mathf.Max(maxBottomRotationVariance, Quaternion.Angle(bottom.rotation, bottomRotation));
                maxProductPositionVariance = Mathf.Max(maxProductPositionVariance, Vector3.Distance(product.transform.position, productPosition));
                maxProductRotationVariance = Mathf.Max(maxProductRotationVariance, Quaternion.Angle(product.transform.rotation, productRotation));
                maxTilt = Mathf.Max(maxTilt, Vector3.Angle(top.forward, Vector3.up));
                minimumVerticalGap = Mathf.Min(minimumVerticalGap, topRenderer.bounds.min.y - bottomRenderer.bounds.max.y);
                if (slide < -1e-8f || slide > MaximumTravel + 1e-8f) illegalSlides++;
                if (!MatrixApproximately(camera.transform.localToWorldMatrix, cameraMatrix, 1e-8f)) cameraMotionFrames++;
                containmentMisses += CountCoverageMisses(topCollider, pivot, 32);

                int detent = angle >= 359.999f ? 1 : Mathf.FloorToInt((angle + 0.0001f) / 12f) % 30 + 1;
                statusText.text =
                    $"UNITY WHITE MODEL · FIXED CAMERA\n" +
                    $"{phase}\n" +
                    $"ANGLE {angle:000.0}°   DETENT {detent:00}/30   SLIDE {(slide / MaximumTravel * 100f):00}%\n" +
                    $"RED LINE = ONE FIXED WORLD AXIS · NO SHIPPING BUILD";
                if (frame is 0 or 29 or 59 or 60 or 240 or 269 or 270 or 450 or 509 or 539 or 569)
                    keyPoses.Add(new PoseRecord(frame, phase, slide, angle, fixedAxis.position, top.TransformPoint(q)));

                Canvas.ForceUpdateCanvases();
                camera.Render();
                RenderTexture.active = target;
                readback.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
                readback.Apply(false);
                File.WriteAllBytes(Path.Combine(frameDirectory, $"frame-{frame:D4}.png"), readback.EncodeToPNG());
            }

            float partialClosure = Quaternion.Angle(partialStart, partialEnd);
            float maximumClosure = Quaternion.Angle(maximumStart, maximumEnd);
            float finalClosure = Quaternion.Angle(topBaseline, top.rotation);
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
                width = Width,
                height = Height,
                frames = Frames,
                fps = 30,
                durationSeconds = Frames / 30f,
                transform = "M_top(s,theta)=T(P)*R_worldUp(theta)*T(-q(s))",
                fixedPivotMeters = new[] { pivot.x, pivot.y, pivot.z },
                q0LocalMeters = new[] { q0.x, q0.y, q0.z },
                partialSlideMeters = PartialTravel,
                maximumSlideMeters = MaximumTravel,
                maxPivotVarianceMeters = maxPivotVariance,
                maxConstraintResidualMeters = maxResidual,
                maxBottomPositionVarianceMeters = maxBottomPositionVariance,
                maxBottomRotationVarianceDegrees = maxBottomRotationVariance,
                maxProductPositionVarianceMeters = maxProductPositionVariance,
                maxProductRotationVarianceDegrees = maxProductRotationVariance,
                maxPitchRollDegrees = maxTilt,
                minimumVerticalGapMeters = minimumVerticalGap,
                containmentRayMisses = containmentMisses,
                illegalSlideFrames = illegalSlides,
                cameraMotionFrames = cameraMotionFrames,
                visitedDetentIndices = detents.OrderBy(value => value).ToArray(),
                partialRevolution = new RevolutionRecord(PartialTravel, 0f, 360f, partialClosure),
                maximumRevolution = new RevolutionRecord(MaximumTravel, 0f, 360f, maximumClosure),
                finalOrientationClosureDegrees = finalClosure,
                rendererWhitelist = activeRenderers,
                keyPoses = keyPoses.ToArray(),
                priorRecordingStatus = "valid-partial-evidence-superseded-for-full-rotation-approval",
                build = false,
                install = false,
                phone = false,
            };
            report.pass =
                maxPivotVariance <= 1e-9f
                && maxResidual <= 1e-7f
                && maxBottomPositionVariance <= 1e-9f
                && maxBottomRotationVariance <= 0.0001f
                && maxProductPositionVariance <= 1e-9f
                && maxProductRotationVariance <= 0.0001f
                && maxTilt <= 0.0001f
                && minimumVerticalGap > 0f
                && containmentMisses == 0
                && illegalSlides == 0
                && cameraMotionFrames == 0
                && detents.Count == 30
                && partialClosure <= 0.0001f
                && maximumClosure <= 0.0001f
                && finalClosure <= 0.0001f
                && activeRenderers.Length == 2;
            File.WriteAllText(
                Path.Combine(output, "unity-full-rotation-validation.json"),
                JsonUtility.ToJson(report, true));
            AssetDatabase.SaveAssets();
            if (!report.pass)
                throw new InvalidOperationException(JsonUtility.ToJson(report, true));
            Debug.Log($"GATE05_R012_FULL_ROTATION_PASS frames={Frames} detents={detents.Count} residual={maxResidual:R}");
        }

        private static Text BuildStatusOverlay(Camera camera)
        {
            GameObject canvasObject = new GameObject("FullRotationStatusCanvas");
            Canvas canvas = canvasObject.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceCamera;
            canvas.worldCamera = camera;
            canvas.planeDistance = 0.02f;
            canvas.sortingOrder = 100;
            CanvasScaler scaler = canvasObject.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920f, 1080f);

            GameObject panelObject = new GameObject("StatusPanel");
            panelObject.transform.SetParent(canvasObject.transform, false);
            Image panel = panelObject.AddComponent<Image>();
            panel.color = new Color(0.02f, 0.025f, 0.035f, 0.80f);
            RectTransform panelRect = panel.rectTransform;
            panelRect.anchorMin = new Vector2(0f, 1f);
            panelRect.anchorMax = new Vector2(0f, 1f);
            panelRect.pivot = new Vector2(0f, 1f);
            panelRect.anchoredPosition = new Vector2(36f, -36f);
            panelRect.sizeDelta = new Vector2(920f, 190f);

            GameObject textObject = new GameObject("StatusText");
            textObject.transform.SetParent(panelObject.transform, false);
            Text text = textObject.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = 34;
            text.lineSpacing = 1.05f;
            text.alignment = TextAnchor.UpperLeft;
            text.color = Color.white;
            RectTransform textRect = text.rectTransform;
            textRect.anchorMin = Vector2.zero;
            textRect.anchorMax = Vector2.one;
            textRect.offsetMin = new Vector2(28f, 20f);
            textRect.offsetMax = new Vector2(-28f, -20f);
            return text;
        }

        private static int CountCoverageMisses(MeshCollider topCollider, Vector3 pivot, int samples)
        {
            int misses = 0;
            for (int index = 0; index < samples; index++)
            {
                float angle = index * Mathf.PI * 2f / samples;
                Vector3 point = pivot + new Vector3(
                    Mathf.Cos(angle) * DiskRadius,
                    0.05f,
                    Mathf.Sin(angle) * DiskRadius);
                if (!topCollider.Raycast(new Ray(point, Vector3.down), out _, 0.1f))
                    misses++;
            }
            return misses;
        }

        private static bool MatrixApproximately(Matrix4x4 first, Matrix4x4 second, float tolerance)
        {
            for (int row = 0; row < 4; row++)
                for (int column = 0; column < 4; column++)
                    if (Mathf.Abs(first[row, column] - second[row, column]) > tolerance)
                        return false;
            return true;
        }

        private static void GetPose(int frame, out float slide, out float angle, out string phase)
        {
            if (frame < 30)
            {
                slide = 0f; angle = 0f; phase = "CLOSED · ZERO MOTION"; return;
            }
            if (frame < 60)
            {
                float t = (frame - 30) / 29f;
                slide = Mathf.Lerp(0f, PartialTravel, t);
                angle = 0f;
                phase = "OPEN TO 50% SLIDE";
                return;
            }
            if (frame <= 240)
            {
                slide = PartialTravel;
                angle = (frame - 60) * 2f;
                phase = "FULL 360° · 50% LEGAL SLIDE";
                return;
            }
            if (frame < 270)
            {
                float t = (frame - 241) / 28f;
                slide = Mathf.Lerp(PartialTravel, MaximumTravel, t);
                angle = 360f;
                phase = "OPEN TO MAXIMUM LEGAL SLIDE";
                return;
            }
            if (frame <= 450)
            {
                slide = MaximumTravel;
                angle = (frame - 270) * 2f;
                phase = "FULL 360° · MAXIMUM LEGAL SLIDE";
                return;
            }
            if (frame < 510)
            {
                float t = (frame - 451) / 58f;
                slide = Mathf.Lerp(MaximumTravel, MaximumTravel * 0.45f, t);
                angle = Mathf.Lerp(360f, 300f, t);
                phase = "COMPOUND SLIDE + ROTATION";
                return;
            }
            if (frame < 540)
            {
                float t = (frame - 510) / 29f;
                slide = Mathf.Lerp(MaximumTravel * 0.45f, 0f, t);
                angle = Mathf.Lerp(300f, 360f, t);
                phase = "RETURN TO CLOSED + 360°";
                return;
            }
            slide = 0f;
            angle = 360f;
            phase = "FINAL LOOP CLOSURE · 360° = 0°";
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
            public int width;
            public int height;
            public int frames;
            public int fps;
            public float durationSeconds;
            public string transform;
            public float[] fixedPivotMeters;
            public float[] q0LocalMeters;
            public float partialSlideMeters;
            public float maximumSlideMeters;
            public float maxPivotVarianceMeters;
            public float maxConstraintResidualMeters;
            public float maxBottomPositionVarianceMeters;
            public float maxBottomRotationVarianceDegrees;
            public float maxProductPositionVarianceMeters;
            public float maxProductRotationVarianceDegrees;
            public float maxPitchRollDegrees;
            public float minimumVerticalGapMeters;
            public int containmentRayMisses;
            public int illegalSlideFrames;
            public int cameraMotionFrames;
            public int[] visitedDetentIndices;
            public RevolutionRecord partialRevolution;
            public RevolutionRecord maximumRevolution;
            public float finalOrientationClosureDegrees;
            public string[] rendererWhitelist;
            public PoseRecord[] keyPoses;
            public string priorRecordingStatus;
            public bool build;
            public bool install;
            public bool phone;
            public bool pass;
        }

        [Serializable]
        private sealed class RevolutionRecord
        {
            public float slideMeters;
            public float startUnwrappedDegrees;
            public float endUnwrappedDegrees;
            public float orientationClosureDegrees;

            public RevolutionRecord(float slide, float start, float end, float closure)
            {
                slideMeters = slide;
                startUnwrappedDegrees = start;
                endUnwrappedDegrees = end;
                orientationClosureDegrees = closure;
            }
        }

        [Serializable]
        private sealed class PoseRecord
        {
            public int frame;
            public string phase;
            public float slideMeters;
            public float unwrappedAngleDegrees;
            public float[] pivot;
            public float[] lockedSlotPoint;

            public PoseRecord(int frame, string phase, float slide, float angle, Vector3 pivot, Vector3 locked)
            {
                this.frame = frame;
                this.phase = phase;
                slideMeters = slide;
                unwrappedAngleDegrees = angle;
                this.pivot = new[] { pivot.x, pivot.y, pivot.z };
                lockedSlotPoint = new[] { locked.x, locked.y, locked.z };
            }
        }
    }
}

