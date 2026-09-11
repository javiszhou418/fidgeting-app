using System;
using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase.IsolatedCandidate.R021;
using FidgetingApp.DisplayCase.IsolatedCandidate.R021.Editor;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R021.Tests
{
    public sealed class IsolatedR021ProofTests
    {
        [Test]
        public void ProfileLocksShortProofSevenPosesAndCompactSeal()
        {
            Assert.That(
                IsolatedR021Profile.TotalSeconds,
                Is.InRange(1.2f, 1.8f));
            Assert.That(
                IsolatedR021Profile.AuthoredPoseProgresses.Length,
                Is.EqualTo(7));
            CollectionAssert.AreEqual(
                new[] { 0f, 0.11f, 0.28f, 0.50f, 0.70f, 0.86f, 1f },
                IsolatedR021Profile.AuthoredPoseProgresses);
            Assert.That(
                IsolatedR021ProofSequence.TopSealHeightFraction,
                Is.InRange(0.015f, 0.030f));
            Assert.That(
                IsolatedR021ProofSequence.ReleasedStripHeightFraction,
                Is.InRange(0.035f, 0.065f));
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
                "Assets/Source/R021/PackOpeningGate04R021PackOnlyRig.fbx");
            Assert.That(rig, Is.Not.Null);
            SkinnedMeshRenderer[] renderers =
                rig.GetComponentsInChildren<SkinnedMeshRenderer>(true);
            Assert.That(
                renderers.Length,
                Is.EqualTo(IsolatedR021ProofSequence.ExpectedRendererCount));
            Assert.That(
                renderers.All(renderer =>
                    renderer.sharedMesh.blendShapeCount
                        == IsolatedR021ProofSequence.ExpectedBlendShapeCount),
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
                "Assets/Source/R021/PackOpeningGate04R021PackOnlyRig.fbx");
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

        [TestCase(0.35f, 0.12f, 0.38f)]
        [TestCase(0.70f, 0.68f, 0.70f)]
        [TestCase(0.90f, 0.93f, 0.96f)]
        public void TopSealUsesAContinuousScreenRightTearFront(
            float progress,
            float lowerBound,
            float upperBound)
        {
            IsolatedR021ProofSequence sequence =
                IsolatedR021ProofBuilder.BuildSequenceForTests();
            Material material = sequence.TopSeal.sharedMaterial;
            Assert.That(material, Is.Not.Null);
            Assert.That(
                material.shader.name,
                Is.EqualTo("FidgetingApp/Isolated/R021/TopSealTearClip"));
            Assert.That(material.HasProperty("_TearFront"), Is.True);
            sequence.SetNormalizedTearProgress(progress);
            Assert.That(
                sequence.NormalizedTearFront,
                Is.InRange(lowerBound, upperBound));
        }

        [Test]
        public void TopRightStripRuleWouldRejectR018LeftSideFrame()
        {
            bool r018Passes = IsolatedR021Preflight
                .MeetsTopRightStripBoundsForTesting(
                    new Rect(0.312724f, 0.239136f, 0.374552f, 0.529367f),
                    new Rect(0.313002f, 0.648468f, 0.373997f, 0.133325f),
                    new Rect(0.309498f, 0.733028f, 0.078143f, 0.079429f),
                    new Rect(0.300067f, 0.763760f, 0.050580f, 0.059746f),
                    new Vector2(0.330f, 0.770f));
            Assert.That(
                r018Passes,
                Is.False,
                "The actual R018 left-side strip bounds must fail R021.");
        }

        [Test]
        public void ReversedProgressReturnsEveryPackStateToSealed()
        {
            IsolatedR021ProofSequence sequence =
                IsolatedR021ProofBuilder.BuildSequenceForTests();
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
            IsolatedR021ProofSequence sequence =
                IsolatedR021ProofBuilder.BuildSequenceForTests();
            sequence.SetTime(0.94f, false);
            Assert.That(
                sequence.CurrentSample.Occlusion,
                Is.EqualTo(IsolatedR021Occlusion.CaseContained));
            Assert.That(sequence.IsCaseContainedInMouth(), Is.True);
            EntityId rootId = sequence.CaseRootId;
            EntityId[] rendererIds = sequence.CaseRendererIds.ToArray();
            Vector3 scale = sequence.CaseAuthoredScale;
            sequence.SetTime(1.16f, false);
            Assert.That(
                sequence.CurrentSample.Occlusion,
                Is.EqualTo(IsolatedR021Occlusion.CaseCrossingMouth));
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
                "IsolatedProofR021"));
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
                "FidgetingApp/Isolated/R021/OrientationCalibrationUnlit"),
                Is.Not.Null);
            Assert.That(Shader.Find(
                "FidgetingApp/Isolated/R021/RenderedBandMaskUnlit"),
                Is.Not.Null);
            Assert.That(Shader.Find(
                "FidgetingApp/Isolated/R021/TopSealTearClip"),
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
