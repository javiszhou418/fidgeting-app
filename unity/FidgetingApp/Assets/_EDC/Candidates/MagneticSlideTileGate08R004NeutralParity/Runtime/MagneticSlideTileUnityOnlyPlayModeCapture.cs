using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FidgetingApp.EDC.Candidates;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.UI;

namespace FidgetingApp.EDC.Runtime
{
    public sealed class MagneticSlideTileUnityOnlyPlayModeCapture : MonoBehaviour
    {
        private const int Width = 1920;
        private const int Height = 1080;
        private const int FrameRate = 30;
        private const int FrameCount = 450;
        private const float MaximumTravel = 0.018076433f;
        private const string ImportedFbx =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R009/Imported/magnetic-slide-tile-render-r009.fbx";
        private const string SharedEnvironmentExr =
            "Assets/_EDC/Candidates/MagneticSlideTileGate08R004NeutralParity/Environment/neutral-parity-studio-r004.exr";
        private static readonly Vector3 AxisWorld = new(0f, 0f, -0.009f);
        private static readonly Vector3 HeroTarget = new(0f, 0.005f, -0.002f);
        private static readonly Vector3 HeroCamera = new(0.074f, 0.072f, -0.116f);

        [SerializeField] private Camera captureCamera;
        [SerializeField] private GameObject product;
        [SerializeField] private MagneticSlideTileGate11PreviewController poseController;
        [SerializeField] private MagneticSlideTileGate11Metadata metadata;
        [SerializeField] private string outputDirectory = "";

        private readonly List<FrameRecord> frames = new();
        private PoseBaseline baseline;
        private Transform bottom;
        private Transform fixedAxis;
        private Matrix4x4 productMatrix;
        private Matrix4x4 bottomMatrix;
        private Matrix4x4 fixedAxisMatrix;
        private RenderTexture renderTarget;
        private Texture2D readback;
        private Text title;
        private Text stateLabel;

        public void Configure(
            Camera camera,
            GameObject model,
            MagneticSlideTileGate11PreviewController controller,
            MagneticSlideTileGate11Metadata modelMetadata,
            string output)
        {
            captureCamera = camera;
            product = model;
            poseController = controller;
            metadata = modelMetadata;
            outputDirectory = output;
        }

        private void Start()
        {
            if (
                captureCamera == null
                || product == null
                || poseController == null
                || metadata == null
                || string.IsNullOrWhiteSpace(outputDirectory)
            )
            {
                Fail("Capture scene configuration is incomplete.");
                return;
            }
            bottom = FindTransform("BottomExterior");
            fixedAxis = FindTransform("FixedAxisBoss");
            baseline = new PoseBaseline(poseController);
            productMatrix = product.transform.localToWorldMatrix;
            bottomMatrix = bottom.localToWorldMatrix;
            fixedAxisMatrix = fixedAxis.localToWorldMatrix;
            Directory.CreateDirectory(outputDirectory);
            ConfigureRendering();
            CreateOverlay();
            StartCoroutine(Capture());
        }

        private void ConfigureRendering()
        {
            Time.captureFramerate = FrameRate;
            QualitySettings.vSyncCount = 0;
            Application.targetFrameRate = FrameRate;
            captureCamera.aspect = Width / (float)Height;
            renderTarget = new RenderTexture(
                Width,
                Height,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB)
            {
                name = "Gate08R004UnityOnlyPlayModeCapture",
                antiAliasing = 1,
                useMipMap = false,
                autoGenerateMips = false,
            };
            renderTarget.Create();
            captureCamera.targetTexture = renderTarget;
            readback = new Texture2D(Width, Height, TextureFormat.RGB24, false, false);
        }

