using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Runtime.InteropServices;
using FidgetingApp.EDC;
using Unity.Profiling;
using UnityEngine;
using UnityEngine.Profiling;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.OptimizationValidation
{
    public sealed class EdcOptimizationBootstrap : MonoBehaviour
    {
        private void Start()
        {
            string tier = Environment.GetEnvironmentVariable("EDC_OPT_TIER");
            string scene;
            if (string.Equals(tier, "416273", StringComparison.Ordinal))
            {
                scene = "EDC_Optimization_416273";
            }
            else if (string.Equals(tier, "500000", StringComparison.Ordinal))
            {
                scene = "EDC_Optimization_500000";
            }
            else
            {
                scene = "EDC_Optimization_750000";
            }
            SceneManager.LoadScene(scene, LoadSceneMode.Single);
        }
    }

    public sealed class EdcOptimizationMotionDriver : MonoBehaviour
    {
        [SerializeField] private int triangleTier;
        private EdcSliderController controller;

        public void Configure(int triangles)
        {
            triangleTier = triangles;
        }

        private void Awake()
        {
            Application.targetFrameRate = 60;
            QualitySettings.vSyncCount = 0;
            controller = GetComponent<EdcSliderController>();
        }

        private void Update()
        {
            if (controller == null)
            {
                return;
            }
            float progress = 0.5f - 0.5f * Mathf.Cos(Time.unscaledTime * Mathf.PI);
            controller.SetSlideProgress(progress);
        }
    }

    public sealed class EdcOptimizationShortAudit : MonoBehaviour
    {
        private const string LaunchArgument = "--edc-opt-short-audit";
        private const float WarmupSeconds = 10f;
        private const float MeasureSeconds = 60f;
        private const float MissedVsyncMilliseconds = 25f;
        private const float LongFrameMilliseconds = 1000f / 30f;
        private const double Mebibyte = 1024d * 1024d;

        private readonly FrameTiming[] latestTiming = new FrameTiming[1];
        private readonly List<float> cpu = new List<float>(4000);
        private readonly List<float> gpu = new List<float>(4000);
        private readonly List<float> frame = new List<float>(4000);
        private double startedAt;
        private double nextSystemSample;
        private int observedFrames;
        private int missedFrames;
        private int consecutiveLongPairs;
        private bool previousLong;
        private long physPeak;
        private long availableMin = long.MaxValue;
        private long physicalMemory;
        private int thermalInitial = -1;
        private int thermalMax;
        private int seriousSamples;
        private int criticalSamples;
        private long drawCallMax;
        private long batchMax;
        private long triangleRecorderMax;
        private long vertexRecorderMax;
        private long gfxMemoryMax;
        private ProfilerRecorder drawCalls;
        private ProfilerRecorder batches;
        private ProfilerRecorder triangles;
        private ProfilerRecorder vertices;
        private ProfilerRecorder gfxMemory;
        private bool completed;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void CreateWhenRequested()
        {
            bool requested = Environment.GetEnvironmentVariable("EDC_OPT_SHORT_AUDIT") == "1"
                || Environment.GetCommandLineArgs().Contains(LaunchArgument);
            if (!requested)
            {
                return;
            }
            var audit = new GameObject("[EDC Optimization Short Audit]");
            DontDestroyOnLoad(audit);
            audit.AddComponent<EdcOptimizationShortAudit>();
        }

        private void Awake()
        {
            Application.targetFrameRate = 60;
            QualitySettings.vSyncCount = 0;
            Screen.sleepTimeout = SleepTimeout.NeverSleep;
            Native.Begin();
            drawCalls = StartRecorder(ProfilerCategory.Render, "Draw Calls Count");
            batches = StartRecorder(ProfilerCategory.Render, "Batches Count");
            triangles = StartRecorder(ProfilerCategory.Render, "Triangles Count");
            vertices = StartRecorder(ProfilerCategory.Render, "Vertices Count");
            gfxMemory = StartRecorder(ProfilerCategory.Memory, "Gfx Used Memory");
            startedAt = Time.realtimeSinceStartupAsDouble;
            nextSystemSample = WarmupSeconds;
            FrameTimingManager.CaptureFrameTimings();
            Debug.Log(string.Format(
                CultureInfo.InvariantCulture,
                "EDC_IPHONE_SHORT_START {{\"tier\":\"{0}\",\"warmupSec\":10,\"measureSec\":60}}",
                Environment.GetEnvironmentVariable("EDC_OPT_TIER") ?? "750000"));
        }

        private void Update()
        {
            double elapsed = Time.realtimeSinceStartupAsDouble - startedAt;
            FrameTimingManager.CaptureFrameTimings();
            if (elapsed < WarmupSeconds)
            {
                return;
            }

            double measured = elapsed - WarmupSeconds;
            observedFrames++;
            float interval = Time.unscaledDeltaTime * 1000f;
            bool isLong = interval > LongFrameMilliseconds;
            if (isLong && previousLong)
            {
                consecutiveLongPairs++;
            }
            previousLong = isLong;
            if (interval > MissedVsyncMilliseconds)
            {
                missedFrames++;
            }

            uint count = FrameTimingManager.GetLatestTimings(1, latestTiming);
            if (count > 0)
            {
                float cpuMs = (float)latestTiming[0].cpuMainThreadFrameTime;
                float gpuMs = (float)latestTiming[0].gpuFrameTime;
                if (FinitePositive(cpuMs) && FinitePositive(gpuMs))
                {
                    cpu.Add(cpuMs);
                    gpu.Add(gpuMs);
                    frame.Add(interval);
                }
            }

            drawCallMax = Math.Max(drawCallMax, RecorderValue(drawCalls));
            batchMax = Math.Max(batchMax, RecorderValue(batches));
            triangleRecorderMax = Math.Max(triangleRecorderMax, RecorderValue(triangles));
            vertexRecorderMax = Math.Max(vertexRecorderMax, RecorderValue(vertices));
            gfxMemoryMax = Math.Max(gfxMemoryMax, RecorderValue(gfxMemory));

            if (measured >= nextSystemSample - WarmupSeconds)
            {
                SampleSystem();
                nextSystemSample += 2d;
            }
            if (measured >= MeasureSeconds)
            {
                WriteSummary();
                enabled = false;
            }
        }

        private void SampleSystem()
        {
            long footprint = Native.PhysFootprint();
            long available = Native.AvailableMemory();
            physicalMemory = Math.Max(physicalMemory, Native.PhysicalMemory());
            int thermal = Native.ThermalState();
            physPeak = Math.Max(physPeak, footprint);
            if (available > 0)
            {
                availableMin = Math.Min(availableMin, available);
            }
            if (thermalInitial < 0)
            {
                thermalInitial = thermal;
            }
            thermalMax = Math.Max(thermalMax, thermal);
            if (thermal == 2) seriousSamples++;
            if (thermal >= 3) criticalSamples++;
        }

        private void WriteSummary()
        {
            if (completed) return;
            completed = true;
            Stats cpuStats = Stats.From(cpu);
            Stats gpuStats = Stats.From(gpu);
            Stats frameStats = Stats.From(frame);
            double missedPercent = observedFrames > 0
                ? missedFrames * 100d / observedFrames
                : 100d;
            double physMiB = physPeak / Mebibyte;
            double availableMiB = availableMin == long.MaxValue ? 0d : availableMin / Mebibyte;
            double headroom = availableMin == long.MaxValue || physPeak <= 0
                ? 0d
                : availableMin * 100d / (availableMin + physPeak);
            double gateMiB = Math.Min(350d, physicalMemory * 0.20d / Mebibyte);
            bool coverage = cpu.Count >= MeasureSeconds * 60d * 0.90d;
            bool framePassed = coverage && gpuStats.Average <= 8d && gpuStats.P95 <= 10.5d
                && gpuStats.P99 <= 13.5d && cpuStats.P95 <= 8d && cpuStats.P99 <= 10d
                && missedPercent < 0.1d && consecutiveLongPairs == 0;
            bool memoryPassed = physPeak > 0 && availableMin != long.MaxValue
                && physMiB <= gateMiB && headroom >= 30d;
            bool thermalPassed = thermalInitial == 0 && seriousSamples == 0 && criticalSamples == 0;
            string tier = Environment.GetEnvironmentVariable("EDC_OPT_TIER") ?? "750000";
            Debug.Log(string.Format(
                CultureInfo.InvariantCulture,
                "EDC_IPHONE_SHORT_SUMMARY {{\"tier\":\"{0}\",\"shortPassed\":{1}," +
                "\"framePassed\":{2},\"memoryPassed\":{3},\"thermalPassed\":{4}," +
                "\"timingCoveragePassed\":{5},\"frames\":{6},\"observedFrames\":{7}," +
                "\"cpuMainMedianMs\":{8:F3},\"cpuMainAvgMs\":{9:F3},\"cpuMainP95Ms\":{10:F3}," +
                "\"cpuMainP99Ms\":{11:F3},\"gpuMedianMs\":{12:F3},\"gpuAvgMs\":{13:F3}," +
                "\"gpuP95Ms\":{14:F3},\"gpuP99Ms\":{15:F3},\"frameMedianMs\":{16:F3}," +
                "\"frameP95Ms\":{17:F3},\"missedFramePercent\":{18:F4}," +
                "\"consecutiveLongFramePairs\":{19},\"physPeakMiB\":{20:F1}," +
                "\"physGateMiB\":{21:F1},\"availableMinMiB\":{22:F1}," +
                "\"availableHeadroomMinPercent\":{23:F1},\"unityAllocatedMiB\":{24:F1}," +
                "\"thermalInitial\":{25},\"thermalMax\":{26},\"seriousSamples\":{27}," +
                "\"criticalSamples\":{28},\"drawCallsMax\":{29},\"batchesMax\":{30}," +
                "\"renderTrianglesMax\":{31},\"renderVerticesMax\":{32}," +
                "\"gfxUsedMemoryMaxMiB\":{33:F1},\"drawRecorderValid\":{34}," +
                "\"triangleRecorderValid\":{35},\"completeAuditStillRequired\":true}}",
                tier, Bool(framePassed && memoryPassed && thermalPassed), Bool(framePassed),
                Bool(memoryPassed), Bool(thermalPassed), Bool(coverage), cpu.Count, observedFrames,
                cpuStats.Median, cpuStats.Average, cpuStats.P95, cpuStats.P99,
                gpuStats.Median, gpuStats.Average, gpuStats.P95, gpuStats.P99,
                frameStats.Median, frameStats.P95, missedPercent, consecutiveLongPairs,
                physMiB, gateMiB, availableMiB, headroom,
                Profiler.GetTotalAllocatedMemoryLong() / Mebibyte, thermalInitial, thermalMax,
                seriousSamples, criticalSamples, drawCallMax, batchMax, triangleRecorderMax,
                vertexRecorderMax, gfxMemoryMax / Mebibyte, Bool(drawCalls.Valid),
                Bool(triangles.Valid)));
        }

        private void OnDisable()
        {
            drawCalls.Dispose();
            batches.Dispose();
            triangles.Dispose();
            vertices.Dispose();
            gfxMemory.Dispose();
            Native.End();
        }

        private static ProfilerRecorder StartRecorder(ProfilerCategory category, string name)
        {
            try { return ProfilerRecorder.StartNew(category, name, 1); }
            catch { return default; }
        }

        private static long RecorderValue(ProfilerRecorder recorder)
        {
            return recorder.Valid ? Math.Max(0, recorder.LastValue) : 0;
        }

        private static bool FinitePositive(float value)
        {
            return value > 0f && !float.IsNaN(value) && !float.IsInfinity(value);
        }

        private static string Bool(bool value) => value ? "true" : "false";

        private readonly struct Stats
        {
            private Stats(int count, double median, double average, double p95, double p99)
            {
                Count = count; Median = median; Average = average; P95 = p95; P99 = p99;
            }
            public int Count { get; }
            public double Median { get; }
            public double Average { get; }
            public double P95 { get; }
            public double P99 { get; }

            public static Stats From(List<float> values)
            {
                if (values.Count == 0) return new Stats(0, 0, 0, 0, 0);
                float[] sorted = values.ToArray();
                Array.Sort(sorted);
                return new Stats(sorted.Length, Percentile(sorted, 0.5d), sorted.Average(),
                    Percentile(sorted, 0.95d), Percentile(sorted, 0.99d));
            }

            private static double Percentile(float[] sorted, double p)
            {
                double index = (sorted.Length - 1) * p;
                int lo = (int)Math.Floor(index); int hi = (int)Math.Ceiling(index);
                return lo == hi ? sorted[lo] : sorted[lo] + (sorted[hi] - sorted[lo]) * (index - lo);
            }
        }

        private static class Native
        {
            public static void Begin()
            {
#if UNITY_IOS && !UNITY_EDITOR
                CodexPerformanceBeginDeviceMetrics();
#endif
            }

            public static void End()
            {
#if UNITY_IOS && !UNITY_EDITOR
                CodexPerformanceEndDeviceMetrics();
#endif
            }

            public static long PhysFootprint()
            {
#if UNITY_IOS && !UNITY_EDITOR
                return CodexPerformancePhysFootprintBytes();
#else
                return 0;
#endif
            }

            public static long AvailableMemory()
            {
#if UNITY_IOS && !UNITY_EDITOR
                return CodexPerformanceAvailableMemoryBytes();
#else
                return 0;
#endif
            }

            public static long PhysicalMemory()
            {
#if UNITY_IOS && !UNITY_EDITOR
                return CodexPerformancePhysicalMemoryBytes();
#else
                return 0;
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

#if UNITY_IOS && !UNITY_EDITOR
            [DllImport("__Internal")] private static extern void CodexPerformanceBeginDeviceMetrics();
            [DllImport("__Internal")] private static extern void CodexPerformanceEndDeviceMetrics();
            [DllImport("__Internal")] private static extern long CodexPerformancePhysFootprintBytes();
            [DllImport("__Internal")] private static extern long CodexPerformanceAvailableMemoryBytes();
            [DllImport("__Internal")] private static extern long CodexPerformancePhysicalMemoryBytes();
            [DllImport("__Internal")] private static extern int CodexPerformanceThermalState();
#endif
        }
    }
}
