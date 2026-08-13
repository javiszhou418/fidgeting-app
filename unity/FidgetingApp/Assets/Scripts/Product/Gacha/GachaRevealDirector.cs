using System;
using UnityEngine;
using FidgetingApp.DisplayCase;

namespace FidgetingApp.Product.Gacha
{
    public enum GachaRevealPhase
    {
        Idle = 0,
        Suspense = 1,
        Revealing = 2,
        Complete = 3
    }

    /// <summary>
    /// Orchestrates one prize reveal: instantiates the neutral premium display
    /// case, applies the per-rarity signature (suspense hold + director-owned
    /// accent light + capsule preset by prize kind), plays the frozen 2.20 s
    /// case timeline, and forwards completion exactly once. The prize node is
    /// caller-owned; the case contract restores its parent/pose on teardown.
    /// Never writes Rigidbody state and never calls haptics directly.
    /// </summary>
    public sealed class GachaRevealDirector : MonoBehaviour
    {
        public event Action revealCompleted;

        private PremiumDisplayCase activeCase;
        private Light accentLight;
        private GachaRevealSignature signature;
        private GachaRevealPhase phase = GachaRevealPhase.Idle;
        private float suspenseRemaining;
        private bool completionForwarded;

        public GachaRevealPhase Phase => phase;
        public PremiumDisplayCase ActiveCase => activeCase;
        public Light AccentLight => accentLight;

        public void Begin(GachaDrawOutcome outcome, Transform prizeNode)
        {
            GachaPrizeDefinition? prize = GachaCatalog.ResolvePrize(outcome.PrizeId);
            GachaPrizeKind kind = prize.HasValue
                ? prize.Value.Kind
                : GachaPrizeKind.ToySkin;
            Begin(outcome.Rarity, kind, prizeNode);
        }

        public void Begin(GachaRarity rarity, GachaPrizeKind kind, Transform prizeNode)
        {
            Dismiss();
            signature = GachaRevealRules.Signature(rarity);
            activeCase = PremiumDisplayCaseFactory.Instantiate(transform);
            activeCase.setCapsulePreset(GachaRevealRules.CapsulePresetFor(kind));
            activeCase.setContent(prizeNode);
            activeCase.onRevealComplete += HandleRevealComplete;
            CreateAccentLight();
            suspenseRemaining = signature.SuspenseHoldSeconds;
            completionForwarded = false;
            phase = suspenseRemaining > 0f
                ? GachaRevealPhase.Suspense
                : GachaRevealPhase.Revealing;
            if (phase == GachaRevealPhase.Revealing)
            {
                activeCase.play();
            }
        }

        /// <summary>Deterministic step, called from Update and from tests.</summary>
        public void Tick(float deltaTime)
        {
            if (activeCase == null || phase == GachaRevealPhase.Idle)
            {
                return;
            }

            float dt = Mathf.Max(0f, deltaTime);
            if (phase == GachaRevealPhase.Suspense)
            {
                suspenseRemaining -= dt;
                if (suspenseRemaining <= 0f)
                {
                    phase = GachaRevealPhase.Revealing;
                    activeCase.play();
                }
            }

            if (accentLight != null)
            {
                float envelope = phase == GachaRevealPhase.Suspense
                    ? 0f
                    : GachaRevealRules.AccentEnvelope(activeCase.RevealProgress);
                accentLight.intensity = envelope
                    * signature.AccentIntensity
                    * GachaRevealRules.AccentLightMaxIntensity;
            }
        }

        /// <summary>
        /// Tears the reveal down. Destroying the case restores the prize
        /// node's original parent, pose, and active state per the case
        /// contract; the prize itself is never destroyed here.
        /// </summary>
        public void Dismiss()
        {
            if (activeCase != null)
            {
                activeCase.onRevealComplete -= HandleRevealComplete;
                // Detach the caller-owned prize before destroying the case.
                // DestroyImmediate can tear down child objects before the case's
                // OnDisable/OnDestroy callbacks run, so lifecycle restoration
                // alone is not sufficient in EditMode or editor tooling.
                activeCase.setContent((Transform)null);
                DestroyOwned(activeCase.gameObject);
                activeCase = null;
            }

            if (accentLight != null)
            {
                DestroyOwned(accentLight.gameObject);
                accentLight = null;
            }

            phase = GachaRevealPhase.Idle;
            completionForwarded = false;
        }

        private void Update()
        {
            Tick(Time.unscaledDeltaTime);
        }

        private void OnDisable()
        {
            Dismiss();
        }

        private void HandleRevealComplete()
        {
            phase = GachaRevealPhase.Complete;
            if (completionForwarded)
            {
                return;
            }

            completionForwarded = true;
            revealCompleted?.Invoke();
        }

        private void CreateAccentLight()
        {
            // Director-owned accent, deliberately outside the case's frozen
            // hierarchy so rarity tinting never leaks into the neutral prefab.
            var lightObject = new GameObject("GachaRarityAccentLight");
            lightObject.transform.SetParent(transform, false);
            lightObject.transform.localPosition = new Vector3(0f, 0.16f, -0.10f);
            accentLight = lightObject.AddComponent<Light>();
            accentLight.type = LightType.Point;
            accentLight.range = 0.85f;
            accentLight.color = signature.LiningColor;
            accentLight.intensity = 0f;
            accentLight.shadows = LightShadows.None;
        }

        private static void DestroyOwned(GameObject target)
        {
            if (Application.isPlaying)
            {
                Destroy(target);
            }
            else
            {
                DestroyImmediate(target);
            }
        }
    }
}
