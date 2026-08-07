using System;
using UnityEditor;
using UnityEngine;

namespace CodexUnityLabEditor
{
    public sealed class ProductStickerArtworkImporter : AssetPostprocessor
    {
        public const string ArtworkRoot =
            "Assets/Resources/ProductStickers/BackdropWhite";

        private void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(ArtworkRoot + "/", StringComparison.Ordinal)
                || !(assetImporter is TextureImporter importer))
            {
                return;
            }

            ConfigureImporter(importer);
        }

        [MenuItem("Tools/Codex/Configure Product Sticker Artwork")]
        public static void ConfigureAllProductStickerArtwork()
        {
            string[] guids = AssetDatabase.FindAssets(
                "t:Texture2D",
                new[] { ArtworkRoot });
            int configured = 0;
            for (int index = 0; index < guids.Length; index++)
            {
                string path = AssetDatabase.GUIDToAssetPath(guids[index]);
                if (!path.EndsWith(".png", StringComparison.OrdinalIgnoreCase)
                    || !(AssetImporter.GetAtPath(path) is TextureImporter importer))
                {
                    continue;
                }

                ConfigureImporter(importer);
                importer.SaveAndReimport();
                configured++;
            }

            Debug.Log(
                $"[Codex] Configured {configured} sticker masks for stable oblique rendering.");
        }

        internal static void ConfigureImporter(TextureImporter importer)
        {
            importer.textureType = TextureImporterType.Default;
            importer.sRGBTexture = false;
            importer.isReadable = false;
            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            importer.alphaIsTransparency = false;
            importer.mipmapEnabled = true;
            importer.mipMapsPreserveCoverage = true;
            importer.alphaTestReferenceValue = 0.10f;
            importer.mipmapFilter = TextureImporterMipFilter.KaiserFilter;
            importer.mipMapBias = -0.50f;
            importer.streamingMipmaps = false;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.filterMode = FilterMode.Trilinear;
            importer.anisoLevel = 8;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.maxTextureSize = 1024;
            importer.textureCompression = TextureImporterCompression.Uncompressed;

            TextureImporterPlatformSettings ios =
                importer.GetPlatformTextureSettings("iPhone");
            ios.overridden = true;
            ios.maxTextureSize = 1024;
            ios.resizeAlgorithm = TextureResizeAlgorithm.Mitchell;
            ios.format = TextureImporterFormat.ASTC_4x4;
            ios.compressionQuality = 100;
            importer.SetPlatformTextureSettings(ios);
        }
    }
}
