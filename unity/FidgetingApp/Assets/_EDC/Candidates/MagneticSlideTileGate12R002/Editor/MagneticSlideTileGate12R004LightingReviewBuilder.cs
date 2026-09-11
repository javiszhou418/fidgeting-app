using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using FidgetingApp.EDC.Gate12R002;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.Editor
{
    public static class MagneticSlideTileGate12R004LightingReviewBuilder
    {
        private const string ShippingScene = "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const string OutputRelative =
            "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/"
            + "12-shipping/rev-004-lighting";
        private const string Build42EvidenceRelative =
            "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/"
            + "12-shipping/runtime-recovery-build42";

        private static readonly ProtectedSource[] ProtectedSources =
        {
            new("interaction-controller",
                "Assets/_EDC/Runtime/EdcSliderController.cs"),
            new("shipping-coordinator",
                "Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Runtime/"
                + "MagneticSlideTileShippingCoordinator.cs"),
            new("shipping-mechanism",
                "Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Runtime/"
                + "MagneticSlideTileShippingMechanism.cs"),
            new("mechanism-settings",
                "Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Settings/"
                + "MagneticSlideTileMechanismSettingsR002.asset"),
            new("candidate-prefab",
                "Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Prefabs/"
                + "MagneticSlideTileGate12R002Candidate.prefab"),
            new("audio-renderer",
                "Assets/_EDC/Runtime/MagneticSlideDetentAudio.cs"),
            new("haptic-router",
                "Assets/Scripts/FidgetSpinner/IosHaptics.cs"),
        };

        private static readonly ViewRecipe[] Views =
        {
            new("library", new Vector3(0f, 0.070f, -0.135f),
                Vector3.zero, 42f, 1600, 1000, Pose.Closed),
            new("hero", new Vector3(0.074f, 0.072f, -0.116f),
                new Vector3(0f, 0.005f, -0.002f), 17.945253f,
                1600, 1000, Pose.Closed),
            new("top", new Vector3(0f, 0.115f, -0.006f),
                Vector3.zero, 38f, 1600, 1000, Pose.Closed),
            new("left-oblique", new Vector3(-0.055f, 0.040f, -0.055f),
                Vector3.zero, 36f, 1600, 1000, Pose.Closed),
            new("right-oblique", new Vector3(0.055f, 0.040f, -0.055f),
                Vector3.zero, 36f, 1600, 1000, Pose.Closed),
            new("low", new Vector3(0.045f, 0.018f, -0.070f),
                new Vector3(0f, 0.002f, 0f), 36f, 1600, 1000, Pose.Closed),
            new("phone", new Vector3(0.030f, 0.030f, -0.050f),
                Vector3.zero, 38f, 1290, 2796, Pose.Closed),
            new("max-open", new Vector3(0.074f, 0.072f, -0.116f),
                new Vector3(0f, 0.005f, 0.006f), 20f,
                1600, 1000, Pose.MaximumOpen),
            new("endpoint-36deg", new Vector3(0.074f, 0.072f, -0.116f),
                new Vector3(0f, 0.005f, 0f), 20f,
                1600, 1000, Pose.Endpoint36),
        };

        [MenuItem("Fidgeting/Model Pipeline/Capture Magnetic Slide Gate 12 R004 Lighting")]
        public static void CaptureLightingReview()
        {
            Scene scene = EditorSceneManager.OpenScene(
                ShippingScene, OpenSceneMode.Single);
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string output = Path.Combine(projectRoot, OutputRelative);
            Directory.CreateDirectory(output);

            Dictionary<string, string> protectedBefore =
                HashProtectedSources(projectRoot);
            string sceneBefore = Sha256(Path.Combine(projectRoot, ShippingScene));

            MagneticSlideTileShippingCoordinator coordinator =
                UnityEngine.Object.FindFirstObjectByType<
                    MagneticSlideTileShippingCoordinator>(
                    FindObjectsInactive.Include)
                ?? throw new InvalidDataException(
                    "The approved shipping coordinator is missing.");
            Camera camera = Camera.main
                ?? throw new InvalidDataException("The shipping camera is missing.");
            Light key = FindLight("Key_UpperLeft");
            Light fill = FindLight("CoolFill");
            MagneticSlideShippingLightingController lighting =
                camera.GetComponent<MagneticSlideShippingLightingController>();
            if (lighting == null)
                lighting = camera.gameObject.AddComponent<
                    MagneticSlideShippingLightingController>();
            lighting.Configure(
                key,
                fill,
                MagneticSlideLightingVariant.BalancedBrighter);

            coordinator.SetPreviewActive(true);
            coordinator.ResetShippingPose(false);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ShippingScene, false);

            CameraState cameraState = new(camera);
            foreach (MagneticSlideLightingVariant variant in
                Enum.GetValues(typeof(MagneticSlideLightingVariant)))
            {
                lighting.ApplyVariant(variant);
                string variantDirectory = Path.Combine(
                    output, VariantDirectory(variant));
                Directory.CreateDirectory(variantDirectory);
                foreach (ViewRecipe view in Views)
                {
                    ApplyPose(coordinator, view.Pose);
                    RenderView(camera, variantDirectory, view);
                }
            }

            lighting.ApplyVariant(
                MagneticSlideLightingVariant.BalancedBrighter);
            coordinator.ResetShippingPose(false);
            cameraState.Restore(camera);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ShippingScene, false);

            Dictionary<string, string> protectedAfter =
                HashProtectedSources(projectRoot);
            bool protectedUnchanged = protectedBefore.All(
                item => protectedAfter.TryGetValue(item.Key, out string after)
                    && after == item.Value);
            LightingReviewReport report = new()
            {
                pass = protectedUnchanged
                    && coordinator.CandidateModelActive
                    && !coordinator.FallbackModelActive
                    && coordinator.Mechanism.IsPoseLegal(),
                sourceScene = ShippingScene,
                sceneSha256Before = sceneBefore,
                sceneSha256After = Sha256(
                    Path.Combine(projectRoot, ShippingScene)),
                evidenceRevision = 4,
                build42FeedbackExactWording =
                    "好多了，但感觉灯光有点奇怪，主要是太暗了.",
                build42InteractionAcceptance = "partial-success",
                build42VisualAcceptance = "failed-dark-lighting",
                recommendation = "B-balanced-brighter",
                defaultSourceVariant =
                    MagneticSlideLightingVariant.BalancedBrighter.ToString(),
                protectedRuntimeUnchanged = protectedUnchanged,
                geometryChanged = false,
                materialsChanged = false,
                artworkChanged = false,
                interactionChanged = false,
                audioChanged = false,
                hapticsChanged = false,
                cameraPositionRecipesChanged = false,
                whiteBalanceTemperature = 0f,
                whiteBalanceTint = 0f,
                buildInstallPhone = false,
                deviceAcceptance = "pending-lighting-approval-and-retest",
                build42SourceHashManifest = Build42EvidenceRelative
                    + "/device-delivery/magnetic-slide-build42-"
                    + "20260901T035903Z-snapshot/source-hashes-snapshot.txt",
                protectedSources = ProtectedSources.Select(source =>
                    new HashRecord
                    {
                        id = source.Id,
                        path = source.Path,
                        sha256 = protectedAfter[source.Id],
                    }).ToArray(),
                variants = Enum.GetValues(typeof(MagneticSlideLightingVariant))
                    .Cast<MagneticSlideLightingVariant>()
                    .Select(CreateVariantRecord)
                    .ToArray(),
            };
            if (!report.pass)
                throw new InvalidDataException(
                    "Gate 12 lighting-only scope validation failed.");
            File.WriteAllText(
                Path.Combine(output, "lighting-review-report.json"),
                JsonUtility.ToJson(report, true) + Environment.NewLine);
        }

        private static VariantRecord CreateVariantRecord(
            MagneticSlideLightingVariant variant)
        {
            MagneticSlideLightingValues values =
                MagneticSlideShippingLighting.Resolve(variant);
            return new VariantRecord
            {
                id = VariantDirectory(variant),
                postExposureEv = values.PostExposureEv,
                ambientMultiplier = values.AmbientMultiplier,
                reflectionIntensity = values.ReflectionIntensity,
                keyIntensity = values.KeyIntensity,
                fillIntensity = values.FillIntensity,
                hdr = values.Hdr,
                tonemapping = values.Tonemapping.ToString(),
                whiteBalanceTemperature = 0f,
                whiteBalanceTint = 0f,
            };
        }

        private static void ApplyPose(
            MagneticSlideTileShippingCoordinator coordinator,
            Pose pose)
        {
            coordinator.ResetShippingPose(false);
            if (pose == Pose.Closed)
                return;
            coordinator.TryApplySlideInput(
                coordinator.Settings.MaximumTravelMeters, false);
            if (pose == Pose.Endpoint36)
                coordinator.TryApplyRotationInput(36f, false);
        }

        private static void RenderView(
            Camera camera,
            string directory,
            ViewRecipe view)
        {
            camera.transform.SetPositionAndRotation(
                view.Position,
                Quaternion.LookRotation(view.LookAt - view.Position, Vector3.up));
            camera.usePhysicalProperties = false;
            camera.fieldOfView = view.FieldOfView;
            camera.aspect = (float)view.Width / view.Height;
            VolumeManager.instance.Update(camera.transform, ~0);

            RenderTexture target = new(
                view.Width,
                view.Height,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.Default);
            target.Create();
            RenderTexture previousActive = RenderTexture.active;
            RenderTexture previousTarget = camera.targetTexture;
            camera.targetTexture = target;
            camera.Render();
            camera.Render();
            RenderTexture.active = target;
            Texture2D image = new(
                view.Width,
                view.Height,
                TextureFormat.RGBA32,
                false,
                false);
            image.ReadPixels(
                new Rect(0, 0, view.Width, view.Height), 0, 0);
            image.Apply(false, false);
            File.WriteAllBytes(
                Path.Combine(directory, view.Id + ".png"),
                image.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(image);
            camera.targetTexture = previousTarget;
            RenderTexture.active = previousActive;
            target.Release();
            UnityEngine.Object.DestroyImmediate(target);
        }

        private static Light FindLight(string name)
        {
            return UnityEngine.Object.FindObjectsByType<Light>(
                    FindObjectsInactive.Include,
                    FindObjectsSortMode.None)
                .Single(light => light.name == name);
        }

        private static Dictionary<string, string> HashProtectedSources(
            string projectRoot)
        {
            return ProtectedSources.ToDictionary(
                source => source.Id,
                source => Sha256(Path.Combine(projectRoot, source.Path)));
        }

        private static string VariantDirectory(
            MagneticSlideLightingVariant variant)
        {
            return variant switch
            {
                MagneticSlideLightingVariant.BalancedBrighter =>
                    "B-balanced-brighter",
                MagneticSlideLightingVariant.EverydayD65 =>
                    "C-everyday-d65",
                _ => "A-build42-baseline",
            };
        }

        private static string Sha256(string path)
        {
            using FileStream stream = File.OpenRead(path);
            using SHA256 algorithm = SHA256.Create();
            return string.Concat(
                algorithm.ComputeHash(stream)
                    .Select(value => value.ToString("x2")));
        }

        private enum Pose
        {
            Closed,
            MaximumOpen,
            Endpoint36,
        }

        private readonly struct ProtectedSource
        {
            public ProtectedSource(string id, string path)
            {
                Id = id;
                Path = path;
            }

            public string Id { get; }
            public string Path { get; }
        }

        private readonly struct ViewRecipe
        {
            public ViewRecipe(
                string id,
                Vector3 position,
                Vector3 lookAt,
                float fieldOfView,
                int width,
                int height,
                Pose pose)
            {
                Id = id;
                Position = position;
                LookAt = lookAt;
                FieldOfView = fieldOfView;
                Width = width;
                Height = height;
                Pose = pose;
            }

            public string Id { get; }
            public Vector3 Position { get; }
            public Vector3 LookAt { get; }
            public float FieldOfView { get; }
            public int Width { get; }
            public int Height { get; }
            public Pose Pose { get; }
        }

        private readonly struct CameraState
        {
            private readonly Vector3 position;
            private readonly Quaternion rotation;
            private readonly float fieldOfView;
            private readonly bool usePhysicalProperties;

            public CameraState(Camera camera)
            {
                position = camera.transform.position;
                rotation = camera.transform.rotation;
                fieldOfView = camera.fieldOfView;
                usePhysicalProperties = camera.usePhysicalProperties;
            }

            public void Restore(Camera camera)
            {
                camera.transform.SetPositionAndRotation(position, rotation);
                camera.fieldOfView = fieldOfView;
                camera.usePhysicalProperties = usePhysicalProperties;
            }
        }

        [Serializable]
        private sealed class LightingReviewReport
        {
            public bool pass;
            public string sourceScene;
            public string sceneSha256Before;
            public string sceneSha256After;
            public int evidenceRevision;
            public string build42FeedbackExactWording;
            public string build42InteractionAcceptance;
            public string build42VisualAcceptance;
            public string recommendation;
            public string defaultSourceVariant;
            public bool protectedRuntimeUnchanged;
            public bool geometryChanged;
            public bool materialsChanged;
            public bool artworkChanged;
            public bool interactionChanged;
            public bool audioChanged;
            public bool hapticsChanged;
            public bool cameraPositionRecipesChanged;
            public float whiteBalanceTemperature;
            public float whiteBalanceTint;
            public bool buildInstallPhone;
            public string deviceAcceptance;
            public string build42SourceHashManifest;
            public HashRecord[] protectedSources;
            public VariantRecord[] variants;
        }

        [Serializable]
        private sealed class HashRecord
        {
            public string id;
            public string path;
            public string sha256;
        }

        [Serializable]
        private sealed class VariantRecord
        {
            public string id;
            public float postExposureEv;
            public float ambientMultiplier;
            public float reflectionIntensity;
            public float keyIntensity;
            public float fillIntensity;
            public bool hdr;
            public string tonemapping;
            public float whiteBalanceTemperature;
            public float whiteBalanceTint;
        }
    }
}
