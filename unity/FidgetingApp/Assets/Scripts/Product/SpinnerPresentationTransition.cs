using UnityEngine;

namespace FidgetingApp.Product
{
    public readonly struct ProductFramingProfile
    {
        public ProductFramingProfile(
            string modelId,
            float detailWidthFraction,
            float detailHeightFraction,
            float libraryWidthFraction,
            float libraryHeightFraction)
        {
            ModelId = modelId;
            DetailWidthFraction = detailWidthFraction;
            DetailHeightFraction = detailHeightFraction;
            LibraryWidthFraction = libraryWidthFraction;
            LibraryHeightFraction = libraryHeightFraction;
        }

        public string ModelId { get; }
        public float DetailWidthFraction { get; }
        public float DetailHeightFraction { get; }
        public float LibraryWidthFraction { get; }
        public float LibraryHeightFraction { get; }
    }

    /// <summary>
    /// Defines the visible viewport boundary for every product. Circular
    /// products share one boundary. Long products receive a wider boundary so
    /// their thin aspect ratio does not make them feel materially smaller.
    /// Camera distance is derived from live renderer bounds rather than an
    /// authored world-space distance.
    /// </summary>
    public static class ProductFramingCatalog
    {
        public const float CircularDetailFraction = 0.64f;
        public const float CircularLibraryFraction = 0.58f;
        public const float ElongatedDetailWidthFraction = 0.86f;
        public const float ElongatedDetailHeightFraction = 0.60f;
        public const float ElongatedLibraryWidthFraction = 0.80f;
        public const float ElongatedLibraryHeightFraction = 0.56f;
        public const float BarDetailWidthFraction = 0.82f;
        public const float BarDetailHeightFraction = 0.62f;
        public const float BarLibraryWidthFraction = 0.76f;
        public const float BarLibraryHeightFraction = 0.58f;
        public const float FanCardDetailWidthFraction = 0.84f;
        public const float FanCardDetailHeightFraction = 0.78f;
        public const float FanCardLibraryWidthFraction = 0.79f;
        public const float FanCardLibraryHeightFraction = 0.73f;

        public static ProductFramingProfile Resolve(string scenePath)
        {
            if (scenePath == SpinnerEnvironmentCatalog.TwoLobeScenePath)
            {
                return new ProductFramingProfile(
                    "graphite-two-lobe",
                    BarDetailWidthFraction,
                    BarDetailHeightFraction,
                    BarLibraryWidthFraction,
                    BarLibraryHeightFraction);
            }

            if (scenePath == SpinnerEnvironmentCatalog.EdcScenePath)
            {
                return new ProductFramingProfile(
                    "magnetic-slide-tile",
                    ElongatedDetailWidthFraction,
                    ElongatedDetailHeightFraction,
                    ElongatedLibraryWidthFraction,
                    ElongatedLibraryHeightFraction);
            }

            if (scenePath == SpinnerEnvironmentCatalog.FanCardScenePath)
            {
                return new ProductFramingProfile(
                    "magnetic-fan-card",
                    FanCardDetailWidthFraction,
                    FanCardDetailHeightFraction,
                    FanCardLibraryWidthFraction,
                    FanCardLibraryHeightFraction);
            }

            string modelId = scenePath == SpinnerEnvironmentCatalog.PointedScenePath
                ? "pointed-three-blade"
                : scenePath == SpinnerEnvironmentCatalog.ImportedScenePath
                    ? "gold-four-wing"
                    : "metal-three-blade";
            return new ProductFramingProfile(
                modelId,
                CircularDetailFraction,
                CircularDetailFraction,
                CircularLibraryFraction,
                CircularLibraryFraction);
        }
    }

    public static class ProductCameraFraming
    {
        public const float MinimumDistance = 0.01f;
        public const float DistancePadding = 0.004f;

        public static bool TryGetProductBounds(
            Transform root,
            out Bounds bounds)
        {
            bounds = default;
            if (root == null)
            {
                return false;
            }

            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            bool found = false;
            for (int index = 0; index < renderers.Length; index++)
            {
                Renderer renderer = renderers[index];
                if (renderer == null
                    || !renderer.enabled
                    || !renderer.gameObject.activeInHierarchy
                    || renderer.GetComponentInParent<Camera>() != null)
                {
                    continue;
                }

                if (!found)
                {
                    bounds = renderer.bounds;
                    found = true;
                }
                else
                {
                    bounds.Encapsulate(renderer.bounds);
                }
            }

            return found;
        }

