using System;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Editor
{
    /// <summary>
    /// R053 (user 2026-09-09): restyle only the label plate of the approved
    /// Gate 12 R004 prefab in place — English Oxanium copy, no LEVEL / id,
    /// holo-foil plate driven by tilt. Deliberately does not call
    /// <see cref="PremiumDisplayCaseGate12Builder"/>, which would refresh the
    /// shells' materials from the Gate 11 source.
    /// </summary>
    public static class PremiumDisplayCaseGate12LabelRestyle
    {
        public const string PrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R004/PresentationRoot.prefab";
        public const string FoilMaterialPath =
            "Assets/_DisplayCase/Generated/Gate12R004/Materials/Gate12R004LabelHoloFoil.mat";
        public const string FoilShaderName = "FidgetingApp/PremiumDisplayCaseLabelHoloFoil";
        public const string ProductFontPath =
            "Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf";

        public readonly struct Row
        {
            public Row(string objectName, float z, float characterSize, FontStyle style, Color ink)
            {
                ObjectName = objectName;
                Z = z;
                CharacterSize = characterSize;
                Style = style;
                Ink = ink;
            }

            public string ObjectName { get; }
            public float Z { get; }
            public float CharacterSize { get; }
            public FontStyle Style { get; }
            public Color Ink { get; }
        }

        public const float LeftMarginX = -0.00084f;
        /// <summary>Dark graphite ink on a bright foil plate.</summary>
        public static readonly Color NameInk = new Color(0.05f, 0.055f, 0.065f, 1f);
        public static readonly Color EditionInk = new Color(0.13f, 0.14f, 0.16f, 1f);
        public static readonly Color RarityInk = new Color(0.08f, 0.085f, 0.10f, 1f);
        public static readonly Color DateInk = new Color(0.17f, 0.18f, 0.20f, 1f);

        /// <summary>Top to bottom: edition · name · rarity · acquired. Id row is emptied.</summary>
        public static readonly Row[] Rows =
        {
            new Row("AuthoritativeEditionFinish", -0.00021f, 0.0000098f, FontStyle.Normal, EditionInk),
            new Row("AuthoritativeProductName", -0.00008f, 0.0000215f, FontStyle.Bold, NameInk),
            new Row("AuthoritativeRarityLevel", 0.00008f, 0.0000110f, FontStyle.Bold, RarityInk),
            new Row("AuthoritativeAcquiredDate", 0.00019f, 0.0000090f, FontStyle.Normal, DateInk),
            new Row("AuthoritativeCollectibleId", 0.00027f, 0.0000090f, FontStyle.Normal, DateInk),
        };

        [MenuItem("Fidgeting/Display Case/Gate 12 R004/Restyle Label (R053 holo foil)")]
        public static void Apply()
        {
            Font font = AssetDatabase.LoadAssetAtPath<Font>(ProductFontPath);
            if (font == null)
            {
                throw new FileNotFoundException("Product font is missing.", ProductFontPath);
            }
            Material foil = CreateOrUpdateFoilMaterial();

            GameObject root = PrefabUtility.LoadPrefabContents(PrefabPath);
            try
            {
                Transform[] transforms = root.GetComponentsInChildren<Transform>(true);
                Renderer plate = null;
                foreach (Transform candidate in transforms)
                {
                    if (candidate.name == "PhysicalLabel")
                    {
                        plate = candidate.GetComponent<Renderer>();
                    }
                }
                if (plate == null)
                {
                    throw new InvalidOperationException("Prefab has no PhysicalLabel renderer.");
                }
                plate.sharedMaterial = foil;

                foreach (Row row in Rows)
                {
                    TextMesh text = FindTextMesh(transforms, row.ObjectName);
                    text.font = font;
                    text.fontSize = 64;
                    text.richText = false;
                    text.fontStyle = row.Style;
                    text.characterSize = row.CharacterSize;
                    text.color = row.Ink;
                    text.anchor = TextAnchor.MiddleLeft;
                    text.alignment = TextAlignment.Left;
                    text.transform.localPosition = new Vector3(LeftMarginX, -0.000002f, row.Z);
                    text.GetComponent<MeshRenderer>().sharedMaterial = font.material;
                }

                var driver = root.GetComponent<PremiumDisplayCaseLabelFoil>()
                    ?? root.AddComponent<PremiumDisplayCaseLabelFoil>();
                driver.ConfigureAuthoring(plate);

                PrefabUtility.SaveAsPrefabAsset(root, PrefabPath);
            }
            finally
            {
                PrefabUtility.UnloadPrefabContents(root);
            }
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log($"Gate 12 R004 label restyled (R053): {PrefabPath}");
        }

        public static Material CreateOrUpdateFoilMaterial()
        {
            Shader shader = Shader.Find(FoilShaderName);
            if (shader == null)
            {
                throw new InvalidOperationException($"Shader {FoilShaderName} did not compile.");
            }
            Material material = AssetDatabase.LoadAssetAtPath<Material>(FoilMaterialPath);
            if (material == null)
            {
                material = new Material(shader);
                Directory.CreateDirectory(Path.GetDirectoryName(FoilMaterialPath));
                AssetDatabase.CreateAsset(material, FoilMaterialPath);
            }
            else
            {
                material.shader = shader;
            }
            material.SetColor("_BaseColor", new Color(0.44f, 0.45f, 0.47f, 1f));
            material.SetFloat("_GrainStrength", 0.10f);
            material.SetFloat("_GrainScale", 160f);
            material.SetFloat("_SpectralStrength", 0.30f);
            material.SetFloat("_SpectralScale", 1.8f);
            material.SetFloat("_SpectralStretch", 1.2f);
            material.SetFloat("_SpecStrength", 0.45f);
            material.SetFloat("_SpecPower", 48f);
            material.SetFloat("_FresnelPower", 2.4f);
            material.SetFloat("_Saturation", 0.72f);
            EditorUtility.SetDirty(material);
            return material;
        }

        private static TextMesh FindTextMesh(Transform[] transforms, string name)
        {
            foreach (Transform candidate in transforms)
            {
                if (candidate.name == name)
                {
                    TextMesh text = candidate.GetComponent<TextMesh>();
                    if (text != null)
                    {
                        return text;
                    }
                }
            }
            throw new InvalidOperationException($"Prefab has no TextMesh '{name}'.");
        }
    }
}
