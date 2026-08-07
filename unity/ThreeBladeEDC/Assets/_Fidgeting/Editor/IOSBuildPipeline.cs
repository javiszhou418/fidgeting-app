using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.Callbacks;
using UnityEditor.iOS.Xcode;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace ThreeBladeEDC.EditorTools
{
    public static class IOSBuildPipeline
    {
        public const string BundleIdentifier = "com.jiaweizhou.threebladeedc";
        public const string ProductName = "Three-Blade EDC";
        public const string RelativeOutputPath = "Builds/iOS/ThreeBladeEDC";
        private const string ExportLockPath = "/tmp/three-blade-edc-unity-export.lock";

        [Serializable]
        private sealed class BuildManifest
        {
            public string status;
            public string unityVersion;
            public string bundleIdentifier;
            public string version;
            public string buildNumber;
            public string developmentTeam;
            public string outputPath;
            public string completedUtc;
            public ulong totalBytes;
        }

        [MenuItem("Fidgeting/Three-Blade/Build iOS Device Project")]
        public static void BuildDevice()
        {
            using FileStream exportLock = AcquireExportLock();
            string teamId = DetectDevelopmentTeam();
            ConfigurePlayer(teamId);
            ThreeBladeSceneBuilder.BuildPresentation();

            string projectRoot = Directory.GetParent(Application.dataPath).FullName;
            string outputPath = Path.GetFullPath(
                Path.Combine(projectRoot, RelativeOutputPath));
            QuarantinePreviousOutput(outputPath);
            Directory.CreateDirectory(Path.GetDirectoryName(outputPath));

            string[] scenes = EditorBuildSettings.scenes
                .Where(scene => scene.enabled)
                .Select(scene => scene.path)
                .ToArray();
            if (scenes.Length == 0)
            {
                throw new BuildFailedException("No enabled scene is configured for iOS.");
            }

            var options = new BuildPlayerOptions
            {
                scenes = scenes,
                locationPathName = outputPath,
                target = BuildTarget.iOS,
                options = BuildOptions.Development | BuildOptions.AllowDebugging
            };

            BuildReport report = BuildPipeline.BuildPlayer(options);
            if (report.summary.result != BuildResult.Succeeded)
            {
                throw new BuildFailedException(
                    $"iOS export failed: {report.summary.result}; "
                    + $"errors={report.summary.totalErrors}.");
            }

            VerifyXcodeProject(outputPath);
            WriteManifest(outputPath, teamId, report.summary.totalSize);
            UnityEngine.Debug.Log(
                $"iOS Xcode export succeeded: {outputPath} ({report.summary.totalSize} bytes)");
        }

        [MenuItem("Fidgeting/Three-Blade/Configure iOS Device Settings")]
        public static void ConfigureDeviceProject()
        {
            using FileStream exportLock = AcquireExportLock();
            string teamId = DetectDevelopmentTeam();
            ConfigurePlayer(teamId);
            UnityEngine.Debug.Log(
                $"iOS device settings configured: {BundleIdentifier}; team={teamId}");
        }

        public static string DetectDevelopmentTeam()
        {
            string configured = Environment.GetEnvironmentVariable("IOS_DEVELOPMENT_TEAM");
            if (!string.IsNullOrWhiteSpace(configured))
            {
                configured = configured.Trim();
                if (!Regex.IsMatch(configured, "^[A-Z0-9]{10}$"))
                {
                    throw new BuildFailedException(
                        "IOS_DEVELOPMENT_TEAM must be a 10-character Apple Team ID.");
                }
                return configured;
            }

            string output = RunProcess(
                "/usr/bin/security",
                "find-identity -v -p codesigning");
            MatchCollection identityMatches = Regex.Matches(
                output,
                "\\\"(Apple Development:[^\\\"]+)\\\"");
            List<string> identities = identityMatches
                .Cast<Match>()
                .Select(match => match.Groups[1].Value)
                .Distinct(StringComparer.Ordinal)
                .ToList();
            if (identities.Count != 1)
            {
                throw new BuildFailedException(
                    $"Expected exactly one valid Apple Development identity, "
                    + $"found {identities.Count}. Set IOS_DEVELOPMENT_TEAM explicitly "
                    + "only after resolving the signing identities.");
            }

            string escapedIdentity = identities[0].Replace("\\", "\\\\").Replace("\"", "\\\"");
            string certificatePem = RunProcess(
                "/usr/bin/security",
                $"find-certificate -c \"{escapedIdentity}\" -p");
            string subject = RunProcess(
                "/usr/bin/openssl",
                "x509 -noout -subject",
                certificatePem);
            Match team = Regex.Match(subject, "OU\\s*=\\s*([A-Z0-9]{10})");
            if (!team.Success)
            {
                throw new BuildFailedException(
                    "The unique Apple Development certificate does not contain a "
                    + "10-character Team ID in its organization unit (OU).");
            }
            return team.Groups[1].Value;
        }

        private static void ConfigurePlayer(string teamId)
        {
            NamedBuildTarget ios = NamedBuildTarget.iOS;
            PlayerSettings.productName = ProductName;
            PlayerSettings.bundleVersion = "0.1.0";
            PlayerSettings.SetApplicationIdentifier(ios, BundleIdentifier);
            PlayerSettings.SetScriptingBackend(ios, ScriptingImplementation.IL2CPP);
            PlayerSettings.SetIl2CppCompilerConfiguration(
                ios,
                Il2CppCompilerConfiguration.Release);
            PlayerSettings.SetArchitecture(ios, 1);
            PlayerSettings.stripEngineCode = true;
            PlayerSettings.iOS.sdkVersion = iOSSdkVersion.DeviceSDK;
            PlayerSettings.iOS.targetDevice = iOSTargetDevice.iPhoneOnly;
            PlayerSettings.iOS.targetOSVersionString = "15.0";
            PlayerSettings.iOS.buildNumber = "1";
            PlayerSettings.iOS.hideHomeButton = true;
            PlayerSettings.iOS.appleDeveloperTeamID = teamId;
            PlayerSettings.iOS.appleEnableAutomaticSigning = true;
            PlayerSettings.defaultInterfaceOrientation = UIOrientation.AutoRotation;
            PlayerSettings.allowedAutorotateToPortrait = false;
            PlayerSettings.allowedAutorotateToPortraitUpsideDown = false;
            PlayerSettings.allowedAutorotateToLandscapeLeft = true;
            PlayerSettings.allowedAutorotateToLandscapeRight = true;
            PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.iOS, false);
            PlayerSettings.SetGraphicsAPIs(
                BuildTarget.iOS,
                new[] { GraphicsDeviceType.Metal });

            UniversalRenderPipelineAsset mobilePipeline =
                AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(
                    "Assets/Settings/Mobile_RPAsset.asset");
            if (mobilePipeline == null)
            {
                throw new BuildFailedException("Mobile URP asset is missing.");
            }
            mobilePipeline.msaaSampleCount = 4;
            mobilePipeline.renderScale = 1f;
            QualitySettings.renderPipeline = mobilePipeline;
            EditorUtility.SetDirty(mobilePipeline);
            AssetDatabase.SaveAssets();

            if (!EditorUserBuildSettings.SwitchActiveBuildTarget(
                    BuildTargetGroup.iOS,
                    BuildTarget.iOS))
            {
                throw new BuildFailedException("Unity could not switch to the iOS build target.");
            }
        }

        private static FileStream AcquireExportLock()
        {
            try
            {
                FileStream stream = new FileStream(
                    ExportLockPath,
                    FileMode.OpenOrCreate,
                    FileAccess.ReadWrite,
                    FileShare.None);
                stream.SetLength(0);
                using var writer = new StreamWriter(
                    stream,
                    System.Text.Encoding.UTF8,
                    1024,
                    true);
                writer.Write($"pid={Process.GetCurrentProcess().Id}; utc={DateTime.UtcNow:O}");
                writer.Flush();
                stream.Position = 0;
                return stream;
            }
            catch (IOException exception)
            {
                throw new BuildFailedException(
                    "Another Unity iOS export currently owns the project lock. "
                    + exception.Message);
            }
        }

        private static void QuarantinePreviousOutput(string outputPath)
        {
            if (!Directory.Exists(outputPath))
            {
                return;
            }

            string archiveRoot = Path.Combine(
                Path.GetDirectoryName(outputPath),
                "Archive");
            Directory.CreateDirectory(archiveRoot);
            string archivePath = Path.Combine(
                archiveRoot,
                $"ThreeBladeEDC-{DateTime.UtcNow:yyyyMMdd-HHmmss}");
            Directory.Move(outputPath, archivePath);
            UnityEngine.Debug.Log($"Previous iOS export quarantined: {archivePath}");
        }

        private static void VerifyXcodeProject(string outputPath)
        {
            string projectFile = Path.Combine(
                outputPath,
                "Unity-iPhone.xcodeproj/project.pbxproj");
            string infoPlist = Path.Combine(outputPath, "Info.plist");
            if (!File.Exists(projectFile) || !File.Exists(infoPlist))
            {
                throw new BuildFailedException(
                    "Unity reported success but the Xcode project or Info.plist is missing.");
            }
        }

        private static void WriteManifest(
            string outputPath,
            string teamId,
            ulong totalBytes)
        {
            var manifest = new BuildManifest
            {
                status = "exported",
                unityVersion = Application.unityVersion,
                bundleIdentifier = BundleIdentifier,
                version = PlayerSettings.bundleVersion,
                buildNumber = PlayerSettings.iOS.buildNumber,
                developmentTeam = teamId,
                outputPath = outputPath,
                completedUtc = DateTime.UtcNow.ToString("O"),
                totalBytes = totalBytes
            };
            File.WriteAllText(
                Path.Combine(outputPath, "three-blade-build-manifest.json"),
                JsonUtility.ToJson(manifest, true));
        }

        private static string RunProcess(
            string executable,
            string arguments,
            string standardInput = null)
        {
            var startInfo = new ProcessStartInfo(executable, arguments)
            {
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                RedirectStandardInput = standardInput != null,
                CreateNoWindow = true
            };
            using Process process = Process.Start(startInfo);
            if (standardInput != null)
            {
                process.StandardInput.Write(standardInput);
                process.StandardInput.Close();
            }
            string output = process.StandardOutput.ReadToEnd();
            string error = process.StandardError.ReadToEnd();
            process.WaitForExit();
            if (process.ExitCode != 0)
            {
                throw new BuildFailedException(
                    $"{Path.GetFileName(executable)} failed ({process.ExitCode}): {error}");
            }
            return output;
        }
    }

    public static class IOSXcodePostProcessor
    {
        [PostProcessBuild(100)]
        public static void ConfigureXcode(BuildTarget target, string path)
        {
            if (target != BuildTarget.iOS)
            {
                return;
            }

            string teamId = IOSBuildPipeline.DetectDevelopmentTeam();
            string projectPath = PBXProject.GetPBXProjectPath(path);
            var project = new PBXProject();
            project.ReadFromFile(projectPath);
            foreach (string targetGuid in new[]
                     {
                         project.GetUnityMainTargetGuid(),
                         project.GetUnityFrameworkTargetGuid()
                     })
            {
                project.SetBuildProperty(targetGuid, "DEVELOPMENT_TEAM", teamId);
                project.SetBuildProperty(targetGuid, "CODE_SIGN_STYLE", "Automatic");
                project.SetBuildProperty(targetGuid, "ENABLE_BITCODE", "NO");
            }
            project.SetBuildProperty(
                project.GetUnityMainTargetGuid(),
                "PRODUCT_BUNDLE_IDENTIFIER",
                IOSBuildPipeline.BundleIdentifier);
            project.WriteToFile(projectPath);

            string plistPath = Path.Combine(path, "Info.plist");
            var plist = new PlistDocument();
            plist.ReadFromFile(plistPath);
            plist.root.SetBoolean("UIRequiresFullScreen", true);
            PlistElementArray orientations =
                plist.root.CreateArray("UISupportedInterfaceOrientations");
            orientations.AddString("UIInterfaceOrientationLandscapeLeft");
            orientations.AddString("UIInterfaceOrientationLandscapeRight");
            plist.WriteToFile(plistPath);
        }
    }
}
