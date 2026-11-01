import bpy, math, os, sys
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
target = args[0]
out = args[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=target)

meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
corners = []
for o in meshes:
    corners.extend([o.matrix_world @ Vector(c) for c in o.bound_box])
lo = Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners)))
hi = Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners)))
print('FILE', target)
print('OBJECTS', len(bpy.context.scene.objects), 'MESHES', len(meshes))
print('BOUNDS', tuple(round(x, 4) for x in lo), tuple(round(x, 4) for x in hi))
print('SIZE', tuple(round(x, 4) for x in (hi - lo)))
for o in meshes[:80]:
    print('MESH', o.name, 'verts', len(o.data.vertices), 'faces', len(o.data.polygons))
    print('MATERIALS', [m.name for m in o.data.materials])

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 900
scene.render.resolution_y = 650
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = out
scene.world = bpy.data.worlds.new('World')
scene.world.color = (0.05, 0.05, 0.05)
for loc, energy, size in [((2.5, -3.0, 3.0), 900, 2.5), ((-2.0, -2.0, 1.8), 500, 2.0), ((0, 2.5, 2.5), 700, 2.0)]:
    ld = bpy.data.lights.new('area', 'AREA'); ld.energy = energy; ld.shape = 'DISK'; ld.size = size
    lo_obj = bpy.data.objects.new('area', ld); lo_obj.location = loc; scene.collection.objects.link(lo_obj)
    q = (Vector((0, 0, (lo.z + hi.z) / 2)) - lo_obj.location).to_track_quat('-Z', 'Y'); lo_obj.rotation_euler = q.to_euler()
camd = bpy.data.cameras.new('camera'); cam = bpy.data.objects.new('camera', camd); scene.collection.objects.link(cam)
center = (lo + hi) / 2
cam.location = center + Vector((max(hi.x-lo.x, hi.y-lo.y)*1.4, -max(hi.x-lo.x, hi.y-lo.y)*2.0, max(hi.z-lo.z, 0.2)*1.0))
camd.lens = 55
cam.rotation_euler = (center - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam
bpy.ops.wm.save_as_mainfile(filepath=out.replace('.png', '.blend'))
bpy.ops.render.render(write_still=True)
