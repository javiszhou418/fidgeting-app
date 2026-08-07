#import <CoreHaptics/CoreHaptics.h>
#import <UIKit/UIKit.h>

namespace
{
    CHHapticEngine *gHapticEngine = nil;
    id<CHHapticAdvancedPatternPlayer> gContinuousPlayer = nil;
    bool gCheckedCapabilities = false;
    bool gSupportsCoreHaptics = false;
    bool gHapticEngineRunning = false;
    float gContinuousIntensity = 0.0f;
    float gContinuousSharpness = 0.0f;
    float gContinuousAttack = 0.025f;
    float gContinuousRelease = 0.040f;
    bool gContinuousRequested = false;
    uint64_t gContinuousGeneration = 0;

    void StartContinuousPattern(
        float intensity,
        float sharpness,
        float attack,
        float release);
    void RestartEngineAndRestorePlayers();
    void PlayFallbackImpact(float intensity);

    void PerformOnMainQueue(dispatch_block_t block)
    {
        if ([NSThread isMainThread])
        {
            block();
        }
        else
        {
            dispatch_async(dispatch_get_main_queue(), block);
        }
    }

    float ClampUnit(float value)
    {
        return MAX(0.0f, MIN(1.0f, value));
    }

    bool EnsureEngine()
    {
        if (@available(iOS 13.0, *))
        {
            if (!gCheckedCapabilities)
            {
                gSupportsCoreHaptics =
                    [CHHapticEngine capabilitiesForHardware].supportsHaptics;
                gCheckedCapabilities = true;
            }

            if (!gSupportsCoreHaptics)
            {
                return false;
            }

            if (gHapticEngine == nil)
            {
                NSError *creationError = nil;
                gHapticEngine = [[CHHapticEngine alloc] initAndReturnError:&creationError];
                if (gHapticEngine == nil || creationError != nil)
                {
                    gHapticEngine = nil;
                    return false;
                }

                // One scene-lifetime engine owns isolated transients, finite
                // magnetic cues and the rotary texture player. Only the rotary
                // texture is a requested loop that survives engine resets.
                gHapticEngine.autoShutdownEnabled = false;
                gHapticEngine.resetHandler = ^{
                    gContinuousPlayer = nil;
                    gHapticEngineRunning = false;
                    PerformOnMainQueue(^{
                        RestartEngineAndRestorePlayers();
                    });
                };
                gHapticEngine.stoppedHandler = ^(CHHapticEngineStoppedReason reason) {
                    (void)reason;
                    gHapticEngineRunning = false;
                    gContinuousPlayer = nil;
                    PerformOnMainQueue(^{
                        RestartEngineAndRestorePlayers();
                    });
                };
            }

            if (gHapticEngineRunning)
            {
                return true;
            }

            NSError *startError = nil;
            [gHapticEngine startAndReturnError:&startError];
            gHapticEngineRunning = startError == nil;
            return gHapticEngineRunning;
        }

        return false;
    }

    void RestartEngineAndRestorePlayers()
    {
        if (@available(iOS 13.0, *))
        {
            if (gHapticEngine == nil
                || !gSupportsCoreHaptics
                || UIApplication.sharedApplication.applicationState
                    != UIApplicationStateActive)
            {
                return;
            }

            NSError *startError = nil;
            [gHapticEngine startAndReturnError:&startError];
            gHapticEngineRunning = startError == nil;
            if (gHapticEngineRunning && gContinuousRequested)
            {
                StartContinuousPattern(
                    gContinuousIntensity,
                    gContinuousSharpness,
                    gContinuousAttack,
                    gContinuousRelease);
            }
        }
    }

