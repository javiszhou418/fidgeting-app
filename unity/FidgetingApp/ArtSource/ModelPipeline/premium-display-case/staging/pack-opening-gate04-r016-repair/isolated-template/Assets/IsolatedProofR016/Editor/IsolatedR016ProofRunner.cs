using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase.IsolatedCandidate.R016;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R016.Editor
{
    public static class IsolatedR016ProofRunner
    {
        private static string ResultsPath => Path.Combine(
            Directory.GetParent(Application.dataPath).FullName,
            "r016-structural-check-results.xml");

        public static void RunStructuralChecks()
        {
            var results = new List<CheckResult>();
            RunCheck(results, "ProfileLocksProofAndCompactSeal", () =>
            {
                Require(
                    IsolatedR016Profile.TotalSeconds >= 1.2f
                    && IsolatedR016Profile.TotalSeconds <= 1.8f,
                    "Proof duration is outside 1.2–1.8 seconds.");
                Require(
                    IsolatedR016Profile.AuthoredPoseProgresses.Length == 7,
                    "R016 must have seven authored poses.");
                Require(
                    IsolatedR016ProofSequence.TopSealHeightFraction >= 0.06f
                    && IsolatedR016ProofSequence.TopSealHeightFraction <= 0.10f,
                    "Released seal strip is outside 6–10 percent Pack height.");
            });
            RunCheck(results, "PackOnlyRigImportsSixBlendShapes", () =>
            {
                GameObject rig = AssetDatabase.LoadAssetAtPath<GameObject>(
                    "Assets/Source/R016/PackOpeningGate04R016PackOnlyRig.fbx");
                Require(rig != null, "R016 Pack-only FBX is missing.");
                SkinnedMeshRenderer[] renderers =
                    rig.GetComponentsInChildren<SkinnedMeshRenderer>(true);
                Require(
                    renderers.Length
                        == IsolatedR016ProofSequence.ExpectedRendererCount,
                    "R016 renderer count is wrong.");
                Require(
                    renderers.All(renderer =>
                        renderer.sharedMesh.blendShapeCount
                            == IsolatedR016ProofSequence.ExpectedBlendShapeCount),
                    "Each Pack-only mesh must have six blend shapes.");
                Require(
                    !rig.GetComponentsInChildren<Transform>(true).Any(item =>
                        item.name.Contains("Case", StringComparison.Ordinal)
                        || item.name.Contains("Prize", StringComparison.Ordinal)),
                    "Pack-only FBX contains case or prize geometry.");
            });
            RunCheck(results, "ReverseProgressRestoresSealedState", () =>
            {
                IsolatedR016ProofSequence sequence =
                    IsolatedR016ProofBuilder.BuildSequenceForTests();
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
                IsolatedR016ProofSequence sequence =
                    IsolatedR016ProofBuilder.BuildSequenceForTests();
                sequence.SetTime(0.94f, false);
                Require(
                    sequence.CurrentSample.Occlusion
                        == IsolatedR016Occlusion.CaseContained,
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
                        == IsolatedR016Occlusion.CaseCrossingMouth,
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
                    "IsolatedProofR016");
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
                    "R016 isolated checks failed. See r016-check-results.xml.");
            }
            Debug.Log($"R016_ISOLATED_CHECKS_PASS count={results.Count}");
        }

        public static void RunPreflight()
        {
            IsolatedR016ProofBuilder.RunPreCaptureStaticTest();
        }

        public static void RunScrub()
        {
            IsolatedR016ProofBuilder.RunScrub();
        }

        public static void RunFullProof()
        {
            IsolatedR016ProofBuilder.RunFullProof();
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
                $"<testsuite name=\"IsolatedR016ProofChecks\" tests=\"{results.Count}\" failures=\"{failures}\" errors=\"0\">"
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
