using UnityEngine;

namespace ThreeBladeEDC.Interaction
{
    /// <summary>
    /// Deterministic synthesis parameters derived from the rotor's measured
    /// angular velocity. This model is read-only: it never drives motion.
    /// </summary>
    public readonly struct RotorWindAudioFrame
    {
        public RotorWindAudioFrame(
            float normalizedSpeed,
            float gain,
            float bladePassFrequency,
            float bodyCutoff,
            float midBandCenter,
            float edgeCutoff,
            float primaryResonance,
            float secondaryResonance,
            float upperAlloyResonance)
        {
            NormalizedSpeed = normalizedSpeed;
            Gain = gain;
            BladePassFrequency = bladePassFrequency;
            BodyCutoff = bodyCutoff;
            MidBandCenter = midBandCenter;
            EdgeCutoff = edgeCutoff;
            PrimaryResonance = primaryResonance;
            SecondaryResonance = secondaryResonance;
            UpperAlloyResonance = upperAlloyResonance;
        }

        public float NormalizedSpeed { get; }
        public float Gain { get; }
        public float BladePassFrequency { get; }
        public float BodyCutoff { get; }
        public float MidBandCenter { get; }
        public float EdgeCutoff { get; }
        public float PrimaryResonance { get; }
        public float SecondaryResonance { get; }
        public float UpperAlloyResonance { get; }
        public bool IsAudible => Gain > 0f;
    }

    /// <summary>
    /// Shared tuning for the four shipping rotors. Wind is continuous in both
    /// resistance modes; magnetic-detent clicks are layered independently by
    /// MetalRatchetDetentAudio when the mechanism emits a detent crossing.
    /// </summary>
    public static class RotorWindAudioModel
    {
        public const float AudibleThresholdRadians = 0.35f;
        public const float FullScaleAngularSpeed =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultMaximumAngularSpeed;
        public const float DefaultMasterVolume = 0.50f;
        public const float DefaultAlloyResonance = 1f;
        public const float GainCurveExponent = 0.62f;
        public const float ResonancePitchTrackingExponent = 0.78f;
        public const float FinalMetalPitchSemitones = 9f;
        public const float ResonancePitchMinimumRpm = 20f;
        public const float ResonancePitchMaximumRpm = 400f;
        public const float ParameterSmoothingSeconds = 0.004f;
        public const int DspBufferSamples = 256;
        public const float BodyNoiseMix = 0.86f;
        public const float MidNoiseMix = 0.14f;
        public const float EdgeNoiseMix = 0.018f;
        public const float PrimaryResonanceMix = 0.105f;
        public const float SecondaryResonanceMix = 0.215f;
        public const float UpperAlloyResonanceMix = 0.160f;
        public const float MetalStrikeNoiseMix = 0.34f;
        public const float MetalPulseDutyCycle = 0.14f;
        public const float MetalRingAttackSeconds = 0.003f;
        public const float MetalRingMaximumSeconds = 0.065f;
        public const float MetalRingMaximumDutyCycle = 0.72f;
        public const float RestBodyCutoff = 210f;
        public const float RestMidBandCenter = 540f;
        public const float RestEdgeCutoff = 3200f;
        public const float RestPrimaryResonance = 669f;
        public const float RestSecondaryResonance = 1539f;
        public const float RestUpperAlloyResonance = 2776f;
        public const float MaximumPrimaryResonance = 1076f;
        public const float MaximumSecondaryResonance = 2474f;
        public const float MaximumUpperAlloyResonance = 4464f;
        public static float FinalMetalPitchRatio => Mathf.Pow(
            2f,
            FinalMetalPitchSemitones / 12f);
        public static float TunedRestPrimaryResonance =>
            RestPrimaryResonance * FinalMetalPitchRatio;
        public static float TunedMaximumPrimaryResonance =>
            MaximumPrimaryResonance * FinalMetalPitchRatio;

