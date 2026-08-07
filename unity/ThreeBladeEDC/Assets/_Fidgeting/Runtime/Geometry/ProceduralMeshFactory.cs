using System.Collections.Generic;
using UnityEngine;

namespace ThreeBladeEDC.Geometry
{
    /// <summary>
    /// Creates the small set of reusable product-visualization meshes used by
    /// the three-blade concept. Y is the spin axis and geometry lies in XZ.
    /// Dimensions are metres.
    /// </summary>
    public static class ProceduralMeshFactory
    {
        public static Mesh CreateBlade(string name = "M_ThreeBladeSector")
        {
            return CreateBevelledPolygon(
                name,
                CreateBladeOutline(5),
                0.007f,
                0.00125f,
                5);
        }

        public static Mesh CreateBladeInset(string name = "M_BladeInset")
        {
            Vector2[] outline =
            {
                new Vector2(-0.0067f, 0.0213f),
                new Vector2( 0.0067f, 0.0213f),
                new Vector2( 0.0081f, 0.0254f),
                new Vector2( 0.0054f, 0.0332f),
                new Vector2( 0.0000f, 0.0372f),
                new Vector2(-0.0054f, 0.0332f),
                new Vector2(-0.0081f, 0.0254f)
            };

            return CreateBevelledPolygon(name, outline, 0.00055f, 0.00016f, 3);
        }

        public static Mesh CreateBladeCollision(string name = "M_BladeCollision")
        {
            Vector2[] outline =
            {
                new Vector2(-0.0108f, 0.0163f),
                new Vector2( 0.0108f, 0.0163f),
                new Vector2( 0.0134f, 0.0225f),
                new Vector2( 0.0115f, 0.0305f),
                new Vector2( 0.0052f, 0.0392f),
                new Vector2( 0.0000f, 0.0422f),
                new Vector2(-0.0052f, 0.0392f),
                new Vector2(-0.0115f, 0.0305f),
                new Vector2(-0.0134f, 0.0225f)
            };

            return CreatePrism(name, outline, 0.007f);
        }

        public static Mesh CreateFacetedDisc(
            string name,
            float radius,
            float height,
            int segments,
            float bevel)
        {
            segments = Mathf.Max(6, segments);
            radius = Mathf.Max(0.0001f, radius);
            height = Mathf.Max(0.0001f, height);
            bevel = Mathf.Clamp(bevel, 0f, Mathf.Min(radius * 0.3f, height * 0.45f));

            var vertices = new List<Vector3>();
            var uvs = new List<Vector2>();
            var body = new List<int>();
            var highlight = new List<int>();
            float half = height * 0.5f;
            float innerRadius = Mathf.Max(radius - bevel, radius * 0.72f);
            // Keep all 48-64 radial top facets co-planar. A domed fan of
            // triangles creates a strong strobing/moire pattern when the
            // product rotates; the brushing normal map supplies the subtle
            // radial read without changing the silhouette.
            const float crown = 0f;

            for (int i = 0; i < segments; i++)
            {
                float a0 = i * Mathf.PI * 2f / segments;
                float a1 = (i + 1) * Mathf.PI * 2f / segments;
                Vector3 center = new Vector3(0f, half + crown, 0f);
                Vector3 p0 = Radial(innerRadius, half, a0);
                Vector3 p1 = Radial(innerRadius, half, a1);
                AddTriangle(vertices, uvs, body, center, p1, p0, radius);

                Vector3 outer0 = Radial(radius, half - bevel, a0);
                Vector3 outer1 = Radial(radius, half - bevel, a1);
                AddQuad(vertices, uvs, highlight, p0, p1, outer1, outer0, radius);

                Vector3 lower0 = Radial(radius, -half + bevel, a0);
                Vector3 lower1 = Radial(radius, -half + bevel, a1);
                AddQuad(vertices, uvs, body, outer0, outer1, lower1, lower0, radius);

                Vector3 bottom0 = Radial(innerRadius, -half, a0);
                Vector3 bottom1 = Radial(innerRadius, -half, a1);
                AddQuad(vertices, uvs, highlight, lower0, lower1, bottom1, bottom0, radius);
                AddTriangle(
                    vertices,
                    uvs,
                    body,
                    new Vector3(0f, -half, 0f),
                    bottom0,
                    bottom1,
                    radius);
            }

            return BuildMesh(name, vertices, uvs, body, highlight);
        }

