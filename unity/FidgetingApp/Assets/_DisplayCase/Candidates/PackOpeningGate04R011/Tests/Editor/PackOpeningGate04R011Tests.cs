using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using FidgetingApp.DisplayCase.MakeItShineCc0;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Playables;
using UnityEngine.SceneManagement;
using UnityEngine.Timeline;

namespace FidgetingApp.DisplayCase.Candidates.Tests
{
    public sealed class PackOpeningGate04R011Tests
    {
        private PackOpeningGate04R011Profile profile;

        [SetUp]
        public void SetUp()
        {
            profile = ScriptableObject.CreateInstance<
                PackOpeningGate04R011Profile>();
        }

        [TearDown]
        public void TearDown()
        {
            UnityEngine.Object.DestroyImmediate(profile);
        }

        [TestCase(0.00f, PackOpeningGate04R011Phase.Handoff)]
        [TestCase(0.28f, PackOpeningGate04R011Phase.Anticipation)]
        [TestCase(0.55f, PackOpeningGate04R011Phase.Resistance)]
        [TestCase(0.85f, PackOpeningGate04R011Phase.Snap)]
        [TestCase(0.90f, PackOpeningGate04R011Phase.Tear)]
        [TestCase(1.60f, PackOpeningGate04R011Phase.SourceImpact)]
        [TestCase(1.78f, PackOpeningGate04R011Phase.SourceReveal)]
        [TestCase(3.10f, PackOpeningGate04R011Phase.Settled)]
        public void Evaluate_UsesRetargetedSourceTimeline(
            float elapsed,
            PackOpeningGate04R011Phase expected)
        {
            Assert.That(profile.Evaluate(elapsed).Phase, Is.EqualTo(expected));
        }

        [Test]
        public void SourceTimestamps_MapWithoutChangingEffectIntervals()
        {
            Assert.That(
                PackOpeningGate04R011Profile
                    .TargetProxyResultStart
                    - PackOpeningGate04R011Profile.ImpactStart,
                Is.EqualTo(
                    PackOpeningGate04R011Profile.SourceProxyResultStart
                    - PackOpeningGate04R011Profile.SourceExplosionStart)
                    .Within(0.000001f));
            Assert.That(
                PackOpeningGate04R011Profile
                    .TargetProxyResultOff
                    - PackOpeningGate04R011Profile.ImpactStart,
                Is.EqualTo(
                    PackOpeningGate04R011Profile.SourceProxyResultOff
                    - PackOpeningGate04R011Profile.SourceExplosionStart)
                    .Within(0.000001f));
        }

        [Test]
        public void PackDissolve_UsesExactCc0DiscardCurve()
        {
            AnimationCurve curve =
                MakeItShineCc0EffectCurves.CreateDiscardDissolveCurve();
            Assert.That(
                MakeItShineCc0EffectCurves.MatchesDiscardDissolveCurve(curve),
                Is.True);
            float target = Mathf.Lerp(
                PackOpeningGate04R011Profile.TargetSolidPackOff,
                PackOpeningGate04R011Profile.TargetProxyResultOff,
                0.6166667f);
            Assert.That(
                profile.Evaluate(target).PackDissolve,
                Is.EqualTo(0.37030068f).Within(0.00001f));
        }

        [Test]
        public void Tear_StillUsesFiftyMillisecondSnap()
        {
            Assert.That(
                PackOpeningGate04R011Profile.SnapDuration,
                Is.EqualTo(0.05f).Within(0.00001f));
            Assert.That(
                profile.Evaluate(0.90f).TearProgress,
                Is.EqualTo(0.20f).Within(0.002f));
        }

