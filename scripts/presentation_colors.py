"""Presentation palette in the original Trellis local coordinate frame.

Only raised keyboard surfaces and the recessed CRT interior receive accents;
keep the enclosure, bevels, transforms, cameras, and lights intact.
"""
import bpy


def material(name, rgb, roughness):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*rgb, 1)
    shader = mat.node_tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value = (*rgb, 1)
    shader.inputs['Roughness'].default_value = roughness
    return mat


core = bpy.data.objects['IBM 5100 continuous reference shell']
white = material('IBM 5100 presentation white keys', (0.95, 0.95, 0.95), 0.38)
screen = material('IBM 5100 presentation dark gray screen', (0.055, 0.055, 0.055), 0.32)
core.data.materials.append(white)
key_index = len(core.data.materials) - 1
core.data.materials.append(screen)
screen_index = len(core.data.materials) - 1
counts = [0, 0]
for face in core.data.polygons:
    x, y, z = face.center
    # Raised key surfaces on the sloped deck, above the recessed keyboard bed.
    deck_height = -0.060 + (y + 0.46) * 0.32
    if -0.255 < x < 0.255 and -0.485 < y < -0.335 and deck_height + 0.012 < z < deck_height + 0.045 and face.normal.z > 0.35:
        face.material_index = key_index
        counts[0] += 1
    # Inset CRT face beneath the top enclosure, behind its molded surround.
    if -0.240 < x < -0.080 and -0.289 < y < -0.260 and 0.020 < z < 0.105 and face.normal.y < -0.45:
        face.material_index = screen_index
        counts[1] += 1
print('Presentation key / CRT faces:', counts)
assert all(counts), 'Presentation regions must contain geometry'
table = material('Light gray presentation table', (0.63, 0.63, 0.63), 0.55)
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH' and obj.name.startswith('table '):
        obj.data.materials.clear()
        obj.data.materials.append(table)
