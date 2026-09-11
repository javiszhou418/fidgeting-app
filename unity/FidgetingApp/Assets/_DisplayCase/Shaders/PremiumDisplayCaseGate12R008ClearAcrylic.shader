// R008 shell: glossy clear acrylic for a black-void turntable. HDR output
// (no clamp) so bloom can pick the specular streak and the edge glow.
// Edge dispersion: thick acrylic splits light at grazing angles; the hue is
// tied to which way the edge faces relative to the key, so the key-side
// edges run warm and the far side runs cyan, as in the reference render.
Shader "FidgetingApp/Gate12R008ClearAcrylic"
{
    Properties
    {
        _BaseColor("Body Tint", Color) = (0.10, 0.12, 0.15, 1)
        _Opacity("Base Opacity", Range(0, 1)) = 0.04
        _KeyDirection("Key Direction", Vector) = (0.45, 0.55, -0.70, 0)
        _FillDirection("Fill Direction", Vector) = (-0.70, 0.20, -0.65, 0)
        _RimStrength("Rim Strength", Range(0, 3)) = 0.55
        _RimPower("Rim Tightness", Range(0.5, 8)) = 3.2
        _SpecularStrength("Specular Streak", Range(0, 6)) = 2.2
        _SpecularPower("Specular Tightness", Range(4, 400)) = 48
        _HotspotStrength("Specular Hotspot", Range(0, 12)) = 4.0
        _Dispersion("Edge Dispersion", Range(0, 4)) = 1.6
        _DispersionSaturation("Dispersion Saturation", Range(0, 1)) = 0.85
        _EdgeGlow("Side Wall Glow", Range(0, 4)) = 1.2
        _WallOverride("Treat Whole Mesh As Side Wall", Range(0, 1)) = 0
        [Enum(UnityEngine.Rendering.CullMode)] _Cull("Cull", Float) = 0
        _FrostColor("Frost Diffusion Colour", Color) = (0.86, 0.89, 0.93, 1)
        _Frost("Frost Diffusion", Range(0, 1)) = 0
        _FrostGrain("Frost Grain", Range(0, 0.2)) = 0.05
        // Kept so PremiumDisplayCaseLabelFoil / reveal drivers can still write them.
        _SheenPhase("Tilt Phase", Float) = 0
        _LightRevealProgress("Arrival Rim Progress", Range(0, 1)) = 0
        _LightRevealStrength("Arrival Rim Strength", Range(0, 1)) = 0
        _RotationRimProgress("Rotation Rim Progress", Range(0, 1)) = 0
        _RotationRimStrength("Rotation Rim Strength", Range(0, 1)) = 0
        _SheenStrength("Mesh Sheen Strength", Range(0, 1)) = 0
    }

    SubShader
    {
        Tags
        {
            "Queue"="Transparent"
            "RenderType"="Transparent"
            "RenderPipeline"="UniversalPipeline"
        }
        Blend One OneMinusSrcAlpha
        ZWrite Off
        Cull [_Cull]

        Pass
        {
            Name "Gate12R008ClearAcrylic"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.0

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _BaseColor;
                half _Opacity;
                float4 _KeyDirection;
                float4 _FillDirection;
                half _RimStrength;
                half _RimPower;
                half _SpecularStrength;
                half _SpecularPower;
                half _HotspotStrength;
                half _Dispersion;
                half _DispersionSaturation;
                half _EdgeGlow;
                half _WallOverride;
                half4 _FrostColor;
                half _Frost;
                half _FrostGrain;
                half _SheenPhase;
                half _LightRevealProgress;
                half _LightRevealStrength;
                half _RotationRimProgress;
                half _RotationRimStrength;
                half _SheenStrength;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                float3 positionOS : TEXCOORD2;
                float3 normalOS : TEXCOORD3;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                VertexPositionInputs positions = GetVertexPositionInputs(input.positionOS.xyz);
                VertexNormalInputs normals = GetVertexNormalInputs(input.normalOS);
                output.positionCS = positions.positionCS;
                output.positionWS = positions.positionWS;
                output.normalWS = normals.normalWS;
                output.positionOS = input.positionOS.xyz;
                output.normalOS = input.normalOS;
                return output;
            }

            half Hash(float3 value)
            {
                return frac(sin(dot(value, float3(12.9898, 78.233, 37.719))) * 43758.5453);
            }

            half3 Spectrum(half t)
            {
                return 0.5h + 0.5h * cos(6.28318h * (t + half3(0.0h, 0.33h, 0.67h)));
            }

            half4 Frag(Varyings input) : SV_Target
            {
                // Geometric normal from derivatives: the imported shell meshes
                // carry smoothed vertex normals that tilt ~45° on the flat
                // face, which painted the whole front with edge dispersion.
                half3 normalWS = normalize(cross(ddy(input.positionWS), ddx(input.positionWS)));
                half3 viewDirection = SafeNormalize(GetWorldSpaceViewDir(input.positionWS));
                // Two-sided: light the face that points at the eye.
                normalWS *= sign(dot(normalWS, viewDirection) + 1e-4h);
                half facing = saturate(dot(normalWS, viewDirection));
                half fresnel = pow(1.0h - facing, _RimPower);

                half3 key = normalize(_KeyDirection.xyz);
                half3 fill = normalize(_FillDirection.xyz);
                half3 reflected = reflect(-viewDirection, normalWS);
                half streak = pow(saturate(dot(reflected, key)), _SpecularPower) * _SpecularStrength
                    + pow(saturate(dot(reflected, fill)), _SpecularPower * 0.6h) * _SpecularStrength * 0.35h;
                half hotspot = pow(saturate(dot(reflected, key)), _SpecularPower * 9.0h) * _HotspotStrength;

                // Dispersion: spectral fringe across the fresnel falloff
                // (red deepest in the edge, cyan at the rim), the way thick
                // acrylic splits a highlight. Wall glow is tinted by which way
                // the wall faces the key: warm toward it, cool away from it.
                half hue = 0.95h + (1.0h - facing) * 0.55h;
                half3 prism = lerp(half3(1, 1, 1), Spectrum(hue), _DispersionSaturation);
                half toward = saturate(dot(normalWS, key) * 0.5h + 0.5h);
                half3 wallTint = lerp(
                    lerp(half3(0.55h, 0.85h, 1.0h), half3(1.0h, 0.55h, 0.65h), toward),
                    half3(1, 1, 1), 0.35h);
                half edge = pow(1.0h - facing, 2.2h);
                half3 dispersion = prism * edge * _Dispersion
                    * (0.35h + saturate(dot(normalWS, key)) * 0.65h);
                // Side walls: light piped through the slab exits the edges as
                // a hot white streak with a coloured fringe. A flat tint here
                // read as painted plastic.
                // Side-wall mask in object space (the case meshes' depth axis
                // is object Y) so it survives the turntable. The shells are
                // dishes: their side walls are what shows edge-on.
                half3 geometricOS = normalize(mul((float3x3)GetWorldToObjectMatrix(), normalWS));
                half wall = max(_WallOverride,
                    saturate(1.0h - abs(geometricOS.y) - 0.15h));
                half wallStreak = pow(saturate(dot(reflected, key)), 9.0h)
                    + pow(saturate(dot(reflected, fill)), 9.0h) * 0.5h;
                half wallLit = saturate(dot(normalWS, key)) * 0.10h + saturate(dot(normalWS, fill)) * 0.04h;
                // Internal reflections break the wall into soft bands; a
                // wall facing the eye is lit by light piped through the slab.
                half bands = 0.78h + 0.22h * sin(input.positionWS.y * 260.0h
                    + input.positionWS.x * 140.0h + Hash(floor(input.positionWS * 40.0h)) * 6.28h);
                half piped = facing * facing * 0.30h;
                half3 sideGlow = wall * _EdgeGlow
                    * (wallTint * (0.03h + wallLit + piped) * bands
                        + lerp(wallTint, half3(1, 1, 1), 0.45h) * wallStreak * 2.2h);

                half grain = (Hash(input.positionOS * 1900.0h) - 0.5h) * 0.012h;
                half diffuse = 0.10h + saturate(dot(normalWS, key)) * 0.10h + grain;
                half3 color = _BaseColor.rgb * diffuse;
                half frostGrain = (Hash(input.positionOS * 640.0h) - 0.5h) * _FrostGrain;
                half frostLit = 0.50h + saturate(dot(normalWS, key)) * 0.50h + frostGrain;
                half frost = _Frost * (0.70h + fresnel * 0.30h);
                color = lerp(color, _FrostColor.rgb * frostLit, frost);

                color += half3(1, 1, 1) * (fresnel * _RimStrength + streak + hotspot);
                color += dispersion + sideGlow;

                half alpha = saturate(_Opacity + frost
                    + fresnel * _RimStrength * 0.35h
                    + streak * 0.20h + hotspot * 0.10h
                    + edge * _Dispersion * 0.30h
                    + wall * _EdgeGlow * (0.16h + piped * 0.9h));
                // Premultiplied: colour carries the energy (HDR, unclamped),
                // alpha only darkens what is behind.
                return half4(color, alpha);
            }
            ENDHLSL
        }
    }
}