        public static RotorWindAudioFrame Evaluate(
            float angularSpeedRadians,
            int bladeCount,
            float masterVolume = DefaultMasterVolume)
        {
            float speed = Mathf.Abs(angularSpeedRadians);
            int blades = Mathf.Clamp(bladeCount, 2, 4);
            float normalized = Mathf.Clamp01(Mathf.InverseLerp(
                AudibleThresholdRadians,
                FullScaleAngularSpeed,
                speed));
            float gain = normalized <= 0f
                ? 0f
                : Mathf.Clamp01(masterVolume)
                    * Mathf.Pow(normalized, GainCurveExponent);
            float revolutionsPerMinute = speed / (Mathf.PI * 2f) * 60f;
            float resonancePitchTracking = Mathf.Pow(
                Mathf.Clamp01(Mathf.InverseLerp(
                    ResonancePitchMinimumRpm,
                    ResonancePitchMaximumRpm,
                    revolutionsPerMinute)),
                ResonancePitchTrackingExponent);
            float finalPitchRatio = FinalMetalPitchRatio;
            float bladePassFrequency = speed / (Mathf.PI * 2f) * blades;

            return new RotorWindAudioFrame(
                normalized,
                gain,
                bladePassFrequency,
                Mathf.Lerp(RestBodyCutoff, 780f, normalized),
                Mathf.Lerp(RestMidBandCenter, 1450f, normalized),
                Mathf.Lerp(RestEdgeCutoff, 5600f, normalized),
                Mathf.Lerp(
                    RestPrimaryResonance,
                    MaximumPrimaryResonance,
                    resonancePitchTracking) * finalPitchRatio,
                Mathf.Lerp(
                    RestSecondaryResonance,
                    MaximumSecondaryResonance,
                    resonancePitchTracking) * finalPitchRatio,
                Mathf.Lerp(
                    RestUpperAlloyResonance,
                    MaximumUpperAlloyResonance,
                    resonancePitchTracking) * finalPitchRatio);
        }

        public static float ResolveMetalPulse(float bladePhase)
        {
            float turnPhase = Mathf.Repeat(bladePhase / (Mathf.PI * 2f), 1f);
            if (turnPhase >= MetalPulseDutyCycle)
            {
                return 0f;
            }

            float decay = 1f - turnPhase / MetalPulseDutyCycle;
            return decay * decay * decay;
        }

        public static float ResolveMetalRing(float bladePhase, float bladePassFrequency)
        {
            if (bladePassFrequency <= 0f)
            {
                return 0f;
            }

            float dutyCycle = Mathf.Min(
                MetalRingMaximumDutyCycle,
                bladePassFrequency * MetalRingMaximumSeconds);
            float attackFraction = Mathf.Min(
                dutyCycle * 0.25f,
                bladePassFrequency * MetalRingAttackSeconds);
            float turnPhase = Mathf.Repeat(bladePhase / (Mathf.PI * 2f), 1f);
            if (turnPhase < attackFraction)
            {
                return turnPhase / attackFraction;
            }

            if (turnPhase >= dutyCycle)
            {
                return 0f;
            }

            float decay = 1f - (turnPhase - attackFraction)
                / (dutyCycle - attackFraction);
            return Mathf.Pow(decay, 1.45f);
        }

        public static float ResolveBrightAlloyTriangle(
            float phase,
            float frequency,
            float sampleRate)
        {
            float fundamental = Mathf.Sin(phase);
            if (frequency * 3f >= sampleRate * 0.45f)
            {
                return fundamental;
            }

            return 9f / 8f * (fundamental + Mathf.Sin(phase * 3f) / 9f);
        }
    }

    /// <summary>
    /// Procedural rotor wind renderer. It reads real Rigidbody angular speed
    /// and renders air movement, blade-pass modulation and restrained alloy
    /// resonance. Natural physics deceleration therefore produces matching
    /// audio deceleration and fade-out without a separate timeline.
    /// </summary>
    [DisallowMultipleComponent]
    [RequireComponent(typeof(AudioSource))]
    [DefaultExecutionOrder(100)]
    public sealed class RotorWindAudio : MonoBehaviour
    {
        private const int OutputChannels = 2;
        private const float TwoPi = Mathf.PI * 2f;

        [SerializeField] private RotorRigidbodyController rotor;
        [SerializeField, Range(2, 4)] private int bladeCount = 3;
        [SerializeField, Range(0f, 1f)] private float masterVolume =
            RotorWindAudioModel.DefaultMasterVolume;
        [SerializeField, Range(0f, 1f)] private float bladePulseDepth = 0.22f;
        [SerializeField, Range(0f, 1f)] private float alloyResonance =
            RotorWindAudioModel.DefaultAlloyResonance;

