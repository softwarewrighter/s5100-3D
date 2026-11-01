import bpy
import os
import sys
from mathutils import Vector


def bounds(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    lo = Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners)))
    hi = Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners)))
    return lo, hi


def region(obj):
    lo, hi = bounds(obj)
    center = (lo + hi) / 2
    size = hi - lo
    if center.y < -0.40 and center.x < -0.02 and -0.14 < center.z < 0.02:
        return "front-crt-control"
    if center.y < -0.28 and center.z < -0.07:
        return "keyboard-deck"
    if center.y < -0.40 and center.x > 0.02 and -0.14 < center.z < 0.03:
        return "front-tape-controls"
    if center.z > 0.02:
        return "upper-case"
    if center.y > 0.15:
        return "rear-case"
    if size.z > size.x * 1.5:
        return "vertical-case"
    return "case-and-trim"


args = sys.argv[sys.argv.index("--") + 1:]
source = args[0] if args else "references/trellis5100-reference.glb"
output_dir = args[1] if len(args) > 1 else "work/ibm5100/parts"
os.makedirs(output_dir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=source)
source_mesh = bpy.data.objects.get("geometry_0")
if source_mesh is None:
    raise RuntimeError("geometry_0 was not found in the reference GLB")

bpy.context.view_layer.objects.active = source_mesh
source_mesh.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set(mode="OBJECT")

root = bpy.data.collections.new("IBM 5100 semantic part inventory")
bpy.context.scene.collection.children.link(root)
collections = {}
for name in ("front-crt-control", "keyboard-deck", "front-tape-controls", "upper-case", "rear-case", "vertical-case", "case-and-trim"):
    collection = bpy.data.collections.new(name)
    root.children.link(collection)
    collections[name] = collection

parts = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj.name.startswith("geometry_0")]
rows = []
for index, obj in enumerate(parts, 1):
    group = region(obj)
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    collections[group].objects.link(obj)
    obj.name = f"{group} part {index:04d}"
    lo, hi = bounds(obj)
    size = hi - lo
    center = (lo + hi) / 2
    rows.append((group, obj.name, len(obj.data.vertices), len(obj.data.polygons), size.x, size.y, size.z, center.x, center.y, center.z))

rows.sort(key=lambda row: (row[0], -row[2]))
report = os.path.join(output_dir, "parts-report.txt")
with open(report, "w", encoding="utf-8") as stream:
    stream.write("IBM 5100 Trellis loose-part inventory\n")
    stream.write(f"source: {source}\n")
    stream.write(f"parts: {len(rows)}\n\n")
    current = None
    for row in rows:
        if row[0] != current:
            current = row[0]
            stream.write(f"[{current}]\n")
        stream.write("  %s verts=%d faces=%d size=(%.4f, %.4f, %.4f) center=(%.4f, %.4f, %.4f)\n" % (row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))

for group, collection in collections.items():
    members = [obj for obj in collection.objects if obj.type == "MESH"]
    if not members:
        continue
    bpy.ops.object.select_all(action="DESELECT")
    for obj in members:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = members[0]
    bpy.ops.object.join()
    members[0].name = f"IBM 5100 {group} assembly"

# Export each joined assembly as an independently inspectable GLB.  These are
# staging artifacts: the original reference remains the source of truth until
# a part passes both front and oblique checks and is deliberately recombined.
for group, collection in collections.items():
    assembly = bpy.data.objects.get(f"IBM 5100 {group} assembly")
    if assembly is None:
        continue
    bpy.ops.object.select_all(action="DESELECT")
    assembly.select_set(True)
    bpy.context.view_layer.objects.active = assembly
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(output_dir, f"{group}.glb"),
        export_format="GLB",
        use_selection=True,
        export_materials="EXPORT",
    )

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(output_dir, "ibm5100-parts.blend"))
print(f"WROTE {len(rows)} parts to {output_dir}")
print(f"REPORT {report}")
