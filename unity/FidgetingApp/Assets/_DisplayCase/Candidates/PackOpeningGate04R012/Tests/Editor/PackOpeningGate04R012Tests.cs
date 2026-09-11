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
    public sealed class PackOpeningGate04R012Tests
    {
        private PackOpeningGate04R012Profile profile;

        [SetUp]
        public void SetUp()
        {
            profile = ScriptableObject.CreateInstance<
                PackOpeningGate04R012Profile>();
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
            PackOpeningGate04R012Sample sample = profile.Evaluate(
                Mathf.Lerp(
                    PackOpeningGate04R012Profile.TargetSolidPackOff,
                    PackOpeningGate04R012Profile.TargetProxyResultOff,
                    0.6166667f));
            Assert.That(sample.PackDissolve, Is.EqualTo(0.37030068f)
                .Within(0.00001f));
        }

        [Test]
        public void TearProgress_IsProgressiveAndHalfPackStaysSealed()
        {
            PackOpeningGate04R012Sample early = profile.Evaluate(0.75f);
            PackOpeningGate04R012Sample middle = profile.Evaluate(0.92f);
            PackOpeningGate04R012Sample late = profile.Evaluate(1.06f);
            Assert.That(early.TearProgress, Is.InRange(0.12f, 0.18f));
            Assert.That(middle.TearProgress, Is.InRange(0.50f, 0.66f));
            Assert.That(late.TearProgress, Is.InRange(0.70f, 0.82f));
            Assert.That(
                PackOpeningGate04R012Profile.SnapEnd
                    - PackOpeningGate04R012Profile.ResistanceEnd,
                Is.EqualTo(0.05f).Within(0.00001f));
        }

        [Test]
        public void ReduceMotion_PreservesCausalityWithoutSensoryPunch()
        {
            PackOpeningGate04R012Sample standard = profile.Evaluate(1.74f);
            PackOpeningGate04R012Sample reduced = profile.Evaluate(1.74f, true);
            Assert.That(reduced.Occlusion, Is.EqualTo(standard.Occlusion));
            Assert.That(reduced.PackDissolve, Is.EqualTo(standard.PackDissolve));
            Assert.That(reduced.CaseTravel, Is.EqualTo(standard.CaseTravel));
            Assert.That(reduced.SourceSweep, Is.Zero);
            Assert.That(reduced.SourceImpact, Is.Zero);
            Assert.That(reduced.CameraPush, Is.Zero);
            Assert.That(reduced.CameraKick, Is.EqualTo(Vector2.zero));
        }

        [Test]
        public void Scene_UsesOneActualCaseAndCallerOwnedContent()
        {
            PackOpeningGate04R012Sequence sequence = OpenSequence();
            Transform[] transforms = AllTransforms(sequence.gameObject.scene);
            Assert.That(
                transforms.Count(value =>
                    value.name == "ActualAssembledPremiumDisplayCase"),
                Is.EqualTo(1));
            Assert.That(
                transforms.Count(value =>
                    value.name == "CallerOwnedThreeBladeContent"),
                Is.EqualTo(1));
            Assert.That(
                transforms.Any(value =>
                    value.name.Contains("Opening_Booster", StringComparison.Ordinal)
                    || value.name.Contains(
                        "BoosterFractured",
                        StringComparison.Ordinal)
                    || value.name.Contains(
                        "Exploded",
                        StringComparison.OrdinalIgnoreCase)),
                Is.False);
            Assert.That(sequence.CasePresentation.ContentSlot, Is.Not.Null);
        }

        [Test]
        public void Mesh_HasFineTearAndPhysicalMouth()
        {
            PackOpeningGate04R012Sequence sequence = OpenSequence();
            Assert.That(
                PackOpeningGate04R012Sequence.LongitudinalSegments,
                Is.GreaterThanOrEqualTo(96));
            sequence.SetTime(0f, false);
            Assert.That(sequence.CavityVisibleColumnCount, Is.Zero);

            sequence.SetTime(0.92f, false);
            Assert.That(sequence.CavityVisibleColumnCount, Is.GreaterThan(35));
            Assert.That(sequence.CavityMaximumOpenHeight, Is.GreaterThan(
                PackOpeningGate04R012Sequence.MouthMaximumHeight * 0.70f));
            Assert.That(
                sequence.MaximumAheadLayerSeparation,
                Is.LessThanOrEqualTo(0.000081f));

            sequence.SetTime(1.50f, false);
            Assert.That(sequence.CavityMaximumOpenHeight, Is.GreaterThan(
                PackOpeningGate04R012Sequence.MouthMaximumHeight * 0.90f));
            Assert.That(
                sequence.CavityBackWallWorldZ,
                Is.GreaterThan(sequence.CaseRearWorldZ));
        }

        [Test]
        public void TornStrip_IsNarrowCurledAndTexturedOnBothSides()
        {
            PackOpeningGate04R012Sequence sequence = OpenSequence();
            sequence.SetTime(1.26f, false);
            Assert.That(
                PackOpeningGate04R012Sequence.FoilStripWidth,
                Is.LessThan(PackOpeningGate04R012Sequence.PackHeight * 0.08f));
            Assert.That(sequence.MeasureFoilTailCurvature(), Is.GreaterThan(
                0.0005f));
            MeshRenderer strip = FindTransform("CurledNarrowTornSealStrip")
                .GetComponent<MeshRenderer>();
            Assert.That(strip.sharedMaterials.Length, Is.EqualTo(3));
            Assert.That(
                strip.sharedMaterials[1].name,
                Does.Contain("DarkUnderside"));
        }

        [Test]
        public void SameCase_StaysInstantiatedAndContinuous()
        {
            PackOpeningGate04R012Sequence sequence = OpenSequence();
            EntityId rootId = sequence.CaseRootEntityId;
            EntityId[] rendererIds = sequence.CaseRendererIds.ToArray();
            Vector3 scale = sequence.CaseMotionRoot.localScale;
            Rect previous = default;
            float maxCenterStep = 0f;
            float maxHeightStep = 0f;
            Camera.main.aspect = PackOpeningGate04R012Capture.Width
                / (float)PackOpeningGate04R012Capture.Height;
            for (int frame = 0;
                frame < PackOpeningGate04R012Capture.FrameCount;
                frame++)
            {
                sequence.SetTime(frame / 60f, false);
                Assert.That(sequence.CaseRootEntityId, Is.EqualTo(rootId));
                Assert.That(sequence.CaseRendererIds, Is.EqualTo(rendererIds));
                Assert.That(sequence.CaseMotionRoot.localScale, Is.EqualTo(scale));
                Assert.That(
                    sequence.TryGetCaseViewportBounds(out Rect current),
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
        public void Pack_DissolvesAfterCaseBeginsContinuousExit()
        {
            PackOpeningGate04R012Sequence sequence = OpenSequence();
            sequence.SetTime(
                PackOpeningGate04R012Profile.TargetSolidPackOff - 0.01f,
                false);
            Assert.That(sequence.CurrentSample.PackDissolve, Is.Zero);
            Assert.That(sequence.CurrentSample.CaseTravel, Is.GreaterThan(0f));
            sequence.SetTime(
                PackOpeningGate04R012Profile.TargetProxyResultOff - 0.01f,
                false);
            Assert.That(sequence.CurrentSample.PackDissolve, Is.GreaterThan(0.6f));
            Assert.That(sequence.PackVisible, Is.True);
            sequence.SetTime(
                PackOpeningGate04R012Profile.TargetProxyResultOff + 0.03f,
                false);
            Assert.That(sequence.PackVisible, Is.False);
        }

        [Test]
        public void SealedRebound_IsExact()
        {
            PackOpeningGate04R012Sequence sequence = OpenSequence();
            sequence.SetTime(0.66f, false);
            Assert.That(
                sequence.CurrentStateFingerprint,
                Is.Not.EqualTo(sequence.SealedStateFingerprint));
            Assert.That(sequence.ReboundToSealed(), Is.True);
        }

        [Test]
        public void ProductAssets_AndDirectCc0CopiesPreserveHashes()
        {
            Assert.That(
                Sha256(Editor.PackOpeningGate04R012Builder.PackBodyPath),
                Is.EqualTo(
                    "ebc17bb238ebbcb82d36134bb2781838df610f8a3d1750c27b8ade10fc4681d6"));
            Assert.That(
                Sha256(Editor.PackOpeningGate04R012Builder.PackFlapPath),
                Is.EqualTo(
                    "b031fc5c57d194e9603e9b32e1cd603285aa564490f599f29bb0cd67dab33d49"));
            Assert.That(
                Sha256(
                    Editor.PackOpeningGate04R012Builder.ImportedSourceRoot
                    + "/Animation/Booster_Discarded.anim"),
                Is.EqualTo(
                    "be661fe81b095f7f1ad08fb2a1c003b15f8690ee08d43f9f705dc849924fb2c6"));
            Assert.That(
                Sha256(
                    Editor.PackOpeningGate04R012Builder.ImportedSourceRoot
                    + "/Textures/TX_Flare_2x2_M.png"),
                Is.EqualTo(
                    "bbf7c86f5435ec3097717ef092e531214916e9cbb7db2b71f059e3d12f90ffa3"));
        }

        [Test]
        public void SourceMapping_RecordsDirectAdaptedAndRejected()
        {
            string mapping = File.ReadAllText(AssetAbsolutePath(
                Editor.PackOpeningGate04R012Builder.EvidenceRoot
                + "/source-to-canonical-mapping.json"));
            StringAssert.Contains("\"decision\": \"direct-copy\"", mapping);
            StringAssert.Contains("\"decision\": \"adapted\"", mapping);
            StringAssert.Contains("\"decision\": \"rejected\"", mapping);
            StringAssert.Contains("\"shurikenAdapter\": true", mapping);
            StringAssert.Contains("\"vfxGraphDependency\": false", mapping);
        }

        [Test]
        public void Candidate_HasNoVfxGraphRawHapticsOrBusinessCta()
        {
            string root = AssetAbsolutePath(
                "Assets/_DisplayCase/Candidates/PackOpeningGate04R012");
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

        private static PackOpeningGate04R012Sequence OpenSequence()
        {
            Assert.That(
                File.Exists(AssetAbsolutePath(
                    Editor.PackOpeningGate04R012Builder.ScenePath)),
                Is.True,
                "Build the R012 scene before tests.");
            Scene scene = EditorSceneManager.OpenScene(
                Editor.PackOpeningGate04R012Builder.ScenePath,
                OpenSceneMode.Single);
            PackOpeningGate04R012Sequence sequence = scene
                .GetRootGameObjects()
                .SelectMany(root =>
                    root.GetComponentsInChildren<PackOpeningGate04R012Sequence>(
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

        private static Transform FindTransform(string name)
        {
            Transform found = UnityEngine.Object
                .FindObjectsByType<Transform>(
                    FindObjectsInactive.Include,
                    FindObjectsSortMode.None)
                .SingleOrDefault(value => value.name == name);
            Assert.That(found, Is.Not.Null, $"Missing {name}.");
            return found;
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
