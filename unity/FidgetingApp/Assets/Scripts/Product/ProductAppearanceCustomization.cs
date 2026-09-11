using System;
using System.Collections.Generic;
using System.Globalization;
using System.Runtime.InteropServices;
using CodexUnityLab;
using FidgetingApp.EDC;
using ThreeBladeEDC.Interaction;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.Product
{
    public readonly struct ProductStickerDefinition
    {
        public ProductStickerDefinition(
            string id,
            string displayName,
            string artworkAssetName,
            string symbolName,
            Color tint)
        {
            Id = id;
            DisplayName = displayName;
            ArtworkAssetName = artworkAssetName;
            SymbolName = symbolName;
            Tint = tint;
        }

        public string Id { get; }
        public string DisplayName { get; }
        public string ArtworkAssetName { get; }
        public string SymbolName { get; }
        public Color Tint { get; }
    }

    /// <summary>
    /// Temporary product-owned sticker artwork. The IDs and persistence are
    /// stable so final art can replace these procedural placeholders later.
    /// </summary>
    public static class ProductStickerCatalog
    {
        public const string NoneId = "none";
        public const string ArtworkResourceRoot =
            "ProductStickers/BackdropWhite";

        private static readonly ProductStickerDefinition[] stickers =
        {
            new ProductStickerDefinition(
                NoneId,
                "无贴纸",
                string.Empty,
                "nosign",
                Hex("AEB5BC")),
            new ProductStickerDefinition(
                "01-polygon-cube",
                "多面方块",
                "01-polygon-cube",
                "cube.transparent.fill",
                Hex("8FE8FF")),
            new ProductStickerDefinition(
                "02-hw-studio",
                "HW 徽章",
                "02-hw-studio",
                "square.grid.3x3.fill",
                Hex("FFD45D")),
            new ProductStickerDefinition(
                "03-top-right-monogram",
                "组合字标",
                "03-top-right-monogram",
                "scribble.variable",
                Hex("FF8FB8")),
            new ProductStickerDefinition(
                "04-rabbit-hand",
                "兔手势",
                "04-rabbit-hand",
                "hand.raised.fingers.spread.fill",
                Hex("C4A7FF")),
            new ProductStickerDefinition(
                "05-wawu-word",
                "WAWU 字标",
                "05-wawu-word",
                "textformat",
                Hex("A6F0C6")),
            new ProductStickerDefinition(
                "06-round-mascot",
                "圆形吉祥物",
                "06-round-mascot",
                "pawprint.circle.fill",
                Hex("FFB86B")),
            new ProductStickerDefinition(
                "07-nck-word",
                "NCK 字标",
                "07-nck-word",
                "character.cursor.ibeam",
                Hex("8FE8FF")),
            new ProductStickerDefinition(
                "08-geeone",
                "GEEONE 徽章",
                "08-geeone",
                "capsule.fill",
                Hex("E8EDF2")),
            new ProductStickerDefinition(
                "09-tiger-head",
                "虎头",
                "09-tiger-head",
                "cat.fill",
                Hex("FFD45D")),
            new ProductStickerDefinition(
                "10-meteor",
                "流星",
                "10-meteor",
                "sparkles",
                Hex("FF8FB8")),
            new ProductStickerDefinition(
                "11-mackie",
                "MACKIE 徽章",
                "11-mackie",
                "badge.plus.radiowaves.right",
                Hex("C4A7FF")),
            new ProductStickerDefinition(
                "12-turci-word",
                "TURCI 字标",
                "12-turci-word",
                "textformat.alt",
                Hex("A6F0C6")),
            new ProductStickerDefinition(
                "13-astronaut",
                "宇航头盔",
                "13-astronaut",
                "moon.stars.fill",
                Hex("8FE8FF")),
            new ProductStickerDefinition(
                "14-target",
                "同心靶",
                "14-target",
                "scope",
                Hex("FFD45D")),
            new ProductStickerDefinition(
                "15-knot",
                "几何结",
                "15-knot",
                "point.3.connected.trianglepath.dotted",
                Hex("FF8FB8")),
            new ProductStickerDefinition(
                "16-flame-leaf",
                "火焰叶",
                "16-flame-leaf",
                "flame.fill",
                Hex("FFB86B")),
            new ProductStickerDefinition(
                "17-chemy-word",
                "CHEMY 字标",
                "17-chemy-word",
                "character.textbox",
                Hex("C4A7FF")),
            new ProductStickerDefinition(
                "18-emoji-face",
                "表情脸",
                "18-emoji-face",
                "face.smiling.inverse",
                Hex("FFD45D")),
            new ProductStickerDefinition(
                "19-box-t",
                "方框 T",
                "19-box-t",
                "t.square.fill",
                Hex("8FE8FF")),
            new ProductStickerDefinition(
                "20-warning-triangle",
                "警示三角",
                "20-warning-triangle",
                "exclamationmark.triangle.fill",
                Hex("FFB86B")),
            new ProductStickerDefinition(
                "21-triple-stroke",
                "三重笔画",
                "21-triple-stroke",
                "line.3.horizontal",
                Hex("E8EDF2")),
            new ProductStickerDefinition(
                "22-section-s",
                "S 图腾",
                "22-section-s",
                "s.circle.fill",
                Hex("A6F0C6")),
            new ProductStickerDefinition(
                "23-fierce-head",
                "猛兽头像",
                "23-fierce-head",
                "hare.fill",
                Hex("FF8FB8")),
            new ProductStickerDefinition(
                "24-round-chinese",
                "圆形印章",
                "24-round-chinese",
                "seal.fill",
                Hex("FFD45D"))
        };

        public static IReadOnlyList<ProductStickerDefinition> Stickers => stickers;

        public static ProductStickerDefinition Resolve(string requestedId)
        {
            requestedId = MigrateLegacyId(requestedId);
            for (int index = 0; index < stickers.Length; index++)
            {
                if (stickers[index].Id == requestedId)
                {
                    return stickers[index];
                }
            }

            return stickers[0];
        }

        public static string CatalogPayload()
        {
            var rows = new string[stickers.Length];
            for (int index = 0; index < stickers.Length; index++)
            {
                ProductStickerDefinition sticker = stickers[index];
                rows[index] = string.Join(
                    "\t",
                    sticker.Id,
                    sticker.DisplayName,
                    sticker.ArtworkAssetName,
                    sticker.SymbolName,
                    ColorUtility.ToHtmlStringRGB(sticker.Tint));
            }

            return string.Join("\n", rows);
        }

        private static string MigrateLegacyId(string requestedId)
        {
            switch (requestedId)
            {
                case "orbit-ring":
                    return "14-target";
                case "charge-bolt":
                    return "20-warning-triangle";
                case "pixel-smile":
                    return "18-emoji-face";
                case "race-checker":
                    return "01-polygon-cube";
                default:
                    return requestedId;
            }
        }

        private static Color Hex(string value)
        {
            return ColorUtility.TryParseHtmlString("#" + value, out Color color)
                ? color
                : Color.white;
        }
    }

    /// <summary>
    /// Deterministic long-press state independent of frame rate and input API.
    /// Distances are supplied in logical points by the caller.
    /// </summary>
    public sealed class ProductAppearanceLongPressGesture
    {
        public const float RequiredDurationSeconds = 0.55f;
        public const float MaximumMovementPoints = 12f;

        private bool tracking;
        private bool triggered;
        private Vector2 startPositionPoints;
        private float startTime;

        public bool IsTracking => tracking;

        public void Begin(bool hitProduct, Vector2 positionPoints, float time)
        {
            tracking = hitProduct;
            triggered = false;
            startPositionPoints = positionPoints;
            startTime = time;
        }

        public bool Update(bool pressed, Vector2 positionPoints, float time)
        {
            if (!tracking || triggered || !pressed)
            {
                if (!pressed)
                {
                    Cancel();
                }
                return false;
            }

            if (Vector2.Distance(startPositionPoints, positionPoints)
                > MaximumMovementPoints)
            {
                Cancel();
                return false;
            }

            if (time - startTime < RequiredDurationSeconds)
            {
                return false;
            }

            tracking = false;
            triggered = true;
            return true;
        }

        public void Cancel()
        {
            tracking = false;
            triggered = false;
        }
    }

    public readonly struct ProductAppearanceActivationSample
    {
        public ProductAppearanceActivationSample(
            float apparentScale,
            bool shouldPresentHalfSheet)
        {
            ApparentScale = apparentScale;
            ShouldPresentHalfSheet = shouldPresentHalfSheet;
        }

        public float ApparentScale { get; }
        public bool ShouldPresentHalfSheet { get; }
    }

    /// <summary>
    /// A short, deterministic presentation-only response between a confirmed
    /// model hold and the native appearance half sheet. The coordinator maps
    /// ApparentScale to camera framing, never to the product transform, so the
    /// sequence cannot change colliders, physical body state, or angular velocity.
    /// </summary>
    public sealed class ProductAppearanceActivationSequence
    {
        public const float DurationSeconds = 0.22f;
        public const float PeakTimeSeconds = 0.075f;
        public const float SettleTimeSeconds = 0.15f;
        public const float PeakScale = 1.035f;
        public const float SettleScale = 0.992f;

        private bool active;
        private float startTime;

        public bool IsActive => active;

        public bool Begin(float time)
        {
            if (active)
            {
                return false;
            }

            startTime = time;
            active = true;
            return true;
        }

        public ProductAppearanceActivationSample Update(float time)
        {
            if (!active)
            {
                return new ProductAppearanceActivationSample(1f, false);
            }

            float elapsed = Mathf.Max(0f, time - startTime);
            if (elapsed >= DurationSeconds)
            {
                active = false;
                return new ProductAppearanceActivationSample(1f, true);
            }

            return new ProductAppearanceActivationSample(
                EvaluateApparentScale(elapsed),
                false);
        }

        public void Cancel()
        {
            active = false;
        }

        public static float EvaluateApparentScale(float elapsedSeconds)
        {
            float elapsed = Mathf.Clamp(elapsedSeconds, 0f, DurationSeconds);
            if (elapsed <= PeakTimeSeconds)
            {
                return Mathf.SmoothStep(
                    1f,
                    PeakScale,
                    elapsed / PeakTimeSeconds);
            }

            if (elapsed <= SettleTimeSeconds)
            {
                return Mathf.SmoothStep(
                    PeakScale,
                    SettleScale,
                    (elapsed - PeakTimeSeconds)
                        / (SettleTimeSeconds - PeakTimeSeconds));
            }

            return Mathf.SmoothStep(
                SettleScale,
                1f,
                (elapsed - SettleTimeSeconds)
                    / (DurationSeconds - SettleTimeSeconds));
        }
    }

    /// <summary>
    /// Resolves appearance-editor hit testing through each mechanism's own
    /// authoritative touch surface. This is intentionally shared with the
    /// real interaction controllers: the metal spinner's fixed center cap is
    /// a sibling of RotorDynamic, so transform ancestry alone is insufficient.
    /// </summary>
    public static class ProductAppearanceHitTester
    {
        public static bool ContainsScreenPoint(
            Vector2 screenPosition,
            FidgetSpinnerController blueSpinner,
            MobileGestureController metalGestures,
            EdcSliderController edcSlider,
            Transform fallbackProduct,
            Camera camera)
        {
            if (blueSpinner != null && blueSpinner.ContainsScreenPoint(screenPosition))
            {
                return true;
            }

            if (metalGestures != null
                && metalGestures.ClassifyScreenPoint(screenPosition)
                    == MobileGestureMode.Spin)
            {
                return true;
            }

            if (edcSlider != null && edcSlider.ContainsScreenPoint(screenPosition))
            {
                return true;
            }

            if (fallbackProduct == null || camera == null)
            {
                return false;
            }

            Ray ray = camera.ScreenPointToRay(screenPosition);
            RaycastHit[] hits = Physics.RaycastAll(
                ray,
                camera.farClipPlane,
                Physics.DefaultRaycastLayers,
                QueryTriggerInteraction.Collide);
            for (int index = 0; index < hits.Length; index++)
            {
                Transform hit = hits[index].transform;
                if (hit == fallbackProduct
                    || hit.IsChildOf(fallbackProduct)
                    || fallbackProduct.IsChildOf(hit))
                {
                    return true;
                }
            }

            return false;
        }
    }

    /// <summary>
    /// Presentation-only conformal laser engraving shared by all product models.
    /// Artwork is projected into copies of the product's actual receiver meshes,
    /// so the mark follows curved metal, holes, bevels, and rotor motion without
    /// creating a floating card or changing physics and Haptics.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class ProductStickerPresenter : MonoBehaviour
    {
        public const string StickerRootName = "ProductStickerVisual";
        public const string EngravingSurfaceNamePrefix =
            "ProductLaserEngravingSurface_";
        public const string LaserEngravingShaderName =
            "FidgetingApp/Product Laser Engraving";
        public const string LaserEngravingShaderResourcePath =
            "ProductStickers/ProductLaserEngraving";

        private static readonly int ReceiverToProjectorId =
            Shader.PropertyToID("_ReceiverToProjector");
        private static readonly int ProjectionNormalOsId =
            Shader.PropertyToID("_ProjectionNormalOS");
        private static readonly Color EngravedMetalColor =
            new Color(0.045f, 0.052f, 0.060f, 1f);
        private static readonly Color CutEdgeColor =
            new Color(0.76f, 0.80f, 0.84f, 1f);

        private readonly List<GameObject> engravingSurfaces = new List<GameObject>();
        private GameObject stickerRoot;
        private Material stickerMaterial;
        private Texture2D stickerTexture;
        private string appliedStickerId = ProductStickerCatalog.NoneId;
        private bool usesTopCapReceiver;

        public string AppliedStickerId => appliedStickerId;
        public bool HasAppliedSticker => appliedStickerId == ProductStickerCatalog.NoneId
            || (stickerRoot != null
                && stickerRoot.activeSelf
                && engravingSurfaces.Count > 0);
        public int GeneratedSurfaceCount => engravingSurfaces.Count;
        public bool UsesConformalReceiverMeshes => engravingSurfaces.Count > 0;
        public bool UsesTopCapReceiver => usesTopCapReceiver;
        public int GeneratedColliderCount
        {
            get
            {
                int count = 0;
                for (int index = 0; index < engravingSurfaces.Count; index++)
                {
                    GameObject surface = engravingSurfaces[index];
                    if (surface != null)
                    {
                        count += surface.GetComponents<Collider>().Length;
                    }
                }

                return count;
            }
        }

        public void Apply(string requestedId, Camera presentationCamera)
        {
            ProductStickerDefinition sticker = ProductStickerCatalog.Resolve(requestedId);
            appliedStickerId = sticker.Id;
            if (sticker.Id == ProductStickerCatalog.NoneId)
            {
                SetEngravingActive(false);
                return;
            }

            Texture2D artwork = Resources.Load<Texture2D>(
                ProductStickerCatalog.ArtworkResourceRoot
                + "/"
                + sticker.ArtworkAssetName);
            if (artwork == null)
            {
                FailClosed();
                return;
            }

            var receivers = new List<MeshRenderer>();
            if (!TryCollectReceivers(
                    receivers,
                    out Bounds bounds,
                    out usesTopCapReceiver)
                || !TryCalculateProjection(
                    presentationCamera,
                    bounds,
                    usesTopCapReceiver ? 0.68f : 0.30f,
                    out Matrix4x4 projectorWorldToLocal,
                    out Vector3 projectionNormalWorld))
            {
                FailClosed();
                return;
            }

            EnsureEngravingResources();
            ReplaceTexture(artwork);
            RebuildConformalSurfaces(
                receivers,
                projectorWorldToLocal,
                projectionNormalWorld);
            if (engravingSurfaces.Count == 0)
            {
                FailClosed();
                return;
            }

            SetEngravingActive(true);
        }

        private bool TryCollectReceivers(
            List<MeshRenderer> receivers,
            out Bounds bounds,
            out bool selectedTopCap)
        {
            MeshRenderer[] renderers = GetComponentsInChildren<MeshRenderer>(true);
            Transform topCapAnchor = transform.Find("HubStatic/TopCap");
            MeshRenderer visibleTopCap = null;
            int visibleTopCapPriority = int.MinValue;
            bool hasBounds = false;
            selectedTopCap = false;
            bounds = default;
            for (int index = 0; index < renderers.Length; index++)
            {
                MeshRenderer candidate = renderers[index];
                if (candidate == null
                    || !candidate.enabled
                    || !candidate.gameObject.activeInHierarchy
                    || candidate.gameObject.name.StartsWith(
                        EngravingSurfaceNamePrefix,
                        StringComparison.Ordinal))
                {
                    continue;
                }

                MeshFilter filter = candidate.GetComponent<MeshFilter>();
                if (filter == null
                    || filter.sharedMesh == null
                    || filter.sharedMesh.vertexCount == 0)
                {
                    continue;
                }

                bool belongsToTopCap = topCapAnchor != null
                    && (candidate.transform == topCapAnchor
                        || candidate.transform.IsChildOf(topCapAnchor));
                if (belongsToTopCap)
                {
                    int priority = GetTopCapReceiverPriority(candidate);
                    if (priority > visibleTopCapPriority)
                    {
                        visibleTopCap = candidate;
                        visibleTopCapPriority = priority;
                    }
                    continue;
                }

                receivers.Add(candidate);
                if (!hasBounds)
                {
                    bounds = candidate.bounds;
                    hasBounds = true;
                }
                else
                {
                    bounds.Encapsulate(candidate.bounds);
                }
            }

            if (visibleTopCap != null)
            {
                receivers.Clear();
                receivers.Add(visibleTopCap);
                bounds = visibleTopCap.bounds;
                selectedTopCap = true;
                return true;
            }

            return hasBounds && receivers.Count > 0;
        }

        private static int GetTopCapReceiverPriority(MeshRenderer candidate)
        {
            // The imported cap is layered: FingerCap_Top is the structural
            // shell, while FingerCapTop_BrushedFace is the separate metal face
            // that physically sits 2.08 mm above it. Projecting onto the shell
            // lets the face occlude the engraving in a direct top view.
            if (string.Equals(
                candidate.gameObject.name,
                "FingerCapTop_BrushedFace",
                StringComparison.Ordinal))
            {
                return 300;
            }

            // GEEONE 龙鳞三叶: the top cap is one mesh (14-sector dish + crown + skirt); it is both the
            // structural shell and the visible face.
            if (string.Equals(
                candidate.gameObject.name,
                "Cap_Top",
                StringComparison.Ordinal))
            {
                return 300;
            }

            if (string.Equals(
                candidate.gameObject.name,
                "FingerCap_Top",
                StringComparison.Ordinal))
            {
                return 200;
            }

            if (candidate.gameObject.name.IndexOf(
                    "AccentLine",
                    StringComparison.OrdinalIgnoreCase) >= 0)
            {
                return 0;
            }

            return 100;
        }

        private bool TryCalculateProjection(
            Camera presentationCamera,
            Bounds bounds,
            float sizeFraction,
            out Matrix4x4 projectorWorldToLocal,
            out Vector3 projectionNormalWorld)
        {
            projectionNormalWorld = transform.up.normalized;
            if (projectionNormalWorld.sqrMagnitude < 0.5f)
            {
                projectionNormalWorld = Vector3.up;
            }

            if (presentationCamera != null
                && Vector3.Dot(
                    projectionNormalWorld,
                    presentationCamera.transform.position - bounds.center) < 0f)
            {
                projectionNormalWorld = -projectionNormalWorld;
            }

            Vector3 projectionUp = presentationCamera != null
                ? Vector3.ProjectOnPlane(
                    presentationCamera.transform.up,
                    projectionNormalWorld)
                : Vector3.ProjectOnPlane(-transform.forward, projectionNormalWorld);
            if (projectionUp.sqrMagnitude < 0.25f)
            {
                projectionUp = Vector3.ProjectOnPlane(
                    transform.forward,
                    projectionNormalWorld);
            }
            if (projectionUp.sqrMagnitude < 0.25f)
            {
                projectorWorldToLocal = default;
                return false;
            }

            projectionUp.Normalize();
            Quaternion rotation = Quaternion.LookRotation(
                -projectionNormalWorld,
                projectionUp);
            Vector3 projectionRight = rotation * Vector3.right;
            float projectedWidth = SupportDistance(
                bounds.extents,
                projectionRight) * 2f;
            float projectedHeight = SupportDistance(
                bounds.extents,
                projectionUp) * 2f;
            float projectedMinimum = Mathf.Min(projectedWidth, projectedHeight);
            float size = Mathf.Max(
                0.006f,
                projectedMinimum * Mathf.Clamp(sizeFraction, 0.20f, 0.80f));
            projectorWorldToLocal = Matrix4x4.TRS(
                bounds.center,
                rotation,
                Vector3.one * size).inverse;
            return true;
        }

        private static float SupportDistance(Vector3 extents, Vector3 direction)
        {
            return Mathf.Abs(direction.x) * extents.x
                + Mathf.Abs(direction.y) * extents.y
                + Mathf.Abs(direction.z) * extents.z;
        }

        private void EnsureEngravingResources()
        {
            if (stickerRoot == null)
            {
                stickerRoot = new GameObject(StickerRootName);
                stickerRoot.layer = gameObject.layer;
                stickerRoot.transform.SetParent(transform, false);
            }

            if (stickerMaterial != null)
            {
                return;
            }

            Shader shader = Resources.Load<Shader>(
                    LaserEngravingShaderResourcePath)
                ?? Shader.Find(LaserEngravingShaderName);
            if (shader == null)
            {
                throw new InvalidOperationException(
                    "The bundled product laser engraving shader is required.");
            }

            stickerMaterial = new Material(shader)
            {
                name = "ProductConformalLaserEngravingMaterial",
                renderQueue = 2475
            };
            stickerMaterial.SetColor("_EngraveColor", EngravedMetalColor);
            stickerMaterial.SetColor("_EdgeColor", CutEdgeColor);
            stickerMaterial.SetFloat("_Strength", 0.94f);
            stickerMaterial.SetFloat("_BevelStrength", 0.88f);
            stickerMaterial.SetFloat("_SurfaceAlignment", 0.12f);
            stickerMaterial.SetFloat("_SurfaceLift", 0.00018f);
            stickerMaterial.SetOverrideTag("RenderType", "TransparentCutout");
        }

        private void RebuildConformalSurfaces(
            List<MeshRenderer> receivers,
            Matrix4x4 projectorWorldToLocal,
            Vector3 projectionNormalWorld)
        {
            DestroyConformalSurfaces();
            for (int index = 0; index < receivers.Count; index++)
            {
                MeshRenderer source = receivers[index];
                if (source == null)
                {
                    continue;
                }

                MeshFilter sourceFilter = source.GetComponent<MeshFilter>();
                Mesh sourceMesh = sourceFilter != null
                    ? sourceFilter.sharedMesh
                    : null;
                if (sourceMesh == null)
                {
                    continue;
                }

                var surface = new GameObject(
                    EngravingSurfaceNamePrefix + source.gameObject.name);
                surface.layer = source.gameObject.layer;
                surface.transform.SetParent(source.transform, false);
                surface.AddComponent<MeshFilter>().sharedMesh = sourceMesh;
                MeshRenderer renderer = surface.AddComponent<MeshRenderer>();

                int materialCount = Mathf.Max(1, sourceMesh.subMeshCount);
                var materials = new Material[materialCount];
                for (int materialIndex = 0;
                     materialIndex < materialCount;
                     materialIndex++)
                {
                    materials[materialIndex] = stickerMaterial;
                }
                renderer.sharedMaterials = materials;
                renderer.shadowCastingMode =
                    UnityEngine.Rendering.ShadowCastingMode.Off;
                renderer.receiveShadows = false;
                renderer.lightProbeUsage = UnityEngine.Rendering.LightProbeUsage.Off;
                renderer.reflectionProbeUsage =
                    UnityEngine.Rendering.ReflectionProbeUsage.Off;
                renderer.motionVectorGenerationMode =
                    MotionVectorGenerationMode.ForceNoMotion;
                renderer.allowOcclusionWhenDynamic = false;
                renderer.sortingOrder = source.sortingOrder + 20;

                Matrix4x4 receiverToProjector =
                    projectorWorldToLocal * source.transform.localToWorldMatrix;
                Vector3 projectionNormalObject = source.transform
                    .InverseTransformDirection(projectionNormalWorld)
                    .normalized;
                var properties = new MaterialPropertyBlock();
                properties.SetMatrix(
                    ReceiverToProjectorId,
                    receiverToProjector);
                properties.SetVector(
                    ProjectionNormalOsId,
                    projectionNormalObject);
                renderer.SetPropertyBlock(properties);
                engravingSurfaces.Add(surface);
            }
        }

        private void ReplaceTexture(Texture2D texture)
        {
            stickerTexture = texture;
            stickerMaterial.mainTexture = stickerTexture;
            if (stickerMaterial.HasProperty("_BaseMap"))
            {
                stickerMaterial.SetTexture("_BaseMap", stickerTexture);
            }
        }

        private void SetEngravingActive(bool active)
        {
            if (stickerRoot != null)
            {
                stickerRoot.SetActive(active);
            }

            for (int index = 0; index < engravingSurfaces.Count; index++)
            {
                GameObject surface = engravingSurfaces[index];
                if (surface != null)
                {
                    surface.SetActive(active);
                }
            }
        }

        private void FailClosed()
        {
            appliedStickerId = ProductStickerCatalog.NoneId;
            SetEngravingActive(false);
        }

        private void DestroyConformalSurfaces()
        {
            for (int index = engravingSurfaces.Count - 1; index >= 0; index--)
            {
                DestroyObject(engravingSurfaces[index]);
            }
            engravingSurfaces.Clear();
        }

        private void OnDestroy()
        {
            DestroyConformalSurfaces();
            DestroyObject(stickerMaterial);
            if (stickerRoot != null)
            {
                DestroyObject(stickerRoot);
            }
        }

        private static void DestroyObject(UnityEngine.Object value)
        {
            if (value == null)
            {
                return;
            }

            if (Application.isPlaying)
            {
                Destroy(value);
            }
            else
            {
                DestroyImmediate(value);
            }
        }
    }

    public static class ProductAppearanceNativeBridge
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void CodexAppearanceEditorSetPresented(int presented);
#endif

        public static void SetPresented(bool presented)
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexAppearanceEditorSetPresented(presented ? 1 : 0);
#endif
        }
    }
}
