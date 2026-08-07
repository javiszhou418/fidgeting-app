using System.Collections.Generic;
using ThreeBladeEDC.Interaction;
using UnityEngine;

namespace ThreeBladeEDC.Presentation
{
    /// <summary>
    /// Keeps multiple spinner appearances inside one app while sharing the
    /// same Rigidbody and input controller.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class SpinnerVariantSwitcher : MonoBehaviour
    {
        private const string RuntimeVariantName = "VariantGraphite";

        [SerializeField] private RotorRigidbodyController rotor;
        [SerializeField, Range(0, 1)] private int selectedVariant;

        private readonly List<GameObject> _classicParts = new List<GameObject>();
        private GameObject _graphiteVariant;
        private Material _graphiteMaterial;
        private Material _accentMaterial;
        private Texture2D _buttonTexture;
        private Texture2D _buttonPressedTexture;
        private GUIStyle _buttonStyle;

        public void Configure(RotorRigidbodyController controller)
        {
            rotor = controller;
            if (Application.isPlaying && isActiveAndEnabled)
            {
                InitializePresentation();
            }
        }

        private void Awake()
        {
            Application.targetFrameRate = 60;
            Screen.sleepTimeout = SleepTimeout.NeverSleep;
            InitializePresentation();
        }

        private void Start()
        {
            InitializePresentation();
        }

        private void InitializePresentation()
        {
            if (rotor == null)
            {
                rotor = FindAnyObjectByType<RotorRigidbodyController>();
            }

            if (rotor == null)
            {
                return;
            }

            ConfigureBlackStage();
            CollectClassicParts();
            if (_graphiteVariant == null)
            {
                Transform existing = rotor.transform.Find(RuntimeVariantName);
                _graphiteVariant = existing != null
                    ? existing.gameObject
                    : BuildGraphiteVariant(rotor.transform);
            }

            SetVariant(selectedVariant, false);
        }

        private static void ConfigureBlackStage()
        {
            Camera mainCamera = Camera.main;
            if (mainCamera != null)
            {
                mainCamera.clearFlags = CameraClearFlags.SolidColor;
                mainCamera.backgroundColor = Color.black;
            }

            GameObject floor = GameObject.Find("StudioFloor");
            if (floor != null)
            {
                floor.SetActive(false);
            }
        }

        private void CollectClassicParts()
        {
            if (_classicParts.Count > 0)
            {
                return;
            }

            AddClassicPart("RotorCore");
            AddClassicPart("BearingOuterRace");
            AddClassicPart("Blade_00");
            AddClassicPart("Blade_01");
            AddClassicPart("Blade_02");
        }

        private void AddClassicPart(string childName)
        {
            Transform part = rotor.transform.Find(childName);
            if (part != null)
            {
                _classicParts.Add(part.gameObject);
            }
        }

        private GameObject BuildGraphiteVariant(Transform parent)
        {
            CreateMaterials();

            GameObject variant = new GameObject(RuntimeVariantName);
            variant.transform.SetParent(parent, false);

            CreatePrimitive(
                PrimitiveType.Cylinder,
                "GraphiteCore",
                variant.transform,
                Vector3.zero,
                Quaternion.identity,
                new Vector3(0.052f, 0.0042f, 0.052f),
                _graphiteMaterial);

            for (int i = 0; i < 3; i++)
            {
                float angle = i * 120f;
                Quaternion rotation = Quaternion.Euler(0f, angle, 0f);

                CreatePrimitive(
                    PrimitiveType.Cube,
                    $"Arm_{i:00}",
                    variant.transform,
                    rotation * new Vector3(0f, 0f, 0.029f),
                    rotation,
                    new Vector3(0.020f, 0.0072f, 0.046f),
                    _graphiteMaterial);

                Vector3 lobePosition = rotation * new Vector3(0f, 0f, 0.052f);
                CreatePrimitive(
                    PrimitiveType.Cylinder,
                    $"Lobe_{i:00}",
                    variant.transform,
                    lobePosition,
                    Quaternion.identity,
                    new Vector3(0.031f, 0.0045f, 0.031f),
                    _graphiteMaterial);
                CreatePrimitive(
                    PrimitiveType.Cylinder,
                    $"Accent_{i:00}",
                    variant.transform,
                    lobePosition + Vector3.up * 0.0047f,
                    Quaternion.identity,
                    new Vector3(0.018f, 0.0007f, 0.018f),
                    _accentMaterial);
            }

            return variant;
        }

        private void CreateMaterials()
        {
            if (_graphiteMaterial != null && _accentMaterial != null)
            {
                return;
            }

            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null)
            {
                shader = Shader.Find("Standard");
            }

            _graphiteMaterial = new Material(shader)
            {
                name = "M_RuntimeGraphite",
                color = new Color(0.055f, 0.065f, 0.075f, 1f)
            };
            _accentMaterial = new Material(shader)
            {
                name = "M_RuntimeCyanAccent",
                color = new Color(0.05f, 0.72f, 0.86f, 1f)
            };

            SetMaterialProperties(_graphiteMaterial, 0.82f, 0.62f);
            SetMaterialProperties(_accentMaterial, 0.72f, 0.8f);
        }

