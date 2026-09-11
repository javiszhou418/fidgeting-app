using System;
using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase.IsolatedCandidate.R018;
using FidgetingApp.DisplayCase.IsolatedCandidate.R018.Editor;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R018.Tests
{
    public sealed class IsolatedR018ProofTests
    {
        [Test]
        public void ProfileLocksShortProofSevenPosesAndCompactSeal()
        {
            Assert.That(
                IsolatedR018Profile.TotalSeconds,
                Is.InRange(1.2f, 1.8f));
            Assert.That(
                IsolatedR018Profile.AuthoredPoseProgresses.Length,
                Is.EqualTo(7));
            Assert.That(
                IsolatedR018ProofSequence.TopSealHeightFraction,
                Is.InRange(0.06f, 0.10f));
        }

        [Test]
        public void SourceArtworkRetainsIts384x512Canvas()
        {
            Texture2D artwork = AssetDatabase.LoadAssetAtPath<Texture2D>(
                "Assets/Source/Pack/gacha-pack-standard-body.png");
            Assert.That(artwork, Is.Not.Null);
            var rawArtwork = new Texture2D(
                2,
                2,
                TextureFormat.RGBA32,
                false);
            try
            {
                Assert.That(
                    ImageConversion.LoadImage(
                        rawArtwork,
                        File.ReadAllBytes(
                            AssetDatabase.GetAssetPath(artwork))),
                    Is.True);
                Assert.That(rawArtwork.width, Is.EqualTo(384));
                Assert.That(rawArtwork.height, Is.EqualTo(512));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(rawArtwork);
            }
        }

        [Test]
        public void ImportedRigIsPackOnlyAndPreservesAuthoredPoses()
        {
            GameObject rig = AssetDatabase.LoadAssetAtPath<GameObject>(
                "Assets/Source/R018/PackOpeningGate04R018PackOnlyRig.fbx");
            Assert.That(rig, Is.Not.Null);
            SkinnedMeshRenderer[] renderers =
                rig.GetComponentsInChildren<SkinnedMeshRenderer>(true);
            Assert.That(
                renderers.Length,
                Is.EqualTo(IsolatedR018ProofSequence.ExpectedRendererCount));
            Assert.That(
                renderers.All(renderer =>
                    renderer.sharedMesh.blendShapeCount
                        == IsolatedR018ProofSequence.ExpectedBlendShapeCount),
                Is.True);
            Assert.That(
                rig.GetComponentsInChildren<Transform>(true).Any(item =>
                    item.name.Contains("Case", StringComparison.Ordinal)
                    || item.name.Contains("Prize", StringComparison.Ordinal)),
                Is.False);
            GameObject r017Control = AssetDatabase.LoadAssetAtPath<GameObject>(
                "Assets/Source/R017Control/PackOpeningGate04R017MirrorControl.fbx");
            Assert.That(r017Control, Is.Not.Null);
        }

        [Test]
        public void ImportedFrontFoilUsesPhysicalTopAndCameraFacingWinding()
        {
            GameObject rig = AssetDatabase.LoadAssetAtPath<GameObject>(
                "Assets/Source/R018/PackOpeningGate04R018PackOnlyRig.fbx");
            SkinnedMeshRenderer front = rig.GetComponentsInChildren<
                SkinnedMeshRenderer>(true).Single(item =>
                item.name == "Pack_FrontPrintedFoil");
            float bottomY = ObjectYAtArtworkV(front.sharedMesh, 0.020f);
            float topY = ObjectYAtArtworkV(front.sharedMesh, 0.815f);
            float archiveY = ObjectYAtArtworkV(front.sharedMesh, 0.735f);
            float standardY = ObjectYAtArtworkV(front.sharedMesh, 0.215f);
            Assert.That(
                topY,
                Is.GreaterThan(bottomY + 0.25f),
                "The tear seam must be the physical Pack top.");
            Assert.That(
                archiveY,
                Is.GreaterThan(standardY + 0.10f),
                "FIDGET ARCHIVE must map above STANDARD in object space.");
            Assert.That(
                front.sharedMesh.normals.Average(normal => normal.z),
                Is.LessThan(-0.90f),
                "Bottom-to-top rows must retain front camera-facing winding.");
        }

        [Test]
        public void ReversedProgressReturnsEveryPackStateToSealed()
        {
            IsolatedR018ProofSequence sequence =
                IsolatedR018ProofBuilder.BuildSequenceForTests();
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
            IsolatedR018ProofSequence sequence =
                IsolatedR018ProofBuilder.BuildSequenceForTests();
            sequence.SetTime(0.94f, false);
            Assert.That(
                sequence.CurrentSample.Occlusion,
                Is.EqualTo(IsolatedR018Occlusion.CaseContained));
            Assert.That(sequence.IsCaseContainedInMouth(), Is.True);
            EntityId rootId = sequence.CaseRootId;
            EntityId[] rendererIds = sequence.CaseRendererIds.ToArray();
            Vector3 scale = sequence.CaseAuthoredScale;
            sequence.SetTime(1.16f, false);
            Assert.That(
                sequence.CurrentSample.Occlusion,
                Is.EqualTo(IsolatedR018Occlusion.CaseCrossingMouth));
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
                "IsolatedProofR018"));
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
            Assert.That(Shader.Find(
                "FidgetingApp/Isolated/R018/OrientationCalibrationUnlit"),
                Is.Not.Null);
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
