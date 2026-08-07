using System;
using System.Globalization;
using System.Runtime.InteropServices;
using UnityEngine;
using Unity.Profiling;
using UnityEngine.Profiling;

namespace ThreeBladeEDC.Diagnostics
{
    /// <summary>
    /// Opt-in, read-only telemetry for the 30-minute iPhone release audit.
    /// It never drives the rotor or synthesizes input. Enable it only by
    /// launching the player with --fidgeting-performance-audit.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class IPhonePerformanceAudit : MonoBehaviour
    {
        public const string LaunchArgument = "--fidgeting-performance-audit";
        public const string EnvironmentVariable = "FIDGETING_PERFORMANCE_AUDIT";
        public const string ModeEnvironmentVariable = "FIDGETING_PERFORMANCE_AUDIT_MODE";
        public const string DevelopmentGcMode = "development-gc";
        public const float WarmupSeconds = 10f;
        public const float AuditSeconds = 1800f;
        public const float DevelopmentGcAuditSeconds = 300f;
        public const float MemorySampleSeconds = 5f;

        private const int TargetFramesPerSecond = 60;
        private const int MaximumFramesPerSecond = 120;
        private const float TargetFrameMilliseconds = 1000f / TargetFramesPerSecond;
        private const float MissedVsyncMilliseconds = TargetFrameMilliseconds * 1.5f;
        private const float LongFrameMilliseconds = TargetFrameMilliseconds * 2f;
        private const int MaximumFrameSamples = (int)(AuditSeconds * MaximumFramesPerSecond);
        private const double Mebibyte = 1024d * 1024d;

        private readonly FrameTiming[] latestTiming = new FrameTiming[1];
        private readonly float[] cpuMainMilliseconds = new float[MaximumFrameSamples];
        private readonly float[] gpuMilliseconds = new float[MaximumFrameSamples];
        private readonly float[] frameMilliseconds = new float[MaximumFrameSamples];

        private double startedAt;
        private double nextMemorySampleAt;
        private double nextProgressLogAt;
        private int frameSampleCount;
        private int observedFrameCount;
        private int missedFrameCount;
        private int consecutiveLongFramePairs;
        private bool previousFrameWasLong;
        private long peakFootprintBytes;
        private long peakUnityAllocatedBytes;
        private long minimumAvailableBytes = long.MaxValue;
        private double minimumAvailableFraction = 1d;
        private int maximumThermalState;
        private int initialThermalState = -1;
        private double initialBatteryLevelPercent = -1d;
        private double lastBatteryLevelPercent = -1d;
        private int initialBatteryState = -1;
        private int nonUnpluggedBatterySamples;
        private double initialBrightnessPercent = -1d;
        private double minimumBrightnessPercent = double.MaxValue;
        private double maximumBrightnessPercent = -1d;
        private int memorySampleCount;
        private int seriousThermalSamples;
        private int criticalThermalSamples;
        private double currentFairSeconds;
        private double longestFairSeconds;
        private int initialGen0Collections;
        private int initialGen1Collections;
        private int initialGen2Collections;
        private ProfilerRecorder gcAllocatedInFrame;
        private long gcAllocatedTotalBytes;
        private long gcAllocatedPeakBytes;
        private int gcAllocationSampleCount;
        private int gcAllocationNonzeroFrames;
        private bool skipNextGcSample;
        private bool warmupFinished;
        private WindowAccumulator firstFiveMinutes;
        private WindowAccumulator lastFiveMinutes;
        private bool summaryWritten;
        private int previousSleepTimeout;
        private bool developmentGcMode;
        private double auditDurationSeconds;

        public static bool LaunchArgumentsRequestAudit(string[] arguments)
        {
            if (arguments == null)
            {
                return false;
            }

            foreach (string argument in arguments)
            {
                if (string.Equals(argument, LaunchArgument, StringComparison.Ordinal))
                {
                    return true;
                }
            }

            return false;
        }

        public static bool EnvironmentRequestsAudit(string value)
        {
            return string.Equals(value, "1", StringComparison.Ordinal);
        }

        public static bool EnvironmentRequestsDevelopmentGcMode(string value)
        {
            return string.Equals(value, DevelopmentGcMode, StringComparison.Ordinal);
        }

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void CreateWhenRequested()
        {
            bool requested = LaunchArgumentsRequestAudit(Environment.GetCommandLineArgs())
                || EnvironmentRequestsAudit(
                    Environment.GetEnvironmentVariable(EnvironmentVariable));
            if (!requested)
            {
                return;
            }

            var auditObject = new GameObject("[iPhone Performance Audit]");
            DontDestroyOnLoad(auditObject);
            auditObject.AddComponent<IPhonePerformanceAudit>();
        }

        private void Awake()
        {
            previousSleepTimeout = Screen.sleepTimeout;
            Screen.sleepTimeout = SleepTimeout.NeverSleep;
            NativeMetrics.BeginDeviceMetrics();
            developmentGcMode = EnvironmentRequestsDevelopmentGcMode(
                Environment.GetEnvironmentVariable(ModeEnvironmentVariable));
            auditDurationSeconds = developmentGcMode
                ? DevelopmentGcAuditSeconds
                : AuditSeconds;
            startedAt = Time.realtimeSinceStartupAsDouble;
            nextMemorySampleAt = WarmupSeconds;
            nextProgressLogAt = WarmupSeconds + 60d;
            initialGen0Collections = GC.CollectionCount(0);
            initialGen1Collections = GC.CollectionCount(1);
            initialGen2Collections = GC.CollectionCount(2);
            gcAllocatedInFrame = ProfilerRecorder.StartNew(
                ProfilerCategory.Memory,
                "GC Allocated In Frame",
                1);
            FrameTimingManager.CaptureFrameTimings();
            Debug.Log(string.Format(
                CultureInfo.InvariantCulture,
                "FIDGET_PERF_AUDIT_START {{\"mode\":\"{0}\",\"developmentBuild\":{1}," +
                "\"warmupSec\":10,\"auditSec\":{2:F0},\"targetFps\":60}}",
                developmentGcMode ? "developmentGc" : "release",
                JsonBoolean(Debug.isDebugBuild),
                auditDurationSeconds));
        }

        private void Update()
        {
            double elapsed = Time.realtimeSinceStartupAsDouble - startedAt;
            FrameTimingManager.CaptureFrameTimings();

            if (elapsed < WarmupSeconds)
            {
                return;
            }

            if (!warmupFinished)
            {
                // Exclude scene startup and asset unloading from steady-state
                // collection deltas. LastValue describes the previous frame, so
                // discard the first sample at the warmup boundary as well.
                initialGen0Collections = GC.CollectionCount(0);
                initialGen1Collections = GC.CollectionCount(1);
                initialGen2Collections = GC.CollectionCount(2);
                skipNextGcSample = true;
                warmupFinished = true;
            }

            double auditElapsed = elapsed - WarmupSeconds;
            CaptureGcAllocation();
            CaptureFrame(auditElapsed);

            if (auditElapsed >= nextMemorySampleAt - WarmupSeconds)
            {
                CaptureMemoryAndThermal();
                nextMemorySampleAt += MemorySampleSeconds;
            }

            if (auditElapsed >= nextProgressLogAt - WarmupSeconds)
            {
                WriteProgress(auditElapsed);
                skipNextGcSample = true;
                nextProgressLogAt += 60d;
            }

            if (auditElapsed >= auditDurationSeconds)
            {
                WriteSummary("completed");
                enabled = false;
            }
        }

        private void OnApplicationPause(bool paused)
        {
            if (paused)
            {
                WriteSummary("backgrounded");
                Screen.sleepTimeout = previousSleepTimeout;
                enabled = false;
            }
        }

        private void OnApplicationQuit()
        {
            WriteSummary("terminated");
            Screen.sleepTimeout = previousSleepTimeout;
        }

        private void OnDisable()
        {
            gcAllocatedInFrame.Dispose();
            NativeMetrics.EndDeviceMetrics();
            Screen.sleepTimeout = previousSleepTimeout;
        }

        private void CaptureGcAllocation()
        {
            if (skipNextGcSample)
            {
                skipNextGcSample = false;
                return;
            }
            if (!gcAllocatedInFrame.Valid)
            {
                return;
            }

            long bytes = Math.Max(0L, gcAllocatedInFrame.LastValue);
            gcAllocatedTotalBytes += bytes;
            gcAllocatedPeakBytes = Math.Max(gcAllocatedPeakBytes, bytes);
            gcAllocationSampleCount++;
            if (bytes > 0)
            {
                gcAllocationNonzeroFrames++;
            }
        }

        private void CaptureFrame(double auditElapsed)
        {
            float intervalMilliseconds = Time.unscaledDeltaTime * 1000f;
            observedFrameCount++;
            bool longFrame = intervalMilliseconds > LongFrameMilliseconds;
            if (longFrame && previousFrameWasLong)
            {
                consecutiveLongFramePairs++;
            }
            previousFrameWasLong = longFrame;

            if (intervalMilliseconds > MissedVsyncMilliseconds)
            {
                missedFrameCount++;
            }

            uint timingCount = FrameTimingManager.GetLatestTimings(1, latestTiming);
            if (timingCount == 0 || frameSampleCount >= MaximumFrameSamples)
            {
                return;
            }

            FrameTiming timing = latestTiming[0];
            float cpuMain = (float)timing.cpuMainThreadFrameTime;
            float gpu = (float)timing.gpuFrameTime;
            if (!IsFinitePositive(cpuMain) || !IsFinitePositive(gpu))
            {
                return;
            }

            cpuMainMilliseconds[frameSampleCount] = cpuMain;
            gpuMilliseconds[frameSampleCount] = gpu;
            frameMilliseconds[frameSampleCount] = intervalMilliseconds;
            frameSampleCount++;

            if (auditElapsed <= 300d)
            {
                firstFiveMinutes.Add(cpuMain, gpu, intervalMilliseconds);
            }
            if (auditElapsed >= auditDurationSeconds - 300d)
            {
                lastFiveMinutes.Add(cpuMain, gpu, intervalMilliseconds);
            }
        }

        private void CaptureMemoryAndThermal()
        {
            long footprint = NativeMetrics.PhysFootprintBytes();
            long available = NativeMetrics.AvailableMemoryBytes();
            long physicalMemory = NativeMetrics.PhysicalMemoryBytes();
            int thermal = NativeMetrics.ThermalState();
            double batteryLevel = NativeMetrics.BatteryLevelPercent();
            int batteryState = NativeMetrics.BatteryState();
            double brightness = NativeMetrics.ScreenBrightnessPercent();
            long unityAllocated = Profiler.GetTotalAllocatedMemoryLong();
            memorySampleCount++;
            if (initialThermalState < 0)
            {
                initialThermalState = thermal;
            }
            if (batteryLevel >= 0d)
            {
                if (initialBatteryLevelPercent < 0d)
                {
                    initialBatteryLevelPercent = batteryLevel;
                }
                lastBatteryLevelPercent = batteryLevel;
            }
            if (initialBatteryState < 0)
            {
                initialBatteryState = batteryState;
            }
            if (batteryState != 1)
            {
                nonUnpluggedBatterySamples++;
            }
            if (brightness >= 0d)
            {
                if (initialBrightnessPercent < 0d)
                {
                    initialBrightnessPercent = brightness;
                }
                minimumBrightnessPercent = Math.Min(minimumBrightnessPercent, brightness);
                maximumBrightnessPercent = Math.Max(maximumBrightnessPercent, brightness);
            }

            peakFootprintBytes = Math.Max(peakFootprintBytes, footprint);
            peakUnityAllocatedBytes = Math.Max(peakUnityAllocatedBytes, unityAllocated);
            if (available > 0)
            {
                minimumAvailableBytes = Math.Min(minimumAvailableBytes, available);
            }
            if (available > 0 && footprint > 0)
            {
                minimumAvailableFraction = Math.Min(
                    minimumAvailableFraction,
                    available / (double)(available + footprint));
            }

            maximumThermalState = Math.Max(maximumThermalState, thermal);
            if (thermal == 1)
            {
                currentFairSeconds += MemorySampleSeconds;
                longestFairSeconds = Math.Max(longestFairSeconds, currentFairSeconds);
            }
            else
            {
                currentFairSeconds = 0d;
            }
            if (thermal == 2)
            {
                seriousThermalSamples++;
            }
            else if (thermal >= 3)
            {
                criticalThermalSamples++;
            }

            // Keep the physical-memory call in the sampled path so the final
            // gate can use min(350 MiB, 20% RAM) without a hard-coded device SKU.
            NativeMetrics.LastPhysicalMemoryBytes = physicalMemory;
        }

        private void WriteProgress(double auditElapsed)
        {
            double footprintMiB = peakFootprintBytes / Mebibyte;
            double gcAverage = gcAllocationSampleCount > 0
                ? gcAllocatedTotalBytes / (double)gcAllocationSampleCount
                : 0d;
            double gcNonzeroPercent = gcAllocationSampleCount > 0
                ? gcAllocationNonzeroFrames * 100d / gcAllocationSampleCount
                : -1d;
            Debug.Log(string.Format(
                CultureInfo.InvariantCulture,
                "FIDGET_PERF_PROGRESS {{\"elapsedSec\":{0:F0},\"frames\":{1}," +
                "\"physPeakMiB\":{2:F1},\"thermalMax\":{3}," +
                "\"gcCounterAvailable\":{4},\"gcAllocatedAvgBytes\":{5:F3}," +
                "\"gcAllocatedPeakBytes\":{6},\"gcAllocatedNonzeroPercent\":{7:F4}}}",
                auditElapsed,
                frameSampleCount,
                footprintMiB,
                maximumThermalState,
                JsonBoolean(gcAllocationSampleCount > 0),
                gcAverage,
                gcAllocatedPeakBytes,
                gcNonzeroPercent));
        }

        private void WriteSummary(string completionReason)
        {
            if (summaryWritten)
            {
                return;
            }
            summaryWritten = true;

            FrameStatistics cpu = FrameStatistics.Calculate(cpuMainMilliseconds, frameSampleCount);
            FrameStatistics gpu = FrameStatistics.Calculate(gpuMilliseconds, frameSampleCount);
            FrameStatistics frame = FrameStatistics.Calculate(frameMilliseconds, frameSampleCount);
            double missedPercent = observedFrameCount > 0
                ? missedFrameCount * 100d / observedFrameCount
                : 100d;
            double footprintMiB = peakFootprintBytes / Mebibyte;
            double availableMiB = minimumAvailableBytes == long.MaxValue
                ? 0d
                : minimumAvailableBytes / Mebibyte;
            double physicalMemoryGate = NativeMetrics.LastPhysicalMemoryBytes > 0
                ? NativeMetrics.LastPhysicalMemoryBytes * 0.20d / Mebibyte
                : 350d;
            double footprintGateMiB = Math.Min(350d, physicalMemoryGate);
            double cpuDegradation = WindowAccumulator.PercentChange(
                firstFiveMinutes.CpuAverage,
                lastFiveMinutes.CpuAverage);
            double gpuDegradation = WindowAccumulator.PercentChange(
                firstFiveMinutes.GpuAverage,
                lastFiveMinutes.GpuAverage);
            double fpsDegradation = WindowAccumulator.PercentDecrease(
                firstFiveMinutes.FramesPerSecond,
                lastFiveMinutes.FramesPerSecond);
            int gen0Collections = GC.CollectionCount(0) - initialGen0Collections;
            int gen1Collections = GC.CollectionCount(1) - initialGen1Collections;
            int gen2Collections = GC.CollectionCount(2) - initialGen2Collections;
            double gcAllocatedAverage = gcAllocationSampleCount > 0
                ? gcAllocatedTotalBytes / (double)gcAllocationSampleCount
                : 0d;
            double gcAllocatedNonzeroPercent = gcAllocationSampleCount > 0
                ? gcAllocationNonzeroFrames * 100d / gcAllocationSampleCount
                : -1d;

            bool durationPassed = completionReason == "completed";
            bool timingCoveragePassed = frameSampleCount >= auditDurationSeconds
                * TargetFramesPerSecond * 0.90d;
            bool gcCounterAvailable = gcAllocationSampleCount >= observedFrameCount * 0.90d;
            bool gcPassed = gcCounterAvailable && gcAllocationNonzeroFrames == 0;
            bool externalGcCheckRequired = !gcCounterAvailable;
            bool framePassed = timingCoveragePassed
                && gpu.Average <= 8d && gpu.P95 <= 10.5d && gpu.P99 <= 13.5d
                && cpu.P95 <= 8d && cpu.P99 <= 10d
                && missedPercent < 0.1d && consecutiveLongFramePairs == 0;
            bool memoryPassed = memorySampleCount > 0
                && peakFootprintBytes > 0
                && minimumAvailableBytes != long.MaxValue
                && footprintMiB <= footprintGateMiB
                && minimumAvailableFraction >= 0.30d;
            bool thermalPassed = memorySampleCount > 0
                && initialThermalState == 0
                && seriousThermalSamples == 0
                && criticalThermalSamples == 0
                && longestFairSeconds <= 120d;
            bool environmentPassed = memorySampleCount > 0
                && initialBatteryState == 1
                && nonUnpluggedBatterySamples == 0
                && initialBrightnessPercent >= 45d
                && initialBrightnessPercent <= 55d
                && minimumBrightnessPercent >= 45d
                && maximumBrightnessPercent <= 55d;
            bool stabilityPassed = firstFiveMinutes.Count > 0
                && lastFiveMinutes.Count > 0
                && cpuDegradation <= 10d
                && gpuDegradation <= 10d
                && fpsDegradation <= 10d;
            // Unity documents that GC Allocated In Frame is unavailable in a
            // non-Development Player. Release telemetry evaluates the gates it
            // can measure and reports a separate external-GC obligation. When
            // the counter is available, managed allocations remain a hard gate.
            bool passed = developmentGcMode
                ? durationPassed && Debug.isDebugBuild && gcPassed
                : durationPassed && framePassed && memoryPassed
                    && thermalPassed && environmentPassed && stabilityPassed
                    && (externalGcCheckRequired || gcPassed);

            string summary = string.Format(
                CultureInfo.InvariantCulture,
                "FIDGET_PERF_SUMMARY {{\"reason\":\"{0}\",\"passed\":{1}," +
                "\"mode\":\"{41}\",\"developmentBuild\":{42}," +
                "\"environmentPassed\":{43},\"batteryInitialPercent\":{44:F1}," +
                "\"batteryFinalPercent\":{45:F1},\"batteryInitialState\":{46}," +
                "\"nonUnpluggedBatterySamples\":{47}," +
                "\"brightnessInitialPercent\":{48:F1},\"brightnessMinPercent\":{49:F1}," +
                "\"brightnessMaxPercent\":{50:F1}," +
                "\"durationPassed\":{2},\"timingCoveragePassed\":{3}," +
                "\"gcCounterAvailable\":{4},\"gcPassed\":{5}," +
                "\"externalGcCheckRequired\":{40}," +
                "\"framePassed\":{6},\"memoryPassed\":{7}," +
                "\"thermalPassed\":{8},\"stabilityPassed\":{9},\"frames\":{10}," +
                "\"cpuMainAvgMs\":{11:F3},\"cpuMainP95Ms\":{12:F3},\"cpuMainP99Ms\":{13:F3}," +
                "\"gpuAvgMs\":{14:F3},\"gpuP95Ms\":{15:F3},\"gpuP99Ms\":{16:F3}," +
                "\"frameP95Ms\":{17:F3},\"frameP99Ms\":{18:F3}," +
                "\"missedFramePercent\":{19:F4},\"consecutiveLongFramePairs\":{20}," +
                "\"gcAllocatedAvgBytes\":{21:F3},\"gcAllocatedPeakBytes\":{22}," +
                "\"gcAllocatedNonzeroPercent\":{23:F4}," +
                "\"physPeakMiB\":{24:F1},\"physGateMiB\":{25:F1}," +
                "\"availableMinMiB\":{26:F1},\"availableHeadroomMinPercent\":{27:F1}," +
                "\"unityAllocatedPeakMiB\":{28:F1},\"thermalInitial\":{29},\"thermalMax\":{30}," +
                "\"fairLongestSec\":{31:F0},\"seriousSamples\":{32},\"criticalSamples\":{33}," +
                "\"cpuLastVsFirstPercent\":{34:F2},\"gpuLastVsFirstPercent\":{35:F2}," +
                "\"fpsDegradationPercent\":{36:F2},\"gcCollections\":[{37},{38},{39}]}}",
                completionReason,
                JsonBoolean(passed),
                JsonBoolean(durationPassed),
                JsonBoolean(timingCoveragePassed),
                JsonBoolean(gcCounterAvailable),
                JsonBoolean(gcPassed),
                JsonBoolean(framePassed),
                JsonBoolean(memoryPassed),
                JsonBoolean(thermalPassed),
                JsonBoolean(stabilityPassed),
                frameSampleCount,
                cpu.Average,
                cpu.P95,
                cpu.P99,
                gpu.Average,
                gpu.P95,
                gpu.P99,
                frame.P95,
                frame.P99,
                missedPercent,
                consecutiveLongFramePairs,
                gcAllocatedAverage,
                gcAllocatedPeakBytes,
                gcAllocatedNonzeroPercent,
                footprintMiB,
                footprintGateMiB,
                availableMiB,
                minimumAvailableFraction * 100d,
                peakUnityAllocatedBytes / Mebibyte,
                initialThermalState,
                maximumThermalState,
                longestFairSeconds,
                seriousThermalSamples,
                criticalThermalSamples,
                cpuDegradation,
                gpuDegradation,
                fpsDegradation,
                gen0Collections,
                gen1Collections,
                gen2Collections,
                JsonBoolean(externalGcCheckRequired),
                developmentGcMode ? "developmentGc" : "release",
                JsonBoolean(Debug.isDebugBuild),
                JsonBoolean(environmentPassed),
                initialBatteryLevelPercent,
                lastBatteryLevelPercent,
                initialBatteryState,
                nonUnpluggedBatterySamples,
                initialBrightnessPercent,
                minimumBrightnessPercent == double.MaxValue ? -1d : minimumBrightnessPercent,
                maximumBrightnessPercent);
            Debug.Log(summary);
        }

        private static bool IsFinitePositive(float value)
        {
            return !float.IsNaN(value) && !float.IsInfinity(value) && value > 0f;
        }

        private static string JsonBoolean(bool value)
        {
            return value ? "true" : "false";
        }

        public readonly struct FrameStatistics
        {
            public FrameStatistics(double average, double p95, double p99)
            {
                Average = average;
                P95 = p95;
                P99 = p99;
            }

            public double Average { get; }
            public double P95 { get; }
            public double P99 { get; }

            public static FrameStatistics Calculate(float[] values, int count)
            {
                if (values == null || count <= 0 || count > values.Length)
                {
                    return new FrameStatistics(0d, 0d, 0d);
                }

                var sorted = new float[count];
                Array.Copy(values, sorted, count);
                Array.Sort(sorted);
                double sum = 0d;
                for (int i = 0; i < count; i++)
                {
                    sum += sorted[i];
                }

                return new FrameStatistics(
                    sum / count,
                    Percentile(sorted, count, 0.95d),
                    Percentile(sorted, count, 0.99d));
            }

            private static double Percentile(float[] sorted, int count, double percentile)
            {
                double index = (count - 1) * percentile;
                int lower = (int)Math.Floor(index);
                int upper = (int)Math.Ceiling(index);
                if (lower == upper)
                {
                    return sorted[lower];
                }

                double fraction = index - lower;
                return sorted[lower] + (sorted[upper] - sorted[lower]) * fraction;
            }
        }

        private struct WindowAccumulator
        {
            private double cpuTotal;
            private double gpuTotal;
            private double frameTotal;

            public int Count { get; private set; }
            public double CpuAverage => Count > 0 ? cpuTotal / Count : 0d;
            public double GpuAverage => Count > 0 ? gpuTotal / Count : 0d;
            public double FramesPerSecond => Count > 0 && frameTotal > 0d
                ? 1000d * Count / frameTotal
                : 0d;

            public void Add(float cpu, float gpu, float frame)
            {
                cpuTotal += cpu;
                gpuTotal += gpu;
                frameTotal += frame;
                Count++;
            }

            public static double PercentChange(double baseline, double current)
            {
                if (baseline <= 0d || current <= 0d)
                {
                    return 100d;
                }

                return (current - baseline) * 100d / baseline;
            }

            public static double PercentDecrease(double baseline, double current)
            {
                if (baseline <= 0d || current <= 0d)
                {
                    return 100d;
                }

                return (baseline - current) * 100d / baseline;
            }
        }

        private static class NativeMetrics
        {
            public static long LastPhysicalMemoryBytes { get; set; }

            public static void BeginDeviceMetrics()
            {
#if UNITY_IOS && !UNITY_EDITOR
                CodexPerformanceBeginDeviceMetrics();
#endif
            }

            public static void EndDeviceMetrics()
            {
#if UNITY_IOS && !UNITY_EDITOR
                CodexPerformanceEndDeviceMetrics();
#endif
            }

            public static long PhysFootprintBytes()
            {
#if UNITY_IOS && !UNITY_EDITOR
                return CodexPerformancePhysFootprintBytes();
#else
                return Profiler.GetTotalReservedMemoryLong();
#endif
            }

            public static long AvailableMemoryBytes()
            {
#if UNITY_IOS && !UNITY_EDITOR
                return CodexPerformanceAvailableMemoryBytes();
#else
                return 1024L * 1024L * 1024L;
#endif
            }

            public static long PhysicalMemoryBytes()
            {
#if UNITY_IOS && !UNITY_EDITOR
                return CodexPerformancePhysicalMemoryBytes();
#else
                return 8L * 1024L * 1024L * 1024L;
#endif
            }

            public static int ThermalState()
            {
#if UNITY_IOS && !UNITY_EDITOR
                return CodexPerformanceThermalState();
#else
                return 0;
#endif
            }

            public static double BatteryLevelPercent()
            {
#if UNITY_IOS && !UNITY_EDITOR
                return CodexPerformanceBatteryLevelPercent();
#else
                return 50d;
#endif
            }

            public static int BatteryState()
            {
#if UNITY_IOS && !UNITY_EDITOR
                return CodexPerformanceBatteryState();
#else
                return 1;
#endif
            }

            public static double ScreenBrightnessPercent()
            {
#if UNITY_IOS && !UNITY_EDITOR
                return CodexPerformanceScreenBrightnessPercent();
#else
                return 50d;
#endif
            }

#if UNITY_IOS && !UNITY_EDITOR
            [DllImport("__Internal")]
            private static extern void CodexPerformanceBeginDeviceMetrics();

            [DllImport("__Internal")]
            private static extern void CodexPerformanceEndDeviceMetrics();

            [DllImport("__Internal")]
            private static extern long CodexPerformancePhysFootprintBytes();

            [DllImport("__Internal")]
            private static extern long CodexPerformanceAvailableMemoryBytes();

            [DllImport("__Internal")]
            private static extern long CodexPerformancePhysicalMemoryBytes();

            [DllImport("__Internal")]
            private static extern int CodexPerformanceThermalState();

            [DllImport("__Internal")]
            private static extern double CodexPerformanceBatteryLevelPercent();

            [DllImport("__Internal")]
            private static extern int CodexPerformanceBatteryState();

            [DllImport("__Internal")]
            private static extern double CodexPerformanceScreenBrightnessPercent();
#endif
        }
    }
}