        public static float RequiredDistance(
            Camera camera,
            Bounds bounds,
            Vector3 framingBackward,
            float widthFraction,
            float heightFraction,
            float minimumDistance = MinimumDistance,
            float distancePadding = DistancePadding,
            Vector3? focusPoint = null)
        {
            if (camera == null)
            {
                return Mathf.Max(MinimumDistance, minimumDistance);
            }

            Vector3 backward = framingBackward.sqrMagnitude > 0.0001f
                ? framingBackward.normalized
                : Vector3.back;
            Quaternion viewRotation = Quaternion.LookRotation(-backward, Vector3.up);
            Vector3 viewRight = viewRotation * Vector3.right;
            Vector3 viewUp = viewRotation * Vector3.up;
            Vector3 viewForward = viewRotation * Vector3.forward;
            // Read the effective projection rather than rebuilding it from
            // fieldOfView/aspect. Physical cameras with Horizontal gate fit
            // intentionally alter that relationship on portrait screens.
            Matrix4x4 projection = camera.projectionMatrix;
            float horizontalTangent = 1f
                / Mathf.Max(Mathf.Abs(projection.m00), 0.0001f);
            float verticalTangent = 1f
                / Mathf.Max(Mathf.Abs(projection.m11), 0.0001f);
            float usableWidth = Mathf.Clamp(widthFraction, 0.30f, 0.90f);
            float usableHeight = Mathf.Clamp(heightFraction, 0.30f, 0.90f);
            float requiredDistance = Mathf.Max(MinimumDistance, minimumDistance);
            Vector3 extents = bounds.extents;
            Vector3 focus = focusPoint ?? bounds.center;

            for (int x = -1; x <= 1; x += 2)
            {
                for (int y = -1; y <= 1; y += 2)
                {
                    for (int z = -1; z <= 1; z += 2)
                    {
                        Vector3 corner = bounds.center + new Vector3(
                            extents.x * x,
                            extents.y * y,
                            extents.z * z);
                        Vector3 offset = corner - focus;
                        float viewX = Vector3.Dot(offset, viewRight);
                        float viewY = Vector3.Dot(offset, viewUp);
                        float viewZ = Vector3.Dot(offset, viewForward);
                        float horizontalDistance = Mathf.Abs(viewX)
                            / (horizontalTangent * usableWidth)
                            - viewZ;
                        float verticalDistance = Mathf.Abs(viewY)
                            / (verticalTangent * usableHeight)
                            - viewZ;
                        requiredDistance = Mathf.Max(
                            requiredDistance,
                            horizontalDistance,
                            verticalDistance);
                    }
                }
            }

            return requiredDistance + Mathf.Max(0f, distancePadding);
        }

        public static Vector2 ProjectedViewportSize(Camera camera, Bounds bounds)
        {
            float minimumX = float.PositiveInfinity;
            float maximumX = float.NegativeInfinity;
            float minimumY = float.PositiveInfinity;
            float maximumY = float.NegativeInfinity;
            Vector3 extents = bounds.extents;
            for (int x = -1; x <= 1; x += 2)
            {
                for (int y = -1; y <= 1; y += 2)
                {
                    for (int z = -1; z <= 1; z += 2)
                    {
                        Vector3 corner = bounds.center + new Vector3(
                            extents.x * x,
                            extents.y * y,
                            extents.z * z);
                        Vector3 viewport = camera.WorldToViewportPoint(corner);
                        minimumX = Mathf.Min(minimumX, viewport.x);
                        maximumX = Mathf.Max(maximumX, viewport.x);
                        minimumY = Mathf.Min(minimumY, viewport.y);
                        maximumY = Mathf.Max(maximumY, viewport.y);
                    }
                }
            }

            return new Vector2(maximumX - minimumX, maximumY - minimumY);
        }
    }

    /// <summary>
    /// Shared timing curve for moving the same product presentation between
    /// the library pose and the interactive detail pose.
    /// </summary>
    public static class SpinnerPresentationTransition
    {
        public const float DurationSeconds = 0.42f;

        public static float ResolveProgress(float elapsedSeconds)
        {
            float normalized = Mathf.Clamp01(
                elapsedSeconds / DurationSeconds);
            return normalized * normalized * (3f - 2f * normalized);
        }
    }
}
