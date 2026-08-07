using System;
using CodexUnityLab;
using UnityEngine;

namespace FidgetingApp.EDC
{
    /// <summary>
    /// Deterministic mapping from the magnetic-slide semantic event to audio.
    /// The renderer never reads raw input and never schedules its own rhythm.
    /// </summary>
    public static class MagneticSlideAudioModel
    {
        public const int VoiceCount = 6;
        public const float DefaultMasterVolume = 0.78f;
        public const string EffectName = "Alloy Click 766 Hz";

        public static bool ShouldRender(FidgetSemanticEvent semanticEvent)
        {
            return semanticEvent == FidgetSemanticEvent.DetentCrossed;
        }

        public static float ResolveGain(float normalizedSpeed)
        {
            float speed = Mathf.Clamp01(normalizedSpeed);
            return Mathf.Lerp(1f, 0.72f, Mathf.SmoothStep(0f, 1f, speed));
        }
    }

    /// <summary>
    /// Plays one complete Alloy Click 766 Hz sound for each authorized physical
    /// detent crossing. Capture, breakaway, reset, assistant drive and
    /// programmatic pose changes do not create an extra click.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class MagneticSlideDetentAudio : MonoBehaviour
    {
        [SerializeField] private EdcSliderController slider;
        [SerializeField] private AudioClip effectClip;
        [SerializeField] private AudioSource[] voices = Array.Empty<AudioSource>();
        [SerializeField, Range(0f, 1f)] private float masterVolume =
            MagneticSlideAudioModel.DefaultMasterVolume;

        private int nextVoiceIndex;
        private bool subscribed;

        public EdcSliderController Slider => slider;
        public AudioClip EffectClip => effectClip;
        public AudioSource[] Voices => voices;
        public float MasterVolume => masterVolume;

        public void Configure(
            EdcSliderController configuredSlider,
            AudioClip configuredEffectClip,
            AudioSource[] configuredVoices,
            float configuredMasterVolume = MagneticSlideAudioModel.DefaultMasterVolume)
        {
            Unsubscribe();
            slider = configuredSlider;
            effectClip = configuredEffectClip;
            voices = configuredVoices ?? Array.Empty<AudioSource>();
            masterVolume = Mathf.Clamp01(configuredMasterVolume);
            ConfigureVoices();
            if (isActiveAndEnabled)
            {
                Subscribe();
            }
        }

        private void Awake()
        {
            if (slider == null)
            {
                slider = GetComponentInParent<EdcSliderController>();
            }
            ConfigureVoices();
        }

        private void OnEnable()
        {
            Subscribe();
        }

        private void OnDisable()
        {
            Unsubscribe();
            foreach (AudioSource voice in voices)
            {
                voice?.Stop();
            }
        }

        private void Subscribe()
        {
            if (subscribed || slider == null)
            {
                return;
            }
            slider.SemanticEventRaised += HandleSemanticEvent;
            subscribed = true;
        }

        private void Unsubscribe()
        {
            if (!subscribed || slider == null)
            {
                subscribed = false;
                return;
            }
            slider.SemanticEventRaised -= HandleSemanticEvent;
            subscribed = false;
        }

        private void HandleSemanticEvent(
            FidgetSemanticEvent semanticEvent,
            float normalizedSignal)
        {
            if (!MagneticSlideAudioModel.ShouldRender(semanticEvent)
                || effectClip == null
                || voices.Length == 0)
            {
                return;
            }

            AudioSource voice = ResolveVoice();
            if (voice == null)
            {
                return;
            }

            voice.pitch = 1f;
            float volume = masterVolume
                * MagneticSlideAudioModel.ResolveGain(normalizedSignal);
            voice.PlayOneShot(effectClip, volume);
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

                voice.clip = null;
                voice.playOnAwake = false;
                voice.loop = false;
                voice.spatialBlend = 0f;
                voice.dopplerLevel = 0f;
                voice.reverbZoneMix = 0f;
                voice.bypassReverbZones = true;
                voice.priority = 48;
            }
        }
    }
}
