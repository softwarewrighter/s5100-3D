"""Validate one tape-bay candidate in the exported shell coordinate frame."""
import os, sys, bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
source, out = args[0], args[1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=source)
scene = bpy.context.scene
for obj in scene.objects:
    if obj.type == "MESH" and obj.name != "IBM 5100 continuous reference shell":
        obj.hide_render = True
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1200; scene.render.resolution_y = 800; scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.world = bpy.data.worlds.new("bay candidate world"); scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.02, 0.02, 0.02, 1.0)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25

gray = bpy.data.materials.new("candidate gray tape"); gray.use_nodes = True
gray.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.28, 0.30, 0.28, 1.0)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.12, -0.325, 0.96))
tape = bpy.context.object; tape.name = "bay candidate cartridge"; tape.dimensions = (0.10, 0.010, 0.025); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); tape.data.materials.append(gray)

def light(name, loc, energy):
    d=bpy.data.lights.new(name,"AREA"); d.energy=energy; d.size=1.4; o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc; o.rotation_euler=(Vector((0,-.25,.95))-o.location).to_track_quat("-Z","Y").to_euler()
light("bay key",(-.8,-1,1.4),130); light("bay fill",(.8,-.8,1),90)
target=Vector((0,-.25,.94))
for loc,name in [((0,-.95,.98),"bay-candidate-front.png"),((.55,-.85,1.02),"bay-candidate-right.png"),((-.55,-.85,1.02),"bay-candidate-left.png")]:
    d=bpy.data.cameras.new(name); c=bpy.data.objects.new(name,d); scene.collection.objects.link(c); c.location=loc; d.lens=70; c.rotation_euler=(target-c.location).to_track_quat("-Z","Y").to_euler(); scene.camera=c; scene.render.filepath=os.path.join(out,name); bpy.ops.render.render(write_still=True)
print("WROTE BAY CANDIDATE VIEWS",out)
