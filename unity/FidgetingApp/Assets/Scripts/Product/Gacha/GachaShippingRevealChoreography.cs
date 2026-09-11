using System;
using UnityEngine;

namespace FidgetingApp.Product.Gacha
{
    /// <summary>
    /// CSS-style cubic-bezier easing (x1, y1, x2, y2), solved on x by
    /// bisection so the spec curves are used as written, not replaced by a
    /// default ease.
    /// </summary>
    public readonly struct GachaCubicBezier
    {
        private readonly float x1;
        private readonly float y1;
        private readonly float x2;
        private readonly float y2;

        public GachaCubicBezier(float x1, float y1, float x2, float y2)
        {
            this.x1 = x1;
            this.y1 = y1;
            this.x2 = x2;
            this.y2 = y2;
        }

        public static readonly GachaCubicBezier EaseOut =
            new GachaCubicBezier(0.16f, 1f, 0.3f, 1f);
        public static readonly GachaCubicBezier EaseInOut =
            new GachaCubicBezier(0.83f, 0f, 0.17f, 1f);
        public static readonly GachaCubicBezier Overshoot =
            new GachaCubicBezier(0.34f, 1.56f, 0.64f, 1f);
        public static readonly GachaCubicBezier Anticipate =
            new GachaCubicBezier(0.36f, 0f, 0.66f, -0.56f);
        public static readonly GachaCubicBezier Pull =
            new GachaCubicBezier(0.2f, 0f, 0.1f, 1f);

        public float Evaluate(float t)
        {
            t = Mathf.Clamp01(t);
            if (t <= 0f) return 0f;
            if (t >= 1f) return 1f;
            float low = 0f;
            float high = 1f;
            float s = t;
            for (int i = 0; i < 24; i++)
            {
                s = (low + high) * 0.5f;
                float x = Sample(x1, x2, s);
                if (x < t) low = s; else high = s;
            }
            return Sample(y1, y2, s);
        }

        private static float Sample(float p1, float p2, float s)
        {
            float u = 1f - s;
            return 3f * u * u * s * p1 + 3f * u * s * s * p2 + s * s * s;
        }
    }

    /// <summary>
    /// Gacha reveal v2 timeline for the live case, in seconds from case play.
    /// Case play happens at T0 + 0.70 s (T0 = tear trigger), so every value
    /// here is 0.70 s earlier than the spec's T0-relative number.
    ///
    /// Pack release (0) → pull (0.24–1.02) → settle (0.24) → hold back (0.40)
    /// → anticipate (0.20) → flip (0.42, reveal effects fire as the face
    /// passes 90°) → overshoot (0.18) → labels (3.26) → complete → idle.
    ///
    /// User review of rev-005: the Pack must start leaving before the case
    /// starts moving, with overlap. So the Pack is released at case play and
    /// the pull begins <see cref="PullStartSeconds"/> later.
    /// </summary>
    public static class GachaShippingRevealChoreography
    {
        public const float CasePlayAfterTearSeconds = 0.70f;

        /// <summary>
        /// Pack drop lead before the case starts to move. The case also
        /// starts hidden below the mouth, so the Pack's fall is what first
        /// exposes it; only then does the pull begin.
        /// rev-009 review (gacha-reveal-timeline canvas): 0.35 → 0.24 to
        /// match the shorter 0.58 s Pack fall.
        /// </summary>
        public const float PullStartSeconds = 0.24f;
        /// <summary>rev-008 review: the rise-then-settle reads a touch slow; 0.90 → 0.78.</summary>
        public const float PullSeconds = 0.78f;
        public const float PullLeanDegrees = -6f;
        public const float PullStartScaleFraction = 0.72f;
        public const float SettleSeconds = 0.24f;
        public const float HoldBackSeconds = 0.40f;
        public const float AnticipateSeconds = 0.20f;
        public const float AnticipateYawDegrees = 12f;
        public const float AnticipateScale = 0.97f;
        public const float FlipSeconds = 0.42f;
        public const float FlipOvershootDegrees = 4f;
        public const float FlipOvershootSeconds = 0.18f;
        public const float FlashSeconds = 0.26f;
        public const float FlashRiseSeconds = 0.06f;
        public const float GlowPeakSeconds = 0.12f;
        public const float GlowDecaySeconds = 1.20f;
        public const float GlowHoldFraction = 0.6f;
        public const float GlowHoldBeforeFlipFraction = 0.5f;
        public const float BladeEmissiveSeconds = 0.22f;
        /// <summary>
        /// The Pack-hue gradient backdrop holds through tear, pull and hold;
        /// it fades to the live environment scene the moment the face passes
        /// 90° (user: 卡片啪转过来那一刻再切场景). Short, because the flash
        /// covers the cut.
        /// </summary>
        public const float StageLightUpSeconds = 0.35f;
        public const float HaloSeconds = 0.60f;
        public const float HaloOpacity = 0.35f;
        public const float HaloRadiusCaseWidths = 1.6f;
        public const float LabelSeconds = 3.26f;
        public const float LabelFadeSeconds = 0.30f;
        public const float IdleYawDegrees = 3f;
        public const float IdleYawPeriodSeconds = 4.0f;

