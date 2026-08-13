using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    /// <summary>
    /// Shipping Resources entry point used by the gacha result coordinator.
    /// Prize loading/import remains the caller's responsibility.
    /// </summary>
    public static class PremiumDisplayCaseFactory
    {
        public const string ResourcesPath = "Gacha/PremiumDisplayCase";

        public static PremiumDisplayCase Instantiate(Transform parent = null)
        {
            PremiumDisplayCase prefab = Resources.Load<PremiumDisplayCase>(
                ResourcesPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(
                    $"Missing Resources/{ResourcesPath}.prefab.");
            }

            return Object.Instantiate(prefab, parent, false);
        }
    }
}
