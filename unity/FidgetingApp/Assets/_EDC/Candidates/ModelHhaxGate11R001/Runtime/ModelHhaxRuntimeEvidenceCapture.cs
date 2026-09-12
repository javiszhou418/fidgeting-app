#if UNITY_EDITOR
using System;
using System.Globalization;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.EDC.Candidates.ModelHhax
{
    /// <summary>
    /// Editor-only PlayMode recorder. It applies explicit commands during the
    /// transition segments and performs zero writes during every idle/hold
    /// segment so any pose drift is measurable rather than being overwritten.
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
        private Vector3 holdUpperPosition;
        private Quaternion holdRotorRotation;
        private Color ambientColor;
        private bool[] lightStates;
        private bool floorState;
        private float maximumPositionDriftMeters;
        private float maximumRotationDriftDegrees;
        private int zeroWriteSampleCount;
        private bool started;
        private bool finished;
        private bool restored;

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
            if (controller == null || reviewCamera == null
                || string.IsNullOrWhiteSpace(outputDirectory))
                throw new InvalidOperationException("model-hhax runtime capture is not configured.");
            Directory.CreateDirectory(outputDirectory);
            controller.ResetPose();
            closedUpperPosition = controller.MovingUpper.localPosition;
            closedRotorRotation = controller.RearRotor.localRotation;
            ambientColor = RenderSettings.ambientLight;
            lightStates = reviewLights == null
                ? Array.Empty<bool>() : Array.ConvertAll(reviewLights, item => item != null && item.enabled);
            floorState = floorRenderer != null && floorRenderer.enabled;
            Time.captureFramerate = 30;
            started = true;
        }

        private void LateUpdate()
        {
            if (finished) return;
            ApplyEvidencePose(frame);
            CaptureFrame(frame);
            frame += 1;
            if (frame >= frameCount) Finish();
        }

        private void ApplyEvidencePose(int index)
        {
            if (index < 30)
            {
                MeasureZeroWriteDrift(closedUpperPosition, closedRotorRotation);
            }
            else if (index < 70)
            {
                controller.SetTravelMm(Mathf.Lerp(0f,
                    ModelHhaxDirectPoseController.MaximumTravelMm, (index - 30) / 39f));
                controller.SetRotorAngleDegrees(0f);
            }
            else if (index < 100)
            {
                if (index == 70) SnapshotHoldPose();
                MeasureZeroWriteDrift(holdUpperPosition, holdRotorRotation);
            }
            else if (index < 130)
            {
                controller.SetTravelMm(ModelHhaxDirectPoseController.MaximumTravelMm);
                controller.SetRotorAngleDegrees(Mathf.Lerp(0f, 135f, (index - 100) / 29f));
            }
            else if (index < 150)
            {
                if (index == 130) SnapshotHoldPose();
                MeasureZeroWriteDrift(holdUpperPosition, holdRotorRotation);
            }
            else
            {
                if (index == 150)
                {
                    controller.ResetPose();
                    SetLights(false);
                    if (floorRenderer != null) floorRenderer.enabled = false;
                    RenderSettings.ambientLight = Color.black;
                    ModelHhaxArtworkEmission.Set(controller.gameObject, 3.6f);
                }
                MeasureZeroWriteDrift(closedUpperPosition, closedRotorRotation);
            }
        }

        private void SnapshotHoldPose()
        {
            holdUpperPosition = controller.MovingUpper.localPosition;
            holdRotorRotation = controller.RearRotor.localRotation;
        }

        private void MeasureZeroWriteDrift(Vector3 expectedPosition, Quaternion expectedRotation)
        {
            maximumPositionDriftMeters = Mathf.Max(maximumPositionDriftMeters,
                Vector3.Distance(expectedPosition, controller.MovingUpper.localPosition));
            maximumRotationDriftDegrees = Mathf.Max(maximumRotationDriftDegrees,
                Quaternion.Angle(expectedRotation, controller.RearRotor.localRotation));
            zeroWriteSampleCount += 1;
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
            finished = true;
            bool finalClosedPoseMatch = Vector3.Distance(closedUpperPosition,
                    controller.MovingUpper.localPosition) <= 0.0000001f
                && Quaternion.Angle(closedRotorRotation,
                    controller.RearRotor.localRotation) <= 0.001f;
            bool zeroWriteDriftPass = maximumPositionDriftMeters <= 0.0000001f
                && maximumRotationDriftDegrees <= 0.001f;
            string report = "{\n"
                + "  \"schemaVersion\": 1,\n"
                + "  \"engine\": \"Unity 6000.5.6f1 PlayMode\",\n"
                + "  \"frameRate\": 30,\n"
                + $"  \"frameCount\": {frameCount},\n"
                + "  \"captureHarnessOnly\": true,\n"
                + "  \"productionAutomaticMotion\": false,\n"
                + "  \"productionUpdateLoop\": false,\n"
                + "  \"directPoseCallsOnly\": true,\n"
                + $"  \"zeroWriteSampleCount\": {zeroWriteSampleCount},\n"
                + $"  \"maximumPositionDriftMeters\": {F(maximumPositionDriftMeters)},\n"
                + $"  \"maximumRotationDriftDegrees\": {F(maximumRotationDriftDegrees)},\n"
                + $"  \"zeroWriteDriftPass\": {B(zeroWriteDriftPass)},\n"
                + $"  \"initialAndFinalClosedPoseMatch\": {B(finalClosedPoseMatch)},\n"
                + "  \"states\": [\"closed-idle-zero-write\", \"straight-slide\", \"open-hold-zero-write\", \"independent-rear-rotation\", \"rotated-hold-zero-write\", \"dark-closed-zero-write\"]\n"
                + "}\n";
            File.WriteAllText(Path.Combine(outputDirectory, "runtime-capture-report.json"), report);
            RestoreCaptureState();
            EditorApplication.Exit(finalClosedPoseMatch && zeroWriteDriftPass ? 0 : 2);
        }

        private void OnDisable()
        {
            if (started && !restored) RestoreCaptureState();
        }

        private void RestoreCaptureState()
        {
            if (restored) return;
            restored = true;
            controller.ResetPose();
            ModelHhaxArtworkEmission.Clear(controller.gameObject);
            Time.captureFramerate = 0;
            RenderSettings.ambientLight = ambientColor;
            if (reviewLights != null)
                for (int index = 0; index < reviewLights.Length; index++)
                    if (reviewLights[index] != null)
                        reviewLights[index].enabled = index < lightStates.Length && lightStates[index];
            if (floorRenderer != null) floorRenderer.enabled = floorState;
        }

        private void SetLights(bool enabled)
        {
            if (reviewLights == null) return;
            foreach (Light light in reviewLights)
                if (light != null) light.enabled = enabled;
        }

        private static string F(float value) =>
            value.ToString("R", CultureInfo.InvariantCulture);

        private static string B(bool value) => value.ToString().ToLowerInvariant();
    }
}
#endif
