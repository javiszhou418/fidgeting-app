# Gate 04 rev 7 mesh-clipped light correction

Date: 2026-08-26

User feedback:

> 节奏上面我还有很多想要调整的，尤其是你的过光，不应该超过这个物体本身。我觉得大概的动画是这样吧，但是可能你后面我们再去调节奏吧。

The user then asked where the real 3D animation should be tuned and told us to continue.

Disposition:

- Preserve the approved whole-case ownership and bounded entry/rotation overlap.
- Remove the external settle halo.
- Clip arrival rim, rotation rim and final sheen to the case silhouette.
- Keep Pack seam light confined to the Pack opening.
- Use Unity object-local or UV shader masks driven by MaterialPropertyBlock.
- Do not use an external Point Light for the final sheen.
- Blender owns geometry, pivot, UV and material zones.
- Unity owns runtime motion, curves, lighting, camera and performance.
- SwiftUI/Rive owns Pack selection, tear and foreground handoff.
- React is review tooling only.
- Runtime state authority remains GachaRevealDirector plus a tunable ScriptableObject profile.
- Timeline is preview and scrub tooling only.
- Timing, easing, overlap, Z travel and light parameters remain unapproved.
