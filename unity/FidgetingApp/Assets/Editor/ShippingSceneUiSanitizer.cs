using FidgetingApp.Product;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.Editor
{
    public static class ShippingSceneUiSanitizer
    {
        [MenuItem("Tools/Codex/Strip Legacy HUD From Shipping Scenes")]
        public static void StripLegacyHudFromShippingScenes()
        {
            foreach (ProductCatalogEntry product in ProductCatalog.ShippingEntries)
            {
                Scene scene = EditorSceneManager.OpenScene(
                    product.ScenePath,
                    OpenSceneMode.Single);
                bool changed = false;
                foreach (GameObject root in scene.GetRootGameObjects())
                {
                    Transform[] transforms = root.GetComponentsInChildren<Transform>(true);
                    for (int index = transforms.Length - 1; index >= 0; index--)
                    {
                        Transform candidate = transforms[index];
                        if (candidate == null
                            || (candidate.name != "MobileCanvas"
                                && candidate.name != "EventSystem"))
                        {
                            continue;
                        }

                        Object.DestroyImmediate(candidate.gameObject);
                        changed = true;
                    }
                }

                if (changed)
                {
                    EditorSceneManager.MarkSceneDirty(scene);
                    EditorSceneManager.SaveScene(scene);
                    Debug.Log($"[Codex] Removed legacy HUD objects from {product.ScenePath}");
                }
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
        }
    }
}