        /// <summary>
        /// Case top relative to the Pack mouth at pull start, in points.
        /// Negative = hidden behind the Pack body until the Pack drops.
        /// </summary>
        public const float PullStartPeekPoints = -12f;
        /// <summary>
        /// Screen fraction (from the bottom) of the Pack mouth line. The
        /// shipping Pack rests centred at 44% from the top with a 244×325 pt
        /// artwork whose body top edge sits 18% down the artwork, so the
        /// mouth is at 1 − (0.44 − 0.186 + 0.067) ≈ 0.68 on a 874 pt stage.
        /// </summary>
        public const float MouthViewportYFraction = 0.68f;
        /// <summary>
        /// The case is squarer and shorter than the Pack, so a pull straight
        /// to its rest centre would happen entirely behind the Pack body.
        /// It is pulled up to an apex (centre 28% from the top) so it clears
        /// the mouth, then settles down to rest while the Pack falls away.
        /// </summary>
        public const float PullApexCenterViewportYFraction = 0.72f;
        /// <summary>Case centre at rest: y = 44% from the top.</summary>
        public const float RestCenterViewportYFraction = 0.56f;
        public const float RestCaseViewportWidthFraction = 0.60f;
        public const float MaximumRestOffsetMeters = 0.45f;

        public const float BackYawDegrees = 180f;

        public static float PullEndSeconds => PullStartSeconds + PullSeconds;
        public static float SettleEndSeconds => PullEndSeconds + SettleSeconds;
        public static float HoldBackEndSeconds => SettleEndSeconds + HoldBackSeconds;
        public static float AnticipateEndSeconds =>
            HoldBackEndSeconds + AnticipateSeconds;
        public static float FlipEndSeconds => AnticipateEndSeconds + FlipSeconds;
        public static float OvershootEndSeconds =>
            FlipEndSeconds + FlipOvershootSeconds;
        public static float CompleteSeconds => LabelSeconds;

        private static float revealSecondsCache = -1f;

        /// <summary>The frame the face passes 90°; every reveal effect keys off it.</summary>
        public static float RevealSeconds
        {
            get
            {
                if (revealSecondsCache < 0f)
                {
                    float low = AnticipateEndSeconds;
                    float high = FlipEndSeconds;
                    for (int i = 0; i < 40; i++)
                    {
                        float mid = (low + high) * 0.5f;
                        if (YawDegrees(mid) > 90f) low = mid; else high = mid;
                    }
                    revealSecondsCache = (low + high) * 0.5f;
                }
                return revealSecondsCache;
            }
        }

        public static float PullProgress(float seconds)
        {
            float local = seconds - PullStartSeconds;
            if (local <= 0f) return 0f;
            if (local >= PullSeconds) return 1f;
            return GachaCubicBezier.Pull.Evaluate(local / PullSeconds);
        }

        /// <summary>
        /// The native Pack may start its drop. Published on the first played
        /// frame so the Pack leads the case by <see cref="PullStartSeconds"/>.
        /// </summary>
        public static bool HasCrossedPackLip(float seconds)
        {
            return seconds >= 0f;
        }

        public static float ScaleMultiplier(float seconds)
        {
            float scale = Mathf.Lerp(
                PullStartScaleFraction,
                1f,
                PullProgress(seconds));
            if (seconds >= HoldBackEndSeconds && seconds < AnticipateEndSeconds)
            {
                float t = GachaCubicBezier.Anticipate.Evaluate(
                    (seconds - HoldBackEndSeconds) / AnticipateSeconds);
                scale *= Mathf.Lerp(1f, AnticipateScale, t);
            }
            else if (seconds >= AnticipateEndSeconds && seconds < FlipEndSeconds)
            {
                float t = GachaCubicBezier.EaseInOut.Evaluate(
                    (seconds - AnticipateEndSeconds) / FlipSeconds);
                scale *= Mathf.Lerp(AnticipateScale, 1f, t);
            }
            return scale;
        }