        public static Mesh CreateRing(
            string name,
            float outerRadius,
            float innerRadius,
            float height,
            int segments)
        {
            segments = Mathf.Max(8, segments);
            outerRadius = Mathf.Max(0.0002f, outerRadius);
            innerRadius = Mathf.Clamp(innerRadius, 0.0001f, outerRadius - 0.0001f);
            height = Mathf.Max(0.0001f, height);

            var vertices = new List<Vector3>();
            var uvs = new List<Vector2>();
            var triangles = new List<int>();
            float half = height * 0.5f;

            for (int i = 0; i < segments; i++)
            {
                float a0 = i * Mathf.PI * 2f / segments;
                float a1 = (i + 1) * Mathf.PI * 2f / segments;
                Vector3 ot0 = Radial(outerRadius, half, a0);
                Vector3 ot1 = Radial(outerRadius, half, a1);
                Vector3 ob0 = Radial(outerRadius, -half, a0);
                Vector3 ob1 = Radial(outerRadius, -half, a1);
                Vector3 it0 = Radial(innerRadius, half, a0);
                Vector3 it1 = Radial(innerRadius, half, a1);
                Vector3 ib0 = Radial(innerRadius, -half, a0);
                Vector3 ib1 = Radial(innerRadius, -half, a1);

                AddQuad(vertices, uvs, triangles, ot0, ot1, ob1, ob0, outerRadius);
                AddQuad(vertices, uvs, triangles, it1, it0, ib0, ib1, outerRadius);
                AddQuad(vertices, uvs, triangles, it0, it1, ot1, ot0, outerRadius);
                AddQuad(vertices, uvs, triangles, ib1, ib0, ob0, ob1, outerRadius);
            }

            return BuildMesh(name, vertices, uvs, triangles, null);
        }

        private static Mesh CreateBevelledPolygon(
            string name,
            IReadOnlyList<Vector2> outline,
            float height,
            float bevel,
            int bevelSegments)
        {
            var vertices = new List<Vector3>();
            var uvs = new List<Vector2>();
            var body = new List<int>();
            var highlight = new List<int>();
            float half = height * 0.5f;
            bevelSegments = Mathf.Clamp(bevelSegments, 1, 8);

            Vector2 centroid = Vector2.zero;
            for (int i = 0; i < outline.Count; i++)
            {
                centroid += outline[i];
            }
            centroid /= outline.Count;

            var topRings = new Vector3[bevelSegments + 1][];
            var bottomRings = new Vector3[bevelSegments + 1][];
            for (int segment = 0; segment <= bevelSegments; segment++)
            {
                float t = segment / (float)bevelSegments;
                float angle = t * Mathf.PI * 0.5f;
                float insetDistance = bevel * (1f - Mathf.Sin(angle));
                float verticalDrop = bevel * (1f - Mathf.Cos(angle));
                topRings[segment] = new Vector3[outline.Count];
                bottomRings[segment] = new Vector3[outline.Count];

                for (int i = 0; i < outline.Count; i++)
                {
                    Vector2 direction = centroid - outline[i];
                    Vector2 insetPoint = outline[i]
                        + direction.normalized * insetDistance;
                    topRings[segment][i] = ToXZ(insetPoint, half - verticalDrop);
                    bottomRings[segment][i] = ToXZ(
                        insetPoint,
                        -half + verticalDrop);
                }
            }

            for (int i = 0; i < outline.Count; i++)
            {
                int next = (i + 1) % outline.Count;
                Vector3 topCenter = new Vector3(centroid.x, half, centroid.y);
                Vector3 bottomCenter = new Vector3(centroid.x, -half, centroid.y);

                AddTriangle(
                    vertices,
                    uvs,
                    body,
                    topCenter,
                    topRings[0][next],
                    topRings[0][i],
                    0.05f);
                AddTriangle(
                    vertices,
                    uvs,
                    body,
                    bottomCenter,
                    bottomRings[0][i],
                    bottomRings[0][next],
                    0.05f);

                for (int segment = 0; segment < bevelSegments; segment++)
                {
                    AddQuad(
                        vertices,
                        uvs,
                        highlight,
                        topRings[segment][i],
                        topRings[segment][next],
                        topRings[segment + 1][next],
                        topRings[segment + 1][i],
                        0.05f);
                    AddQuad(
                        vertices,
                        uvs,
                        highlight,
                        bottomRings[segment + 1][i],
                        bottomRings[segment + 1][next],
                        bottomRings[segment][next],
                        bottomRings[segment][i],
                        0.05f);
                }

                AddQuad(
                    vertices,
                    uvs,
                    body,
                    topRings[bevelSegments][i],
                    topRings[bevelSegments][next],
                    bottomRings[bevelSegments][next],
                    bottomRings[bevelSegments][i],
                    0.05f);
            }

            return BuildMesh(name, vertices, uvs, body, highlight);
        }

