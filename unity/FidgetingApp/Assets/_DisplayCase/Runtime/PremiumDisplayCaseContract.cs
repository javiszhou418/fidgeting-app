using System;
using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    public static class PremiumDisplayCaseCameraRules
    {
        public const float ReferenceAspect = 1200f / 1600f;
        public const float ReferenceVerticalFieldOfView = 29f;
        public const float PresentationNearClipPlane = 0.01f;
        public const float PresentationFarClipPlane = 10f;
        public const float PositionToleranceMeters = 0.001f;
        public const float RotationToleranceDegrees = 0.10f;
        public const float FieldOfViewToleranceDegrees = 0.05f;
        public const float ProjectionCenterTolerance = 0.001f;
        public const float MinimumCaseViewportSpan = 0.12f;
        public const float MaximumCaseViewportOverflow = 0.08f;
        public const float MaximumCaseViewportCenterOffset = 0.18f;
        public static readonly Vector3 FrontCameraPosition =
            new Vector3(0f, 0.006f, -0.72f);
        public static readonly Vector3 FrontLookAt =
            new Vector3(0f, 0.006f, 0.008f);

        public static Quaternion FrontCameraRotation => Quaternion.LookRotation(
            FrontLookAt - FrontCameraPosition,
            Vector3.up);

        public static float ResolveVerticalFieldOfView(float targetAspect)
        {
            float safeAspect = Mathf.Max(0.1f, targetAspect);
            float horizontalFieldOfView = Camera.VerticalToHorizontalFieldOfView(
                ReferenceVerticalFieldOfView,
                ReferenceAspect);
            return Camera.HorizontalToVerticalFieldOfView(
                horizontalFieldOfView,
                safeAspect);
        }

        public static void ApplyFrontPresentation(Camera camera)
        {
            if (camera == null)
            {
                return;
            }

            camera.transform.SetPositionAndRotation(
                FrontCameraPosition,
                FrontCameraRotation);
            camera.orthographic = false;
            camera.usePhysicalProperties = false;
            camera.nearClipPlane = PresentationNearClipPlane;
            camera.farClipPlane = PresentationFarClipPlane;
            camera.lensShift = Vector2.zero;
            camera.fieldOfView = ResolveVerticalFieldOfView(camera.aspect);
            camera.ResetProjectionMatrix();
            camera.nonJitteredProjectionMatrix = camera.projectionMatrix;
        }

        public static bool TryValidateFrontPresentation(
            Camera camera,
            Transform displayCaseRoot,
            out string failureReason)
        {
            if (camera == null || !camera.isActiveAndEnabled)
            {
                failureReason = "display-camera-inactive";
                return false;
            }
            if (camera.orthographic)
            {
                failureReason = "display-camera-orthographic";
                return false;
            }
            if (camera.usePhysicalProperties)
            {
                failureReason = "display-camera-physical";
                return false;
            }
            if (Vector3.Distance(camera.transform.position, FrontCameraPosition)
                > PositionToleranceMeters
                || Quaternion.Angle(camera.transform.rotation, FrontCameraRotation)
                    > RotationToleranceDegrees)
            {
                failureReason = "display-camera-pose-overwritten";
                return false;
            }

            float expectedFieldOfView = ResolveVerticalFieldOfView(camera.aspect);
            if (Mathf.Abs(camera.fieldOfView - expectedFieldOfView)
                > FieldOfViewToleranceDegrees)
            {
                failureReason = "display-camera-fov-overwritten";
                return false;
            }
            if (camera.lensShift.sqrMagnitude
                > ProjectionCenterTolerance * ProjectionCenterTolerance
                || Mathf.Abs(camera.projectionMatrix.m02)
                    > ProjectionCenterTolerance
                || Mathf.Abs(camera.projectionMatrix.m12)
                    > ProjectionCenterTolerance)
            {
                failureReason = "display-camera-projection-offset";
                return false;
            }

            if (!TryMeasureCaseViewport(
                    camera,
                    displayCaseRoot,
                    out Rect viewport,
                    out float nearestDepth))
            {
                failureReason = "display-case-viewport-missing";
                return false;
            }
            if (nearestDepth <= camera.nearClipPlane)
            {
                failureReason = "display-case-behind-camera";
                return false;
            }
            if (viewport.width < MinimumCaseViewportSpan
                || viewport.height < MinimumCaseViewportSpan)
            {
                failureReason = "display-case-viewport-edge-on";
                return false;
            }
            if (viewport.xMin < -MaximumCaseViewportOverflow
                || viewport.xMax > 1f + MaximumCaseViewportOverflow
                || viewport.yMin < -MaximumCaseViewportOverflow
                || viewport.yMax > 1f + MaximumCaseViewportOverflow)
            {
                failureReason = "display-case-viewport-clipped";
                return false;
            }
            if (Mathf.Abs(viewport.center.x - 0.5f)
                    > MaximumCaseViewportCenterOffset
                || Mathf.Abs(viewport.center.y - 0.5f)
                    > MaximumCaseViewportCenterOffset)
            {
                failureReason = "display-case-viewport-off-center";
                return false;
            }

            failureReason = string.Empty;
            return true;
        }

        public static bool TryMeasureCaseViewport(
            Camera camera,
            Transform displayCaseRoot,
            out Rect viewport,
            out float nearestDepth)
        {
            viewport = default;
            nearestDepth = float.PositiveInfinity;
            if (camera == null || displayCaseRoot == null)
            {
                return false;
            }

            Renderer[] renderers = displayCaseRoot.GetComponentsInChildren<Renderer>(
                false);
            Bounds bounds = default;
            bool hasBounds = false;
            for (int index = 0; index < renderers.Length; index++)
            {
                Renderer renderer = renderers[index];
                if (renderer == null
                    || !renderer.enabled
                    || !renderer.gameObject.activeInHierarchy
                    || !IsFinite(renderer.bounds))
                {
                    continue;
                }

                if (!hasBounds)
                {
                    bounds = renderer.bounds;
                    hasBounds = true;
                }
                else
                {
                    bounds.Encapsulate(renderer.bounds);
                }
            }
            if (!hasBounds)
            {
                return false;
            }

            float minimumX = float.PositiveInfinity;
            float maximumX = float.NegativeInfinity;
            float minimumY = float.PositiveInfinity;
            float maximumY = float.NegativeInfinity;
            Vector3 extents = bounds.extents;
            for (int x = -1; x <= 1; x += 2)
            {
                for (int y = -1; y <= 1; y += 2)
                {
                    for (int z = -1; z <= 1; z += 2)
                    {
                        Vector3 corner = bounds.center + new Vector3(
                            extents.x * x,
                            extents.y * y,
                            extents.z * z);
                        Vector3 projected = camera.WorldToViewportPoint(corner);
                        if (!IsFinite(projected))
                        {
                            return false;
                        }
                        minimumX = Mathf.Min(minimumX, projected.x);
                        maximumX = Mathf.Max(maximumX, projected.x);
                        minimumY = Mathf.Min(minimumY, projected.y);
                        maximumY = Mathf.Max(maximumY, projected.y);
                        nearestDepth = Mathf.Min(nearestDepth, projected.z);
                    }
                }
            }

            viewport = Rect.MinMaxRect(
                minimumX,
                minimumY,
                maximumX,
                maximumY);
            return IsFinite(viewport.xMin)
                && IsFinite(viewport.yMin)
                && IsFinite(viewport.xMax)
                && IsFinite(viewport.yMax)
                && IsFinite(nearestDepth);
        }

        private static bool IsFinite(Bounds bounds)
        {
            return IsFinite(bounds.center) && IsFinite(bounds.extents);
        }

        private static bool IsFinite(Vector3 value)
        {
            return IsFinite(value.x) && IsFinite(value.y) && IsFinite(value.z);
        }

        private static bool IsFinite(float value)
        {
            return !float.IsNaN(value) && !float.IsInfinity(value);
        }
    }

    public enum PremiumDisplayCaseCapsulePreset
    {
        CircularCompact = 0,
        CircularStandard = 1,
        CircularDeep = 2,
        RoundedSquareStandard = 3,
        RoundedSquareDeep = 4,
        CircularWide = 5,
        CollectorSlabLarge = 6
    }

    public enum PremiumDisplayCaseCapsuleShape
    {
        Circular = 0,
        RoundedSquare = 1
    }

    [Serializable]
    public readonly struct PremiumDisplayCaseCapsuleDimensions
    {
        public PremiumDisplayCaseCapsuleDimensions(
            PremiumDisplayCaseCapsuleShape shape,
            float diameter,
            float depth,
            float cornerRadius)
            : this(shape, diameter, diameter, depth, cornerRadius)
        {
        }

        /// <summary>
        /// Width and height remain independent for non-shipping preview/gacha
        /// callers. Shipping product profiles all resolve the same approved
        /// magnetic-slide dimensions; prize fitting remains uniform.
        /// </summary>
        public PremiumDisplayCaseCapsuleDimensions(
            PremiumDisplayCaseCapsuleShape shape,
            float width,
            float height,
            float depth,
            float cornerRadius,
            float contentPaddingFraction = PremiumDisplayCaseLayout.ContentPaddingFraction)
        {
            Shape = shape;
            Width = Mathf.Clamp(width, 0.060f, 0.200f);
            Height = Mathf.Clamp(height, 0.060f, 0.220f);
            Depth = Mathf.Clamp(depth, 0.012f, 0.080f);
            CornerRadius = Mathf.Clamp(
                cornerRadius,
                0.002f,
                Mathf.Min(Width, Height) * 0.45f);
            ContentPaddingFraction = Mathf.Clamp(contentPaddingFraction, 0f, 0.35f);
        }

        public PremiumDisplayCaseCapsuleShape Shape { get; }
        public float Width { get; }
        public float Height { get; }
        // Kept for the circular preset API and legacy callers. New rectangular
        // profiles must use Width / Height rather than stretching their prize.
        public float Diameter => Mathf.Min(Width, Height);
        public float Depth { get; }
        public float CornerRadius { get; }
        public Vector3 InnerSize => new Vector3(Width, Height, Depth);

        /// <summary>
        /// Baked-in default padding for <see cref="PremiumDisplayCaseLayout.Fit"/>.
        /// Only the Collector Slab's larger, label-bearing footprint overrides
        /// the shared default; every other preset keeps it implicit.
        /// </summary>
        public float ContentPaddingFraction { get; }
    }

    public static class PremiumDisplayCaseCapsulePresets
    {
        public static PremiumDisplayCaseCapsuleDimensions Resolve(
            PremiumDisplayCaseCapsulePreset preset)
        {
            return preset switch
            {
                PremiumDisplayCaseCapsulePreset.CircularCompact =>
                    new PremiumDisplayCaseCapsuleDimensions(
                        PremiumDisplayCaseCapsuleShape.Circular,
                        0.072f,
                        0.020f,
                        0.008f),
                PremiumDisplayCaseCapsulePreset.CircularDeep =>
                    new PremiumDisplayCaseCapsuleDimensions(
                        PremiumDisplayCaseCapsuleShape.Circular,
                        0.084f,
                        0.036f,
                        0.010f),
                PremiumDisplayCaseCapsulePreset.CircularWide =>
                    new PremiumDisplayCaseCapsuleDimensions(
                        PremiumDisplayCaseCapsuleShape.Circular,
                        0.0987f,
                        0.032f,
                        0.012f),
                PremiumDisplayCaseCapsulePreset.RoundedSquareStandard =>
                    new PremiumDisplayCaseCapsuleDimensions(
                        PremiumDisplayCaseCapsuleShape.RoundedSquare,
                        0.084f,
                        0.026f,
                        0.014f),
                PremiumDisplayCaseCapsulePreset.RoundedSquareDeep =>
                    new PremiumDisplayCaseCapsuleDimensions(
                        PremiumDisplayCaseCapsuleShape.RoundedSquare,
                        0.084f,
                        0.038f,
                        0.014f),
                PremiumDisplayCaseCapsulePreset.CollectorSlabLarge =>
                    new PremiumDisplayCaseCapsuleDimensions(
                        PremiumDisplayCaseCapsuleShape.RoundedSquare,
                        0.180f,
                        0.198f,
                        0.048f,
                        0.016f,
                        PremiumDisplayCaseLayout.CollectorSlabContentPaddingFraction),
                _ => new PremiumDisplayCaseCapsuleDimensions(
                    PremiumDisplayCaseCapsuleShape.Circular,
                    0.084f,
                    0.026f,
                    0.010f)
            };
        }
    }

    public enum PremiumDisplayCaseCollectorTier
    {
        Standard = 0,
        Refined = 1,
        Signature = 2,
        Heirloom = 3
    }

    public static class PremiumDisplayCaseCollectorTierRules
    {
        public static PremiumDisplayCaseCollectorTier ResolveForLevel(int level)
        {
            int clamped = Mathf.Clamp(level, 1, 100);
            if (clamped >= 70)
            {
                return PremiumDisplayCaseCollectorTier.Heirloom;
            }
            if (clamped >= 40)
            {
                return PremiumDisplayCaseCollectorTier.Signature;
            }
            return clamped >= 20
                ? PremiumDisplayCaseCollectorTier.Refined
                : PremiumDisplayCaseCollectorTier.Standard;
        }

        public static string DisplayName(PremiumDisplayCaseCollectorTier tier)
        {
            return tier.ToString().ToUpperInvariant();
        }

        public static Color FoilColor(PremiumDisplayCaseCollectorTier tier)
        {
            return tier switch
            {
                PremiumDisplayCaseCollectorTier.Refined =>
                    new Color(0.40f, 0.57f, 0.68f, 1f),
                PremiumDisplayCaseCollectorTier.Signature =>
                    new Color(0.72f, 0.58f, 0.34f, 1f),
                PremiumDisplayCaseCollectorTier.Heirloom =>
                    new Color(0.31f, 0.25f, 0.36f, 1f),
                _ => new Color(0.60f, 0.64f, 0.67f, 1f)
            };
        }
    }

    public readonly struct PremiumDisplayCaseCollectorLabel
    {
        public PremiumDisplayCaseCollectorLabel(
            string productName,
            string edition,
            int level,
            string firstObtainedDate,
            string collectibleId = "",
            PremiumDisplayCaseCollectorTier? tierOverride = null)
        {
            ProductName = string.IsNullOrWhiteSpace(productName)
                ? "COLLECTOR EDITION"
                : productName.Trim().ToUpperInvariant();
            Edition = string.IsNullOrWhiteSpace(edition)
                ? "ORIGINAL FINISH"
                : edition.Trim().ToUpperInvariant();
            Level = Mathf.Clamp(level, 1, 100);
            FirstObtainedDate = firstObtainedDate?.Trim() ?? string.Empty;
            CollectibleId = collectibleId?.Trim().ToUpperInvariant() ?? string.Empty;
            Tier = tierOverride
                ?? PremiumDisplayCaseCollectorTierRules.ResolveForLevel(Level);
        }

        public string ProductName { get; }
        public string Edition { get; }
        public int Level { get; }
        public string FirstObtainedDate { get; }
        public string CollectibleId { get; }
        public PremiumDisplayCaseCollectorTier Tier { get; }
        public string AcquiredDisplay => string.IsNullOrEmpty(FirstObtainedDate)
            ? "ACQUIRED —"
            : "ACQUIRED " + FirstObtainedDate.Replace('-', '.');
        public string TierAndLevelDisplay => string.Concat(
            PremiumDisplayCaseCollectorTierRules.DisplayName(Tier),
            " · LEVEL ",
            Level.ToString());
        public string CollectibleDisplay => string.IsNullOrEmpty(CollectibleId)
            ? string.Empty
            : "COLLECTIBLE " + CollectibleId;
    }

    [Serializable]
    public readonly struct PremiumDisplayCaseContentOptions
    {
        public PremiumDisplayCaseContentOptions(
            bool idleRotationEnabled,
            float idleRotationPeriodSeconds,
            Vector3 initialEulerAngles)
        {
            IdleRotationEnabled = idleRotationEnabled;
            IdleRotationPeriodSeconds = Mathf.Clamp(
                idleRotationPeriodSeconds,
                1.5f,
                30f);
            InitialEulerAngles = initialEulerAngles;
        }

        public bool IdleRotationEnabled { get; }
        public float IdleRotationPeriodSeconds { get; }
        public Vector3 InitialEulerAngles { get; }

        public static PremiumDisplayCaseContentOptions Default =>
            new PremiumDisplayCaseContentOptions(
                true,
                6f,
                new Vector3(90f, -8f, 0f));
    }

    public readonly struct PremiumDisplayCaseFitResult
    {
        public PremiumDisplayCaseFitResult(float scale, Vector3 centerOffset)
        {
            UniformScale = scale;
            CenterOffset = centerOffset;
        }

        public float UniformScale { get; }
        public Vector3 CenterOffset { get; }
    }

    public static class PremiumDisplayCaseLayout
    {
        public const float ContentPaddingFraction = 0.08f;

        /// <summary>
        /// The Collector Slab's larger, label-bearing footprint needs more
        /// breathing room than the shared default; every other capsule
        /// preset keeps <see cref="ContentPaddingFraction"/>.
        /// </summary>
        public const float CollectorSlabContentPaddingFraction = 0.30f;

        public static PremiumDisplayCaseFitResult Fit(
            Bounds contentBounds,
            PremiumDisplayCaseCapsuleDimensions capsule,
            float? paddingFractionOverride = null)
        {
            float padding = Mathf.Clamp(
                paddingFractionOverride ?? capsule.ContentPaddingFraction,
                0f,
                0.35f);
            Vector3 available = capsule.InnerSize * (1f - padding);
            Vector3 size = contentBounds.size;
            float scale = Mathf.Min(
                SafeRatio(available.x, size.x),
                SafeRatio(available.y, size.y),
                SafeRatio(available.z, size.z));
            if (float.IsNaN(scale) || float.IsInfinity(scale))
            {
                scale = 1f;
            }
            scale = Mathf.Clamp(scale, 0.0001f, 1000f);
            return new PremiumDisplayCaseFitResult(
                scale,
                -contentBounds.center * scale);
        }

        private static float SafeRatio(float available, float size)
        {
            return size <= 0.000001f ? float.PositiveInfinity : available / size;
        }
    }

    public readonly struct PremiumDisplayCaseRevealSample
    {
        public PremiumDisplayCaseRevealSample(
            float lidLift,
            float lidOpen,
            float caseRise,
            float caseScale,
            float acrylicVisibility,
            float contentVisibility,
            float lightBoost,
            float sweep,
            bool complete)
        {
            LidLift = lidLift;
            LidOpen = lidOpen;
            CaseRise = caseRise;
            CaseScale = caseScale;
            AcrylicVisibility = acrylicVisibility;
            ContentVisibility = contentVisibility;
            LightBoost = lightBoost;
            Sweep = sweep;
            Complete = complete;
        }

        public float LidLift { get; }
        public float LidOpen { get; }
        public float CaseRise { get; }
        public float CaseScale { get; }
        public float AcrylicVisibility { get; }
        public float ContentVisibility { get; }
        public float LightBoost { get; }
        public float Sweep { get; }
        public bool Complete { get; }
    }

    public static class PremiumDisplayCaseRevealMotion
    {
        public const float DurationSeconds = 2.20f;

        public static PremiumDisplayCaseRevealSample Evaluate(float elapsedSeconds)
        {
            float t = Mathf.Clamp01(elapsedSeconds / DurationSeconds);
            float lidLift = SmoothRange(t, 0.03f, 0.24f);
            float lidOpen = SmoothRange(t, 0.12f, 0.38f);
            float caseRise = EaseOutBack(SmoothRange(t, 0.18f, 0.63f), 0.72f);
            float acrylicVisibility = SmoothRange(t, 0.34f, 0.64f);
            float contentVisibility = EaseOutBack(
                SmoothRange(t, 0.48f, 0.79f),
                0.54f);
            float sweep = SmoothRange(t, 0.42f, 0.86f);
            float lightBoost = Mathf.Sin(
                Mathf.Clamp01(Mathf.InverseLerp(0.40f, 0.92f, t))
                * Mathf.PI);
            float settle = Mathf.Sin(
                Mathf.Clamp01(Mathf.InverseLerp(0.54f, 1f, t))
                * Mathf.PI * 2f)
                * (1f - SmoothRange(t, 0.54f, 1f));
            float caseScale = 0.92f
                + caseRise * 0.08f
                + settle * 0.012f;
            return new PremiumDisplayCaseRevealSample(
                lidLift,
                lidOpen,
                caseRise,
                caseScale,
                acrylicVisibility,
                contentVisibility,
                Mathf.Clamp01(lightBoost),
                sweep,
                t >= 1f);
        }

        private static float SmoothRange(float value, float start, float end)
        {
            float t = Mathf.InverseLerp(start, end, value);
            return t * t * (3f - 2f * t);
        }

        private static float EaseOutBack(float value, float overshoot)
        {
            float x = Mathf.Clamp01(value) - 1f;
            return 1f + (overshoot + 1f) * x * x * x + overshoot * x * x;
        }
    }

    public readonly struct PremiumDisplayCaseLidPose
    {
        public PremiumDisplayCaseLidPose(Vector3 positionOffset, Vector3 eulerOffset)
        {
            PositionOffset = positionOffset;
            EulerOffset = eulerOffset;
        }

        public Vector3 PositionOffset { get; }
        public Vector3 EulerOffset { get; }
    }

    public static class PremiumDisplayCaseLidMotion
    {
        public static PremiumDisplayCaseLidPose Evaluate(
            PremiumDisplayCaseRevealSample sample)
        {
            return new PremiumDisplayCaseLidPose(
                Vector3.up * (0.185f * sample.LidLift)
                    + Vector3.right * (0.310f * sample.LidOpen)
                    + Vector3.back * (0.060f * sample.LidOpen),
                new Vector3(
                    -15f * sample.LidOpen,
                    14f * sample.LidOpen,
                    -10f * sample.LidOpen));
        }
    }

    public readonly struct PremiumDisplayCaseParallaxSample
    {
        public PremiumDisplayCaseParallaxSample(
            Vector3 boxOffset,
            Vector3 acrylicOffset,
            Vector3 interiorOffset,
            Vector3 contentOffset,
            Vector3 eulerAngles)
        {
            BoxOffset = boxOffset;
            AcrylicOffset = acrylicOffset;
            InteriorOffset = interiorOffset;
            ContentOffset = contentOffset;
            EulerAngles = eulerAngles;
        }

        public Vector3 BoxOffset { get; }
        public Vector3 AcrylicOffset { get; }
        public Vector3 InteriorOffset { get; }
        public Vector3 ContentOffset { get; }
        public Vector3 EulerAngles { get; }
    }

    public static class PremiumDisplayCaseParallaxRules
    {
        public const float MaximumTiltDegrees = 4.8f;

        public static PremiumDisplayCaseParallaxSample Evaluate(Vector2 normalizedTilt)
        {
            Vector2 tilt = Vector2.ClampMagnitude(normalizedTilt, 1f);
            return new PremiumDisplayCaseParallaxSample(
                new Vector3(-tilt.x * 0.0012f, -tilt.y * 0.0008f, 0f),
                new Vector3(tilt.x * 0.0007f, tilt.y * 0.0005f, -0.0003f),
                new Vector3(tilt.x * 0.0016f, tilt.y * 0.0011f, 0.0004f),
                new Vector3(tilt.x * 0.0032f, tilt.y * 0.0022f, -0.0007f),
                new Vector3(
                    -tilt.y * MaximumTiltDegrees,
                    tilt.x * MaximumTiltDegrees,
                    -tilt.x * 0.65f));
        }
    }
}
