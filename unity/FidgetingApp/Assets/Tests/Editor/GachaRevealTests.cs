using System;
using System.Collections.Generic;
using System.Linq;
using FidgetingApp.DisplayCase;
using FidgetingApp.Product.Gacha;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class GachaRevealTests
    {
        [Test]
        public void EveryLaunchPrizeHasOneStableRealPresentation()
        {
            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(
                GachaCatalog.LaunchSeriesId);
            Assert.That(series, Is.Not.Null);
            Assert.That(series.Prizes.Count, Is.EqualTo(8));
            Assert.That(GachaPrizePresentationResolver.Descriptors.Count,
                Is.EqualTo(8));
            Assert.That(
                GachaPrizePresentationResolver.Descriptors
                    .Select(item => item.ContentReference),
                Is.Unique);

            foreach (GachaPrizeDefinition prize in series.Prizes)
            {
                Assert.That(GachaPrizePresentationResolver.TryResolveDescriptor(
                    prize.ContentReference,
                    out GachaPrizePresentationDescriptor descriptor),
                    Is.True,
                    prize.ContentReference);
                Assert.That(descriptor.DisplayName, Is.EqualTo(prize.DisplayName));
                Assert.That(descriptor.CapsulePreset,
                    Is.EqualTo(PremiumDisplayCaseCapsulePreset.CollectorSlabCompact));
                Assert.That(descriptor.ContentOptions.IdleRotationEnabled, Is.True,
                    "Gacha prizes float once revealed instead of holding still.");
                Assert.That(descriptor.ContentOptions.InitialEulerAngles,
                    Is.EqualTo(PremiumDisplayCaseProductProfiles
                        .SharedContentOptions.InitialEulerAngles));
            }
        }

        [Test]
        public void ResolvedPresentationsAreVisibleRendererOnlyAndDisposable()
        {
            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(
                GachaCatalog.LaunchSeriesId);
            foreach (GachaPrizeDefinition prize in series.Prizes)
            {
                GachaResolvedPrizePresentation presentation = null;
                try
                {
                    presentation = GachaPrizePresentationResolver.Resolve(prize);
                    Assert.That(presentation.Root, Is.Not.Null, prize.Id);
                    Assert.That(presentation.Renderers, Is.Not.Empty, prize.Id);
                    Assert.That(GachaPrizePresentationResolver.IsRendererOnly(
                        presentation.Root), Is.True, prize.Id);
                    Assert.That(presentation.Root
                        .GetComponentsInChildren<Rigidbody>(true), Is.Empty, prize.Id);
                    Assert.That(presentation.Root
                        .GetComponentsInChildren<Collider>(true), Is.Empty, prize.Id);
                    Assert.That(presentation.Root
                        .GetComponentsInChildren<AudioSource>(true), Is.Empty, prize.Id);
                }
                finally
                {
                    GameObject root = presentation?.Root;
                    presentation?.Dispose();
                    Assert.That(root == null, Is.True,
                        prize.Id + " must release its presentation root.");
                }
            }
        }

        [Test]
        public void SkinPrizesUseTheDedicatedThreeBladeDisplayModel()
        {
            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(
                GachaCatalog.LaunchSeriesId);
            foreach (GachaPrizeDefinition prize in series.Prizes.Where(
                         item => item.Kind == GachaPrizeKind.ToySkin))
            {
                using GachaResolvedPrizePresentation presentation =
                    GachaPrizePresentationResolver.Resolve(prize);
                Assert.That(presentation.Descriptor.UsesThreeBladeDisplayModel,
                    Is.True, prize.Id);
                Assert.That(presentation.Root.transform
                    .Find("RotorVisual"), Is.Not.Null, prize.Id);
                Assert.That(presentation.Renderers.Length,
                    Is.GreaterThanOrEqualTo(8), prize.Id);
            }
        }

        [Test]
        public void PrizeVisualFamiliesHaveReadableDistinctStructure()
        {
            using GachaResolvedPrizePresentation blue =
                GachaPrizePresentationResolver.Resolve(
                    GachaCatalog.ResolvePrize(
                        "canyon-ref-bluesteel-wash").Value);
            using GachaResolvedPrizePresentation copper =
                GachaPrizePresentationResolver.Resolve(
                    GachaCatalog.ResolvePrize(
                        "canyon-sig-copper-strata").Value);
            using GachaResolvedPrizePresentation aurora =
                GachaPrizePresentationResolver.Resolve(
                    GachaCatalog.ResolvePrize(
                        "canyon-heir-aurora-vein").Value);
            using GachaResolvedPrizePresentation slate =
                GachaPrizePresentationResolver.Resolve(
                    GachaCatalog.ResolvePrize(
                        "canyon-std-slate-lining").Value);
            using GachaResolvedPrizePresentation basalt =
                GachaPrizePresentationResolver.Resolve(
                    GachaCatalog.ResolvePrize(
                        "canyon-std-basalt-base").Value);
            using GachaResolvedPrizePresentation dusk =
                GachaPrizePresentationResolver.Resolve(
                    GachaCatalog.ResolvePrize(
                        "canyon-ref-ridge-tint").Value);

            Assert.That(DescendantsNamed(
                blue.Root,
                "BlueSteelSkinSurfacePattern_").Count,
                Is.EqualTo(9));
            Assert.That(DescendantsNamed(
                copper.Root,
                "CopperStrataSkinSurfacePattern_").Count,
                Is.EqualTo(12));
            Assert.That(DescendantsNamed(
                aurora.Root,
                "AuroraVeinSkinSurfacePattern_").Count,
                Is.EqualTo(9));
            Assert.That(DescendantsNamed(
                aurora.Root,
                "AuroraVeinBranch_").Count,
                Is.EqualTo(3));

            Assert.That(slate.Root.transform.Find("SlateBeveledFace"),
                Is.Not.Null);
            Assert.That(basalt.Root.transform.Find("BasaltPedestalFoot"),
                Is.Not.Null);
            Assert.That(basalt.Root.transform.Find("BasaltPedestalRiser"),
                Is.Not.Null);
            Assert.That(basalt.Root.transform.Find("BasaltPedestalTopDeck"),
                Is.Not.Null);
            Assert.That(DescendantsNamed(dusk.Root, "DuskGlassEdge_").Count,
                Is.EqualTo(4));
            Assert.That(DescendantsNamed(
                dusk.Root,
                "DuskGlassReflection_").Count,
                Is.EqualTo(3));

            Material glass = dusk.Root.transform
                .Find("DuskGlassMaterialSample")
                .GetComponent<Renderer>()
                .sharedMaterial;
            Assert.That(glass.GetColor("_BaseColor").a,
                Is.LessThan(0.5f),
                "The environment tint must read as a transparent glass sample.");
            Assert.That(glass.renderQueue,
                Is.GreaterThanOrEqualTo(3000));
        }

        [Test]
        public void StickerPrizesUsePhysicalStableArtworkNotLabels()
        {
            GachaPrizeDefinition strata = GachaCatalog.ResolvePrize(
                "canyon-std-strata-sticker").Value;
            GachaPrizeDefinition dust = GachaCatalog.ResolvePrize(
                "canyon-std-dust-sticker").Value;
            using GachaResolvedPrizePresentation strataPresentation =
                GachaPrizePresentationResolver.Resolve(strata);
            using GachaResolvedPrizePresentation dustPresentation =
                GachaPrizePresentationResolver.Resolve(dust);

            Assert.That(strataPresentation.Descriptor.IsPhysicalArtwork, Is.True);
            Assert.That(dustPresentation.Descriptor.IsPhysicalArtwork, Is.True);
            Assert.That(DescendantsNamed(
                strataPresentation.Root,
                "StrataArtwork_").Count,
                Is.EqualTo(9));
            Assert.That(DescendantsNamed(
                dustPresentation.Root,
                "MineralDustArtwork_").Count,
                Is.EqualTo(28));
            Assert.That(strataPresentation.Root
                .GetComponentsInChildren<TextMesh>(true), Is.Empty);
            Assert.That(dustPresentation.Root
                .GetComponentsInChildren<TextMesh>(true), Is.Empty);
        }

        [Test]
        public void EveryPrizeKindUsesTheApprovedMagneticSlideDeepSquareCase()
        {
            foreach (GachaPrizeKind kind in Enum.GetValues(typeof(GachaPrizeKind)))
            {
                Assert.That(GachaRevealRules.CapsulePresetFor(kind),
                    Is.EqualTo(PremiumDisplayCaseCapsulePreset.CollectorSlabCompact),
                    kind.ToString());
            }
            Assert.That(GachaRevealRules.TotalRevealSeconds(GachaRarity.Standard),
                Is.EqualTo(GachaRevealTimeline.TotalSeconds).Within(0.000001f));
            Assert.That(GachaRevealRules.TotalRevealSeconds(GachaRarity.Heirloom),
                Is.EqualTo(GachaRevealTimeline.TotalSeconds).Within(0.000001f),
                "Rarity may tint the reveal but must not fork the timeline.");
        }

        [Test]
        public void GachaRevealSettlesOnTheReadableCaseWithoutForkingTheTimeline()
        {
            Assert.That(GachaRevealTimeline.TotalSeconds,
                Is.EqualTo(GachaRevealTimeline.ReadableEnd).Within(0.000001f));
            Assert.That(GachaRevealPrizePresentation
                .ShowsFrontIdentification(GachaRevealPhase.Back), Is.False);
            Assert.That(GachaRevealPrizePresentation
                .ShowsFrontIdentification(GachaRevealPhase.Front), Is.True);
            Assert.That(GachaRevealPrizePresentation
                .ShowsFrontIdentification(GachaRevealPhase.Readable), Is.True);
            Assert.That(GachaRevealPrizePresentation
                .ShowsFrontIdentification(GachaRevealPhase.Complete), Is.True);
        }

        [Test]
        public void PrepareDoesNotStartAndStartPublishesStrictPhaseOrder()
        {
            var host = new GameObject("director-host");
            try
            {
                GachaPrizeDefinition prize = GachaCatalog.ResolvePrize(
                    "canyon-sig-copper-strata").Value;
                var outcome = new GachaDrawOutcome(
                    prize.Id,
                    prize.Rarity,
                    false,
                    false,
                    false);
                var director = host.AddComponent<GachaRevealDirector>();
                var phases = new List<GachaRevealPhase>();
                int completions = 0;
                director.phaseChanged += phases.Add;
                director.revealCompleted += () => completions++;

                Assert.That(director.Prepare(outcome), Is.True,
                    director.FailureReason);
                Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Idle));
                Assert.That(director.ActiveCase.gameObject.activeSelf, Is.False);
                Assert.That(director.ActivePrize.parent,
                    Is.Not.EqualTo(host.transform),
                    "Preparing an inactive case must keep the prize attached to contentSlot.");
                Assert.That(director.StartReveal(), Is.True);
                Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Back));

                director.Tick(GachaRevealTimeline.TotalSeconds + 1f);
                Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Complete));
                Assert.That(phases, Is.EqualTo(new[]
                {
                    GachaRevealPhase.Back,
                    GachaRevealPhase.Front,
                    GachaRevealPhase.Readable,
                    GachaRevealPhase.Complete
                }));
                Assert.That(completions, Is.EqualTo(1));
                director.Tick(99f);
                Assert.That(completions, Is.EqualTo(1));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(host);
            }
        }

        [Test]
        public void BackHidesFrontLabelsAndCaseAndPrizeStayTogetherThroughComplete()
        {
            var host = new GameObject("director-host");
            try
            {
                GachaPrizeDefinition prize = GachaCatalog.ResolvePrize(
                    "canyon-ref-ridge-tint").Value;
                var director = host.AddComponent<GachaRevealDirector>();
                Assert.That(director.Prepare(prize), Is.True,
                    director.FailureReason);
                Transform fitRoot = director.ActivePrize.parent;
                Vector3 fittedScale = fitRoot.localScale;
                Vector3 fittedPosition = fitRoot.localPosition;
                Assert.That(director.StartReveal(), Is.True);

                Renderer[] identification = director.ActiveCase
                    .GetComponentsInChildren<Renderer>(true)
                    .Where(renderer => renderer.name == "CollectorTierAndLevel"
                        || renderer.name == "CollectorProductName"
                        || renderer.name == "CollectorEdition"
                        || renderer.name == "CollectorAcquiredDate"
                        || renderer.name == "Collector_LabelPaper"
                        || renderer.name == "Collector_RarityFoilBand")
                    .ToArray();
                Assert.That(identification, Is.Not.Empty);
                Assert.That(identification.All(renderer => !renderer.enabled),
                    Is.True,
                    "Back entry must not expose upside-down front labels.");

                var prizeSet = new HashSet<Renderer>(director.ActivePrize
                    .GetComponentsInChildren<Renderer>(true));
                // The lid retracts off-frame once open (see
                // GachaBuild42ShippingCapture's IsTransientBoxLid) and gacha's
                // compact viewport scale shortens that escape distance enough
                // that it is explicitly disabled once retracted -- it is not
                // part of the settled shell this test is verifying.
                Renderer[] shellRenderers = director.ActiveCase
                    .GetComponentsInChildren<Renderer>(true)
                    .Where(renderer => !prizeSet.Contains(renderer)
                        && !IsUnderNamedAncestor(renderer.transform, "BoxLidRoot"))
                    .ToArray();
                Assert.That(shellRenderers, Is.Not.Empty);

                director.Tick(GachaRevealTimeline.TotalSeconds + 1f);

                Assert.That(director.Phase,
                    Is.EqualTo(GachaRevealPhase.Complete));
                Assert.That(identification.All(renderer => renderer.enabled),
                    Is.True,
                    "The front labels must be visible once the case settles.");
                Assert.That(shellRenderers.All(renderer => renderer.enabled),
                    Is.True,
                    "The case shell must remain on screen instead of dissolving.");
                Renderer[] prizeRenderers = director.ActivePrize
                    .GetComponentsInChildren<Renderer>(true);
                Assert.That(prizeRenderers, Is.Not.Empty);
                Assert.That(prizeRenderers.All(renderer => renderer.enabled),
                    Is.True);
                Assert.That(fitRoot.localScale, Is.EqualTo(fittedScale),
                    "The fitted prize must never be re-scaled after the reveal.");
                Assert.That(fitRoot.localPosition, Is.EqualTo(fittedPosition));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(host);
            }
        }

        [Test]
        public void DismissRestoresExternalPrizeWithoutDestroyingIt()
        {
            var host = new GameObject("director-host");
            var originalParent = new GameObject("original-parent");
            var prize = new GameObject("external-prize");
            prize.transform.SetParent(originalParent.transform, false);
            prize.transform.localPosition = new Vector3(1f, 2f, 3f);
            prize.AddComponent<MeshFilter>().sharedMesh = new Mesh();
            prize.AddComponent<MeshRenderer>();
            try
            {
                var director = host.AddComponent<GachaRevealDirector>();
                director.Begin(
                    GachaRarity.Refined,
                    GachaPrizeKind.ToySkin,
                    prize.transform);
                Assert.That(prize.transform.parent,
                    Is.Not.EqualTo(originalParent.transform));

                director.Dismiss();
                Assert.That(prize == null, Is.False);
                Assert.That(prize.transform.parent,
                    Is.EqualTo(originalParent.transform));
                Assert.That(prize.transform.localPosition,
                    Is.EqualTo(new Vector3(1f, 2f, 3f)));
                Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Idle));
                Assert.That(director.ActiveCase, Is.Null);
                Assert.That(director.ActivePrize, Is.Null);
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

        private static List<Transform> DescendantsNamed(
            GameObject root,
            string prefix)
        {
            return root.GetComponentsInChildren<Transform>(true)
                .Where(item => item.name.StartsWith(prefix, StringComparison.Ordinal))
                .ToList();
        }

        private static bool IsUnderNamedAncestor(Transform item, string name)
        {
            for (Transform cursor = item; cursor != null; cursor = cursor.parent)
            {
                if (cursor.name == name)
                {
                    return true;
                }
            }
            return false;
        }
    }
}
