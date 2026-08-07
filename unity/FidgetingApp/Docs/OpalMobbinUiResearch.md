# Opal / Mobbin UI Research for Fidget Spinner

Last reviewed: 2026-08-06

Status: design research only. This document is evidence and implementation guidance; it does not claim runtime integration or iPhone validation.

## Source and access evidence

- Source collection: [Opal — Focus, app blocker & timer](https://mobbin.com/apps/opal-ios-3cd5ac67-b82e-481c-b1fb-6c817ac87321/5e028b5d-803b-4bdc-a0dd-568f9e3e5b55/screens)
- Access path: no Mobbin MCP or connector was available, so the Browser integration used the user's existing signed-in Chrome session.
- Collection size observed in Mobbin: 208 screens, 208 tagged UI elements, and 62 flows.
- Captured device size on screen-detail pages: iOS 393 x 852.
- Research scope: Screens, UI Elements, and Flows were cross-checked. The conclusions below are patterns across the collection, not a trace of only the highlighted gallery row.

Representative evidence:

| Screen | Mobbin evidence | Useful pattern |
| --- | --- | --- |
| Home | [1b3deee1-a193-4e36-93b0-7e89740f9c5c](https://mobbin.com/screens/1b3deee1-a193-4e36-93b0-7e89740f9c5c) | Hero material, score hierarchy, contextual card, three-item bottom navigation |
| Score detail | [3f912d2e-2bc2-400b-aba4-88b02852a4c8](https://mobbin.com/screens/3f912d2e-2bc2-400b-aba4-88b02852a4c8) | Semicircular gauge, status pills, labeled progress bars |
| Sign up | [5011b2b9-7a00-4b62-b368-44e139b8cf6e](https://mobbin.com/screens/5011b2b9-7a00-4b62-b368-44e139b8cf6e) | Pill actions, clear primary/secondary hierarchy, sparse centered layout |
| App detail sheet | [9a9094c8-e1ef-4d85-95e3-af37fde9bec0](https://mobbin.com/screens/9a9094c8-e1ef-4d85-95e3-af37fde9bec0) | Context-preserving bottom sheet, nested rule cards, full-width primary action |
| Profile range chips | [8305b14b-b451-4351-9b38-f1b2ed465463](https://mobbin.com/screens/8305b14b-b451-4351-9b38-f1b2ed465463) | Week / Month / All Time compact filters above a chart |
| Milestone progress | [1ab1ceef-2aad-4a64-bf1d-b26d6e193f38](https://mobbin.com/screens/1ab1ceef-2aad-4a64-bf1d-b26d6e193f38) | Thin linear progress, value caption, disabled/locked action |
| Card samples | [855071e1-9fad-4bf8-bcd7-9feb3fe8032e](https://mobbin.com/screens/855071e1-9fad-4bf8-bcd7-9feb3fe8032e), [2cccc546-f51f-413e-bbb9-e421e0c9edc5](https://mobbin.com/screens/2cccc546-f51f-413e-bbb9-e421e0c9edc5), [78d2246d-f084-475c-8296-1a041feb9bb6](https://mobbin.com/screens/78d2246d-f084-475c-8296-1a041feb9bb6) | Reward, rule, and media cards using the same rounded/glass grammar |

Mobbin's UI Elements filters reported these Opal-specific result counts during review: Button 6, Card 3, Bottom Sheet 3, Progress Indicator 1, Tab Bar 1, Chip 1, and Switch 1. The tags are useful discovery aids, but the screen itself remains the visual authority because a tag can describe only one element inside a larger screenshot.

## Flow evidence

Mobbin groups the 62 flows into the following product hierarchy:

- Onboarding: creating an account, screen-time quiz, account setup, and subscription.
- Home: gems, gem unlocking, theme changes, Opal score, focus report, profile, and rewards.
- Apps: blocked-app detail, unblocking, rules, schedule/time/open-limit creation, rule editing/detail, distracting apps, and never-allowed apps.
- Timer: completion/end states, timer-specific blocked apps, digital detox, mix creation, volume/editing, sleep stories, and downloads.
- Settings: Pro information, account details, notification/block-screen/waiting-room/autofocus controls, support, emergency pass, and about.
- Platform surfaces: login, Live Activities, Dynamic Island, and widgets.

The important lesson for Fidget Spinner is that visual reuse follows product semantics. A single glass card primitive supports rewards, rules, metrics, and settings, but each screen composes it differently. The reusable library should therefore separate visual primitives from product state and Unity bridge calls.

## Visual language

### Composition

- A black or near-black field makes the physical product the dominant object.
- Natural-material imagery is used as one focal Hero, not as decorative wallpaper on every panel.
- Large empty areas provide calm and make the next action obvious.
- Main screens typically use a single Hero/statistic, one contextual card, and compact navigation. Detailed screens swap the Hero for gauges, progress bars, or lists.
- Sheets preserve the obscured screen as context rather than replacing it with another full-screen route.

### Color

- White is the primary text and selected-state color.
- Secondary copy is cool white/gray; tertiary metadata is clearly quieter.
- Material-derived green/opal color is a low-opacity tint, not a permanent brand-colored control fill.
- Green communicates positive/allowed/great states. Pink/red communicates short, blocked, or warning states. These semantic accents should not become global navigation colors.
- Avoid copying Opal's gem artwork, trademark, score taxonomy, or product copy. The transferable ideas are hierarchy, material-responsive tint, spacing, and interaction grammar.

### Typography

- Rounded/system sans serif typography is used with a compact weight range: regular body, semibold labels, bold numeric emphasis.
- Product typography always keeps the font's native letter spacing. Do not add tracking or kerning; create hierarchy with size, weight, color, opacity, and layout spacing instead.
- In every metric, the numeric value is the visual headline and sits at least one semantic type level above its label or subhead. Use stable-width digits, weight, and contrast to highlight the number itself; units and explanations recede to subheadline/caption without added letter spacing.
- Practical Fidget Spinner mapping: title 20-28 pt, section title 17-20 pt, body 13-15 pt, caption 10-12 pt, with monospaced digits for speed/RPM/XP.
- Keep line lengths short on overlays. Onboarding and action sheets rarely combine a long headline, long body, and multiple controls in the same vertical region.

### Shape, spacing, and depth

- Minimum interactive target: 44 x 44 pt.
- Primary action: approximately 52 pt high with a full pill radius.
- Compact action/card radii form a three-step family: about 16, 22, and 26-28 pt.
- Common internal gaps are 4, 8, and 12-16 pt; screen-edge content insets are about 16-20 pt.
- Glass depth has three roles: compact icon/segment controls, normal information/action cards, and a context-preserving sheet. Do not apply the same opacity and interaction effect to all three.
- Selected segments are primarily white with a restrained translucent fill. Unselected items use low-opacity white rather than a competing accent color.

## Interaction patterns

- Compact segmented navigation uses icons where semantics are already learned; labels remain available to VoiceOver.
- Horizontal paging and carousels show one clear selection and restrained page indicators.
- Disclosure rows carry secondary editing/detail routes without turning the whole screen into a dense settings form.
- Bottom sheets group a title, optional subtitle/state selector, compact cards, one primary action, and tiny quota/status footer.
- Step controls use separate minus/plus hit targets around a prominent value.
- Hold-to-start or hold-to-commit is reserved for consequential actions. It should expose progress and cancellation rather than behaving like a delayed tap.
- Motion is short and quiet: approximately 180-240 ms ease-out for selection and state changes; sheets may use the system spring. No decorative motion should create or imply rotor self-spin.

## Reusable native component contract

The shared component layer should remain independent of `UnityBridge` and product enums. Domain screens inject labels, symbols, color, state, and callbacks.

| Component | Responsibility | Suggested state surface |
| --- | --- | --- |
| `FidgetUITokens` | Sizes, radii, spacing, opacity, motion | Static values only |
| `ProductBackdrop` | Neutral black field with restrained depth | Optional material tint, no product artwork |
| `ProductGlassModifier` | iOS 26 glass plus older-material fallback | Radius, tint, interactive/static |
| `ProductIconButton` | Compact destination/action | Symbol, selected, label, action |
| `ProductIconSegmentedControl` | Mode or destination selection | Options, selection, symbol/title/hint closures |
| `ProductPageIndicator` | Paged library position | Items, selection, combined accessibility label |
| `ProductPrimaryActionLabel` | 52 pt prominent action label | Title, symbol, accent |
| `ProductActionLabel` | 44 pt secondary action label | Title, symbol, accent |
| `ProductSectionCard` | Reusable titled static glass card | Title, symbol, content builder |
| `ProductMetricCard` | Compact number/value tile | Title, value, symbol, semantic accent |
| `ProductBottomSheetShell` | Shared native sheet container | Title, close label, content builder; optional actions remain composed content |
| `ProductDisclosureRow` | Navigation/edit row | Leading symbol, title, value, destination action |
| `ProductStatusPill` | Score/state/filter chip | Symbol, title/value, selected or semantic state |
| `ProductProgressGauge` | Thin linear progress presentation | Clamped value, semantic accent; display only |
| `ProductSpeedDashboard` | Compact bottom-anchored rotary Hero metric | Display value, unit, normalized fraction, hysteretic semantic accent, high-contrast persistent caption, accessibility copy; read-only and grouped above the progression HUD; no decorative flame layer |
| `ProductSideMetricDashboard` | Separate subordinate live metric wing | Independent value/fraction, unit, inherited Hero accent, accessibility copy; read-only, visually lower weight, and never overlapping the Hero |
| `ProductStepperRow` | Minus/value/plus control | Bounded value and change callbacks |
| `ProductHoldAction` | Consequential hold interaction | Duration/progress/cancel/commit; semantic event callback |

`FidgetUITokens` through `ProductMetricCard`, plus `ProductBottomSheetShell`, `ProductStatusPill`, the linear `ProductProgressGauge`, the 180° `ProductSpeedDashboard`, and its subordinate `ProductSideMetricDashboard` wings, are implemented and consumed by the shipping overlay. `ProductDisclosureRow`, `ProductStepperRow`, and `ProductHoldAction` remain candidates; they should not be added until real repeated call sites appear.

### Bottom sheet, chip, and progress specifications

These three candidates have direct filtered-screen evidence and are sufficiently distinct to warrant explicit contracts:

- `ProductBottomSheetShell`: based on [9a9094c8-e1ef-4d85-95e3-af37fde9bec0](https://mobbin.com/screens/9a9094c8-e1ef-4d85-95e3-af37fde9bec0). The observed sheet occupies roughly the lower 35-45% of a 393 x 852 screen, retains the Apps screen behind it, and uses about 26-28 pt top corners. Use 16-20 pt content insets and 12-16 pt vertical rhythm. The implemented shell owns only the title, close action, dark navigation context, and content builder; header detail, primary action, and safe-area footer remain explicit content composition. The shell must not assume every presentation is draggable or every sheet commits an action.
- `ProductStatusPill`: based on [8305b14b-b451-4351-9b38-f1b2ed465463](https://mobbin.com/screens/8305b14b-b451-4351-9b38-f1b2ed465463). The Week / Month / All Time controls are compact chart filters, visually about 24-28 pt high, with 8-10 pt horizontal content padding and a capsule radius. Use caption/footnote text, a low-opacity white outline or fill, and a white selected label. The outer hit target still expands to at least 44 pt. Expose `.isSelected` to accessibility and never encode status by tint alone. The same primitive may display a semantic status value, but selection and semantic color should be separate inputs.
- `ProductProgressGauge`: linear evidence is [1ab1ceef-2aad-4a64-bf1d-b26d6e193f38](https://mobbin.com/screens/1ab1ceef-2aad-4a64-bf1d-b26d6e193f38); arc/metric evidence is [3f912d2e-2bc2-400b-aba4-88b02852a4c8](https://mobbin.com/screens/3f912d2e-2bc2-400b-aba4-88b02852a4c8). The implemented component intentionally covers only linear progress: a restrained 5 pt track with rounded ends, externally supplied accent, 0...1 display clamping, and one combined accessibility value. Arc progress is a separate future Hero component with a large monospaced value and label; it should not inherit the small linear gauge typography or be forced into the same geometry. The visual component never writes gameplay progression.

## Fidget Spinner-specific guardrails

- The 3D model remains the Hero. Do not replace it with an Opal-style gem or a static SF Symbol.
- Material tint should come from the confirmed equipped skin/model state and remain subordinate to white selection states.
- Component taps may request a product-level selection/action event, but must not call raw `IosHaptics`. The required route remains input -> mechanism/product state -> semantic event -> Haptic recipe -> iOS renderer.
- Hold actions and progress views must not alter rotor angular velocity. The rotor starts/resets at zero and receives speed only from explicit user/device input.
- Mode and detent UI must read the same canonical mechanism setting used by physics and Haptics; visual segments must not introduce duplicate defaults.
- Safe area, Reduce Transparency, Dynamic Type, VoiceOver labels, and a minimum 44 pt hit target are part of the component contract.
- iPhone validation remains pending until performed on hardware across dark metal, bright highlights, and translucent overlays.

## Recommended acceptance checks

- Static/source tests keep every shared hit target at or above 44 pt and the primary action at 52 pt.
- Component primitives contain no `UnitySendMessage`, `IosHaptics`, or model-specific enum dependencies.
- The older-iOS fallback retains a 0.7 pt, low-opacity white highlight stroke.
- The selected mode/destination is identifiable without depending only on tint color.
- Page indicator count and accessibility text derive from the same item collection.
- Any shared hold-action implementation exposes cancellation and emits commit once.
- Runtime screen wiring and iPhone visual validation are recorded separately in `IMPLEMENTATION_STATUS.md`; this research document alone is not integration evidence.
