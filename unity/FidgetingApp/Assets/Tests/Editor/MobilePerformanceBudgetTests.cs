using System.IO;
using NUnit.Framework;
using ThreeBladeEDC.Diagnostics;
using UnityEditor;
using UnityEngine.Rendering.Universal;

namespace FidgetingApp.Tests.Editor
{
    public sealed class MobilePerformanceBudgetTests
    {
        [Test]
        public void MobilePipeline_PreservesSixtyFpsHeadroomWithoutHdrBuffer()
        {
            UniversalRenderPipelineAsset pipeline =
                AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(
                    "Assets/Settings/Mobile_RPAsset.asset");

            Assert.That(pipeline, Is.Not.Null);
            Assert.That(pipeline.msaaSampleCount, Is.EqualTo(2));
            Assert.That(pipeline.renderScale, Is.EqualTo(0.9f).Within(0.001f));
            Assert.That(pipeline.supportsHDR, Is.False);
        }

        [Test]
        public void NativeMotion_UsesOneSensorBackendAndSuspendsWhenUnfocused()
        {
            string classic = File.ReadAllText(
                "Assets/Scripts/FidgetSpinner/DeviceMotionController.cs");
            string metal = File.ReadAllText(
                "Assets/Scripts/Product/MetalDeviceMotionController.cs");

            StringAssert.Contains("if (nativeMotionAvailable)", classic);
            StringAssert.Contains("DisableFallbackSensors();", classic);
            StringAssert.Contains("else\n            {\n                EnableFallbackSensors();", classic);
            StringAssert.Contains("private void SuspendMotion()", classic);
            StringAssert.Contains("private void OnApplicationFocus(bool focused)", metal);
            StringAssert.Contains("motionAvailable = false;", metal);
        }

        [Test]
        public void HapticEngine_PersistsAndCoalescesStableContinuousParameters()
        {
            string native = File.ReadAllText(
                "Assets/Plugins/iOS/CodexIosHaptics.mm");

            StringAssert.Contains("gHapticEngine.autoShutdownEnabled = false", native);
            StringAssert.Contains("const float parameterDeadband = 0.003f", native);
            StringAssert.Contains("gHapticEngineRunning = false", native);
        }

        [Test]
        public void IdlePresentation_DoesNotRewriteSettledTransforms()
        {
            string cage = File.ReadAllText(
                "Assets/_Fidgeting/Runtime/Interaction/BearingCageVisualSync.cs");
            string exploded = File.ReadAllText(
                "Assets/_Fidgeting/Runtime/Presentation/ExplodedViewController.cs");

            StringAssert.Contains("_hasAppliedPose", cage);
            StringAssert.Contains("return;", cage);
            StringAssert.Contains("Mathf.Abs(_progress - destination) < 0.0001f", exploded);
        }

        [Test]
        public void PerformanceAudit_IsExplicitOptInAndCalculatesInterpolatedPercentiles()
        {
            Assert.That(
                IPhonePerformanceAudit.LaunchArgumentsRequestAudit(null),
                Is.False);
            Assert.That(
                IPhonePerformanceAudit.LaunchArgumentsRequestAudit(
                    new[] { "--unrelated" }),
                Is.False);
            Assert.That(
                IPhonePerformanceAudit.LaunchArgumentsRequestAudit(
                    new[] { IPhonePerformanceAudit.LaunchArgument }),
                Is.True);
            Assert.That(IPhonePerformanceAudit.EnvironmentRequestsAudit(null), Is.False);
            Assert.That(IPhonePerformanceAudit.EnvironmentRequestsAudit("true"), Is.False);
            Assert.That(IPhonePerformanceAudit.EnvironmentRequestsAudit("1"), Is.True);
            Assert.That(
                IPhonePerformanceAudit.EnvironmentRequestsDevelopmentGcMode(null),
                Is.False);
            Assert.That(
                IPhonePerformanceAudit.EnvironmentRequestsDevelopmentGcMode("release"),
                Is.False);
            Assert.That(
                IPhonePerformanceAudit.EnvironmentRequestsDevelopmentGcMode(
                    IPhonePerformanceAudit.DevelopmentGcMode),
                Is.True);

            float[] values = { 1f, 2f, 3f, 4f, 5f };
            IPhonePerformanceAudit.FrameStatistics result =
                IPhonePerformanceAudit.FrameStatistics.Calculate(values, values.Length);
            Assert.That(result.Average, Is.EqualTo(3d).Within(0.0001d));
            Assert.That(result.P95, Is.EqualTo(4.8d).Within(0.0001d));
            Assert.That(result.P99, Is.EqualTo(4.96d).Within(0.0001d));
        }