        private AudioSource _source;
        private AudioClip _proceduralClip;
        private int _sampleRate = 48000;
        private uint _noiseState = 0xA341316Cu;
        private volatile int _resetRequested;
        private volatile float _targetNormalizedSpeed;
        private volatile float _targetGain;
        private volatile float _targetBladePassFrequency;
        private volatile float _targetBodyCutoff;
        private volatile float _targetMidBandCenter;
        private volatile float _targetEdgeCutoff;
        private volatile float _targetPrimaryResonance;
        private volatile float _targetSecondaryResonance;
        private volatile float _targetUpperAlloyResonance;

        private float _currentNormalizedSpeed;
        private float _currentGain;
        private float _currentBladePassFrequency;
        private float _currentBodyCutoff = RotorWindAudioModel.RestBodyCutoff;
        private float _currentMidBandCenter = RotorWindAudioModel.RestMidBandCenter;
        private float _currentEdgeCutoff = RotorWindAudioModel.RestEdgeCutoff;
        private float _currentPrimaryResonance =
            RotorWindAudioModel.RestPrimaryResonance
            * RotorWindAudioModel.FinalMetalPitchRatio;
        private float _currentSecondaryResonance =
            RotorWindAudioModel.RestSecondaryResonance
            * RotorWindAudioModel.FinalMetalPitchRatio;
        private float _currentUpperAlloyResonance =
            RotorWindAudioModel.RestUpperAlloyResonance
            * RotorWindAudioModel.FinalMetalPitchRatio;
        private float _bodyNoise;
        private float _bodySmooth;
        private float _midLow;
        private float _midHigh;
        private float _edgeLow;
        private float _strikeLow;
        private float _strikeHigh;
        private float _bladePhase;
        private float _primaryPhase;
        private float _secondaryPhase;
        private float _upperAlloyPhase;

        public RotorRigidbodyController Rotor => rotor;
        public int BladeCount => bladeCount;
        public float MasterVolume => masterVolume;
        public float BladePulseDepth => bladePulseDepth;
        public float AlloyResonance => alloyResonance;

        public void Configure(
            RotorRigidbodyController configuredRotor,
            int configuredBladeCount,
            float configuredMasterVolume = RotorWindAudioModel.DefaultMasterVolume,
            float configuredAlloyResonance = RotorWindAudioModel.DefaultAlloyResonance)
        {
            rotor = configuredRotor;
            bladeCount = Mathf.Clamp(configuredBladeCount, 2, 4);
            masterVolume = Mathf.Clamp01(configuredMasterVolume);
            alloyResonance = Mathf.Clamp01(configuredAlloyResonance);
            ConfigureAudioSource();
            UpdateTargets();
        }

        private void Awake()
        {
            if (rotor == null)
            {
                rotor = GetComponentInParent<RotorRigidbodyController>();
            }

            ConfigureAudioSource();
            UpdateTargets();
        }

        private void OnEnable()
        {
            if (rotor != null)
            {
                rotor.ResetPerformed += HandleRotorReset;
            }

            if (Application.isPlaying)
            {
                StartProceduralAudio();
            }
        }

        private void Update()
        {
            UpdateTargets();
        }

        private void OnDisable()
        {
            if (rotor != null)
            {
                rotor.ResetPerformed -= HandleRotorReset;
            }

            _targetGain = 0f;
            _resetRequested = 1;
            _source?.Stop();
        }

        private void OnDestroy()
        {
            if (_proceduralClip != null)
            {
                Destroy(_proceduralClip);
                _proceduralClip = null;
            }
        }

        private void OnValidate()
        {
            bladeCount = Mathf.Clamp(bladeCount, 2, 4);
            masterVolume = Mathf.Clamp01(masterVolume);
            bladePulseDepth = Mathf.Clamp01(bladePulseDepth);
            alloyResonance = Mathf.Clamp01(alloyResonance);
            ConfigureAudioSource();
        }

        private void HandleRotorReset()
        {
            _targetGain = 0f;
            _resetRequested = 1;
        }

