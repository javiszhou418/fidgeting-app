using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.Product
{
    public enum SpinnerGroundingStageShape
    {
        Round = 0,
        SoftSquare = 1,
        Oblong = 2
    }

    /// <summary>
    /// Resolves product bounds and the visual contact plane used by image-based
    /// lighting. Profiles with an authored ledge keep the procedural meshes
    /// disabled; legacy profiles can still render them. The object never owns a
    /// collider, rigidbody, or interaction state.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class SpinnerGroundingStage : MonoBehaviour
    {
        public const string ObjectName = "SpinnerGroundingStage";

        private const int SegmentCount = 64;
        private const int NormalTextureSize = 96;
        private static Texture2D sharedRoughStoneNormal;
        private static Texture2D sharedRoughStoneAlbedo;

        private Mesh stageMesh;
        private Material stageMaterial;
        private Mesh supportMesh;
        private Material supportMaterial;
        private Vector3 visiblePosition;
        private float retreatDistance;
        private float presentationVisibility = 1f;
        private float targetPresentationVisibility = 1f;
        private float transitionStartPresentationVisibility = 1f;
        private float presentationTransitionElapsed;
        private bool presentationTransitionActive;
        private bool usesBakedSupportSurface;

        public MeshRenderer StageRenderer { get; private set; }
        public MeshRenderer SupportRenderer { get; private set; }
        public IReadOnlyList<Renderer> ModelRenderers { get; private set; } =
            Array.Empty<Renderer>();
        public Bounds ModelBounds { get; private set; }
        public float TopY { get; private set; }
        public float SupportTopY { get; private set; }
        public float PresentationVisibility => presentationVisibility;

        public static SpinnerGroundingStage Install(SpinnerEnvironmentProfile profile)
        {
            Renderer[] modelRenderers = FindProductRenderers();
            if (modelRenderers.Length == 0)
            {
                Debug.LogWarning(
                    $"[FidgetingApp] No product renderers found for {profile.ModelId}; "
                    + "the grounding stage was not installed.");
                return null;
            }

            GameObject existing = GameObject.Find(ObjectName);
            SpinnerGroundingStage stage = existing != null
                ? existing.GetComponent<SpinnerGroundingStage>()
                : null;
            if (stage == null)
            {
                GameObject stageObject = existing ?? new GameObject(ObjectName);
                stage = stageObject.AddComponent<SpinnerGroundingStage>();
            }

            stage.Configure(profile, modelRenderers);
            return stage;
        }

        public void SetLightingColors(
            Color environmentStoneColor,
            Color modelBounceColor,
            float modelBounceStrength)
        {
            if (StageRenderer == null)
            {
                return;
            }

            Color neutralStone = new Color(0.092f, 0.095f, 0.091f, 1f);
            Color environmentTint = ClampStoneColor(environmentStoneColor);
            Color bounceTint = ClampStoneColor(modelBounceColor);
            // The shelf is part of the canyon: its hue/value is driven by the
            // sampled ground palette, with only a small neutral stabilizer.
            Color baseColor = Color.Lerp(environmentTint, neutralStone, 0.12f);
            baseColor = Color.Lerp(
                baseColor,
                bounceTint,
                Mathf.Clamp01(modelBounceStrength) * 0.055f);
            baseColor.a = 1f;

            var properties = new MaterialPropertyBlock();
            StageRenderer.GetPropertyBlock(properties);
            properties.SetColor("_BaseColor", baseColor);
            StageRenderer.SetPropertyBlock(properties);

            if (SupportRenderer != null)
            {
                Color supportColor = Color.Lerp(
                    baseColor,
                    environmentTint,
                    0.64f);
                supportColor = Color.Lerp(
                    supportColor,
                    bounceTint,
                    Mathf.Clamp01(modelBounceStrength) * 0.045f);
                supportColor.a = 1f;
                var supportProperties = new MaterialPropertyBlock();
                SupportRenderer.GetPropertyBlock(supportProperties);
                supportProperties.SetColor("_BaseColor", supportColor);
                SupportRenderer.SetPropertyBlock(supportProperties);
            }
        }

        public void SetLibraryPreviewActive(bool active, bool immediate = false)
        {
            float targetVisibility = active ? 1f : 0f;
            if (immediate)
            {
                presentationTransitionActive = false;
                targetPresentationVisibility = targetVisibility;
                presentationVisibility = targetVisibility;
                ApplyPresentationVisibility();
                return;
            }

            if (Mathf.Approximately(
                    targetPresentationVisibility,
                    targetVisibility))
            {
                return;
            }

            transitionStartPresentationVisibility = presentationVisibility;
            targetPresentationVisibility = targetVisibility;
            presentationTransitionElapsed = 0f;
            presentationTransitionActive = true;
        }

        public void SetDetailEntranceProgressForPreview(float progress)
        {
            presentationTransitionActive = false;
            presentationVisibility = 1f - Mathf.Clamp01(progress);
            targetPresentationVisibility = presentationVisibility;
            ApplyPresentationVisibility();
        }

        public static Renderer[] FindProductRenderers()
        {
            var unique = new HashSet<Renderer>();
            Rigidbody[] bodies = FindObjectsByType<Rigidbody>(
                FindObjectsInactive.Exclude,
                FindObjectsSortMode.None);
            for (int bodyIndex = 0; bodyIndex < bodies.Length; bodyIndex++)
            {
                Rigidbody body = bodies[bodyIndex];
                if (body == null || !body.gameObject.scene.IsValid())
                {
                    continue;
                }

                Renderer[] renderers = body.GetComponentsInChildren<Renderer>(false);
                for (int rendererIndex = 0; rendererIndex < renderers.Length; rendererIndex++)
                {
                    Renderer renderer = renderers[rendererIndex];
                    if (renderer != null
                        && renderer.enabled
                        && !(renderer is ParticleSystemRenderer)
                        && !(renderer is LineRenderer))
                    {
                        unique.Add(renderer);
                    }
                }
            }

            if (unique.Count == 0)
            {
                FidgetingApp.EDC.EdcSliderController slider =
                    FindAnyObjectByType<FidgetingApp.EDC.EdcSliderController>();
                if (slider != null)
                {
                    Renderer[] renderers = slider.GetComponentsInChildren<Renderer>(false);
                    for (int index = 0; index < renderers.Length; index++)
                    {
                        Renderer renderer = renderers[index];
                        if (renderer != null
                            && renderer.enabled
                            && !(renderer is ParticleSystemRenderer)
                            && !(renderer is LineRenderer))
                        {
                            unique.Add(renderer);
                        }
                    }
                }
            }

            if (unique.Count == 0)
            {
                FidgetingApp.FanCard.FanCardController fanCard =
                    FindAnyObjectByType<FidgetingApp.FanCard.FanCardController>();
                if (fanCard != null)
                {
                    Renderer[] renderers = fanCard.GetComponentsInChildren<Renderer>(false);
                    for (int index = 0; index < renderers.Length; index++)
                    {
                        Renderer renderer = renderers[index];
                        if (renderer != null
                            && renderer.enabled
                            && !(renderer is ParticleSystemRenderer)
                            && !(renderer is LineRenderer))
                        {
                            unique.Add(renderer);
                        }
                    }
                }
            }

            return unique.ToArray();
        }

        public static Bounds CombineBounds(IReadOnlyList<Renderer> renderers)
        {
            if (renderers == null || renderers.Count == 0)
            {
                return new Bounds(Vector3.zero, Vector3.one);
            }

            Bounds bounds = renderers[0].bounds;
            for (int index = 1; index < renderers.Count; index++)
            {
                bounds.Encapsulate(renderers[index].bounds);
            }
            return bounds;
        }

        private void Configure(
            SpinnerEnvironmentProfile profile,
            Renderer[] modelRenderers)
        {
            ModelRenderers = modelRenderers;
            ModelBounds = CombineBounds(modelRenderers);
            usesBakedSupportSurface = profile.UsesBakedSupportSurface;

            float planarSize = Mathf.Max(ModelBounds.size.x, ModelBounds.size.z);
            float stageWidth = Mathf.Max(
                planarSize * 0.72f,
                ModelBounds.size.x * profile.StageScale);
            float stageDepth = Mathf.Max(
                planarSize * 0.72f,
                ModelBounds.size.z * profile.StageScale);
            if (profile.StageShape == SpinnerGroundingStageShape.Round)
            {
                float diameter = Mathf.Max(stageWidth, stageDepth);
                stageWidth = diameter;
                stageDepth = diameter;
            }
            else if (profile.StageShape == SpinnerGroundingStageShape.Oblong)
            {
                float longAxis = Mathf.Max(stageWidth, stageDepth);
                float shortAxis = Mathf.Min(stageWidth, stageDepth);
                shortAxis = Mathf.Max(shortAxis, longAxis * 0.58f);
                if (stageWidth >= stageDepth)
                {
                    stageWidth = longAxis;
                    stageDepth = shortAxis;
                }
                else
                {
                    stageWidth = shortAxis;
                    stageDepth = longAxis;
                }
            }

            // A broad, shallow shelf reads as the canyon floor continuing
            // toward camera instead of a separate product pedestal.
            stageWidth *= 1.22f;
            stageDepth *= 1.36f;

            float thickness = Mathf.Max(
                planarSize * Mathf.Min(profile.StageThicknessRatio, 0.065f),
                ModelBounds.size.y * 0.18f);
            float contactGap = Mathf.Max(
                planarSize * 0.006f,
                ModelBounds.size.y * 0.025f);
            float supportHeight = Mathf.Max(
                planarSize * 0.024f,
                ModelBounds.size.y * 0.16f);
            TopY = ModelBounds.min.y - contactGap - supportHeight;
            SupportTopY = TopY + supportHeight;

            Vector3 stageCenter = ModelBounds.center;
            Camera presentationCamera = Camera.main ?? FindAnyObjectByType<Camera>();
            if (presentationCamera != null)
            {
                Vector3 towardViewer =
                    presentationCamera.transform.position - ModelBounds.center;
                towardViewer.y = 0f;
                if (towardViewer.sqrMagnitude > 0.000001f)
                {
                    stageCenter += towardViewer.normalized * planarSize * 0.19f;
                }
            }

            visiblePosition = new Vector3(
                stageCenter.x,
                TopY - thickness * 0.5f,
                stageCenter.z);
            retreatDistance = Mathf.Max(planarSize * 1.35f, ModelBounds.size.y * 2.8f);
            transform.position = visiblePosition;
            transform.rotation = Quaternion.identity;
            transform.localScale = Vector3.one;

            RebuildMesh(profile.StageShape, stageWidth, stageDepth, thickness);
            EnsureRenderer();
            EnsureSupport(
                planarSize,
                supportHeight,
                thickness,
                new Vector2(
                    ModelBounds.center.x - stageCenter.x,
                    ModelBounds.center.z - stageCenter.z));
            StageRenderer.sharedMaterial = stageMaterial;
            StageRenderer.shadowCastingMode = ShadowCastingMode.On;
            StageRenderer.receiveShadows = true;
            StageRenderer.lightProbeUsage = LightProbeUsage.Off;
            StageRenderer.reflectionProbeUsage = ReflectionProbeUsage.BlendProbes;
            StageRenderer.motionVectorGenerationMode =
                MotionVectorGenerationMode.ForceNoMotion;
            StageRenderer.allowOcclusionWhenDynamic = false;
            gameObject.SetActive(true);
            ApplyPresentationVisibility();
        }

        private void EnsureRenderer()
        {
            MeshFilter filter = GetComponent<MeshFilter>();
            if (filter == null)
            {
                filter = gameObject.AddComponent<MeshFilter>();
            }
            filter.sharedMesh = stageMesh;

            StageRenderer = GetComponent<MeshRenderer>();
            if (StageRenderer == null)
            {
                StageRenderer = gameObject.AddComponent<MeshRenderer>();
            }

            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null)
            {
                throw new MissingReferenceException(
                    "URP Lit is required for the realtime grounding stage.");
            }

            if (stageMaterial != null)
            {
                DestroyRuntimeObject(stageMaterial);
            }
            stageMaterial = new Material(shader)
            {
                name = "SpinnerGroundingStageMaterial_Runtime"
            };
            stageMaterial.SetColor("_BaseColor", new Color(0.10f, 0.105f, 0.10f, 1f));
            stageMaterial.SetFloat("_Metallic", 0f);
            stageMaterial.SetFloat("_Smoothness", 0.018f);
            stageMaterial.SetFloat("_SpecularHighlights", 0f);
            stageMaterial.EnableKeyword("_SPECULARHIGHLIGHTS_OFF");
            stageMaterial.SetTexture("_BaseMap", GetOrCreateRoughStoneAlbedo());
            stageMaterial.SetTexture("_BumpMap", GetOrCreateRoughStoneNormal());
            stageMaterial.SetFloat("_BumpScale", 0.13f);
            stageMaterial.EnableKeyword("_NORMALMAP");
        }

        private void EnsureSupport(
            float planarSize,
            float supportHeight,
            float stageThickness,
            Vector2 supportOffset)
        {
            Transform supportTransform = transform.Find("SpinnerCenterSupport");
            GameObject supportObject;
            if (supportTransform == null)
            {
                supportObject = new GameObject("SpinnerCenterSupport");
                supportObject.transform.SetParent(transform, false);
            }
            else
            {
                supportObject = supportTransform.gameObject;
            }

            float diameter = Mathf.Max(
                planarSize * 0.30f,
                ModelBounds.size.y * 1.05f);
            DestroyRuntimeObject(supportMesh);
            supportMesh = CreateStageMesh(
                SpinnerGroundingStageShape.Round,
                diameter,
                diameter,
                supportHeight);
            supportMesh.name = "SpinnerCenterSupportMesh_Runtime";

            MeshFilter filter = supportObject.GetComponent<MeshFilter>();
            if (filter == null)
            {
                filter = supportObject.AddComponent<MeshFilter>();
            }
            filter.sharedMesh = supportMesh;

            SupportRenderer = supportObject.GetComponent<MeshRenderer>();
            if (SupportRenderer == null)
            {
                SupportRenderer = supportObject.AddComponent<MeshRenderer>();
            }

            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null)
            {
                throw new MissingReferenceException(
                    "URP Lit is required for the realtime center support.");
            }
            DestroyRuntimeObject(supportMaterial);
            supportMaterial = new Material(shader)
            {
                name = "SpinnerCenterSupportMaterial_Runtime"
            };
            supportMaterial.SetColor("_BaseColor", new Color(0.075f, 0.078f, 0.074f, 1f));
            supportMaterial.SetFloat("_Metallic", 0f);
            supportMaterial.SetFloat("_Smoothness", 0.018f);
            supportMaterial.SetFloat("_SpecularHighlights", 0f);
            supportMaterial.EnableKeyword("_SPECULARHIGHLIGHTS_OFF");
            supportMaterial.SetTexture("_BaseMap", GetOrCreateRoughStoneAlbedo());
            supportMaterial.SetTexture("_BumpMap", GetOrCreateRoughStoneNormal());
            supportMaterial.SetFloat("_BumpScale", 0.10f);
            supportMaterial.EnableKeyword("_NORMALMAP");
            SupportRenderer.sharedMaterial = supportMaterial;
            SupportRenderer.shadowCastingMode = ShadowCastingMode.On;
            SupportRenderer.receiveShadows = true;
            SupportRenderer.lightProbeUsage = LightProbeUsage.Off;
            SupportRenderer.reflectionProbeUsage = ReflectionProbeUsage.BlendProbes;
            SupportRenderer.motionVectorGenerationMode =
                MotionVectorGenerationMode.ForceNoMotion;

            supportObject.transform.localPosition = new Vector3(
                supportOffset.x,
                stageThickness * 0.5f + supportHeight * 0.5f,
                supportOffset.y);
            supportObject.transform.localRotation = Quaternion.identity;
            supportObject.transform.localScale = Vector3.one;
        }

        private void LateUpdate()
        {
            if (presentationTransitionActive)
            {
                presentationTransitionElapsed += Mathf.Max(
                    0f,
                    Time.unscaledDeltaTime);
                float progress = SpinnerPresentationTransition.ResolveProgress(
                    presentationTransitionElapsed);
                presentationVisibility = Mathf.Lerp(
                    transitionStartPresentationVisibility,
                    targetPresentationVisibility,
                    progress);
                if (progress >= 1f)
                {
                    presentationVisibility = targetPresentationVisibility;
                    presentationTransitionActive = false;
                }
            }
            ApplyPresentationVisibility();
        }

        private void ApplyPresentationVisibility()
        {
            float eased = presentationVisibility * presentationVisibility
                * (3f - 2f * presentationVisibility);
            transform.position = visiblePosition + Vector3.down * ((1f - eased) * retreatDistance);
            transform.localScale = Vector3.one * Mathf.Lerp(1.08f, 1f, eased);
            // The approved unified canyon plate already contains the ledge.
            // Keep this object as invisible bounds/lighting metadata so image-
            // based lighting still samples the model, but never draw a second
            // procedural platform over the photographed rock surface.
            bool visible = !usesBakedSupportSurface
                && presentationVisibility > 0.01f;
            if (StageRenderer != null)
            {
                StageRenderer.enabled = visible;
            }
            if (SupportRenderer != null)
            {
                SupportRenderer.enabled = visible;
            }
        }

        private void RebuildMesh(
            SpinnerGroundingStageShape shape,
            float width,
            float depth,
            float thickness)
        {
            if (stageMesh != null)
            {
                DestroyRuntimeObject(stageMesh);
            }

            stageMesh = CreateStageMesh(shape, width, depth, thickness);
            stageMesh.name = "SpinnerGroundingStageMesh_Runtime";
        }

        public static Mesh CreateStageMesh(
            SpinnerGroundingStageShape shape,
            float width,
            float depth,
            float thickness)
        {
            float exponent = shape == SpinnerGroundingStageShape.SoftSquare
                ? 4.4f
                : shape == SpinnerGroundingStageShape.Oblong
                    ? 3.2f
                    : 2.0f;
            float halfWidth = Mathf.Max(0.001f, width * 0.5f);
            float halfDepth = Mathf.Max(0.001f, depth * 0.5f);
            float halfHeight = Mathf.Max(0.0005f, thickness * 0.5f);

            var vertices = new List<Vector3>(1 + SegmentCount * 3);
            var uvs = new List<Vector2>(1 + SegmentCount * 3);
            var triangles = new List<int>(SegmentCount * 15);

            vertices.Add(new Vector3(0f, halfHeight, 0f));
            uvs.Add(new Vector2(0.5f, 0.5f));

            for (int ring = 0; ring < 3; ring++)
            {
                float ringY = ring == 0
                    ? halfHeight
                    : ring == 1
                        ? halfHeight * 0.48f
                        : -halfHeight;
                float ringScale = ring == 0 ? 0.93f : ring == 1 ? 1f : 0.965f;
                for (int segment = 0; segment < SegmentCount; segment++)
                {
                    float angle = segment * Mathf.PI * 2f / SegmentCount;
                    float cosine = Mathf.Cos(angle);
                    float sine = Mathf.Sin(angle);
                    float power = 2f / exponent;
                    float x = Mathf.Sign(cosine)
                        * Mathf.Pow(Mathf.Abs(cosine), power)
                        * halfWidth;
                    float z = Mathf.Sign(sine)
                        * Mathf.Pow(Mathf.Abs(sine), power)
                        * halfDepth;
                    float irregularity = 1f
                        + Mathf.Sin(angle * 5f + 0.7f) * 0.010f
                        + Mathf.Sin(angle * 11f + 1.9f) * 0.006f;
                    vertices.Add(new Vector3(
                        x * ringScale * irregularity,
                        ringY + Mathf.Sin(angle * 7f) * halfHeight * 0.018f,
                        z * ringScale * irregularity));
                    uvs.Add(new Vector2(
                        x / (halfWidth * 2f) + 0.5f,
                        z / (halfDepth * 2f) + 0.5f));
                }
            }

            int topStart = 1;
            int bevelStart = topStart + SegmentCount;
            int bottomStart = bevelStart + SegmentCount;
            for (int segment = 0; segment < SegmentCount; segment++)
            {
                int next = (segment + 1) % SegmentCount;
                triangles.Add(0);
                triangles.Add(topStart + next);
                triangles.Add(topStart + segment);
                AddQuad(triangles,
                    topStart + segment,
                    topStart + next,
                    bevelStart + next,
                    bevelStart + segment);
                AddQuad(triangles,
                    bevelStart + segment,
                    bevelStart + next,
                    bottomStart + next,
                    bottomStart + segment);
            }

            var mesh = new Mesh();
            mesh.SetVertices(vertices);
            mesh.SetUVs(0, uvs);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateTangents();
            mesh.RecalculateBounds();
            return mesh;
        }

        private static void AddQuad(
            ICollection<int> triangles,
            int topLeft,
            int topRight,
            int bottomRight,
            int bottomLeft)
        {
            triangles.Add(topLeft);
            triangles.Add(topRight);
            triangles.Add(bottomRight);
            triangles.Add(topLeft);
            triangles.Add(bottomRight);
            triangles.Add(bottomLeft);
        }

        private static Texture2D GetOrCreateRoughStoneNormal()
        {
            if (sharedRoughStoneNormal != null)
            {
                return sharedRoughStoneNormal;
            }

            float[,] height = new float[NormalTextureSize, NormalTextureSize];
            for (int y = 0; y < NormalTextureSize; y++)
            {
                for (int x = 0; x < NormalTextureSize; x++)
                {
                    float u = (float)x / NormalTextureSize;
                    float v = (float)y / NormalTextureSize;
                    height[x, y] = Mathf.PerlinNoise(u * 8.5f + 0.37f, v * 8.5f + 1.19f)
                        * 0.62f
                        + Mathf.PerlinNoise(u * 23f + 3.1f, v * 23f + 0.4f)
                        * 0.38f;
                }
            }

            sharedRoughStoneNormal = new Texture2D(
                NormalTextureSize,
                NormalTextureSize,
                TextureFormat.RGBA32,
                true,
                true)
            {
                name = "SpinnerRoughStoneNormal_Runtime",
                wrapMode = TextureWrapMode.Repeat,
                filterMode = FilterMode.Bilinear
            };
            var pixels = new Color[NormalTextureSize * NormalTextureSize];
            for (int y = 0; y < NormalTextureSize; y++)
            {
                for (int x = 0; x < NormalTextureSize; x++)
                {
                    float left = height[(x - 1 + NormalTextureSize) % NormalTextureSize, y];
                    float right = height[(x + 1) % NormalTextureSize, y];
                    float down = height[x, (y - 1 + NormalTextureSize) % NormalTextureSize];
                    float up = height[x, (y + 1) % NormalTextureSize];
                    Vector3 normal = new Vector3(
                        (left - right) * 2.8f,
                        (down - up) * 2.8f,
                        1f).normalized;
                    pixels[y * NormalTextureSize + x] = new Color(
                        normal.x * 0.5f + 0.5f,
                        normal.y * 0.5f + 0.5f,
                        normal.z * 0.5f + 0.5f,
                        normal.x * 0.5f + 0.5f);
                }
            }
            sharedRoughStoneNormal.SetPixels(pixels);
            sharedRoughStoneNormal.Apply(true, true);
            return sharedRoughStoneNormal;
        }

        private static Texture2D GetOrCreateRoughStoneAlbedo()
        {
            if (sharedRoughStoneAlbedo != null)
            {
                return sharedRoughStoneAlbedo;
            }

            sharedRoughStoneAlbedo = new Texture2D(
                NormalTextureSize,
                NormalTextureSize,
                TextureFormat.RGBA32,
                true,
                true)
            {
                name = "SpinnerRoughStoneAlbedo_Runtime",
                wrapMode = TextureWrapMode.Repeat,
                filterMode = FilterMode.Trilinear
            };
            var pixels = new Color[NormalTextureSize * NormalTextureSize];
            for (int y = 0; y < NormalTextureSize; y++)
            {
                for (int x = 0; x < NormalTextureSize; x++)
                {
                    float u = (float)x / NormalTextureSize;
                    float v = (float)y / NormalTextureSize;
                    float broad = Mathf.PerlinNoise(u * 7.2f + 0.8f, v * 7.2f + 2.1f);
                    float grain = Mathf.PerlinNoise(u * 31f + 1.3f, v * 31f + 4.7f);
                    float value = Mathf.Lerp(0.58f, 0.90f, broad * 0.78f + grain * 0.22f);
                    pixels[y * NormalTextureSize + x] = new Color(
                        value * 0.96f,
                        value * 0.98f,
                        value,
                        1f);
                }
            }
            sharedRoughStoneAlbedo.SetPixels(pixels);
            sharedRoughStoneAlbedo.Apply(true, true);
            return sharedRoughStoneAlbedo;
        }

        private static Color ClampStoneColor(Color source)
        {
            Color.RGBToHSV(source, out float hue, out float saturation, out float value);
            saturation = Mathf.Min(saturation, 0.32f);
            value = Mathf.Clamp(value, 0.055f, 0.24f);
            Color result = Color.HSVToRGB(hue, saturation, value);
            result.a = 1f;
            return result;
        }

        private void OnDestroy()
        {
            DestroyRuntimeObject(stageMaterial);
            DestroyRuntimeObject(stageMesh);
            DestroyRuntimeObject(supportMaterial);
            DestroyRuntimeObject(supportMesh);
        }

        private static void DestroyRuntimeObject(UnityEngine.Object value)
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
}
