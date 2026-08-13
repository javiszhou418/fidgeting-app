using System;
using CodexUnityLab;
using UnityEngine;

namespace FidgetingApp.FanCard
{
    /// <summary>
    /// Deterministic heavy-alloy tuning for the sixth product. The fan card
    /// sits lower in pitch than the rotor ratchet and becomes only slightly
    /// brighter with a faster physical detent crossing.
    /// </summary>
    public static class FanCardMetalAudioModel
    {
        public const int VoiceCount = 8;
        public const float DefaultMasterVolume = 0.90f;

        private static readonly float[] VariantOffsets =
        {
            -0.18f,
            0.08f,
            0.22f,
            -0.06f,
            0.14f
        };

        public static int NextVariantIndex(int variantCount, int previousIndex)
        {
            if (variantCount <= 1)
            {
                return 0;
            }

            return previousIndex < 0
                ? 0
                : (previousIndex + 1) % variantCount;
        }

        public static float ResolvePitch(float normalizedSignal, int variantIndex)
        {
            int safeIndex = Mathf.Abs(variantIndex) % VariantOffsets.Length;
            float semitones = -2.60f
                + Mathf.Clamp01(normalizedSignal) * 0.85f
                + VariantOffsets[safeIndex];
            return Mathf.Pow(2f, semitones / 12f);
        }

        public static float ResolveVolume(float normalizedSignal, float masterVolume)
        {
            float crossingEnergy = Mathf.SmoothStep(
                0.82f,
                1f,
                Mathf.Clamp01(normalizedSignal));
            return Mathf.Clamp01(masterVolume) * crossingEnergy;
        }
    }

    /// <summary>
    /// One authorized physical DetentCrossed semantic event produces exactly
    /// one atomic metal click. There is no Update loop, timer, scheduler, or
    /// raw-input path, so assistant motion and reset stay silent.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class FanCardMetalDetentAudio : MonoBehaviour
    {
        [SerializeField] private FanCardController controller;
        [SerializeField] private AudioClip[] clickVariants = Array.Empty<AudioClip>();
        [SerializeField] private AudioSource[] voices = Array.Empty<AudioSource>();
        [SerializeField, Range(0f, 1f)] private float masterVolume =
            FanCardMetalAudioModel.DefaultMasterVolume;

        private int lastVariantIndex = -1;
        private int nextVoiceIndex;

        public FanCardController Controller => controller;
        public AudioClip[] ClickVariants => clickVariants;
        public AudioSource[] Voices => voices;
        public float MasterVolume => masterVolume;

        public void Configure(
            FanCardController configuredController,
            AudioClip[] configuredVariants,
            AudioSource[] configuredVoices,
            float configuredMasterVolume = FanCardMetalAudioModel.DefaultMasterVolume)
        {
            controller = configuredController;
            clickVariants = configuredVariants ?? Array.Empty<AudioClip>();
            voices = configuredVoices ?? Array.Empty<AudioSource>();
            masterVolume = Mathf.Clamp01(configuredMasterVolume);
            ConfigureVoices();
        }

        private void Awake()
        {
            if (controller == null)
            {
                controller = GetComponentInParent<FanCardController>();
            }

            ConfigureVoices();
        }

        private void OnEnable()
        {
            if (controller != null)
            {
                controller.SemanticEventRaised += HandleSemanticEvent;
            }
        }

        private void OnDisable()
        {
            if (controller != null)
            {
                controller.SemanticEventRaised -= HandleSemanticEvent;
            }

            foreach (AudioSource voice in voices)
            {
                voice?.Stop();
            }
        }

        private void HandleSemanticEvent(
            FidgetSemanticEvent semanticEvent,
            float normalizedSignal)
        {
            if (semanticEvent != FidgetSemanticEvent.DetentCrossed
                || clickVariants.Length == 0
                || voices.Length == 0)
            {
                return;
            }

            int variantIndex = FanCardMetalAudioModel.NextVariantIndex(
                clickVariants.Length,
                lastVariantIndex);
            AudioClip clip = clickVariants[variantIndex];
            AudioSource voice = ResolveVoice();
            if (clip == null || voice == null)
            {
                return;
            }

            lastVariantIndex = variantIndex;
            voice.pitch = FanCardMetalAudioModel.ResolvePitch(
                normalizedSignal,
                variantIndex);
            voice.PlayOneShot(
                clip,
                FanCardMetalAudioModel.ResolveVolume(
                    normalizedSignal,
                    masterVolume));
        }

        private AudioSource ResolveVoice()
        {
            for (int offset = 0; offset < voices.Length; offset++)
            {
                int index = (nextVoiceIndex + offset) % voices.Length;
                AudioSource candidate = voices[index];
                if (candidate != null && !candidate.isPlaying)
                {
                    nextVoiceIndex = (index + 1) % voices.Length;
                    return candidate;
                }
            }

            AudioSource fallback = voices[nextVoiceIndex % voices.Length];
            nextVoiceIndex = (nextVoiceIndex + 1) % voices.Length;
            return fallback;
        }

        private void ConfigureVoices()
        {
            foreach (AudioSource voice in voices)
            {
                if (voice == null)
                {
                    continue;
                }

                voice.playOnAwake = false;
                voice.loop = false;
                voice.spatialBlend = 0f;
                voice.dopplerLevel = 0f;
                voice.reverbZoneMix = 0f;
                voice.bypassReverbZones = true;
                voice.priority = 44;
            }
        }
    }
}
