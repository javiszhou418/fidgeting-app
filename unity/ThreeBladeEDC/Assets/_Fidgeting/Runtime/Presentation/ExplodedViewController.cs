using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;

namespace ThreeBladeEDC.Presentation
{
    [DisallowMultipleComponent]
    public sealed class ExplodedViewController : MonoBehaviour
    {
        [Serializable]
        public struct ExplodedPart
        {
            public Transform transform;
            public Vector3 localOffset;
        }

        [SerializeField] private Rigidbody rotorBody;
        [SerializeField] private List<ExplodedPart> parts = new List<ExplodedPart>();
        [SerializeField, Min(0.05f)] private float transitionDuration = 0.45f;

        private readonly List<Vector3> _assembledPositions = new List<Vector3>();
        private bool _exploded;
        private float _progress;
        private bool _cachedKinematic;

        public bool IsExploded => _exploded;

        public void Configure(Rigidbody rotor, IEnumerable<ExplodedPart> explodedParts)
        {
            rotorBody = rotor;
            parts = new List<ExplodedPart>(explodedParts);
            CacheAssembledPositions();
        }

        private void Awake()
        {
            CacheAssembledPositions();
        }

        private void Update()
        {
            Keyboard keyboard = Keyboard.current;
            if (keyboard != null && keyboard.eKey.wasPressedThisFrame)
            {
                Toggle();
            }

            float destination = _exploded ? 1f : 0f;
            _progress = Mathf.MoveTowards(
                _progress,
                destination,
                Time.unscaledDeltaTime / transitionDuration);

            float eased = _progress * _progress * (3f - 2f * _progress);
            int count = Mathf.Min(parts.Count, _assembledPositions.Count);
            for (int i = 0; i < count; i++)
            {
                Transform part = parts[i].transform;
                if (part == null)
                {
                    continue;
                }

                part.localPosition = Vector3.LerpUnclamped(
                    _assembledPositions[i],
                    _assembledPositions[i] + parts[i].localOffset,
                    eased);
            }
        }

        public void Toggle()
        {
            SetExploded(!_exploded);
        }

        public void SetExploded(bool value)
        {
            if (_exploded == value)
            {
                return;
            }

            _exploded = value;
            if (rotorBody == null)
            {
                return;
            }

            if (_exploded)
            {
                _cachedKinematic = rotorBody.isKinematic;
                rotorBody.angularVelocity = Vector3.zero;
                rotorBody.isKinematic = true;
            }
            else
            {
                rotorBody.isKinematic = _cachedKinematic;
            }
        }

        private void CacheAssembledPositions()
        {
            _assembledPositions.Clear();
            foreach (ExplodedPart part in parts)
            {
                _assembledPositions.Add(
                    part.transform == null ? Vector3.zero : part.transform.localPosition);
            }
        }
    }
}
