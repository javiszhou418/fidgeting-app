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
            Vector2[] grooveOuter =
            {
                new Vector2(-0.0072f, 0.0193f),
                new Vector2( 0.0072f, 0.0193f),
                new Vector2( 0.0076f, 0.0237f),
                new Vector2( 0.0000f, 0.0303f),
                new Vector2(-0.0076f, 0.0237f)
            };
            Vector2[] grooveInner =
            {
                new Vector2(-0.0062f, 0.0200f),
                new Vector2( 0.0062f, 0.0200f),
                new Vector2( 0.0066f, 0.0234f),
                new Vector2( 0.0000f, 0.0293f),
                new Vector2(-0.0066f, 0.0234f)
            };

            return CreateBevelledPolygon(
                name,
                CreateBladeOutline(),
                0.0060f,
                0.00082f,
                4,
                0.00008f,
                grooveOuter,
                grooveInner,
                0.00322f);
        }

        public static Mesh CreateBladeInset(string name = "M_BladeInset")
        {
            // The reference has a shallow triangular pocket, not a raised
            // plate. A nearly coplanar dark insert gives that depth cue
            // without a runtime parallax/height-map cost or boolean mesh.
            Vector2[] outline =
            {
                new Vector2(-0.0056f, 0.0206f),
                new Vector2( 0.0056f, 0.0206f),
                new Vector2( 0.0060f, 0.0232f),
                new Vector2( 0.0000f, 0.0284f),
                new Vector2(-0.0060f, 0.0232f)
            };

            return CreatePrism(name, outline, 0.00006f);
        }

        public static Mesh CreateBladeCollision(string name = "M_BladeCollision")
        {
            Vector2[] outline =
            {
                new Vector2(-0.0094f, 0.0155f),
                new Vector2( 0.0094f, 0.0155f),
                new Vector2( 0.0135f, 0.0220f),
                new Vector2( 0.0124f, 0.0308f),
                new Vector2( 0.0000f, 0.0385f),
                new Vector2(-0.0124f, 0.0308f),
                new Vector2(-0.0135f, 0.0220f)
            };

            return CreatePrism(name, outline, 0.0060f);
        }

        /// <summary>
        /// Combines equal radial copies into one renderer while preserving the
        /// source material slots. Colliders remain separate so the visual
        /// optimization cannot change touch geometry or physical ownership.
        /// </summary>
        public static Mesh CreateRadialCopies(
            Mesh source,
            string name,
            int copyCount = 3)
        {
            if (source == null)
            {
                throw new System.ArgumentNullException(nameof(source));
            }

            copyCount = Mathf.Max(1, copyCount);
            var vertices = new List<Vector3>(source.vertexCount * copyCount);
            var uvs = new List<Vector2>(source.vertexCount * copyCount);
            var submeshIndices = new List<int>[source.subMeshCount];
            for (int submesh = 0; submesh < submeshIndices.Length; submesh++)
            {
                submeshIndices[submesh] = new List<int>(
                    (int)source.GetIndexCount(submesh) * copyCount);
            }

            Vector3[] sourceVertices = source.vertices;
            Vector2[] sourceUvs = source.uv;
            for (int copy = 0; copy < copyCount; copy++)
            {
                Quaternion rotation = Quaternion.Euler(
                    0f,
                    copy * 360f / copyCount,
                    0f);
                int vertexOffset = vertices.Count;
                for (int vertex = 0; vertex < sourceVertices.Length; vertex++)
                {
                    vertices.Add(rotation * sourceVertices[vertex]);
                    uvs.Add(sourceUvs[vertex]);
                }

                for (int submesh = 0; submesh < submeshIndices.Length; submesh++)
                {
                    int[] indices = source.GetTriangles(submesh);
                    for (int index = 0; index < indices.Length; index++)
                    {
                        submeshIndices[submesh].Add(vertexOffset + indices[index]);
                    }
                }
            }

            return BuildMesh(
                name,
                vertices,
                uvs,
                submeshIndices[0],
                submeshIndices.Length > 1 ? submeshIndices[1] : null);
        }

        /// <summary>
        /// Builds the eight visible bearing balls as one smooth mesh and one
        /// draw call. This remains a visual cage; bearing dynamics continue to
        /// come exclusively from RotorRigidbodyController.
        /// </summary>
        public static Mesh CreateBearingBallCage(
            string name = "M_BearingBallCage",
            int ballCount = 8,
            int longitudeSegments = 16,
            int latitudeSegments = 8)
        {
            ballCount = Mathf.Max(3, ballCount);
            longitudeSegments = Mathf.Clamp(longitudeSegments, 8, 24);
            latitudeSegments = Mathf.Clamp(latitudeSegments, 4, 12);
            const float cageRadius = 0.0075f;
            const float ballRadius = 0.00155f;

            var vertices = new List<Vector3>();
            var uvs = new List<Vector2>();
            var triangles = new List<int>();
            for (int ball = 0; ball < ballCount; ball++)
            {
                float cageAngle = ball * Mathf.PI * 2f / ballCount;
                Vector3 center = new Vector3(
                    Mathf.Cos(cageAngle) * cageRadius,
                    0f,
                    Mathf.Sin(cageAngle) * cageRadius);
                int vertexOffset = vertices.Count;

                vertices.Add(center + Vector3.up * ballRadius);
                uvs.Add(new Vector2(0.5f, 1f));
                for (int latitude = 1; latitude < latitudeSegments; latitude++)
                {
                    float v = latitude / (float)latitudeSegments;
                    float polar = v * Mathf.PI;
                    float ringRadius = Mathf.Sin(polar) * ballRadius;
                    float y = Mathf.Cos(polar) * ballRadius;
                    for (int longitude = 0; longitude < longitudeSegments; longitude++)
                    {
                        float u = longitude / (float)longitudeSegments;
                        float azimuth = u * Mathf.PI * 2f;
                        vertices.Add(center + new Vector3(
                            Mathf.Cos(azimuth) * ringRadius,
                            y,
                            Mathf.Sin(azimuth) * ringRadius));
                        uvs.Add(new Vector2(u, v));
                    }
                }
                int bottomIndex = vertices.Count;
                vertices.Add(center - Vector3.up * ballRadius);
                uvs.Add(new Vector2(0.5f, 0f));

                int firstRing = vertexOffset + 1;
                for (int longitude = 0; longitude < longitudeSegments; longitude++)
                {
                    int next = (longitude + 1) % longitudeSegments;
                    triangles.Add(vertexOffset);
                    triangles.Add(firstRing + next);
                    triangles.Add(firstRing + longitude);
                }

                int ringCount = latitudeSegments - 1;
                for (int ring = 0; ring < ringCount - 1; ring++)
                {
                    int currentRing = firstRing + ring * longitudeSegments;
                    int nextRing = currentRing + longitudeSegments;
                    for (int longitude = 0; longitude < longitudeSegments; longitude++)
                    {
                        int next = (longitude + 1) % longitudeSegments;
                        int a = currentRing + longitude;
                        int b = nextRing + longitude;
                        int c = nextRing + next;
                        int d = currentRing + next;
                        triangles.Add(a);
                        triangles.Add(b);
                        triangles.Add(c);
                        triangles.Add(a);
                        triangles.Add(c);
                        triangles.Add(d);
                    }
                }

                int lastRing = firstRing + (ringCount - 1) * longitudeSegments;
                for (int longitude = 0; longitude < longitudeSegments; longitude++)
                {
                    int next = (longitude + 1) % longitudeSegments;
                    triangles.Add(lastRing + longitude);
                    triangles.Add(lastRing + next);
                    triangles.Add(bottomIndex);
                }
            }

            return BuildMesh(name, vertices, uvs, triangles, null);
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

            return CreateRadialDisc(
                name,
                radius,
                height,
                segments,
                bevel,
                0,
                0f);
        }

        /// <summary>
        /// Creates a metal finger cap with a smooth dog-tooth/scalloped grip
        /// around its circumference. Each tooth is sampled several times so
        /// the silhouette reads as a machined wave rather than a low-poly
        /// polygon. The maximum radius is preserved and the valleys cut
        /// inward, matching how a real knurled cap is machined.
        /// </summary>
        public static Mesh CreateScallopedDisc(
            string name,
            float radius,
            float height,
            int toothCount,
            int samplesPerTooth,
            float toothDepth,
            float bevel)
        {
            radius = Mathf.Max(0.0001f, radius);
            height = Mathf.Max(0.0001f, height);
            toothCount = Mathf.Max(3, toothCount);
            samplesPerTooth = Mathf.Clamp(samplesPerTooth, 4, 12);
            toothDepth = Mathf.Clamp(toothDepth, 0.00005f, radius * 0.12f);
            bevel = Mathf.Clamp(bevel, 0f, Mathf.Min(radius * 0.3f, height * 0.45f));

            return CreateRadialDisc(
                name,
                radius,
                height,
                toothCount * samplesPerTooth,
                bevel,
                toothCount,
                toothDepth);
        }

        private static Mesh CreateRadialDisc(
            string name,
            float radius,
            float height,
            int segments,
            float bevel,
            int toothCount,
            float toothDepth)
        {

            var vertices = new List<Vector3>();
            var uvs = new List<Vector2>();
            var body = new List<int>();
            var highlight = new List<int>();
            float half = height * 0.5f;
            // Keep all radial top facets co-planar. A domed fan of
            // triangles creates a strong strobing/moire pattern when the
            // product rotates; the brushing normal map supplies the subtle
            // radial read without changing the silhouette.
            const float crown = 0f;

            for (int i = 0; i < segments; i++)
            {
                float a0 = i * Mathf.PI * 2f / segments;
                float a1 = (i + 1) * Mathf.PI * 2f / segments;
                float outerRadius0 = ScallopedRadius(
                    radius,
                    toothDepth,
                    toothCount,
                    a0);
                float outerRadius1 = ScallopedRadius(
                    radius,
                    toothDepth,
                    toothCount,
                    a1);
                float innerRadius0 = Mathf.Max(
                    outerRadius0 - bevel,
                    outerRadius0 * 0.72f);
                float innerRadius1 = Mathf.Max(
                    outerRadius1 - bevel,
                    outerRadius1 * 0.72f);
                Vector3 center = new Vector3(0f, half + crown, 0f);
                Vector3 p0 = Radial(innerRadius0, half, a0);
                Vector3 p1 = Radial(innerRadius1, half, a1);
                AddTriangle(vertices, uvs, body, center, p1, p0, radius);

                Vector3 outer0 = Radial(outerRadius0, half - bevel, a0);
                Vector3 outer1 = Radial(outerRadius1, half - bevel, a1);
                AddQuad(vertices, uvs, highlight, p0, p1, outer1, outer0, radius);

                Vector3 lower0 = Radial(outerRadius0, -half + bevel, a0);
                Vector3 lower1 = Radial(outerRadius1, -half + bevel, a1);
                AddQuad(vertices, uvs, body, outer0, outer1, lower1, lower0, radius);

                Vector3 bottom0 = Radial(innerRadius0, -half, a0);
                Vector3 bottom1 = Radial(innerRadius1, -half, a1);
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

        private static float ScallopedRadius(
            float maximumRadius,
            float toothDepth,
            int toothCount,
            float angle)
        {
            if (toothCount <= 0 || toothDepth <= 0f)
            {
                return maximumRadius;
            }

            float valleyAmount = 0.5f - 0.5f * Mathf.Cos(angle * toothCount);
            return maximumRadius - toothDepth * valleyAmount;
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
            int bevelSegments,
            float topCrown = 0f,
            IReadOnlyList<Vector2> polishedInsetOuter = null,
            IReadOnlyList<Vector2> polishedInsetInner = null,
            float polishedInsetY = 0f)
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
                Vector3 topCenter = new Vector3(
                    centroid.x,
                    half + Mathf.Max(0f, topCrown),
                    centroid.y);
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

            AppendPlanarRing(
                vertices,
                uvs,
                highlight,
                polishedInsetOuter,
                polishedInsetInner,
                polishedInsetY);

            return BuildMesh(name, vertices, uvs, body, highlight);
        }

        private static void AppendPlanarRing(
            List<Vector3> vertices,
            List<Vector2> uvs,
            List<int> indices,
            IReadOnlyList<Vector2> outer,
            IReadOnlyList<Vector2> inner,
            float y)
        {
            if (outer == null && inner == null)
            {
                return;
            }

            if (outer == null || inner == null || outer.Count != inner.Count
                || outer.Count < 3)
            {
                throw new System.ArgumentException(
                    "Polished inset outlines must have equal vertex counts.");
            }

            for (int index = 0; index < outer.Count; index++)
            {
                int next = (index + 1) % outer.Count;
                // Inner-first winding faces +Y. The ring is folded into the
                // blade's existing polished submesh, so the machined border
                // costs geometry only—no extra material or draw call.
                AddQuad(
                    vertices,
                    uvs,
                    indices,
                    ToXZ(inner[index], y),
                    ToXZ(inner[next], y),
                    ToXZ(outer[next], y),
                    ToXZ(outer[index], y),
                    0.05f);
            }
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

        private static IReadOnlyList<Vector2> CreateBladeOutline()
        {
            // Deliberately faceted rather than spline-smoothed. The reference
            // reads as a machined triangular wing whose bevels catch discrete
            // strips of light, not as a rounded injection-moulded lobe.
            return new[]
            {
                new Vector2(-0.0094f, 0.0155f),
                new Vector2( 0.0094f, 0.0155f),
                new Vector2( 0.0138f, 0.0225f),
                new Vector2( 0.0100f, 0.0300f),
                new Vector2( 0.0000f, 0.0385f),
                new Vector2(-0.0100f, 0.0300f),
                new Vector2(-0.0138f, 0.0225f)
            };
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
