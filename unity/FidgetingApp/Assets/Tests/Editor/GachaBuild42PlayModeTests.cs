using System.Collections;
using System.Collections.Generic;
using FidgetingApp.DisplayCase;
using FidgetingApp.Product;
using FidgetingApp.Product.Gacha;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.TestTools;

namespace FidgetingApp.Tests.Editor
{
    /// <summary>
    /// Build 42 frame-level gates. These tests deliberately enter Play Mode so
    /// MonoBehaviour Update/LateUpdate, deferred Destroy and EndOfFrame match
    /// the shipping reveal lifecycle instead of only sampling editor state.
    /// The transparent SwiftUI hand-off and app restart path remain XCUITest
    /// coverage because they require the generated iOS host.
    /// </summary>
    public sealed class GachaBuild42PlayModeTests
    {
        private const string TransactionPrefix =
            "fidgeting.gacha.playmode.build42.internal.v2.";

        [UnityTearDown]
        public IEnumerator LeavePlayModeAndClearTransactionState()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                // Assertions can abort a test before its normal Dismiss path.
                // Dispose only this fixture's reveal hosts while their parent
                // hierarchy is still active, then allow deferred Destroy to
                // finish before Play Mode tears the scene down.
                DismissAndDestroyTestHost("Build42RevealDirectorHost");
                DismissAndDestroyTestHost("Build42CameraRevealHost");
                DestroyTestObject("Build42ShippingCamera");
                yield return null;