        [Test]
        public void ReduceMotion_PreservesHandoffAndDisablesSensorySystems()
        {
            PackOpeningGate04R011Sample standard = profile.Evaluate(1.93f);
            PackOpeningGate04R011Sample reduced = profile.Evaluate(1.93f, true);
            Assert.That(reduced.Occlusion, Is.EqualTo(standard.Occlusion));
            Assert.That(reduced.PackRetreat, Is.EqualTo(standard.PackRetreat));
            Assert.That(reduced.PackDissolve, Is.EqualTo(standard.PackDissolve));
            Assert.That(reduced.CaseTravel, Is.EqualTo(standard.CaseTravel));
            Assert.That(reduced.ActivationEnabled, Is.False);
            Assert.That(reduced.LightningEnabled, Is.False);
            Assert.That(reduced.ExplosionEnabled, Is.False);
            Assert.That(reduced.CameraKick, Is.EqualTo(Vector2.zero));
            Assert.That(reduced.CameraPush, Is.Zero);
        }

        [Test]
        public void RarityReveal_CannotPrecedeAuthoritativeResultBoundary()
        {
            for (int frame = 0; frame < PackOpeningGate04R011Capture.FrameCount; frame++)
            {
                float time = frame / 60f;
                if (time < PackOpeningGate04R011Profile.TargetRealResultStart)
                {
                    Assert.That(profile.Evaluate(time).RarityReveal, Is.Zero);
                }
            }
            Assert.That(
                profile.Evaluate(
                    PackOpeningGate04R011Profile.CaseSettleEnd).RarityReveal,
                Is.EqualTo(1f));
        }

        [Test]
        public void SemanticEvents_RemainPlatformIndependent()
        {
            Assert.That(
                profile.ResolveSemanticEvents(0f, 3.45f),
                Is.EqualTo(new[]
                {
                    PackOpeningGate04R011SemanticEvent.TearResistance,
                    PackOpeningGate04R011SemanticEvent.TearSnap,
                    PackOpeningGate04R011SemanticEvent.Impact,
                    PackOpeningGate04R011SemanticEvent.CaseSettled
                }));
            string source = File.ReadAllText(AssetAbsolutePath(
                "Assets/_DisplayCase/Candidates/PackOpeningGate04R011/Runtime/PackOpeningGate04R011Profile.cs"));
            StringAssert.DoesNotContain("IosHaptics", source);
            StringAssert.DoesNotContain("UnitySendMessage", source);
        }

        [Test]
        public void DirectCopies_PreserveAuditedSourceHashes()
        {
            Assert.That(
                Sha256(Editor.PackOpeningGate04R011Builder.SourceDiscardClipPath),
                Is.EqualTo(
                    "be661fe81b095f7f1ad08fb2a1c003b15f8690ee08d43f9f705dc849924fb2c6"));
            Assert.That(
                Sha256(Editor.PackOpeningGate04R011Builder.SourceFlareTexturePath),
                Is.EqualTo(
                    "bbf7c86f5435ec3097717ef092e531214916e9cbb7db2b71f059e3d12f90ffa3"));
            Assert.That(
                Sha256(Editor.PackOpeningGate04R011Builder.SourceNoiseTexturePath),
                Is.EqualTo(
                    "2303e1fb3c86af9e9b6a4ccd4ecb615b9cdd172253eea8988c7a6ac4a165e886"));
            Assert.That(
                Sha256(Editor.PackOpeningGate04R011Builder.SourceSelectedGraphPath),
                Is.EqualTo(
                    "75eb59c320c80b693d24d61df3c9238a8670cef64f73247727558e6db512308b"));
            Assert.That(
                Sha256(Editor.PackOpeningGate04R011Builder.SourceCardMaskGraphPath),
                Is.EqualTo(
                    "20bf26a2efe854ee561cbdca77697c63651124ca3c095185837885984f19234c"));
            Assert.That(
                Sha256(
                    "ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-011/source-raw/Booster to Card Timeline.playable"),
                Is.EqualTo(
                    "baec0abcf084db64a2b353947a9e67408e6b41ec27d5c645621d8f93aec9b086"));
        }