        private static Mesh CreatePrism(
            string name,
            IReadOnlyList<Vector2> outline,
            float height)
        {
            var vertices = new List<Vector3>();
            var uvs = new List<Vector2>();
            var triangles = new List<int>();
            float half = height * 0.5f;

            for (int i = 0; i < outline.Count; i++)
            {
                vertices.Add(ToXZ(outline[i], half));
                uvs.Add(PlanarUv(vertices[vertices.Count - 1], 0.05f));
            }
            for (int i = 0; i < outline.Count; i++)
            {
                vertices.Add(ToXZ(outline[i], -half));
                uvs.Add(PlanarUv(vertices[vertices.Count - 1], 0.05f));
            }

            for (int i = 1; i < outline.Count - 1; i++)
            {
                triangles.Add(0);
                triangles.Add(i + 1);
                triangles.Add(i);
                triangles.Add(outline.Count);
                triangles.Add(outline.Count + i);
                triangles.Add(outline.Count + i + 1);
            }

            for (int i = 0; i < outline.Count; i++)
            {
                int next = (i + 1) % outline.Count;
                triangles.Add(i);
                triangles.Add(next);
                triangles.Add(outline.Count + next);
                triangles.Add(i);
                triangles.Add(outline.Count + next);
                triangles.Add(outline.Count + i);
            }

            return BuildMesh(name, vertices, uvs, triangles, null);
        }

        private static IReadOnlyList<Vector2> CreateBladeOutline(int samplesPerSegment)
        {
            Vector2[] rightControlPoints =
            {
                new Vector2(0.0108f, 0.0163f),
                new Vector2(0.0129f, 0.0192f),
                new Vector2(0.0135f, 0.0236f),
                new Vector2(0.0125f, 0.0293f),
                new Vector2(0.0101f, 0.0344f),
                new Vector2(0.0068f, 0.0388f),
                new Vector2(0.0025f, 0.0414f),
                new Vector2(0.0000f, 0.0422f)
            };

            samplesPerSegment = Mathf.Clamp(samplesPerSegment, 2, 8);
            var rightCurve = new List<Vector2> { rightControlPoints[0] };
            for (int segment = 0; segment < rightControlPoints.Length - 1; segment++)
            {
                Vector2 p0 = rightControlPoints[Mathf.Max(0, segment - 1)];
                Vector2 p1 = rightControlPoints[segment];
                Vector2 p2 = rightControlPoints[segment + 1];
                Vector2 p3 = rightControlPoints[
                    Mathf.Min(rightControlPoints.Length - 1, segment + 2)];

                for (int sample = 1; sample <= samplesPerSegment; sample++)
                {
                    float t = sample / (float)samplesPerSegment;
                    rightCurve.Add(CatmullRom(p0, p1, p2, p3, t));
                }
            }

            var outline = new List<Vector2>(rightCurve.Count * 2);
            outline.Add(new Vector2(-rightControlPoints[0].x, rightControlPoints[0].y));
            outline.AddRange(rightCurve);
            for (int i = rightCurve.Count - 2; i > 0; i--)
            {
                outline.Add(new Vector2(-rightCurve[i].x, rightCurve[i].y));
            }
            return outline;
        }

