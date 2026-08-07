using CodexUnityLab;
using ThreeBladeEDC.Interaction;
using UnityEngine;

namespace ThreeBladeEDC.Presentation
{
    /// <summary>
    /// Adds a short local highlight to polished bevel material slots. The
    /// effect is driven only by actual rotor speed and semantic mechanism
    /// events; it never applies force or changes the mechanical state.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class MetalGlintController : MonoBehaviour
    {
        private static readonly int EmissionColorId =
            Shader.PropertyToID("_EmissionColor");

        [SerializeField] private RotorRigidbodyController rotor;
        [SerializeField] private Renderer[] polishedRenderers;
        [SerializeField, Min(0)] private int polishedMaterialIndex = 1;
        [SerializeField, Min(0f)] private float speedStartRadians = 8f;
        [SerializeField, Min(0.1f)] private float speedFullRadians = 34f;
        [SerializeField, Range(0f, 0.35f)] private float speedGlintMaximum = 0.16f;
        [SerializeField, Min(0.1f)] private float pulseDecayPerSecond = 3.6f;
        [SerializeField] private Color warmGlint = new Color(1f, 0.24f, 0.055f, 1f);

        private MaterialPropertyBlock[] _blocks;
        private float _semanticPulse;
        private float _currentIntensity;
        private float _lastAppliedIntensity = -1f;
        private bool _subscribed;

        public float CurrentIntensity => _currentIntensity;
        public RotorRigidbodyController Rotor => rotor;

        public void Configure(
            RotorRigidbodyController rotorController,
            Renderer[] renderers,
            int materialIndex = 1)
        {
            Unsubscribe();
            rotor = rotorController;
            polishedRenderers = renderers;
            polishedMaterialIndex = Mathf.Max(0, materialIndex);
            PrepareBlocks();
            Subscribe();
            ClearGlint();
        }

        private void OnEnable()
        {
            PrepareBlocks();
            Subscribe();
        }

        private void OnDisable()
        {
            Unsubscribe();
            ClearGlint();
        }

        private void Update()
        {
            float speed = rotor != null
                ? Mathf.Abs(rotor.AngularSpeedRadians)
                : 0f;
            float speedRange = Mathf.Max(0.1f, speedFullRadians - speedStartRadians);
            float normalizedSpeed = Mathf.Clamp01(
                (speed - speedStartRadians) / speedRange);
            float speedGlint = Mathf.SmoothStep(0f, 1f, normalizedSpeed)
                * speedGlintMaximum;

            _semanticPulse = Mathf.MoveTowards(
                _semanticPulse,
                0f,
                pulseDecayPerSecond * Time.unscaledDeltaTime);
            float target = Mathf.Clamp01(speedGlint + _semanticPulse);
            _currentIntensity = Mathf.MoveTowards(
                _currentIntensity,
                target,
                Time.unscaledDeltaTime * 8f);

            if (Mathf.Abs(_currentIntensity - _lastAppliedIntensity) >= 0.005f
                || (_currentIntensity == 0f && _lastAppliedIntensity != 0f))
            {
                ApplyGlint(_currentIntensity);
            }
        }

        private void HandleSemanticEvent(FidgetSemanticEvent semanticEvent, float strength)
        {
            float normalizedStrength = Mathf.Clamp01(strength);
            switch (semanticEvent)
            {
                case FidgetSemanticEvent.Breakaway:
                    _semanticPulse = Mathf.Max(
                        _semanticPulse,
                        Mathf.Lerp(0.42f, 0.80f, normalizedStrength));
                    break;
                case FidgetSemanticEvent.DetentCaptured:
                    _semanticPulse = Mathf.Max(
                        _semanticPulse,
                        Mathf.Lerp(0.32f, 0.62f, normalizedStrength));
                    break;
            }
        }

        private void HandleReset()
        {
            ClearGlint();
        }

        private void Subscribe()
        {
            if (_subscribed || rotor == null)
            {
                return;
            }

            rotor.SemanticEventRaised += HandleSemanticEvent;
            rotor.ResetPerformed += HandleReset;
            _subscribed = true;
        }

        private void Unsubscribe()
        {
            if (!_subscribed || rotor == null)
            {
                _subscribed = false;
                return;
            }

            rotor.SemanticEventRaised -= HandleSemanticEvent;
            rotor.ResetPerformed -= HandleReset;
            _subscribed = false;
        }

        private void PrepareBlocks()
        {
            int count = polishedRenderers != null ? polishedRenderers.Length : 0;
            if (_blocks != null && _blocks.Length == count)
            {
                return;
            }

            _blocks = new MaterialPropertyBlock[count];
            for (int index = 0; index < count; index++)
            {
                _blocks[index] = new MaterialPropertyBlock();
            }
        }

        private void ClearGlint()
        {
            _semanticPulse = 0f;
            _currentIntensity = 0f;
            ApplyGlint(0f);
        }

        private void ApplyGlint(float intensity)
        {
            PrepareBlocks();
            if (polishedRenderers == null)
            {
                _lastAppliedIntensity = intensity;
                return;
            }

            Color emission = warmGlint * Mathf.Max(0f, intensity);
            for (int index = 0; index < polishedRenderers.Length; index++)
            {
                Renderer target = polishedRenderers[index];
                if (target == null
                    || target.sharedMaterials.Length <= polishedMaterialIndex)
                {
                    continue;
                }

                MaterialPropertyBlock block = _blocks[index];
                target.GetPropertyBlock(block, polishedMaterialIndex);
                block.SetColor(EmissionColorId, emission);
                target.SetPropertyBlock(block, polishedMaterialIndex);
            }

            _lastAppliedIntensity = intensity;
        }
    }
}
