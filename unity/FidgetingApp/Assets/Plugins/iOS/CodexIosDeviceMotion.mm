#import <CoreMotion/CoreMotion.h>
#import <UIKit/UIKit.h>

namespace
{
    CMMotionManager *MotionManager()
    {
        static CMMotionManager *manager = nil;
        static dispatch_once_t onceToken;
        dispatch_once(&onceToken, ^{
            manager = [[CMMotionManager alloc] init];
        });
        return manager;
    }

    // Two clients share the single CMMotionManager: the Unity spinner
    // controllers and the native gacha Pack sheen. Updates stop only when
    // neither still needs them, so one side leaving never cuts the other.
    BOOL unityClientActive = NO;
    BOOL nativeUiClientActive = NO;

    int StartSharedUpdates()
    {
        CMMotionManager *manager = MotionManager();
        if (!manager.deviceMotionAvailable)
        {
            return 0;
        }

        manager.deviceMotionUpdateInterval = 1.0 / 60.0;
        if (!manager.deviceMotionActive)
        {
            [manager startDeviceMotionUpdatesUsingReferenceFrame:CMAttitudeReferenceFrameXArbitraryZVertical];
        }

        return 1;
    }

    void StopSharedUpdatesIfIdle()
    {
        if (unityClientActive || nativeUiClientActive)
        {
            return;
        }
        CMMotionManager *manager = MotionManager();
        if (manager.deviceMotionActive)
        {
            [manager stopDeviceMotionUpdates];
        }
    }
}

extern "C" int CodexIosDeviceMotionStart()
{
    int started = StartSharedUpdates();
    unityClientActive = started != 0;
    return started;
}

extern "C" void CodexIosDeviceMotionStop()
{
    unityClientActive = NO;
    StopSharedUpdatesIfIdle();
}

extern "C" int CodexIosDeviceMotionNativeUiStart()
{
    int started = StartSharedUpdates();
    nativeUiClientActive = started != 0;
    return started;
}

extern "C" void CodexIosDeviceMotionNativeUiStop()
{
    nativeUiClientActive = NO;
    StopSharedUpdatesIfIdle();
}

extern "C" int CodexIosReduceMotionEnabled()
{
    return UIAccessibilityIsReduceMotionEnabled() ? 1 : 0;
}

extern "C" int CodexIosDeviceMotionRead(
    double *roll,
    double *pitch,
    double *yaw,
    double *rotationRateX,
    double *rotationRateY,
    double *rotationRateZ,
    double *gravityX,
    double *gravityY,
    double *gravityZ,
    double *userAccelerationX,
    double *userAccelerationY,
    double *userAccelerationZ)
{
    CMDeviceMotion *motion = MotionManager().deviceMotion;
    if (motion == nil)
    {
        return 0;
    }

    *roll = motion.attitude.roll;
    *pitch = motion.attitude.pitch;
    *yaw = motion.attitude.yaw;
    *rotationRateX = motion.rotationRate.x;
    *rotationRateY = motion.rotationRate.y;
    *rotationRateZ = motion.rotationRate.z;
    *gravityX = motion.gravity.x;
    *gravityY = motion.gravity.y;
    *gravityZ = motion.gravity.z;
    *userAccelerationX = motion.userAcceleration.x;
    *userAccelerationY = motion.userAcceleration.y;
    *userAccelerationZ = motion.userAcceleration.z;
    return 1;
}
