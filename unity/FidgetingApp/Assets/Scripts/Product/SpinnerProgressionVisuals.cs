using System.Collections.Generic;
using UnityEngine;

namespace FidgetingApp.Product
{
    /// <summary>
    /// Data-only compatibility adapter for the five progression tiers.
    /// Progression names, levels, and rewards remain authoritative in
    /// <see cref="SpinnerProgressionRules"/>, but progression never adds
    /// visible geometry to a shipping product.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class SpinnerProgressionVisuals : MonoBehaviour
    {
        // Retained so migration and acceptance tests can prove that the
        // retired hierarchy remains absent. This component never creates it.
        public const string VisualRootName = "ProgressionVisuals";

        private int activeStageIndex = -1;
        private string activeModelId = string.Empty;

        public int ActiveStageIndex => activeStageIndex;
        public string ActiveModelId => activeModelId;
        public string ActiveMaterialName
        {
            get
            {
                if (activeStageIndex < 0)
                {
                    return string.Empty;
                }

                SpinnerUpgradeStage stage = SpinnerProgressionRules.Stages[activeStageIndex];
                return $"Progression_{stage.LevelThreshold:000}_{Sanitize(stage.MaterialName)}";
            }
        }

        // Compatibility properties remain false so legacy callers cannot
        // recreate the rejected collars, bearing rings, cage, or crown.
        public bool WeightRingVisible => false;
        public bool AuxiliaryBearingsVisible => false;
        public bool LowResistanceCageVisible => false;
        public bool FinalCrownVisible => false;
        public int GeneratedColliderCount => 0;
        public int GeneratedRendererCount => 0;
        public bool CreatesRuntimeGeometry => false;

        public static int StageIndexForLevel(int level)
        {
            IReadOnlyList<SpinnerUpgradeStage> stages = SpinnerProgressionRules.Stages;
            int active = 0;
            for (int index = 1; index < stages.Count; index++)
            {
                if (level < stages[index].LevelThreshold)
                {
                    break;
                }

                active = index;
            }

            return active;
        }

        public void Apply(string modelId, int level)
        {
            activeModelId = modelId ?? string.Empty;
            activeStageIndex = StageIndexForLevel(level);
        }

        private static string Sanitize(string value)
        {
            return string.IsNullOrEmpty(value)
                ? "Material"
                : value.Replace(" ", string.Empty).Replace("+", "Plus");
        }
    }
}