        private void CreateOverlay()
        {
            GameObject canvasObject = new("UnityOnlyCaptureOverlay");
            Canvas canvas = canvasObject.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceCamera;
            canvas.worldCamera = captureCamera;
            canvas.planeDistance = 0.03f;
            canvas.sortingOrder = 1000;
            CanvasScaler scaler = canvasObject.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(Width, Height);

            Font font = Font.CreateDynamicFontFromOSFont(
                new[] { "Hiragino Sans GB", "Arial Unicode MS", "Arial" },
                30);
            title = CreateText(
                canvas.transform,
                "RuntimeLevel",
                font,
                34,
                FontStyle.Bold,
                new Vector2(48f, -40f),
                new Vector2(1200f, 52f));
            title.text = "Unity URP PlayMode · 不是 iPhone Build";
            stateLabel = CreateText(
                canvas.transform,
                "State",
                font,
                24,
                FontStyle.Normal,
                new Vector2(48f, -92f),
                new Vector2(1750f, 44f));
        }

        private static Text CreateText(
            Transform parent,
            string name,
            Font font,
            int size,
            FontStyle style,
            Vector2 position,
            Vector2 dimensions)
        {
            GameObject item = new(name);
            item.transform.SetParent(parent, false);
            Text text = item.AddComponent<Text>();
            text.font = font;
            text.fontSize = size;
            text.fontStyle = style;
            text.color = Color.white;
            text.alignment = TextAnchor.MiddleLeft;
            text.horizontalOverflow = HorizontalWrapMode.Overflow;
            text.verticalOverflow = VerticalWrapMode.Truncate;
            text.raycastTarget = false;
            text.material = font.material;
            Shadow shadow = item.AddComponent<Shadow>();
            shadow.effectColor = new Color(0f, 0f, 0f, 0.85f);
            shadow.effectDistance = new Vector2(2f, -2f);
            RectTransform rect = text.rectTransform;
            rect.anchorMin = new Vector2(0f, 1f);
            rect.anchorMax = new Vector2(0f, 1f);
            rect.pivot = new Vector2(0f, 1f);
            rect.anchoredPosition = position;
            rect.sizeDelta = dimensions;
            return text;
        }

        private IEnumerator Capture()
        {
            yield return null;
            for (int frame = 0; frame < FrameCount; frame++)
            {
                FrameState state = StateForFrame(frame);
                ApplyPose(state);
                ApplyCamera(state);
                stateLabel.text = LabelFor(state);
                Canvas.ForceUpdateCanvases();
                ValidateFrame(frame, state);
                captureCamera.Render();
                CaptureFrame(frame);
                frames.Add(FrameRecord.From(frame, state, captureCamera));
                yield return null;
            }
            WriteReport();
            Exit(0);
        }

        private static FrameState StateForFrame(int frame)
        {
            if (frame <= 44)
                return new FrameState("closed-hero", "闭合 Hero · 物体固定", 0f, 0f, 0f, 24f);
            if (frame <= 134)
            {
                float phase = (frame - 45f) / 89f;
                return new FrameState(
                    "horizontal-camera-orbit",
                    "水平相机环绕 · 物体固定",
                    35f * Mathf.Sin(phase * Mathf.PI * 2f),
                    0f,
                    0f,
                    24f);
            }
            if (frame <= 194)
            {
                float progress = Mathf.Clamp01((frame - 135f) / 59f);
                float eased = progress * progress * (3f - 2f * progress);
                return new FrameState(
                    "legal-top-slide",
                    "顶片沿槽轴直推 · 底座与固定轴不动",
                    0f,
                    0f,
                    MaximumTravel * eased,
                    24f);
            }
            if (frame <= 224)
                return new FrameState(
                    "max-open",
                    "最大合法直推 · +Z 旋转 0°",
                    0f,
                    0f,
                    MaximumTravel,
                    24f);
            if (frame <= 269)
                return new FrameState(
                    "detent-12",
                    "顶片 +Z 旋转 · 12° detent",
                    0f,
                    12f,
                    0f,
                    24f);
            if (frame <= 314)
                return new FrameState(
                    "detent-36",
                    "顶片 +Z 旋转 · 36° detent",
                    0f,
                    36f,
                    0f,
                    24f);
            if (frame <= 374)
                return new FrameState(
                    "combined-legal",
                    "合法复合姿态 · 半行程 + 12°",
                    0f,
                    12f,
                    MaximumTravel * 0.5f,
                    24f);
            if (frame <= 419)
                return new FrameState(
                    "four-track-inspection",
                    "四轨 / 凸起轴检查 · 仅切换后侧低机位",
                    180f,
                    36f,
                    MaximumTravel,
                    12f);
            return new FrameState(
                "end-closed",
                "结束 · 闭合 Hero · 物体固定",
                0f,
                0f,
                0f,
                24f);
        }

