using System;
using System.Collections.Generic;
using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    /// <summary>
    /// Marks a component on the shipping camera that can author its pose or
    /// projection after the coordinator has configured the display-case view.
    /// The display case owns the camera temporarily and suspends every marked
    /// author for the complete presentation lifetime.
    /// </summary>
    public interface IPremiumDisplayCaseCameraStateAuthor
    {
        void SetDisplayCaseCameraControlSuppressed(bool suppressed);
    }

    /// <summary>
    /// Exact camera state restored when the display case closes.  Keeping the
    /// physical-camera fields and custom projection matrices avoids making a
    /// product's library framing depend on which presentation opened last.
    /// </summary>
    public readonly struct PremiumDisplayCaseCameraState
    {
        private PremiumDisplayCaseCameraState(Camera camera)
        {
            Position = camera.transform.position;
            Rotation = camera.transform.rotation;
            Orthographic = camera.orthographic;
            OrthographicSize = camera.orthographicSize;
            FieldOfView = camera.fieldOfView;
            Aspect = camera.aspect;
            NearClipPlane = camera.nearClipPlane;
            FarClipPlane = camera.farClipPlane;
            UsePhysicalProperties = camera.usePhysicalProperties;
            FocalLength = camera.focalLength;
            SensorSize = camera.sensorSize;
            LensShift = camera.lensShift;
            GateFit = camera.gateFit;
            Iso = camera.iso;
            ShutterSpeed = camera.shutterSpeed;
            Aperture = camera.aperture;
            FocusDistance = camera.focusDistance;
            BladeCount = camera.bladeCount;
            Curvature = camera.curvature;
            BarrelClipping = camera.barrelClipping;
            Anamorphism = camera.anamorphism;
            ProjectionMatrix = camera.projectionMatrix;
            NonJitteredProjectionMatrix = camera.nonJitteredProjectionMatrix;
            UseJitteredProjectionMatrixForTransparentRendering =
                camera.useJitteredProjectionMatrixForTransparentRendering;
        }

        public Vector3 Position { get; }
        public Quaternion Rotation { get; }
        public bool Orthographic { get; }
        public float OrthographicSize { get; }
        public float FieldOfView { get; }
        public float Aspect { get; }
        public float NearClipPlane { get; }
        public float FarClipPlane { get; }
        public bool UsePhysicalProperties { get; }
        public float FocalLength { get; }
        public Vector2 SensorSize { get; }
        public Vector2 LensShift { get; }
        public Camera.GateFitMode GateFit { get; }
        public int Iso { get; }
        public float ShutterSpeed { get; }
        public float Aperture { get; }
        public float FocusDistance { get; }
        public int BladeCount { get; }
        public Vector2 Curvature { get; }
        public float BarrelClipping { get; }
        public float Anamorphism { get; }
        public Matrix4x4 ProjectionMatrix { get; }
        public Matrix4x4 NonJitteredProjectionMatrix { get; }
        public bool UseJitteredProjectionMatrixForTransparentRendering { get; }

        public static PremiumDisplayCaseCameraState Capture(Camera camera)
        {
            if (camera == null)
            {
                throw new ArgumentNullException(nameof(camera));
            }

            return new PremiumDisplayCaseCameraState(camera);
        }

        public void Restore(Camera camera)
        {
            if (camera == null)
            {
                return;
            }

            // Configure while non-physical so restoring one representation
            // cannot silently rewrite another through Unity's focal/FOV link.
            camera.usePhysicalProperties = false;
            camera.orthographic = Orthographic;
            camera.orthographicSize = OrthographicSize;
            camera.aspect = Aspect;
            camera.nearClipPlane = NearClipPlane;
            camera.farClipPlane = FarClipPlane;
            camera.sensorSize = SensorSize;
            camera.lensShift = LensShift;
            camera.gateFit = GateFit;
            camera.focalLength = FocalLength;
            camera.iso = Iso;
            camera.shutterSpeed = ShutterSpeed;
            camera.aperture = Aperture;
            camera.focusDistance = FocusDistance;
            camera.bladeCount = BladeCount;
            camera.curvature = Curvature;
            camera.barrelClipping = BarrelClipping;
            camera.anamorphism = Anamorphism;
            camera.usePhysicalProperties = UsePhysicalProperties;
            if (UsePhysicalProperties)
            {
                camera.focalLength = FocalLength;
            }
            else
            {
                camera.fieldOfView = FieldOfView;
            }
            camera.projectionMatrix = ProjectionMatrix;
            camera.nonJitteredProjectionMatrix = NonJitteredProjectionMatrix;
            camera.useJitteredProjectionMatrixForTransparentRendering =
                UseJitteredProjectionMatrixForTransparentRendering;
            camera.transform.SetPositionAndRotation(Position, Rotation);
        }
    }

    /// <summary>
    /// Owns one shipping camera while the display case is visible.  Acquisition
    /// is ordered deliberately: capture first, disable all active authors, then
    /// install the shared front projection.  Restoration enables authors before
    /// restoring the snapshot so OnEnable callbacks cannot corrupt the returned
    /// library pose.
    /// </summary>
    public sealed class PremiumDisplayCaseCameraLease : IDisposable
    {
        private readonly struct AuthorState
        {
            public AuthorState(MonoBehaviour author)
            {
                Author = author;
                Enabled = author != null && author.enabled;
            }

            public MonoBehaviour Author { get; }
            public bool Enabled { get; }
        }

        private readonly Camera camera;
        private readonly PremiumDisplayCaseCameraState savedState;
        private readonly List<AuthorState> authorStates;
        private bool restored;

        private PremiumDisplayCaseCameraLease(Camera targetCamera)
        {
            camera = targetCamera;
            savedState = PremiumDisplayCaseCameraState.Capture(targetCamera);
            authorStates = new List<AuthorState>();

            MonoBehaviour[] behaviours = targetCamera.GetComponents<MonoBehaviour>();
            for (int index = 0; index < behaviours.Length; index++)
            {
                MonoBehaviour behaviour = behaviours[index];
                if (behaviour == null
                    || !(behaviour is IPremiumDisplayCaseCameraStateAuthor))
                {
                    continue;
                }

                var state = new AuthorState(behaviour);
                authorStates.Add(state);
                ((IPremiumDisplayCaseCameraStateAuthor)behaviour)
                    .SetDisplayCaseCameraControlSuppressed(true);
                if (state.Enabled)
                {
                    behaviour.enabled = false;
                }
            }

            PremiumDisplayCaseCameraRules.ApplyFrontPresentation(camera);
        }

        public Camera Camera => camera;
        public PremiumDisplayCaseCameraState SavedState => savedState;
        public int CameraStateAuthorCount => authorStates.Count;

        public static PremiumDisplayCaseCameraLease Acquire(Camera camera)
        {
            return camera == null
                ? null
                : new PremiumDisplayCaseCameraLease(camera);
        }

        public bool IsPresentationStable(
            Transform displayCaseRoot,
            out string failureReason)
        {
            if (restored || camera == null)
            {
                failureReason = "display-camera-lease-missing";
                return false;
            }

            MonoBehaviour[] behaviours = camera.GetComponents<MonoBehaviour>();
            for (int index = 0; index < behaviours.Length; index++)
            {
                MonoBehaviour behaviour = behaviours[index];
                if (behaviour != null
                    && behaviour.enabled
                    && behaviour is IPremiumDisplayCaseCameraStateAuthor)
                {
                    failureReason =
                        $"display-camera-author-active:{behaviour.GetType().Name}";
                    return false;
                }
            }

            return PremiumDisplayCaseCameraRules.TryValidateFrontPresentation(
                camera,
                displayCaseRoot,
                out failureReason);
        }

        public void Restore()
        {
            if (restored)
            {
                return;
            }
            restored = true;

            // Restore enabled states while their writes remain suppressed.
            // Portrait framers legitimately write from OnEnable, so the exact
            // snapshot is installed only after every callback has returned.
            for (int index = 0; index < authorStates.Count; index++)
            {
                AuthorState state = authorStates[index];
                if (state.Author != null)
                {
                    state.Author.enabled = state.Enabled;
                }
            }

            savedState.Restore(camera);
            for (int index = 0; index < authorStates.Count; index++)
            {
                AuthorState state = authorStates[index];
                if (state.Author != null)
                {
                    ((IPremiumDisplayCaseCameraStateAuthor)state.Author)
                        .SetDisplayCaseCameraControlSuppressed(false);
                }
            }
        }

        public void Dispose()
        {
            Restore();
        }
    }
}
