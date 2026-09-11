using System;
using System.IO;
using UnityEngine;

namespace FidgetingApp.EDC.Candidates.ModelHhax
{
    /// <summary>
    /// Direct, deterministic pose control for the model-hhax reconstruction.
    /// There is deliberately no Update loop, easing, inertia, detent, haptic,
    /// or slide/rotation coupling. A caller must explicitly set every pose.
    /// </summary>
    public sealed class ModelHhaxDirectPoseController : MonoBehaviour
    {
        public const float MaximumTravelMm = 18.7f;

        [SerializeField] private Transform movingUpper;
        [SerializeField] private Transform rearRotor;
        [SerializeField] private Vector3 slideAxisLocal = Vector3.forward;
        [SerializeField] private Vector3 rotorAxisLocal = Vector3.up;

        private Vector3 upperClosedLocalPosition;
        private Quaternion rotorClosedLocalRotation;
        private bool configured;

        public Transform MovingUpper => movingUpper;
        public Transform RearRotor => rearRotor;
        public float TravelMm { get; private set; }
        public float RotorAngleDegrees { get; private set; }

        public void Configure(Transform upper, Transform rotor, Vector3 slideAxis, Vector3 rotorAxis)
        {
            movingUpper = upper != null ? upper : throw new ArgumentNullException(nameof(upper));
            rearRotor = rotor != null ? rotor : throw new ArgumentNullException(nameof(rotor));
            slideAxisLocal = slideAxis.normalized;
            rotorAxisLocal = rotorAxis.normalized;
            CaptureClosedPose();
            ResetPose();
        }

        private void Awake()
        {
            if (!configured && movingUpper != null && rearRotor != null)
                CaptureClosedPose();
        }

        private void CaptureClosedPose()
        {
            upperClosedLocalPosition = movingUpper.localPosition;
            rotorClosedLocalRotation = rearRotor.localRotation;
            configured = true;
        }

        public void SetTravelMm(float travelMm)
        {
            EnsureConfigured();
            TravelMm = Mathf.Clamp(travelMm, 0f, MaximumTravelMm);
            movingUpper.localPosition = upperClosedLocalPosition + slideAxisLocal * (TravelMm * 0.001f);
        }

        public void SetRotorAngleDegrees(float angleDegrees)
        {
            EnsureConfigured();
            RotorAngleDegrees = Mathf.Repeat(angleDegrees, 360f);
            rearRotor.localRotation = rotorClosedLocalRotation * Quaternion.AngleAxis(RotorAngleDegrees, rotorAxisLocal);
        }

        public void ResetPose()
        {
            EnsureConfigured();
            TravelMm = 0f;
            RotorAngleDegrees = 0f;
            movingUpper.localPosition = upperClosedLocalPosition;
            rearRotor.localRotation = rotorClosedLocalRotation;
        }

        private void EnsureConfigured()
        {
            if (!configured)
            {
                if (movingUpper == null || rearRotor == null)
                    throw new InvalidOperationException("model-hhax direct-pose controller is not configured.");
                CaptureClosedPose();
            }
        }
    }

    /// <summary>
    /// Evidence-only PlayMode recorder. It drives the direct-pose API explicitly
    /// and is never stored on the candidate prefab or used as shipping behaviour.
    /// </summary>
    public sealed class ModelHhaxRuntimeEvidenceCapture : MonoBehaviour
    {
        [SerializeField] private ModelHhaxDirectPoseController controller;
        [SerializeField] private Camera reviewCamera;
        [SerializeField] private Light[] reviewLights;
        [SerializeField] private Renderer floorRenderer;
        [SerializeField] private string outputDirectory;
        [SerializeField] private int width = 900;
        [SerializeField] private int height = 900;
        [SerializeField] private int frameCount = 180;

        private int frame;
        private Vector3 closedUpperPosition;
        private Quaternion closedRotorRotation;
        private Color ambientColor;

        public void Configure(
            ModelHhaxDirectPoseController directController,
            Camera camera,
            Light[] lights,
            Renderer floor,
            string output,
            int captureWidth,
            int captureHeight,
            int frames)
        {
            controller = directController;
            reviewCamera = camera;
            reviewLights = lights;
            floorRenderer = floor;
            outputDirectory = output;
            width = captureWidth;
            height = captureHeight;
            frameCount = frames;
        }

