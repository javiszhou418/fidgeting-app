using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.Product.Gacha
{
    /// <summary>
    /// Temporarily limits the live reveal camera to one canonical case root.
    /// It prevents scene objects behind a transparent native aperture from
    /// appearing before or beside that case.
    /// </summary>
    public sealed class GachaNativeHybridSceneIsolation
    {
        private const int HighestCandidateLayer = 31;
        private const int LowestCandidateLayer = 8;
        private static readonly Color CavityClearColor = new Color(
            0.075f,
            0.080f,
            0.082f,
            1f);
        private const float CavityClearColorTolerance = 0.002f;

        private readonly List<LayerSnapshot> originalLayers =
            new List<LayerSnapshot>();
        private readonly List<CameraSnapshot> otherCameras =
            new List<CameraSnapshot>();
        private readonly List<RendererSnapshot> otherRenderers =
            new List<RendererSnapshot>();
        private Camera camera;
        private Transform caseRoot;
        private int originalCullingMask;
        private CameraClearFlags originalClearFlags;
        private Color originalBackgroundColor;
        private bool originalCameraEnabled;
        private bool renderGuardRegistered;

        public int IsolatedLayer { get; private set; } = -1;
        public int CaseRendererCount { get; private set; }
        public bool IsActive => camera != null
            && caseRoot != null
            && IsolatedLayer >= 0;
        public bool UsesCavityClearBackdrop => IsActive
            && camera.clearFlags == CameraClearFlags.SolidColor
            && MatchesCavityClearColor(camera.backgroundColor);
        public bool HasNoForeignCameras
        {
            get
            {
                for (int index = 0; index < otherCameras.Count; index++)
                {
                    Camera otherCamera = otherCameras[index].Camera;
                    if (otherCamera != null && otherCamera.enabled)
                    {
                        return false;
                    }
                }
                return true;
            }
        }
        public int ForeignRendererCount => CountForeignRenderers();
        public bool HasNoForeignRenderers
        {
            get
            {
                for (int index = 0; index < otherRenderers.Count; index++)
                {
                    Renderer renderer = otherRenderers[index].Renderer;
                    if (renderer != null && renderer.enabled)
                    {
                        return false;
                    }
                }
                return true;
            }
        }
        public bool HasOnlyCaseRenderers => IsActive
            && CaseRendererCount > 0
            && ForeignRendererCount == 0
            && HasNoForeignCameras
            && HasNoForeignRenderers;

        /// <summary>
        /// Reasserts the original isolation contract without taking new
        /// snapshots. This repairs transient camera or renderer mutations
        /// while preserving the state that Restore must return to.
        /// </summary>
        public void Maintain()
        {
            if (!IsActive)
            {
                return;
            }

            camera.enabled = true;
            camera.cullingMask = 1 << IsolatedLayer;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = CavityClearColor;
            for (int index = 0; index < otherCameras.Count; index++)
            {
                Camera otherCamera = otherCameras[index].Camera;
                if (otherCamera != null)
                {
                    otherCamera.enabled = false;
                }
            }
            for (int index = 0; index < otherRenderers.Count; index++)
            {
                Renderer otherRenderer = otherRenderers[index].Renderer;
                if (otherRenderer != null)
                {
                    otherRenderer.enabled = false;
                }
            }
        }

        public void RenderIsolatedFrame()
        {
            Maintain();
            if (!HasOnlyCaseRenderers || !UsesCavityClearBackdrop)
            {
                throw new InvalidOperationException(
                    "native-hybrid-camera-isolation-invalid");
            }
            camera.Render();
        }

        public void Apply(Camera targetCamera, Transform targetCaseRoot)
        {
            if (targetCamera == null)
            {
                throw new ArgumentNullException(nameof(targetCamera));
            }
            if (targetCaseRoot == null)
            {
                throw new ArgumentNullException(nameof(targetCaseRoot));
            }

            Restore();
            camera = targetCamera;
            caseRoot = targetCaseRoot;
            IsolatedLayer = FindUnusedLayer(targetCaseRoot);
            originalCullingMask = targetCamera.cullingMask;
            originalClearFlags = targetCamera.clearFlags;
            originalBackgroundColor = targetCamera.backgroundColor;
            originalCameraEnabled = targetCamera.enabled;
            CaptureAndAssignLayers(targetCaseRoot, IsolatedLayer);
            CaseRendererCount = CountCaseRenderers(targetCaseRoot);
            DisableForeignRenderers(targetCaseRoot);
            DisableForeignCameras(targetCamera);
            Maintain();
            RegisterRenderGuard();

            if (!HasOnlyCaseRenderers)
            {
                Restore();
                throw new InvalidOperationException(
                    "native-hybrid-camera-isolation-failed");
            }
        }

        public void Restore()
        {
            UnregisterRenderGuard();
            for (int index = originalLayers.Count - 1; index >= 0; index--)
            {
                LayerSnapshot snapshot = originalLayers[index];
                if (snapshot.Transform != null)
                {
                    snapshot.Transform.gameObject.layer = snapshot.Layer;
                }
            }
            originalLayers.Clear();
            for (int index = otherRenderers.Count - 1; index >= 0; index--)
            {
                RendererSnapshot snapshot = otherRenderers[index];
                if (snapshot.Renderer != null)
                {
                    snapshot.Renderer.enabled = snapshot.Enabled;
                }
            }
            otherRenderers.Clear();
            for (int index = otherCameras.Count - 1; index >= 0; index--)
            {
                CameraSnapshot snapshot = otherCameras[index];
                if (snapshot.Camera != null)
                {
                    snapshot.Camera.enabled = snapshot.Enabled;
                }
            }
            otherCameras.Clear();
            if (camera != null)
            {
                camera.enabled = originalCameraEnabled;
                camera.cullingMask = originalCullingMask;
                camera.clearFlags = originalClearFlags;
                camera.backgroundColor = originalBackgroundColor;
            }
            camera = null;
            caseRoot = null;
            IsolatedLayer = -1;
            CaseRendererCount = 0;
            originalCameraEnabled = false;
        }

        private void RegisterRenderGuard()
        {
            if (renderGuardRegistered)
            {
                return;
            }

            RenderPipelineManager.beginContextRendering +=
                MaintainBeforeContextRendering;
            RenderPipelineManager.beginCameraRendering +=
                MaintainBeforeCameraRendering;
            renderGuardRegistered = true;
        }

        private void UnregisterRenderGuard()
        {
            if (!renderGuardRegistered)
            {
                return;
            }

            RenderPipelineManager.beginContextRendering -=
                MaintainBeforeContextRendering;
            RenderPipelineManager.beginCameraRendering -=
                MaintainBeforeCameraRendering;
            renderGuardRegistered = false;
        }

        private void MaintainBeforeContextRendering(
            ScriptableRenderContext context,
            List<Camera> cameras)
        {
            Maintain();
        }

        private void MaintainBeforeCameraRendering(
            ScriptableRenderContext context,
            Camera renderingCamera)
        {
            Maintain();
        }

        private int FindUnusedLayer(Transform targetCaseRoot)
        {
            for (int layer = HighestCandidateLayer;
                 layer >= LowestCandidateLayer;
                 layer--)
            {
                if (CountForeignRenderers(layer, targetCaseRoot) == 0)
                {
                    return layer;
                }
            }
            throw new InvalidOperationException(
                "native-hybrid-camera-layer-unavailable");
        }

        private void CaptureAndAssignLayers(
            Transform root,
            int layer)
        {
            CaptureAndAssignLayer(root, layer);
            for (int index = 0; index < root.childCount; index++)
            {
                CaptureAndAssignLayers(root.GetChild(index), layer);
            }
        }

        private void CaptureAndAssignLayer(
            Transform target,
            int layer)
        {
            originalLayers.Add(new LayerSnapshot(
                target,
                target.gameObject.layer));
            target.gameObject.layer = layer;
        }

        private void DisableForeignCameras(Camera targetCamera)
        {
            Camera[] cameras = UnityEngine.Object.FindObjectsByType<Camera>(
                FindObjectsInactive.Include);
            for (int index = 0; index < cameras.Length; index++)
            {
                Camera candidate = cameras[index];
                if (candidate == null || candidate == targetCamera)
                {
                    continue;
                }
                otherCameras.Add(new CameraSnapshot(
                    candidate,
                    candidate.enabled));
                candidate.enabled = false;
            }
        }

        private void DisableForeignRenderers(Transform targetCaseRoot)
        {
            Renderer[] renderers = UnityEngine.Object.FindObjectsByType<
                Renderer>(FindObjectsInactive.Include);
            for (int index = 0; index < renderers.Length; index++)
            {
                Renderer renderer = renderers[index];
                if (renderer == null
                    || IsOwnedByCase(renderer.transform, targetCaseRoot))
                {
                    continue;
                }
                otherRenderers.Add(new RendererSnapshot(
                    renderer,
                    renderer.enabled));
                renderer.enabled = false;
            }
        }

        private int CountCaseRenderers(Transform root)
        {
            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            int count = 0;
            for (int index = 0; index < renderers.Length; index++)
            {
                Renderer renderer = renderers[index];
                if (renderer != null
                    && renderer.enabled
                    && renderer.gameObject.activeInHierarchy)
                {
                    count++;
                }
            }
            return count;
        }

        private int CountForeignRenderers()
        {
            return CountForeignRenderers(IsolatedLayer, caseRoot);
        }

        private static int CountForeignRenderers(
            int layer,
            Transform targetCaseRoot)
        {
            if (layer < 0 || targetCaseRoot == null)
            {
                return int.MaxValue;
            }

            Renderer[] renderers = UnityEngine.Object.FindObjectsByType<
                Renderer>(FindObjectsInactive.Include);
            int count = 0;
            for (int index = 0; index < renderers.Length; index++)
            {
                Renderer renderer = renderers[index];
                if (renderer == null
                    || renderer.gameObject.layer != layer
                    || IsOwnedByCase(renderer.transform, targetCaseRoot))
                {
                    continue;
                }
                count++;
            }
            return count;
        }

        private static bool IsOwnedByCase(
            Transform target,
            Transform targetCaseRoot)
        {
            return target == targetCaseRoot
                || target.IsChildOf(targetCaseRoot);
        }

        private static bool MatchesCavityClearColor(Color color)
        {
            return Mathf.Abs(color.r - CavityClearColor.r)
                    <= CavityClearColorTolerance
                && Mathf.Abs(color.g - CavityClearColor.g)
                    <= CavityClearColorTolerance
                && Mathf.Abs(color.b - CavityClearColor.b)
                    <= CavityClearColorTolerance
                && Mathf.Abs(color.a - CavityClearColor.a)
                    <= CavityClearColorTolerance;
        }

        private readonly struct LayerSnapshot
        {
            public LayerSnapshot(Transform transform, int layer)
            {
                Transform = transform;
                Layer = layer;
            }

            public Transform Transform { get; }
            public int Layer { get; }
        }

        private readonly struct CameraSnapshot
        {
            public CameraSnapshot(Camera camera, bool enabled)
            {
                Camera = camera;
                Enabled = enabled;
            }

            public Camera Camera { get; }
            public bool Enabled { get; }
        }

        private readonly struct RendererSnapshot
        {
            public RendererSnapshot(Renderer renderer, bool enabled)
            {
                Renderer = renderer;
                Enabled = enabled;
            }

            public Renderer Renderer { get; }
            public bool Enabled { get; }
        }
    }
}
