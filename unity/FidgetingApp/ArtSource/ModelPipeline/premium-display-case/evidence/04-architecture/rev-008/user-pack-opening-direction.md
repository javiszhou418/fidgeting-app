# Pack Opening 动效重构 · Gate 04 输入

- Source task: `43ca0cec-1fb6-43dc-b651-2418c0df3ddf`
- Date: `2026-08-28`
- Exact engine choice: `使用现有 Unity 6.5 工程实施（推荐）`
- DecisionState: `Current Direction · Gate 04 Visual Pending`
- DeliveryState: `Candidate Timing Profile + Complete Recording`

The user superseded Gate 12 rev 4 and stopped unregistered rev 5 work. Preserve rev 1–4 evidence.

## Current sequence

| Phase | Window |
| --- | --- |
| handoff | `0–350 ms` |
| anticipation | `350–650 ms` |
| resistance | `650–950 ms` |
| snap | `950–1000 ms` |
| escalating tear | `1000–1750 ms` |
| Epic fake-out | `1550–1610 ms` |
| multi-layer impact | `1750–1930 ms` |
| one settling reveal | `1930–2530 ms` |
| native settle and staged CTA | `2530–3100 ms` |

The sequence rejects rigid-strip translation, opacity crossfade, repeated `720°` turntable motion, an empty idle tail, and a single-frame CTA pop.

## Locked boundaries

- Keep one assembled Premium Display Case and caller-owned `contentSlot`.
- Do not change the toy, its geometry, materials, artwork, pivot, physics, Haptics, mechanism, or angular velocity.
- Native owns Pack gesture, product metadata, business controls, CTA, receipt, award, and exact-once ACK.
- Unity owns 3D content, preloaded environment, effect rendering, camera response, and phase events.
- Haptics remain semantic event → recipe → platform renderer.
- Preserve same-request readiness, stale-request rejection, interruption restoration, and no black frame.
- Reduce Motion keeps the same cause and order. It removes shake, CA, distortion, speed lines, and hitstop, and reduces flash and bloom.
- Rarity result profiles are Common, Rare, Epic, and Legendary. Six Pack display tiers remain independent and cannot reveal result rarity.
- Use Unity `6000.5.6f1`, URP `17.5.0`, Timeline `1.8.12`, AnimationCurve, native orchestration, and Shuriken. Do not add VFX Graph or tween packages.

Exact timings, `3–5 events/s`, and YAVG are acceptance targets for this direction. They are not universal facts.
