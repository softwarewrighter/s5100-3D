"""Stage a CRT-face refinement on the segmented IBM 5100 source model.

The source GLB uses approximately x=width, y=depth (front is negative), and
z=height.  This pass deliberately adds only the CRT bezel/glass candidate;
the original parts remain present so the result can be rejected without loss.
"""

import os
import sys

import bpy
from mathutils import Vector


args = sys.argv[sys.argv.index("--") + 1:]
source = args[0]
out = args[1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=source)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

if scene.world is None:
    scene.world = bpy.data.worlds.new("CRT refinement world")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.10, 0.10, 0.10, 1.0)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.30


def material(name, color, roughness=0.35, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    return mat


tan = material("CRT refinement tan bezel", (0.50, 0.43, 0.32), 0.42)
glass = material("CRT refinement dark glass", (0.006, 0.010, 0.009), 0.18)
phosphor = material("CRT refinement inactive phosphor", (0.015, 0.035, 0.025), 0.25)


def cube(name, location, dimensions, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("rounded molded edge", "BEVEL")
        mod.width = bevel
        mod.segments = 3
    return obj


# Coordinates are in the unscaled Trellis source frame.  The CRT face is
# recessed behind the front lip (the diagnostic bounds span y=-0.50..-0.31),
# so it must live near the recessed face at y=-0.32 rather than on the outer
# shell plane.  This also avoids the camera pitching the candidate downward.
cx, cy, cz = -0.145, -0.507, 0.073
width, height = 0.218, 0.118
bar = 0.014
depth = 0.012

cube("refined CRT glass", (cx, cy - 0.002, cz), (width - 2 * bar, depth, height - 2 * bar), glass, 0.008)
cube("refined CRT phosphor inset", (cx, cy - 0.009, cz), (width - 2 * bar - 0.012, 0.002, height - 2 * bar - 0.012), phosphor, 0.006)
cube("refined CRT bezel top", (cx, cy - 0.006, cz + height / 2 - bar / 2), (width, depth, bar), tan, 0.004)
cube("refined CRT bezel bottom", (cx, cy - 0.006, cz - height / 2 + bar / 2), (width, depth, bar), tan, 0.004)
cube("refined CRT bezel left", (cx - width / 2 + bar / 2, cy - 0.006, cz), (bar, depth, height - 2 * bar), tan, 0.004)
cube("refined CRT bezel right", (cx + width / 2 - bar / 2, cy - 0.006, cz), (bar, depth, height - 2 * bar), tan, 0.004)


def area(name, location, energy, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector((0, -0.1, -0.02)) - obj.location).to_track_quat("-Z", "Y").to_euler()


area("CRT key", (-1.0, -1.4, 1.2), 100, 1.6)
area("CRT fill", (1.0, -0.8, 0.8), 70, 1.4)

target = Vector((0.0, 0.0, -0.01))
locations = [
    ((0.0, -1.35, 0.12), "crt-refined-front.png"),
    ((0.70, -1.20, 0.24), "crt-refined-oblique.png"),
]
for location, filename in locations:
    data = bpy.data.cameras.new(filename)
    camera = bpy.data.objects.new(filename, data)
    scene.collection.objects.link(camera)
    camera.location = location
    data.lens = 58
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    scene.render.filepath = os.path.join(out, filename)
    bpy.ops.render.render(write_still=True)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "crt-refined-candidate.blend"))
print("WROTE CRT REFINEMENT CANDIDATE", out)
