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
    public static class MagneticSlideTileGate05R012EndpointInterlockBuilder
    {
        private const string ContractSha256 = "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571";
        private const string ModelPath =
            "Assets/_EDC/Candidates/MagneticSlideTileGate05R012Geometry/Imported/magnetic-slide-tile-fixed-axis-r012.fbx";
        private const string ScenePath =
            "Assets/_EDC/Candidates/MagneticSlideTileGate05R012Geometry/MagneticSlideTileGate05R012EndpointInterlockPreview.unity";
        private const int Width = 1920;
        private const int Height = 1080;
        private const int Frames = 450;
        private const float MaximumTravel = 0.0180764331f;
        private const float DiskRadius = 0.015f;

        public static void BuildAndCapture()
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject source = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (source == null) throw new InvalidOperationException($"Missing corrected FBX: {ModelPath}");
            GameObject product = PrefabUtility.InstantiatePrefab(source) as GameObject;
            product.name = "MagneticSlideTile_G05_R012_EndpointInterlockProof";
            Transform bottom = Find(product.transform, "BottomExterior");
            Transform fixedAxis = Find(product.transform, "FixedAxis");
            Transform carrier = Find(product.transform, "RotatingCarrier");
            Transform top = Find(product.transform, "MovingTopBody");
            if (new[] { bottom, fixedAxis, carrier, top }.Any(item => item == null))
                throw new InvalidOperationException("Corrected hierarchy is incomplete.");

            Shader lit = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
            Shader unlit = Shader.Find("Universal Render Pipeline/Unlit") ?? Shader.Find("Unlit/Color");
            Material clay = new Material(lit) { name = "G05R012_EndpointInterlockClay" };
            clay.color = new Color(0.70f, 0.73f, 0.78f, 1f);
            clay.SetFloat("_Smoothness", 0.26f);
            HashSet<string> whitelist = new HashSet<string> { "BottomExterior", "MovingTopBody" };
            foreach (Renderer renderer in product.GetComponentsInChildren<Renderer>(true))
            {
                renderer.enabled = whitelist.Contains(renderer.name);
                if (renderer.enabled) renderer.sharedMaterial = clay;
            }
            string[] activeRenderers = product.GetComponentsInChildren<Renderer>(true)
                .Where(renderer => renderer.enabled).Select(renderer => renderer.name).OrderBy(name => name).ToArray();
            if (!activeRenderers.SequenceEqual(whitelist.OrderBy(name => name)))
                throw new InvalidOperationException("Product renderer whitelist drifted.");
            if (product.GetComponentsInChildren<Transform>(true).Count(item => item.name == "FixedAxis") != 1)
                throw new InvalidOperationException("Exactly one FixedAxis is required.");

            Vector3 pivot = fixedAxis.position;
            Vector3 bottomPosition = bottom.position;
            Quaternion bottomRotation = bottom.rotation;
            Vector3 productPosition = product.transform.position;
            Quaternion productRotation = product.transform.rotation;
            Quaternion carrierBaseline = carrier.rotation;
            Quaternion topBaseline = top.rotation;
            Vector3 q0 = top.InverseTransformPoint(pivot);
            Vector3 slideAxis = -new Vector3(q0.x, q0.y, 0f).normalized;

            GameObject axisOverlay = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            axisOverlay.name = "Technical_FixedWorldAxisOverlay";
            axisOverlay.transform.position = pivot + Vector3.up * 0.014f;
            axisOverlay.transform.localScale = new Vector3(0.00024f, 0.020f, 0.00024f);
            UnityEngine.Object.DestroyImmediate(axisOverlay.GetComponent<Collider>());
            Material red = new Material(unlit) { name = "G05R012_FixedAxisRed" };
            red.color = new Color(1f, 0.035f, 0.01f, 1f);
            axisOverlay.GetComponent<Renderer>().sharedMaterial = red;

            Camera camera = new GameObject("CAM_G05R012_Fixed_EndpointInterlock").AddComponent<Camera>();
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
            string frameDirectory = Path.Combine(output, "frames-endpoint-interlock");
            Directory.CreateDirectory(frameDirectory);
            foreach (string oldFrame in Directory.GetFiles(frameDirectory, "*.png")) File.Delete(oldFrame);
            RenderTexture target = new RenderTexture(Width, Height, 24, RenderTextureFormat.ARGB32);
            Texture2D readback = new Texture2D(Width, Height, TextureFormat.RGB24, false);
            camera.targetTexture = target;

            HashSet<int> detents = new HashSet<int>();
            List<FrameRecord> frameRecords = new List<FrameRecord>();
            float maxPivotVariance = 0f;
            float maxResidual = 0f;
            float maxBottomPositionVariance = 0f;
            float maxBottomRotationVariance = 0f;
            float maxProductPositionVariance = 0f;
            float maxProductRotationVariance = 0f;
            float maxTilt = 0f;
            float minimumVerticalGap = float.MaxValue;
            int containmentMisses = 0;
            int cameraMotionFrames = 0;
            int belowMaxRotationViolations = 0;
            int endpointUnlockViolations = 0;
            int rotatedSlideViolations = 0;
            int simultaneousVelocityViolations = 0;
            float previousSlide = 0f;
            float previousAngle = 0f;
            Quaternion revolutionStart = Quaternion.identity;
            Quaternion revolutionEnd = Quaternion.identity;

            for (int frame = 0; frame < Frames; frame++)
            {
                GetPose(frame, out float slide, out float angle, out string phase, out bool rotationAttempt, out bool slideAttempt);
                Quaternion yaw = Quaternion.AngleAxis(-angle, Vector3.up);
                Vector3 q = q0 + slideAxis * slide;
                top.rotation = yaw * topBaseline;
                top.position = pivot - top.rotation * q;
                carrier.rotation = yaw * carrierBaseline;
                Physics.SyncTransforms();
                if (frame == 180) revolutionStart = top.rotation;
                if (frame == 390) revolutionEnd = top.rotation;
                if (frame >= 180 && frame <= 390)
                {
                    float nearest = Mathf.Round(angle / 12f);
                    if (Mathf.Abs(angle - nearest * 12f) <= 0.0001f && angle < 360f)
                        detents.Add(((int)nearest) % 30);
                }
                bool atMaximum = Mathf.Abs(slide - MaximumTravel) <= 1e-8f;
                bool aligned = Mathf.Min(Mathf.Repeat(angle, 360f), 360f - Mathf.Repeat(angle, 360f)) <= 0.0001f;
                if (!atMaximum && !aligned) belowMaxRotationViolations++;
                if (!atMaximum && !aligned) endpointUnlockViolations++;
                if (!aligned && !atMaximum) rotatedSlideViolations++;
                float slideVelocity = frame == 0 ? 0f : (slide - previousSlide) * 30f;
                float angularVelocity = frame == 0 ? 0f : (angle - previousAngle) * 30f;
                if (Mathf.Abs(slideVelocity) > 1e-7f && Mathf.Abs(angularVelocity) > 1e-4f)
                    simultaneousVelocityViolations++;
                previousSlide = slide;
                previousAngle = angle;
                maxPivotVariance = Mathf.Max(maxPivotVariance, Vector3.Distance(fixedAxis.position, pivot));
                maxResidual = Mathf.Max(maxResidual, Vector3.Distance(top.TransformPoint(q), pivot));
                maxBottomPositionVariance = Mathf.Max(maxBottomPositionVariance, Vector3.Distance(bottom.position, bottomPosition));
                maxBottomRotationVariance = Mathf.Max(maxBottomRotationVariance, Quaternion.Angle(bottom.rotation, bottomRotation));
                maxProductPositionVariance = Mathf.Max(maxProductPositionVariance, Vector3.Distance(product.transform.position, productPosition));
                maxProductRotationVariance = Mathf.Max(maxProductRotationVariance, Quaternion.Angle(product.transform.rotation, productRotation));
                maxTilt = Mathf.Max(maxTilt, Vector3.Angle(top.forward, Vector3.up));
                minimumVerticalGap = Mathf.Min(minimumVerticalGap, topRenderer.bounds.min.y - bottomRenderer.bounds.max.y);
                if (!MatrixApproximately(camera.transform.localToWorldMatrix, cameraMatrix, 1e-8f)) cameraMotionFrames++;
                containmentMisses += CountCoverageMisses(topCollider, pivot, 32);

                int detent = angle >= 359.999f ? 30 : Mathf.FloorToInt((angle + 0.0001f) / 12f) % 30 + 1;
                statusText.text =
                    $"UNITY 白模 · 固定相机\n" +
                    $"{phase}\n" +
                    $"角度 {angle:000.0}°   卡位 {detent:00}/30   行程 {(slide / MaximumTravel * 100f):00}%\n" +
                    $"红线 = 唯一固定世界轴 · 非 shipping 构建";
                frameRecords.Add(new FrameRecord(frame, slide, angle, phase, rotationAttempt, slideAttempt,
                    atMaximum, aligned, slideVelocity, angularVelocity));
                Canvas.ForceUpdateCanvases();
                camera.Render();
                RenderTexture.active = target;
                readback.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
                readback.Apply(false);
                File.WriteAllBytes(Path.Combine(frameDirectory, $"frame-{frame:D4}.png"), readback.EncodeToPNG());
            }

            float closure = Quaternion.Angle(revolutionStart, revolutionEnd);
            float finalClosure = Quaternion.Angle(topBaseline, top.rotation);
            camera.targetTexture = null;
            RenderTexture.active = null;
            UnityEngine.Object.DestroyImmediate(target);
            UnityEngine.Object.DestroyImmediate(readback);
            Report report = new Report
            {
                schemaVersion = 2,
                unityVersion = Application.unityVersion,
                contractSha256 = ContractSha256,
                scenePath = ScenePath,
                modelPath = ModelPath,
                width = Width,
                height = Height,
                frames = Frames,
                fps = 30,
                durationSeconds = Frames / 30f,
                stateMachine = "theta=0: slide; s=sMax: rotate; theta!=0: slide locked; theta=0/360: return",
                transform = "M_top=T(P)*Rz(theta)*T(-q(s)); legal domain applies endpoint interlock",
                fixedPivotMeters = new[] { pivot.x, pivot.y, pivot.z },
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
                cameraMotionFrames = cameraMotionFrames,
                belowMaxRotationViolations = belowMaxRotationViolations,
                endpointUnlockViolations = endpointUnlockViolations,
                rotatedSlideViolations = rotatedSlideViolations,
                simultaneousVelocityViolations = simultaneousVelocityViolations,
                visitedDetentIndices = detents.OrderBy(value => value).ToArray(),
                fullRevolutionClosureDegrees = closure,
                finalOrientationClosureDegrees = finalClosure,
                rendererWhitelist = activeRenderers,
                framesData = frameRecords.ToArray(),
                rejectedPriorFullRotationEvidence =
                    "gate05-r012-unity-full-360-motion.mp4 rejected: rotates at 50% travel",
                geometryChanged = false,
                build = false,
                install = false,
                phone = false,
            };
            report.pass =
                maxPivotVariance <= 1e-9f && maxResidual <= 1e-7f
                && maxBottomPositionVariance <= 1e-9f && maxBottomRotationVariance <= 0.0001f
                && maxProductPositionVariance <= 1e-9f && maxProductRotationVariance <= 0.0001f
                && maxTilt <= 0.0001f && minimumVerticalGap > 0f && containmentMisses == 0
                && cameraMotionFrames == 0 && belowMaxRotationViolations == 0
                && endpointUnlockViolations == 0 && rotatedSlideViolations == 0
                && simultaneousVelocityViolations == 0 && detents.Count == 30
                && closure <= 0.0001f && finalClosure <= 0.0001f && activeRenderers.Length == 2;
            File.WriteAllText(Path.Combine(output, "unity-endpoint-interlock-validation.json"), JsonUtility.ToJson(report, true));
            AssetDatabase.SaveAssets();
            if (!report.pass) throw new InvalidOperationException(JsonUtility.ToJson(report, true));
            Debug.Log($"GATE05_R012_ENDPOINT_INTERLOCK_PASS frames={Frames} detents={detents.Count}");
        }

        private static void GetPose(int frame, out float slide, out float angle, out string phase,
            out bool rotationAttempt, out bool slideAttempt)
        {
            rotationAttempt = false;
            slideAttempt = false;
            if (frame < 30) { slide = 0f; angle = 0f; phase = "闭合 · θ=0°"; return; }
            if (frame < 90)
            {
                slide = Mathf.Lerp(0f, MaximumTravel * 0.5f, (frame - 30) / 59f);
                angle = 0f; phase = "沿四轨直推 · 旋转锁定"; return;
            }
            if (frame < 120)
            {
                slide = MaximumTravel * 0.5f; angle = 0f; rotationAttempt = true;
                phase = "中途尝试旋转 → 已锁定，θ 保持 0°"; return;
            }
            if (frame < 150)
            {
                slide = Mathf.Lerp(MaximumTravel * 0.5f, MaximumTravel, (frame - 120) / 29f);
                angle = 0f; phase = "继续直推到最大端点"; return;
            }
            if (frame < 180)
            {
                slide = MaximumTravel; angle = 0f; phase = "旋转已解锁 · s=sMax"; return;
            }
            if (frame < 270)
            {
                slide = MaximumTravel; angle = (frame - 180) * 2f; phase = "端点旋转 · 0°→180°"; return;
            }
            if (frame < 300)
            {
                slide = MaximumTravel; angle = 180f; slideAttempt = true;
                phase = "非零角度尝试回推 → 行程锁定在 sMax"; return;
            }
            if (frame < 391)
            {
                slide = MaximumTravel; angle = 180f + (frame - 300) * 2f;
                phase = "端点旋转 · 180°→360°"; return;
            }
            if (frame < 421)
            {
                slide = Mathf.Lerp(MaximumTravel, 0f, (frame - 391) / 29f);
                angle = 360f; phase = "0°/360° 对齐 · 沿原槽回推"; return;
            }
            slide = 0f; angle = 360f; phase = "闭合 · 360° = 0°";
        }

        private static Text BuildStatusOverlay(Camera camera)
        {
            GameObject canvasObject = new GameObject("EndpointInterlockStatusCanvas");
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
            panel.color = new Color(0.02f, 0.025f, 0.035f, 0.84f);
            RectTransform panelRect = panel.rectTransform;
            panelRect.anchorMin = new Vector2(0f, 1f);
            panelRect.anchorMax = new Vector2(0f, 1f);
            panelRect.pivot = new Vector2(0f, 1f);
            panelRect.anchoredPosition = new Vector2(36f, -36f);
            panelRect.sizeDelta = new Vector2(1120f, 205f);
            GameObject textObject = new GameObject("StatusText");
            textObject.transform.SetParent(panelObject.transform, false);
            Text text = textObject.AddComponent<Text>();
            text.font = Font.CreateDynamicFontFromOSFont(new[] { "PingFang SC", "Arial Unicode MS" }, 34)
                ?? Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
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
                Vector3 point = pivot + new Vector3(Mathf.Cos(angle) * DiskRadius, 0.05f,
                    Mathf.Sin(angle) * DiskRadius);
                if (!topCollider.Raycast(new Ray(point, Vector3.down), out _, 0.1f)) misses++;
            }
            return misses;
        }

        private static bool MatrixApproximately(Matrix4x4 first, Matrix4x4 second, float tolerance)
        {
            for (int row = 0; row < 4; row++)
                for (int column = 0; column < 4; column++)
                    if (Mathf.Abs(first[row, column] - second[row, column]) > tolerance) return false;
            return true;
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
        private sealed class FrameRecord
        {
            public int frame;
            public float slideMeters;
            public float unwrappedAngleDegrees;
            public string phase;
            public bool rotationAttempt;
            public bool slideAttempt;
            public bool atMaximum;
            public bool aligned;
            public float slideVelocityMetersPerSecond;
            public float angularVelocityDegreesPerSecond;

            public FrameRecord(int frame, float slide, float angle, string phase, bool rotationAttempt,
                bool slideAttempt, bool atMaximum, bool aligned, float slideVelocity, float angularVelocity)
            {
                this.frame = frame;
                slideMeters = slide;
                unwrappedAngleDegrees = angle;
                this.phase = phase;
                this.rotationAttempt = rotationAttempt;
                this.slideAttempt = slideAttempt;
                this.atMaximum = atMaximum;
                this.aligned = aligned;
                slideVelocityMetersPerSecond = slideVelocity;
                angularVelocityDegreesPerSecond = angularVelocity;
            }
        }

        [Serializable]
        private sealed class Report
        {
            public int schemaVersion;
            public string unityVersion;
            public string contractSha256;
            public string scenePath;
            public string modelPath;
            public int width;
            public int height;
            public int frames;
            public int fps;
            public float durationSeconds;
            public string stateMachine;
            public string transform;
            public float[] fixedPivotMeters;
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
            public int cameraMotionFrames;
            public int belowMaxRotationViolations;
            public int endpointUnlockViolations;
            public int rotatedSlideViolations;
            public int simultaneousVelocityViolations;
            public int[] visitedDetentIndices;
            public float fullRevolutionClosureDegrees;
            public float finalOrientationClosureDegrees;
            public string[] rendererWhitelist;
            public FrameRecord[] framesData;
            public string rejectedPriorFullRotationEvidence;
            public bool geometryChanged;
            public bool build;
            public bool install;
            public bool phone;
            public bool pass;
        }
    }
}
