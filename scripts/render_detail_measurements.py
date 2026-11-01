"""Measure exported detail placement with grid, labels, and Y drop lines."""
import math, os, sys
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
source, out = args[0], args[1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=source)
scene = bpy.context.scene
for obj in scene.objects:
    if obj.type == "MESH" and obj.name not in ("IBM 5100 continuous reference shell", "Local gray inserted tape"):
        obj.hide_render = True
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1400
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = -1.0
scene.world = bpy.data.worlds.new("measurement world")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.02, 0.02, 0.02, 1.0)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25

def mat(name, color):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1.0)
    p.inputs["Emission Color"].default_value = (*color, 1.0)
    p.inputs["Emission Strength"].default_value = 1.0
    return m

grid = mat("measurement grid", (0.05, 0.45, 1.0))
major = mat("measurement major", (0.10, 0.90, 1.0))
orange = mat("measurement tape", (1.0, 0.25, 0.02))
green = mat("measurement target", (0.2, 1.0, 0.2))
yellow = mat("measurement labels", (1.0, 0.9, 0.1))

def cube(name, loc, dims, material):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.object; o.name = name; o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    return o

def label(text, loc, size=0.012):
    d = bpy.data.curves.new("measurement label", "FONT")
    d.body = text; d.align_x = "CENTER"; d.size = size; d.extrude = 0.0002
    o = bpy.data.objects.new(text, d); scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (math.pi / 2, 0, 0); o.data.materials.append(yellow)

front_y = -0.325
xmin, xmax, zmin, zmax, step = -0.30, 0.30, 0.82, 1.08, 0.025
x = xmin
while x <= xmax + 1e-6:
    is_major = abs(round(x / 0.1) * 0.1 - x) < 1e-5
    cube("grid X %.3f" % x, (x, front_y, (zmin + zmax) / 2), (0.002 if is_major else 0.001, 0.001, zmax - zmin), major if is_major else grid)
    if is_major: label("X=%.2f" % x, (x, front_y - 0.004, zmin - 0.016))
    x += step
z = zmin
while z <= zmax + 1e-6:
    is_major = abs(round(z / 0.1) * 0.1 - z) < 1e-5
    cube("grid Z %.3f" % z, ((xmin + xmax) / 2, front_y, z), (xmax - xmin, 0.001, 0.002 if is_major else 0.001), major if is_major else grid)
    if is_major: label("Z=%.2f" % z, (xmin - 0.035, front_y - 0.004, z))
    z += step

tape = bpy.data.objects.get("Local gray inserted tape")
if tape:
    points = [tape.matrix_world @ Vector(c) for c in tape.bound_box]
    center = sum(points, Vector()) / 8.0
    cube("tape center", center, (0.012, 0.012, 0.012), orange)
    cube("tape depth drop", (center.x, (center.y + front_y) / 2, center.z), (0.003, abs(center.y - front_y), 0.003), orange)
    label("TAPE", center + Vector((0, -0.008, 0.018)))
    label("dY=%.3f" % (center.y - front_y), (center.x, (center.y + front_y) / 2, center.z + 0.025), 0.010)
    print("TAPE CENTER", tuple(round(v, 5) for v in center), "dY", round(center.y - front_y, 5))

bay = Vector((0.12, front_y, 0.96))
cube("bay target", bay, (0.016, 0.006, 0.016), green)
label("BAY TARGET", bay + Vector((0, -0.006, 0.018)))

def light(name, loc, energy):
    d = bpy.data.lights.new(name, "AREA"); d.energy = energy; d.size = 1.3
    o = bpy.data.objects.new(name, d); scene.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, -0.25, 0.94)) - o.location).to_track_quat("-Z", "Y").to_euler()

light("measurement key", (-0.8, -1.0, 1.4), 120)
light("measurement fill", (0.8, -0.8, 1.0), 90)
target = Vector((0, -0.25, 0.94))
for loc, name in [((0, -0.95, 0.98), "measure-front.png"), ((0.55, -0.85, 1.02), "measure-right.png"), ((-0.55, -0.85, 1.02), "measure-left.png")]:
    d = bpy.data.cameras.new(name); c = bpy.data.objects.new(name, d); scene.collection.objects.link(c)
    c.location = loc; d.lens = 70; c.rotation_euler = (target - c.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = c; scene.render.filepath = os.path.join(out, name); bpy.ops.render.render(write_still=True)
print("WROTE MEASUREMENT VIEWS", out)
