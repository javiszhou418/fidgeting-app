using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.Product
{
    /// <summary>
    /// Purely visual progression assembly shared by every product model.
    /// It creates no colliders or rigidbodies and never changes spinner physics.
    /// All dimensions are derived from the current rotor's renderer bounds.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class SpinnerProgressionVisuals : MonoBehaviour
    {
        public const string VisualRootName = "ProgressionVisuals";

        private const int TorusSegments = 48;
        private const int TorusSides = 8;
        private const int BearingBallCount = 8;
        private const int BearingBallLongitudeSegments = 16;
        private const int BearingBallLatitudeSegments = 8;

        private static readonly Color[] StageColors =
        {
            new Color(0.42f, 0.46f, 0.52f, 1f),
            new Color(0.62f, 0.66f, 0.70f, 1f),
            new Color(0.34f, 0.38f, 0.43f, 1f),
            new Color(0.36f, 0.48f, 0.58f, 1f),
            new Color(0.78f, 0.81f, 0.85f, 1f)
        };

        private static readonly float[] StageMetallic = { 0.82f, 1f, 1f, 0.95f, 1f };
        private static readonly float[] StageSmoothness = { 0.55f, 0.72f, 0.86f, 0.80f, 0.96f };

        private readonly List<Mesh> generatedMeshes = new List<Mesh>();
        private readonly List<Material> generatedMaterials = new List<Material>();
        private readonly List<Renderer> upgradeRenderers = new List<Renderer>();
        private readonly List<Renderer> bearingBallRenderers = new List<Renderer>();

        private GameObject visualRoot;
        private GameObject weightRing;
        private GameObject auxiliaryBearings;
        private GameObject lowResistanceCage;
        private GameObject finalCrown;
        private Material[] stageMaterials;
        private Material ceramicMaterial;
        private int activeStageIndex = -1;
        private string activeModelId = string.Empty;
        private bool initialized;

        public int ActiveStageIndex => activeStageIndex;
        public string ActiveModelId => activeModelId;
        public string ActiveMaterialName => activeStageIndex >= 0 && stageMaterials != null
            ? stageMaterials[activeStageIndex].name
            : string.Empty;
        public bool WeightRingVisible => weightRing != null && weightRing.activeSelf;
        public bool AuxiliaryBearingsVisible =>
            auxiliaryBearings != null && auxiliaryBearings.activeSelf;
        public bool LowResistanceCageVisible =>
            lowResistanceCage != null && lowResistanceCage.activeSelf;
        public bool FinalCrownVisible => finalCrown != null && finalCrown.activeSelf;
        public int GeneratedColliderCount => visualRoot != null
            ? visualRoot.GetComponentsInChildren<Collider>(true).Length
            : 0;

        public static int StageIndexForLevel(int level)
        {
            IReadOnlyList<SpinnerUpgradeStage> stages = SpinnerProgressionRules.Stages;
            int active = 0;
            for (int index = 1; index < stages.Count; index++)
            {
                if (level < stages[index].LevelThreshold)
                {
                    break;
                }

                active = index;
            }

            return active;
        }

        public void Apply(string modelId, int level)
        {
            activeModelId = modelId ?? string.Empty;
            EnsureBuilt();
            int nextStage = StageIndexForLevel(level);
            if (nextStage == activeStageIndex)
            {
                return;
            }

            activeStageIndex = nextStage;
            Material stageMaterial = stageMaterials[activeStageIndex];
            for (int index = 0; index < upgradeRenderers.Count; index++)
            {
                Renderer renderer = upgradeRenderers[index];
                if (renderer != null)
                {
                    renderer.sharedMaterial = stageMaterial;
                }
            }

            Material ballMaterial = activeStageIndex >= 4
                ? ceramicMaterial
                : stageMaterial;
            for (int index = 0; index < bearingBallRenderers.Count; index++)
            {
                Renderer renderer = bearingBallRenderers[index];
                if (renderer != null)
                {
                    renderer.sharedMaterial = ballMaterial;
                }
            }

            weightRing.SetActive(activeStageIndex >= 1);
            auxiliaryBearings.SetActive(activeStageIndex >= 2);
            lowResistanceCage.SetActive(activeStageIndex >= 3);
            finalCrown.SetActive(activeStageIndex >= 4);
        }

        private void EnsureBuilt()
        {
            if (initialized)
            {
                return;
            }

            initialized = true;
            Bounds localBounds = CalculateLocalBounds();
            float radius = Mathf.Max(0.01f, Mathf.Max(localBounds.extents.x, localBounds.extents.z));
            float hubRadius = radius * HubRadiusRatio(activeModelId);
            float thickness = Mathf.Max(radius * 0.08f, localBounds.size.y);
            float surfaceOffset = Mathf.Max(radius * 0.008f, thickness * 0.035f);
            float topSurface = localBounds.max.y;
            float bottomSurface = localBounds.min.y;
            IncludeActiveStaticHubVerticalBounds(ref topSurface, ref bottomSurface);
            float top = topSurface + surfaceOffset;
            float bottom = bottomSurface - surfaceOffset;

            visualRoot = new GameObject(VisualRootName);
            visualRoot.layer = gameObject.layer;
            visualRoot.transform.SetParent(transform, false);

            CreateMaterials();

            // A small collar remains visible through all five stages, making
            // every material tier a real visual change rather than UI copy.
            CreateTorus(
                "StageMaterialCollar",
                visualRoot.transform,
                hubRadius * 0.82f,
                hubRadius * 0.035f,
                top,
                true);

            weightRing = CreateGroup("Lv20_PrecisionWeightRing");
            CreateTorus(
                "PrecisionSteelWeightRing",
                weightRing.transform,
                hubRadius * 1.13f,
                hubRadius * 0.07f,
                top + surfaceOffset * 0.25f,
                true);

            auxiliaryBearings = CreateGroup("Lv50_DualAuxiliaryBearing");
            CreateTorus(
                "AuxiliaryBearingTop",
                auxiliaryBearings.transform,
                hubRadius * 0.68f,
                hubRadius * 0.055f,
                top + surfaceOffset * 0.55f,
                true);
            CreateTorus(
                "AuxiliaryBearingBottom",
                auxiliaryBearings.transform,
                hubRadius * 0.68f,
                hubRadius * 0.055f,
                bottom - surfaceOffset * 0.25f,
                true);

            lowResistanceCage = CreateGroup("Lv75_LowResistanceCage");
            CreateTorus(
                "TitaniumBearingCage",
                lowResistanceCage.transform,
                hubRadius * 0.86f,
                hubRadius * 0.03f,
                top + surfaceOffset * 0.85f,
                true);
            CreateBearingBalls(
                lowResistanceCage.transform,
                hubRadius * 0.86f,
                hubRadius * 0.08f,
                top + surfaceOffset * 0.85f);

            finalCrown = CreateGroup("Lv100_CeramicMirrorFinale");
            CreateTorus(
                "MirrorSteelCrown",
                finalCrown.transform,
                hubRadius * 1.28f,
                hubRadius * 0.035f,
                top + surfaceOffset * 0.35f,
                true);

            weightRing.SetActive(false);
            auxiliaryBearings.SetActive(false);
            lowResistanceCage.SetActive(false);
            finalCrown.SetActive(false);
        }

        private Bounds CalculateLocalBounds()
        {
            Renderer[] renderers = GetComponentsInChildren<Renderer>(true);
            bool hasBounds = false;
            Bounds localBounds = new Bounds(Vector3.zero, new Vector3(0.1f, 0.01f, 0.1f));
            for (int index = 0; index < renderers.Length; index++)
            {
                Renderer renderer = renderers[index];
                if (renderer.transform.IsChildOf(transform)
                    && renderer.transform.name != VisualRootName)
                {
                    Bounds worldBounds = renderer.bounds;
                    Vector3 center = worldBounds.center;
                    Vector3 extents = worldBounds.extents;
                    for (int x = -1; x <= 1; x += 2)
                    {
                        for (int y = -1; y <= 1; y += 2)
                        {
                            for (int z = -1; z <= 1; z += 2)
                            {
                                Vector3 worldCorner = center + Vector3.Scale(
                                    extents,
                                    new Vector3(x, y, z));
                                Vector3 localCorner = transform.InverseTransformPoint(worldCorner);
                                if (!hasBounds)
                                {
                                    localBounds = new Bounds(localCorner, Vector3.zero);
                                    hasBounds = true;
                                }
                                else
                                {
                                    localBounds.Encapsulate(localCorner);
                                }
                            }
                        }
                    }
                }
            }

            return localBounds;
        }

        private void IncludeActiveStaticHubVerticalBounds(
            ref float topSurface,
            ref float bottomSurface)
        {
            Transform parent = transform.parent;
            Transform hub = parent != null ? parent.Find("HubStatic") : null;
            if (hub == null || !hub.gameObject.activeInHierarchy)
            {
                return;
            }

            Renderer[] renderers = hub.GetComponentsInChildren<Renderer>(false);
            for (int index = 0; index < renderers.Length; index++)
            {
                Bounds bounds = renderers[index].bounds;
                Vector3 center = bounds.center;
                Vector3 extents = bounds.extents;
                for (int x = -1; x <= 1; x += 2)
                {
                    for (int y = -1; y <= 1; y += 2)
                    {
                        for (int z = -1; z <= 1; z += 2)
                        {
                            Vector3 worldCorner = center + Vector3.Scale(
                                extents,
                                new Vector3(x, y, z));
                            float localY = transform.InverseTransformPoint(worldCorner).y;
                            topSurface = Mathf.Max(topSurface, localY);
                            bottomSurface = Mathf.Min(bottomSurface, localY);
                        }
                    }
                }
            }
        }

        private GameObject CreateGroup(string groupName)
        {
            GameObject group = new GameObject(groupName);
            group.layer = gameObject.layer;
            group.transform.SetParent(visualRoot.transform, false);
            return group;
        }

        private Renderer CreateTorus(
            string objectName,
            Transform parent,
            float majorRadius,
            float tubeRadius,
            float localY,
            bool includeInStageMaterial)
        {
            GameObject ring = new GameObject(objectName);
            ring.layer = gameObject.layer;
            ring.transform.SetParent(parent, false);
            ring.transform.localPosition = new Vector3(0f, localY, 0f);

            Mesh mesh = BuildTorusMesh(objectName + "Mesh", majorRadius, tubeRadius);
            generatedMeshes.Add(mesh);
            MeshFilter filter = ring.AddComponent<MeshFilter>();
            filter.sharedMesh = mesh;
            MeshRenderer renderer = ring.AddComponent<MeshRenderer>();
            ConfigureRenderer(renderer);
            renderer.sharedMaterial = stageMaterials[0];
            if (includeInStageMaterial)
            {
                upgradeRenderers.Add(renderer);
            }

            return renderer;
        }

        private void CreateBearingBalls(
            Transform parent,
            float orbitRadius,
            float ballRadius,
            float localY)
        {
            Mesh ballMesh = BuildSphereMesh(
                "ProgressionBearingBallMesh",
                BearingBallLongitudeSegments,
                BearingBallLatitudeSegments);
            generatedMeshes.Add(ballMesh);

            for (int index = 0; index < BearingBallCount; index++)
            {
                float angle = index * Mathf.PI * 2f / BearingBallCount;
                GameObject ball = new GameObject($"BearingBall_{index + 1:00}");
                ball.layer = gameObject.layer;
                ball.transform.SetParent(parent, false);
                ball.transform.localPosition = new Vector3(
                    Mathf.Cos(angle) * orbitRadius,
                    localY,
                    Mathf.Sin(angle) * orbitRadius);
                ball.transform.localScale = Vector3.one * ballRadius * 2f;

                MeshFilter filter = ball.AddComponent<MeshFilter>();
                filter.sharedMesh = ballMesh;
                MeshRenderer renderer = ball.AddComponent<MeshRenderer>();
                ConfigureRenderer(renderer);
                renderer.sharedMaterial = stageMaterials[0];
                bearingBallRenderers.Add(renderer);
            }
        }

        private void CreateMaterials()
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null)
            {
                shader = Shader.Find("Standard");
            }

            stageMaterials = new Material[SpinnerProgressionRules.Stages.Count];
            for (int index = 0; index < stageMaterials.Length; index++)
            {
                SpinnerUpgradeStage stage = SpinnerProgressionRules.Stages[index];
                Material material = new Material(shader)
                {
                    name = $"Progression_{stage.LevelThreshold:000}_{Sanitize(stage.MaterialName)}",
                    enableInstancing = true,
                    hideFlags = HideFlags.HideAndDontSave
                };
                SetPbr(material, StageColors[index], StageMetallic[index], StageSmoothness[index]);
                stageMaterials[index] = material;
                generatedMaterials.Add(material);
            }

            ceramicMaterial = new Material(shader)
            {
                name = "Progression_100_CeramicBearing",
                enableInstancing = true,
                hideFlags = HideFlags.HideAndDontSave
            };
            SetPbr(ceramicMaterial, new Color(0.92f, 0.94f, 0.98f, 1f), 0.08f, 0.92f);
            generatedMaterials.Add(ceramicMaterial);
        }

        private static void SetPbr(Material material, Color color, float metallic, float smoothness)
        {
            if (material.HasProperty("_BaseColor"))
            {
                material.SetColor("_BaseColor", color);
            }
            if (material.HasProperty("_Color"))
            {
                material.SetColor("_Color", color);
            }
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
        }

        private static void ConfigureRenderer(Renderer renderer)
        {
            renderer.shadowCastingMode = ShadowCastingMode.On;
            renderer.receiveShadows = true;
            renderer.lightProbeUsage = LightProbeUsage.Off;
            renderer.reflectionProbeUsage = ReflectionProbeUsage.BlendProbes;
            renderer.motionVectorGenerationMode = MotionVectorGenerationMode.ForceNoMotion;
        }

        private static Mesh BuildTorusMesh(string meshName, float majorRadius, float tubeRadius)
        {
            int vertexCount = TorusSegments * TorusSides;
            var vertices = new Vector3[vertexCount];
            var normals = new Vector3[vertexCount];
            var uvs = new Vector2[vertexCount];
            var triangles = new int[TorusSegments * TorusSides * 6];

            for (int segment = 0; segment < TorusSegments; segment++)
            {
                float u = segment * Mathf.PI * 2f / TorusSegments;
                Vector3 radial = new Vector3(Mathf.Cos(u), 0f, Mathf.Sin(u));
                for (int side = 0; side < TorusSides; side++)
                {
                    float v = side * Mathf.PI * 2f / TorusSides;
                    Vector3 normal = radial * Mathf.Cos(v) + Vector3.up * Mathf.Sin(v);
                    int vertex = segment * TorusSides + side;
                    vertices[vertex] = radial * majorRadius + normal * tubeRadius;
                    normals[vertex] = normal.normalized;
                    uvs[vertex] = new Vector2(
                        (float)segment / TorusSegments,
                        (float)side / TorusSides);
                }
            }

            int triangle = 0;
            for (int segment = 0; segment < TorusSegments; segment++)
            {
                int nextSegment = (segment + 1) % TorusSegments;
                for (int side = 0; side < TorusSides; side++)
                {
                    int nextSide = (side + 1) % TorusSides;
                    int a = segment * TorusSides + side;
                    int b = nextSegment * TorusSides + side;
                    int c = nextSegment * TorusSides + nextSide;
                    int d = segment * TorusSides + nextSide;
                    triangles[triangle++] = a;
                    triangles[triangle++] = c;
                    triangles[triangle++] = b;
                    triangles[triangle++] = a;
                    triangles[triangle++] = d;
                    triangles[triangle++] = c;
                }
            }

            var mesh = new Mesh
            {
                name = meshName,
                hideFlags = HideFlags.HideAndDontSave,
                vertices = vertices,
                normals = normals,
                uv = uvs,
                triangles = triangles
            };
            mesh.RecalculateBounds();
            return mesh;
        }

        private static Mesh BuildSphereMesh(
            string meshName,
            int longitudeSegments,
            int latitudeSegments)
        {
            longitudeSegments = Mathf.Max(8, longitudeSegments);
            latitudeSegments = Mathf.Max(4, latitudeSegments);
            int verticesPerRing = longitudeSegments + 1;
            var vertices = new Vector3[(latitudeSegments + 1) * verticesPerRing];
            var normals = new Vector3[vertices.Length];
            var uvs = new Vector2[vertices.Length];
            var triangles = new int[latitudeSegments * longitudeSegments * 6];

            int vertex = 0;
            for (int latitude = 0; latitude <= latitudeSegments; latitude++)
            {
                float v = latitude / (float)latitudeSegments;
                float polar = v * Mathf.PI;
                float ringRadius = Mathf.Sin(polar) * 0.5f;
                float y = Mathf.Cos(polar) * 0.5f;
                for (int longitude = 0; longitude <= longitudeSegments; longitude++)
                {
                    float u = longitude / (float)longitudeSegments;
                    float azimuth = u * Mathf.PI * 2f;
                    Vector3 position = new Vector3(
                        Mathf.Cos(azimuth) * ringRadius,
                        y,
                        Mathf.Sin(azimuth) * ringRadius);
                    vertices[vertex] = position;
                    normals[vertex] = position.normalized;
                    uvs[vertex] = new Vector2(u, 1f - v);
                    vertex++;
                }
            }

            int triangle = 0;
            for (int latitude = 0; latitude < latitudeSegments; latitude++)
            {
                int currentRing = latitude * verticesPerRing;
                int nextRing = currentRing + verticesPerRing;
                for (int longitude = 0; longitude < longitudeSegments; longitude++)
                {
                    int a = currentRing + longitude;
                    int b = nextRing + longitude;
                    int c = nextRing + longitude + 1;
                    int d = currentRing + longitude + 1;
                    triangles[triangle++] = a;
                    triangles[triangle++] = c;
                    triangles[triangle++] = b;
                    triangles[triangle++] = a;
                    triangles[triangle++] = d;
                    triangles[triangle++] = c;
                }
            }

            var mesh = new Mesh
            {
                name = meshName,
                hideFlags = HideFlags.HideAndDontSave,
                vertices = vertices,
                normals = normals,
                uv = uvs,
                triangles = triangles
            };
            mesh.RecalculateBounds();
            return mesh;
        }

        private static string Sanitize(string value)
        {
            return string.IsNullOrEmpty(value)
                ? "Material"
                : value.Replace(" ", string.Empty).Replace("+", "Plus");
        }

        private static float HubRadiusRatio(string modelId)
        {
            switch (modelId)
            {
                case "blue-classic":
                    return 0.11f;
                case "metal-three-blade":
                    return 0.29f;
                case "gold-four-wing":
                    return 0.23f;
                case "graphite-two-lobe":
                    return 0.24f;
                default:
                    return 0.22f;
            }
        }

        private void OnDestroy()
        {
            for (int index = 0; index < generatedMaterials.Count; index++)
            {
                ReleaseGeneratedObject(generatedMaterials[index]);
            }
            for (int index = 0; index < generatedMeshes.Count; index++)
            {
                ReleaseGeneratedObject(generatedMeshes[index]);
            }
        }

        private static void ReleaseGeneratedObject(Object target)
        {
            if (target == null)
            {
                return;
            }

            if (Application.isPlaying)
            {
                Object.Destroy(target);
            }
            else
            {
                Object.DestroyImmediate(target);
            }
        }
    }
}
