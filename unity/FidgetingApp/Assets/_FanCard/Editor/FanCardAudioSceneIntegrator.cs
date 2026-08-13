using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.FanCard.EditorTools
{
    public static class FanCardAudioSceneIntegrator
    {
        private static readonly string[] ClickPaths =
        {
            "Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_01.wav",
            "Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_02.wav",
            "Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_03.wav",
            "Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_04.wav",
            "Assets/_Fidgeting/Audio/RatchetClicks/MetalDetent_Click_05.wav"
        };

        [MenuItem("Tools/Codex/Fan Card/3 Apply Metal Audio To Shipping Scene")]
        public static void ApplyToShippingScene()
        {
            Scene scene = EditorSceneManager.OpenScene(
                FanCardSpecifications.ScenePath,
                OpenSceneMode.Single);
            FanCardController controller = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<FanCardController>(true))
                .Single();
            FanCardMetalDetentAudio audio = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<FanCardMetalDetentAudio>(true))
                .SingleOrDefault();
            if (audio == null)
            {
                var audioObject = new GameObject("FanCardMetalAudio");
                audioObject.transform.SetParent(controller.transform, false);
                audio = audioObject.AddComponent<FanCardMetalDetentAudio>();
            }

            AudioSource[] voices = audio.GetComponentsInChildren<AudioSource>(true);
            for (int index = voices.Length;
                index < FanCardMetalAudioModel.VoiceCount;
                index++)
            {
                var voiceObject = new GameObject($"Voice_{index:00}");
                voiceObject.transform.SetParent(audio.transform, false);
                voiceObject.AddComponent<AudioSource>();
            }

            voices = audio.GetComponentsInChildren<AudioSource>(true)
                .Take(FanCardMetalAudioModel.VoiceCount)
                .ToArray();
            AudioClip[] variants = ClickPaths
                .Select(path => AssetDatabase.LoadAssetAtPath<AudioClip>(path))
                .ToArray();
            if (variants.Any(clip => clip == null))
            {
                throw new FileNotFoundException(
                    "One or more canonical metal detent click assets are missing.");
            }

            audio.Configure(
                controller,
                variants,
                voices,
                FanCardMetalAudioModel.DefaultMasterVolume);
            EditorUtility.SetDirty(audio);
            foreach (AudioSource voice in voices)
            {
                EditorUtility.SetDirty(voice);
            }

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene);
            AssetDatabase.SaveAssets();
            Debug.Log(
                "[FanCardAudio] Applied 5 heavy-alloy variants and 8 voices "
                + "to the shipping magnetic fan card scene.");
        }
    }
}
