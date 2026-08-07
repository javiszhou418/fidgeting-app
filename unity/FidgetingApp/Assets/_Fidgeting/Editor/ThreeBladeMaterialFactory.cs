using UnityEditor;
using UnityEngine;

namespace ThreeBladeEDC.EditorTools
{
    public static class ThreeBladeMaterialFactory
    {
        public sealed class MaterialSet
        {
            public Material blade;
            public Material cap;
            public Material bevel;
            public Material darkRing;
            public Material bearing;
            public Material inset;
            public Material floor;
            public Cubemap studioReflection;
        }

        private const string GeneratedRoot = "Assets/_Fidgeting/Generated";
        private const string MaterialsFolder = GeneratedRoot + "/Materials";
        private const string TexturesFolder = GeneratedRoot + "/Textures";

        public static MaterialSet CreateOrUpdate()
        {
            EnsureFolders();

            Texture2D sandblast = CreateOrUpdateTexture(
                TexturesFolder + "/T_Sandblast.asset",
                false);
            Texture2D radialBrush = CreateOrUpdateTexture(
                TexturesFolder + "/T_RadialBrush.asset",
                true);
            Texture2D sandblastNormal = CreateOrUpdateNormalTexture(
                TexturesFolder + "/N_Sandblast.asset",
                false);
            Texture2D radialNormal = CreateOrUpdateNormalTexture(
                TexturesFolder + "/N_RadialBrush.asset",
                true);

            MaterialSet set = new MaterialSet
            {
                blade = CreateOrUpdateMaterial(
                    "M_BladeSandblast", new Color32(0xAE, 0xB3, 0xB6, 0xFF), 1f, 0.72f, sandblast, sandblastNormal, 0.16f),
                cap = CreateOrUpdateMaterial(
                    "M_CapRadialBrushed", new Color32(0xC2, 0xC5, 0xC7, 0xFF), 1f, 0.79f, radialBrush, radialNormal, 0.10f,
                    "ThreeBlade/RadialBrushedMetal"),
                bevel = CreateOrUpdateMaterial(
                    "M_BevelPolished", new Color32(0xD6, 0xDA, 0xDD, 0xFF), 1f, 0.90f, null, null, 0f),
                darkRing = CreateOrUpdateMaterial(
                    "M_DarkRing", new Color32(0x0B, 0x0D, 0x10, 0xFF), 0f, 0.45f, sandblast, sandblastNormal, 0.08f),
                bearing = CreateOrUpdateMaterial(
                    "M_BearingSteel", new Color32(0x68, 0x70, 0x77, 0xFF), 1f, 0.76f, null, null, 0f),
                inset = CreateOrUpdateMaterial(
                    "M_BladeInset", new Color32(0x28, 0x2D, 0x32, 0xFF), 0.85f, 0.48f, sandblast, sandblastNormal, 0.08f),
                floor = CreateOrUpdateMaterial(
                    "M_StudioFloor", new Color32(0x01, 0x02, 0x03, 0xFF), 0f, 0.08f, null, null, 0f),
                studioReflection = CreateOrUpdateStudioReflection(
                    TexturesFolder + "/C_StudioReflection.asset")
            };

            // URP strips emission variants unless the source material opts
            // in. Runtime glints only override this already-present black
            // channel; they never instantiate or mutate shared materials.
            SetIfPresent(set.bevel, "_EmissionColor", Color.black);
            set.bevel.EnableKeyword("_EMISSION");
            EditorUtility.SetDirty(set.bevel);

            // The cap should show broad machined sectors, not a high-contrast
            // starburst. Keep the shader contribution below the albedo grain.
            SetIfPresent(set.cap, "_RadialContrast", 0.10f);
            EditorUtility.SetDirty(set.cap);

            AssetDatabase.SaveAssets();
            return set;
        }

        private static Material CreateOrUpdateMaterial(
            string name,
            Color color,
            float metallic,
            float smoothness,
            Texture2D texture,
            Texture2D normalMap,
            float normalStrength,
            string shaderName = null)
        {
            string path = MaterialsFolder + "/" + name + ".mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            Shader shader = Shader.Find(
                string.IsNullOrEmpty(shaderName)
                    ? "Universal Render Pipeline/Lit"
                    : shaderName);
            if (shader == null)
            {
                throw new MissingReferenceException(
                    $"Required shader was not found: {shaderName}");
            }

