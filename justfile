# IBM 5100 3D model, generated with X_eTaL-extensions and Blender

set positional-arguments

xetal_bin := "../X_eTaL-extensions/target/debug/xetal-x"
ext_dir := "../X_eTaL-extensions/extensions"
lib_dir := "../X_eTaL-extensions/extensions/blender/lib"
blender_bin := env_var_or_default("BLENDER_BIN", "blender")
port := "5100"

default:
    @just --list

render:
    python3 ../lucy-3D/scripts/build_model.py 5100 --repo .

# Clean procedural reconstruction, separate from the previous Trellis scene.
render-clean:
    python3 scripts/build_clean_5100.py

render-clean-gpu:
    python3 scripts/build_clean_5100.py --device OPTIX

legends-clean:
    uv run scripts/make_5100_legends.py

preview-index:
    python3 scripts/make_preview_index.py

# Rebuild just the inspection page after changing shared controls.
viewer:
    python3 ../lucy-3D/scripts/make_viewer.py 5100 work/ibm5100/out

check-blender:
    python3 ../lucy-3D/scripts/check_blender.py --source work/ibm5100/out/ibm5100.glb

segment:
    "{{blender_bin}}" --background --factory-startup --python scripts/segment_trellis5100.py -- references/trellis5100-reference.glb work/ibm5100/parts

coordinate-debug:
    "{{blender_bin}}" --background --factory-startup --python scripts/render_coordinate_debug.py -- work/ibm5100/parts/crt-refined-candidate.blend work/ibm5100/parts "refined CRT glass"

serve:
    python3 scripts/make_preview_index.py
    python3 -m http.server {{port}} --bind 0.0.0.0 --directory work/preview

view:
    @if command -v open >/dev/null 2>&1; then open http://127.0.0.1:{{port}}/; else echo "Viewer: http://127.0.0.1:{{port}}/"; fi

# Isolated Chromium profile for hosts whose normal browser cannot initialize WebGL.
view-software:
    #!/usr/bin/env bash
    set -euo pipefail
    browser="$(command -v chromium || command -v chromium-browser || command -v google-chrome || true)"
    if [ -z "$browser" ]; then echo "Chromium or Google Chrome is required." >&2; exit 1; fi
    profile="$(mktemp -d /tmp/ibm5100-viewer.XXXXXX)"
    echo "Opening the 5100 with software WebGL; temporary profile: $profile"
    exec "$browser" --user-data-dir="$profile" --no-first-run --no-default-browser-check --use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader http://127.0.0.1:{{port}}/

view-serve:
    python3 scripts/make_preview_index.py
    @if [ -f "work/preview/index.html" ]; then (sleep 1; if command -v open >/dev/null 2>&1; then open http://127.0.0.1:{{port}}/; fi) >/dev/null 2>&1 & python3 -m http.server {{port}} --bind 0.0.0.0 --directory work/preview; else echo "Run 'just render-clean' first."; exit 1; fi

clean:
    rm -rf work