        private void ConfigureAudioSource()
        {
            if (_source == null)
            {
                _source = GetComponent<AudioSource>();
            }

            if (_source == null)
            {
                return;
            }

            _source.playOnAwake = false;
            _source.loop = true;
            _source.spatialBlend = 0f;
            _source.dopplerLevel = 0f;
            _source.reverbZoneMix = 0f;
            _source.bypassReverbZones = true;
            _source.priority = 64;
            _source.volume = 1f;
        }

        private void StartProceduralAudio()
        {
            ConfigureAudioSource();
            if (_source == null)
            {
                return;
            }

            _sampleRate = Mathf.Max(8000, AudioSettings.outputSampleRate);
            if (_proceduralClip == null)
            {
                _proceduralClip = AudioClip.Create(
                    "RotorWind_Procedural",
                    _sampleRate,
                    OutputChannels,
                    _sampleRate,
                    false);
            }

            _source.clip = _proceduralClip;
            if (!_source.isPlaying)
            {
                _source.Play();
            }
        }

        private void UpdateTargets()
        {
            RotorWindAudioFrame frame = RotorWindAudioModel.Evaluate(
                rotor != null ? rotor.AngularSpeedRadians : 0f,
                bladeCount,
                masterVolume);
            _targetNormalizedSpeed = frame.NormalizedSpeed;
            _targetGain = frame.Gain;
            _targetBladePassFrequency = frame.BladePassFrequency;
            _targetBodyCutoff = frame.BodyCutoff;
            _targetMidBandCenter = frame.MidBandCenter;
            _targetEdgeCutoff = frame.EdgeCutoff;
            _targetPrimaryResonance = frame.PrimaryResonance;
            _targetSecondaryResonance = frame.SecondaryResonance;
            _targetUpperAlloyResonance = frame.UpperAlloyResonance;
        }

        private void OnAudioFilterRead(float[] data, int channels)
        {
            if (channels <= 0)
            {
                return;
            }

            if (_resetRequested != 0)
            {
                ResetSynthState();
                _resetRequested = 0;
            }

            float smoothing = 1f - Mathf.Exp(
                -1f / (_sampleRate * RotorWindAudioModel.ParameterSmoothingSeconds));
            for (int index = 0; index < data.Length; index += channels)
            {
                SmoothParameters(smoothing);

                float white = NextWhiteNoise();
                float bodyAlpha = LowPassAlpha(_currentBodyCutoff);
                _bodyNoise += bodyAlpha * (white - _bodyNoise);
                _bodySmooth += bodyAlpha * 0.34f * (_bodyNoise - _bodySmooth);

                float midLowAlpha = LowPassAlpha(_currentMidBandCenter * 0.48f);
                float midHighAlpha = LowPassAlpha(_currentMidBandCenter * 1.62f);
                _midLow += midLowAlpha * (white - _midLow);
                _midHigh += midHighAlpha * (white - _midHigh);
                float midBand = _midHigh - _midLow;

                float edgeAlpha = LowPassAlpha(_currentEdgeCutoff);
                _edgeLow += edgeAlpha * (white - _edgeLow);
                float edge = white - _edgeLow;

                float resonancePitchTracking = Mathf.InverseLerp(
                    RotorWindAudioModel.TunedRestPrimaryResonance,
                    RotorWindAudioModel.TunedMaximumPrimaryResonance,
                    _currentPrimaryResonance);
                float finalPitchRatio = RotorWindAudioModel.FinalMetalPitchRatio;
                float strikeLowAlpha = LowPassAlpha(
                    (2000f + 900f * resonancePitchTracking) * finalPitchRatio);
                float strikeHighAlpha = LowPassAlpha(
                    (6000f + 1800f * resonancePitchTracking) * finalPitchRatio);
                _strikeLow += strikeLowAlpha * (white - _strikeLow);
                _strikeHigh += strikeHighAlpha * (white - _strikeHigh);
                float strikeBand = _strikeHigh - _strikeLow;

                AdvancePhase(ref _bladePhase, _currentBladePassFrequency);
                AdvancePhase(ref _primaryPhase, _currentPrimaryResonance);
                AdvancePhase(ref _secondaryPhase, _currentSecondaryResonance);
                AdvancePhase(ref _upperAlloyPhase, _currentUpperAlloyResonance);

                float bladePulse = 1f + bladePulseDepth
                    * (0.02f + 0.04f * _currentNormalizedSpeed)
                    * Mathf.Sin(_bladePhase);
                float strikePulse = RotorWindAudioModel.ResolveMetalPulse(_bladePhase);
                float ringEnvelope = RotorWindAudioModel.ResolveMetalRing(
                    _bladePhase,
                    _currentBladePassFrequency);
                float resonanceDrive = alloyResonance;
                float airPresence = Mathf.Max(
                    0.12f,
                    1f - 0.88f * Mathf.Pow(alloyResonance, 0.85f));
                float air = airPresence
                    * (RotorWindAudioModel.BodyNoiseMix * _bodySmooth
                    + RotorWindAudioModel.MidNoiseMix * midBand
                    + RotorWindAudioModel.EdgeNoiseMix * edge) * bladePulse;
                float resonanceExcitation = 0.65f
                    + 1.35f * Mathf.Abs(_bodySmooth);
                float ringing = resonanceExcitation
                    * (RotorWindAudioModel.PrimaryResonanceMix
                        * Mathf.Sin(_primaryPhase)
                        + RotorWindAudioModel.SecondaryResonanceMix
                        * RotorWindAudioModel.ResolveBrightAlloyTriangle(
                            _secondaryPhase,
                            _currentSecondaryResonance,
                            _sampleRate)
                        + RotorWindAudioModel.UpperAlloyResonanceMix
                        * RotorWindAudioModel.ResolveBrightAlloyTriangle(
                            _upperAlloyPhase,
                            _currentUpperAlloyResonance,
                            _sampleRate));
                float strike = RotorWindAudioModel.MetalStrikeNoiseMix * strikeBand;
                float metal = resonanceDrive
                    * (ringEnvelope * ringing + strikePulse * strike);
                float sample = _currentGain * (air + metal);
                sample = sample / (1f + Mathf.Abs(sample));

                int frameEnd = Mathf.Min(index + channels, data.Length);
                for (int channel = index; channel < frameEnd; channel++)
                {
                    data[channel] = sample;
                }
            }
        }

