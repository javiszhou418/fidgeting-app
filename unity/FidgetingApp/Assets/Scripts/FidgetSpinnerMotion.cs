using UnityEngine;

namespace ThreeBladeEDC
{
    public enum SpinnerResistanceMode
    {
        Freewheel = 0,
        MagneticDetent = 1
    }

    /// <summary>
    /// Pure motion helpers kept separate from input and Transform state so the
    /// interaction curves can be verified with Edit Mode tests.
    /// </summary>
    public static class FidgetSpinnerMotion
    {
        public const float DefaultTouchResponse = 0.55f;
        public const float DefaultRatchetTouchResponse = 0.48f;
        public const float DefaultSpinResistance = 0.58f;
        public const float DefaultMaximumAngularSpeed = 29.2425f;
        public const float DefaultScreenSpeedForFullSpin = 1179.27f;
        public const float DefaultDragFollowResponse = 34.9435f;
        public const float DefaultDragBrakeResponse = 66.691f;
        public const float DefaultCoastHalfLife = 1.17994f;
        public const float MinimumCoastHalfLife = 0.22f;
        public const float MaximumCoastHalfLife = 12f;
        public const float MinimumDragSamplePixels = 0.75f;
        public const float MinimumReleaseTravelPixels = 28f;
        public const float MinimumReleaseDuration = 0.07f;
        public const float MinimumReleasePixelVelocity = 220f;

        public readonly struct TouchResponseProfile
        {
            public TouchResponseProfile(
                float normalizedResponse,
                float maximumAngularSpeed,
                float screenSpeedForFullSpin,
                float dragFollowResponse,
                float dragBrakeResponse)
            {
                NormalizedResponse = normalizedResponse;
                MaximumAngularSpeed = maximumAngularSpeed;
                ScreenSpeedForFullSpin = screenSpeedForFullSpin;
                DragFollowResponse = dragFollowResponse;
                DragBrakeResponse = dragBrakeResponse;
            }

            public float NormalizedResponse { get; }
            public float MaximumAngularSpeed { get; }
            public float ScreenSpeedForFullSpin { get; }
            public float DragFollowResponse { get; }
            public float DragBrakeResponse { get; }
        }

        /// <summary>
        /// Resolves the single 0...1 product-facing touch response into one
        /// coherent servo profile. Callers must not expose these derived
        /// values as independent controls because they describe one feel.
        /// </summary>
        public static TouchResponseProfile ResolveTouchResponse(float normalizedResponse)
        {
            float response = Mathf.Clamp01(normalizedResponse);
            float shaped = response * response * (3f - 2f * response);
            return new TouchResponseProfile(
                response,
                Mathf.Lerp(12f, 42f, shaped),
                Mathf.Lerp(1800f, 720f, shaped),
                Mathf.Lerp(20f, 46f, shaped),
                Mathf.Lerp(46f, 82f, shaped));
        }

        public static float TouchResponseToSensitivityGain(float normalizedResponse)
        {
            return Mathf.Lerp(
                0.18f,
                1.65f,
                Mathf.Pow(Mathf.Clamp01(normalizedResponse), 0.9f));
        }

        public static float ScaleSwipeVelocity(
            float pixelsPerSecond,
            float speedScale,
            float maxAngularSpeed)
        {
            return Mathf.Clamp(
                pixelsPerSecond * Mathf.Max(0f, speedScale),
                -Mathf.Abs(maxAngularSpeed),
                Mathf.Abs(maxAngularSpeed));
        }

