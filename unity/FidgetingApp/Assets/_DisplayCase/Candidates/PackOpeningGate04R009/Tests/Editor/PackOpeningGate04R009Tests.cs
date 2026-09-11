using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Candidates.Tests
{
    public sealed class PackOpeningGate04R009Tests
    {
        private PackOpeningGate04R009Profile profile;

        [SetUp]
        public void SetUp()
        {
            profile = ScriptableObject.CreateInstance<
                PackOpeningGate04R009Profile>();
        }

        [TearDown]
        public void TearDown()
        {
            UnityEngine.Object.DestroyImmediate(profile);
        }

        [TestCase(0.00f, PackOpeningGate04R009Phase.Handoff)]
        [TestCase(0.35f, PackOpeningGate04R009Phase.Anticipation)]
        [TestCase(0.65f, PackOpeningGate04R009Phase.Resistance)]
        [TestCase(0.95f, PackOpeningGate04R009Phase.Snap)]
        [TestCase(1.00f, PackOpeningGate04R009Phase.Tear)]
        [TestCase(1.75f, PackOpeningGate04R009Phase.Impact)]
        [TestCase(1.93f, PackOpeningGate04R009Phase.Reveal)]
        [TestCase(2.53f, PackOpeningGate04R009Phase.Settled)]
        public void Evaluate_UsesFullSignatureTimeline(
            float elapsed,
            PackOpeningGate04R009Phase expected)
        {
            Assert.That(profile.Evaluate(elapsed).Phase, Is.EqualTo(expected));
        }

        [Test]
        public void Tear_UsesReadableResistanceAndFiftyMillisecondSnap()
        {
            Assert.That(
                PackOpeningGate04R009Profile.SnapDuration,
                Is.EqualTo(0.05f).Within(0.00001f));
            float beforeSnap = profile.Evaluate(0.949f).TearProgress;
            float afterSnap = profile.Evaluate(1.000f).TearProgress;

            Assert.That(beforeSnap, Is.InRange(0.045f, 0.060f));
            Assert.That(afterSnap, Is.EqualTo(0.24f).Within(0.002f));
        }

        [Test]
        public void Impact_IsOneHundredEightyMillisecondsWithOneFlashFrame()
        {
            Assert.That(
                PackOpeningGate04R009Profile.ImpactDuration,
                Is.EqualTo(0.18f).Within(0.00001f));
            int flashFrames = Enumerable.Range(0, 186)
                .Count(frame =>
                    profile.Evaluate(frame / 60f).LocalizedFlash > 0.001f);

            Assert.That(flashFrames, Is.EqualTo(1));
            Assert.That(profile.Evaluate(106f / 60f).LocalizedFlash, Is.Zero);
            Assert.That(
                profile.Evaluate(106f / 60f).HeroSilhouetteRequired,
                Is.True);
        }

        [Test]
        public void Handoff_OverlapsOnlyAsApertureOcclusion()
        {
            PackOpeningGate04R009Sample overlap = profile.Evaluate(1.70f);

            Assert.That(overlap.OpeningProgress, Is.GreaterThan(0.65f));
            Assert.That(overlap.CaseEntry, Is.GreaterThan(0f));
            Assert.That(overlap.PackRetreat, Is.GreaterThan(0f));
            Assert.That(overlap.PackRetreat, Is.LessThan(1f));
            Assert.That(
                PackOpeningGate04R009Profile.CaseEntryStart,
                Is.LessThan(PackOpeningGate04R009Profile.PackRetreatStart));
        }

        [Test]
        public void Reveal_UsesOneMonotonicMinusTwentyFiveToZeroSettle()
        {
            float previous = -25.001f;
            for (int frame = 0; frame < 186; frame++)
            {
                float rotation = profile.Evaluate(frame / 60f)
                    .CaseRotationDegrees;
                Assert.That(rotation, Is.GreaterThanOrEqualTo(previous - 0.0001f));
                Assert.That(rotation, Is.InRange(-25f, 0f));
                previous = rotation;
            }
            Assert.That(
                profile.Evaluate(3.10f).CaseRotationDegrees,
                Is.EqualTo(0f).Within(0.0001f));
        }

        [Test]
        public void ReduceMotion_PreservesCausalityAndRemovesSensoryPunch()
        {
            PackOpeningGate04R009Sample standard = profile.Evaluate(1.82f);
            PackOpeningGate04R009Sample reduced = profile.Evaluate(1.82f, true);

            Assert.That(reduced.Phase, Is.EqualTo(standard.Phase));
            Assert.That(reduced.TearProgress, Is.EqualTo(standard.TearProgress));
            Assert.That(reduced.PackRetreat, Is.EqualTo(standard.PackRetreat));
            Assert.That(reduced.CaseEntry, Is.EqualTo(standard.CaseEntry));
            Assert.That(reduced.ShockwaveProgress, Is.Zero);
            Assert.That(reduced.ImpactParticlesEnabled, Is.False);
            Assert.That(reduced.DirectionalStreaksEnabled, Is.False);
            Assert.That(reduced.CameraKick, Is.EqualTo(Vector2.zero));
            Assert.That(reduced.CameraPush, Is.Zero);
        }

        [Test]
        public void SemanticEvents_AreOrderedAndDoNotCallAPlatformRenderer()
        {
            PackOpeningGate04R009SemanticEvent[] events =
                profile.ResolveSemanticEvents(0f, 3.10f);

            Assert.That(
                events,
                Is.EqualTo(new[]
                {
                    PackOpeningGate04R009SemanticEvent.TearResistance,
                    PackOpeningGate04R009SemanticEvent.TearSnap,
                    PackOpeningGate04R009SemanticEvent.Impact,
                    PackOpeningGate04R009SemanticEvent.CaseSettled
                }));
            string source = File.ReadAllText(
                AssetAbsolutePath(
                    "Assets/_DisplayCase/Candidates/PackOpeningGate04R009/Runtime/PackOpeningGate04R009Profile.cs"));
            StringAssert.DoesNotContain("IosHaptics", source);
            StringAssert.DoesNotContain("UnitySendMessage", source);
        }

        [Test]
        public void ActualPackAssets_PreserveAuthoredCanvasAndHashes()
        {
            Texture2D body = AssetDatabase.LoadAssetAtPath<Texture2D>(
                Editor.PackOpeningGate04R009Builder.PackBodyPath);
            Texture2D flap = AssetDatabase.LoadAssetAtPath<Texture2D>(
                Editor.PackOpeningGate04R009Builder.PackFlapPath);

            Assert.That(body, Is.Not.Null);
            Assert.That(flap, Is.Not.Null);
            Assert.That(
                ReadPngDimensions(
                    Editor.PackOpeningGate04R009Builder.PackBodyPath),
                Is.EqualTo(new Vector2Int(384, 512)));
            Assert.That(
                ReadPngDimensions(
                    Editor.PackOpeningGate04R009Builder.PackFlapPath),
                Is.EqualTo(new Vector2Int(384, 512)));
            Assert.That(
                Sha256(Editor.PackOpeningGate04R009Builder.PackBodyPath),
                Is.EqualTo(
                    "ebc17bb238ebbcb82d36134bb2781838df610f8a3d1750c27b8ade10fc4681d6"));
            Assert.That(
                Sha256(Editor.PackOpeningGate04R009Builder.PackFlapPath),
                Is.EqualTo(
                    "b031fc5c57d194e9603e9b32e1cd603285aa564490f599f29bb0cd67dab33d49"));
        }

        [Test]
        public void ActualCasePrefab_KeepsWholeAssemblyAndContentSlot()
        {
            GameObject casePrefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                Editor.PackOpeningGate04R009Builder.ActualCasePrefabPath);
            PremiumDisplayCaseShippingPresentation presentation =
                casePrefab != null
                    ? casePrefab.GetComponent<
                        PremiumDisplayCaseShippingPresentation>()
                    : null;
            GameObject prize = AssetDatabase.LoadAssetAtPath<GameObject>(
                Editor.PackOpeningGate04R009Builder.ActualPrizePrefabPath);

            Assert.That(presentation, Is.Not.Null);
            Assert.That(presentation.CaseAssembly, Is.Not.Null);
            Assert.That(presentation.ContentSlot, Is.Not.Null);
            Assert.That(prize, Is.Not.Null);
            Assert.That(
                presentation.GetComponentsInChildren<Transform>(true)
                    .Any(value => value.name.Contains(
                        "Exploded",
                        StringComparison.OrdinalIgnoreCase)),
                Is.False);
        }

        [Test]
        public void GeneratedScene_UsesShurikenAndNoVfxGraph()
        {
            Assert.That(
                File.Exists(AssetAbsolutePath(
                    Editor.PackOpeningGate04R009Builder.ScenePath)),
                Is.True,
                "Build the rev 9 candidate scene before running this assertion.");
            Scene scene = EditorSceneManager.OpenScene(
                Editor.PackOpeningGate04R009Builder.ScenePath,
                OpenSceneMode.Single);
            GameObject[] roots = scene.GetRootGameObjects();
            ParticleSystem[] systems = roots
                .SelectMany(root => root.GetComponentsInChildren<
                    ParticleSystem>(true))
                .ToArray();
            Transform[] transforms = roots
                .SelectMany(root => root.GetComponentsInChildren<Transform>(true))
                .ToArray();

            Assert.That(systems.Length, Is.EqualTo(3));
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
                    value.name.Contains("VisualEffect", StringComparison.Ordinal)),
                Is.False);
        }

        [Test]
        public void CandidateSources_ContainNoNoiseDissolveOrTweenDependency()
        {
            string root = AssetAbsolutePath(
                "Assets/_DisplayCase/Candidates/PackOpeningGate04R009");
            string sources = string.Join(
                "\n",
                Directory.GetFiles(root, "*.*", SearchOption.AllDirectories)
                    .Where(path =>
                        !path.Contains(
                            $"{Path.DirectorySeparatorChar}Tests{Path.DirectorySeparatorChar}",
                            StringComparison.Ordinal)
                        && (
                            path.EndsWith(".cs", StringComparison.Ordinal)
                            || path.EndsWith(".shader", StringComparison.Ordinal)
                        ))
                    .Select(File.ReadAllText));

            StringAssert.DoesNotContain("VFXGraph", sources);
            StringAssert.DoesNotContain("PrimeTween", sources);
            StringAssert.DoesNotContain("DOTween", sources);
            StringAssert.DoesNotContain("pack-dissolve-noise", sources);
            StringAssert.DoesNotContain("pixel noise", sources);
        }

        private static string Sha256(string assetPath)
        {
            using SHA256 sha = SHA256.Create();
            using FileStream stream = File.OpenRead(AssetAbsolutePath(assetPath));
            return string.Concat(
                sha.ComputeHash(stream).Select(value => value.ToString("x2")));
        }

        private static Vector2Int ReadPngDimensions(string assetPath)
        {
            byte[] header = new byte[24];
            using FileStream stream = File.OpenRead(AssetAbsolutePath(assetPath));
            Assert.That(stream.Read(header, 0, header.Length), Is.EqualTo(24));
            int width =
                header[16] << 24
                | header[17] << 16
                | header[18] << 8
                | header[19];
            int height =
                header[20] << 24
                | header[21] << 16
                | header[22] << 8
                | header[23];
            return new Vector2Int(width, height);
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
