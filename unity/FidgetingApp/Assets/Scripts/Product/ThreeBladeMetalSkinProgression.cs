using System;
using System.Collections.Generic;
using System.Globalization;
using UnityEngine;

namespace FidgetingApp.Product
{
    public enum ThreeBladeMetalPattern
    {
        MicroSand = 0,
        LinearBrush = 1,
        LuminousIndex = 2,
        Honeycomb = 3,
        Guilloche = 4,
        Damascus = 5,
        Circuit = 6,
        HeatTitanium = 7,
        Meteor = 8,
        MirrorAurora = 9
    }

    public readonly struct ThreeBladeMetalSkinDefinition
    {
        public ThreeBladeMetalSkinDefinition(
            string id,
            int level,
            string displayName,
            string metalName,
            string patternName,
            string decorationName,
            string modificationName,
            Color baseColor,
            Color accentColor,
            float metallic,
            float smoothness,
            ThreeBladeMetalPattern pattern,
            float emissionStrength)
        {
            Id = id;
            Level = Mathf.Clamp(level, 1, SpinnerProgressionRules.MaximumLevel);
            DisplayName = displayName;
            MetalName = metalName;
            PatternName = patternName;
            DecorationName = decorationName;
            ModificationName = modificationName;
            BaseColor = baseColor;
            AccentColor = accentColor;
            Metallic = Mathf.Clamp01(metallic);
            Smoothness = Mathf.Clamp01(smoothness);
            Pattern = pattern;
            EmissionStrength = Mathf.Max(0f, emissionStrength);
        }

        public string Id { get; }
        public int Level { get; }
        public string DisplayName { get; }
        public string MetalName { get; }
        public string PatternName { get; }
        public string DecorationName { get; }
        public string ModificationName { get; }
        public Color BaseColor { get; }
        public Color AccentColor { get; }
        public float Metallic { get; }
        public float Smoothness { get; }
        public ThreeBladeMetalPattern Pattern { get; }
        public float EmissionStrength { get; }
    }

    /// <summary>
    /// Product-owned skin catalog for the three-blade metal spinner. Every
    /// entry maps to an existing level band, so runtime visuals, native UI and
    /// tests consume one deterministic unlock source.
    /// </summary>
    public static class ThreeBladeMetalSkinCatalog
    {
        public const string ModelId = "metal-three-blade";
        public const string AutomaticSelectionId = "auto";