        private static Vector2 CatmullRom(
            Vector2 p0,
            Vector2 p1,
            Vector2 p2,
            Vector2 p3,
            float t)
        {
            float t2 = t * t;
            float t3 = t2 * t;
            return 0.5f * ((2f * p1)
                + (-p0 + p2) * t
                + (2f * p0 - 5f * p1 + 4f * p2 - p3) * t2
                + (-p0 + 3f * p1 - 3f * p2 + p3) * t3);
        }

        private static Mesh BuildMesh(
            string name,
            List<Vector3> vertices,
            List<Vector2> uvs,
            List<int> primary,
            List<int> secondary)
        {
            var mesh = new Mesh { name = name };
            mesh.SetVertices(vertices);
            mesh.SetUVs(0, uvs);
            mesh.subMeshCount = secondary == null ? 1 : 2;
            mesh.SetTriangles(primary, 0, false);
            if (secondary != null)
            {
                mesh.SetTriangles(secondary, 1, false);
            }
            mesh.RecalculateNormals();
            mesh.RecalculateTangents();
            mesh.RecalculateBounds();
            return mesh;
        }

        private static void AddTriangle(
            List<Vector3> vertices,
            List<Vector2> uvs,
            List<int> indices,
            Vector3 a,
            Vector3 b,
            Vector3 c,
            float uvScale)
        {
            int start = vertices.Count;
            vertices.Add(a);
            vertices.Add(b);
            vertices.Add(c);
            uvs.Add(PlanarUv(a, uvScale));
            uvs.Add(PlanarUv(b, uvScale));
            uvs.Add(PlanarUv(c, uvScale));
            indices.Add(start);
            indices.Add(start + 1);
            indices.Add(start + 2);
        }

        private static void AddQuad(
            List<Vector3> vertices,
            List<Vector2> uvs,
            List<int> indices,
            Vector3 a,
            Vector3 b,
            Vector3 c,
            Vector3 d,
            float uvScale)
        {
            int start = vertices.Count;
            vertices.Add(a);
            vertices.Add(b);
            vertices.Add(c);
            vertices.Add(d);
            uvs.Add(PlanarUv(a, uvScale));
            uvs.Add(PlanarUv(b, uvScale));
            uvs.Add(PlanarUv(c, uvScale));
            uvs.Add(PlanarUv(d, uvScale));
            indices.Add(start);
            indices.Add(start + 1);
            indices.Add(start + 2);
            indices.Add(start);
            indices.Add(start + 2);
            indices.Add(start + 3);
        }

        private static Vector2 PlanarUv(Vector3 value, float scale)
        {
            float safeScale = Mathf.Max(0.0001f, scale);
            return new Vector2(value.x / safeScale + 0.5f, value.z / safeScale + 0.5f);
        }

        private static Vector3 Radial(float radius, float y, float angle)
        {
            return new Vector3(Mathf.Cos(angle) * radius, y, Mathf.Sin(angle) * radius);
        }

        private static Vector3 ToXZ(Vector2 value, float y)
        {
            return new Vector3(value.x, y, value.y);
        }
    }
}
