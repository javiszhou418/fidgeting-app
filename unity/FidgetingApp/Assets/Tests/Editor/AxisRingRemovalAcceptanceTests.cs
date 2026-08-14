using System;
using System.IO;
using System.Linq;
using FidgetingApp.Product;
using NUnit.Framework;

namespace FidgetingApp.Tests.Editor
{
    public sealed class AxisRingRemovalAcceptanceTests
    {
        [Test]
        public void RotorFlickInput_HasNoScreenSpaceTouchRingPath()
        {
            string source = File.ReadAllText(
                "Assets/_Fidgeting/Runtime/Interaction/RotorFlickInput.cs");

            StringAssert.DoesNotContain("OnGUI", source);
            StringAssert.DoesNotContain("GUI.DrawTexture", source);
            StringAssert.DoesNotContain("Touch Feedback Ring", source);
            StringAssert.DoesNotContain("showTouchFeedback", source);
            StringAssert.DoesNotContain("EnsureTouchRingTexture", source);
        }

        [Test]
        public void ProgressionAdapter_HasNoDynamicRingOrMeshConstructionPath()
        {
            string source = File.ReadAllText(
                "Assets/Scripts/Product/SpinnerProgressionVisuals.cs");

            StringAssert.Contains("SpinnerProgressionRules.Stages", source);
            StringAssert.Contains("CreatesRuntimeGeometry => false", source);
            StringAssert.DoesNotContain("new GameObject", source);
            StringAssert.DoesNotContain("Torus", source);
            StringAssert.DoesNotContain("MeshRenderer", source);
            StringAssert.DoesNotContain("MeshFilter", source);
            StringAssert.DoesNotContain("StageMaterialCollar", source);
            StringAssert.DoesNotContain("PrecisionSteelWeightRing", source);
            StringAssert.DoesNotContain("\"AuxiliaryBearing", source);
            StringAssert.DoesNotContain("TitaniumBearingCage", source);
            StringAssert.DoesNotContain("MirrorSteelCrown", source);
        }

        [Test]
        public void SixProductShippingRuntime_HasNoDynamicTorusOrTouchRingSource()
        {
            string[] shippingModels = ProductCatalog.ShippingModelIds();
            Assert.That(shippingModels, Has.Length.EqualTo(6));
            Assert.That(shippingModels.Distinct().Count(), Is.EqualTo(6));

            string[] runtimeSources = Directory.GetFiles(
                    "Assets",
                    "*.cs",
                    SearchOption.AllDirectories)
                .Where(path => path.Contains("/Runtime/", StringComparison.Ordinal)
                    || path.Contains("/Scripts/", StringComparison.Ordinal))
                .Where(path => !path.Contains("/Tests/", StringComparison.Ordinal)
                    && !path.Contains("/Editor/", StringComparison.Ordinal))
                .ToArray();

            foreach (string path in runtimeSources)
            {
                string source = File.ReadAllText(path);
                StringAssert.DoesNotContain("CreateTorus", source, path);
                StringAssert.DoesNotContain("BuildTorusMesh", source, path);
                StringAssert.DoesNotContain("Touch Feedback Ring", source, path);
            }
        }
    }
}
