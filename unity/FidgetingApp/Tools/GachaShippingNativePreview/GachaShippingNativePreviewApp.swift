import SwiftUI

@_cdecl("UnitySendMessage")
public func PreviewUnitySendMessage(
    _ objectName: UnsafePointer<CChar>,
    _ methodName: UnsafePointer<CChar>,
    _ message: UnsafePointer<CChar>) {}

// The preview app has no CodexIosDeviceMotion.mm; report "no motion
// hardware" so GachaPackMotionFeed falls back to idle / scripted.
@_cdecl("CodexIosDeviceMotionNativeUiStart")
public func PreviewDeviceMotionNativeUiStart() -> Int32 { 0 }

@_cdecl("CodexIosDeviceMotionNativeUiStop")
public func PreviewDeviceMotionNativeUiStop() {}

@_cdecl("CodexIosDeviceMotionRead")
public func PreviewDeviceMotionRead(
    _ roll: UnsafeMutablePointer<Double>,
    _ pitch: UnsafeMutablePointer<Double>,
    _ yaw: UnsafeMutablePointer<Double>,
    _ rotationRateX: UnsafeMutablePointer<Double>,
    _ rotationRateY: UnsafeMutablePointer<Double>,
    _ rotationRateZ: UnsafeMutablePointer<Double>,
    _ gravityX: UnsafeMutablePointer<Double>,
    _ gravityY: UnsafeMutablePointer<Double>,
    _ gravityZ: UnsafeMutablePointer<Double>,
    _ userAccelerationX: UnsafeMutablePointer<Double>,
    _ userAccelerationY: UnsafeMutablePointer<Double>,
    _ userAccelerationZ: UnsafeMutablePointer<Double>
) -> Int32 { 0 }

@main
struct GachaShippingNativePreviewApp: App {
    init() {
        ProductTypography.configureUIKitAppearance()
    }

    var body: some Scene {
        WindowGroup {
            if let tier = PackArcBandsPackPreview.requestedTier {
                PackArcBandsPackPreview(tier: tier)
            } else if ProcessInfo.processInfo.arguments.contains(
                "--pack-arc-bands-source-only"
            ) || ProcessInfo.processInfo.arguments.contains(where: {
                $0.hasPrefix("--pack-arc-bands-tier=")
            }) {
                PackArcBandsSourceOnlyPreview()
            } else if ProcessInfo.processInfo.arguments.contains(
                "--pack-tear-candidate-preview"
            ) || ProcessInfo.processInfo.arguments.contains(
                "--pack-arc-bands-preview"
            ) || ProcessInfo.processInfo.arguments.contains(where: {
                $0.hasPrefix("--pack-arc-bands-static=")
            }) {
                PackTearCandidatePreview()
            } else if ProcessInfo.processInfo.arguments.contains(
                "--pack-storefront-preview"
            ) {
                PackStorefrontPreview()
            } else {
                GachaShippingPreviewHost()
            }
        }
    }
}

/// `--pack-arc-bands-source-only` renders the untinted source palette;
/// `--pack-arc-bands-tier=<rawValue>` renders one Pack tier's colourway
/// through the same shipping component.
private struct PackArcBandsSourceOnlyPreview: View {
    private var tier: GachaPackTier? {
        guard let argument = ProcessInfo.processInfo.arguments.first(where: {
            $0.hasPrefix("--pack-arc-bands-tier=")
        }), let rawValue = argument.split(separator: "=").last else {
            return nil
        }
        return GachaPackTier(rawValue: String(rawValue))
    }

    var body: some View {
        ProductPackArcBandsBackdrop(
            intensity: 1,
            colourway: tier.map {
                GachaPackArcBackdropRules.Colourway.forTier($0)
            } ?? .source)
            .ignoresSafeArea()
            .productDesignSystem()
    }
}

/// `--pack-arc-bands-pack=<rawValue>`: one Pack's sealed artwork and caption
/// over its own colourway, at the shipping tear-stage size and position.
private struct PackArcBandsPackPreview: View {
    let tier: GachaPackTier

