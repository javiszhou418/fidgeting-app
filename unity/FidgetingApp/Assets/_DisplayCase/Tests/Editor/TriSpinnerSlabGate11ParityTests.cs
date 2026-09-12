using System.Collections.Generic;
using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase.Editor;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Tests
{
    /// <summary>
    /// Gate 11 rev-004 regression rules for the tri-spinner-slab-v3-cmf candidate.
    /// The candidate must stay byte-identical to the approved export, keep the
    /// Blender hierarchy/pivots/bounds, use one URP material per cmf zone, and
    /// leave the shipping display case untouched.
    /// </summary>
    public sealed class TriSpinnerSlabGate11ParityTests
    {
        private const float PivotToleranceMeters = 0.00005f;

        [Test]
        public void ApprovedExportAndDecalAreByteIdentical()
        {
            Assert.AreEqual(
                TriSpinnerSlabGate11ParityBuilder.ApprovedFbxSha256,
                TriSpinnerSlabGate11ParityBuilder.Sha256File(
                    TriSpinnerSlabGate11ParityBuilder.AssetAbsolutePath(TriSpinnerSlabGate11ParityBuilder.ModelPath)));
            Assert.AreEqual(
                TriSpinnerSlabGate11ParityBuilder.ApprovedDecalSha256,
                TriSpinnerSlabGate11ParityBuilder.Sha256File(
                    TriSpinnerSlabGate11ParityBuilder.AssetAbsolutePath(TriSpinnerSlabGate11ParityBuilder.DecalPath)));
        }

        [Test]
        public void Gate11SourceAssetsStayUntouchedAfterR010Promotion()
        {
            Assert.DoesNotThrow(TriSpinnerSlabGate11ParityBuilder.AssertSourceAndShippingHashes);
            Assert.AreEqual(
                PremiumDisplayCaseGate12R010ReviewBuilder.ResourcesPath,
                PremiumDisplayCaseShippingFactory.ResourcesPath,
                "The user approved R010 and authorized the phone delivery on 2026-09-12.");
        }

        [Test]
        public void ImportedModelHasIdentityTransformsAndBlenderPivots()
        {
            GameObject prefab = LoadPrefab();
            TriSpinnerSlabGate11ParityBuilder.ParityReference reference = TriSpinnerSlabGate11ParityBuilder.LoadReference();
            Dictionary<string, TriSpinnerSlabGate11ParityBuilder.ReferenceObject> byName =
                reference.objects.ToDictionary(item => item.name);

            Assert.AreEqual(TriSpinnerSlabGate11ParityBuilder.RootName, prefab.name);
            Assert.AreEqual(Quaternion.identity, prefab.transform.localRotation);
            Assert.AreEqual(Vector3.one, prefab.transform.localScale);

            foreach (Transform item in prefab.GetComponentsInChildren<Transform>(true))
            {
                Assert.IsTrue(item.localScale.x > 0f && item.localScale.y > 0f && item.localScale.z > 0f, $"{item.name} negative scale");
                if (item == prefab.transform || item.name == TriSpinnerSlabGate11ParityBuilder.DecalName)
                {
                    continue;
                }
                Assert.IsTrue(byName.ContainsKey(item.name), $"{item.name} is not part of the approved export");
                TriSpinnerSlabGate11ParityBuilder.ReferenceObject expected = byName[item.name];
                string expectedParent = expected.parent == "ROOT_PDC_PRESENTATION"
                    ? TriSpinnerSlabGate11ParityBuilder.RootName
                    : expected.parent;
                Assert.AreEqual(expectedParent, item.parent.name, $"{item.name} parent");
                Assert.AreEqual(Quaternion.identity, item.localRotation, $"{item.name} rotation");
                if (expected.type == "EMPTY")
                {
                    Vector3 expectedPosition = new Vector3(
                        expected.unityLocalPosition[0],
                        expected.unityLocalPosition[1],
                        expected.unityLocalPosition[2]);
                    Assert.Less((item.position - expectedPosition).magnitude, PivotToleranceMeters, $"{item.name} pivot");
                }
            }
            Assert.IsNotNull(
                prefab.GetComponentsInChildren<Transform>(true).FirstOrDefault(item => item.name == TriSpinnerSlabGate11ParityBuilder.ContentSlotName),
                "content slot pivot must survive import for the caller-owned toy");
        }

        [Test]
        public void EveryCaseMeshUsesItsZoneMaterialWithinTheSlotBudget()
        {
            GameObject prefab = LoadPrefab();
            TriSpinnerSlabGate11ParityBuilder.ParityReference reference = TriSpinnerSlabGate11ParityBuilder.LoadReference();
            Dictionary<string, TriSpinnerSlabGate11ParityBuilder.ReferenceObject> byName =
                reference.objects.ToDictionary(item => item.name);
            Dictionary<int, string> zoneMaterialNames =
                TriSpinnerSlabGate11ParityBuilder.ZoneSpecs.ToDictionary(spec => spec.Zone, spec => spec.Name);

            MeshRenderer[] renderers = prefab.GetComponentsInChildren<MeshRenderer>(true);
            MeshRenderer[] caseRenderers = renderers.Where(item => item.name != TriSpinnerSlabGate11ParityBuilder.DecalName).ToArray();
            Assert.AreEqual(TriSpinnerSlabGate11ParityBuilder.ExpectedMeshCount, caseRenderers.Length);

            int triangles = 0;
            HashSet<Material> slots = new HashSet<Material>();
            foreach (MeshRenderer renderer in caseRenderers)
            {
                int zone = byName[renderer.name].cmfZoneId;
                Assert.IsNotNull(renderer.sharedMaterial, $"{renderer.name} has no material");
                Assert.AreEqual(zoneMaterialNames[zone], renderer.sharedMaterial.name, $"{renderer.name} zone {zone}");
                Assert.AreEqual("Universal Render Pipeline/Lit", renderer.sharedMaterial.shader.name);
                slots.Add(renderer.sharedMaterial);
                triangles += renderer.GetComponent<MeshFilter>().sharedMesh.triangles.Length / 3;
            }
            Assert.AreEqual(TriSpinnerSlabGate11ParityBuilder.ExpectedTriangles, triangles);
            Assert.LessOrEqual(slots.Count, TriSpinnerSlabGate11ParityBuilder.CaseMaterialSlotBudget);

            MeshRenderer decal = renderers.Single(item => item.name == TriSpinnerSlabGate11ParityBuilder.DecalName);
            Assert.AreEqual(TriSpinnerSlabGate11ParityBuilder.HeaderPlaneName, decal.transform.parent.name);
            Assert.IsNotNull(decal.sharedMaterial.GetTexture("_BaseMap"), "header label decal must carry the approved PNG");
            Assert.AreEqual(1f, decal.sharedMaterial.GetFloat("_Surface"), "decal must be transparent");
        }

        [Test]
        public void TransparentZonesRenderAfterOpaqueCaseAndBeforeCrystal()
        {
            GameObject prefab = LoadPrefab();
            Material crystal = MaterialFor(prefab, "GEO_PDC_OUTER_CRYSTAL_FRAME");
            Material liner = MaterialFor(prefab, "GEO_PDC_SMOKE_INNER_LINER");
            Material field = MaterialFor(prefab, "GEO_PDC_MAIN_MICROBLAST_FIELD");
            Assert.AreEqual(3000, crystal.renderQueue);
            Assert.AreEqual(2990, liner.renderQueue);
            Assert.LessOrEqual(field.renderQueue, 2000);
            Assert.AreEqual(0f, crystal.GetFloat("_ZWrite"));
            Assert.IsTrue(crystal.IsKeywordEnabled("_SURFACE_TYPE_TRANSPARENT"));
            Assert.IsTrue(crystal.IsKeywordEnabled("_ALPHAPREMULTIPLY_ON"), "clear crystal keeps specular at low alpha");
            Assert.IsFalse(field.IsKeywordEnabled("_SURFACE_TYPE_TRANSPARENT"));
            Assert.AreEqual(Color.black, crystal.GetColor("_EmissionColor"), "emissive case pixels are forbidden");
        }

        [Test]
        public void PrefabBoundsMatchTheExportManifest()
        {
            GameObject prefab = LoadPrefab();
            Bounds union = new Bounds();
            bool first = true;
            foreach (MeshRenderer renderer in prefab.GetComponentsInChildren<MeshRenderer>(true))
            {
                if (renderer.name == TriSpinnerSlabGate11ParityBuilder.DecalName)
                {
                    continue;
                }
                if (first)
                {
                    union = renderer.bounds;
                    first = false;
                }
                else
                {
                    union.Encapsulate(renderer.bounds);
                }
            }
            Vector3 expected = TriSpinnerSlabGate11ParityBuilder.ExpectedCaseSize;
            Assert.Less(Mathf.Abs(union.size.x / expected.x - 1f) * 100f, TriSpinnerSlabGate11ParityBuilder.BoundsTolerancePercent);
            Assert.Less(Mathf.Abs(union.size.y / expected.y - 1f) * 100f, TriSpinnerSlabGate11ParityBuilder.BoundsTolerancePercent);
            Assert.Less(Mathf.Abs(union.size.z / expected.z - 1f) * 100f, TriSpinnerSlabGate11ParityBuilder.BoundsTolerancePercent);
            Assert.Less(union.min.z, 0f, "front (crystal) must face -Z");
            Assert.Greater(union.max.z, 0.008f, "rear plate must sit at +Z");
        }

        [Test]
        public void ParityReportsRecordedPass()
        {
            string root = TriSpinnerSlabGate11ParityBuilder.EvidenceRoot;
            foreach (string file in new[]
                     {
                         "unity-hierarchy-pivot-material-report.json",
                         "unity-bounds-digest-validation.json",
                         "unity-capture-report.json"
                     })
            {
                string path = Path.Combine(root, file);
                Assert.IsTrue(File.Exists(path), path);
                StringAssert.Contains("\"status\": \"pass\"", File.ReadAllText(path), file);
            }
            foreach (string capture in new[]
                     {
                         "unity-shipping-hero.png",
                         "unity-shipping-front.png",
                         "unity-shipping-low-oblique.png",
                         "unity-neutral-hero.png",
                         "unity-silhouette-front.png"
                     })
            {
                Assert.IsTrue(File.Exists(Path.Combine(root, capture)), capture);
            }
        }

        private static GameObject LoadPrefab()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(TriSpinnerSlabGate11ParityBuilder.PrefabPath);
            Assert.IsNotNull(prefab, $"Missing candidate prefab {TriSpinnerSlabGate11ParityBuilder.PrefabPath}");
            return prefab;
        }

        private static Material MaterialFor(GameObject prefab, string name)
        {
            MeshRenderer renderer = prefab.GetComponentsInChildren<MeshRenderer>(true).Single(item => item.name == name);
            return renderer.sharedMaterial;
        }
    }
}
