using UnityEngine;

namespace ThreeBladeEDC.Presentation
{
    [DisallowMultipleComponent]
    public sealed class PresentationOverlay : MonoBehaviour
    {
        [SerializeField] private Rigidbody rotorBody;
        [SerializeField] private string title = "THREE-BLADE EDC / CONCEPT VISUALIZATION";
        [SerializeField] private bool showDiagnosticsInPlayer;

        public void Configure(Rigidbody rotor)
        {
            rotorBody = rotor;
        }

        private void OnGUI()
        {
            if (!Application.isEditor && !showDiagnosticsInPlayer)
            {
                return;
            }

            float rpm = rotorBody == null
                ? 0f
                : Vector3.Dot(rotorBody.angularVelocity, Vector3.up) * 9.549296f;

            GUI.color = new Color(0.94f, 0.96f, 0.98f, 0.94f);
            GUI.Label(new Rect(28f, 22f, 720f, 28f), title);
            GUI.color = new Color(1f, 0.48f, 0.16f, 0.95f);
            GUI.Label(new Rect(28f, 50f, 420f, 24f), $"ROTOR  {rpm:0} RPM");
            GUI.color = new Color(0.72f, 0.78f, 0.84f, 0.92f);
            GUI.Label(
                new Rect(28f, Screen.height - 54f, 860f, 36f),
                "左键拖拽/甩动 · Space 电机 · E 拆解 · R 复位 · V 视角 · 右键环绕 · 滚轮缩放");
        }
    }
}