        [Test]
        public void Scene_UsesSourceShurikenCapacitiesAndNoGenericRing()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            ParticleSystem[] systems = controller.SourceEffectSystems.ToArray();
            Assert.That(systems.Length, Is.EqualTo(5));
            Assert.That(
                systems.Select(system => system.main.maxParticles),
                Is.EqualTo(new[] { 3, 25, 512, 512, 16 }));
            Assert.That(systems.All(system => !system.useAutoRandomSeed), Is.True);
            Assert.That(systems[1].trails.enabled, Is.True);
            // Every port must address exactly one cell of the source 2x2 flare
            // atlas. Sampling the whole atlas is what drew the four-point star.
            foreach (ParticleSystem system in systems)
            {
                Material material = system
                    .GetComponent<ParticleSystemRenderer>()
                    .sharedMaterial;
                if (!material.HasProperty("_BaseMap"))
                {
                    continue;
                }
                Assert.That(
                    material.GetTextureScale("_BaseMap"),
                    Is.EqualTo(new Vector2(0.5f, 0.5f)),
                    $"{material.name} does not address a single atlas cell.");
            }
            // A spun cell reads as a symmetric sparkle glyph regardless of which
            // cell it is, so only the radial glow port may rotate.
            Assert.That(
                systems[4].rotationOverLifetime.enabled,
                Is.False);
            Assert.That(
                systems[4].main.startSize3D,
                Is.True,
                "Flares must be flattened so the source glyph reads as a streak.");
            Transform effectRoot = FindTransform(
                "AuditedMakeItShineCc0ShurikenPort");
            Transform[] transforms = effectRoot.GetComponentsInChildren<
                Transform>(true);
            Assert.That(
                transforms.Any(value =>
                    value.name.Contains(
                        "EnergyRing",
                        StringComparison.OrdinalIgnoreCase)
                    || value.name.Contains(
                        "PurpleWash",
                        StringComparison.OrdinalIgnoreCase)
                    || value.name.Contains(
                        "Concentric",
                        StringComparison.OrdinalIgnoreCase)),
                Is.False);
        }

