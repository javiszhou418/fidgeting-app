# Magnetic Fan Card reference-matched lookdev

## User request

Install the selected GitHub camera, material, lighting, look-development, and
light-estimation toolchain. Regenerate preview images in which the existing
Magnetic Fan Card fits the chosen background in perspective, contact,
reflection direction, light softness, color temperature, and material response.

## Locked product boundary

- Use the existing three-layer Magnetic Fan Card only.
- Do not generate, redraw, add, remove, or reshape product geometry.
- Preserve the canonical pivot, three rigid slabs, two air gaps, layer order,
  Q/K/A or AAA face contract, rear tracks, magnets, and bearing cap.
- External NXEDC images are environment, camera, and lighting references only.
- The generated charcoal hard-case image is an environment target only.
- Preview output remains approval-pending and cannot enter a phone build.

## Current visible mismatch

The prior 2D composite has three independent errors:

1. The background and product use different camera perspective.
2. The product reflection direction and softness do not match the background.
3. Flat Unity material response and synthetic contact shadow make the product
   appear pasted onto the surface.

The next stage must analyze these separately before any Blender lookdev work.
