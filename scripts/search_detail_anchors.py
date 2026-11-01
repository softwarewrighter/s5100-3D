"""Render a small labeled world-space search grid for a detail anchor."""
import math
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
    if obj.type == "MESH" and obj.name not in ("IBM 5100 continuous reference shell",):
        obj.hide_render = True
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1200
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = -1.5
scene.world = bpy.data.worlds.new("anchor search world")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.02, 0.02, 0.02, 1.0)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.2

def mat(name, color):
    m = bpy.data.materials.new(name); m.diffuse_color = (*color, 1.0); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]; p.inputs["Base Color"].default_value = (*color, 1.0); p.inputs["Emission Color"].default_value = (*color, 1.0); p.inputs["Emission Strength"].default_value = 1.2
    return m

colors = [mat("candidate y0", (1.0, 0.05, 0.02)), mat("candidate y1", (1.0, 0.45, 0.02)), mat("candidate y2", (1.0, 0.95, 0.02))]
label_mat = mat("candidate label", (0.2, 0.9, 1.0))

def cube(name, location, dimensions, material):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    o = bpy.context.object; o.name = name; o.dimensions = dimensions; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); o.data.materials.append(material); return o

def label(text, location):
    d = bpy.data.curves.new("candidate label", "FONT"); d.body = text; d.align_x = "CENTER"; d.size = 0.012; d.extrude = 0.0002
    o = bpy.data.objects.new("label " + text, d); scene.collection.objects.link(o); o.location = location; o.rotation_euler = (math.pi / 2, 0, 0); o.data.materials.append(label_mat)

# Candidate centers in exported/world coordinates. Columns vary Y depth;
# rows vary Z. The labels make the chosen point reproducible.
xs = (-0.04, 0.0, 0.04)
zs = (0.92, 0.94, 0.96)
ys = (-0.31, -0.28, -0.25)
for xi, x in enumerate(xs):
    for yi, y in enumerate(ys):
        for zi, z in enumerate(zs):
            name = "R%d%d%d" % (xi, yi, zi)
            cube(name, (x, y, z), (0.010, 0.007, 0.010), colors[yi])
            label(name, (x, y - 0.006, z + 0.012))

def area(name, location, energy):
    d = bpy.data.lights.new(name, "AREA"); d.energy = energy; d.size = 1.2
    o = bpy.data.objects.new(name, d); scene.collection.objects.link(o); o.location = location; o.rotation_euler = (Vector((0, -0.25, 0.93)) - o.location).to_track_quat("-Z", "Y").to_euler()
area("search key", (-0.8, -1.0, 1.4), 100); area("search fill", (0.8, -0.8, 1.0), 80)
target = Vector((0, -0.25, 0.93))
for location, filename in [((0, -0.95, 0.98), "anchor-search-front.png"), ((0.55, -0.85, 1.02), "anchor-search-oblique.png"), ((-0.55, -0.85, 1.02), "anchor-search-left.png")]:
    d = bpy.data.cameras.new(filename); c = bpy.data.objects.new(filename, d); scene.collection.objects.link(c); c.location = location; d.lens = 70; c.rotation_euler = (target - c.location).to_track_quat("-Z", "Y").to_euler(); scene.camera = c; scene.render.filepath = os.path.join(out, filename); bpy.ops.render.render(write_still=True)
print("WROTE ANCHOR SEARCH", out)
