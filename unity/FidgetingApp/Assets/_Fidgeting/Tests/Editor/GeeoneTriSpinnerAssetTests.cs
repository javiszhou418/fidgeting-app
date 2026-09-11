using System.Linq;
using NUnit.Framework;
using ThreeBladeEDC.EditorTools;
using ThreeBladeEDC.Interaction;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace ThreeBladeEDC.Tests.Editor
{
    /// <summary>
    /// GEEONE 龙鳞三叶 (ModelPipeline metal-three-blade, Gate 10 rev-002 export): the metal scene must show the
    /// two-part structure the user approved on 2026-09-08 13:55 — Rotor_Body spins, Cap_Top / Cap_Bottom / Hub_Core
    /// stay with the fingers — at 85 mm, with no DragonScale or procedural metal visual left visible.
    /// </summary>
    public sealed class GeeoneTriSpinnerAssetTests
    {
        private const string VisualModelPath = ThreeBladeSceneBuilder.GeeoneModelPath;
        private const string CollisionModelPath =
            "Assets/_Fidgeting/Models/GeeoneTriSpinner/GeeoneTriSpinner_Collision.fbx";
        private const string DeliveryScenePath =
            "Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity";
        private const string DragonScaleRollbackPath =
            "Assets/_Fidgeting/Models/BlenderDragonScale/DragonScaleEDC.fbx";

        // 2R = 85 mm (user-authorized-provisional). Three blades at 120°: AABB width = 2R sin 60° = 73.6 mm.
        private const float RadiusM = 0.0425f;
        private const float AabbWidthM = 0.07361f;
        private const float RotorThicknessM = 0.01007f;   // 0.17 R + hard-cut crest (Gate 06 rev-008)
        private const float HubCoreDiameterM = 0.03485f;  // 0.41 R static hub core
        private const float CapDiameterM = 0.04111f;      // 0.485 R (dish + crown + skirt rim)

        [Test]
        public void VisualAsset_HasTwoKinematicGroupsAtRealScale()
        {
            GameObject asset = AssetDatabase.LoadAssetAtPath<GameObject>(VisualModelPath);
            Assert.That(asset, Is.Not.Null, $"Missing model: {VisualModelPath}");
            Assert.That(
                AssetDatabase.LoadAssetAtPath<GameObject>(CollisionModelPath),
                Is.Not.Null,
                $"Missing collision model: {CollisionModelPath}");

            GameObject instance = Object.Instantiate(asset);
            try
            {
                Transform[] transforms = instance.GetComponentsInChildren<Transform>(true);
                Transform rotorRoot = Require(transforms, "Rotor_Root");
                Transform fixedRoot = Require(transforms, "Fixed_Root");
                Transform rotorBody = Require(transforms, "Rotor_Body");
                Transform capTop = Require(transforms, "Cap_Top");
                Transform capBottom = Require(transforms, "Cap_Bottom");
                Transform hubCore = Require(transforms, "Hub_Core");

                Assert.That(rotorBody.parent, Is.SameAs(rotorRoot), "The rotor is the only rotating part.");
                Assert.That(capTop.parent, Is.SameAs(fixedRoot));
                Assert.That(capBottom.parent, Is.SameAs(fixedRoot));
                Assert.That(hubCore.parent, Is.SameAs(fixedRoot), "The hub core is static: it is held by the caps.");
                Assert.That(
                    instance.GetComponentsInChildren<MeshFilter>(true).Length,
                    Is.EqualTo(4),
                    "Exactly four shipping meshes: rotor, two caps, hub core.");
                Assert.That(
                    transforms.Any(t => t.name.Contains("Hub_Seat")),
                    Is.False,
                    "The rejected one-piece hub seats (rev-005..007) must not come back.");

                // World-space renderer bounds: the FBX keeps the mesh data in Blender axes and carries the
                // Z-up -> Y-up conversion on the imported node transforms, so mesh-local bounds are not Y-up.
                Bounds rotor = rotorBody.GetComponent<MeshRenderer>().bounds;
                Assert.That(rotor.size.x, Is.EqualTo(AabbWidthM).Within(0.001f), "rotor AABB width (2R sin 60°)");
                Assert.That(rotor.size.y, Is.EqualTo(RotorThicknessM).Within(0.0007f), "Blender Z (spin axis) must be Unity Y");
                Assert.That(rotor.extents.magnitude, Is.GreaterThan(RadiusM * 0.99f), "85 mm circumscribed diameter");

                Bounds hub = hubCore.GetComponent<MeshRenderer>().bounds;
                Assert.That(hub.size.x, Is.EqualTo(HubCoreDiameterM).Within(0.0007f));
                Assert.That(hub.size.z, Is.EqualTo(HubCoreDiameterM).Within(0.0007f));
                Assert.That(hub.size.y, Is.GreaterThan(rotor.size.y), "the hub core runs through the rotor from cap to cap");
                Bounds cap = capTop.GetComponent<MeshRenderer>().bounds;
                Assert.That(Mathf.Max(cap.size.x, cap.size.z), Is.EqualTo(CapDiameterM).Within(0.0007f), "cap rim = 0.485 R");
                Assert.That(Mathf.Min(cap.size.x, cap.size.z), Is.GreaterThan(hub.size.x), "cap radius > hub core radius (user 18:33)");
                Assert.That(cap.min.y, Is.GreaterThan(rotor.max.y), "the top cap floats above the rotor face (clearance)");
            }
            finally
            {
                Object.DestroyImmediate(instance);
            }
        }

        [Test]
        public void DeliveryScene_UsesGeeoneTwoPartVisualAndKeepsExplodedOrder()
        {
            SceneSetup[] previousSetup = EditorSceneManager.GetSceneManagerSetup();
            try
            {
                Scene scene = EditorSceneManager.OpenScene(
                    DeliveryScenePath,
                    OpenSceneMode.Single);
                Transform root = scene.GetRootGameObjects()
                    .Single(candidate => candidate.name == "ThreeBladeEDC_Root")
                    .transform;

                Transform rotor = RequirePath(root, "RotorDynamic");
                Transform rotorBody = RequirePath(rotor, "Rotor_Root/Rotor_Body");
                var bodyRenderer = rotorBody.GetComponent<MeshRenderer>();
                Assert.That(bodyRenderer, Is.Not.Null);
                Assert.That(bodyRenderer.enabled, Is.True);
                Assert.That(
                    AssetDatabase.GetAssetPath(rotorBody.GetComponent<MeshFilter>().sharedMesh),
                    Is.EqualTo(VisualModelPath));
                Assert.That(bodyRenderer.sharedMaterial.name, Is.EqualTo("M_GeeoneSatin"));

                Transform capTop = RequirePath(root, "HubStatic/TopCap/Cap_Top");
                Transform capBottom = RequirePath(root, "HubStatic/BottomCap/Cap_Bottom");
                Transform hubCore = RequirePath(root, "HubStatic/Hub_Core");
                Assert.That(capTop.GetComponent<MeshRenderer>().enabled, Is.True);
                Assert.That(capBottom.GetComponent<MeshRenderer>().enabled, Is.True);
                Assert.That(hubCore.GetComponent<MeshRenderer>().enabled, Is.True);
                Assert.That(hubCore.GetComponent<MeshRenderer>().sharedMaterial.name, Is.EqualTo("M_GeeoneHubDark"));
                CollectionAssert.Contains(
                    capTop.GetComponent<MeshRenderer>().sharedMaterials.Select(material => material.name).ToArray(),
                    "M_GeeoneDiscTurned");
                Assert.That(
                    capTop.IsChildOf(rotor),
                    Is.False,
                    "Caps must not spin with the rotor.");
                Assert.That(
                    hubCore.IsChildOf(rotor),
                    Is.False,
                    "The hub core must not spin with the rotor.");

                Assert.That(
                    RequirePath(rotor, "ThreeBladeFrame").GetComponent<MeshRenderer>().enabled,
                    Is.False,
                    "The superseded procedural visual must stay hidden.");
                Assert.That(
                    RequirePath(root, "HubStatic/TopCap").GetComponent<MeshRenderer>().enabled,
                    Is.False,
                    "The procedural cap is hidden under the imported one.");
                Assert.That(
                    RequirePath(root, "BearingVisual/BallCage/BearingBalls").GetComponent<MeshRenderer>().enabled,
                    Is.False,
                    "No bearing is visible on the GEEONE design (D09).");
                Assert.That(
                    root.GetComponentsInChildren<Transform>(true).Any(t => t.name == "RotorBody_OnePiece" || t.name == "FingerCapTop_BrushedFace"),
                    Is.False,
                    "The DragonScale rollback visual must be gone from the metal scene.");
                CollectionAssert.DoesNotContain(
                    AssetDatabase.GetDependencies(DeliveryScenePath, true),
                    DragonScaleRollbackPath);

                ExplodedViewController exploded = root.GetComponent<ExplodedViewController>();
                Assert.That(exploded, Is.Not.Null);
                SerializedProperty parts = new SerializedObject(exploded).FindProperty("parts");
                Assert.That(parts.arraySize, Is.EqualTo(6));
                string[] expectedNames = { "TopCap", "TopWasher", "BearingVisual", "RotorDynamic", "BottomWasher", "BottomCap" };
                for (int index = 0; index < expectedNames.Length; index++)
                {
                    Transform partTransform = parts.GetArrayElementAtIndex(index)
                        .FindPropertyRelative("transform").objectReferenceValue as Transform;
                    Assert.That(partTransform, Is.Not.Null);
                    Assert.That(partTransform.name, Is.EqualTo(expectedNames[index]));
                }

                Rigidbody body = rotor.GetComponent<Rigidbody>();
                Assert.That(body, Is.Not.Null);
                Assert.That(body.angularVelocity, Is.EqualTo(Vector3.zero), "The rotor starts at zero angular velocity.");
                Assert.That(rotor.GetComponent<RotorRigidbodyController>(), Is.Not.Null);

                OrbitPresentationCamera orbit = Object.FindAnyObjectByType<OrbitPresentationCamera>();
                Assert.That(orbit, Is.Not.Null);
                Assert.That(orbit.FocusTarget, Is.SameAs(capTop), "The camera frames the visible top cap.");
            }
            finally
            {
                if (previousSetup != null && previousSetup.Any(setup => setup.isLoaded))
                {
                    EditorSceneManager.RestoreSceneManagerSetup(previousSetup);
                }
                else
                {
                    EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                }
            }
        }

        private static Transform Require(Transform[] transforms, string name)
        {
            Transform match = transforms.FirstOrDefault(t => t.name == name);
            Assert.That(match, Is.Not.Null, $"Missing transform {name}");
            return match;
        }

        private static Transform RequirePath(Transform root, string path)
        {
            Transform match = root.Find(path);
            Assert.That(match, Is.Not.Null, $"Missing {path} under {root.name}");
            return match;
        }
    }
}
