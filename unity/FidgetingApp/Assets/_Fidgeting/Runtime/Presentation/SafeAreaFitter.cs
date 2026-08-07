using UnityEngine;

namespace ThreeBladeEDC.Presentation
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(RectTransform))]
    public sealed class SafeAreaFitter : MonoBehaviour
    {
        private Rect _lastSafeArea;
        private Vector2Int _lastScreenSize;

        private void OnEnable()
        {
            Apply();
        }

        private void Update()
        {
            if (_lastSafeArea != Screen.safeArea
                || _lastScreenSize.x != Screen.width
                || _lastScreenSize.y != Screen.height)
            {
                Apply();
            }
        }

        public void Apply()
        {
            if (Screen.width <= 0 || Screen.height <= 0)
            {
                return;
            }

            Rect safe = Screen.safeArea;
            RectTransform rectTransform = (RectTransform)transform;
            rectTransform.anchorMin = new Vector2(
                safe.xMin / Screen.width,
                safe.yMin / Screen.height);
            rectTransform.anchorMax = new Vector2(
                safe.xMax / Screen.width,
                safe.yMax / Screen.height);
            rectTransform.offsetMin = Vector2.zero;
            rectTransform.offsetMax = Vector2.zero;
            _lastSafeArea = safe;
            _lastScreenSize = new Vector2Int(Screen.width, Screen.height);
        }
    }
}
