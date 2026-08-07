using ThreeBladeEDC.Interaction;
using UnityEngine;
using UnityEngine.UI;

namespace ThreeBladeEDC.Presentation
{
    [DisallowMultipleComponent]
    public sealed class MobileViewerUI : MonoBehaviour
    {
        [SerializeField] private RotorRigidbodyController rotor;
        [SerializeField] private ExplodedViewController explodedView;
        [SerializeField] private OrbitPresentationCamera orbitCamera;
        [SerializeField] private Button explodeButton;
        [SerializeField] private Button resetButton;
        [SerializeField] private Button motorButton;
        [SerializeField] private Button viewButton;
        [SerializeField] private Text explodeLabel;
        [SerializeField] private Text motorLabel;
        [SerializeField] private Text rpmLabel;

        private bool _motorEnabled;
        private bool _bound;

        public bool MotorEnabled => _motorEnabled;

        public void Configure(
            RotorRigidbodyController rotorController,
            ExplodedViewController exploded,
            OrbitPresentationCamera orbit,
            Button explode,
            Button reset,
            Button motor,
            Button view,
            Text explodeText,
            Text motorText,
            Text rpmText)
        {
            rotor = rotorController;
            explodedView = exploded;
            orbitCamera = orbit;
            explodeButton = explode;
            resetButton = reset;
            motorButton = motor;
            viewButton = view;
            explodeLabel = explodeText;
            motorLabel = motorText;
            rpmLabel = rpmText;
            Bind();
            RefreshLabels();
        }

        private void Awake()
        {
            Bind();
            RefreshLabels();
        }

        private void Update()
        {
            if (rpmLabel != null && rotor != null)
            {
                float rpm = Mathf.Abs(rotor.AngularSpeedRadians) * 9.549296f;
                rpmLabel.text = $"{rpm:0} RPM";
            }
        }

        private void OnApplicationPause(bool paused)
        {
            if (paused)
            {
                _motorEnabled = false;
                rotor?.SetMotorActive(false);
                RefreshLabels();
            }
        }

        public void ToggleExploded()
        {
            if (explodedView == null)
            {
                return;
            }
            explodedView.Toggle();
            RefreshLabels();
        }

        public void ResetPresentation()
        {
            _motorEnabled = false;
            rotor?.SetMotorActive(false);
            explodedView?.SetExploded(false);
            rotor?.ResetRotor();
            orbitCamera?.ResetHero();
            RefreshLabels();
        }

        public void ToggleMotor()
        {
            _motorEnabled = !_motorEnabled;
            rotor?.SetMotorActive(_motorEnabled);
            RefreshLabels();
        }

        public void CycleView()
        {
            orbitCamera?.CyclePreset();
        }

        private void Bind()
        {
            if (_bound)
            {
                return;
            }

            explodeButton?.onClick.AddListener(ToggleExploded);
            resetButton?.onClick.AddListener(ResetPresentation);
            motorButton?.onClick.AddListener(ToggleMotor);
            viewButton?.onClick.AddListener(CycleView);
            _bound = true;
        }

        private void RefreshLabels()
        {
            if (explodeLabel != null)
            {
                explodeLabel.text = explodedView != null && explodedView.IsExploded
                    ? "ASSEMBLE"
                    : "EXPLODE";
            }
            if (motorLabel != null)
            {
                motorLabel.text = _motorEnabled ? "MOTOR ON" : "MOTOR";
            }
        }
    }
}