        [Test]
        public void PerformanceAudit_IsReadOnlyAndUsesLiveIosResourceSignals()
        {
            string managed = File.ReadAllText(
                "Assets/_Fidgeting/Runtime/Diagnostics/IPhonePerformanceAudit.cs");
            string native = File.ReadAllText(
                "Assets/Plugins/iOS/CodexIosPerformanceAudit.mm");

            StringAssert.Contains("--fidgeting-performance-audit", managed);
            StringAssert.Contains("FIDGETING_PERFORMANCE_AUDIT", managed);
            StringAssert.Contains("Screen.sleepTimeout = SleepTimeout.NeverSleep", managed);
            StringAssert.Contains("FrameTimingManager.GetLatestTimings", managed);
            StringAssert.Contains("GC Allocated In Frame", managed);
            StringAssert.Contains("gcAllocationNonzeroFrames == 0", managed);
            StringAssert.Contains("externalGcCheckRequired", managed);
            StringAssert.Contains("gcAllocatedNonzeroPercent = gcAllocationSampleCount > 0", managed);
            StringAssert.Contains("developmentGcMode", managed);
            StringAssert.Contains("Debug.isDebugBuild && gcPassed", managed);
            StringAssert.Contains("NativeMetrics.BeginDeviceMetrics()", managed);
            StringAssert.Contains("NativeMetrics.EndDeviceMetrics()", managed);
            StringAssert.Contains("environmentPassed", managed);
            StringAssert.Contains("nonUnpluggedBatterySamples == 0", managed);
            StringAssert.Contains("minimumBrightnessPercent >= 45d", managed);
            StringAssert.Contains("public const float AuditSeconds = 1800f", managed);
            StringAssert.Contains("public const float DevelopmentGcAuditSeconds = 300f", managed);
            StringAssert.DoesNotContain("angularVelocity", managed);
            StringAssert.DoesNotContain("SetMotorActive", managed);
            StringAssert.DoesNotContain("DriveFromFinger", managed);
            StringAssert.DoesNotContain("IosHaptics", managed);

            StringAssert.Contains("TASK_VM_INFO", native);
            StringAssert.Contains("info.phys_footprint", native);
            StringAssert.Contains("os_proc_available_memory()", native);
            StringAssert.Contains("NSProcessInfo.processInfo.thermalState", native);
            StringAssert.Contains("batteryMonitoringEnabled = YES", native);
            StringAssert.Contains("CodexPreviousBatteryMonitoring", native);
            StringAssert.Contains("UIScreen.mainScreen.brightness", native);
        }

        [Test]
        public void PerformanceBuild_EnablesFrameTimingAndInstallerPerformsLiveDdiHandshake()
        {
            string pipeline = File.ReadAllText("Assets/Editor/IosBuildPipeline.cs");
            string projectSettings = File.ReadAllText(
                "ProjectSettings/ProjectSettings.asset");
            string installer = File.ReadAllText(
                Path.GetFullPath("../../scripts/ios_build_and_install.sh"));

            StringAssert.Contains("PlayerSettings.enableFrameTimingStats = true", pipeline);
            StringAssert.Contains("BuildOptions.Development | BuildOptions.ConnectWithProfiler", pipeline);
            StringAssert.Contains("Builds/iOS/FidgetingAppDevelopment", pipeline);
            StringAssert.Contains("enableFrameTimingStats: 1", projectSettings);
            StringAssert.Contains(
                "run_devicectl_json \"$DEVICE_DETAILS_JSON\" device info details",
                installer);
            StringAssert.Contains("result.connectionProperties.tunnelState", installer);
            StringAssert.Contains("result.deviceProperties.ddiServicesAvailable", installer);
            StringAssert.Contains(
                "run_devicectl_json \"$DEVICE_LOCK_JSON\" device info lockState",
                installer);
            StringAssert.Contains("result.passcodeRequired", installer);
            StringAssert.Contains("--development", installer);
            StringAssert.Contains("--no-launch", installer);
            StringAssert.Contains("BuildIosDevelopmentProject", installer);

            string soakRunner = File.ReadAllText(
                Path.GetFullPath("../../scripts/ios_performance_soak.sh"));
            StringAssert.Contains("\"reason\":\"completed\"", soakRunner);
            StringAssert.Contains("\"passed\":true", soakRunner);
            StringAssert.Contains("--development-gc", soakRunner);
            StringAssert.Contains("devicectl device info lockState", soakRunner);
            StringAssert.Contains("FIDGET_AUDIT_ENVIRONMENT_C", soakRunner);
            StringAssert.Contains("FIDGET_AUDIT_BRIGHTNESS_PERCENT", soakRunner);
            StringAssert.Contains("FIDGET_AUDIT_POWER_STATE=unplugged", soakRunner);
            StringAssert.Contains("summary.json", soakRunner);
            StringAssert.Contains("REPORT.md", soakRunner);
            StringAssert.Contains("\"gcCounterAvailable\":true", soakRunner);
            StringAssert.Contains("\"developmentBuild\":true", soakRunner);
            StringAssert.Contains("\"environmentPassed\":true", soakRunner);
        }
    }
}
