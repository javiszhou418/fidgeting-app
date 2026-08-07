using System;
using UnityEngine;

namespace ThreeBladeEDC.Interaction
{
    /// <summary>
    /// Immutable data captured by the mechanism at the exact instant one
    /// physical detent boundary is crossed. Audio never schedules its own
    /// rhythm; every instance of this value corresponds to one click.
    /// </summary>
    public readonly struct RatchetDetentAudioSignal
    {
        public RatchetDetentAudioSignal(
            float normalizedAngularSpeed,
            float initialFlickForce,
            int initialFlickClickIndex,
            int detentIndex)
        {
            NormalizedAngularSpeed = Mathf.Clamp01(normalizedAngularSpeed);
            InitialFlickForce = Mathf.Clamp01(initialFlickForce);
            InitialFlickClickIndex = initialFlickClickIndex;
            DetentIndex = detentIndex;
        }

        public float NormalizedAngularSpeed { get; }
        public float InitialFlickForce { get; }
        public int InitialFlickClickIndex { get; }
        public int DetentIndex { get; }
    }

    /// <summary>
    /// Pure parameter mapping for the ratchet renderer. Slow teeth seat at
    /// full per-click level; high-speed teeth become lighter and overlap into
    /// a whir naturally. No value here changes the rotor simulation.
    /// </summary>
    public static class RatchetAudioPhysicsModel
    {
        public const int InitialFlickClickCount = 5;
        public const int MinimumVoiceCount = 8;
        public const float HighSpeedVolumeGain = 0.34f;

        private static readonly float[] FlickClickEnvelope =
        {
            0.20f,
            0.15f,
            0.10f,
            0.06f,
            0.03f
        };

        public static float ResolveVolume(
            float normalizedAngularSpeed,
            float initialFlickForce,
            int initialFlickClickIndex)
        {
            float speed = Mathf.Clamp01(normalizedAngularSpeed);
            float speedGain = Mathf.Lerp(
                1f,
                HighSpeedVolumeGain,
                Mathf.SmoothStep(0f, 1f, speed));
            float flickGain = initialFlickClickIndex >= 0
                && initialFlickClickIndex < FlickClickEnvelope.Length
                    ? Mathf.Clamp01(initialFlickForce)
                        * FlickClickEnvelope[initialFlickClickIndex]
                    : 0f;
            return Mathf.Clamp01(speedGain + flickGain);
        }

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

        public static int CrossedDetentCount(int previousIndex, int currentIndex)
        {
            return Mathf.Abs(currentIndex - previousIndex);
        }

        public static float ResolvePitchSemitones(
            float normalizedAngularSpeed,
            ref uint randomState)
        {
            float sign = NextUnit(ref randomState) < 0.5f ? -1f : 1f;
            float randomMagnitude = Mathf.Lerp(1f, 2f, NextUnit(ref randomState));
            float speedRise = Mathf.Clamp01(normalizedAngularSpeed)
                * NextUnit(ref randomState);
            return sign * randomMagnitude + speedRise;
        }

        public static float SemitonesToPitch(float semitones)
        {
            return Mathf.Pow(2f, semitones / 12f);
        }

        private static float NextUnit(ref uint state)
        {
            if (state == 0)
            {
                state = 0x9E3779B9u;
            }

            state ^= state << 13;
            state ^= state >> 17;
            state ^= state << 5;
            return (state & 0x00FFFFFFu) / 16777215f;
        }
    }

    /// <summary>
    /// Polyphonic, event-only renderer for the metal ratchet. One mechanism
    /// event executes exactly one PlayOneShot call. It has no Update loop,
    /// timeline, scheduler, gate, rate limit, or high-speed mode switch.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class MetalRatchetDetentAudio : MonoBehaviour
    {
        [SerializeField] private RotorRigidbodyController rotor;
        [SerializeField] private AudioClip[] clickVariants = Array.Empty<AudioClip>();
        [SerializeField] private AudioSource[] voices = Array.Empty<AudioSource>();
        [SerializeField, Range(0f, 1f)] private float masterVolume = 0.82f;

        private int lastVariantIndex = -1;
        private int nextVoiceIndex;
        private uint randomState = 0xC001CAFEu;

        public RotorRigidbodyController Rotor => rotor;
        public AudioClip[] ClickVariants => clickVariants;
        public AudioSource[] Voices => voices;
        public float MasterVolume => masterVolume;

        public void Configure(
            RotorRigidbodyController configuredRotor,
            AudioClip[] configuredVariants,
            AudioSource[] configuredVoices,
            float configuredMasterVolume = 0.82f)
        {
            rotor = configuredRotor;
            clickVariants = configuredVariants ?? Array.Empty<AudioClip>();
            voices = configuredVoices ?? Array.Empty<AudioSource>();
            masterVolume = Mathf.Clamp01(configuredMasterVolume);
            ConfigureVoices();
        }

        private void Awake()
        {
            if (rotor == null)
            {
                rotor = GetComponentInParent<RotorRigidbodyController>();
            }

            ConfigureVoices();
        }

        private void OnEnable()
        {
            if (rotor != null)
            {
                rotor.RatchetDetentCrossed += HandleRatchetDetentCrossed;
            }
        }

        private void OnDisable()
        {
            if (rotor != null)
            {
                rotor.RatchetDetentCrossed -= HandleRatchetDetentCrossed;
            }

            foreach (AudioSource voice in voices)
            {
                voice?.Stop();
            }
        }

        private void HandleRatchetDetentCrossed(RatchetDetentAudioSignal signal)
        {
            if (clickVariants.Length == 0 || voices.Length == 0)
            {
                return;
            }

            int variantIndex = RatchetAudioPhysicsModel.NextVariantIndex(
                clickVariants.Length,
                lastVariantIndex);
            AudioClip clip = clickVariants[variantIndex];
            AudioSource voice = ResolveVoice();
            if (clip == null || voice == null)
            {
                return;
            }

            lastVariantIndex = variantIndex;
            float volume = masterVolume * RatchetAudioPhysicsModel.ResolveVolume(
                signal.NormalizedAngularSpeed,
                signal.InitialFlickForce,
                signal.InitialFlickClickIndex);
            float semitones = RatchetAudioPhysicsModel.ResolvePitchSemitones(
                signal.NormalizedAngularSpeed,
                ref randomState);
            voice.pitch = RatchetAudioPhysicsModel.SemitonesToPitch(semitones);
            voice.PlayOneShot(clip, volume);
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

            // No click is dropped when every source is busy. PlayOneShot is
            // itself polyphonic, so round-robin reuse adds the new voice to
            // the existing mix instead of stopping or gating it.
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
                voice.priority = 48;
            }
        }
    }
}
