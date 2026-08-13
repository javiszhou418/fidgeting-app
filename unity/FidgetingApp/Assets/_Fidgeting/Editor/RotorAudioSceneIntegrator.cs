using System;
using System.Collections.Generic;
using System.Linq;
using ThreeBladeEDC.Interaction;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace ThreeBladeEDC.EditorTools
{
    /// <summary>
    /// Applies the shared rotor audio stack without regenerating model meshes,
    /// materials, lighting or camera composition in the shipping scenes.
    /// </summary>
    public static class RotorAudioSceneIntegrator
    {
        public const int RatchetVoiceCount = 12;

        private static readonly (string Path, int BladeCount)[] RotorScenes =
        {
            ("Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity", 3),
            ("Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity", 3),
            ("Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity", 3),
            ("Assets/_TwoLobeBar/Scenes/TwoLobeBar.unity", 2)
        };

        [MenuItem("Fidgeting/Audio/Apply Wind And Ratchet To Shipping Rotors")]
        public static void ApplyToShippingRotorScenes()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            AudioClip[] clickVariants = LoadRatchetClickVariants();
            SceneSetup[] previousSetup = EditorSceneManager.GetSceneManagerSetup();

            try
            {
                foreach ((string path, int blades) in RotorScenes)
                {
                    ApplyToScene(path, blades, clickVariants);
                }
            }
            finally
            {
                if (previousSetup.Any(setup => setup.isLoaded))
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

            AssetDatabase.SaveAssets();
            Debug.Log(
                "[RotorAudio] Wind plus ratchet audio applied to all four shipping rotor scenes.");
        }

        private static void ApplyToScene(
            string scenePath,
            int bladeCount,
            AudioClip[] clickVariants)
        {
            Scene scene = EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
            RotorRigidbodyController[] rotors = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<RotorRigidbodyController>(true))
                .ToArray();
            if (rotors.Length != 1)
            {
                throw new InvalidOperationException(
                    $"Expected one rotor in {scenePath}, found {rotors.Length}.");
            }

            RotorRigidbodyController rotor = rotors[0];
            Transform sceneRoot = rotor.transform.root;
            RotorWindAudio wind =
                sceneRoot.GetComponentInChildren<RotorWindAudio>(true);
            if (wind == null)
            {
                GameObject windObject = new GameObject("RotorWindAudio");
                windObject.transform.SetParent(sceneRoot, false);
                wind = windObject.AddComponent<RotorWindAudio>();
            }
            wind.gameObject.name = "RotorWindAudio";
            wind.Configure(
                rotor,
                bladeCount,
                RotorWindAudioModel.DefaultMasterVolume);

            MetalRatchetDetentAudio ratchet =
                sceneRoot.GetComponentInChildren<MetalRatchetDetentAudio>(true);
            if (ratchet == null)
            {
                GameObject ratchetObject = new GameObject("RatchetAudio");
                ratchetObject.transform.SetParent(sceneRoot, false);
                ratchet = ratchetObject.AddComponent<MetalRatchetDetentAudio>();
            }
            ratchet.gameObject.name = "RatchetAudio";

            List<AudioSource> voices = ratchet.gameObject
                .GetComponentsInChildren<AudioSource>(true)
                .OrderBy(source => source.gameObject.name, StringComparer.Ordinal)
                .ToList();
            while (voices.Count < RatchetVoiceCount)
            {
                GameObject voiceObject = new GameObject($"Voice_{voices.Count:00}");
                voiceObject.transform.SetParent(ratchet.transform, false);
                voices.Add(voiceObject.AddComponent<AudioSource>());
            }

            ratchet.Configure(
                rotor,
                clickVariants,
                voices.Take(RatchetVoiceCount).ToArray(),
                0.82f);

            EditorUtility.SetDirty(wind);
            EditorUtility.SetDirty(wind.GetComponent<AudioSource>());
            EditorUtility.SetDirty(ratchet);
            foreach (AudioSource voice in voices)
            {
                EditorUtility.SetDirty(voice);
            }
            EditorSceneManager.MarkSceneDirty(scene);
            if (!EditorSceneManager.SaveScene(scene))
            {
                throw new InvalidOperationException(
                    $"Failed to save rotor audio wiring in {scenePath}.");
            }
        }

        private static AudioClip[] LoadRatchetClickVariants()
        {
            string[] guids = AssetDatabase.FindAssets(
                "t:AudioClip",
                new[] { "Assets/_Fidgeting/Audio/RatchetClicks" });
            AudioClip[] clips = guids
                .Select(AssetDatabase.GUIDToAssetPath)
                .OrderBy(path => path, StringComparer.Ordinal)
                .Select(AssetDatabase.LoadAssetAtPath<AudioClip>)
                .Where(clip => clip != null)
                .ToArray();
            if (clips.Length != 5)
            {
                throw new InvalidOperationException(
                    $"Expected five atomic ratchet click clips, found {clips.Length}.");
            }
            return clips;
        }
    }
}
