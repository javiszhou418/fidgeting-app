using System;
using System.Collections;
using System.IO;
using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R025
{
    public enum IsolatedR025RunMode
    {
        PreCaptureStatic,
        Scrub,
        FullProof
    }

    public sealed class IsolatedR025ProofRuntimeDriver : MonoBehaviour
    {
        [SerializeField] private IsolatedR025RunMode mode;
        [SerializeField] private IsolatedR025Profile profile;
        [SerializeField] private Camera captureCamera;
        [SerializeField] private Transform packRoot;
        [SerializeField] private SkinnedMeshRenderer[] packRenderers;
        [SerializeField] private Transform caseMotionRoot;
        [SerializeField] private SkinnedMeshRenderer r017MirrorControlFront;
        [SerializeField] private string outputRoot;
        [SerializeField] private string scenePath;

        public void Configure(
            IsolatedR025RunMode requestedMode,
            IsolatedR025Profile requestedProfile,
            Camera requestedCamera,
            Transform requestedPackRoot,
            SkinnedMeshRenderer[] requestedPackRenderers,
            Transform requestedCaseMotionRoot,
            SkinnedMeshRenderer requestedR017MirrorControlFront,
            string requestedOutputRoot,
            string requestedScenePath)
        {
            mode = requestedMode;
            profile = requestedProfile;
            captureCamera = requestedCamera;
            packRoot = requestedPackRoot;
            packRenderers = requestedPackRenderers;
            caseMotionRoot = requestedCaseMotionRoot;
            r017MirrorControlFront = requestedR017MirrorControlFront;
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
                var sequence = new IsolatedR025ProofSequence(
                    profile,
                    captureCamera,
                    packRoot,
                    packRenderers,
                    caseMotionRoot);
                sequence.InitializeSealedState();
                routine = mode switch
                {
                    IsolatedR025RunMode.PreCaptureStatic =>
                        IsolatedR025ProofCapture.RunPreCaptureStaticTest(
                            captureCamera,
                            sequence,
                            r017MirrorControlFront,
                            outputRoot,
                            scenePath),
                    IsolatedR025RunMode.Scrub =>
                        IsolatedR025ProofCapture.RunScrub(
                            captureCamera,
                            sequence,
                            outputRoot,
                            scenePath),
                    _ => IsolatedR025ProofCapture.RunFullProof(
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
                Debug.Log($"R025_{mode}_COMPLETE");
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
