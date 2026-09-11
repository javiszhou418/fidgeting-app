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
    public sealed class PackOpeningGate04R010Tests
    {
        private PackOpeningGate04R010Profile profile;

        [SetUp]
        public void SetUp()
        {
            profile = ScriptableObject.CreateInstance<
                PackOpeningGate04R010Profile>();
        }

        [TearDown]
        public void TearDown()
        {
            UnityEngine.Object.DestroyImmediate(profile);
        }

        [TestCase(0.00f, PackOpeningGate04R010Phase.Handoff)]
        [TestCase(0.28f, PackOpeningGate04R010Phase.Anticipation)]
        [TestCase(0.55f, PackOpeningGate04R010Phase.Resistance)]
        [TestCase(0.85f, PackOpeningGate04R010Phase.Snap)]
        [TestCase(0.90f, PackOpeningGate04R010Phase.Tear)]
        [TestCase(1.60f, PackOpeningGate04R010Phase.Impact)]
        [TestCase(1.78f, PackOpeningGate04R010Phase.Reveal)]
        [TestCase(2.45f, PackOpeningGate04R010Phase.Settled)]
        public void Evaluate_UsesAuthoredSignatureTimeline(
            float elapsed,
            PackOpeningGate04R010Phase expected)
        {
            Assert.That(profile.Evaluate(elapsed).Phase, Is.EqualTo(expected));
        }

        [Test]
        public void Tear_UsesFiftyMillisecondSnapThenProgressiveFront()
        {
            Assert.That(
                PackOpeningGate04R010Profile.SnapDuration,
                Is.EqualTo(0.05f).Within(0.00001f));
            float resistance = profile.Evaluate(0.849f).TearProgress;
            float snapped = profile.Evaluate(0.90f).TearProgress;
            float halfway = profile.Evaluate(1.18f).TearProgress;

            Assert.That(resistance, Is.InRange(0.050f, 0.061f));
            Assert.That(snapped, Is.EqualTo(0.20f).Within(0.002f));
            Assert.That(halfway, Is.GreaterThan(snapped));
            Assert.That(halfway, Is.LessThan(1f));
        }

        [Test]
        public void Impact_IsOneHundredEightyMillisecondsAndRemovesPack()
        {
            Assert.That(
                PackOpeningGate04R010Profile.ImpactDuration,
                Is.EqualTo(0.18f).Within(0.00001f));
            Assert.That(profile.Evaluate(1.60f).PackRetreat, Is.Zero);
            Assert.That(profile.Evaluate(1.78f).PackRetreat, Is.EqualTo(1f));
            Assert.That(
                profile.Evaluate(1.78f).Occlusion,
                Is.EqualTo(PackOpeningGate04R010Occlusion.PackGone));
            int flashFrames = Enumerable.Range(0, 186)
                .Count(frame =>
                    profile.Evaluate(frame / 60f).LocalizedFlash > 0.001f);
            Assert.That(flashFrames, Is.EqualTo(1));
        }

        [Test]
        public void CaseTravel_BeginsAtImpactWithoutScaleOrIdentityPhase()
        {
            Assert.That(profile.Evaluate(1.59f).CaseTravel, Is.Zero);
            Assert.That(profile.Evaluate(1.68f).CaseTravel, Is.InRange(0f, 1f));
            Assert.That(profile.Evaluate(1.78f).CaseTravel, Is.EqualTo(1f));
            Assert.That(
                profile.Evaluate(1.50f).Occlusion,
                Is.EqualTo(PackOpeningGate04R010Occlusion.AperturePartial));
            Assert.That(
                profile.Evaluate(1.68f).Occlusion,
                Is.EqualTo(PackOpeningGate04R010Occlusion.CrossingOccluder));
        }

        [Test]
        public void Reveal_UsesOneMonotonicMinusTwentyFiveDegreeSettle()
        {
            float previous = PackOpeningGate04R010Profile
                .StandardStartRotationDegrees;
            for (int frame = 0; frame < 186; frame++)
            {
                float rotation = profile.Evaluate(frame / 60f)
                    .CaseRotationDegrees;
                Assert.That(
                    rotation,
                    Is.GreaterThanOrEqualTo(previous - 0.0001f));
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
            PackOpeningGate04R010Sample standard = profile.Evaluate(1.68f);
            PackOpeningGate04R010Sample reduced = profile.Evaluate(1.68f, true);

            Assert.That(reduced.Phase, Is.EqualTo(standard.Phase));
            Assert.That(reduced.Occlusion, Is.EqualTo(standard.Occlusion));
            Assert.That(reduced.TearProgress, Is.EqualTo(standard.TearProgress));
            Assert.That(reduced.PackRetreat, Is.EqualTo(standard.PackRetreat));
            Assert.That(reduced.CaseTravel, Is.EqualTo(standard.CaseTravel));
            Assert.That(reduced.EnergyRingProgress, Is.Zero);
            Assert.That(reduced.ImpactParticlesEnabled, Is.False);
            Assert.That(reduced.DirectionalStreaksEnabled, Is.False);
            Assert.That(reduced.CameraKick, Is.EqualTo(Vector2.zero));
            Assert.That(reduced.CameraPush, Is.Zero);
        }

        [Test]
        public void SemanticEvents_AreOrderedAndPlatformIndependent()
        {
            PackOpeningGate04R010SemanticEvent[] events =
                profile.ResolveSemanticEvents(0f, 3.10f);
            Assert.That(
                events,
                Is.EqualTo(new[]
                {
                    PackOpeningGate04R010SemanticEvent.TearResistance,
                    PackOpeningGate04R010SemanticEvent.TearSnap,
                    PackOpeningGate04R010SemanticEvent.Impact,
                    PackOpeningGate04R010SemanticEvent.CaseSettled
                }));
            string source = File.ReadAllText(AssetAbsolutePath(
                "Assets/_DisplayCase/Candidates/PackOpeningGate04R010/Runtime/PackOpeningGate04R010Profile.cs"));
            StringAssert.DoesNotContain("IosHaptics", source);
            StringAssert.DoesNotContain("UnitySendMessage", source);
        }

        [Test]
        public void Scene_UsesSubdividedVolumeStripAndShapedCavity()
        {
            PackOpeningGate04R010Controller controller = OpenController();
            controller.SetTime(1.32f, false);
            MeshFilter strip = FindTransform(
                "SubdividedDeformableFoilStrip").GetComponent<MeshFilter>();
            MeshFilter cavity = FindTransform(
                "ShapedInnerFoilCavity").GetComponent<MeshFilter>();

            Assert.That(
                strip.sharedMesh.vertexCount,
                Is.EqualTo(
                    (PackOpeningGate04R010Controller.StripSegments + 1)
                    * (PackOpeningGate04R010Controller.StripRows + 1)
                    * 2));
            Assert.That(strip.sharedMesh.subMeshCount, Is.EqualTo(3));
            Assert.That(strip.GetComponent<Renderer>().sharedMaterials.Length,
                Is.EqualTo(3));
            Assert.That(cavity.sharedMesh.vertexCount, Is.GreaterThan(100));
            Assert.That(cavity.sharedMesh.GetIndexCount(0), Is.GreaterThan(0));
        }

        [Test]
        public void TearEdge_IsSharedLowAmplitudeAndNotSawtoothed()
        {
            PackOpeningGate04R010Controller controller = OpenController();
            controller.SetTime(1.24f, false);
            float maximum = controller.SharedTearOffsets
                .Max(value => Mathf.Abs(value));
            float maximumDelta = Enumerable
                .Range(1, controller.SharedTearOffsets.Count - 1)
                .Max(index => Mathf.Abs(
                    controller.SharedTearOffsets[index]
                    - controller.SharedTearOffsets[index - 1]));

            Assert.That(
                maximum,
                Is.LessThanOrEqualTo(
                    PackOpeningGate04R010Controller.MaximumTearAmplitude
                    + 0.000001f));
            Assert.That(maximumDelta, Is.LessThan(0.0011f));
            Assert.That(
                controller.MaximumAheadOfFrontSeparation,
                Is.LessThan(0.000001f));
        }

        [Test]
        public void FreedTail_ChangesCurvatureAndShowsRealThickness()
        {
            PackOpeningGate04R010Controller controller = OpenController();
            float curvature20 = controller.MeasureFreedTailCurvature(0.20f);
            float curvature50 = controller.MeasureFreedTailCurvature(0.50f);
            float curvature80 = controller.MeasureFreedTailCurvature(0.80f);
            Renderer strip = FindTransform(
                "SubdividedDeformableFoilStrip").GetComponent<Renderer>();

            Assert.That(curvature20, Is.GreaterThan(0.0001f));
            Assert.That(
                Mathf.Abs(curvature50 - curvature20),
                Is.GreaterThan(0.0001f));
            Assert.That(
                Mathf.Abs(curvature80 - curvature50),
                Is.GreaterThan(0.0001f));
            Assert.That(
                PackOpeningGate04R010Controller.StripThickness,
                Is.GreaterThan(0f));
            StringAssert.Contains("DarkUnderside", strip.sharedMaterials[1].name);
            StringAssert.Contains("ThinEdge", strip.sharedMaterials[2].name);
            Assert.That(
                FindTransform("MovingNarrowFoilSpecular"),
                Is.Not.Null);
            Assert.That(
                FindTransform("RestrainedStripContactShadow"),
                Is.Not.Null);
        }

        [Test]
        public void BelowThresholdRebound_RestoresFullUnityStateExactly()
        {
            PackOpeningGate04R010Controller controller = OpenController();
            controller.SetTime(0.76f, false);
            string disturbed = controller.CurrentStateFingerprint;

            Assert.That(disturbed, Is.Not.EqualTo(controller.SealedStateFingerprint));
            Assert.That(controller.ReboundToSealed(), Is.True);
            Assert.That(
                controller.CurrentStateFingerprint,
                Is.EqualTo(controller.SealedStateFingerprint));
        }

        [Test]
        public void SameCaseInstance_StaysActiveAndConstantScale()
        {
            PackOpeningGate04R010Controller controller = OpenController();
            controller.SetTime(0f, false);
            EntityId rootId = controller.CaseRootEntityId;
            EntityId[] rendererIds = controller.CaseRendererEntityIds.ToArray();
            Vector3 scale = controller.CaseMotionRoot.localScale;

            foreach (float time in new[]
                     {
                         0f, 0.90f, 1.20f, 1.50f, 1.60f, 1.68f, 1.78f, 2.10f, 3.10f
                     })
            {
                controller.SetTime(time, false);
                Assert.That(controller.CaseRootEntityId, Is.EqualTo(rootId));
                Assert.That(
                    controller.CaseRendererEntityIds,
                    Is.EqualTo(rendererIds));
                Assert.That(controller.CaseMotionRoot.localScale, Is.EqualTo(scale));
                Assert.That(
                    controller.CaseMotionRoot.gameObject.activeInHierarchy,
                    Is.True);
            }
            Assert.That(
                scale,
                Is.EqualTo(Vector3.one
                    * PackOpeningGate04R010Controller.CaseScale));
        }

        [Test]
        public void ProjectedCaseBounds_FollowAContinuousCurve()
        {
            PackOpeningGate04R010Controller controller = OpenController();
            Camera camera = Camera.main;
            camera.aspect =
                PackOpeningGate04R010Capture.Width
                / (float)PackOpeningGate04R010Capture.Height;
            Rect previous = default;
            float maximumCenterStep = 0f;
            float maximumHeightStep = 0f;
            for (int frame = 0; frame < PackOpeningGate04R010Capture.FrameCount; frame++)
            {
                controller.SetTime(
                    frame / (float)PackOpeningGate04R010Capture.FrameRate,
                    false);
                Assert.That(
                    controller.TryGetCaseViewportBounds(out Rect current),
                    Is.True);
                if (frame > 0)
                {
                    maximumCenterStep = Mathf.Max(
                        maximumCenterStep,
                        Vector2.Distance(previous.center, current.center));
                    maximumHeightStep = Mathf.Max(
                        maximumHeightStep,
                        Mathf.Abs(previous.height - current.height));
                }
                previous = current;
            }

            Assert.That(maximumCenterStep, Is.LessThan(0.060f));
            Assert.That(maximumHeightStep, Is.LessThan(0.065f));
            Assert.That(previous.height, Is.InRange(0.48f, 0.62f));
        }

        [Test]
        public void Pack_IsPhysicalOccluderAndGoneAtImpactEnd()
        {
            PackOpeningGate04R010Controller controller = OpenController();
            controller.SetTime(1.50f, false);
            Assert.That(controller.PackVisible, Is.True);
            Assert.That(controller.CavityVisible, Is.True);
            Assert.That(
                controller.CurrentSample.Occlusion,
                Is.EqualTo(PackOpeningGate04R010Occlusion.AperturePartial));

            controller.SetTime(
                PackOpeningGate04R010Profile.ImpactEnd,
                false);
            Assert.That(controller.PackVisible, Is.False);
            Assert.That(controller.CavityVisible, Is.False);
            Assert.That(
                controller.CurrentSample.Occlusion,
                Is.EqualTo(PackOpeningGate04R010Occlusion.PackGone));
        }

        [Test]
        public void Scene_ContainsOneRealWholeCaseAndNoPreviewDuplicate()
        {
            PackOpeningGate04R010Controller controller = OpenController();
            Transform[] transforms = controller.gameObject.scene
                .GetRootGameObjects()
                .SelectMany(root =>
                    root.GetComponentsInChildren<Transform>(true))
                .ToArray();
            SpriteRenderer[] sprites = controller.gameObject.scene
                .GetRootGameObjects()
                .SelectMany(root =>
                    root.GetComponentsInChildren<SpriteRenderer>(true))
                .ToArray();

            Assert.That(
                transforms.Count(value =>
                    value.name == "ActualAssembledPremiumDisplayCase"),
                Is.EqualTo(1));
            Assert.That(
                transforms.Count(value =>
                    value.name == "CallerOwnedThreeBladeContent"),
                Is.EqualTo(1));
            Assert.That(sprites.Length, Is.Zero);
            Assert.That(controller.CasePresentation.CaseAssembly, Is.Not.Null);
            Assert.That(controller.CasePresentation.ContentSlot, Is.Not.Null);
            Assert.That(
                transforms.Any(value =>
                    value.name.Contains(
                        "Exploded",
                        StringComparison.OrdinalIgnoreCase)),
                Is.False);
        }

        [Test]
        public void Scene_UsesActualShippingEnvironmentWithoutDebugBlocks()
        {
            OpenController();
            Transform environment = FindTransform(
                "ActualShippingDarkMineralEnvironment");
            Renderer renderer = environment.GetComponent<Renderer>();
            string materialPath = AssetDatabase.GetAssetPath(
                renderer.sharedMaterial);
            Transform[] all = environment.gameObject.scene
                .GetRootGameObjects()
                .SelectMany(root =>
                    root.GetComponentsInChildren<Transform>(true))
                .ToArray();

            Assert.That(
                materialPath,
                Is.EqualTo(
                    Editor.PackOpeningGate04R010Builder
                        .ShippingEnvironmentMaterialPath));
            Assert.That(
                AssetDatabase.LoadAssetAtPath<Texture2D>(
                    Editor.PackOpeningGate04R010Builder
                        .ShippingEnvironmentTexturePath),
                Is.Not.Null);
            Assert.That(
                all.Any(value =>
                    value.name.Contains("MineralBackdrop")
                    || value.name.Contains("DebugBlock")
                    || value.name.Contains("WarmNeutralPlinth")),
                Is.False);
        }

        [Test]
        public void Scene_UsesOneRingAndThreeSeededShurikenSystems()
        {
            PackOpeningGate04R010Controller controller = OpenController();
            GameObject[] roots = controller.gameObject.scene.GetRootGameObjects();
            ParticleSystem[] systems = roots
                .SelectMany(root =>
                    root.GetComponentsInChildren<ParticleSystem>(true))
                .ToArray();
            Transform[] transforms = roots
                .SelectMany(root =>
                    root.GetComponentsInChildren<Transform>(true))
                .ToArray();

            Assert.That(systems.Length, Is.EqualTo(3));
            Assert.That(systems.All(system => !system.useAutoRandomSeed), Is.True);
            Assert.That(
                transforms.Count(value =>
                    value.name == "OneThinEnergyRingBehindProduct"),
                Is.EqualTo(1));
            Assert.That(
                transforms.Any(value =>
                    value.name.Contains("Concentric", StringComparison.OrdinalIgnoreCase)
                    || value.name.Contains("Fog", StringComparison.OrdinalIgnoreCase)
                    || value.name.Contains("Confetti", StringComparison.OrdinalIgnoreCase)),
                Is.False);
        }

        [Test]
        public void ActualSourceAssets_PreserveHashesAndAuthoredCanvas()
        {
            Assert.That(
                Sha256(Editor.PackOpeningGate04R010Builder.PackBodyPath),
                Is.EqualTo(
                    "ebc17bb238ebbcb82d36134bb2781838df610f8a3d1750c27b8ade10fc4681d6"));
            Assert.That(
                Sha256(Editor.PackOpeningGate04R010Builder.PackFlapPath),
                Is.EqualTo(
                    "b031fc5c57d194e9603e9b32e1cd603285aa564490f599f29bb0cd67dab33d49"));
            Assert.That(
                Sha256(Editor.PackOpeningGate04R010Builder.ActualCasePrefabPath),
                Is.EqualTo(
                    "7a96aae6245b5a1d5463dabc3cb4518af8693ba8f8328ad9f2fe4ee6c6a67e2c"));
            Assert.That(
                Sha256(Editor.PackOpeningGate04R010Builder.ActualPrizePrefabPath),
                Is.EqualTo(
                    "d68f51b0034199987fa9e0cd44a8e3ba351b70b4289ff4773edc296e9395a8e1"));
            Assert.That(
                Sha256(Editor.PackOpeningGate04R010Builder
                    .ShippingEnvironmentTexturePath),
                Is.EqualTo(
                    "ed1fc13c9419f350fd772e31f505cabe016995e17c06c576c873b19a2a526d5d"));
            Assert.That(
                ReadPngDimensions(
                    Editor.PackOpeningGate04R010Builder.PackBodyPath),
                Is.EqualTo(new Vector2Int(384, 512)));
            Assert.That(
                ReadPngDimensions(
                    Editor.PackOpeningGate04R010Builder.PackFlapPath),
                Is.EqualTo(new Vector2Int(384, 512)));
        }

        [Test]
        public void CandidateSources_HaveNoVfxTweenNoiseOrShippingWiring()
        {
            string root = AssetAbsolutePath(
                "Assets/_DisplayCase/Candidates/PackOpeningGate04R010");
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

            StringAssert.DoesNotContain("UnityEngine.VFX", sources);
            StringAssert.DoesNotContain("PrimeTween", sources);
            StringAssert.DoesNotContain("DOTween", sources);
            StringAssert.DoesNotContain("pack-dissolve-noise", sources);
            StringAssert.DoesNotContain("pixel noise", sources);
            StringAssert.DoesNotContain("IosHaptics", sources);
            StringAssert.DoesNotContain("StartGachaRevealFromNativeUi", sources);
        }

        private static PackOpeningGate04R010Controller OpenController()
        {
            Assert.That(
                File.Exists(AssetAbsolutePath(
                    Editor.PackOpeningGate04R010Builder.ScenePath)),
                Is.True,
                "Build the rev 10 candidate scene before running tests.");
            Scene scene = EditorSceneManager.OpenScene(
                Editor.PackOpeningGate04R010Builder.ScenePath,
                OpenSceneMode.Single);
            PackOpeningGate04R010Controller controller = scene
                .GetRootGameObjects()
                .SelectMany(root =>
                    root.GetComponentsInChildren<
                        PackOpeningGate04R010Controller>(true))
                .Single();
            controller.SetTime(0f, false);
            return controller;
        }

        private static Transform FindTransform(string name)
        {
            Transform value = UnityEngine.Object
                .FindObjectsByType<Transform>(
                    FindObjectsInactive.Include,
                    FindObjectsSortMode.None)
                .SingleOrDefault(transform => transform.name == name);
            Assert.That(value, Is.Not.Null, $"Missing scene object {name}.");
            return value;
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
