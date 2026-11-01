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
Up/Down             camera target up/down
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

The reusable Codex skill is named `less-wrong-3d` and is installed at `/Users/mike/.codex/skills/less-wrong-3d/SKILL.md`. It is installed Codex configuration, not repository source.

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