            if (material == null)
            {
                material = new Material(shader) { name = name };
                AssetDatabase.CreateAsset(material, path);
            }
            else
            {
                material.shader = shader;
            }

            SetIfPresent(material, "_BaseColor", color);
            SetIfPresent(material, "_Color", color);
            SetIfPresent(material, "_Metallic", metallic);
            SetIfPresent(material, "_Smoothness", smoothness);
            if (material.HasProperty("_BaseMap"))
            {
                material.SetTexture("_BaseMap", texture);
            }

            if (material.HasProperty("_MainTex"))
            {
                material.SetTexture("_MainTex", texture);
            }

            if (material.HasProperty("_BumpMap"))
            {
                material.SetTexture("_BumpMap", normalMap);
                material.SetFloat("_BumpScale", normalStrength);
                if (normalMap != null)
                {
                    material.EnableKeyword("_NORMALMAP");
                }
                else
                {
                    material.DisableKeyword("_NORMALMAP");
                }
            }

            EditorUtility.SetDirty(material);
            return material;
        }

        private static Texture2D CreateOrUpdateTexture(string path, bool radial)
        {
            Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (texture == null)
            {
                texture = new Texture2D(256, 256, TextureFormat.RGBA32, true)
                {
                    name = System.IO.Path.GetFileNameWithoutExtension(path),
                    wrapMode = TextureWrapMode.Repeat,
                    filterMode = FilterMode.Trilinear,
                    anisoLevel = 4
                };
                AssetDatabase.CreateAsset(texture, path);
            }

            Color32[] pixels = new Color32[texture.width * texture.height];
            for (int y = 0; y < texture.height; y++)
            {
                for (int x = 0; x < texture.width; x++)
                {
                    float u = (x + 0.5f) / texture.width - 0.5f;
                    float v = (y + 0.5f) / texture.height - 0.5f;
                    float pattern;
                    if (radial)
                    {
                        float angle = Mathf.Atan2(v, u);
                        // A real radial brushing pass follows straight rays
                        // from the centre. Keep the colour variation very
                        // low so it reads as machining grain instead of a
                        // high-contrast spiral/moire pattern on mobile.
                        float broadRay = Mathf.Sin(angle * 8f) * 0.38f;
                        float fineRay = Mathf.Sin(angle * 24f) * 0.08f;
                        float grain = (Hash01(x, y) - 0.5f) * 0.16f;
                        pattern = broadRay + fineRay + grain;
                    }
                    else
                    {
                        uint hash = (uint)(x * 374761393 + y * 668265263);
                        hash = (hash ^ (hash >> 13)) * 1274126177u;
                        pattern = ((hash & 1023u) / 1023f) - 0.5f;
                    }

                    float baseValue = radial ? 224f : 232f;
                    float amplitude = radial ? 18f : 4f;
                    byte value = (byte)Mathf.Clamp(
                        baseValue + pattern * amplitude,
                        0f,
                        255f);
                    pixels[y * texture.width + x] = new Color32(value, value, value, 255);
                }
            }

            texture.SetPixels32(pixels);
            texture.Apply(true, false);
            EditorUtility.SetDirty(texture);
            return texture;
        }

        private static Texture2D CreateOrUpdateNormalTexture(string path, bool radial)
        {
            Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (texture == null)
            {
                texture = new Texture2D(256, 256, TextureFormat.RGBA32, true, true)
                {
                    name = System.IO.Path.GetFileNameWithoutExtension(path),
                    wrapMode = TextureWrapMode.Repeat,
                    filterMode = FilterMode.Trilinear,
                    anisoLevel = 4
                };
                AssetDatabase.CreateAsset(texture, path);
            }

            Color32[] pixels = new Color32[texture.width * texture.height];
            for (int y = 0; y < texture.height; y++)
            {
                for (int x = 0; x < texture.width; x++)
                {
                    float u = (x + 0.5f) / texture.width - 0.5f;
                    float v = (y + 0.5f) / texture.height - 0.5f;
                    float nx;
                    float ny;
                    if (radial)
                    {
                        float angle = Mathf.Atan2(v, u);
                        float phase = Mathf.Sin(angle * 24f);
                        nx = -Mathf.Sin(angle) * phase * 0.018f;
                        ny = Mathf.Cos(angle) * phase * 0.018f;
                    }
                    else
                    {
                        float horizontal = Hash01(x, y) - Hash01(x + 1, y);
                        float vertical = Hash01(x, y) - Hash01(x, y + 1);
                        nx = horizontal * 0.07f;
                        ny = vertical * 0.07f;
                    }

                    Vector3 normal = new Vector3(nx, ny, 1f).normalized;
                    pixels[y * texture.width + x] = new Color32(
                        (byte)Mathf.RoundToInt((normal.x * 0.5f + 0.5f) * 255f),
                        (byte)Mathf.RoundToInt((normal.y * 0.5f + 0.5f) * 255f),
                        (byte)Mathf.RoundToInt((normal.z * 0.5f + 0.5f) * 255f),
                        255);
                }
            }

            texture.SetPixels32(pixels);
            texture.Apply(true, false);
            EditorUtility.SetDirty(texture);
            return texture;
        }

