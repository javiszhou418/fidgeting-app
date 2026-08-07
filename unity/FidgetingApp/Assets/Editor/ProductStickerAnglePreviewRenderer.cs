using System;
using System.IO;
using System.Linq;
using FidgetingApp.Product;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace CodexUnityLabEditor
{
    public static class ProductStickerAnglePreviewRenderer
    {
        private const string ScenePath =
            "Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity";
        private const int PreviewSize = 640;

        private readonly struct PreviewAngle
        {
            public PreviewAngle(string name, float pitch, float yaw, float distance)
            {
                Name = name;
                Pitch = pitch;
                Yaw = yaw;
                Distance = distance;
            }

            public string Name { get; }
            public float Pitch { get; }
            public float Yaw { get; }
            public float Distance { get; }
        }

        private readonly struct PreviewSticker
        {
            public PreviewSticker(string id, string name)
            {
                Id = id;
                Name = name;
            }

            public string Id { get; }
            public string Name { get; }
        }

        private readonly struct ActivationPhase
        {
            public ActivationPhase(string name, float elapsedSeconds)
            {
                Name = name;
                ElapsedSeconds = elapsedSeconds;
            }

            public string Name { get; }
            public float ElapsedSeconds { get; }
            public float ApparentScale =>
                ProductAppearanceActivationSequence.EvaluateApparentScale(
                    ElapsedSeconds);
        }

        [MenuItem("Tools/Codex/Render Long Press Activation Approval Preview")]
        public static void RenderLongPressActivationApprovalPreview()
        {
            ProductStickerArtworkImporter.ConfigureAllProductStickerArtwork();
            Scene scene = EditorSceneManager.OpenScene(
                ScenePath,
                OpenSceneMode.Single);
            GameObject productRoot = scene.GetRootGameObjects()
                .First(root => root.name == "ThreeBladeEDC_Root");
            Transform visibleTopCap = productRoot.transform.Find(
                "HubStatic/TopCap/TopCap_Root/FingerCapTop_BrushedFace");
            if (visibleTopCap == null
                || !(visibleTopCap.GetComponent<MeshRenderer>() is MeshRenderer capRenderer)
                || !capRenderer.enabled)
            {
                throw new MissingReferenceException(
                    "The topmost imported FingerCapTop_BrushedFace receiver is required.");
            }

            Camera camera = Camera.main;
            if (camera == null)
            {
                throw new MissingReferenceException("ThreeBladeEDC needs its MainCamera.");
            }

            Transform rotor = productRoot.transform.Find("RotorDynamic");
            ThreeBladeMetalSkinProgression skins = rotor != null
                ? rotor.GetComponent<ThreeBladeMetalSkinProgression>()
                    ?? rotor.gameObject.AddComponent<ThreeBladeMetalSkinProgression>()
                : null;
            if (skins == null)
            {
                throw new MissingReferenceException(
                    "The original metal scene needs its RotorDynamic skin receiver.");
            }
            skins.Apply(10, "night-cyan-index");

            SpinnerEnvironmentPresenter environment =
                SpinnerEnvironmentPresenter.Install(ScenePath);
            environment.SetLibraryPreviewActive(false, true);

            ProductStickerPresenter presenter =
                productRoot.GetComponent<ProductStickerPresenter>()
                ?? productRoot.AddComponent<ProductStickerPresenter>();
            string outputRoot = Path.Combine(
                Path.GetFullPath(Path.Combine(Application.dataPath, "..")),
                "Artifacts/Appearance/LongPressActivationV1");
            string framesRoot = Path.Combine(outputRoot, "HeroFrames");
            Directory.CreateDirectory(outputRoot);
            Directory.CreateDirectory(framesRoot);

            var angles = new[]
            {
                new PreviewAngle("top-89", 89f, 0f, 0.22f),
                new PreviewAngle("hero-42", 42f, 32f, 0.24f),
                new PreviewAngle("left-35", 35f, -48f, 0.24f),
                new PreviewAngle("right-35", 35f, 112f, 0.24f),
                new PreviewAngle("low-15", 15f, 32f, 0.25f)
            };
            var phases = new[]
            {
                new ActivationPhase("rest", 0f),
                new ActivationPhase(
                    "peak",
                    ProductAppearanceActivationSequence.PeakTimeSeconds),
                new ActivationPhase(
                    "settle",
                    ProductAppearanceActivationSequence.SettleTimeSeconds),
                new ActivationPhase(
                    "sheet-ready",
                    ProductAppearanceActivationSequence.DurationSeconds)
            };

            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            var target = new RenderTexture(
                PreviewSize,
                PreviewSize,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB)
            {
                antiAliasing = 4,
                name = "ProductLongPressActivationPreview"
            };
            target.Create();
            var readback = new Texture2D(
                PreviewSize,
                PreviewSize,
                TextureFormat.RGB24,
                false,
                false);
            var contactSheet = new Texture2D(
                PreviewSize * phases.Length,
                PreviewSize * angles.Length,
                TextureFormat.RGB24,
                false,
                false);

            try
            {
                camera.targetTexture = target;
                camera.aspect = 1f;
                camera.clearFlags = CameraClearFlags.SolidColor;
                camera.backgroundColor = Color.black;
                camera.allowHDR = false;
                camera.allowMSAA = true;
                Vector3 targetPoint = capRenderer.bounds.center;

                ApplyCameraPose(camera, targetPoint, angles[1]);
                presenter.Apply("10-meteor", camera);
                RenderCamera(camera, target);

                for (int angleIndex = 0; angleIndex < angles.Length; angleIndex++)
                {
                    for (int phaseIndex = 0; phaseIndex < phases.Length; phaseIndex++)
                    {
                        PreviewAngle angle = angles[angleIndex];
                        ActivationPhase phase = phases[phaseIndex];
                        ApplyCameraPose(
                            camera,
                            targetPoint,
                            angle,
                            phase.ApparentScale);
                        CaptureCamera(camera, target, readback);
                        File.WriteAllBytes(
                            Path.Combine(
                                outputRoot,
                                $"{angleIndex + 1:00}-{phaseIndex + 1:00}-{angle.Name}-{phase.Name}.png"),
                            readback.EncodeToPNG());
                        contactSheet.SetPixels(
                            phaseIndex * PreviewSize,
                            (angles.Length - angleIndex - 1) * PreviewSize,
                            PreviewSize,
                            PreviewSize,
                            readback.GetPixels());
                    }
                }

                contactSheet.Apply(false, false);
                File.WriteAllBytes(
                    Path.Combine(outputRoot, "long-press-activation-contact-v1.png"),
                    contactSheet.EncodeToPNG());

                const int animationFrameRate = 30;
                const int animationFrameCount = 30;
                const int leadingRestFrames = 6;
                for (int frame = 0; frame < animationFrameCount; frame++)
                {
                    float elapsed = Mathf.Clamp(
                        (frame - leadingRestFrames) / (float)animationFrameRate,
                        0f,
                        ProductAppearanceActivationSequence.DurationSeconds);
                    ApplyCameraPose(
                        camera,
                        targetPoint,
                        angles[1],
                        ProductAppearanceActivationSequence.EvaluateApparentScale(elapsed));
                    CaptureCamera(camera, target, readback);
                    File.WriteAllBytes(
                        Path.Combine(framesRoot, $"hero-{frame:000}.png"),
                        readback.EncodeToPNG());
                }

                File.WriteAllText(
                    Path.Combine(outputRoot, "README.txt"),
                    "Shipping scene: Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity\n"
                    + "Rows, top to bottom: top-89, hero-42, left-35, right-35, low-15.\n"
                    + "Columns, left to right: rest 1.000, peak 1.035 at 0.075 s, "
                    + "settle 0.992 at 0.150 s, sheet-ready 1.000 at 0.220 s.\n"
                    + "The runtime opens the existing native half sheet after sheet-ready.\n"
                    + "The visual scale is camera framing only; model transforms and physics are unchanged.\n");
            }
            finally
            {
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                UnityEngine.Object.DestroyImmediate(contactSheet);
                UnityEngine.Object.DestroyImmediate(readback);
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
            }

            Debug.Log(
                $"[Codex] Long-press activation approval preview rendered to {outputRoot}");
        }

        [MenuItem("Tools/Codex/Render Sticker Multi-Angle Approval Preview")]
        public static void RenderApprovalPreview()
        {
            ProductStickerArtworkImporter.ConfigureAllProductStickerArtwork();
            Scene scene = EditorSceneManager.OpenScene(
                ScenePath,
                OpenSceneMode.Single);
            GameObject productRoot = scene.GetRootGameObjects()
                .First(root => root.name == "ThreeBladeEDC_Root");
            Transform visibleTopCap = productRoot.transform.Find(
                "HubStatic/TopCap/TopCap_Root/FingerCapTop_BrushedFace");
            if (visibleTopCap == null
                || !(visibleTopCap.GetComponent<MeshRenderer>() is MeshRenderer capRenderer)
                || !capRenderer.enabled)
            {
                throw new MissingReferenceException(
                    "The topmost imported FingerCapTop_BrushedFace receiver is required.");
            }
            LogReceiverDiagnostics(visibleTopCap, capRenderer);

            Camera camera = Camera.main;
            if (camera == null)
            {
                throw new MissingReferenceException("ThreeBladeEDC needs its MainCamera.");
            }

            Transform rotor = productRoot.transform.Find("RotorDynamic");
            ThreeBladeMetalSkinProgression skins = rotor != null
                ? rotor.GetComponent<ThreeBladeMetalSkinProgression>()
                    ?? rotor.gameObject.AddComponent<ThreeBladeMetalSkinProgression>()
                : null;
            if (skins == null)
            {
                throw new MissingReferenceException(
                    "The original metal scene needs its RotorDynamic skin receiver.");
            }
            skins.Apply(10, "night-cyan-index");

            SpinnerEnvironmentPresenter environment =
                SpinnerEnvironmentPresenter.Install(ScenePath);
            environment.SetLibraryPreviewActive(false, true);

            ProductStickerPresenter presenter =
                productRoot.GetComponent<ProductStickerPresenter>()
                ?? productRoot.AddComponent<ProductStickerPresenter>();
            string outputRoot = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../../../Artifacts/OriginalMetalRecoveryV23"));
            Directory.CreateDirectory(outputRoot);

            var stickers = new[]
            {
                new PreviewSticker("01-polygon-cube", "pictogram"),
                new PreviewSticker("02-hw-studio", "text"),
                new PreviewSticker("21-triple-stroke", "thin-line")
            };
            var angles = new[]
            {
                new PreviewAngle("top-89", 89f, 0f, 0.22f),
                new PreviewAngle("hero-42", 42f, 32f, 0.24f),
                new PreviewAngle("left-35", 35f, -48f, 0.24f),
                new PreviewAngle("right-35", 35f, 112f, 0.24f),
                new PreviewAngle("low-15", 15f, 32f, 0.25f)
            };

            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            var target = new RenderTexture(
                PreviewSize,
                PreviewSize,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB)
            {
                antiAliasing = 4,
                name = "ProductStickerAnglePreview"
            };
            target.Create();
            var readback = new Texture2D(
                PreviewSize,
                PreviewSize,
                TextureFormat.RGB24,
                false,
                false);
            var contactSheet = new Texture2D(
                PreviewSize * angles.Length,
                PreviewSize * stickers.Length,
                TextureFormat.RGB24,
                false,
                false);
            var iceContactSheet = new Texture2D(
                PreviewSize * angles.Length,
                PreviewSize,
                TextureFormat.RGB24,
                false,
                false);

            try
            {
                camera.targetTexture = target;
                camera.aspect = 1f;
                camera.clearFlags = CameraClearFlags.SolidColor;
                camera.backgroundColor = Color.black;
                camera.allowHDR = false;
                camera.allowMSAA = true;
                Vector3 targetPoint = capRenderer.bounds.center;

                for (int stickerIndex = 0;
                     stickerIndex < stickers.Length;
                     stickerIndex++)
                {
                    PreviewSticker sticker = stickers[stickerIndex];
                    ApplyCameraPose(
                        camera,
                        targetPoint,
                        angles[1]);
                    presenter.Apply(sticker.Id, camera);
                    if (!presenter.HasAppliedSticker
                        || !presenter.UsesTopCapReceiver
                        || presenter.GeneratedSurfaceCount != 1)
                    {
                        throw new InvalidOperationException(
                            $"Sticker {sticker.Id} did not bind to one visible top cap.");
                    }

                    // Resource upload and the newly-created renderer can settle
                    // one render later in batch mode. Never approve a visual
                    // from the creation frame.
                    RenderCamera(camera, target);

                    for (int angleIndex = 0;
                         angleIndex < angles.Length;
                         angleIndex++)
                    {
                        PreviewAngle angle = angles[angleIndex];
                        ApplyCameraPose(camera, targetPoint, angle);
                        RenderCamera(camera, target);
                        RenderTexture.active = target;
                        readback.ReadPixels(
                            new Rect(0f, 0f, PreviewSize, PreviewSize),
                            0,
                            0,
                            false);
                        readback.Apply(false, false);
                        contactSheet.SetPixels(
                            angleIndex * PreviewSize,
                            (stickers.Length - stickerIndex - 1) * PreviewSize,
                            PreviewSize,
                            PreviewSize,
                            readback.GetPixels());
                        string fileName = string.Format(
                            "{0:00}-{1:00}-{2}-{3}.png",
                            stickerIndex + 1,
                            angleIndex + 1,
                            sticker.Name,
                            angle.Name);
                        File.WriteAllBytes(
                            Path.Combine(outputRoot, fileName),
                            readback.EncodeToPNG());
                    }
                }

                contactSheet.Apply(false, false);
                File.WriteAllBytes(
                    Path.Combine(outputRoot, "night-cyan-three-sticker-contact.png"),
                    contactSheet.EncodeToPNG());

                skins.Apply(35, "ice-guilloche");
                presenter.Apply("01-polygon-cube", camera);
                RenderCamera(camera, target);
                for (int angleIndex = 0; angleIndex < angles.Length; angleIndex++)
                {
                    ApplyCameraPose(camera, targetPoint, angles[angleIndex]);
                    CaptureCamera(camera, target, readback);
                    iceContactSheet.SetPixels(
                        angleIndex * PreviewSize,
                        0,
                        PreviewSize,
                        PreviewSize,
                        readback.GetPixels());
                }
                iceContactSheet.Apply(false, false);
                File.WriteAllBytes(
                    Path.Combine(outputRoot, "ice-guilloche-five-angle-contact.png"),
                    iceContactSheet.EncodeToPNG());
            }
            finally
            {
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                UnityEngine.Object.DestroyImmediate(iceContactSheet);
                UnityEngine.Object.DestroyImmediate(contactSheet);
                UnityEngine.Object.DestroyImmediate(readback);
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
            }

            Debug.Log(
                $"[Codex] Sticker approval preview rendered to {outputRoot}");
        }

        private static void ApplyCameraPose(
            Camera camera,
            Vector3 targetPoint,
            PreviewAngle angle)
        {
            ApplyCameraPose(camera, targetPoint, angle, 1f);
        }

        private static void ApplyCameraPose(
            Camera camera,
            Vector3 targetPoint,
            PreviewAngle angle,
            float apparentScale)
        {
            Quaternion orbit = Quaternion.Euler(angle.Pitch, angle.Yaw, 0f);
            camera.transform.position = targetPoint
                + orbit * (Vector3.back * angle.Distance / apparentScale);
            camera.transform.LookAt(targetPoint, Vector3.up);
        }

        private static void CaptureCamera(
            Camera camera,
            RenderTexture target,
            Texture2D readback)
        {
            RenderCamera(camera, target);
            RenderTexture.active = target;
            readback.ReadPixels(
                new Rect(0f, 0f, PreviewSize, PreviewSize),
                0,
                0,
                false);
            readback.Apply(false, false);
        }

        private static void RenderCamera(Camera camera, RenderTexture target)
        {
            RenderTexture.active = target;
            GL.Clear(true, true, Color.black);
            camera.Render();
        }

        private static void LogReceiverDiagnostics(
            Transform receiver,
            MeshRenderer renderer)
        {
            MeshFilter filter = receiver.GetComponent<MeshFilter>();
            Mesh mesh = filter != null ? filter.sharedMesh : null;
            if (mesh == null)
            {
                return;
            }

            Vector3[] normals = mesh.normals;
            Vector3 projectionNormal = receiver.InverseTransformDirection(
                Vector3.up).normalized;
            int upwardNormals = normals.Count(normal =>
                Vector3.Dot(normal.normalized, projectionNormal) >= 0.12f);
            string materialCull = "n/a";
            Material material = renderer.sharedMaterial;
            if (material != null && material.HasProperty("_Cull"))
            {
                materialCull = material.GetFloat("_Cull").ToString("0.###");
            }

            Debug.Log(
                "[Codex] Sticker receiver diagnostics: "
                + $"mesh={mesh.name}, vertices={mesh.vertexCount}, "
                + $"upwardNormals={upwardNormals}/{normals.Length}, "
                + $"worldDeterminant={receiver.localToWorldMatrix.determinant:0.######}, "
                + $"sourceCull={materialCull}, sourceShader={material?.shader?.name}.");
        }
    }
}
