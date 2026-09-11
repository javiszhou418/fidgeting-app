using System;
using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase.MakeItShineCc0;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Candidates.Tests
{
    public sealed class PackOpeningGate04R014Tests
    {
        private PackOpeningGate04R014Profile profile;

        [SetUp]
        public void SetUp()
        {
            profile = ScriptableObject.CreateInstance<
                PackOpeningGate04R014Profile>();
        }

        [TearDown]
        public void TearDown()
        {
            UnityEngine.Object.DestroyImmediate(profile);
        }

        [Test]
        public void ProofDurationAndAuthoredPoseCount_AreLocked()
        {
            Assert.That(
                PackOpeningGate04R014Profile.TotalSeconds,
                Is.InRange(1.2f, 1.8f));
            Assert.That(
                PackOpeningGate04R014Profile.AuthoredPoseProgresses.Length,
                Is.EqualTo(7));
            Assert.That(
                PackOpeningGate04R014Sequence.TopSealHeightFraction,
                Is.InRange(0.06f - 0.00001f, 0.10f));
            Assert.That(
                PackOpeningGate04R014Sequence.MouthDepthMeters,
                Is.GreaterThan(0.04f));
        }

        [Test]
        public void SourceDiscardCurve_RemainsExact()
        {
            AnimationCurve curve =
                MakeItShineCc0EffectCurves.CreateDiscardDissolveCurve();
            Assert.That(
                MakeItShineCc0EffectCurves.MatchesDiscardDissolveCurve(curve),
                Is.True);
            PackOpeningGate04R014Sample sample = profile.Evaluate(
                Mathf.Lerp(
                    PackOpeningGate04R014Profile.PackDiscardStart,
                    PackOpeningGate04R014Profile.PackDiscardEnd,
                    0.6166667f));
            Assert.That(
                sample.PackDissolve,
                Is.EqualTo(0.37030068f).Within(0.00001f));
        }

        [Test]
        public void BlenderRig_ImportsSevenHandAuthoredPackOnlyPoses()
        {
            GameObject rig = AssetDatabase.LoadAssetAtPath<GameObject>(
                Editor.PackOpeningGate04R014Builder.RigPath);
            Assert.That(rig, Is.Not.Null);
            SkinnedMeshRenderer[] renderers = rig.GetComponentsInChildren<
                SkinnedMeshRenderer>(true);
            Assert.That(renderers.Length, Is.EqualTo(10));
            Assert.That(renderers.Sum(renderer =>
                renderer.sharedMesh.blendShapeCount), Is.EqualTo(60));
            foreach (SkinnedMeshRenderer renderer in renderers)
            {
                foreach (string pose in new[]
                         {
                             "Pose_TabCatch",
                             "Pose_NarrowPeel",
                             "Pose_TearAdvance",
                             "Pose_FormedMouth",
                             "Pose_CaseContained",
                             "Pose_ContinuousRise"
                         })
                {
                    Assert.That(
                        renderer.sharedMesh.GetBlendShapeIndex(pose),
                        Is.GreaterThanOrEqualTo(0));
                }
            }
            Assert.That(
                rig.GetComponentsInChildren<Transform>(true).Any(item =>
                    item.name.Contains("Case", StringComparison.Ordinal)
                    || item.name.Contains("Prize", StringComparison.Ordinal)),
                Is.False);
        }

        [Test]
        public void Scene_UsesOneLiveCaseAndCallerOwnedContent()
        {
            PackOpeningGate04R014Sequence sequence = OpenSequence();
            Transform[] transforms = AllTransforms(sequence.gameObject.scene);
            Assert.That(
                transforms.Count(value =>
                    value.name == "ActualAssembledPremiumDisplayCase"),
                Is.EqualTo(1));
            Assert.That(
                transforms.Count(value =>
                    value.name == "CallerOwnedThreeBladeContent"),
                Is.EqualTo(1));
            Assert.That(sequence.CasePresentation.ContentSlot, Is.Not.Null);
        }

        [Test]
        public void TearIsReversibleAndPhysicalCoreSurvivesEffectsOff()
        {
            PackOpeningGate04R014Sequence sequence = OpenSequence();
            string sealedFingerprint = sequence.SealedStateFingerprint;
            sequence.SetNormalizedTearProgress(0.28f);
            Assert.That(sequence.MouthContactOcclusionActive, Is.True);
            sequence.SetNormalizedTearProgress(0.68f);
            Assert.That(sequence.PackVisible, Is.True);
            sequence.SetOpticalSweepEnabled(false);
            sequence.SetTime(0.86f, false);
            Assert.That(sequence.OpticalSweepEnabled, Is.False);
            Assert.That(sequence.PackVisible, Is.True);
            Assert.That(sequence.MouthContactOcclusionActive, Is.True);
            Assert.That(sequence.IsCaseContainedInMouth(), Is.True);
            Assert.That(sequence.ReboundToSealed(), Is.True);
            Assert.That(
                sequence.CurrentStateFingerprint,
                Is.EqualTo(sealedFingerprint));
        }

        [Test]
        public void CaseOnlyTravelsAfterItIsContainedAndNeverSwaps()
        {
            PackOpeningGate04R014Sequence sequence = OpenSequence();
            sequence.SetTime(
                PackOpeningGate04R014Profile.CaseContainedEnd - 0.01f,
                false);
            Assert.That(sequence.CurrentSample.CaseTravel, Is.Zero);
            Assert.That(sequence.IsCaseContainedInMouth(), Is.True);
            EntityId rootId = sequence.CaseRootEntityId;
            EntityId[] rendererIds = sequence.CaseRendererIds.ToArray();
            Vector3 authoredScale = sequence.CaseAuthoredScale;
            sequence.SetTime(1.18f, false);
            Assert.That(sequence.CurrentSample.CaseTravel, Is.GreaterThan(0f));
            Assert.That(sequence.CaseRootEntityId, Is.EqualTo(rootId));
            Assert.That(sequence.CaseRendererIds, Is.EqualTo(rendererIds));
            Assert.That(
                sequence.CaseMotionRoot.localScale,
                Is.EqualTo(authoredScale));
        }

        [Test]
        public void CandidateExcludesParticlesVfxHapticsAndBusinessUi()
        {
            string root = AssetAbsolutePath(Editor.PackOpeningGate04R014Builder.CandidateRoot);
            string sources = string.Join(
                "\n",
                Directory.GetFiles(root, "*.*", SearchOption.AllDirectories)
                    .Where(path => !path.Contains(
                        $"{Path.DirectorySeparatorChar}Tests{Path.DirectorySeparatorChar}",
                        StringComparison.Ordinal)
                        && (path.EndsWith(".cs", StringComparison.Ordinal)
                            || path.EndsWith(".shader", StringComparison.Ordinal)))
                    .Select(File.ReadAllText));
            StringAssert.DoesNotContain("ParticleSystem", sources);
            StringAssert.DoesNotContain("UnityEngine.VFX", sources);
            StringAssert.DoesNotContain("IosHaptics", sources);
            StringAssert.DoesNotContain("ProductPrimaryActionButton", sources);
            StringAssert.DoesNotContain("DOTween", sources);
            StringAssert.DoesNotContain("PrimeTween", sources);
        }

        [Test]
        public void PackDiscardBeginsAfterContainedCaseAndEndsCleanly()
        {
            PackOpeningGate04R014Sample before = profile.Evaluate(
                PackOpeningGate04R014Profile.PackDiscardStart - 0.01f);
            PackOpeningGate04R014Sample during = profile.Evaluate(
                PackOpeningGate04R014Profile.PackDiscardStart + 0.10f);
            PackOpeningGate04R014Sample after = profile.Evaluate(
                PackOpeningGate04R014Profile.PackDiscardEnd);
            Assert.That(before.PackDissolve, Is.Zero);
            Assert.That(during.PackDissolve, Is.GreaterThan(0f));
            Assert.That(after.PackDissolve, Is.EqualTo(1f).Within(0.00001f));
        }

        private static PackOpeningGate04R014Sequence OpenSequence()
        {
            Assert.That(
                File.Exists(AssetAbsolutePath(
                    Editor.PackOpeningGate04R014Builder.ScenePath)),
                Is.True,
                "Build the R014 scene before tests.");
            Scene scene = EditorSceneManager.OpenScene(
                Editor.PackOpeningGate04R014Builder.ScenePath,
                OpenSceneMode.Single);
            PackOpeningGate04R014Sequence sequence = scene
                .GetRootGameObjects()
                .SelectMany(root =>
                    root.GetComponentsInChildren<PackOpeningGate04R014Sequence>(
                        true))
                .Single();
            sequence.SetTime(0f, false);
            return sequence;
        }

        private static Transform[] AllTransforms(Scene scene)
        {
            return scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<Transform>(true))
                .ToArray();
        }

        private static string AssetAbsolutePath(string assetPath)
        {
            return Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "..",
                assetPath));
        }
    }
}
