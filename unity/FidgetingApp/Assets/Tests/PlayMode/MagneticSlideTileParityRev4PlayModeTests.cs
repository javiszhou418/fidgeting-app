using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace FidgetingApp.Tests.PlayMode
{
    public sealed class MagneticSlideTileParityRev4PlayModeTests
    {
        [UnityTest]
        public IEnumerator ShippingShadersRenderWithoutFallbackOrEmission()
        {
            Shader crystalShader =
                Shader.Find("FidgetingApp/EDC/MagneticCrystalShippingR3");
            Shader silverShader =
                Shader.Find("FidgetingApp/EDC/MagneticSilverShippingR3");
            Assert.That(crystalShader, Is.Not.Null);
            Assert.That(silverShader, Is.Not.Null);
            Assert.That(crystalShader.isSupported, Is.True);
            Assert.That(silverShader.isSupported, Is.True);

            var crystal = new Material(crystalShader);
            var silver = new Material(silverShader);
            Assert.That(crystal.HasProperty("_EmissionColor"), Is.False);
            Assert.That(silver.HasProperty("_EmissionColor"), Is.False);
            crystal.SetColor("_CrystalColor", new Color(0.72f, 0.46f, 0.47f));
            crystal.SetFloat("_Iridescence", 0.20f);
            crystal.SetFloat("_RefractionCue", 0.12f);
            silver.SetColor("_BaseColor", new Color(0.970f, 0.965f, 0.940f));
            silver.SetFloat("_Metallic", 1f);
            silver.SetFloat("_Roughness", 0.03f);

            GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
            Renderer renderer = cube.GetComponent<Renderer>();
            renderer.sharedMaterial = silver;
            var cameraObject = new GameObject("Gate11Rev4PlayModeCamera");
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.black;
            camera.transform.position = new Vector3(0f, 0f, -3f);
            camera.transform.LookAt(cube.transform);
            var target = new RenderTexture(64, 64, 24, RenderTextureFormat.ARGB32);
            camera.targetTexture = target;

            yield return null;
            camera.Render();
            RenderTexture previous = RenderTexture.active;
            RenderTexture.active = target;
            var image = new Texture2D(64, 64, TextureFormat.RGBA32, false);
            image.ReadPixels(new Rect(0, 0, 64, 64), 0, 0);
            image.Apply();
            Color center = image.GetPixel(32, 32);
            Assert.That(float.IsNaN(center.r), Is.False);
            Assert.That(float.IsNaN(center.g), Is.False);
            Assert.That(float.IsNaN(center.b), Is.False);
            Assert.That(
                center.r > 0.95f && center.b > 0.95f && center.g < 0.15f,
                Is.False,
                "Silver shader rendered Unity fallback magenta.");

            renderer.sharedMaterial = crystal;
            camera.Render();
            image.ReadPixels(new Rect(0, 0, 64, 64), 0, 0);
            image.Apply();
            center = image.GetPixel(32, 32);
            Assert.That(float.IsNaN(center.r), Is.False);
            Assert.That(
                center.r > 0.95f && center.b > 0.95f && center.g < 0.15f,
                Is.False,
                "Crystal shader rendered Unity fallback magenta.");

            RenderTexture.active = previous;
            Object.Destroy(image);
            target.Release();
            Object.Destroy(target);
            Object.Destroy(cameraObject);
            Object.Destroy(cube);
            Object.Destroy(crystal);
            Object.Destroy(silver);
            yield return null;
        }
    }
}
