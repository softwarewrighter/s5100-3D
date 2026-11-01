"""Render a lightweight production-coordinate placement guide.

This avoids the generated production .blend and uses the source GLB plus the
known X_eTaL transform, so placement diagnostics do not inherit old helpers or
materials.  Red is the current selector placement; cyan/orange markers are
measured candidate anchors for the CRT and tape face.
"""

import math
import os
import sys

import bpy
from mathutils import Vector


args = sys.argv[sys.argv.index("--") + 1:]
source = args[0]
out = args[1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=source)
core = bpy.context.selected_objects[0]
core.name = "5100 guide shell"
core.scale = (0.445 / 0.590, 0.610 / 1.0004, 0.203 / 0.2784)
core.location = (0.0, 0.0, 0.82 + 0.203 / 2.0)
bpy.context.view_layer.update()

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.world = bpy.data.worlds.new("panel guide world")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.035, 0.035, 0.035, 1.0)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35


def mat(name, color, emission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1.0)
    p.inputs["Roughness"].default_value = 0.45
    if emission:
        p.inputs["Emission Color"].default_value = (*color, 1.0)
        p.inputs["Emission Strength"].default_value = emission
    return m


shell_mat = mat("guide tan shell", (0.52, 0.43, 0.30))
red_mat = mat("current red selector", (0.85, 0.02, 0.01), 1.0)
cyan_mat = mat("CRT target marker", (0.02, 0.75, 1.0), 1.0)
orange_mat = mat("tape target marker", (1.0, 0.42, 0.02), 1.0)
grid_mat = mat("panel coordinate grid", (0.03, 0.55, 1.0), 0.8)
major_mat = mat("panel major grid", (0.15, 0.95, 1.0), 1.0)
label_mat = mat("panel coordinate labels", (1.0, 0.85, 0.08), 1.0)
core.data.materials.clear()
core.data.materials.append(shell_mat)


def cube(name, location, dimensions, material, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if parent:
        world = obj.matrix_world.copy()
        obj.parent = parent
        obj.matrix_world = world
    return obj


def world_from_local(local):
    return core.matrix_world @ Vector(local)


# Current selector: the exact local coordinate used by the production XTL.
red_world = world_from_local((-0.020, -0.435, -0.045))
cube("CURRENT red selector", red_world, (0.020, 0.006, 0.012), red_mat)

# Candidate anchors are markers only. They let the next part be placed against
# the same panel coordinate frame before real geometry is added.
crt_world = world_from_local((-0.145, -0.500, 0.073))
tape_world = world_from_local((0.145, -0.350, 0.080))
cube("TARGET CRT anchor", crt_world, (0.012, 0.004, 0.012), cyan_mat)
cube("TARGET tape anchor", tape_world, (0.012, 0.004, 0.012), orange_mat)
print("CURRENT RED WORLD", tuple(round(v, 5) for v in red_world))
print("TARGET CRT WORLD", tuple(round(v, 5) for v in crt_world))
print("TARGET TAPE WORLD", tuple(round(v, 5) for v in tape_world))


def label(text, location):
    data = bpy.data.curves.new("guide label", "FONT")
    data.body = text
    data.align_x = "CENTER"
    data.size = 0.015
    data.extrude = 0.0003
    obj = bpy.data.objects.new("guide " + text, data)
    scene.collection.objects.link(obj)
    obj.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
    obj.location = location
    obj.data.materials.append(label_mat)


# World-space panel grid. World front plane is approximately y=-0.31 after the
# production transform; use a slightly forward plane so it remains visible.
grid_y = -0.325
xmin, xmax = -0.30, 0.30
zmin, zmax = 0.84, 1.08
step = 0.025
x = xmin
while x <= xmax + 1e-6:
    major = abs(round(x / 0.1) * 0.1 - x) < 1e-5
    cube("panel X %.3f" % x, (x, grid_y, (zmin + zmax) / 2), (0.0015 if not major else 0.003, 0.001, zmax - zmin), major_mat if major else grid_mat)
    if major:
        label("X %.2f" % x, (x, grid_y - 0.002, zmin - 0.015))
    x += step
z = zmin
while z <= zmax + 1e-6:
    major = abs(round(z / 0.1) * 0.1 - z) < 1e-5
    cube("panel Z %.3f" % z, ((xmin + xmax) / 2, grid_y, z), (xmax - xmin, 0.001, 0.0015 if not major else 0.003), major_mat if major else grid_mat)
    if major:
        label("Z %.2f" % z, (xmin - 0.025, grid_y - 0.002, z))
    z += step
label("RED", red_world + Vector((0, -0.004, 0.018)))
label("CRT", crt_world + Vector((0, -0.004, 0.018)))
label("TAPE", tape_world + Vector((0, -0.004, 0.018)))


def area(name, location, energy):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.size = 1.5
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector((0, -0.2, 0.92)) - obj.location).to_track_quat("-Z", "Y").to_euler()


area("guide key", (-1.0, -1.2, 1.5), 100)
area("guide fill", (1.0, -0.8, 1.0), 70)

target = Vector((0, -0.25, 0.94))
for location, filename in [
    ((0.0, -1.15, 1.02), "panel-guides-front.png"),
    ((0.62, -1.0, 1.14), "panel-guides-oblique.png"),
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

print("WROTE PANEL GUIDE RENDERS", out)
