using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.UI;

namespace FidgetingApp.EDC.Candidates
{
    public sealed class MagneticSlideTileGate11R011PlayModeCapture : MonoBehaviour
    {
        private const int Width = 1920;
        private const int Height = 1080;
        private const int FrameRate = 30;
        private const int FrameCount = 540;

        [SerializeField] private Camera captureCamera;
        [SerializeField] private MagneticSlideTileEndpointInterlockController controller;
        [SerializeField] private Transform productRoot;
        [SerializeField] private string outputDirectory;
        [SerializeField] private Vector3 orbitTarget = new(0f, 0.005f, -0.002f);
        [SerializeField] private Vector3 heroCamera = new(0.074f, 0.072f, -0.116f);

        private readonly List<FrameRecord> frames = new();
        private Matrix4x4 productBaseline;
        private float cameraElevation;
        private float orbitRadius;
        private Text stateLabel;

        public void Configure(
            Camera camera,
            MagneticSlideTileEndpointInterlockController endpointController,
            Transform root,
            string output)
        {
            captureCamera = camera;
            controller = endpointController;
            productRoot = root;
            outputDirectory = output;
        }

        private void Start()
        {
            Time.captureFramerate = FrameRate;
            Directory.CreateDirectory(outputDirectory);
            productBaseline = productRoot.localToWorldMatrix;
            cameraElevation = heroCamera.y;
            orbitRadius = Vector2.Distance(
                new Vector2(heroCamera.x, heroCamera.z),
                new Vector2(orbitTarget.x, orbitTarget.z));
            BuildOverlay();
            controller.ResetPose();
            StartCoroutine(Capture());
        }

        private IEnumerator Capture()
        {
            yield return null;
            for (int frame = 0; frame < FrameCount; frame++)
            {
                FrameIntent intent = ApplyFrameIntent(frame);
                ApplyCamera(intent.orbitDegrees);
                stateLabel.text =
                    "Unity URP PlayMode · 不是 iPhone Build\n"
                    + intent.label
                    + $"\nframe {frame + 1:D3}/{FrameCount} · "
                    + $"s={controller.TravelMeters * 1000f:F2} mm · "
                    + $"θ={controller.AngleDegrees:F0}°";
                Canvas.ForceUpdateCanvases();
                ValidateFrame(frame, intent);
                captureCamera.Render();
                CaptureFrame(frame);
                frames.Add(FrameRecord.Create(frame, intent, captureCamera, controller));
                yield return null;
            }

            WriteReport();
#if UNITY_EDITOR
            UnityEditor.EditorApplication.ExitPlaymode();
            UnityEditor.EditorApplication.delayCall += () => UnityEditor.EditorApplication.Exit(0);
#else
            Application.Quit(0);
#endif
        }

        private FrameIntent ApplyFrameIntent(int frame)
        {
            if (frame < 45)
            {
                controller.ResetPose();
                return new FrameIntent("Closed hero · zero motion", 0f, true);
            }

            if (frame < 90)
            {
                controller.TrySetAngle(0f);
                controller.TrySetTravel(controller.MaximumTravelMeters * 0.5f);
                bool rejected = !controller.TrySetAngle(12f);
                return new FrameIntent(
                    "Mid-travel rotation attempt · correctly locked",
                    Mathf.Lerp(-18f, 18f, (frame - 45) / 44f),
                    rejected);
            }

            if (frame < 150)
            {
                controller.TrySetAngle(0f);
                float t = (frame - 90) / 59f;
                controller.TrySetTravel(
                    Mathf.Lerp(controller.MaximumTravelMeters * 0.5f,
                        controller.MaximumTravelMeters, t));
                return new FrameIntent("Legal top slide to sMax", 18f, true);
            }

            if (frame < 210)
            {
                controller.TrySetTravel(controller.MaximumTravelMeters);
                controller.TrySetAngle(0f);
                return new FrameIntent(
                    "Maximum open · rotation unlocked", 18f, true);
            }

            if (frame < 390)
            {
                controller.TrySetTravel(controller.MaximumTravelMeters);
                int detent = Mathf.Min(30, ((frame - 210) / 6) + 1);
                controller.TrySetEndpointDetent(detent);
                float orbit = Mathf.Sin((frame - 210) * Mathf.PI / 179f) * 25f;
                return new FrameIntent(
                    $"Endpoint full rotation · detent {detent:D2}/30",
                    orbit,
                    true);
            }

            if (frame < 435)
            {
                controller.TrySetEndpointDetent(3);
                bool rejected = !controller.TrySetTravel(0f);
                return new FrameIntent(
                    "Return attempt at 36° · slide correctly locked",
                    -18f,
                    rejected);
            }

            if (frame < 480)
            {
                controller.TrySetAngle(0f);
                return new FrameIntent(
                    "Align top to 0° · slide unlocked", -18f, true);
            }

            if (frame < 525)
            {
                controller.TrySetAngle(0f);
                float t = (frame - 480) / 44f;
                controller.TrySetTravel(
                    Mathf.Lerp(controller.MaximumTravelMeters, 0f, t));
                return new FrameIntent("Legal aligned close", Mathf.Lerp(-18f, 0f, t), true);
            }

            controller.ResetPose();
            return new FrameIntent("Closed · zero motion end hold", 0f, true);
        }

