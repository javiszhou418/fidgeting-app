using UnityEngine;

namespace FidgetingApp.TwoLobeBar.Geometry
{
    /// <summary>
    /// Single runtime/editor source of truth for the graphite two-lobe model.
    /// Unity units are metres and Y is the bearing/spin axis.
    /// </summary>
    public static class TwoLobeBarSpecifications
    {
        public const float BodyLength = 0.050f;
        public const float BodyWidth = 0.018f;
        public const float BodyThickness = 0.013f;
        public const float EdgeFilletRadius = 0.0035f;
        // The reference reads as a long bar with a short rolled/chamfered end,
        // not as a capsule whose semicircular ends consume 18 mm of length.
        public const float EndTransitionLength = 0.0035f;
        public const float EndFaceInset = 0.0023f;
        public const float HalfBodyLength = BodyLength * 0.5f;
        // The reference video shows a continuous shallow crown across the
        // broad body face, not a planar face surrounded by a bevel. A
        // superellipse keeps a generous central crown while rolling smoothly
        // into the side walls without a flat patch or a sharp tangent break.
        public const float BodyCrownExponent = 3.2f;

        public const float ButtonDiameter = 0.024f;
        public const float ButtonRadius = ButtonDiameter * 0.5f;
        public const float ButtonProudHeight = 0.003f;
        public const float ButtonDishDepth = 0.0015f;
        public const float ButtonRimWidth = 0.0012f;
        // A recessed neck supports the finger disc. The full-size disc
        // overhangs this neck, creating a real undercut/shadow gap instead of
        // relying on a painted dark line at the body junction.
        public const float ButtonUndercutRadius = 0.0102f;
        public const float ButtonUndercutReveal = 0.00072f;
        public const float ButtonUndercutSink = 0.00016f;
        public const float ButtonOverhang = ButtonRadius - ButtonUndercutRadius;

        public const float OffsetFromCollinearDegrees = 0f;
        public const float FirstLobeAngleDegrees = 0f;
        public const float SecondLobeAngleDegrees = 180f;

        public const float Metallic = 1f;
        // The photographed zirconium is bead-blasted and deliberately matte.
        // A higher perceptual roughness prevents small, mirror-like hotspots
        // while retaining the broad metallic sheen across the crown.
        public const float Roughness = 0.76f;
        public const float Smoothness = 1f - Roughness;
        public const int GrainTextureSize = 256;

        public const string ModelId = "graphite-two-lobe";
        public const string ScenePath =
            "Assets/_TwoLobeBar/Scenes/TwoLobeBar.unity";

        public static Color BodyBaseColor =>
            new Color32(0x3A, 0x3D, 0x40, 0xFF);
    }
}
