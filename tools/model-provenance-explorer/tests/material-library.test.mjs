import assert from "node:assert/strict";
import test from "node:test";
import {
  deriveMaterialLibrary,
  hexFromLinear,
  hexFromSrgb,
  linearToSrgb,
  loadMaterialLibrary,
  markdownInSync,
  renderMaterialsMarkdown,
  srgbFromHex,
  srgbToLinear,
  validateMaterialLibrary
} from "../material-library-core.mjs";

const library = loadMaterialLibrary();

test("repository material library validates with thumbnails and sources present", () => {
  assert.deepEqual(validateMaterialLibrary(library), []);
  assert.ok(library.materials.length >= 12);
  assert.ok(library.materials.every((material) => material.thumbnail?.sha256));
});

test("materials.md is generated from materials.json and in sync", () => {
  assert.equal(markdownInSync(library), true);
  const markdown = renderMaterialsMarkdown(library);
  for (const material of library.materials) assert.match(markdown, new RegExp(`\`${material.id}\``));
  assert.match(markdown, /ChatGPT Image Gen/);
});

test("colour helpers round-trip between sRGB hex and linear", () => {
  assert.equal(hexFromSrgb([0.155, 0.163, 0.172]), "#282A2C");
  assert.equal(hexFromLinear([0.78, 0.79, 0.80]), "#E5E6E7");
  for (const channel of [0, 0.003, 0.155, 0.5, 0.93, 1]) {
    assert.ok(Math.abs(linearToSrgb(srgbToLinear(channel)) - channel) < 1e-9);
  }
  assert.deepEqual(srgbFromHex("#FF8000").map((value) => +value.toFixed(3)), [1, 0.502, 0]);
});

test("derived library exposes swatch hex, status labels and thumbnail urls", () => {
  const derived = deriveMaterialLibrary(library);
  const satin = derived.materials.find((material) => material.id === "steel-satin");
  assert.equal(satin.swatchHex, "#E5E6E7");
  assert.equal(satin.statusLabel, "Gate 07 已批准");
  assert.equal(satin.thumbnailUrl, "/repo/unity/FidgetingApp/ArtSource/MaterialLibrary/spheres/steel-satin.png");
  assert.equal(derived.derived.count, library.materials.length);
  assert.equal(derived.derived.thumbnailCount, library.materials.length);
});

test("axis matte stays contract-locked with zero specular and reflections", () => {
  const axis = library.materials.find((material) => material.id === "axis-matte");
  assert.equal(axis.status, "contract-locked");
  assert.equal(axis.unity.material, "M_FanCardAxisMatte");
  assert.equal(axis.unity.metallic, 0);
  assert.equal(axis.unity.smoothness, 0);
  assert.equal(axis.unity.specularHighlights, false);
  assert.equal(axis.unity.environmentReflections, false);
  assert.equal(axis.blender.roughness, 1);
  assert.ok(axis.sources.some((source) => source.path.endsWith("fan_card_guardrails.json")));
});

function clone() {
  return JSON.parse(JSON.stringify(library));
}

test("validator rejects duplicate ids, bad hex, unknown family and drifted derivations", () => {
  const duplicate = clone();
  duplicate.materials.push({ ...duplicate.materials[0] });
  assert.ok(validateMaterialLibrary(duplicate, { checkFiles: false }).some((error) => /duplicate id/.test(error)));

  const badHex = clone();
  badHex.materials[0].unity.baseColorHex = "#c6c8ca";
  assert.ok(validateMaterialLibrary(badHex, { checkFiles: false }).some((error) => /#RRGGBB uppercase/.test(error)));

  const badFamily = clone();
  badFamily.materials[0].family = "velvet";
  assert.ok(validateMaterialLibrary(badFamily, { checkFiles: false }).some((error) => /unknown family/.test(error)));

  const drifted = clone();
  const derivedEntry = drifted.materials.find((material) => material.blender.authority === "derived-from-unity");
  derivedEntry.blender.roughness = 0.5;
  assert.ok(validateMaterialLibrary(drifted, { checkFiles: false }).some((error) => /1 − unity.smoothness/.test(error)));

  const missingUnity = clone();
  const shipping = missingUnity.materials.find((material) => material.status === "shipping-unity");
  shipping.unity = null;
  assert.ok(validateMaterialLibrary(missingUnity, { checkFiles: false }).some((error) => /requires a unity block/.test(error)));
});

test("validator flags thumbnail hash drift", () => {
  const drifted = clone();
  drifted.materials[0].thumbnail.sha256 = "0".repeat(64);
  assert.ok(validateMaterialLibrary(drifted).some((error) => /sha256 drifted/.test(error)));
});