    static var requestedTier: GachaPackTier? {
        guard let argument = ProcessInfo.processInfo.arguments.first(where: {
            $0.hasPrefix("--pack-arc-bands-pack=")
        }), let rawValue = argument.split(separator: "=").last else {
            return nil
        }
        return GachaPackTier(rawValue: String(rawValue))
    }

    var body: some View {
        ZStack {
            ProductPackArcBandsBackdrop(
                intensity: 1,
                colourway: GachaPackArcBackdropRules.Colourway.forTier(tier))
                .ignoresSafeArea()

            GeometryReader { proxy in
                ProductPackSealedArtwork(
                    bodyAssetName: tier.bodyAssetName,
                    flapAssetName: tier.flapAssetName,
                    printAssetName: tier.printAssetName)
                    .scaledToFit()
                    .frame(
                        width: GachaPackOpeningRules.artworkWidthPoints,
                        height: GachaPackOpeningRules.artworkHeightPoints)
                    .modifier(ProductPackIdleFloat(
                        active: true,
                        reference: Date(),
                        settledAt: nil,
                        sheenMaskAssetName: tier.foilAssetName))
                    .position(
                        x: proxy.size.width * 0.5,
                        y: proxy.size.height
                            * GachaPackHandoffRules.stagePackCenterYFraction)
            }

            VStack {
                Spacer(minLength: 0)
                ProductPackTierCaption(
                    title: tier.storefrontPriceLabel,
                    detail: tier.storefrontOddsLine,
                    accent: tier.storefrontAccent)
                    .padding(.horizontal, FidgetUITokens.Spacing.section)
                    .padding(.bottom, FidgetUITokens.Spacing.section)
            }
        }
        .productDesignSystem()
    }
}

private struct PackStorefrontPreview: View {
    @State private var selectedPack = GachaPackTier.standard

    var body: some View {
        ZStack {
            ProductPackHueBackdrop(accent: selectedPack.storefrontAccent)
                .ignoresSafeArea()

            VStack(spacing: FidgetUITokens.Spacing.section) {
                ProductScreenHeading(
                    title: selectedPack.title,
                    subtitle: selectedPack.storefrontOddsLine,
                    centered: true,
                    titleStyle: .title2,
                    subtitleStyle: .footnote)
                    .padding(.top, FidgetUITokens.Spacing.section)

                ProductPackSealedArtwork(
                    bodyAssetName: selectedPack.bodyAssetName,
                    flapAssetName: selectedPack.flapAssetName,
                    printAssetName: selectedPack.printAssetName)
                    .scaledToFit()
                    .frame(width: 224, height: 330)

                ProductPackTierCaption(
                    title: selectedPack.storefrontPriceLabel,
                    detail: "一张抽取券 · 余 0 张",
                    accent: .white)

                Spacer(minLength: 0)
            }
            .padding(.horizontal, FidgetUITokens.Spacing.section)
        }
        .productDesignSystem()
    }
}

private struct PackTearCandidatePreview: View {
    @State private var tearProgress = 0.0
    @State private var seamLightStrength = 0.0
    @State private var releasePulseStrength = 0.0
    @State private var retreatProgress = 0.0

    private var staticTearProgress: Double? {
        guard let argument = ProcessInfo.processInfo.arguments.first(where: {
            $0.hasPrefix("--pack-arc-bands-static=")
        }) else { return nil }
        switch argument.split(separator: "=").last {
        case "sealed": return 0
        case "partial": return GachaPackOpeningRules.tearCommitProgress * 0.5
        case "commit": return GachaPackOpeningRules.tearCommitProgress
        case "faded": return 1
        default: return nil
        }
    }

    var body: some View {
        ZStack {
            Color.black
                .ignoresSafeArea()

            ProductPackArcBandsBackdrop(
                intensity: GachaPackArcBackdropRules.visibility(
                    tearProgress: tearProgress,
                    stageEligible: true))
                .ignoresSafeArea()

            ProductPackTearRevealLayer(
                bodyAssetName: GachaPackTier.standard.bodyAssetName,
                flapAssetName: GachaPackTier.standard.flapAssetName,
                tearProgress: tearProgress,
                seamLightStrength: seamLightStrength,
                releasePulseStrength: releasePulseStrength,
                liveCaseReady: false,
                retreatProgress: retreatProgress,
                printAssetName: GachaPackTier.standard.printAssetName,
                interiorTier: .standard)
        }
        .productDesignSystem()
        .onAppear {
            if let progress = staticTearProgress {
                tearProgress = progress
                seamLightStrength = GachaPackOpeningRules.seamLightStrength(
                    progress: progress,
                    gestureActive: progress > 0,
                    handoffActive: false,
                    retreatProgress: 0)
                return
            }
            Task { @MainActor in
                try? await Task.sleep(nanoseconds: 600_000_000)
                playOnce()
            }
        }
    }

