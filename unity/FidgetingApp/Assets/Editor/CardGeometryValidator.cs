using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using FidgetingApp.FanCard;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FidgetingApp.EditorTools
{
    /// <summary>
    /// Frozen geometry gate for the shipping magnetic fan-card scene.
    ///
    /// World X/Z AABBs are deliberately not used for layer overlap: the three
    /// cards are meant to overlap in plan while fanning around a common Y axis.
    /// Separation is measured along that spindle axis instead.
    /// </summary>
    public static class CardGeometryValidator
    {
        private static readonly string[] CardNames =
        {
            "BottomCard",
            "MiddleCard",
            "TopCard"
        };
        private const string BodyName = "GunmetalFrame";
        private const string FrontFaceName = "WarmSilverFace";
        private const string BackFaceName = "WarmSilverBackFace";
        private const float DimensionTolerance = 0.000025f;
        private const float PlaneTolerance = 0.000002f;
        // Cross products below are measured in square metres, so the linear
        // plane tolerance cannot be reused without swallowing millimetre-scale
        // hole triangles.
        private const float SignedAreaTolerance = 0.000000000001f;
        private const float WeldTolerance =
            FanCardSpecifications.VisualMeshWeldTolerance;
        private const float MinimumShaftClearance = 0.00010f;
        private const float MinimumLayerAirGap =
            FanCardSpecifications.LayerAirGap;

        private static readonly List<string> Report = new();
        private static int failureCount;

        [MenuItem("Tools/Codex/Fan Card/0 Validate Shipping Geometry")]
        public static void ValidateMenu()
        {
            bool passed = ValidateShippingScene();
            EditorUtility.DisplayDialog(
                "Fan-card geometry",
                passed ? "ALL PASS" : $"{failureCount} check(s) failed. See Console.",
                "OK");
        }

        // Batch entry point:
        // Unity -batchmode -projectPath ... -executeMethod
        // FidgetingApp.EditorTools.CardGeometryValidator.ValidateBatch
        public static void ValidateBatch()
        {
            bool passed = ValidateShippingScene();
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string logFolder = Path.Combine(projectRoot, "Logs");
            Directory.CreateDirectory(logFolder);
            File.WriteAllLines(
                Path.Combine(logFolder, "CardGeometryValidation.log"),
                Report);
            if (!passed)
            {
                throw new InvalidDataException(
                    $"Fan-card geometry validation failed ({failureCount} checks)." );
            }
        }

        public static bool ValidateShippingScene()
        {
            EditorSceneManager.OpenScene(
                FanCardSpecifications.ScenePath,
                OpenSceneMode.Single);
            Report.Clear();
            failureCount = 0;
            Write("=== FAN CARD GEOMETRY VALIDATION ===");
            Write($"Scene: {FanCardSpecifications.ScenePath}");
            Write(
                "Frozen thresholds: "
                + $"thickness={Millimetres(FanCardSpecifications.CardThickness)}, "
                + $"air-gap>={Millimetres(MinimumLayerAirGap)}, "
                + $"shaft-clearance>={Millimetres(MinimumShaftClearance)}");

            GameObject root = GameObject.Find("MagneticFanCard_Root");
            Check(root != null, "Shipping root exists");
            if (root == null)
            {
                Finish();
                return false;
            }

            Check(
                root.GetComponentsInChildren<Cloth>(true).Length == 0,
                "No cloth/soft-body components");
            Check(
                root.GetComponentsInChildren<SkinnedMeshRenderer>(true).Length == 0,
                "No deforming skinned meshes");

            var cards = new List<CardRecord>();
            foreach (string cardName in CardNames)
            {
                Transform card = root.transform.Find(cardName);
                Check(card != null, $"{cardName}: root exists");
                if (card == null)
                {
                    continue;
                }
                CardRecord record = ValidateCard(card);
                if (record != null)
                {
                    cards.Add(record);
                }
            }

            ValidateLayerSeparation(cards);
            ValidateCommonAxis(root.transform, cards);
            ValidateVisibleAxisHardware(root.transform);
            Finish();
            return failureCount == 0;
        }

        private static CardRecord ValidateCard(Transform card)
        {
            Transform bodyTransform = card.Find(BodyName);
            Check(bodyTransform != null, $"{card.name}: {BodyName} exists");
            if (bodyTransform == null)
            {
                return null;
            }

            MeshFilter filter = bodyTransform.GetComponent<MeshFilter>();
            MeshRenderer renderer = bodyTransform.GetComponent<MeshRenderer>();
            Check(filter != null && filter.sharedMesh != null,
                $"{card.name}: body mesh is assigned");
            Check(renderer != null, $"{card.name}: body renderer exists");
            if (filter == null || filter.sharedMesh == null || renderer == null)
            {
                return null;
            }

            Mesh mesh = filter.sharedMesh;
            Vector3 size = mesh.bounds.size;
            CheckNear(size.x, FanCardSpecifications.CardWidth,
                $"{card.name}: solid width");
            CheckNear(size.z, FanCardSpecifications.CardHeight,
                $"{card.name}: solid height");
            CheckNear(size.y, FanCardSpecifications.CardThickness,
                $"{card.name}: solid thickness");
            Check(mesh.vertexCount >= 128,
                $"{card.name}: sufficient rounded/bevel/hole topology ({mesh.vertexCount} vertices)");
            Check(mesh.subMeshCount >= 1,
                $"{card.name}: triangle surface exists");
            Check(IsFiniteAndRigid(mesh),
                $"{card.name}: vertices are finite and confined to a rigid slab");
            Check(IsClosedWeldedManifold(mesh, out string manifoldDetail),
                $"{card.name}: watertight two-sided solid ({manifoldDetail})");
            Check(IsIdentityScale(bodyTransform.localScale),
                $"{card.name}: body has no non-uniform scale");

            ValidateProjectedFace(card, FrontFaceName);
            ValidateProjectedFace(card, BackFaceName);

            return new CardRecord(card, mesh, renderer);
        }

        private static void ValidateProjectedFace(Transform card, string faceName)
        {
            Transform face = card.Find(faceName);
            Check(face != null, $"{card.name}: {faceName} exists");
            if (face == null)
            {
                return;
            }
            MeshFilter filter = face.GetComponent<MeshFilter>();
            Check(filter != null && filter.sharedMesh != null,
                $"{card.name}: {faceName} mesh is assigned");
            if (filter == null || filter.sharedMesh == null)
            {
                return;
            }

            Mesh mesh = filter.sharedMesh;
            bool flat = mesh.vertices.All(vertex => Mathf.Abs(vertex.y) <= PlaneTolerance);
            Check(flat, $"{card.name}: {faceName} is a flat projection");
            Check(
                HasConsistentPositiveFacingTriangles(mesh, out string facingDetail),
                $"{card.name}: {faceName} has no folded/inverted triangles ({facingDetail})");
            Check(
                AllVerticesInsideRoundedFace(mesh, out int outsideCount),
                $"{card.name}: {faceName} stays inside its rounded panel ({outsideCount} outside vertices)");
        }

        private static void ValidateLayerSeparation(List<CardRecord> cards)
        {
            if (cards.Count != CardNames.Length)
            {
                Check(false, "Three measurable card bodies are present");
                return;
            }

            CardRecord[] ordered = cards.OrderBy(card => card.MinY).ToArray();
            for (int index = 1; index < ordered.Length; index++)
            {
                CardRecord lower = ordered[index - 1];
                CardRecord upper = ordered[index];
                float gap = upper.MinY - lower.MaxY;
                Check(
                    gap + DimensionTolerance >= MinimumLayerAirGap,
                    $"{lower.Root.name}->{upper.Root.name}: spindle-axis air gap "
                    + $"{Millimetres(gap)} >= {Millimetres(MinimumLayerAirGap)}");
            }

            float firstPitch = ordered[1].CenterY - ordered[0].CenterY;
            float secondPitch = ordered[2].CenterY - ordered[1].CenterY;
            Check(
                Mathf.Abs(firstPitch - secondPitch) <= DimensionTolerance,
                "Three card centres use a uniform spindle-axis pitch "
                + $"({Millimetres(firstPitch)} / {Millimetres(secondPitch)})");
        }

        private static void ValidateCommonAxis(
            Transform root,
            List<CardRecord> cards)
        {
            Transform shaft = root.Find("CommonAxis_ShadowSleeve");
            Check(shaft != null, "Common spindle exists");
            if (shaft == null)
            {
                return;
            }

            float shaftRadius = FanCardSpecifications.AxisInnerRadius * 0.76f;
            foreach (CardRecord card in cards)
            {
                Vector2 localHoleCenter = new(
                    FanCardSpecifications.PivotX,
                    FanCardSpecifications.PivotZ);
                float minimumRadius = MinimumHoleBoundaryRadius(
                    card.Mesh,
                    localHoleCenter);
                float clearance = minimumRadius - shaftRadius;
                Check(
                    clearance + DimensionTolerance >= MinimumShaftClearance,
                    $"{card.Root.name}: through-hole clears spindle by "
                    + Millimetres(clearance));
                Check(
                    !CapContainsPoint(
                        card.Mesh,
                        localHoleCenter,
                        FanCardSpecifications.CardThickness * 0.5f),
                    $"{card.Root.name}: top cap contains a real spindle opening");
                Check(
                    !CapContainsPoint(
                        card.Mesh,
                        localHoleCenter,
                        -FanCardSpecifications.CardThickness * 0.5f),
                    $"{card.Root.name}: bottom cap contains a real spindle opening");
            }
        }

        private static void ValidateVisibleAxisHardware(Transform root)
        {
            Transform[] axisObjects = root
                .Cast<Transform>()
                .Where(item => item.name.StartsWith(
                    "CommonAxis_",
                    StringComparison.Ordinal))
                .ToArray();
            Transform[] visibleAxisObjects = axisObjects
                .Where(item =>
                {
                    Renderer renderer = item.GetComponent<Renderer>();
                    return renderer != null && renderer.enabled;
                })
                .ToArray();
            Check(
                visibleAxisObjects.Length == 1
                    && visibleAxisObjects[0].name
                        == FanCardSpecifications.FrontVisibleAxisRendererName,
                "Only the recessed matte spindle renders at the common axis");
            Check(
                !axisObjects.Any(item =>
                    FanCardSpecifications.ForbiddenAxisHardwareNameTokens.Any(
                        token => item.name.IndexOf(
                            token,
                            StringComparison.OrdinalIgnoreCase) >= 0)),
                "No common-axis cap, ring, washer, seat, cover disc, or chrome ball");

            Transform spindle = root.Find("CommonAxis_RecessedMatteSpindle");
            Renderer spindleRenderer = spindle != null
                ? spindle.GetComponent<Renderer>()
                : null;
            Check(
                spindleRenderer != null
                    && spindleRenderer.sharedMaterial != null
                    && spindleRenderer.sharedMaterial.name
                        == FanCardSpecifications.FrontVisibleAxisMaterialName
                    && Mathf.Approximately(
                        spindleRenderer.sharedMaterial.GetFloat("_Metallic"),
                        FanCardSpecifications.FrontVisibleAxisMetallic)
                    && Mathf.Approximately(
                        spindleRenderer.sharedMaterial.GetFloat("_Smoothness"),
                        FanCardSpecifications.FrontVisibleAxisSmoothness)
                    && spindleRenderer.sharedMaterial.GetFloat(
                        "_SpecularHighlights") == 0f
                    && spindleRenderer.sharedMaterial.GetFloat(
                        "_EnvironmentReflections") == 0f,
                "The sole visible spindle is matte with no specular or environment reflection");

            Transform marker = root.Find("CommonAxis_ShadowSleeve");
            Renderer markerRenderer = marker != null
                ? marker.GetComponent<Renderer>()
                : null;
            Check(
                marker != null
                    && (markerRenderer == null || !markerRenderer.enabled),
                "The structural axis marker remains non-rendered");
        }

        private static bool IsFiniteAndRigid(Mesh mesh)
        {
            float halfThickness = FanCardSpecifications.CardThickness * 0.5f;
            foreach (Vector3 vertex in mesh.vertices)
            {
                if (!float.IsFinite(vertex.x)
                    || !float.IsFinite(vertex.y)
                    || !float.IsFinite(vertex.z)
                    || vertex.y < -halfThickness - DimensionTolerance
                    || vertex.y > halfThickness + DimensionTolerance)
                {
                    return false;
                }
            }
            return true;
        }

        private static bool IsClosedWeldedManifold(Mesh mesh, out string detail)
        {
            Vector3[] vertices = mesh.vertices;
            int[] triangles = mesh.triangles;
            var edges = new Dictionary<GeometricEdge, int>();
            int degenerate = 0;
            for (int index = 0; index < triangles.Length; index += 3)
            {
                QuantizedPoint a = new(vertices[triangles[index]], WeldTolerance);
                QuantizedPoint b = new(vertices[triangles[index + 1]], WeldTolerance);
                QuantizedPoint c = new(vertices[triangles[index + 2]], WeldTolerance);
                if (a.Equals(b) || b.Equals(c) || c.Equals(a))
                {
                    degenerate++;
                    continue;
                }
                Increment(edges, new GeometricEdge(a, b));
                Increment(edges, new GeometricEdge(b, c));
                Increment(edges, new GeometricEdge(c, a));
            }
            int open = edges.Count(pair => pair.Value != 2);
            detail = $"open/nonmanifold={open}, degenerate={degenerate}";
            return open == 0 && degenerate == 0;
        }

        private static bool HasConsistentPositiveFacingTriangles(
            Mesh mesh,
            out string detail)
        {
            Vector3[] vertices = mesh.vertices;
            int[] triangles = mesh.triangles;
            int inverted = 0;
            int degenerate = 0;
            for (int index = 0; index < triangles.Length; index += 3)
            {
                Vector3 a = vertices[triangles[index]];
                Vector3 b = vertices[triangles[index + 1]];
                Vector3 c = vertices[triangles[index + 2]];
                float signedArea = Vector3.Cross(b - a, c - a).y;
                if (Mathf.Abs(signedArea) < 0.00000000001f)
                {
                    degenerate++;
                }
                else if (signedArea < 0f)
                {
                    inverted++;
                }
            }
            detail = $"inverted={inverted}, degenerate={degenerate}";
            return inverted == 0 && degenerate == 0;
        }

        private static bool AllVerticesInsideRoundedFace(
            Mesh mesh,
            out int outsideCount)
        {
            outsideCount = 0;
            float halfWidth = FanCardSpecifications.FaceWidth * 0.5f;
            float halfHeight = FanCardSpecifications.FaceHeight * 0.5f;
            float radius = FanCardSpecifications.FaceCornerRadius;
            Vector2 corner = new(halfWidth - radius, halfHeight - radius);
            foreach (Vector3 vertex in mesh.vertices)
            {
                float x = Mathf.Abs(vertex.x);
                float z = Mathf.Abs(vertex.z);
                bool inside = x <= halfWidth + PlaneTolerance
                    && z <= halfHeight + PlaneTolerance;
                if (inside && x > corner.x && z > corner.y)
                {
                    Vector2 delta = new(x - corner.x, z - corner.y);
                    inside = delta.sqrMagnitude
                        <= Mathf.Pow(radius + PlaneTolerance, 2f);
                }
                if (!inside)
                {
                    outsideCount++;
                }
            }
            return outsideCount == 0;
        }

        private static float MinimumHoleBoundaryRadius(
            Mesh mesh,
            Vector2 center)
        {
            float minimum = float.PositiveInfinity;
            foreach (Vector3 vertex in mesh.vertices)
            {
                float radius = Vector2.Distance(
                    new Vector2(vertex.x, vertex.z),
                    center);
                if (radius < FanCardSpecifications.AxisOuterRadius)
                {
                    minimum = Mathf.Min(minimum, radius);
                }
            }
            return minimum;
        }

        private static bool CapContainsPoint(
            Mesh mesh,
            Vector2 point,
            float y)
        {
            Vector3[] vertices = mesh.vertices;
            int[] triangles = mesh.triangles;
            for (int index = 0; index < triangles.Length; index += 3)
            {
                Vector3 a3 = vertices[triangles[index]];
                Vector3 b3 = vertices[triangles[index + 1]];
                Vector3 c3 = vertices[triangles[index + 2]];
                if (Mathf.Abs(a3.y - y) > PlaneTolerance
                    || Mathf.Abs(b3.y - y) > PlaneTolerance
                    || Mathf.Abs(c3.y - y) > PlaneTolerance)
                {
                    continue;
                }
                if (PointInTriangle(
                    point,
                    new Vector2(a3.x, a3.z),
                    new Vector2(b3.x, b3.z),
                    new Vector2(c3.x, c3.z)))
                {
                    return true;
                }
            }
            return false;
        }

        private static bool PointInTriangle(
            Vector2 point,
            Vector2 a,
            Vector2 b,
            Vector2 c)
        {
            float d1 = Cross(point - a, b - a);
            float d2 = Cross(point - b, c - b);
            float d3 = Cross(point - c, a - c);
            bool negative = d1 < -SignedAreaTolerance
                || d2 < -SignedAreaTolerance
                || d3 < -SignedAreaTolerance;
            bool positive = d1 > SignedAreaTolerance
                || d2 > SignedAreaTolerance
                || d3 > SignedAreaTolerance;
            return !(negative && positive);
        }

        private static float Cross(Vector2 a, Vector2 b)
        {
            return a.x * b.y - a.y * b.x;
        }

        private static void Increment(
            Dictionary<GeometricEdge, int> edges,
            GeometricEdge edge)
        {
            edges.TryGetValue(edge, out int count);
            edges[edge] = count + 1;
        }

        private static bool IsIdentityScale(Vector3 scale)
        {
            return Vector3.Distance(scale, Vector3.one) <= 0.00001f;
        }

        private static void CheckNear(float actual, float expected, string label)
        {
            Check(
                Mathf.Abs(actual - expected) <= DimensionTolerance,
                $"{label}: {Millimetres(actual)} (expected {Millimetres(expected)})");
        }

        private static void Check(bool passed, string message)
        {
            if (!passed)
            {
                failureCount++;
            }
            Write($"[{(passed ? "PASS" : "FAIL")}] {message}");
        }

        private static void Finish()
        {
            Write(failureCount == 0
                ? "=== VALIDATION: ALL PASS ==="
                : $"=== VALIDATION: {failureCount} FAILURE(S) ===");
        }

        private static string Millimetres(float metres)
        {
            return (metres * 1000f).ToString("F3", CultureInfo.InvariantCulture)
                + " mm";
        }

        private static void Write(string line)
        {
            Report.Add(line);
            Debug.Log(line);
        }

        private sealed class CardRecord
        {
            public CardRecord(Transform root, Mesh mesh, Renderer renderer)
            {
                Root = root;
                Mesh = mesh;
                MinY = renderer.bounds.min.y;
                MaxY = renderer.bounds.max.y;
                CenterY = renderer.bounds.center.y;
            }

            public Transform Root { get; }
            public Mesh Mesh { get; }
            public float MinY { get; }
            public float MaxY { get; }
            public float CenterY { get; }
        }

        private readonly struct QuantizedPoint : IEquatable<QuantizedPoint>,
            IComparable<QuantizedPoint>
        {
            private readonly long x;
            private readonly long y;
            private readonly long z;

            public QuantizedPoint(Vector3 point, float tolerance)
            {
                x = (long)Math.Round(point.x / tolerance);
                y = (long)Math.Round(point.y / tolerance);
                z = (long)Math.Round(point.z / tolerance);
            }

            public bool Equals(QuantizedPoint other)
            {
                return x == other.x && y == other.y && z == other.z;
            }

            public override bool Equals(object value)
            {
                return value is QuantizedPoint other && Equals(other);
            }

            public override int GetHashCode()
            {
                return HashCode.Combine(x, y, z);
            }

            public int CompareTo(QuantizedPoint other)
            {
                int compare = x.CompareTo(other.x);
                if (compare != 0) return compare;
                compare = y.CompareTo(other.y);
                return compare != 0 ? compare : z.CompareTo(other.z);
            }
        }

        private readonly struct GeometricEdge : IEquatable<GeometricEdge>
        {
            private readonly QuantizedPoint a;
            private readonly QuantizedPoint b;

            public GeometricEdge(QuantizedPoint first, QuantizedPoint second)
            {
                if (first.CompareTo(second) <= 0)
                {
                    a = first;
                    b = second;
                }
                else
                {
                    a = second;
                    b = first;
                }
            }

            public bool Equals(GeometricEdge other)
            {
                return a.Equals(other.a) && b.Equals(other.b);
            }

            public override bool Equals(object value)
            {
                return value is GeometricEdge other && Equals(other);
            }

            public override int GetHashCode()
            {
                return HashCode.Combine(a, b);
            }
        }
    }
}
