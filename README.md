# IBM 5100 3D Model in X_eTaL and Blender

This project builds an interactive 3D presentation of the ca. 1970 IBM 5100 Portable Computer using [X_eTaL](../X_eTaL-extensions) and Blender. The scene places the computer on a plain four-legged table in a white room and exports Blender, glTF, and OBJ assets for browser inspection.

The current enclosure reference is the supplied Trellis-generated GLB. The model is being improved through measured, reference-checked increments: the continuous enclosure is the stable foundation, while fine CRT, key-cap, selector, and tape details remain under controlled refinement.

## Introduction

The IBM 5100 was an early portable all-in-one computer with an integrated CRT, keyboard, numeric keypad, and cartridge tape drive. Its compact molded enclosure is distinct from the later IBM 5120 and should not be represented as a generic luggable computer.

This repository also exercises the X_eTaL-to-Blender pipeline on a historically grounded hardware assembly. It covers imported reference geometry, scale and camera transforms, Blender batch rendering, glTF export, and an interactive `<model-viewer>` preview.

## Overview

### Reference dimensions

- Width: 17.5 in / 445 mm
- Depth: 24.0 in / 609.6 mm
- Height: 8.0 in / 203 mm

The primary reference asset is [references/trellis5100-reference.glb](references/trellis5100-reference.glb). It supplies the continuous shell, sloped keyboard deck, CRT/control recesses, tape-bay form, and key geometry.

### Scene and viewer

The presentation scene contains a four-legged table, white-room floor and wall, neutral lighting, and named overview/operator/front-panel/keyboard/tape cameras. The interactive preview runs on port `5100`.

Viewer controls:

```text
W/S                 zoom
A/D or Left/Right   horizontal orbit
Up/Down             orbit elevation up/down
I/K                 vertical pan
Space               pause/resume rotation
R                   reset
```

The authored scene is Blender Z-up. The viewer conversion is:

```text
Blender (x, y, z) -> model-viewer (x, z, -y)
```

### Accuracy workflow

Each improvement should change one measurable feature, match a reference camera, render a front and oblique view, inspect the exported GLB, and keep the change only if it remains attached under rotation. The full procedure is documented in [docs/less-wrong.md](docs/less-wrong.md).

The reusable skill is versioned in `../lucy-3D/skills/less-wrong-3d/SKILL.md` and shared by all three modeling repositories.

## Source files

- [Ibm5100.xtl](Ibm5100.xtl) — master X_eTaL scene and Blender-generation logic.
- [Ibm5100Colors.xtl](Ibm5100Colors.xtl) — color/material definitions.
- [make-ibm5100.xtl](make-ibm5100.xtl) — X_eTaL build driver.
- [justfile](justfile) — render and port-5100 viewer recipes.
- [web/index.html](web/index.html) — interactive viewer and controls.
- [scripts/make-open-glb.js](scripts/make-open-glb.js) — browser GLB copy helper.
- [scripts/inspect_compare_glb.py](scripts/inspect_compare_glb.py) — GLB inspection helper.
- [references/trellis5100-reference.glb](references/trellis5100-reference.glb) — supplied reference mesh.
- [docs/less-wrong.md](docs/less-wrong.md) — incremental validation method.

## Build and usage

### Prerequisites

- Blender 5.x at `/Applications/Blender.app` or on `PATH`.
- `xetal-x` built in `../X_eTaL-extensions`.
- `just`, optional but recommended.
- Node.js for the GLB-copy helper.

### Render

```sh
just render
```

This runs X_eTaL, generates the Blender scene, renders validation PNGs, and exports `ibm5100.blend`, `ibm5100.glb`, and `ibm5100.obj` under `work/ibm5100/out/`.

### Run the interactive preview

```sh
just view-serve
```

