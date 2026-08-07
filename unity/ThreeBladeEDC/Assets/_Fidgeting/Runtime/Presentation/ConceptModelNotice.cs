using UnityEngine;

namespace ThreeBladeEDC.Presentation
{
    public sealed class ConceptModelNotice : MonoBehaviour
    {
        [TextArea(3, 8)]
        public string notice =
            "Concept visualization reconstructed from reference images. " +
            "Bearing dimensions, internal fit, tolerances and fasteners are visual assumptions, " +
            "not manufacturing-ready CAD or a bill of materials.";
    }
}
