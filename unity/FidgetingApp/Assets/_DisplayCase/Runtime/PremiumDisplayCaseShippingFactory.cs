using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    public static class PremiumDisplayCaseShippingFactory
    {
        public const string ResourcesPath =
            "Gacha/PremiumDisplayCaseGate12R004/PresentationRoot";
        public static readonly Vector3 ThreeBladeContentEuler =
            new Vector3(0f, -18f, 0f);

        public static PremiumDisplayCaseShippingPresentation Instantiate(
            Transform parent = null)
        {
            PremiumDisplayCaseShippingPresentation prefab =
                Resources.Load<PremiumDisplayCaseShippingPresentation>(
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
