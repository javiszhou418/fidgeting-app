# Gacha Pack V7 Shipping Native Preview

Status: shipping visual approval pending; not installed on iPhone.

This preview is compiled from the shipping Swift sources:

- `Assets/Plugins/iOS/FidgetGachaPackPresentation.swift`
- `Assets/Plugins/iOS/FidgetGachaStore.swift`
- `Assets/Plugins/iOS/FidgetGachaStorefront.swift`
- `Assets/Plugins/iOS/FidgetProductUIComponents.swift`
- `Assets/Plugins/iOS/FidgetStoreKit.swift`

`Tools/GachaShippingNativePreview/capture-pack-v7.sh` builds those sources with the 12 production Pack layers in `Assets/Plugins/iOS/GachaPacks/` and captures them from an iPhone 17 Pro Simulator. The four frames show the real storefront Pack entry, sealed Pack, 68% tear position, and handoff into the existing collection-case reveal.

Contact sheet: `gacha-pack-v7-shipping-contact-sheet.png` (`1200 × 652`, SHA-256 `f96ce7a8a703418e7064cf8371d090d0a5772b82e5a3ffadb0793c5c4dead263`).

Verification:

- Pack presentation rules harness: `9/9` passed.
- Shipping Swift iPhoneOS 15 typecheck: passed.
- `GachaStorefrontIntegrationTests`: `2/2` passed.
- Related Gacha EditMode regression: `41/41` passed (`Logs/GachaPackV7RelatedEditMode.xml`).
- Re-exporting all 12 Pack PNG layers and comparing them byte-for-byte: passed.

The approved V7 concept contact sheet remains outside `Docs/DesignBibleAssets/`. This shipping preview also stays outside that directory until the user explicitly approves the rendered shipping implementation.
