using System;
using System.Reflection;
using FidgetingApp.DisplayCase;
using FidgetingApp.Product.Gacha;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class GachaRevealTests
    {
        private static readonly MethodInfo CaseUpdate =
            typeof(PremiumDisplayCase).GetMethod(
                "Update",
                BindingFlags.Instance | BindingFlags.NonPublic);

        [Test]
        public void SignaturesEscalateSuspenseAndAccentWithRarity()
        {
            GachaRevealSignature standard = GachaRevealRules.Signature(GachaRarity.Standard);
            GachaRevealSignature refined = GachaRevealRules.Signature(GachaRarity.Refined);
            GachaRevealSignature signature = GachaRevealRules.Signature(GachaRarity.Signature);
            GachaRevealSignature heirloom = GachaRevealRules.Signature(GachaRarity.Heirloom);

            Assert.That(standard.SuspenseHoldSeconds, Is.Zero);
            Assert.That(refined.SuspenseHoldSeconds, Is.Zero);
            Assert.That(signature.SuspenseHoldSeconds,
                Is.EqualTo(GachaRevealRules.SignatureSuspenseSeconds));
            Assert.That(heirloom.SuspenseHoldSeconds,
                Is.EqualTo(GachaRevealRules.HeirloomSuspenseSeconds));

            Assert.That(refined.AccentIntensity, Is.GreaterThan(standard.AccentIntensity));
            Assert.That(signature.AccentIntensity, Is.GreaterThan(refined.AccentIntensity));
            Assert.That(heirloom.AccentIntensity, Is.GreaterThan(signature.AccentIntensity));

            var colors = new[]
            {
                standard.LiningColor,
                refined.LiningColor,
                signature.LiningColor,
                heirloom.LiningColor
            };
            for (int a = 0; a < colors.Length; a++)
            {
                for (int b = a + 1; b < colors.Length; b++)
                {
                    Assert.That(colors[a] != colors[b], Is.True,
                        "Every rarity must publish a distinct lining color.");
                }
            }
        }

        [Test]
        public void TotalRevealAddsSuspenseOnTopOfTheFrozenCaseTimeline()
        {
            Assert.That(GachaRevealRules.TotalRevealSeconds(GachaRarity.Standard),
                Is.EqualTo(PremiumDisplayCaseRevealMotion.DurationSeconds).Within(1e-6));
            Assert.That(GachaRevealRules.TotalRevealSeconds(GachaRarity.Heirloom),
                Is.EqualTo(PremiumDisplayCaseRevealMotion.DurationSeconds + 1.2f)
                    .Within(1e-6));
        }

        [Test]
        public void EveryPrizeKindResolvesACapsulePreset()
        {
            Assert.That(GachaRevealRules.CapsulePresetFor(GachaPrizeKind.Toy),
                Is.EqualTo(PremiumDisplayCaseCapsulePreset.CollectorSlabLarge));
            Assert.That(GachaRevealRules.CapsulePresetFor(GachaPrizeKind.ToySkin),
                Is.EqualTo(PremiumDisplayCaseCapsulePreset.CollectorSlabLarge));
            Assert.That(GachaRevealRules.CapsulePresetFor(GachaPrizeKind.Sticker),
                Is.EqualTo(PremiumDisplayCaseCapsulePreset.CollectorSlabLarge));
            Assert.That(GachaRevealRules.CapsulePresetFor(GachaPrizeKind.DisplayBase),
                Is.EqualTo(PremiumDisplayCaseCapsulePreset.CollectorSlabLarge));
            Assert.That(GachaRevealRules.CapsulePresetFor(GachaPrizeKind.EnvironmentTint),
                Is.EqualTo(PremiumDisplayCaseCapsulePreset.CollectorSlabLarge));
        }

        [Test]
        public void AccentEnvelopeStaysDarkThroughTheLidPhaseThenSwellsAndSustains()
        {
            Assert.That(GachaRevealRules.AccentEnvelope(0f), Is.Zero);
            Assert.That(GachaRevealRules.AccentEnvelope(0.30f), Is.Zero);
            Assert.That(GachaRevealRules.AccentEnvelope(0.67f), Is.GreaterThan(0.9f));
            Assert.That(GachaRevealRules.AccentEnvelope(1f), Is.GreaterThan(0.15f),
                "A sustained floor must keep the lining tint readable after reveal.");
        }

        [Test]
        public void DirectorHoldsSuspenseBeforePlayingTheCase()
        {
            var host = new GameObject("director-host");
            GameObject prize = GameObject.CreatePrimitive(PrimitiveType.Cube);
            try
            {
                var director = host.AddComponent<GachaRevealDirector>();
                director.Begin(GachaRarity.Heirloom, GachaPrizeKind.ToySkin, prize.transform);

                Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Suspense));
                Assert.That(director.ActiveCase, Is.Not.Null);
                Assert.That(director.ActiveCase.IsRevealPlaying, Is.False,
                    "The case must not play during the suspense hold.");
                Assert.That(director.AccentLight.intensity, Is.Zero);

                director.Tick(0.6f);
                Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Suspense),
                    "Heirloom holds 1.2 s; 0.6 s is still suspense.");

                director.Tick(0.7f);
                Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Revealing));
                Assert.That(director.ActiveCase.IsRevealPlaying, Is.True);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(host);
                UnityEngine.Object.DestroyImmediate(prize);
            }
        }

        [Test]
        public void StandardRarityPlaysImmediatelyWithoutSuspense()
        {
            var host = new GameObject("director-host");
            GameObject prize = GameObject.CreatePrimitive(PrimitiveType.Cube);
            try
            {
                var director = host.AddComponent<GachaRevealDirector>();
                director.Begin(GachaRarity.Standard, GachaPrizeKind.Sticker, prize.transform);
                Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Revealing));
                Assert.That(director.ActiveCase.IsRevealPlaying, Is.True);
                Assert.That(director.ActiveCase.CapsulePreset,
                    Is.EqualTo(PremiumDisplayCaseCapsulePreset.CollectorSlabLarge));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(host);
                UnityEngine.Object.DestroyImmediate(prize);
            }
        }

        [Test]
        public void CompletionForwardsExactlyOnceAndAccentFollowsTheEnvelope()
        {
            var host = new GameObject("director-host");
            GameObject prize = GameObject.CreatePrimitive(PrimitiveType.Cube);
            try
            {
                var director = host.AddComponent<GachaRevealDirector>();
                int completions = 0;
                director.revealCompleted += () => completions += 1;
                director.Begin(GachaRarity.Signature, GachaPrizeKind.ToySkin, prize.transform);

                director.Tick(GachaRevealRules.SignatureSuspenseSeconds + 0.01f);
                Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Revealing));

                bool sawAccent = false;
                for (int step = 0; step < 60; step++)
                {
                    CaseUpdate.Invoke(director.ActiveCase, null);
                    director.Tick(0.05f);
                    if (director.AccentLight.intensity > 0f)
                    {
                        sawAccent = true;
                    }
                }

                Assert.That(sawAccent, Is.True,
                    "The rarity accent light must swell during the reveal.");
                Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Complete));
                Assert.That(completions, Is.EqualTo(1));
                Assert.That(director.AccentLight.color,
                    Is.EqualTo(GachaRevealRules.Signature(GachaRarity.Signature).LiningColor));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(host);
                UnityEngine.Object.DestroyImmediate(prize);
            }
        }

        [Test]
        public void DismissRestoresThePrizeNodeAndTearsDownEverything()
        {
            var host = new GameObject("director-host");
            var originalParent = new GameObject("original-parent");
            GameObject prize = GameObject.CreatePrimitive(PrimitiveType.Cube);
            try
            {
                prize.transform.SetParent(originalParent.transform, false);
                prize.transform.localPosition = new Vector3(1f, 2f, 3f);

                var director = host.AddComponent<GachaRevealDirector>();
                director.Begin(GachaRarity.Refined, GachaPrizeKind.ToySkin, prize.transform);
                Assert.That(prize.transform.parent, Is.Not.EqualTo(originalParent.transform),
                    "The case must have adopted the prize for the reveal.");

                director.Dismiss();
                Assert.That(prize == null, Is.False, "Dismiss must never destroy the prize.");
                Assert.That(prize.transform.parent, Is.EqualTo(originalParent.transform));
                Assert.That(prize.transform.localPosition,
                    Is.EqualTo(new Vector3(1f, 2f, 3f)));
                Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Idle));
                Assert.That(director.ActiveCase, Is.Null);
                Assert.That(director.AccentLight, Is.Null);
                Assert.That(host.GetComponentsInChildren<PremiumDisplayCase>(true),
                    Is.Empty);
                Assert.That(host.GetComponentsInChildren<Light>(true), Is.Empty);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(host);
                UnityEngine.Object.DestroyImmediate(originalParent);
                if (prize != null)
                {
                    UnityEngine.Object.DestroyImmediate(prize);
                }
            }
        }
    }
}
