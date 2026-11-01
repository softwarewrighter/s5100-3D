"""Render a coordinate overlay for diagnosing misplaced 5100 parts.

The source Trellis frame is treated as X=left/right, Y=depth (front is
negative), and Z=up.  The grid is placed just in front of the source front
plane and is intentionally a debug artifact, never production geometry.
"""

import math
import os
import sys

import bpy
from mathutils import Vector


args = sys.argv[sys.argv.index("--") + 1:]
source = args[0]
out = args[1]
part_name = args[2] if len(args) > 2 else "refined CRT glass"
os.makedirs(out, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=source)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

if scene.world is None:
    scene.world = bpy.data.worlds.new("coordinate debug world")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.04, 0.04, 0.04, 1.0)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35


def mat(name, color, emission=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1.0)
    p.inputs["Roughness"].default_value = 0.55
    if emission:
        p.inputs["Emission Color"].default_value = (*color, 1.0)
        p.inputs["Emission Strength"].default_value = emission
    return m


grid = mat("coordinate grid", (0.04, 0.35, 0.85), 0.5)
major = mat("coordinate major grid", (0.10, 0.80, 1.0), 1.0)
xmat = mat("coordinate X axis", (0.95, 0.12, 0.08), 1.0)
ymat = mat("coordinate Y axis", (0.12, 0.85, 0.18), 1.0)
zmat = mat("coordinate Z axis", (0.16, 0.35, 1.0), 1.0)
label_mat = mat("coordinate labels", (1.0, 0.85, 0.12), 1.0)

part = bpy.data.objects.get(part_name)
if part:
    corners = [part.matrix_world @ Vector(corner) for corner in part.bound_box]
    part_lo = Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners)))
    part_hi = Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners)))
    part_center = (part_lo + part_hi) / 2.0
    print("PART", part_name, "bounds", tuple(round(v, 5) for v in part_lo), tuple(round(v, 5) for v in part_hi), "center", tuple(round(v, 5) for v in part_center))
else:
    part_lo = part_hi = part_center = Vector((0.0, 0.0, 0.0))
    print("PART NOT FOUND", part_name)


def cube(name, location, dimensions, material):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return obj


def label(text, location, size=0.014):
    data = bpy.data.curves.new("coordinate label", "FONT")
    data.body = text
    data.align_x = "CENTER"
    data.size = size
    data.extrude = 0.0003
    obj = bpy.data.objects.new("coord " + text, data)
    scene.collection.objects.link(obj)
    # Text's default normal is +Z; rotate it to face the camera at negative Y.
    obj.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
    obj.location = location
    obj.data.materials.append(label_mat)
    return obj


# Debug grid in the X/Z front plane. One small cell is 0.025 source units.
# Anchor it to the selected part so translated production scenes work too.
y = part_center.y - 0.026 if part else -0.535
xmin, xmax = part_center.x - 0.35, part_center.x + 0.35
zmin, zmax = part_center.z - 0.16, part_center.z + 0.16
step = 0.025
count = 0
x = xmin
while x <= xmax + 1e-6:
    is_major = abs(round(x / 0.1) * 0.1 - x) < 1e-5
    cube("grid x %.3f" % x, (x, y, (zmin + zmax) / 2), (0.0015 if not is_major else 0.003, 0.001, zmax - zmin), major if is_major else grid)
    if is_major:
        label("X %.2f" % x, (x, y - 0.002, zmin - 0.014), 0.010)
    x += step
z = zmin
while z <= zmax + 1e-6:
    is_major = abs(round(z / 0.1) * 0.1 - z) < 1e-5
    cube("grid z %.3f" % z, ((xmin + xmax) / 2, y, z), (xmax - xmin, 0.001, 0.0015 if not is_major else 0.003), major if is_major else grid)
    if is_major:
        label("Z %.2f" % z, (xmin - 0.025, y - 0.002, z), 0.010)
    z += step

# A Y-depth ruler at the selected part's X, with a green axis and labels showing the frontward
# direction. This is visible in the oblique view and explains front-plane drift.
for depth in (-0.55, -0.50, -0.45, -0.40, -0.35, -0.30):
    cube("depth %.2f" % depth, (part_center.x, depth, zmin - 0.015), (0.003, 0.002, 0.03), ymat)
    label("Y %.2f" % depth, (part_center.x, depth, zmin - 0.035), 0.009)
cube("origin X axis", (part_center.x, y - 0.002, part_center.z), (0.30, 0.003, 0.002), xmat)
cube("origin Z axis", (part_center.x, y - 0.002, part_center.z), (0.002, 0.003, 0.30), zmat)
label("ORIGIN", (part_center.x, y - 0.004, part_center.z + 0.018), 0.012)
cube("part center marker", (part_center.x, y - 0.004, part_center.z), (0.006, 0.004, 0.006), xmat)


def light(name, location, energy):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.size = 1.5
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector((0, 0, -0.02)) - obj.location).to_track_quat("-Z", "Y").to_euler()


light("debug key", (-1.0, -1.2, 1.2), 100)
light("debug fill", (1.0, -0.8, 0.8), 70)

target = Vector((part_center.x, part_center.y, part_center.z))
for location, filename in [
    ((part_center.x, part_center.y - 1.35, part_center.z + 0.08), "coordinate-front.png"),
    ((part_center.x + 0.70, part_center.y - 1.20, part_center.z + 0.22), "coordinate-oblique.png"),
]:
    camera_data = bpy.data.cameras.new(filename)
    camera = bpy.data.objects.new(filename, camera_data)
    scene.collection.objects.link(camera)
    camera.location = location
    camera_data.lens = 58
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    scene.render.filepath = os.path.join(out, filename)
    bpy.ops.render.render(write_still=True)

print("WROTE COORDINATE DEBUG RENDERS", out)
