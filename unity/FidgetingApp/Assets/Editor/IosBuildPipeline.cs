using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.iOS.Xcode;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using FidgetingApp.Product;

namespace CodexUnityLabEditor
{
    public static class IosBuildPipeline
    {
        private const string RelativeBuildPath = "Builds/iOS/FidgetingApp";
        private const string RelativeDevelopmentBuildPath = "Builds/iOS/FidgetingAppDevelopment";
        private const string RelativeSimulatorBuildPath = "Builds/iOS/FidgetingAppSimulator";
        private const string RelativeGate12SimulatorBuildPath =
            "Builds/iOS/PremiumDisplayCaseGate12Rev4Simulator";
        private const string RelativeGate04NativeHybridSimulatorBuildPath =
            "Builds/iOS/PackTearNativeHybridGate04R026H1Simulator";
        private const string RelativeGate04NativeHybridR027SimulatorBuildPath =
            "Builds/iOS/PackTearNativeHybridGate04R027Simulator";
        private const string RelativeGate04NativeHybridR028SimulatorBuildPath =
            "Builds/iOS/PackTearNativeHybridGate04R028Simulator";
        private const string RelativeGate04NativeHybridR029SimulatorBuildPath =
            "Builds/iOS/PackTearNativeHybridGate04R029Simulator";
        private const string RelativeGate04NativeHybridR030SimulatorBuildPath =
            "Builds/iOS/PackTearNativeHybridGate04R030Simulator";
        private const string RelativeGate04NativeHybridR031SimulatorBuildPath =
            "Builds/iOS/PackTearNativeHybridGate04R031Simulator";
        private const string ProductName = "Fidget Spinner";
        private const string BundleIdentifier = "com.jiaweizhou.fidgetspinner.codex";
        private const string MinimumIosVersion = "15.0";
        private const string SourceCommitEnvironmentKey = "FIDGET_SOURCE_COMMIT";
        private const string UniqueExportPathEnvironmentKey =
            "FIDGET_IOS_EXPORT_RELATIVE_PATH";
        private const string BuildNumberEnvironmentKey =
            "FIDGET_IOS_BUILD_NUMBER";
        private const string BuildManifestFileName = "FidgetingBuildManifest.json";
        private const string PersonalTeamIdentifier = "2RJ2CW6NK5";
        private const string OxaniumFontAssetPath =
            "Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf";
        private const string OxaniumFontFileName = "Oxanium-VariableFont_wght.ttf";
        private const string ProductThumbnailAssetRootPath =
            "Assets/Plugins/iOS/Thumbnails";
        private const string SceneWallpaperAssetRootPath =
            "Assets/Plugins/iOS/SceneWallpapers";
        private const string ProductBadgeArtworkAssetRootPath =
            "Assets/Plugins/iOS/BadgeArtwork";
        private const string GachaPackArtworkAssetRootPath =
            "Assets/Plugins/iOS/GachaPacks";
        private const string ProductStickerArtworkAssetRootPath =
            "Assets/Resources/ProductStickers/BackdropWhite";
        private const string MobileRenderPipelineAssetPath =
            "Assets/Settings/Mobile_RPAsset.asset";
        private const string Gate12DisplayCasePrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R004/PresentationRoot.prefab";
        private const string Gate12DisplayCaseProfilePath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R004Profile.asset";
        private const string Gate11DisplayCaseFbxPath =
            "Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001/Models/PremiumDisplayCaseGate11R001.fbx";
        private const int SimulatorMsaaSampleCount = 4;

        private static readonly string[] ProductScenes =
            ProductCatalog.ShippingScenePaths();

        [MenuItem("Tools/Codex/Configure iOS Development Build")]
        public static void ConfigureIosDevelopmentBuild()
        {
            ConfigureIosBuild(development: true);
        }

        [MenuItem("Tools/Codex/Configure iOS Performance Build")]
        public static void ConfigureIosPerformanceBuild()
        {
            ConfigureIosBuild(development: false);
        }

        private static void ConfigureIosBuild(
            bool development,
            string buildNumber = null,
            iOSSdkVersion? sdkVersion = null)
        {
            PlayerSettings.productName = ProductName;
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.iOS, BundleIdentifier);
            PlayerSettings.bundleVersion = "0.1.0";
            if (!string.IsNullOrWhiteSpace(buildNumber))
            {
                PlayerSettings.iOS.buildNumber = buildNumber;
            }
            PlayerSettings.iOS.targetOSVersionString = MinimumIosVersion;
            PlayerSettings.iOS.targetDevice = iOSTargetDevice.iPhoneOnly;
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.iOS, ScriptingImplementation.IL2CPP);
            if (sdkVersion.HasValue)
            {
                PlayerSettings.iOS.sdkVersion = sdkVersion.Value;
            }

            PlayerSettings.defaultInterfaceOrientation = UIOrientation.Portrait;
            PlayerSettings.allowedAutorotateToPortrait = true;
            PlayerSettings.allowedAutorotateToPortraitUpsideDown = false;
            PlayerSettings.allowedAutorotateToLandscapeLeft = false;
            PlayerSettings.allowedAutorotateToLandscapeRight = false;
            PlayerSettings.statusBarHidden = true;
            PlayerSettings.iOS.requiresFullScreen = true;
            PlayerSettings.fullScreenMode = FullScreenMode.FullScreenWindow;