        private static readonly ThreeBladeMetalSkinDefinition[] skins =
        {
            new ThreeBladeMetalSkinDefinition(
                "factory-silver", 1, "原生雾银", "雾面航空铝", "微珠喷砂",
                "原厂抛光倒角", "标准单列轴承",
                Hex("AEB3B6"), Hex("E5E9EC"), 1f, 0.72f,
                ThreeBladeMetalPattern.MicroSand, 0f),
            new ThreeBladeMetalSkinDefinition(
                "gunmetal-brush", 5, "枪灰拉丝", "枪灰不锈钢", "纵向细拉丝",
                "黑铬边线", "磨合配平",
                Hex("4A5158"), Hex("AEB7BF"), 1f, 0.78f,
                ThreeBladeMetalPattern.LinearBrush, 0f),
            new ThreeBladeMetalSkinDefinition(
                "night-cyan-index", 10, "夜航刻度", "深海蓝钢", "十二段夜光刻度",
                "齐平青蓝蚀刻", "表面平衡刻线",
                Hex("142A36"), Hex("4FF5E7"), 0.96f, 0.82f,
                ThreeBladeMetalPattern.LuminousIndex, 1.35f),
            new ThreeBladeMetalSkinDefinition(
                "tungsten-honeycomb", 20, "钨金蜂巢", "钨黑 PVD × 香槟金", "微蚀刻蜂巢",
                "香槟金凹槽", "精钢配重环",
                Hex("17191B"), Hex("D7A84B"), 1f, 0.76f,
                ThreeBladeMetalPattern.Honeycomb, 0.08f),
            new ThreeBladeMetalSkinDefinition(
                "ice-guilloche", 35, "冰银回纹", "冷银镍铬", "机刻交错回纹",
                "冰蓝抛光边", "静音缓冲垫圈",
                Hex("A9B6BE"), Hex("8DE9FF"), 1f, 0.88f,
                ThreeBladeMetalPattern.Guilloche, 0.18f),
            new ThreeBladeMetalSkinDefinition(
                "blue-damascus", 50, "蓝钢水波", "回火蓝钢", "大马士革水波纹",
                "银蓝刃线", "双列辅助轴承",
                Hex("203E5A"), Hex("A9D8EE"), 1f, 0.84f,
                ThreeBladeMetalPattern.Damascus, 0.10f),
            new ThreeBladeMetalSkinDefinition(
                "copper-circuit", 65, "赤铜回路", "烟熏铜合金", "精密电路蚀刻",
                "齐平赤铜节点", "蓝钢冠环表面",
                Hex("5E3027"), Hex("F0A65B"), 0.94f, 0.74f,
                ThreeBladeMetalPattern.Circuit, 0.20f),
            new ThreeBladeMetalSkinDefinition(
                "titanium-heat", 75, "钛虹热变", "阳极氧化钛", "热变虹彩渐层",
                "紫金倒角", "低阻保持架",
                Hex("445A73"), Hex("D966FF"), 0.98f, 0.88f,
                ThreeBladeMetalPattern.HeatTitanium, 0.12f),
            new ThreeBladeMetalSkinDefinition(
                "meteor-obsidian", 90, "星陨黑曜", "黑曜 DLC", "陨石颗粒与银屑",
                "齐平典藏铭纹", "黑曜凹槽处理",
                Hex("101215"), Hex("C7D0D8"), 1f, 0.67f,
                ThreeBladeMetalPattern.Meteor, 0.10f),
            new ThreeBladeMetalSkinDefinition(
                "mirror-aurora", 100, "镜铬极光", "镜面精钢", "极光镜切纹",
                "陶瓷白冠环", "陶瓷主轴承 + 镜钢完成体",
                Hex("DDE4EA"), Hex("9BF4FF"), 1f, 0.97f,
                ThreeBladeMetalPattern.MirrorAurora, 0.22f)
        };

        public static IReadOnlyList<ThreeBladeMetalSkinDefinition> Skins => skins;

        public static ThreeBladeMetalSkinDefinition HighestUnlocked(int level)
        {
            ThreeBladeMetalSkinDefinition resolved = skins[0];
            for (int index = 1; index < skins.Length; index++)
            {
                if (skins[index].Level > level)
                {
                    break;
                }

                resolved = skins[index];
            }

            return resolved;
        }

        public static ThreeBladeMetalSkinDefinition Resolve(
            string requestedId,
            int level)
        {
            if (string.IsNullOrEmpty(requestedId)
                || requestedId == AutomaticSelectionId)
            {
                return HighestUnlocked(level);
            }

            for (int index = 0; index < skins.Length; index++)
            {
                if (skins[index].Id == requestedId && skins[index].Level <= level)
                {
                    return skins[index];
                }
            }

            return HighestUnlocked(level);
        }

        public static bool IsUnlocked(string skinId, int level)
        {
            for (int index = 0; index < skins.Length; index++)
            {
                if (skins[index].Id == skinId)
                {
                    return skins[index].Level <= level;
                }
            }

            return false;
        }

        public static string CatalogPayload()
        {
            var rows = new string[skins.Length];
            for (int index = 0; index < skins.Length; index++)
            {
                ThreeBladeMetalSkinDefinition skin = skins[index];
                rows[index] = string.Join(
                    "\t",
                    skin.Id,
                    skin.Level.ToString(CultureInfo.InvariantCulture),
                    skin.DisplayName,
                    skin.MetalName,
                    skin.PatternName,
                    skin.DecorationName,
                    skin.ModificationName,
                    ColorUtility.ToHtmlStringRGB(skin.BaseColor),
                    ColorUtility.ToHtmlStringRGB(skin.AccentColor));
            }

            return string.Join("\n", rows);
        }

        private static Color Hex(string value)
        {
            return ColorUtility.TryParseHtmlString("#" + value, out Color color)
                ? color
                : Color.white;
        }
    }

