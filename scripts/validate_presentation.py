"""Validate exported materials and add the left oblique to the overview."""
import bpy
import json
import os
import sys

out = os.path.abspath(sys.argv[sys.argv.index('--') + 1])
bpy.ops.wm.open_mainfile(filepath=os.path.join(out, 'ibm5100.blend'))
scene = bpy.context.scene
cam = bpy.data.objects['cam_overview']
# overview.png already supplies the matching right oblique.
for side, x in [('left', -1.25)]:
    cam.location.x = x
    scene.camera = cam
    scene.render.filepath = os.path.join(out, side + '.png')
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(out, 'ibm5100.glb'))
expected = {
    'IBM 5100 presentation white keys': (0.95, 0.95, 0.95),
    'IBM 5100 presentation dark gray screen': (0.055, 0.055, 0.055),
    'Light gray presentation table': (0.63, 0.63, 0.63),
}
report = {}
for name, rgb in expected.items():
    mat = bpy.data.materials[name]
    actual = mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:3]
    assert all(abs(a-b) < 0.0001 for a,b in zip(actual, rgb)), (name, actual)
    faces = sum(1 for obj in bpy.context.scene.objects if obj.type == 'MESH' for face in obj.data.polygons if obj.data.materials[face.material_index] == mat)
    assert faces > 0, name
    report[name] = {'rgb': list(actual), 'exported_faces': faces}
with open(os.path.join(out, 'presentation-validation.json'), 'w') as stream:
    json.dump(report, stream, indent=2)
print('PASS: presentation colors survive GLB export and reimport')
