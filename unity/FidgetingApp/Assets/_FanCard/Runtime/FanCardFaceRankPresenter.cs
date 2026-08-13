using System;
using UnityEngine;

namespace FidgetingApp.FanCard
{
    public enum FanCardRank
    {
        Ace,
        Queen,
        King
    }

    public enum FanCardRankPattern
    {
        TripleAce,
        QueenKingAce
    }

    [Serializable]
    public sealed class FanCardRankLayerBinding
    {
        [SerializeField] private MeshFilter topLeft;
        [SerializeField] private MeshFilter bottomRight;

        public MeshFilter TopLeft => topLeft;
        public MeshFilter BottomRight => bottomRight;

        public void Configure(MeshFilter topLeftFilter, MeshFilter bottomRightFilter)
        {
            topLeft = topLeftFilter;
            bottomRight = bottomRightFilter;
        }

        public void Apply(Mesh mesh)
        {
            if (topLeft != null)
            {
                topLeft.sharedMesh = mesh;
            }
            if (bottomRight != null)
            {
                bottomRight.sharedMesh = mesh;
            }
        }
    }

    /// <summary>
    /// Owns the visible playing-card rank without changing any rigid-card
    /// transform, collider, magnetic state, audio, or Haptic behavior.
    /// A pattern is always selected as one complete bottom/middle/top set.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class FanCardFaceRankPresenter : MonoBehaviour
    {
        [SerializeField] private Mesh aceMesh;
        [SerializeField] private Mesh queenMesh;
        [SerializeField] private Mesh kingMesh;
        [SerializeField] private FanCardRankLayerBinding[] layers;
        [SerializeField] private bool randomizeOnDetailEntry = true;
        [SerializeField] private FanCardRankPattern currentPattern =
            FanCardRankPattern.TripleAce;

        public FanCardRankPattern CurrentPattern => currentPattern;
        public int LayerCount => layers?.Length ?? 0;

        public void Configure(
            Mesh ace,
            Mesh queen,
            Mesh king,
            FanCardRankLayerBinding[] layerBindings)
        {
            aceMesh = ace;
            queenMesh = queen;
            kingMesh = king;
            layers = layerBindings;
            ValidateConfiguration();
            ApplyPattern(FanCardRankPattern.TripleAce);
        }

        private void Start()
        {
            if (Application.isPlaying && randomizeOnDetailEntry)
            {
                RandomizeForDetailEntry();
            }
        }

        public static FanCardRankPattern ResolvePattern(float unitSample)
        {
            return Mathf.Clamp01(unitSample)
                < FanCardSpecifications.TripleAcePatternProbability
                ? FanCardRankPattern.TripleAce
                : FanCardRankPattern.QueenKingAce;
        }

        public void RandomizeForDetailEntry()
        {
            RandomizeForDetailEntry(UnityEngine.Random.value);
        }

        public void RandomizeForDetailEntry(float unitSample)
        {
            if (!randomizeOnDetailEntry)
            {
                return;
            }
            ApplyPattern(ResolvePattern(unitSample));
        }

        public void ApplyPattern(FanCardRankPattern pattern)
        {
            ValidateConfiguration();
            currentPattern = pattern;
            if (pattern == FanCardRankPattern.TripleAce)
            {
                ApplyLayer(0, FanCardRank.Ace);
                ApplyLayer(1, FanCardRank.Ace);
                ApplyLayer(2, FanCardRank.Ace);
                return;
            }

            // Authored/fanned read order is bottom, middle, top: Q, K, A.
            ApplyLayer(0, FanCardRank.Queen);
            ApplyLayer(1, FanCardRank.King);
            ApplyLayer(2, FanCardRank.Ace);
        }

        public FanCardRank RankForLayer(int layerIndex)
        {
            if (layerIndex < 0 || layerIndex >= 3)
            {
                throw new ArgumentOutOfRangeException(nameof(layerIndex));
            }
            if (currentPattern == FanCardRankPattern.TripleAce)
            {
                return FanCardRank.Ace;
            }
            return layerIndex switch
            {
                0 => FanCardRank.Queen,
                1 => FanCardRank.King,
                _ => FanCardRank.Ace
            };
        }

        private void ApplyLayer(int layerIndex, FanCardRank rank)
        {
            layers[layerIndex].Apply(MeshForRank(rank));
        }

        private Mesh MeshForRank(FanCardRank rank)
        {
            return rank switch
            {
                FanCardRank.Queen => queenMesh,
                FanCardRank.King => kingMesh,
                _ => aceMesh
            };
        }

        private void ValidateConfiguration()
        {
            if (aceMesh == null || queenMesh == null || kingMesh == null)
            {
                throw new InvalidOperationException(
                    "Fan Card rank presenter requires A, Q, and K meshes.");
            }
            if (layers == null || layers.Length != 3)
            {
                throw new InvalidOperationException(
                    "Fan Card rank presenter requires bottom/middle/top bindings.");
            }
            for (int index = 0; index < layers.Length; index++)
            {
                if (layers[index] == null
                    || layers[index].TopLeft == null
                    || layers[index].BottomRight == null)
                {
                    throw new InvalidOperationException(
                        $"Fan Card rank layer {index} requires both corner marks.");
                }
            }
        }
    }
}
