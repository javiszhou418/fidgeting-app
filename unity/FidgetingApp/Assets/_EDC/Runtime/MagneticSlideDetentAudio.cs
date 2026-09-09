using System;
using System.Collections.Generic;
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
            return semanticEvent == FidgetSemanticEvent.MagneticEdgeProbe
                || semanticEvent == FidgetSemanticEvent.Breakaway
                || semanticEvent == FidgetSemanticEvent.DetentCrossed
                || semanticEvent == FidgetSemanticEvent.DetentCaptured;
        }

        public static float ResolveGain(
            FidgetSemanticEvent semanticEvent,
            float normalizedSignal)
        {
            float signal = Mathf.Clamp01(normalizedSignal);
            return semanticEvent switch
            {
                FidgetSemanticEvent.MagneticEdgeProbe =>
                    Mathf.Lerp(0.34f, 0.58f, signal),
                FidgetSemanticEvent.Breakaway => 0.82f,
                FidgetSemanticEvent.DetentCaptured => 0.68f,
                _ => Mathf.Lerp(
                    1f,
                    0.72f,
                    Mathf.SmoothStep(0f, 1f, signal)),
            };
        }

        public static float ResolvePitch(FidgetSemanticEvent semanticEvent)
        {
            return semanticEvent switch
            {
                FidgetSemanticEvent.MagneticEdgeProbe => 0.88f,
                FidgetSemanticEvent.Breakaway => 0.76f,
                FidgetSemanticEvent.DetentCaptured => 0.82f,
                _ => 1f,
            };
        }
    }

    /// <summary>
    /// Plays one event-routed Alloy Click for slide steps, endpoint unlock,
    /// rotational detents and endpoint lock. Programmatic poses stay silent.
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
        private readonly Dictionary<FidgetSemanticEvent, int> playbackCounts = new();

        public EdcSliderController Slider => slider;
        public AudioClip EffectClip => effectClip;
        public AudioSource[] Voices => voices;
        public float MasterVolume => masterVolume;
        public bool AudioReady { get; private set; }
        public int PlaybackCount { get; private set; }
        public int InitializationCount { get; private set; }
        public double LastPlaybackDspTime { get; private set; }
        public FidgetSemanticEvent LastPlaybackEvent { get; private set; }
        public int LastDetentDirection { get; private set; }
        public int LastDetentIndex { get; private set; }
        public int ActiveVoiceCount
        {
            get
            {
                int count = 0;
                foreach (AudioSource voice in voices)
                {
                    if (voice != null && voice.isPlaying)
                        count++;
                }
                return count;
            }
        }

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
            ReportAudioReady();
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
            ReportAudioReady();
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

            voice.pitch = MagneticSlideAudioModel.ResolvePitch(semanticEvent);
            float volume = masterVolume
                * MagneticSlideAudioModel.ResolveGain(
                    semanticEvent,
                    normalizedSignal);
            voice.PlayOneShot(effectClip, volume);
            PlaybackCount++;
            playbackCounts.TryGetValue(semanticEvent, out int eventCount);
            playbackCounts[semanticEvent] = eventCount + 1;
            LastPlaybackEvent = semanticEvent;
            if (semanticEvent == FidgetSemanticEvent.DetentCrossed)
            {
                LastDetentDirection = slider.LastSemanticDetentDirection;
                LastDetentIndex = slider.LastSemanticDetentIndex;
            }
            LastPlaybackDspTime = AudioSettings.dspTime;
            Debug.Log(
                "[MagneticSlideRuntime] audio-play "
                + $"event={semanticEvent} count={PlaybackCount} "
                + $"direction={LastDetentDirection} "
                + $"detent={LastDetentIndex} "
                + $"volume={volume:F3} pitch={voice.pitch:F3}");
        }

        public int PlaybackCountFor(FidgetSemanticEvent semanticEvent)
        {
            return playbackCounts.TryGetValue(
                semanticEvent,
                out int count)
                ? count
                : 0;
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

        private void ReportAudioReady()
        {
            bool ready = slider != null
                && effectClip != null
                && voices.Length == MagneticSlideAudioModel.VoiceCount;
            foreach (AudioSource voice in voices)
            {
                ready &= voice != null && voice.enabled;
            }
            AudioReady = ready;
            if (!AudioReady)
                return;

            InitializationCount++;
            AudioSettings.GetDSPBufferSize(
                out int bufferLength,
                out int bufferCount);
            Debug.Log(
                "[MagneticSlideRuntime] audio-ready "
                + $"clip={effectClip.name} voices={voices.Length} "
                + $"sampleRate={AudioSettings.outputSampleRate} "
                + $"dspBuffer={bufferLength}x{bufferCount}");
        }
    }
}
