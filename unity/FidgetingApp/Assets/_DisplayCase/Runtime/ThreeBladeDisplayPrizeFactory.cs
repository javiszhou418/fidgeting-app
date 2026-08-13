using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    /// <summary>
    /// Shipping Resources entry point for the authored three-blade prize.
    /// The 90-degree X rotation maps the spinner's XZ presentation plane to
    /// the display case's XY-facing content slot.
    /// </summary>
    public static class ThreeBladeDisplayPrizeFactory
    {
        public const string ResourcesPath = "Gacha/ThreeBladeDisplayPrize";

        public static PremiumDisplayCaseContentOptions ContentOptions =>
            new PremiumDisplayCaseContentOptions(
                true,
                4f,
                new Vector3(90f, -18f, 0f));

        public static GameObject Instantiate(Transform parent = null)
        {
            GameObject prefab = Resources.Load<GameObject>(ResourcesPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(
                    $"Missing Resources/{ResourcesPath}.prefab.");
            }

            return Object.Instantiate(prefab, parent, false);
        }
    }
}