        /// <summary>
        /// Maps a two-dimensional finger sample to an angular velocity. The
        /// angular sample preserves circular/tangential direction while a
        /// dead-zoned screen-speed curve prevents near-hub sample spikes.
        /// </summary>
        public static float MapGestureToAngularSpeed(
            float signedAngleDegrees,
            float screenDistancePixels,
            float deltaTime,
            float sensitivity,
            float maxAngularSpeed,
            float screenSpeedForFullSpin,
            float normalizedPressure = 1f,
            float minimumSampleDistancePixels = MinimumDragSamplePixels)
        {
            float maximum = Mathf.Abs(maxAngularSpeed);
            if (deltaTime <= 0f
                || maximum <= Mathf.Epsilon
                || Mathf.Abs(signedAngleDegrees) <= Mathf.Epsilon
                || Mathf.Abs(screenDistancePixels)
                    < Mathf.Max(0f, minimumSampleDistancePixels))
            {
                return 0f;
            }

            // Ignore pressure here. iPhone touch pressure availability varies,
            // and mixing it into velocity made an identically sized drag feel
            // different across devices. Product "力度" belongs to Haptics.
            _ = normalizedPressure;
            float sampleDeltaTime = Mathf.Max(deltaTime, 1f / 120f);
            float angularMagnitude = Mathf.Abs(signedAngleDegrees)
                * Mathf.Deg2Rad
                / sampleDeltaTime;
            float screenSpeed = Mathf.Abs(screenDistancePixels) / sampleDeltaTime;
            const float minimumMeaningfulScreenSpeed = 24f;
            float speedRatio = Mathf.InverseLerp(
                minimumMeaningfulScreenSpeed,
                Mathf.Max(minimumMeaningfulScreenSpeed + 1f, screenSpeedForFullSpin),
                screenSpeed);
            float screenMagnitude = maximum * Mathf.Pow(speedRatio, 1.15f);

            // Screen speed bounds the angle estimate. This prevents a tiny
            // radius or a short sampling interval from turning one pixel into
            // a maximum-speed spin while retaining genuine circular motion.
            float geometryMagnitude = Mathf.Min(
                angularMagnitude * 1.2f,
                screenMagnitude);
            float mappedMagnitude = Mathf.Lerp(
                geometryMagnitude,
                screenMagnitude,
                0.35f);
            float sensitivityGain = TouchResponseToSensitivityGain(sensitivity);
            float magnitude = Mathf.Clamp(
                mappedMagnitude * sensitivityGain,
                0f,
                maximum);
            return Mathf.Sign(signedAngleDegrees) * magnitude;
        }

        /// <summary>
        /// Position/velocity servo for the active drag. Braking intentionally
        /// has a faster response than acceleration so slowing the finger slows
        /// the model immediately instead of fighting stored inertia.
        /// </summary>
        public static float FollowDragSpeed(
            float currentSpeed,
            float targetSpeed,
            float deltaTime,
            float followResponse,
            float brakeResponse,
            float maximumAngularSpeed)
        {
            if (deltaTime <= 0f)
            {
                return Mathf.Clamp(
                    currentSpeed,
                    -Mathf.Abs(maximumAngularSpeed),
                    Mathf.Abs(maximumAngularSpeed));
            }

            bool braking = Mathf.Abs(targetSpeed) < Mathf.Abs(currentSpeed)
                || (Mathf.Abs(targetSpeed) > Mathf.Epsilon
                    && Mathf.Abs(currentSpeed) > Mathf.Epsilon
                    && Mathf.Sign(targetSpeed) != Mathf.Sign(currentSpeed));
            float response = braking
                ? Mathf.Max(0f, brakeResponse)
                : Mathf.Max(0f, followResponse);
            float blend = response <= Mathf.Epsilon
                ? 1f
                : 1f - Mathf.Exp(-response * deltaTime);
            float followed = Mathf.Lerp(currentSpeed, targetSpeed, blend);
            return Mathf.Clamp(
                followed,
                -Mathf.Abs(maximumAngularSpeed),
                Mathf.Abs(maximumAngularSpeed));
        }

