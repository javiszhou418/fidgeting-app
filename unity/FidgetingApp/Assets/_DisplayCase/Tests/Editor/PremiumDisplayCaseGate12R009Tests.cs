using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using FidgetingApp.DisplayCase.Editor;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace FidgetingApp.DisplayCase.Tests
{
    /// <summary>
    /// Gate 12 R009 (tri-spinner-slab-v3-cmf shipping candidate). Approval of
    /// the preview is the user's; these tests prove the candidate is wired
    /// like the shipping contract and that nothing shipping changed.
    /// </summary>
    public sealed class PremiumDisplayCaseGate12R009Tests
    {
        private const string R004Prefab = "Assets/Resources/Gacha/PremiumDisplayCaseGate12R004/PresentationRoot.prefab";

        [Test]
        public void CandidatePrefabWrapsTheApprovedGate11Export()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PremiumDisplayCaseGate12R009Builder.PrefabPath);
            Assert.That(prefab, Is.Not.Null, "build the R009 candidate first");
            Assert.That(prefab.name, Is.EqualTo(PremiumDisplayCaseGate12R009Builder.RootName));
            Assert.That(prefab.transform.localPosition, Is.EqualTo(Vector3.zero));
            Assert.That(Quaternion.Angle(prefab.transform.localRotation, Quaternion.identity), Is.LessThan(0.01f));
            Assert.That(prefab.transform.localScale, Is.EqualTo(Vector3.one));

            var presentation = prefab.GetComponent<PremiumDisplayCaseShippingPresentation>();
            Assert.That(presentation, Is.Not.Null);
            Assert.That(presentation.CaseAssembly.name, Is.EqualTo(PremiumDisplayCaseGate12R009Builder.CaseAssemblyName));
            Assert.That(presentation.ContentSlot.name, Is.EqualTo(PremiumDisplayCaseGate12R009Builder.ContentSlotName));
            Transform orient = presentation.ContentSlot.Find(PremiumDisplayCaseGate12R009Builder.ContentOrientName);
            Assert.That(orient, Is.Not.Null);
            Assert.That(Quaternion.Angle(orient.localRotation, Quaternion.Euler(PremiumDisplayCaseGate12R009Builder.ContentOrientEuler)), Is.LessThan(0.01f));
            Assert.That(orient.Find(PremiumDisplayCaseGate12R009Builder.ContentFitName), Is.Not.Null);
            Assert.That(presentation.RevealProfile, Is.Not.Null);

            Transform[] nodes = prefab.GetComponentsInChildren<Transform>(true);
            int caseMeshes = presentation.CaseAssembly.GetComponentsInChildren<MeshFilter>(false)
                .Count(f => f.sharedMesh != null && f.name.StartsWith("GEO_PDC_", StringComparison.Ordinal));
            Assert.That(caseMeshes, Is.EqualTo(PremiumDisplayCaseGate12R009Builder.ExpectedCaseMeshCount));
            Transform decal = nodes.FirstOrDefault(t => t.name == PremiumDisplayCaseGate12R009Builder.PlaceholderDecalName);
            Assert.That(decal == null || !decal.gameObject.activeSelf, "placeholder decal copy must not ship");
            Assert.That(nodes.Any(t => t.name.IndexOf("explode", StringComparison.OrdinalIgnoreCase) >= 0), Is.False);
            Assert.That(Sha256(TriSpinnerSlabGate11ParityBuilder.ModelPath),
                Is.EqualTo(TriSpinnerSlabGate11ParityBuilder.ApprovedFbxSha256));
        }

        [Test]
        public void ContentFitIsThePocketWellAndLegacyPrefabsKeepTheR004Fit()
        {
            var candidate = AssetDatabase.LoadAssetAtPath<GameObject>(PremiumDisplayCaseGate12R009Builder.PrefabPath)
                .GetComponent<PremiumDisplayCaseShippingPresentation>();
            Assert.That(candidate.ContentFitAvailableSize, Is.EqualTo(PremiumDisplayCaseGate12R009Builder.ContentFitAvailableSize));
            Assert.That(candidate.ContentFitDepthOffsetMeters, Is.EqualTo(PremiumDisplayCaseGate12R009Builder.ContentFitDepthOffsetMeters));
            Assert.That(candidate.ContentFitAvailableSize.x, Is.LessThan(PremiumDisplayCaseGate12R009Builder.PocketWellDiameterMeters));

            var legacy = AssetDatabase.LoadAssetAtPath<GameObject>(R004Prefab).GetComponent<PremiumDisplayCaseShippingPresentation>();
            Assert.That(legacy.ContentFitAvailableSize, Is.EqualTo(new Vector3(0.165f, 0.182f, 0.040f)));
            Assert.That(legacy.ContentFitDepthOffsetMeters, Is.EqualTo(0.015f));
        }

        [Test]
        public void AttachedPrizeSitsInsideThePocketWellWithZeroAngularVelocity()
        {
            GameObject root = null;
            GameObject prize = null;
            try
            {
                root = (GameObject)PrefabUtility.InstantiatePrefab(
                    AssetDatabase.LoadAssetAtPath<GameObject>(PremiumDisplayCaseGate12R009Builder.PrefabPath));
                var presentation = root.GetComponent<PremiumDisplayCaseShippingPresentation>();
                prize = ThreeBladeDisplayPrizeFactory.Instantiate();
                presentation.AttachContent(prize.transform, PremiumDisplayCaseShippingFactory.ThreeBladeContentEuler);

                Renderer[] renderers = prize.GetComponentsInChildren<Renderer>(true).Where(r => r.enabled).ToArray();
                Bounds bounds = renderers[0].bounds;
                foreach (Renderer renderer in renderers.Skip(1))
                {
                    bounds.Encapsulate(renderer.bounds);
                }
                Vector3 slot = presentation.ContentSlot.position;
                Assert.That(Mathf.Max(bounds.size.x, bounds.size.y),
                    Is.LessThanOrEqualTo(PremiumDisplayCaseGate12R009Builder.PocketWellDiameterMeters));
                Assert.That(Mathf.Abs(bounds.center.x - slot.x), Is.LessThan(0.0005f));
                Assert.That(Mathf.Abs(bounds.center.y - slot.y), Is.LessThan(0.0005f));
                // Faces the front: the spinner disc spans XY, its thickness is the design 14.5 mm along Z.
                Assert.That(bounds.size.z, Is.LessThanOrEqualTo(PremiumDisplayCaseGate12R009Builder.ContentFitAvailableSize.z + 0.0001f));
                Assert.That(Mathf.Min(bounds.size.x, bounds.size.y), Is.GreaterThan(0.045f));
                Assert.That(presentation.ContentFitHoldsOnlyAttachedContent, Is.True);
                Assert.That(presentation.ToyAngularVelocityIsZero, Is.True);
                Assert.That(prize.transform.IsChildOf(presentation.ContentSlot), Is.True);
            }
            finally
            {
                if (prize != null) UnityEngine.Object.DestroyImmediate(prize);
                if (root != null) UnityEngine.Object.DestroyImmediate(root);
            }
        }

        [Test]
        public void SetLabelDrivesTheHeaderTextInsideThePlate()
        {
            GameObject root = null;
            try
            {
                root = (GameObject)PrefabUtility.InstantiatePrefab(
                    AssetDatabase.LoadAssetAtPath<GameObject>(PremiumDisplayCaseGate12R009Builder.PrefabPath));
                var presentation = root.GetComponent<PremiumDisplayCaseShippingPresentation>();
                PremiumDisplayCaseLabelData data = PremiumDisplayCaseGate12R005Builder.BuildAuthoritativeReviewLabel();
                presentation.SetLabel(data);
                Assert.That(presentation.HasAuthoritativeLabel, Is.True);

                Transform labelRoot = root.transform.Find(PremiumDisplayCaseGate12R009Builder.HeaderLabelRootName);
                Assert.That(labelRoot, Is.Not.Null);
                TextMesh Text(string name) => labelRoot.Find(name).GetComponent<TextMesh>();
                Assert.That(Text("LABEL_PRODUCT_NAME").text, Is.EqualTo(data.ProductName));
                Assert.That(Text("LABEL_EDITION_FINISH").text, Is.EqualTo(data.EditionFinish));
                Assert.That(Text("LABEL_ACQUIRED_DATE").text, Is.EqualTo("ACQUIRED " + data.AcquiredDate));
                Assert.That(Text("LABEL_RARITY").text, Is.EqualTo(data.RarityLevel));
                Assert.That(Text("LABEL_COLLECTIBLE_ID").text, Is.Empty, "collectible id stays off the plate (R053)");

                Bounds plate = root.GetComponentsInChildren<Renderer>(true)
                    .Single(r => r.name == PremiumDisplayCaseGate12R009Builder.HeaderPlaneName).bounds;
                foreach (TextMesh text in labelRoot.GetComponentsInChildren<TextMesh>(true))
                {
                    // Depth-tested font material: the label must not print through the rear plate.
                    Renderer textRenderer = text.GetComponent<Renderer>();
                    Assert.That(textRenderer.sharedMaterial.shader.name,
                        Is.EqualTo(PremiumDisplayCaseGate12R009Builder.LabelTextShaderName), text.name + " shader");
                    Assert.That(text.GetComponent<PremiumDisplayCaseLabelTextMaterial>(), Is.Not.Null, text.name + " atlas binder");
                    if (string.IsNullOrEmpty(text.text)) continue;
                    Bounds glyphs = text.GetComponent<Renderer>().bounds;
                    Assert.That(glyphs.min.x, Is.GreaterThanOrEqualTo(plate.min.x - 0.0002f), text.name + " left");
                    Assert.That(glyphs.max.x, Is.LessThanOrEqualTo(plate.max.x + 0.0002f), text.name + " right");
                    Assert.That(glyphs.min.y, Is.GreaterThanOrEqualTo(plate.min.y - 0.0002f), text.name + " bottom");
                    Assert.That(glyphs.max.y, Is.LessThanOrEqualTo(plate.max.y + 0.0002f), text.name + " top");
                    Assert.That(glyphs.center.z, Is.LessThan(plate.min.z), text.name + " must sit in front of the plate");
                }
            }
            finally
            {
                if (root != null) UnityEngine.Object.DestroyImmediate(root);
            }
        }

        [Test]
        public void BeautyVolumeStaysInsideTheContractRanges()
        {
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(PremiumDisplayCaseGate12R009Builder.VolumeProfilePath);
            Assert.That(profile, Is.Not.Null);
            Assert.That(profile.TryGet(out Bloom bloom), Is.True);
            Assert.That(bloom.threshold.value, Is.InRange(1.1f, 1.4f));
            Assert.That(bloom.intensity.value, Is.InRange(0.05f, 0.12f));
            Assert.That(bloom.scatter.value, Is.InRange(0.45f, 0.55f));
            Assert.That(bloom.clamp.value, Is.InRange(8f, 12f));
            Assert.That(bloom.dirtIntensity.value, Is.EqualTo(0f));
            Assert.That(profile.TryGet(out Tonemapping tonemapping) && tonemapping.active, Is.True);
            Assert.That(profile.TryGet(out Vignette vignette), Is.True);
            Assert.That(vignette.intensity.value, Is.InRange(0.08f, 0.12f));
            Assert.That(vignette.smoothness.value, Is.InRange(0.25f, 0.35f));
            Assert.That(profile.Has<ChromaticAberration>(), Is.False);
            Assert.That(profile.Has<FilmGrain>(), Is.False);
        }

        [Test]
        public void ShippingFactoryStillPointsAtR004UntilTheUserApprovesThePreview()
        {
            Assert.That(PremiumDisplayCaseShippingFactory.ResourcesPath,
                Is.EqualTo("Gacha/PremiumDisplayCaseGate12R004/PresentationRoot"));
            Assert.That(Resources.Load<GameObject>(PremiumDisplayCaseGate12R009Builder.ResourcesPath), Is.Not.Null,
                "candidate must be loadable from Resources so the flip is a one-line change after approval");
            Assert.DoesNotThrow(TriSpinnerSlabGate11ParityBuilder.AssertSourceAndShippingHashes,
                "shipping prefab / scene / FBX must be byte-identical to the Gate 11 baseline");
        }

        [Test]
        public void ReportRecordedPassWithinTheLightBudget()
        {
            string path = Path.Combine(PremiumDisplayCaseGate12R009Builder.EvidenceRoot, "gate12-r009-report.json");
            Assert.That(File.Exists(path), Is.True, path);
            var report = JsonUtility.FromJson<PremiumDisplayCaseGate12R009Builder.Report>(File.ReadAllText(path));
            Assert.That(report.status, Is.EqualTo("pass"));
            Assert.That(report.failures, Is.Empty);
            Assert.That(report.prizeInsidePocketWell, Is.True);
            Assert.That(report.additionalRealtimeLights, Is.LessThanOrEqualTo(3));
            Assert.That(report.mainDirectionalLights, Is.EqualTo(1));
            Assert.That(report.caseMeshCount, Is.EqualTo(PremiumDisplayCaseGate12R009Builder.ExpectedCaseMeshCount));
            Assert.That(report.shippingFactoryResourcesPath, Is.EqualTo("Gacha/PremiumDisplayCaseGate12R004/PresentationRoot"));
            Assert.That(report.turntableFrames, Is.EqualTo(PremiumDisplayCaseGate12R009Builder.TurntableFrames));
        }

        private static string Sha256(string assetPath)
        {
            using (SHA256 sha = SHA256.Create())
            using (FileStream stream = File.OpenRead(TriSpinnerSlabGate11ParityBuilder.AssetAbsolutePath(assetPath)))
            {
                return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", string.Empty).ToLowerInvariant();
            }
        }
    }
}