            // Unity 6 normalizes iOS to automatic mode during BuildPipeline.
            // iOS automatic mode resolves to Metal as its sole supported API.
            PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.iOS, true);
            PlayerSettings.enableFrameTimingStats = true;

            EditorBuildSettings.scenes = Array.ConvertAll(
                ProductScenes,
                scene => new EditorBuildSettingsScene(scene, true));
            EditorUserBuildSettings.development = development;

            int mobileQualityIndex = Array.IndexOf(QualitySettings.names, "Mobile");
            if (mobileQualityIndex >= 0)
            {
                QualitySettings.SetQualityLevel(mobileQualityIndex, true);
            }

            ProductStickerArtworkImporter.ConfigureAllProductStickerArtwork();
            AssetDatabase.SaveAssets();
            Debug.Log($"[Codex] iOS settings configured: {ProductName}, {BundleIdentifier}, iOS {MinimumIosVersion}+");
        }

        public static void PrepareUniqueIosDevelopmentSnapshot()
        {
            string buildNumber = RequireBuildNumberEnvironment();
            if (!BuildPipeline.IsBuildTargetSupported(
                    BuildTargetGroup.iOS,
                    BuildTarget.iOS))
            {
                throw new BuildFailedException(
                    "iOS Build Support is not installed for this Unity editor.");
            }
            if (!EditorUserBuildSettings.SwitchActiveBuildTarget(
                    BuildTargetGroup.iOS,
                    BuildTarget.iOS))
            {
                throw new BuildFailedException(
                    "Unity could not switch the active build target to iOS.");
            }

            ConfigureIosBuild(
                development: true,
                buildNumber,
                iOSSdkVersion.DeviceSDK);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            EnsurePreparedIosSnapshot(
                iOSSdkVersion.DeviceSDK,
                development: true,
                buildNumber);
            Debug.Log(
                $"[Codex] iOS immutable snapshot prepared for Build {buildNumber}");
        }

        [MenuItem("Tools/Codex/Build iOS Development Project")]
        public static void BuildIosDevelopmentProject()
        {
            BuildIosProject(
                iOSSdkVersion.DeviceSDK,
                RelativeDevelopmentBuildPath,
                configureSigning: true,
                development: true);
        }

        [MenuItem("Tools/Codex/Build Unique iOS Development Project")]
        public static void BuildUniqueIosDevelopmentProject()
        {
            string relativePath = Environment.GetEnvironmentVariable(
                UniqueExportPathEnvironmentKey);
            string buildNumber = RequireBuildNumberEnvironment();
            if (string.IsNullOrWhiteSpace(relativePath)
                || !relativePath.StartsWith(
                    "Builds/iOS/DeviceJobs/", StringComparison.Ordinal)
                || relativePath.Contains(".."))
            {
                throw new BuildFailedException(
                    $"{UniqueExportPathEnvironmentKey} must name a unique "
                    + "Builds/iOS/DeviceJobs/ child.");
            }
            BuildIosProject(
                iOSSdkVersion.DeviceSDK,
                relativePath,
                configureSigning: true,
                development: true,
                usePreparedSnapshot: true,
                expectedBuildNumber: buildNumber);
        }

        [MenuItem("Tools/Codex/Build iOS Performance Project")]
        public static void BuildIosPerformanceProject()
        {
            BuildIosProject(
                iOSSdkVersion.DeviceSDK,
                RelativeBuildPath,
                configureSigning: true,
                development: false);
        }

        [MenuItem("Tools/Codex/Clean Generated Cache Duplicates")]
        public static void CleanGeneratedCacheDuplicates()
        {
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            EnsureNoSourceDuplicateFiles(projectRoot);
            QuarantineGeneratedCacheDuplicates(projectRoot);
        }

        [MenuItem("Tools/Codex/Build iOS Simulator Project")]
        public static void BuildIosSimulatorProject()
        {
            BuildIosProject(
                iOSSdkVersion.SimulatorSDK,
                RelativeSimulatorBuildPath,
                configureSigning: false,
                development: false);
        }

        [MenuItem("Tools/Codex/Build Premium Display Case Gate 12 Simulator")]
        public static void BuildPremiumDisplayCaseGate12SimulatorProject()
        {
            NamedBuildTarget target = NamedBuildTarget.iOS;
            string previousDefines =
                PlayerSettings.GetScriptingDefineSymbols(target);
            string previewDefines = string.IsNullOrWhiteSpace(previousDefines)
                ? "FIDGET_GATE12_SIMULATOR_PREVIEW"
                : previousDefines + ";FIDGET_GATE12_SIMULATOR_PREVIEW";
            try
            {
                PlayerSettings.SetScriptingDefineSymbols(
                    target,
                    previewDefines);
                BuildIosProject(
                    iOSSdkVersion.SimulatorSDK,
                    RelativeGate12SimulatorBuildPath,
                    configureSigning: false,
                    development: false);
            }
            finally
            {
                PlayerSettings.SetScriptingDefineSymbols(
                    target,
                    previousDefines);
            }
        }

        [MenuItem("Tools/Codex/Build Pack Tear Native Hybrid Gate 04 Simulator")]
        public static void BuildPackTearNativeHybridGate04SimulatorProject()
        {
            NamedBuildTarget target = NamedBuildTarget.iOS;
            string previousDefines =
                PlayerSettings.GetScriptingDefineSymbols(target);
            string previewDefines = string.IsNullOrWhiteSpace(previousDefines)
                ? "FIDGET_GATE12_SIMULATOR_PREVIEW;FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE"
                : previousDefines
                    + ";FIDGET_GATE12_SIMULATOR_PREVIEW"
                    + ";FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE";
            try
            {
                PlayerSettings.SetScriptingDefineSymbols(
                    target,
                    previewDefines);
                BuildIosProject(
                    iOSSdkVersion.SimulatorSDK,
                    RelativeGate04NativeHybridSimulatorBuildPath,
                    configureSigning: false,
                    development: false);
                ConfigureNativeHybridCandidateSwiftPreview();
            }
            finally
            {
                PlayerSettings.SetScriptingDefineSymbols(
                    target,
                    previousDefines);
            }
        }

        [MenuItem(
            "Tools/Codex/Build Pack Tear Isolated Native Hybrid Gate 04 R027 Simulator")]
        public static void BuildPackTearNativeHybridGate04R027SimulatorProject()
        {
            NamedBuildTarget target = NamedBuildTarget.iOS;
            string previousDefines =
                PlayerSettings.GetScriptingDefineSymbols(target);
            string previewDefines = string.IsNullOrWhiteSpace(previousDefines)
                ? "FIDGET_GATE12_SIMULATOR_PREVIEW;FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE"
                : previousDefines
                    + ";FIDGET_GATE12_SIMULATOR_PREVIEW"
                    + ";FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE";
            try
            {
                PlayerSettings.SetScriptingDefineSymbols(
                    target,
                    previewDefines);
                BuildIosProject(
                    iOSSdkVersion.SimulatorSDK,
                    RelativeGate04NativeHybridR027SimulatorBuildPath,
                    configureSigning: false,
                    development: false);
            }
            finally
            {
                PlayerSettings.SetScriptingDefineSymbols(
                    target,
                    previousDefines);
            }
        }

        [MenuItem(
            "Tools/Codex/Build Pack Tear Isolated Native Hybrid Gate 04 R028 Simulator")]
        public static void BuildPackTearNativeHybridGate04R028SimulatorProject()
        {
            NamedBuildTarget target = NamedBuildTarget.iOS;
            string previousDefines =
                PlayerSettings.GetScriptingDefineSymbols(target);
            string previewDefines = string.IsNullOrWhiteSpace(previousDefines)
                ? "FIDGET_GATE12_SIMULATOR_PREVIEW;FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE"
                : previousDefines
                    + ";FIDGET_GATE12_SIMULATOR_PREVIEW"
                    + ";FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE";
            try
            {
                PlayerSettings.SetScriptingDefineSymbols(
                    target,
                    previewDefines);
                BuildIosProject(
                    iOSSdkVersion.SimulatorSDK,
                    RelativeGate04NativeHybridR028SimulatorBuildPath,
                    configureSigning: false,
                    development: false);
            }
            finally
            {
                PlayerSettings.SetScriptingDefineSymbols(
                    target,
                    previousDefines);
            }
        }

        [MenuItem(
            "Tools/Codex/Build Pack Tear Isolated Native Hybrid Gate 04 R029 Simulator")]
        public static void BuildPackTearNativeHybridGate04R029SimulatorProject()
        {
            NamedBuildTarget target = NamedBuildTarget.iOS;
            string previousDefines =
                PlayerSettings.GetScriptingDefineSymbols(target);
            string previewDefines = string.IsNullOrWhiteSpace(previousDefines)
                ? "FIDGET_GATE12_SIMULATOR_PREVIEW;FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE"
                : previousDefines
                    + ";FIDGET_GATE12_SIMULATOR_PREVIEW"
                    + ";FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE";
            try
            {
                PlayerSettings.SetScriptingDefineSymbols(
                    target,
                    previewDefines);
                BuildIosProject(
                    iOSSdkVersion.SimulatorSDK,
                    RelativeGate04NativeHybridR029SimulatorBuildPath,
                    configureSigning: false,
                    development: false);
            }
            finally
            {
                PlayerSettings.SetScriptingDefineSymbols(
                    target,
                    previousDefines);
            }
        }

        [MenuItem(
            "Tools/Codex/Build Pack Tear Isolated Native Hybrid Gate 04 R030 Simulator")]
        public static void BuildPackTearNativeHybridGate04R030SimulatorProject()
        {
            NamedBuildTarget target = NamedBuildTarget.iOS;
            string previousDefines =
                PlayerSettings.GetScriptingDefineSymbols(target);
            string previewDefines = string.IsNullOrWhiteSpace(previousDefines)
                ? "FIDGET_GATE12_SIMULATOR_PREVIEW;FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE"
                : previousDefines
                    + ";FIDGET_GATE12_SIMULATOR_PREVIEW"
                    + ";FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE";
            try
            {
                PlayerSettings.SetScriptingDefineSymbols(
                    target,
                    previewDefines);
                BuildIosProject(
                    iOSSdkVersion.SimulatorSDK,
                    RelativeGate04NativeHybridR030SimulatorBuildPath,
                    configureSigning: false,
                    development: false);
            }
            finally
            {
                PlayerSettings.SetScriptingDefineSymbols(
                    target,
                    previousDefines);
            }
        }

        [MenuItem(
            "Tools/Codex/Build Pack Tear Isolated Native Hybrid Gate 04 R031 Simulator")]
        public static void BuildPackTearNativeHybridGate04R031SimulatorProject()
        {
            NamedBuildTarget target = NamedBuildTarget.iOS;
            string previousDefines =
                PlayerSettings.GetScriptingDefineSymbols(target);
            string previewDefines = string.IsNullOrWhiteSpace(previousDefines)
                ? "FIDGET_GATE12_SIMULATOR_PREVIEW;FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE"
                : previousDefines
                    + ";FIDGET_GATE12_SIMULATOR_PREVIEW"
                    + ";FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE";
            try
            {
                PlayerSettings.SetScriptingDefineSymbols(
                    target,
                    previewDefines);
                BuildIosProject(
                    iOSSdkVersion.SimulatorSDK,
                    RelativeGate04NativeHybridR031SimulatorBuildPath,
                    configureSigning: false,
                    development: false);
            }
            finally
            {
                PlayerSettings.SetScriptingDefineSymbols(
                    target,
                    previousDefines);
            }
        }

        private static void ConfigureNativeHybridCandidateSwiftPreview()
        {
            string projectRoot = Path.GetFullPath(
                Path.Combine(Application.dataPath, ".."));
            string outputPath = Path.Combine(
                projectRoot,
                RelativeGate04NativeHybridSimulatorBuildPath);
            string projectPath = PBXProject.GetPBXProjectPath(outputPath);
            var project = new PBXProject();
            project.ReadFromFile(projectPath);
            project.AddBuildProperty(
                project.GetUnityFrameworkTargetGuid(),
                "SWIFT_ACTIVE_COMPILATION_CONDITIONS",
                "FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE");
            project.WriteToFile(projectPath);
        }

        private static void BuildIosProject(
            iOSSdkVersion sdkVersion,
            string relativeBuildPath,
            bool configureSigning,
            bool development,
            bool usePreparedSnapshot = false,
            string expectedBuildNumber = null)
        {
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            QuarantineGeneratedCacheDuplicates(projectRoot);

            if (!BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.iOS, BuildTarget.iOS))
            {
                throw new BuildFailedException("iOS Build Support is not installed for this Unity editor.");
            }

            if (usePreparedSnapshot)
            {
                EnsurePreparedIosSnapshot(
                    sdkVersion,
                    development,
                    expectedBuildNumber);
            }
            else
            {
                if (!EditorUserBuildSettings.SwitchActiveBuildTarget(
                        BuildTargetGroup.iOS,
                        BuildTarget.iOS))
                {
                    throw new BuildFailedException(
                        "Unity could not switch the active build target to iOS.");
                }
                ConfigureIosBuild(
                    development,
                    sdkVersion: sdkVersion);
            }

            EnsureCanonicalProductIdentity();
            if (sdkVersion == iOSSdkVersion.SimulatorSDK)
            {
                // Apple-silicon Simulator devices reject x86_64-only apps.
                // Keep preview builds on the same arm64 architecture used by
                // the currently supported local Simulator runtime.
                PlayerSettings.iOS.simulatorSdkArchitecture =
                    AppleMobileArchitectureSimulator.ARM64;
            }
            QuarantineGeneratedCacheDuplicates(projectRoot);

            string outputPath = Path.Combine(projectRoot, relativeBuildPath);
            if (Directory.Exists(outputPath))
            {
                string previousOutputPath = Path.Combine(
                    Path.GetTempPath(),
                    "FidgetingAppPreviousXcode",
                    DateTime.UtcNow.ToString("yyyyMMdd-HHmmss-fff"));
                Directory.CreateDirectory(Path.GetDirectoryName(previousOutputPath));
                Directory.Move(outputPath, previousOutputPath);
                Debug.Log($"[Codex] Previous generated Xcode project moved to {previousOutputPath}");
            }
            Directory.CreateDirectory(outputPath);

            BuildPlayerOptions options = new BuildPlayerOptions
            {
                scenes = ProductScenes,
                locationPathName = outputPath,
                target = BuildTarget.iOS,
                targetGroup = BuildTargetGroup.iOS,
                options = development
                    ? BuildOptions.Development | BuildOptions.ConnectWithProfiler
                    : BuildOptions.None
            };

            BuildReport report = BuildPlayerWithSimulatorMsaaWorkaround(
                options,
                sdkVersion);
            if (report.summary.result != BuildResult.Succeeded)
            {
                throw new BuildFailedException($"iOS build failed: {report.summary.result}");
            }

            ConfigureProductFont(projectRoot, outputPath);
            ConfigureProductThumbnails(projectRoot, outputPath);
            ConfigureGeneratedPlist(outputPath);
            ConfigureSwiftSupport(outputPath);
            if (configureSigning)
            {
                ConfigureXcodeAutomaticSigning(outputPath);
            }
            WriteBuildManifest(outputPath, development, sdkVersion);

            string sdkLabel = sdkVersion == iOSSdkVersion.SimulatorSDK ? "Simulator" : "Device";
            Debug.Log($"[Codex] iOS {sdkLabel} Xcode project created at {outputPath}");
        }

        private static string RequireBuildNumberEnvironment()
        {
            string buildNumber = Environment.GetEnvironmentVariable(
                BuildNumberEnvironmentKey);
            if (!int.TryParse(buildNumber, out int numericBuildNumber)
                || numericBuildNumber <= 0)
            {
                throw new BuildFailedException(
                    $"{BuildNumberEnvironmentKey} must be a positive integer.");
            }
            return numericBuildNumber.ToString();
        }

        private static void EnsurePreparedIosSnapshot(
            iOSSdkVersion sdkVersion,
            bool development,
            string expectedBuildNumber)
        {
            if (EditorUserBuildSettings.activeBuildTarget != BuildTarget.iOS)
            {
                throw new BuildFailedException(
                    "The immutable snapshot was not prepared for iOS.");
            }
            if (string.IsNullOrWhiteSpace(expectedBuildNumber)
                || PlayerSettings.iOS.buildNumber != expectedBuildNumber)
            {
                throw new BuildFailedException(
                    "The prepared iOS build number changed after snapshot setup.");
            }
            if (PlayerSettings.bundleVersion != "0.1.0"
                || PlayerSettings.iOS.sdkVersion != sdkVersion
                || EditorUserBuildSettings.development != development)
            {
                throw new BuildFailedException(
                    "Prepared iOS PlayerSettings do not match the requested build.");
            }
            GraphicsDeviceType[] graphicsApis =
                PlayerSettings.GetGraphicsAPIs(BuildTarget.iOS);
            if (!PlayerSettings.GetUseDefaultGraphicsAPIs(BuildTarget.iOS)
                || graphicsApis.Length != 1
                || graphicsApis[0] != GraphicsDeviceType.Metal)
            {
                throw new BuildFailedException(
                    "Prepared iOS graphics APIs must be automatic Metal-only.");
            }
            EnsureCanonicalProductIdentity();
        }

        private static BuildReport BuildPlayerWithSimulatorMsaaWorkaround(
            BuildPlayerOptions options,
            iOSSdkVersion sdkVersion)
        {
            if (sdkVersion != iOSSdkVersion.SimulatorSDK)
            {
                return BuildPipeline.BuildPlayer(options);
            }

            UniversalRenderPipelineAsset mobilePipeline =
                AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(
                    MobileRenderPipelineAssetPath);
            if (mobilePipeline == null)
            {
                throw new BuildFailedException(
                    $"Simulator MSAA workaround requires {MobileRenderPipelineAssetPath}.");
            }

            int originalPipelineMsaa = mobilePipeline.msaaSampleCount;
            int originalQualityMsaa = QualitySettings.antiAliasing;
            try
            {
                // Current Apple-silicon iOS Simulator backbuffers are 4x.
                // Matching them during export prevents URP's final pass from
                // requesting a 2x attachment inside a 4x native render pass.
                // The finally block restores the shipping iPhone 2x budget.
                mobilePipeline.msaaSampleCount = SimulatorMsaaSampleCount;
                QualitySettings.antiAliasing = SimulatorMsaaSampleCount;
                EditorUtility.SetDirty(mobilePipeline);
                AssetDatabase.SaveAssets();
                return BuildPipeline.BuildPlayer(options);
            }
            finally
            {
                mobilePipeline.msaaSampleCount = originalPipelineMsaa;
                QualitySettings.antiAliasing = originalQualityMsaa;
                EditorUtility.SetDirty(mobilePipeline);
                AssetDatabase.SaveAssets();
            }
        }

        [Serializable]
        private sealed class IosBuildManifest
        {
            public string bundleIdentifier;
            public string version;
            public string buildNumber;
            public string sourceCommit;
            public string generatedAtUtc;
            public string sdk;
            public bool development;
            public string[] scenes;
            public string gate12DisplayCasePrefab;
            public string gate12DisplayCasePrefabSha256;
            public string gate12DisplayCaseProfileSha256;
            public string gate11DisplayCaseFbxSha256;
            public bool physicalPhoneInstallAuthorized;
        }

        private static void WriteBuildManifest(
            string outputPath,
            bool development,
            iOSSdkVersion sdkVersion)
        {
            string sourceCommit = Environment.GetEnvironmentVariable(
                SourceCommitEnvironmentKey);
            bool deviceRelease = !development && sdkVersion == iOSSdkVersion.DeviceSDK;
            if (deviceRelease && string.IsNullOrWhiteSpace(sourceCommit))
            {
                throw new BuildFailedException(
                    $"Release builds require {SourceCommitEnvironmentKey}; use the guarded repository build script.");
            }

            string projectRoot = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                ".."));
            var manifest = new IosBuildManifest
            {
                bundleIdentifier = BundleIdentifier,
                version = PlayerSettings.bundleVersion,
                buildNumber = PlayerSettings.iOS.buildNumber,
                sourceCommit = string.IsNullOrWhiteSpace(sourceCommit)
                    ? "local-preview"
                    : sourceCommit,
                generatedAtUtc = DateTime.UtcNow.ToString("O"),
                sdk = sdkVersion.ToString(),
                development = development,
                scenes = (string[])ProductScenes.Clone(),
                gate12DisplayCasePrefab = Gate12DisplayCasePrefabPath,
                gate12DisplayCasePrefabSha256 = Sha256File(Path.Combine(
                    projectRoot,
                    Gate12DisplayCasePrefabPath)),
                gate12DisplayCaseProfileSha256 = Sha256File(Path.Combine(
                    projectRoot,
                    Gate12DisplayCaseProfilePath)),
                gate11DisplayCaseFbxSha256 = Sha256File(Path.Combine(
                    projectRoot,
                    Gate11DisplayCaseFbxPath)),
                physicalPhoneInstallAuthorized = false
            };
            File.WriteAllText(
                Path.Combine(outputPath, BuildManifestFileName),
                JsonUtility.ToJson(manifest, true));
        }

        private static string Sha256File(string path)
        {
            if (!File.Exists(path))
            {
                throw new BuildFailedException(
                    "Build provenance source is missing: " + path);
            }
            using SHA256 sha = SHA256.Create();
            byte[] digest = sha.ComputeHash(File.ReadAllBytes(path));
            return BitConverter.ToString(digest)
                .Replace("-", string.Empty)
                .ToLowerInvariant();
        }

        private static void EnsureCanonicalProductIdentity()
        {
            string configuredIdentifier = PlayerSettings.GetApplicationIdentifier(NamedBuildTarget.iOS);
            if (!string.Equals(configuredIdentifier, BundleIdentifier, StringComparison.Ordinal))
            {
                throw new BuildFailedException(
                    $"Refusing to build a second app identity. Expected {BundleIdentifier}, " +
                    $"but found {configuredIdentifier}.");
            }

            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            foreach (string scenePath in ProductScenes)
            {
                if (!File.Exists(Path.Combine(projectRoot, scenePath)))
                {
                    throw new BuildFailedException($"Required product scene is missing: {scenePath}");
                }
            }
        }

        private static void EnsureNoSourceDuplicateFiles(string projectRoot)
        {
            string assetsPath = Path.Combine(projectRoot, "Assets");
            if (!Directory.Exists(assetsPath))
            {
                return;
            }

            List<string> conflicts = new List<string>();
            string[] candidates = Directory.GetFiles(assetsPath, "*.*", SearchOption.AllDirectories);
            foreach (string candidatePath in candidates)
            {
                if (!IsBuildSourceFile(candidatePath) ||
                    !TryGetCanonicalDuplicatePath(candidatePath, out string canonicalPath))
                {
                    continue;
                }

                conflicts.Add(
                    Path.GetRelativePath(projectRoot, candidatePath) +
                    " duplicates " +
                    Path.GetRelativePath(projectRoot, canonicalPath));
            }

            if (conflicts.Count > 0)
            {
                throw new BuildFailedException(
                    "Numbered source duplicates were found in Assets. Resolve them before building:\n" +
                    string.Join("\n", conflicts));
            }
        }

        private static bool IsBuildSourceFile(string path)
        {
            string extension = Path.GetExtension(path);
            return string.Equals(extension, ".cs", StringComparison.OrdinalIgnoreCase)
                || string.Equals(extension, ".swift", StringComparison.OrdinalIgnoreCase)
                || string.Equals(extension, ".m", StringComparison.OrdinalIgnoreCase)
                || string.Equals(extension, ".mm", StringComparison.OrdinalIgnoreCase)
                || string.Equals(extension, ".h", StringComparison.OrdinalIgnoreCase)
                || string.Equals(extension, ".hpp", StringComparison.OrdinalIgnoreCase)
                || string.Equals(extension, ".cpp", StringComparison.OrdinalIgnoreCase);
        }

        private static void QuarantineGeneratedCacheDuplicates(string projectRoot)
        {
            string beeArtifactsPath = Path.Combine(projectRoot, "Library/Bee/artifacts");
            if (!Directory.Exists(beeArtifactsPath))
            {
                return;
            }

            string quarantineRoot = Path.Combine(
                Path.GetTempPath(),
                "CodexUnityGeneratedDuplicates",
                DateTime.UtcNow.ToString("yyyyMMdd-HHmmss-fff"));
            int quarantinedCount = 0;
            int promotedNewerCount = 0;

            // iCloud conflict copies use names such as "Assembly-CSharp 3.dll".
            // Only treat a numbered file as a duplicate when its canonical sibling exists.
            string[] candidates = Directory.GetFiles(beeArtifactsPath, "*.dll", SearchOption.AllDirectories);
            int duplicateCount = 0;
            foreach (string candidatePath in candidates)
            {
                if (TryGetCanonicalDuplicatePath(candidatePath, out _))
                {
                    duplicateCount++;
                }
            }

            // A large conflict set means the generated graph is broadly polluted.
            // Quarantining the whole rebuildable cache is both safer and much faster
            // than moving hundreds of iCloud conflict files one at a time.
            if (duplicateCount >= 20)
            {
                string fullCacheQuarantinePath = Path.Combine(
                    Path.GetDirectoryName(beeArtifactsPath),
                    "artifacts.codex-quarantine-" + DateTime.UtcNow.ToString("yyyyMMdd-HHmmss-fff"));
                Directory.Move(beeArtifactsPath, fullCacheQuarantinePath);
                Directory.CreateDirectory(beeArtifactsPath);
                Debug.Log(
                    $"[Codex] Build preflight found {duplicateCount} generated duplicate assemblies; " +
                    $"quarantined the complete rebuildable Bee artifacts cache at {fullCacheQuarantinePath}");
                return;
            }

            foreach (string duplicatePath in candidates)
            {
                if (!TryGetCanonicalDuplicatePath(duplicatePath, out string canonicalPath))
                {
                    continue;
                }

                string relativePath = Path.GetRelativePath(beeArtifactsPath, duplicatePath);
                string quarantinePath = Path.Combine(quarantineRoot, relativePath);
                Directory.CreateDirectory(Path.GetDirectoryName(quarantinePath));

                if (File.GetLastWriteTimeUtc(duplicatePath) > File.GetLastWriteTimeUtc(canonicalPath))
                {
                    string oldCanonicalPath = quarantinePath + ".older-canonical";
                    File.Move(canonicalPath, oldCanonicalPath);
                    File.Move(duplicatePath, canonicalPath);
                    promotedNewerCount++;
                }
                else
                {
                    File.Move(duplicatePath, quarantinePath);
                }

                quarantinedCount++;
            }

            if (quarantinedCount > 0)
            {
                Debug.Log(
                    $"[Codex] Build preflight quarantined {quarantinedCount} generated duplicate assemblies " +
                    $"({promotedNewerCount} newer copies promoted) at {quarantineRoot}");
            }
        }

        private static bool TryGetCanonicalDuplicatePath(
            string candidatePath,
            out string canonicalPath)
        {
            canonicalPath = null;
            string fileNameWithoutExtension = Path.GetFileNameWithoutExtension(candidatePath);
            int separatorIndex = fileNameWithoutExtension.LastIndexOf(' ');
            if (separatorIndex <= 0 ||
                !int.TryParse(fileNameWithoutExtension.Substring(separatorIndex + 1), out int suffix) ||
                suffix < 2)
            {
                return false;
            }

            string canonicalName = fileNameWithoutExtension.Substring(0, separatorIndex)
                + Path.GetExtension(candidatePath);
            canonicalPath = Path.Combine(Path.GetDirectoryName(candidatePath), canonicalName);
            return File.Exists(canonicalPath);
        }

        [MenuItem("Tools/Codex/Configure Generated Xcode Signing")]
        public static void ConfigureGeneratedXcodeSigning()
        {
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            ConfigureXcodeAutomaticSigning(Path.Combine(projectRoot, RelativeBuildPath));
        }

        private static void ConfigureXcodeAutomaticSigning(string outputPath)
        {
            string projectPath = PBXProject.GetPBXProjectPath(outputPath);
            if (!File.Exists(projectPath))
            {
                throw new FileNotFoundException("Generated Xcode project was not found.", projectPath);
            }

            PBXProject project = new PBXProject();
            project.ReadFromFile(projectPath);
            string mainTarget = project.GetUnityMainTargetGuid();
            project.SetBuildProperty(mainTarget, "DEVELOPMENT_TEAM", PersonalTeamIdentifier);
            project.SetBuildProperty(mainTarget, "CODE_SIGN_STYLE", "Automatic");

            string frameworkTarget = project.GetUnityFrameworkTargetGuid();
            if (!string.IsNullOrEmpty(frameworkTarget))
            {
                project.SetBuildProperty(frameworkTarget, "DEVELOPMENT_TEAM", PersonalTeamIdentifier);
                project.SetBuildProperty(frameworkTarget, "CODE_SIGN_STYLE", "Automatic");
            }
            project.WriteToFile(projectPath);

            string projectText = File.ReadAllText(projectPath);
            string targetMarker = $"{mainTarget} = {{";
            int targetStart = projectText.IndexOf(targetMarker, StringComparison.Ordinal);
            int teamStart = targetStart < 0
                ? -1
                : projectText.IndexOf("DevelopmentTeam = ", targetStart, StringComparison.Ordinal);
            if (teamStart >= 0 && teamStart - targetStart < 512)
            {
                int teamEnd = projectText.IndexOf(';', teamStart) + 1;
                projectText = projectText.Remove(teamStart, teamEnd - teamStart)
                    .Insert(teamStart, $"DevelopmentTeam = {PersonalTeamIdentifier};");
            }
            else if (targetStart >= 0)
            {
                int insertionPoint = targetStart + targetMarker.Length;
                projectText = projectText.Insert(
                    insertionPoint,
                    $"\n\t\t\t\t\t\tDevelopmentTeam = {PersonalTeamIdentifier};");
            }

            int provisioningStyle = targetStart < 0
                ? -1
                : projectText.IndexOf("ProvisioningStyle = Manual;", targetStart, StringComparison.Ordinal);
            if (provisioningStyle >= 0 && provisioningStyle - targetStart < 512)
            {
                projectText = projectText.Remove(provisioningStyle, "ProvisioningStyle = Manual;".Length)
                    .Insert(provisioningStyle, "ProvisioningStyle = Automatic;");
            }

            File.WriteAllText(projectPath, projectText);

            Debug.Log($"[Codex] Xcode automatic signing configured for Personal Team {PersonalTeamIdentifier}");
        }

        private static void ConfigureSwiftSupport(string outputPath)
        {
            string projectPath = PBXProject.GetPBXProjectPath(outputPath);
            PBXProject project = new PBXProject();
            project.ReadFromFile(projectPath);

            string mainTarget = project.GetUnityMainTargetGuid();
            string frameworkTarget = project.GetUnityFrameworkTargetGuid();
            project.SetBuildProperty(mainTarget, "SWIFT_VERSION", "5.0");
            project.SetBuildProperty(mainTarget, "ALWAYS_EMBED_SWIFT_STANDARD_LIBRARIES", "YES");

            if (!string.IsNullOrEmpty(frameworkTarget))
            {
                project.SetBuildProperty(frameworkTarget, "SWIFT_VERSION", "5.0");
                project.SetBuildProperty(frameworkTarget, "CLANG_ENABLE_MODULES", "YES");
                project.AddBuildProperty(
                    frameworkTarget,
                    "OTHER_SWIFT_FLAGS",
                    "-Xcc -Wno-incomplete-umbrella");
                project.AddBuildProperty(
                    frameworkTarget,
                    "OTHER_SWIFT_FLAGS",
                    "-Xfrontend -module-interface-preserve-types-as-written");
                project.AddFrameworkToProject(frameworkTarget, "SwiftUI.framework", false);
                project.AddFrameworkToProject(frameworkTarget, "CoreHaptics.framework", false);
            }

            project.WriteToFile(projectPath);
        }

        private static void ConfigureProductFont(string projectRoot, string outputPath)
        {
            string sourcePath = Path.Combine(projectRoot, OxaniumFontAssetPath);
            if (!File.Exists(sourcePath))
            {
                throw new FileNotFoundException(
                    "The canonical Oxanium product font is missing.",
                    sourcePath);
            }

            string destinationPath = Path.Combine(outputPath, OxaniumFontFileName);
            File.Copy(sourcePath, destinationPath, true);

            string projectPath = PBXProject.GetPBXProjectPath(outputPath);
            PBXProject project = new PBXProject();
            project.ReadFromFile(projectPath);
            string mainTarget = project.GetUnityMainTargetGuid();
            string fontGuid = project.FindFileGuidByProjectPath(OxaniumFontFileName);
            if (string.IsNullOrEmpty(fontGuid))
            {
                fontGuid = project.AddFile(
                    OxaniumFontFileName,
                    OxaniumFontFileName,
                    PBXSourceTree.Source);
            }
            project.AddFileToBuild(mainTarget, fontGuid);
            project.WriteToFile(projectPath);
        }

        private static void ConfigureProductThumbnails(string projectRoot, string outputPath)
        {
            var shippingModelThumbnailNames = new HashSet<string>(
                StringComparer.Ordinal);
            foreach (ProductCatalogEntry product in ProductCatalog.ShippingEntries)
            {
                shippingModelThumbnailNames.Add(
                    "product-thumbnail-" + product.ModelId + ".png");
            }

            string[] sourceRoots =
            {
                Path.Combine(projectRoot, ProductThumbnailAssetRootPath),
                Path.Combine(projectRoot, SceneWallpaperAssetRootPath),
                Path.Combine(projectRoot, ProductStickerArtworkAssetRootPath),
                Path.Combine(projectRoot, ProductBadgeArtworkAssetRootPath),
                Path.Combine(projectRoot, GachaPackArtworkAssetRootPath)
            };

            var allThumbnailPaths = new List<string>();
            foreach (string sourceRoot in sourceRoots)
            {
                if (!Directory.Exists(sourceRoot))
                {
                    throw new DirectoryNotFoundException(
                        "Canonical product artwork is missing: " + sourceRoot);
                }

                foreach (string candidate in Directory.GetFiles(
                             sourceRoot,
                             "*.png",
                             SearchOption.AllDirectories))
                {
                    bool isModelThumbnail = string.Equals(
                        new DirectoryInfo(Path.GetDirectoryName(candidate)).Name,
                        "Models",
                        StringComparison.Ordinal);
                    if (!isModelThumbnail
                        || shippingModelThumbnailNames.Contains(Path.GetFileName(candidate)))
                    {
                        allThumbnailPaths.Add(candidate);
                    }
                }
            }

            string[] thumbnailPaths = allThumbnailPaths.ToArray();
            Array.Sort(thumbnailPaths, StringComparer.Ordinal);
            if (thumbnailPaths.Length == 0)
            {
                throw new BuildFailedException(
                    "No square product thumbnails, sticker artwork, or Badge artwork were found.");
            }

            string projectPath = PBXProject.GetPBXProjectPath(outputPath);
            PBXProject project = new PBXProject();
            project.ReadFromFile(projectPath);
            string mainTarget = project.GetUnityMainTargetGuid();

            foreach (string thumbnailPath in thumbnailPaths)
            {
                string fileName = Path.GetFileName(thumbnailPath);
                string destinationPath = Path.Combine(outputPath, fileName);
                File.Copy(thumbnailPath, destinationPath, true);

                string fileGuid = project.FindFileGuidByProjectPath(fileName);
                if (string.IsNullOrEmpty(fileGuid))
                {
                    fileGuid = project.AddFile(fileName, fileName, PBXSourceTree.Source);
                }
                project.AddFileToBuild(mainTarget, fileGuid);
            }

            project.WriteToFile(projectPath);
        }

        private static void ConfigureGeneratedPlist(string outputPath)
        {
            string plistPath = Path.Combine(outputPath, "Info.plist");
            if (!File.Exists(plistPath))
            {
                throw new FileNotFoundException("Generated iOS Info.plist was not found.", plistPath);
            }

            PlistDocument plist = new PlistDocument();
            plist.ReadFromFile(plistPath);
            plist.root.SetString(
                "NSMotionUsageDescription",
                "Device motion adds a subtle perspective effect to the fidget spinner.");
            plist.root.SetString("UIUserInterfaceStyle", "Dark");
            PlistElementArray productFonts = plist.root.CreateArray("UIAppFonts");
            productFonts.AddString(OxaniumFontFileName);
            plist.WriteToFile(plistPath);
        }
    }
}
