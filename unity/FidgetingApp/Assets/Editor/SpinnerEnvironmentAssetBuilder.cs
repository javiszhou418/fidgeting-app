using System;
using FidgetingApp.Product;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.Editor
{
    public static class SpinnerEnvironmentAssetBuilder
    {
        public const string MaterialAssetPath =
            "Assets/Resources/EnvironmentBackgrounds/EnvironmentBackgroundMaterial.mat";
        public const string ParallaxMaterialAssetPath =
            "Assets/Resources/EnvironmentBackgrounds/EnvironmentParallaxMaterial.mat";
        public const string StarfieldMaterialAssetPath =
            "Assets/Resources/EnvironmentBackgrounds/EnvironmentStarfieldMaterial.mat";
        public const string ParallaxShaderName =
            "FidgetingApp/EnvironmentParallaxUnlit";
        public const string StarfieldShaderName =
            "FidgetingApp/EnvironmentStarfield";
        public const string LeftForegroundAssetPath =
            "Assets/Resources/EnvironmentForegrounds/canyon-left-foreground-v1.png";
        public const string RightForegroundAssetPath =
            "Assets/Resources/EnvironmentForegrounds/canyon-right-foreground-v1.png";

        [MenuItem("Fidgeting/Product/Rebuild Environment Background Assets")]
        public static void Build()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);

            foreach (SpinnerEnvironmentProfile profile in SpinnerEnvironmentCatalog.Profiles)
            {
                ConfigureTexture(profile);
            }

            ConfigureForegroundTexture(LeftForegroundAssetPath);
            ConfigureForegroundTexture(RightForegroundAssetPath);

            CreateOrUpdateMaterial();
            CreateOrUpdateParallaxMaterial();
            CreateOrUpdateStarfieldMaterial();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            Debug.Log(
                "[FidgetingApp] Unified five-product canyon background imported " +
                "and the opaque/parallax materials rebuilt.");
        }

        private static void ConfigureTexture(SpinnerEnvironmentProfile profile)
        {
            string assetPath = profile.TextureAssetPath;
            TextureImporter importer = AssetImporter.GetAtPath(assetPath) as TextureImporter;
            if (importer == null)
            {
                throw new InvalidOperationException(
                    $"Environment background is missing or not a texture: {assetPath}");
            }

            importer.textureType = TextureImporterType.Default;
            importer.sRGBTexture = true;
            importer.isReadable = false;
            importer.alphaSource = TextureImporterAlphaSource.None;
            importer.mipmapEnabled = false;
            importer.streamingMipmaps = false;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.filterMode = FilterMode.Bilinear;
            importer.anisoLevel = 1;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.maxTextureSize = profile.ImportMaxTextureSize;
            importer.textureCompression = TextureImporterCompression.Compressed;

            TextureImporterPlatformSettings ios =
                importer.GetPlatformTextureSettings("iPhone");
            ios.overridden = true;
            ios.maxTextureSize = profile.ImportMaxTextureSize;
            ios.resizeAlgorithm = TextureResizeAlgorithm.Mitchell;
            ios.format = TextureImporterFormat.ASTC_8x8;
            ios.compressionQuality = 100;
            importer.SetPlatformTextureSettings(ios);

            importer.SaveAndReimport();
        }

        private static void ConfigureForegroundTexture(string assetPath)
        {
            TextureImporter importer = AssetImporter.GetAtPath(assetPath) as TextureImporter;
            if (importer == null)
            {
                throw new InvalidOperationException(
                    $"Environment foreground is missing or not a texture: {assetPath}");
            }

            importer.textureType = TextureImporterType.Default;
            importer.sRGBTexture = true;
            importer.isReadable = false;
            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            importer.alphaIsTransparency = true;
            importer.mipmapEnabled = false;
            importer.streamingMipmaps = false;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.filterMode = FilterMode.Bilinear;
            importer.anisoLevel = 1;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.maxTextureSize = 4096;
            importer.textureCompression = TextureImporterCompression.CompressedHQ;

            TextureImporterPlatformSettings ios =
                importer.GetPlatformTextureSettings("iPhone");
            ios.overridden = true;
            ios.maxTextureSize = 4096;
            ios.resizeAlgorithm = TextureResizeAlgorithm.Mitchell;
            ios.format = TextureImporterFormat.ASTC_6x6;
            ios.compressionQuality = 100;
            importer.SetPlatformTextureSettings(ios);
            importer.SaveAndReimport();
        }

        private static void CreateOrUpdateMaterial()
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Unlit");
            if (shader == null)
            {
                throw new InvalidOperationException(
                    "Universal Render Pipeline/Unlit shader is unavailable.");
            }

            Material material = AssetDatabase.LoadAssetAtPath<Material>(MaterialAssetPath);
            if (material == null)
            {
                material = new Material(shader)
                {
                    name = "EnvironmentBackgroundMaterial"
                };
                AssetDatabase.CreateAsset(material, MaterialAssetPath);
            }
            else
            {
                material.shader = shader;
            }

            material.SetColor("_BaseColor", Color.white);
            material.SetFloat("_Surface", 0f);
            material.SetFloat("_AlphaClip", 0f);
            material.SetFloat("_Cull", 0f);
            material.SetFloat("_ZWrite", 1f);
            material.DisableKeyword("_SURFACE_TYPE_TRANSPARENT");
            material.DisableKeyword("_ALPHATEST_ON");
            // URP validates opaque Unlit materials back to the Geometry queue.
            // The quad is physically placed behind every product model and
            // writes depth, so standard opaque ordering is deterministic.
            material.renderQueue = (int)RenderQueue.Geometry;
            material.doubleSidedGI = true;
            material.enableInstancing = false;
            EditorUtility.SetDirty(material);
        }

        private static void CreateOrUpdateParallaxMaterial()
        {
            Shader shader = Shader.Find(ParallaxShaderName);
            if (shader == null)
            {
                throw new InvalidOperationException(
                    $"Environment parallax shader is unavailable: {ParallaxShaderName}");
            }

            Material material = AssetDatabase.LoadAssetAtPath<Material>(
                ParallaxMaterialAssetPath);
            if (material == null)
            {
                material = new Material(shader)
                {
                    name = "EnvironmentParallaxMaterial"
                };
                AssetDatabase.CreateAsset(material, ParallaxMaterialAssetPath);
            }
            else
            {
                material.shader = shader;
            }

            material.SetColor("_BaseColor", Color.white);
            material.SetFloat("_Saturation", 1f);
            material.SetFloat("_LayerMask", 0f);
            material.SetFloat("_LayerMaskStart", 0.38f);
            material.SetFloat("_LayerMaskFeather", 0.10f);
            material.SetFloat("_Opacity", 1f);
            material.SetFloat("_GlowEnabled", 0f);
            material.SetFloat("_GlowIntensity", 0f);
            material.SetVector("_GlowScaleA", new Vector4(0.5625f, 1f, 0f, 0f));
            material.SetVector("_GlowScaleB", new Vector4(0.5625f, 1f, 0f, 0f));
            material.SetFloat("_SrcBlend", (float)BlendMode.One);
            material.SetFloat("_DstBlend", (float)BlendMode.Zero);
            material.SetFloat("_ZWrite", 1f);
            material.SetFloat("_ZTest", (float)CompareFunction.LessEqual);
            material.renderQueue = (int)RenderQueue.Geometry;
            material.doubleSidedGI = true;
            material.enableInstancing = false;
            EditorUtility.SetDirty(material);
        }

        private static void CreateOrUpdateStarfieldMaterial()
        {
            Shader shader = Shader.Find(StarfieldShaderName);
            if (shader == null)
            {
                throw new InvalidOperationException(
                    $"Environment starfield shader is unavailable: {StarfieldShaderName}");
            }

            Material material = AssetDatabase.LoadAssetAtPath<Material>(
                StarfieldMaterialAssetPath);
            if (material == null)
            {
                material = new Material(shader)
                {
                    name = "EnvironmentStarfieldMaterial"
                };
                AssetDatabase.CreateAsset(material, StarfieldMaterialAssetPath);
            }
            else
            {
                material.shader = shader;
            }

            material.SetColor("_StarColor", new Color(0.75f, 0.82f, 0.78f, 1f));
            material.SetFloat("_Density", 0.035f);
            material.SetFloat("_Grid", 72f);
            material.SetFloat("_Seed", 1f);
            material.SetFloat("_Intensity", 0.65f);
            material.SetFloat("_PointRadius", 0.14f);
            material.renderQueue = (int)RenderQueue.Transparent;
            material.doubleSidedGI = true;
            material.enableInstancing = false;
            EditorUtility.SetDirty(material);
        }
    }
}