    /// <summary>
    /// Presentation-only skin renderer for the canonical three-blade model.
    /// It skins the enabled, physically authored product surfaces in place and
    /// never creates geometry above the model. It never touches Rigidbody,
    /// colliders, angular velocity, detent rules, input or Haptics.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class ThreeBladeMetalSkinProgression : MonoBehaviour
    {
        public const string DecorationRootName = "MetalSkinDecorations";
        public const string IndexMarkerName = "Lv10_LuminousIndexMarkers";
        public const string WeightPlugName = "Lv65_CollectorWeightPlugs";

        private const int TextureSize = 256;

        private readonly Dictionary<string, SkinResources> resources =
            new Dictionary<string, SkinResources>(StringComparer.Ordinal);
        private readonly List<SurfaceBinding> surfaceBindings =
            new List<SurfaceBinding>();

        private Renderer primaryBodyRenderer;
        private bool initialized;
        private int activeLevel = 1;
        private ThreeBladeMetalSkinDefinition activeSkin;

        public string ActiveSkinId => activeSkin.Id ?? string.Empty;
        public string ActiveSkinName => activeSkin.DisplayName ?? string.Empty;
        public int ActiveSkinLevel => activeSkin.Level;
        public int ActiveLevel => activeLevel;
        public bool IndexMarkersVisible => false;
        public bool WeightPlugsVisible => false;
        public int GeneratedColliderCount => 0;
        public int AppliedRendererCount => surfaceBindings.Count;
        public string FrameBodyMaterialName => primaryBodyRenderer != null
            && primaryBodyRenderer.sharedMaterials.Length > 0
            && primaryBodyRenderer.sharedMaterials[0] != null
                ? primaryBodyRenderer.sharedMaterials[0].name
                : string.Empty;
        public bool HasAppliedSkin => ValidateAppliedSkin();

        public void Apply(int level, string requestedSkinId)
        {
            EnsureInitialized();
            activeLevel = Mathf.Clamp(level, 1, SpinnerProgressionRules.MaximumLevel);
            activeSkin = ThreeBladeMetalSkinCatalog.Resolve(requestedSkinId, activeLevel);
            SkinResources skinResources = GetOrCreateResources(activeSkin);

            for (int index = 0; index < surfaceBindings.Count; index++)
            {
                surfaceBindings[index].Apply(skinResources);
            }
        }

        private void EnsureInitialized()
        {
            if (initialized)
            {
                return;
            }

            initialized = true;
            Transform productRoot = transform.parent;
            Transform hub = productRoot != null ? productRoot.Find("HubStatic") : null;
            Transform bearing = productRoot != null
                ? productRoot.Find("BearingVisual")
                : null;

            CaptureEnabledSurfaces(transform);
            CaptureEnabledSurfaces(hub);
            CaptureEnabledSurfaces(bearing);
        }

        private SkinResources GetOrCreateResources(ThreeBladeMetalSkinDefinition skin)
        {
            if (resources.TryGetValue(skin.Id, out SkinResources cached))
            {
                return cached;
            }

            Texture2D baseMap = GenerateBaseMap(skin);
            Texture2D normalMap = GenerateNormalMap(skin);
            Material body = CreateMaterial(
                $"MetalSkin_{skin.Level:000}_{skin.Id}_Body",
                Color.white,
                skin.Metallic,
                skin.Smoothness,
                baseMap,
                normalMap,
                0.22f,
                Color.black);
            Material accent = CreateMaterial(
                $"MetalSkin_{skin.Level:000}_{skin.Id}_Accent",
                skin.AccentColor,
                Mathf.Max(0.72f, skin.Metallic),
                Mathf.Min(1f, skin.Smoothness + 0.06f),
                null,
                null,
                0f,
                skin.AccentColor * skin.EmissionStrength);
            Color insetColor = Color.Lerp(skin.BaseColor, Color.black, 0.58f);
            Material inset = CreateMaterial(
                $"MetalSkin_{skin.Level:000}_{skin.Id}_Inset",
                insetColor,
                Mathf.Max(0.72f, skin.Metallic),
                Mathf.Max(0.42f, skin.Smoothness - 0.18f),
                null,
                null,
                0f,
                Color.black);

            cached = new SkinResources(baseMap, normalMap, body, accent, inset);
            resources.Add(skin.Id, cached);
            return cached;
        }

        private static Material CreateMaterial(
            string materialName,
            Color color,
            float metallic,
            float smoothness,
            Texture2D baseMap,
            Texture2D normalMap,
            float normalStrength,
            Color emission)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Lit")
                ?? Shader.Find("Standard");
            Material material = new Material(shader)
            {
                name = materialName,
                enableInstancing = true,
                hideFlags = HideFlags.HideAndDontSave
            };
            SetColor(material, "_BaseColor", color);
            SetColor(material, "_Color", color);
            SetFloat(material, "_Metallic", metallic);
            SetFloat(material, "_Smoothness", smoothness);
            SetFloat(material, "_Glossiness", smoothness);
            SetTexture(material, "_BaseMap", baseMap);
            SetTexture(material, "_MainTex", baseMap);
            SetTexture(material, "_BumpMap", normalMap);
            SetFloat(material, "_BumpScale", normalStrength);
            if (normalMap != null)
            {
                material.EnableKeyword("_NORMALMAP");
            }
            if (emission.maxColorComponent > 0f)
            {
                SetColor(material, "_EmissionColor", emission);
                material.EnableKeyword("_EMISSION");
            }
            return material;
        }

