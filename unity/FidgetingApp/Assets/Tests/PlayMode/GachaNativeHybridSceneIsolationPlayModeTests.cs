using System;
using System.Collections;
using System.Linq;
using System.Reflection;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace FidgetingApp.GachaNativeHybrid.PlayModeTests
{
    public sealed class GachaNativeHybridSceneIsolationPlayModeTests
    {
        [UnityTest]
        public IEnumerator MaintainRepairsFrameMutationAndRestorePreservesSnapshots()
        {
            GameObject cameraObject = new GameObject("R030IsolationCamera");
            GameObject caseObject = GameObject.CreatePrimitive(PrimitiveType.Cube);
            GameObject foreignObject = GameObject.CreatePrimitive(PrimitiveType.Cube);
            GameObject foreignCameraObject = new GameObject(
                "R030ForeignCamera");
            Camera camera = cameraObject.AddComponent<Camera>();
            Camera foreignCamera = foreignCameraObject.AddComponent<Camera>();
            Renderer foreignRenderer = foreignObject.GetComponent<Renderer>();
            camera.enabled = false;
            camera.cullingMask = 1 << 6;
            camera.clearFlags = CameraClearFlags.Skybox;
            camera.backgroundColor = new Color(0.24f, 0.18f, 0.12f, 1f);
            foreignObject.layer = 31;
            int originalCullingMask = camera.cullingMask;
            CameraClearFlags originalClearFlags = camera.clearFlags;
            Color originalBackground = camera.backgroundColor;
            bool originalCameraEnabled = camera.enabled;
            bool originalForeignCameraEnabled = foreignCamera.enabled;
            bool originalForeignRendererEnabled = foreignRenderer.enabled;
            object isolation = Activator.CreateInstance(RequireType(
                "FidgetingApp.Product.Gacha.GachaNativeHybridSceneIsolation"));
            try
            {
                Invoke(
                    isolation,
                    "Apply",
                    camera,
                    caseObject.transform);
                camera.enabled = false;
                camera.cullingMask = ~0;
                camera.clearFlags = CameraClearFlags.Skybox;
                camera.backgroundColor = Color.black;
                foreignCamera.enabled = true;
                foreignRenderer.enabled = true;

                Invoke(isolation, "Maintain");

                Assert.That(camera.enabled, Is.True);
                Assert.That(
                    camera.cullingMask,
                    Is.EqualTo(1 << Get<int>(isolation, "IsolatedLayer")));
                Assert.That(
                    camera.clearFlags,
                    Is.EqualTo(CameraClearFlags.SolidColor));
                Assert.That(
                    Get<bool>(isolation, "UsesCavityClearBackdrop"),
                    Is.True);
                Assert.That(foreignCamera.enabled, Is.False);
                Assert.That(foreignRenderer.enabled, Is.False);

                camera.backgroundColor = Color.white;
                foreignCamera.enabled = true;
                foreignRenderer.enabled = true;
                yield return null;
                Invoke(isolation, "Maintain");

                Assert.That(
                    Get<bool>(isolation, "UsesCavityClearBackdrop"),
                    Is.True);
                Assert.That(foreignCamera.enabled, Is.False);
                Assert.That(foreignRenderer.enabled, Is.False);
            }
            finally
            {
                Invoke(isolation, "Restore");
                Assert.That(camera.cullingMask, Is.EqualTo(originalCullingMask));
                Assert.That(camera.clearFlags, Is.EqualTo(originalClearFlags));
                Assert.That(camera.backgroundColor, Is.EqualTo(originalBackground));
                Assert.That(camera.enabled, Is.EqualTo(originalCameraEnabled));
                Assert.That(
                    foreignCamera.enabled,
                    Is.EqualTo(originalForeignCameraEnabled));
                Assert.That(
                    foreignRenderer.enabled,
                    Is.EqualTo(originalForeignRendererEnabled));
                UnityEngine.Object.Destroy(cameraObject);
                UnityEngine.Object.Destroy(caseObject);
                UnityEngine.Object.Destroy(foreignObject);
                UnityEngine.Object.Destroy(foreignCameraObject);
            }
        }

        private static Type RequireType(string fullName)
        {
            Type type = AppDomain.CurrentDomain.GetAssemblies()
                .Select(assembly => assembly.GetType(fullName, false))
                .FirstOrDefault(candidate => candidate != null);
            Assert.That(type, Is.Not.Null, fullName);
            return type;
        }

        private static void Invoke(
            object target,
            string methodName,
            params object[] arguments)
        {
            MethodInfo method = target.GetType().GetMethod(
                methodName,
                BindingFlags.Instance | BindingFlags.Public);
            Assert.That(method, Is.Not.Null, methodName);
            method.Invoke(target, arguments);
        }

        private static T Get<T>(object target, string propertyName)
        {
            PropertyInfo property = target.GetType().GetProperty(
                propertyName,
                BindingFlags.Instance | BindingFlags.Public);
            Assert.That(property, Is.Not.Null, propertyName);
            return (T)property.GetValue(target);
        }
    }
}
