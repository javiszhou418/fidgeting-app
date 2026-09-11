using System.Linq;
using FidgetingApp.DisplayCase.Candidates;
using FidgetingApp.DisplayCase.IsolatedCandidate;
using FidgetingApp.DisplayCase.IsolatedCandidate.Editor;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.Tests
{
    public sealed class IsolatedR014ProofTests
    {
        [Test]
        public void ProfileLocksShortProofAndSevenAuthoredPoses()
        {
            Assert.That(PackOpeningGate04R014Profile.TotalSeconds, Is.EqualTo(1.60f));
            Assert.That(PackOpeningGate04R014Profile.AuthoredPoseProgresses.Length, Is.EqualTo(7));
            Assert.That(IsolatedR014ProofSequence.TopSealHeightFraction,
                Is.InRange(0.06f, 0.10f));
        }

        [Test]
        public void ImportedRigHasTenMeshesAndSixBlendShapes()
        {
            GameObject rig = AssetDatabase.LoadAssetAtPath<GameObject>(
                "Assets/Source/R014/PackOpeningGate04R014PackOnlyRig.fbx");
            Assert.That(rig, Is.Not.Null);
            SkinnedMeshRenderer[] renderers =
                rig.GetComponentsInChildren<SkinnedMeshRenderer>(true);
            Assert.That(renderers.Length, Is.EqualTo(10));
            Assert.That(renderers.All(item => item.sharedMesh.blendShapeCount == 6),
                Is.True);
        }

        [Test]
        public void SingleLiveCaseStaysContainedBeforeRiseAndRespectsEffectsOff()
        {
            IsolatedR014ProofSequence sequence =
                IsolatedR014ProofBuilder.BuildSequenceForTests();
            sequence.SetTime(0.84f, false);
            Assert.That(sequence.CurrentSample.Occlusion,
                Is.EqualTo(PackOpeningGate04R014Occlusion.CaseContained));
            Assert.That(sequence.IsCaseContainedInMouth(), Is.True);
            EntityId entityId = sequence.CaseEntityId;
            sequence.SetTime(1.36f, false);
            Assert.That(sequence.CaseEntityId, Is.EqualTo(entityId));
            Assert.That(sequence.CurrentSample.Occlusion,
                Is.EqualTo(PackOpeningGate04R014Occlusion.PackRetreating));
        }
    }
}
