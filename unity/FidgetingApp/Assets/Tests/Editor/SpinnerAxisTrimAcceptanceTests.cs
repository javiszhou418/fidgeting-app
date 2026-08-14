using System;
using System.Linq;
using NUnit.Framework;
using ThreeBladeEDC.Interaction;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.Tests.Editor
{
    public sealed class SpinnerAxisTrimAcceptanceTests
    {
        private static readonly string[] ForbiddenDecorativeAxisRings =
        {
            "RotorCoreTopTrim",
            "RotorCrownTrim",
            "FingerCapTop_PolishedBezel",
            "FingerCapBottom_PolishedBezel",
            "FingerCapTop_ShadowGap",
            "FingerCapBottom_ShadowGap",
            "FingerCapTop_AccentLine",
            "FingerCapBottom_AccentLine",
            "UndercutShadowGap",
            "BearingOuterRace",
            "BearingInnerRace",
            "TopWasher",
            "BottomWasher",
            "BearingShield_Top",
            "BearingShield_Bottom",
            "BearingBalls"
        };

        [TestCase(
            "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity",
            "ThreeBladeEDC_Root",
            "TopCap",
            "Axle")]
        [TestCase(
            "Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity",
            "ThreeBladeEDC_Root",
            "TopCap",
            "Axle")]
        [TestCase(
            "Assets/_TwoLobeBar/Scenes/TwoLobeBar.unity",
            "TwoLobeBar_Root",
            "TopButton",
            "Axle")]
        public void ShippingRotorKeepsMechanicalAxisButHasNoDecorativeRing(
            string scenePath,
            string rootName,
            string capName,
            string mechanicalAxisName)
        {
            SceneSetup[] previousSetup = EditorSceneManager.GetSceneManagerSetup();
            try
            {
                Scene scene = EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
                Transform root = scene.GetRootGameObjects()
                    .Single(candidate => candidate.name == rootName)
                    .transform;
                Transform[] transforms = root.GetComponentsInChildren<Transform>(true);

                foreach (string rejectedName in ForbiddenDecorativeAxisRings)
                {
                    foreach (Transform rejected in transforms.Where(
                        transform => transform.name == rejectedName))
                    {
                        Assert.That(
                            rejected.GetComponentsInChildren<Renderer>(true),
                            Is.Empty,
                            $"{scenePath} must not render decorative ring {rejectedName}.");
                        Assert.That(
                            rejected.GetComponentsInChildren<MeshFilter>(true),
                            Is.Empty,
                            $"{scenePath} must not retain hidden decorative mesh {rejectedName}.");
                    }
                }

                Transform cap = transforms.FirstOrDefault(
                    transform => transform.name == capName
                        && transform.GetComponent<Renderer>()?.enabled == true);
                Transform mechanicalAxis = transforms.FirstOrDefault(
                    transform => transform.name == mechanicalAxisName);
                Assert.That(cap, Is.Not.Null, $"{scenePath} lost its real finger cap.");
                Assert.That(
                    cap.GetComponent<Renderer>(),
                    Is.Not.Null,
                    $"{scenePath} finger cap must remain visible and touch-legible.");
                Assert.That(mechanicalAxis, Is.Not.Null, $"{scenePath} lost its mechanical axle.");
                if (scenePath != "Assets/_TwoLobeBar/Scenes/TwoLobeBar.unity")
                {
                    Assert.That(
                        mechanicalAxis.GetComponentsInChildren<Renderer>(true),
                        Is.Empty,
                        $"{scenePath} mechanical axis transform must not add a second visible circle.");
                    Assert.That(
                        mechanicalAxis.GetComponentsInChildren<MeshFilter>(true),
                        Is.Empty,
                        $"{scenePath} mechanical axis must not retain render mesh geometry.");
                }

                Renderer[] productRenderers = root
                    .GetComponentsInChildren<Renderer>(true)
                    .Where(renderer => renderer.enabled
                        && renderer.gameObject.activeInHierarchy
                        && !HasAncestorNamed(renderer.transform, "Studio"))
                    .ToArray();
                float minX = productRenderers.Min(renderer => renderer.bounds.min.x);
                float maxX = productRenderers.Max(renderer => renderer.bounds.max.x);
                float minZ = productRenderers.Min(renderer => renderer.bounds.min.z);
                float maxZ = productRenderers.Max(renderer => renderer.bounds.max.z);
                float productSpan = Mathf.Max(maxX - minX, maxZ - minZ);
                float capSpan = Mathf.Max(
                    cap.GetComponent<Renderer>().bounds.size.x,
                    cap.GetComponent<Renderer>().bounds.size.z);
                Assert.That(
                    capSpan / productSpan,
                    Is.LessThanOrEqualTo(0.22f),
                    $"{scenePath} visual cap must not dominate the assembled product.");

                RotorRigidbodyController rotor = root
                    .GetComponentInChildren<RotorRigidbodyController>(true);
                Rigidbody rotorBody = rotor.GetComponent<Rigidbody>();
                Rigidbody hubBody = transforms
                    .First(transform => transform.name == "HubStatic")
                    .GetComponent<Rigidbody>();
                Assert.That(rotorBody, Is.Not.Null);
                Assert.That(rotorBody.isKinematic, Is.False);
                Assert.That(hubBody, Is.Not.Null);
                Assert.That(hubBody.isKinematic, Is.True);
                Assert.That(rotorBody, Is.Not.SameAs(hubBody));
            }
            finally
            {
                if (previousSetup != null && previousSetup.Any(setup => setup.isLoaded))
                {
                    EditorSceneManager.RestoreSceneManagerSetup(previousSetup);
                }
                else
                {
                    EditorSceneManager.NewScene(
                        NewSceneSetup.EmptyScene,
                        NewSceneMode.Single);
                }
            }
        }

        [Test]
        public void MirrorQuadKeepsTouchableMechanicalRotorWithoutSeparateAxisRingRenderer()
        {
            const string scenePath = "Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity";
            SceneSetup[] previousSetup = EditorSceneManager.GetSceneManagerSetup();
            try
            {
                Scene scene = EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
                Transform root = scene.GetRootGameObjects()
                    .Single(candidate => candidate.name == "ImportedSpinner_Root")
                    .transform;
                Transform[] transforms = root.GetComponentsInChildren<Transform>(true);
                foreach (string rejectedName in ForbiddenDecorativeAxisRings)
                {
                    foreach (Transform rejected in transforms.Where(
                        transform => transform.name == rejectedName))
                    {
                        Assert.That(rejected.GetComponentsInChildren<Renderer>(true), Is.Empty);
                        Assert.That(rejected.GetComponentsInChildren<MeshFilter>(true), Is.Empty);
                    }
                }

                Transform mirrorQuad = transforms.Single(
                    transform => transform.name == "MirrorQuadVisual");
                MeshFilter[] mirrorMeshes =
                    mirrorQuad.GetComponentsInChildren<MeshFilter>(true);
                Assert.That(mirrorMeshes, Is.Not.Empty);
                Assert.That(
                    mirrorMeshes.All(filter =>
                        UnityEditor.AssetDatabase.GetAssetPath(filter.sharedMesh)
                            == "Assets/_ImportedSpinner/Models/ImportedSpinner_Runtime.obj"),
                    Is.True,
                    "Mirror Quad must use the restored true four-wing source mesh.");
                Assert.That(
                    string.Join("\n", UnityEditor.AssetDatabase.GetDependencies(
                        scenePath,
                        true)),
                    Does.Not.Contain("RingNeutral"),
                    "Rejected wide-ring DCC v1-v10 assets must stay excluded.");

                RotorRigidbodyController rotor = root
                    .GetComponentInChildren<RotorRigidbodyController>(true);
                Assert.That(rotor, Is.Not.Null);
                Assert.That(rotor.GetComponent<Rigidbody>(), Is.Not.Null);
                Assert.That(rotor.GetComponent<Rigidbody>().isKinematic, Is.False);
                Assert.That(rotor.GetComponent<Collider>(), Is.Not.Null);
                Assert.That(rotor.GetComponent<SpinnerTouchSurface>(), Is.Not.Null);
                Assert.That(
                    transforms.Any(transform => transform.name == "MirrorQuadAxisFocus"),
                    Is.True,
                    "Mirror Quad must retain a numerical axis focus without a ring renderer.");
            }
            finally
            {
                if (previousSetup != null && previousSetup.Any(setup => setup.isLoaded))
                {
                    EditorSceneManager.RestoreSceneManagerSetup(previousSetup);
                }
                else
                {
                    EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                }
            }
        }

        private static bool HasAncestorNamed(Transform transform, string ancestorName)
        {
            Transform current = transform;
            while (current != null)
            {
                if (current.name == ancestorName)
                {
                    return true;
                }
                current = current.parent;
            }
            return false;
        }
    }
}