        private static Texture2D GenerateBaseMap(ThreeBladeMetalSkinDefinition skin)
        {
            var texture = new Texture2D(
                TextureSize,
                TextureSize,
                TextureFormat.RGBA32,
                true,
                false)
            {
                name = $"MetalSkin_{skin.Level:000}_{skin.Id}_BaseMap",
                wrapMode = TextureWrapMode.Repeat,
                filterMode = FilterMode.Trilinear,
                anisoLevel = 4,
                hideFlags = HideFlags.HideAndDontSave
            };
            var pixels = new Color32[TextureSize * TextureSize];
            for (int y = 0; y < TextureSize; y++)
            {
                for (int x = 0; x < TextureSize; x++)
                {
                    float u = (x + 0.5f) / TextureSize;
                    float v = (y + 0.5f) / TextureSize;
                    EvaluatePattern(skin.Pattern, u, v, x, y, out float height, out float accent);
                    float brightness = Mathf.Lerp(0.72f, 1.12f, height);
                    Color baseColor = skin.BaseColor * brightness;
                    Color accentColor = skin.AccentColor * Mathf.Lerp(0.82f, 1.18f, height);
                    Color output = Color.Lerp(baseColor, accentColor, accent);
                    output.a = 1f;
                    pixels[y * TextureSize + x] = output;
                }
            }
            texture.SetPixels32(pixels);
            texture.Apply(true, false);
            return texture;
        }

        private static Texture2D GenerateNormalMap(ThreeBladeMetalSkinDefinition skin)
        {
            var texture = new Texture2D(
                TextureSize,
                TextureSize,
                TextureFormat.RGBA32,
                true,
                true)
            {
                name = $"MetalSkin_{skin.Level:000}_{skin.Id}_NormalMap",
                wrapMode = TextureWrapMode.Repeat,
                filterMode = FilterMode.Trilinear,
                anisoLevel = 4,
                hideFlags = HideFlags.HideAndDontSave
            };
            var heights = new float[TextureSize * TextureSize];
            for (int y = 0; y < TextureSize; y++)
            {
                for (int x = 0; x < TextureSize; x++)
                {
                    EvaluatePattern(
                        skin.Pattern,
                        (x + 0.5f) / TextureSize,
                        (y + 0.5f) / TextureSize,
                        x,
                        y,
                        out float height,
                        out float accent);
                    heights[y * TextureSize + x] = height + accent * 0.35f;
                }
            }

            var pixels = new Color32[TextureSize * TextureSize];
            for (int y = 0; y < TextureSize; y++)
            {
                for (int x = 0; x < TextureSize; x++)
                {
                    int left = y * TextureSize + (x + TextureSize - 1) % TextureSize;
                    int right = y * TextureSize + (x + 1) % TextureSize;
                    int down = ((y + TextureSize - 1) % TextureSize) * TextureSize + x;
                    int up = ((y + 1) % TextureSize) * TextureSize + x;
                    float nx = (heights[left] - heights[right]) * 0.72f;
                    float ny = (heights[down] - heights[up]) * 0.72f;
                    Vector3 normal = new Vector3(nx, ny, 1f).normalized;
                    pixels[y * TextureSize + x] = new Color32(
                        (byte)Mathf.RoundToInt((normal.x * 0.5f + 0.5f) * 255f),
                        (byte)Mathf.RoundToInt((normal.y * 0.5f + 0.5f) * 255f),
                        (byte)Mathf.RoundToInt((normal.z * 0.5f + 0.5f) * 255f),
                        255);
                }
            }
            texture.SetPixels32(pixels);
            texture.Apply(true, false);
            return texture;
        }

