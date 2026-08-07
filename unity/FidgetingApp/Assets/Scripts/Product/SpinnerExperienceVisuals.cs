using System;
using UnityEngine;

namespace FidgetingApp.Product
{
    public static class SpinnerExperienceVisualRules
    {
        public const float SparkThresholdNormalizedSpeed = 0.72f;
        public const float MaximumSparkRate = 72f;

        public static Color ResolveAccent(
            SpinnerComboTier comboTier,
            SpinnerSpinRewardKind rewardKind)
        {
            if (rewardKind != SpinnerSpinRewardKind.None)
            {
                switch (rewardKind)
                {
                    case SpinnerSpinRewardKind.CleanSpin:
                        return new Color(0.28f, 0.88f, 0.78f);
                    case SpinnerSpinRewardKind.PowerSpin:
                        return new Color(1f, 0.62f, 0.18f);
                    case SpinnerSpinRewardKind.SpeedRun:
                        return new Color(0.32f, 0.76f, 1f);
                    case SpinnerSpinRewardKind.Endurance:
                        return new Color(0.70f, 0.52f, 1f);
                    case SpinnerSpinRewardKind.PerfectSpin:
                        return new Color(1f, 0.34f, 0.72f);
                }
            }

            switch (comboTier)
            {
                case SpinnerComboTier.Flow:
                    return new Color(0.20f, 0.92f, 0.78f);
                case SpinnerComboTier.Drive:
                    return new Color(1f, 0.62f, 0.18f);
                case SpinnerComboTier.Overdrive:
                    return new Color(1f, 0.28f, 0.72f);
                default:
                    return Color.black;
            }
        }

        public static Color ResolveDarkBackground(
            SpinnerComboTier comboTier,
            SpinnerSpinRewardKind rewardKind)
        {
            bool rewardActive = rewardKind != SpinnerSpinRewardKind.None;
            if (!rewardActive && comboTier == SpinnerComboTier.None)
            {
                return Color.black;
            }

            Color accent = ResolveAccent(comboTier, rewardKind);
            float strength = rewardActive ? 0.115f : 0.085f + (int)comboTier * 0.012f;
            return new Color(
                accent.r * strength,
                accent.g * strength,
                accent.b * strength,
                1f);
        }

        public static float ResolveSparkRate(float angularSpeedRadians)
        {
            float normalizedSpeed = SpinnerComboRules.NormalizeSpeed(angularSpeedRadians);
            float heat = Mathf.InverseLerp(
                SparkThresholdNormalizedSpeed,
                1f,
                normalizedSpeed);
            return heat * heat * MaximumSparkRate;
        }

        public static float ResolveMoteRate(
            SpinnerComboTier comboTier,
            SpinnerSpinRewardKind rewardKind)
        {
            if (rewardKind != SpinnerSpinRewardKind.None)
            {
                return 22f;
            }

            return comboTier == SpinnerComboTier.None
                ? 0f
                : 5f + (int)comboTier * 5f;
        }
    }

