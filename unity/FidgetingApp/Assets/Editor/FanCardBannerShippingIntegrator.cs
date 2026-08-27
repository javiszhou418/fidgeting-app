using System;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.EditorTools
{
    public static class FanCardBannerShippingIntegrator
    {
        private const string DestinationAssetPath =
            "Assets/Plugins/iOS/GachaBanners/product-banner-magnetic-fan-card.png";
        private const int ExpectedWidth = 1179;
        private const int ExpectedHeight = 654;

        [MenuItem("Tools/Codex/Fan Card/Integrate Approved Gacha Banner")]
        public static void IntegrateMenu()
        {
            Integrate();
        }

        public static void IntegrateBatch()
        {
            Integrate();
        }

        private static void Integrate()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string sourcePath = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-fan-card/evidence/"
                    + "09-environment/rev-007/surreal-clean-20mm-banner.png");
            string destinationPath = Path.Combine(
                projectRoot,
                DestinationAssetPath);
            string evidenceFolder = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-fan-card/evidence/"
                    + "12-shipping/rev-002");
            if (!File.Exists(sourcePath))
            {
                throw new FileNotFoundException(
                    "The approved surreal levitation Banner is missing.",
                    sourcePath);
            }
            Directory.CreateDirectory(Path.GetDirectoryName(destinationPath)!);
            Directory.CreateDirectory(evidenceFolder);
            File.Copy(sourcePath, destinationPath, true);
            AssetDatabase.ImportAsset(
                DestinationAssetPath,
                ImportAssetOptions.ForceSynchronousImport
                    | ImportAssetOptions.ForceUpdate);

            byte[] png = File.ReadAllBytes(destinationPath);
            var texture = new Texture2D(2, 2, TextureFormat.RGBA32, false);
            try
            {
                if (!ImageConversion.LoadImage(texture, png, false)
                    || texture.width != ExpectedWidth
                    || texture.height != ExpectedHeight)
                {
                    throw new InvalidDataException(
                        $"Banner must be {ExpectedWidth}×{ExpectedHeight}; "
                        + $"actual={texture.width}×{texture.height}.");
                }
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(texture);
            }

            File.WriteAllText(
                Path.Combine(evidenceFolder, "banner-integration-report.json"),
                JsonUtility.ToJson(new IntegrationReport
                {
                    source = sourcePath,
                    destinationAssetPath = DestinationAssetPath,
                    width = ExpectedWidth,
                    height = ExpectedHeight,
                    storefrontAssetName = "product-banner-magnetic-fan-card",
                    aspectPolicy = "scaledToFit at intrinsic 1179:654",
                    screenSpaceParticles = 0,
                    shippingIntegrated = true,
                    built = false,
                    installed = false,
                    deviceValidated = false
                }, true) + "\n");
            Debug.Log(
                $"[FanCardBannerShipping] Integrated {DestinationAssetPath} "
                + $"({ExpectedWidth}×{ExpectedHeight}); build/install not started.");
        }

        [Serializable]
        private sealed class IntegrationReport
        {
            public string source;
            public string destinationAssetPath;
            public int width;
            public int height;
            public string storefrontAssetName;
            public string aspectPolicy;
            public int screenSpaceParticles;
            public bool shippingIntegrated;
            public bool built;
            public bool installed;
            public bool deviceValidated;
        }
    }
}
