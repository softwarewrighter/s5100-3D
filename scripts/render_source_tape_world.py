"""Stage the actual source loose component in the production world frame."""
import os, sys, bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
source, out = args[0], args[1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=source)
full = bpy.context.selected_objects[0]
full.name = "IBM 5100 continuous reference shell"
full.scale = (0.445 / 0.590, 0.610 / 1.0004, 0.203 / 0.2784)
full.location = (0.0, 0.0, 0.9215)

# Import a second copy, separate loose components, and retain the measured
# tape-control component from the source inventory.
bpy.ops.import_scene.gltf(filepath=source)
fragment = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = fragment
fragment.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set(mode="OBJECT")

target = Vector((0.1873 * 0.445 / 0.590, -0.4499 * 0.610 / 1.0004, 0.9215 + (-0.0559 * 0.203 / 0.2784)))
def center(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return (lo + hi) / 2

parts = [o for o in bpy.context.scene.objects if o.type == "MESH" and o is not full]
# The separated copy has no parent carrying the production transform. Apply
# the same world frame explicitly to every loose component before inspecting it.
for obj in parts:
    obj.scale = (0.445 / 0.590, 0.610 / 1.0004, 0.203 / 0.2784)
    obj.location = (0.0, 0.0, 0.9215)
chosen = min(parts, key=lambda o: (center(o) - target).length)
chosen.name = "source tape component candidate"
for o in parts:
    if o is not chosen: o.hide_render = True
mat = bpy.data.materials.new("diagnostic source tape")
mat.diffuse_color = (0.25, 0.27, 0.25, 1.0); mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.25, 0.27, 0.25, 1.0)
chosen.data.materials.clear(); chosen.data.materials.append(mat)
print("source candidate center", tuple(round(v, 5) for v in center(chosen)))

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1200; scene.render.resolution_y = 800; scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.world = bpy.data.worlds.new("source tape diagnostic world"); scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.03, 0.03, 0.03, 1.0)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25
def light(name, loc, energy):
    data=bpy.data.lights.new(name, "AREA"); data.energy=energy; data.size=1.4
    obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj); obj.location=loc
    obj.rotation_euler=(Vector((0,-.28,.90))-obj.location).to_track_quat("-Z","Y").to_euler()
light("key",(-.8,-1.0,1.4),130); light("fill",(.8,-.8,1.0),90)
target_world=Vector((0.141,-0.274,0.881))
for loc, name in [((0,-1.0,.98),"source-tape-front.png"),((.55,-.9,1.02),"source-tape-right.png"),((-.55,-.9,1.02),"source-tape-left.png")]:
    data=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,data); scene.collection.objects.link(cam)
    cam.location=loc; data.lens=70; cam.rotation_euler=(target_world-cam.location).to_track_quat("-Z","Y").to_euler()
    scene.camera=cam; scene.render.filepath=os.path.join(out,name); bpy.ops.render.render(write_still=True)
