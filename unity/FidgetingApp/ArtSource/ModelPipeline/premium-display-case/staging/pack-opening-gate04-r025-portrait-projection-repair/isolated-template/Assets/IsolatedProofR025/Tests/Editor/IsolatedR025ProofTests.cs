using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using FidgetingApp.DisplayCase.IsolatedCandidate.R025;
using FidgetingApp.DisplayCase.IsolatedCandidate.R025.Editor;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R025.Tests
{
    public sealed class IsolatedR025ProofTests
    {
        [Test]
        public void ProfileLocksShortProofSevenPosesAndCompactSeal()
        {
            Assert.That(
                IsolatedR025Profile.TotalSeconds,
                Is.InRange(1.2f, 1.8f));
            Assert.That(
                IsolatedR025Profile.AuthoredPoseProgresses.Length,
                Is.EqualTo(7));
            CollectionAssert.AreEqual(
                new[] { 0f, 0.11f, 0.28f, 0.50f, 0.70f, 0.86f, 1f },
                IsolatedR025Profile.AuthoredPoseProgresses);
            Assert.That(
                IsolatedR025ProofSequence.TopSealHeightFraction,
                Is.InRange(0.015f, 0.030f));
            Assert.That(
                IsolatedR025ProofSequence.ReleasedStripHeightFraction,
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
                "Assets/Source/R024/PackOpeningGate04R024PackOnlyRig.fbx");
            Assert.That(rig, Is.Not.Null);
            SkinnedMeshRenderer[] renderers =
                rig.GetComponentsInChildren<SkinnedMeshRenderer>(true);
            Assert.That(
                renderers.Length,
                Is.EqualTo(IsolatedR025ProofSequence.ExpectedRendererCount));
            Assert.That(
                renderers.All(renderer =>
                    renderer.sharedMesh.blendShapeCount
                        == IsolatedR025ProofSequence.ExpectedBlendShapeCount),
                Is.True);
            Assert.That(
                renderers.All(renderer =>
                    renderer.rootBone == null
                    && renderer.bones.Length == 0
                    && renderer.sharedMesh.bindposes.Length == 0),
                Is.True);
            Assert.That(
                renderers.All(renderer =>
                    renderer.transform.localPosition.sqrMagnitude
                        <= 0.0000000001f
                    && Quaternion.Angle(
                        renderer.transform.localRotation,
                        Quaternion.identity) <= 0.0001f
                    && (renderer.transform.localScale - Vector3.one)
                        .sqrMagnitude <= 0.0000000001f),
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
        public void R024FbxHashRemainsTheExactR025Input()
        {
            GameObject rig = AssetDatabase.LoadAssetAtPath<GameObject>(
                "Assets/Source/R024/PackOpeningGate04R024PackOnlyRig.fbx");
            Assert.That(rig, Is.Not.Null);
            byte[] bytes = File.ReadAllBytes(AssetDatabase.GetAssetPath(rig));
            using SHA256 sha = SHA256.Create();
            string hash = string.Concat(sha.ComputeHash(bytes)
                .Select(value => value.ToString("x2")));
            Assert.That(
                hash,
                Is.EqualTo(
                    "a7a8c6ae76a89355cb2f74978f896bdcedba062b8fa02624ffae07803f4f8810"));
        }

        [Test]
        public void PortraitRenderSessionAppliesAndRestoresTargetProjection()
        {
            IsolatedR025ProofSequence sequence =
                IsolatedR025ProofBuilder.BuildSequenceForTests();
            Camera camera = sequence.CaptureCamera;
            float originalAspect = camera.aspect;
            RenderTexture originalTarget = camera.targetTexture;
            float expectedAspect = IsolatedR025ProofCapture.Width
                / (float)IsolatedR025ProofCapture.Height;
            using (var render = new IsolatedR025PortraitRenderSession(
                camera,
                IsolatedR025ProofCapture.Width,
                IsolatedR025ProofCapture.Height))
            {
                Assert.That(camera.aspect, Is.EqualTo(expectedAspect));
                Assert.That(render.TargetAspect, Is.EqualTo(expectedAspect));
                Assert.That(camera.targetTexture, Is.Not.Null);
                Assert.That(
                    sequence.TryGetPackBodyViewportBounds(out _),
                    Is.True);
            }
            Assert.That(camera.aspect, Is.EqualTo(originalAspect));
            Assert.That(camera.targetTexture, Is.EqualTo(originalTarget));
        }

        [Test]
        public void ImportedFrontFoilUsesPhysicalTopAndCameraFacingWinding()
        {
            GameObject rig = AssetDatabase.LoadAssetAtPath<GameObject>(
                "Assets/Source/R024/PackOpeningGate04R024PackOnlyRig.fbx");
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
        public void TopSealUsesSegmentedPhysicalScreenRightTearFront(
            float progress,
            float lowerBound,
            float upperBound)
        {
            IsolatedR025ProofSequence sequence =
                IsolatedR025ProofBuilder.BuildSequenceForTests();
            Material material = sequence.TopSeal.sharedMaterial;
            Assert.That(material, Is.Not.Null);
            Assert.That(
                material.shader.name,
                Is.EqualTo("Universal Render Pipeline/Lit"));
            Assert.That(material.HasProperty("_TearFront"), Is.False);
            sequence.SetNormalizedTearProgress(progress);
            Assert.That(
                sequence.NormalizedTearFront,
                Is.InRange(lowerBound, upperBound));
        }

        [Test]
        public void MouthUsesFineIndependentSegmentsWithoutATransverseRoof()
        {
            IsolatedR025ProofSequence sequence =
                IsolatedR025ProofBuilder.BuildSequenceForTests();
            sequence.SetNormalizedTearProgress(0.70f);
            foreach (SkinnedMeshRenderer renderer in new[]
                     {
                         sequence.TopSeal,
                         sequence.InnerMouth,
                         sequence.InnerBackRim,
                         sequence.RolledCrimpLip
                     })
            {
                Mesh mesh = renderer.sharedMesh;
                Assert.That(mesh, Is.Not.Null);
                Assert.That(
                    MaximumTriangleSpanX(mesh),
                    Is.LessThanOrEqualTo(0.0056f),
                    $"{renderer.name} bridges more than one 49-station segment.");
            }
            Assert.That(
                IsolatedR025ProofSequence.LinerDepthMeters,
                Is.InRange(0.003f, 0.006f));
        }

        [TestCase(0.50f)]
        [TestCase(0.70f)]
        [TestCase(0.90f)]
        public void InterpolatedCollapsedSegmentsStayLocalAtStaticFrames(
            float seconds)
        {
            IsolatedR025ProofSequence sequence =
                IsolatedR025ProofBuilder.BuildSequenceForTests();
            sequence.SetTime(seconds, false);
            foreach (SkinnedMeshRenderer renderer in new[]
                     {
                         sequence.PackRenderers.Single(item =>
                             item.name == "Pack_RearInnerFoil"),
                         sequence.TopSeal,
                         sequence.InnerMouth,
                         sequence.InnerBackRim,
                         sequence.RolledCrimpLip,
                         sequence.TornContour
                     })
            {
                AssertInterpolatedSegmentsStayLocal(renderer);
            }
        }

        [Test]
        public void TopRightStripRuleWouldRejectR018LeftSideFrame()
        {
            bool r018Passes = IsolatedR025Preflight
                .MeetsTopRightStripBoundsForTesting(
                    new Rect(0.312724f, 0.239136f, 0.374552f, 0.529367f),
                    new Rect(0.313002f, 0.648468f, 0.373997f, 0.133325f),
                    new Rect(0.309498f, 0.733028f, 0.078143f, 0.079429f),
                    new Rect(0.300067f, 0.763760f, 0.050580f, 0.059746f),
                    new Vector2(0.330f, 0.770f));
            Assert.That(
                r018Passes,
                Is.False,
                "The actual R018 left-side strip bounds must fail R025.");
        }

        [Test]
        public void ReversedProgressReturnsEveryPackStateToSealed()
        {
            IsolatedR025ProofSequence sequence =
                IsolatedR025ProofBuilder.BuildSequenceForTests();
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
            IsolatedR025ProofSequence sequence =
                IsolatedR025ProofBuilder.BuildSequenceForTests();
            sequence.SetTime(0.94f, false);
            Assert.That(
                sequence.CurrentSample.Occlusion,
                Is.EqualTo(IsolatedR025Occlusion.CaseContained));
            Assert.That(sequence.IsCaseContainedInMouth(), Is.True);
            EntityId rootId = sequence.CaseRootId;
            EntityId[] rendererIds = sequence.CaseRendererIds.ToArray();
            Vector3 scale = sequence.CaseAuthoredScale;
            sequence.SetTime(1.16f, false);
            Assert.That(
                sequence.CurrentSample.Occlusion,
                Is.EqualTo(IsolatedR025Occlusion.CaseCrossingMouth));
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
                "IsolatedProofR025"));
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
                "FidgetingApp/Isolated/R025/OrientationCalibrationUnlit"),
                Is.Not.Null);
            Assert.That(Shader.Find(
                "FidgetingApp/Isolated/R025/RenderedBandMaskUnlit"),
                Is.Not.Null);
            StringAssert.DoesNotContain("TopSealTearClip", source);
            StringAssert.DoesNotContain("_Tear" + "Front (", source);
        }

        private static float MaximumTriangleSpanX(Mesh mesh)
        {
            Vector3[] vertices = mesh.vertices;
            int[] triangles = mesh.triangles;
            float maximum = 0f;
            for (int index = 0; index < triangles.Length; index += 3)
            {
                float min = Mathf.Min(
                    vertices[triangles[index]].x,
                    vertices[triangles[index + 1]].x,
                    vertices[triangles[index + 2]].x);
                float max = Mathf.Max(
                    vertices[triangles[index]].x,
                    vertices[triangles[index + 1]].x,
                    vertices[triangles[index + 2]].x);
                maximum = Mathf.Max(maximum, max - min);
            }
            return maximum;
        }

        private static void AssertInterpolatedSegmentsStayLocal(
            SkinnedMeshRenderer renderer)
        {
            var baked = new Mesh { name = "R025_InterpolatedSegmentAudit" };
            bool wasEnabled = renderer.enabled;
            try
            {
                renderer.enabled = true;
                renderer.BakeMesh(baked);
                Bounds bakedBounds = BoundsFromVertices(baked.vertices);
                Assert.That(
                    MaximumTriangleSpanX(baked),
                    Is.LessThanOrEqualTo(0.0056f),
                    $"{renderer.name} has an interpolated bridge.");
                Assert.That(
                    bakedBounds.min.x,
                    Is.GreaterThanOrEqualTo(-0.12751f),
                    $"{renderer.name} leaves the Pack's left bound.");
                Assert.That(
                    bakedBounds.max.x,
                    Is.LessThanOrEqualTo(0.12751f),
                    $"{renderer.name} leaves the Pack's right bound.");
                int collapsedTriangles = 0;
                int activeTriangles = 0;
                int[] triangles = baked.triangles;
                foreach (int triangle in Enumerable.Range(
                    0,
                    triangles.Length / 3))
                {
                    Vector3 a = baked.vertices[triangles[triangle * 3]];
                    Vector3 b = baked.vertices[triangles[triangle * 3 + 1]];
                    Vector3 c = baked.vertices[triangles[triangle * 3 + 2]];
                    if (Vector3.Cross(b - a, c - a).sqrMagnitude
                        > 0.000000000001f)
                    {
                        activeTriangles++;
                        float minimum = Mathf.Min(a.x, b.x, c.x);
                        float maximum = Mathf.Max(a.x, b.x, c.x);
                        Assert.That(
                            maximum - minimum,
                            Is.LessThanOrEqualTo(0.0056f),
                            $"{renderer.name} has an active triangle bridge.");
                        continue;
                    }
                    collapsedTriangles++;
                    Vector3 anchor = (a + b + c) / 3f;
                    Assert.That(
                        anchor.x,
                        Is.InRange(-0.12751f, 0.12751f),
                        $"{renderer.name} collapsed triangle leaves the Pack.");
                }
                Assert.That(
                    activeTriangles + collapsedTriangles,
                    Is.GreaterThan(0),
                    $"{renderer.name} has no segment triangles.");
            }
            finally
            {
                renderer.enabled = wasEnabled;
                UnityEngine.Object.DestroyImmediate(baked);
            }
        }

        private static Bounds BoundsFromVertices(
            IReadOnlyList<Vector3> vertices)
        {
            Assert.That(vertices.Count, Is.GreaterThan(0));
            var bounds = new Bounds(vertices[0], Vector3.zero);
            for (int index = 1; index < vertices.Count; index++)
            {
                bounds.Encapsulate(vertices[index]);
            }
            return bounds;
        }

        private static int VerticesPerSegment(string rendererName)
        {
            return rendererName switch
            {
                "Pack_RearInnerFoil" => 8,
                "Pack_TopSealRemaining" => 4,
                "Pack_InnerFoilMouth" => 8,
                "Pack_InnerBackFoilRim" => 4,
                "Pack_RolledCrimpLip" => 16,
                "Pack_TornContourSweepCarrier" => 4,
                _ => throw new ArgumentOutOfRangeException(
                    nameof(rendererName),
                    rendererName,
                    "R025 does not define this segmented renderer.")
            };
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