    void PlayIsolatedTransient(
        float intensity,
        float sharpness)
    {
        if (@available(iOS 13.0, *))
        {
            if (!EnsureEngine())
            {
                PlayFallbackImpact(intensity);
                return;
            }

            NSArray<CHHapticEventParameter *> *hapticParameters = @[
                [[CHHapticEventParameter alloc]
                    initWithParameterID:CHHapticEventParameterIDHapticIntensity
                    value:ClampUnit(intensity)],
                [[CHHapticEventParameter alloc]
                    initWithParameterID:CHHapticEventParameterIDHapticSharpness
                    value:ClampUnit(sharpness)]
            ];
            NSArray<CHHapticEvent *> *events = @[
                [[CHHapticEvent alloc]
                    initWithEventType:CHHapticEventTypeHapticTransient
                    parameters:hapticParameters
                    relativeTime:0.0]
            ];

            NSError *patternError = nil;
            CHHapticPattern *pattern = [[CHHapticPattern alloc]
                initWithEvents:events
                parameters:@[]
                error:&patternError];
            if (pattern == nil || patternError != nil)
            {
                PlayFallbackImpact(intensity);
                return;
            }

            NSError *playerError = nil;
            id<CHHapticPatternPlayer> player =
                [gHapticEngine createPlayerWithPattern:pattern error:&playerError];
            if (player == nil || playerError != nil)
            {
                PlayFallbackImpact(intensity);
                return;
            }

            NSError *playError = nil;
            [player startAtTime:CHHapticTimeImmediate error:&playError];
            if (playError != nil)
            {
                PlayFallbackImpact(intensity);
            }
            return;
        }

        PlayFallbackImpact(intensity);
    }

    NSArray<CHHapticEventParameter *> *EventParameters(
        float attack,
        float decay,
        float release,
        bool sustained,
        float baseIntensity,
        float baseSharpness)
        API_AVAILABLE(ios(13.0))
    {
        return @[
            [[CHHapticEventParameter alloc]
                initWithParameterID:CHHapticEventParameterIDHapticIntensity
                value:ClampUnit(baseIntensity)],
            [[CHHapticEventParameter alloc]
                initWithParameterID:CHHapticEventParameterIDHapticSharpness
                value:ClampUnit(baseSharpness)],
            [[CHHapticEventParameter alloc]
                initWithParameterID:CHHapticEventParameterIDAttackTime
                value:ClampUnit(attack)],
            [[CHHapticEventParameter alloc]
                initWithParameterID:CHHapticEventParameterIDDecayTime
                value:ClampUnit(decay)],
            [[CHHapticEventParameter alloc]
                initWithParameterID:CHHapticEventParameterIDReleaseTime
                value:ClampUnit(release)],
            [[CHHapticEventParameter alloc]
                initWithParameterID:CHHapticEventParameterIDSustained
                value:sustained ? 1.0f : 0.0f]
        ];
    }

    void AddEvents(
        NSMutableArray<CHHapticEvent *> *events,
        int waveform,
        NSTimeInterval time,
        NSTimeInterval duration,
        NSArray<CHHapticEventParameter *> *parameters)
        API_AVAILABLE(ios(13.0))
    {
        if (waveform == 0 || waveform == 2)
        {
            [events addObject:[[CHHapticEvent alloc]
                initWithEventType:CHHapticEventTypeHapticTransient
                parameters:parameters
                relativeTime:time]];
        }

        if (waveform == 1 || waveform == 2)
        {
            [events addObject:[[CHHapticEvent alloc]
                initWithEventType:CHHapticEventTypeHapticContinuous
                parameters:parameters
                relativeTime:time
                duration:MAX(0.01, duration)]];
        }
    }

    void PlayFallbackImpact(float intensity)
    {
        UIImpactFeedbackStyle style = intensity >= 0.82f
            ? UIImpactFeedbackStyleHeavy
            : (intensity >= 0.52f ? UIImpactFeedbackStyleMedium : UIImpactFeedbackStyleLight);
        UIImpactFeedbackGenerator *generator =
            [[UIImpactFeedbackGenerator alloc] initWithStyle:style];
        [generator prepare];
        [generator impactOccurredWithIntensity:ClampUnit(intensity)];
    }