        private static void EvaluatePattern(
            ThreeBladeMetalPattern pattern,
            float u,
            float v,
            int x,
            int y,
            out float height,
            out float accent)
        {
            float noise = Hash01(x, y) - 0.5f;
            height = 0.5f + noise * 0.12f;
            accent = 0f;
            switch (pattern)
            {
                case ThreeBladeMetalPattern.MicroSand:
                    height = 0.5f + noise * 0.22f;
                    break;
                case ThreeBladeMetalPattern.LinearBrush:
                    height = 0.5f
                        + Mathf.Sin(u * Mathf.PI * 180f) * 0.08f
                        + noise * 0.08f;
                    break;
                case ThreeBladeMetalPattern.LuminousIndex:
                    height = 0.48f + Mathf.Sin(u * Mathf.PI * 96f) * 0.04f;
                    accent = PeriodicLine(u, 12f, 0.035f)
                        * StepRange(v, 0.18f, 0.82f)
                        * 0.18f;
                    break;
                case ThreeBladeMetalPattern.Honeycomb:
                {
                    float a = PeriodicLine(u + v * 0.58f, 8f, 0.08f);
                    float b = PeriodicLine(u - v * 0.58f, 8f, 0.08f);
                    float c = PeriodicLine(v, 9.2f, 0.08f);
                    accent = Mathf.Clamp01(
                        Mathf.Max(a * b, Mathf.Max(a * c, b * c))) * 0.28f;
                    height = 0.44f + accent * 0.30f + noise * 0.05f;
                    break;
                }
                case ThreeBladeMetalPattern.Guilloche:
                {
                    float waveA = Mathf.Abs(Mathf.Sin((v + Mathf.Sin(u * 12f) * 0.08f) * 44f));
                    float waveB = Mathf.Abs(Mathf.Sin((v - Mathf.Sin(u * 12f) * 0.08f) * 44f));
                    accent = Mathf.Pow(1f - Mathf.Min(waveA, waveB), 5f);
                    height = 0.50f + accent * 0.24f + noise * 0.04f;
                    break;
                }
                case ThreeBladeMetalPattern.Damascus:
                {
                    float phase = v * 42f
                        + Mathf.Sin(u * 11f) * 2.8f
                        + Mathf.Sin((u + v) * 19f) * 0.8f;
                    float ribbon = 0.5f + 0.5f * Mathf.Sin(phase);
                    accent = Mathf.Pow(ribbon, 6f) * 0.62f;
                    height = 0.30f + ribbon * 0.46f;
                    break;
                }
                case ThreeBladeMetalPattern.Circuit:
                {
                    float horizontal = PeriodicLine(v, 10f, 0.055f)
                        * StepRange(Repeat01(u * 4f), 0.08f, 0.72f);
                    float vertical = PeriodicLine(u, 8f, 0.055f)
                        * StepRange(Repeat01(v * 5f), 0.28f, 0.90f);
                    float node = CircleMask(Repeat01(u * 8f), Repeat01(v * 10f), 0.13f);
                    accent = Mathf.Clamp01(Mathf.Max(Mathf.Max(horizontal, vertical), node));
                    height = 0.42f + accent * 0.30f + noise * 0.04f;
                    break;
                }
                case ThreeBladeMetalPattern.HeatTitanium:
                    height = 0.44f
                        + 0.25f * Mathf.Sin((u + v) * Mathf.PI * 3f)
                        + noise * 0.05f;
                    accent = Mathf.Clamp01(0.5f + 0.5f * Mathf.Sin((u * 0.8f + v) * Mathf.PI * 4f));
                    break;
                case ThreeBladeMetalPattern.Meteor:
                {
                    float fleck = Hash01(x / 3, y / 3);
                    accent = fleck > 0.965f ? Mathf.InverseLerp(0.965f, 1f, fleck) : 0f;
                    float crater = Hash01(x / 12, y / 12);
                    height = 0.34f + noise * 0.14f - (crater > 0.90f ? 0.18f : 0f);
                    break;
                }
                case ThreeBladeMetalPattern.MirrorAurora:
                    height = 0.70f + Mathf.Sin((u - v) * Mathf.PI * 48f) * 0.035f;
                    accent = Mathf.Pow(0.5f + 0.5f * Mathf.Sin((u + v) * Mathf.PI * 5f), 7f) * 0.34f;
                    break;
            }

            height = Mathf.Clamp01(height);
            accent = Mathf.Clamp01(accent);
        }