        private void ApplyPose(FrameState state)
        {
            Quaternion yaw = Quaternion.AngleAxis(-state.angleDegrees, Vector3.up);
            float radians = state.angleDegrees * Mathf.Deg2Rad;
            Vector3 slide = new(
                Mathf.Sin(radians) * state.travelMeters,
                0f,
                -Mathf.Cos(radians) * state.travelMeters);
            baseline.RestoreLogicalParents(poseController);
            foreach (PoseEntry entry in baseline.carrierRenderers)
                entry.Apply(AxisWorld, yaw, Vector3.zero);
            foreach (PoseEntry entry in baseline.topRenderers)
                entry.Apply(AxisWorld, yaw, slide);
        }

        private void ApplyCamera(FrameState state)
        {
            Vector3 baseOffset = HeroCamera - HeroTarget;
            float horizontalDistance = new Vector2(baseOffset.x, baseOffset.z).magnitude;
            float baseYaw = Mathf.Atan2(baseOffset.x, baseOffset.z) * Mathf.Rad2Deg;
            float yaw = baseYaw - state.cameraYawDegrees;
            float pitch = state.cameraPitchDegrees * Mathf.Deg2Rad;
            float horizontal = Mathf.Cos(pitch) * Vector3.Distance(HeroCamera, HeroTarget);
            if (state.cameraPitchDegrees == 24f)
                horizontal = horizontalDistance;
            Vector3 position = HeroTarget + new Vector3(
                Mathf.Sin(yaw * Mathf.Deg2Rad) * horizontal,
                Mathf.Tan(pitch) * horizontal,
                Mathf.Cos(yaw * Mathf.Deg2Rad) * horizontal);
            captureCamera.transform.position = position;
            captureCamera.transform.LookAt(HeroTarget, Vector3.up);
        }

        private static string LabelFor(FrameState state)
        {
            return $"{state.displayName}  |  camera yaw {state.cameraYawDegrees:F1}°"
                + $"  |  top +Z {state.angleDegrees:F0}°"
                + $"  |  travel {state.travelMeters * 1000f:F2} mm";
        }

