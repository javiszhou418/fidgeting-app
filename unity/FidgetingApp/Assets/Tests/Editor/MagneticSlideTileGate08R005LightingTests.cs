using System.IO;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class MagneticSlideTileGate08R005LightingTests
    {
        private const string Root =
            "Assets/_EDC/Candidates/MagneticSlideTileGate08R005EndpointLighting";

        [Test]
        public void IsolatedPreviewImportsCurrentExteriorFbx()
        {
            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(
                Root + "/Models/magnetic-slide-tile-lighting-r005-unity-preview.fbx");
            Assert.That(model, Is.Not.Null);
            Assert.That(model.GetComponentsInChildren<MeshRenderer>(true), Has.Length.EqualTo(2));
        }

        [Test]
        public void SharedHdrUsesHalfFloatImportAndOneReflectionSource()
        {
            string report = ReadEvidence("neutral-parity-unity-report.json");
            StringAssert.Contains("\"sourceTextureFormat\": \"R16G16B16A16_SFloat\"", report);
            StringAssert.Contains("\"reflectionSourceCount\": 1", report);
            StringAssert.Contains("\"directLightCount\": 0", report);
            StringAssert.Contains("\"groundCount\": 0", report);
            StringAssert.Contains("\"displayTransform\": \"shared post-render neutral-display-v1\"", report);
        }

        [Test]
        public void ShippingSceneRemainsByteIdentical()
        {
            string report = ReadEvidence("neutral-parity-unity-report.json");
            StringAssert.Contains(
                "\"shippingSceneHashBefore\": \"99083a32fbad262f615707d0904bf68f7989e8e351579f8691066bd4bc97850d\"",
                report);
            StringAssert.Contains(
                "\"shippingSceneHashAfter\": \"99083a32fbad262f615707d0904bf68f7989e8e351579f8691066bd4bc97850d\"",
                report);
            StringAssert.Contains("\"shippingSceneModified\": false", report);
            StringAssert.Contains("\"buildInstallPhone\": false", report);
        }

        [Test]
        public void CurrentMaterialAndContractHashesPassAudit()
        {
            string audit = ReadEvidence("lighting-parity-audit.json");
            StringAssert.Contains(
                "\"materialBlend\": \"953929045453e1d9c3bb46612da85a70eb1a078a115a103040778d2703988588\"",
                audit);
            StringAssert.Contains(
                "\"contract\": \"9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571\"",
                audit);
            StringAssert.Contains(
                "\"geometryDigest\": \"2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952\"",
                audit);
            StringAssert.Contains("\"pass\": true", audit);
        }

        [Test]
        public void EndpointTurntableContainsNoIllegalMotion()
        {
            string report = ReadEvidence("legal-lighting-turntable-report.json");
            StringAssert.Contains("\"rotationOnlyAtEndpoint\": true", report);
            StringAssert.Contains("\"slideReturnOnlyAligned\": true", report);
            StringAssert.Contains("\"full360Covered\": true", report);
            StringAssert.Contains("\"fixedAxisInvariant\": true", report);
            StringAssert.Contains("\"noPitchRollFlip\": true", report);
        }

        private static string ReadEvidence(string filename)
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string path = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-005",
                filename);
            Assert.That(File.Exists(path), Is.True, path);
            return File.ReadAllText(path);
        }
    }
}