        /// <summary>0 at the apex, 1 at rest; runs over the settle beat.</summary>
        public static float SettleProgress(float seconds)
        {
            if (seconds <= PullEndSeconds) return 0f;
            if (seconds >= SettleEndSeconds) return 1f;
            return GachaCubicBezier.EaseOut.Evaluate(
                (seconds - PullEndSeconds) / SettleSeconds);
        }

        /// <summary>Lean back while being pulled; upright by the end of the settle.</summary>
        public static float TiltDegrees(float seconds)
        {
            if (seconds < PullEndSeconds) return PullLeanDegrees;
            if (seconds < SettleEndSeconds)
            {
                float t = GachaCubicBezier.EaseOut.Evaluate(
                    (seconds - PullEndSeconds) / SettleSeconds);
                return Mathf.Lerp(PullLeanDegrees, 0f, t);
            }
            return 0f;
        }

        /// <summary>180 = back to the viewer, 0 = front.</summary>
        public static float YawDegrees(float seconds)
        {
            if (seconds < HoldBackEndSeconds) return BackYawDegrees;
            if (seconds < AnticipateEndSeconds)
            {
                float t = GachaCubicBezier.Anticipate.Evaluate(
                    (seconds - HoldBackEndSeconds) / AnticipateSeconds);
                return BackYawDegrees + AnticipateYawDegrees * t;
            }
            if (seconds < FlipEndSeconds)
            {
                float t = GachaCubicBezier.EaseInOut.Evaluate(
                    (seconds - AnticipateEndSeconds) / FlipSeconds);
                return Mathf.Lerp(BackYawDegrees + AnticipateYawDegrees, 0f, t);
            }
            if (seconds < OvershootEndSeconds)
            {
                float p = (seconds - FlipEndSeconds) / FlipOvershootSeconds;
                return -FlipOvershootDegrees * Mathf.Sin(p * Mathf.PI);
            }
            if (seconds >= CompleteSeconds)
            {
                return IdleYawDegrees * Mathf.Sin(
                    (seconds - CompleteSeconds) / IdleYawPeriodSeconds * 2f * Mathf.PI);
            }
            return 0f;
        }

        /// <summary>Edge glow as a fraction of the rarity intensity.</summary>
        public static float GlowFraction(float seconds)
        {
            if (seconds < SettleEndSeconds) return 0f;
            if (seconds < HoldBackEndSeconds)
            {
                return GlowHoldBeforeFlipFraction
                    * ((seconds - SettleEndSeconds) / HoldBackSeconds);
            }
            float since = seconds - RevealSeconds;
            if (since < 0f) return GlowHoldBeforeFlipFraction;
            if (since < GlowPeakSeconds)
            {
                return Mathf.Lerp(
                    GlowHoldBeforeFlipFraction,
                    1f,
                    since / GlowPeakSeconds);
            }
            float decay = (since - GlowPeakSeconds) / GlowDecaySeconds;
            return Mathf.Lerp(1f, GlowHoldFraction, GachaCubicBezier.EaseOut.Evaluate(decay));
        }

        public static float FlashOpacity(float seconds, GachaRevealRarityStyle style)
        {
            float since = seconds - RevealSeconds;
            if (since < 0f || since >= FlashSeconds) return 0f;
            if (since < FlashRiseSeconds)
            {
                return style.FlashAlpha * (since / FlashRiseSeconds);
            }
            float fall = (since - FlashRiseSeconds) / (FlashSeconds - FlashRiseSeconds);
            return style.FlashAlpha * (1f - GachaCubicBezier.EaseOut.Evaluate(fall));
        }

        public static float BladeEmissive(float seconds)
        {
            float since = seconds - RevealSeconds;
            if (since <= 0f) return 0f;
            return GachaCubicBezier.EaseOut.Evaluate(since / BladeEmissiveSeconds);
        }

        /// <summary>1 = stage at 25% brightness, 0 = scene fully lit.</summary>
        public static float StageDim(float seconds)
        {
            float since = seconds - RevealSeconds;
            if (since <= 0f) return 1f;
            return 1f - GachaCubicBezier.EaseOut.Evaluate(since / StageLightUpSeconds);
        }