    private func playOnce() {
        withAnimation(.linear(
            duration: GachaPackHandoffRules.nativeHybridTearDurationSeconds)) {
            tearProgress = GachaPackOpeningRules.tearCommitProgress
            seamLightStrength = 1
        }
        Task { @MainActor in
            try? await Task.sleep(nanoseconds: UInt64(
                (GachaPackHandoffRules.nativeHybridTearDurationSeconds
                    + 0.04) * 1_000_000_000))
            // Linear drive: the lid pose smoothsteps internally, and a second
            // easing on top reads as a jump cut at commit.
            withAnimation(.linear(
                duration: GachaPackOpeningRules.flapExitDurationSeconds)) {
                tearProgress = 1
                seamLightStrength = 0
            }
            withAnimation(.easeOut(
                duration: GachaPackOpeningRules.releasePulseRiseSeconds)) {
                releasePulseStrength = 1
            }
            try? await Task.sleep(nanoseconds: UInt64(
                GachaPackOpeningRules.releasePulsePeakSeconds
                    * 1_000_000_000))
            withAnimation(.easeOut(
                duration: GachaPackOpeningRules.releasePulseDurationSeconds
                    - GachaPackOpeningRules.releasePulsePeakSeconds)) {
                releasePulseStrength = 0
            }
            try? await Task.sleep(nanoseconds: UInt64(
                (GachaPackOpeningRules.flapExitDurationSeconds
                    - GachaPackOpeningRules.releasePulsePeakSeconds)
                    * 1_000_000_000))
            withAnimation(.easeIn(
                duration: GachaPackHandoffRules
                    .nativeHybridPackDepartureDurationSeconds)) {
                retreatProgress = 1
            }
        }
    }
}

private struct GachaShippingPreviewHost: View {
    @State private var showingStore = true

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            Button("打开机巧工坊") { showingStore = true }
                .foregroundColor(.black)
                .padding(.horizontal, 22)
                .frame(height: 52)
                .background(Color.white, in: RoundedRectangle(cornerRadius: 17))
        }
        .sheet(isPresented: $showingStore) {
            GachaStoreView()
        }
        .onAppear {
            GachaStoreModel.shared.ingest(
                catalog: Self.catalog,
                snapshot: Self.snapshot,
                receipt: "")
            if ProcessInfo.processInfo.arguments.contains("--preview-reveal") {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.65) {
                    GachaStoreModel.shared.ingest(
                        catalog: "",
                        snapshot: "",
                        receipt: Self.receipt)
                }
            }
        }
    }

    private static let catalog = """
    series\tlaunch-series\t启航系列\t0.70\t0.24\t0.05\t0.01
    prize\tblue-steel\tlaunch-series\t1\t0\t蓝钢冲刷
    prize\tcopper-strata\tlaunch-series\t2\t0\t铜层岩理
    prize\taurora-vein\tlaunch-series\t3\t0\t极光矿脉
    prize\tmechanical-mark\tlaunch-series\t0\t1\t机巧标记
    prize\tgraphite-base\tlaunch-series\t1\t2\t石墨展示底座
    """

    private static let snapshot = """
    wallet\t8\t2480
    series-state\tlaunch-series\t18\t42\t24\t64
    owned\tblue-steel|mechanical-mark
    """

    private static let receipt = """
    result\tok
    row\taurora-vein\t极光矿脉\t3\t0\t1\t0\t0\t0\t0
    """
}

private extension GachaPackTier {
    var storefrontAccent: Color {
        let rgb = storefrontAccentRGB
        return Color(red: rgb.red, green: rgb.green, blue: rgb.blue)
    }
}
