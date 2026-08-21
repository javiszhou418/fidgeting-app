using System;
using System.Collections.Generic;
using FidgetingApp.DisplayCase;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.Product.Gacha
{
    public enum GachaPrizePresentationKind
    {
        SlateLining = 0,
        StrataSticker = 1,
        DustSticker = 2,
        BasaltBase = 3,
        BlueSteelSkin = 4,
        RidgeDuskTint = 5,
        CopperStrataSkin = 6,
        AuroraVeinSkin = 7
    }

    public readonly struct GachaPrizePresentationDescriptor
    {
        public GachaPrizePresentationDescriptor(
            string contentReference,
            string displayName,
            GachaPrizePresentationKind kind,
            bool usesThreeBladeDisplayModel,
            bool isPhysicalArtwork)
        {
            ContentReference = contentReference ?? string.Empty;
            DisplayName = displayName ?? string.Empty;
            Kind = kind;
            UsesThreeBladeDisplayModel = usesThreeBladeDisplayModel;
            IsPhysicalArtwork = isPhysicalArtwork;
        }

        public string ContentReference { get; }
        public string DisplayName { get; }
        public GachaPrizePresentationKind Kind { get; }
        public bool UsesThreeBladeDisplayModel { get; }
        public bool IsPhysicalArtwork { get; }
        public PremiumDisplayCaseCapsulePreset CapsulePreset =>
            GachaRevealRules.SharedCapsulePreset;
        public PremiumDisplayCaseContentOptions ContentOptions =>
            GachaPrizePresentationResolver.SharedContentOptions;
    }

    /// <summary>
    /// One resolver-owned, renderer-only prize. Dispose destroys only the
    /// generated presentation node and its runtime meshes/materials.
    /// </summary>
    public sealed class GachaResolvedPrizePresentation : IDisposable
    {
        private bool disposed;

        internal GachaResolvedPrizePresentation(
            GachaPrizePresentationDescriptor descriptor,
            GameObject root)
        {
            Descriptor = descriptor;
            Root = root;
        }

        public GachaPrizePresentationDescriptor Descriptor { get; }
        public GameObject Root { get; private set; }
        public Transform Transform => Root != null ? Root.transform : null;
        public Renderer[] Renderers => Root != null
            ? Root.GetComponentsInChildren<Renderer>(true)
            : Array.Empty<Renderer>();

        public void Dispose()
        {
            if (disposed)
            {
                return;
            }

            disposed = true;
            if (Root != null)
            {
                GachaPrizePresentationResolver.DestroyOwned(Root);
                Root = null;
            }
        }
    }

    /// <summary>
    /// Stable ContentReference -> real 3D presentation mapping for the launch
    /// pool. These are intentionally presentation-only nodes: no Collider,
    /// Rigidbody, AudioSource, input, Update loop or Haptic component enters
    /// the reveal hierarchy.
    /// </summary>
    public static class GachaPrizePresentationResolver
    {
        public static readonly PremiumDisplayCaseContentOptions
            SharedContentOptions = new PremiumDisplayCaseContentOptions(
                true,
                PremiumDisplayCaseProductProfiles.SharedContentOptions
                    .IdleRotationPeriodSeconds,
                PremiumDisplayCaseProductProfiles.SharedContentOptions
                    .InitialEulerAngles);

        private static readonly GachaPrizePresentationDescriptor[] descriptors =
        {
            Descriptor(
                "display-lining/slate",
                "板岩内衬",
                GachaPrizePresentationKind.SlateLining,
                false,
                false),
            Descriptor(
                "sticker/canyon-strata",
                "岩层纹贴纸",
                GachaPrizePresentationKind.StrataSticker,
                false,
                true),
            Descriptor(
                "sticker/canyon-dust",
                "矿尘贴纸",
                GachaPrizePresentationKind.DustSticker,
                false,
                true),
            Descriptor(
                "display-base/basalt",
                "玄武岩底座",
                GachaPrizePresentationKind.BasaltBase,
                false,
                false),
            Descriptor(
                "skin/pointed-three-blade/gacha-bluesteel-wash",
                "蓝钢冲刷",
                GachaPrizePresentationKind.BlueSteelSkin,
                true,
                false),
            Descriptor(
                "environment-tint/canyon-ridge-dusk",
                "岭线暮色",
                GachaPrizePresentationKind.RidgeDuskTint,
                false,
                false),
            Descriptor(
                "skin/pointed-three-blade/gacha-copper-strata",
                "铜层岩理",
                GachaPrizePresentationKind.CopperStrataSkin,
                true,
                false),
            Descriptor(
                "skin/pointed-three-blade/gacha-aurora-vein",
                "极光矿脉",
                GachaPrizePresentationKind.AuroraVeinSkin,
                true,
                false)
        };

        public static IReadOnlyList<GachaPrizePresentationDescriptor>
            Descriptors => descriptors;

        public static bool TryResolveDescriptor(
            string contentReference,
            out GachaPrizePresentationDescriptor descriptor)
        {
            string normalized = (contentReference ?? string.Empty).Trim();
            for (int index = 0; index < descriptors.Length; index++)
            {
                if (string.Equals(
                        descriptors[index].ContentReference,
                        normalized,
                        StringComparison.Ordinal))
                {
                    descriptor = descriptors[index];
                    return true;
                }
            }

            descriptor = default;
            return false;
        }

        public static bool TryResolve(
            GachaPrizeDefinition prize,
            Transform parent,
            out GachaResolvedPrizePresentation presentation,
            out string failureReason)
        {
            if (!TryResolveDescriptor(prize.ContentReference, out var descriptor))
            {
                presentation = null;
                failureReason = "unmapped-content-reference:" +
                    (prize.ContentReference ?? string.Empty);
                return false;
            }

            GameObject root = null;
            try
            {
                root = Build(descriptor, parent);
                ValidateRendererOnly(root);
                presentation = new GachaResolvedPrizePresentation(
                    descriptor,
                    root);
                failureReason = string.Empty;
                return true;
            }
            catch (Exception exception)
            {
                if (root != null)
                {
                    DestroyOwned(root);
                }
                presentation = null;
                failureReason = "prize-presentation-failed:" + exception.Message;
                return false;
            }
        }

        public static GachaResolvedPrizePresentation Resolve(
            GachaPrizeDefinition prize,
            Transform parent = null)
        {
            if (!TryResolve(prize, parent, out var presentation, out string reason))
            {
                throw new InvalidOperationException(reason);
            }

            return presentation;
        }

        public static bool IsRendererOnly(GameObject root)
        {
            return root != null
                && root.GetComponentsInChildren<Rigidbody>(true).Length == 0
                && root.GetComponentsInChildren<Collider>(true).Length == 0
                && root.GetComponentsInChildren<AudioSource>(true).Length == 0
                && root.GetComponentsInChildren<ParticleSystem>(true).Length == 0;
        }

        internal static void DestroyOwned(UnityEngine.Object target)
        {
            if (target == null)
            {
                return;
            }

            if (Application.isPlaying)
            {
                UnityEngine.Object.Destroy(target);
            }
            else
            {
                UnityEngine.Object.DestroyImmediate(target);
            }
        }

        private static GachaPrizePresentationDescriptor Descriptor(
            string contentReference,
            string displayName,
            GachaPrizePresentationKind kind,
            bool usesThreeBlade,
            bool artwork)
        {
            return new GachaPrizePresentationDescriptor(
                contentReference,
                displayName,
                kind,
                usesThreeBlade,
                artwork);
        }

        private static GameObject Build(
            GachaPrizePresentationDescriptor descriptor,
            Transform parent)
        {
            GameObject root;
            switch (descriptor.Kind)
            {
                case GachaPrizePresentationKind.BlueSteelSkin:
                case GachaPrizePresentationKind.CopperStrataSkin:
                case GachaPrizePresentationKind.AuroraVeinSkin:
                    root = BuildThreeBladeSkin(descriptor);
                    break;
                case GachaPrizePresentationKind.StrataSticker:
                    root = BuildSticker(descriptor, true);
                    break;
                case GachaPrizePresentationKind.DustSticker:
                    root = BuildSticker(descriptor, false);
                    break;
                case GachaPrizePresentationKind.SlateLining:
                    root = BuildSlateLining(descriptor);
                    break;
                case GachaPrizePresentationKind.BasaltBase:
                    root = BuildBasaltBase(descriptor);
                    break;
                case GachaPrizePresentationKind.RidgeDuskTint:
                    root = BuildRidgeDusk(descriptor);
                    break;
                default:
                    throw new ArgumentOutOfRangeException();
            }

            root.name = "GachaPrize_" + descriptor.Kind;
            root.transform.SetParent(parent, false);
            root.transform.localPosition = Vector3.zero;
            root.transform.localRotation = Quaternion.identity;
            root.transform.localScale = Vector3.one;
            return root;
        }

        private static GameObject BuildThreeBladeSkin(
            GachaPrizePresentationDescriptor descriptor)
        {
            GameObject root = ThreeBladeDisplayPrizeFactory.Instantiate();
            GachaPrizeRuntimeResourceOwner owner =
                root.GetComponent<GachaPrizeRuntimeResourceOwner>()
                ?? root.AddComponent<GachaPrizeRuntimeResourceOwner>();
            Color primary;
            Color secondary;
            Color pattern;
            switch (descriptor.Kind)
            {
                case GachaPrizePresentationKind.CopperStrataSkin:
                    primary = new Color(0.50f, 0.13f, 0.035f, 1f);
                    secondary = new Color(0.96f, 0.42f, 0.09f, 1f);
                    pattern = new Color(1.00f, 0.73f, 0.24f, 1f);
                    break;
                case GachaPrizePresentationKind.AuroraVeinSkin:
                    primary = new Color(0.15f, 0.035f, 0.36f, 1f);
                    secondary = new Color(0.05f, 0.78f, 0.68f, 1f);
                    pattern = new Color(0.93f, 0.19f, 0.94f, 1f);
                    break;
                default:
                    primary = new Color(0.035f, 0.16f, 0.31f, 1f);
                    secondary = new Color(0.50f, 0.75f, 0.91f, 1f);
                    pattern = new Color(0.76f, 0.90f, 0.98f, 1f);
                    break;
            }

            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            var properties = new MaterialPropertyBlock();
            for (int index = 0; index < renderers.Length; index++)
            {
                Renderer renderer = renderers[index];
                if (renderer == null)
                {
                    continue;
                }

                bool usesSecondary = IsThreeBladeAccentRenderer(renderer.name);
                Color tint = usesSecondary ? secondary : primary;
                renderer.GetPropertyBlock(properties);
                properties.SetColor("_BaseColor", tint);
                properties.SetColor("_Color", tint);
                properties.SetFloat("_Metallic", usesSecondary ? 0.78f : 0.94f);
                properties.SetFloat("_Smoothness", usesSecondary ? 0.66f : 0.82f);
                renderer.SetPropertyBlock(properties);
                renderer.shadowCastingMode = ShadowCastingMode.On;
                renderer.receiveShadows = true;
            }

            AddThreeBladeSkinPattern(
                root.transform,
                owner,
                descriptor.Kind,
                pattern);
            return root;
        }

        private static bool IsThreeBladeAccentRenderer(string rendererName)
        {
            string name = rendererName ?? string.Empty;
            return name.IndexOf("Inset", StringComparison.Ordinal) >= 0
                || name.IndexOf("Trim", StringComparison.Ordinal) >= 0
                || name.IndexOf("Washer", StringComparison.Ordinal) >= 0
                || name.IndexOf("Bearing", StringComparison.Ordinal) >= 0;
        }

        private static void AddThreeBladeSkinPattern(
            Transform root,
            GachaPrizeRuntimeResourceOwner owner,
            GachaPrizePresentationKind kind,
            Color patternColor)
        {
            Mesh box = owner.Own(CreateBoxMesh());
            Material pattern = owner.Own(CreateLitMaterial(
                kind + "Pattern",
                patternColor,
                kind == GachaPrizePresentationKind.AuroraVeinSkin
                    ? 0.28f
                    : 0.88f,
                0.72f));
            if (kind == GachaPrizePresentationKind.AuroraVeinSkin)
            {
                SetEmission(pattern, patternColor * 1.65f);
            }

            Material alternate = pattern;
            if (kind == GachaPrizePresentationKind.AuroraVeinSkin)
            {
                Color cyan = new Color(0.04f, 0.92f, 0.88f, 1f);
                alternate = owner.Own(CreateLitMaterial(
                    "AuroraVeinCyan",
                    cyan,
                    0.20f,
                    0.76f));
                SetEmission(alternate, cyan * 1.75f);
            }

            int stripeCount = kind == GachaPrizePresentationKind.CopperStrataSkin
                ? 4
                : 3;
            float width = kind == GachaPrizePresentationKind.AuroraVeinSkin
                ? 0.0085f
                : 0.0105f;
            for (int blade = 0; blade < 3; blade++)
            {
                float angle = 30f + blade * 120f;
                float radians = angle * Mathf.Deg2Rad;
                Vector3 radial = new Vector3(
                    Mathf.Cos(radians),
                    0f,
                    Mathf.Sin(radians));
                for (int stripe = 0; stripe < stripeCount; stripe++)
                {
                    float sideStep = stripe - (stripeCount - 1) * 0.5f;
                    Transform rail = AddMesh(
                        root,
                        $"{kind}SurfacePattern_{blade}_{stripe}",
                        box,
                        stripe % 2 == 0 ? pattern : alternate).transform;
                    rail.localPosition = radial * (0.022f + sideStep * 0.0024f)
                        + Vector3.down * 0.00615f;
                    rail.localRotation = Quaternion.Euler(
                        0f,
                        -angle + (kind == GachaPrizePresentationKind.AuroraVeinSkin
                            ? sideStep * 13f
                            : 0f),
                        0f);
                    rail.localScale = new Vector3(
                        width - Mathf.Abs(sideStep) * 0.0007f,
                        0.00032f,
                        kind == GachaPrizePresentationKind.CopperStrataSkin
                            ? 0.00072f
                            : 0.00052f);
                }

                if (kind == GachaPrizePresentationKind.AuroraVeinSkin)
                {
                    Transform branch = AddMesh(
                        root,
                        $"AuroraVeinBranch_{blade}",
                        box,
                        blade % 2 == 0 ? alternate : pattern).transform;
                    branch.localPosition = radial * 0.024f
                        + Vector3.down * 0.00618f;
                    branch.localRotation = Quaternion.Euler(
                        0f,
                        -angle + 44f,
                        0f);
                    branch.localScale = new Vector3(
                        0.0065f,
                        0.00034f,
                        0.00050f);
                }
            }
        }

        private static GameObject BuildSticker(
            GachaPrizePresentationDescriptor descriptor,
            bool strata)
        {
            var root = NewRuntimeRoot(descriptor.Kind.ToString());
            GachaPrizeRuntimeResourceOwner owner =
                root.GetComponent<GachaPrizeRuntimeResourceOwner>();
            Mesh slab = owner.Own(CreateRoundedSlabMesh(
                0.066f,
                0.066f,
                0.0024f,
                0.007f,
                5));
            Material card = owner.Own(CreateLitMaterial(
                "StickerCard",
                new Color(0.055f, 0.058f, 0.060f, 1f),
                0.45f,
                0.62f));
            AddMesh(root.transform, "PhysicalStickerCard", slab, card);

            Material ink = owner.Own(CreateLitMaterial(
                strata ? "StrataCopperInk" : "MineralDustInk",
                strata
                    ? new Color(0.78f, 0.40f, 0.16f, 1f)
                    : new Color(0.72f, 0.69f, 0.58f, 1f),
                0.70f,
                0.72f));
            Mesh box = owner.Own(CreateBoxMesh());
            if (strata)
            {
                for (int index = 0; index < 9; index++)
                {
                    float z = -0.024f + index * 0.006f;
                    float width = 0.045f - Mathf.Abs(index - 4) * 0.003f;
                    Transform stroke = AddMesh(
                        root.transform,
                        $"StrataArtwork_{index:00}",
                        box,
                        ink).transform;
                    stroke.localPosition = new Vector3(
                        (index - 4) * 0.0015f,
                        -0.00145f,
                        z);
                    stroke.localRotation = Quaternion.Euler(0f, 17f, 0f);
                    stroke.localScale = new Vector3(width, 0.00028f, 0.0014f);
                }
            }
            else
            {
                uint state = 0xC0DEC0DEu;
                for (int index = 0; index < 28; index++)
                {
                    float x = NextSigned(ref state) * 0.025f;
                    float z = NextSigned(ref state) * 0.025f;
                    float size = 0.0008f + Next01(ref state) * 0.0018f;
                    Transform fleck = AddMesh(
                        root.transform,
                        $"MineralDustArtwork_{index:00}",
                        box,
                        ink).transform;
                    fleck.localPosition = new Vector3(x, -0.00145f, z);
                    fleck.localRotation = Quaternion.Euler(
                        0f,
                        Next01(ref state) * 180f,
                        0f);
                    fleck.localScale = new Vector3(
                        size * 1.8f,
                        0.00032f,
                        size);
                }
            }

            return root;
        }

        private static GameObject BuildSlateLining(
            GachaPrizePresentationDescriptor descriptor)
        {
            var root = NewRuntimeRoot(descriptor.Kind.ToString());
            GachaPrizeRuntimeResourceOwner owner =
                root.GetComponent<GachaPrizeRuntimeResourceOwner>();
            Mesh slab = owner.Own(CreateRoundedSlabMesh(
                0.068f,
                0.060f,
                0.008f,
                0.006f,
                5));
            Mesh box = owner.Own(CreateBoxMesh());
            Material slate = owner.Own(CreateLitMaterial(
                "SlateLining",
                new Color(0.14f, 0.17f, 0.20f, 1f),
                0.10f,
                0.24f));
            Material slateFace = owner.Own(CreateLitMaterial(
                "SlateCutFace",
                new Color(0.22f, 0.26f, 0.29f, 1f),
                0.12f,
                0.30f));
            Material seam = owner.Own(CreateLitMaterial(
                "SlateGrain",
                new Color(0.52f, 0.58f, 0.61f, 1f),
                0.18f,
                0.38f));
            AddMesh(root.transform, "SlateMaterialSample", slab, slate);
            Mesh face = owner.Own(CreateRoundedSlabMesh(
                0.062f,
                0.054f,
                0.0008f,
                0.005f,
                5));
            Transform cutFace = AddMesh(
                root.transform,
                "SlateBeveledFace",
                face,
                slateFace).transform;
            cutFace.localPosition = new Vector3(0f, -0.00435f, 0f);
            for (int index = 0; index < 13; index++)
            {
                Transform grain = AddMesh(
                    root.transform,
                    $"SlateGrain_{index:00}",
                    box,
                    seam).transform;
                grain.localPosition = new Vector3(
                    -0.026f + index * 0.0043f,
                    -0.00482f,
                    (index % 4 - 1.5f) * 0.0023f);
                grain.localRotation = Quaternion.Euler(
                    0f,
                    -13f + (index % 3) * 5f,
                    0f);
                grain.localScale = new Vector3(
                    0.00045f,
                    0.00022f,
                    0.037f - (index % 4) * 0.0025f);
            }

            return root;
        }

        private static GameObject BuildBasaltBase(
            GachaPrizePresentationDescriptor descriptor)
        {
            var root = NewRuntimeRoot(descriptor.Kind.ToString());
            GachaPrizeRuntimeResourceOwner owner =
                root.GetComponent<GachaPrizeRuntimeResourceOwner>();
            Mesh foot = owner.Own(CreateRoundedSlabMesh(
                0.072f,
                0.014f,
                0.010f,
                0.004f,
                4));
            Mesh riser = owner.Own(CreateRoundedSlabMesh(
                0.050f,
                0.030f,
                0.012f,
                0.005f,
                4));
            Mesh deck = owner.Own(CreateRoundedSlabMesh(
                0.066f,
                0.014f,
                0.009f,
                0.004f,
                4));
            Mesh box = owner.Own(CreateBoxMesh());
            Material basalt = owner.Own(CreateLitMaterial(
                "Basalt",
                new Color(0.12f, 0.14f, 0.16f, 1f),
                0.16f,
                0.26f));
            Material edge = owner.Own(CreateLitMaterial(
                "BasaltCutEdge",
                new Color(0.38f, 0.42f, 0.45f, 1f),
                0.25f,
                0.40f));
            Transform footNode = AddMesh(
                root.transform,
                "BasaltPedestalFoot",
                foot,
                basalt).transform;
            footNode.localPosition = new Vector3(0f, 0f, -0.022f);
            Transform riserNode = AddMesh(
                root.transform,
                "BasaltPedestalRiser",
                riser,
                basalt).transform;
            riserNode.localPosition = new Vector3(0f, 0f, -0.001f);
            Transform deckNode = AddMesh(
                root.transform,
                "BasaltPedestalTopDeck",
                deck,
                basalt).transform;
            deckNode.localPosition = new Vector3(0f, 0f, 0.021f);
            for (int index = 0; index < 6; index++)
            {
                Transform cut = AddMesh(
                    root.transform,
                    $"BasaltFacet_{index:00}",
                    box,
                    edge).transform;
                cut.localPosition = new Vector3(
                    -0.019f + index * 0.0076f,
                    -0.00615f,
                    -0.001f + (index % 2 == 0 ? -0.003f : 0.003f));
                cut.localRotation = Quaternion.Euler(0f, -18f, 0f);
                cut.localScale = new Vector3(0.0042f, 0.00032f, 0.017f);
            }

            Transform deckHighlight = AddMesh(
                root.transform,
                "BasaltTopCutHighlight",
                box,
                edge).transform;
            deckHighlight.localPosition = new Vector3(0f, -0.00465f, 0.021f);
            deckHighlight.localScale = new Vector3(0.052f, 0.00028f, 0.0020f);

            return root;
        }

        private static GameObject BuildRidgeDusk(
            GachaPrizePresentationDescriptor descriptor)
        {
            var root = NewRuntimeRoot(descriptor.Kind.ToString());
            GachaPrizeRuntimeResourceOwner owner =
                root.GetComponent<GachaPrizeRuntimeResourceOwner>();
            Mesh glassMesh = owner.Own(CreateRoundedSlabMesh(
                0.067f,
                0.061f,
                0.004f,
                0.007f,
                6));
            Mesh box = owner.Own(CreateBoxMesh());
            Material glass = owner.Own(CreateLitMaterial(
                "RidgeDuskGlass",
                new Color(0.18f, 0.12f, 0.42f, 0.38f),
                0.08f,
                0.94f,
                true));
            Material glassEdge = owner.Own(CreateLitMaterial(
                "RidgeDuskGlassEdge",
                new Color(0.28f, 0.70f, 1.00f, 0.82f),
                0.10f,
                0.96f,
                true));
            SetEmission(
                glassEdge,
                new Color(0.05f, 0.18f, 0.32f, 1f));
            Material reflection = owner.Own(CreateLitMaterial(
                "RidgeDuskGlassReflection",
                new Color(0.66f, 0.42f, 1.00f, 0.24f),
                0.05f,
                1.00f,
                true));
            Material ridge = owner.Own(CreateLitMaterial(
                "RidgeSilhouette",
                new Color(0.025f, 0.040f, 0.070f, 0.82f),
                0.20f,
                0.42f,
                true));
            Material horizon = owner.Own(CreateLitMaterial(
                "DuskHorizon",
                new Color(1.00f, 0.29f, 0.12f, 1f),
                0.25f,
                0.70f));
            SetEmission(horizon, new Color(0.44f, 0.065f, 0.015f, 1f));
            AddMesh(root.transform, "DuskGlassMaterialSample", glassMesh, glass);
            AddGlassSampleEdges(root.transform, box, glassEdge);
            for (int index = 0; index < 3; index++)
            {
                Transform glint = AddMesh(
                    root.transform,
                    $"DuskGlassReflection_{index:00}",
                    box,
                    reflection).transform;
                glint.localPosition = new Vector3(
                    -0.020f + index * 0.019f,
                    -0.00232f,
                    0.002f);
                glint.localRotation = Quaternion.Euler(0f, -28f, 0f);
                glint.localScale = new Vector3(0.0011f, 0.00024f, 0.046f);
            }
            float[] heights = { 0.010f, 0.019f, 0.013f, 0.025f, 0.016f, 0.021f };
            for (int index = 0; index < heights.Length; index++)
            {
                Transform mountain = AddMesh(
                    root.transform,
                    $"RidgeSilhouette_{index:00}",
                    box,
                    ridge).transform;
                mountain.localPosition = new Vector3(
                    -0.026f + index * 0.0105f,
                    -0.00235f,
                    -0.021f + heights[index] * 0.5f);
                mountain.localRotation = Quaternion.Euler(0f, 45f, 0f);
                mountain.localScale = new Vector3(
                    0.009f,
                    0.00035f,
                    heights[index]);
            }
            Transform horizonBar = AddMesh(
                root.transform,
                "RidgeDuskHorizonGlow",
                box,
                horizon).transform;
            horizonBar.localPosition = new Vector3(0f, -0.00242f, 0.013f);
            horizonBar.localScale = new Vector3(0.048f, 0.00025f, 0.0012f);
            return root;
        }

        private static void AddGlassSampleEdges(
            Transform root,
            Mesh box,
            Material material)
        {
            for (int index = 0; index < 4; index++)
            {
                bool vertical = index < 2;
                Transform edge = AddMesh(
                    root,
                    $"DuskGlassEdge_{index:00}",
                    box,
                    material).transform;
                edge.localPosition = vertical
                    ? new Vector3(index == 0 ? -0.0324f : 0.0324f, -0.00236f, 0f)
                    : new Vector3(0f, -0.00236f, index == 2 ? -0.0293f : 0.0293f);
                edge.localScale = vertical
                    ? new Vector3(0.0010f, 0.00028f, 0.050f)
                    : new Vector3(0.056f, 0.00028f, 0.0010f);
            }
        }

        private static GameObject NewRuntimeRoot(string name)
        {
            var root = new GameObject(name);
            root.AddComponent<GachaPrizeRuntimeResourceOwner>();
            return root;
        }

        private static GameObject AddMesh(
            Transform parent,
            string name,
            Mesh mesh,
            Material material)
        {
            var visual = new GameObject(name);
            visual.transform.SetParent(parent, false);
            MeshFilter filter = visual.AddComponent<MeshFilter>();
            filter.sharedMesh = mesh;
            MeshRenderer renderer = visual.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.On;
            renderer.receiveShadows = true;
            return visual;
        }

        private static Material CreateLitMaterial(
            string name,
            Color color,
            float metallic,
            float smoothness,
            bool transparent = false)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Lit")
                ?? Shader.Find("Standard")
                ?? Shader.Find("Unlit/Color");
            if (shader == null)
            {
                throw new MissingReferenceException("No shipping lit shader found.");
            }

            var material = new Material(shader) { name = name };
            material.SetColor("_BaseColor", color);
            material.SetColor("_Color", color);
            if (material.HasProperty("_Metallic"))
            {
                material.SetFloat("_Metallic", metallic);
            }
            if (material.HasProperty("_Smoothness"))
            {
                material.SetFloat("_Smoothness", smoothness);
            }
            if (material.HasProperty("_Glossiness"))
            {
                material.SetFloat("_Glossiness", smoothness);
            }
            if (transparent)
            {
                material.SetFloat("_Surface", 1f);
                material.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
                material.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
                material.SetFloat("_ZWrite", 0f);
                material.SetOverrideTag("RenderType", "Transparent");
                material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
                material.renderQueue = (int)RenderQueue.Transparent;
            }
            return material;
        }

        private static void SetEmission(Material material, Color color)
        {
            if (material == null || !material.HasProperty("_EmissionColor"))
            {
                return;
            }
            material.SetColor("_EmissionColor", color);
            material.EnableKeyword("_EMISSION");
        }

        private static Mesh CreateBoxMesh()
        {
            var mesh = new Mesh { name = "GachaPresentationBox" };
            Vector3[] vertices =
            {
                new Vector3(-.5f,-.5f,-.5f), new Vector3(.5f,-.5f,-.5f), new Vector3(.5f,.5f,-.5f), new Vector3(-.5f,.5f,-.5f),
                new Vector3(.5f,-.5f,.5f), new Vector3(-.5f,-.5f,.5f), new Vector3(-.5f,.5f,.5f), new Vector3(.5f,.5f,.5f),
                new Vector3(-.5f,-.5f,.5f), new Vector3(-.5f,-.5f,-.5f), new Vector3(-.5f,.5f,-.5f), new Vector3(-.5f,.5f,.5f),
                new Vector3(.5f,-.5f,-.5f), new Vector3(.5f,-.5f,.5f), new Vector3(.5f,.5f,.5f), new Vector3(.5f,.5f,-.5f),
                new Vector3(-.5f,.5f,-.5f), new Vector3(.5f,.5f,-.5f), new Vector3(.5f,.5f,.5f), new Vector3(-.5f,.5f,.5f),
                new Vector3(-.5f,-.5f,.5f), new Vector3(.5f,-.5f,.5f), new Vector3(.5f,-.5f,-.5f), new Vector3(-.5f,-.5f,-.5f)
            };
            int[] triangles =
            {
                0,2,1, 0,3,2, 4,6,5, 4,7,6,
                8,10,9, 8,11,10, 12,14,13, 12,15,14,
                16,18,17, 16,19,18, 20,22,21, 20,23,22
            };
            mesh.vertices = vertices;
            mesh.triangles = triangles;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        private static Mesh CreateRoundedSlabMesh(
            float width,
            float depth,
            float thickness,
            float radius,
            int cornerSegments)
        {
            int segments = Mathf.Max(2, cornerSegments);
            float safeRadius = Mathf.Min(radius, Mathf.Min(width, depth) * 0.49f);
            var outline = new List<Vector3>(segments * 4 + 4);
            Vector2[] centers =
            {
                new Vector2(width * 0.5f - safeRadius, depth * 0.5f - safeRadius),
                new Vector2(-width * 0.5f + safeRadius, depth * 0.5f - safeRadius),
                new Vector2(-width * 0.5f + safeRadius, -depth * 0.5f + safeRadius),
                new Vector2(width * 0.5f - safeRadius, -depth * 0.5f + safeRadius)
            };
            float[] starts = { 0f, 90f, 180f, 270f };
            for (int corner = 0; corner < 4; corner++)
            {
                for (int step = 0; step <= segments; step++)
                {
                    float angle = (starts[corner] + 90f * step / segments)
                        * Mathf.Deg2Rad;
                    outline.Add(new Vector3(
                        centers[corner].x + Mathf.Cos(angle) * safeRadius,
                        0f,
                        centers[corner].y + Mathf.Sin(angle) * safeRadius));
                }
            }

            int count = outline.Count;
            var vertices = new List<Vector3>(count * 4 + 2);
            var triangles = new List<int>(count * 12);
            float half = thickness * 0.5f;
            int topCenter = vertices.Count;
            vertices.Add(new Vector3(0f, half, 0f));
            int bottomCenter = vertices.Count;
            vertices.Add(new Vector3(0f, -half, 0f));
            int topStart = vertices.Count;
            for (int index = 0; index < count; index++)
            {
                Vector3 point = outline[index];
                vertices.Add(new Vector3(point.x, half, point.z));
            }
            int bottomStart = vertices.Count;
            for (int index = 0; index < count; index++)
            {
                Vector3 point = outline[index];
                vertices.Add(new Vector3(point.x, -half, point.z));
            }
            for (int index = 0; index < count; index++)
            {
                int next = (index + 1) % count;
                triangles.Add(topCenter);
                triangles.Add(topStart + next);
                triangles.Add(topStart + index);
                triangles.Add(bottomCenter);
                triangles.Add(bottomStart + index);
                triangles.Add(bottomStart + next);

                int sideStart = vertices.Count;
                vertices.Add(vertices[topStart + index]);
                vertices.Add(vertices[topStart + next]);
                vertices.Add(vertices[bottomStart + next]);
                vertices.Add(vertices[bottomStart + index]);
                triangles.Add(sideStart);
                triangles.Add(sideStart + 1);
                triangles.Add(sideStart + 2);
                triangles.Add(sideStart);
                triangles.Add(sideStart + 2);
                triangles.Add(sideStart + 3);
            }

            var mesh = new Mesh { name = "GachaRoundedMaterialSample" };
            mesh.SetVertices(vertices);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        private static float Next01(ref uint state)
        {
            state = state * 1664525u + 1013904223u;
            return (state & 0x00FFFFFFu) / 16777215f;
        }

        private static float NextSigned(ref uint state)
        {
            return Next01(ref state) * 2f - 1f;
        }

        private static void ValidateRendererOnly(GameObject root)
        {
            if (root == null)
            {
                throw new MissingReferenceException("Prize root was not created.");
            }
            if (root.GetComponentsInChildren<Renderer>(true).Length == 0)
            {
                throw new InvalidOperationException(
                    "Prize presentation contains no renderer.");
            }
            if (!IsRendererOnly(root))
            {
                throw new InvalidOperationException(
                    "Prize presentation must be renderer-only.");
            }
        }
    }

    /// <summary>
    /// Owns generated meshes/materials only. It has no Update and cannot
    /// affect mechanics, input, audio or Haptics.
    /// </summary>
    [DisallowMultipleComponent]
    internal sealed class GachaPrizeRuntimeResourceOwner : MonoBehaviour
    {
        private readonly List<UnityEngine.Object> resources =
            new List<UnityEngine.Object>();

        public T Own<T>(T resource) where T : UnityEngine.Object
        {
            if (resource != null)
            {
                resources.Add(resource);
            }
            return resource;
        }

        private void OnDestroy()
        {
            for (int index = resources.Count - 1; index >= 0; index--)
            {
                GachaPrizePresentationResolver.DestroyOwned(resources[index]);
            }
            resources.Clear();
        }
    }
}
