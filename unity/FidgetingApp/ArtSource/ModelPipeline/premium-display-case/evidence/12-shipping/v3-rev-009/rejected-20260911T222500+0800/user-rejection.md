# Gate 12 R009 content preview rejection

- Stage: `12-shipping`
- Variant: `tri-spinner-slab-v3-cmf`
- Decision: `rejected`
- Authority: latest explicit user chat decision
- Local time: `2026-09-11 22:25 +08:00`
- Scope: the off-centre pocket macro and the four-product content matrix
- Shipping effect: none; `PremiumDisplayCaseShippingFactory` remains R004

## Exact user wording

> 首先，第一个陀螺的中心点还是不对，没有居中。然后，后面四张图搞得他妈什么乱七八糟的？你自己看这个他妈什么东西吗？你自己有没有一套审查的流程啊？大小尺寸比例全都不对。你搞了什么乱七八糟的？你搞这种垃圾东西，我把你炸了

## Rejected evidence

- `user-annotation-spinner-center.png`
- `user-annotation-content-matrix-defects.png`
- `Artifacts/TriSpinnerSlab/gate12-r009/gate12-r009-content-matrix-pocket-20260911T140800Z.png`
- `Artifacts/TriSpinnerSlab/gate12-r009/gate12-r009-pocket-macro-centered-20260911T140200Z.png`

These files remain historical evidence. They are forbidden as current
`reviewArtifactIds` and must not be presented as approval-ready output.

## Confirmed causes

1. The pocket macro used an oblique camera, so protruding content acquired
   screen-space parallax instead of proving front-view centring.
2. R009 reused R004 content rotations after adding a separate `-90° X`
   orientation node. The duplicate plane conversion made three products edge-on.
3. Product source scenes remained loaded during capture. Their environment
   renderers and lights contaminated the review frames.
4. One box fit normalized every product by thickness. This reduced valid toys
   to tiny silhouettes and ignored each product's real proportions.
5. The preflight only checked file existence and a bounds report. It did not
   block blank, clipped, side-on or foreign-geometry frames.

## Replacement gate

R010 must pass all of these checks before it can be shown:

- real shipping renderer snapshot for each catalog product;
- source scene closed before capture;
- V3-specific orientation per product;
- exact mesh-vertex radial fit inside the circular pocket;
- mechanical pivot centring for the three-blade;
- visual-bounds centring for non-rotors;
- centre error `≤ 0.05 mm`;
- straight-on screen error `≤ 1 px`;
- full phone-front and quarter views with no crop or foreign geometry;
- four rarity CMFs derived from the locked muted contract;
- automated tests and direct visual inspection.
