using FidgetingApp.DisplayCase;

namespace FidgetingApp.Product.Gacha
{
    public static class GachaRevealRules
    {
        public const PremiumDisplayCaseCapsulePreset SharedCapsulePreset =
            PremiumDisplayCaseCapsulePreset.CollectorSlabCompact;

        /// <summary>
        /// The camera and outer case shell are both fixed-size; only this
        /// uniform root scale controls how much of the viewport the settled
        /// case occupies. Stays well clear of
        /// <see cref="PremiumDisplayCaseCameraRules.MinimumCaseViewportSpan"/>.
        /// </summary>
        public const float CaseViewportScale = 0.62f;

        public static PremiumDisplayCaseCapsulePreset CapsulePresetFor(GachaPrizeKind kind)
        {
            _ = kind;
            return SharedCapsulePreset;
        }

        public static float TotalRevealSeconds(GachaRarity rarity)
        {
            _ = rarity;
            return GachaRevealTimeline.TotalSeconds;
        }
    }
}
