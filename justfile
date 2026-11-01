# IBM 5100 3D model, generated with X_eTaL-extensions and Blender

set positional-arguments

xetal_bin := "../X_eTaL-extensions/target/debug/xetal-x"
ext_dir := "../X_eTaL-extensions/extensions"
lib_dir := "../X_eTaL-extensions/extensions/blender/lib"
blender_bin := "/Applications/Blender.app/Contents/MacOS/Blender"
port := "5100"

default:
    @just --list

render:
    XETAL_PATH="{{lib_dir}}:." {{xetal_bin}} --ext {{ext_dir}} run make-ibm5100.xtl
    "{{blender_bin}}" --background --factory-startup --python-exit-code 1 --python work/ibm5100/scene.py -- work/ibm5100/out
    @cp web/index.html work/ibm5100/out/index.html
    @node scripts/make-open-glb.js work/ibm5100/out/ibm5100.glb work/ibm5100/out/ibm5100-open.glb

segment:
    "{{blender_bin}}" --background --factory-startup --python scripts/segment_trellis5100.py -- references/trellis5100-reference.glb work/ibm5100/parts

coordinate-debug:
    "{{blender_bin}}" --background --factory-startup --python scripts/render_coordinate_debug.py -- work/ibm5100/parts/crt-refined-candidate.blend work/ibm5100/parts "refined CRT glass"

serve:
    @if [ -f "work/ibm5100/out/index.html" ]; then python3 -m http.server {{port}} --directory work/ibm5100/out; else echo "Run 'just render' first."; exit 1; fi

view:
    @if command -v open >/dev/null 2>&1; then open http://127.0.0.1:{{port}}/; else echo "Viewer: http://127.0.0.1:{{port}}/"; fi

view-serve:
    @if [ -f "work/ibm5100/out/index.html" ]; then (sleep 1; if command -v open >/dev/null 2>&1; then open http://127.0.0.1:{{port}}/; fi) >/dev/null 2>&1 & python3 -m http.server {{port}} --directory work/ibm5100/out; else echo "Run 'just render' first."; exit 1; fi

clean:
    rm -rf work
