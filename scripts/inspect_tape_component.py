"""Inspect loose source geometry near the tape-control bay."""
import os
import sys
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
source, out = args[0], args[1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=source)
full = bpy.context.selected_objects[0]
full.name = "full source shell"
bpy.ops.import_scene.gltf(filepath=source)
fragment = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = fragment
fragment.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set(mode="OBJECT")

def local_center(obj):
    inv = full.matrix_world.inverted()
    points = [inv @ (obj.matrix_world @ Vector(c)) for c in obj.bound_box]
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return (lo + hi) / 2.0, hi - lo

target = Vector((0.1873, -0.4499, -0.0559))
found = []
for obj in list(bpy.context.scene.objects):
    if obj.type != "MESH" or obj is full:
        continue
    center, size = local_center(obj)
    distance = (center - target).length
    if distance < 0.035:
        found.append((distance, obj, center, size))
found.sort(key=lambda row: row[0])
if not found:
    raise RuntimeError("no loose component found near tape-control target")

candidate_material = bpy.data.materials.new("tape component candidate")
candidate_material.diffuse_color = (1.0, 0.08, 0.02, 1.0)
candidate_material.use_nodes = True
candidate_material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1.0, 0.08, 0.02, 1.0)
keep = set()
for index, (_, obj, center, size) in enumerate(found[:8]):
    obj.name = "tape component candidate %02d" % index
    obj.data.materials.clear()
    obj.data.materials.append(candidate_material)
    keep.add(obj)
    print(obj.name, "center", tuple(round(v, 5) for v in center), "size", tuple(round(v, 5) for v in size))
for obj in bpy.context.scene.objects:
    if obj.type == "MESH" and obj is not full and obj not in keep:
        obj.hide_render = True

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1200
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.world = bpy.data.worlds.new("component inspection world")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.03, 0.03, 0.03, 1.0)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.3

def add_light(name, location, energy):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.size = 1.5
    light = bpy.data.objects.new(name, data)
    scene.collection.objects.link(light)
    light.location = location
    light.rotation_euler = (Vector((0, -0.25, 0.95)) - light.location).to_track_quat("-Z", "Y").to_euler()

add_light("component key", (-0.8, -1.0, 1.4), 130)
add_light("component fill", (0.8, -0.8, 1.0), 90)
target_world = full.matrix_world @ Vector((0.12, -0.32, -0.04))
for location, filename in [
    ((0.0, -1.0, 0.98), "tape-component-front.png"),
    ((0.55, -0.9, 1.02), "tape-component-right.png"),
    ((-0.55, -0.9, 1.02), "tape-component-left.png"),
]:
    data = bpy.data.cameras.new(filename)
    camera = bpy.data.objects.new(filename, data)
    scene.collection.objects.link(camera)
    camera.location = location
    data.lens = 70
    camera.rotation_euler = (target_world - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    scene.render.filepath = os.path.join(out, filename)
    bpy.ops.render.render(write_still=True)
print("WROTE COMPONENT VIEWS", out)
