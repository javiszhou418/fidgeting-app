using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R019
{
    public static class IsolatedR019OrientationCalibration
    {
        private const int Width = 768;
        private const int Height = 1024;
        private const int CalibrationLayer = 30;
        private const float ArtworkBottomV = 0.020f;
        private const float ArtworkTopV = 0.815f;
        private const float MinimumIdentityMargin = 0.0125f;
        private const string SourceArtworkPath =
            "Assets/Source/Pack/gacha-pack-standard-body.png";

        public static IEnumerator Capture(
            IsolatedR019ProofSequence sequence,
            SkinnedMeshRenderer r017MirrorControlFront,
            string outputRoot,
            Result result)
        {
            if (r017MirrorControlFront == null)
            {
                throw new ArgumentNullException(nameof(r017MirrorControlFront));
            }
            if (result == null)
            {
                throw new ArgumentNullException(nameof(result));
            }

            string calibrationRoot = Path.Combine(
                outputRoot,
                "orientation-calibration");
            Directory.CreateDirectory(calibrationRoot);
            Texture2D source = LoadSourceArtwork();
            try
            {
                sequence.SetTime(0f, false);
                yield return CaptureTarget(
                    sequence.FrontFoil,
                    source,
                    Path.Combine(calibrationRoot, "r019-pack-artwork.png"),
                    "R019",
                    result.r019);
                yield return CaptureTarget(
                    r017MirrorControlFront,
                    source,
                    Path.Combine(calibrationRoot, "r017-mirror-control.png"),
                    "R017-control",
                    result.r017Control);
            }
            finally
            {
                UnityEngine.Object.Destroy(source);
            }

            result.schema =
                "premium-display-case-gate04-r019-orientation-calibration.v1";
            result.sourceArtwork = SourceArtworkPath;
            result.sourceCanvasWidth = 384;
            result.sourceCanvasHeight = 512;
            result.calibrationWidth = Width;
            result.calibrationHeight = Height;
            result.background = "neutral-unlit-rgb-46-48-52";
            result.minimumIdentityMargin = MinimumIdentityMargin;
            result.r017MirrorRegressionObserved =
                !result.r017Control.identityWins
                && string.Equals(
                    result.r017Control.winner,
                    TransformName.HorizontalFlip.ToString(),
                    StringComparison.Ordinal)
                && result.r017Control.winnerMargin >= MinimumIdentityMargin;
            result.passed = result.r019.identityWins
                && result.r019.identityMargin >= MinimumIdentityMargin
                && result.r019.frontFaceCameraFacing
                && result.r017MirrorRegressionObserved;
            WriteJson(
                Path.Combine(calibrationRoot, "r019-orientation-calibration.json"),
                result);
        }

        private static IEnumerator CaptureTarget(
            SkinnedMeshRenderer target,
            Texture2D source,
            string outputPath,
            string id,
            Candidate result)
        {
            if (target == null)
            {
                throw new ArgumentNullException(nameof(target));
            }

            Transform root = target.transform.root;
            bool wasRootActive = root.gameObject.activeSelf;
            bool wasEnabled = target.enabled;
            int previousLayer = target.gameObject.layer;
            Material[] originalMaterials = target.sharedMaterials;
            var cameraObject = new GameObject($"{id}OrientationCalibrationCamera");
            var camera = cameraObject.AddComponent<Camera>();
            var targetTexture = new RenderTexture(
                Width,
                Height,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB);
            var readback = new Texture2D(
                Width,
                Height,
                TextureFormat.RGB24,
                false,
                false);
            var baked = new Mesh { name = $"{id}_OrientationBake" };
            Material material = null;
            try
            {
                if (!wasRootActive)
                {
                    root.gameObject.SetActive(true);
                }
                target.enabled = true;
                target.gameObject.layer = CalibrationLayer;
                material = CreateCalibrationMaterial(source);
                target.sharedMaterials = new[] { material };
                ConfigureCamera(camera, target, baked);
                targetTexture.Create();

                int stateSetFrame = Time.frameCount;
                yield return null;
                int renderedAfterFrame = Time.frameCount;
                Color32[] pixels = Capture(camera, targetTexture, readback, outputPath);
                result.id = id;
                result.capturePath = Path.GetFileName(outputPath);
                result.stateSetFrame = stateSetFrame;
                result.renderedAfterFrame = renderedAfterFrame;
                result.frontFaceCameraFacing =
                    AverageFacingDot(target, baked, camera) >= 0.90f;
                Evaluate(
                    source,
                    pixels,
                    camera,
                    target,
                    baked,
                    result);
            }
            finally
            {
                target.sharedMaterials = originalMaterials;
                target.enabled = wasEnabled;
                target.gameObject.layer = previousLayer;
                if (!wasRootActive)
                {
                    root.gameObject.SetActive(false);
                }
                if (material != null)
                {
                    UnityEngine.Object.Destroy(material);
                }
                targetTexture.Release();
                UnityEngine.Object.Destroy(targetTexture);
                UnityEngine.Object.Destroy(readback);
                UnityEngine.Object.Destroy(baked);
                UnityEngine.Object.Destroy(cameraObject);
            }
        }

        private static Texture2D LoadSourceArtwork()
        {
            string path = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "..",
                SourceArtworkPath));
            byte[] bytes = File.ReadAllBytes(path);
            var source = new Texture2D(2, 2, TextureFormat.RGBA32, false);
            if (!ImageConversion.LoadImage(source, bytes, false)
                || source.width != 384
                || source.height != 512)
            {
                UnityEngine.Object.Destroy(source);
                throw new InvalidDataException(
                    "R019 needs the unchanged 384x512 Pack source artwork.");
            }
            source.filterMode = FilterMode.Bilinear;
            source.wrapMode = TextureWrapMode.Clamp;
            return source;
        }

        private static Material CreateCalibrationMaterial(Texture2D source)
        {
            Shader shader = Shader.Find(
                "FidgetingApp/Isolated/R019/OrientationCalibrationUnlit");
            if (shader == null)
            {
                throw new MissingReferenceException(
                    "R019 orientation calibration shader is unavailable.");
            }
            var material = new Material(shader)
            {
                name = "R019OrientationCalibrationUnlit",
                renderQueue = 3000
            };
            material.SetTexture("_BaseMap", source);
            material.SetColor("_BaseColor", Color.white);
            return material;
        }

        private static void ConfigureCamera(
            Camera camera,
            SkinnedMeshRenderer target,
            Mesh baked)
        {
            Bounds bounds = GetWorldBounds(target, baked);
            float aspect = Width / (float)Height;
            camera.orthographic = true;
            camera.aspect = aspect;
            camera.orthographicSize = Mathf.Max(
                bounds.size.y,
                bounds.size.x / aspect) * 0.5f + 0.015f;
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 4f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color32(46, 48, 52, 255);
            camera.allowHDR = false;
            camera.allowMSAA = false;
            camera.cullingMask = 1 << CalibrationLayer;
            camera.transform.SetPositionAndRotation(
                bounds.center + Vector3.back,
                Quaternion.LookRotation(Vector3.forward, Vector3.up));
        }

        private static Bounds GetWorldBounds(
            SkinnedMeshRenderer target,
            Mesh baked)
        {
            target.BakeMesh(baked);
            if (baked.vertexCount == 0)
            {
                throw new InvalidOperationException(
                    "R019 orientation calibration has no baked front vertices.");
            }
            Vector3 first = target.transform.TransformPoint(baked.vertices[0]);
            var result = new Bounds(first, Vector3.zero);
            foreach (Vector3 vertex in baked.vertices)
            {
                result.Encapsulate(target.transform.TransformPoint(vertex));
            }
            return result;
        }

        private static Color32[] Capture(
            Camera camera,
            RenderTexture target,
            Texture2D readback,
            string outputPath)
        {
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
                File.WriteAllBytes(outputPath, readback.EncodeToPNG());
                return readback.GetPixels32();
            }
            finally
            {
                RenderTexture.active = previous;
            }
        }

        private static void Evaluate(
            Texture2D source,
            IReadOnlyList<Color32> pixels,
            Camera camera,
            SkinnedMeshRenderer target,
            Mesh baked,
            Candidate result)
        {
            Bounds bounds = GetWorldBounds(target, baked);
            float depth = bounds.center.z - camera.transform.position.z;
            float[] error = new float[4];
            int compared = 0;
            int visible = 0;
            for (int y = 0; y < Height; y++)
            {
                float viewportY = (y + 0.5f) / Height;
                for (int x = 0; x < Width; x++)
                {
                    float viewportX = (x + 0.5f) / Width;
                    Vector3 world = camera.ViewportToWorldPoint(
                        new Vector3(viewportX, viewportY, depth));
                    float physicalU = Mathf.InverseLerp(
                        bounds.min.x,
                        bounds.max.x,
                        world.x);
                    float physicalT = Mathf.InverseLerp(
                        bounds.min.y,
                        bounds.max.y,
                        world.y);
                    if (physicalU <= 0.01f || physicalU >= 0.99f
                        || physicalT <= 0.01f || physicalT >= 0.99f)
                    {
                        continue;
                    }

                    float sourceV = Mathf.Lerp(
                        ArtworkBottomV,
                        ArtworkTopV,
                        physicalT);
                    Color identity = source.GetPixelBilinear(
                        physicalU,
                        sourceV);
                    if (identity.a < 0.96f)
                    {
                        continue;
                    }

                    Color32 actual = pixels[y * Width + x];
                    if (ColorDistance(actual, new Color32(46, 48, 52, 255))
                        > 6f)
                    {
                        visible++;
                    }
                    for (int transform = 0; transform < 4; transform++)
                    {
                        Color expected = SampleTransform(
                            source,
                            physicalU,
                            sourceV,
                            (TransformName)transform);
                        error[transform] += ColorDistance(
                            actual,
                            (Color32)expected);
                    }
                    compared++;
                }
            }

            result.comparedPixels = compared;
            result.visiblePixels = visible;
            result.scores = Enumerable.Range(0, 4)
                .Select(index => new TransformScore
                {
                    transform = ((TransformName)index).ToString(),
                    score = compared == 0
                        ? 0f
                        : 1f - error[index] / (compared * 3f * 255f)
                })
                .ToArray();
            TransformScore[] ordered = result.scores
                .OrderByDescending(item => item.score)
                .ToArray();
            result.winner = ordered[0].transform;
            result.winnerMargin = ordered[0].score - ordered[1].score;
            float identityScore = result.scores[
                (int)TransformName.Identity].score;
            float bestAlternative = result.scores
                .Where(item => item.transform != TransformName.Identity.ToString())
                .Max(item => item.score);
            result.identityMargin = identityScore - bestAlternative;
            result.identityWins = string.Equals(
                result.winner,
                TransformName.Identity.ToString(),
                StringComparison.Ordinal)
                && result.identityMargin >= MinimumIdentityMargin
                && result.comparedPixels >= 20000
                && result.visiblePixels >= 20000;
        }

        private static Color SampleTransform(
            Texture2D source,
            float u,
            float v,
            TransformName transform)
        {
            return transform switch
            {
                TransformName.HorizontalFlip =>
                    source.GetPixelBilinear(1f - u, v),
                TransformName.VerticalFlip =>
                    source.GetPixelBilinear(u, 1f - v),
                TransformName.Rotate180 =>
                    source.GetPixelBilinear(1f - u, 1f - v),
                _ => source.GetPixelBilinear(u, v)
            };
        }

        private static float AverageFacingDot(
            SkinnedMeshRenderer target,
            Mesh baked,
            Camera camera)
        {
            if (baked.normals.Length == 0)
            {
                return -1f;
            }
            Bounds bounds = GetWorldBounds(target, baked);
            Vector3 toCamera = (camera.transform.position - bounds.center)
                .normalized;
            float total = 0f;
            int count = 0;
            foreach (Vector3 normal in baked.normals)
            {
                if (normal.sqrMagnitude <= 0.000001f)
                {
                    continue;
                }
                total += Vector3.Dot(
                    target.transform.TransformDirection(normal).normalized,
                    toCamera);
                count++;
            }
            return count == 0 ? -1f : total / count;
        }

        private static float ColorDistance(Color32 left, Color32 right)
        {
            return Mathf.Abs(left.r - right.r)
                + Mathf.Abs(left.g - right.g)
                + Mathf.Abs(left.b - right.b);
        }

        private static void WriteJson(string path, object value)
        {
            File.WriteAllText(path, JsonUtility.ToJson(value, true) + "\n");
        }

        private enum TransformName
        {
            Identity,
            HorizontalFlip,
            VerticalFlip,
            Rotate180
        }

        [Serializable]
        public sealed class Result
        {
            public string schema;
            public string sourceArtwork;
            public int sourceCanvasWidth;
            public int sourceCanvasHeight;
            public int calibrationWidth;
            public int calibrationHeight;
            public string background;
            public float minimumIdentityMargin;
            public Candidate r019 = new();
            public Candidate r017Control = new();
            public bool r017MirrorRegressionObserved;
            public bool passed;
        }

        [Serializable]
        public sealed class Candidate
        {
            public string id;
            public string capturePath;
            public int stateSetFrame;
            public int renderedAfterFrame;
            public bool frontFaceCameraFacing;
            public int comparedPixels;
            public int visiblePixels;
            public TransformScore[] scores;
            public string winner;
            public float winnerMargin;
            public float identityMargin;
            public bool identityWins;
        }

        [Serializable]
        public sealed class TransformScore
        {
            public string transform;
            public float score;
        }
    }
}
