#if UNITY_EDITOR
using System;
using System.Globalization;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.EDC.Candidates.ModelHhax
{
    /// <summary>
    /// Editor-only recorder hosted transiently by the real shipping scene.
    /// Existing product roots are restored before exit, while the real Studio
    /// root stays active. Idle/hold segments issue no pose writes and measure drift.
    /// </summary>
    public sealed class ModelHhaxShippingRuntimeEvidenceCapture : MonoBehaviour
    {
        [SerializeField] private GameObject[] existingShippingRoots;
        [SerializeField] private bool[] existingShippingRootStates;
        [SerializeField] private GameObject candidate;
        [SerializeField] private GameObject presentation;
        [SerializeField] private ModelHhaxDirectPoseController controller;
        [SerializeField] private Camera reviewCamera;
        [SerializeField] private Light[] reviewLights;
        [SerializeField] private Renderer floorRenderer;
        [SerializeField] private string outputDirectory;

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
            GameObject[] shippingRoots,
            bool[] shippingRootStates,
            GameObject shippingCandidate,
            GameObject shippingPresentation,
            ModelHhaxDirectPoseController directController,
            Camera camera,
            Light[] lights,
            Renderer floor,
            string output)
        {
            existingShippingRoots = shippingRoots ?? throw new ArgumentNullException(nameof(shippingRoots));
            existingShippingRootStates = shippingRootStates
                ?? throw new ArgumentNullException(nameof(shippingRootStates));
            if (existingShippingRoots.Length != existingShippingRootStates.Length)
                throw new ArgumentException("Shipping root/state arrays must have the same length.");
            candidate = shippingCandidate;
            presentation = shippingPresentation;
            controller = directController;
            reviewCamera = camera;
            reviewLights = lights;
            floorRenderer = floor;
            outputDirectory = output;
        }

        private void Start()
        {
            if (existingShippingRoots == null || existingShippingRootStates == null
                || existingShippingRoots.Length != existingShippingRootStates.Length
                || candidate == null || presentation == null || controller == null
                || reviewCamera == null || string.IsNullOrWhiteSpace(outputDirectory))
                throw new InvalidOperationException("model-hhax shipping runtime capture is not configured.");
            Directory.CreateDirectory(outputDirectory);
            SetExistingShippingRootsActive(false);
            candidate.SetActive(true);
            presentation.SetActive(true);
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
            ApplyPose(frame);
            CaptureFrame(frame);
            frame += 1;
            if (frame >= 210) Finish();
        }

        private void ApplyPose(int index)
        {
            if (index < 45)
            {
                MeasureZeroWriteDrift(closedUpperPosition, closedRotorRotation);
            }
            else if (index < 90)
            {
                controller.SetTravelMm(Mathf.Lerp(0f,
                    ModelHhaxDirectPoseController.MaximumTravelMm, (index - 45) / 44f));
                controller.SetRotorAngleDegrees(0f);
            }
            else if (index < 120)
            {
                if (index == 90) SnapshotHoldPose();
                MeasureZeroWriteDrift(holdUpperPosition, holdRotorRotation);
            }
            else if (index < 160)
            {
                controller.SetTravelMm(ModelHhaxDirectPoseController.MaximumTravelMm);
                controller.SetRotorAngleDegrees(Mathf.Lerp(0f, 180f, (index - 120) / 39f));
            }
            else if (index < 180)
            {
                if (index == 160) SnapshotHoldPose();
                MeasureZeroWriteDrift(holdUpperPosition, holdRotorRotation);
            }
            else
            {
                if (index == 180)
                {
                    controller.ResetPose();
                    SetLights(false);
                    if (floorRenderer != null) floorRenderer.enabled = false;
                    RenderSettings.ambientLight = Color.black;
                    ModelHhaxArtworkEmission.Set(candidate, 3.6f);
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
            const int width = 900;
            const int height = 900;
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
                + "  \"engine\": \"Unity 6000.5.6f1 PlayMode in MeshyEDC.unity\",\n"
                + "  \"frameRate\": 30,\n"
                + "  \"frameCount\": 210,\n"
                + "  \"realShippingStudioActive\": true,\n"
                + "  \"savedExistingRootStatesRestored\": true,\n"
                + "  \"savedCandidateDefaultActive\": false,\n"
                + "  \"captureHarnessOnly\": true,\n"
                + "  \"productionAutomaticMotion\": false,\n"
                + "  \"directPoseCallsOnly\": true,\n"
                + $"  \"zeroWriteSampleCount\": {zeroWriteSampleCount},\n"
                + $"  \"maximumPositionDriftMeters\": {F(maximumPositionDriftMeters)},\n"
                + $"  \"maximumRotationDriftDegrees\": {F(maximumRotationDriftDegrees)},\n"
                + $"  \"zeroWriteDriftPass\": {B(zeroWriteDriftPass)},\n"
                + $"  \"initialAndFinalClosedPoseMatch\": {B(finalClosedPoseMatch)},\n"
                + "  \"phoneBuildInstallPush\": \"not-started\"\n"
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
            ModelHhaxArtworkEmission.Clear(candidate);
            RestoreExistingShippingRootStates();
            candidate.SetActive(false);
            presentation.SetActive(false);
            Time.captureFramerate = 0;
            RenderSettings.ambientLight = ambientColor;
            if (reviewLights != null)
                for (int index = 0; index < reviewLights.Length; index++)
                    if (reviewLights[index] != null)
                        reviewLights[index].enabled = index < lightStates.Length && lightStates[index];
            if (floorRenderer != null) floorRenderer.enabled = floorState;
        }

        private void SetExistingShippingRootsActive(bool active)
        {
            foreach (GameObject root in existingShippingRoots)
                if (root != null) root.SetActive(active);
        }

        private void RestoreExistingShippingRootStates()
        {
            for (int index = 0; index < existingShippingRoots.Length; index++)
                if (existingShippingRoots[index] != null)
                    existingShippingRoots[index].SetActive(existingShippingRootStates[index]);
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
