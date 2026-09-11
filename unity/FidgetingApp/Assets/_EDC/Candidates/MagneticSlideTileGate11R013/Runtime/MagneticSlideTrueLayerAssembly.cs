using System;
using UnityEngine;

namespace FidgetingApp.EDC.Gate11R013
{
    public sealed class MagneticSlideTrueLayerAssembly : MonoBehaviour
    {
        public const float SubstrateInsetMeters = 0.00028f;
        public const float MotifInsetMeters = 0.00014f;
        public const float CrystalCapThicknessMeters = 0.00028f;
        public const float MotifPhysicalThicknessMeters = 0.00005f;
        public const float CrystalIor = 1.52f;

        [SerializeField] private MeshRenderer substrate;
        [SerializeField] private MeshRenderer motif;
        [SerializeField] private MeshRenderer crystalCap;
        [SerializeField] private Vector3 localOutwardNormal;
        [SerializeField] private string faceId;

        public MeshRenderer Substrate => substrate;
        public MeshRenderer Motif => motif;
        public MeshRenderer CrystalCap => crystalCap;
        public Vector3 LocalOutwardNormal => localOutwardNormal;
        public string FaceId => faceId;

        public float SubstrateInset => SubstrateInsetMeters;
        public float MotifInset => MotifInsetMeters;
        public float CrystalCapThickness => CrystalCapThicknessMeters;

        public void Configure(
            string id,
            Vector3 outwardNormal,
            MeshRenderer substrateRenderer,
            MeshRenderer motifRenderer,
            MeshRenderer capRenderer)
        {
            if (outwardNormal.sqrMagnitude < 0.99f)
                throw new ArgumentOutOfRangeException(nameof(outwardNormal));
            faceId = id;
            localOutwardNormal = outwardNormal.normalized;
            substrate = substrateRenderer;
            motif = motifRenderer;
            crystalCap = capRenderer;
        }
    }
}