Open [http://127.0.0.1:5100/](http://127.0.0.1:5100/). Keep the terminal running while using the viewer; press `Ctrl-C` to stop it.

To serve already-built output without rebuilding:

```sh
just serve
```

If your normal browser reports `Error creating WebGL context`, keep the server
running and use `just view-software`. This opens Chromium in a separate temporary
profile with SwiftShader software WebGL. It leaves your normal browser profile
unchanged. This mode is intended for the trusted local demo and may render more
slowly than working hardware acceleration. The page itself cannot change the
browser's graphics backend.

### Generated output

`work/` is generated and ignored by Git. Its main outputs are:

- `ibm5100.blend` — native Blender scene;
- `ibm5100.glb` and `ibm5100-open.glb` — glTF assets;
- `ibm5100.obj` and `ibm5100.mtl` — Wavefront export;
- `overview.png`, `operator.png`, `front-panel.png`, `keyboard.png`, and `tape.png` — validation renders;
- `index.html` — copied interactive preview.

## Research references

- [IBM 5100 Maintenance Information Manual, SY31-0405-2](https://computermuseum.informatik.uni-stuttgart.de/ftp/ibm/ibm5100/SY31-0405-2_IBM5100_MaintenceInformationManual_Oct1976.pdf)
- [IBM 5100 Maintenance Information Manual, SY31-0405-3](https://bitsavers.org/pdf/ibm/5100/SY31-0405-3_IBM_5100_Maintenance_Information_Manual_Oct1979.pdf)
- [IBM 5100 Parts Catalog, S131-0599-3](https://bitsavers.org/pdf/ibm/5100/S131-0599-3_IBM_5100_Portable_Computer_Parts_Catalog_Nov1976.pdf)
- [IBM 5110 Maintenance Information Manual](https://bitsavers.trailing-edge.com/pdf/ibm/5110/SY31-0550-2_IBM_5110_Computer_Maintenance_Information_Manual_Feb1979.pdf) — same-family enclosure reference; the IBM 5120 is intentionally excluded.
- [UvA Computer Museum IBM 5100 page](https://ub.fnwi.uva.nl/computermuseum/ibm5100.html)
- [Wikimedia Commons IBM 5100 category](https://commons.wikimedia.org/wiki/Category:IBM_5100)

## Copyright

Copyright (c) 2026 Michael A. Wright. See [COPYRIGHT](COPYRIGHT).

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Shared Linux/Mac workflow

The shared controls, portable Blender runner, and versioned refinement skill live in
[`../lucy-3D`](../lucy-3D). Run `just viewer` to regenerate an existing output's
inspection page, or `just render` for a full build. `BLENDER_BIN` defaults to
`blender`; `XETAL_EXTENSIONS_ROOT` and `XETAL_BIN` override the extensions checkout
and executable. Missing Blender/Bpy modules produce an explicit dependency error.

Common controls: W/S zoom; A/D or left/right orbit; up/down change elevation;
I/K pan vertically; Space toggles rotation; R restores the overview and pauses
rotation. Camera targets use glTF Y-up. Mechanical controls remain model-specific.
The generated viewer replaces the older embedded/source-page controls described
above. Full production builds still require the X_eTaL Blender extension libraries.

## Clean procedural 5100 preview

The new preview rebuilds the enclosure, keycaps, CRT, controls, and tape recess
as clean geometry. The Trellis mesh is retained only in the previous preview.
The new GLB contains the hardware; the studio tabletop is render-only.

```sh
just render-clean-gpu  # OptiX; use just render-clean for CPU
just serve            # index on 0.0.0.0:5100
```

The top-level index links the model versions and comparison evidence:

- `/clean/` — new procedural reconstruction, interactive model and eight renders;
- `/previous/` — preserved Trellis-based preview;
- `/comparisons/` — frozen-camera photo comparison evidence.

From another LAN device, use `http://<server-LAN-address>:5100/`. The current
server address can be found with `ip -4 route get 1.1.1.1` on Linux. `0.0.0.0`
is the bind address; use the server's actual LAN address in a browser.

`just preview-index` refreshes the index without rebuilding. `just view-software`
opens that index in the isolated Chromium software-WebGL window. Safari on the
Mac can use the same served files without Linux launch flags.

The clean model is a photo-led APL/BASIC exterior study with a 443 × 610 × 200 mm
envelope constraint. Fine APL legends, exact key spacing, molding radii, rear
fittings, and vent spacing remain provisional. See
[reference provenance](references/ibm5100-front-provenance.md). The original
print artwork is committed under `textures/`; regenerate it with
`just legends-clean` (requires `uv`, which installs Pillow in its script environment).

Photo-based refinement now has a separate `/comparisons/` page with three
camera-matched original/before/revised views and opacity overlays. See
[photo-refinement evidence and remaining deviations](docs/photo-refinement.md).
The frozen cameras are in `models/photo-cameras.json`; the supplied Trellis mesh
is excluded from fitting and correction measurements.

The clean preview checks WebGL before loading the renderer and switches to
Blender renders if initialization fails. `/clean/?renders=1` bypasses WebGL
entirely; the view buttons select rendered images. `just view-software` uses
explicit ANGLE/SwiftShader flags in a fresh Chromium profile for interactive
inspection on Linux hosts with a broken normal-browser graphics context.
