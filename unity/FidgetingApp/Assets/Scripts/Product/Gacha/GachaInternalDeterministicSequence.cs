#if FIDGET_GACHA_INTERNAL_UNLIMITED
using System;
using System.Collections.Generic;
#if UNITY_IOS && !UNITY_EDITOR
using System.Runtime.InteropServices;
#endif
using UnityEngine;

namespace FidgetingApp.Product.Gacha
{
    /// <summary>
    /// Internal-build-only launch-argument gate for deterministic catalog
    /// coverage. The entire type is absent from production assemblies.
    /// </summary>
    public static class GachaInternalUnlimitedRuntimeFactory
    {
        public const string SequenceLaunchArgument = "--fidget-gacha-sequence";
        public const string CatalogEightSequence = "catalog8";

#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern int CodexProcessHasLaunchArgumentValue(
            string argumentName,
            string argumentValue);
#endif

        public static GachaInventoryRuntime Create(
            IReadOnlyList<string> launchArguments = null,
            string storagePrefix = null,
            IGachaRandom fallbackRandom = null)
        {
            IReadOnlyList<string> arguments = launchArguments
                ?? Environment.GetCommandLineArgs();
            string resolvedPrefix = string.IsNullOrEmpty(storagePrefix)
                ? GachaInventoryRuntime.InternalUnlimitedPrefix
                : storagePrefix;
            int committedDrawCount = Math.Max(
                0,
                PlayerPrefs.GetInt(
                    resolvedPrefix + GachaCatalog.LaunchSeriesId + ".draws",
                    0));
            int validPendingCount = 0;
            string pendingPayload = PlayerPrefs.GetString(
                resolvedPrefix + "transaction.pending",
                string.Empty);
            if (GachaTransactionCodec.TryDeserialize(
                    pendingPayload,
                    GachaRuntimeMode.InternalUnlimited,
                    out GachaPendingTransaction pending)
                && pending.Phase != GachaTransactionPhase.Completed)
            {
                validPendingCount = pending.Count;
            }

            IGachaRandom random = ResolveRandom(
                arguments,
                fallbackRandom,
                committedDrawCount + validPendingCount);
            return new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                resolvedPrefix,
                random);
        }

        /// <summary>
        /// Missing or invalid arguments preserve the caller's normal random
        /// source. Determinism is never enabled merely by using an internal
        /// build; the explicit catalog8 launch argument is mandatory.
        /// </summary>
        public static IGachaRandom ResolveRandom(
            IReadOnlyList<string> launchArguments,
            IGachaRandom fallbackRandom)
        {
            return ResolveRandom(launchArguments, fallbackRandom, 0);
        }

        public static IGachaRandom ResolveRandom(
            IReadOnlyList<string> launchArguments,
            IGachaRandom fallbackRandom,
            int committedAndPendingDrawCount)
        {
            return TryCreateDeterministicRandom(
                launchArguments,
                committedAndPendingDrawCount,
                out IGachaRandom deterministic)
                    ? deterministic
                    : fallbackRandom;
        }

        public static bool TryCreateDeterministicRandom(
            IReadOnlyList<string> launchArguments,
            out IGachaRandom random)
        {
            return TryCreateDeterministicRandom(launchArguments, 0, out random);
        }

        public static bool TryCreateDeterministicRandom(
            IReadOnlyList<string> launchArguments,
            int committedAndPendingDrawCount,
            out IGachaRandom random)
        {
            random = null;
            if (!CatalogEightWasRequested(launchArguments))
            {
                return false;
            }

            random = new CatalogEightRandom(committedAndPendingDrawCount);
            return true;
        }

        private static bool CatalogEightWasRequested(
            IReadOnlyList<string> launchArguments)
        {
            // XCUIApplication arguments reach NSProcessInfo on iOS, but IL2CPP
            // does not reliably include them in Environment.GetCommandLineArgs.
            // Keep the managed parser for Editor/tests and use a tiny native
            // read-only probe as the iOS source of truth.
            if (launchArguments != null)
            {
                for (int index = 0; index < launchArguments.Count; index++)
                {
                    string argument = launchArguments[index] ?? string.Empty;
                    if (string.Equals(
                            argument,
                            SequenceLaunchArgument + "=" + CatalogEightSequence,
                            StringComparison.Ordinal))
                    {
                        return true;
                    }

                    if (string.Equals(
                            argument,
                            SequenceLaunchArgument,
                            StringComparison.Ordinal)
                        && index + 1 < launchArguments.Count
                        && string.Equals(
                            launchArguments[index + 1],
                            CatalogEightSequence,
                            StringComparison.Ordinal))
                    {
                        return true;
                    }
                }
            }

#if UNITY_IOS && !UNITY_EDITOR
            return CodexProcessHasLaunchArgumentValue(
                SequenceLaunchArgument,
                CatalogEightSequence) != 0;
#else
            return false;
#endif
        }

        /// <summary>
        /// Two values per draw: rarity band then index within that rarity.
        /// The order matches the eight launch-catalog definitions exactly.
        /// </summary>
        private sealed class CatalogEightRandom : IGachaRandom
        {
            private static readonly double[] values =
            {
                // Four Standard prizes.
                0.90d, 0.125d,
                0.90d, 0.375d,
                0.90d, 0.625d,
                0.90d, 0.875d,
                // Two Refined prizes.
                0.15d, 0.25d,
                0.15d, 0.75d,
                // Signature, then Heirloom.
                0.03d, 0.50d,
                0.005d, 0.50d
            };

            private int cursor;

            public CatalogEightRandom(int committedAndPendingDrawCount)
            {
                int normalizedDrawCount = Math.Max(0, committedAndPendingDrawCount)
                    % GachaCatalog.ResolveSeries(GachaCatalog.LaunchSeriesId).Prizes.Count;
                cursor = normalizedDrawCount * 2;
            }

            public double NextDouble()
            {
                double value = values[cursor];
                cursor = (cursor + 1) % values.Length;
                return value;
            }
        }
    }
}
#endif