        public static float HaloOpacityAt(float seconds)
        {
            float since = seconds - RevealSeconds;
            if (since <= 0f) return 0f;
            return HaloOpacity * GachaCubicBezier.EaseOut.Evaluate(since / HaloSeconds);
        }

        public static float LabelAlpha(float seconds)
        {
            float since = seconds - LabelSeconds;
            if (since <= 0f) return 0f;
            return GachaCubicBezier.EaseOut.Evaluate(since / LabelFadeSeconds);
        }

        public static bool IsComplete(float seconds)
        {
            return seconds >= CompleteSeconds;
        }
    }

    /// <summary>
    /// Effect table keyed by rarity (spec RARITY_TABLE). Standard is nearly
    /// silent; Heirloom gets the full flash, glow and particle count. The
    /// flow length never changes with rarity.
    /// </summary>
    public readonly struct GachaRevealRarityStyle
    {
        public GachaRevealRarityStyle(
            Color glow,
            float glowIntensity,
            float flashAlpha,
            int particleCount,
            float hapticSignal)
        {
            Glow = glow;
            GlowIntensity = glowIntensity;
            FlashAlpha = flashAlpha;
            ParticleCount = particleCount;
            HapticSignal = hapticSignal;
        }

        public Color Glow { get; }
        public float GlowIntensity { get; }
        public float FlashAlpha { get; }
        public int ParticleCount { get; }
        /// <summary>0–1 signal for the semantic Haptic recipe (light → heavy).</summary>
        public float HapticSignal { get; }

        public static readonly Color StandardGlow = new Color(0.604f, 0.639f, 0.678f);
        public static readonly Color RareGlow = new Color(0.373f, 0.722f, 1f);
        public static readonly Color HeirloomGlow = new Color(0.784f, 0.949f, 0.753f);

        public static GachaRevealRarityStyle For(GachaRarity rarity)
        {
            switch (rarity)
            {
                // rev-006 review: particles must read clearly — counts are
                // 2× the spec table; size, speed and brightness are raised in
                // GachaRevealStageFX.EmitBurst. Standard stays at 0.
                case GachaRarity.Heirloom:
                    return new GachaRevealRarityStyle(HeirloomGlow, 1.0f, 0.85f, 240, 1f);
                case GachaRarity.Signature:
                    return new GachaRevealRarityStyle(RareGlow, 0.6f, 0.4f, 96, 0.7f);
                case GachaRarity.Refined:
                    return new GachaRevealRarityStyle(RareGlow, 0.5f, 0.25f, 56, 0.55f);
                default:
                    return new GachaRevealRarityStyle(StandardGlow, 0.35f, 0f, 0, 0.35f);
            }
        }
    }

    /// <summary>
    /// Stage-side effects owned by the reveal: a dimmer that keeps the cave
    /// at 25% until the reveal, a full-frame flash, a radial halo behind the
    /// case and a burst of drifting particles. All quads face the camera and
    /// use unlit alpha materials.
    /// </summary>
    public sealed class GachaRevealStageFX : IDisposable
    {
        public const float IdleStageDim = 0.75f;
        /// <summary>Above the environment's foreground planes (1000/1001).</summary>
        public const int BackdropSortingOrder = 1002;
        /// <summary>Case renderers sort above the stage quads but below the flash.</summary>
        public const int CaseSortingOrder = 1010;
        public const int FlashSortingOrder = 2000;
        /// <summary>Backdrop texture height in texels; width follows the camera aspect.</summary>
        public const int BackdropTextureHeight = 512;
        /// <summary>Point-space reference height used by the native backdrop gradients.</summary>
        public const float BackdropReferenceHeightPoints = 874f;
        /// <summary>Value (HSV) of the stage tint so the hue reads, not just darkness.</summary>
        public const float StageTintValue = 0.30f;
        public const float NeutralStageTintValue = 0.08f;

        private static readonly int ColorId = Shader.PropertyToID("_Color");
        private Color dimTint = Color.black;

        private readonly Camera camera;
        private readonly Transform root;
        private readonly Transform dimmer;
        private readonly Transform flash;
        private readonly Transform halo;
        private readonly Material dimmerMaterial;
        private readonly Material flashMaterial;
        private readonly Material haloMaterial;
        private Texture2D haloTexture;
        private Texture2D sparkTexture;
        private Texture2D backdropTexture;
        private bool backdropMode;
        private ParticleSystem particles;
        private float caseDistanceMeters;

