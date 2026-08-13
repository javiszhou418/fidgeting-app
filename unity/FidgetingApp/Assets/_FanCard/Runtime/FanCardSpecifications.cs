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
        // The warm-silver surface now follows the complete rounded card corner
        // instead of opening a notch from the spindle hole to the outside.
        // A 0.5 mm gunmetal reveal remains around the full perimeter.
        public const float FaceInset = 0.0005f;
        public const float FaceWidth = CardWidth - FaceInset * 2f;
        public const float FaceHeight = CardHeight - FaceInset * 2f;
        public const float FaceCornerRadius = CardCornerRadius - FaceInset;
        // The real mechanism reads as a tight stack. One millimetre of clear
        // air remains visible at a grazing angle without making three 2.5 mm
        // slabs appear disconnected from their shared spindle.
        public const float LayerAirGap = 0.0010f;
        public const float LayerPitch = CardThickness + LayerAirGap;
        public const float InteractionPadding = 0.010f;
        public const float InteractionDepthPadding = 0.004f;
        // Gesture motion is projected onto the tangent of the current three-card
        // visual centroid. The physical layers still rotate around the real
        // spindle, but the user no longer has to draw a circle around a corner.
        public const float GestureTravelGain = 1.08f;
        // Kept only for deterministic migration tests and saved-scene
        // compatibility. Runtime touch input no longer uses corner-pivot arcs.
        public const float PointerAngularGain = 1.25f;
        public const float MaximumGestureProgressPerFrame = 0.24f;
        public const float GestureDistanceStartScreenWidths = 0.018f;
        public const float GestureDistanceFullScreenWidths = 0.28f;
        public const float GestureFrequencyMinimumHertz = 0.25f;
        public const float GestureFrequencyFullHertz = 2.20f;
        public const float GestureFrequencyDecayHalfLifeSeconds = 1.10f;
        public const float GestureSpeedFilterHalfLifeSeconds = 0.035f;
        public const float FastTraversalMinimumDistance = 0.18f;
        // Library artwork shows two of the three opening intervals: the middle
        // plate reaches 30 degrees and the outer plate reaches 60 degrees.
        // This is a presentation override only; the magnetic track retains the
        // user's real captured detent and is restored unchanged in detail view.
        public const int LibraryPreviewDetentIndex = 2;
        public const float LibraryPreviewProgress = 2f / 3f;
        public const float LibraryPreviewRollDegrees = 45f;
        // The bottom plate is the fixed 0-degree reference. A 90-degree root
        // presentation keeps the shared opening in the authored lower-right
        // corner while the middle/top plates fan by 45/90 degrees.
        public const float PresentationRotationDegrees = 90f;

        public const float PivotX = CardWidth * 0.5f - CardCornerRadius;
        public const float PivotZ = CardHeight * 0.5f - CardCornerRadius;
        public static readonly Vector3 CardCenterFromPivot =
            new(-PivotX, 0f, -PivotZ);

        /// <summary>
        /// Stable root-local bounds covering every rigid card pose from 0 to
        /// 90 degrees. The camera uses this instead of following the changing
        /// renderer AABB while a finger is dragging.
        /// </summary>
        public static Bounds VisualSweepBounds => ResolveSweepBounds(0f, 0f);

        // The exact sweep envelope includes the mathematical tangent points of
        // every rounded card. A sub-percent camera-only inset prevents those
        // invisible extrema from making the closed stack miss the repository's
        // minimum viewport-occupancy boundary, while the 20% framing margin
        // still contains the complete 0-90 degree sweep without clipping.
        public const float CameraSweepBoundsScale = 0.992f;
        public static Bounds CameraSweepBounds
        {
            get
            {
                Bounds bounds = VisualSweepBounds;
                bounds.size *= CameraSweepBoundsScale;
                return bounds;
            }
        }

        /// <summary>
        /// Forgiving hit region for the complete fan, including the exposed
        /// middle and bottom cards. It is intentionally independent from the
        /// fixed top card so every visible layer can start the same gesture.
        /// </summary>
        public static Bounds InteractionSweepBounds => ResolveSweepBounds(
            InteractionPadding,
            InteractionDepthPadding);

        // The follower is intentionally inset toward the lower-left. The
        // complete 6.2 mm undercut contour must keep at least 6 mm of metal
        // between itself and the rounded card outline across the full sweep.
        public static readonly Vector2 FollowerFromPivot =
            new(-0.0490f, -0.0270f);
        // Open is +90 degrees on the outer/lower plate. Returning from open
        // to closed therefore travels counterclockwise in the authored top
        // view, from 90 degrees back to the fixed top plate's 0 degrees.
        public const float OpeningRotationSign = 1f;
        public const float TrackShellWidth = 0.0062f;
        public const float TrackMeshWidth = 0.00425f;
        public const float MinimumTrackOuterEdgeClearance = 0.0060f;
        public const string BackMechanismModelPath =
            "Assets/_FanCard/Models/FanCardBackMechanism.fbx";
        // Unity splits Blender's 3510 source vertices at hard-normal seams;
        // the imported shipping mesh therefore has 4095 render vertices.
        public const int TrackGridExpectedVertexCount = 4095;
        public const int TrackGridExpectedTriangleCount = 6048;
        // All track hardware is authored on the underside. These offsets are
        // measured outward from the rigid slab's back face so the front view
        // remains completely clean while the back still reads as a machined
        // magnetic mechanism.
        public const float BackTrackUndercutOffset = 0.00018f;
        // The grille sits just outward of the magnet caps. Its real openings,
        // rather than a transparent texture, reveal the three inserts below.
        public const float BackTrackInlayOffset = 0.00046f;
        public const float BackMagnetCenterOffset = 0.00032f;
        public const float MagnetRadius = 0.00165f;
        // Followers belong to the hidden back mechanism. Their shallow exposed
        // cap remains inside the tightened gap and never punches through the
        // front face as an unexplained chrome dot.
        public const float FollowerBallRadius = 0.00100f;
        public const float FollowerBallProtrusion = 0.00045f;
        public const float FollowerSeatRadius = 0.00135f;
        public const float FollowerSeatHeight = 0.00022f;
        public const float AxisOuterRadius = 0.00365f;
        public const float AxisInnerRadius = 0.00255f;
        public const float AxisHoleRadius = 0.00215f;
        public const float AxisHoleBevel = 0.00022f;
        // The shaft nearly fills the through-hole but remains below the face.
        // This leaves one intentional mechanical shadow gap instead of the
        // layered bright crescents that previously read as a floating ring.
        public const float RecessedSpindleRadius = 0.00200f;
        public const float RecessedSpindleTopInset = 0.00012f;
        public const float BearingCapRadius = 0.00207f;
        public const float BearingCapHeight = 0.00065f;

        // Standard playing-card corner indices: one upright pair at the
        // upper-left and one 180-degree pair at the lower-right. The active
        // A/Q/K rank and its small spade share the same orientation in each
        // corner. Runtime patterns are selected as a complete three-card set;
        // individual layers are never randomized independently.
        public const int CornerIndexCountPerFront = 2;
        public const string TripleAcePatternId = "AAA";
        public const string QueenKingAcePatternId = "QKA";
        public const float TripleAcePatternProbability = 0.5f;
        public static readonly Vector2 CornerTopLeftRankOffset =
            new(-0.0172f, 0.0250f);
        public static readonly Vector2 CornerTopLeftSpadeOffset =
            new(-0.0146f, 0.0169f);
        public static readonly Vector2 CornerBottomRightRankOffset =
            new(0.0172f, -0.0250f);
        public static readonly Vector2 CornerBottomRightSpadeOffset =
            new(0.0146f, -0.0169f);
        public const float CornerTopLeftRotationDegrees = 0f;
        public const float CornerBottomRightRotationDegrees = 180f;
        public const float CornerSpadeScale = 0.245f;

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

        private static Bounds ResolveSweepBounds(
            float planarPadding,
            float depthPadding)
        {
            float halfWidth = CardWidth * 0.5f;
            float halfHeight = CardHeight * 0.5f;
            float minimumX = float.PositiveInfinity;
            float maximumX = float.NegativeInfinity;
            float minimumZ = float.PositiveInfinity;
            float maximumZ = float.NegativeInfinity;

            // One-degree sampling is conservative once the explicit padding
            // is applied, and keeps the authored bounds deterministic in both
            // editor scene generation and runtime tests.
            for (int degrees = 0; degrees <= 90; degrees++)
            {
                Quaternion rotation = Quaternion.Euler(
                    0f,
                    OpeningRotationSign * degrees,
                    0f);
                for (int xSign = -1; xSign <= 1; xSign += 2)
                {
                    for (int zSign = -1; zSign <= 1; zSign += 2)
                    {
                        Vector3 corner = CardCenterFromPivot + new Vector3(
                            halfWidth * xSign,
                            0f,
                            halfHeight * zSign);
                        Vector3 rotated = rotation * corner;
                        minimumX = Mathf.Min(minimumX, rotated.x);
                        maximumX = Mathf.Max(maximumX, rotated.x);
                        minimumZ = Mathf.Min(minimumZ, rotated.z);
                        maximumZ = Mathf.Max(maximumZ, rotated.z);
                    }
                }
            }

            float minimumY = -CardThickness * 0.5f
                - FollowerBallProtrusion;
            float maximumY = LayerPitch * 2f
                + CardThickness * 0.5f
                + FollowerBallProtrusion;
            Vector3 padding = new(
                Mathf.Max(0f, planarPadding) * 0.5f,
                Mathf.Max(0f, depthPadding) * 0.5f,
                Mathf.Max(0f, planarPadding) * 0.5f);
            Vector3 minimum = new Vector3(minimumX, minimumY, minimumZ)
                - padding;
            Vector3 maximum = new Vector3(maximumX, maximumY, maximumZ)
                + padding;
            Bounds bounds = new((minimum + maximum) * 0.5f, maximum - minimum);
            return bounds;
        }
    }
}
