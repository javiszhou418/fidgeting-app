using CodexUnityLab;
using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    /// <summary>
    /// Presentation-only consumer of the app's canonical Core Motion stream.
    /// It never starts or stops the native sensor, so showing the case cannot
    /// steal lifecycle ownership from the active product scene.
    /// </summary>
    [DisallowMultipleComponent]
    [RequireComponent(typeof(PremiumDisplayCase))]
    public sealed class PremiumDisplayCaseGyroAdapter : MonoBehaviour
    {
        [SerializeField, Min(1f)] private float caseFullScaleAngleDegrees = 15f;
        [SerializeField, Range(0.25f, 1f)] private float verticalScale = 0.72f;
        [SerializeField] private bool usePointerFallbackInEditor = true;

        private PremiumDisplayCase displayCase;

        private void Awake()
        {
            displayCase = GetComponent<PremiumDisplayCase>();
        }

        private void OnEnable()
        {
            displayCase ??= GetComponent<PremiumDisplayCase>();
        }

        private void OnDisable()
        {
            displayCase?.SetParallaxInput(Vector2.zero);
        }

        private void Update()
        {
            if (displayCase == null)
            {
                return;
            }
            if (SceneParallaxInput.TryGetRecent(
                out Vector2 publishedTilt,
                out float sourceFullScaleAngleDegrees,
                4))
            {
                displayCase.SetParallaxInput(SceneParallaxInput.MapToParallax(
                    publishedTilt,
                    sourceFullScaleAngleDegrees,
                    caseFullScaleAngleDegrees,
                    verticalScale));
                return;
            }

#if UNITY_EDITOR
            if (usePointerFallbackInEditor && Camera.main != null)
            {
                Vector2 pointer = SceneParallaxInput.NormalizePointer(
                    Input.mousePosition,
                    new Vector2(Screen.width, Screen.height));
                displayCase.SetParallaxInput(new Vector2(
                    pointer.x,
                    pointer.y * verticalScale));
                return;
            }
#endif
            displayCase.SetParallaxInput(Vector2.zero);
        }
    }
}
