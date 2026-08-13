using System;
using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    public static class PremiumDisplayCaseCameraRules
    {
        public const float ReferenceAspect = 1200f / 1600f;
        public const float ReferenceVerticalFieldOfView = 29f;
        public static readonly Vector3 FrontCameraPosition =
            new Vector3(0f, 0.006f, -0.72f);
        public static readonly Vector3 FrontLookAt =
            new Vector3(0f, 0.006f, 0.008f);

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
    }

    public enum PremiumDisplayCaseCapsulePreset
    {
        CircularCompact = 0,
        CircularStandard = 1,
        CircularDeep = 2,
        RoundedSquareStandard = 3,
        RoundedSquareDeep = 4
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
        {
            Shape = shape;
            Diameter = Mathf.Clamp(diameter, 0.060f, 0.160f);
            Depth = Mathf.Clamp(depth, 0.012f, 0.080f);
            CornerRadius = Mathf.Clamp(
                cornerRadius,
                0.002f,
                Diameter * 0.45f);
        }

        public PremiumDisplayCaseCapsuleShape Shape { get; }
        public float Diameter { get; }
        public float Depth { get; }
        public float CornerRadius { get; }
        public Vector3 InnerSize => new Vector3(Diameter, Diameter, Depth);
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
                _ => new PremiumDisplayCaseCapsuleDimensions(
                    PremiumDisplayCaseCapsuleShape.Circular,
                    0.084f,
                    0.026f,
                    0.010f)
            };
        }
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
                4f,
                new Vector3(0f, -18f, 0f));
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

        public static PremiumDisplayCaseFitResult Fit(
            Bounds contentBounds,
            PremiumDisplayCaseCapsuleDimensions capsule,
            float paddingFraction = ContentPaddingFraction)
        {
            float padding = Mathf.Clamp(paddingFraction, 0f, 0.35f);
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
