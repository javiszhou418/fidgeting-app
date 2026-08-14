using FidgetingApp.EDC;
using FidgetingApp.DisplayCase;
using UnityEngine;

namespace FidgetingApp.FanCard
{
    /// <summary>
    /// The shared EDC framer defaults to a 36 x 24 mm physical camera with
    /// Horizontal gate fit. That is correct for the long fifth slider, but a
    /// portrait card rendered into a portrait target can inherit the sensor
    /// gate a second time and appear horizontally compressed. The fan card
    /// uses an ordinary perspective projection with the same nominal 50 mm
    /// vertical field of view, preserving millimetre proportions on screen.
    /// </summary>
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Camera))]
    [DefaultExecutionOrder(100)]
    public sealed class FanCardCameraProjectionGuard : MonoBehaviour,
        IPremiumDisplayCaseCameraStateAuthor
    {
        public const float ReferenceFieldOfViewDegrees = 26.991f;
        private bool displayCaseCameraControlSuppressed;

        public void ApplyNow()
        {
            if (displayCaseCameraControlSuppressed)
            {
                return;
            }

            Camera targetCamera = GetComponent<Camera>();
            EdcPortraitCameraFramer framer =
                GetComponent<EdcPortraitCameraFramer>();
            if (framer != null)
            {
                framer.ConfigureProjection(
                    false,
                    ReferenceFieldOfViewDegrees);
                return;
            }

            targetCamera.usePhysicalProperties = false;
            targetCamera.fieldOfView = ReferenceFieldOfViewDegrees;
            targetCamera.ResetProjectionMatrix();
        }

        private void OnEnable()
        {
            ApplyNow();
        }

        public void SetDisplayCaseCameraControlSuppressed(bool suppressed)
        {
            displayCaseCameraControlSuppressed = suppressed;
        }
    }
}