    void PlayCorePattern(
        int pattern,
        float intensity,
        float sharpness,
        int waveform,
        float duration,
        float attack,
        float decay,
        float release,
        bool sustained,
        float endIntensity,
        float endSharpness,
        int pulseCount,
        float pulseInterval,
        float impactBoost,
        float dynamicIntensity,
        float dynamicSharpness,
        float dynamicAttack,
        float dynamicDecay,
        float dynamicRelease)
    {
        (void)pattern;
        if (@available(iOS 13.0, *))
        {
            if (!EnsureEngine())
            {
                PlayFallbackImpact(intensity);
                return;
            }

            int resolvedPulseCount = MAX(1, MIN(12, pulseCount));
            NSTimeInterval resolvedInterval = MAX(0.01, MIN(0.5, pulseInterval));
            NSTimeInterval resolvedDuration = MAX(0.01, MIN(5.0, duration));
            float resolvedBoost = MAX(1.0f, MIN(4.0f, impactBoost));
            int resolvedLayerCount = (int)ceilf(resolvedBoost);
            const NSTimeInterval layerInterval = 0.006;
            NSMutableArray<CHHapticEvent *> *events = [NSMutableArray array];

            for (int index = 0; index < resolvedPulseCount; index++)
            {
                NSTimeInterval pulseTime = index * resolvedInterval;
                float progress = resolvedPulseCount <= 1
                    ? 0.0f
                    : (float)index / (float)(resolvedPulseCount - 1);
                float pulseIntensity = intensity + (endIntensity - intensity) * progress;
                float pulseSharpness = sharpness + (endSharpness - sharpness) * progress;
                for (int layer = 0; layer < resolvedLayerCount; layer++)
                {
                    float layerGain = ClampUnit(resolvedBoost - layer);
                    NSArray<CHHapticEventParameter *> *parameters = EventParameters(
                        attack,
                        decay,
                        release,
                        sustained,
                        pulseIntensity * layerGain,
                        pulseSharpness);
                    AddEvents(
                        events,
                        waveform,
                        pulseTime + layer * layerInterval,
                        resolvedDuration,
                        parameters);
                }
            }

            NSArray<CHHapticDynamicParameter *> *dynamicParameters = @[
                [[CHHapticDynamicParameter alloc]
                    initWithParameterID:CHHapticDynamicParameterIDHapticIntensityControl
                    value:ClampUnit(dynamicIntensity)
                    relativeTime:0.0],
                [[CHHapticDynamicParameter alloc]
                    initWithParameterID:CHHapticDynamicParameterIDHapticSharpnessControl
                    value:MAX(-1.0f, MIN(1.0f, dynamicSharpness))
                    relativeTime:0.0],
                [[CHHapticDynamicParameter alloc]
                    initWithParameterID:CHHapticDynamicParameterIDHapticAttackTimeControl
                    value:MAX(-1.0f, MIN(1.0f, dynamicAttack))
                    relativeTime:0.0],
                [[CHHapticDynamicParameter alloc]
                    initWithParameterID:CHHapticDynamicParameterIDHapticDecayTimeControl
                    value:MAX(-1.0f, MIN(1.0f, dynamicDecay))
                    relativeTime:0.0],
                [[CHHapticDynamicParameter alloc]
                    initWithParameterID:CHHapticDynamicParameterIDHapticReleaseTimeControl
                    value:MAX(-1.0f, MIN(1.0f, dynamicRelease))
                    relativeTime:0.0]
            ];
            NSError *patternError = nil;
            CHHapticPattern *hapticPattern = [[CHHapticPattern alloc]
                initWithEvents:events
                parameters:dynamicParameters
                error:&patternError];
            if (hapticPattern == nil || patternError != nil)
            {
                PlayFallbackImpact(intensity);
                return;
            }

            NSError *playerError = nil;
            id<CHHapticPatternPlayer> player =
                [gHapticEngine createPlayerWithPattern:hapticPattern error:&playerError];
            if (player == nil || playerError != nil)
            {
                PlayFallbackImpact(intensity);
                return;
            }

            NSError *playError = nil;
            [player startAtTime:CHHapticTimeImmediate error:&playError];
            if (playError != nil)
            {
                PlayFallbackImpact(intensity);
            }
            return;
        }

        PlayFallbackImpact(intensity);
    }

