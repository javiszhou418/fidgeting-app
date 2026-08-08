using UnityEngine;

namespace FidgetingApp.FanCard
{
    public static class FanCardSpecifications
    {
        public const string ModelId = "magnetic-fan-card";
        public const string ScenePath = "Assets/_FanCard/Scenes/MagneticFanCard.unity";
        public const string ProfilePath =
            "Assets/_FanCard/Generated/FanCardDetentProfile.asset";

        public const float CardWidth = 0.0635f;
        public const float CardHeight = 0.0889f;
        public const float CardThickness = 0.0025f;
        public const float CardCornerRadius = CardWidth * 0.06f;
        public const float EdgeBevel = CardThickness * 0.15f;
        public const float FaceWidth = 0.0587f;
        public const float FaceHeight = 0.0841f;
        public const float FaceCornerRadius = 0.0026f;
        // 2.5 mm slab plus a 3.75 mm face-to-face air gap.
        public const float LayerPitch = 0.00625f;
        public const float InteractionPadding = 0.006f;
        // The top plate is the fixed 0-degree reference. A 90-degree root
        // presentation keeps its spindle opening in the authored lower-right
        // corner while the middle/bottom plates sit at -45/-90 degrees.
        public const float PresentationRotationDegrees = 90f;

        public const float PivotX = CardWidth * 0.5f - CardCornerRadius;
        public const float PivotZ = CardHeight * 0.5f - CardCornerRadius;
        public static readonly Vector3 CardCenterFromPivot =
            new(-PivotX, 0f, -PivotZ);

        // The follower is safely inset toward the lower-left; rotating it by
        // +45 degrees around the pivot stays inside the rounded card boundary.
        public static readonly Vector2 FollowerFromPivot =
            new(-0.0536f, -0.0211f);
        // Open is +90 degrees on the outer/lower plate. Returning from open
        // to closed therefore travels counterclockwise in the authored top
        // view, from 90 degrees back to the fixed top plate's 0 degrees.
        public const float OpeningRotationSign = 1f;
        public const float TrackShellWidth = 0.0062f;
        public const float TrackMeshWidth = 0.00425f;
        // All track hardware is authored on the underside. These offsets are
        // measured outward from the rigid slab's back face so the front view
        // remains completely clean while the back still reads as a machined
        // magnetic mechanism.
        public const float BackTrackUndercutOffset = 0.00018f;
        public const float BackTrackInlayOffset = 0.00023f;
        public const float BackMagnetCenterOffset = 0.00032f;
        public const float MagnetRadius = 0.00165f;
        public const float FollowerBallRadius = 0.00210f;
        // Only this shallow chrome cap sits outside the upper card. Keeping it
        // below the inter-layer air gap prevents the follower from entering
        // the lower plate while the rest of the sphere remains in its seat.
        public const float FollowerBallProtrusion = 0.00070f;
        public const float FollowerSeatRadius = 0.00255f;
        public const float FollowerSeatHeight = 0.00032f;
        public const float AxisOuterRadius = 0.00365f;
        public const float AxisInnerRadius = 0.00255f;
        public const float AxisHoleRadius = 0.00215f;
        public const float AxisHoleBevel = 0.00022f;
        public const float AxisBallRadius = 0.00265f;

        public static readonly Color GunmetalColor =
            new(0.155f, 0.163f, 0.172f, 1f);
        public static readonly Color WarmSilverColor =
            new(0.40f, 0.385f, 0.36f, 1f);
        public static readonly Color EtchingColor =
            new(0.050f, 0.052f, 0.054f, 1f);
        public static readonly Color GrooveColor =
            new(0.018f, 0.020f, 0.022f, 1f);
        public static readonly Color MagnetGoldColor =
            new(0.63f, 0.38f, 0.095f, 1f);

        public const float GunmetalMetallic = 0.90f;
        public const float GunmetalSmoothness = 0.34f;
        public const float SilverMetallic = 1.0f;
        // Satin bead-blasted face: metallic, but deliberately below polished
        // metal so the studio reflection stays broad instead of clipping to a
        // white mirror band in the overhead view.
        public const float SilverSmoothness = 0.36f;
        public const float ChromeSmoothness = 0.92f;
        public const float GrainBumpScale = 0.11f;
    }
}