        public static bool QualifiesReleaseFling(
            float recentSignedPixelVelocity,
            float signedTravelPixels,
            float totalTravelPixels,
            float duration)
        {
            float directionalConsistency = Mathf.Abs(signedTravelPixels)
                / Mathf.Max(1f, totalTravelPixels);
            return totalTravelPixels >= MinimumReleaseTravelPixels
                && duration >= MinimumReleaseDuration
                && Mathf.Abs(recentSignedPixelVelocity)
                    >= MinimumReleasePixelVelocity
                && directionalConsistency >= 0.62f;
        }

        /// <summary>
        /// Resolves the velocity at touch-up. A qualified flick replaces the
        /// final drag velocity; it is never added as a second impulse. Short,
        /// noisy or directionally inconsistent gestures retain only a reduced
        /// share of their drag velocity.
        /// </summary>
        public static float ResolveReleaseAngularSpeed(
            float currentDragSpeed,
            float recentSignedPixelVelocity,
            float signedTravelPixels,
            float totalTravelPixels,
            float duration,
            float touchResponse,
            float maximumAngularSpeed,
            float screenSpeedForFullSpin)
        {
            float maximum = Mathf.Abs(maximumAngularSpeed);
            if (!QualifiesReleaseFling(
                    recentSignedPixelVelocity,
                    signedTravelPixels,
                    totalTravelPixels,
                    duration))
            {
                float distanceRetention = Mathf.Clamp01(
                    totalTravelPixels / MinimumReleaseTravelPixels);
                float timeRetention = Mathf.Clamp01(
                    duration / MinimumReleaseDuration);
                float retention = distanceRetention * timeRetention;
                return Mathf.Clamp(
                    currentDragSpeed * retention * retention * retention,
                    -maximum,
                    maximum);
            }

            float averageSignedVelocity = signedTravelPixels
                / Mathf.Max(duration, MinimumReleaseDuration);
            float blendedVelocity = Mathf.Lerp(
                averageSignedVelocity,
                recentSignedPixelVelocity,
                0.72f);
            float speedRatio = Mathf.InverseLerp(
                MinimumReleasePixelVelocity,
                Mathf.Max(MinimumReleasePixelVelocity + 1f, screenSpeedForFullSpin),
                Mathf.Abs(blendedVelocity));
            float magnitude = maximum
                * Mathf.Pow(speedRatio, 1.08f)
                * TouchResponseToSensitivityGain(touchResponse);
            return Mathf.Sign(blendedVelocity)
                * Mathf.Clamp(magnitude, 0f, maximum);
        }

        /// <summary>
        /// Converts the screen-space counter-clockwise tangent sign into the
        /// rotor's physical axis sign. When the camera looks against the spin
        /// axis, positive physical rotation appears clockwise on screen.
        /// </summary>
        public static float AlignScreenTangentToSpinAxis(
            float screenTangentialPixels,
            Vector3 cameraForward,
            Vector3 spinAxisWorld)
        {
            if (cameraForward.sqrMagnitude <= Mathf.Epsilon
                || spinAxisWorld.sqrMagnitude <= Mathf.Epsilon)
            {
                return screenTangentialPixels;
            }

            float viewAlignment = Vector3.Dot(
                cameraForward.normalized,
                spinAxisWorld.normalized);
            return Mathf.Abs(viewAlignment) <= 0.05f
                ? screenTangentialPixels
                : screenTangentialPixels * Mathf.Sign(viewAlignment);
        }

        public static bool ConfirmsDirectionReversal(
            float currentAngularSpeed,
            float requestedAngularSpeed,
            float oppositeTravelPixels,
            float minimumSpeed,
            float confirmationTravelPixels)
        {
            return Mathf.Abs(currentAngularSpeed) >= Mathf.Max(0f, minimumSpeed)
                && Mathf.Abs(requestedAngularSpeed) >= Mathf.Max(0f, minimumSpeed)
                && Mathf.Sign(currentAngularSpeed) != Mathf.Sign(requestedAngularSpeed)
                && oppositeTravelPixels >= Mathf.Max(0f, confirmationTravelPixels);
        }

