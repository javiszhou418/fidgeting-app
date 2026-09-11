using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    /// <summary>
    /// Keeps a depth-tested TextMesh material bound to its dynamic font atlas.
    /// The built-in font material is ZTest Always; a custom material loses the
    /// atlas whenever the dynamic font rebuilds it, so this re-binds on every
    /// Font.textureRebuilt.
    /// </summary>
    [ExecuteAlways]
    [DisallowMultipleComponent]
    [RequireComponent(typeof(TextMesh))]
    public sealed class PremiumDisplayCaseLabelTextMaterial : MonoBehaviour
    {
        [SerializeField] private Material depthTestedMaterial;

        private TextMesh text;
        private MeshRenderer meshRenderer;

        public Material DepthTestedMaterial => depthTestedMaterial;

        public void Configure(Material material)
        {
            depthTestedMaterial = material;
            Bind();
        }

        private void OnEnable()
        {
            Font.textureRebuilt += HandleFontTextureRebuilt;
            Bind();
        }

        private void OnDisable()
        {
            Font.textureRebuilt -= HandleFontTextureRebuilt;
        }

        private void HandleFontTextureRebuilt(Font font)
        {
            if (text != null && font == text.font)
            {
                Bind();
            }
        }

        public bool IsBound =>
            depthTestedMaterial != null
            && text != null
            && text.font != null
            && meshRenderer != null
            && meshRenderer.sharedMaterial == depthTestedMaterial
            && depthTestedMaterial.mainTexture == text.font.material.mainTexture;

        private void Bind()
        {
            text ??= GetComponent<TextMesh>();
            meshRenderer ??= GetComponent<MeshRenderer>();
            if (depthTestedMaterial == null || text == null || text.font == null || meshRenderer == null)
            {
                return;
            }
            Texture atlas = text.font.material != null ? text.font.material.mainTexture : null;
            if (atlas != null && depthTestedMaterial.mainTexture != atlas)
            {
                depthTestedMaterial.mainTexture = atlas;
            }
            if (meshRenderer.sharedMaterial != depthTestedMaterial)
            {
                meshRenderer.sharedMaterial = depthTestedMaterial;
            }
        }
    }
}