        public GachaRevealStageFX(Transform parent, Camera camera)
        {
            this.camera = camera;
            root = new GameObject("GachaRevealStageFX").transform;
            root.SetParent(parent, false);
            Shader shader = Shader.Find("Sprites/Default");
            // The cave environment layers render at 3000–3002 with ZTest
            // Always, so anything meant to sit between the environment and
            // the case must queue above them and below the case shells (3020+).
            dimmerMaterial = new Material(shader) { renderQueue = 3005 };
            haloMaterial = new Material(shader) { renderQueue = 3006 };
            flashMaterial = new Material(shader) { renderQueue = 3990 };
            // Transparent sorting puts sortingOrder before render queue, and
            // the cave's foreground rock planes sit at sortingOrder 1000/1001,
            // so stage quads must sort above them. The director lifts the
            // case renderers above these (CaseSortingOrder) so its shells
            // still draw over the backdrop.
            dimmer = CreateQuad(root, "StageDimmer", dimmerMaterial, BackdropSortingOrder);
            halo = CreateQuad(root, "RevealHalo", haloMaterial, BackdropSortingOrder + 1);
            flash = CreateQuad(root, "RevealFlash", flashMaterial, FlashSortingOrder);
            haloTexture = BuildRadialTexture(128);
            haloMaterial.mainTexture = haloTexture;
            PlaceForCaseDistance(0.4f);
            SetDim(IdleStageDim);
            SetFlash(0f, Color.white);
            halo.gameObject.SetActive(false);
        }

        public bool IsWired => dimmer != null && flash != null && halo != null;

        /// <summary>Re-place the quads once the case position is known.</summary>
        public void PlaceForCaseDistance(float distanceMeters)
        {
            caseDistanceMeters = Mathf.Max(0.05f, distanceMeters);
            // The gradient backdrop must map 1:1 onto the screen so its glows
            // sit where the native backdrop drew them; the plain dim can
            // overscan.
            Place(dimmer, caseDistanceMeters + 0.30f, backdropMode ? 1.0f : 1.8f);
            Place(flash, 0.04f, 1.8f);
        }

        /// <summary>
        /// Pack-hue wash for the dim stage (rev-006 review: the background
        /// must carry visible saturation and hue while the Pack is selected).
        /// The tint keeps the incoming hue/saturation at a fixed dark value.
        /// </summary>
        public void SetDimTint(Color tint)
        {
            Color.RGBToHSV(tint, out float h, out float sat, out _);
            // Neutral tiers (STANDARD silver) stay a near-black dim; only a
            // saturated tier hue lifts the wash toward StageTintValue.
            float value = Mathf.Lerp(
                NeutralStageTintValue,
                StageTintValue,
                Mathf.Clamp01(sat / 0.85f));
            dimTint = Color.HSVToRGB(h, sat, value);
            SetDim(currentDim);
        }

        private float currentDim = IdleStageDim;

        /// <summary>0 = lit scene, 1 = idle 25% brightness stage.</summary>
        public void SetDim(float dim)
        {
            currentDim = Mathf.Clamp01(dim);
            Color color = backdropMode ? Color.white : dimTint;
            color.a = currentDim;
            dimmerMaterial.SetColor(ColorId, color);
            dimmer.gameObject.SetActive(currentDim > 0.001f);
        }

        /// <summary>
        /// Stage strength 0–1 for the choreography: 1 = the Pack stage is
        /// fully in front of the environment (opaque gradient backdrop, or
        /// the 75% dim when no backdrop was supplied), 0 = environment shown.
        /// </summary>
        public void SetStageStrength(float strength)
        {
            float s = Mathf.Clamp01(strength);
            SetDim(backdropMode ? s : s * IdleStageDim);
        }

        public bool HasBackdrop => backdropMode;

        /// <summary>
        /// Replaces the dim with an opaque Pack-hue gradient that mirrors the
        /// native `ProductPackHueBackdrop` (black base, centre glow, floor
        /// glow, top wash), so the storefront's backdrop fade at selection
        /// is invisible and the environment stays hidden until the flip.
        /// Opacities are the native rules × <paramref name="strength"/>.
        /// </summary>
        public void SetBackdrop(Color accent, float strength)
        {
            float aspect = camera != null ? camera.aspect : 0.46f;
            int height = BackdropTextureHeight;
            int width = Mathf.Max(8, Mathf.RoundToInt(height * aspect));
            DestroyOwned(backdropTexture);
            backdropTexture = BuildBackdropTexture(width, height, accent, Mathf.Clamp01(strength));
            dimmerMaterial.mainTexture = backdropTexture;
            backdropMode = true;
            PlaceForCaseDistance(caseDistanceMeters);
            SetDim(1f);
        }

