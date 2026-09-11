using System;
using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    /// <summary>Foil family printed on the plate's rarity block.</summary>
    public enum PremiumDisplayCaseFoilTier
    {
        Steel = 0,
        Copper = 1,
        Silver = 2,
        Gold = 3
    }

    /// <summary>
    /// R005 plate layout: a left text column and a right rarity block
    /// (emblem over tier word) on a holographic graphite plate. The plate
    /// owns two physical rules the R004 text ignored: every printed line
    /// must fit inside the plate, and the foil tint follows rarity.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class PremiumDisplayCaseLabelPlate : MonoBehaviour
    {
        private static readonly int FoilColorId = Shader.PropertyToID("_FoilColor");
        private static readonly int MainTexId = Shader.PropertyToID("_MainTex");

        [SerializeField] private Transform plateFrame;
        [SerializeField] private TextMesh[] leftColumn = Array.Empty<TextMesh>();
        [SerializeField] private TextMesh tierLabel;
        [SerializeField] private MeshRenderer emblemRenderer;
        [SerializeField] private MeshRenderer[] foilRenderers = Array.Empty<MeshRenderer>();
        [SerializeField] private Texture2D[] emblemByTier = new Texture2D[4];
        [SerializeField] private Color[] foilByTier =
        {
            new Color(0.62f, 0.65f, 0.69f, 1f),
            new Color(0.80f, 0.50f, 0.30f, 1f),
            new Color(0.88f, 0.90f, 0.93f, 1f),
            new Color(0.96f, 0.78f, 0.38f, 1f)
        };

        /// <summary>Widest a left-column line may be, in plate-local units.</summary>
        [SerializeField] private float leftColumnMaxWidth;

        /// <summary>Widest the tier word may be, in plate-local units.</summary>
        [SerializeField] private float tierMaxWidth;

        // Property blocks do not serialize; the tier does, so a reloaded
        // scene or prefab can restore the foil tint and emblem.
        [SerializeField] private PremiumDisplayCaseFoilTier appliedTier;

        private float[] authoredLeftSizes = Array.Empty<float>();
        private float authoredTierSize;
        private MaterialPropertyBlock block;

        public PremiumDisplayCaseFoilTier Tier => appliedTier;

        private void OnEnable()
        {
            Font.textureRebuilt += OnFontTextureRebuilt;
            if (IsWired)
            {
                ApplyTier(appliedTier);
            }
        }

        private void OnDisable()
        {
            Font.textureRebuilt -= OnFontTextureRebuilt;
        }

        // A dynamic font atlas is a runtime texture, so a foil-shaded tier
        // word cannot keep it in a serialized material. Re-push it whenever
        // the atlas is rebuilt.
        private void OnFontTextureRebuilt(Font font)
        {
            if (tierLabel != null && tierLabel.font == font && TierWordUsesFoil)
            {
                ApplyTier(appliedTier);
            }
        }

        /// <summary>
        /// True when the tier word's renderer is in the foil set, meaning it
        /// renders through a foil shader that needs the font atlas as
        /// <c>_MainTex</c> instead of the font's own material.
        /// </summary>
        public bool TierWordUsesFoil
        {
            get
            {
                if (tierLabel == null)
                {
                    return false;
                }
                MeshRenderer renderer = tierLabel.GetComponent<MeshRenderer>();
                return renderer != null && Array.IndexOf(foilRenderers, renderer) >= 0;
            }
        }
        public Color FoilColor => foilByTier[(int)Tier];
        public Texture2D Emblem => emblemByTier[(int)Tier];
        public bool IsWired =>
            plateFrame != null
            && leftColumn.Length > 0
            && tierLabel != null
            && emblemRenderer != null
            && leftColumnMaxWidth > 0f
            && tierMaxWidth > 0f;

        public void ConfigureAuthoring(
            Transform frame,
            TextMesh[] column,
            TextMesh tier,
            MeshRenderer emblem,
            MeshRenderer[] foils,
            Texture2D[] emblems,
            float columnMaxWidth,
            float tierWordMaxWidth)
        {
            plateFrame = frame;
            leftColumn = column ?? Array.Empty<TextMesh>();
            tierLabel = tier;
            emblemRenderer = emblem;
            foilRenderers = foils ?? Array.Empty<MeshRenderer>();
            if (emblems == null || emblems.Length != 4)
            {
                throw new ArgumentException(
                    "Plate needs one emblem per foil tier.",
                    nameof(emblems));
            }
            emblemByTier = emblems;
            leftColumnMaxWidth = columnMaxWidth;
            tierMaxWidth = tierWordMaxWidth;
            CaptureAuthoredSizes();
            ApplyTier(PremiumDisplayCaseFoilTier.Steel);
        }

        /// <summary>Registers another renderer that takes the tier foil tint.</summary>
        public void AddFoilRenderer(MeshRenderer renderer)
        {
            if (renderer == null || Array.IndexOf(foilRenderers, renderer) >= 0)
            {
                return;
            }
            Array.Resize(ref foilRenderers, foilRenderers.Length + 1);
            foilRenderers[foilRenderers.Length - 1] = renderer;
            ApplyTier(appliedTier);
        }

        public int FoilRendererCount => foilRenderers.Length;

        /// <summary>
        /// Runs after the presentation has written the label strings. Text
        /// content stays the presentation's job; this only enforces fit and
        /// finish.
        /// </summary>
        public void Apply(PremiumDisplayCaseLabelData data)
        {
            if (!IsWired)
            {
                return;
            }
            CaptureAuthoredSizes();
            ApplyTier(ResolveTier(data.RarityLevel));
            for (int index = 0; index < leftColumn.Length; index++)
            {
                FitWidth(leftColumn[index], authoredLeftSizes[index], leftColumnMaxWidth);
            }
            FitWidth(tierLabel, authoredTierSize, tierMaxWidth);
        }

        /// <summary>
        /// Rarity words arrive upper-cased from the receipt authority. The
        /// mapping is fixed here so a new rarity cannot silently print as
        /// gold.
        /// </summary>
        public static PremiumDisplayCaseFoilTier ResolveTier(string rarityLevel)
        {
            string value = (rarityLevel ?? string.Empty).Trim().ToUpperInvariant();
            switch (value)
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

        /// <summary>Plate-local width of a text line, or 0 when empty.</summary>
        public float MeasureWidth(TextMesh text)
        {
            if (text == null || string.IsNullOrEmpty(text.text) || plateFrame == null)
            {
                return 0f;
            }
            Renderer renderer = text.GetComponent<Renderer>();
            Bounds bounds = renderer.bounds;
            Vector3 right = plateFrame.right;
            // Project the world box onto the plate's X so a tilted case does
            // not inflate the width.
            float width = Mathf.Abs(Vector3.Dot(bounds.size, new Vector3(
                Mathf.Abs(right.x),
                Mathf.Abs(right.y),
                Mathf.Abs(right.z))));
            return width / Mathf.Max(plateFrame.lossyScale.x, 0.000001f);
        }

        public float LeftColumnMaxWidth => leftColumnMaxWidth;
        public float TierMaxWidth => tierMaxWidth;

        private void FitWidth(TextMesh text, float authoredSize, float maxWidth)
        {
            if (text == null)
            {
                return;
            }
            text.characterSize = authoredSize;
            if (string.IsNullOrEmpty(text.text))
            {
                return;
            }
            // Two passes: bounds are exact for the current size, so one
            // ratio lands inside; the second guards rounding.
            for (int pass = 0; pass < 2; pass++)
            {
                float width = MeasureWidth(text);
                if (width <= maxWidth || width <= 0f)
                {
                    return;
                }
                text.characterSize *= maxWidth / width * 0.995f;
            }
        }

        private void ApplyTier(PremiumDisplayCaseFoilTier tier)
        {
            appliedTier = tier;
            block ??= new MaterialPropertyBlock();
            Color foil = foilByTier[(int)tier];
            for (int index = 0; index < foilRenderers.Length; index++)
            {
                MeshRenderer renderer = foilRenderers[index];
                if (renderer == null)
                {
                    continue;
                }
                renderer.GetPropertyBlock(block);
                block.SetColor(FoilColorId, foil);
                renderer.SetPropertyBlock(block);
            }
            if (emblemRenderer != null)
            {
                emblemRenderer.GetPropertyBlock(block);
                block.SetColor(FoilColorId, foil);
                Texture2D emblem = emblemByTier[(int)tier];
                if (emblem != null)
                {
                    block.SetTexture(MainTexId, emblem);
                }
                emblemRenderer.SetPropertyBlock(block);
            }
            if (tierLabel != null)
            {
                Color ink = foil;
                ink.a = tierLabel.color.a;
                tierLabel.color = ink;
                PushFontAtlas();
            }
        }

        private void PushFontAtlas()
        {
            if (!TierWordUsesFoil || tierLabel.font == null || tierLabel.font.material == null)
            {
                return;
            }
            Texture atlas = tierLabel.font.material.mainTexture;
            if (atlas == null)
            {
                return;
            }
            MeshRenderer renderer = tierLabel.GetComponent<MeshRenderer>();
            renderer.GetPropertyBlock(block);
            block.SetTexture(MainTexId, atlas);
            renderer.SetPropertyBlock(block);
        }

        /// <summary>Texture the tier word renderer currently receives as its mask, if any.</summary>
        public Texture TierWordAtlas
        {
            get
            {
                if (tierLabel == null)
                {
                    return null;
                }
                MeshRenderer renderer = tierLabel.GetComponent<MeshRenderer>();
                if (renderer == null)
                {
                    return null;
                }
                block ??= new MaterialPropertyBlock();
                renderer.GetPropertyBlock(block);
                return block.GetTexture(MainTexId);
            }
        }

        private void CaptureAuthoredSizes()
        {
            if (authoredLeftSizes.Length == leftColumn.Length && authoredTierSize > 0f)
            {
                return;
            }
            authoredLeftSizes = new float[leftColumn.Length];
            for (int index = 0; index < leftColumn.Length; index++)
            {
                authoredLeftSizes[index] = leftColumn[index] != null
                    ? leftColumn[index].characterSize
                    : 0f;
            }
            authoredTierSize = tierLabel != null ? tierLabel.characterSize : 0f;
        }
    }
}