        private static float PeriodicLine(float value, float frequency, float width)
        {
            float distance = Mathf.Abs(Repeat01(value * frequency) - 0.5f) * 2f;
            return 1f - Mathf.SmoothStep(width, width * 2.2f, distance);
        }

        private static float StepRange(float value, float minimum, float maximum)
        {
            return value >= minimum && value <= maximum ? 1f : 0f;
        }

        private static float CircleMask(float u, float v, float radius)
        {
            float distance = Vector2.Distance(new Vector2(u, v), new Vector2(0.5f, 0.5f));
            return 1f - Mathf.SmoothStep(radius, radius * 1.35f, distance);
        }

        private static float Repeat01(float value)
        {
            return value - Mathf.Floor(value);
        }

        private static float Hash01(int x, int y)
        {
            uint hash = (uint)(x * 374761393 + y * 668265263);
            hash = (hash ^ (hash >> 13)) * 1274126177u;
            return (hash & 65535u) / 65535f;
        }

        private void CaptureEnabledSurfaces(Transform root)
        {
            if (root == null)
            {
                return;
            }

            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            for (int rendererIndex = 0; rendererIndex < renderers.Length; rendererIndex++)
            {
                Renderer renderer = renderers[rendererIndex];
                if (renderer == null
                    || !renderer.enabled
                    || !renderer.gameObject.activeInHierarchy
                    || IsGeneratedOverlay(renderer.transform))
                {
                    continue;
                }

                Material[] originals = renderer.sharedMaterials;
                if (originals == null || originals.Length == 0)
                {
                    continue;
                }

                var roles = new SurfaceRole[originals.Length];
                bool containsBody = false;
                for (int materialIndex = 0; materialIndex < originals.Length; materialIndex++)
                {
                    roles[materialIndex] = ResolveSurfaceRole(
                        renderer.name,
                        originals[materialIndex]);
                    containsBody |= roles[materialIndex] == SurfaceRole.Body;
                }

                surfaceBindings.Add(new SurfaceBinding(renderer, originals, roles));
                if (primaryBodyRenderer == null && containsBody)
                {
                    primaryBodyRenderer = renderer;
                }
            }
        }

        private static bool IsGeneratedOverlay(Transform candidate)
        {
            Transform current = candidate;
            while (current != null)
            {
                string name = current.name;
                if (name == DecorationRootName
                    || name == FidgetAppCoordinator.LegacyProgressionRingRootName
                    || name == ProductStickerPresenter.StickerRootName)
                {
                    return true;
                }
                current = current.parent;
            }
            return false;
        }