        /// <summary>
        /// Uses a PNG snapshot of the native stage backdrop (rendered by the
        /// storefront at selection) so the hand-off from the native layer to
        /// this quad is pixel-identical, whatever the native design is.
        /// Returns false when the file cannot be read; callers then fall back
        /// to <see cref="SetBackdrop"/>.
        /// </summary>
        public bool TrySetBackdropImage(string path)
        {
            if (string.IsNullOrEmpty(path) || !System.IO.File.Exists(path))
            {
                return false;
            }
            byte[] bytes;
            try
            {
                bytes = System.IO.File.ReadAllBytes(path);
            }
            catch (System.Exception)
            {
                return false;
            }
            Texture2D texture = new Texture2D(2, 2, TextureFormat.RGBA32, false)
            {
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Bilinear
            };
            if (!ImageConversion.LoadImage(texture, bytes, false))
            {
                DestroyOwned(texture);
                return false;
            }
            DestroyOwned(backdropTexture);
            backdropTexture = texture;
            dimmerMaterial.mainTexture = backdropTexture;
            backdropMode = true;
            PlaceForCaseDistance(caseDistanceMeters);
            SetDim(1f);
            return true;
        }

        // Native rules (GachaPackStorefrontBackdropRules) in points on a
        // 402×874 stage: centre glow (0.5, 0.42) r 24→420 stops 0.42/0.16/0;
        // floor glow (0.5, 0.94) r 12→280 stops 0.24/0; top wash 0.12 → black
        // 0.88 → black 1.0 (linear, top→bottom).
        private static Texture2D BuildBackdropTexture(int width, int height, Color accent, float strength)
        {
            Texture2D texture = new Texture2D(width, height, TextureFormat.RGBA32, false)
            {
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Bilinear
            };
            float heightPoints = BackdropReferenceHeightPoints;
            float widthPoints = heightPoints * width / height;
            Color[] pixels = new Color[width * height];
            for (int y = 0; y < height; y++)
            {
                // Texture rows run bottom-up; the native gradients are top-down.
                float v = 1f - (y + 0.5f) / height;
                float py = v * heightPoints;
                for (int x = 0; x < width; x++)
                {
                    float px = (x + 0.5f) / width * widthPoints;
                    Color color = Color.black;
                    // Centre glow.
                    float dCenter = Vector2.Distance(
                        new Vector2(px, py),
                        new Vector2(widthPoints * 0.5f, heightPoints * 0.42f));
                    float tCenter = Mathf.Clamp01((dCenter - 24f) / (420f - 24f));
                    float aCenter = tCenter < 0.5f
                        ? Mathf.Lerp(0.42f, 0.16f, tCenter / 0.5f)
                        : Mathf.Lerp(0.16f, 0f, (tCenter - 0.5f) / 0.5f);
                    color = Over(color, accent, aCenter * strength);
                    // Floor glow.
                    float dFloor = Vector2.Distance(
                        new Vector2(px, py),
                        new Vector2(widthPoints * 0.5f, heightPoints * 0.94f));
                    float tFloor = Mathf.Clamp01((dFloor - 12f) / (280f - 12f));
                    color = Over(color, accent, Mathf.Lerp(0.24f, 0f, tFloor) * strength);
                    // Top wash: accent 0.12 → black 0.88 → black 1.0.
                    if (v < 0.5f)
                    {
                        float t = v / 0.5f;
                        Color wash = Color.Lerp(accent, Color.black, t);
                        float a = Mathf.Lerp(0.12f * strength, 0.88f, t);
                        color = Over(color, wash, a);
                    }
                    else
                    {
                        float t = (v - 0.5f) / 0.5f;
                        color = Over(color, Color.black, Mathf.Lerp(0.88f, 1f, t));
                    }
                    color.a = 1f;
                    pixels[y * width + x] = color;
                }
            }
            texture.SetPixels(pixels);
            texture.Apply(false, false);
            return texture;
        }

