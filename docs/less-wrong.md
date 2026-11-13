# A less-wrong workflow for iterative 3D reconstruction

When a generated model is visibly wrong, improve one measurable feature at a time. Do not keep adding approximate parts to a scene that has not passed a rotated-view check.

## 1. Establish a reference frame

Choose the reference image and record:

- camera direction and elevation;
- visible front, side, and top edges;
- the model center and scale;
- three or more landmarks that are easy to recognize in both images.

For an IBM 5100, useful landmarks are the CRT bezel, the keyboard front edge, the tape-bay opening, the center selector, and the enclosure top corners.

Keep Blender coordinates and viewer coordinates explicit. In this project the authored scene is Blender Z-up and the viewer uses Y-up:

```text
Blender (x, y, z) -> model-viewer (x, z, -y)
```

Do not mix viewer camera coordinates with Blender object coordinates. A placement that looks correct from one camera can be wrong in depth and detach when orbiting.

## 2. Match the reference camera before changing geometry

For every reference photo, create a named Blender camera with the same approximate azimuth, elevation, target, and focal length. Render the model from that camera. The comparison is only meaningful when the outer enclosure edges overlap.

Use a small set of named validation views:

```text
front      straight-on operator/reference view
left       left-front oblique view
right      right-front oblique view
top        top/depth view
```

The web viewer’s buttons should correspond to these same views. If a reference cannot be matched by rotating the model and camera, fix the camera convention before judging the model.

## 3. Work on one feature per iteration

Use a feature queue such as:

1. enclosure silhouette;
2. CRT opening and screen surface;
3. keyboard deck and key-cap material;
4. tape-bay opening and cartridge;
5. selector and small controls;
6. colors, labels, and lighting.

For each feature, write down its expected measurable result before editing. Example:

```text
Feature: red selector
Front target: centered below the control knobs
Oblique target: remains attached to the same panel face
Pass: correct in front and both oblique renders
```

Do not work on the CRT, tape, and selector in the same pass. If one feature fails, remove or roll back only that feature.

## 4. Prefer source-local geometry over guessed world coordinates

If a part is derived from an imported mesh, define its location in the source mesh’s local coordinate frame and apply the imported object transform once. Do not independently guess world-space X/Y/Z values for several helper objects.

A helper object must be tested in at least two cameras. A front-only match is not a match: depth errors commonly appear as parts floating beside or behind the enclosure in an oblique view.

When the imported mesh has usable disconnected parts, separate them before assigning materials. Blender supports separating selected geometry, by material, or by loose parts; material assignment can then be applied to the separated objects or selected faces. See the [Blender Separate manual](https://docs.blender.org/manual/en/5.1/modeling/meshes/editing/mesh/separate.html) and [material assignment manual](https://docs.blender.org/manual/en/5.0/render/materials/assignment.html).

If the mesh is one connected or ambiguously overlapping surface, do not paint broad regions using only bounding boxes. That can color the keyboard tray, shell, and controls together. First inspect topology, normals, disconnected components, and material slots. If those do not identify the feature reliably, use a better segmented source mesh or perform deliberate Blender mesh editing.

## 5. Validate every change

The minimum validation loop is:

```text
edit one feature
build the Blender scene
render front
render left/right oblique
inspect all renders
inspect the interactive viewer after orbiting
```

A feature passes only if:

- it is in the intended location in the reference view;
- it remains attached in at least one rotated view;
- it does not create new floating, oversized, or intersecting geometry;
- unrelated features are unchanged.

Keep the render output from the previous passing iteration so a failed attempt can be compared and reverted. Do not present a failed iteration as an improvement.

## 6. Treat warnings separately from visual defects

Duplicate-edge and degenerate-triangle warnings from an imported GLB may be repairable mesh-topology issues, but they are not proof that a visual result is acceptable. Record them, inspect the resulting mesh, and decide whether to clean the mesh in Blender. A successful export is not a successful reconstruction.

Likewise, camera-control bugs, material errors, and geometry errors should be isolated. Fixing a viewer camera must not be used to disguise a misplaced model part.

## 7. Stop when the evidence says the approach is not working

After two or three targeted attempts with no improvement, stop changing coordinates. State the failed hypothesis, preserve the last stable artifact, and choose a new approach:

- inspect and repair the imported mesh in Blender;
- separate loose parts or material regions;
- use a segmented reference model;
- create a deliberately modeled replacement for the affected feature;
- or document the limitation instead of adding another approximate helper.

The goal is not to produce a new render every cycle. The goal is to produce a visibly less-wrong model whose improvement is demonstrated from the same reference-aligned cameras.

## Presentation palette (2026-11-08)

User-requested presentation colors: neutral light gray table (linear RGB 0.63),
white key tops (0.95), and dark gray inactive CRT (0.055). These are display
choices, not historical color measurements. `scripts/presentation_colors.py`
runs after the stable shell cleanup so earlier experimental masks cannot erase
them. Its regions use the source mesh's local frame and existing surface normals;
no replacement geometry is added. The keyboard is still the soft Trellis mesh.

Acceptance: table RGB channels are equal and differ from the tan enclosure;
raised key tops receive white while the surrounding deck stays tan; the inset
CRT receives neutral dark gray while its surround stays tan. Preserve camera,
lighting, and geometry settings for comparison. `just render` preserves previous
output; `scripts/validate_presentation.py` adds the left oblique and checks all
three material colors and nonempty face assignments after GLB reimport.

## Clean procedural reconstruction (2026-11-10)

The old presentation exposed the reconstruction mesh as finished hardware,
removed its texture materials, and outlined its surface artifacts with Freestyle.
The new `scripts/ibm5100_clean_scene.py` constructs the 5100 independently:
continuous beveled enclosure with Boolean CRT/tape recesses, a smooth curved CRT,
71 individual tapered/dished keycaps, operator controls, and original print atlases.
Parts are batched by material only after their deliberate edge treatments are
applied. Geometry, not coordinate masks on Trellis triangles, defines color edges.

Acceptance: straight enclosure edges; an unbroken smooth CRT outline; discrete
keycaps with no white paint on the deck; no screen/tape helpers floating outside
the body; intact part relationships from front, left, right, and top; hardware-only
GLB export with matching semantic identities and bounds after independent import.
The envelope follows the Museums Victoria 443 × 610 × 200 mm record, within the
small added feet, seams, and badges. Photo and configuration evidence is recorded
in `references/ibm5100-front-provenance.md`. Hidden details remain provisional.

A CPU baseline completed six Cycles renders and passed round-trip validation.
The final OptiX presentation uses 48 samples, AgX, broad studio lights, no
Freestyle, and a render-only neutral gray tabletop. Inspected corresponding front
and both oblique views, top, and detail. The preview index preserves both models.
A real Chromium check loaded the model through the LAN address, exercised shared
zoom/pan/reset and side/top presets, checked mobile overflow, and found no severe
console errors. These establish a reviewable reconstruction, not measured fidelity.