        private void SmoothParameters(float amount)
        {
            _currentNormalizedSpeed += amount
                * (_targetNormalizedSpeed - _currentNormalizedSpeed);
            _currentGain += amount * (_targetGain - _currentGain);
            _currentBladePassFrequency += amount
                * (_targetBladePassFrequency - _currentBladePassFrequency);
            _currentBodyCutoff += amount
                * (_targetBodyCutoff - _currentBodyCutoff);
            _currentMidBandCenter += amount
                * (_targetMidBandCenter - _currentMidBandCenter);
            _currentEdgeCutoff += amount
                * (_targetEdgeCutoff - _currentEdgeCutoff);
            _currentPrimaryResonance += amount
                * (_targetPrimaryResonance - _currentPrimaryResonance);
            _currentSecondaryResonance += amount
                * (_targetSecondaryResonance - _currentSecondaryResonance);
            _currentUpperAlloyResonance += amount
                * (_targetUpperAlloyResonance - _currentUpperAlloyResonance);
        }

        private float LowPassAlpha(float cutoff)
        {
            float normalized = TwoPi * Mathf.Clamp(cutoff, 10f, _sampleRate * 0.45f)
                / _sampleRate;
            return normalized / (1f + normalized);
        }

        private void AdvancePhase(ref float phase, float frequency)
        {
            phase += TwoPi * frequency / _sampleRate;
            if (phase >= TwoPi)
            {
                phase -= TwoPi * Mathf.Floor(phase / TwoPi);
            }
        }

        private float NextWhiteNoise()
        {
            uint value = _noiseState;
            value ^= value << 13;
            value ^= value >> 17;
            value ^= value << 5;
            _noiseState = value;
            return ((value & 0x00FFFFFFu) / 8388607.5f) - 1f;
        }

        private void ResetSynthState()
        {
            _currentNormalizedSpeed = 0f;
            _currentGain = 0f;
            _currentBladePassFrequency = 0f;
            _bodyNoise = 0f;
            _bodySmooth = 0f;
            _midLow = 0f;
            _midHigh = 0f;
            _edgeLow = 0f;
            _strikeLow = 0f;
            _strikeHigh = 0f;
            _bladePhase = 0f;
            _primaryPhase = 0f;
            _secondaryPhase = 0f;
            _upperAlloyPhase = 0f;
        }
    }
}
