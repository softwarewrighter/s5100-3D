import bpy
import os
import sys
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
blend = args[0]
out = args[1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=blend)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
if scene.world is None:
    scene.world = bpy.data.worlds.new("segmentation diagnostic world")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.12, 0.12, 0.12, 1.0)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35

def area_light(name, location, energy, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    light = bpy.data.objects.new(name, data)
    scene.collection.objects.link(light)
    light.location = location
    light.rotation_euler = (Vector((0, 0, 0)) - light.location).to_track_quat("-Z", "Y").to_euler()

area_light("diagnostic key", (-1.0, -1.5, 2.0), 120, 2.0)
area_light("diagnostic fill", (1.5, -0.8, 1.0), 80, 1.5)
area_light("diagnostic rim", (0.0, 1.2, 1.8), 140, 1.5)

colors = {
    "front-crt-control": (0.06, 0.30, 0.90, 1.0),
    "keyboard-deck": (0.90, 0.72, 0.12, 1.0),
    "front-tape-controls": (0.12, 0.70, 0.28, 1.0),
    "upper-case": (0.70, 0.38, 0.10, 1.0),
    "rear-case": (0.45, 0.18, 0.65, 1.0),
    "vertical-case": (0.70, 0.20, 0.30, 1.0),
    "case-and-trim": (0.55, 0.55, 0.55, 1.0),
}
for obj in [o for o in scene.objects if o.type == "MESH"]:
    key = next((name for name in colors if name in obj.name), "case-and-trim")
    mat = bpy.data.materials.get("diagnostic-" + key) or bpy.data.materials.new("diagnostic-" + key)
    mat.diffuse_color = colors[key]
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = colors[key]
    obj.data.materials.clear()
    obj.data.materials.append(mat)

lo = Vector((10, 10, 10)); hi = Vector((-10, -10, -10))
for obj in [o for o in scene.objects if o.type == "MESH"]:
    for corner in obj.bound_box:
        p = obj.matrix_world @ Vector(corner)
        lo.x = min(lo.x, p.x); lo.y = min(lo.y, p.y); lo.z = min(lo.z, p.z)
        hi.x = max(hi.x, p.x); hi.y = max(hi.y, p.y); hi.z = max(hi.z, p.z)
center = (lo + hi) / 2
radius = max((hi - lo).x, (hi - lo).y) * 1.4

def camera(name, location, filename):
    data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, data)
    scene.collection.objects.link(cam)
    cam.location = location
    data.lens = 58
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    scene.render.filepath = os.path.join(out, filename)
    bpy.ops.render.render(write_still=True)

for location, filename in [
    ((0.0, -radius, center.z + radius * 0.15), "segmented-front.png"),
    ((radius * 0.75, -radius, center.z + radius * 0.30), "segmented-oblique.png"),
]:
    camera(filename, location, filename)
