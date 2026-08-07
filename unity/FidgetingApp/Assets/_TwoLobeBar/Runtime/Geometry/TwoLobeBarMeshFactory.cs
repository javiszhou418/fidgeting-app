using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.TwoLobeBar.Geometry
{
    /// <summary>
    /// Deterministic mobile meshes for one radial bar half and the stationary
    /// concave finger button. The two lobe instances share one mesh asset.
    /// </summary>
    public static class TwoLobeBarMeshFactory
    {
        public static Mesh CreateBody(
            string name = "M_TwoLobeBarBody",
            int endSegments = 28,
            int crossSegments = 48)
        {
            endSegments = Mathf.Clamp(endSegments, 12, 64);
            crossSegments = Mathf.Clamp(crossSegments, 24, 96);

            float halfWidth = TwoLobeBarSpecifications.BodyWidth * 0.5f;
            float halfThickness = TwoLobeBarSpecifications.BodyThickness * 0.5f;
            float halfLength = TwoLobeBarSpecifications.HalfBodyLength;
            float transition = TwoLobeBarSpecifications.EndTransitionLength;
            float straightEnd = halfLength - transition;
            float endFaceHalfWidth = halfWidth
                - TwoLobeBarSpecifications.EndFaceInset;
            float endFaceHalfThickness = halfThickness
                - TwoLobeBarSpecifications.EndFaceInset;
            float superellipsePower = 2f / TwoLobeBarSpecifications.BodyCrownExponent;

            int ringCount = endSegments * 2 + 2;
            var vertices = new List<Vector3>(ringCount * crossSegments + 2);
            var uvs = new List<Vector2>(ringCount * crossSegments + 2);
            var triangles = new List<int>(ringCount * crossSegments * 6);

            // Short negative end roll. The first ring is a substantial flat
            // end face; it expands smoothly into the full crowned body over
            // only 3.5 mm, preserving the reference's long visual proportion.
            for (int segment = 0; segment <= endSegments; segment++)
            {
                float t = segment / (float)endSegments;
                float angle = t * Mathf.PI * 0.5f;
                float blend = Mathf.Sin(angle);
                AddCrownedCrossSectionSized(
                    vertices,
                    uvs,
                    -halfLength + transition * (1f - Mathf.Cos(angle)),
                    crossSegments,
                    Mathf.Lerp(endFaceHalfWidth, halfWidth, blend),
                    Mathf.Lerp(endFaceHalfThickness, halfThickness, blend),
                    superellipsePower);
            }

            AddCrownedCrossSectionSized(
                vertices,
                uvs,
                straightEnd,
                crossSegments,
                halfWidth,
                halfThickness,
                superellipsePower);

            // Mirrored positive end roll, finishing on the planar end face.
            for (int segment = 1; segment <= endSegments; segment++)
            {
                float t = segment / (float)endSegments;
                float angle = t * Mathf.PI * 0.5f;
                float blend = Mathf.Cos(angle);
                AddCrownedCrossSectionSized(
                    vertices,
                    uvs,
                    straightEnd + transition * Mathf.Sin(angle),
                    crossSegments,
                    Mathf.Lerp(endFaceHalfWidth, halfWidth, blend),
                    Mathf.Lerp(endFaceHalfThickness, halfThickness, blend),
                    superellipsePower);
            }

            for (int ring = 0; ring < ringCount - 1; ring++)
            {
                int lower = ring * crossSegments;
                int upper = (ring + 1) * crossSegments;
                for (int point = 0; point < crossSegments; point++)
                {
                    int next = (point + 1) % crossSegments;
                    int a = lower + point;
                    int b = lower + next;
                    int c = upper + point;
                    int d = upper + next;
                    triangles.Add(a);
                    triangles.Add(b);
                    triangles.Add(d);
                    triangles.Add(a);
                    triangles.Add(d);
                    triangles.Add(c);
                }
            }

            int negativeTip = vertices.Count;
            vertices.Add(new Vector3(0f, 0f, -halfLength));
            uvs.Add(new Vector2(0.5f, 0f));
            for (int point = 0; point < crossSegments; point++)
            {
                int next = (point + 1) % crossSegments;
                triangles.Add(negativeTip);
                triangles.Add(next);
                triangles.Add(point);
            }

            int positiveTip = vertices.Count;
            vertices.Add(new Vector3(0f, 0f, halfLength));
            uvs.Add(new Vector2(0.5f, 1f));
            int finalRing = (ringCount - 1) * crossSegments;
            for (int point = 0; point < crossSegments; point++)
            {
                int next = (point + 1) % crossSegments;
                triangles.Add(finalRing + point);
                triangles.Add(finalRing + next);
                triangles.Add(positiveTip);
            }

            return BuildMesh(name, vertices, uvs, triangles);
        }

        public static Mesh CreateLobe(
            string name = "M_TwoLobeBarHalf",
            int endSegments = 28,
            int filletSegments = 6)
        {
            endSegments = Mathf.Clamp(endSegments, 12, 64);
            int crossSegments = Mathf.Clamp(filletSegments * 8, 24, 96);

            float halfWidth = TwoLobeBarSpecifications.BodyWidth * 0.5f;
            float halfThickness = TwoLobeBarSpecifications.BodyThickness * 0.5f;
            float straightEnd = TwoLobeBarSpecifications.HalfBodyLength - halfWidth;
            float exponent = TwoLobeBarSpecifications.BodyCrownExponent;
            float superellipsePower = 2f / exponent;

            // Two full cross-sections form the straight portion. Successive
            // scaled rings close the outer end as an ellipsoidal dome. The
            // superellipse section is continuously curved across the broad
            // face, so there is no planar top cap to misread as a flat slab.
            int ringCount = endSegments + 1;
            var vertices = new List<Vector3>(ringCount * crossSegments + 2);
            var uvs = new List<Vector2>(ringCount * crossSegments + 2);
            var triangles = new List<int>(ringCount * crossSegments * 6);

            AddCrownedCrossSection(
                vertices,
                uvs,
                0f,
                1f,
                crossSegments,
                halfWidth,
                halfThickness,
                superellipsePower);
            AddCrownedCrossSection(
                vertices,
                uvs,
                straightEnd,
                1f,
                crossSegments,
                halfWidth,
                halfThickness,
                superellipsePower);

            for (int segment = 1; segment < endSegments; segment++)
            {
                float t = segment / (float)endSegments;
                float angle = t * Mathf.PI * 0.5f;
                AddCrownedCrossSection(
                    vertices,
                    uvs,
                    straightEnd + halfWidth * Mathf.Sin(angle),
                    Mathf.Cos(angle),
                    crossSegments,
                    halfWidth,
                    halfThickness,
                    superellipsePower);
            }

            int generatedRings = 2 + (endSegments - 1);
            for (int ring = 0; ring < generatedRings - 1; ring++)
            {
                int lower = ring * crossSegments;
                int upper = (ring + 1) * crossSegments;
                for (int point = 0; point < crossSegments; point++)
                {
                    int next = (point + 1) % crossSegments;
                    int a = lower + point;
                    int b = lower + next;
                    int c = upper + point;
                    int d = upper + next;
                    triangles.Add(a);
                    triangles.Add(b);
                    triangles.Add(d);
                    triangles.Add(a);
                    triangles.Add(d);
                    triangles.Add(c);
                }
            }

            int innerCenter = vertices.Count;
            vertices.Add(Vector3.zero);
            uvs.Add(new Vector2(0.5f, 0f));
            for (int point = 0; point < crossSegments; point++)
            {
                int next = (point + 1) % crossSegments;
                triangles.Add(innerCenter);
                triangles.Add(next);
                triangles.Add(point);
            }

            int tip = vertices.Count;
            vertices.Add(new Vector3(
                0f,
                0f,
                TwoLobeBarSpecifications.HalfBodyLength));
            uvs.Add(new Vector2(0.5f, 1f));
            int finalRing = (generatedRings - 1) * crossSegments;
            for (int point = 0; point < crossSegments; point++)
            {
                int next = (point + 1) % crossSegments;
                triangles.Add(finalRing + point);
                triangles.Add(finalRing + next);
                triangles.Add(tip);
            }

            return BuildMesh(name, vertices, uvs, triangles);
        }

        public static Mesh CreateConcaveButton(
            string name = "M_TwoLobeConcaveButton",
            int radialSegments = 64,
            int dishRings = 10,
            int bevelSegments = 4)
        {
            radialSegments = Mathf.Clamp(radialSegments, 32, 128);
            dishRings = Mathf.Clamp(dishRings, 5, 20);
            bevelSegments = Mathf.Clamp(bevelSegments, 2, 8);

            float radius = TwoLobeBarSpecifications.ButtonRadius;
            float proud = TwoLobeBarSpecifications.ButtonProudHeight;
            float dishDepth = TwoLobeBarSpecifications.ButtonDishDepth;
            float rimWidth = TwoLobeBarSpecifications.ButtonRimWidth;
            float bevel = Mathf.Min(0.00065f, rimWidth * 0.55f);
            float dishRadius = radius - rimWidth;
            float undercutRadius = TwoLobeBarSpecifications.ButtonUndercutRadius;
            float undercutReveal = TwoLobeBarSpecifications.ButtonUndercutReveal;

            var vertices = new List<Vector3>();
            var uvs = new List<Vector2>();
            var triangles = new List<int>();

            int topCenter = vertices.Count;
            vertices.Add(new Vector3(0f, proud - dishDepth, 0f));
            uvs.Add(new Vector2(0.5f, 0.5f));

            var rings = new List<ButtonRing>(dishRings + bevelSegments * 2 + 4);
            for (int ring = 1; ring <= dishRings; ring++)
            {
                float t = ring / (float)dishRings;
                float ringRadius = dishRadius * t;
                float height = proud - dishDepth * (1f - t * t);
                rings.Add(new ButtonRing(ringRadius, height));
            }

            rings.Add(new ButtonRing(radius - bevel, proud));
            for (int segment = 1; segment <= bevelSegments; segment++)
            {
                float t = segment / (float)bevelSegments;
                float angle = Mathf.PI * 0.5f * (1f - t);
                rings.Add(new ButtonRing(
                    radius - bevel + bevel * Mathf.Cos(angle),
                    proud - bevel + bevel * Mathf.Sin(angle)));
            }

            // Keep the outer wall at full diameter until the lower edge of
            // the finger disc, then roll underneath into a recessed narrow
            // neck. This makes the edge visibly overhang the dark cavity.
            rings.Add(new ButtonRing(radius, undercutReveal + bevel * 0.65f));
            for (int segment = 1; segment <= bevelSegments; segment++)
            {
                float t = segment / (float)bevelSegments;
                float eased = Mathf.SmoothStep(0f, 1f, t);
                rings.Add(new ButtonRing(
                    Mathf.Lerp(radius, radius - bevel * 0.38f, eased),
                    Mathf.Lerp(
                        undercutReveal + bevel * 0.65f,
                        undercutReveal,
                        eased)));
            }

            // Nearly horizontal underside shelf: its inward run is the
            // visible overhang and stays self-shadowed under the disc.
            for (int segment = 1; segment <= bevelSegments; segment++)
            {
                float t = segment / (float)bevelSegments;
                float eased = Mathf.SmoothStep(0f, 1f, t);
                rings.Add(new ButtonRing(
                    Mathf.Lerp(
                        radius - bevel * 0.38f,
                        undercutRadius + bevel * 0.28f,
                        eased),
                    Mathf.Lerp(
                        undercutReveal,
                        undercutReveal - bevel * 0.16f,
                        eased)));
            }

            // Small inner roll followed by the vertical recessed neck.
            for (int segment = 1; segment <= bevelSegments; segment++)
            {
                float t = segment / (float)bevelSegments;
                float eased = Mathf.SmoothStep(0f, 1f, t);
                rings.Add(new ButtonRing(
                    Mathf.Lerp(
                        undercutRadius + bevel * 0.28f,
                        undercutRadius,
                        eased),
                    Mathf.Lerp(
                        undercutReveal - bevel * 0.16f,
                        undercutReveal - bevel * 0.42f,
                        eased)));
            }
            rings.Add(new ButtonRing(undercutRadius, 0f));

            int previousRingStart = -1;
            for (int ringIndex = 0; ringIndex < rings.Count; ringIndex++)
            {
                ButtonRing ring = rings[ringIndex];
                int ringStart = vertices.Count;
                AddCircularRing(
                    vertices,
                    uvs,
                    ring.Radius,
                    ring.Height,
                    radialSegments,
                    radius);

                if (previousRingStart < 0)
                {
                    for (int segment = 0; segment < radialSegments; segment++)
                    {
                        int next = (segment + 1) % radialSegments;
                        triangles.Add(topCenter);
                        triangles.Add(ringStart + segment);
                        triangles.Add(ringStart + next);
                    }
                }
                else
                {
                    ConnectCircularRings(
                        triangles,
                        previousRingStart,
                        ringStart,
                        radialSegments);
                }

                previousRingStart = ringStart;
            }

            int bottomCenter = vertices.Count;
            vertices.Add(Vector3.zero);
            uvs.Add(new Vector2(0.5f, 0.5f));
            for (int segment = 0; segment < radialSegments; segment++)
            {
                int next = (segment + 1) % radialSegments;
                triangles.Add(bottomCenter);
                triangles.Add(previousRingStart + next);
                triangles.Add(previousRingStart + segment);
            }

            return BuildMesh(name, vertices, uvs, triangles);
        }

        public static Mesh CreateUndercutShadowCollar(
            string name = "M_TwoLobeUndercutShadowCollar",
            int radialSegments = 64)
        {
            radialSegments = Mathf.Clamp(radialSegments, 32, 128);
            float radius = TwoLobeBarSpecifications.ButtonUndercutRadius
                + 0.00004f;
            float height = TwoLobeBarSpecifications.ButtonUndercutReveal
                - 0.00008f;
            var vertices = new List<Vector3>();
            var uvs = new List<Vector2>();
            var triangles = new List<int>();

            int bottomRing = vertices.Count;
            AddCircularRing(
                vertices,
                uvs,
                radius,
                0f,
                radialSegments,
                radius);
            int topRing = vertices.Count;
            AddCircularRing(
                vertices,
                uvs,
                radius,
                height,
                radialSegments,
                radius);
            ConnectCircularRings(
                triangles,
                bottomRing,
                topRing,
                radialSegments);

            // Deliberately leave the collar open. Its only visible surface is
            // the recessed cylindrical wall; coplanar caps would overlap the
            // button underside and cause Z-fighting in Unity.
            return BuildMesh(name, vertices, uvs, triangles);
        }

        private static void AddCrownedCrossSection(
            List<Vector3> vertices,
            List<Vector2> uvs,
            float z,
            float scale,
            int segments,
            float halfWidth,
            float halfThickness,
            float superellipsePower)
        {
            for (int segment = 0; segment < segments; segment++)
            {
                float angle = segment * Mathf.PI * 2f / segments;
                float cosine = Mathf.Cos(angle);
                float sine = Mathf.Sin(angle);
                float x = Mathf.Sign(cosine)
                    * Mathf.Pow(Mathf.Abs(cosine), superellipsePower)
                    * halfWidth
                    * scale;
                float y = Mathf.Sign(sine)
                    * Mathf.Pow(Mathf.Abs(sine), superellipsePower)
                    * halfThickness
                    * scale;
                vertices.Add(new Vector3(x, y, z));
                uvs.Add(new Vector2(
                    segment / (float)segments,
                    z / TwoLobeBarSpecifications.HalfBodyLength));
            }
        }

        private static void AddCrownedCrossSectionSized(
            List<Vector3> vertices,
            List<Vector2> uvs,
            float z,
            int segments,
            float halfWidth,
            float halfThickness,
            float superellipsePower)
        {
            for (int segment = 0; segment < segments; segment++)
            {
                float angle = segment * Mathf.PI * 2f / segments;
                float cosine = Mathf.Cos(angle);
                float sine = Mathf.Sin(angle);
                float x = Mathf.Sign(cosine)
                    * Mathf.Pow(Mathf.Abs(cosine), superellipsePower)
                    * halfWidth;
                float y = Mathf.Sign(sine)
                    * Mathf.Pow(Mathf.Abs(sine), superellipsePower)
                    * halfThickness;
                vertices.Add(new Vector3(x, y, z));
                uvs.Add(new Vector2(
                    segment / (float)segments,
                    z / TwoLobeBarSpecifications.BodyLength + 0.5f));
            }
        }

        private static void AddCircularRing(
            List<Vector3> vertices,
            List<Vector2> uvs,
            float radius,
            float height,
            int segments,
            float uvRadius)
        {
            for (int segment = 0; segment < segments; segment++)
            {
                float angle = -segment * Mathf.PI * 2f / segments;
                float x = Mathf.Cos(angle) * radius;
                float z = Mathf.Sin(angle) * radius;
                vertices.Add(new Vector3(x, height, z));
                uvs.Add(new Vector2(
                    x / (uvRadius * 2f) + 0.5f,
                    z / (uvRadius * 2f) + 0.5f));
            }
        }

        private static void ConnectCircularRings(
            List<int> triangles,
            int innerStart,
            int outerStart,
            int segments)
        {
            for (int segment = 0; segment < segments; segment++)
            {
                int next = (segment + 1) % segments;
                int a = innerStart + segment;
                int b = innerStart + next;
                int c = outerStart + segment;
                int d = outerStart + next;
                triangles.Add(a);
                triangles.Add(c);
                triangles.Add(d);
                triangles.Add(a);
                triangles.Add(d);
                triangles.Add(b);
            }
        }

        private static Mesh BuildMesh(
            string name,
            List<Vector3> vertices,
            List<Vector2> uvs,
            List<int> triangles)
        {
            var mesh = new Mesh
            {
                name = name,
                indexFormat = vertices.Count > ushort.MaxValue
                    ? IndexFormat.UInt32
                    : IndexFormat.UInt16
            };
            mesh.SetVertices(vertices);
            mesh.SetUVs(0, uvs);
            mesh.SetTriangles(triangles, 0, true);
            mesh.RecalculateNormals();
            mesh.RecalculateTangents();
            mesh.RecalculateBounds();
            return mesh;
        }

        private readonly struct ButtonRing
        {
            public ButtonRing(float radius, float height)
            {
                Radius = radius;
                Height = height;
            }

            public float Radius { get; }
            public float Height { get; }
        }
    }
}