        private static SurfaceRole ResolveSurfaceRole(
            string rendererName,
            Material original)
        {
            string materialName = original != null ? original.name : string.Empty;
            string token = (rendererName + " " + materialName).ToLowerInvariant();
            if (token.Contains("pocketfloor")
                || token.Contains("recess")
                || token.Contains("black_pom")
                || token.Contains("darkring")
                || token.Contains("inset"))
            {
                return SurfaceRole.Inset;
            }

            if (token.Contains("polished")
                || token.Contains("bevel")
                || token.Contains("bearing")
                || token.Contains("accent")
                || token.Contains("crowntrim")
                || token.Contains("inlay")
                || token.Contains("washer")
                || token.Contains("axle"))
            {
                return SurfaceRole.Accent;
            }

            return SurfaceRole.Body;
        }

        private bool ValidateAppliedSkin()
        {
            if (string.IsNullOrEmpty(ActiveSkinId) || surfaceBindings.Count == 0)
            {
                return false;
            }

            for (int bindingIndex = 0; bindingIndex < surfaceBindings.Count; bindingIndex++)
            {
                if (!surfaceBindings[bindingIndex].UsesSkin(ActiveSkinId))
                {
                    return false;
                }
            }
            return true;
        }

        private static void SetColor(Material material, string property, Color value)
        {
            if (material.HasProperty(property))
            {
                material.SetColor(property, value);
            }
        }

        private static void SetFloat(Material material, string property, float value)
        {
            if (material.HasProperty(property))
            {
                material.SetFloat(property, value);
            }
        }

        private static void SetTexture(Material material, string property, Texture value)
        {
            if (material.HasProperty(property))
            {
                material.SetTexture(property, value);
            }
        }

        private void OnDestroy()
        {
            for (int index = 0; index < surfaceBindings.Count; index++)
            {
                surfaceBindings[index].Restore();
            }

            foreach (SkinResources skinResources in resources.Values)
            {
                Release(skinResources.Body);
                Release(skinResources.Accent);
                Release(skinResources.Inset);
                Release(skinResources.BaseMap);
                Release(skinResources.NormalMap);
            }
        }

        private static void Release(UnityEngine.Object target)
        {
            if (target == null)
            {
                return;
            }
#if UNITY_EDITOR
            if (!Application.isPlaying)
            {
                UnityEngine.Object.DestroyImmediate(target);
                return;
            }
#endif
            UnityEngine.Object.Destroy(target);
        }

        private enum SurfaceRole
        {
            Body = 0,
            Accent = 1,
            Inset = 2
        }

        private sealed class SurfaceBinding
        {
            private readonly Renderer renderer;
            private readonly Material[] originals;
            private readonly SurfaceRole[] roles;

            public SurfaceBinding(
                Renderer renderer,
                Material[] originals,
                SurfaceRole[] roles)
            {
                this.renderer = renderer;
                this.originals = (Material[])originals.Clone();
                this.roles = roles;
            }

            public void Apply(SkinResources resources)
            {
                if (renderer == null)
                {
                    return;
                }

                var replacements = new Material[roles.Length];
                for (int index = 0; index < roles.Length; index++)
                {
                    replacements[index] = roles[index] switch
                    {
                        SurfaceRole.Accent => resources.Accent,
                        SurfaceRole.Inset => resources.Inset,
                        _ => resources.Body
                    };
                }
                renderer.sharedMaterials = replacements;
            }

            public bool UsesSkin(string skinId)
            {
                if (renderer == null)
                {
                    return false;
                }

                Material[] current = renderer.sharedMaterials;
                if (current.Length != roles.Length)
                {
                    return false;
                }

                for (int index = 0; index < current.Length; index++)
                {
                    Material material = current[index];
                    if (material == null
                        || material.name.IndexOf(
                            skinId,
                            StringComparison.Ordinal) < 0)
                    {
                        return false;
                    }
                }
                return true;
            }

            public void Restore()
            {
                if (renderer != null)
                {
                    renderer.sharedMaterials = originals;
                }
            }
        }

        private readonly struct SkinResources
        {
            public SkinResources(
                Texture2D baseMap,
                Texture2D normalMap,
                Material body,
                Material accent,
                Material inset)
            {
                BaseMap = baseMap;
                NormalMap = normalMap;
                Body = body;
                Accent = accent;
                Inset = inset;
            }

            public Texture2D BaseMap { get; }
            public Texture2D NormalMap { get; }
            public Material Body { get; }
            public Material Accent { get; }
            public Material Inset { get; }
        }
    }
}
