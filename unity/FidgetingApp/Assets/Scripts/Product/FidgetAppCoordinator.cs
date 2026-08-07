using System.Collections;
using System.Globalization;
using CodexUnityLab;
using FidgetingApp.EDC;
using FidgetingApp.FanCard;
using ThreeBladeEDC;
using ThreeBladeEDC.Interaction;
using ThreeBladeEDC.Presentation;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Controls;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.Product
{
    public static class AssistantDriveSpeedRules
    {
        public const float DefaultMultiplier = 1f;
        public const float BaseAngularSpeedRadiansPerSecond = 2.2f;
        public const float BaseSliderSpeedMetersPerSecond = 0.030f;

        private static readonly float[] SupportedMultipliers =
        {
            1f,
            1.5f,
            2f,
            3f
        };

        public static bool TryResolveMultiplier(float requested, out float resolved)
        {
            for (int index = 0; index < SupportedMultipliers.Length; index++)
            {
                float candidate = SupportedMultipliers[index];
                if (Mathf.Abs(requested - candidate) <= 0.001f)
                {
                    resolved = candidate;
                    return true;
                }
            }

            resolved = DefaultMultiplier;
            return false;
        }

        public static float AngularSpeedFor(float multiplier)
        {
            return BaseAngularSpeedRadiansPerSecond * multiplier;
        }

        public static float SliderSpeedFor(float multiplier)
        {
            return BaseSliderSpeedMetersPerSecond * multiplier;
        }
    }

    public enum FidgetRatchetFeel
    {
        Freewheel = 0,
        Light = 1,
        Mechanical = 2,
        Heavy = 3
    }

    public enum FidgetInteractionMode
    {
        Smooth = 0,
        Ratchet = 1
    }

    public enum FidgetMotionSensitivityPreset
    {
        Low = 0,
        Medium = 1,
        High = 2
    }

    public readonly struct FidgetMotionSensitivityProfile
    {
        public FidgetMotionSensitivityProfile(
            float maximumInputAngle,
            float motionResponse,
            float gyroscopeLead,
            float maximumMotionOrbit)
        {
            MaximumInputAngle = maximumInputAngle;
            MotionResponse = motionResponse;
            GyroscopeLead = gyroscopeLead;
            MaximumMotionOrbit = maximumMotionOrbit;
        }

        public float MaximumInputAngle { get; }
        public float MotionResponse { get; }
        public float GyroscopeLead { get; }
        public float MaximumMotionOrbit { get; }
    }

    public static class FidgetMotionSensitivityPresetCatalog
    {
        public static FidgetMotionSensitivityProfile Default =>
            Resolve(FidgetMotionSensitivityPreset.Low);

        public static FidgetMotionSensitivityProfile Resolve(
            FidgetMotionSensitivityPreset preset)
        {
            switch (preset)
            {
                case FidgetMotionSensitivityPreset.High:
                    return new FidgetMotionSensitivityProfile(
                        7f,
                        22f,
                        0.10f,
                        16f);
                case FidgetMotionSensitivityPreset.Medium:
                    return new FidgetMotionSensitivityProfile(
                        10f,
                        15f,
                        0.06f,
                        11f);
                default:
                    return new FidgetMotionSensitivityProfile(
                        18f,
                        8f,
                        0.035f,
                        6.5f);
            }
        }

        public static bool TryResolve(
            string value,
            out FidgetMotionSensitivityPreset preset)
        {
            switch (value?.Trim().ToLowerInvariant())
            {
                case "high":
                    preset = FidgetMotionSensitivityPreset.High;
                    return true;
                case "medium":
                    preset = FidgetMotionSensitivityPreset.Medium;
                    return true;
                case "low":
                    preset = FidgetMotionSensitivityPreset.Low;
                    return true;
                default:
                    preset = FidgetMotionSensitivityPreset.Low;
                    return false;
            }
        }
    }

    public readonly struct FidgetInteractionPreset
    {
        public FidgetInteractionPreset(
            float hapticIntensity,
            float hapticFrequencyFeel,
            float hapticSpeedFollow,
            FidgetHapticRhythm hapticRhythm,
            float spinResponse,
            float spinResistance,
            FidgetRatchetFeel ratchetFeel,
            int detentsPerTurn,
            bool classicDetentHapticsEnabled)
        {
            HapticIntensity = hapticIntensity;
            HapticFrequencyFeel = hapticFrequencyFeel;
            HapticSpeedFollow = hapticSpeedFollow;
            HapticRhythm = hapticRhythm;
            SpinResponse = spinResponse;
            SpinResistance = spinResistance;
            RatchetFeel = ratchetFeel;
            DetentsPerTurn = detentsPerTurn;
            ClassicDetentHapticsEnabled = classicDetentHapticsEnabled;
        }

        public float HapticIntensity { get; }
        public float HapticFrequencyFeel { get; }
        public float HapticSpeedFollow { get; }
        public FidgetHapticRhythm HapticRhythm { get; }
        public float SpinResponse { get; }
        public float SpinResistance { get; }
        public FidgetRatchetFeel RatchetFeel { get; }
        public int DetentsPerTurn { get; }
        public bool ClassicDetentHapticsEnabled { get; }
    }

    /// <summary>
    /// Stable native bridge and model catalog for the single Fidget Spinner app.
    /// Model scenes can change without changing the iOS product identity or UI shell.
    /// </summary>
    [DefaultExecutionOrder(-1000)]
    public sealed class FidgetAppCoordinator : MonoBehaviour
    {
        public const string BridgeObjectName = "FidgetApp";

        private const string PointedModelId = ProductCatalog.PointedThreeBladeModelId;
        private const string MetalModelId = ProductCatalog.MetalThreeBladeModelId;
        private const string ImportedModelId = ProductCatalog.GoldFourWingModelId;
        private const string TwoLobeModelId = ProductCatalog.GraphiteTwoLobeModelId;
        private const string EdcModelId = ProductCatalog.MagneticSlideTileModelId;
        private const string FanCardModelId = "magnetic-fan-card";
        private static readonly string[] ProductModelIds =
            ProductCatalog.ShippingModelIds();
        private const string PointedScenePath = SpinnerEnvironmentCatalog.PointedScenePath;
        private const string MetalScenePath = SpinnerEnvironmentCatalog.MetalScenePath;
        private const string ImportedScenePath = SpinnerEnvironmentCatalog.ImportedScenePath;
        private const string TwoLobeScenePath = SpinnerEnvironmentCatalog.TwoLobeScenePath;
        private const string EdcScenePath = SpinnerEnvironmentCatalog.EdcScenePath;
        private const string FanCardScenePath =
            SpinnerEnvironmentCatalog.FanCardScenePath;
        private const int TargetFrameRate = 60;
        private const float FixedStepSeconds = 1f / TargetFrameRate;
        private const float MaximumCatchUpSeconds = 0.1f;
        private const float HapticTelemetryInterval = 0.1f;
        private const float ProgressionPublishInterval = 0.25f;
        private const float ProgressionPersistenceInterval = 5f;
        private const float ProgressionStoppedSpeed = 0.04f;
        private const float MaximumCreditableRotationPerFrame = 180f;
        private const string ThreeBladeMetalSkinSelectionKey =
            "fidgeting.progression.skin.v1.metal-three-blade";
        private const string ProductStickerSelectionKeyPrefix =
            "fidgeting.appearance.sticker.v1.";

        private static FidgetAppCoordinator instance;

        private FidgetSpinnerController blueSpinner;
        private DeviceMotionController blueMotion;
        private PortraitCameraFramer blueCamera;
        private RotorRigidbodyController metalSpinner;
        private MobileGestureController metalGestures;
        private OrbitPresentationCamera metalCamera;
        private MetalDeviceMotionController metalMotion;
        private ExplodedViewController explodedView;
        private EdcSliderController edcSlider;
        private EdcPortraitCameraFramer edcCamera;
        private EdcDeviceMotionController edcMotion;
        private SharedPresentationGestureController edcPresentationGestures;
        private FanCardController fanCard;
        private SpinnerEnvironmentPresenter environmentPresenter;

        private bool hapticsEnabled = true;
        private float hapticIntensity = 0.62f;
        private float hapticFrequencyFeel = 0.62f;
        private int detentsPerTurn =
            DetentFeelPresetCatalog.Default.Config.DetentsPerRevolution;
        private float hapticSpeedFollow = 0.20f;
        private FidgetHapticRhythm hapticRhythm = FidgetHapticRhythm.Single;
        private FidgetInteractionMode interactionMode = FidgetInteractionMode.Smooth;
        private float spinResponse = FidgetSpinnerMotion.DefaultTouchResponse;
        private float spinResistance = FidgetSpinnerMotion.DefaultSpinResistance;
        private float coastHalfLife = FidgetSpinnerMotion.DefaultCoastHalfLife;
        private SpinnerResistanceMode resistanceMode = SpinnerResistanceMode.Freewheel;
        private FidgetRatchetFeel ratchetFeel = FidgetRatchetFeel.Freewheel;
        private int magneticDetentsPerTurn =
            DetentFeelPresetCatalog.Default.Config.DetentsPerRevolution;
        private float magneticBreakawaySpeed = 2.2f;
        private float magneticCaptureSpeed = 1.2f;
        private float magneticSnapResponse = 16f;
        private FidgetMotionSensitivityPreset motionSensitivityPreset =
            FidgetMotionSensitivityPreset.Low;
        private float maximumInputAngle =
            FidgetMotionSensitivityPresetCatalog.Default.MaximumInputAngle;
        private float motionResponse =
            FidgetMotionSensitivityPresetCatalog.Default.MotionResponse;
        private float gyroscopeLead =
            FidgetMotionSensitivityPresetCatalog.Default.GyroscopeLead;
        private float maximumMotionOrbit =
            FidgetMotionSensitivityPresetCatalog.Default.MaximumMotionOrbit;
        private float reversalStopDuration = 0.3f;
        private float flipDuration = 0.4f;
        private float flipOvershoot = 0.1f;
        private bool flipOnRelease;
        private bool libraryPreviewActive;
        private Coroutine modelSceneLoad;
        private string queuedModelId = string.Empty;
        private bool speedTexturePreviewActive;
        private float nextHapticTelemetryTime;
        private float nextProgressionPublishTime;
        private float nextProgressionPersistenceTime;
        private float previousProgressionAngle;
        private bool hasProgressionAngle;
        private bool progressionUiDirty;
        private bool progressionSuspended;
        private bool assistantDriveRequestedThisSession;
        private float assistantDriveMultiplierThisSession =
            AssistantDriveSpeedRules.DefaultMultiplier;
        private SpinnerProgressionVisuals progressionVisuals;
        private ThreeBladeMetalSkinProgression threeBladeMetalSkins;
        private ProductStickerPresenter productStickerPresenter;
        private string selectedThreeBladeMetalSkinId =
            ThreeBladeMetalSkinCatalog.AutomaticSelectionId;
        private string selectedProductStickerId = ProductStickerCatalog.NoneId;
        private readonly ProductAppearanceLongPressGesture appearanceLongPress =
            new ProductAppearanceLongPressGesture();
        private readonly ProductAppearanceActivationSequence appearanceActivation =
            new ProductAppearanceActivationSequence();
        private bool appearanceEditorPresented;
        private SpinnerExperienceVisuals experienceVisuals;
        private SpinnerProgressionRuntime progression;
        private CollectorProgressionRuntime collectorProgression;
        private SpinnerComboRuntime combo;
        private float lastComboHudPublishTime = float.NegativeInfinity;
        private float lastMotionTelemetryPublishTime = float.NegativeInfinity;
        private float lastComboHaloProjectionPublishTime = float.NegativeInfinity;
        private SpinnerSpeedBand speedDashboardBand = SpinnerSpeedBand.Calm;
        private SpinnerSpinRewardRuntime spinReward;
        private SpinnerOfflineReward pendingOfflineReward;
        private int pendingLivePreviousLevel;
        private string pendingLiveRewardName = string.Empty;
        private HapticSpeedTextureProfile hapticSpeedTextureProfile =
            HapticSpeedTextureProfile.Recommended;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void Bootstrap()
        {
            if (instance != null)
            {
                return;
            }

            GameObject bridge = new GameObject(BridgeObjectName);
            instance = bridge.AddComponent<FidgetAppCoordinator>();
            DontDestroyOnLoad(bridge);
        }

        private void Awake()
        {
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }

            instance = this;
            gameObject.name = BridgeObjectName;
            DontDestroyOnLoad(gameObject);
            DetentFeelRuntime.ResetToDefault();
            detentsPerTurn = DetentFeelRuntime.ActiveConfig.DetentsPerRevolution;
            magneticDetentsPerTurn = detentsPerTurn;
            selectedThreeBladeMetalSkinId = PlayerPrefs.GetString(
                ThreeBladeMetalSkinSelectionKey,
                ThreeBladeMetalSkinCatalog.AutomaticSelectionId);
            SceneManager.sceneLoaded += HandleSceneLoaded;
            ProductCatalogMigration.Apply();
            progression = new SpinnerProgressionRuntime(PointedModelId);
            collectorProgression = new CollectorProgressionRuntime(PointedModelId);
            combo = new SpinnerComboRuntime();
            spinReward = new SpinnerSpinRewardRuntime();
            experienceVisuals = gameObject.AddComponent<SpinnerExperienceVisuals>();
            pendingOfflineReward = progression.Resume(System.DateTime.UtcNow);
            BackfillCollectorProgressionIfNeeded();
            ConfigureFramePacing();
            ApplyHapticSettings();
            FidgetHapticRouter.ConfigureSpeedTexture(hapticSpeedTextureProfile);
            IosHaptics.Prepare();
        }

        private void Update()
        {
            UpdateAppearanceLongPressInput();
            UpdateAppearanceActivation();
            UpdateProgression();

            if (!speedTexturePreviewActive)
            {
                if (metalSpinner != null)
                {
                    FidgetHapticRouter.UpdateSpeedTexture(
                        metalSpinner.AngularSpeedRadians,
                        detentsPerTurn,
                        !libraryPreviewActive);
                }
                else if (blueSpinner != null)
                {
                    FidgetHapticRouter.UpdateSpeedTexture(
                        blueSpinner.AngularSpeedRadians,
                        detentsPerTurn,
                        !libraryPreviewActive);
                }
                else
                {
                    FidgetHapticRouter.UpdateSpeedTexture(0f, detentsPerTurn, false);
                }
            }

            if (Time.unscaledTime >= nextHapticTelemetryTime)
            {
                nextHapticTelemetryTime = Time.unscaledTime + HapticTelemetryInterval;
                HapticLabTelemetryBridge.Publish(FidgetHapticRouter.GetTelemetry());
            }
        }

        private void OnApplicationFocus(bool hasFocus)
        {
            if (hasFocus)
            {
                ConfigureFramePacing();
                ResumeProgression();
                return;
            }

            StopAssistantDrive(true);
            CancelAppearanceActivation(true);
            SuspendProgression();
            StopHapticSpeedTexturePreview();
            FidgetHapticRouter.StopAllContinuous(true);
        }

        private void OnApplicationPause(bool paused)
        {
            if (paused)
            {
                StopAssistantDrive(true);
                CancelAppearanceActivation(true);
                SuspendProgression();
                StopHapticSpeedTexturePreview();
                FidgetHapticRouter.StopAllContinuous(true);
            }
            else
            {
                ResumeProgression();
            }
        }

        private void OnApplicationQuit()
        {
            StopAssistantDrive(true);
            CancelAppearanceActivation(false);
            SuspendProgression();
            FidgetHapticRouter.StopAllContinuous(true);
        }

        private void OnDestroy()
        {
            if (instance != this)
            {
                return;
            }

            SceneManager.sceneLoaded -= HandleSceneLoaded;
            if (blueSpinner != null)
            {
                blueSpinner.SpinGestureCompleted -= HandleSpinGestureCompleted;
            }
            if (metalSpinner != null)
            {
                metalSpinner.SemanticEventRaised -= HandleRotorSemanticEvent;
            }
            if (metalGestures != null)
            {
                metalGestures.SpinGestureCompleted -= HandleSpinGestureCompleted;
            }
            if (edcSlider != null)
            {
                edcSlider.InteractionGestureCompleted -= HandleSpinGestureCompleted;
                edcSlider.SemanticEventRaised -= HandleEdcSemanticEvent;
            }
            if (fanCard != null)
            {
                fanCard.InteractionGestureCompleted -= HandleSpinGestureCompleted;
                fanCard.SemanticEventRaised -= HandleFanCardSemanticEvent;
            }
            StopAssistantDrive(false);
            CancelAppearanceActivation(false);
            progression?.SaveIfDirty(true);
            collectorProgression?.SaveIfDirty(true);
            StopHapticSpeedTexturePreview();
            FidgetHapticRouter.StopAllContinuous(true);
            ProductMotionTelemetryNativeBridge.Clear();
            ComboHaloProjectionNativeBridge.Clear();
            instance = null;
        }

        private void HandleSceneLoaded(Scene scene, LoadSceneMode mode)
        {
            ConfigureProductScene(scene.path);
        }

        private void ConfigureProductScene(string scenePath)
        {
            appearanceLongPress.Cancel();
            appearanceActivation.Cancel();
            ApplyAppearanceActivationScale(1f);
            StopHapticSpeedTexturePreview();
            FidgetHapticRouter.StopAllContinuous(true);
            Screen.autorotateToPortrait = true;
            Screen.autorotateToPortraitUpsideDown = false;
            Screen.autorotateToLandscapeLeft = false;
            Screen.autorotateToLandscapeRight = false;
            Screen.orientation = ScreenOrientation.Portrait;
            ConfigureFramePacing();
            Screen.sleepTimeout = SleepTimeout.SystemSetting;

            foreach (Camera sceneCamera in FindObjectsByType<Camera>())
            {
                sceneCamera.clearFlags = CameraClearFlags.SolidColor;
                sceneCamera.backgroundColor = Color.black;
            }

            GameObject standaloneCanvas = GameObject.Find("MobileCanvas");
            if (standaloneCanvas != null)
            {
                standaloneCanvas.SetActive(false);
            }

            foreach (SpinnerVariantSwitcher switcher in FindObjectsByType<SpinnerVariantSwitcher>(
                         FindObjectsInactive.Include))
            {
                switcher.enabled = false;
            }

            if (blueSpinner != null)
            {
                blueSpinner.SpinGestureCompleted -= HandleSpinGestureCompleted;
            }
            if (metalGestures != null)
            {
                metalGestures.SpinGestureCompleted -= HandleSpinGestureCompleted;
            }
            if (edcSlider != null)
            {
                edcSlider.InteractionGestureCompleted -= HandleSpinGestureCompleted;
                edcSlider.SemanticEventRaised -= HandleEdcSemanticEvent;
            }
            if (fanCard != null)
            {
                fanCard.InteractionGestureCompleted -= HandleSpinGestureCompleted;
                fanCard.SemanticEventRaised -= HandleFanCardSemanticEvent;
            }
            StopAssistantDrive(true);

            blueSpinner = FindAnyObjectByType<FidgetSpinnerController>();
            if (blueSpinner != null)
            {
                blueSpinner.SpinGestureCompleted += HandleSpinGestureCompleted;
            }
            blueMotion = FindAnyObjectByType<DeviceMotionController>();
            blueCamera = FindAnyObjectByType<PortraitCameraFramer>();
            if (metalSpinner != null)
            {
                metalSpinner.SemanticEventRaised -= HandleRotorSemanticEvent;
            }
            metalSpinner = FindAnyObjectByType<RotorRigidbodyController>();
            if (metalSpinner != null)
            {
                metalSpinner.SemanticEventRaised += HandleRotorSemanticEvent;
            }
            metalGestures = FindAnyObjectByType<MobileGestureController>();
            if (metalGestures != null)
            {
                metalGestures.SpinGestureCompleted += HandleSpinGestureCompleted;
            }
            metalCamera = FindAnyObjectByType<OrbitPresentationCamera>();
            explodedView = FindAnyObjectByType<ExplodedViewController>();
            edcSlider = FindAnyObjectByType<EdcSliderController>();
            if (edcSlider != null)
            {
                edcSlider.InteractionGestureCompleted += HandleSpinGestureCompleted;
                edcSlider.SemanticEventRaised += HandleEdcSemanticEvent;
            }
            fanCard = FindAnyObjectByType<FanCardController>();
            if (fanCard != null)
            {
                fanCard.InteractionGestureCompleted += HandleSpinGestureCompleted;
                fanCard.SemanticEventRaised += HandleFanCardSemanticEvent;
            }
            edcCamera = FindAnyObjectByType<EdcPortraitCameraFramer>();
            ApplyAppearanceActivationScale(1f);
            ProductFramingProfile framingProfile =
                ProductFramingCatalog.Resolve(scenePath);
            blueCamera?.ConfigureFraming(framingProfile);
            metalCamera?.ConfigureFraming(framingProfile);
            edcCamera?.ConfigureFraming(framingProfile);
            edcMotion = null;
            if ((scenePath == EdcScenePath || scenePath == FanCardScenePath)
                && edcCamera != null)
            {
                edcMotion = edcCamera.GetComponent<EdcDeviceMotionController>();
                if (edcMotion == null)
                {
                    edcMotion = edcCamera.gameObject.AddComponent<
                        EdcDeviceMotionController>();
                }
                edcMotion.Configure(
                    maximumInputAngle,
                    motionResponse,
                    gyroscopeLead,
                    maximumMotionOrbit);
            }
            edcPresentationGestures = FindAnyObjectByType<
                SharedPresentationGestureController>();

            metalMotion = null;
            if ((scenePath == PointedScenePath
                    || scenePath == MetalScenePath
                    || scenePath == ImportedScenePath
                    || scenePath == TwoLobeScenePath)
                && metalCamera != null)
            {
                metalMotion = metalCamera.GetComponent<MetalDeviceMotionController>();
                if (metalMotion == null)
                {
                    metalMotion = metalCamera.gameObject.AddComponent<MetalDeviceMotionController>();
                }
            }

            ApplyAllSettings();
            ActivateProgressionModel(ModelIdForScene(scenePath));
            ConfigureProgressionVisuals();
            ConfigureProductSticker();
            ConfigureExperienceVisuals();
            environmentPresenter = SpinnerEnvironmentPresenter.Install(scenePath);
            ApplyLibraryPreviewPose();
            ResetProgressionRotationBaseline();
            ResetMotionTelemetry(!libraryPreviewActive && HasRotarySpeedTelemetry());
            ResetComboHaloProjection(!libraryPreviewActive);
            PublishProgressionState();
        }

        private static void HandleRotorSemanticEvent(
            FidgetSemanticEvent semanticEvent,
            float normalizedSignal)
        {
            FidgetHapticRouter.Emit(semanticEvent, normalizedSignal);
        }

        private void HandleEdcSemanticEvent(
            FidgetSemanticEvent semanticEvent,
            float normalizedSignal)
        {
            if (libraryPreviewActive || edcSlider == null || edcSlider.Profile == null)
            {
                return;
            }

            LinearMagneticDetentProfile profile = edcSlider.Profile;
            FidgetHapticRouter.EmitMagneticSlider(
                semanticEvent,
                normalizedSignal,
                new MagneticSliderHapticTuning(
                    profile.EdgeProbeMinimumIntensity,
                    profile.EdgeProbeMaximumIntensity,
                    profile.EdgeProbeMinimumSharpness,
                    profile.EdgeProbeMaximumSharpness,
                    profile.EdgeProbePulseDurationSeconds,
                    profile.DetentHapticIntensity,
                    profile.DetentHapticSharpness,
                    profile.DetentHapticSecondaryIntensity,
                    profile.DetentHapticSecondarySharpness,
                    profile.DetentHapticPulseIntervalSeconds));
        }

        private void HandleFanCardSemanticEvent(
            FidgetSemanticEvent semanticEvent,
            float normalizedSignal)
        {
            if (!libraryPreviewActive)
            {
                FidgetHapticRouter.Emit(semanticEvent, normalizedSignal);
            }
        }

        private void HandleSpinGestureCompleted(float normalizedForce)
        {
            if (libraryPreviewActive || progression == null)
            {
                return;
            }

            float angularSpeed = CurrentAngularSpeedRadians();
            combo.RecordGesture(
                Time.unscaledTime,
                angularSpeed,
                normalizedForce);
            SpinnerSpinRewardNativeBridge.Clear();
            SpinnerComboNativeBridge.Publish(combo.Snapshot, angularSpeed);
            lastComboHudPublishTime = Time.unscaledTime;
            spinReward.RecordGesture(
                normalizedForce,
                angularSpeed);

            int previousLevel = progression.Snapshot.Level;
            double collectorBonus = collectorProgression?.ActiveBonusForModel(
                progression.ActiveModelId) ?? 0d;
            progression.RecordGesture(
                normalizedForce,
                combo.Snapshot.ExperienceMultiplier,
                angularSpeed,
                true,
                null,
                collectorBonus);
            collectorProgression?.RecordGesture(progression.ActiveModelId);
            HandleProgressionChanged(previousLevel);
        }

        private void UpdateProgression()
        {
            if (progression == null)
            {
                return;
            }

            float angle;
            float angularSpeed;
            bool fingerInteracting;
            bool fingerActivelyTouching;
            if (metalSpinner != null)
            {
                angle = metalSpinner.AccumulatedRotationDegrees;
                angularSpeed = metalSpinner.AngularSpeedRadians;
                fingerInteracting = metalSpinner.IsFingerControlling;
                fingerActivelyTouching = fingerInteracting;
            }
            else if (blueSpinner != null)
            {
                angle = blueSpinner.AccumulatedRotationDegrees;
                angularSpeed = blueSpinner.AngularSpeedRadians;
                fingerInteracting = blueSpinner.IsFingerControlling;
                fingerActivelyTouching = fingerInteracting;
            }
            else if (edcSlider != null)
            {
                angle = edcSlider.AccumulatedActivityDegrees;
                angularSpeed = edcSlider.ActivitySpeedRadians;
                fingerInteracting = edcSlider.IsDragging || edcSlider.IsSettling;
                fingerActivelyTouching = edcSlider.IsDragging;
            }
            else if (fanCard != null)
            {
                angle = fanCard.AccumulatedActivityDegrees;
                angularSpeed = fanCard.ActivitySpeedRadians;
                fingerInteracting = fanCard.IsDragging || fanCard.IsSettling;
                fingerActivelyTouching = fanCard.IsDragging;
            }
            else
            {
                hasProgressionAngle = false;
                return;
            }

            if (!libraryPreviewActive
                && progression.RecordActivity(
                    angularSpeed,
                    fingerActivelyTouching ? Time.unscaledDeltaTime : 0f,
                    fingerActivelyTouching || progression.HasSpinCredit))
            {
                progressionUiDirty = true;
            }
            if (!libraryPreviewActive
                && fingerActivelyTouching
                && collectorProgression != null
                && collectorProgression.RecordActivity(Time.unscaledDeltaTime))
            {
                progressionUiDirty = true;
            }

            if (combo.Tick(Time.unscaledTime))
            {
                SpinnerComboNativeBridge.Publish(combo.Snapshot, 0f);
                lastComboHudPublishTime = float.NegativeInfinity;
            }
            else if (combo.Snapshot.IsActive
                && Time.unscaledTime - lastComboHudPublishTime
                    >= SpinnerComboRules.HudUpdateIntervalSeconds)
            {
                SpinnerComboNativeBridge.Publish(combo.Snapshot, angularSpeed);
                lastComboHudPublishTime = Time.unscaledTime;
            }

            PublishMotionTelemetryIfDue(angularSpeed);
            PublishComboHaloProjectionIfDue();

            if (!hasProgressionAngle)
            {
                previousProgressionAngle = angle;
                hasProgressionAngle = true;
            }
            else
            {
                float deltaDegrees = angle - previousProgressionAngle;
                previousProgressionAngle = angle;
                float absoluteDelta = Mathf.Abs(deltaDegrees);
                if (!libraryPreviewActive
                    && absoluteDelta > Mathf.Epsilon
                    && absoluteDelta <= MaximumCreditableRotationPerFrame)
                {
                    if (!IsAssistantDriveActive()
                        && combo.RecordMechanicalActivity(
                            Time.unscaledTime,
                            absoluteDelta,
                            angularSpeed))
                    {
                        SpinnerComboNativeBridge.Publish(
                            combo.Snapshot,
                            angularSpeed);
                        lastComboHudPublishTime = Time.unscaledTime;
                    }

                    int previousLevel = progression.Snapshot.Level;
                    double gained = progression.RecordRotationDegrees(
                        absoluteDelta,
                        combo.Snapshot.ExperienceMultiplier,
                        collectorProgression?.ActiveBonusForModel(
                            progression.ActiveModelId) ?? 0d);
                    if (gained > 0d)
                    {
                        HandleProgressionChanged(previousLevel);
                        spinReward.RecordRotation(absoluteDelta, angularSpeed);
                    }
                }
            }

            if (!fingerInteracting
                && Mathf.Abs(angularSpeed) <= ProgressionStoppedSpeed
                && !IsAssistantDriveActive()
                && progression.HasSpinCredit)
            {
                progression.EndSpinCredit();
                spinReward.EndSpin(Time.unscaledTime);
            }

            if (spinReward.TryReveal(
                    Time.unscaledTime,
                    out SpinnerSpinRewardSnapshot reward))
            {
                ResetComboForReward();
                SpinnerSpinRewardNativeBridge.Publish(reward);
                experienceVisuals?.ShowReward(reward, Time.unscaledTime);
            }

            experienceVisuals?.UpdateFrame(
                combo.Snapshot,
                angularSpeed,
                CurrentSpinAxisWorld(),
                Time.unscaledTime,
                libraryPreviewActive);

            if (progressionUiDirty && Time.unscaledTime >= nextProgressionPublishTime)
            {
                PublishProgressionState();
            }

            if (Time.unscaledTime >= nextProgressionPersistenceTime)
            {
                nextProgressionPersistenceTime =
                    Time.unscaledTime + ProgressionPersistenceInterval;
                progression.SaveIfDirty(false);
                collectorProgression?.SaveIfDirty(false);
            }
        }

        private void HandleProgressionChanged(int previousLevel)
        {
            int newLevel = progression.Snapshot.Level;
            progressionUiDirty = true;
            collectorProgression?.RecordToyLevel(progression.ActiveModelId, newLevel);
            RecordCollectorCosmetics(progression.Snapshot);
            if (newLevel > previousLevel)
            {
                ApplyProgressionVisualStage();
                pendingLivePreviousLevel = previousLevel;
                SpinnerProgressionMilestone? milestone =
                    SpinnerProgressionRules.MilestoneCrossed(previousLevel, newLevel);
                pendingLiveRewardName = milestone?.RewardName ?? "成长罐容量提升";
                FidgetHapticRouter.Emit(FidgetSemanticEvent.Pop, 1f);
                PublishProgressionState();
            }
        }

        private void ActivateProgressionModel(string modelId)
        {
            if (progression == null || string.IsNullOrEmpty(modelId))
            {
                return;
            }

            progression.SetActiveModel(modelId);
            selectedProductStickerId = PlayerPrefs.GetString(
                ProductStickerSelectionKeyPrefix + modelId,
                ProductStickerCatalog.NoneId);
            selectedProductStickerId = ProductStickerCatalog.Resolve(
                selectedProductStickerId).Id;
            ResetCombo();
            ResetProgressionRotationBaseline();
            progressionUiDirty = true;
        }

        private void ResetProgressionRotationBaseline()
        {
            hasProgressionAngle = false;
            previousProgressionAngle = 0f;
        }

        private void SuspendProgression()
        {
            if (progression == null || progressionSuspended)
            {
                return;
            }

            progression.EndSpinCredit();
            ResetCombo();
            progression.Suspend(System.DateTime.UtcNow);
            collectorProgression?.SaveIfDirty(true);
            progressionSuspended = true;
            ResetProgressionRotationBaseline();
        }

        private void ResumeProgression()
        {
            if (progression == null || !progressionSuspended)
            {
                return;
            }

            SpinnerOfflineReward reward = progression.Resume(System.DateTime.UtcNow);
            progressionSuspended = false;
            if (reward.HasReward)
            {
                pendingOfflineReward = reward;
            }
            ApplyProgressionVisualStage();
            collectorProgression?.RecordToyLevel(reward.ModelId, reward.NewLevel);
            RecordCollectorCosmetics(progression.SnapshotFor(reward.ModelId));
            progressionUiDirty = true;
            ResetProgressionRotationBaseline();
            PublishProgressionState();
        }

        private void PublishProgressionState()
        {
            if (progression == null)
            {
                return;
            }

            SpinnerProgressionSnapshot snapshot = progression.Snapshot;
            SpinnerOfflineReward reward = pendingOfflineReward.HasReward
                ? pendingOfflineReward
                : SpinnerOfflineReward.None(snapshot.ModelId);
            SpinnerProgressionNativeBridge.Publish(
                snapshot,
                reward,
                pendingLivePreviousLevel,
                pendingLiveRewardName,
                assistantDriveRequestedThisSession
                    ? assistantDriveMultiplierThisSession
                    : AssistantDriveSpeedRules.DefaultMultiplier,
                AppliedThreeBladeMetalSkinId(snapshot),
                AppliedProductStickerId(snapshot));
            if (collectorProgression != null)
            {
                CollectorProgressionNativeBridge.Publish(
                    collectorProgression.Snapshot,
                    collectorProgression.ConsumePendingPreviousRank());
            }
            pendingOfflineReward = SpinnerOfflineReward.None(snapshot.ModelId);
            pendingLivePreviousLevel = 0;
            pendingLiveRewardName = string.Empty;
            progressionUiDirty = false;
            nextProgressionPublishTime = Time.unscaledTime + ProgressionPublishInterval;
        }

        private void BackfillCollectorProgressionIfNeeded()
        {
            if (collectorProgression == null
                || collectorProgression.HasInitializedProfile
                || progression == null)
            {
                return;
            }

            foreach (string modelId in ProductModelIds)
            {
                SpinnerProgressionSnapshot snapshot = progression.SnapshotFor(modelId);
                bool meaningfullyUsed = snapshot.TotalExperience > 0d
                    || snapshot.LifetimeGestureCount > 0L
                    || snapshot.ActiveInteractionSeconds > 0d;
                collectorProgression.BackfillModel(
                    modelId,
                    snapshot.Level,
                    meaningfullyUsed);
                if (meaningfullyUsed)
                {
                    RecordCollectorCosmetics(snapshot);
                }
            }

            collectorProgression.CompleteBackfill();
        }

        private void RecordCollectorCosmetics(SpinnerProgressionSnapshot snapshot)
        {
            if (collectorProgression == null
                || snapshot.ModelId != ThreeBladeMetalSkinCatalog.ModelId)
            {
                return;
            }

            foreach (ThreeBladeMetalSkinDefinition skin in ThreeBladeMetalSkinCatalog.Skins)
            {
                if (skin.Level > snapshot.Level)
                {
                    break;
                }
                collectorProgression.RecordCosmeticUnlock(
                    snapshot.ModelId + ":" + skin.Id);
            }
        }

        private string AppliedThreeBladeMetalSkinId(SpinnerProgressionSnapshot snapshot)
        {
            if (snapshot.ModelId != ThreeBladeMetalSkinCatalog.ModelId)
            {
                return string.Empty;
            }

            if (threeBladeMetalSkins != null && threeBladeMetalSkins.HasAppliedSkin)
            {
                return threeBladeMetalSkins.ActiveSkinId;
            }

            return string.Empty;
        }

        private string AppliedProductStickerId(SpinnerProgressionSnapshot snapshot)
        {
            string sceneModelId = ModelIdForScene(SceneManager.GetActiveScene().path);
            if (snapshot.ModelId != sceneModelId
                || productStickerPresenter == null
                || !productStickerPresenter.HasAppliedSticker)
            {
                return string.Empty;
            }

            return productStickerPresenter.AppliedStickerId;
        }

        private static string ModelIdForScene(string scenePath)
        {
            if (ProductCatalog.TryGetModelId(scenePath, out string modelId))
            {
                return modelId;
            }

            if (scenePath == FanCardScenePath)
            {
                return FanCardModelId;
            }

            return PointedModelId;
        }

        private void ConfigureProgressionVisuals()
        {
            progressionVisuals = null;
            threeBladeMetalSkins = null;
            Transform rotor = metalSpinner != null
                ? metalSpinner.transform
                : blueSpinner != null
                    ? blueSpinner.transform
                    : edcSlider != null
                        ? edcSlider.transform
                        : fanCard != null
                            ? fanCard.transform
                        : null;
            if (rotor == null || progression == null)
            {
                return;
            }

            bool usesIntegratedThreeBladeSkins = metalSpinner != null
                && progression.ActiveModelId == ThreeBladeMetalSkinCatalog.ModelId;
            if (!usesIntegratedThreeBladeSkins)
            {
                progressionVisuals = rotor.GetComponent<SpinnerProgressionVisuals>();
                if (progressionVisuals == null)
                {
                    progressionVisuals =
                        rotor.gameObject.AddComponent<SpinnerProgressionVisuals>();
                }
            }

            if (usesIntegratedThreeBladeSkins)
            {
                threeBladeMetalSkins =
                    rotor.GetComponent<ThreeBladeMetalSkinProgression>();
                if (threeBladeMetalSkins == null)
                {
                    threeBladeMetalSkins =
                        rotor.gameObject.AddComponent<ThreeBladeMetalSkinProgression>();
                }
            }

            ApplyProgressionVisualStage();
        }

        private void ConfigureExperienceVisuals()
        {
            Transform rotor = ActiveProductTransform();
            experienceVisuals?.Configure(
                FindObjectsByType<Camera>(),
                rotor);
        }

        private Transform ActiveProductTransform()
        {
            return metalSpinner != null
                ? metalSpinner.transform
                : blueSpinner != null
                    ? blueSpinner.transform
                    : edcSlider != null
                        ? edcSlider.transform
                        : fanCard != null
                            ? fanCard.transform
                        : null;
        }

        private void ConfigureProductSticker()
        {
            productStickerPresenter = null;
            Transform product = ProductStickerReceiverRoot();
            if (product == null)
            {
                return;
            }

            productStickerPresenter = product.GetComponent<ProductStickerPresenter>();
            if (productStickerPresenter == null)
            {
                productStickerPresenter =
                    product.gameObject.AddComponent<ProductStickerPresenter>();
            }
            ApplyProductSticker();
        }

        private Transform ProductStickerReceiverRoot()
        {
            Transform product = ActiveProductTransform();
            if (metalSpinner == null || product == null || product.parent == null)
            {
                return product;
            }

            Transform productRoot = product.parent;
            Transform hub = productRoot.Find("HubStatic");
            return hub != null && hub.Find("TopCap") != null
                ? productRoot
                : product;
        }

        private void ApplyProductSticker()
        {
            productStickerPresenter?.Apply(selectedProductStickerId, Camera.main);
        }

        private void ApplyProgressionVisualStage()
        {
            if (progression == null)
            {
                return;
            }

            string sceneModelId = ModelIdForScene(SceneManager.GetActiveScene().path);
            if (sceneModelId != progression.ActiveModelId)
            {
                return;
            }

            SpinnerProgressionSnapshot snapshot = progression.Snapshot;
            progressionVisuals?.Apply(snapshot.ModelId, snapshot.Level);
            threeBladeMetalSkins?.Apply(
                snapshot.Level,
                selectedThreeBladeMetalSkinId);
        }

        private static void ConfigureFramePacing()
        {
            QualitySettings.vSyncCount = 0;
            OnDemandRendering.renderFrameInterval = 1;
            Application.targetFrameRate = TargetFrameRate;
            Time.fixedDeltaTime = FixedStepSeconds;
            Time.maximumDeltaTime = MaximumCatchUpSeconds;
        }

        public void SelectModelFromNativeUi(string modelId)
        {
            if (!ProductCatalog.TryGetScenePath(modelId, out string scenePath))
            {
                Debug.LogWarning($"[FidgetingApp] Unknown or non-shipping model id: {modelId}");
                return;
            }

            // A paged TabView can publish another selection while the previous
            // Unity scene is still loading. Unity scene loads cannot be cancelled,
            // so keep only the latest requested page and resolve it after the
            // in-flight load completes.
            if (modelSceneLoad != null)
            {
                queuedModelId = modelId;
                return;
            }

            Scene activeScene = SceneManager.GetActiveScene();
            if (activeScene.path == scenePath)
            {
                StopAssistantDrive(true);
                ActivateProgressionModel(modelId);
                PublishProgressionState();
                ApplyLibraryPreviewPose();
                return;
            }

            int buildIndex = SceneUtility.GetBuildIndexByScenePath(scenePath);
            if (buildIndex < 0)
            {
                Debug.LogError($"[FidgetingApp] Model scene is missing from build settings: {scenePath}");
                return;
            }

            LoadResolvedModelScene(modelId, buildIndex);
        }

        private void LoadResolvedModelScene(string modelId, int buildIndex)
        {
            if (modelSceneLoad != null)
            {
                queuedModelId = modelId;
                return;
            }

            modelSceneLoad = StartCoroutine(
                LoadResolvedModelSceneAsync(modelId, buildIndex));
        }

        private IEnumerator LoadResolvedModelSceneAsync(string modelId, int buildIndex)
        {
            StopAssistantDrive(true);
            ActivateProgressionModel(modelId);
            PublishProgressionState();
            AsyncOperation load = SceneManager.LoadSceneAsync(
                buildIndex,
                LoadSceneMode.Single);
            if (load == null)
            {
                Debug.LogError(
                    $"[FidgetingApp] Failed to start async model scene load: {modelId}");
                modelSceneLoad = null;
                yield break;
            }

            while (!load.isDone)
            {
                yield return null;
            }

            modelSceneLoad = null;
            if (!string.IsNullOrEmpty(queuedModelId))
            {
                string latestModelId = queuedModelId;
                queuedModelId = string.Empty;
                SelectModelFromNativeUi(latestModelId);
            }
        }

        public void SetLibraryPreviewActiveFromNativeUi(string value)
        {
            libraryPreviewActive = value == "1"
                || value.Equals("true", System.StringComparison.OrdinalIgnoreCase);
            if (libraryPreviewActive)
            {
                StopAssistantDrive(true);
                FidgetHapticRouter.StopAllContinuous(true);
                progression?.EndSpinCredit();
                ResetCombo();
            }
            ResetMotionTelemetry(!libraryPreviewActive && HasRotarySpeedTelemetry());
            ResetProgressionRotationBaseline();
            ApplyLibraryPreviewPose();
            ResetComboHaloProjection(!libraryPreviewActive);
        }

        public void ResetCurrentSpinnerFromNativeUi(string unused)
        {
            progression?.EndSpinCredit();
            StopAssistantDrive(true);
            ResetCombo();
            if (blueSpinner != null)
            {
                blueSpinner.ResetFromNativeUi(string.Empty);
            }

            if (metalSpinner != null)
            {
                metalSpinner.ResetRotor();
                explodedView?.SetExploded(false);
                metalCamera?.ResetHero();
                metalMotion?.ResetReference();
                FidgetHapticRouter.Emit(FidgetSemanticEvent.Reset);
            }
            if (edcSlider != null)
            {
                edcSlider.ResetToDefaultDetent();
                edcCamera?.ResetInteractiveView();
                edcMotion?.ResetReference();
            }
            if (fanCard != null)
            {
                fanCard.ResetClosed();
                edcCamera?.ResetInteractiveView();
                edcMotion?.ResetReference();
            }
            ResetMotionTelemetry(HasRotarySpeedTelemetry());
            ResetProgressionRotationBaseline();
            ResetComboHaloProjection(true);
        }

        public void RequestProgressionStateFromNativeUi(string unused)
        {
            PublishProgressionState();
            SpinnerComboNativeBridge.Publish(
                combo != null ? combo.Snapshot : SpinnerComboSnapshot.Rest,
                CurrentAngularSpeedRadians());
            PublishMotionTelemetryNow(CurrentAngularSpeedRadians());
            PublishComboHaloProjectionNow();
        }

        public void SetCollectorFocusFromNativeUi(string modelId)
        {
            if (collectorProgression == null
                || System.Array.IndexOf(ProductModelIds, modelId) < 0)
            {
                return;
            }

            if (collectorProgression.SetFocusModel(modelId))
            {
                progressionUiDirty = true;
                PublishProgressionState();
            }
        }

        private float CurrentAngularSpeedRadians()
        {
            if (metalSpinner != null)
            {
                return metalSpinner.AngularSpeedRadians;
            }

            if (blueSpinner != null)
            {
                return blueSpinner.AngularSpeedRadians;
            }

            if (edcSlider != null)
            {
                return edcSlider.ActivitySpeedRadians;
            }
            return fanCard != null ? fanCard.ActivitySpeedRadians : 0f;
        }

        private bool HasRotarySpeedTelemetry()
        {
            return metalSpinner != null || blueSpinner != null;
        }

        private void PublishMotionTelemetryIfDue(float angularSpeedRadians)
        {
            if (libraryPreviewActive
                || !HasRotarySpeedTelemetry()
                || Time.unscaledTime - lastMotionTelemetryPublishTime
                    < SpinnerComboRules.HudUpdateIntervalSeconds)
            {
                return;
            }

            PublishMotionTelemetryNow(angularSpeedRadians);
        }

        private void PublishMotionTelemetryNow(float angularSpeedRadians)
        {
            bool available = !libraryPreviewActive && HasRotarySpeedTelemetry();
            float normalizedSpeed = available
                ? SpinnerComboRules.NormalizeSpeed(angularSpeedRadians)
                : 0f;
            speedDashboardBand = available
                ? SpinnerSpeedDashboardRules.ResolveBand(
                    normalizedSpeed,
                    speedDashboardBand)
                : SpinnerSpeedBand.Calm;
            ProductMotionTelemetryNativeBridge.Publish(
                available,
                angularSpeedRadians,
                speedDashboardBand);
            lastMotionTelemetryPublishTime = Time.unscaledTime;
        }

        private void ResetMotionTelemetry(bool available)
        {
            speedDashboardBand = SpinnerSpeedBand.Calm;
            lastMotionTelemetryPublishTime = float.NegativeInfinity;
            ProductMotionTelemetryNativeBridge.Publish(
                available,
                0f,
                SpinnerSpeedBand.Calm);
        }

        private void PublishComboHaloProjectionIfDue()
        {
            if (libraryPreviewActive
                || Time.unscaledTime - lastComboHaloProjectionPublishTime
                    < SpinnerComboRules.HudUpdateIntervalSeconds)
            {
                return;
            }

            PublishComboHaloProjectionNow();
        }

        private void PublishComboHaloProjectionNow()
        {
            if (libraryPreviewActive
                || !TryResolveComboHaloProjection(out ComboHaloProjection projection))
            {
                ComboHaloProjectionNativeBridge.Clear();
            }
            else
            {
                ComboHaloProjectionNativeBridge.Publish(projection);
            }

            lastComboHaloProjectionPublishTime = Time.unscaledTime;
        }

        private void ResetComboHaloProjection(bool available)
        {
            lastComboHaloProjectionPublishTime = float.NegativeInfinity;
            if (available)
            {
                PublishComboHaloProjectionNow();
            }
            else
            {
                ComboHaloProjectionNativeBridge.Clear();
            }
        }

        private bool TryResolveComboHaloProjection(
            out ComboHaloProjection projection)
        {
            projection = default;
            Camera camera = Camera.main;
            if (camera == null)
            {
                return false;
            }

            Transform productRoot;
            Vector3 planeNormal;
            bool usesAuthoredAxisFocus = false;
            if (metalSpinner != null)
            {
                productRoot = metalCamera != null && metalCamera.Target != null
                    ? metalCamera.Target
                    : metalSpinner.transform;
                planeNormal = metalSpinner.SpinAxisWorld;
                usesAuthoredAxisFocus = metalCamera != null;
            }
            else if (blueSpinner != null)
            {
                productRoot = blueCamera != null && blueCamera.Target != null
                    ? blueCamera.Target
                    : blueSpinner.transform;
                planeNormal = Vector3.up;
            }
            else if (edcSlider != null || fanCard != null)
            {
                productRoot = edcCamera != null && edcCamera.Target != null
                    ? edcCamera.Target
                    : edcSlider != null
                        ? edcSlider.transform
                        : fanCard.transform;
                planeNormal = productRoot.up;
            }
            else
            {
                return false;
            }

            if (!ProductCameraFraming.TryGetProductBounds(
                    productRoot,
                    out Bounds bounds))
            {
                return false;
            }

            Vector3 modelCenter = usesAuthoredAxisFocus
                ? metalCamera.FocusPoint
                : bounds.center;
            float sampleRadius = Mathf.Max(
                0.001f,
                bounds.extents.magnitude * 0.18f);
            return ComboHaloProjectionRules.TryProject(
                camera,
                modelCenter,
                planeNormal,
                sampleRadius,
                out projection);
        }

        private Vector3 CurrentSpinAxisWorld()
        {
            if (metalSpinner != null)
            {
                return metalSpinner.SpinAxisWorld;
            }

            return edcCamera != null ? edcCamera.transform.up : Vector3.up;
        }

        private void ResetCombo()
        {
            spinReward?.Reset();
            SpinnerSpinRewardNativeBridge.Clear();
            experienceVisuals?.ResetVisuals();
            if (combo != null && combo.Reset())
            {
                SpinnerComboNativeBridge.Publish(combo.Snapshot, 0f);
            }
            lastComboHudPublishTime = float.NegativeInfinity;
        }

        private void ResetComboForReward()
        {
            if (combo != null && combo.Reset())
            {
                SpinnerComboNativeBridge.Publish(combo.Snapshot, 0f);
            }
            lastComboHudPublishTime = float.NegativeInfinity;
        }

        public void SetProgressionAssistantFromNativeUi(string value)
        {
            bool requestedStop = value == "0"
                || value.Equals("false", System.StringComparison.OrdinalIgnoreCase);
            float requestedMultiplier = AssistantDriveSpeedRules.DefaultMultiplier;
            if (!requestedStop
                && !value.Equals("true", System.StringComparison.OrdinalIgnoreCase)
                && (!float.TryParse(
                        value,
                        NumberStyles.Float,
                        CultureInfo.InvariantCulture,
                        out requestedMultiplier)
                    || !AssistantDriveSpeedRules.TryResolveMultiplier(
                        requestedMultiplier,
                        out requestedMultiplier)))
            {
                PublishProgressionState();
                return;
            }

            bool wasEnabled = assistantDriveRequestedThisSession;
            bool enabled = !requestedStop;
            enabled &= !libraryPreviewActive;
            assistantDriveRequestedThisSession = enabled;
            assistantDriveMultiplierThisSession = enabled
                ? requestedMultiplier
                : AssistantDriveSpeedRules.DefaultMultiplier;
            float angularSpeed = AssistantDriveSpeedRules.AngularSpeedFor(
                assistantDriveMultiplierThisSession);
            float sliderSpeed = AssistantDriveSpeedRules.SliderSpeedFor(
                assistantDriveMultiplierThisSession);
            progression?.SetAssistantEnabled(enabled);
            blueSpinner?.SetAssistantDrive(enabled, angularSpeed);
            metalSpinner?.SetAssistantDrive(enabled, angularSpeed);
            edcSlider?.SetAssistantDrive(enabled, sliderSpeed);
            fanCard?.SetAssistantDrive(enabled, sliderSpeed);
            if (enabled && !wasEnabled && progression != null)
            {
                int previousLevel = progression.Snapshot.Level;
                progression.RecordGesture(0.22f, 1f, 0f, false);
                HandleProgressionChanged(previousLevel);
            }
            progressionUiDirty = true;
            PublishProgressionState();
        }

        public void SetThreeBladeMetalSkinFromNativeUi(string skinId)
        {
            if (progression == null
                || progression.ActiveModelId != ThreeBladeMetalSkinCatalog.ModelId)
            {
                return;
            }

            string requested = string.IsNullOrEmpty(skinId)
                ? ThreeBladeMetalSkinCatalog.AutomaticSelectionId
                : skinId;
            if (requested != ThreeBladeMetalSkinCatalog.AutomaticSelectionId
                && !ThreeBladeMetalSkinCatalog.IsUnlocked(
                    requested,
                    progression.Snapshot.Level))
            {
                return;
            }

            selectedThreeBladeMetalSkinId = requested;
            PlayerPrefs.SetString(ThreeBladeMetalSkinSelectionKey, requested);
            PlayerPrefs.Save();
            ApplyProgressionVisualStage();
            FidgetHapticRouter.Emit(FidgetSemanticEvent.Selection);
            progressionUiDirty = true;
            PublishProgressionState();
        }

        public void SetProductStickerFromNativeUi(string stickerId)
        {
            if (progression == null)
            {
                return;
            }

            ProductStickerDefinition sticker = ProductStickerCatalog.Resolve(stickerId);
            selectedProductStickerId = sticker.Id;
            PlayerPrefs.SetString(
                ProductStickerSelectionKeyPrefix + progression.ActiveModelId,
                selectedProductStickerId);
            PlayerPrefs.Save();
            ApplyProductSticker();
            FidgetHapticRouter.Emit(FidgetSemanticEvent.Selection);
            progressionUiDirty = true;
            PublishProgressionState();
        }

        public void SetAppearanceEditorPresentedFromNativeUi(string value)
        {
            bool presented = value == "1"
                || value.Equals("true", System.StringComparison.OrdinalIgnoreCase);
            appearanceEditorPresented = presented;
            appearanceLongPress.Cancel();
            appearanceActivation.Cancel();
            ApplyAppearanceActivationScale(1f);
            SetProductInteractionEnabled(!presented);
            if (presented)
            {
                StopAssistantDrive(true);
                FidgetHapticRouter.StopAllContinuous(true);
            }
        }

        private bool IsAssistantDriveActive()
        {
            return assistantDriveRequestedThisSession
                && ((blueSpinner != null && blueSpinner.IsAssistantDriving)
                    || (metalSpinner != null && metalSpinner.IsAssistantDriving)
                    || (edcSlider != null && edcSlider.IsAssistantDriving)
                    || (fanCard != null && fanCard.IsAssistantDriving));
        }

        private void StopAssistantDrive(bool publishState)
        {
            assistantDriveRequestedThisSession = false;
            assistantDriveMultiplierThisSession =
                AssistantDriveSpeedRules.DefaultMultiplier;
            blueSpinner?.SetAssistantDrive(
                false,
                AssistantDriveSpeedRules.BaseAngularSpeedRadiansPerSecond);
            metalSpinner?.SetAssistantDrive(
                false,
                AssistantDriveSpeedRules.BaseAngularSpeedRadiansPerSecond);
            edcSlider?.SetAssistantDrive(
                false,
                AssistantDriveSpeedRules.BaseSliderSpeedMetersPerSecond);
            fanCard?.SetAssistantDrive(
                false,
                AssistantDriveSpeedRules.BaseSliderSpeedMetersPerSecond);
            progression?.SetAssistantEnabled(false);
            if (publishState && progression != null)
            {
                progressionUiDirty = true;
                PublishProgressionState();
            }
        }

        public void RecenterMotionFromNativeUi(string unused)
        {
            blueMotion?.ResetReference();
            metalMotion?.ResetReference();
            edcMotion?.ResetReference();
            FidgetHapticRouter.Emit(FidgetSemanticEvent.Selection);
        }

        public void SetHapticsEnabledFromNativeUi(string value)
        {
            hapticsEnabled = value == "1" || value.Equals("true", System.StringComparison.OrdinalIgnoreCase);
            ApplyHapticSettings();
        }

        public void SetHapticIntensityFromNativeUi(string value)
        {
            if (TryParse(value, out float parsed))
            {
                hapticIntensity = Mathf.Clamp01(parsed);
                ApplyHapticSettings();
            }
        }

        public void SetHapticFrequencyFromNativeUi(string value)
        {
            if (TryParse(value, out float parsed))
            {
                hapticFrequencyFeel = Mathf.Clamp01(parsed);
                ApplyHapticSettings();
            }
        }

        // Legacy bridge name retained for already-exported native shells.
        public void SetHapticSharpnessFromNativeUi(string value)
        {
            SetHapticFrequencyFromNativeUi(value);
        }

        public void SetDetentsPerTurnFromNativeUi(string value)
        {
            if (int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out int parsed))
            {
                int presetIndex = DetentFeelPresetCatalog
                    .FindClosestIndexByDetentCount(Mathf.Clamp(parsed, 1, 120));
                DetentFeelRuntime.SelectPreset(presetIndex);
                ApplyActiveDetentFeel();
            }
        }

        public void SetHapticDetentsPerTurnFromNativeUi(string value)
        {
            SetDetentsPerTurnFromNativeUi(value);
        }

        public void SetDetentFeelPresetFromNativeUi(string value)
        {
            if (!int.TryParse(
                    value,
                    NumberStyles.Integer,
                    CultureInfo.InvariantCulture,
                    out int presetIndex))
            {
                return;
            }

            DetentFeelRuntime.SelectPreset(presetIndex);
            ApplyActiveDetentFeel();
        }

        public void SetDetentIntensityOverrideFromNativeUi(string value)
        {
            if (TryParse(value, out float intensity))
            {
                DetentFeelRuntime.OverrideIntensity(intensity);
                ApplyActiveDetentFeel();
            }
        }

        public void SetDetentSharpnessOverrideFromNativeUi(string value)
        {
            if (TryParse(value, out float sharpness))
            {
                DetentFeelRuntime.OverrideSharpness(sharpness);
                ApplyActiveDetentFeel();
            }
        }

        public void RequestDetentFeelStateFromNativeUi(string unused)
        {
            DetentFeelDebugBridge.Publish();
        }

        public void SetHapticSpeedFollowFromNativeUi(string value)
        {
            if (TryParse(value, out float parsed))
            {
                hapticSpeedFollow = Mathf.Clamp01(parsed);
                ApplyHapticSettings();
            }
        }

        public void SetHapticSpeedInfluenceFromNativeUi(string value)
        {
            SetHapticSpeedFollowFromNativeUi(value);
        }

        public void SetHapticRhythmFromNativeUi(string value)
        {
            switch (value)
            {
                case "double":
                    hapticRhythm = FidgetHapticRhythm.Double;
                    break;
                case "burst":
                    hapticRhythm = FidgetHapticRhythm.Burst;
                    break;
                default:
                    hapticRhythm = FidgetHapticRhythm.Single;
                    break;
            }
            ApplyHapticSettings();
        }

        public void SetRatchetFeelFromNativeUi(string value)
        {
            switch (value)
            {
                case "light":
                    ratchetFeel = FidgetRatchetFeel.Light;
                    break;
                case "heavy":
                    ratchetFeel = FidgetRatchetFeel.Heavy;
                    break;
                case "mechanical":
                    ratchetFeel = FidgetRatchetFeel.Mechanical;
                    break;
                default:
                    ratchetFeel = FidgetRatchetFeel.Freewheel;
                    break;
            }
            ApplyRatchetFeel();
        }

        public void SetInteractionModeFromNativeUi(string value)
        {
            interactionMode = value == "ratchet"
                ? FidgetInteractionMode.Ratchet
                : FidgetInteractionMode.Smooth;
            ApplyInteractionPreset(ResolveInteractionPreset(interactionMode));
            FidgetHapticRouter.Emit(FidgetSemanticEvent.Selection);
        }

        public void PreviewHapticFromNativeUi(string unused)
        {
            FidgetHapticRouter.Emit(FidgetSemanticEvent.Preview, 0.7f);
        }

        public void SetHapticSpeedTextureProfileFromNativeUi(string value)
        {
            // The dedicated detent lab owns this policy now. Keep the legacy
            // bridge callable for older native shells, but do not allow a
            // saved experimental profile to override the fixed 30/s blur
            // threshold or the active preset's final intensity/sharpness.
            hapticSpeedTextureProfile = HapticSpeedTextureProfile.Recommended;
            FidgetHapticRouter.ConfigureSpeedTexture(hapticSpeedTextureProfile);
        }

        public void PreviewHapticSpeedTextureFromNativeUi(string value)
        {
            float signal = TryParse(value, out float parsed) ? Mathf.Clamp01(parsed) : 0.75f;
            CancelInvoke(nameof(StopHapticSpeedTexturePreview));
            speedTexturePreviewActive = true;
            FidgetHapticRouter.PreviewSpeedTexture(signal);
            Invoke(nameof(StopHapticSpeedTexturePreview), 0.75f);
        }

        private void StopHapticSpeedTexturePreview()
        {
            CancelInvoke(nameof(StopHapticSpeedTexturePreview));
            if (!speedTexturePreviewActive)
            {
                return;
            }

            speedTexturePreviewActive = false;
            FidgetHapticRouter.StopSpeedTexture(false);
        }

        public void SetHapticRecipeOverrideFromNativeUi(string value)
        {
            string[] parts = value.Split('|');
            if (parts.Length != 19
                || !int.TryParse(parts[0], NumberStyles.Integer, CultureInfo.InvariantCulture, out int semanticValue)
                || !int.TryParse(parts[1], NumberStyles.Integer, CultureInfo.InvariantCulture, out int waveformValue)
                || !TryParse(parts[2], out float intensity)
                || !TryParse(parts[3], out float sharpness)
                || !TryParse(parts[4], out float duration)
                || !TryParse(parts[5], out float attack)
                || !TryParse(parts[6], out float decay)
                || !TryParse(parts[7], out float release)
                || !int.TryParse(parts[8], NumberStyles.Integer, CultureInfo.InvariantCulture, out int sustainedValue)
                || !TryParse(parts[9], out float endIntensity)
                || !TryParse(parts[10], out float endSharpness)
                || !int.TryParse(parts[11], NumberStyles.Integer, CultureInfo.InvariantCulture, out int pulseCount)
                || !TryParse(parts[12], out float pulseInterval)
                || !TryParse(parts[13], out float impactLayers)
                || !TryParse(parts[14], out float dynamicIntensity)
                || !TryParse(parts[15], out float dynamicSharpness)
                || !TryParse(parts[16], out float dynamicAttack)
                || !TryParse(parts[17], out float dynamicDecay)
                || !TryParse(parts[18], out float dynamicRelease))
            {
                Debug.LogWarning("[FidgetingApp] Ignored malformed Haptic recipe override.");
                return;
            }

            FidgetSemanticEvent semanticEvent = (FidgetSemanticEvent)Mathf.Clamp(
                semanticValue,
                (int)FidgetSemanticEvent.Selection,
                (int)FidgetSemanticEvent.InertiaShift);
            FidgetHapticWaveform waveform = (FidgetHapticWaveform)Mathf.Clamp(
                waveformValue,
                (int)FidgetHapticWaveform.Transient,
                (int)FidgetHapticWaveform.Hybrid);
            FidgetHapticRecipeLibrary.SetOverride(
                semanticEvent,
                new HapticRecipeOverride(
                    waveform,
                    intensity,
                    sharpness,
                    duration,
                    attack,
                    decay,
                    release,
                    sustainedValue != 0,
                    endIntensity,
                    endSharpness,
                    pulseCount,
                    pulseInterval,
                    impactLayers,
                    dynamicIntensity,
                    dynamicSharpness,
                    dynamicAttack,
                    dynamicDecay,
                    dynamicRelease));
        }

        public void PreviewHapticRecipeFromNativeUi(string value)
        {
            if (!int.TryParse(
                    value,
                    NumberStyles.Integer,
                    CultureInfo.InvariantCulture,
                    out int semanticValue))
            {
                return;
            }

            FidgetSemanticEvent semanticEvent = (FidgetSemanticEvent)Mathf.Clamp(
                semanticValue,
                (int)FidgetSemanticEvent.Selection,
                (int)FidgetSemanticEvent.Preview);
            FidgetHapticRouter.Emit(semanticEvent, 1f);
        }

        public void PreviewSystemHapticFromNativeUi(string value)
        {
            if (int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out int parsed))
            {
                IosHaptics.PlaySystemPreset((IosSystemHapticPreset)Mathf.Clamp(parsed, 0, 8));
            }
        }

        public void SetSpinSensitivityFromNativeUi(string value)
        {
            SetSpinResponseFromNativeUi(value);
        }

        public void SetSpinResponseFromNativeUi(string value)
        {
            if (!TryParse(value, out float parsed))
            {
                return;
            }

            spinResponse = Mathf.Clamp01(parsed);
            blueSpinner?.SetTouchResponse(spinResponse);
            metalGestures?.SetTouchResponse(spinResponse);
        }

        public void SetMaximumSpinSpeedFromNativeUi(string value)
        {
            // Compatibility endpoint for older exported Swift shells. Maximum
            // speed is now derived exclusively from the normalized touch
            // response profile, so this intentionally cannot override it.
            _ = value;
        }

        public void SetCoastHalfLifeFromNativeUi(string value)
        {
            if (!TryParse(value, out float parsed))
            {
                return;
            }

            coastHalfLife = Mathf.Clamp(parsed, 0.05f, 30f);
            spinResistance = FidgetSpinnerMotion.CoastHalfLifeToResistance(coastHalfLife);
            blueSpinner?.SetCoastHalfLife(coastHalfLife);
            metalSpinner?.SetCoastHalfLife(coastHalfLife);
        }

        public void SetSpinResistanceFromNativeUi(string value)
        {
            if (!TryParse(value, out float parsed))
            {
                return;
            }

            spinResistance = Mathf.Clamp01(parsed);
            coastHalfLife = FidgetSpinnerMotion.ResistanceToCoastHalfLife(spinResistance);
            blueSpinner?.SetCoastHalfLife(coastHalfLife);
            metalSpinner?.SetCoastHalfLife(coastHalfLife);
        }

        public void SetSpinnerResistanceModeFromNativeUi(string value)
        {
            ratchetFeel = value == "magnetic"
                ? FidgetRatchetFeel.Mechanical
                : FidgetRatchetFeel.Freewheel;
            interactionMode = ratchetFeel == FidgetRatchetFeel.Freewheel
                ? FidgetInteractionMode.Smooth
                : FidgetInteractionMode.Ratchet;
            blueSpinner?.SetDetentHapticsEnabled(
                interactionMode == FidgetInteractionMode.Ratchet);
            ApplyRatchetFeel();
        }

        public void SetMagneticDetentsPerTurnFromNativeUi(string value)
        {
            SetDetentsPerTurnFromNativeUi(value);
        }

        public void SetMagneticBreakawaySpeedFromNativeUi(string value)
        {
            if (TryParse(value, out float parsed))
            {
                magneticBreakawaySpeed = Mathf.Clamp(parsed, 0f, 20f);
                metalSpinner?.SetMagneticBreakawaySpeed(magneticBreakawaySpeed);
            }
        }

        public void SetMagneticCaptureSpeedFromNativeUi(string value)
        {
            if (TryParse(value, out float parsed))
            {
                magneticCaptureSpeed = Mathf.Clamp(parsed, 0f, 12f);
                metalSpinner?.SetMagneticCaptureSpeed(magneticCaptureSpeed);
            }
        }

        public void SetMagneticSnapResponseFromNativeUi(string value)
        {
            if (TryParse(value, out float parsed))
            {
                magneticSnapResponse = Mathf.Clamp(parsed, 0.1f, 40f);
                metalSpinner?.SetMagneticSnapResponse(magneticSnapResponse);
            }
        }

        public void SetMaximumInputAngleFromNativeUi(string value)
        {
            if (!TryParse(value, out float parsed))
            {
                return;
            }

            maximumInputAngle = Mathf.Clamp(parsed, 4f, 45f);
            blueMotion?.SetMaximumInputAngleFromNativeUi(Invariant(maximumInputAngle));
            ApplyMetalMotionSettings();
        }

        public void SetMotionSensitivityPresetFromNativeUi(string value)
        {
            if (!FidgetMotionSensitivityPresetCatalog.TryResolve(
                    value,
                    out FidgetMotionSensitivityPreset preset))
            {
                return;
            }

            FidgetMotionSensitivityProfile profile =
                FidgetMotionSensitivityPresetCatalog.Resolve(preset);
            bool presetChanged = motionSensitivityPreset != preset;
            motionSensitivityPreset = preset;
            maximumInputAngle = profile.MaximumInputAngle;
            motionResponse = profile.MotionResponse;
            gyroscopeLead = profile.GyroscopeLead;
            maximumMotionOrbit = profile.MaximumMotionOrbit;
            ApplyDeviceMotionSettings();

            // Rebase at the user's current hold angle so changing a preset
            // cannot make the model jump before the next deliberate tilt.
            if (presetChanged)
            {
                blueMotion?.ResetReference();
                metalMotion?.ResetReference();
                edcMotion?.ResetReference();
            }
        }

        public void SetResponseFromNativeUi(string value)
        {
            if (!TryParse(value, out float parsed))
            {
                return;
            }

            motionResponse = Mathf.Clamp(parsed, 1f, 30f);
            blueMotion?.SetResponseFromNativeUi(Invariant(motionResponse));
            ApplyMetalMotionSettings();
        }

        public void SetGyroscopeLeadFromNativeUi(string value)
        {
            if (!TryParse(value, out float parsed))
            {
                return;
            }

            gyroscopeLead = Mathf.Clamp(parsed, 0f, 0.25f);
            blueMotion?.SetGyroscopeLeadFromNativeUi(Invariant(gyroscopeLead));
            ApplyMetalMotionSettings();
        }

        public void SetMaximumMotionOrbitDegreesFromNativeUi(string value)
        {
            if (!TryParse(value, out float parsed))
            {
                return;
            }

            maximumMotionOrbit = Mathf.Clamp(parsed, 0f, 24f);
            blueCamera?.SetMaximumMotionOrbitDegreesFromNativeUi(Invariant(maximumMotionOrbit));
            ApplyMetalMotionSettings();
        }

        public void SetReversalStopDurationFromNativeUi(string value)
        {
            if (!TryParse(value, out float parsed))
            {
                return;
            }

            reversalStopDuration = Mathf.Clamp(parsed, 0.05f, 1.5f);
            metalSpinner?.SetReversalStopDuration(reversalStopDuration);
            metalGestures?.SetReversalStopDuration(reversalStopDuration);
        }

        public void SetFlipDurationFromNativeUi(string value)
        {
            if (TryParse(value, out float parsed))
            {
                flipDuration = Mathf.Clamp(parsed, 0.05f, 2f);
                metalSpinner?.SetFlipMotion(flipDuration, flipOvershoot);
            }
        }

        public void SetFlipOvershootFromNativeUi(string value)
        {
            if (TryParse(value, out float parsed))
            {
                flipOvershoot = Mathf.Clamp(parsed, 0f, 0.25f);
                metalSpinner?.SetFlipMotion(flipDuration, flipOvershoot);
            }
        }

        public void SetFlipOnReleaseFromNativeUi(string value)
        {
            flipOnRelease = value == "1"
                || value.Equals("true", System.StringComparison.OrdinalIgnoreCase);
            metalGestures?.SetFlipOnRelease(flipOnRelease);
        }

        private void ApplyAllSettings()
        {
            ApplyHapticSettings();
            blueSpinner?.SetTouchResponse(spinResponse);
            blueSpinner?.SetCoastHalfLife(coastHalfLife);
            blueSpinner?.SetDetentsPerTurn(detentsPerTurn);
            blueSpinner?.SetDetentHapticsEnabled(
                interactionMode == FidgetInteractionMode.Ratchet);
            metalGestures?.SetTouchResponse(spinResponse);
            metalGestures?.SetReversalStopDuration(reversalStopDuration);
            metalGestures?.SetFlipOnRelease(flipOnRelease);
            metalSpinner?.SetCoastHalfLife(coastHalfLife);
            ApplyRatchetFeel();
            metalSpinner?.SetReversalStopDuration(reversalStopDuration);
            metalSpinner?.SetFlipMotion(flipDuration, flipOvershoot);

            ApplyDeviceMotionSettings();
        }

        private void ApplyDeviceMotionSettings()
        {
            blueMotion?.SetMaximumInputAngleFromNativeUi(Invariant(maximumInputAngle));
            blueMotion?.SetResponseFromNativeUi(Invariant(motionResponse));
            blueMotion?.SetGyroscopeLeadFromNativeUi(Invariant(gyroscopeLead));
            blueCamera?.SetMaximumMotionOrbitDegreesFromNativeUi(Invariant(maximumMotionOrbit));
            ApplyMetalMotionSettings();
        }

        private void ApplyMetalMotionSettings()
        {
            metalMotion?.Configure(
                maximumInputAngle,
                motionResponse,
                gyroscopeLead,
                maximumMotionOrbit);
            edcMotion?.Configure(
                maximumInputAngle,
                motionResponse,
                gyroscopeLead,
                maximumMotionOrbit);
        }

        private void ApplyLibraryPreviewPose()
        {
            blueCamera?.SetLibraryPreviewActive(libraryPreviewActive);
            metalCamera?.SetLibraryPreviewActive(libraryPreviewActive);
            edcCamera?.SetLibraryPreviewActive(libraryPreviewActive);
            environmentPresenter?.SetLibraryPreviewActive(libraryPreviewActive);
        }

        private void UpdateAppearanceLongPressInput()
        {
            if (libraryPreviewActive
                || appearanceEditorPresented
                || appearanceActivation.IsActive
                || modelSceneLoad != null
                || ActiveProductTransform() == null)
            {
                appearanceLongPress.Cancel();
                return;
            }

            Touchscreen touchscreen = Touchscreen.current;
            TouchControl singleTouch = null;
            int pressedTouchCount = 0;
            if (touchscreen != null)
            {
                foreach (TouchControl touch in touchscreen.touches)
                {
                    if (!touch.press.isPressed)
                    {
                        continue;
                    }

                    pressedTouchCount++;
                    singleTouch = touch;
                    if (pressedTouchCount > 1)
                    {
                        appearanceLongPress.Cancel();
                        return;
                    }
                }
            }

            if (singleTouch != null)
            {
                Vector2 positionPixels = singleTouch.position.ReadValue();
                Vector2 positionPoints = ToLogicalPoints(positionPixels);
                if (singleTouch.press.wasPressedThisFrame)
                {
                    appearanceLongPress.Begin(
                        TryHitActiveProduct(positionPixels),
                        positionPoints,
                        Time.unscaledTime);
                }

                if (appearanceLongPress.Update(
                        true,
                        positionPoints,
                        Time.unscaledTime))
                {
                    PresentAppearanceEditor();
                }
                return;
            }

            Mouse mouse = Mouse.current;
            if (mouse != null)
            {
                Vector2 positionPixels = mouse.position.ReadValue();
                Vector2 positionPoints = ToLogicalPoints(positionPixels);
                if (mouse.leftButton.wasPressedThisFrame)
                {
                    appearanceLongPress.Begin(
                        TryHitActiveProduct(positionPixels),
                        positionPoints,
                        Time.unscaledTime);
                }
                if (mouse.leftButton.isPressed)
                {
                    if (appearanceLongPress.Update(
                            true,
                            positionPoints,
                            Time.unscaledTime))
                    {
                        PresentAppearanceEditor();
                    }
                    return;
                }
            }

            appearanceLongPress.Cancel();
        }

        private static Vector2 ToLogicalPoints(Vector2 positionPixels)
        {
            float pixelsPerPoint = Screen.dpi > 0f
                ? Mathf.Max(1f, Screen.dpi / 163f)
                : 2f;
            return positionPixels / pixelsPerPoint;
        }

        private bool TryHitActiveProduct(Vector2 screenPosition)
        {
            Transform product = ActiveProductTransform();
            Camera camera = Camera.main;
            return ProductAppearanceHitTester.ContainsScreenPoint(
                screenPosition,
                blueSpinner,
                metalGestures,
                edcSlider,
                product,
                camera);
        }

        private void PresentAppearanceEditor()
        {
            if (appearanceEditorPresented
                || !appearanceActivation.Begin(Time.unscaledTime))
            {
                return;
            }

            appearanceLongPress.Cancel();
            SetProductInteractionEnabled(false);
            StopAssistantDrive(true);
            FidgetHapticRouter.StopAllContinuous(true);
            FidgetHapticRouter.Emit(FidgetSemanticEvent.Pop);
            ApplyAppearanceActivationScale(1f);
        }

        private void UpdateAppearanceActivation()
        {
            if (!appearanceActivation.IsActive)
            {
                return;
            }

            ProductAppearanceActivationSample sample =
                appearanceActivation.Update(Time.unscaledTime);
            ApplyAppearanceActivationScale(sample.ApparentScale);
            if (!sample.ShouldPresentHalfSheet)
            {
                return;
            }

            appearanceEditorPresented = true;
            PublishProgressionState();
            ProductAppearanceNativeBridge.SetPresented(true);
        }

        private void CancelAppearanceActivation(bool restoreProductInteraction)
        {
            bool wasActive = appearanceActivation.IsActive;
            appearanceActivation.Cancel();
            ApplyAppearanceActivationScale(1f);
            if (wasActive
                && restoreProductInteraction
                && !appearanceEditorPresented)
            {
                SetProductInteractionEnabled(true);
            }
        }

        private void ApplyAppearanceActivationScale(float apparentScale)
        {
            blueCamera?.SetAppearanceActivationScale(apparentScale);
            metalCamera?.SetAppearanceActivationScale(apparentScale);
            edcCamera?.SetAppearanceActivationScale(apparentScale);
        }

        private void SetProductInteractionEnabled(bool enabled)
        {
            if (blueSpinner != null)
            {
                blueSpinner.enabled = enabled;
            }
            if (metalGestures != null)
            {
                metalGestures.enabled = enabled;
            }
            if (edcSlider != null)
            {
                edcSlider.enabled = enabled;
            }
            if (fanCard != null)
            {
                fanCard.enabled = enabled;
            }
            if (edcPresentationGestures != null)
            {
                edcPresentationGestures.enabled = enabled;
            }
        }

        private void ApplyHapticSettings()
        {
            FidgetHapticRouter.ConfigureDetentFeel(DetentFeelRuntime.ActiveConfig);
            IosHaptics.Configure(new FidgetHapticSettings(
                hapticsEnabled,
                hapticIntensity,
                hapticFrequencyFeel,
                hapticRhythm,
                hapticSpeedFollow,
                detentsPerTurn));
            if (!hapticsEnabled)
            {
                FidgetHapticRouter.StopAllContinuous(true);
            }
        }

        private void ApplyActiveDetentFeel()
        {
            DetentFeelConfig config = DetentFeelRuntime.ActiveConfig;
            detentsPerTurn = config.DetentsPerRevolution;
            magneticDetentsPerTurn = detentsPerTurn;
            blueSpinner?.SetDetentsPerTurn(detentsPerTurn);
            metalSpinner?.SetMagneticDetentsPerTurn(detentsPerTurn);
            ApplyHapticSettings();
            DetentFeelDebugBridge.Publish();
        }

        private void ApplyRatchetFeel()
        {
            FidgetRatchetFeel activeFeel = interactionMode == FidgetInteractionMode.Smooth
                ? FidgetRatchetFeel.Freewheel
                : ratchetFeel;
            ResolveRatchetFeel(
                activeFeel,
                out resistanceMode,
                out magneticBreakawaySpeed,
                out magneticCaptureSpeed,
                out magneticSnapResponse);
            magneticDetentsPerTurn = detentsPerTurn;
            metalSpinner?.SetMagneticDetentsPerTurn(detentsPerTurn);
            metalSpinner?.SetMagneticBreakawaySpeed(magneticBreakawaySpeed);
            metalSpinner?.SetMagneticCaptureSpeed(magneticCaptureSpeed);
            metalSpinner?.SetMagneticSnapResponse(magneticSnapResponse);
            metalSpinner?.SetResistanceMode(resistanceMode);
        }

        private void ApplyInteractionPreset(FidgetInteractionPreset preset)
        {
            hapticIntensity = preset.HapticIntensity;
            hapticFrequencyFeel = preset.HapticFrequencyFeel;
            hapticSpeedFollow = preset.HapticSpeedFollow;
            hapticRhythm = preset.HapticRhythm;
            spinResponse = preset.SpinResponse;
            spinResistance = preset.SpinResistance;
            coastHalfLife = FidgetSpinnerMotion.ResistanceToCoastHalfLife(spinResistance);
            ratchetFeel = preset.RatchetFeel;
            detentsPerTurn = DetentFeelRuntime.ActiveConfig.DetentsPerRevolution;
            magneticDetentsPerTurn = detentsPerTurn;
            ApplyAllSettings();
            blueSpinner?.SetDetentHapticsEnabled(preset.ClassicDetentHapticsEnabled);
            DetentFeelDebugBridge.Publish();
        }

        public static FidgetInteractionPreset ResolveInteractionPreset(
            FidgetInteractionMode mode)
        {
            if (mode == FidgetInteractionMode.Ratchet)
            {
                return new FidgetInteractionPreset(
                    0.95f,
                    0.88f,
                    0.35f,
                    FidgetHapticRhythm.Single,
                    FidgetSpinnerMotion.DefaultRatchetTouchResponse,
                    FidgetSpinnerMotion.DefaultSpinResistance,
                    FidgetRatchetFeel.Mechanical,
                    DetentFeelPresetCatalog.Default.Config.DetentsPerRevolution,
                    true);
            }

            return new FidgetInteractionPreset(
                0.62f,
                0.62f,
                0.20f,
                FidgetHapticRhythm.Single,
                FidgetSpinnerMotion.DefaultTouchResponse,
                FidgetSpinnerMotion.DefaultSpinResistance,
                FidgetRatchetFeel.Freewheel,
                DetentFeelPresetCatalog.Default.Config.DetentsPerRevolution,
                false);
        }

        public static void ResolveRatchetFeel(
            FidgetRatchetFeel feel,
            out SpinnerResistanceMode mode,
            out float breakawaySpeed,
            out float captureSpeed,
            out float snapResponse)
        {
            mode = feel == FidgetRatchetFeel.Freewheel
                ? SpinnerResistanceMode.Freewheel
                : SpinnerResistanceMode.MagneticDetent;

            switch (feel)
            {
                case FidgetRatchetFeel.Light:
                    breakawaySpeed = 1.4f;
                    captureSpeed = 0.8f;
                    snapResponse = 10f;
                    break;
                case FidgetRatchetFeel.Heavy:
                    breakawaySpeed = 3.4f;
                    captureSpeed = 1.6f;
                    snapResponse = 24f;
                    break;
                default:
                    breakawaySpeed = 2.2f;
                    captureSpeed = 1.2f;
                    snapResponse = 16f;
                    break;
            }
        }

        private static bool TryParse(string value, out float parsed)
        {
            bool parsedValue = float.TryParse(
                value,
                NumberStyles.Float,
                CultureInfo.InvariantCulture,
                out parsed);
            return parsedValue && !float.IsNaN(parsed) && !float.IsInfinity(parsed);
        }

        private static string Invariant(float value)
        {
            return value.ToString(CultureInfo.InvariantCulture);
        }
    }
}
