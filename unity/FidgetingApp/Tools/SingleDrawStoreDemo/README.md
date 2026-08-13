# Isolated Single-Draw Store Demo

This preview is disposable and intentionally independent from the shipping
gacha implementation.

## Isolation boundary

- Does not import StoreKit.
- Does not reference `GachaStoreModel`, `GachaStoreView`, `GachaStoreKit`, or
  any Unity bridge.
- Does not mutate tickets, coins, prizes, receipts, pity, or ownership in the
  shipping app.
- Recharge opens a local explanation sheet only. Product loading may happen
  only after an explicit recharge tap in a future integration.
- Product names and artwork are read-only copies of the canonical model catalog,
  `ThreeBladeMetalSkinCatalog`, and their shipping iOS thumbnails. The Demo
  does not invent a price or a successful purchase state.
- Delete this directory and `Artifacts/SingleDrawStoreDemo` to remove the demo.
- The single-draw animation bundles read-only copies of the six existing
  `DisplayCaseRarityRevealPrototype` storyboard frames. It does not run Unity,
  modify the case prefab, or promote the prototype to shipping.

## Current storefront proposal

- Three-Blade Metal is the featured spinner hero. The catalog currently has no
  sellable SKU, price, or release date, so the Demo says that purchasing is not
  yet open instead of inventing commerce metadata.
- The related skin shelf uses Mirror Aurora, Meteor Obsidian, and Titanium Heat
  with their real level requirements from the ten-skin catalog.
- The featured product establishes the spinner category and its related shelf
  establishes the skin category, while ticket-only draws remain separate.
- The storefront uses a neutral black/gray system; rarity color is limited to
  small semantic marks. A text-only back action returns to a disposable main
  entry page, which can reopen the store.

## Proposed future split

1. `GachaCatalogSnapshot`: server/Unity-owned prize, rarity and ownership data.
2. `GachaWalletSnapshot`: tickets and gear coins with separate spending APIs.
3. `GachaDrawService`: ticket-only single/ten draw requests and receipts.
4. `GachaCraftingService`: gear-coin crafting fees and cosmetic customization.
5. `GachaStorefrontLoader`: lazy App Store initialization after recharge tap.
6. `GachaProbabilityDisclosure`: secondary probability/pity detail surface.

## Product questions still open

- Exact blue/green/purple/gold rates and whether blueprint/item rates split
  inside each rarity.
- Pity thresholds, whether pity carries between series, and legal copy.
- Duplicate-to-fragment conversion ratios and blueprint redemption costs.
- Single-draw ticket price and eventual ten-draw discount/guarantee.
- Which cosmetics can spend gear coins and whether crafting can fail or queue.
- Recharge catalog, regions, parental controls, restore/refund behavior.
