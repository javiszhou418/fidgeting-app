#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>
#import <mach/mach.h>
#import <os/proc.h>

static BOOL CodexOwnsBatteryMonitoring = NO;
static BOOL CodexPreviousBatteryMonitoring = NO;

extern "C" void CodexPerformanceBeginDeviceMetrics(void)
{
    if (CodexOwnsBatteryMonitoring)
    {
        return;
    }
    UIDevice *device = UIDevice.currentDevice;
    CodexPreviousBatteryMonitoring = device.batteryMonitoringEnabled;
    device.batteryMonitoringEnabled = YES;
    CodexOwnsBatteryMonitoring = YES;
}

extern "C" void CodexPerformanceEndDeviceMetrics(void)
{
    if (!CodexOwnsBatteryMonitoring)
    {
        return;
    }
    UIDevice.currentDevice.batteryMonitoringEnabled = CodexPreviousBatteryMonitoring;
    CodexOwnsBatteryMonitoring = NO;
}

extern "C" long long CodexPerformancePhysFootprintBytes(void)
{
    task_vm_info_data_t info = {};
    mach_msg_type_number_t count = TASK_VM_INFO_COUNT;
    kern_return_t result = task_info(
        mach_task_self_,
        TASK_VM_INFO,
        reinterpret_cast<task_info_t>(&info),
        &count);
    return result == KERN_SUCCESS
        ? static_cast<long long>(info.phys_footprint)
        : 0LL;
}

extern "C" long long CodexPerformanceAvailableMemoryBytes(void)
{
    return static_cast<long long>(os_proc_available_memory());
}

extern "C" long long CodexPerformancePhysicalMemoryBytes(void)
{
    return static_cast<long long>(NSProcessInfo.processInfo.physicalMemory);
}

extern "C" int CodexPerformanceThermalState(void)
{
    if (@available(iOS 11.0, *))
    {
        return static_cast<int>(NSProcessInfo.processInfo.thermalState);
    }
    return 0;
}

extern "C" double CodexPerformanceBatteryLevelPercent(void)
{
    float level = UIDevice.currentDevice.batteryLevel;
    return level < 0.0f ? -1.0 : static_cast<double>(level * 100.0f);
}

extern "C" int CodexPerformanceBatteryState(void)
{
    switch (UIDevice.currentDevice.batteryState)
    {
        case UIDeviceBatteryStateUnplugged:
            return 1;
        case UIDeviceBatteryStateCharging:
            return 2;
        case UIDeviceBatteryStateFull:
            return 3;
        case UIDeviceBatteryStateUnknown:
        default:
            return 0;
    }
}

extern "C" double CodexPerformanceScreenBrightnessPercent(void)
{
    return static_cast<double>(UIScreen.mainScreen.brightness * 100.0f);
}