        private void ApplyCamera(float orbitDegrees)
        {
            Vector3 radial = heroCamera - orbitTarget;
            radial.y = 0f;
            radial = Quaternion.AngleAxis(orbitDegrees, Vector3.up) * radial.normalized
                * orbitRadius;
            captureCamera.transform.position =
                orbitTarget + radial + Vector3.up * (cameraElevation - orbitTarget.y);
            captureCamera.transform.rotation = Quaternion.LookRotation(
                orbitTarget - captureCamera.transform.position, Vector3.up);
        }

        private void ValidateFrame(int frame, FrameIntent intent)
        {
            if (!MatrixApproximately(productRoot.localToWorldMatrix, productBaseline))
                throw new InvalidDataException($"Frame {frame}: product root moved.");
            if (!controller.IsPoseLegal())
                throw new InvalidDataException($"Frame {frame}: illegal endpoint pose.");
            if (!intent.expectedTransitionResult)
                throw new InvalidDataException($"Frame {frame}: expected transition result failed.");
            if (Mathf.Abs(captureCamera.transform.position.y - cameraElevation) > 0.000001f)
                throw new InvalidDataException($"Frame {frame}: camera elevation changed.");
            if (Mathf.Abs(Vector3.Dot(captureCamera.transform.right, Vector3.up)) > 0.00001f)
                throw new InvalidDataException($"Frame {frame}: camera roll is nonzero.");
            Vector3 rootUp = productRoot.transform.up;
            if (Vector3.Angle(rootUp, Vector3.up) > 0.0001f)
                throw new InvalidDataException($"Frame {frame}: product pitch/roll detected.");
            Vector3 scale = productRoot.lossyScale;
            if (scale.x <= 0f || scale.y <= 0f || scale.z <= 0f)
                throw new InvalidDataException($"Frame {frame}: inversion detected.");
            if (Mathf.Abs(controller.LinearVelocityMetersPerSecond) > 0.000001f
                || Mathf.Abs(controller.AngularVelocityDegreesPerSecond) > 0.0001f)
                throw new InvalidDataException($"Frame {frame}: self-motion detected.");
        }

        private void CaptureFrame(int frame)
        {
            RenderTexture target = new(
                Width, Height, 24, RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.Default);
            RenderTexture previousTarget = captureCamera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            try
            {
                target.Create();
                captureCamera.targetTexture = target;
                captureCamera.Render();
                RenderTexture.active = target;
                Texture2D image = new(Width, Height, TextureFormat.RGBA32, false, false);
                image.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
                image.Apply(false, false);
                File.WriteAllBytes(
                    Path.Combine(outputDirectory, $"frame-{frame:D4}.png"),
                    image.EncodeToPNG());
                Destroy(image);
            }
            finally
            {
                captureCamera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                target.Release();
                Destroy(target);
            }
        }

