using System;
using FidgetingApp.Product;
using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    public enum PremiumDisplayCasePocketAnchor
    {
        VisualBoundsCenter = 0,
        MechanicalPivot = 1
    }

    public readonly struct PremiumDisplayCasePocketContentProfile
    {
        public PremiumDisplayCasePocketContentProfile(
            string modelId,
            Vector3 initialEulerAngles,
            PremiumDisplayCasePocketAnchor anchor,
            float fitDiameterMeters,
            float referenceDepthMeters,
            bool constrainScaleByDepth)
        {
            if (string.IsNullOrWhiteSpace(modelId))
            {
                throw new ArgumentException("A pocket profile requires a model id.", nameof(modelId));
            }
            if (fitDiameterMeters <= 0f)
            {
                throw new ArgumentOutOfRangeException(nameof(fitDiameterMeters));
            }
            if (referenceDepthMeters <= 0f)
            {
                throw new ArgumentOutOfRangeException(nameof(referenceDepthMeters));
            }

            ModelId = modelId;
            InitialEulerAngles = initialEulerAngles;
            Anchor = anchor;
            FitDiameterMeters = fitDiameterMeters;
            ReferenceDepthMeters = referenceDepthMeters;
            ConstrainScaleByDepth = constrainScaleByDepth;
        }

        public string ModelId { get; }
        public Vector3 InitialEulerAngles { get; }
        public PremiumDisplayCasePocketAnchor Anchor { get; }
        public float FitDiameterMeters { get; }
        public float ReferenceDepthMeters { get; }
        public bool ConstrainScaleByDepth { get; }
    }

    public readonly struct PremiumDisplayCasePocketFitResult
    {
        public PremiumDisplayCasePocketFitResult(
            float uniformScale,
            float radialExtentMeters,
            float depthMeters,
            Vector3 centerOffsetSlotLocal)
        {
            UniformScale = uniformScale;
            RadialExtentMeters = radialExtentMeters;
            DepthMeters = depthMeters;
            CenterOffsetSlotLocal = centerOffsetSlotLocal;
        }

        public float UniformScale { get; }
        public float RadialExtentMeters { get; }
        public float DepthMeters { get; }
        public Vector3 CenterOffsetSlotLocal { get; }
    }

    /// <summary>
    /// The V3 slab adds one -90 degree X orientation node before ContentFit.
    /// These rotations are therefore local to that node and must not reuse the
    /// older R004 profiles, which already contain their own +/-90 degree pitch.
    /// </summary>
    public static class PremiumDisplayCaseV3PocketProfiles
    {
        public const float FitDiameterMeters = 0.0654f;
        public const float FitDepthMeters = 0.0145f;

        private static readonly PremiumDisplayCasePocketContentProfile[] profiles =
        {
            Profile(
                ProductCatalog.MetalThreeBladeModelId,
                new Vector3(0f, -18f, 0f),
                PremiumDisplayCasePocketAnchor.MechanicalPivot,
                true),
            Profile(
                ProductCatalog.GraphiteTwoLobeModelId,
                new Vector3(0f, -8f, 0f),
                PremiumDisplayCasePocketAnchor.VisualBoundsCenter,
                false),
            Profile(
                ProductCatalog.MagneticSlideTileModelId,
                new Vector3(0f, -8f, 0f),
                PremiumDisplayCasePocketAnchor.VisualBoundsCenter,
                false),
            Profile(
                ProductCatalog.MagneticFanCardModelId,
                new Vector3(0f, -8f, 0f),
                PremiumDisplayCasePocketAnchor.VisualBoundsCenter,
                false)
        };

        public static PremiumDisplayCasePocketContentProfile Resolve(string modelId)
        {
            for (int index = 0; index < profiles.Length; index++)
            {
                if (string.Equals(profiles[index].ModelId, modelId, StringComparison.Ordinal))
                {
                    return profiles[index];
                }
            }

            throw new ArgumentOutOfRangeException(
                nameof(modelId),
                modelId,
                "The V3 slab has no reviewed pocket profile for this model.");
        }

        private static PremiumDisplayCasePocketContentProfile Profile(
            string modelId,
            Vector3 euler,
            PremiumDisplayCasePocketAnchor anchor,
            bool constrainScaleByDepth)
        {
            return new PremiumDisplayCasePocketContentProfile(
                modelId,
                euler,
                anchor,
                FitDiameterMeters,
                FitDepthMeters,
                constrainScaleByDepth);
        }
    }
}