        private void ValidateFrame(int frame, FrameState state)
        {
            const float tolerance = 0.0001f;
            AssertMatrix(product.transform.localToWorldMatrix, productMatrix, "product", frame);
            AssertMatrix(bottom.localToWorldMatrix, bottomMatrix, "BottomExterior", frame);
            AssertMatrix(fixedAxis.localToWorldMatrix, fixedAxisMatrix, "FixedAxisBoss", frame);
            if (Vector3.Dot(product.transform.up, Vector3.up) < 0.99999f)
                throw new InvalidOperationException($"Frame {frame}: product vertical flip.");
            if (state.travelMeters < -tolerance || state.travelMeters > MaximumTravel + tolerance)
                throw new InvalidOperationException($"Frame {frame}: illegal slide.");
            if (
                Mathf.Abs(state.angleDegrees) > 36f + tolerance
                || (
                    Mathf.Abs(state.angleDegrees) > tolerance
                    && Mathf.Abs(state.angleDegrees - 12f) > tolerance
                    && Mathf.Abs(state.angleDegrees - 36f) > tolerance
                )
            )
                throw new InvalidOperationException($"Frame {frame}: illegal angle.");
            if (
                Quaternion.Angle(
                    poseController.RotatingCarrier.rotation,
                    baseline.carrierRotation) > tolerance
                || Quaternion.Angle(
                    poseController.MovingTop.rotation,
                    baseline.movingTopRotation) > tolerance
            )
                throw new InvalidOperationException(
                    $"Frame {frame}: logical hierarchy gained pitch or roll.");
            Quaternion expectedYaw = Quaternion.AngleAxis(-state.angleDegrees, Vector3.up);
            float radians = state.angleDegrees * Mathf.Deg2Rad;
            Vector3 expectedSlide = new(
                Mathf.Sin(radians) * state.travelMeters,
                0f,
                -Mathf.Cos(radians) * state.travelMeters);
            foreach (PoseEntry entry in baseline.carrierRenderers)
                entry.Validate(AxisWorld, expectedYaw, Vector3.zero, tolerance, frame);
            foreach (PoseEntry entry in baseline.topRenderers)
                entry.Validate(AxisWorld, expectedYaw, expectedSlide, tolerance, frame);
            foreach (Transform item in product.GetComponentsInChildren<Transform>(true))
            {
                Vector3 scale = item.localScale;
                if (scale.x <= 0f || scale.y <= 0f || scale.z <= 0f)
                    throw new InvalidOperationException(
                        $"Frame {frame}: {item.name} has negative scale.");
            }
            if (
                Mathf.Abs(captureCamera.transform.right.y) > tolerance
                || captureCamera.transform.up.y <= 0f
            )
                throw new InvalidOperationException(
                    $"Frame {frame}: camera roll or horizon failure.");
        }

        private static void AssertMatrix(
            Matrix4x4 actual,
            Matrix4x4 expected,
            string label,
            int frame)
        {
            for (int index = 0; index < 16; index++)
            {
                if (Mathf.Abs(actual[index] - expected[index]) > 0.000001f)
                    throw new InvalidOperationException(
                        $"Frame {frame}: fixed {label} transform changed.");
            }
        }

        private void CaptureFrame(int frame)
        {
            RenderTexture previous = RenderTexture.active;
            RenderTexture.active = renderTarget;
            readback.ReadPixels(new Rect(0, 0, Width, Height), 0, 0, false);
            readback.Apply(false, false);
            RenderTexture.active = previous;
            File.WriteAllBytes(
                Path.Combine(outputDirectory, $"frame-{frame:D4}.png"),
                readback.EncodeToPNG());
        }

        private void WriteReport()
        {
            MaterialRecord[] materials = product
                .GetComponentsInChildren<Renderer>(true)
                .SelectMany(renderer => renderer.sharedMaterials)
                .Where(material => material != null)
                .Distinct()
                .Select(MaterialRecord.From)
                .ToArray();
            CaptureReport report = new()
            {
                pass = true,
                evidenceLevel = "Unity Editor PlayMode",
                onScreenDisclosure = "Unity URP PlayMode · 不是 iPhone Build",
                unityVersion = Application.unityVersion,
                renderPipeline = GraphicsSettings.currentRenderPipeline != null
                    ? GraphicsSettings.currentRenderPipeline.name
                    : "Built-in",
                scene = gameObject.scene.path,
                dimensions = new[] { Width, Height },
                frameRate = FrameRate,
                frameCount = FrameCount,
                durationSeconds = FrameCount / (float)FrameRate,
                gate10GlbSha256 = metadata.Gate10GlbSha256,
                geometryDigest = metadata.GeometryDigest,
                portabilityContractSha256 = metadata.PortabilityContractSha256,
                importedFbx = ImportedFbx,
                importedFbxSha256 = HashAsset(ImportedFbx),
                sharedEnvironmentExr = SharedEnvironmentExr,
                sharedEnvironmentExrSha256 = HashAsset(SharedEnvironmentExr),
                captureSceneSha256 = HashAsset(gameObject.scene.path),
                maximumTravelMeters = metadata.MaximumTravelMeters,
                detentCount = metadata.DetentCount,
                detentStepDegrees = metadata.DetentStepDegrees,
                blenderFrameCount = 0,
                offlineCompositeCount = 0,
                perFrameTransformValidation = true,
                shippingSceneModified = false,
                iPhoneBuild = false,
                materials = materials,
                camera = CameraRecord.From(captureCamera),
                frames = frames.ToArray(),
            };
            File.WriteAllText(
                Path.Combine(outputDirectory, "unity-playmode-capture-report.json"),
                JsonUtility.ToJson(report, true) + Environment.NewLine);
        }

