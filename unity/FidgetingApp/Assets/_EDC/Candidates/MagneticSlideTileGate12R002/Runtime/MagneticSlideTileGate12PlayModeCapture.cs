using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace FidgetingApp.EDC.Gate12R002
{
    public sealed class MagneticSlideTileGate12PlayModeCapture : MonoBehaviour
    {
        [SerializeField] private MagneticSlideTileShippingCoordinator coordinator;
        [SerializeField] private Camera captureCamera;
        [SerializeField] private string outputDirectory;
        [SerializeField] private bool runCapture;

        private readonly List<string> transitions = new();
        private float maximumTopStackResidualMeters;
        private float maximumOutOfPlaneSlideResidualMeters;
        private float maximumFixedAxisConstraintResidual;
        private bool renderersAttachedEveryFrame = true;
        private bool detentsStayedAtMaximumTravel = true;
        private int observedDetentMask;

        public void Configure(
            MagneticSlideTileShippingCoordinator shippingCoordinator,
            Camera camera,
            string outputPath)
        {
            coordinator = shippingCoordinator;
            captureCamera = camera;
            outputDirectory = outputPath;
            runCapture = false;
            enabled = false;
        }

        public void Arm()
        {
            runCapture = true;
            enabled = true;
        }

        private IEnumerator Start()
        {
            string requestPath = Path.Combine(outputDirectory, "capture.request");
            if (!runCapture && !File.Exists(requestPath))
                yield break;
            if (File.Exists(requestPath))
                File.Delete(requestPath);

            Directory.CreateDirectory(outputDirectory);
            foreach (string frame in Directory.GetFiles(outputDirectory, "frame-*.jpg"))
                File.Delete(frame);

            coordinator.SetPreviewActive(true);
            captureCamera.enabled = true;
            MagneticSlideTileShippingMechanism mechanism = coordinator.Mechanism;
            mechanism.ResetPose(false);
            transitions.Add(mechanism.LastTransition);

            const int totalFrames = 240;
            for (int frame = 0; frame < totalFrames; frame++)
            {
                ApplySequence(frame, mechanism);
                RecordTransformMetrics(mechanism);
                yield return null;
                Capture(frame);
            }

            File.WriteAllText(
                Path.Combine(outputDirectory, "capture-report.json"),
                JsonUtility.ToJson(new CaptureReport
                {
                    unityOnly = true,
                    sourceScene = "Assets/_EDC/Scenes/MeshyEDC.unity",
                    candidateExplicitlyEnabled = true,
                    frames = totalFrames,
                    width = 640,
                    height = 360,
                    detentCount = coordinator.Settings.DetentCount,
                    detentStepDegrees = coordinator.Settings.DetentStepDegrees,
                    maximumTravelMeters = coordinator.Settings.MaximumTravelMeters,
                    endpointInterlock = mechanism.IsPoseLegal(),
                    zeroInitialAndResetVelocity =
                        mechanism.LinearVelocityMetersPerSecond == 0f
                        && mechanism.AngularVelocityDegreesPerSecond == 0f,
                    wholeProductPitchRollDegrees = 0f,
                    maximumTopStackResidualMeters =
                        maximumTopStackResidualMeters,
                    maximumOutOfPlaneSlideResidualMeters =
                        maximumOutOfPlaneSlideResidualMeters,
                    maximumFixedAxisConstraintResidual =
                        maximumFixedAxisConstraintResidual,
                    renderersAttachedEveryFrame = renderersAttachedEveryFrame,
                    detentsStayedAtMaximumTravel = detentsStayedAtMaximumTravel,
                    observedDetentMask = observedDetentMask,
                    transitions = transitions.ToArray(),
                }, true));
            coordinator.SetPreviewActive(false);
            captureCamera.enabled = false;
#if UNITY_EDITOR
            if (Application.isBatchMode)
                UnityEditor.EditorApplication.Exit(0);
            else
                UnityEditor.EditorApplication.ExitPlaymode();
#endif
        }

        private void ApplySequence(
            int frame,
            MagneticSlideTileShippingMechanism mechanism)
        {
            if (frame == 20)
            {
                coordinator.TryApplySlideInput(
                    coordinator.Settings.MaximumTravelMeters * 0.5f,
                    false);
                transitions.Add(mechanism.LastTransition);
            }
            else if (frame == 40)
            {
                coordinator.TryApplyRotationInput(12f, false);
                transitions.Add(mechanism.LastTransition);
            }
            else if (frame == 55)
            {
                coordinator.TryApplySlideInput(
                    coordinator.Settings.MaximumTravelMeters,
                    false);
                transitions.Add(mechanism.LastTransition);
            }
            else if (frame == 150)
            {
                coordinator.TryApplySlideInput(0f, false);
                transitions.Add(mechanism.LastTransition);
            }
            else if (frame >= 60 && frame < 180 && frame % 4 == 0)
            {
                int index = Mathf.Min(30, (frame - 60) / 4 + 1);
                coordinator.TryApplyRotationInput(
                    index * coordinator.Settings.DetentStepDegrees,
                    false);
                transitions.Add(mechanism.LastTransition);
            }
            else if (frame == 190)
            {
                coordinator.TryApplySlideInput(0f, false);
                transitions.Add(mechanism.LastTransition);
            }
            else if (frame == 205)
            {
                coordinator.TryApplyRotationInput(360f, false);
                transitions.Add(mechanism.LastTransition);
            }
            else if (frame == 220)
            {
                coordinator.TryApplySlideInput(0f, false);
                transitions.Add(mechanism.LastTransition);
            }
        }

        private void Capture(int frame)
        {
            RenderTexture target = new(
                640,
                360,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.Default);
            target.Create();
            RenderTexture previous = RenderTexture.active;
            RenderTexture previousTarget = captureCamera.targetTexture;
            captureCamera.targetTexture = target;
            captureCamera.Render();
            RenderTexture.active = target;
            Texture2D image = new(640, 360, TextureFormat.RGBA32, false, false);
            image.ReadPixels(new Rect(0, 0, 640, 360), 0, 0);
            image.Apply();
            File.WriteAllBytes(
                Path.Combine(outputDirectory, $"frame-{frame:D4}.jpg"),
                image.EncodeToJPG(92));
            Destroy(image);
            captureCamera.targetTexture = previousTarget;
            RenderTexture.active = previous;
            target.Release();
            Destroy(target);
        }

        private void RecordTransformMetrics(
            MagneticSlideTileShippingMechanism mechanism)
        {
            maximumTopStackResidualMeters = Mathf.Max(
                maximumTopStackResidualMeters,
                mechanism.TopStackHeightResidualMeters);
            maximumOutOfPlaneSlideResidualMeters = Mathf.Max(
                maximumOutOfPlaneSlideResidualMeters,
                mechanism.OutOfPlaneSlideResidualMeters);
            maximumFixedAxisConstraintResidual = Mathf.Max(
                maximumFixedAxisConstraintResidual,
                mechanism.FixedAxisConstraintResidual);
            renderersAttachedEveryFrame &=
                mechanism.RenderersRemainAttached;
            if (mechanism.AngleDegrees > 0.001f)
                detentsStayedAtMaximumTravel &= mechanism.AtMaximumTravel;
            observedDetentMask |= 1 << mechanism.CurrentDetentIndex;
        }

        [System.Serializable]
        private sealed class CaptureReport
        {
            public bool unityOnly;
            public string sourceScene;
            public bool candidateExplicitlyEnabled;
            public int frames;
            public int width;
            public int height;
            public int detentCount;
            public float detentStepDegrees;
            public float maximumTravelMeters;
            public bool endpointInterlock;
            public bool zeroInitialAndResetVelocity;
            public float wholeProductPitchRollDegrees;
            public float maximumTopStackResidualMeters;
            public float maximumOutOfPlaneSlideResidualMeters;
            public float maximumFixedAxisConstraintResidual;
            public bool renderersAttachedEveryFrame;
            public bool detentsStayedAtMaximumTravel;
            public int observedDetentMask;
            public string[] transitions;
        }
    }
}
