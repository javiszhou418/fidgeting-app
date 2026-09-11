using System;
using System.IO;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R025
{
    public sealed class IsolatedR025PortraitRenderSession : IDisposable
    {
        private readonly Camera camera;
        private readonly RenderTexture originalTarget;
        private readonly float originalAspect;
        private readonly RenderTexture target;
        private readonly Texture2D readback;
        private bool disposed;

        public IsolatedR025PortraitRenderSession(
            Camera camera,
            int width,
            int height)
        {
            if (camera == null)
            {
                throw new ArgumentNullException(nameof(camera));
            }
            if (width <= 0 || height <= 0)
            {
                throw new ArgumentOutOfRangeException(
                    nameof(width),
                    "Portrait target dimensions must be positive.");
            }

            this.camera = camera;
            Width = width;
            Height = height;
            originalAspect = camera.aspect;
            originalTarget = camera.targetTexture;
            target = new RenderTexture(
                width,
                height,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB)
            {
                antiAliasing = 1,
                useMipMap = false,
                autoGenerateMips = false
            };
            target.Create();
            readback = new Texture2D(
                width,
                height,
                TextureFormat.RGB24,
                false,
                false);
            PrepareForMeasurement();
        }

        public Camera Camera => camera;
        public int Width { get; }
        public int Height { get; }
        public float TargetAspect => Width / (float)Height;
        public float OriginalAspect => originalAspect;
        public RenderTexture OriginalTarget => originalTarget;
        public bool AspectExactlyMatchesTarget => camera.aspect == TargetAspect;
        public bool TargetExactlyMatchesSession => camera.targetTexture == target;

        public void PrepareForMeasurement()
        {
            ThrowIfDisposed();
            camera.targetTexture = target;
            camera.aspect = TargetAspect;
            if (!AspectExactlyMatchesTarget || !TargetExactlyMatchesSession)
            {
                throw new InvalidOperationException(
                    "R025 portrait projection target was not applied.");
            }
        }

        public Color32[] Capture(string path)
        {
            ThrowIfDisposed();
            if (string.IsNullOrWhiteSpace(path))
            {
                throw new ArgumentException(
                    "A capture path is required.",
                    nameof(path));
            }
            PrepareForMeasurement();
            RenderPipeline.SubmitRenderRequest(
                camera,
                new RenderPipeline.StandardRequest { destination = target });
            RenderTexture previous = RenderTexture.active;
            try
            {
                RenderTexture.active = target;
                readback.ReadPixels(
                    new Rect(0f, 0f, Width, Height),
                    0,
                    0,
                    false);
                readback.Apply(false, false);
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                File.WriteAllBytes(path, readback.EncodeToPNG());
                return readback.GetPixels32();
            }
            finally
            {
                RenderTexture.active = previous;
            }
        }

        public void Dispose()
        {
            if (disposed)
            {
                return;
            }
            disposed = true;
            camera.targetTexture = originalTarget;
            camera.aspect = originalAspect;
            target.Release();
            DestroyObject(target);
            DestroyObject(readback);
        }

        private static void DestroyObject(UnityEngine.Object item)
        {
#if UNITY_EDITOR
            if (!Application.isPlaying)
            {
                UnityEngine.Object.DestroyImmediate(item);
                return;
            }
#endif
            UnityEngine.Object.Destroy(item);
        }

        private void ThrowIfDisposed()
        {
            if (disposed)
            {
                throw new ObjectDisposedException(
                    nameof(IsolatedR025PortraitRenderSession));
            }
        }
    }
}