        private static Color Over(Color under, Color over, float alpha)
        {
            float a = Mathf.Clamp01(alpha);
            return new Color(
                Mathf.Lerp(under.r, over.r, a),
                Mathf.Lerp(under.g, over.g, a),
                Mathf.Lerp(under.b, over.b, a),
                1f);
        }

        public void SetFlash(float opacity, Color color)
        {
            color.a = Mathf.Clamp01(opacity);
            flashMaterial.SetColor(ColorId, color);
            flash.gameObject.SetActive(opacity > 0.001f);
        }

        /// <summary>Radial glow behind the case; radius in metres.</summary>
        public void SetHalo(float opacity, Color color, float radiusMeters, Vector3 caseCenter)
        {
            color.a = Mathf.Clamp01(opacity);
            haloMaterial.SetColor(ColorId, color);
            halo.localScale = new Vector3(radiusMeters * 2f, radiusMeters * 2f, 1f);
            if (camera != null)
            {
                halo.position = caseCenter + camera.transform.forward * 0.06f;
                halo.rotation = camera.transform.rotation;
            }
            halo.gameObject.SetActive(opacity > 0.001f);
        }

        /// <summary>
        /// One burst from the case outline. Speeds are given in screen px/s
        /// and converted with the camera's px-per-metre at the case depth.
        /// </summary>
        public void EmitBurst(
            Vector3 caseCenter,
            Vector2 caseExtentsMeters,
            int count,
            Color color,
            float pixelsPerMeter)
        {
            if (count <= 0 || camera == null) return;
            float ppm = Mathf.Max(pixelsPerMeter, 1f);
            if (particles == null)
            {
                GameObject holder = new GameObject("RevealParticles");
                holder.transform.SetParent(root, false);
                particles = holder.AddComponent<ParticleSystem>();
                ParticleSystemRenderer renderer = holder.GetComponent<ParticleSystemRenderer>();
                // Soft round sparks, not the default square particle.
                sparkTexture ??= BuildRadialTexture(32);
                Material sparkMaterial = new Material(Shader.Find("Sprites/Default"))
                {
                    mainTexture = sparkTexture,
                    renderQueue = 3007
                };
                renderer.material = sparkMaterial;
                renderer.sortingOrder = BackdropSortingOrder + 2;
                renderer.renderMode = ParticleSystemRenderMode.Billboard;
                ParticleSystem.MainModule main = particles.main;
                main.playOnAwake = false;
                main.loop = false;
                main.simulationSpace = ParticleSystemSimulationSpace.World;
                main.startLifetime = new ParticleSystem.MinMaxCurve(0.9f, 1.6f);
                main.startSpeed = 0f;
                main.startSize = new ParticleSystem.MinMaxCurve(
                    7f / ppm,
                    15f / ppm);
                main.gravityModifier = -60f / (ppm * 9.81f);
                main.maxParticles = 512;
                ParticleSystem.EmissionModule emission = particles.emission;
                emission.enabled = false;
                ParticleSystem.ColorOverLifetimeModule colorOverLifetime =
                    particles.colorOverLifetime;
                colorOverLifetime.enabled = true;
                Gradient gradient = new Gradient();
                gradient.SetKeys(
                    new[] { new GradientColorKey(Color.white, 0f), new GradientColorKey(Color.white, 1f) },
                    new[] { new GradientAlphaKey(1f, 0f), new GradientAlphaKey(0f, 1f) });
                colorOverLifetime.color = gradient;
            }
            particles.transform.position = caseCenter;
            particles.transform.rotation = camera.transform.rotation;
            ParticleSystem.EmitParams emitParams = new ParticleSystem.EmitParams();
            for (int index = 0; index < count; index++)
            {
                // Spawn around the case outline with jitter (an even ring
                // reads as a drawn border), travel outward in the screen plane.
                float u = (float)index / count;
                float angle = u * 2f * Mathf.PI + Hash(index) * 0.6f;
                Vector2 direction = new Vector2(Mathf.Cos(angle), Mathf.Sin(angle));
                float radial = Mathf.Lerp(0.82f, 1.12f, Hash(index * 3 + 11));
                Vector2 edge = new Vector2(
                    Mathf.Clamp(direction.x * 1.6f, -1f, 1f) * caseExtentsMeters.x * radial,
                    Mathf.Clamp(direction.y * 1.6f, -1f, 1f) * caseExtentsMeters.y * radial);
                // Spawn slightly toward the camera so the clear shells never
                // hide the burst.
                Vector3 start = caseCenter
                    + camera.transform.right * edge.x
                    + camera.transform.up * edge.y
                    - camera.transform.forward * 0.03f;
                float speed = Mathf.Lerp(260f, 560f, Hash(index * 7 + 3)) / ppm;
                Vector3 velocity =
                    (camera.transform.right * direction.x + camera.transform.up * direction.y)
                    * speed;
                // Brighter core: half-way to white, so the sparks read over
                // the lit cave as well as the dim stage.
                Color spark = Color.Lerp(color, Color.white, 0.45f);
                spark.a = 1f;
                emitParams.position = start;
                emitParams.velocity = velocity;
                emitParams.startColor = spark;
                emitParams.startLifetime = Mathf.Lerp(0.9f, 1.6f, Hash(index * 13 + 5));
                particles.Emit(emitParams, 1);
            }
        }

