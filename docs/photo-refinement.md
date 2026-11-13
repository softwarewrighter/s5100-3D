# Photo-constrained refinement, November 2026

The original Trellis reconstruction is not a measurement source and is excluded
from camera fitting and geometric corrections. The photo corpus, creator/license,
variant differences, and download URLs are in
`references/ibm5100-photo-sources.json`. Preserve original files unmodified.

## Evidence and measurement limits

Three independent closed-case photographs are matched: Snuci's elevated front,
Bobo11's Enter Museum left oblique, and Sandstein's high front at MfK Bern.
Snuci's open-case overhead photograph additionally constrains keyboard grouping;
it cannot constrain the absent roof. All three matched units show three-switch
single-language configurations; German captions at Bern are a separate variant.
The procedural Model C follows IBM's APL/BASIC drawings rather than combining
incompatible switch layouts from those photos.

IBM SY31-0405-3, fourth edition, October 1979, provides:

- printed 2-9 / PDF 27: panel divisions, four Model C switches, keyboard grouping;
- printed 2-39 / PDF 57: 5-inch display and switch arrangement;
- printed 2-44 / PDF 62: Model C key layout, exposing two missing keys;
- printed B-1 / PDF 349: F/S/H 17.5 / 24 / 8 inches, 445 / 609.6 / 203 mm.

The museum record reports 443 / 610 / 200 mm; the existing model envelope is
approximately 444 / 611 / 201 mm including seams and badge. These near-agreeing
numbers do not verify individual radii, fascia tilt, screen recess, or key spacing.
A 5-inch tube rating also does not directly specify the outside glass/bezel size.

## Frozen-camera comparison

`models/photo-views.json` records manually selected cabinet corner landmarks at
1200 px image width. `scripts/fit_5100_photos.py` fits perspective pose, lens,
image translation, and small roll. `models/photo-cameras.json` freezes the result.
Render both candidates with `scripts/render_5100_photo_views.py`; never refit
cameras to make a changed feature appear better. Lighting and exposure stay fixed.

Cabinet fit RMS per coordinate is 13.4 px (Snuci), 15.4 px (Enter), and 26.4 px
(Bern). These are approximate camera matches. Unknown distortion, hand-selected
points, and an imperfect cabinet prevent pixel-perfect overlays. Roof/deck profile
and fascia tilt remain visibly unresolved, especially in Bern. No silhouette IoU
or historical-accuracy percentage is claimed.

Brightness dial, display-width switch, power rocker, and top status lamp are
withheld from the camera fit. Moving that control group 14 mm right changes mean
Euclidean control-center error:

| Photo | Before | Revised |
| --- | ---: | ---: |
| Snuci front | 29.5 px | 9.5 px |
| Enter left | 10.1 px | 8.6 px |
| Bern front | 34.9 px | 7.7 px |

These diagnose positional agreement, not physical measurement precision.

## Accepted corrections and remaining deviations

- CRT surround 147 → 134 mm wide; glass 120 → 108 mm wide; repositioned upward
  and inward relative to the photographed frame. Exact recess depth remains inferred.
- Operator group moved 14 mm right and panel shortened at its bottom.
- Tape aperture 37 → 54 mm high, top aligned below the switch panel. Cartridge
  now lies horizontally with reel faces on top; exact insertion depth remains inferred.
- Model C upper switches 3 → 4; restored Restart and panel divisions.
- Keyboard 71 → 73 caps; added missing positions. Separate Boolean-cut main,
  numeric, and spacebar wells replace raised black pads. CMD/Execute remain
  rectangular approximations of the photographed L-shaped caps.
- Side vent paths extend about 97 mm vertically and wrap the top corner,
  replacing 24 mm marks. Exact slot count, perforation depth, and rear details
  remain provisional. Slots currently depict dark surfaces, not through-holes.
- White modifiers are retained by user request; original photos show dark modifiers.

The first correction candidate exposed raised backing pads; a second candidate
cut the wells into the deck and retained matching key-top height. Checked front,
left, right, top and detail renders and independent GLB name/bounds round trip.
Both regular views and the three locked photo views were inspected before promotion.

## Reproduce the evidence

```sh
python3 scripts/fetch_5100_references.py
uv run scripts/fit_5100_photos.py  # research only: do not overwrite accepted cameras implicitly
# The accepted frozen cameras are already in models/photo-cameras.json.
blender --background --factory-startup -noaudio --python-exit-code 1 \
  --python scripts/render_5100_photo_views.py -- \
  --blend work/ibm5100-clean/out/ibm5100-clean.blend --out work/photo-comparison/after
uv run scripts/make_5100_comparison.py --after work/photo-comparison/after
just preview-index
just serve
```

Before renders and previous passing models remain under ignored `work/`.
`make_5100_comparison.py` needs the preserved baseline renders in
`work/photo-comparison/before/`. Comparison page: `/comparisons/`; improved model:
`/clean/`; top-level LAN index: `/`. The server binds `0.0.0.0:5100`.

Final browser verification loaded the revised GLB over the LAN, exercised shared
controls, verified all three index links and the nine comparison thumbnails, and
checked the opacity slider and mobile overflow without severe console errors.
The normal Linux browser still failed WebGL initialization. The clean preview
now probes WebGL before importing model-viewer, supports `?renders=1`, disposes
shared 3D controls on failure, and maps the existing preset buttons to renders.
Both forced render mode and an explicitly WebGL-disabled Chromium session passed;
model-viewer was never imported in either case. Interactive SwiftShader loading
also passed after the bootstrap change.

## Case rake, CRT depth, and cartridge follow-up

