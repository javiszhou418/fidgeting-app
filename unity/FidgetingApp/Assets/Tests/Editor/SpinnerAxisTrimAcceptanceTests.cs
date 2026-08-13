using System;
using System.Linq;
using NUnit.Framework;
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
            "UndercutShadowGap"
        };

        [TestCase(
            "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity",
            "ThreeBladeEDC_Root",
            "TopCap",
            "BearingOuterRace")]
        [TestCase(
            "Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity",
            "ThreeBladeEDC_Root",
            "FingerCap_Top",
            "BearingOuterRace")]
        [TestCase(
            "Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity",
            "ImportedSpinner_Root",
            "FingerCap_Top",
            "BearingOuterRace")]
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
                    Assert.That(
                        transforms.Any(transform => transform.name == rejectedName),
                        Is.False,
                        $"{scenePath} must not restore decorative ring {rejectedName}.");
                }

                Transform cap = transforms.FirstOrDefault(
                    transform => transform.name == capName
                        && transform.GetComponent<Renderer>()?.enabled == true);
                Transform mechanicalAxis = transforms.FirstOrDefault(
                    transform => transform.name == mechanicalAxisName
                        && transform.GetComponent<Renderer>()?.enabled == true);
                Assert.That(cap, Is.Not.Null, $"{scenePath} lost its real finger cap.");
                Assert.That(
                    cap.GetComponent<Renderer>(),
                    Is.Not.Null,
                    $"{scenePath} finger cap must remain visible and touch-legible.");
                Assert.That(
                    mechanicalAxis,
                    Is.Not.Null,
                    $"{scenePath} lost its mechanical axle or bearing component.");
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
    }
}