        private void BuildOverlay()
        {
            GameObject canvasObject = new("Gate11R011CaptureOverlay");
            Canvas canvas = canvasObject.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasObject.AddComponent<CanvasScaler>().referenceResolution =
                new Vector2(Width, Height);
            GameObject textObject = new("EvidenceLabel");
            textObject.transform.SetParent(canvasObject.transform, false);
            stateLabel = textObject.AddComponent<Text>();
            stateLabel.font = Font.CreateDynamicFontFromOSFont(
                new[] { "PingFang SC", "Helvetica Neue", "Arial Unicode MS" }, 28);
            stateLabel.fontSize = 28;
            stateLabel.color = new Color(0.95f, 0.97f, 0.98f, 1f);
            stateLabel.alignment = TextAnchor.UpperLeft;
            stateLabel.horizontalOverflow = HorizontalWrapMode.Overflow;
            stateLabel.verticalOverflow = VerticalWrapMode.Overflow;
            RectTransform rect = stateLabel.rectTransform;
            rect.anchorMin = new Vector2(0f, 1f);
            rect.anchorMax = new Vector2(0f, 1f);
            rect.pivot = new Vector2(0f, 1f);
            rect.anchoredPosition = new Vector2(42f, -36f);
            rect.sizeDelta = new Vector2(1100f, 130f);
        }

        private void WriteReport()
        {
            CaptureReport report = new()
            {
                schemaVersion = 1,
                gate = "11-unity-parity",
                revision = 11,
                unityVersion = Application.unityVersion,
                runtimeLevel = "Editor PlayMode",
                scenePath =
                    "Assets/_EDC/Candidates/MagneticSlideTileGate11R011/Scenes/MagneticSlideTileGate11R011Parity.unity",
                width = Width,
                height = Height,
                fps = FrameRate,
                frameCount = FrameCount,
                durationSeconds = (float)FrameCount / FrameRate,
                cameraName = captureCamera.name,
                urpShader = "FidgetingApp/MagneticSlideTile/PortablePBRR011",
                sharedEnvironmentOnly = true,
                blenderFrames = 0,
                offlineCompositeFrames = 0,
                productPitchRollDegrees = 0f,
                cameraRollDegrees = 0f,
                cameraElevationVarianceMeters = 0f,
                fixedBottomAndAxis = true,
                endpointInterlock = true,
                fullRotationDetents = 30,
                closedZeroMotion = true,
                buildInstallPhone = false,
                frames = frames.ToArray(),
                pass = frames.Count == FrameCount,
            };
            File.WriteAllText(
                Path.Combine(outputDirectory, "unity-playmode-capture-report.json"),
                JsonUtility.ToJson(report, true) + Environment.NewLine);
        }

        private static bool MatrixApproximately(Matrix4x4 first, Matrix4x4 second)
        {
            for (int row = 0; row < 4; row++)
            for (int column = 0; column < 4; column++)
            {
                if (Mathf.Abs(first[row, column] - second[row, column]) > 0.000001f)
                    return false;
            }
            return true;
        }

        [Serializable]
        private readonly struct FrameIntent
        {
            public readonly string label;
            public readonly float orbitDegrees;
            public readonly bool expectedTransitionResult;

            public FrameIntent(
                string frameLabel,
                float cameraOrbitDegrees,
                bool transitionResult)
            {
                label = frameLabel;
                orbitDegrees = cameraOrbitDegrees;
                expectedTransitionResult = transitionResult;
            }
        }

        [Serializable]
        private sealed class FrameRecord
        {
            public int frame;
            public string label;
            public float travelMillimeters;
            public float angleDegrees;
            public string transition;
            public Vector3 cameraPosition;

            public static FrameRecord Create(
                int index,
                FrameIntent intent,
                Camera camera,
                MagneticSlideTileEndpointInterlockController endpointController)
            {
                return new FrameRecord
                {
                    frame = index,
                    label = intent.label,
                    travelMillimeters = endpointController.TravelMeters * 1000f,
                    angleDegrees = endpointController.AngleDegrees,
                    transition = endpointController.LastTransition,
                    cameraPosition = camera.transform.position,
                };
            }
        }

        [Serializable]
        private sealed class CaptureReport
        {
            public int schemaVersion;
            public string gate;
            public int revision;
            public string unityVersion;
            public string runtimeLevel;
            public string scenePath;
            public int width;
            public int height;
            public int fps;
            public int frameCount;
            public float durationSeconds;
            public string cameraName;
            public string urpShader;
            public bool sharedEnvironmentOnly;
            public int blenderFrames;
            public int offlineCompositeFrames;
            public float productPitchRollDegrees;
            public float cameraRollDegrees;
            public float cameraElevationVarianceMeters;
            public bool fixedBottomAndAxis;
            public bool endpointInterlock;
            public int fullRotationDetents;
            public bool closedZeroMotion;
            public bool buildInstallPhone;
            public FrameRecord[] frames;
            public bool pass;
        }
    }
}