User review identified vertical case-front edges and glass projecting toward the
viewer. The case front now rakes back by a photo-estimated 8 degrees about the
keyboard/fascia joint at Z=79 mm. The case profile and aperture cutters use the
same slope, and the complete front assembly is transformed once in its own frame.
The bezel front is flush with the case plane; glass sits 10.5–15 mm behind that
plane (about 10.4–14.9 mm perpendicular to the raked face). Roof/deck and measured
rake accuracy remain provisional; 8 degrees is not a measured hardware value.

A subsequent user request specified 3–4 times more cartridge thickness. The
complete cartridge has been scaled 3.5 times vertically and seated on the lower
ledge, giving an approximately 40.25 mm presentation height. This is an explicit
user-directed visual proportion, not a verified DC300 physical dimension.
Regular front and both oblique views were inspected; independent GLB names and
bounds validation passed. Preserved prior outputs remain under `work/`.

## Raised mounting plane and common fascia setback

Further photo review showed the keyboard mounting plane itself sits above the
lower shell, while the CRT, operator panels, and tape drive sit behind the top
cover and side cheeks. Added a distinct 5 mm raised mounting panel with a visible
perimeter; keys, well floors, and instruction strip follow it. Both the mounting
panel and lower case have matching Boolean-cut key apertures.

The complete front assembly moves 20 mm back in its raked construction frame,
including CRT bezel/glass, operator controls/printing, tape rails, and cartridge.
A common fascia pocket leaves the case's top lip and side cheeks overhanging the
assembly. Control faces are approximately 12 mm behind the outer front plane;
the CRT bezel is 20 mm behind it, with glass a further 10.5–15 mm behind its bezel.
The existing 8-degree rake and 3.5x cartridge thickness are retained. These small
relative dimensions are photo-estimated presentation corrections, not measured
hardware specifications. Front and both obliques inspected; independent GLB
identity/bounds validation passed. Prior preview preserved before promotion.

With the cabinet-only cameras still frozen, the final fascia setback changes the
withheld control-center errors to 17.8 px / 12.4 px / 20.9 px (Snuci/Enter/Bern).
These are larger than the prior rake-only revision, and Enter is worse than the
initial baseline. The comparison page reports those values rather than claiming
uniform numerical improvement. The explicit overhang/depth correction follows
photo review and user feedback; the cabinet camera approximation and precise
setback require further calibration. No camera was refitted to hide the regression.

## Relative material colors

Photo feedback identified insufficient separation between the cover, keyboard
surround, and front fascia. The cover now uses a darker warm gray, the raised
keyboard panel a lighter warm gray/ivory, and the CRT bezel/operator/tape fascia
a deeper yellow sand tan. `models/presentation-palette.json` is the common source
for linear Blender colors and matching sRGB printed-panel backgrounds. The CRT
bezel and tape ledge now share the fascia material; keyboard mounting panel and
instruction strip share the lighter surround material. Cartridge reel colors
remain independent of the cover. White keys and dark gray CRT are retained.

Lighting, exposure, cameras, and geometry are held fixed for this palette pass.
The first candidate's panel was still too pale under the existing studio lights;
the second reduces the tan's blue component and lightness. These values reproduce
relative photographic relationships, not calibrated original paint samples.

## Complete keyboard photo-plane layout

The first keypad-only candidate corrected gray colors and group gaps, but review
requested the spacing of the entire keyboard. `scripts/measure_5100_keyboard.py`
now traces all 73 caps from the original public-domain overhead photo. Four
mounting-panel corner correspondences rectify the photo plane into the raised
mounting-panel frame; bright cap components supply white outlines, with shadowed
numeric skirts corrected and gray modifiers traced manually. This is an
approximate photo-plane construction, not a measurement of the physical switch
plate. Original source photos stay unmodified.

The source is `models/keyboard-layout.json`: per-key position, width, depth,
color, legend position, original pixel outline, and construction outline. It
captures the wide first numeral key, row-specific staggering, wider spacebar,
L-shaped CMD/Execute caps, and group-specific well boundaries. Small overlaps
from projected face segmentation are regularized to at least 0.8 mm; rectangular
cap envelopes were checked for overlaps above 0.2 mm and none remain.

The result has 63 white caps and 10 gray caps: four gray keypad-top keys plus
CMD, two Shift keys, Execute, and the two horizontal arrows. A user-mentioned
seventh gray main key is not identifiable in the examined photos and remains
pending clarification; no extra key was arbitrarily recolored.

Numeric grouping is eleven white caps in a three-column block with a double-width
zero, three gray keys above that block, and a separated right column containing
gray Hold plus four white operators. Added a dedicated `keyboard-layout.png`
render and viewer preset for close inspection. Gray caps have a separate light
legend atlas. Source trace image and layout JSON are linked from the preview.

A rejected first full-layout candidate cut a nearly coplanar lower-case surface
and generated an invalid bridge face across the fascia. Mesh inspection located
that face in the outer-cover assembly. The wells only need to cut the raised
mounting panel: their floors sit above the lower case. Restricting the cut to
that panel removed the artifact. Checked the corrected front, both obliques,
detail, and keyboard-top render; GLB name/bounds round trip passed. Prior output
was retained before publishing the revised preview.


Power switch correction (2026-11-12): the two user screenshots in /disk1 show a thin horizontal red lever in a tall inset, rather than the protruding red rocker previously modeled. Cut the operator fascia and its print texture, added dark upper paddle and sand-colored lower well, and placed the red lever behind the fascia plane. Estimated opening 19.5 × 39 mm; lever 16.5 × 2.8 mm, recessed 3.1 mm. These are photo-relative estimates, not measured hardware dimensions. Candidate power-switch-01 passes GLB round-trip validation and front/both-oblique/close-up visual checks.