    /// <summary>
    /// Presentation-only feedback. Background color is applied through each
    /// Unity camera's clear color, so rendered spinner materials remain in the
    /// foreground and never receive the combo tint. Particle systems are
    /// persistent, bounded, and driven by real angular speed.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class SpinnerExperienceVisuals : MonoBehaviour
    {
        private const float BackgroundResponse = 7f;
        private const float RewardVisualDuration = 2.4f;
        private const int MoteParticleLimit = 40;
        private const int SparkParticleLimit = 72;

        private Camera[] sceneCameras = Array.Empty<Camera>();
        private Transform rotor;
        private Transform effectRoot;
        private ParticleSystem motes;
        private ParticleSystem sparks;
        private Material particleMaterial;
        private float effectRadius = 0.12f;
        private float rewardVisibleUntil;
        private SpinnerSpinRewardKind visibleRewardKind;

        public void Configure(Camera[] cameras, Transform targetRotor)
        {
            ApplyBackground(Color.black, true);
            StopParticles(true);
            sceneCameras = cameras ?? Array.Empty<Camera>();
            rotor = targetRotor;
            visibleRewardKind = SpinnerSpinRewardKind.None;
            rewardVisibleUntil = 0f;

            if (rotor == null)
            {
                return;
            }

            EnsureParticleSystems();
            effectRadius = ResolveEffectRadius(rotor);
            ConfigureShapeRadius(motes, effectRadius * 0.94f);
            ConfigureShapeRadius(sparks, effectRadius * 0.98f);
        }

        public void UpdateFrame(
            SpinnerComboSnapshot combo,
            float angularSpeedRadians,
            Vector3 spinAxisWorld,
            float unscaledTime,
            bool suppressed)
        {
            bool rewardActive = visibleRewardKind != SpinnerSpinRewardKind.None
                && unscaledTime < rewardVisibleUntil;
            if (!rewardActive)
            {
                visibleRewardKind = SpinnerSpinRewardKind.None;
            }

            SpinnerComboTier comboTier = suppressed
                ? SpinnerComboTier.None
                : combo.Tier;
            SpinnerSpinRewardKind rewardKind = suppressed
                ? SpinnerSpinRewardKind.None
                : visibleRewardKind;
            Color background = SpinnerExperienceVisualRules.ResolveDarkBackground(
                comboTier,
                rewardKind);
            ApplyBackground(background, false);

            if (suppressed || rotor == null)
            {
                StopParticles(false);
                return;
            }

            EnsureParticleSystems();
            UpdateEffectPose(spinAxisWorld);
            Color accent = SpinnerExperienceVisualRules.ResolveAccent(
                comboTier,
                rewardKind);
            float moteRate = SpinnerExperienceVisualRules.ResolveMoteRate(
                comboTier,
                rewardKind);
            SetParticleColor(motes, accent, Color.Lerp(accent, Color.white, 0.46f));
            SetEmissionRate(motes, moteRate);

            float sparkRate = SpinnerExperienceVisualRules.ResolveSparkRate(
                angularSpeedRadians);
            SetParticleColor(
                sparks,
                new Color(1f, 0.86f, 0.24f),
                new Color(1f, 0.20f, 0.02f));
            SetEmissionRate(sparks, sparkRate);
        }

        public void ShowReward(SpinnerSpinRewardSnapshot reward, float unscaledTime)
        {
            if (!reward.IsReward)
            {
                return;
            }

            visibleRewardKind = reward.Kind;
            rewardVisibleUntil = unscaledTime + RewardVisualDuration;
        }

        public void ResetVisuals()
        {
            visibleRewardKind = SpinnerSpinRewardKind.None;
            rewardVisibleUntil = 0f;
            ApplyBackground(Color.black, true);
            StopParticles(true);
        }

        private void EnsureParticleSystems()
        {
            if (effectRoot == null)
            {
                var root = new GameObject("ExperienceFeedbackParticles");
                effectRoot = root.transform;
                effectRoot.SetParent(transform, false);
            }

            if (particleMaterial == null)
            {
                Shader shader = Shader.Find("Universal Render Pipeline/Particles/Unlit")
                    ?? Shader.Find("Particles/Standard Unlit")
                    ?? Shader.Find("Sprites/Default");
                if (shader != null)
                {
                    particleMaterial = new Material(shader)
                    {
                        name = "ExperienceFeedbackParticles_Runtime"
                    };
                }
            }

            if (motes == null)
            {
                motes = CreateParticleSystem(
                    "ComboLightMotes",
                    MoteParticleLimit,
                    0.72f,
                    0.022f,
                    0.14f,
                    false);
            }

            if (sparks == null)
            {
                sparks = CreateParticleSystem(
                    "HighSpeedFireSparks",
                    SparkParticleLimit,
                    0.34f,
                    0.014f,
                    1.9f,
                    true);
            }
        }

        private ParticleSystem CreateParticleSystem(
            string objectName,
            int maximumParticles,
            float lifetime,
            float relativeSize,
            float relativeSpeed,
            bool stretched)
        {
            var particleObject = new GameObject(objectName);
            particleObject.transform.SetParent(effectRoot, false);
            ParticleSystem system = particleObject.AddComponent<ParticleSystem>();

            ParticleSystem.MainModule main = system.main;
            main.playOnAwake = false;
            main.loop = true;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.maxParticles = maximumParticles;
            main.startLifetime = lifetime;
            main.startSize = Mathf.Max(0.0015f, effectRadius * relativeSize);
            main.startSpeed = Mathf.Max(0.01f, effectRadius * relativeSpeed);

            ParticleSystem.EmissionModule emission = system.emission;
            emission.enabled = true;
            emission.rateOverTime = 0f;

            ParticleSystem.ShapeModule shape = system.shape;
            shape.enabled = true;
            shape.shapeType = ParticleSystemShapeType.Circle;
            shape.radius = effectRadius;
            shape.radiusThickness = stretched ? 0.08f : 0.24f;

            ParticleSystem.ColorOverLifetimeModule colorOverLifetime =
                system.colorOverLifetime;
            colorOverLifetime.enabled = true;
            var fade = new Gradient();
            fade.SetKeys(
                new[]
                {
                    new GradientColorKey(Color.white, 0f),
                    new GradientColorKey(Color.white, 1f)
                },
                new[]
                {
                    new GradientAlphaKey(0f, 0f),
                    new GradientAlphaKey(1f, 0.12f),
                    new GradientAlphaKey(0.72f, 0.56f),
                    new GradientAlphaKey(0f, 1f)
                });
            colorOverLifetime.color = fade;

            ParticleSystemRenderer particleRenderer =
                particleObject.GetComponent<ParticleSystemRenderer>();
            particleRenderer.sharedMaterial = particleMaterial;
            particleRenderer.sortingOrder = 2;
            if (stretched)
            {
                particleRenderer.renderMode = ParticleSystemRenderMode.Stretch;
                particleRenderer.velocityScale = 0.16f;
                particleRenderer.lengthScale = 1.8f;
            }
            else
            {
                particleRenderer.renderMode = ParticleSystemRenderMode.Billboard;
            }

            return system;
        }

        private void UpdateEffectPose(Vector3 spinAxisWorld)
        {
            if (effectRoot == null || rotor == null)
            {
                return;
            }

            Vector3 axis = spinAxisWorld.sqrMagnitude > Mathf.Epsilon
                ? spinAxisWorld.normalized
                : Vector3.up;
            effectRoot.SetPositionAndRotation(
                rotor.position,
                Quaternion.FromToRotation(Vector3.forward, axis));
        }

        private void ApplyBackground(Color target, bool immediate)
        {
            float blend = immediate
                ? 1f
                : 1f - Mathf.Exp(-BackgroundResponse * Mathf.Max(0f, Time.unscaledDeltaTime));
            for (int index = 0; index < sceneCameras.Length; index++)
            {
                Camera camera = sceneCameras[index];
                if (camera == null)
                {
                    continue;
                }

                camera.clearFlags = CameraClearFlags.SolidColor;
                camera.backgroundColor = immediate
                    ? target
                    : Color.Lerp(camera.backgroundColor, target, blend);
                camera.GetComponent<SpinnerEnvironmentPresenter>()?.SetExperienceTint(
                    camera.backgroundColor);
            }
        }

        private static float ResolveEffectRadius(Transform targetRotor)
        {
            Renderer[] renderers = targetRotor.GetComponentsInChildren<Renderer>(true);
            bool hasBounds = false;
            Bounds combined = default;
            for (int index = 0; index < renderers.Length; index++)
            {
                Renderer renderer = renderers[index];
                if (renderer == null || renderer is ParticleSystemRenderer)
                {
                    continue;
                }

                if (!hasBounds)
                {
                    combined = renderer.bounds;
                    hasBounds = true;
                }
                else
                {
                    combined.Encapsulate(renderer.bounds);
                }
            }

            if (!hasBounds)
            {
                return 0.12f;
            }

            return Mathf.Max(0.05f, Mathf.Max(combined.extents.x, combined.extents.z) * 1.05f);
        }

        private static void ConfigureShapeRadius(ParticleSystem system, float radius)
        {
            if (system == null)
            {
                return;
            }

            ParticleSystem.ShapeModule shape = system.shape;
            shape.radius = radius;
        }

        private static void SetParticleColor(
            ParticleSystem system,
            Color minimum,
            Color maximum)
        {
            if (system == null)
            {
                return;
            }

            ParticleSystem.MainModule main = system.main;
            main.startColor = new ParticleSystem.MinMaxGradient(minimum, maximum);
        }

        private static void SetEmissionRate(ParticleSystem system, float rate)
        {
            if (system == null)
            {
                return;
            }

            ParticleSystem.EmissionModule emission = system.emission;
            emission.rateOverTime = Mathf.Max(0f, rate);
            if (rate > 0.01f)
            {
                if (!system.isPlaying)
                {
                    system.Play(true);
                }
            }
            else if (system.isPlaying)
            {
                system.Stop(true, ParticleSystemStopBehavior.StopEmitting);
            }
        }

        private void StopParticles(bool clear)
        {
            ParticleSystemStopBehavior behavior = clear
                ? ParticleSystemStopBehavior.StopEmittingAndClear
                : ParticleSystemStopBehavior.StopEmitting;
            if (motes != null)
            {
                motes.Stop(true, behavior);
            }
            if (sparks != null)
            {
                sparks.Stop(true, behavior);
            }
        }

        private void OnDestroy()
        {
            if (particleMaterial == null)
            {
                return;
            }

            if (Application.isPlaying)
            {
                Destroy(particleMaterial);
            }
            else
            {
                DestroyImmediate(particleMaterial);
            }
        }
    }
}
