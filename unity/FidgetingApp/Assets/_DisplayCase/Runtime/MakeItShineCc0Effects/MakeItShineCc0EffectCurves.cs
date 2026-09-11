using UnityEngine;

namespace FidgetingApp.DisplayCase.MakeItShineCc0
{
    public static class MakeItShineCc0EffectCurves
    {
        public const string SourceRepository =
            "https://github.com/remi-chapelain/Unite2025-MakeItShine-Release";
        public const string SourceCommit =
            "88842be0063b5b0b75e82ed6572752a37a13c82b";
        public const string DiscardCurveSha256 =
            "be661fe81b095f7f1ad08fb2a1c003b15f8690ee08d43f9f705dc849924fb2c6";

        public static AnimationCurve CreateDiscardDissolveCurve()
        {
            return new AnimationCurve(
                new Keyframe(0f, 0f, 0f, 0f),
                new Keyframe(
                    0.6166667f,
                    0.37030068f,
                    1.4681917f,
                    1.4681917f),
                new Keyframe(
                    1f,
                    1f,
                    0.1272332f,
                    0.1272332f));
        }

        public static bool MatchesDiscardDissolveCurve(
            AnimationCurve candidate,
            float tolerance = 0.00001f)
        {
            if (candidate == null)
            {
                return false;
            }
            AnimationCurve expected = CreateDiscardDissolveCurve();
            if (candidate.length != expected.length)
            {
                return false;
            }
            for (int index = 0; index < expected.length; index++)
            {
                Keyframe actualKey = candidate.keys[index];
                Keyframe expectedKey = expected.keys[index];
                if (Mathf.Abs(actualKey.time - expectedKey.time) > tolerance
                    || Mathf.Abs(actualKey.value - expectedKey.value) > tolerance
                    || Mathf.Abs(actualKey.inTangent - expectedKey.inTangent)
                        > tolerance
                    || Mathf.Abs(actualKey.outTangent - expectedKey.outTangent)
                        > tolerance)
                {
                    return false;
                }
            }
            return true;
        }
    }
}
