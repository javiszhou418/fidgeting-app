using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase.IsolatedCandidate.R019;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R019.Editor
{
    public static class IsolatedR019ProofRunner
    {
        private static string ResultsPath => Path.Combine(
            Directory.GetParent(Application.dataPath).FullName,
            "r019-structural-check-results.xml");

        public static void RunStructuralChecks()
        {
            var results = new List<CheckResult>();
            RunCheck(results, "ProfileLocksProofAndCompactSeal", () =>
            {
                Require(
                    IsolatedR019Profile.TotalSeconds >= 1.2f
                    && IsolatedR019Profile.TotalSeconds <= 1.8f,
                    "Proof duration is outside 1.2–1.8 seconds.");
                Require(
                    IsolatedR019Profile.AuthoredPoseProgresses.Length == 7,
                    "R019 must have seven authored poses.");
                Require(
                    IsolatedR019ProofSequence.TopSealHeightFraction >= 0.015f
                    && IsolatedR019ProofSequence.TopSealHeightFraction <= 0.030f,
                    "Top crimp is outside the thin 1.5–3 percent Pack-height band.");
                Require(
                    IsolatedR019ProofSequence.ReleasedStripHeightFraction >= 0.035f
                    && IsolatedR019ProofSequence.ReleasedStripHeightFraction <= 0.065f,
                    "Released strip is outside the narrow 3.5–6.5 percent Pack-height band.");
            });
            RunCheck(results, "RightStripRuleRejectsR018LeftSideFixture", () =>
            {
                Require(
                    !IsolatedR019Preflight.MeetsTopRightStripBoundsForTesting(
                        new Rect(0.312724f, 0.239136f, 0.374552f, 0.529367f),
                        new Rect(0.313002f, 0.648468f, 0.373997f, 0.133325f),
                        new Rect(0.309498f, 0.733028f, 0.078143f, 0.079429f),
                        new Rect(0.300067f, 0.763760f, 0.050580f, 0.059746f),
                        new Vector2(0.330f, 0.770f)),
                    "The actual R018 left-side strip must fail the R019 rule.");
            });
            RunCheck(results, "PackOnlyRigImportsSixBlendShapes", () =>
            {
                GameObject rig = AssetDatabase.LoadAssetAtPath<GameObject>(
                    "Assets/Source/R019/PackOpeningGate04R019PackOnlyRig.fbx");
                Require(rig != null, "R019 Pack-only FBX is missing.");
                SkinnedMeshRenderer[] renderers =
                    rig.GetComponentsInChildren<SkinnedMeshRenderer>(true);
                Require(
                    renderers.Length
                        == IsolatedR019ProofSequence.ExpectedRendererCount,
                    "R019 renderer count is wrong.");
                Require(
                    renderers.All(renderer =>
                        renderer.sharedMesh.blendShapeCount
                            == IsolatedR019ProofSequence.ExpectedBlendShapeCount),
                    "Each Pack-only mesh must have six blend shapes.");
                Require(
                    !rig.GetComponentsInChildren<Transform>(true).Any(item =>
                        item.name.Contains("Case", StringComparison.Ordinal)
                        || item.name.Contains("Prize", StringComparison.Ordinal)),
                    "Pack-only FBX contains case or prize geometry.");
            });
            RunCheck(results, "ReverseProgressRestoresSealedState", () =>
            {
                IsolatedR019ProofSequence sequence =
                    IsolatedR019ProofBuilder.BuildSequenceForTests();
                string sealedState = sequence.SealedStateFingerprint;
                sequence.SetNormalizedTearProgress(0.28f);
                Require(sequence.PackVisible, "Pack disappears during resistance.");
                sequence.SetNormalizedTearProgress(0.86f);
                Require(
                    sequence.MouthContactOcclusionActive,
                    "Physical lip is missing at containment.");
                Require(
                    sequence.ReboundToSealed(),
                    "Reverse progress did not restore sealed state.");
                Require(
                    sequence.CurrentStateFingerprint == sealedState,
                    "Sealed state fingerprint drifted after rebound.");
            });
            RunCheck(results, "OneLiveCaseStaysContainedBeforeRise", () =>
            {
                IsolatedR019ProofSequence sequence =
                    IsolatedR019ProofBuilder.BuildSequenceForTests();
                sequence.SetTime(0.94f, false);
                Require(
                    sequence.CurrentSample.Occlusion
                        == IsolatedR019Occlusion.CaseContained,
                    "Case did not enter contained state.");
                Require(
                    sequence.IsCaseContainedInMouth(),
                    "Case depth or lip state does not prove containment.");
                EntityId root = sequence.CaseRootId;
                EntityId[] renderers = sequence.CaseRendererIds.ToArray();
                Vector3 scale = sequence.CaseAuthoredScale;
                sequence.SetTime(1.16f, false);
                Require(
                    sequence.CurrentSample.Occlusion
                        == IsolatedR019Occlusion.CaseCrossingMouth,
                    "Case did not cross the same mouth.");
                Require(
                    sequence.CaseRootId.Equals(root)
                    && sequence.CaseRendererIds.SequenceEqual(renderers),
                    "Case identity changed during extraction.");
                Require(
                    sequence.CaseMotionRootScale == scale,
                    "Case scale changed during extraction.");
            });
            RunCheck(results, "CandidateExcludesForbiddenPorts", () =>
            {
                string root = Path.Combine(
                    Application.dataPath,
                    "IsolatedProofR019");
                string source = string.Join(
                    "\n",
                    Directory.GetFiles(root, "*.*", SearchOption.AllDirectories)
                        .Where(path =>
                            !path.Contains(
                                $"{Path.DirectorySeparatorChar}Tests{Path.DirectorySeparatorChar}",
                                StringComparison.Ordinal)
                            && (path.EndsWith(".cs", StringComparison.Ordinal)
                                || path.EndsWith(".shader", StringComparison.Ordinal)))
                        .Select(File.ReadAllText));
                Require(
                    !source.Contains("Particle" + "System", StringComparison.Ordinal),
                    "Particle port is forbidden.");
                Require(
                    !source.Contains("UnityEngine." + "VFX", StringComparison.Ordinal),
                    "VFX Graph port is forbidden.");
                Require(
                    !source.Contains("Ios" + "Haptics", StringComparison.Ordinal),
                    "Direct haptics port is forbidden.");
                Require(
                    !source.Contains("ProductPrimary" + "ActionButton", StringComparison.Ordinal),
                    "Business CTA is forbidden.");
            });

            WriteResults(results);
            if (results.Any(result => !result.Passed))
            {
                throw new InvalidOperationException(
                    "R019 isolated checks failed. See r019-check-results.xml.");
            }
            Debug.Log($"R019_ISOLATED_CHECKS_PASS count={results.Count}");
        }

        public static void RunPreflight()
        {
            IsolatedR019ProofBuilder.RunPreCaptureStaticTest();
        }

        public static void RunScrub()
        {
            IsolatedR019ProofBuilder.RunScrub();
        }

        public static void RunFullProof()
        {
            IsolatedR019ProofBuilder.RunFullProof();
        }

        private static void RunCheck(
            ICollection<CheckResult> results,
            string name,
            Action action)
        {
            try
            {
                action();
                results.Add(new CheckResult(name, true, string.Empty));
            }
            catch (Exception exception)
            {
                results.Add(new CheckResult(name, false, exception.Message));
            }
        }

        private static void Require(bool condition, string message)
        {
            if (!condition)
            {
                throw new InvalidOperationException(message);
            }
        }

        private static void WriteResults(IReadOnlyList<CheckResult> results)
        {
            int failures = results.Count(result => !result.Passed);
            var lines = new List<string>
            {
                "<?xml version=\"1.0\" encoding=\"utf-8\"?>",
                $"<testsuite name=\"IsolatedR019ProofChecks\" tests=\"{results.Count}\" failures=\"{failures}\" errors=\"0\">"
            };
            foreach (CheckResult result in results)
            {
                if (result.Passed)
                {
                    lines.Add($"  <testcase name=\"{Escape(result.Name)}\" />");
                }
                else
                {
                    lines.Add($"  <testcase name=\"{Escape(result.Name)}\"><failure message=\"{Escape(result.Message)}\" /></testcase>");
                }
            }
            lines.Add("</testsuite>");
            File.WriteAllText(ResultsPath, string.Join("\n", lines) + "\n");
        }

        private static string Escape(string value)
        {
            return value.Replace("&", "&amp;")
                .Replace("\"", "&quot;")
                .Replace("<", "&lt;")
                .Replace(">", "&gt;");
        }

        private readonly struct CheckResult
        {
            public CheckResult(string name, bool passed, string message)
            {
                Name = name;
                Passed = passed;
                Message = message;
            }

            public string Name { get; }
            public bool Passed { get; }
            public string Message { get; }
        }
    }
}
