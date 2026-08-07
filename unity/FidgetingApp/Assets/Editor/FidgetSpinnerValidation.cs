using System.IO;
using CodexUnityLab;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace CodexUnityLabEditor
{
    public static class FidgetSpinnerValidation
    {
        public const string PortraitPreviewPath = "/tmp/FidgetSpinnerPortrait.png";
        private const int PreviewWidth = 1170;
        private const int PreviewHeight = 2532;

        [MenuItem("Tools/Codex/Capture iPhone Portrait Preview")]
        public static void CaptureIphonePortraitPreview()
        {
            Camera sourceCamera = Camera.main;
            GameObject spinner = GameObject.Find("FidgetSpinner");
            if (sourceCamera == null || spinner == null)
            {
                throw new MissingReferenceException("The active scene must contain Main Camera and FidgetSpinner.");
            }

            GameObject captureObject = Object.Instantiate(sourceCamera.gameObject);
            captureObject.name = "Portrait Validation Camera";
            captureObject.hideFlags = HideFlags.HideAndDontSave;
            Camera captureCamera = captureObject.GetComponent<Camera>();
            PortraitCameraFramer framer = captureObject.GetComponent<PortraitCameraFramer>();
            RenderTexture renderTexture = new RenderTexture(PreviewWidth, PreviewHeight, 24, RenderTextureFormat.ARGB32);
            Texture2D image = new Texture2D(PreviewWidth, PreviewHeight, TextureFormat.RGBA32, false);
            RenderTexture previousActive = RenderTexture.active;

            try
            {
                renderTexture.Create();
                captureCamera.targetTexture = renderTexture;
                framer.SetTarget(spinner.transform);
                framer.FrameNow();

                UnityEngine.Rendering.RenderPipeline.StandardRequest request =
                    new UnityEngine.Rendering.RenderPipeline.StandardRequest
                {
                    destination = renderTexture
                };
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(captureCamera, request);

                RenderTexture.active = renderTexture;
                image.ReadPixels(new Rect(0f, 0f, PreviewWidth, PreviewHeight), 0, 0);
                image.Apply();
                File.WriteAllBytes(PortraitPreviewPath, image.EncodeToPNG());

                CalculateMargins(captureCamera, spinner);
                Debug.Log($"[Codex] Portrait preview captured: {PortraitPreviewPath}");
            }
            finally
            {
                RenderTexture.active = previousActive;
                captureCamera.targetTexture = null;
                renderTexture.Release();
                Object.DestroyImmediate(image);
                Object.DestroyImmediate(renderTexture);
                Object.DestroyImmediate(captureObject);
            }
        }

        private static void CalculateMargins(Camera camera, GameObject spinner)
        {
            float minimumX = float.PositiveInfinity;
            float minimumY = float.PositiveInfinity;
            float maximumX = float.NegativeInfinity;
            float maximumY = float.NegativeInfinity;

            foreach (Renderer renderer in spinner.GetComponentsInChildren<Renderer>())
            {
                Bounds bounds = renderer.bounds;
                Vector3 extents = bounds.extents;
                for (int x = -1; x <= 1; x += 2)
                {
                    for (int y = -1; y <= 1; y += 2)
                    {
                        for (int z = -1; z <= 1; z += 2)
                        {
                            Vector3 corner = bounds.center + new Vector3(extents.x * x, extents.y * y, extents.z * z);
                            Vector3 viewportPoint = camera.WorldToViewportPoint(corner);
                            if (viewportPoint.z <= 0f)
                            {
                                continue;
                            }

                            minimumX = Mathf.Min(minimumX, viewportPoint.x);
                            minimumY = Mathf.Min(minimumY, viewportPoint.y);
                            maximumX = Mathf.Max(maximumX, viewportPoint.x);
                            maximumY = Mathf.Max(maximumY, viewportPoint.y);
                        }
                    }
                }
            }

            float left = minimumX * 100f;
            float right = (1f - maximumX) * 100f;
            float bottom = minimumY * 100f;
            float top = (1f - maximumY) * 100f;
            Debug.Log($"[Codex] Portrait margins: left={left:F2}%, right={right:F2}%, top={top:F2}%, bottom={bottom:F2}%");
        }
    }
}