        private static void SetMaterialProperties(
            Material material,
            float metallic,
            float smoothness)
        {
            if (material.HasProperty("_BaseColor"))
            {
                material.SetColor("_BaseColor", material.color);
            }
            if (material.HasProperty("_Metallic"))
            {
                material.SetFloat("_Metallic", metallic);
            }
            if (material.HasProperty("_Smoothness"))
            {
                material.SetFloat("_Smoothness", smoothness);
            }
        }

        private static GameObject CreatePrimitive(
            PrimitiveType primitiveType,
            string objectName,
            Transform parent,
            Vector3 localPosition,
            Quaternion localRotation,
            Vector3 localScale,
            Material material)
        {
            GameObject instance = GameObject.CreatePrimitive(primitiveType);
            instance.name = objectName;
            instance.transform.SetParent(parent, false);
            instance.transform.localPosition = localPosition;
            instance.transform.localRotation = localRotation;
            instance.transform.localScale = localScale;

            Collider collider = instance.GetComponent<Collider>();
            if (collider != null)
            {
                collider.enabled = false;
                Destroy(collider);
            }

            Renderer renderer = instance.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.sharedMaterial = material;
            }

            return instance;
        }

        private void SetVariant(int index, bool smoothStop)
        {
            selectedVariant = Mathf.Clamp(index, 0, 1);
            for (int i = 0; i < _classicParts.Count; i++)
            {
                if (_classicParts[i] != null)
                {
                    _classicParts[i].SetActive(selectedVariant == 0);
                }
            }

            if (_graphiteVariant != null)
            {
                _graphiteVariant.SetActive(selectedVariant == 1);
            }

            if (smoothStop && rotor != null)
            {
                rotor.SmoothStop(0.2f);
            }
        }

        private void OnGUI()
        {
            if (rotor == null)
            {
                return;
            }

            EnsureGuiStyle();
            Rect buttonRect = GetControlRect();

            string label = selectedVariant == 0
                ? "MODEL 01  ·  CLASSIC   ›"
                : "MODEL 02  ·  GRAPHITE   ›";
            if (GUI.Button(buttonRect, label, _buttonStyle))
            {
                SetVariant(1 - selectedVariant, true);
            }
        }

        public static bool IsScreenPointOverControls(Vector2 screenPoint)
        {
            Vector2 guiPoint = new Vector2(
                screenPoint.x,
                Screen.height - screenPoint.y);
            return GetControlRect().Contains(guiPoint);
        }

        private static Rect GetControlRect()
        {
            Rect safeArea = Screen.safeArea;
            float width = Mathf.Clamp(Screen.width * 0.28f, 230f, 340f);
            float height = Mathf.Clamp(Screen.height * 0.035f, 68f, 96f);
            float margin = 24f;
            float safeTop = Screen.height - safeArea.yMax;
            return new Rect(
                safeArea.xMax - width - margin,
                safeTop + margin,
                width,
                height);
        }

        private void EnsureGuiStyle()
        {
            if (_buttonStyle != null)
            {
                return;
            }

            _buttonTexture = MakeTexture(new Color(0.015f, 0.02f, 0.025f, 0.92f));
            _buttonPressedTexture = MakeTexture(new Color(0.03f, 0.36f, 0.43f, 0.96f));
            _buttonStyle = new GUIStyle(GUI.skin.button)
            {
                alignment = TextAnchor.MiddleCenter,
                fontSize = Mathf.Clamp(Mathf.RoundToInt(Screen.width * 0.016f), 16, 24),
                fontStyle = FontStyle.Bold,
                padding = new RectOffset(12, 12, 8, 8)
            };
            _buttonStyle.normal.background = _buttonTexture;
            _buttonStyle.hover.background = _buttonTexture;
            _buttonStyle.active.background = _buttonPressedTexture;
            _buttonStyle.normal.textColor = new Color(0.86f, 0.95f, 0.97f, 1f);
            _buttonStyle.hover.textColor = Color.white;
            _buttonStyle.active.textColor = Color.white;
        }

        private static Texture2D MakeTexture(Color color)
        {
            Texture2D texture = new Texture2D(1, 1, TextureFormat.RGBA32, false)
            {
                hideFlags = HideFlags.HideAndDontSave
            };
            texture.SetPixel(0, 0, color);
            texture.Apply(false, true);
            return texture;
        }

        private void OnDestroy()
        {
            if (_graphiteMaterial != null)
            {
                Destroy(_graphiteMaterial);
            }
            if (_accentMaterial != null)
            {
                Destroy(_accentMaterial);
            }
            if (_buttonTexture != null)
            {
                Destroy(_buttonTexture);
            }
            if (_buttonPressedTexture != null)
            {
                Destroy(_buttonPressedTexture);
            }
        }
    }
}
