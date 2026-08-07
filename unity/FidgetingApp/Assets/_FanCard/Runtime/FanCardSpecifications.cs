using UnityEngine;

namespace FidgetingApp.FanCard
{
    public static class FanCardSpecifications
    {
        public const string ModelId = "magnetic-fan-card";
        public const string ScenePath = "Assets/_FanCard/Scenes/MagneticFanCard.unity";
        public const string ProfilePath =
            "Assets/_FanCard/Generated/FanCardDetentProfile.asset";

        public const float CardWidth = 0.052f;
        public const float CardHeight = 0.074f;
        public const float CardThickness = 0.0026f;
        public const float CardCornerRadius = 0.007f;
        public const float EdgeBevel = 0.00075f;
        public const float FaceWidth = 0.0472f;
        public const float FaceHeight = 0.0692f;
        public const float FaceCornerRadius = 0.0052f;
        public const float FaceThickness = 0.00055f;
        public const float LayerPitch = 0.00335f;
        public const float InteractionPadding = 0.006f;
        public const float PresentationRotationDegrees = 180f;

        public const float PivotX = CardWidth * 0.5f - CardCornerRadius;
        public const float PivotZ = CardHeight * 0.5f - CardCornerRadius;
        public static readonly Vector3 CardCenterFromPivot =
            new(-PivotX, 0f, -PivotZ);

        // The follower is safely inset toward the lower-left; rotating it by
        // -45 degrees around the pivot stays inside the rounded card boundary.
        public static readonly Vector2 FollowerFromPivot =
            new(-0.0134f, -0.0408f);
        public const float TrackShellWidth = 0.0062f;
        public const float TrackMeshWidth = 0.00425f;
        public const float TrackSurfaceHeight = 0.00194f;
        public const float MagnetRadius = 0.00165f;
        public const float FollowerBallRadius = 0.00210f;
        public const float AxisOuterRadius = 0.00365f;
        public const float AxisInnerRadius = 0.00255f;
        public const float AxisBallRadius = 0.00235f;

        public static readonly Color GunmetalColor =
            new(0.135f, 0.142f, 0.150f, 1f);
        public static readonly Color WarmSilverColor =
            new(0.34f, 0.325f, 0.30f, 1f);
        public static readonly Color EtchingColor =
            new(0.050f, 0.052f, 0.054f, 1f);
        public static readonly Color GrooveColor =
            new(0.018f, 0.020f, 0.022f, 1f);
        public static readonly Color MagnetGoldColor =
            new(0.63f, 0.38f, 0.095f, 1f);

        public const float GunmetalMetallic = 0.96f;
        public const float GunmetalSmoothness = 0.18f;
        public const float SilverMetallic = 1.0f;
        // Satin bead-blasted face: metallic, but deliberately below polished
        // metal so the studio reflection stays broad instead of clipping to a
        // white mirror band in the overhead view.
        public const float SilverSmoothness = 0.22f;
        public const float ChromeSmoothness = 0.97f;
        public const float GrainBumpScale = 0.20f;
    }
}
