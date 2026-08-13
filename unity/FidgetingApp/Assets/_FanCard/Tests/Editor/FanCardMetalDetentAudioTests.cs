using System.IO;
using System.Linq;
using FidgetingApp.FanCard;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.Tests.Editor
{
    public sealed class FanCardMetalDetentAudioTests
    {
        private SceneSetup[] previousSceneSetup;

        [SetUp]
        public void CaptureSceneSetup()
        {
            previousSceneSetup = EditorSceneManager.GetSceneManagerSetup();
        }

        [TearDown]
        public void RestoreSceneSetup()
        {
            if (previousSceneSetup != null
                && previousSceneSetup.Any(setup => setup.isLoaded))
            {
                EditorSceneManager.RestoreSceneManagerSetup(previousSceneSetup);
            }
            else
            {
                EditorSceneManager.NewScene(
                    NewSceneSetup.EmptyScene,
                    NewSceneMode.Single);
            }
        }

        [Test]
        public void HeavyAlloyMapping_RotatesVariantsAndStaysBelowOriginalPitch()
        {
            Assert.That(FanCardMetalAudioModel.NextVariantIndex(5, -1), Is.Zero);
            Assert.That(FanCardMetalAudioModel.NextVariantIndex(5, 4), Is.Zero);
            Assert.That(FanCardMetalAudioModel.ResolvePitch(0f, 0), Is.LessThan(0.90f));
            Assert.That(
                FanCardMetalAudioModel.ResolvePitch(1f, 0),
                Is.GreaterThan(FanCardMetalAudioModel.ResolvePitch(0f, 0)));
            Assert.That(
                FanCardMetalAudioModel.ResolveVolume(
                    1f,
                    FanCardMetalAudioModel.DefaultMasterVolume),
                Is.EqualTo(FanCardMetalAudioModel.DefaultMasterVolume).Within(0.0001f));
        }

        [Test]
        public void Renderer_IsOneClickPerAuthorizedSemanticCrossingOnly()
        {
            string source = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "_FanCard/Runtime/FanCardMetalDetentAudio.cs"));

            StringAssert.Contains(
                "controller.SemanticEventRaised += HandleSemanticEvent",
                source);
            StringAssert.Contains(
                "semanticEvent != FidgetSemanticEvent.DetentCrossed",
                source);
            Assert.That(source.Split(new[] { "PlayOneShot(" },
                System.StringSplitOptions.None), Has.Length.EqualTo(2));
            StringAssert.DoesNotContain("void Update(", source);
            StringAssert.DoesNotContain("IosHaptics", source);
            StringAssert.DoesNotContain("InputSystem", source);
        }

        [Test]
        public void ShippingFanCard_HasFiveMetalVariantsAndEightVoices()
        {
            Assert.That(
                AssetDatabase.LoadAssetAtPath<SceneAsset>(
                    FanCardSpecifications.ScenePath),
                Is.Not.Null);
            Scene scene = EditorSceneManager.OpenScene(
                FanCardSpecifications.ScenePath,
                OpenSceneMode.Single);
            FanCardController controller = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<FanCardController>(true))
                .Single();
            FanCardMetalDetentAudio audio = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<FanCardMetalDetentAudio>(true))
                .Single();

            Assert.That(audio.Controller, Is.SameAs(controller));
            Assert.That(audio.ClickVariants, Has.Length.EqualTo(5));
            Assert.That(audio.ClickVariants, Has.None.Null);
            Assert.That(
                audio.Voices,
                Has.Length.EqualTo(FanCardMetalAudioModel.VoiceCount));
            Assert.That(audio.Voices, Has.None.Null);
            Assert.That(
                audio.MasterVolume,
                Is.EqualTo(FanCardMetalAudioModel.DefaultMasterVolume)
                    .Within(0.0001f));
            Assert.That(audio.Voices.All(voice => !voice.playOnAwake), Is.True);
            Assert.That(audio.Voices.All(voice => !voice.loop), Is.True);
        }
    }
}
