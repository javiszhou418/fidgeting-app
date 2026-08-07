using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FidgetingApp.EDC.EditorTools;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEditor.iOS.Xcode;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.OptimizationValidation.Editor
{
    public static class EdcOptimizationIosBuild
    {
        public const string BundleIdentifier =
            "com.jiaweizhou.fidgetspinner.codex.edcopt";
        private const string CandidateRoot =
            "/tmp/fidgeting_edc_optimization_candidates";
        private const string GeneratedRoot =
            "Assets/_EDC/Tests/OptimizationValidation/Generated";
        private const string BootstrapScene = GeneratedRoot + "/EDC_Optimization_Bootstrap.unity";
        private const string TeamIdentifier = "2RJ2CW6NK5";

        public static void BuildIsolatedRelease()
        {
            if (!BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.iOS, BuildTarget.iOS))
            {
                throw new BuildFailedException("iOS Build Support is unavailable.");
            }

            Directory.CreateDirectory(Path.Combine(Application.dataPath,
                "_EDC/Tests/OptimizationValidation/Generated"));
            string scene750 = PrepareTier(750000);
            string scene500 = PrepareTier(500000);
            string scene416 = PrepareTier(416273);
            PrepareBootstrap();

            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string stamp = DateTime.UtcNow.ToString("yyyyMMdd-HHmmss");
            string output = Path.Combine(
                projectRoot,
                "Builds/iOS/EDCOptimizationValidation-" + stamp);
            Directory.CreateDirectory(output);

            string oldProductName = PlayerSettings.productName;
            string oldIdentifier = PlayerSettings.GetApplicationIdentifier(NamedBuildTarget.iOS);
            string oldBundleVersion = PlayerSettings.bundleVersion;
            bool oldFrameTiming = PlayerSettings.enableFrameTimingStats;
            bool oldUseDefaultGraphics = PlayerSettings.GetUseDefaultGraphicsAPIs(BuildTarget.iOS);
            GraphicsDeviceType[] oldGraphics = PlayerSettings.GetGraphicsAPIs(BuildTarget.iOS);
            bool oldDevelopment = EditorUserBuildSettings.development;
            try
            {
                if (!EditorUserBuildSettings.SwitchActiveBuildTarget(
                    BuildTargetGroup.iOS,
                    BuildTarget.iOS))
                {
                    throw new BuildFailedException("Could not switch to iOS.");
                }

                PlayerSettings.productName = "EDC Optimization Validation";
                PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.iOS, BundleIdentifier);
                PlayerSettings.bundleVersion = "0.1.1";
                PlayerSettings.iOS.buildNumber = "1";
                PlayerSettings.iOS.targetOSVersionString = "15.0";
                PlayerSettings.iOS.targetDevice = iOSTargetDevice.iPhoneOnly;
                PlayerSettings.SetScriptingBackend(
                    NamedBuildTarget.iOS,
                    ScriptingImplementation.IL2CPP);
                PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.iOS, false);
                PlayerSettings.SetGraphicsAPIs(
                    BuildTarget.iOS,
                    new[] { GraphicsDeviceType.Metal });
                PlayerSettings.enableFrameTimingStats = true;
                PlayerSettings.defaultInterfaceOrientation = UIOrientation.Portrait;
                PlayerSettings.statusBarHidden = true;
                EditorUserBuildSettings.development = false;

                int mobileQuality = Array.IndexOf(QualitySettings.names, "Mobile");
                if (mobileQuality >= 0)
                {
                    QualitySettings.SetQualityLevel(mobileQuality, true);
                }

                var options = new BuildPlayerOptions
                {
                    scenes = new[] { BootstrapScene, scene750, scene500, scene416 },
                    locationPathName = output,
                    target = BuildTarget.iOS,
                    targetGroup = BuildTargetGroup.iOS,
                    options = BuildOptions.None
                };
                BuildReport report = BuildPipeline.BuildPlayer(options);
                if (report.summary.result != BuildResult.Succeeded)
                {
                    throw new BuildFailedException(
                        "EDC optimization iOS build failed: " + report.summary.result);
                }
                ConfigureSigning(output);
                File.WriteAllText("/tmp/woz-edc-ios-build-path.txt", output + "\n");
                Debug.Log(
                    $"EDC_OPT_IOS_BUILD_COMPLETE path={output} bundle={BundleIdentifier} " +
                    $"sizeBytes={report.summary.totalSize}");
            }
            finally
            {
                PlayerSettings.productName = oldProductName;
                PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.iOS, oldIdentifier);
                PlayerSettings.bundleVersion = oldBundleVersion;
                PlayerSettings.enableFrameTimingStats = oldFrameTiming;
                PlayerSettings.SetUseDefaultGraphicsAPIs(
                    BuildTarget.iOS,
                    oldUseDefaultGraphics);
                if (!oldUseDefaultGraphics && oldGraphics != null && oldGraphics.Length > 0)
                {
                    PlayerSettings.SetGraphicsAPIs(BuildTarget.iOS, oldGraphics);
                }
                EditorUserBuildSettings.development = oldDevelopment;
                AssetDatabase.SaveAssets();
            }
        }

        public static void RepairGeneratedXcode()
        {
            string output = File.ReadAllText("/tmp/woz-edc-ios-build-path.txt").Trim();
            ConfigureSigning(output);
            Debug.Log("EDC_OPT_XCODE_REPAIRED path=" + output);
        }

        private static string PrepareTier(int tier)
        {
            string candidateFolder = Path.Combine(
                CandidateRoot,
                tier == 416273
                    ? "qem_a0_t416273"
                    : "qem_a1_t" + tier.ToString());
            string manifestPath = Path.Combine(candidateFolder, "layer-manifest.json");
            LayerManifest manifest = JsonUtility.FromJson<LayerManifest>(
                File.ReadAllText(manifestPath));
            string assetFolder = GeneratedRoot + "/t" + tier.ToString();
            Directory.CreateDirectory(Path.Combine(
                Application.dataPath,
                "_EDC/Tests/OptimizationValidation/Generated/t" + tier.ToString()));

            var meshAssets = new Dictionary<string, string>();
            foreach (LayerEntry layer in manifest.layers)
            {
                string fileName = layer.name + "_Runtime.obj";
                string source = Path.Combine(candidateFolder, fileName);
                string assetPath = assetFolder + "/" + fileName;
                string absolute = Path.GetFullPath(Path.Combine(Application.dataPath, "..", assetPath));
                File.Copy(source, absolute, true);
                meshAssets[layer.name] = assetPath;
            }
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            foreach (string assetPath in meshAssets.Values)
            {
                ConfigureImporter(assetPath);
            }

            Scene scene = EditorSceneManager.OpenScene(
                EdcSceneBuilder.ScenePath,
                OpenSceneMode.Single);
            GameObject root = scene.GetRootGameObjects()
                .Single(candidate => candidate.name == "EDC_Root");
            var paths = new Dictionary<string, string>
            {
                { "L1_TopFrame", "SliderGroup/L1_TopFrame" },
                { "L2_UpperShell", "SliderGroup/L2_UpperShell" },
                { "L3_Gasket", "Base/L3_Gasket" },
                { "L6_InnerFrame", "Base/L6_InnerFrame" },
                { "L7_BottomShell", "Base/L7_BottomShell" }
            };
            foreach (LayerEntry layer in manifest.layers)
            {
                Transform target = root.transform.Find(paths[layer.name]);
                Mesh mesh = AssetDatabase.LoadAllAssetsAtPath(meshAssets[layer.name])
                    .OfType<Mesh>()
                    .OrderByDescending(candidate => candidate.vertexCount)
                    .First();
                target.GetComponent<MeshFilter>().sharedMesh = mesh;
                target.localPosition = new Vector3(
                    layer.pivotPosition[0],
                    layer.pivotPosition[1],
                    layer.pivotPosition[2]);
            }
            EdcOptimizationMotionDriver driver =
                root.GetComponent<EdcOptimizationMotionDriver>() ??
                root.AddComponent<EdcOptimizationMotionDriver>();
            driver.Configure(tier);
            string scenePath = GeneratedRoot + "/EDC_Optimization_" + tier + ".unity";
            EditorSceneManager.SaveScene(scene, scenePath, true);
            return scenePath;
        }

        private static void PrepareBootstrap()
        {
            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            var root = new GameObject("EDC Optimization Bootstrap");
            root.AddComponent<EdcOptimizationBootstrap>();
            EditorSceneManager.SaveScene(scene, BootstrapScene, false);
        }

        private static void ConfigureImporter(string assetPath)
        {
            var importer = AssetImporter.GetAtPath(assetPath) as ModelImporter;
            if (importer == null)
            {
                throw new FileNotFoundException("Missing candidate importer", assetPath);
            }
            importer.globalScale = 1f;
            importer.useFileScale = false;
            importer.importAnimation = false;
            importer.importBlendShapes = false;
            importer.importCameras = false;
            importer.importLights = false;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            importer.meshCompression = ModelImporterMeshCompression.Off;
            importer.optimizeMeshPolygons = true;
            importer.optimizeMeshVertices = true;
            importer.weldVertices = false;
            importer.isReadable = false;
            importer.importNormals = ModelImporterNormals.Calculate;
            importer.normalCalculationMode = ModelImporterNormalCalculationMode.AreaAndAngleWeighted;
            importer.normalSmoothingAngle = 180f;
            importer.importTangents = ModelImporterTangents.CalculateMikk;
            importer.SaveAndReimport();
        }

        private static void ConfigureSigning(string output)
        {
            string projectPath = PBXProject.GetPBXProjectPath(output);
            var project = new PBXProject();
            project.ReadFromFile(projectPath);
            string main = project.GetUnityMainTargetGuid();
            string framework = project.GetUnityFrameworkTargetGuid();
            foreach (string target in new[] { main, framework })
            {
                project.SetBuildProperty(target, "DEVELOPMENT_TEAM", TeamIdentifier);
                project.SetBuildProperty(target, "CODE_SIGN_STYLE", "Automatic");
            }
            project.SetBuildProperty(main, "SWIFT_VERSION", "5.0");
            project.SetBuildProperty(main, "ALWAYS_EMBED_SWIFT_STANDARD_LIBRARIES", "YES");
            project.SetBuildProperty(
                main,
                "PRODUCT_BUNDLE_IDENTIFIER",
                BundleIdentifier);
            project.SetBuildProperty(framework, "SWIFT_VERSION", "5.0");
            project.SetBuildProperty(framework, "CLANG_ENABLE_MODULES", "YES");
            project.SetBuildProperty(
                framework,
                "PRODUCT_BUNDLE_IDENTIFIER",
                "com.unity3d.framework");
            project.AddFrameworkToProject(framework, "SwiftUI.framework", false);
            project.AddFrameworkToProject(framework, "CoreHaptics.framework", false);
            project.WriteToFile(projectPath);
        }

        [Serializable]
        private sealed class LayerManifest
        {
            public LayerEntry[] layers;
        }

        [Serializable]
        private sealed class LayerEntry
        {
            public string name;
            public float[] pivotPosition;
        }
    }
}