        private Transform FindTransform(string name)
        {
            return product.GetComponentsInChildren<Transform>(true)
                .Single(item => item.name == name);
        }

        private static string HashAsset(string assetPath)
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string absolutePath = Path.Combine(projectRoot, assetPath);
            using System.Security.Cryptography.SHA256 algorithm =
                System.Security.Cryptography.SHA256.Create();
            using FileStream stream = File.OpenRead(absolutePath);
            return BitConverter.ToString(algorithm.ComputeHash(stream))
                .Replace("-", "")
                .ToLowerInvariant();
        }

        private void Fail(string message)
        {
            Debug.LogError(message);
            Exit(1);
        }

        private static void Exit(int code)
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.Exit(code);
#else
            Application.Quit(code);
#endif
        }

        [Serializable]
        private readonly struct FrameState
        {
            public readonly string state;
            public readonly string displayName;
            public readonly float cameraYawDegrees;
            public readonly float angleDegrees;
            public readonly float travelMeters;
            public readonly float cameraPitchDegrees;

            public FrameState(
                string state,
                string displayName,
                float cameraYawDegrees,
                float angleDegrees,
                float travelMeters,
                float cameraPitchDegrees)
            {
                this.state = state;
                this.displayName = displayName;
                this.cameraYawDegrees = cameraYawDegrees;
                this.angleDegrees = angleDegrees;
                this.travelMeters = travelMeters;
                this.cameraPitchDegrees = cameraPitchDegrees;
            }
        }

        [Serializable]
        private sealed class FrameRecord
        {
            public int frame;
            public float timeSeconds;
            public string state;
            public float cameraYawDegrees;
            public float cameraPitchDegrees;
            public float topZDegrees;
            public float travelMeters;
            public float cameraRollDegrees;
            public bool fixedTransforms;
            public bool positiveScale;

            public static FrameRecord From(int frame, FrameState state, Camera camera)
            {
                return new FrameRecord
                {
                    frame = frame,
                    timeSeconds = frame / (float)FrameRate,
                    state = state.state,
                    cameraYawDegrees = state.cameraYawDegrees,
                    cameraPitchDegrees = state.cameraPitchDegrees,
                    topZDegrees = state.angleDegrees,
                    travelMeters = state.travelMeters,
                    cameraRollDegrees = 0f,
                    fixedTransforms = true,
                    positiveScale = true,
                };
            }
        }

        [Serializable]
        private sealed class MaterialRecord
        {
            public string material;
            public string shader;
            public string environment;
            public float emission;

            public static MaterialRecord From(Material source)
            {
                Texture environment = source.HasProperty("_EnvironmentCube")
                    ? source.GetTexture("_EnvironmentCube")
                    : null;
                return new MaterialRecord
                {
                    material = source.name,
                    shader = source.shader != null ? source.shader.name : "missing",
                    environment = environment != null ? environment.name : "",
                    emission = source.IsKeywordEnabled("_EMISSION") ? 1f : 0f,
                };
            }
        }

        [Serializable]
        private sealed class CaptureReport
        {
            public bool pass;
            public string evidenceLevel;
            public string onScreenDisclosure;
            public string unityVersion;
            public string renderPipeline;
            public string scene;
            public int[] dimensions;
            public int frameRate;
            public int frameCount;
            public float durationSeconds;
            public string gate10GlbSha256;
            public string geometryDigest;
            public string portabilityContractSha256;
            public string importedFbx;
            public string importedFbxSha256;
            public string sharedEnvironmentExr;
            public string sharedEnvironmentExrSha256;
            public string captureSceneSha256;
            public float maximumTravelMeters;
            public int detentCount;
            public float detentStepDegrees;
            public int blenderFrameCount;
            public int offlineCompositeCount;
            public bool perFrameTransformValidation;
            public bool shippingSceneModified;
            public bool iPhoneBuild;
            public MaterialRecord[] materials;
            public CameraRecord camera;
            public FrameRecord[] frames;
        }

        [Serializable]
        private sealed class CameraRecord
        {
            public string name;
            public float fieldOfView;
            public float nearClip;
            public float farClip;
            public float aspect;
            public float[] heroPosition;
            public float[] heroTarget;
            public string orbitPolicy;

            public static CameraRecord From(Camera source)
            {
                return new CameraRecord
                {
                    name = source.name,
                    fieldOfView = source.fieldOfView,
                    nearClip = source.nearClipPlane,
                    farClip = source.farClipPlane,
                    aspect = Width / (float)Height,
                    heroPosition = new[] { HeroCamera.x, HeroCamera.y, HeroCamera.z },
                    heroTarget = new[] { HeroTarget.x, HeroTarget.y, HeroTarget.z },
                    orbitPolicy =
                        "horizontal yaw only; stable world-up; zero roll; rear low inspection uses a labeled camera cut",
                };
            }
        }

        private sealed class PoseBaseline
        {
            public readonly Vector3 carrierPosition;
            public readonly Quaternion carrierRotation;
            public readonly Vector3 movingTopPosition;
            public readonly Quaternion movingTopRotation;
            public readonly Vector3 topSlidePosition;
            public readonly Quaternion topSlideRotation;
            public readonly PoseEntry[] carrierRenderers;
            public readonly PoseEntry[] topRenderers;

            public PoseBaseline(MagneticSlideTileGate11PreviewController controller)
            {
                carrierPosition = controller.RotatingCarrier.position;
                carrierRotation = controller.RotatingCarrier.rotation;
                movingTopPosition = controller.MovingTop.position;
                movingTopRotation = controller.MovingTop.rotation;
                topSlidePosition = controller.TopLocalSlide.position;
                topSlideRotation = controller.TopLocalSlide.rotation;
                carrierRenderers = controller.RotatingCarrier
                    .GetComponentsInChildren<Renderer>(true)
                    .Select(renderer => new PoseEntry(renderer.transform))
                    .ToArray();
                topRenderers = controller.MovingTop
                    .GetComponentsInChildren<Renderer>(true)
                    .Select(renderer => new PoseEntry(renderer.transform))
                    .ToArray();
            }

            public void RestoreLogicalParents(
                MagneticSlideTileGate11PreviewController controller)
            {
                controller.RotatingCarrier.SetPositionAndRotation(
                    carrierPosition,
                    carrierRotation);
                controller.MovingTop.SetPositionAndRotation(
                    movingTopPosition,
                    movingTopRotation);
                controller.TopLocalSlide.SetPositionAndRotation(
                    topSlidePosition,
                    topSlideRotation);
            }
        }

        private sealed class PoseEntry
        {
            private readonly Transform item;
            private readonly Vector3 position;
            private readonly Quaternion rotation;

            public PoseEntry(Transform item)
            {
                this.item = item;
                position = item.position;
                rotation = item.rotation;
            }

            public void Apply(Vector3 axis, Quaternion yaw, Vector3 slide)
            {
                item.SetPositionAndRotation(
                    axis + yaw * (position - axis) + slide,
                    yaw * rotation);
            }

            public void Validate(
                Vector3 axis,
                Quaternion yaw,
                Vector3 slide,
                float tolerance,
                int frame)
            {
                Vector3 expectedPosition = axis + yaw * (position - axis) + slide;
                Quaternion expectedRotation = yaw * rotation;
                if (
                    Vector3.Distance(item.position, expectedPosition) > tolerance
                    || Quaternion.Angle(item.rotation, expectedRotation) > tolerance
                )
                    throw new InvalidOperationException(
                        $"Frame {frame}: {item.name} left its legal transform.");
            }
        }
    }
}
