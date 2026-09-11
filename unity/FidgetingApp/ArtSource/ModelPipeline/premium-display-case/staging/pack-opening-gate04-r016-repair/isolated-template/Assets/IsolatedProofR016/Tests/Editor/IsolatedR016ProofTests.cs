using System;
using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase.IsolatedCandidate.R016;
using FidgetingApp.DisplayCase.IsolatedCandidate.R016.Editor;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R016.Tests
{
    public sealed class IsolatedR016ProofTests
    {
        [Test]
        public void ProfileLocksShortProofSevenPosesAndCompactSeal()
        {
            Assert.That(
                IsolatedR016Profile.TotalSeconds,
                Is.InRange(1.2f, 1.8f));
            Assert.That(
                IsolatedR016Profile.AuthoredPoseProgresses.Length,
                Is.EqualTo(7));
            Assert.That(
                IsolatedR016ProofSequence.TopSealHeightFraction,
                Is.InRange(0.06f, 0.10f));
        }

        [Test]
        public void ImportedRigIsPackOnlyAndPreservesAuthoredPoses()
        {
            GameObject rig = AssetDatabase.LoadAssetAtPath<GameObject>(
                "Assets/Source/R016/PackOpeningGate04R016PackOnlyRig.fbx");
            Assert.That(rig, Is.Not.Null);
            SkinnedMeshRenderer[] renderers =
                rig.GetComponentsInChildren<SkinnedMeshRenderer>(true);
            Assert.That(
                renderers.Length,
                Is.EqualTo(IsolatedR016ProofSequence.ExpectedRendererCount));
            Assert.That(
                renderers.All(renderer =>
                    renderer.sharedMesh.blendShapeCount
                        == IsolatedR016ProofSequence.ExpectedBlendShapeCount),
                Is.True);
            Assert.That(
                rig.GetComponentsInChildren<Transform>(true).Any(item =>
                    item.name.Contains("Case", StringComparison.Ordinal)
                    || item.name.Contains("Prize", StringComparison.Ordinal)),
                Is.False);
        }

        [Test]
        public void ImportedFrontFoilMapsFidgetArchiveAboveStandard()
        {
            Texture2D artwork = AssetDatabase.LoadAssetAtPath<Texture2D>(
                "Assets/Source/Pack/gacha-pack-standard-body.png");
            Assert.That(artwork, Is.Not.Null);
            Assert.That(artwork.width, Is.EqualTo(384));
            Assert.That(artwork.height, Is.EqualTo(512));
            GameObject rig = AssetDatabase.LoadAssetAtPath<GameObject>(
                "Assets/Source/R016/PackOpeningGate04R016PackOnlyRig.fbx");
            SkinnedMeshRenderer front = rig.GetComponentsInChildren<
                SkinnedMeshRenderer>(true).Single(item =>
                item.name == "Pack_FrontPrintedFoil");
            float archiveY = ObjectYAtArtworkV(front.sharedMesh, 0.735f);
            float standardY = ObjectYAtArtworkV(front.sharedMesh, 0.215f);
            Assert.That(
                archiveY,
                Is.GreaterThan(standardY + 0.10f),
                "FIDGET ARCHIVE must map above STANDARD in object space.");
        }

        [Test]
        public void ReversedProgressReturnsEveryPackStateToSealed()
        {
            IsolatedR016ProofSequence sequence =
                IsolatedR016ProofBuilder.BuildSequenceForTests();
            string sealedFingerprint = sequence.SealedStateFingerprint;
            sequence.SetNormalizedTearProgress(0.28f);
            Assert.That(sequence.PackVisible, Is.True);
            sequence.SetNormalizedTearProgress(0.86f);
            Assert.That(sequence.MouthContactOcclusionActive, Is.True);
            Assert.That(sequence.ReboundToSealed(), Is.True);
            Assert.That(
                sequence.CurrentStateFingerprint,
                Is.EqualTo(sealedFingerprint));
        }

        [Test]
        public void OneLiveCaseRemainsContainedBeforeVerticalExtraction()
        {
            IsolatedR016ProofSequence sequence =
                IsolatedR016ProofBuilder.BuildSequenceForTests();
            sequence.SetTime(0.94f, false);
            Assert.That(
                sequence.CurrentSample.Occlusion,
                Is.EqualTo(IsolatedR016Occlusion.CaseContained));
            Assert.That(sequence.IsCaseContainedInMouth(), Is.True);
            EntityId rootId = sequence.CaseRootId;
            EntityId[] rendererIds = sequence.CaseRendererIds.ToArray();
            Vector3 scale = sequence.CaseAuthoredScale;
            sequence.SetTime(1.16f, false);
            Assert.That(
                sequence.CurrentSample.Occlusion,
                Is.EqualTo(IsolatedR016Occlusion.CaseCrossingMouth));
            Assert.That(sequence.CaseRootId, Is.EqualTo(rootId));
            Assert.That(sequence.CaseRendererIds, Is.EqualTo(rendererIds));
            Assert.That(sequence.CaseMotionRootScale, Is.EqualTo(scale));
            Assert.That(
                sequence.CaseMotionRootPosition.y,
                Is.GreaterThan(-0.030f));
        }

        [Test]
        public void CandidateHasNoParticlesVfxHapticsOrBusinessUi()
        {
            string root = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "IsolatedProofR016"));
            string source = string.Join(
                "\n",
                Directory.GetFiles(
                    root,
                    "*.*",
                    SearchOption.AllDirectories)
                    .Where(path =>
                        !path.Contains(
                            $"{Path.DirectorySeparatorChar}Tests{Path.DirectorySeparatorChar}",
                            StringComparison.Ordinal)
                        && (path.EndsWith(".cs", StringComparison.Ordinal)
                            || path.EndsWith(".shader", StringComparison.Ordinal)))
                    .Select(File.ReadAllText));
            StringAssert.DoesNotContain("ParticleSystem", source);
            StringAssert.DoesNotContain("UnityEngine.VFX", source);
            StringAssert.DoesNotContain("IosHaptics", source);
            StringAssert.DoesNotContain("ProductPrimaryActionButton", source);
            StringAssert.DoesNotContain("DOTween", source);
            StringAssert.DoesNotContain("PrimeTween", source);
        }

        private static float ObjectYAtArtworkV(Mesh mesh, float targetV)
        {
            Vector2[] uvs = mesh.uv;
            Vector3[] vertices = mesh.vertices;
            float nearest = float.PositiveInfinity;
            for (int index = 0; index < uvs.Length; index++)
            {
                nearest = Mathf.Min(nearest, Mathf.Abs(uvs[index].y - targetV));
            }

            float total = 0f;
            int count = 0;
            for (int index = 0; index < uvs.Length; index++)
            {
                if (Mathf.Abs(uvs[index].y - targetV) <= nearest + 0.00001f)
                {
                    total += vertices[index].y;
                    count++;
                }
            }
            Assert.That(count, Is.GreaterThan(0));
            return total / count;
        }
    }
}
