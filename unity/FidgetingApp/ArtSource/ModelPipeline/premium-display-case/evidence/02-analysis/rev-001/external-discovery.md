# Premium Display Case Gate 02 discovery

## Extracted keywords

- User terms: 闭环管状外框、四角连通、任意角注水贯通、磨砂／摩擦背景、标签可读、Logo、雪花成就。
- English search terms: cyclic curve tube, tangent-continuous rounded bend, watertight manifold, boundary edge, flood-fill connectivity, matte charcoal EVA, fine matte grain, iPhone typography legibility.

## Sources

1. Blender 5.2 Curve editing: <https://docs.blender.org/manual/en/latest/modeling/curves/editing/curve.html>
   - A spline can be toggled cyclic.
   - Use: deterministic closed-loop path.
   - Boundary: this does not define the product shape or dimensions.
2. Blender 5.2 Curve geometry: <https://docs.blender.org/manual/en/latest/modeling/curves/properties/geometry.html>
   - Bevel turns a 1D curve into a 3D tube; a custom curve can define the cross-section.
   - Use: one cyclic path plus one closed profile, instead of four joined bars.
3. Blender 4.1 3D Print Toolbox: <https://docs.blender.org/manual/en/4.1/addons/mesh/3d_print_toolbox.html>
   - Watertight meshes must be closed; manifold edges connect to exactly two faces.
   - Use: zero non-manifold and bad-contiguous edge validation.
4. Apple HIG Typography: <https://developer.apple.com/design/human-interface-guidelines/typography>
   - iOS recommends 17 pt default and 11 pt minimum for UI text and requires context testing.
   - Use: phone-scale legibility warning only. The physical 3D label remains world-space product artwork, not Dynamic Type UI.
5. Matte EVA / fine matte ABS search candidates:
   - <https://aitextured.com/textures/plastic/foam-eva-closed-cell.html>
   - <https://aitextured.com/textures/plastic/abs-plastic-fine-matte-grain.html>
   - Use: material vocabulary only—microcellular or fine-grain, non-metallic, diffuse, low-gloss.
   - Boundary: these generated commercial pages are not approved source textures and must not be copied into shipping.

## Discovery conclusion

- The user-approved closed-loop topology remains authoritative.
- External sources support a cyclic-curve/custom-profile build route and watertight validation, not appearance.
- Background texture must be built deterministically or from a separately approved licensed source.
- Label size must be accepted from the real phone composition; an abstract point-size claim cannot approve the 3D result.