        public void Dispose()
        {
            DestroyOwned(root != null ? root.gameObject : null);
            DestroyOwned(dimmerMaterial);
            DestroyOwned(flashMaterial);
            DestroyOwned(haloMaterial);
            DestroyOwned(haloTexture);
            DestroyOwned(sparkTexture);
            DestroyOwned(backdropTexture);
        }

        private static float Hash(int index)
        {
            float value = Mathf.Sin(index * 12.9898f + 78.233f) * 43758.5453f;
            return value - Mathf.Floor(value);
        }

        private static Texture2D BuildRadialTexture(int size)
        {
            Texture2D texture = new Texture2D(size, size, TextureFormat.RGBA32, false)
            {
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Bilinear
            };
            Color[] pixels = new Color[size * size];
            float half = (size - 1) * 0.5f;
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    float dx = (x - half) / half;
                    float dy = (y - half) / half;
                    float d = Mathf.Sqrt(dx * dx + dy * dy);
                    float alpha = Mathf.Clamp01(1f - d);
                    alpha *= alpha;
                    pixels[y * size + x] = new Color(1f, 1f, 1f, alpha);
                }
            }
            texture.SetPixels(pixels);
            texture.Apply(false, false);
            return texture;
        }

        private static Transform CreateQuad(Transform parent, string name, Material material, int sortingOrder)
        {
            GameObject quad = GameObject.CreatePrimitive(PrimitiveType.Quad);
            quad.name = name;
            Collider collider = quad.GetComponent<Collider>();
            if (collider != null) DestroyOwned(collider);
            Renderer renderer = quad.GetComponent<Renderer>();
            renderer.sharedMaterial = material;
            renderer.sortingOrder = sortingOrder;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            quad.transform.SetParent(parent, false);
            return quad.transform;
        }

        private readonly Vector3[] frustumCorners = new Vector3[4];

        // Sized from the real frustum corners: the hero camera may use a
        // horizontal FOV axis or physical properties, so 2·d·tan(fov/2) with
        // `fieldOfView` under-sizes the quad (seen as a narrow dark column).
        private void Place(Transform quad, float distance, float coverage)
        {
            if (camera == null || quad == null) return;
            quad.position = camera.transform.position + camera.transform.forward * distance;
            quad.rotation = camera.transform.rotation;
            camera.CalculateFrustumCorners(
                new Rect(0f, 0f, 1f, 1f),
                distance,
                Camera.MonoOrStereoscopicEye.Mono,
                frustumCorners);
            float minX = float.MaxValue, maxX = float.MinValue, minY = float.MaxValue, maxY = float.MinValue;
            for (int i = 0; i < 4; i++)
            {
                minX = Mathf.Min(minX, frustumCorners[i].x);
                maxX = Mathf.Max(maxX, frustumCorners[i].x);
                minY = Mathf.Min(minY, frustumCorners[i].y);
                maxY = Mathf.Max(maxY, frustumCorners[i].y);
            }
            float width = Mathf.Max(0.001f, maxX - minX);
            float height = Mathf.Max(0.001f, maxY - minY);
            // Frustum corners are in camera space; recentre on the view axis.
            quad.position += camera.transform.right * (minX + maxX) * 0.5f
                + camera.transform.up * (minY + maxY) * 0.5f;
            if (coverage > 0f)
            {
                quad.localScale = new Vector3(width * coverage, height * coverage, 1f);
            }
        }

        private static void DestroyOwned(UnityEngine.Object target)
        {
            if (target == null) return;
            if (Application.isPlaying) UnityEngine.Object.Destroy(target);
            else UnityEngine.Object.DestroyImmediate(target);
        }
    }
}