        private static Cubemap CreateOrUpdateStudioReflection(string path)
        {
            Cubemap cubemap = AssetDatabase.LoadAssetAtPath<Cubemap>(path);
            if (cubemap == null)
            {
                cubemap = new Cubemap(256, TextureFormat.RGBA32, true)
                {
                    name = System.IO.Path.GetFileNameWithoutExtension(path),
                    filterMode = FilterMode.Trilinear
                };
                AssetDatabase.CreateAsset(cubemap, path);
            }
            else if (cubemap.width != 256)
            {
                var replacement = new Cubemap(256, TextureFormat.RGBA32, true)
                {
                    name = cubemap.name,
                    filterMode = FilterMode.Trilinear
                };
                EditorUtility.CopySerialized(replacement, cubemap);
                UnityEngine.Object.DestroyImmediate(replacement);
                EditorUtility.SetDirty(cubemap);
            }

            foreach (CubemapFace face in new[]
                     {
                         CubemapFace.PositiveX,
                         CubemapFace.NegativeX,
                         CubemapFace.PositiveY,
                         CubemapFace.NegativeY,
                         CubemapFace.PositiveZ,
                         CubemapFace.NegativeZ
                     })
            {
                var pixels = new Color[cubemap.width * cubemap.width];
                for (int y = 0; y < cubemap.width; y++)
                {
                    for (int x = 0; x < cubemap.width; x++)
                    {
                        float u = (x + 0.5f) / cubemap.width * 2f - 1f;
                        float v = (y + 0.5f) / cubemap.width * 2f - 1f;
                        float strip = Mathf.Exp(-Mathf.Pow((v - 0.22f) / 0.16f, 2f));
                        float edge = Mathf.Exp(-Mathf.Pow((u + 0.55f) / 0.18f, 2f));
                        float baseLevel = face == CubemapFace.PositiveY ? 0.16f : 0.075f;
                        Color cool = new Color(0.55f, 0.66f, 0.78f) * strip * 0.28f;
                        Color warm = new Color(1.0f, 0.38f, 0.10f)
                            * edge
                            * (face == CubemapFace.PositiveX ? 0.24f : 0.05f);
                        pixels[y * cubemap.width + x] =
                            new Color(baseLevel, baseLevel * 1.05f, baseLevel * 1.12f)
                            + cool
                            + warm;
                    }
                }
                cubemap.SetPixels(pixels, face);
            }

            cubemap.Apply(true, false);
            EditorUtility.SetDirty(cubemap);
            return cubemap;
        }

        private static float Hash01(int x, int y)
        {
            uint hash = (uint)(x * 374761393 + y * 668265263);
            hash = (hash ^ (hash >> 13)) * 1274126177u;
            return (hash & 65535u) / 65535f;
        }

        private static void SetIfPresent(Material material, string property, Color value)
        {
            if (material.HasProperty(property))
            {
                material.SetColor(property, value);
            }
        }

        private static void SetIfPresent(Material material, string property, float value)
        {
            if (material.HasProperty(property))
            {
                material.SetFloat(property, value);
            }
        }

        private static void EnsureFolders()
        {
            EnsureFolder("Assets", "_Fidgeting");
            EnsureFolder("Assets/_Fidgeting", "Generated");
            EnsureFolder(GeneratedRoot, "Materials");
            EnsureFolder(GeneratedRoot, "Textures");
            EnsureFolder(GeneratedRoot, "Meshes");
            EnsureFolder("Assets/_Fidgeting", "Scenes");
        }

        private static void EnsureFolder(string parent, string name)
        {
            string path = parent + "/" + name;
            if (!AssetDatabase.IsValidFolder(path))
            {
                AssetDatabase.CreateFolder(parent, name);
            }
        }
    }
}