    void StartContinuousPattern(
        float intensity,
        float sharpness,
        float attack,
        float release)
    {
        gContinuousRequested = true;
        gContinuousIntensity = ClampUnit(intensity);
        gContinuousSharpness = ClampUnit(sharpness);
        gContinuousAttack = ClampUnit(attack);
        gContinuousRelease = ClampUnit(release);
        if (@available(iOS 13.0, *))
        {
            if (!EnsureEngine())
            {
                PlayFallbackImpact(intensity);
                return;
            }

            gContinuousGeneration++;
            if (gContinuousPlayer != nil)
            {
                NSError *stopError = nil;
                [gContinuousPlayer stopAtTime:CHHapticTimeImmediate error:&stopError];
                gContinuousPlayer = nil;
            }

            NSArray<CHHapticEventParameter *> *parameters = EventParameters(
                attack,
                0.0f,
                release,
                true,
                1.0f,
                0.0f);
            CHHapticEvent *event = [[CHHapticEvent alloc]
                initWithEventType:CHHapticEventTypeHapticContinuous
                parameters:parameters
                relativeTime:0.0
                duration:1.0];
            NSError *patternError = nil;
            CHHapticPattern *pattern = [[CHHapticPattern alloc]
                initWithEvents:@[event]
                parameters:@[]
                error:&patternError];
            if (pattern == nil || patternError != nil)
            {
                PlayFallbackImpact(intensity);
                return;
            }

            NSError *playerError = nil;
            gContinuousPlayer = [gHapticEngine
                createAdvancedPlayerWithPattern:pattern
                error:&playerError];
            if (gContinuousPlayer == nil || playerError != nil)
            {
                gContinuousPlayer = nil;
                PlayFallbackImpact(intensity);
                return;
            }

            gContinuousPlayer.loopEnabled = YES;
            gContinuousPlayer.loopEnd = 1.0;
            NSArray<CHHapticDynamicParameter *> *dynamicParameters = @[
                [[CHHapticDynamicParameter alloc]
                    initWithParameterID:CHHapticDynamicParameterIDHapticIntensityControl
                    value:gContinuousIntensity
                    relativeTime:0.0],
                [[CHHapticDynamicParameter alloc]
                    initWithParameterID:CHHapticDynamicParameterIDHapticSharpnessControl
                    value:gContinuousSharpness
                    relativeTime:0.0]
            ];
            NSError *playError = nil;
            [gContinuousPlayer startAtTime:CHHapticTimeImmediate error:&playError];
            NSError *parameterError = nil;
            if (playError == nil)
            {
                [gContinuousPlayer sendParameters:dynamicParameters
                    atTime:CHHapticTimeImmediate
                    error:&parameterError];
            }
            if (parameterError != nil || playError != nil)
            {
                NSError *stopError = nil;
                [gContinuousPlayer stopAtTime:CHHapticTimeImmediate error:&stopError];
                gContinuousPlayer = nil;
                PlayFallbackImpact(intensity);
            }
            return;
        }

        PlayFallbackImpact(intensity);
    }

    void UpdateContinuousPattern(float intensity, float sharpness)
    {
        if (@available(iOS 13.0, *))
        {
            if (gContinuousPlayer == nil)
            {
                StartContinuousPattern(intensity, sharpness, 0.025f, 0.060f);
                return;
            }

            float resolvedIntensity = ClampUnit(intensity);
            float resolvedSharpness = ClampUnit(sharpness);
            const float parameterDeadband = 0.003f;
            if (fabsf(resolvedIntensity - gContinuousIntensity) < parameterDeadband
                && fabsf(resolvedSharpness - gContinuousSharpness) < parameterDeadband)
            {
                return;
            }

            gContinuousIntensity = resolvedIntensity;
            gContinuousSharpness = resolvedSharpness;
            NSArray<CHHapticDynamicParameter *> *parameters = @[
                [[CHHapticDynamicParameter alloc]
                    initWithParameterID:CHHapticDynamicParameterIDHapticIntensityControl
                    value:gContinuousIntensity
                    relativeTime:0.0],
                [[CHHapticDynamicParameter alloc]
                    initWithParameterID:CHHapticDynamicParameterIDHapticSharpnessControl
                    value:gContinuousSharpness
                    relativeTime:0.0]
            ];
            NSError *error = nil;
            [gContinuousPlayer sendParameters:parameters
                atTime:CHHapticTimeImmediate
                error:&error];
        }
    }

