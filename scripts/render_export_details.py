"""Close-up front/oblique validation of exported detail placement."""
import os
import sys
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
source, out = args[0], args[1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=source)
scene = bpy.context.scene
for obj in scene.objects:
    if obj.type == "MESH" and obj.name not in ("IBM 5100 continuous reference shell", "Local red selector test", "Local gray inserted tape", "Measured red power switch", "Measured gray DC300 cartridge"):
        obj.hide_render = True
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1200
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.world = bpy.data.worlds.new("detail validation world")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.025, 0.025, 0.025, 1.0)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.3

def material(name, color):
    m = bpy.data.materials.new(name); m.diffuse_color = (*color, 1.0); m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1.0)
    return m

red = material("validation red", (0.85, 0.01, 0.005))
gray = material("validation gray", (0.34, 0.35, 0.33))
for name, mat in (("Local red selector test", red), ("Local gray inserted tape", gray), ("Measured red power switch", red), ("Measured gray DC300 cartridge", gray)):
    obj = bpy.data.objects.get(name)
    if obj:
        obj.data.materials.clear(); obj.data.materials.append(mat)

def area(name, location, energy):
    data = bpy.data.lights.new(name, "AREA"); data.energy = energy; data.size = 1.2
    obj = bpy.data.objects.new(name, data); scene.collection.objects.link(obj); obj.location = location
    obj.rotation_euler = (Vector((0, -0.25, 0.92)) - obj.location).to_track_quat("-Z", "Y").to_euler()

area("validation key", (-0.7, -1.0, 1.4), 180)
area("validation fill", (0.8, -0.8, 1.0), 120)
target = Vector((0.0, -0.25, 0.93))
for location, filename in [
    ((0.0, -0.95, 0.98), "export-details-front.png"),
    ((0.55, -0.85, 1.02), "export-details-oblique.png"),
    ((-0.55, -0.85, 1.02), "export-details-left.png"),
]:
    data = bpy.data.cameras.new(filename); cam = bpy.data.objects.new(filename, data); scene.collection.objects.link(cam)
    cam.location = location; data.lens = 70; cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam; scene.render.filepath = os.path.join(out, filename); bpy.ops.render.render(write_still=True)
print("WROTE", out)
