using System;
using System.Collections.Generic;
using FidgetingApp.Product.Gacha;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class GachaInternalDeterministicSequenceTests
    {
#if FIDGET_GACHA_INTERNAL_UNLIMITED
        private const string CursorPrefix =
            "fidgeting.gacha.internal-sequence-tests.v2.";

        private sealed class SentinelRandom : IGachaRandom
        {
            public double NextDouble()
            {
                return 0.777d;
            }
        }

        [TearDown]
        public void TearDown()
        {
            new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                CursorPrefix).DeleteAllForTests();
            PlayerPrefs.Save();
        }

        [Test]
        public void MissingOrInvalidLaunchArgumentKeepsNormalRandomSource()
        {
            var fallback = new SentinelRandom();
            Assert.That(
                GachaInternalUnlimitedRuntimeFactory.ResolveRandom(
                    Array.Empty<string>(),
                    fallback),
                Is.SameAs(fallback));
            Assert.That(
                GachaInternalUnlimitedRuntimeFactory.ResolveRandom(
                    new[] { "--fidget-gacha-sequence", "unknown" },
                    fallback),
                Is.SameAs(fallback));
        }

        [Test]
        public void ExplicitCatalogEightArgumentYieldsEveryPrizeInStableCatalogOrder()
        {
            Assert.That(
                GachaInternalUnlimitedRuntimeFactory.TryCreateDeterministicRandom(
                    new[] { "--fidget-gacha-sequence=catalog8" },
                    out IGachaRandom random),
                Is.True);

            GachaSeriesDefinition series =
                GachaCatalog.ResolveSeries(GachaCatalog.LaunchSeriesId);
            var pity = new GachaPityState();
            var actual = new List<string>();
            for (int index = 0; index < series.Prizes.Count; index++)
            {
                actual.Add(GachaDrawEngine.Draw(series, ref pity, random).PrizeId);
            }

            var expected = new List<string>();
            for (int index = 0; index < series.Prizes.Count; index++)
            {
                expected.Add(series.Prizes[index].Id);
            }

            Assert.That(actual, Is.EqualTo(expected));
        }

        [Test]
        public void PairFormLaunchArgumentAlsoEnablesCatalogEight()
        {
            Assert.That(
                GachaInternalUnlimitedRuntimeFactory.TryCreateDeterministicRandom(
                    new[] { "--fidget-gacha-sequence", "catalog8" },
                    out IGachaRandom random),
                Is.True);
            Assert.That(random, Is.Not.Null);
        }

        [Test]
        public void FactoryResumesCatalogCursorFromCommittedDrawCountAfterRestart()
        {
            CleanCursorPrefix();
            string[] arguments = { "--fidget-gacha-sequence", "catalog8" };
            GachaSeriesDefinition series =
                GachaCatalog.ResolveSeries(GachaCatalog.LaunchSeriesId);
            GachaInventoryRuntime first =
                GachaInternalUnlimitedRuntimeFactory.Create(arguments, CursorPrefix);
            GachaTransactionResult drawA = Prepare(first, "cursor-a");
            Assert.That(drawA.Receipt.Rows[0].Outcome.PrizeId,
                Is.EqualTo(series.Prizes[0].Id));
            Accept(first, "cursor-a");

            GachaInventoryRuntime restarted =
                GachaInternalUnlimitedRuntimeFactory.Create(arguments, CursorPrefix);
            GachaTransactionResult drawB = Prepare(restarted, "cursor-b");
            Assert.That(drawB.Receipt.Rows[0].Outcome.PrizeId,
                Is.EqualTo(series.Prizes[1].Id),
                "Committed draw count must advance catalog8 after process restart.");
        }

        [Test]
        public void FactoryCountsRestoredPendingSoAckThenNextDrawDoesNotRepeat()
        {
            CleanCursorPrefix();
            string[] arguments = { "--fidget-gacha-sequence=catalog8" };
            GachaSeriesDefinition series =
                GachaCatalog.ResolveSeries(GachaCatalog.LaunchSeriesId);
            GachaInventoryRuntime first =
                GachaInternalUnlimitedRuntimeFactory.Create(arguments, CursorPrefix);
            Prepare(first, "pending-a");
            Accept(first, "pending-a");
            GachaTransactionResult pendingB = Prepare(first, "pending-b");
            Assert.That(pendingB.Receipt.Rows[0].Outcome.PrizeId,
                Is.EqualTo(series.Prizes[1].Id));

            GachaInventoryRuntime restarted =
                GachaInternalUnlimitedRuntimeFactory.Create(arguments, CursorPrefix);
            GachaTransactionResult restoredB = restarted.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "pending-b");
            Assert.That(restoredB.Receipt.Rows[0].Outcome.PrizeId,
                Is.EqualTo(pendingB.Receipt.Rows[0].Outcome.PrizeId));
            Accept(restarted, "pending-b");

            GachaTransactionResult drawC = Prepare(restarted, "pending-c");
            Assert.That(drawC.Receipt.Rows[0].Outcome.PrizeId,
                Is.EqualTo(series.Prizes[2].Id),
                "Factory cursor must include the valid restored pending count.");
        }

        [Test]
        public void FactoryYieldsCatalogOrderAcrossEightCommitsAndPendingRestart()
        {
            CleanCursorPrefix();
            string[] arguments = { "--fidget-gacha-sequence", "catalog8" };
            GachaSeriesDefinition series =
                GachaCatalog.ResolveSeries(GachaCatalog.LaunchSeriesId);

            for (int index = 0; index < series.Prizes.Count; index++)
            {
                string requestId = "catalog-order-" + index;
                GachaInventoryRuntime runtime =
                    GachaInternalUnlimitedRuntimeFactory.Create(arguments, CursorPrefix);
                GachaTransactionResult prepared = Prepare(runtime, requestId);
                Assert.That(prepared.Success, Is.True);
                Assert.That(
                    prepared.Receipt.Rows[0].Outcome.PrizeId,
                    Is.EqualTo(series.Prizes[index].Id),
                    $"Committed draw {index + 1} must follow GachaCatalog order.");

                // Exercise a real pending recovery in the middle of the same
                // eight-draw sequence. The restored receipt must not consume
                // another catalog slot.
                if (index == 3)
                {
                    runtime = GachaInternalUnlimitedRuntimeFactory.Create(
                        arguments,
                        CursorPrefix);
                    GachaTransactionResult restored = Prepare(runtime, requestId);
                    Assert.That(restored.Success, Is.True);
                    Assert.That(
                        restored.Receipt.Rows[0].Outcome.PrizeId,
                        Is.EqualTo(series.Prizes[index].Id));
                }

                Accept(runtime, requestId);
            }

            GachaInventoryRuntime wrapped =
                GachaInternalUnlimitedRuntimeFactory.Create(arguments, CursorPrefix);
            GachaTransactionResult ninth = Prepare(wrapped, "catalog-order-wrap");
            Assert.That(ninth.Receipt.Rows[0].Outcome.PrizeId,
                Is.EqualTo(series.Prizes[0].Id),
                "The internal coverage sequence must wrap only after all eight commits.");
        }

        private static void CleanCursorPrefix()
        {
            new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                CursorPrefix).DeleteAllForTests();
            PlayerPrefs.Save();
        }

        private static GachaTransactionResult Prepare(
            GachaInventoryRuntime runtime,
            string requestId)
        {
            return runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                requestId);
        }

        private static void Accept(GachaInventoryRuntime runtime, string requestId)
        {
            Assert.That(runtime.MarkRevealAwaitingAcceptance(requestId).Success, Is.True);
            Assert.That(runtime.AcknowledgePending(requestId).Success, Is.True);
        }
#else
        [Test]
        public void ProductionAssemblyDoesNotExposeDeterministicSequenceHook()
        {
            Type hook = typeof(GachaInventoryRuntime).Assembly.GetType(
                "FidgetingApp.Product.Gacha.GachaInternalUnlimitedRuntimeFactory",
                false);
            Assert.That(hook, Is.Null,
                "Production compilation must entirely exclude the deterministic hook.");
        }
#endif
    }
}