    void StopContinuousPattern(float release)
    {
        gContinuousRequested = false;
        if (@available(iOS 13.0, *))
        {
            if (gContinuousPlayer == nil)
            {
                return;
            }

            gContinuousGeneration++;
            uint64_t generation = gContinuousGeneration;
            NSTimeInterval resolvedRelease = MAX(0.0, MIN(1.0, release));
            if (resolvedRelease <= 0.001)
            {
                NSError *error = nil;
                [gContinuousPlayer stopAtTime:CHHapticTimeImmediate error:&error];
                gContinuousPlayer = nil;
                gContinuousIntensity = 0.0f;
                gContinuousSharpness = 0.0f;
                return;
            }

            NSArray<CHHapticParameterCurveControlPoint *> *points = @[
                [[CHHapticParameterCurveControlPoint alloc]
                    initWithRelativeTime:0.0
                    value:gContinuousIntensity],
                [[CHHapticParameterCurveControlPoint alloc]
                    initWithRelativeTime:resolvedRelease
                    value:0.0f]
            ];
            CHHapticParameterCurve *curve = [[CHHapticParameterCurve alloc]
                initWithParameterID:CHHapticDynamicParameterIDHapticIntensityControl
                controlPoints:points
                relativeTime:0.0];
            NSError *curveError = nil;
            [gContinuousPlayer scheduleParameterCurve:curve
                atTime:CHHapticTimeImmediate
                error:&curveError];

            dispatch_after(
                dispatch_time(
                    DISPATCH_TIME_NOW,
                    (int64_t)(resolvedRelease * NSEC_PER_SEC)),
                dispatch_get_main_queue(),
                ^{
                    if (generation != gContinuousGeneration || gContinuousPlayer == nil)
                    {
                        return;
                    }
                    NSError *stopError = nil;
                    [gContinuousPlayer stopAtTime:CHHapticTimeImmediate error:&stopError];
                    gContinuousPlayer = nil;
                    gContinuousIntensity = 0.0f;
                    gContinuousSharpness = 0.0f;
                });
        }
    }

    void PlayMagneticEdgeProbePattern(
        float intensity,
        float sharpness,
        float duration)
    {
        float resolvedDuration = MAX(0.005f, MIN(0.080f, duration));
        PlayCorePattern(
            14,
            ClampUnit(intensity),
            ClampUnit(sharpness),
            1,
            resolvedDuration,
            0.002f,
            resolvedDuration * 0.50f,
            0.006f,
            false,
            ClampUnit(intensity),
            ClampUnit(sharpness),
            1,
            0.010f,
            1.0f,
            1.0f,
            0.0f,
            0.0f,
            0.0f,
            0.0f);
    }

    void PlayMagneticCrossingTremorPattern(
        float primaryIntensity,
        float primarySharpness,
        float secondaryIntensity,
        float secondarySharpness,
        float pulseInterval)
    {
        PlayCorePattern(
            1,
            ClampUnit(primaryIntensity),
            ClampUnit(primarySharpness),
            0,
            0.012f,
            0.0f,
            0.012f,
            0.010f,
            false,
            ClampUnit(secondaryIntensity),
            ClampUnit(secondarySharpness),
            2,
            MAX(0.010f, MIN(0.080f, pulseInterval)),
            1.0f,
            1.0f,
            0.0f,
            0.0f,
            0.0f,
            0.0f);
    }
    void PlaySystemPreset(int preset, float intensity)
    {
        if (preset == 0)
        {
            UISelectionFeedbackGenerator *generator =
                [[UISelectionFeedbackGenerator alloc] init];
            [generator prepare];
            [generator selectionChanged];
            return;
        }

        if (preset >= 6)
        {
            UINotificationFeedbackType type = UINotificationFeedbackTypeSuccess;
            if (preset == 7)
            {
                type = UINotificationFeedbackTypeWarning;
            }
            else if (preset == 8)
            {
                type = UINotificationFeedbackTypeError;
            }

            UINotificationFeedbackGenerator *generator =
                [[UINotificationFeedbackGenerator alloc] init];
            [generator prepare];
            [generator notificationOccurred:type];
            return;
        }

        UIImpactFeedbackStyle style = UIImpactFeedbackStyleLight;
        switch (preset)
        {
            case 2: style = UIImpactFeedbackStyleMedium; break;
            case 3: style = UIImpactFeedbackStyleHeavy; break;
            case 4: style = UIImpactFeedbackStyleSoft; break;
            case 5: style = UIImpactFeedbackStyleRigid; break;
            default: break;
        }

        UIImpactFeedbackGenerator *generator =
            [[UIImpactFeedbackGenerator alloc] initWithStyle:style];
        [generator prepare];
        [generator impactOccurredWithIntensity:ClampUnit(intensity)];
    }
}

