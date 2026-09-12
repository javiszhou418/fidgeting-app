using System;
using System.IO;
using FidgetingApp.DisplayCase;
using FidgetingApp.Product.Gacha;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class GachaNativeHybridCandidateTests
    {
        [Test]
        public void NativeHybridKeepsOneLiveCaseContinuousThroughPackLip()
        {
            GameObject host = new GameObject("native-hybrid-host");
            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            var director = host.AddComponent<GachaShippingRevealDirector>();
            int lipCrossings = 0;
            int completions = 0;
            try
            {
                director.caseCrossedPackLip += () => lipCrossings += 1;
                director.revealCompleted += () => completions += 1;
                director.BeginNativeHybridCandidate(
                    CanonicalToyPrize(),
                    AuthoritativeReceipt(),
                    1,
                    prize.transform,
                    false);

                PremiumDisplayCaseShippingPresentation liveCase =
                    director.ActiveCase;
                Assert.That(liveCase, Is.Not.Null);
                EntityId caseEntityId = director.NativeHybridCaseEntityId;
                Assert.That(caseEntityId, Is.Not.EqualTo(default(EntityId)));
                Assert.That(
                    host.GetComponentsInChildren<
                        PremiumDisplayCaseShippingPresentation>(true),
                    Has.Length.EqualTo(1));
                Assert.That(
                    prize.transform.IsChildOf(liveCase.ContentSlot),
                    Is.True);

                Vector3 previousPosition = liveCase.transform.localPosition;
                Vector3 previousScale = liveCase.transform.localScale;
                director.Play();
                int steps = 0;
                while (!director.IsComplete && steps++ < 180)
                {
                    director.Tick(1f / 120f);
                    Assert.That(director.ActiveCase, Is.SameAs(liveCase));
                    Assert.That(
                        director.NativeHybridCaseEntityId,
                        Is.EqualTo(caseEntityId));
                    Vector3 scale = liveCase.transform.localScale;
                    Assert.That(
                        scale.x,
                        Is.InRange(
                            director.NativeHybridInitialScale.x - 0.0001f,
                            director.NativeHybridCaseScale.x + 0.0001f));
                    Assert.That(
                        scale.y,
                        Is.GreaterThanOrEqualTo(previousScale.y - 0.00001f));
                    Assert.That(
                        scale.z,
                        Is.GreaterThanOrEqualTo(previousScale.z - 0.00001f));
                    Vector3 position = liveCase.transform.localPosition;
                    Assert.That(
                        position.y,
                        Is.GreaterThanOrEqualTo(
                            previousPosition.y - 0.00001f));
                    Assert.That(
                        Vector3.Distance(position, previousPosition),
                        Is.LessThan(0.008f));
                    previousPosition = position;
                    previousScale = scale;
                }

                Assert.That(steps, Is.LessThan(180));
                Assert.That(director.NativeHybridProgress, Is.EqualTo(1f));
                Assert.That(lipCrossings, Is.EqualTo(1));
                Assert.That(completions, Is.EqualTo(1));
                Assert.That(
                    liveCase.transform.localPosition,
                    Is.EqualTo(director.NativeHybridFinalPosition));
                Assert.That(
                    liveCase.transform.localScale,
                    Is.EqualTo(director.NativeHybridCaseScale));
                Assert.That(
                    director.NativeHybridInitialScale.x,
                    Is.LessThan(director.NativeHybridCaseScale.x));
                Assert.That(liveCase.ToyAngularVelocityIsZero, Is.True);
            }
            finally
            {
                director.Dismiss();
                UnityEngine.Object.DestroyImmediate(host);
                if (prize != null)
                {
                    UnityEngine.Object.DestroyImmediate(prize);
                }
            }
        }

        [Test]
        public void NativeHybridReduceMotionEndsAtSameLiveCasePose()
        {
            GameObject host = new GameObject("native-hybrid-reduced-host");
            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            var director = host.AddComponent<GachaShippingRevealDirector>();
            int lipCrossings = 0;
            int completions = 0;
            try
            {
                director.caseCrossedPackLip += () => lipCrossings += 1;
                director.revealCompleted += () => completions += 1;
                director.BeginNativeHybridCandidate(
                    CanonicalToyPrize(),
                    AuthoritativeReceipt(),
                    1,
                    prize.transform,
                    true);
                PremiumDisplayCaseShippingPresentation liveCase =
                    director.ActiveCase;

                director.Play();

                Assert.That(director.IsComplete, Is.True);
                Assert.That(director.NativeHybridProgress, Is.EqualTo(1f));
                Assert.That(lipCrossings, Is.EqualTo(1));
                Assert.That(completions, Is.EqualTo(1));
                Assert.That(director.ActiveCase, Is.SameAs(liveCase));
                Assert.That(
                    liveCase.transform.localPosition,
                    Is.EqualTo(director.NativeHybridFinalPosition));
                Assert.That(liveCase.ToyAngularVelocityIsZero, Is.True);
            }
            finally
            {
                director.Dismiss();
                UnityEngine.Object.DestroyImmediate(host);
                if (prize != null)
                {
                    UnityEngine.Object.DestroyImmediate(prize);
                }
            }
        }

        [Test]
        public void NativeHybridIsolationShowsOnlyCanonicalCaseRenderers()
        {
            GameObject host = new GameObject("native-hybrid-isolation-host");
            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            GameObject cameraObject = new GameObject(
                "native-hybrid-isolation-camera");
            GameObject foreignObject = GameObject.CreatePrimitive(
                PrimitiveType.Cube);
            GameObject foreignCameraObject = new GameObject(
                "native-hybrid-foreign-camera");
            var director = host.AddComponent<GachaShippingRevealDirector>();
            var isolation = new GachaNativeHybridSceneIsolation();
            Camera camera = cameraObject.AddComponent<Camera>();
            Camera foreignCamera = foreignCameraObject.AddComponent<Camera>();
            int originalCullingMask = camera.cullingMask;
            CameraClearFlags originalClearFlags = camera.clearFlags;
            Color originalBackground = camera.backgroundColor;
            foreignObject.layer = 31;
            try
            {
                director.BeginNativeHybridCandidate(
                    CanonicalToyPrize(),
                    AuthoritativeReceipt(),
                    1,
                    prize.transform,
                    false);
                PremiumDisplayCaseShippingPresentation liveCase =
                    director.ActiveCase;

                isolation.Apply(camera, liveCase.transform);

                Assert.That(
                    director.HasCanonicalNativeHybridCase,
                    Is.True);
                Assert.That(
                    director.NativeHybridCaseRootName,
                    Is.EqualTo(
                        PremiumDisplayCaseShippingFactory
                            .NativeHybridPresentationInstanceName));
                Assert.That(
                    director.NativeHybridCaseTypeName,
                    Is.EqualTo(typeof(
                        PremiumDisplayCaseShippingPresentation).FullName));
                Assert.That(
                    director.NativeHybridCaseEntityId,
                    Is.Not.EqualTo(default(EntityId)));
                Assert.That(isolation.CaseRendererCount, Is.GreaterThan(0));
                Assert.That(isolation.HasOnlyCaseRenderers, Is.True);
                Assert.That(isolation.HasNoForeignRenderers, Is.True);
                Assert.That(isolation.ForeignRendererCount, Is.Zero);
                Assert.That(
                    camera.cullingMask,
                    Is.EqualTo(1 << isolation.IsolatedLayer));
                Assert.That(
                    camera.cullingMask & (1 << foreignObject.layer),
                    Is.Zero);
                Assert.That(
                    camera.clearFlags,
                    Is.EqualTo(CameraClearFlags.SolidColor));
                Assert.That(foreignCamera.enabled, Is.False);
                Assert.That(
                    foreignObject.GetComponent<Renderer>().enabled,
                    Is.False);
                Assert.That(
                    isolation.UsesCavityClearBackdrop,
                    Is.True);
                camera.backgroundColor = new Color(
                    0.0758f,
                    0.0792f,
                    0.0828f,
                    1f);
                Assert.That(
                    isolation.UsesCavityClearBackdrop,
                    Is.True);
                camera.backgroundColor = Color.black;
                Assert.That(
                    isolation.UsesCavityClearBackdrop,
                    Is.False);
            }
            finally
            {
                isolation.Restore();
                Assert.That(camera.cullingMask, Is.EqualTo(originalCullingMask));
                Assert.That(camera.clearFlags, Is.EqualTo(originalClearFlags));
                Assert.That(camera.backgroundColor, Is.EqualTo(originalBackground));
                Assert.That(foreignCamera.enabled, Is.True);
                Assert.That(
                    foreignObject.GetComponent<Renderer>().enabled,
                    Is.True);
                director.Dismiss();
                UnityEngine.Object.DestroyImmediate(host);
                UnityEngine.Object.DestroyImmediate(cameraObject);
                UnityEngine.Object.DestroyImmediate(foreignObject);
                UnityEngine.Object.DestroyImmediate(foreignCameraObject);
                if (prize != null)
                {
                    UnityEngine.Object.DestroyImmediate(prize);
                }
            }
        }

        [Test]
        public void NativeHybridIsolationMaintainReassertsWithoutRebasingRestore()
        {
            GameObject host = new GameObject("native-hybrid-maintain-host");
            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            GameObject cameraObject = new GameObject(
                "native-hybrid-maintain-camera");
            GameObject foreignObject = GameObject.CreatePrimitive(
                PrimitiveType.Cube);
            GameObject foreignCameraObject = new GameObject(
                "native-hybrid-maintain-foreign-camera");
            var director = host.AddComponent<GachaShippingRevealDirector>();
            var isolation = new GachaNativeHybridSceneIsolation();
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
            try
            {
                director.BeginNativeHybridCandidate(
                    CanonicalToyPrize(),
                    AuthoritativeReceipt(),
                    1,
                    prize.transform,
                    false);
                isolation.Apply(camera, director.ActiveCase.transform);

                camera.enabled = false;
                camera.cullingMask = ~0;
                camera.clearFlags = CameraClearFlags.Skybox;
                camera.backgroundColor = Color.black;
                foreignCamera.enabled = true;
                foreignRenderer.enabled = true;

                isolation.Maintain();

                Assert.That(camera.enabled, Is.True);
                Assert.That(
                    camera.cullingMask,
                    Is.EqualTo(1 << isolation.IsolatedLayer));
                Assert.That(
                    camera.clearFlags,
                    Is.EqualTo(CameraClearFlags.SolidColor));
                Assert.That(isolation.UsesCavityClearBackdrop, Is.True);
                Assert.That(foreignCamera.enabled, Is.False);
                Assert.That(foreignRenderer.enabled, Is.False);
                Assert.That(isolation.HasOnlyCaseRenderers, Is.True);
            }
            finally
            {
                isolation.Restore();
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
                director.Dismiss();
                UnityEngine.Object.DestroyImmediate(host);
                UnityEngine.Object.DestroyImmediate(cameraObject);
                UnityEngine.Object.DestroyImmediate(foreignObject);
                UnityEngine.Object.DestroyImmediate(foreignCameraObject);
                if (prize != null)
                {
                    UnityEngine.Object.DestroyImmediate(prize);
                }
            }
        }

        [Test]
        public void NativeHybridSkipEndsAtTheSameLiveCasePose()
        {
            GameObject host = new GameObject("native-hybrid-skip-host");
            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            var director = host.AddComponent<GachaShippingRevealDirector>();
            int lipCrossings = 0;
            int completions = 0;
            try
            {
                director.caseCrossedPackLip += () => lipCrossings += 1;
                director.revealCompleted += () => completions += 1;
                director.BeginNativeHybridCandidate(
                    CanonicalToyPrize(),
                    AuthoritativeReceipt(),
                    1,
                    prize.transform,
                    false);
                PremiumDisplayCaseShippingPresentation liveCase =
                    director.ActiveCase;

                director.Play();
                director.Tick(0.10f);
                director.Skip();

                Assert.That(director.IsComplete, Is.True);
                Assert.That(director.ActiveCase, Is.SameAs(liveCase));
                Assert.That(director.NativeHybridProgress, Is.EqualTo(1f));
                Assert.That(lipCrossings, Is.EqualTo(1));
                Assert.That(completions, Is.EqualTo(1));
                Assert.That(
                    liveCase.transform.localPosition,
                    Is.EqualTo(director.NativeHybridFinalPosition));
            }
            finally
            {
                director.Dismiss();
                UnityEngine.Object.DestroyImmediate(host);
                if (prize != null)
                {
                    UnityEngine.Object.DestroyImmediate(prize);
                }
            }
        }

        [Test]
        public void NativeOverlayUsesTransparentMouthAndAuthoritativeGate()
        {
            string components = ReadAsset(
                "Plugins/iOS/FidgetProductUIComponents.swift");
            string storefront = ReadAsset(
                "Plugins/iOS/FidgetGachaShippingStorefront.swift");
            string rules = ReadAsset(
                "Plugins/iOS/FidgetGachaPackPresentation.swift");
            string gate = ReadAsset(
                "Plugins/iOS/FidgetGachaRiveGateRules.swift");
            string coordinator = ReadAsset(
                "Scripts/Product/FidgetAppCoordinator.cs");
            string director = ReadAsset(
                "Scripts/Product/Gacha/GachaShippingRevealDirector.cs");

            StringAssert.Contains("struct ProductPackTearRevealLayer", components);
            StringAssert.Contains("struct ProductPackSlitBodyMask", components);
            // R035: the attached-fin mask is an explicit complement; the
            // even-odd subtraction left the attached fin invisible.
            StringAssert.Contains(
                "FillStyle(eoFill: false)",
                components);
            StringAssert.DoesNotContain(
                "FillStyle(eoFill: true)",
                components);
            StringAssert.Contains(
                "struct ProductPackMouthMask",
                components);
            StringAssert.Contains("ProductPackSlitCavity", components);
            // No lip line or outline above the body edge: on the dark stage it
            // read as a plate floating on the seal.
            StringAssert.DoesNotContain("ProductPackMouthLip", components);
            StringAssert.DoesNotContain("ProductPackTornEdge", components);
            StringAssert.DoesNotContain(
                "ProductPackApertureHostingMask",
                components);
            StringAssert.DoesNotContain(
                "ProductPackApertureOccluder",
                components);
            StringAssert.DoesNotContain("openingOpacity", components);

            StringAssert.Contains(
                "ProductPackTearRevealLayer(",
                storefront);
            StringAssert.Contains(
                "liveCaseReady: liveCaseReady",
                storefront);
            StringAssert.Contains(
                "liveCaseApertureAvailable",
                storefront);
            StringAssert.Contains(
                "beginNativeHybridPackDeparture(transactionID)",
                storefront);
            StringAssert.DoesNotContain(
                "opacity(gate.unityCaseReady",
                storefront);
            StringAssert.Contains(
                "case-crossing-pack-lip",
                storefront);
            StringAssert.Contains(
                "nativeHybridContainmentHoldNanoseconds",
                storefront);

            StringAssert.Contains(
                "shouldCommit(progress: openingProgress)",
                rules);
            StringAssert.Contains(
                "canRevealLiveCase",
                rules);
            StringAssert.Contains(
                "allowsLiveCaseAperture",
                gate);
            StringAssert.Contains(
                "PresentGachaNativeHybridCandidateFromNativeUi",
                coordinator);
            StringAssert.Contains(
                "ConfirmGachaRevealReadyAfterTwoFrames",
                coordinator);
            StringAssert.Contains(
                "FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE",
                coordinator);
            StringAssert.Contains(
                "SetGachaNativeHybridPreviewProgressFromNativeUi",
                coordinator);
            StringAssert.Contains(
                "EnsureNativeHybridCaseStartsInsidePack",
                director);
            StringAssert.Contains(
                "CaseRiseScaleStartFraction",
                director);
            StringAssert.DoesNotContain(
                "ContainedAperturePreviewProgress",
                director);
        }

        [Test]
        public void R027UsesTransparentNativeOverlayAndLiveUnityCasePath()
        {
            string candidate = ReadAsset(
                "Plugins/iOS/FidgetGachaNativeHybridR027Candidate.swift");
            string components = ReadAsset(
                "Plugins/iOS/FidgetProductUIComponents.swift");
            string overlay = ReadAsset(
                "Plugins/iOS/CodexSwiftUIOverlay.swift");
            string store = ReadAsset("Plugins/iOS/FidgetGachaStore.swift");
            string rules = ReadAsset(
                "Plugins/iOS/FidgetGachaPackPresentation.swift");
            string coordinator = ReadAsset(
                "Scripts/Product/FidgetAppCoordinator.cs");

            StringAssert.Contains(
                "struct GachaNativeHybridR027CandidateView",
                candidate);
            StringAssert.Contains(
                "ProductLiveUnityPackRevealLayer",
                candidate);
            StringAssert.Contains(
                "gate.allowsLiveCaseAperture",
                candidate);
            StringAssert.Contains(
                "nativeHybridCandidate: true",
                candidate);
            StringAssert.Contains(
                "case-crossing-pack-lip",
                candidate);
            StringAssert.Contains(
                "GachaNativeHybridR027OverlayDiagnostics",
                candidate);
            StringAssert.DoesNotContain("Color.black", candidate);
            StringAssert.DoesNotContain("ProductBackdrop", candidate);
            StringAssert.DoesNotContain("IosHaptics", candidate);
            StringAssert.DoesNotContain("VFX", candidate);
            StringAssert.DoesNotContain("Particle", candidate);

            StringAssert.Contains(
                "struct ProductLiveUnityPackRevealLayer",
                components);
            StringAssert.Contains(
                "ProductTearablePackArtwork(",
                components);
            StringAssert.Contains(
                "_ = exposesLiveUnityBackground",
                components);
            StringAssert.DoesNotContain(
                "caseReady || exposesLiveUnityBackground",
                components);
            StringAssert.Contains(
                "ProductPackSlitCavity",
                components);
            StringAssert.DoesNotContain(
                "ProductPackMouthRingShape",
                components);
            StringAssert.DoesNotContain(
                ".blendMode(.destinationOut)",
                components);
            StringAssert.Contains(
                "frontLipRemainsOpaque",
                candidate);

            StringAssert.Contains(
                "nativeHybridR027CandidateController",
                overlay);
            StringAssert.Contains(
                "configure(controller, in: rootController, background: .clear)",
                overlay);
            StringAssert.Contains(
                "controller.view.isOpaque = background != .clear",
                overlay);

            StringAssert.Contains(
                "beginNativeHybridCandidate",
                store);
            StringAssert.Contains(
                "Gate04NativeHybridR027PreviewToken",
                coordinator);
            StringAssert.Contains(
                "HasStableTransform",
                coordinator);
            StringAssert.Contains(
                "HasStableCamera",
                coordinator);
            StringAssert.Contains(
                "premium-display-case-gate04-native-hybrid-r027",
                rules);
        }

        [Test]
        public void R028GatesApertureAndIsolatesTheLiveUnityCase()
        {
            string candidate = ReadAsset(
                "Plugins/iOS/FidgetGachaNativeHybridR028Candidate.swift");
            string components = ReadAsset(
                "Plugins/iOS/FidgetProductUIComponents.swift");
            string rules = ReadAsset(
                "Plugins/iOS/FidgetGachaPackPresentation.swift");
            string store = ReadAsset("Plugins/iOS/FidgetGachaStore.swift");
            string coordinator = ReadAsset(
                "Scripts/Product/FidgetAppCoordinator.cs");
            string isolation = ReadAsset(
                "Scripts/Product/Gacha/GachaNativeHybridSceneIsolation.cs");
            string bridge = ReadAsset(
                "Scripts/Product/Gacha/GachaPresentationNativeBridge.cs");

            StringAssert.Contains(
                "struct GachaNativeHybridR028CandidateView",
                candidate);
            StringAssert.Contains(
                "GachaPackHandoffRules.canRevealLiveCase",
                candidate);
            StringAssert.Contains(
                "stageRealCaseBeforeStaticTear",
                candidate);
            StringAssert.Contains(
                "setNativeHybridApertureHold",
                candidate);
            StringAssert.Contains(
                "apertureAlphaIsZero",
                candidate);
            StringAssert.Contains(
                "apertureIsShapedAndBounded",
                candidate);
            StringAssert.DoesNotContain("IosHaptics", candidate);
            StringAssert.DoesNotContain("VFX", candidate);
            StringAssert.DoesNotContain("Particle", candidate);

            StringAssert.Contains(
                "ProductPackSlitCavity",
                components);
            StringAssert.Contains(
                "public static func cavityMode",
                rules);
            StringAssert.Contains(
                "return false",
                rules);
            StringAssert.DoesNotContain(
                "lineWidth: 5.2",
                components);
            StringAssert.Contains(
                "maximumOpeningHeightPoints: Double = 5",
                rules);
            StringAssert.Contains(
                "GachaNativeHybridR028StaticStage",
                rules);
            StringAssert.Contains(
                "PresentGachaNativeHybridR028CandidateFromNativeUi",
                store);
            StringAssert.Contains(
                "CodexGachaRevealReceiveComposition",
                store);
            StringAssert.Contains(
                "Gate04NativeHybridR028PreviewToken",
                coordinator);
            StringAssert.Contains(
                "SetGachaNativeHybridApertureHoldFromNativeUi",
                coordinator);
            StringAssert.Contains(
                "native-hybrid-case-staged",
                coordinator);
            StringAssert.Contains(
                "GachaNativeHybridSceneIsolation",
                coordinator);
            StringAssert.Contains(
                "PublishComposition",
                bridge);
            StringAssert.Contains(
                "FindUnusedLayer",
                isolation);
            StringAssert.Contains(
                "CameraClearFlags.SolidColor",
                isolation);
            StringAssert.Contains(
                "HasOnlyCaseRenderers",
                isolation);
        }

        [Test]
        public void R029UsesOneRigidLidAndTheRealReadinessTrace()
        {
            string candidate = ReadAsset(
                "Plugins/iOS/FidgetGachaNativeHybridR029Candidate.swift");
            string components = ReadAsset(
                "Plugins/iOS/FidgetProductUIComponents.swift");
            string rules = ReadAsset(
                "Plugins/iOS/FidgetGachaPackPresentation.swift");
            string store = ReadAsset("Plugins/iOS/FidgetGachaStore.swift");
            string overlay = ReadAsset(
                "Plugins/iOS/CodexSwiftUIOverlay.swift");
            string coordinator = ReadAsset(
                "Scripts/Product/FidgetAppCoordinator.cs");
            string bridge = ReadAsset(
                "Scripts/Product/Gacha/GachaPresentationNativeBridge.cs");

            StringAssert.Contains(
                "private struct ProductPackLid: View",
                components);
            StringAssert.DoesNotContain(
                "struct ProductPackPeeledSeal:",
                components);
            StringAssert.DoesNotContain(
                "ProductPackSegmentedPeeledSeal",
                components);
            StringAssert.DoesNotContain(
                "ProductPackSealSegmentMask",
                components);
            StringAssert.Contains(
                "struct ProductPackTornAwayTopShape: Shape",
                components);
            StringAssert.Contains(
                "GachaPackLidRules",
                components);
            StringAssert.DoesNotContain(
                ".opacity(Double(tearFront))",
                components);

            StringAssert.Contains(
                "public enum GachaPackLidRules",
                rules);
            StringAssert.DoesNotContain(
                "GachaPackSegmentedSealRules",
                rules);
            // R035: the seam is the fin/body boundary (body top edge).
            StringAssert.Contains(
                "authoredSeamYFraction: Double = 92.0 / 512.0",
                rules);
            StringAssert.Contains(
                "GachaNativeHybridR029CaptureCheckpoint",
                rules);
            StringAssert.Contains(
                "premium-display-case-gate04-native-hybrid-r029",
                rules);
            StringAssert.Contains(
                "crossfadeEnabled = false",
                rules);

            StringAssert.Contains(
                "struct GachaNativeHybridR029CandidateView",
                candidate);
            StringAssert.Contains(
                "ProductLiveUnityPackRevealLayer",
                candidate);
            StringAssert.Contains(
                "nativeUnityCaseReady",
                candidate);
            StringAssert.Contains(
                "revealSetupFailure",
                candidate);
            StringAssert.DoesNotContain("Task.sleep", candidate);
            StringAssert.DoesNotContain("Camera.Render", candidate);
            StringAssert.DoesNotContain("IosHaptics", candidate);
            StringAssert.DoesNotContain("VFX", candidate);
            StringAssert.DoesNotContain("Particle", candidate);

            StringAssert.Contains(
                "CodexGachaRevealReceiveR029Trace",
                store);
            StringAssert.Contains(
                "revealSetupCallbackSerial",
                store);
            StringAssert.Contains(
                "nativeHybridR029CandidateController",
                overlay);
            StringAssert.Contains(
                "PresentGachaNativeHybridR029CandidateFromNativeUi",
                coordinator);
            StringAssert.Contains(
                "ConfigureGachaNativeHybridR029CaptureCheckpointFromNativeUi",
                coordinator);
            StringAssert.Contains(
                "ConfirmGachaRevealReadyAfterTwoFrames",
                coordinator);
            StringAssert.Contains(
                "if (!activeGachaNativeHybridR029Candidate)",
                coordinator);
            StringAssert.Contains(
                "activeGachaSceneIsolation.IsActive",
                coordinator);
            StringAssert.Contains(
                "PublishGachaNativeHybridR029Trace",
                coordinator);
            StringAssert.Contains(
                "GachaNativeHybridR029Trace",
                bridge);
        }

        [Test]
        public void R030MaintainsIsolationAndUsesTheRigidLidNativePack()
        {
            string candidate = ReadAsset(
                "Plugins/iOS/FidgetGachaNativeHybridR030Candidate.swift");
            string components = ReadAsset(
                "Plugins/iOS/FidgetProductUIComponents.swift");
            string rules = ReadAsset(
                "Plugins/iOS/FidgetGachaPackPresentation.swift");
            string store = ReadAsset("Plugins/iOS/FidgetGachaStore.swift");
            string overlay = ReadAsset(
                "Plugins/iOS/CodexSwiftUIOverlay.swift");
            string coordinator = ReadAsset(
                "Scripts/Product/FidgetAppCoordinator.cs");
            string isolation = ReadAsset(
                "Scripts/Product/Gacha/GachaNativeHybridSceneIsolation.cs");
            string bridge = ReadAsset(
                "Scripts/Product/Gacha/GachaPresentationNativeBridge.cs");

            StringAssert.Contains(
                "struct GachaNativeHybridR030CandidateView",
                candidate);
            StringAssert.Contains(
                "ProductLiveUnityPackRevealLayer",
                candidate);
            StringAssert.DoesNotContain("Text(", candidate);
            StringAssert.DoesNotContain(
                "accessibilityIdentifier",
                candidate);
            StringAssert.DoesNotContain("Task.sleep", candidate);
            StringAssert.DoesNotContain("Camera.Render", candidate);
            StringAssert.DoesNotContain("IosHaptics", candidate);
            StringAssert.DoesNotContain("VFX", candidate);
            StringAssert.DoesNotContain("Particle", candidate);
            // Full-sequence runs share the shipping commit beat: the rigid
            // lid leaves and the release pulse fires. Capture checkpoints
            // keep the tear parked at commit.
            StringAssert.Contains("private func playLidRelease()", candidate);
            StringAssert.Contains(
                "guard captureCheckpoint == nil, !reduceMotion else { return }",
                candidate);
            StringAssert.Contains(
                "GachaPackOpeningRules.flapExitDurationSeconds",
                candidate);
            StringAssert.Contains(
                "releasePulseStrength: releasePulseStrength",
                candidate);
            // The Pack stays mounted until its 0.24 s slide has run.
            StringAssert.Contains(
                "retreatProgress: packDeparted ? 1 : 0",
                candidate);

            StringAssert.Contains(
                "ProductPackLid(",
                components);
            StringAssert.Contains(
                "var releasePulseStrength: Double = 0",
                components);
            StringAssert.Contains(
                "GachaNativeHybridR030CaptureCheckpoint",
                rules);
            StringAssert.Contains(
                "premium-display-case-gate04-native-hybrid-r030",
                rules);
            StringAssert.Contains(
                "presentR030NativeHybridReveal",
                store);
            StringAssert.Contains(
                "CodexGachaRevealReceiveR030Trace",
                store);
            StringAssert.Contains(
                "nativeHybridR030CandidateController",
                overlay);
            StringAssert.Contains(
                "PresentGachaNativeHybridR030CandidateFromNativeUi",
                coordinator);
            StringAssert.Contains(
                "ConfigureGachaNativeHybridR030CaptureCheckpointFromNativeUi",
                coordinator);
            StringAssert.Contains(
                "MaintainActiveGachaNativeHybridIsolation",
                coordinator);
            StringAssert.Contains(
                "PublishGachaNativeHybridR030Trace",
                coordinator);
            StringAssert.Contains("public void Maintain()", isolation);
            StringAssert.Contains(
                "RenderPipelineManager.beginCameraRendering",
                isolation);
            StringAssert.Contains(
                "GachaNativeHybridR030Trace",
                bridge);
        }

        [Test]
        public void R033UsesNarrowSlitWithoutTransparentInsetAperture()
        {
            string components = ReadAsset(
                "Plugins/iOS/FidgetProductUIComponents.swift");
            string rules = ReadAsset(
                "Plugins/iOS/FidgetGachaPackPresentation.swift");
            string director = ReadAsset(
                "Scripts/Product/Gacha/GachaShippingRevealDirector.cs");

            StringAssert.Contains(
                "private struct ProductPackSlitBodyMask: View",
                components);
            StringAssert.Contains(
                "private struct ProductPackSlitCavity: View",
                components);
            StringAssert.DoesNotContain(
                "private struct ProductPackApertureHostingMask: View",
                components);
            StringAssert.DoesNotContain(
                "private struct ProductPackMouthRingShape: Shape",
                components);
            StringAssert.DoesNotContain(
                "transparentInsetAperture",
                components);
            StringAssert.DoesNotContain(
                ".blendMode(.destinationOut)",
                components);

            StringAssert.Contains(
                "maximumOpeningHeightPoints: Double = 5",
                rules);
            StringAssert.Contains(
                "return false",
                rules);
            StringAssert.Contains(
                "&& GachaPackOpeningRules.shouldCommit(progress: openingProgress)",
                rules);
            StringAssert.DoesNotContain(
                "transparentInsetAperture",
                rules);

            StringAssert.Contains(
                "CaseRiseScaleStartFraction = 0.94f",
                director);
            StringAssert.Contains(
                "nativeHybridInitialScale",
                director);
            StringAssert.DoesNotContain(
                "ContainedAperturePreviewProgress",
                director);
        }

        [Test]
        public void R032KeepsLipOutsideInsetHostingMaskAndFailClosedFoilCut()
        {
            Assert.Ignore("Superseded by R033 narrow-slit pack tear motion.");
        }

        [Test]
        public void R031UsesExplicitEvenOddMouthRingAndFailClosedAperture()
        {
            Assert.Ignore("Superseded by R033 narrow-slit pack tear motion.");
        }

        [Test]
        public void R029BridgePreservesRawTraceFields()
        {
            GachaNativeHybridR029Trace observed = default;
            int callbackCount = 0;
            Action<GachaNativeHybridR029Trace> callback = trace =>
            {
                observed = trace;
                callbackCount++;
            };
            GachaPresentationNativeBridge.r029TracePublished += callback;
            try
            {
                GachaPresentationNativeBridge.PublishR029Trace(
                    new GachaNativeHybridR029Trace(
                        "F2",
                        "f6217a76-b92d-43fd-8d25-17f9e707c1af",
                        "f6217a76-b92d-43fd-8d25-17f9e707c1af",
                        42,
                        PremiumDisplayCaseShippingFactory
                            .NativeHybridPresentationInstanceName,
                        typeof(PremiumDisplayCaseShippingPresentation)
                            .FullName,
                        "42",
                        22,
                        0,
                        true,
                        true,
                        true,
                        string.Empty,
                        0f,
                        true,
                        true,
                        true));
            }
            finally
            {
                GachaPresentationNativeBridge.r029TracePublished -= callback;
            }

            Assert.That(callbackCount, Is.EqualTo(1));
            Assert.That(observed.Checkpoint, Is.EqualTo("F2"));
            Assert.That(
                observed.RawRequestUuid,
                Is.EqualTo(observed.ReceiptUuid));
            Assert.That(observed.UnityFrameCount, Is.EqualTo(42));
            Assert.That(
                observed.CaseRootName,
                Is.EqualTo(
                    PremiumDisplayCaseShippingFactory
                        .NativeHybridPresentationInstanceName));
            Assert.That(observed.CaseStableFrame, Is.True);
            Assert.That(observed.CameraStableFrame, Is.True);
            Assert.That(observed.SetupSucceeded, Is.True);
            Assert.That(observed.RevealSetupFailure, Is.Empty);
            Assert.That(observed.ForeignRendererCount, Is.Zero);
        }

        [Test]
        public void R030BridgePreservesIsolationAndSetupTraceFields()
        {
            GachaNativeHybridR030Trace observed = default;
            int callbackCount = 0;
            Action<GachaNativeHybridR030Trace> callback = trace =>
            {
                observed = trace;
                callbackCount++;
            };
            GachaPresentationNativeBridge.r030TracePublished += callback;
            try
            {
                GachaPresentationNativeBridge.PublishR030Trace(
                    new GachaNativeHybridR030Trace(
                        "F2",
                        2,
                        "f6217a76-b92d-43fd-8d25-17f9e707c1af",
                        "f6217a76-b92d-43fd-8d25-17f9e707c1af",
                        42,
                        117,
                        "Main Camera",
                        PremiumDisplayCaseShippingFactory
                            .NativeHybridPresentationInstanceName,
                        typeof(PremiumDisplayCaseShippingPresentation)
                            .FullName,
                        "42",
                        22,
                        0,
                        true,
                        true,
                        true,
                        true,
                        true,
                        true,
                        string.Empty,
                        0f,
                        true,
                        true));
            }
            finally
            {
                GachaPresentationNativeBridge.r030TracePublished -= callback;
            }

            Assert.That(callbackCount, Is.EqualTo(1));
            Assert.That(observed.Checkpoint, Is.EqualTo("F2"));
            Assert.That(observed.StableFrameOrdinal, Is.EqualTo(2));
            Assert.That(
                observed.RawRequestUuid,
                Is.EqualTo(observed.ReceiptUuid));
            Assert.That(observed.UnityFrameCount, Is.EqualTo(42));
            Assert.That(observed.CameraInstanceId, Is.EqualTo(117L));
            Assert.That(observed.CameraName, Is.EqualTo("Main Camera"));
            Assert.That(
                observed.CaseRootName,
                Is.EqualTo(
                    PremiumDisplayCaseShippingFactory
                        .NativeHybridPresentationInstanceName));
            Assert.That(observed.IsolationActive, Is.True);
            Assert.That(observed.UsesCavityClearBackdrop, Is.True);
            Assert.That(observed.PublishSetupPublished, Is.True);
            Assert.That(observed.PublishSetupSucceeded, Is.True);
            Assert.That(observed.PublishSetupFailure, Is.Empty);
            Assert.That(observed.ForeignRendererCount, Is.Zero);
        }

        private static GachaPrizeDefinition CanonicalToyPrize()
        {
            return GachaCatalog.ResolvePrize(
                "canyon-heir-metal-three-blade").Value;
        }

        private static GachaDrawReceiptRow AuthoritativeReceipt()
        {
            return new GachaDrawReceiptRow(
                new GachaDrawOutcome(
                    "canyon-heir-metal-three-blade",
                    GachaRarity.Heirloom,
                    false,
                    true,
                    false),
                true,
                0,
                DateTime.UtcNow.ToString("O"),
                "FDT-NATIVE-HYBRID");
        }

        private static string ReadAsset(string relativePath)
        {
            return File.ReadAllText(Path.Combine(
                Application.dataPath,
                relativePath));
        }
    }
}
