using System.Collections;
using System.Globalization;
using CodexUnityLab;
using FidgetingApp.DisplayCase;
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

    public enum LibrarySwipeEndDisposition
    {
        Ignored = 0,
        Rebound = 1,
        Committed = 2
    }

    public sealed class LibrarySwipeSessionGate
    {
        public long ActiveSessionId { get; private set; }
        public long LastResolvedSessionId { get; private set; }
        public bool IsCommitted { get; private set; }

        public bool Begin(long sessionId)
        {
            if (sessionId <= 0 || sessionId <= LastResolvedSessionId)
            {
                return false;
            }
            if (sessionId == ActiveSessionId)
            {
                return true;
            }

            LastResolvedSessionId = System.Math.Max(
                LastResolvedSessionId,
                ActiveSessionId);
            ActiveSessionId = sessionId;
            IsCommitted = false;
            return true;
        }

        public bool Accepts(long sessionId)
        {
            return sessionId > 0 && sessionId == ActiveSessionId;
        }

        public bool Commit(long sessionId)
        {
            if (!Accepts(sessionId))
            {
                return false;
            }
            IsCommitted = true;
            return true;
        }

        public LibrarySwipeEndDisposition End(long sessionId)
        {
            if (!Accepts(sessionId))
            {
                return LibrarySwipeEndDisposition.Ignored;
            }

            LibrarySwipeEndDisposition disposition = IsCommitted
                ? LibrarySwipeEndDisposition.Committed
                : LibrarySwipeEndDisposition.Rebound;
            LastResolvedSessionId = System.Math.Max(
                LastResolvedSessionId,
                ActiveSessionId);
            ActiveSessionId = 0;
            IsCommitted = false;
            return disposition;
        }

        public void Reset()
        {
            LastResolvedSessionId = System.Math.Max(
                LastResolvedSessionId,
                ActiveSessionId);
            ActiveSessionId = 0;
            IsCommitted = false;
        }
    }

    /// <summary>
    /// Stable native bridge and model catalog for the single Fidget Spinner app.
    /// Model scenes can change without changing the iOS product identity or UI shell.
    /// </summary>
    [DefaultExecutionOrder(-1000)]
    public sealed class FidgetAppCoordinator : MonoBehaviour
    {
        public const string BridgeObjectName = "FidgetApp";

        // Retired from the shipping catalog (FDB-PREF-032); scenes remain
        // loadable so old builds and editor tools can still resolve them.
        private const string PointedModelId = ProductCatalog.PointedThreeBladeModelId;
        private const string MetalModelId = ProductCatalog.MetalThreeBladeModelId;
        private const string ImportedModelId = ProductCatalog.GoldFourWingModelId;
        private const string DefaultModelId = ProductCatalog.DefaultModelId;
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
        private string environmentThemeId = SpinnerEnvironmentThemeCatalog.CanyonId;
        private PremiumDisplayCase activeDisplayCase;
        private PremiumDisplayCaseInteractionController activeDisplayCaseInteraction;
        private GameObject activeDisplayCasePrize;
        private Transform displayCaseHiddenProduct;
        private bool displayCaseHiddenProductWasActive;
        private Camera displayCaseCamera;
        private Vector3 displayCaseCameraPosition;
        private Quaternion displayCaseCameraRotation;
        private float displayCaseCameraFieldOfView;
        private GameObject activeGachaRevealHost;
        private GameObject gachaStageHost;
        private Gacha.GachaRevealStageFX gachaStageFX;
        private readonly System.Collections.Generic.List<Renderer>
            gachaHiddenProductRenderers = new System.Collections.Generic.List<Renderer>();
        private Gacha.GachaShippingRevealDirector activeGachaRevealDirector;
        private GameObject activeGachaPrize;
        private string activeGachaRequestId = string.Empty;
        private Coroutine activeGachaReadiness;
        private bool activeGachaRevealStarted;
        private bool activeGachaNativeHybridCandidate;
        private bool activeGachaNativeHybridR029Candidate;
        private bool activeGachaNativeHybridR030Candidate;
        private bool activeGachaNativeHybridLipPublished;
        private string activeGachaNativeHybridR029CaptureCheckpoint =
            string.Empty;
        private string activeGachaNativeHybridR030CaptureCheckpoint =
            string.Empty;
        private bool activeGachaNativeHybridSetupPublished;
        private bool activeGachaNativeHybridSetupSucceeded;
        private string activeGachaNativeHybridSetupFailure = string.Empty;
        private Gacha.GachaNativeHybridSceneIsolation
            activeGachaSceneIsolation;
        private string activeGachaApertureHoldRequestId = string.Empty;
        private bool activeGachaApertureHeld;
        private bool blueCameraWasEnabled;
        private bool metalCameraWasEnabled;
        private bool edcCameraWasEnabled;

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
        private readonly LibrarySwipeSessionGate librarySwipeSessions =
            new LibrarySwipeSessionGate();
        private Coroutine modelSceneLoad;
        private string queuedModelId = string.Empty;
        private float pendingLibraryPageEntranceDirection;
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
        private BadgeRewardLedger badgeRewards;
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
            environmentThemeId = SpinnerEnvironmentThemeCatalog.NormalizeId(
                PlayerPrefs.GetString(
                    SpinnerEnvironmentThemeCatalog.PreferenceKey,
                    SpinnerEnvironmentThemeCatalog.CanyonId));
            SceneManager.sceneLoaded += HandleSceneLoaded;
            ProductCatalogMigration.Apply();
            badgeRewards = new BadgeRewardLedger();
            progression = new SpinnerProgressionRuntime(DefaultModelId, badgeRewards);
            collectorProgression = new CollectorProgressionRuntime(
                DefaultModelId,
                CollectorProgressionRuntime.DefaultPrefix,
                badgeRewards);
            combo = new SpinnerComboRuntime();
            spinReward = new SpinnerSpinRewardRuntime();
            experienceVisuals = gameObject.AddComponent<SpinnerExperienceVisuals>();
            pendingOfflineReward = progression.Resume(System.DateTime.UtcNow);
            BackfillCollectorProgressionIfNeeded();
            progression.ConsumePendingBadgeUnlockCount();
            collectorProgression.ConsumePendingBadgeUnlockCount();
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

            DismissDisplayCaseExperience();
            DismissActiveGachaReveal(false);

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
            if (libraryPreviewActive
                && !Mathf.Approximately(
                    pendingLibraryPageEntranceDirection,
                    0f))
            {
                environmentPresenter?.ParallaxController?
                    .BeginLibraryPageEntrance(
                        pendingLibraryPageEntranceDirection);
                pendingLibraryPageEntranceDirection = 0f;
            }
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
                if (activeGachaSceneIsolation != null
                    && activeGachaSceneIsolation.IsActive
                    && sceneCamera == displayCaseCamera)
                {
                    continue;
                }
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
            if (blueMotion != null)
            {
                blueMotion.SemanticEventRaised -= HandleRotorSemanticEvent;
            }
            blueMotion = FindAnyObjectByType<DeviceMotionController>();
            if (blueMotion != null)
            {
                // Device Twist dial ticks are mechanism events; the router is
                // reached only through this hub, never from the motion input.
                blueMotion.SemanticEventRaised += HandleRotorSemanticEvent;
            }
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

            if (metalMotion != null)
            {
                metalMotion.SemanticEventRaised -= HandleRotorSemanticEvent;
            }
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
                metalMotion.SemanticEventRaised -= HandleRotorSemanticEvent;
                metalMotion.SemanticEventRaised += HandleRotorSemanticEvent;
            }

            ApplyAllSettings();
            ActivateProgressionModel(ModelIdForScene(scenePath));
            ConfigureProgressionVisuals();
            ConfigureProductSticker();
            ConfigureExperienceVisuals();
            environmentPresenter = SpinnerEnvironmentPresenter.Install(scenePath);
            ApplyLibraryPreviewPose();
            ResetProgressionRotationBaseline();
            ResetMotionTelemetry(!libraryPreviewActive && HasMotionTelemetry());
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
                    profile.DetentHapticBodyIntensity,
                    profile.DetentHapticBodySharpness,
                    profile.DetentHapticBodyDurationSeconds,
                    profile.DetentHapticSecondaryIntensity,
                    profile.DetentHapticSecondarySharpness,
                    profile.DetentHapticPulseIntervalSeconds),
                edcSlider.LastSemanticDetentDirection,
                edcSlider.LastSemanticDetentIndex);
        }

        private void HandleFanCardSemanticEvent(
            FidgetSemanticEvent semanticEvent,
            float normalizedSignal)
        {
            if (libraryPreviewActive || fanCard == null || fanCard.Profile == null)
            {
                return;
            }

            FanCardDetentProfile profile = fanCard.Profile;
            FidgetHapticRouter.EmitFanCard(
                semanticEvent,
                normalizedSignal,
                new FanCardHapticTuning(
                    profile.DetentHapticMinimumIntensity,
                    profile.DetentHapticMaximumIntensity,
                    profile.DetentHapticMinimumSharpness,
                    profile.DetentHapticMaximumSharpness,
                    profile.DetentHapticBodyIntensity,
                    profile.DetentHapticBodySharpness,
                    profile.DetentHapticBodyDurationSeconds,
                    profile.DetentHapticTailIntensity,
                    profile.DetentHapticTailSharpness,
                    profile.DetentHapticTailDelaySeconds));
        }

        private void HandleSpinGestureCompleted(float normalizedForce)
        {
            if (libraryPreviewActive || progression == null)
            {
                return;
            }

            float angularSpeed = CurrentAngularSpeedRadians();
            int previousLevel = progression.Snapshot.Level;
            combo.RecordGesture(
                Time.unscaledTime,
                angularSpeed,
                normalizedForce);
            progression.RecordCombo(combo.Snapshot.Count);
            SpinnerSpinRewardNativeBridge.Clear();
            SpinnerComboNativeBridge.Publish(combo.Snapshot, angularSpeed);
            lastComboHudPublishTime = Time.unscaledTime;
            spinReward.RecordGesture(
                normalizedForce,
                angularSpeed);

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
            PlayPendingBadgeUnlockHaptic();
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

            int activityPreviousLevel = progression.Snapshot.Level;
            bool progressionActivityChanged = !libraryPreviewActive
                && progression.RecordActivity(
                    angularSpeed,
                    fingerActivelyTouching ? Time.unscaledDeltaTime : 0f,
                    fingerActivelyTouching || progression.HasSpinCredit);
            if (progressionActivityChanged)
            {
                progressionUiDirty = true;
                if (progression.Snapshot.Level > activityPreviousLevel)
                {
                    HandleProgressionChanged(activityPreviousLevel);
                }
            }
            bool collectorActivityChanged = !libraryPreviewActive
                && fingerActivelyTouching
                && collectorProgression != null
                && collectorProgression.RecordActivity(Time.unscaledDeltaTime);
            if (collectorActivityChanged)
            {
                progressionUiDirty = true;
            }
            if (progressionActivityChanged || collectorActivityChanged)
            {
                PlayPendingBadgeUnlockHaptic();
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
                        progression.RecordCombo(combo.Snapshot.Count);
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
                        PlayPendingBadgeUnlockHaptic();
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
                int techniquePreviousLevel = progression.Snapshot.Level;
                if (progression.RecordTechnique(reward.Kind))
                {
                    progressionUiDirty = true;
                    if (progression.Snapshot.Level > techniquePreviousLevel)
                    {
                        HandleProgressionChanged(techniquePreviousLevel);
                    }
                    PlayPendingBadgeUnlockHaptic();
                }
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
            progression.ConsumePendingBadgeUnlockCount();
            selectedProductStickerId = PlayerPrefs.GetString(
                ProductStickerSelectionKeyPrefix + modelId,
                ProductStickerCatalog.NoneId);
            selectedProductStickerId = ProductStickerCatalog.Resolve(
                selectedProductStickerId).Id;
            ResetCombo();
            ResetProgressionRotationBaseline();
            progressionUiDirty = true;
        }

        private void PlayPendingBadgeUnlockHaptic()
        {
            int count = progression?.ConsumePendingBadgeUnlockCount() ?? 0;
            count += collectorProgression?.ConsumePendingBadgeUnlockCount() ?? 0;
            if (count > 0)
            {
                FidgetHapticRouter.Emit(
                    FidgetSemanticEvent.BadgeUnlocked,
                    Mathf.Clamp01(count / 3f));
            }
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
                progression.BadgeCatalogPayloadFor(snapshot.ModelId),
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
                if (GachaInventory.SyncRhythmTickets(
                    collectorProgression.Snapshot.CompletedRhythmWeeks) > 0)
                {
                    PublishGachaState();
                }
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

            if (scenePath == PointedScenePath)
            {
                return PointedModelId;
            }

            if (scenePath == ImportedScenePath)
            {
                return ImportedModelId;
            }

            return DefaultModelId;
        }

        private void ConfigureProgressionVisuals()
        {
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

            // Progression never adds geometry to a toy. The removed shared
            // SpinnerProgressionVisuals collar/weight-ring/bearing/crown tori
            // were the "strange ring" on every model (FDB-PREF-034).
            RemoveLegacyProgressionRingRoot(rotor);

            bool usesIntegratedThreeBladeSkins = metalSpinner != null
                && progression.ActiveModelId == ThreeBladeMetalSkinCatalog.ModelId;
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

        private Transform DisplayCaseProductRoot(string modelId)
        {
            PremiumDisplayCaseProductProfile profile =
                PremiumDisplayCaseProductProfiles.Resolve(modelId);
            foreach (GameObject root in SceneManager.GetActiveScene()
                         .GetRootGameObjects())
            {
                if (string.Equals(
                        root.name,
                        profile.SceneRootName,
                        System.StringComparison.Ordinal))
                {
                    return root.transform;
                }
            }

            Debug.LogWarning(
                $"[FidgetingApp] Display-case root {profile.SceneRootName} "
                + $"was not found for {modelId}; falling back to the active controller.");
            Transform product = ActiveProductTransform();
            if (metalSpinner == null || product == null || product.parent == null)
            {
                return product;
            }

            // RotorRigidbodyController lives on RotorDynamic, while the fixed
            // hub, caps and bearing visuals are siblings on the shipping root.
            // The display case must snapshot and hide the complete current toy.
            Transform candidate = product.parent;
            return candidate.Find("HubStatic") != null
                ? candidate
                : product;
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
            threeBladeMetalSkins?.Apply(
                snapshot.Level,
                selectedThreeBladeMetalSkinId);
        }

        public const string LegacyProgressionRingRootName = "ProgressionVisuals";

        /// <summary>
        /// Destroys any generated progression ring assembly left under a toy
        /// root. Kept as a runtime guard so a stale scene or third-party
        /// component can never bring the floating rings back.
        /// </summary>
        public static int RemoveLegacyProgressionRingRoot(Transform toyRoot)
        {
            if (toyRoot == null)
            {
                return 0;
            }

            int removed = 0;
            for (int index = toyRoot.childCount - 1; index >= 0; index--)
            {
                Transform child = toyRoot.GetChild(index);
                if (child.name != LegacyProgressionRingRootName)
                {
                    continue;
                }

                if (Application.isPlaying)
                {
                    Destroy(child.gameObject);
                }
                else
                {
                    DestroyImmediate(child.gameObject);
                }

                removed++;
            }

            return removed;
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
            DismissDisplayCaseExperience();
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

            string activeModelId = ModelIdForScene(activeScene.path);
            LoadResolvedModelScene(
                modelId,
                buildIndex,
                ResolveLibraryPageDirection(activeModelId, modelId));
        }

        public static float ResolveLibraryPageDirection(
            string currentModelId,
            string nextModelId)
        {
            int currentIndex = System.Array.IndexOf(
                ProductModelIds,
                currentModelId);
            int nextIndex = System.Array.IndexOf(ProductModelIds, nextModelId);
            if (currentIndex < 0 || nextIndex < 0 || currentIndex == nextIndex)
            {
                return 0f;
            }
            return Mathf.Sign(nextIndex - currentIndex);
        }

        private void LoadResolvedModelScene(
            string modelId,
            int buildIndex,
            float pageDirection)
        {
            if (modelSceneLoad != null)
            {
                queuedModelId = modelId;
                return;
            }

            modelSceneLoad = StartCoroutine(
                LoadResolvedModelSceneAsync(
                    modelId,
                    buildIndex,
                    pageDirection));
        }

        private IEnumerator LoadResolvedModelSceneAsync(
            string modelId,
            int buildIndex,
            float pageDirection)
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

            bool animatePage = libraryPreviewActive
                && !Mathf.Approximately(pageDirection, 0f)
                && !IosDeviceMotion.IsReduceMotionEnabled();
            load.allowSceneActivation = false;
            float transitionStartedAt = Time.unscaledTime;
            if (animatePage)
            {
                environmentPresenter?.ParallaxController?
                    .BeginLibraryPageExit(-pageDirection);
            }

            while (load.progress < 0.9f
                || (animatePage
                    && Time.unscaledTime - transitionStartedAt
                        < SpinnerSceneParallaxController
                            .LibraryPageExitLeadSeconds))
            {
                yield return null;
            }

            pendingLibraryPageEntranceDirection = animatePage
                ? pageDirection
                : 0f;
            load.allowSceneActivation = true;
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
            else
            {
                librarySwipeSessions.Reset();
            }
            ResetMotionTelemetry(!libraryPreviewActive && HasMotionTelemetry());
            ResetProgressionRotationBaseline();
            ApplyLibraryPreviewPose();
            ResetComboHaloProjection(!libraryPreviewActive);
        }

        public void BeginLibrarySwipeFromNativeUi(string value)
        {
            if (libraryPreviewActive
                && long.TryParse(
                    value,
                    NumberStyles.Integer,
                    CultureInfo.InvariantCulture,
                    out long sessionId))
            {
                librarySwipeSessions.Begin(sessionId);
            }
        }

        public void SetLibrarySwipeProgressFromNativeUi(string value)
        {
            string[] fields = (value ?? string.Empty).Split('|');
            if (!libraryPreviewActive
                || fields.Length != 2
                || !long.TryParse(
                    fields[0],
                    NumberStyles.Integer,
                    CultureInfo.InvariantCulture,
                    out long sessionId)
                || !librarySwipeSessions.Accepts(sessionId)
                || !float.TryParse(
                    fields[1],
                    NumberStyles.Float,
                    CultureInfo.InvariantCulture,
                    out float progress))
            {
                return;
            }

            environmentPresenter?.ParallaxController?
                .SetLibraryPageDragProgress(progress);
        }

        public void CommitLibrarySwipeFromNativeUi(string value)
        {
            if (long.TryParse(
                value,
                NumberStyles.Integer,
                CultureInfo.InvariantCulture,
                out long sessionId))
            {
                librarySwipeSessions.Commit(sessionId);
            }
        }

        public void EndLibrarySwipeFromNativeUi(string value)
        {
            if (!long.TryParse(
                value,
                NumberStyles.Integer,
                CultureInfo.InvariantCulture,
                out long sessionId))
            {
                return;
            }

            // A committed page change owns its exit/entrance animation. A
            // cancelled or boundary session rebounds, and a late End from an
            // older session is ignored instead of disturbing the new drag.
            if (librarySwipeSessions.End(sessionId)
                    == LibrarySwipeEndDisposition.Rebound
                && libraryPreviewActive
                && modelSceneLoad == null)
            {
                environmentPresenter?.ParallaxController?
                    .EndLibraryPageDrag();
            }
        }

        public void SetDisplayCasePresentedFromNativeUi(string value)
        {
            bool presented = value == "1"
                || value.Equals("true", System.StringComparison.OrdinalIgnoreCase);
            if (presented)
            {
                PresentDisplayCaseExperience();
            }
            else
            {
                DismissDisplayCaseExperience();
            }
        }

        public void SetDisplayCaseExplodedProgressFromNativeUi(string value)
        {
            if (activeDisplayCaseInteraction != null
                && float.TryParse(
                    value,
                    NumberStyles.Float,
                    CultureInfo.InvariantCulture,
                    out float progress))
            {
                activeDisplayCaseInteraction.SetExplodedProgress(progress);
            }
        }

        public void SetDisplayCaseOrbitFromNativeUi(string value)
        {
            if (activeDisplayCaseInteraction == null)
            {
                return;
            }
            string[] fields = (value ?? string.Empty).Split(',');
            if (fields.Length != 2
                || !float.TryParse(fields[0], NumberStyles.Float,
                    CultureInfo.InvariantCulture, out float yaw)
                || !float.TryParse(fields[1], NumberStyles.Float,
                    CultureInfo.InvariantCulture, out float pitch))
            {
                return;
            }
            activeDisplayCaseInteraction.SetOrbitDegrees(yaw, pitch);
        }

        public void SetDisplayCaseZoomFromNativeUi(string value)
        {
            if (activeDisplayCaseInteraction != null
                && float.TryParse(
                    value,
                    NumberStyles.Float,
                    CultureInfo.InvariantCulture,
                    out float zoom))
            {
                activeDisplayCaseInteraction.SetZoom(zoom);
            }
        }

        public void SetDisplayCaseLightingFromNativeUi(string value)
        {
            PremiumDisplayCaseLightingPreset preset =
                PremiumDisplayCaseLightingCatalog.Resolve(value);
            PlayerPrefs.SetString(
                PremiumDisplayCaseLightingCatalog.PreferenceKey,
                preset.Id);
            activeDisplayCase?.SetLightingPreset(preset.Id);
        }

        public void PlayDisplayCaseAssemblyFromNativeUi(string unused)
        {
            if (activeDisplayCase == null || activeDisplayCaseInteraction == null)
            {
                return;
            }
            activeDisplayCase.play();
            activeDisplayCaseInteraction.SetExplodedProgress(1f);
            activeDisplayCaseInteraction.PlayAssembly();
        }

        public void ExplodeDisplayCaseFromNativeUi(string unused)
        {
            activeDisplayCaseInteraction?.PlayExplode();
        }

        private void PresentDisplayCaseExperience()
        {
            if (activeDisplayCase != null)
            {
                return;
            }

            PremiumDisplayCase prefab = Resources.Load<PremiumDisplayCase>(
                PremiumDisplayCaseFactory.ResourcesPath);
            if (prefab == null)
            {
                Debug.LogError(
                    "[FidgetingApp] Premium display-case prefab is unavailable.");
                return;
            }

            StopAssistantDrive(true);
            FidgetHapticRouter.StopAllContinuous(true);
            progression?.EndSpinCredit();
            ResetCombo();

            string modelId = ModelIdForScene(SceneManager.GetActiveScene().path);
            displayCaseHiddenProduct = DisplayCaseProductRoot(modelId);
            if (displayCaseHiddenProduct == null)
            {
                Debug.LogError(
                    $"[FidgetingApp] No active product is available for {modelId}.");
                return;
            }

            try
            {
                activeDisplayCasePrize = PremiumDisplayCaseProductSnapshot.Capture(
                    modelId,
                    displayCaseHiddenProduct);
            }
            catch (System.Exception exception)
            {
                activeDisplayCasePrize = null;
                Debug.LogError(
                    $"[FidgetingApp] Could not snapshot {modelId} for the "
                    + $"display case: {exception.Message}");
                displayCaseHiddenProduct = null;
                return;
            }

            if (displayCaseHiddenProduct != null)
            {
                displayCaseHiddenProductWasActive =
                    displayCaseHiddenProduct.gameObject.activeSelf;
                displayCaseHiddenProduct.gameObject.SetActive(false);
            }

            displayCaseCamera = Camera.main;
            if (displayCaseCamera != null)
            {
                displayCaseCameraPosition = displayCaseCamera.transform.position;
                displayCaseCameraRotation = displayCaseCamera.transform.rotation;
                displayCaseCameraFieldOfView = displayCaseCamera.fieldOfView;
                displayCaseCamera.transform.position =
                    PremiumDisplayCaseCameraRules.FrontCameraPosition;
                displayCaseCamera.transform.LookAt(
                    PremiumDisplayCaseCameraRules.FrontLookAt);
                displayCaseCamera.fieldOfView =
                    PremiumDisplayCaseCameraRules.ResolveVerticalFieldOfView(
                        displayCaseCamera.aspect);
            }

            activeDisplayCase = Instantiate(prefab, Vector3.zero, Quaternion.identity);
            activeDisplayCase.name = "PremiumDisplayCaseInteractive";
            activeDisplayCaseInteraction = activeDisplayCase.GetComponent<
                PremiumDisplayCaseInteractionController>();
            activeDisplayCase.SetLightingPreset(PlayerPrefs.GetString(
                PremiumDisplayCaseLightingCatalog.PreferenceKey,
                PremiumDisplayCaseLightingCatalog.DefaultId));
            PremiumDisplayCaseProductProfile productProfile =
                PremiumDisplayCaseProductProfiles.Resolve(modelId);
            SpinnerProgressionSnapshot currentProductProgress = progression != null
                ? progression.SnapshotFor(modelId)
                : default;
            int currentProductLevel = progression != null
                ? currentProductProgress.Level
                : 1;
            activeDisplayCase.SetIdentification(
                productProfile.EnglishDisplayName,
                currentProductLevel);
            if (progression != null
                && BadgeCatalogV2.TryResolveFeaturedToyBadge(
                    currentProductProgress,
                    out BadgeDefinition featuredBadge))
            {
                activeDisplayCase.SetFeaturedBadge(
                    featuredBadge.AssetName,
                    BadgeCatalogV2.ToyDisplayToken(
                        currentProductProgress,
                        featuredBadge),
                    featuredBadge.ShortName,
                    featuredBadge.Grade.ToString());
            }
            else
            {
                activeDisplayCase.ClearFeaturedBadge();
            }
            activeDisplayCase.setCapsulePreset(productProfile.CapsulePreset);
            try
            {
                activeDisplayCase.setContent(
                    activeDisplayCasePrize.transform,
                    productProfile.ContentOptions);
            }
            catch (System.Exception exception)
            {
                Debug.LogError(
                    $"[FidgetingApp] Could not attach {modelId} to the display "
                    + $"case: {exception.Message}");
                DismissDisplayCaseExperience();
                return;
            }
            activeDisplayCase.play();
            if (activeDisplayCaseInteraction != null)
            {
                activeDisplayCaseInteraction.SetExplodedProgress(1f);
                activeDisplayCaseInteraction.PlayAssembly();
            }
        }

        private void DismissDisplayCaseExperience()
        {
            if (activeDisplayCase != null && activeDisplayCasePrize != null)
            {
                activeDisplayCase.setContent((Transform)null);
            }
            if (activeDisplayCase != null)
            {
                Destroy(activeDisplayCase.gameObject);
            }
            if (activeDisplayCasePrize != null)
            {
                Destroy(activeDisplayCasePrize);
            }
            activeDisplayCase = null;
            activeDisplayCaseInteraction = null;
            activeDisplayCasePrize = null;

            if (displayCaseHiddenProduct != null)
            {
                displayCaseHiddenProduct.gameObject.SetActive(
                    displayCaseHiddenProductWasActive);
            }
            displayCaseHiddenProduct = null;

            if (displayCaseCamera != null)
            {
                displayCaseCamera.transform.position = displayCaseCameraPosition;
                displayCaseCamera.transform.rotation = displayCaseCameraRotation;
                displayCaseCamera.fieldOfView = displayCaseCameraFieldOfView;
            }
            displayCaseCamera = null;
        }

        public void SetEnvironmentThemeFromNativeUi(string themeId)
        {
            string normalizedThemeId = SpinnerEnvironmentThemeCatalog.NormalizeId(themeId);
            environmentThemeId = normalizedThemeId;
            PlayerPrefs.SetString(
                SpinnerEnvironmentThemeCatalog.PreferenceKey,
                normalizedThemeId);
            PlayerPrefs.Save();

            if (environmentPresenter == null)
            {
                Debug.LogWarning(
                    "[FidgetingApp] Environment theme was saved before the "
                    + $"scene presenter was ready: {normalizedThemeId}.");
                return;
            }

            if (!environmentPresenter.ApplyTheme(normalizedThemeId))
            {
                Debug.LogError(
                    $"[FidgetingApp] Failed to apply environment theme: {normalizedThemeId}.");
                return;
            }

            ApplyLibraryPreviewPose();
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
            ResetMotionTelemetry(HasMotionTelemetry());
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

        private Gacha.GachaInventoryRuntime gachaInventory;
        private const string Gate12PreviewToken =
            "premium-display-case-gate12-r4";
        private const string Gate12PreviewPrefix =
            "fidgeting.gacha.preview.premium-display-case-gate12-r4.";
        private const string Gate04NativeHybridPreviewToken =
            "premium-display-case-gate04-native-hybrid-r026";
        private const string Gate04NativeHybridPreviewPrefix =
            "fidgeting.gacha.preview.premium-display-case-gate04-native-hybrid-r026.";
        private const string Gate04NativeHybridR027PreviewToken =
            "premium-display-case-gate04-native-hybrid-r027";
        private const string Gate04NativeHybridR027PreviewPrefix =
            "fidgeting.gacha.preview.premium-display-case-gate04-native-hybrid-r027.";
        private const string Gate04NativeHybridR028PreviewToken =
            "premium-display-case-gate04-native-hybrid-r028";
        private const string Gate04NativeHybridR028PreviewPrefix =
            "fidgeting.gacha.preview.premium-display-case-gate04-native-hybrid-r028.";
        private const string Gate04NativeHybridR029PreviewToken =
            "premium-display-case-gate04-native-hybrid-r029";
        private const string Gate04NativeHybridR029PreviewPrefix =
            "fidgeting.gacha.preview.premium-display-case-gate04-native-hybrid-r029.";
        private const string Gate04NativeHybridR030PreviewToken =
            "premium-display-case-gate04-native-hybrid-r030";
        private const string Gate04NativeHybridR030PreviewPrefix =
            "fidgeting.gacha.preview.premium-display-case-gate04-native-hybrid-r030.";
        private const float GachaReadinessPositionTolerance = 0.00001f;
        private const float GachaReadinessRotationToleranceDegrees = 0.01f;

        private Gacha.GachaInventoryRuntime GachaInventory =>
            gachaInventory ??= new Gacha.GachaInventoryRuntime();

        private void PublishGachaState(string receiptPayload = "")
        {
            if (string.IsNullOrEmpty(receiptPayload)
                && GachaInventory.PendingTransaction != null)
            {
                Gacha.GachaPendingTransaction pending =
                    GachaInventory.PendingTransaction;
                receiptPayload = Gacha.GachaNativeBridge.ReceiptPayload(
                    pending.Receipt,
                    pending.RequestId);
            }
            Gacha.GachaNativeBridge.Publish(
                Gacha.GachaCatalog.CatalogPayload(),
                GachaInventory.SnapshotPayload(),
                receiptPayload);
        }

        /// <summary>
        /// Native storefront selected a Pack: hide the spinner cameras, move
        /// the main camera to the reveal pose and keep the cave at 25%
        /// brightness behind the sealed Pack. No black stage.
        /// </summary>
        public void EnterGachaStageFromNativeUi(string payload)
        {
            _ = payload;
            if (gachaStageHost != null || activeGachaRevealDirector != null)
            {
                return;
            }
            try
            {
                DismissDisplayCaseExperience();
                StopAssistantDrive(true);
                FidgetHapticRouter.StopAllContinuous(true);
                AcquireGachaCamera();
                gachaStageHost = new GameObject("GachaStageHost");
                gachaStageFX = new Gacha.GachaRevealStageFX(
                    gachaStageHost.transform,
                    displayCaseCamera);
                // The native backdrop stays in front of the environment
                // until the card flips; the environment is the reward.
                // Payload: "r,g,b,strength|/path/to/snapshot.png".
                string tintPayload = payload ?? string.Empty;
                string snapshotPath = string.Empty;
                int separator = tintPayload.IndexOf('|');
                if (separator >= 0)
                {
                    snapshotPath = tintPayload.Substring(separator + 1);
                    tintPayload = tintPayload.Substring(0, separator);
                }
                if (!gachaStageFX.TrySetBackdropImage(snapshotPath)
                    && TryParseGachaStageTint(tintPayload, out Color tint, out float strength))
                {
                    gachaStageFX.SetBackdrop(tint, strength);
                }
            }
            catch (System.Exception exception)
            {
                // No reveal exists yet, so there is no request to report on;
                // fall back to the library cameras and let the reveal path
                // stage itself later.
                Debug.LogWarning("gacha-stage-enter-failed: " + exception.Message);
                LeaveGachaStage();
            }
        }

        /// <summary>Payload "r,g,b[,strength]" in 0–1 from the selected Pack tier.</summary>
        private static bool TryParseGachaStageTint(
            string payload,
            out Color tint,
            out float strength)
        {
            tint = Color.black;
            strength = 1f;
            if (string.IsNullOrWhiteSpace(payload))
            {
                return false;
            }
            string[] parts = payload.Split(',');
            if (parts.Length != 3 && parts.Length != 4)
            {
                return false;
            }
            float[] channels = new float[parts.Length];
            for (int index = 0; index < parts.Length; index++)
            {
                if (!float.TryParse(
                        parts[index].Trim(),
                        NumberStyles.Float,
                        CultureInfo.InvariantCulture,
                        out channels[index]))
                {
                    return false;
                }
                channels[index] = Mathf.Clamp01(channels[index]);
            }
            tint = new Color(channels[0], channels[1], channels[2], 1f);
            if (parts.Length == 4)
            {
                strength = channels[3];
            }
            return true;
        }

        /// <summary>Storefront closed without a reveal; restore the library cameras.</summary>
        public void LeaveGachaStageFromNativeUi(string payload)
        {
            _ = payload;
            if (activeGachaRevealDirector != null)
            {
                return;
            }
            LeaveGachaStage();
        }

        private void LeaveGachaStage()
        {
            gachaStageFX?.Dispose();
            gachaStageFX = null;
            if (gachaStageHost != null)
            {
                Destroy(gachaStageHost);
                gachaStageHost = null;
            }
            RestoreGachaCamera();
        }

        /// <summary>
        /// The seal finished tearing: one medium transient through the
        /// semantic pipeline (Pack mechanism state → semantic Pop → recipe).
        /// </summary>
        public void EmitGachaTearSnapFromNativeUi(string payload)
        {
            _ = payload;
            FidgetHapticRouter.Emit(FidgetSemanticEvent.Pop, 0.7f);
        }

        /// <summary>
        /// Pack carousel settled on a tier. Payload is the tier-ladder weight
        /// 0–1 (GachaPackTierLadder.snapHapticSignal): richer Packs snap
        /// heavier. One detent through the semantic pipeline.
        /// </summary>
        public void EmitGachaCarouselSnapFromNativeUi(string payload)
        {
            float signal = 0.5f;
            if (!string.IsNullOrWhiteSpace(payload)
                && float.TryParse(
                    payload.Trim(),
                    NumberStyles.Float,
                    CultureInfo.InvariantCulture,
                    out float parsed))
            {
                signal = Mathf.Clamp01(parsed);
            }
            FidgetHapticRouter.Emit(FidgetSemanticEvent.DetentCaptured, signal);
        }

        public void RequestGachaStateFromNativeUi(string previewToken)
        {
#if UNITY_EDITOR || DEVELOPMENT_BUILD || FIDGET_GATE12_SIMULATOR_PREVIEW || FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE
            bool isGate12Preview = string.Equals(
                previewToken,
                Gate12PreviewToken,
                System.StringComparison.Ordinal);
            bool isGate04NativeHybridPreview = string.Equals(
                previewToken,
                Gate04NativeHybridPreviewToken,
                System.StringComparison.Ordinal);
            bool isGate04NativeHybridR027Preview = string.Equals(
                previewToken,
                Gate04NativeHybridR027PreviewToken,
                System.StringComparison.Ordinal);
            bool isGate04NativeHybridR028Preview = string.Equals(
                previewToken,
                Gate04NativeHybridR028PreviewToken,
                System.StringComparison.Ordinal);
            bool isGate04NativeHybridR029Preview = string.Equals(
                previewToken,
                Gate04NativeHybridR029PreviewToken,
                System.StringComparison.Ordinal);
            bool isGate04NativeHybridR030Preview = string.Equals(
                previewToken,
                Gate04NativeHybridR030PreviewToken,
                System.StringComparison.Ordinal);
            if (isGate12Preview
                || isGate04NativeHybridPreview
                || isGate04NativeHybridR027Preview
                || isGate04NativeHybridR028Preview
                || isGate04NativeHybridR029Preview
                || isGate04NativeHybridR030Preview)
            {
                string prefix = isGate04NativeHybridR030Preview
                    ? Gate04NativeHybridR030PreviewPrefix
                    : isGate04NativeHybridR029Preview
                    ? Gate04NativeHybridR029PreviewPrefix
                    : isGate04NativeHybridR028Preview
                    ? Gate04NativeHybridR028PreviewPrefix
                    : isGate04NativeHybridR027Preview
                    ? Gate04NativeHybridR027PreviewPrefix
                    : isGate04NativeHybridPreview
                        ? Gate04NativeHybridPreviewPrefix
                        : Gate12PreviewPrefix;
                if (gachaInventory == null
                    || !string.Equals(
                        gachaInventory.StoragePrefix,
                        prefix,
                        System.StringComparison.Ordinal))
                {
                    gachaInventory = new Gacha.GachaInventoryRuntime(
                        prefix,
                        new Gacha.GachaSplitMix64(0x120011UL));
                }
                gachaInventory.PrimeGate12SimulatorPreview();
            }
#endif
            PublishGachaState();
        }

        /// <summary>Payload: "requestId|seriesId|count|ticket".</summary>
        public void DrawGachaFromNativeUi(string payload)
        {
            string[] parts = (payload ?? string.Empty).Split('|');
            string requestId = parts.Length > 0 ? parts[0] : string.Empty;
            if (parts.Length != 4
                || !int.TryParse(
                    parts[2],
                    System.Globalization.NumberStyles.Integer,
                    CultureInfo.InvariantCulture,
                    out int count))
            {
                PublishGachaState(Gacha.GachaNativeBridge.ReceiptPayload(
                    Gacha.GachaDrawReceipt.Failure("malformed-request"),
                    requestId));
                return;
            }

            Gacha.GachaPaymentMethod method = parts[3] == "coin"
                ? Gacha.GachaPaymentMethod.Coin
                : Gacha.GachaPaymentMethod.Ticket;
            Gacha.GachaTransactionResult result = GachaInventory.PrepareDraw(
                parts[1],
                count,
                method,
                requestId);
            PublishGachaState(Gacha.GachaNativeBridge.ReceiptPayload(
                result.Receipt,
                requestId));
        }

        public void PresentGachaPrizeFromNativeUi(string requestId)
        {
            PresentGachaPrizeFromNativeUi(
                requestId,
                false);
        }

        public void PresentGachaNativeHybridCandidateFromNativeUi(
            string requestId)
        {
#if FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE
            PresentGachaPrizeFromNativeUi(
                requestId,
                true);
#else
            Gacha.GachaPresentationNativeBridge.PublishSetup(
                requestId,
                false,
                "native-hybrid-candidate-disabled");
#endif
        }

        public void PresentGachaNativeHybridR028CandidateFromNativeUi(
            string requestId)
        {
#if FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE
            if (!string.Equals(
                    GachaInventory.StoragePrefix,
                    Gate04NativeHybridR028PreviewPrefix,
                    System.StringComparison.Ordinal))
            {
                Gacha.GachaPresentationNativeBridge.PublishSetup(
                    requestId,
                    false,
                    "native-hybrid-r028-candidate-required");
                return;
            }
            PresentGachaPrizeFromNativeUi(
                requestId,
                true);
#else
            Gacha.GachaPresentationNativeBridge.PublishSetup(
                requestId,
                false,
                "native-hybrid-candidate-disabled");
#endif
        }

        public void PresentGachaNativeHybridR029CandidateFromNativeUi(
            string requestId)
        {
#if FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE
            if (!string.Equals(
                    GachaInventory.StoragePrefix,
                    Gate04NativeHybridR029PreviewPrefix,
                    System.StringComparison.Ordinal))
            {
                Gacha.GachaPresentationNativeBridge.PublishSetup(
                    requestId,
                    false,
                    "native-hybrid-r029-candidate-required");
                return;
            }
            PresentGachaPrizeFromNativeUi(
                requestId,
                true,
                true);
#else
            Gacha.GachaPresentationNativeBridge.PublishSetup(
                requestId,
                false,
                "native-hybrid-r029-candidate-disabled");
#endif
        }

        public void PresentGachaNativeHybridR030CandidateFromNativeUi(
            string requestId)
        {
#if FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE
            if (!string.Equals(
                    GachaInventory.StoragePrefix,
                    Gate04NativeHybridR030PreviewPrefix,
                    System.StringComparison.Ordinal))
            {
                Gacha.GachaPresentationNativeBridge.PublishSetup(
                    requestId,
                    false,
                    "native-hybrid-r030-candidate-required");
                return;
            }
            PresentGachaPrizeFromNativeUi(
                requestId,
                true,
                false,
                true);
#else
            Gacha.GachaPresentationNativeBridge.PublishSetup(
                requestId,
                false,
                "native-hybrid-r030-candidate-disabled");
#endif
        }

        /// <summary>Payload: "requestId|F0" through "requestId|F4".</summary>
        public void ConfigureGachaNativeHybridR029CaptureCheckpointFromNativeUi(
            string payload)
        {
#if FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE
            string[] parts = (payload ?? string.Empty).Split('|');
            string requestId = parts.Length > 0 ? parts[0] : string.Empty;
            bool validCheckpoint = parts.Length == 2
                && IsGachaNativeHybridR029CaptureCheckpoint(parts[1]);
            Gacha.GachaTransactionResult transaction =
                GachaInventory.QueryTransaction(requestId);
            if (!validCheckpoint
                || !transaction.Success
                || transaction.Transaction == null
                || transaction.Transaction.Phase
                    == Gacha.GachaTransactionPhase.Completed
                || !string.Equals(
                    GachaInventory.StoragePrefix,
                    Gate04NativeHybridR029PreviewPrefix,
                    System.StringComparison.Ordinal)
                || activeGachaRevealDirector != null)
            {
                Gacha.GachaPresentationNativeBridge.PublishSetup(
                    requestId,
                    false,
                    "native-hybrid-r029-capture-config-rejected");
                return;
            }
            activeGachaNativeHybridR029CaptureCheckpoint = parts[1];
#else
            Gacha.GachaPresentationNativeBridge.PublishSetup(
                payload ?? string.Empty,
                false,
                "native-hybrid-r029-candidate-disabled");
#endif
        }

        /// <summary>Payload: "requestId|F0" through "requestId|F4".</summary>
        public void ConfigureGachaNativeHybridR030CaptureCheckpointFromNativeUi(
            string payload)
        {
#if FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE
            string[] parts = (payload ?? string.Empty).Split('|');
            string requestId = parts.Length > 0 ? parts[0] : string.Empty;
            bool validCheckpoint = parts.Length == 2
                && IsGachaNativeHybridR030CaptureCheckpoint(parts[1]);
            Gacha.GachaTransactionResult transaction =
                GachaInventory.QueryTransaction(requestId);
            if (!validCheckpoint
                || !transaction.Success
                || transaction.Transaction == null
                || transaction.Transaction.Phase
                    == Gacha.GachaTransactionPhase.Completed
                || !string.Equals(
                    GachaInventory.StoragePrefix,
                    Gate04NativeHybridR030PreviewPrefix,
                    System.StringComparison.Ordinal)
                || activeGachaRevealDirector != null)
            {
                Gacha.GachaPresentationNativeBridge.PublishSetup(
                    requestId,
                    false,
                    "native-hybrid-r030-capture-config-rejected");
                return;
            }
            activeGachaNativeHybridR030CaptureCheckpoint = parts[1];
#else
            Gacha.GachaPresentationNativeBridge.PublishSetup(
                payload ?? string.Empty,
                false,
                "native-hybrid-r030-candidate-disabled");
#endif
        }

        public void SetGachaNativeHybridApertureHoldFromNativeUi(
            string payload)
        {
#if FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE
            string[] parts = (payload ?? string.Empty).Split('|');
            string requestId = parts.Length > 0 ? parts[0] : string.Empty;
            bool validHold = parts.Length == 2
                && (parts[1] == "0" || parts[1] == "1");
            Gacha.GachaTransactionResult transaction =
                GachaInventory.QueryTransaction(requestId);
            if (!validHold
                || !transaction.Success
                || transaction.Transaction == null
                || transaction.Transaction.Phase
                    == Gacha.GachaTransactionPhase.Completed
                || !string.Equals(
                    GachaInventory.StoragePrefix,
                    Gate04NativeHybridR028PreviewPrefix,
                    System.StringComparison.Ordinal)
                || (activeGachaRevealDirector != null
                    && !string.Equals(
                        activeGachaRequestId,
                        requestId,
                        System.StringComparison.Ordinal)))
            {
                Gacha.GachaPresentationNativeBridge.PublishPhase(
                    requestId,
                    "aperture-hold-rejected");
                return;
            }
            activeGachaApertureHoldRequestId = requestId;
            activeGachaApertureHeld = parts[1] == "1";
#else
            Gacha.GachaPresentationNativeBridge.PublishPhase(
                payload ?? string.Empty,
                "aperture-hold-rejected:native-hybrid-candidate-disabled");
#endif
        }

        private void PresentGachaPrizeFromNativeUi(
            string requestId,
            bool useNativeHybridCandidate,
            bool useNativeHybridR029Candidate = false,
            bool useNativeHybridR030Candidate = false)
        {
            Gacha.GachaTransactionResult transaction =
                GachaInventory.QueryTransaction(requestId);
            if (!transaction.Success
                || transaction.Transaction.Phase
                    == Gacha.GachaTransactionPhase.Completed
                || transaction.Receipt.Rows.Count != 1)
            {
                Gacha.GachaPresentationNativeBridge.PublishSetup(
                    requestId,
                    false,
                    transaction.Success
                        ? "receipt-not-presentable"
                        : transaction.FailureReason);
                return;
            }
            if (activeGachaRevealDirector != null)
            {
                if (string.Equals(
                        activeGachaRequestId,
                        requestId,
                        System.StringComparison.Ordinal)
                    && activeGachaNativeHybridCandidate
                        == useNativeHybridCandidate
                    && activeGachaNativeHybridR029Candidate
                        == useNativeHybridR029Candidate
                    && activeGachaNativeHybridR030Candidate
                        == useNativeHybridR030Candidate)
                {
                    Gacha.GachaPresentationNativeBridge.PublishSetup(
                        requestId,
                        true,
                        handoffDurationSeconds:
                            activeGachaRevealDirector
                                .HandoffDurationSeconds);
                }
                else
                {
                    Gacha.GachaPresentationNativeBridge.PublishSetup(
                        requestId,
                        false,
                        activeGachaRequestId == requestId
                            ? "reveal-route-mismatch"
                            : "another-reveal-active");
                }
                return;
            }

            Gacha.GachaDrawReceiptRow row = transaction.Receipt.Rows[0];
            Gacha.GachaPrizeDefinition? resolved =
                Gacha.GachaCatalog.ResolvePrize(row.Outcome.PrizeId);
            if (!resolved.HasValue
                || resolved.Value.Kind != Gacha.GachaPrizeKind.Toy
                || !string.Equals(
                    resolved.Value.ContentReference,
                    "toy/metal-three-blade",
                    System.StringComparison.Ordinal))
            {
                Gacha.GachaPresentationNativeBridge.PublishSetup(
                    requestId,
                    false,
                    "receipt-prize-not-canonical-toy");
                return;
            }

            try
            {
                DismissDisplayCaseExperience();
                StopAssistantDrive(true);
                FidgetHapticRouter.StopAllContinuous(true);
                progression?.EndSpinCredit();
                ResetCombo();
                AcquireGachaCamera();

                activeGachaPrize =
                    ThreeBladeDisplayPrizeFactory.Instantiate();
                activeGachaRevealHost = new GameObject(
                    "GachaShippingRevealHost");
                CreateGachaRevealLighting(
                    activeGachaRevealHost.transform);
                activeGachaRevealDirector =
                    activeGachaRevealHost.AddComponent<
                        Gacha.GachaShippingRevealDirector>();
                activeGachaRevealDirector.revealCompleted +=
                    HandleGachaShippingRevealCompleted;
                activeGachaRevealDirector.caseCrossedPackLip +=
                    HandleGachaNativeHybridCaseCrossedPackLip;
                activeGachaRevealDirector.frontRevealed +=
                    HandleGachaShippingFrontRevealed;
                int productLevel = progression != null
                    ? progression.SnapshotFor(MetalModelId).Level
                    : 1;
                if (useNativeHybridCandidate)
                {
                    activeGachaRevealDirector.BeginNativeHybridCandidate(
                        resolved.Value,
                        row,
                        productLevel,
                        activeGachaPrize.transform,
                        IosDeviceMotion.IsReduceMotionEnabled());
                }
                else
                {
                    if (gachaStageFX != null)
                    {
                        activeGachaRevealDirector.AdoptStageFX(gachaStageFX);
                        gachaStageFX = null;
                    }
                    // The shipping choreography releases the Pack on its
                    // first frame; the request id must exist before Begin.
                    activeGachaRequestId = requestId;
                    activeGachaRevealDirector.Begin(
                        resolved.Value,
                        row,
                        productLevel,
                        activeGachaPrize.transform,
                        IosDeviceMotion.IsReduceMotionEnabled());
                }
                activeGachaNativeHybridCandidate = useNativeHybridCandidate;
                activeGachaNativeHybridR029Candidate =
                    useNativeHybridR029Candidate;
                activeGachaNativeHybridR030Candidate =
                    useNativeHybridR030Candidate;
                activeGachaNativeHybridLipPublished = false;
                activeGachaNativeHybridSetupPublished = false;
                activeGachaNativeHybridSetupSucceeded = false;
                activeGachaNativeHybridSetupFailure = string.Empty;
                if (!activeGachaNativeHybridR029Candidate)
                {
                    activeGachaNativeHybridR029CaptureCheckpoint =
                        string.Empty;
                }
                if (!activeGachaNativeHybridR030Candidate)
                {
                    activeGachaNativeHybridR030CaptureCheckpoint =
                        string.Empty;
                }
                activeGachaRequestId = requestId;
                if (useNativeHybridCandidate)
                {
                    activeGachaSceneIsolation =
                        new Gacha.GachaNativeHybridSceneIsolation();
                    activeGachaSceneIsolation.Apply(
                        displayCaseCamera,
                        activeGachaRevealDirector.ActiveCase.transform);
                    MaintainActiveGachaNativeHybridIsolation();
                    if (!activeGachaRevealDirector
                            .HasCanonicalNativeHybridCase
                        || !activeGachaSceneIsolation
                            .HasOnlyCaseRenderers
                        || !activeGachaSceneIsolation
                            .UsesCavityClearBackdrop)
                    {
                        throw new System.InvalidOperationException(
                            "native-hybrid-case-isolation-invalid");
                    }
                    if (!activeGachaNativeHybridR029Candidate
                        && !activeGachaNativeHybridR030Candidate)
                    {
                        activeGachaSceneIsolation.RenderIsolatedFrame();
                    }
                    MaintainActiveGachaNativeHybridIsolation();
                    Gacha.GachaPresentationNativeBridge
                        .PublishComposition(
                            requestId,
                            activeGachaRevealDirector
                                .NativeHybridCaseRootName,
                            activeGachaRevealDirector
                                .NativeHybridCaseTypeName,
                            activeGachaRevealDirector
                                .NativeHybridCaseEntityId.ToString(),
                            activeGachaRevealDirector
                                .NativeHybridCaseRendererCount,
                            activeGachaRevealDirector
                                .HasCanonicalNativeHybridCase,
                            activeGachaSceneIsolation
                                .HasOnlyCaseRenderers,
                            activeGachaSceneIsolation
                                .UsesCavityClearBackdrop);
                    Gacha.GachaPresentationNativeBridge.PublishPhase(
                        requestId,
                        "native-hybrid-case-staged");
                    PublishGachaNativeHybridTrace(
                        "F0",
                        requestId,
                        false,
                        false);
                }
                activeGachaReadiness = StartCoroutine(
                    ConfirmGachaRevealReadyAfterTwoFrames(requestId));
            }
            catch (System.Exception exception)
            {
                DismissActiveGachaReveal(false);
                Gacha.GachaPresentationNativeBridge.PublishSetup(
                    requestId,
                    false,
                    exception.Message);
            }
        }

        public void AcknowledgeGachaRevealFromNativeUi(string requestId)
        {
            Gacha.GachaTransactionResult result =
                GachaInventory.AcknowledgePending(requestId);
            if (!result.Success)
            {
                Gacha.GachaPresentationNativeBridge.PublishPhase(
                    requestId,
                    "ack-rejected:" + result.FailureReason);
                return;
            }
            Gacha.GachaPresentationNativeBridge.PublishPhase(
                requestId,
                "acknowledged");
            if (string.Equals(
                    activeGachaRequestId,
                    requestId,
                    System.StringComparison.Ordinal))
            {
                DismissActiveGachaReveal(true);
            }
            PublishGachaState();
        }

        public void InterruptGachaRevealFromNativeUi(string requestId)
        {
            if (string.Equals(
                    activeGachaRequestId,
                    requestId,
                    System.StringComparison.Ordinal))
            {
                DismissActiveGachaReveal(false);
            }
        }

        public void StartGachaRevealFromNativeUi(string requestId)
        {
            if (!TryValidateGachaRevealOwnership(
                    requestId,
                    out string failureReason))
            {
                Gacha.GachaPresentationNativeBridge.PublishPhase(
                    requestId,
                    "reveal-start-rejected:" + failureReason);
                return;
            }
            if (activeGachaRevealStarted)
            {
                Gacha.GachaPresentationNativeBridge.PublishPhase(
                    requestId,
                    "revealing");
                return;
            }

            activeGachaRevealStarted = true;
            activeGachaRevealDirector.Play();
            Gacha.GachaPresentationNativeBridge.PublishPhase(
                requestId,
                "revealing");
        }

        public void SetGachaNativeHybridPreviewProgressFromNativeUi(
            string payload)
        {
#if FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE
            string[] parts = (payload ?? string.Empty).Split('|');
            if (parts.Length != 2
                || !float.TryParse(
                    parts[1],
                    System.Globalization.NumberStyles.Float,
                    CultureInfo.InvariantCulture,
                    out float progress))
            {
                Gacha.GachaPresentationNativeBridge.PublishPhase(
                    parts.Length > 0 ? parts[0] : string.Empty,
                    "preview-progress-rejected:malformed-request");
                return;
            }
            if (!TryValidateGachaRevealOwnership(
                    parts[0],
                    out string failureReason)
                || !activeGachaNativeHybridCandidate)
            {
                Gacha.GachaPresentationNativeBridge.PublishPhase(
                    parts[0],
                    "preview-progress-rejected:" + (
                        string.IsNullOrEmpty(failureReason)
                            ? "native-hybrid-candidate-required"
                            : failureReason));
                return;
            }
            try
            {
                activeGachaRevealDirector.SetNativeHybridPreviewProgress(
                    Mathf.Clamp01(progress));
                if (activeGachaRevealDirector.NativeHybridProgress
                    >= Gacha.GachaNativeHybridCandidateMotion
                        .PackLipCrossingProgress)
                {
                    PublishGachaNativeHybridCaseCrossing();
                }
            }
            catch (System.Exception exception)
            {
                Gacha.GachaPresentationNativeBridge.PublishPhase(
                    parts[0],
                    "preview-progress-rejected:" + exception.Message);
            }
#else
            Gacha.GachaPresentationNativeBridge.PublishPhase(
                payload ?? string.Empty,
                "preview-progress-rejected:native-hybrid-candidate-disabled");
#endif
        }

        public void SkipGachaRevealFromNativeUi(string requestId)
        {
            if (!TryValidateGachaRevealOwnership(
                    requestId,
                    out string failureReason))
            {
                Gacha.GachaPresentationNativeBridge.PublishPhase(
                    requestId,
                    "skip-rejected:" + failureReason);
                return;
            }
            activeGachaRevealStarted = true;
            activeGachaRevealDirector.Skip();
        }

        private IEnumerator ConfirmGachaRevealReadyAfterTwoFrames(
            string requestId)
        {
            while (IsGachaNativeHybridCaptureCheckpoint(
                requestId,
                "F0"))
            {
                yield return null;
            }

            yield return new WaitForEndOfFrame();
            MaintainActiveGachaNativeHybridIsolation();
            if (!TryValidateGachaRevealOwnership(
                    requestId,
                    out string firstFailure))
            {
                PublishActiveGachaRevealSetup(
                    requestId,
                    false,
                    firstFailure);
                PublishGachaNativeHybridTrace(
                    "F1",
                    requestId,
                    false,
                    false);
                activeGachaReadiness = null;
                DismissActiveGachaReveal(false);
                yield break;
            }

            PremiumDisplayCaseShippingPresentation caseReference =
                activeGachaRevealDirector.ActiveCase;
            GameObject prizeReference = activeGachaPrize;
            Camera cameraReference = displayCaseCamera;
            Vector3 casePosition = caseReference.transform.localPosition;
            Quaternion caseRotation = caseReference.transform.localRotation;
            Vector3 caseScale = caseReference.transform.localScale;
            Vector3 cameraPosition = cameraReference.transform.position;
            Quaternion cameraRotation = cameraReference.transform.rotation;
            float cameraFieldOfView = cameraReference.fieldOfView;

            PublishGachaNativeHybridTrace(
                "F1",
                requestId,
                true,
                true);
            while (IsGachaNativeHybridCaptureCheckpoint(
                requestId,
                "F1"))
            {
                yield return null;
            }

            yield return new WaitForEndOfFrame();
            MaintainActiveGachaNativeHybridIsolation();
            bool ownershipValid = TryValidateGachaRevealOwnership(
                requestId,
                out string secondFailure);
            bool sameCase = ownershipValid
                && activeGachaRevealDirector.ActiveCase == caseReference;
            bool samePrize = ownershipValid
                && activeGachaPrize == prizeReference;
            bool sameCamera = ownershipValid
                && displayCaseCamera == cameraReference;
            bool caseStable = sameCase && HasStableTransform(
                caseReference.transform,
                casePosition,
                caseRotation,
                caseScale);
            bool cameraStable = sameCamera && HasStableCamera(
                cameraReference,
                cameraPosition,
                cameraRotation,
                cameraFieldOfView);
            if (!ownershipValid
                || !sameCase
                || !samePrize
                || !sameCamera
                || !caseStable
                || !cameraStable)
            {
                string setupFailure = !string.IsNullOrEmpty(secondFailure)
                    ? secondFailure
                    : !sameCase
                        ? "reveal-case-replaced"
                        : !samePrize
                            ? "reveal-prize-replaced"
                            : !sameCamera
                                ? "reveal-camera-replaced"
                                : !caseStable
                                    ? "reveal-case-transform-unstable"
                                    : "reveal-camera-transform-unstable";
                PublishActiveGachaRevealSetup(
                    requestId,
                    false,
                    setupFailure);
                PublishGachaNativeHybridTrace(
                    "F2",
                    requestId,
                    caseStable,
                    cameraStable);
                activeGachaReadiness = null;
                DismissActiveGachaReveal(false);
                yield break;
            }

            while (IsGachaNativeHybridApertureHeld(requestId))
            {
                yield return null;
                MaintainActiveGachaNativeHybridIsolation();
                if (!TryValidateGachaRevealOwnership(
                        requestId,
                        out string holdFailure)
                    || activeGachaRevealDirector.ActiveCase != caseReference
                    || activeGachaPrize != prizeReference
                    || displayCaseCamera != cameraReference)
                {
                    string setupFailure = string.IsNullOrEmpty(holdFailure)
                        ? "reveal-identity-changed"
                        : holdFailure;
                    PublishActiveGachaRevealSetup(
                        requestId,
                        false,
                        setupFailure);
                    PublishGachaNativeHybridTrace(
                        "F2",
                        requestId,
                        false,
                        false);
                    activeGachaReadiness = null;
                    DismissActiveGachaReveal(false);
                    yield break;
                }
            }

            activeGachaReadiness = null;
            PublishActiveGachaRevealSetup(
                requestId,
                true,
                handoffDurationSeconds:
                    activeGachaRevealDirector.HandoffDurationSeconds);
            MaintainActiveGachaNativeHybridIsolation();
            PublishGachaNativeHybridTrace(
                "F2",
                requestId,
                true,
                true);
        }

        private bool TryValidateGachaRevealOwnership(
            string requestId,
            out string failureReason)
        {
            MaintainActiveGachaNativeHybridIsolation();
            if (!string.Equals(
                    activeGachaRequestId,
                    requestId,
                    System.StringComparison.Ordinal))
            {
                failureReason = "stale-request";
                return false;
            }
            if (activeGachaRevealDirector == null
                || activeGachaRevealDirector.ActiveCase == null
                || !activeGachaRevealDirector.ActiveCase.gameObject.activeInHierarchy)
            {
                failureReason = "real-case-missing";
                return false;
            }
            if (activeGachaNativeHybridCandidate
                && (!activeGachaRevealDirector
                        .HasCanonicalNativeHybridCase
                    || activeGachaSceneIsolation == null
                    || !activeGachaSceneIsolation.HasOnlyCaseRenderers
                    || !activeGachaSceneIsolation
                        .UsesCavityClearBackdrop))
            {
                failureReason = "native-hybrid-scene-not-isolated";
                return false;
            }
            if (activeGachaPrize == null
                || activeGachaRevealDirector.Prize
                    != activeGachaPrize.transform
                || !activeGachaPrize.transform.IsChildOf(
                    activeGachaRevealDirector.ActiveCase.ContentSlot))
            {
                failureReason = "real-prize-missing";
                return false;
            }
            if (displayCaseCamera == null
                || displayCaseCamera != Camera.main
                || !displayCaseCamera.enabled)
            {
                failureReason = "real-camera-missing";
                return false;
            }
            failureReason = string.Empty;
            return true;
        }

        private bool IsGachaNativeHybridApertureHeld(string requestId)
        {
            return activeGachaNativeHybridCandidate
                && activeGachaApertureHeld
                && string.Equals(
                    activeGachaApertureHoldRequestId,
                    requestId,
                    System.StringComparison.Ordinal);
        }

        private static bool IsGachaNativeHybridR029CaptureCheckpoint(
            string checkpoint)
        {
            return checkpoint == "F0"
                || checkpoint == "F1"
                || checkpoint == "F2"
                || checkpoint == "F3"
                || checkpoint == "F4";
        }

        private static bool IsGachaNativeHybridR030CaptureCheckpoint(
            string checkpoint)
        {
            return checkpoint == "F0"
                || checkpoint == "F1"
                || checkpoint == "F2"
                || checkpoint == "F3"
                || checkpoint == "F4";
        }

        private bool IsGachaNativeHybridCaptureCheckpoint(
            string requestId,
            string checkpoint)
        {
            return (activeGachaNativeHybridR029Candidate
                && string.Equals(
                    activeGachaRequestId,
                    requestId,
                    System.StringComparison.Ordinal)
                && string.Equals(
                    activeGachaNativeHybridR029CaptureCheckpoint,
                    checkpoint,
                    System.StringComparison.Ordinal))
                || (activeGachaNativeHybridR030Candidate
                    && string.Equals(
                        activeGachaRequestId,
                        requestId,
                        System.StringComparison.Ordinal)
                    && string.Equals(
                        activeGachaNativeHybridR030CaptureCheckpoint,
                        checkpoint,
                        System.StringComparison.Ordinal));
        }

        private void MaintainActiveGachaNativeHybridIsolation()
        {
            if (!activeGachaNativeHybridCandidate)
            {
                return;
            }

            activeGachaSceneIsolation?.Maintain();
        }

        private void PublishActiveGachaRevealSetup(
            string requestId,
            bool succeeded,
            string failureReason = "",
            float handoffDurationSeconds = 0f)
        {
            if (activeGachaNativeHybridCandidate
                && string.Equals(
                    activeGachaRequestId,
                    requestId,
                    System.StringComparison.Ordinal))
            {
                activeGachaNativeHybridSetupPublished = true;
                activeGachaNativeHybridSetupSucceeded = succeeded;
                activeGachaNativeHybridSetupFailure =
                    failureReason ?? string.Empty;
            }

            Gacha.GachaPresentationNativeBridge.PublishSetup(
                requestId,
                succeeded,
                failureReason,
                handoffDurationSeconds);
        }

        private void PublishGachaNativeHybridTrace(
            string checkpoint,
            string requestId,
            bool caseStableFrame,
            bool cameraStableFrame)
        {
            MaintainActiveGachaNativeHybridIsolation();
            bool setupSucceeded = activeGachaNativeHybridSetupPublished
                && activeGachaNativeHybridSetupSucceeded;
            string setupFailure = activeGachaNativeHybridSetupPublished
                ? activeGachaNativeHybridSetupFailure
                : string.Empty;
            PublishGachaNativeHybridR029Trace(
                checkpoint,
                requestId,
                caseStableFrame,
                cameraStableFrame,
                setupSucceeded,
                setupFailure);
            PublishGachaNativeHybridR030Trace(
                checkpoint,
                requestId,
                caseStableFrame,
                cameraStableFrame);
        }

        private void PublishGachaNativeHybridR029Trace(
            string checkpoint,
            string requestId,
            bool caseStableFrame,
            bool cameraStableFrame,
            bool setupSucceeded,
            string revealSetupFailure)
        {
#if FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE
            if (!activeGachaNativeHybridR029Candidate)
            {
                return;
            }

            Gacha.GachaTransactionResult transaction =
                GachaInventory.QueryTransaction(requestId);
            string receiptUuid = transaction.Success
                ? transaction.RequestId
                : string.Empty;
            Gacha.GachaShippingRevealDirector director =
                activeGachaRevealDirector;
            Gacha.GachaNativeHybridSceneIsolation isolation =
                activeGachaSceneIsolation;
            Gacha.GachaPresentationNativeBridge.PublishR029Trace(
                new Gacha.GachaNativeHybridR029Trace(
                    checkpoint,
                    requestId,
                    receiptUuid,
                    Time.frameCount,
                    director != null
                        ? director.NativeHybridCaseRootName
                        : string.Empty,
                    director != null
                        ? director.NativeHybridCaseTypeName
                        : string.Empty,
                    director != null
                        ? director.NativeHybridCaseEntityId.ToString()
                        : string.Empty,
                    director != null
                        ? director.NativeHybridCaseRendererCount
                        : 0,
                    isolation != null
                        ? isolation.ForeignRendererCount
                        : -1,
                    caseStableFrame,
                    cameraStableFrame,
                    setupSucceeded,
                    revealSetupFailure,
                    director != null
                        ? director.NativeHybridProgress
                        : 0f,
                    director != null
                        && director.HasCanonicalNativeHybridCase,
                    isolation != null
                        && isolation.HasOnlyCaseRenderers,
                    isolation != null
                        && isolation.UsesCavityClearBackdrop));
#endif
        }

        private void PublishGachaNativeHybridR030Trace(
            string checkpoint,
            string requestId,
            bool caseStableFrame,
            bool cameraStableFrame)
        {
#if FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE
            if (!activeGachaNativeHybridR030Candidate)
            {
                return;
            }

            Gacha.GachaTransactionResult transaction =
                GachaInventory.QueryTransaction(requestId);
            string receiptUuid = transaction.Success
                ? transaction.RequestId
                : string.Empty;
            Gacha.GachaShippingRevealDirector director =
                activeGachaRevealDirector;
            Gacha.GachaNativeHybridSceneIsolation isolation =
                activeGachaSceneIsolation;
            Camera camera = displayCaseCamera;
            Gacha.GachaPresentationNativeBridge.PublishR030Trace(
                new Gacha.GachaNativeHybridR030Trace(
                    checkpoint,
                    StableFrameOrdinalFor(checkpoint),
                    requestId,
                    receiptUuid,
                    Time.frameCount,
                    camera != null
                        ? (long)EntityId.ToULong(camera.GetEntityId())
                        : 0,
                    camera != null ? camera.name : string.Empty,
                    director != null
                        ? director.NativeHybridCaseRootName
                        : string.Empty,
                    director != null
                        ? director.NativeHybridCaseTypeName
                        : string.Empty,
                    director != null
                        ? director.NativeHybridCaseEntityId.ToString()
                        : string.Empty,
                    director != null
                        ? director.NativeHybridCaseRendererCount
                        : 0,
                    isolation != null
                        ? isolation.ForeignRendererCount
                        : -1,
                    caseStableFrame,
                    cameraStableFrame,
                    isolation != null && isolation.IsActive,
                    isolation != null
                        && isolation.UsesCavityClearBackdrop,
                    activeGachaNativeHybridSetupPublished,
                    activeGachaNativeHybridSetupSucceeded,
                    activeGachaNativeHybridSetupFailure,
                    director != null
                        ? director.NativeHybridProgress
                        : 0f,
                    director != null
                        && director.HasCanonicalNativeHybridCase,
                    isolation != null
                        && isolation.HasOnlyCaseRenderers));
#endif
        }

        private static int StableFrameOrdinalFor(string checkpoint)
        {
            if (checkpoint == "F0")
            {
                return 0;
            }
            if (checkpoint == "F1")
            {
                return 1;
            }
            return 2;
        }

        private static bool HasStableTransform(
            Transform target,
            Vector3 position,
            Quaternion rotation,
            Vector3 scale)
        {
            return target != null
                && Vector3.SqrMagnitude(target.localPosition - position)
                    <= GachaReadinessPositionTolerance
                        * GachaReadinessPositionTolerance
                && Quaternion.Angle(target.localRotation, rotation)
                    <= GachaReadinessRotationToleranceDegrees
                && Vector3.SqrMagnitude(target.localScale - scale)
                    <= GachaReadinessPositionTolerance
                        * GachaReadinessPositionTolerance;
        }

        private static bool HasStableCamera(
            Camera camera,
            Vector3 position,
            Quaternion rotation,
            float fieldOfView)
        {
            return camera != null
                && Vector3.SqrMagnitude(camera.transform.position - position)
                    <= GachaReadinessPositionTolerance
                        * GachaReadinessPositionTolerance
                && Quaternion.Angle(camera.transform.rotation, rotation)
                    <= GachaReadinessRotationToleranceDegrees
                && Mathf.Abs(camera.fieldOfView - fieldOfView)
                    <= GachaReadinessPositionTolerance;
        }

        private void HandleGachaNativeHybridCaseCrossedPackLip()
        {
            if (activeGachaRevealDirector != null
                && activeGachaRevealDirector.IsShippingChoreography)
            {
                // Shipping emerge: the native Pack drops once the case has
                // cleared the mouth. No isolation trace exists on this path.
                if (string.IsNullOrEmpty(activeGachaRequestId)
                    || activeGachaNativeHybridLipPublished)
                {
                    return;
                }
                activeGachaNativeHybridLipPublished = true;
                Gacha.GachaPresentationNativeBridge.PublishPhase(
                    activeGachaRequestId,
                    "case-crossing-pack-lip");
                return;
            }
            PublishGachaNativeHybridCaseCrossing();
        }

        /// <summary>
        /// The front face lands: the reveal burst goes through the semantic
        /// Haptic pipeline, scaled by rarity, and the phase is published so
        /// the native layer can time its own reveal-side UI.
        /// </summary>
        private void HandleGachaShippingFrontRevealed()
        {
            if (activeGachaRevealDirector == null
                || string.IsNullOrEmpty(activeGachaRequestId))
            {
                return;
            }
            // The native motes fade with the stage light-up (R053).
            Gacha.GachaPresentationNativeBridge.PublishPhase(
                activeGachaRequestId,
                "front-revealed");
            Gacha.GachaTransactionResult transaction =
                GachaInventory.QueryTransaction(activeGachaRequestId);
            Gacha.GachaRarity rarity = transaction.Success
                && transaction.Receipt.Rows.Count == 1
                    ? transaction.Receipt.Rows[0].Outcome.Rarity
                    : Gacha.GachaRarity.Standard;
            Gacha.GachaRevealRarityStyle style =
                Gacha.GachaRevealRarityStyle.For(rarity);
            if (rarity == Gacha.GachaRarity.Heirloom)
            {
                FidgetHapticRouter.Emit(FidgetSemanticEvent.BadgeUnlocked, 1f);
            }
            else
            {
                FidgetHapticRouter.Emit(FidgetSemanticEvent.Pop, style.HapticSignal);
            }
            Gacha.GachaPresentationNativeBridge.PublishPhase(
                activeGachaRequestId,
                "front-revealed");
        }

        private void PublishGachaNativeHybridCaseCrossing()
        {
            if (activeGachaRevealDirector == null
                || !activeGachaRevealDirector.IsNativeHybridCandidate
                || string.IsNullOrEmpty(activeGachaRequestId)
                || activeGachaNativeHybridLipPublished)
            {
                return;
            }
            activeGachaNativeHybridLipPublished = true;
            MaintainActiveGachaNativeHybridIsolation();
            bool ownershipValid = TryValidateGachaRevealOwnership(
                activeGachaRequestId,
                out string failureReason);
            PublishGachaNativeHybridTrace(
                "F3",
                activeGachaRequestId,
                ownershipValid,
                ownershipValid);
            Gacha.GachaPresentationNativeBridge.PublishPhase(
                activeGachaRequestId,
                "case-crossing-pack-lip");
        }

        private void HandleGachaShippingRevealCompleted()
        {
            if (activeGachaRevealDirector == null
                || string.IsNullOrEmpty(activeGachaRequestId))
            {
                return;
            }
            Gacha.GachaTransactionResult result =
                GachaInventory.MarkRevealReady(activeGachaRequestId);
            if (!result.Success)
            {
                Gacha.GachaPresentationNativeBridge.PublishPhase(
                    activeGachaRequestId,
                    "reveal-state-rejected:" + result.FailureReason);
                return;
            }
            Gacha.GachaPresentationNativeBridge.PublishPhase(
                activeGachaRequestId,
                "complete");
            MaintainActiveGachaNativeHybridIsolation();
            bool ownershipValid = TryValidateGachaRevealOwnership(
                activeGachaRequestId,
                out string failureReason);
            PublishGachaNativeHybridTrace(
                "F4",
                activeGachaRequestId,
                ownershipValid,
                ownershipValid);
            PublishGachaState(Gacha.GachaNativeBridge.ReceiptPayload(
                result.Receipt,
                activeGachaRequestId));
        }

        private void AcquireGachaCamera()
        {
            if (displayCaseCamera != null)
            {
                // Already staged (the storefront entered the gacha stage at
                // Pack selection); keep the saved restore pose.
                return;
            }
            displayCaseCamera = Camera.main;
            if (displayCaseCamera == null)
            {
                throw new MissingReferenceException(
                    "Shipping gacha reveal requires Camera.main.");
            }
            HideLibraryProductForGacha();
            displayCaseCameraPosition = displayCaseCamera.transform.position;
            displayCaseCameraRotation = displayCaseCamera.transform.rotation;
            displayCaseCameraFieldOfView = displayCaseCamera.fieldOfView;
            blueCameraWasEnabled = blueCamera != null && blueCamera.enabled;
            metalCameraWasEnabled = metalCamera != null && metalCamera.enabled;
            edcCameraWasEnabled = edcCamera != null && edcCamera.enabled;
            if (blueCamera != null)
            {
                blueCamera.enabled = false;
            }
            if (metalCamera != null)
            {
                metalCamera.enabled = false;
            }
            if (edcCamera != null)
            {
                edcCamera.enabled = false;
            }
            displayCaseCamera.transform.position =
                new Vector3(0f, 0.008f, -0.78f);
            displayCaseCamera.transform.rotation = Quaternion.LookRotation(
                new Vector3(0f, 0.008f, 0f)
                    - displayCaseCamera.transform.position,
                Vector3.up);
            displayCaseCamera.fieldOfView = 27f;
        }

        private static void CreateGachaRevealLighting(Transform parent)
        {
            CreateGachaDirectionalLight(
                parent,
                "GachaCaseKey",
                Quaternion.Euler(42f, -34f, 0f),
                new Color(0.96f, 0.97f, 1f),
                2.10f);
            CreateGachaDirectionalLight(
                parent,
                "GachaCaseFill",
                Quaternion.Euler(58f, 132f, 0f),
                new Color(0.72f, 0.80f, 0.90f),
                0.92f);
            CreateGachaDirectionalLight(
                parent,
                "GachaCaseRim",
                Quaternion.Euler(18f, 204f, 0f),
                new Color(0.92f, 0.95f, 1f),
                1.24f);
        }

        private static void CreateGachaDirectionalLight(
            Transform parent,
            string name,
            Quaternion rotation,
            Color color,
            float intensity)
        {
            var lightObject = new GameObject(name);
            lightObject.transform.SetParent(parent, false);
            lightObject.transform.rotation = rotation;
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = color;
            light.intensity = intensity;
            light.shadows = LightShadows.Soft;
        }

        private void DismissActiveGachaReveal(bool destroyPrize)
        {
            if (activeGachaReadiness != null)
            {
                StopCoroutine(activeGachaReadiness);
                activeGachaReadiness = null;
            }
            if (activeGachaSceneIsolation != null)
            {
                activeGachaSceneIsolation.Restore();
                activeGachaSceneIsolation = null;
            }
            if (activeGachaRevealDirector != null)
            {
                activeGachaRevealDirector.revealCompleted -=
                    HandleGachaShippingRevealCompleted;
                activeGachaRevealDirector.caseCrossedPackLip -=
                    HandleGachaNativeHybridCaseCrossedPackLip;
                activeGachaRevealDirector.frontRevealed -=
                    HandleGachaShippingFrontRevealed;
                activeGachaRevealDirector.Dismiss();
            }
            if (activeGachaRevealHost != null)
            {
                Destroy(activeGachaRevealHost);
            }
            if (destroyPrize && activeGachaPrize != null)
            {
                Destroy(activeGachaPrize);
            }
            else if (activeGachaPrize != null)
            {
                activeGachaPrize.SetActive(false);
                Destroy(activeGachaPrize);
            }
            activeGachaRevealDirector = null;
            activeGachaRevealHost = null;
            activeGachaPrize = null;
            activeGachaRequestId = string.Empty;
            activeGachaRevealStarted = false;
            activeGachaNativeHybridCandidate = false;
            activeGachaNativeHybridR029Candidate = false;
            activeGachaNativeHybridR030Candidate = false;
            activeGachaNativeHybridLipPublished = false;
            activeGachaNativeHybridR029CaptureCheckpoint = string.Empty;
            activeGachaNativeHybridR030CaptureCheckpoint = string.Empty;
            activeGachaNativeHybridSetupPublished = false;
            activeGachaNativeHybridSetupSucceeded = false;
            activeGachaNativeHybridSetupFailure = string.Empty;
            activeGachaApertureHoldRequestId = string.Empty;
            activeGachaApertureHeld = false;

            gachaStageFX?.Dispose();
            gachaStageFX = null;
            if (gachaStageHost != null)
            {
                Destroy(gachaStageHost);
                gachaStageHost = null;
            }
            RestoreGachaCamera();
        }

        /// <summary>
        /// The library toy sits at the origin, exactly where the case is
        /// staged, and the reveal camera looks at it edge-on: without this it
        /// shows up inside the case as a second, upright spinner.
        /// </summary>
        private void HideLibraryProductForGacha()
        {
            if (gachaHiddenProductRenderers.Count > 0)
            {
                return;
            }
            string modelId = ModelIdForScene(SceneManager.GetActiveScene().path);
            Transform root = DisplayCaseProductRoot(modelId);
            if (root == null)
            {
                return;
            }
            // Renderer-level only: the product root can also parent the main
            // camera and other scene services, so it must stay active. The
            // cave environment layers hang under that camera
            // (SpinnerEnvironmentPresenter); they are the reveal backdrop
            // and must keep rendering, so anything under a camera or the
            // environment presenter is skipped.
            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(false);
            for (int index = 0; index < renderers.Length; index++)
            {
                Renderer renderer = renderers[index];
                if (renderer == null || !renderer.enabled)
                {
                    continue;
                }
                if (renderer.GetComponentInParent<Camera>() != null
                    || renderer.GetComponentInParent<SpinnerEnvironmentPresenter>() != null)
                {
                    continue;
                }
                renderer.enabled = false;
                gachaHiddenProductRenderers.Add(renderer);
            }
        }

        private void RestoreLibraryProductAfterGacha()
        {
            for (int index = 0; index < gachaHiddenProductRenderers.Count; index++)
            {
                Renderer renderer = gachaHiddenProductRenderers[index];
                if (renderer != null)
                {
                    renderer.enabled = true;
                }
            }
            gachaHiddenProductRenderers.Clear();
        }

        private void RestoreGachaCamera()
        {
            RestoreLibraryProductAfterGacha();
            if (displayCaseCamera != null)
            {
                displayCaseCamera.transform.position = displayCaseCameraPosition;
                displayCaseCamera.transform.rotation = displayCaseCameraRotation;
                displayCaseCamera.fieldOfView = displayCaseCameraFieldOfView;
            }
            if (blueCamera != null)
            {
                blueCamera.enabled = blueCameraWasEnabled;
            }
            if (metalCamera != null)
            {
                metalCamera.enabled = metalCameraWasEnabled;
            }
            if (edcCamera != null)
            {
                edcCamera.enabled = edcCameraWasEnabled;
            }
            displayCaseCamera = null;
        }

        public void RedeemGachaShardsFromNativeUi(string prizeId)
        {
            GachaInventory.TryRedeemShards(prizeId, out string failureReason);
            PublishGachaState(string.IsNullOrEmpty(failureReason)
                ? "result\tok"
                : "result\t" + failureReason);
        }

        /// <summary>
        /// Payload: "tickets|N" or "coins|N". Coins may only be credited by
        /// the StoreKit-verified purchase flow; tickets come from rhythm and
        /// milestone rewards. Never grants XP or physics.
        /// </summary>
        public void CreditGachaFundsFromNativeUi(string payload)
        {
            string[] parts = (payload ?? string.Empty).Split('|');
            if (parts.Length != 2
                || !int.TryParse(
                    parts[1],
                    System.Globalization.NumberStyles.Integer,
                    CultureInfo.InvariantCulture,
                    out int amount)
                || amount <= 0)
            {
                return;
            }

            if (parts[0] == "coins")
            {
                GachaInventory.CreditCoins(amount);
            }
            else if (parts[0] == "tickets")
            {
                GachaInventory.CreditTickets(amount);
            }
            else
            {
                return;
            }

            PublishGachaState();
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

        private bool HasMotionTelemetry()
        {
            return HasRotarySpeedTelemetry()
                || edcSlider != null
                || fanCard != null;
        }

        private void PublishMotionTelemetryIfDue(float angularSpeedRadians)
        {
            if (libraryPreviewActive
                || !HasMotionTelemetry()
                || Time.unscaledTime - lastMotionTelemetryPublishTime
                    < SpinnerComboRules.HudUpdateIntervalSeconds)
            {
                return;
            }

            PublishMotionTelemetryNow(angularSpeedRadians);
        }

        private void PublishMotionTelemetryNow(float angularSpeedRadians)
        {
            bool available = !libraryPreviewActive && HasMotionTelemetry();
            ProductMotionTelemetryKind kind = ProductMotionTelemetryKind.Rotary;
            float normalizedSpeed = 0f;
            float motionRate = 0f;
            float normalizedIntensity = combo.Snapshot.NormalizedIntensity;
            float normalizedFrequency = combo.Snapshot.NormalizedFrequency;
            if (available && edcSlider != null)
            {
                kind = ProductMotionTelemetryKind.LinearPush;
                normalizedSpeed = edcSlider.GestureSpeedNormalized;
                motionRate = edcSlider.GestureSpeedMillimetersPerSecond;
                normalizedIntensity = edcSlider.GestureIntensityNormalized;
                normalizedFrequency = edcSlider.GestureFrequencyNormalized;
            }
            else if (available && fanCard != null)
            {
                kind = ProductMotionTelemetryKind.FanCard;
                normalizedSpeed = fanCard.GestureSpeedNormalized;
                motionRate = fanCard.GestureAngularSpeedDegreesPerSecond;
                normalizedIntensity = fanCard.GestureIntensityNormalized;
                normalizedFrequency = fanCard.GestureFrequencyNormalized;
            }
            else if (available)
            {
                normalizedSpeed = SpinnerComboRules.NormalizeSpeed(
                    angularSpeedRadians);
                motionRate = Mathf.Abs(angularSpeedRadians);
            }
            speedDashboardBand = available
                ? SpinnerSpeedDashboardRules.ResolveBand(
                    normalizedSpeed,
                    speedDashboardBand)
                : SpinnerSpeedBand.Calm;
            ProductMotionTelemetryNativeBridge.Publish(
                available,
                kind,
                normalizedSpeed,
                motionRate,
                speedDashboardBand,
                normalizedIntensity,
                normalizedFrequency);
            lastMotionTelemetryPublishTime = Time.unscaledTime;
        }

        private void ResetMotionTelemetry(bool available)
        {
            speedDashboardBand = SpinnerSpeedBand.Calm;
            lastMotionTelemetryPublishTime = float.NegativeInfinity;
            ProductMotionTelemetryNativeBridge.Publish(
                available,
                edcSlider != null
                    ? ProductMotionTelemetryKind.LinearPush
                    : fanCard != null
                        ? ProductMotionTelemetryKind.FanCard
                        : ProductMotionTelemetryKind.Rotary,
                0f,
                0f,
                SpinnerSpeedBand.Calm,
                0f,
                0f);
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
            // Browsing keeps parallax alive but the phone must not spin, step,
            // or tick a mechanism until the toy is the active detail page.
            bool mechanismDrive = !libraryPreviewActive;
            blueMotion?.SetMechanismDriveEnabled(mechanismDrive);
            metalMotion?.SetMechanismDriveEnabled(mechanismDrive);
            edcMotion?.SetMechanismDriveEnabled(mechanismDrive);
            blueCamera?.SetLibraryPreviewActive(libraryPreviewActive);
            metalCamera?.SetLibraryPreviewActive(libraryPreviewActive);
            // The fan-card Library pose is a visual-only two-step opening.
            // Apply it before framing so live bounds are centered on the
            // visible fan, while the underlying magnetic detent stays intact.
            fanCard?.SetLibraryPreviewActive(libraryPreviewActive);
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
            if (blueCamera != null)
                blueCamera.SetAppearanceActivationScale(apparentScale);
            if (metalCamera != null)
                metalCamera.SetAppearanceActivationScale(apparentScale);
            if (edcCamera != null)
                edcCamera.SetAppearanceActivationScale(apparentScale);
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
