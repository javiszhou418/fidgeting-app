using System;
using System.IO;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class GachaFanaticsCandidateTests
    {
        [Test]
        public void SharedTokensAndComponentsMatchThePendingFanaticsCandidate()
        {
            string components = ReadAsset("Plugins/iOS/FidgetProductUIComponents.swift");

            StringAssert.Contains("static let primaryActionHeight: CGFloat = 52", components);
            StringAssert.Contains("static let filterChipHeight: CGFloat = 32", components);
            StringAssert.Contains("static let statusTagHeight: CGFloat = 26", components);
            StringAssert.Contains("static let section: CGFloat = 16", components);
            StringAssert.Contains("static let pageInset: CGFloat = 20", components);
            StringAssert.Contains("static let sectionGroup: CGFloat = 24", components);
            StringAssert.DoesNotContain("static let section: CGFloat = 15", components);

            int primaryStart = components.IndexOf(
                "struct ProductPrimaryActionLabel", StringComparison.Ordinal);
            int primaryEnd = components.IndexOf(
                "struct ProductPrimaryActionButton", primaryStart, StringComparison.Ordinal);
            string primary = components.Substring(primaryStart, primaryEnd - primaryStart);
            StringAssert.Contains("cornerRadius: FidgetUITokens.Radius.pill", primary);
            StringAssert.Contains("Color.white.opacity", primary);
            StringAssert.DoesNotContain("accent.opacity", primary);
            StringAssert.DoesNotContain("Image(systemName:", primary);
            StringAssert.DoesNotContain("Label(title", primary);

            int filterStart = components.IndexOf(
                "struct ProductFilterChip", StringComparison.Ordinal);
            int filterEnd = components.IndexOf(
                "struct ProductStatusTag", filterStart, StringComparison.Ordinal);
            string filter = components.Substring(filterStart, filterEnd - filterStart);
            StringAssert.Contains("FidgetUITokens.Size.filterChipHeight", filter);
            StringAssert.Contains("FidgetUITokens.Size.minimumHitTarget", filter);
            StringAssert.Contains("Image(systemName: \"checkmark\")", filter);

            int statusStart = components.IndexOf(
                "struct ProductStatusTag", StringComparison.Ordinal);
            int statusEnd = components.IndexOf(
                "struct ProductSectionCard", statusStart, StringComparison.Ordinal);
            string status = components.Substring(statusStart, statusEnd - statusStart);
            StringAssert.Contains("FidgetUITokens.Size.statusTagHeight", status);
            StringAssert.DoesNotContain("Button(", status);

            foreach (string actionState in new[] {
                "case rest", "case loading(String)", "case disabledValue(String?)",
                "case success(String)", "case error(String)" })
            {
                StringAssert.Contains(actionState, components);
            }
            StringAssert.Contains("static var disabled: Self", components);
            StringAssert.Contains("static func disabled(reason: String) -> Self", components);
            StringAssert.Contains("return \"不可用，\\(reason)\"", components);
            StringAssert.Contains("static let pressedScale = 0.98", components);
            StringAssert.Contains("static let pressedDuration = 0.12", components);
        }

        [Test]
        public void SharedActionWrappersOwnTheSameStateAndPressedContract()
        {
            string components = ReadAsset("Plugins/iOS/FidgetProductUIComponents.swift");
            string overlay = ReadAsset("Plugins/iOS/CodexSwiftUIOverlay.swift");

            int primaryStart = components.IndexOf(
                "struct ProductPrimaryActionButton", StringComparison.Ordinal);
            int primaryEnd = components.IndexOf(
                "struct ProductActionLabel", primaryStart, StringComparison.Ordinal);
            string primary = components.Substring(primaryStart, primaryEnd - primaryStart);
            StringAssert.Contains(".buttonStyle(ProductActionButtonStyle())", primary);
            StringAssert.Contains(".disabled(state.disablesInteraction)", primary);

            int secondaryStart = components.IndexOf(
                "struct ProductSecondaryActionButton", StringComparison.Ordinal);
            int secondaryEnd = components.IndexOf(
                "struct ProductFilterChip", secondaryStart, StringComparison.Ordinal);
            string secondary = components.Substring(
                secondaryStart,
                secondaryEnd - secondaryStart);
            StringAssert.Contains("ProductActionLabel(", secondary);
            StringAssert.Contains(".buttonStyle(ProductActionButtonStyle())", secondary);
            StringAssert.Contains(".disabled(state.disablesInteraction)", secondary);

            StringAssert.Contains(
                ".disabled(reason: \"场景仍在加载\")",
                overlay);
            StringAssert.DoesNotContain("ProductPrimaryActionLabel(", overlay);
            StringAssert.Contains("ProductPrimaryActionButton(", overlay);
            StringAssert.Contains("ProductSecondaryActionButton(", overlay);
        }

        [Test]
        public void StorefrontUsesOneSingleLinePrimaryAndStaticTenDrawStatus()
        {
            string storefront = ReadAsset("Plugins/iOS/FidgetGachaStorefront.swift");

            StringAssert.Contains("ProductPrimaryActionButton(\n                title: \"单抽\"", storefront);
            StringAssert.Contains("ProductStatusTag(title: \"十抽后续开放\")", storefront);
            StringAssert.Contains("Text(\"消耗 1 张抽取券\")", storefront);
            StringAssert.Contains("Text(\"剩余 \\(model.tickets) 张\")", storefront);
            StringAssert.Contains("ProductFilterChip(\n                title: \"抽取 / 兑换\"", storefront);
            StringAssert.Contains("ProductFilterChip(title: \"概率与保底\")", storefront);
            StringAssert.DoesNotContain(".font(.system", storefront);
            StringAssert.DoesNotContain(".tracking(", storefront);
            StringAssert.DoesNotContain(".kerning(", storefront);

            int dockStart = storefront.IndexOf(
                "private func drawDock", StringComparison.Ordinal);
            int dockEnd = storefront.IndexOf(
                "private var singleDrawActionState", dockStart, StringComparison.Ordinal);
            string dock = storefront.Substring(dockStart, dockEnd - dockStart);
            int metadataIndex = dock.IndexOf("消耗 1 张抽取券", StringComparison.Ordinal);
            int primaryIndex = dock.IndexOf("ProductPrimaryActionButton", StringComparison.Ordinal);
            Assert.That(metadataIndex, Is.GreaterThanOrEqualTo(0));
            Assert.That(primaryIndex, Is.GreaterThan(metadataIndex));
            StringAssert.DoesNotContain("Button(\"十抽", dock);
        }

        [Test]
        public void GachaResultUsesTheSharedComponentLibraryWithoutAssemblyUi()
        {
            string overlay = ReadAsset("Plugins/iOS/CodexSwiftUIOverlay.swift");
            string components = ReadAsset("Plugins/iOS/FidgetProductUIComponents.swift");
            string rules = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "..",
                "..",
                "..",
                "AGENTS.md"));
            int viewStart = overlay.IndexOf(
                "private struct PremiumDisplayCaseExperienceView",
                StringComparison.Ordinal);
            int viewEnd = overlay.IndexOf(
                "#if DEBUG",
                viewStart,
                StringComparison.Ordinal);
            Assert.That(viewStart, Is.GreaterThanOrEqualTo(0));
            Assert.That(viewEnd, Is.GreaterThan(viewStart));
            string view = overlay.Substring(viewStart, viewEnd - viewStart);

            StringAssert.Contains("ProductBottomActionDock", view);
            StringAssert.Contains("ProductScreenHeading(", view);
            StringAssert.Contains("ProductStatusTag(", view);
            StringAssert.Contains("ProductPrimaryActionButton(", view);
            StringAssert.Contains("title: \"收下\"", view);
            StringAssert.Contains("state: acceptingGachaResult", view);
            StringAssert.Contains(".productDesignSystem()", view);
            StringAssert.DoesNotContain(".font(.system", view);
            StringAssert.DoesNotContain(".tracking(", view);
            StringAssert.DoesNotContain(".kerning(", view);
            StringAssert.DoesNotContain(".ultraThinMaterial", view);
            StringAssert.DoesNotContain(".stroke(", view);
            StringAssert.DoesNotContain("ASSEMBLY", view);
            StringAssert.DoesNotContain(
                "SetDisplayCaseExplodedProgressFromNativeUi",
                view);
            StringAssert.Contains("struct ProductBottomActionDock", components);
            StringAssert.Contains("## Shipping UI component-library gate", rules);
        }

        [Test]
        public void DebugAutoDrawHookCallsProductionPathOnceAndCannotShipInRelease()
        {
            string storefront = ReadAsset("Plugins/iOS/FidgetGachaStorefront.swift");
            const string argument = "--preview-auto-single-draw";
            int argumentIndex = storefront.IndexOf(argument, StringComparison.Ordinal);
            Assert.That(argumentIndex, Is.GreaterThanOrEqualTo(0));

            int blockStart = storefront.LastIndexOf("#if DEBUG", argumentIndex, StringComparison.Ordinal);
            int blockEnd = storefront.IndexOf("#endif", argumentIndex, StringComparison.Ordinal);
            Assert.That(blockStart, Is.GreaterThanOrEqualTo(0));
            Assert.That(blockEnd, Is.GreaterThan(argumentIndex));
            string debugBlock = storefront.Substring(blockStart, blockEnd - blockStart);

            StringAssert.Contains("didRunDebugPreviewSingleDraw", debugBlock);
            StringAssert.Contains("startSingleDraw(series)", debugBlock);
            StringAssert.DoesNotContain("singleDrawGate.begin", debugBlock);
            StringAssert.DoesNotContain("model.draw(", debugBlock);
            Assert.That(Count(debugBlock, "startSingleDraw(series)"), Is.EqualTo(1));
        }

        [Test]
        public void DebugAutoOpenKeepsASealedBeatThenCallsProductionCommit()
        {
            string storefront = ReadAsset("Plugins/iOS/FidgetGachaStorefront.swift");
            const string argument = "--preview-auto-open-pack";
            int argumentIndex = storefront.IndexOf(argument, StringComparison.Ordinal);
            Assert.That(argumentIndex, Is.GreaterThanOrEqualTo(0));

            int blockStart = storefront.LastIndexOf("#if DEBUG", argumentIndex, StringComparison.Ordinal);
            int blockEnd = storefront.IndexOf("#endif", argumentIndex, StringComparison.Ordinal);
            string debugBlock = storefront.Substring(blockStart, blockEnd - blockStart);

            StringAssert.Contains("Task.sleep(nanoseconds: 520_000_000)", debugBlock);
            StringAssert.Contains("Task.sleep(nanoseconds: 420_000_000)", debugBlock);
            StringAssert.Contains("guard !Task.isCancelled", debugBlock);
            StringAssert.Contains("releaseTear(at: 0.55)", debugBlock);
            StringAssert.Contains("releaseTear(at: 0.75)", debugBlock);
        }

        [Test]
        public void PendingOverlaysIsolateTheUnderlyingStorefrontAndFitNarrowPhones()
        {
            string storefront = ReadAsset("Plugins/iOS/FidgetGachaStorefront.swift");
            string rive = ReadAsset("Plugins/iOS/FidgetGachaRivePresentation.swift");

            StringAssert.Contains(".accessibilityHidden(", storefront);
            StringAssert.Contains(".accessibilityAddTraits(.isModal)", storefront);
            StringAssert.Contains(
                ".frame(maxWidth: .infinity, maxHeight: .infinity)",
                rive);
            StringAssert.DoesNotContain(".frame(width: 330, height: 390)\n            .clipped()", rive);
        }

        [Test]
        public void PackCarouselUsesSelectedEmphasisShallowOutwardArcAndFixedReleaseThreshold()
        {
            string storefront = ReadAsset("Plugins/iOS/FidgetGachaStorefront.swift");
            string rules = ReadAsset("Plugins/iOS/FidgetGachaPackPresentation.swift");

            StringAssert.Contains(
                "static let itemSpacingPoints: Double = 160",
                rules);
            StringAssert.Contains(
                "static let selectionCommitPoints: Double = 56",
                rules);
            StringAssert.Contains(
                "static let unselectedPackScale: Double = 0.66",
                rules);
            StringAssert.Contains(
                "static let selectedPackScale: Double = 0.70",
                rules);
            StringAssert.Contains(
                "GachaPackCarouselRules.packScale(",
                storefront);
            StringAssert.Contains(
                "static let maximumSideDropPoints: Double = 16",
                rules);
            StringAssert.Contains(
                "static let maximumSideTiltDegrees: Double = 3.5",
                rules);
            StringAssert.Contains("GachaPackCarouselRules.continuousPosition", storefront);
            StringAssert.Contains("GachaPackCarouselRules.verticalOffset", storefront);
            StringAssert.Contains("GachaPackCarouselRules.tiltDegrees", storefront);
            StringAssert.Contains("GachaPackCarouselRules.nextIndex", storefront);
            StringAssert.Contains("value.translation.width", storefront);
            StringAssert.Contains(
                "continuousPosition * maximumSideTiltDegrees",
                rules);
            StringAssert.DoesNotContain(
                "-continuousPosition * maximumSideTiltDegrees",
                rules);
            StringAssert.DoesNotContain(
                "index == selectedIndex ? 0.66 : 0.48",
                storefront);
            StringAssert.DoesNotContain("arc * arc * 27", storefront);
            StringAssert.DoesNotContain(
                "value.predictedEndTranslation.width",
                storefront);
        }

        private static int Count(string source, string value)
        {
            int count = 0;
            int index = 0;
            while ((index = source.IndexOf(value, index, StringComparison.Ordinal)) >= 0)
            {
                count++;
                index += value.Length;
            }
            return count;
        }

        private static string ReadAsset(string relativePath)
        {
            return File.ReadAllText(Path.Combine(Application.dataPath, relativePath));
        }
    }
}
