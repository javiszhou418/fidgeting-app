using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using FidgetingApp.EDC.Candidates;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.Editor
{
    public static class MagneticSlideTileNeutralParityPreviewBuilder
    {
        private const string ScenePath =
            "Assets/_EDC/Candidates/MagneticSlideTileGate08R004NeutralParity/Scenes/MagneticSlideTileNeutralParityR004.unity";
        private const int Width = 1400;
        private const int Height = 1100;
        private const int FrameCount = 180;
        private const int SourceFps = 15;
        private const float MaximumTravel = 0.018076433f;
        private static readonly Vector3 Target = new(0f, 0.005f, -0.002f);
        private static readonly Vector3 BaseCamera = new(0.074f, 0.072f, -0.116f);

        [MenuItem("Fidgeting/Model Pipeline/Render Gate 08 R004 Preview")]
        public static void RenderSupplementalPreview()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string output = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-004/supplemental-preview");
            string frameRoot = Path.Combine(output, "unity");
            Directory.CreateDirectory(frameRoot);

            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            MagneticSlideTileGate11PreviewController controller =
                scene.GetRootGameObjects()
                    .SelectMany(root => root.GetComponentsInChildren<MagneticSlideTileGate11PreviewController>(true))
                    .Single();
            Camera camera = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<Camera>(true))
                .Single(item => item.name == "CAM_Gate08R004NeutralParity");
            controller.Configure(
                controller.RotatingCarrier,
                controller.MovingTop,
                controller.TopLocalSlide,
                camera,
                null,
                Vector3.up,
                Vector3.forward);
            controller.ResetPose();
            Transform product = controller.transform;
            Transform bottom = product.GetComponentsInChildren<Transform>(true)
                .Single(item => item.name == "BottomExterior");
            Transform fixedAxis = product.GetComponentsInChildren<Transform>(true)
                .Single(item => item.name == "FixedAxisBoss");
            Quaternion bottomBaseline = bottom.rotation;
            Quaternion fixedAxisBaseline = fixedAxis.rotation;
            PoseBaseline poseBaseline = new(controller);
            HashSet<int> selectedFrames = SelectedFrames();

            List<FrameRecord> records = new();
            for (int frame = 0; frame < FrameCount; frame++)
            {
                FrameRecord state = FrameState(frame);
                records.Add(state);
                ApplyLegalPose(controller, poseBaseline, state);
                SetCamera(camera, state.yaw);
                state.validation = ValidateFrame(
                    product,
                    bottom,
                    fixedAxis,
                    bottomBaseline,
                    fixedAxisBaseline,
                    poseBaseline,
                    controller,
                    camera,
                    state);
                if (state.state == "clay" || !selectedFrames.Contains(frame))
                    continue;
                RenderLinear(
                    camera,
                    Path.Combine(frameRoot, $"frame-{frame:0000}-linear.exr"));
            }
            ApplyLegalPose(
                controller,
                poseBaseline,
                State(0, "closed-hero", "hold", 0f, 0f, 0f));
            camera.transform.position = BaseCamera;
            camera.transform.LookAt(Target);

            PreviewReport report = new()
            {
                engine = $"Unity {Application.unityVersion} URP",
                scene = ScenePath,
                frameCount = FrameCount,
                sourceFps = SourceFps,
                resolution = new[] { Width, Height },
                cameraTarget = new[] { Target.x, Target.y, Target.z },
                baseCamera = new[] { BaseCamera.x, BaseCamera.y, BaseCamera.z },
                frames = records.ToArray(),
            };
            File.WriteAllText(
                Path.Combine(output, "unity-frame-metadata.json"),
                JsonUtility.ToJson(report, true) + Environment.NewLine);
            AssetDatabase.Refresh();
        }

        private static HashSet<int> SelectedFrames()
        {
            string[] arguments = Environment.GetCommandLineArgs();
            int index = Array.IndexOf(arguments, "-previewFrameRange");
            if (index < 0 || index + 1 >= arguments.Length)
                return Enumerable.Range(0, FrameCount).ToHashSet();
            string[] range = arguments[index + 1].Split(':');
            int start = int.Parse(range[0], CultureInfo.InvariantCulture);
            int end = int.Parse(range[1], CultureInfo.InvariantCulture);
            return Enumerable.Range(start, end - start + 1).ToHashSet();
        }

        private static FrameRecord FrameState(int frame)
        {
            if (frame <= 22)
                return State(frame, "closed-hero", "hold", 0f, 0f, 0f);
            if (frame <= 74)
            {
                float phase = (frame - 23f) / (74f - 23f);
                return State(
                    frame,
                    "closed-camera-orbit",
                    "camera-orbit",
                    35f * Mathf.Sin(phase * Mathf.PI * 2f),
                    0f,
                    0f);
            }
            if (frame <= 89)
                return State(
                    frame, "detent-12", "top-z-rotation", 0f, 12f, 0f);
            if (frame <= 104)
                return State(
                    frame, "detent-36", "top-z-rotation", 0f, 36f, 0f);
            if (frame <= 119)
                return State(
                    frame, "max-open", "top-slide", 0f, 0f, MaximumTravel);
            if (frame <= 134)
                return State(
                    frame,
                    "combined-legal",
                    "top-slide-and-z-rotation",
                    0f,
                    12f,
                    MaximumTravel * 0.5f);
            if (frame <= 149)
                return State(frame, "clay", "diagnostic", 0f, 0f, 0f);
            return State(frame, "end-closed", "hold", 0f, 0f, 0f);
        }

        private static FrameRecord State(
            int frame,
            string name,
            string mode,
            float yaw,
            float angle,
            float travel)
        {
            return new FrameRecord
            {
                frame = frame,
                time = frame / (float)SourceFps,
                state = name,
                mode = mode,
                yaw = yaw,
                angle = angle,
                travelMeters = travel,
            };
        }

        private static void SetCamera(Camera camera, float blenderYaw)
        {
            Vector3 offset = BaseCamera - Target;
            camera.transform.position =
                Target + Quaternion.AngleAxis(-blenderYaw, Vector3.up) * offset;
            camera.transform.LookAt(Target, Vector3.up);
        }

        private static void ApplyLegalPose(
            MagneticSlideTileGate11PreviewController controller,
            PoseBaseline baseline,
            FrameRecord state)
        {
            Quaternion yaw = Quaternion.AngleAxis(-state.angle, Vector3.up);
            controller.RotatingCarrier.position = baseline.carrierPosition;
            controller.RotatingCarrier.rotation = baseline.carrierRotation;
            controller.MovingTop.position = baseline.movingTopPosition;
            controller.MovingTop.rotation = baseline.movingTopRotation;
            controller.TopLocalSlide.position = baseline.topSlidePosition;
            float radians = state.angle * Mathf.Deg2Rad;
            Vector3 canonicalSlideInUnity = new(
                Mathf.Sin(radians) * state.travelMeters,
                0f,
                -Mathf.Cos(radians) * state.travelMeters);
            foreach (PoseEntry entry in baseline.carrierRenderers)
                entry.Apply(baseline.axisWorld, yaw, Vector3.zero);
            foreach (PoseEntry entry in baseline.topRenderers)
                entry.Apply(baseline.axisWorld, yaw, canonicalSlideInUnity);
        }

        private static FrameValidation ValidateFrame(
            Transform product,
            Transform bottom,
            Transform fixedAxis,
            Quaternion bottomBaseline,
            Quaternion fixedAxisBaseline,
            PoseBaseline baseline,
            MagneticSlideTileGate11PreviewController controller,
            Camera camera,
            FrameRecord state)
        {
            const float tolerance = 0.0001f;
            Vector3 productRotation = CanonicalEuler(product.rotation);
            if (Mathf.Abs(productRotation.x) > tolerance
                || Mathf.Abs(productRotation.y) > tolerance
                || Mathf.Abs(productRotation.z) > tolerance
                || Quaternion.Angle(bottom.rotation, bottomBaseline) > tolerance
                || Quaternion.Angle(fixedAxis.rotation, fixedAxisBaseline) > tolerance)
                throw new InvalidOperationException(
                    "Bottom assembly left its fixed imported basis.");
            Quaternion expectedYaw =
                Quaternion.AngleAxis(-state.angle, Vector3.up);
            if (Quaternion.Angle(
                    controller.RotatingCarrier.rotation,
                    baseline.carrierRotation) > tolerance
                || Quaternion.Angle(
                    controller.MovingTop.rotation,
                    baseline.movingTopRotation) > tolerance)
                throw new InvalidOperationException(
                    "Logical moving parents gained pitch, roll or hidden rotation.");
            float radians = state.angle * Mathf.Deg2Rad;
            Vector3 expectedSlide = new(
                Mathf.Sin(radians) * state.travelMeters,
                0f,
                -Mathf.Cos(radians) * state.travelMeters);
            if (state.travelMeters < -tolerance
                || state.travelMeters > MaximumTravel + tolerance)
                throw new InvalidOperationException(
                    "TopLocalSlide left its converted groove axis.");
            foreach (PoseEntry entry in baseline.carrierRenderers)
                entry.Validate(
                    baseline.axisWorld, expectedYaw, Vector3.zero, tolerance);
            foreach (PoseEntry entry in baseline.topRenderers)
                entry.Validate(
                    baseline.axisWorld, expectedYaw, expectedSlide, tolerance);
            foreach (Transform item in product.GetComponentsInChildren<Transform>(true))
            {
                Vector3 scale = item.localScale;
                if (scale.x <= 0f || scale.y <= 0f || scale.z <= 0f)
                    throw new InvalidOperationException(
                        $"{item.name} has a negative scale or inversion.");
            }
            Vector3 offset = camera.transform.position - Target;
            Vector3 baseOffset = BaseCamera - Target;
            float elevation = Mathf.Atan2(
                offset.y,
                new Vector2(offset.x, offset.z).magnitude) * Mathf.Rad2Deg;
            float baseElevation = Mathf.Atan2(
                baseOffset.y,
                new Vector2(baseOffset.x, baseOffset.z).magnitude) * Mathf.Rad2Deg;
            if (Mathf.Abs(elevation - baseElevation) > tolerance
                || Mathf.Abs(camera.transform.right.y) > tolerance
                || camera.transform.up.y <= 0f)
                throw new InvalidOperationException(
                    "Camera roll/elevation invariant failed.");
            return new FrameValidation
            {
                fixedPitchRollZero = true,
                fixedTransformUnchanged = true,
                topPitchRollZero = true,
                topYawDegrees = state.angle,
                travelMeters = state.travelMeters,
                positiveScale = true,
                cameraRollDegrees = 0f,
                cameraElevationDegrees = elevation,
            };
        }

        private static Vector3 CanonicalEuler(Quaternion unityRotation)
        {
            Vector3 unity = unityRotation.eulerAngles;
            return new Vector3(
                Mathf.DeltaAngle(0f, unity.x),
                Mathf.DeltaAngle(0f, unity.z),
                Mathf.DeltaAngle(0f, unity.y));
        }

        private sealed class PoseBaseline
        {
            public readonly Vector3 axisWorld;
            public readonly Vector3 carrierPosition;
            public readonly Quaternion carrierRotation;
            public readonly Vector3 movingTopPosition;
            public readonly Quaternion movingTopRotation;
            public readonly Vector3 topSlidePosition;
            public readonly PoseEntry[] carrierRenderers;
            public readonly PoseEntry[] topRenderers;

            public PoseBaseline(MagneticSlideTileGate11PreviewController controller)
            {
                axisWorld = new Vector3(0f, 0f, -0.009f);
                carrierPosition = controller.RotatingCarrier.position;
                carrierRotation = controller.RotatingCarrier.rotation;
                movingTopPosition = controller.MovingTop.position;
                movingTopRotation = controller.MovingTop.rotation;
                topSlidePosition = controller.TopLocalSlide.position;
                carrierRenderers = controller.RotatingCarrier
                    .GetComponentsInChildren<Renderer>(true)
                    .Select(renderer => new PoseEntry(renderer.transform))
                    .ToArray();
                topRenderers = controller.MovingTop
                    .GetComponentsInChildren<Renderer>(true)
                    .Select(renderer => new PoseEntry(renderer.transform))
                    .ToArray();
                Debug.Log(
                    $"G08R4_PREVIEW_BASELINE axis={axisWorld:F6} "
                    + $"carrierRenderers={carrierRenderers.Length} "
                    + $"topRenderers={topRenderers.Length} "
                    + $"top={string.Join(",", topRenderers.Select(item => item.Name))}");
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

            public string Name => item.name;

            public void Apply(Vector3 axis, Quaternion yaw, Vector3 slide)
            {
                item.position = axis + yaw * (position - axis) + slide;
                item.rotation = yaw * rotation;
            }

            public void Validate(
                Vector3 axis,
                Quaternion yaw,
                Vector3 slide,
                float tolerance)
            {
                Vector3 expectedPosition = axis + yaw * (position - axis) + slide;
                Quaternion expectedRotation = yaw * rotation;
                if ((item.position - expectedPosition).magnitude > tolerance
                    || Quaternion.Angle(item.rotation, expectedRotation) > tolerance)
                    throw new InvalidOperationException(
                        $"{item.name} left its converted canonical transform.");
            }
        }

        private static void RenderLinear(Camera camera, string path)
        {
            RenderTexture texture = new(
                Width, Height, 24, RenderTextureFormat.ARGBFloat,
                RenderTextureReadWrite.Linear);
            texture.Create();
            RenderTexture previous = camera.targetTexture;
            camera.targetTexture = texture;
            UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(
                camera,
                new UnityEngine.Rendering.RenderPipeline.StandardRequest
                {
                    destination = texture
                });
            RenderTexture.active = texture;
            Texture2D image = new(
                Width, Height, TextureFormat.RGBAFloat, false, true);
            image.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
            image.Apply(false, false);
            File.WriteAllBytes(
                path,
                image.EncodeToEXR(
                    Texture2D.EXRFlags.OutputAsFloat
                    | Texture2D.EXRFlags.CompressZIP));
            camera.targetTexture = previous;
            RenderTexture.active = null;
            UnityEngine.Object.DestroyImmediate(image);
            texture.Release();
            UnityEngine.Object.DestroyImmediate(texture);
        }

        [Serializable]
        private sealed class PreviewReport
        {
            public string engine = "";
            public string scene = "";
            public int frameCount;
            public int sourceFps;
            public int[] resolution = Array.Empty<int>();
            public float[] cameraTarget = Array.Empty<float>();
            public float[] baseCamera = Array.Empty<float>();
            public FrameRecord[] frames = Array.Empty<FrameRecord>();
        }

        [Serializable]
        private sealed class FrameRecord
        {
            public int frame;
            public float time;
            public string state = "";
            public string mode = "";
            public float yaw;
            public float angle;
            public float travelMeters;
            public FrameValidation validation = new();
        }

        [Serializable]
        private sealed class FrameValidation
        {
            public bool fixedPitchRollZero;
            public bool fixedTransformUnchanged;
            public bool topPitchRollZero;
            public float topYawDegrees;
            public float travelMeters;
            public bool positiveScale;
            public float cameraRollDegrees;
            public float cameraElevationDegrees;
        }
    }
}
