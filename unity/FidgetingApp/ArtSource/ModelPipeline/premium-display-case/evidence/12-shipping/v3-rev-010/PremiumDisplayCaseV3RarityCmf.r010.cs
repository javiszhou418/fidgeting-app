using System;
using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    /// <summary>
    /// V3 slab rarity CMF. It changes physical material zones through property
    /// blocks; geometry, toy scale, lighting and mechanism stay unchanged.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class PremiumDisplayCaseV3RarityCmf : MonoBehaviour
    {
        private static readonly int BaseColorId = Shader.PropertyToID("_BaseColor");
        private static readonly int TextColorId = Shader.PropertyToID("_Color");

        [SerializeField] private Renderer headerPlate;
        [SerializeField] private Renderer[] linerRenderers = Array.Empty<Renderer>();
        [SerializeField] private Renderer[] frameRenderers = Array.Empty<Renderer>();
        [SerializeField] private Renderer[] polishedRenderers = Array.Empty<Renderer>();
        [SerializeField] private Renderer[] accentRenderers = Array.Empty<Renderer>();
        [SerializeField] private Renderer rarityTextRenderer;
        [SerializeField] private Renderer labelRuleRenderer;
        [SerializeField] private PremiumDisplayCaseFoilTier appliedTier;

        public PremiumDisplayCaseFoilTier Tier => appliedTier;
        public bool IsWired =>
            headerPlate != null
            && linerRenderers.Length > 0
            && frameRenderers.Length > 0
            && polishedRenderers.Length > 0
            && accentRenderers.Length > 0
            && rarityTextRenderer != null
            && labelRuleRenderer != null;

        public void Configure(
            Renderer authoredHeaderPlate,
            Renderer[] authoredLinerRenderers,
            Renderer[] authoredFrameRenderers,
            Renderer[] authoredPolishedRenderers,
            Renderer[] authoredAccentRenderers,
            Renderer authoredRarityTextRenderer,
            Renderer authoredLabelRuleRenderer)
        {
            headerPlate = authoredHeaderPlate;
            linerRenderers = authoredLinerRenderers ?? Array.Empty<Renderer>();
            frameRenderers = authoredFrameRenderers ?? Array.Empty<Renderer>();
            polishedRenderers = authoredPolishedRenderers ?? Array.Empty<Renderer>();
            accentRenderers = authoredAccentRenderers ?? Array.Empty<Renderer>();
            rarityTextRenderer = authoredRarityTextRenderer;
            labelRuleRenderer = authoredLabelRuleRenderer;
            ApplyTier(appliedTier);
        }

        public void Apply(string rarityLevel)
        {
            ApplyTier(ResolveTier(rarityLevel));
        }

        public static PremiumDisplayCaseFoilTier ResolveTier(string rarityLevel)
        {
            string normalized = (rarityLevel ?? string.Empty).Trim().ToUpperInvariant();
            switch (normalized)
            {
                case "HEIRLOOM":
                    return PremiumDisplayCaseFoilTier.Gold;
                case "SIGNATURE":
                    return PremiumDisplayCaseFoilTier.Silver;
                case "REFINED":
                    return PremiumDisplayCaseFoilTier.Copper;
                default:
                    return PremiumDisplayCaseFoilTier.Steel;
            }
        }

        public static Color AccentSrgb(PremiumDisplayCaseFoilTier tier)
        {
            switch (tier)
            {
                case PremiumDisplayCaseFoilTier.Copper:
                    return new Color(0.70f, 0.58f, 0.52f, 1f);
                case PremiumDisplayCaseFoilTier.Silver:
                    return new Color(0.58f, 0.63f, 0.70f, 1f);
                case PremiumDisplayCaseFoilTier.Gold:
                    return new Color(0.80f, 0.73f, 0.60f, 1f);
                default:
                    return new Color(0.62f, 0.65f, 0.69f, 1f);
            }
        }

        public static Color LinerSrgb(PremiumDisplayCaseFoilTier tier)
        {
            switch (tier)
            {
                case PremiumDisplayCaseFoilTier.Copper:
                    return new Color(0.90f, 0.86f, 0.84f, 1f);
                case PremiumDisplayCaseFoilTier.Silver:
                    return new Color(0.86f, 0.88f, 0.93f, 1f);
                case PremiumDisplayCaseFoilTier.Gold:
                    return new Color(0.90f, 0.88f, 0.90f, 1f);
                default:
                    return new Color(0.86f, 0.88f, 0.92f, 1f);
            }
        }

        /// <summary>
        /// Header values are the R010 proposal requested after FDB-DSP-063.
        /// They remain near-black so rarity never becomes a flat color card.
        /// </summary>
        public static Color HeaderSrgb(PremiumDisplayCaseFoilTier tier)
        {
            switch (tier)
            {
                case PremiumDisplayCaseFoilTier.Copper:
                    return new Color(0.085f, 0.052f, 0.043f, 1f);
                case PremiumDisplayCaseFoilTier.Silver:
                    return new Color(0.043f, 0.055f, 0.078f, 1f);
                case PremiumDisplayCaseFoilTier.Gold:
                    return new Color(0.082f, 0.068f, 0.044f, 1f);
                default:
                    return new Color(0.038f, 0.045f, 0.058f, 1f);
            }
        }

        private void OnEnable()
        {
            if (IsWired)
            {
                ApplyTier(appliedTier);
            }
        }

        private void ApplyTier(PremiumDisplayCaseFoilTier tier)
        {
            appliedTier = tier;
            if (!IsWired)
            {
                return;
            }

            Color accent = AccentSrgb(tier).linear;
            Color liner = LinerSrgb(tier).linear;
            Color header = HeaderSrgb(tier).linear;
            SetBaseColor(headerPlate, header, false);
            SetBaseColor(linerRenderers, liner, true);
            SetBaseColor(frameRenderers, accent, false);
            SetBaseColor(polishedRenderers, accent, false);
            SetBaseColor(accentRenderers, accent, false);
            SetTextColor(rarityTextRenderer, accent);
            SetBaseColor(labelRuleRenderer, accent, false);
        }

        private static void SetBaseColor(
            Renderer[] renderers,
            Color color,
            bool preserveMaterialAlpha)
        {
            for (int index = 0; index < renderers.Length; index++)
            {
                SetBaseColor(renderers[index], color, preserveMaterialAlpha);
            }
        }

        private static void SetBaseColor(
            Renderer renderer,
            Color color,
            bool preserveMaterialAlpha)
        {
            if (renderer == null)
            {
                return;
            }
            if (preserveMaterialAlpha
                && renderer.sharedMaterial != null
                && renderer.sharedMaterial.HasProperty(BaseColorId))
            {
                color.a = renderer.sharedMaterial.GetColor(BaseColorId).a;
            }

            var block = new MaterialPropertyBlock();
            renderer.GetPropertyBlock(block);
            block.SetColor(BaseColorId, color);
            renderer.SetPropertyBlock(block);
        }

        private static void SetTextColor(Renderer renderer, Color color)
        {
            if (renderer == null)
            {
                return;
            }

            var block = new MaterialPropertyBlock();
            renderer.GetPropertyBlock(block);
            block.SetColor(TextColorId, color);
            renderer.SetPropertyBlock(block);
        }
    }
}