        private void Start()
        {
            if (controller == null || reviewCamera == null || string.IsNullOrWhiteSpace(outputDirectory))
                throw new InvalidOperationException("model-hhax runtime capture is not configured.");
            Directory.CreateDirectory(outputDirectory);
            controller.ResetPose();
            closedUpperPosition = controller.MovingUpper.localPosition;
            closedRotorRotation = controller.RearRotor.localRotation;
            ambientColor = RenderSettings.ambientLight;
            Time.captureFramerate = 30;
        }

        private void LateUpdate()
        {
            ApplyEvidencePose(frame);
            CaptureFrame(frame);
            frame += 1;
            if (frame >= frameCount)
                Finish();
        }

        private void ApplyEvidencePose(int index)
        {
            // 0–29: closed idle. 30–69: explicit straight slide.
            // 70–99: open hold. 100–129: independent rear rotation.
            // 130–149: rotated hold. 150–179: closed dark material proof.
            if (index < 30)
            {
                controller.ResetPose();
            }
            else if (index < 70)
            {
                controller.SetTravelMm(Mathf.Lerp(0f, ModelHhaxDirectPoseController.MaximumTravelMm,
                    (index - 30) / 39f));
                controller.SetRotorAngleDegrees(0f);
            }
            else if (index < 100)
            {
                controller.SetTravelMm(ModelHhaxDirectPoseController.MaximumTravelMm);
                controller.SetRotorAngleDegrees(0f);
            }
            else if (index < 130)
            {
                controller.SetTravelMm(ModelHhaxDirectPoseController.MaximumTravelMm);
                controller.SetRotorAngleDegrees(Mathf.Lerp(0f, 135f, (index - 100) / 29f));
            }
            else if (index < 150)
            {
                controller.SetTravelMm(ModelHhaxDirectPoseController.MaximumTravelMm);
                controller.SetRotorAngleDegrees(135f);
            }
            else
            {
                controller.ResetPose();
                if (reviewLights != null)
                    foreach (Light light in reviewLights)
                        if (light != null) light.enabled = false;
                if (floorRenderer != null) floorRenderer.enabled = false;
                RenderSettings.ambientLight = Color.black;
            }
        }

        private void CaptureFrame(int index)
        {
            RenderTexture target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
            target.Create();
            RenderTexture previous = RenderTexture.active;
            reviewCamera.targetTexture = target;
            reviewCamera.Render();
            RenderTexture.active = target;
            Texture2D image = new Texture2D(width, height, TextureFormat.RGB24, false, false);
            image.ReadPixels(new Rect(0f, 0f, width, height), 0, 0);
            image.Apply(false, false);
            File.WriteAllBytes(Path.Combine(outputDirectory, $"frame-{index:D5}.png"), image.EncodeToPNG());
            Destroy(image);
            reviewCamera.targetTexture = null;
            RenderTexture.active = previous;
            target.Release();
            Destroy(target);
        }

        private void Finish()
        {
            controller.ResetPose();
            bool finalClosedPoseMatch = closedUpperPosition == controller.MovingUpper.localPosition
                && closedRotorRotation == controller.RearRotor.localRotation;
            string report = "{\n"
                + "  \"schemaVersion\": 1,\n"
                + "  \"engine\": \"Unity 6000.5.6f1 PlayMode\",\n"
                + "  \"frameRate\": 30,\n"
                + $"  \"frameCount\": {frameCount},\n"
                + "  \"captureHarnessOnly\": true,\n"
                + "  \"productionAutomaticMotion\": false,\n"
                + "  \"productionUpdateLoop\": false,\n"
                + "  \"directPoseCallsOnly\": true,\n"
                + $"  \"initialAndFinalClosedPoseMatch\": {finalClosedPoseMatch.ToString().ToLowerInvariant()},\n"
                + "  \"states\": [\"closed-idle\", \"straight-slide\", \"open-hold\", \"independent-rear-rotation\", \"rotated-hold\", \"dark-material\"]\n"
                + "}\n";
            File.WriteAllText(Path.Combine(outputDirectory, "runtime-capture-report.json"), report);
            Time.captureFramerate = 0;
            RenderSettings.ambientLight = ambientColor;
#if UNITY_EDITOR
            UnityEditor.EditorApplication.Exit(finalClosedPoseMatch ? 0 : 2);
#endif
        }
    }
}
