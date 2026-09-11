using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using FidgetingApp.DisplayCase.MakeItShineCc0;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Candidates.Tests
{
    public sealed class PackOpeningGate04R013Tests
    {
        private PackOpeningGate04R013Profile profile;

        [SetUp]
        public void SetUp()
        {
            profile = ScriptableObject.CreateInstance<
                PackOpeningGate04R013Profile>();
        }

        [TearDown]
        public void TearDown()
        {
            UnityEngine.Object.DestroyImmediate(profile);
        }

        [Test]
        public void SourceDiscardCurve_RemainsExact()
        {
            AnimationCurve curve =
                MakeItShineCc0EffectCurves.CreateDiscardDissolveCurve();
            Assert.That(
                MakeItShineCc0EffectCurves.MatchesDiscardDissolveCurve(curve),
                Is.True);
            PackOpeningGate04R013Sample sample = profile.Evaluate(
                Mathf.Lerp(
                    PackOpeningGate04R013Profile.PackDiscardStart,
                    PackOpeningGate04R013Profile.PackDiscardEnd,
                    0.6166667f));
            Assert.That(sample.PackDissolve, Is.EqualTo(0.37030068f)
                .Within(0.00001f));
        }

        [Test]
        public void TearProgress_UsesContinuousRequiredSamples()
        {
            Assert.That(profile.Evaluate(0.65f).TearProgress,
                Is.EqualTo(0.15f).Within(0.00001f));
            Assert.That(profile.Evaluate(0.85f).TearProgress,
                Is.InRange(0.50f, 0.60f));
            Assert.That(profile.Evaluate(
                PackOpeningGate04R013Profile.TearEnd).TearProgress,
                Is.EqualTo(1f).Within(0.00001f));
            Assert.That(
                PackOpeningGate04R013Profile.SnapEnd
                    - PackOpeningGate04R013Profile.ResistanceEnd,
                Is.EqualTo(0.05f).Within(0.00001f));
        }

        [Test]
        public void BlenderRig_ImportsRelativeBlendShapesWithoutCaseGeometry()
        {
            GameObject rig = AssetDatabase.LoadAssetAtPath<GameObject>(
                Editor.PackOpeningGate04R013Builder.RigPath);
            Assert.That(rig, Is.Not.Null);
            SkinnedMeshRenderer[] renderers = rig.GetComponentsInChildren<
                SkinnedMeshRenderer>(true);
            Assert.That(renderers.Length, Is.EqualTo(10));
            Assert.That(renderers.Sum(renderer =>
                renderer.sharedMesh.vertexCount), Is.GreaterThanOrEqualTo(10000));
            Assert.That(renderers.Sum(renderer =>
                renderer.sharedMesh.blendShapeCount), Is.EqualTo(50));
            Assert.That(rig.GetComponentsInChildren<Transform>(true).Any(item =>
                item.name.Contains("Case", StringComparison.Ordinal)
                || item.name.Contains("Prize", StringComparison.Ordinal)),
                Is.False);
            foreach (SkinnedMeshRenderer renderer in renderers)
            {
                Assert.That(
                    renderer.sharedMesh.GetBlendShapeIndex("Tear_015"),
                    Is.GreaterThanOrEqualTo(0));
                Assert.That(
                    renderer.sharedMesh.GetBlendShapeIndex("Tear_100"),
                    Is.GreaterThanOrEqualTo(0));
            }
        }

        [Test]
        public void Scene_UsesOneActualCaseAndCallerOwnedContent()
        {
            PackOpeningGate04R013Sequence sequence = OpenSequence();
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
        public void DragProgress_IsReversibleAndSealedStateIsExact()
        {
            PackOpeningGate04R013Sequence sequence = OpenSequence();
            string sealedFingerprint = sequence.SealedStateFingerprint;
            sequence.SetNormalizedDragProgress(0.15f);
            Assert.That(sequence.MouthContactOcclusionActive, Is.True);
            sequence.SetNormalizedDragProgress(0.35f);
            Assert.That(sequence.MouthOpenWidthMeters,
                Is.EqualTo(
                    PackOpeningGate04R013Sequence.PackWidthMeters * 0.35f)
                .Within(0.00001f));
            sequence.SetNormalizedDragProgress(0.55f);
            Assert.That(sequence.MouthOpenWidthMeters,
                Is.EqualTo(
                    PackOpeningGate04R013Sequence.PackWidthMeters * 0.55f)
                .Within(0.00001f));
            sequence.SetNormalizedDragProgress(0.75f);
            Assert.That(sequence.CurrentStateFingerprint,
                Is.Not.EqualTo(sealedFingerprint));
            Assert.That(sequence.ReboundToSealed(), Is.True);
            Assert.That(sequence.CurrentStateFingerprint,
                Is.EqualTo(sealedFingerprint));
            Assert.That(sequence.MouthContactOcclusionActive, Is.False);
        }

        [Test]
        public void HalfOpenState_LeavesHalfPackSealedAndCaseContained()
        {
            PackOpeningGate04R013Sequence sequence = OpenSequence();
            sequence.SetNormalizedDragProgress(0.50f);
            Assert.That(sequence.MouthOpenWidthMeters,
                Is.EqualTo(PackOpeningGate04R013Sequence.PackWidthMeters * 0.5f)
                .Within(0.00001f));

            sequence.SetTime(PackOpeningGate04R013Profile.TearEnd, false);
            Assert.That(sequence.NormalizedDragProgress, Is.EqualTo(1f)
                .Within(0.00001f));
            Assert.That(sequence.MouthContactOcclusionActive, Is.True);
            Assert.That(sequence.IsCaseContainedInMouth(), Is.True);
            Assert.That(PackOpeningGate04R013Sequence.MouthDepthMeters,
                Is.GreaterThan(0.20f));
        }

        [Test]
        public void Case_IsNotMovedBeforeMouthOpensAndNeverReplaced()
        {
            PackOpeningGate04R013Sequence sequence = OpenSequence();
            sequence.SetTime(
                PackOpeningGate04R013Profile.CaseTravelStart - 0.01f,
                false);
            Assert.That(sequence.CurrentSample.CaseTravel, Is.Zero);
            EntityId rootId = sequence.CaseRootEntityId;
            EntityId[] rendererIds = sequence.CaseRendererIds.ToArray();
            Vector3 scale = sequence.CaseMotionRoot.localScale;
            Rect previous = default;
            float maxCenterStep = 0f;
            float maxHeightStep = 0f;
            Camera.main.aspect = PackOpeningGate04R013Capture.Width
                / (float)PackOpeningGate04R013Capture.Height;
            for (int frame = 0;
                frame < PackOpeningGate04R013Capture.FrameCount;
                frame++)
            {
                sequence.SetTime(frame / 60f, false);
                Assert.That(sequence.CaseRootEntityId, Is.EqualTo(rootId));
                Assert.That(sequence.CaseRendererIds, Is.EqualTo(rendererIds));
                Assert.That(sequence.CaseMotionRoot.localScale, Is.EqualTo(scale));
                Assert.That(sequence.TryGetCaseViewportBounds(out Rect current),
                    Is.True);
                if (frame > 0)
                {
                    maxCenterStep = Mathf.Max(
                        maxCenterStep,
                        Vector2.Distance(previous.center, current.center));
                    maxHeightStep = Mathf.Max(
                        maxHeightStep,
                        Mathf.Abs(previous.height - current.height));
                }
                previous = current;
            }
            Assert.That(maxCenterStep, Is.LessThan(0.060f));
            Assert.That(maxHeightStep, Is.LessThan(0.065f));
            Assert.That(previous.height, Is.InRange(0.48f, 0.62f));
        }

        [Test]
        public void Pack_DissolvesOnlyAfterFullTearAndCaseContainment()
        {
            PackOpeningGate04R013Sequence sequence = OpenSequence();
            sequence.SetTime(
                PackOpeningGate04R013Profile.TearEnd - 0.01f,
                false);
            Assert.That(sequence.CurrentSample.PackDissolve, Is.Zero);
            Assert.That(sequence.PackVisible, Is.True);
            sequence.SetTime(
                PackOpeningGate04R013Profile.PackDiscardStart + 0.20f,
                false);
            Assert.That(sequence.CurrentSample.PackDissolve, Is.GreaterThan(0f));
            Assert.That(sequence.PackVisible, Is.True);
            sequence.SetTime(
                PackOpeningGate04R013Profile.PackDiscardEnd + 0.03f,
                false);
            Assert.That(sequence.PackVisible, Is.False);
        }

        [Test]
        public void SourceMapping_HasExactCopiesAdaptationsAndRejections()
        {
            string root = AssetAbsolutePath(
                Editor.PackOpeningGate04R013Builder.EvidenceRoot);
            string mapping = File.ReadAllText(Path.Combine(
                root,
                "source-to-canonical-mapping.json"));
            StringAssert.Contains(
                "\"sourceCommit\": \"88842be0063b5b0b75e82ed6572752a37a13c82b\"",
                mapping);
            StringAssert.Contains("\"decision\": \"direct-copy\"", mapping);
            StringAssert.Contains("\"decision\": \"adapted\"", mapping);
            StringAssert.Contains("\"decision\": \"rejected\"", mapping);
            StringAssert.Contains("\"packOnlyBlenderRig\": true", mapping);
            Assert.That(
                Sha256(
                    Editor.PackOpeningGate04R013Builder.CandidateRoot
                    + "/ImportedSource/Animation/Booster_Discarded.anim"),
                Is.EqualTo(
                    "be661fe81b095f7f1ad08fb2a1c003b15f8690ee08d43f9f705dc849924fb2c6"));
            Assert.That(
                Sha256(
                    Editor.PackOpeningGate04R013Builder.CandidateRoot
                    + "/ImportedSource/Textures/TX_Flare_2x2_M.png"),
                Is.EqualTo(
                    "bbf7c86f5435ec3097717ef092e531214916e9cbb7db2b71f059e3d12f90ffa3"));
        }

        [Test]
        public void Candidate_HasNoVfxGraphRawHapticsOrBusinessCta()
        {
            string root = AssetAbsolutePath(
                Editor.PackOpeningGate04R013Builder.CandidateRoot);
            string sources = string.Join(
                "\n",
                Directory.GetFiles(root, "*.*", SearchOption.AllDirectories)
                    .Where(path => !path.Contains(
                        $"{Path.DirectorySeparatorChar}Tests{Path.DirectorySeparatorChar}",
                        StringComparison.Ordinal)
                    && (
                        path.EndsWith(".cs", StringComparison.Ordinal)
                        || path.EndsWith(".shader", StringComparison.Ordinal)))
                    .Select(File.ReadAllText));
            StringAssert.DoesNotContain("UnityEngine.VFX", sources);
            StringAssert.DoesNotContain("IosHaptics", sources);
            StringAssert.DoesNotContain("UnitySendMessage", sources);
            StringAssert.DoesNotContain("ProductPrimaryActionButton", sources);
            StringAssert.DoesNotContain("DOTween", sources);
            StringAssert.DoesNotContain("PrimeTween", sources);
        }

        private static PackOpeningGate04R013Sequence OpenSequence()
        {
            Assert.That(
                File.Exists(AssetAbsolutePath(
                    Editor.PackOpeningGate04R013Builder.ScenePath)),
                Is.True,
                "Build the R013 scene before tests.");
            Scene scene = EditorSceneManager.OpenScene(
                Editor.PackOpeningGate04R013Builder.ScenePath,
                OpenSceneMode.Single);
            PackOpeningGate04R013Sequence sequence = scene
                .GetRootGameObjects()
                .SelectMany(root =>
                    root.GetComponentsInChildren<PackOpeningGate04R013Sequence>(
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

        private static string Sha256(string assetPath)
        {
            using SHA256 hash = SHA256.Create();
            using FileStream stream = File.OpenRead(AssetAbsolutePath(assetPath));
            return string.Concat(hash.ComputeHash(stream).Select(
                value => value.ToString("x2")));
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