        public static float EaseOutCubic(float t)
        {
            t = Mathf.Clamp01(t);
            float inverse = 1f - t;
            return 1f - inverse * inverse * inverse;
        }

        /// <summary>
        /// Converts a requested peak overshoot fraction into the coefficient
        /// used by the standard ease-out-back equation.
        /// </summary>
        public static float BackCoefficientForOvershoot(float overshootFraction)
        {
            float target = Mathf.Max(0f, overshootFraction);
            if (target <= Mathf.Epsilon)
            {
                return 0f;
            }

            // For coefficient c, the curve's exact peak overshoot is:
            // 4c^3 / (27(c + 1)^2). Binary search keeps the Inspector value
            // meaningful (0.1 means a 10% peak overshoot).
            float low = 0f;
            float high = 32f;
            for (int i = 0; i < 20; i++)
            {
                float coefficient = (low + high) * 0.5f;
                float numerator = 4f * coefficient * coefficient * coefficient;
                float denominator = 27f * (coefficient + 1f) * (coefficient + 1f);
                float peakOvershoot = numerator / denominator;

                if (peakOvershoot < target)
                {
                    low = coefficient;
                }
                else
                {
                    high = coefficient;
                }
            }

            return (low + high) * 0.5f;
        }

        public static float EaseOutBack(float t, float backCoefficient)
        {
            t = Mathf.Clamp01(t);
            float shifted = t - 1f;
            return 1f
                + (backCoefficient + 1f) * shifted * shifted * shifted
                + backCoefficient * shifted * shifted;
        }

        public static float DecelerateToStop(
            float initialVelocity,
            float elapsed,
            float duration)
        {
            if (duration <= Mathf.Epsilon)
            {
                return 0f;
            }

            float progress = EaseOutCubic(elapsed / duration);
            return Mathf.LerpUnclamped(initialVelocity, 0f, progress);
        }

        /// <summary>
        /// Applies model-independent exponential coast. A half-life is easier
        /// to compare across meshes than Rigidbody angular damping because the
        /// same value always halves speed in the same amount of real time.
        /// </summary>
        public static float ApplyCoastHalfLife(
            float angularVelocity,
            float deltaTime,
            float halfLife)
        {
            if (halfLife <= Mathf.Epsilon || deltaTime <= 0f)
            {
                return 0f;
            }

            return angularVelocity * Mathf.Pow(0.5f, deltaTime / halfLife);
        }

        public static float ResistanceToCoastHalfLife(float normalizedResistance)
        {
            float resistance = Mathf.Clamp01(normalizedResistance);
            return MaximumCoastHalfLife * Mathf.Pow(
                MinimumCoastHalfLife / MaximumCoastHalfLife,
                resistance);
        }

        public static float CoastHalfLifeToResistance(float halfLife)
        {
            float clamped = Mathf.Clamp(
                halfLife,
                MinimumCoastHalfLife,
                MaximumCoastHalfLife);
            return Mathf.Log(MaximumCoastHalfLife / clamped)
                / Mathf.Log(MaximumCoastHalfLife / MinimumCoastHalfLife);
        }

        public static bool BreaksMagneticDetent(
            float requestedAngularVelocity,
            float breakawayVelocity)
        {
            return Mathf.Abs(requestedAngularVelocity)
                >= Mathf.Max(0f, breakawayVelocity);
        }

        public static float NearestDetentDegrees(float angleDegrees, int detentsPerTurn)
        {
            float step = 360f / Mathf.Max(1, detentsPerTurn);
            return Mathf.Round(angleDegrees / step) * step;
        }

        public static int DetentIndex(float unwrappedAngleDegrees, int detentsPerTurn)
        {
            float step = 360f / Mathf.Max(1, detentsPerTurn);
            return Mathf.RoundToInt(unwrappedAngleDegrees / step);
        }
    }
}