        [Test]
        public void Scene_ContainsOneRealCaseAndNoSampleEntity()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            Transform[] transforms = AllTransforms(controller.gameObject.scene);
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
                    || value.name.Contains("BoosterFractured", StringComparison.Ordinal)
                    || value.name.Contains("Card_v", StringComparison.Ordinal)
                    || value.name.Contains("Exploded", StringComparison.OrdinalIgnoreCase)),
                Is.False);
            Assert.That(controller.CasePresentation.ContentSlot, Is.Not.Null);
        }

        [Test]
        public void Timeline_RetainsSourceStructureWithRetargetedBindings()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            PlayableDirector director =
                controller.GetComponent<PlayableDirector>();
            TimelineAsset timeline = (TimelineAsset)director.playableAsset;
            TrackAsset[] tracks = timeline
                .GetRootTracks()
                .SelectMany(track => track.GetChildTracks().Prepend(track))
                .ToArray();
            Assert.That(tracks.Any(track => track.name == "Booster"), Is.True);
            Assert.That(
                tracks.Any(track =>
                    track.name == "VFX_BoosterActivation → Shuriken"),
                Is.True);
            Assert.That(
                tracks.Any(track =>
                    track.name == "VFXG_LightingStrike → Shuriken"),
                Is.True);
            Assert.That(
                tracks.Any(track =>
                    track.name == "VFX_BoosterExplosion → Shuriken"),
                Is.True);
            Assert.That(
                tracks.Any(track =>
                    track.name == "Card Spawn → Existing Assembled Case"),
                Is.True);
            TrackAsset explosion = tracks.Single(track =>
                track.name == "VFX_BoosterExplosion → Shuriken");
            Assert.That(
                explosion.GetClips().Single().start,
                Is.EqualTo(PackOpeningGate04R011Profile.ImpactStart)
                    .Within(0.000001d));
        }

        [Test]
        public void SameCaseInstance_StaysActiveAtConstantScale()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            EntityId rootId = controller.CaseRootEntityId;
            EntityId[] rendererIds = controller.CaseRendererEntityIds.ToArray();
            Vector3 scale = controller.CaseMotionRoot.localScale;
            foreach (float time in new[]
                     {
                         0f, 0.90f, 1.50f, 1.60f, 1.73f, 1.93f, 2.52f, 3.45f
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
        }

        [Test]
        public void Pack_RemainsOccluderWhileSameCaseCrosses()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            controller.SetTime(1.93f, false);
            Assert.That(controller.PackVisible, Is.True);
            Assert.That(
                controller.CurrentSample.Occlusion,
                Is.EqualTo(PackOpeningGate04R011Occlusion.CrossingOccluder));
            Assert.That(controller.CurrentSample.CaseTravel, Is.InRange(0f, 1f));
            controller.SetTime(
                PackOpeningGate04R011Profile.TargetProxyResultOff + 0.02f,
                false);
            Assert.That(controller.PackVisible, Is.False);
            Assert.That(
                controller.CurrentSample.Occlusion,
                Is.EqualTo(PackOpeningGate04R011Occlusion.PackGone));
        }

        [Test]
        public void PhysicalPackBody_DoesNotCullGridChunksDuringDissolve()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            MeshFilter body = FindTransform("PhysicalPackBodyOccluder")
                .GetComponent<MeshFilter>();
            uint expectedIndexCount =
                (uint)PackOpeningGate04R011Controller.StripSegments
                * (uint)PackOpeningGate04R011Controller.BodyRows
                * 6u;
            foreach (float time in new[] { 0f, 1.60f, 1.93f, 2.30f })
            {
                controller.SetTime(time, false);
                Assert.That(
                    body.sharedMesh.GetIndexCount(0),
                    Is.EqualTo(expectedIndexCount));
            }
        }

        [Test]
        public void TearEdge_RemainsSharedAndLowAmplitude()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            controller.SetTime(1.24f, false);
            Assert.That(
                controller.SharedTearOffsets.Max(value => Mathf.Abs(value)),
                Is.LessThanOrEqualTo(
                    PackOpeningGate04R011Controller.MaximumTearAmplitude
                    + 0.000001f));
            Assert.That(
                controller.MaximumAheadOfFrontSeparation,
                Is.LessThan(0.000001f));
        }

        [Test]
        public void PackRetreat_StaysASettleAndLetsTheDiscardCurveRemoveThePack()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            float maximumTravel = 0f;
            for (
                int frame = 0;
                frame < PackOpeningGate04R011Capture.FrameCount;
                frame++)
            {
                controller.SetTime(frame / 60f, false);
                maximumTravel = Mathf.Max(
                    maximumTravel,
                    controller.PackRetreatTravelMeters);
            }
            Assert.That(
                maximumTravel,
                Is.LessThanOrEqualTo(
                    PackOpeningGate04R011Controller
                        .MaximumPackRetreatTravelMeters));
            controller.SetTime(
                PackOpeningGate04R011Profile.TargetProxyResultOff - 0.05f,
                false);
            Assert.That(
                controller.CurrentSample.PackDissolve,
                Is.GreaterThan(0.60f));
        }

        /// <summary>
        /// Iteration 09 receded the front face but had no back wall, side wall or
        /// lip, so the vacated region showed background and the Pack read as
        /// sliced short instead of opened. The interior must exist and grow.
        /// </summary>
        [Test]
        public void Pack_VisiblyOpensInsteadOfBeingSlicedShort()
        {
            PackOpeningGate04R011Controller controller = OpenController();

            controller.SetTime(0f, false);
            Assert.That(
                controller.CavityVisibleColumnCount,
                Is.Zero,
                "A sealed Pack must expose no interior.");

            controller.SetTime(
                PackOpeningGate04R011Profile.SnapEnd + 0.10f,
                false);
            int earlyColumns = controller.CavityVisibleColumnCount;
            float earlyOpening = controller.CavityMaximumOpenHeight;
            Assert.That(
                earlyColumns,
                Is.GreaterThan(0),
                "The interior must be exposed once the tear front has moved.");

            controller.SetTime(
                PackOpeningGate04R011Profile.TargetSolidPackOff - 0.05f,
                false);
            Assert.That(
                controller.CavityVisibleColumnCount,
                Is.GreaterThan(earlyColumns),
                "The opening must widen as the tear front advances.");
            Assert.That(
                controller.CavityMaximumOpenHeight,
                Is.GreaterThan(earlyOpening));
            // The mouth must read in silhouette, but it must not become a wide
            // rectangular cutout that makes the Pack look decapitated.
            Assert.That(
                controller.CavityMaximumOpenHeight,
                Is.GreaterThan(PackOpeningGate04R011Controller.PackHeight * 0.055f));
            Assert.That(
                controller.CavityMaximumOpenHeight,
                Is.LessThan(PackOpeningGate04R011Controller.PackHeight * 0.10f));
            Assert.That(
                controller.CavityVisible,
                Is.True);
        }

        [Test]
        public void PackStaysVisibleUntilTheDiscardCurveReachesOne()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            for (
                int frame = 0;
                frame < PackOpeningGate04R011Capture.FrameCount;
                frame++)
            {
                controller.SetTime(frame / 60f, false);
                if (!controller.PackVisible)
                {
                    Assert.That(
                        controller.CurrentSample.PackDissolve,
                        Is.EqualTo(1f).Within(0.0001f),
                        $"Pack hidden at frame {frame} with dissolve "
                        + controller.CurrentSample.PackDissolve);
                }
            }
        }

        /// <summary>
        /// The back wall must sit behind the concealed case so the case is inside
        /// the cavity rather than behind an intact bag.
        /// </summary>
        [Test]
        public void CaseIsConcealedInsideTheCavityNotBehindTheBag()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            controller.SetTime(0f, false);

            // Both values are world space on purpose. The iteration-10 version of
            // this test compared a cavity-local constant against the case root's
            // world z, so it passed while the wall was actually between the camera
            // and the case and the mouth rendered as an empty slab.
            float wallWorldZ = controller.InteriorBackWallWorldZ;
            float caseRearWorldZ = controller.CaseRearWorldZ;
            Assert.That(
                caseRearWorldZ,
                Is.Not.NaN,
                "The case must expose renderers to measure.");
            Assert.That(
                wallWorldZ,
                Is.GreaterThan(caseRearWorldZ),
                "The bag's back panel must be farther from the camera than the "
                    + "rear of the concealed case, otherwise it occludes the "
                    + "case and the mouth reveals nothing.");
        }

        /// <summary>
        /// The interior must read as one surface. Iteration 10 built it from one
        /// unwelded quad per column, so neighbouring columns had different
        /// normals and the mouth rendered as a 48-stripe vertical comb.
        /// </summary>
        [Test]
        public void CavityInteriorIsOneWeldedSurfaceNotAPerColumnComb()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            controller.SetTime(
                PackOpeningGate04R011Profile.SnapEnd + 0.30f,
                false);
            Assert.That(
                controller.CavityVisibleColumnCount,
                Is.GreaterThan(4),
                "This assertion needs an open mouth to measure.");
            Assert.That(
                controller.CavityInteriorMaxAdjacentNormalAngleDegrees,
                Is.LessThan(1.5f),
                "Neighbouring interior columns must share normals, otherwise the "
                    + "mouth renders as a vertical comb.");
        }

        /// <summary>
        /// The camera looks along +z from world z -1.35, so "in front of" means a
        /// smaller z. The concealed case must be in front of the back panel and
        /// behind the Pack's front face: that is what "inside the cavity" means.
        /// </summary>
        [Test]
        public void ConcealedCaseSitsBetweenThePackFrontFaceAndTheBackPanel()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            controller.SetTime(0f, false);
            float caseRearWorldZ = controller.CaseRearWorldZ;
            float packFrontWorldZ = controller.PackFrontFaceWorldZ;
            Assert.That(
                caseRearWorldZ,
                Is.GreaterThan(packFrontWorldZ),
                "The concealed case must be behind the Pack's front face.");
            Assert.That(
                controller.InteriorBackWallWorldZ,
                Is.GreaterThan(caseRearWorldZ),
                "The concealed case must be in front of the back panel.");
        }

        /// <summary>
        /// The audited discard edge sweep is the identity of this revision. Keying
        /// it off PackDissolve left it dark for the whole tear.
        /// </summary>
        [Test]
        public void SourceEdgeSweep_IsLitWhileThePackIsStillFullyOpaque()
        {
            PackOpeningGate04R011Sample tearSample = profile.Evaluate(
                PackOpeningGate04R011Profile.SnapEnd + 0.25f);
            Assert.That(
                tearSample.PackDissolve,
                Is.EqualTo(0f).Within(0.000001f),
                "This assertion is only meaningful before the dissolve starts.");
            Assert.That(
                tearSample.TearProgress,
                Is.GreaterThan(0.20f));
            Assert.That(
                PackOpeningGate04R011Controller.TearSweepStrength(tearSample),
                Is.GreaterThan(0.55f),
                "The source sweep must be visible during the tear.");

            PackOpeningGate04R011Sample sealedSample = profile.Evaluate(0f);
            Assert.That(
                PackOpeningGate04R011Controller.TearSweepStrength(sealedSample),
                Is.EqualTo(0f).Within(0.000001f),
                "A sealed Pack must not glow.");

            PackOpeningGate04R011Sample dissolveSample = profile.Evaluate(
                PackOpeningGate04R011Profile.TargetProxyResultOff - 0.05f);
            Assert.That(
                PackOpeningGate04R011Controller.TearSweepStrength(dissolveSample),
                Is.GreaterThan(0.55f),
                "The sweep must stay lit through the dissolve, not restart there.");
        }

        /// <summary>
        /// A smooth C1 curve reads as a machine-cut scallop. The torn edge needs
        /// high-frequency reversals at column scale.
        /// </summary>
        [Test]
        public void TornEdge_IsIrregularRatherThanASmoothCurve()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            controller.SetTime(
                PackOpeningGate04R011Profile.SnapEnd + 0.20f,
                false);
            System.Collections.Generic.IReadOnlyList<float> offsets =
                controller.SharedTearOffsets;
            int reversals = 0;
            for (int index = 2; index < offsets.Count; index++)
            {
                float previousDelta = offsets[index - 1] - offsets[index - 2];
                float delta = offsets[index] - offsets[index - 1];
                if (previousDelta * delta < 0f)
                {
                    reversals++;
                }
            }
            // A pure two-term sine over 48 columns yields only a handful of
            // reversals; genuine irregularity produces many more.
            Assert.That(
                reversals,
                Is.GreaterThan(offsets.Count / 4),
                $"Only {reversals} slope reversals across {offsets.Count} columns.");
        }

        [Test]
        public void FreedFoil_CurlsWithoutPresentingItsWidthToCamera()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            controller.SetTime(1.42f, false);
            Assert.That(
                controller.MeasureFreedTailCurvature(
                    controller.CurrentSample.TearProgress),
                Is.GreaterThan(0.0005f));
            Assert.That(
                PackOpeningGate04R011Controller.FreedFoilTwistDegrees,
                Is.LessThanOrEqualTo(40f));
            Assert.That(
                PackOpeningGate04R011Controller.SealedFoilTwistDegrees,
                Is.LessThan(
                    PackOpeningGate04R011Controller.FreedFoilTwistDegrees));
            Assert.That(
                PackOpeningGate04R011Controller.StripRows,
                Is.GreaterThanOrEqualTo(8),
                "The peel needs enough cross-section rows to render a curl.");
        }

        [Test]
        public void BelowThresholdRebound_RestoresStateExactly()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            controller.SetTime(0.76f, false);
            Assert.That(
                controller.CurrentStateFingerprint,
                Is.Not.EqualTo(controller.SealedStateFingerprint));
            Assert.That(controller.ReboundToSealed(), Is.True);
        }

        [Test]
        public void ProjectedCaseBounds_FollowContinuousCurve()
        {
            PackOpeningGate04R011Controller controller = OpenController();
            Camera camera = Camera.main;
            camera.aspect =
                PackOpeningGate04R011Capture.Width
                / (float)PackOpeningGate04R011Capture.Height;
            Rect previous = default;
            float maximumCenterStep = 0f;
            float maximumHeightStep = 0f;
            for (int frame = 0; frame < PackOpeningGate04R011Capture.FrameCount; frame++)
            {
                controller.SetTime(frame / 60f, false);
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
        public void ActualProductAssets_PreserveHashesAndPackCanvas()
        {
            Assert.That(
                Sha256(Editor.PackOpeningGate04R011Builder.PackBodyPath),
                Is.EqualTo(
                    "ebc17bb238ebbcb82d36134bb2781838df610f8a3d1750c27b8ade10fc4681d6"));
            Assert.That(
                Sha256(Editor.PackOpeningGate04R011Builder.PackFlapPath),
                Is.EqualTo(
                    "b031fc5c57d194e9603e9b32e1cd603285aa564490f599f29bb0cd67dab33d49"));
            Assert.That(
                Sha256(Editor.PackOpeningGate04R011Builder.ActualCasePrefabPath),
                Is.EqualTo(
                    "7a96aae6245b5a1d5463dabc3cb4518af8693ba8f8328ad9f2fe4ee6c6a67e2c"));
            Texture2D body = AssetDatabase.LoadAssetAtPath<Texture2D>(
                Editor.PackOpeningGate04R011Builder.PackBodyPath);
            Assert.That(body, Is.Not.Null);
            Assert.That(
                ReadPngDimensions(
                    Editor.PackOpeningGate04R011Builder.PackBodyPath),
                Is.EqualTo(new Vector2Int(384, 512)));
        }

        [Test]
        public void SourceMapping_RecordsDirectAdaptedAndRejectedAssets()
        {
            string mapping = File.ReadAllText(AssetAbsolutePath(
                Editor.PackOpeningGate04R011Builder.EvidenceIterationRoot
                + "/source-to-canonical-mapping.json"));
            StringAssert.Contains("\"decision\": \"direct-copy\"", mapping);
            StringAssert.Contains("\"decision\": \"adapted\"", mapping);
            StringAssert.Contains("\"decision\": \"rejected\"", mapping);
            StringAssert.Contains(SourceFlareHash, mapping);
            StringAssert.Contains("\"vfxGraphDependency\": false", mapping);
            StringAssert.Contains("\"shippingReady\": false", mapping);
        }

        [Test]
        public void CandidateSources_HaveNoVfxGraphUiOrDirectHaptics()
        {
            string root = AssetAbsolutePath(
                "Assets/_DisplayCase/Candidates/PackOpeningGate04R011");
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
            StringAssert.DoesNotContain("IosHaptics", sources);
            StringAssert.DoesNotContain("ProductPrimaryActionButton", sources);
            StringAssert.DoesNotContain("StartGachaRevealFromNativeUi", sources);
        }

        private const string SourceFlareHash =
            "bbf7c86f5435ec3097717ef092e531214916e9cbb7db2b71f059e3d12f90ffa3";

        private static PackOpeningGate04R011Controller OpenController()
        {
            Assert.That(
                File.Exists(AssetAbsolutePath(
                    Editor.PackOpeningGate04R011Builder.ScenePath)),
                Is.True,
                "Build the rev 11 scene before tests.");
            Scene scene = EditorSceneManager.OpenScene(
                Editor.PackOpeningGate04R011Builder.ScenePath,
                OpenSceneMode.Single);
            PackOpeningGate04R011Controller controller = scene
                .GetRootGameObjects()
                .SelectMany(root =>
                    root.GetComponentsInChildren<
                        PackOpeningGate04R011Controller>(true))
                .Single();
            controller.SetTime(0f, false);
            return controller;
        }

        private static Transform[] AllTransforms(Scene scene)
        {
            return scene
                .GetRootGameObjects()
                .SelectMany(root =>
                    root.GetComponentsInChildren<Transform>(true))
                .ToArray();
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
            int width = header[16] << 24
                | header[17] << 16
                | header[18] << 8
                | header[19];
            int height = header[20] << 24
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
