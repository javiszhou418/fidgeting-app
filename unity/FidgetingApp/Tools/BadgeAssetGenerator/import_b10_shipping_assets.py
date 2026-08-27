#!/usr/bin/env python3
"""Import the approved 2026-08-21 Challenge+Legacy-master Badge artwork
(`ArtSource/BadgeSystem/ChallengeLegacyApproved20260821/`) into the shipping
`Assets/Plugins/iOS/BadgeArtwork/` bundle used by both the iOS SwiftUI runtime
and the Unity Collector Slab display case.

This script only imports the already-approved handoff PNGs unchanged. It does
not redesign, recolor, resize, or add text to any icon, and it does not touch
Badge thresholds, XP, fragments, or reward rules. It binds strictly to the
`badge_id` values already present in `badge-asset-manifest.json`.

It verifies every unlocked PNG against its recorded SHA-256 before copying, so
a corrupted or substituted source file fails loudly instead of shipping.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HANDOFF_ROOT = REPO_ROOT / "ArtSource/BadgeSystem/ChallengeLegacyApproved20260821"
HANDOFF_MANIFEST = HANDOFF_ROOT / "badge-asset-manifest.json"
SHIPPING_ROOT = REPO_ROOT / "Assets/Plugins/iOS/BadgeArtwork"

TEXTURE_IMPORTER_META_TEMPLATE = """fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 13
  mipmaps:
    mipMapMode: 0
    enableMipMap: 1
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
    flipGreenChannel: 0
  isReadable: 0
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMipmapLimit: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 2048
  textureSettings:
    serializedVersion: 2
    filterMode: 1
    aniso: 1
    mipBias: 0
    wrapU: 0
    wrapV: 0
    wrapW: 0
  nPOTScale: 1
  lightmap: 0
  compressionQuality: 50
  spriteMode: 0
  spriteExtrude: 1
  spriteMeshType: 1
  alignment: 0
  spritePivot: {{x: 0.5, y: 0.5}}
  spritePixelsToUnits: 100
  spriteBorder: {{x: 0, y: 0, z: 0, w: 0}}
  spriteGenerateFallbackPhysicsShape: 1
  alphaUsage: 1
  alphaIsTransparency: 0
  spriteTessellationDetail: -1
  textureType: 0
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePngGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  cookieLightType: 0
  platformSettings:
  - serializedVersion: 4
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 1
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  - serializedVersion: 4
    buildTarget: iOS
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 1
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    customData:
    physicsShape: []
    bones: []
    spriteID:
    internalID: 0
    vertices: []
    indices:
    edges: []
    weights: []
    secondaryTextures: []
    spriteCustomMetadata:
      entries: []
    nameFileIdTable: {{}}
  mipmapLimitGroupName:
  pSDRemoveMatte: 0
  userData:
  assetBundleName:
  assetBundleVariant:
"""

TEXT_META_TEMPLATE = """fileFormatVersion: 2
guid: {guid}
TextScriptImporter:
  externalObjects: {{}}
  userData:
  assetBundleName:
  assetBundleVariant:
"""


def new_guid() -> str:
    return uuid.uuid4().hex


def write_meta(target_png: Path) -> None:
    meta_path = target_png.with_name(target_png.name + ".meta")
    meta_path.write_text(
        TEXTURE_IMPORTER_META_TEMPLATE.format(guid=new_guid()), encoding="utf-8"
    )


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    manifest = json.loads(HANDOFF_MANIFEST.read_text(encoding="utf-8"))
    assets = manifest["assets"]
    assert len(assets) == 40, f"expected 40 assets, found {len(assets)}"

    # 1. Verify every unlocked source PNG matches its approved hash before
    #    anything is copied into the shipping bundle.
    for asset in assets:
        source = HANDOFF_ROOT / asset["unlocked_png"]
        actual = sha256_of(source)
        expected = asset["unlocked_sha256"]
        if actual != expected:
            raise SystemExit(
                f"SHA-256 mismatch for {source}: expected {expected}, got {actual}"
            )
    print(f"Verified {len(assets)} unlocked PNG hashes against the approved manifest.")

    # 2. Remove the superseded b8-generation shipping assets (png/svg + meta),
    #    keeping the shared leather texture untouched.
    removed = 0
    for pattern in ("badge-b8-*.png", "badge-b8-*.png.meta",
                     "badge-b8-*.svg", "badge-b8-*.svg.meta",
                     "badge-b8-manifest.json", "badge-b8-manifest.json.meta"):
        for stale in SHIPPING_ROOT.glob(pattern):
            stale.unlink()
            removed += 1
    print(f"Removed {removed} superseded b8-generation files.")

    # 3. Copy the approved b10 unlocked PNGs unchanged and give each a fresh
    #    Unity TextureImporter .meta so AssetDatabase can import it.
    stable_ids = set()
    manifest_assets_out = []
    for asset in assets:
        badge_id = asset["badge_id"]
        assert badge_id not in stable_ids, f"duplicate badge_id {badge_id}"
        stable_ids.add(badge_id)

        source = HANDOFF_ROOT / asset["unlocked_png"]
        asset_name = f"badge-b10-{badge_id.replace('_', '-')}"
        expected_asset_name = Path(asset["unlocked_png"]).stem
        assert asset_name == expected_asset_name, (
            f"asset name convention mismatch for {badge_id}: "
            f"{asset_name} != {expected_asset_name}"
        )

        target = SHIPPING_ROOT / f"{asset_name}.png"
        source_bytes = source.read_bytes()
        if not target.exists() or target.read_bytes() != source_bytes:
            target.write_bytes(source_bytes)
        meta_path = target.with_name(target.name + ".meta")
        if not meta_path.exists():
            write_meta(target)

        manifest_assets_out.append(
            {
                "id": badge_id,
                "assetName": asset_name,
                "category": asset["category"],
                "grade": asset["grade"],
                "displayToken": asset["token"],
                "shortName": asset["short_name"],
            }
        )

    assert len(stable_ids) == 40, "40 unique stable IDs did not resolve exactly once"
    print(f"Imported {len(assets)} unlocked PNGs as badge-b10-*.png with fresh .meta files.")

    # 4. Write the b10 thumbnail manifest consumed by the shipping SwiftUI
    #    preview harness (BadgeNativePreviewRoot / BadgeThumbnailManifest).
    manifest_out_path = SHIPPING_ROOT / "badge-b10-manifest.json"
    manifest_out_path.write_text(
        json.dumps({"assets": manifest_assets_out}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    write_meta_text(manifest_out_path)
    print(f"Wrote {manifest_out_path.relative_to(REPO_ROOT)}")


def write_meta_text(path: Path) -> None:
    meta_path = path.with_name(path.name + ".meta")
    if meta_path.exists():
        return
    meta_path.write_text(TEXT_META_TEMPLATE.format(guid=new_guid()), encoding="utf-8")


if __name__ == "__main__":
    main()
