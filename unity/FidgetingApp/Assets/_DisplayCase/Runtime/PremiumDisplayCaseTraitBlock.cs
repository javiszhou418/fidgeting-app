using System;
using FidgetingApp.Product;
using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    /// <summary>
    /// The three printed trait bars in the lower half of the certificate
    /// card. Rows are authored at full width; this component shortens each
    /// fill to its value and writes the number, so one authored layout serves
    /// every toy.
    ///
    /// The block only draws. <see cref="ToyTalentCatalog"/> owns the values,
    /// and the budget invariant is enforced there, not here.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class PremiumDisplayCaseTraitBlock : MonoBehaviour
    {
        [SerializeField] private Transform[] fills = Array.Empty<Transform>();
        [SerializeField] private TextMesh[] values = Array.Empty<TextMesh>();
        [SerializeField] private TextMesh budgetLabel;

        /// <summary>Authored full-width fill extents, captured at 100%.</summary>
        [SerializeField] private float[] authoredWidths = Array.Empty<float>();
        [SerializeField] private float[] leftEdges = Array.Empty<float>();

        [SerializeField] private string appliedToyId = string.Empty;
        [SerializeField] private int[] appliedValues = new int[ToyTalentCatalog.AxisCount];

        public string AppliedToyId => appliedToyId;

        public bool IsWired =>
            fills.Length == ToyTalentCatalog.AxisCount
            && values.Length == ToyTalentCatalog.AxisCount
            && authoredWidths.Length == ToyTalentCatalog.AxisCount
            && leftEdges.Length == ToyTalentCatalog.AxisCount;

        public int AppliedValue(ToyTalentAxis axis) => appliedValues[(int)axis];

        /// <summary>Fraction of the authored track a row currently fills.</summary>
        public float FilledFraction(ToyTalentAxis axis)
        {
            int index = (int)axis;
            if (!IsWired || authoredWidths[index] <= 0f)
            {
                return 0f;
            }

            return fills[index].localScale.x / authoredWidths[index];
        }

        /// <summary>
        /// Registers rows authored at 100% width. Order must be Spin, Feel,
        /// Craft so a row cannot silently print another axis's number.
        /// </summary>
        public void ConfigureAuthoring(Transform[] rowFills, TextMesh[] rowValues, TextMesh budget)
        {
            if (rowFills == null || rowFills.Length != ToyTalentCatalog.AxisCount)
            {
                throw new ArgumentException(
                    "Trait block needs one fill per axis.", nameof(rowFills));
            }
            if (rowValues == null || rowValues.Length != ToyTalentCatalog.AxisCount)
            {
                throw new ArgumentException(
                    "Trait block needs one number per axis.", nameof(rowValues));
            }

            fills = rowFills;
            values = rowValues;
            budgetLabel = budget;
            authoredWidths = new float[ToyTalentCatalog.AxisCount];
            leftEdges = new float[ToyTalentCatalog.AxisCount];
            for (int index = 0; index < ToyTalentCatalog.AxisCount; index++)
            {
                float width = rowFills[index].localScale.x;
                authoredWidths[index] = width;
                leftEdges[index] = rowFills[index].localPosition.x - width * 0.5f;
            }
        }

        public void Apply(ToyTalentProfile profile)
        {
            if (!profile.IsAuthoritative)
            {
                throw new ArgumentException(
                    "Trait profiles must name a toy and spend the full talent budget.",
                    nameof(profile));
            }
            if (!IsWired)
            {
                throw new MissingReferenceException(
                    "Trait block was never authored with its three rows.");
            }

            for (int index = 0; index < ToyTalentCatalog.AxisCount; index++)
            {
                int value = profile.Value((ToyTalentAxis)index);
                appliedValues[index] = value;
                float width = authoredWidths[index]
                    * value / ToyTalentCatalog.AxisMaximum;
                Transform fill = fills[index];
                Vector3 scale = fill.localScale;
                scale.x = width;
                fill.localScale = scale;
                Vector3 position = fill.localPosition;
                position.x = leftEdges[index] + width * 0.5f;
                fill.localPosition = position;
                // A zero-width quad still renders a hairline seam.
                fill.gameObject.SetActive(width > 0f);
                values[index].text = value.ToString("00");
            }

            if (budgetLabel != null)
            {
                budgetLabel.text = profile.Total
                    + " / " + ToyTalentCatalog.AxisMaximum * ToyTalentCatalog.AxisCount;
            }
            appliedToyId = profile.ToyId;
        }
    }
}