                new GachaInventoryRuntime(
                    GachaRuntimeMode.InternalUnlimited,
                    TransactionPrefix).DeleteAllForTests();
                PlayerPrefs.Save();
                yield return new ExitPlayMode();
            }
        }

        [UnityTest]
        public IEnumerator RevealDirector_PublishesSixVisiblePhasesInOrderAcrossFrames()
        {
            OpenIsolatedEmptyScene();
            yield return new EnterPlayMode();

            var host = new GameObject("Build42RevealDirectorHost");
            GachaRevealDirector director = host.AddComponent<GachaRevealDirector>();
            // This test advances the authoritative clock explicitly. Disable
            // MonoBehaviour.Update so frame duration around EnterPlayMode cannot
            // add a second, nondeterministic clock source.
            director.enabled = false;
            var events = new RevealEventProbe();
            director.phaseChanged += events.HandlePhase;
            director.revealCompleted += events.HandleComplete;

            GachaPrizeDefinition prize = GachaCatalog.ResolvePrize(
                "canyon-sig-copper-strata").Value;
            Assert.That(director.Prepare(prize), Is.True, director.FailureReason);
            PremiumDisplayCase sharedCase = director.ActiveCase;
            Transform sharedPrize = director.ActivePrize;
            Assert.That(sharedCase, Is.Not.Null);
            Assert.That(sharedPrize, Is.Not.Null);
            Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Idle));

            Assert.That(director.StartReveal(), Is.True, director.FailureReason);
            Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Back));
            yield return null;
            AssertSamePresentation(director, sharedCase, sharedPrize);

            AdvanceOnePhase(director, GachaRevealTimeline.BackSeconds);
            Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Front));
            yield return null;
            AssertSamePresentation(director, sharedCase, sharedPrize);

            AdvanceOnePhase(director, GachaRevealTimeline.FrontSeconds);
            Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Readable));
            yield return null;
            AssertSamePresentation(director, sharedCase, sharedPrize);

            AdvanceOnePhase(director, GachaRevealTimeline.ReadableSeconds);
            Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Exploded));
            yield return null;
            AssertSamePresentation(director, sharedCase, sharedPrize);

            AdvanceOnePhase(director, GachaRevealTimeline.ExplodedSeconds);
            Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.PrizeOnly));
            yield return null;
            AssertSamePresentation(director, sharedCase, sharedPrize);

            AdvanceOnePhase(director, GachaRevealTimeline.PrizeOnlySeconds);
            Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Sheen));
            yield return null;
            AssertSamePresentation(director, sharedCase, sharedPrize);

            AdvanceOnePhase(director, GachaRevealTimeline.SheenSeconds);
            Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Complete));
            yield return null;

            Assert.That(events.Phases, Is.EqualTo(new[]
            {
                GachaRevealPhase.Back,
                GachaRevealPhase.Front,
                GachaRevealPhase.Readable,
                GachaRevealPhase.Exploded,
                GachaRevealPhase.PrizeOnly,
                GachaRevealPhase.Sheen,
                GachaRevealPhase.Complete
            }), "Six visible phases plus terminal Complete must be authoritative and ordered.");
            Assert.That(events.CompletionCount, Is.EqualTo(1));
            Assert.That(director.ActiveCase, Is.SameAs(sharedCase),
                "A reveal must never replace the approved shared case per prize or phase.");

            director.Dismiss();
            Object.Destroy(host);
            yield return null;
        }

        [UnityTest]
        public IEnumerator CameraLease_IsStableForTwoEndOfFrames_ThenDismissRestoresEverything()
        {
            OpenIsolatedEmptyScene();
            yield return new EnterPlayMode();

            var cameraObject = new GameObject("Build42ShippingCamera");
            Camera camera = cameraObject.AddComponent<Camera>();
            var author = cameraObject.AddComponent<GachaCameraAuthorProbe>();
            camera.aspect = 942f / 2048f;
            camera.transform.SetPositionAndRotation(
                new Vector3(0.29f, -0.17f, 0.51f),
                Quaternion.Euler(12f, 28f, -7f));
            camera.orthographic = true;
            camera.orthographicSize = 2.7f;
            camera.nearClipPlane = 0.027f;
            camera.farClipPlane = 83f;
            Vector3 originalPosition = camera.transform.position;
            Quaternion originalRotation = camera.transform.rotation;
            bool originalOrthographic = camera.orthographic;
            float originalOrthographicSize = camera.orthographicSize;
            float originalNear = camera.nearClipPlane;
            float originalFar = camera.farClipPlane;

            var host = new GameObject("Build42CameraRevealHost");
            GachaRevealDirector director = host.AddComponent<GachaRevealDirector>();
            // Keep the reveal at the exact Back setup pose while this test
            // crosses EndOfFrame boundaries to exercise only camera ownership.
            director.enabled = false;
            GachaPrizeDefinition prize = GachaCatalog.ResolvePrize(
                "canyon-ref-ridge-tint").Value;
            Assert.That(director.Prepare(prize), Is.True, director.FailureReason);
            GameObject caseObject = director.ActiveCase.gameObject;
            GameObject prizeObject = director.ActivePrize.gameObject;

            PremiumDisplayCaseCameraLease lease =
                PremiumDisplayCaseCameraLease.Acquire(camera);
            Assert.That(lease, Is.Not.Null);
            Assert.That(lease.CameraStateAuthorCount, Is.EqualTo(1));
            Assert.That(author.enabled, Is.False);
            Assert.That(author.Suppressed, Is.True);
            Assert.That(director.StartReveal(), Is.True, director.FailureReason);

            Vector3 leasedPosition = camera.transform.position;
            Quaternion leasedRotation = camera.transform.rotation;
            Matrix4x4 leasedProjection = camera.projectionMatrix;

            yield return new WaitForEndOfFrame();
            AssertCameraLeaseStable(
                lease,
                director.ActiveCase.transform,
                camera,
                leasedPosition,
                leasedRotation,
                leasedProjection,
                "first EndOfFrame");

            yield return new WaitForEndOfFrame();
            AssertCameraLeaseStable(
                lease,
                director.ActiveCase.transform,
                camera,
                leasedPosition,
                leasedRotation,
                leasedProjection,
                "second EndOfFrame");

            Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Back),
                "The two-frame native setup gate must validate the closed/back entry phase.");
            AssertCaseViewportWithinContract(
                camera,
                director.ActiveCase.transform,
                "Back");

            AdvanceOnePhase(director, GachaRevealTimeline.BackSeconds);
            Assert.That(director.Phase, Is.EqualTo(GachaRevealPhase.Front));
            yield return new WaitForEndOfFrame();
            AssertCameraLeaseStable(
                lease,
                director.ActiveCase.transform,
                camera,
                leasedPosition,
                leasedRotation,
                leasedProjection,
                "Front EndOfFrame");
            AssertCaseViewportWithinContract(
                camera,
                director.ActiveCase.transform,
                "Front");

            director.Dismiss();
            lease.Restore();
            Assert.That(camera.transform.position, Is.EqualTo(originalPosition));
            Assert.That(camera.transform.rotation, Is.EqualTo(originalRotation));
            Assert.That(camera.orthographic, Is.EqualTo(originalOrthographic));
            Assert.That(camera.orthographicSize,
                Is.EqualTo(originalOrthographicSize).Within(0.000001f));
            Assert.That(camera.nearClipPlane,
                Is.EqualTo(originalNear).Within(0.000001f));
            Assert.That(camera.farClipPlane,
                Is.EqualTo(originalFar).Within(0.0001f));
            Assert.That(author.enabled, Is.True);
            Assert.That(author.Suppressed, Is.False);
            Assert.That(director.ActiveCase, Is.Null,
                "Dismiss must synchronously release its case reference.");
            Assert.That(director.ActivePrize, Is.Null,
                "Dismiss must synchronously release its prize reference.");
            Assert.That(caseObject.activeInHierarchy, Is.False,
                "Dismiss must synchronously deactivate the queued-for-destroy case.");
            Assert.That(prizeObject.activeInHierarchy, Is.False,
                "Dismiss must synchronously deactivate the queued-for-destroy prize.");

            // Once ownership ends a real Library camera author may resume on
            // the next LateUpdate. Freeze this hostile probe only after the
            // lease's exact synchronous restore has been verified. Physical
            // reclamation remains Unity's deferred-Destroy responsibility;
            // this EditMode-hosted PlayMode test verifies the production-facing
            // synchronous contract instead: no active presentation survives
            // Dismiss, and the director releases both ownership references.
            author.enabled = false;

            Object.Destroy(host);
            Object.Destroy(cameraObject);
            yield return null;
        }

        [UnityTest]
        public IEnumerator PendingTransaction_ReloadsPreparedAndAwaitingWithoutReroll()
        {
            OpenIsolatedEmptyScene();
            yield return new EnterPlayMode();

            var cleaner = new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                TransactionPrefix);
            cleaner.DeleteAllForTests();

            var initialRandom = new CountingRandom(0.8125d);
            var initial = new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                TransactionPrefix,
                initialRandom);
            GachaTransactionResult prepared = initial.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "playmode-recover-001");
            Assert.That(prepared.Success, Is.True, prepared.FailureReason);
            Assert.That(prepared.Transaction.Phase,
                Is.EqualTo(GachaTransactionPhase.Prepared));
            string prizeId = prepared.Receipt.Rows[0].Outcome.PrizeId;
            int initialRandomCalls = initialRandom.Calls;
            Assert.That(initialRandomCalls, Is.GreaterThan(0));
            Assert.That(initial.OwnedCount, Is.Zero,
                "Prepared state must not enter Gallery before acceptance.");
            PlayerPrefs.Save();
            yield return null;

            var preparedReloadRandom = new CountingRandom(0.01d);
            var preparedReload = new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                TransactionPrefix,
                preparedReloadRandom);
            Assert.That(preparedReload.PendingTransaction, Is.Not.Null);
            Assert.That(preparedReload.PendingTransaction.Phase,
                Is.EqualTo(GachaTransactionPhase.Prepared));
            Assert.That(preparedReload.PendingTransaction.Receipt.Rows[0]
                    .Outcome.PrizeId,
                Is.EqualTo(prizeId));

            GachaTransactionResult preparedReplay = preparedReload.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "playmode-recover-001");
            Assert.That(preparedReplay.Success, Is.True);
            Assert.That(preparedReplay.Receipt.Rows[0].Outcome.PrizeId,
                Is.EqualTo(prizeId));
            Assert.That(preparedReloadRandom.Calls, Is.Zero,
                "Prepared receipt replay must read persistence, never reroll.");

            GachaTransactionResult awaiting =
                preparedReload.MarkRevealAwaitingAcceptance(
                    "playmode-recover-001");
            Assert.That(awaiting.Success, Is.True);
            Assert.That(awaiting.Transaction.Phase,
                Is.EqualTo(GachaTransactionPhase.AwaitingAcceptance));
            PlayerPrefs.Save();
            yield return null;

            var awaitingReloadRandom = new CountingRandom(0.99d);
            var awaitingReload = new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                TransactionPrefix,
                awaitingReloadRandom);
            Assert.That(awaitingReload.PendingTransaction, Is.Not.Null);
            Assert.That(awaitingReload.PendingTransaction.Phase,
                Is.EqualTo(GachaTransactionPhase.AwaitingAcceptance));
            Assert.That(awaitingReload.PendingTransaction.Receipt.Rows[0]
                    .Outcome.PrizeId,
                Is.EqualTo(prizeId));

            GachaTransactionResult awaitingReplay = awaitingReload.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "playmode-recover-001");
            Assert.That(awaitingReplay.Success, Is.True);
            Assert.That(awaitingReplay.Transaction.Phase,
                Is.EqualTo(GachaTransactionPhase.AwaitingAcceptance));
            Assert.That(awaitingReplay.Receipt.Rows[0].Outcome.PrizeId,
                Is.EqualTo(prizeId));
            Assert.That(awaitingReloadRandom.Calls, Is.Zero,
                "Awaiting-acceptance replay must return the same receipt without random access.");
            Assert.That(awaitingReload.OwnedCount, Is.Zero);
            Assert.That(
                awaitingReload.TotalDraws(GachaCatalog.LaunchSeriesId),
                Is.Zero,
                "A restored receipt may commit only after the explicit native ACK.");

            awaitingReload.DeleteAllForTests();
            PlayerPrefs.Save();
        }

        private static void OpenIsolatedEmptyScene()
        {
            Assert.That(EditorApplication.isPlayingOrWillChangePlaymode, Is.False,
                "The isolated scene must be installed before entering Play Mode.");
            EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);

            // FidgetAppCoordinator is installed BeforeSceneLoad and performs
            // the same canonical display-case snapshot as shipping startup.
            // Give that startup path the smallest valid pointed-product scene
            // contract instead of inheriting a full product scene from an
            // unrelated test or suppressing its missing-root error.
            PremiumDisplayCaseProductProfile profile =
                PremiumDisplayCaseProductProfiles.Resolve(
                    ProductCatalog.PointedThreeBladeModelId);
            var productRoot = new GameObject(profile.SceneRootName);
            GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Cube);
            visual.name = "Build42RendererOnlyProductVisual";
            visual.transform.SetParent(productRoot.transform, false);
            Collider primitiveCollider = visual.GetComponent<Collider>();
            if (primitiveCollider != null)
            {
                Object.DestroyImmediate(primitiveCollider);
            }

            Assert.That(
                productRoot.GetComponentsInChildren<Renderer>(true).Length,
                Is.EqualTo(1),
                "The isolated scene must satisfy the canonical snapshot contract.");
            Assert.That(
                productRoot.GetComponentsInChildren<Collider>(true),
                Is.Empty,
                "The isolated product fixture must remain renderer-only.");
        }

        private static void DismissAndDestroyTestHost(string objectName)
        {
            GameObject host = GameObject.Find(objectName);
            if (host == null)
            {
                return;
            }

            GachaRevealDirector director = host.GetComponent<GachaRevealDirector>();
            if (director != null)
            {
                director.Dismiss();
            }
            Object.Destroy(host);
        }

        private static void DestroyTestObject(string objectName)
        {
            GameObject target = GameObject.Find(objectName);
            if (target != null)
            {
                Object.Destroy(target);
            }
        }

        private static void AssertSamePresentation(
            GachaRevealDirector director,
            PremiumDisplayCase expectedCase,
            Transform expectedPrize)
        {
            Assert.That(director.ActiveCase, Is.SameAs(expectedCase));
            Assert.That(director.ActivePrize, Is.SameAs(expectedPrize));
        }

        private static void AdvanceOnePhase(
            GachaRevealDirector director,
            float phaseDuration)
        {
            float remaining = phaseDuration
                * (1f - Mathf.Clamp01(director.PhaseProgress));
            director.Tick(remaining + 0.001f);
        }

        private static void AssertCameraLeaseStable(
            PremiumDisplayCaseCameraLease lease,
            Transform displayCaseRoot,
            Camera camera,
            Vector3 expectedPosition,
            Quaternion expectedRotation,
            Matrix4x4 expectedProjection,
            string frameLabel)
        {
            bool presentationStable = lease.IsPresentationStable(
                displayCaseRoot,
                out string failureReason);
            string viewportDiagnostic = string.Empty;
            if (!presentationStable
                && PremiumDisplayCaseCameraRules.TryMeasureCaseViewport(
                    camera,
                    displayCaseRoot,
                    out Rect viewport,
                    out float nearestDepth))
            {
                viewportDiagnostic =
                    $" viewport=({viewport.xMin:F4},{viewport.yMin:F4})-"
                    + $"({viewport.xMax:F4},{viewport.yMax:F4})"
                    + $" nearest={nearestDepth:F4}";
            }
            Assert.That(
                presentationStable,
                Is.True,
                frameLabel + ": " + failureReason + viewportDiagnostic);
            Assert.That(camera.transform.position, Is.EqualTo(expectedPosition),
                frameLabel);
            Assert.That(camera.transform.rotation, Is.EqualTo(expectedRotation),
                frameLabel);
            AssertMatrixEquals(expectedProjection, camera.projectionMatrix, frameLabel);
        }

        private static void AssertCaseViewportWithinContract(
            Camera camera,
            Transform displayCaseRoot,
            string phaseLabel)
        {
            Assert.That(PremiumDisplayCaseCameraRules.TryMeasureCaseViewport(
                    camera,
                    displayCaseRoot,
                    out Rect viewport,
                    out float nearestDepth),
                Is.True,
                phaseLabel);
            Assert.That(nearestDepth, Is.GreaterThan(camera.nearClipPlane), phaseLabel);
            Assert.That(viewport.width,
                Is.GreaterThanOrEqualTo(
                    PremiumDisplayCaseCameraRules.MinimumCaseViewportSpan),
                phaseLabel);
            Assert.That(viewport.height,
                Is.GreaterThanOrEqualTo(
                    PremiumDisplayCaseCameraRules.MinimumCaseViewportSpan),
                phaseLabel);
            Assert.That(viewport.xMin,
                Is.GreaterThanOrEqualTo(
                    -PremiumDisplayCaseCameraRules.MaximumCaseViewportOverflow),
                phaseLabel);
            Assert.That(viewport.xMax,
                Is.LessThanOrEqualTo(
                    1f + PremiumDisplayCaseCameraRules.MaximumCaseViewportOverflow),
                phaseLabel);
            Assert.That(viewport.yMin,
                Is.GreaterThanOrEqualTo(
                    -PremiumDisplayCaseCameraRules.MaximumCaseViewportOverflow),
                phaseLabel);
            Assert.That(viewport.yMax,
                Is.LessThanOrEqualTo(
                    1f + PremiumDisplayCaseCameraRules.MaximumCaseViewportOverflow),
                phaseLabel);
            Assert.That(Mathf.Abs(viewport.center.x - 0.5f),
                Is.LessThanOrEqualTo(
                    PremiumDisplayCaseCameraRules.MaximumCaseViewportCenterOffset),
                phaseLabel);
            Assert.That(Mathf.Abs(viewport.center.y - 0.5f),
                Is.LessThanOrEqualTo(
                    PremiumDisplayCaseCameraRules.MaximumCaseViewportCenterOffset),
                phaseLabel);
        }

        private static void AssertMatrixEquals(
            Matrix4x4 expected,
            Matrix4x4 actual,
            string label)
        {
            for (int row = 0; row < 4; row++)
            {
                for (int column = 0; column < 4; column++)
                {
                    Assert.That(actual[row, column],
                        Is.EqualTo(expected[row, column]).Within(0.000001f),
                        $"{label} matrix[{row},{column}]");
                }
            }
        }

        private sealed class CountingRandom : IGachaRandom
        {
            private readonly double value;

            public CountingRandom(double value)
            {
                this.value = value;
            }

            public int Calls { get; private set; }

            public double NextDouble()
            {
                Calls += 1;
                return value;
            }
        }

        private sealed class RevealEventProbe
        {
            public List<GachaRevealPhase> Phases { get; } =
                new List<GachaRevealPhase>();

            public int CompletionCount { get; private set; }

            public void HandlePhase(GachaRevealPhase phase)
            {
                Phases.Add(phase);
            }

            public void HandleComplete()
            {
                CompletionCount += 1;
            }
        }
    }

    public sealed class GachaCameraAuthorProbe :
        MonoBehaviour,
        IPremiumDisplayCaseCameraStateAuthor
    {
        private Camera targetCamera;

        public bool Suppressed { get; private set; }

        private void Awake()
        {
            targetCamera = GetComponent<Camera>();
        }

        private void LateUpdate()
        {
            if (!Suppressed && targetCamera != null)
            {
                targetCamera.transform.position = new Vector3(8f, 9f, 10f);
                targetCamera.fieldOfView = 81f;
            }
        }

        public void SetDisplayCaseCameraControlSuppressed(bool suppressed)
        {
            Suppressed = suppressed;
        }
    }
}