extern "C" void CodexIosHapticsPrepare()
{
    PerformOnMainQueue(^{
        EnsureEngine();
    });
}

extern "C" int CodexIosHapticsGetStatus()
{
    if (@available(iOS 13.0, *))
    {
        __block int status = 0;
        dispatch_block_t readStatus = ^{
            if (!gCheckedCapabilities)
            {
                gSupportsCoreHaptics =
                    [CHHapticEngine capabilitiesForHardware].supportsHaptics;
                gCheckedCapabilities = true;
            }
            status |= 1;
            if (gSupportsCoreHaptics)
            {
                status |= 2;
            }
            if (gHapticEngineRunning)
            {
                status |= 4;
            }
            if (gContinuousPlayer != nil)
            {
                status |= 8;
            }
        };

        if ([NSThread isMainThread])
        {
            readStatus();
        }
        else
        {
            dispatch_sync(dispatch_get_main_queue(), readStatus);
        }
        return status;
    }

    return 0;
}

extern "C" void CodexIosHapticsPlayPattern(
    int pattern,
    float intensity,
    float sharpness,
    int waveform,
    float duration,
    float attack,
    float decay,
    float release,
    int sustained,
    float endIntensity,
    float endSharpness,
    int pulseCount,
    float pulseInterval,
    float impactBoost,
    float dynamicIntensity,
    float dynamicSharpness,
    float dynamicAttack,
    float dynamicDecay,
    float dynamicRelease)
{
    PerformOnMainQueue(^{
        PlayCorePattern(
            pattern,
            ClampUnit(intensity),
            ClampUnit(sharpness),
            MAX(0, MIN(2, waveform)),
            duration,
            ClampUnit(attack),
            ClampUnit(decay),
            ClampUnit(release),
            sustained != 0,
            ClampUnit(endIntensity),
            ClampUnit(endSharpness),
            pulseCount,
            pulseInterval,
            impactBoost,
            dynamicIntensity,
            dynamicSharpness,
            dynamicAttack,
            dynamicDecay,
            dynamicRelease);
    });
}

extern "C" void CodexIosHapticsPlayIsolatedTransient(
    float intensity,
    float sharpness)
{
    PerformOnMainQueue(^{
        PlayIsolatedTransient(
            ClampUnit(intensity),
            ClampUnit(sharpness));
    });
}

extern "C" void CodexIosHapticsPlaySystemPreset(int preset, float intensity)
{
    PerformOnMainQueue(^{
        PlaySystemPreset(MAX(0, MIN(8, preset)), ClampUnit(intensity));
    });
}

extern "C" void CodexIosHapticsStartContinuous(
    float intensity,
    float sharpness,
    float attack,
    float release)
{
    PerformOnMainQueue(^{
        StartContinuousPattern(
            ClampUnit(intensity),
            ClampUnit(sharpness),
            ClampUnit(attack),
            ClampUnit(release));
    });
}

extern "C" void CodexIosHapticsUpdateContinuous(float intensity, float sharpness)
{
    PerformOnMainQueue(^{
        UpdateContinuousPattern(ClampUnit(intensity), ClampUnit(sharpness));
    });
}

extern "C" void CodexIosHapticsStopContinuous(float release)
{
    PerformOnMainQueue(^{
        StopContinuousPattern(MAX(0.0f, MIN(1.0f, release)));
    });
}

extern "C" void CodexIosHapticsPlayMagneticEdgeProbe(
    float intensity,
    float sharpness,
    float duration)
{
    PerformOnMainQueue(^{
        PlayMagneticEdgeProbePattern(
            ClampUnit(intensity),
            ClampUnit(sharpness),
            MAX(0.005f, MIN(0.080f, duration)));
    });
}

extern "C" void CodexIosHapticsPlayMagneticCrossingTremor(
    float primaryIntensity,
    float primarySharpness,
    float secondaryIntensity,
    float secondarySharpness,
    float pulseInterval)
{
    PerformOnMainQueue(^{
        PlayMagneticCrossingTremorPattern(
            ClampUnit(primaryIntensity),
            ClampUnit(primarySharpness),
            ClampUnit(secondaryIntensity),
            ClampUnit(secondarySharpness),
            MAX(0.010f, MIN(0.080f, pulseInterval)));
    });
}
