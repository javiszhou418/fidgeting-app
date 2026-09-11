using System;
using System.Collections;
using System.IO;
using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R016
{
    public enum IsolatedR016RunMode
    {
        PreCaptureStatic,
        Scrub,
        FullProof
    }

    public sealed class IsolatedR016ProofRuntimeDriver : MonoBehaviour
    {
        [SerializeField] private IsolatedR016RunMode mode;
        [SerializeField] private IsolatedR016Profile profile;
        [SerializeField] private Camera captureCamera;
        [SerializeField] private Transform packRoot;
        [SerializeField] private SkinnedMeshRenderer[] packRenderers;
        [SerializeField] private Transform caseMotionRoot;
        [SerializeField] private string outputRoot;
        [SerializeField] private string scenePath;

        public void Configure(
            IsolatedR016RunMode requestedMode,
            IsolatedR016Profile requestedProfile,
            Camera requestedCamera,
            Transform requestedPackRoot,
            SkinnedMeshRenderer[] requestedPackRenderers,
            Transform requestedCaseMotionRoot,
            string requestedOutputRoot,
            string requestedScenePath)
        {
            mode = requestedMode;
            profile = requestedProfile;
            captureCamera = requestedCamera;
            packRoot = requestedPackRoot;
            packRenderers = requestedPackRenderers;
            caseMotionRoot = requestedCaseMotionRoot;
            outputRoot = requestedOutputRoot;
            scenePath = requestedScenePath;
        }

        private IEnumerator Start()
        {
            yield return null;
            IEnumerator routine = null;
            Exception initializationFailure = null;
            try
            {
                var sequence = new IsolatedR016ProofSequence(
                    profile,
                    captureCamera,
                    packRoot,
                    packRenderers,
                    caseMotionRoot);
                sequence.InitializeSealedState();
                routine = mode switch
                {
                    IsolatedR016RunMode.PreCaptureStatic =>
                        IsolatedR016ProofCapture.RunPreCaptureStaticTest(
                            captureCamera,
                            sequence,
                            outputRoot,
                            scenePath),
                    IsolatedR016RunMode.Scrub =>
                        IsolatedR016ProofCapture.RunScrub(
                            captureCamera,
                            sequence,
                            outputRoot,
                            scenePath),
                    _ => IsolatedR016ProofCapture.RunFullProof(
                        captureCamera,
                        sequence,
                        outputRoot,
                        scenePath)
                };
            }
            catch (Exception exception)
            {
                initializationFailure = exception;
            }

            Exception failure = initializationFailure;
            while (failure == null && routine != null)
            {
                bool hasNext;
                object current = null;
                try
                {
                    hasNext = routine.MoveNext();
                    if (hasNext)
                    {
                        current = routine.Current;
                    }
                }
                catch (Exception exception)
                {
                    failure = exception;
                    break;
                }
                if (!hasNext)
                {
                    break;
                }
                yield return current;
            }

            if (failure == null)
            {
                Debug.Log($"R016_{mode}_COMPLETE");
                yield return null;
                Exit(0);
                yield break;
            }

            Directory.CreateDirectory(outputRoot);
            File.WriteAllText(
                Path.Combine(outputRoot, "runtime-failure.txt"),
                $"{failure.GetType().FullName}: {failure.Message}\n");
            Debug.LogException(failure);
            yield return null;
            Exit(1);
        }

        private static void Exit(int exitCode)
        {
#if UNITY_EDITOR
            EditorApplication.Exit(exitCode);
#else
            Application.Quit(exitCode);
#endif
        }
    }
}
