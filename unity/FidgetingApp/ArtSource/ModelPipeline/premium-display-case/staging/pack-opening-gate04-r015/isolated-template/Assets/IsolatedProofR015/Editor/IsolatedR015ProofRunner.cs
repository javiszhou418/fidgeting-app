using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase.IsolatedCandidate.R015;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R015.Editor
{
    public static class IsolatedR015ProofRunner
    {
        private const string ResultsPath =
            "/tmp/FidgetingApp-PackOpening-R014-Isolated-20260831/r015-check-results.xml";

        public static void Run()
        {
            var results = new List<CheckResult>();
            RunCheck(results, "ProfileLocksProofAndCompactSeal", () =>
            {
                Require(
                    IsolatedR015Profile.TotalSeconds >= 1.2f
                    && IsolatedR015Profile.TotalSeconds <= 1.8f,
                    "Proof duration is outside 1.2–1.8 seconds.");
                Require(
                    IsolatedR015Profile.AuthoredPoseProgresses.Length == 7,
                    "R015 must have seven authored poses.");
                Require(
                    IsolatedR015ProofSequence.TopSealHeightFraction >= 0.06f
                    && IsolatedR015ProofSequence.TopSealHeightFraction <= 0.10f,
                    "Released seal strip is outside 6–10 percent Pack height.");
            });
            RunCheck(results, "PackOnlyRigImportsSixBlendShapes", () =>
            {
                GameObject rig = AssetDatabase.LoadAssetAtPath<GameObject>(
                    "Assets/Source/R015/PackOpeningGate04R015PackOnlyRig.fbx");
                Require(rig != null, "R015 Pack-only FBX is missing.");
                SkinnedMeshRenderer[] renderers =
                    rig.GetComponentsInChildren<SkinnedMeshRenderer>(true);
                Require(
                    renderers.Length
                        == IsolatedR015ProofSequence.ExpectedRendererCount,
                    "R015 renderer count is wrong.");
                Require(
                    renderers.All(renderer =>
                        renderer.sharedMesh.blendShapeCount
                            == IsolatedR015ProofSequence.ExpectedBlendShapeCount),
                    "Each Pack-only mesh must have six blend shapes.");
                Require(
                    !rig.GetComponentsInChildren<Transform>(true).Any(item =>
                        item.name.Contains("Case", StringComparison.Ordinal)
                        || item.name.Contains("Prize", StringComparison.Ordinal)),
                    "Pack-only FBX contains case or prize geometry.");
            });
            RunCheck(results, "ReverseProgressRestoresSealedState", () =>
            {
                IsolatedR015ProofSequence sequence =
                    IsolatedR015ProofBuilder.BuildSequenceForTests();
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
                IsolatedR015ProofSequence sequence =
                    IsolatedR015ProofBuilder.BuildSequenceForTests();
                sequence.SetTime(0.94f, false);
                Require(
                    sequence.CurrentSample.Occlusion
                        == IsolatedR015Occlusion.CaseContained,
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
                        == IsolatedR015Occlusion.CaseCrossingMouth,
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
                    "IsolatedProofR015");
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
                    "R015 isolated checks failed. See r015-check-results.xml.");
            }
            Debug.Log($"R015_ISOLATED_CHECKS_PASS count={results.Count}");
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
                $"<testsuite name=\"IsolatedR015ProofChecks\" tests=\"{results.Count}\" failures=\"{failures}\" errors=\"0\">"
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
