using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    public static class PremiumDisplayCaseShippingFactory
    {
        public const string ResourcesPath =
            "Gacha/PremiumDisplayCaseGate12R010/PresentationRoot";
        public const string PresentationInstanceName =
            "PremiumDisplayCaseGate12R010";
        public const string NativeHybridResourcesPath =
            "Gacha/PremiumDisplayCaseGate12R004/PresentationRoot";
        public const string NativeHybridPresentationInstanceName =
            "PremiumDisplayCaseGate12R004";
        public static readonly Vector3 ThreeBladeContentEuler =
            new Vector3(0f, -18f, 0f);

        public static PremiumDisplayCaseShippingPresentation Instantiate(
            Transform parent = null)
        {
            return InstantiateAt(ResourcesPath, parent);
        }

        public static PremiumDisplayCaseShippingPresentation
            InstantiateNativeHybridBaseline(Transform parent = null)
        {
            return InstantiateAt(NativeHybridResourcesPath, parent);
        }

        private static PremiumDisplayCaseShippingPresentation InstantiateAt(
            string resourcesPath,
            Transform parent)
        {
            PremiumDisplayCaseShippingPresentation prefab =
                Resources.Load<PremiumDisplayCaseShippingPresentation>(
                    resourcesPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(
                    $"Missing Resources/{resourcesPath}.prefab.");
            }
            return Object.Instantiate(prefab, parent, false);
        }
    }
}
