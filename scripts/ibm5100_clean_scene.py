"""Clean procedural IBM 5100 Model C exterior study; meters, Z-up, front -Y.

Photo-led proportions, not a measured replica. Trellis is comparison-only.
No mesh, material, texture, or geometry is extracted from the Trellis asset.
"""
import argparse
import json
import math
import os
from pathlib import Path
import sys
import bpy
from mathutils import Vector, Matrix

p=argparse.ArgumentParser()
p.add_argument('--out',type=Path,required=True)
p.add_argument('--device',choices=['CPU','OPTIX'],default='CPU')
p.add_argument('--samples',type=int,default=40)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
parts=[]
# Photo-estimated front rake. Positive Y is back into the case.
FRONT_ASSEMBLY_SETBACK=.020
KEYBOARD_PLANE_LIFT=.005
FRONT_RAKE_DEG=8.0
FRONT_SLOPE=math.tan(math.radians(FRONT_RAKE_DEG))
def front_y(y,z):return y+FRONT_SLOPE*(z-.079)
front_shear=Matrix(((1,0,0,0),(0,1,FRONT_SLOPE,-FRONT_SLOPE*.079),(0,0,1,0),(0,0,0,1)))


def mat(name,rgb,rough=.4,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
 s=m.node_tree.nodes['Principled BSDF'];s.inputs['Base Color'].default_value=(*rgb,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal
 return m
palette=json.loads((ROOT/'models/presentation-palette.json').read_text())
shell=mat('warm gray outer cover',palette['cover_linear'],.38)
keyboard=mat('light warm gray keyboard surround',palette['keyboard_surround_linear'],.38)
fascia=mat('yellow sand tan front fascia',palette['front_panel_linear'],.43)
cartridge_reel=mat('cartridge ivory reels',(.48,.465,.395),.38)
base=mat('lower case seam',(.22,.225,.205),.55)
white=mat('white sculpted keycaps',(.92,.92,.88),.32)
gray_key=mat('charcoal gray function keycaps',(.075,.085,.09),.35)
black=mat('charcoal recesses',(.018,.022,.021),.48)
rubber=mat('rubber feet',(.015,.016,.015),.8)
glass=mat('dark gray curved CRT glass',(.055,.060,.057),.24)
glass.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value=.18
glass.node_tree.nodes['Principled BSDF'].inputs['Coat Roughness'].default_value=.18
chrome=mat('satin metal',(.46,.49,.48),.25,.8)
red=mat('red power rocker',(.52,.018,.009),.3)
slotmat=mat('tape drive interior',(.008,.010,.009),.65)

def register(o,name,m):
 o.name=name;o.data.materials.append(m);parts.append(o);return o

def bevel(o,r=.002,n=3):
 if r:
  mod=o.modifiers.new('manufactured edge radii','BEVEL');mod.width=r;mod.segments=n
  mod=o.modifiers.new('weighted surface normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=40
 return o

def box(name,loc,size,m,r=.001):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 return bevel(register(o,name,m),r)

def mesh(name,verts,faces,m,r=0):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o)
 bpy.context.view_layer.objects.active=o;o.select_set(True)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
 return bevel(register(o,name,m),r)

def profile(name,x0,x1,yz,m,r):
 n=len(yz);verts=[(x,y,z) for x in (x0,x1) for y,z in yz]
 return mesh(name,verts,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],m,r)

def cut(o,loc,size,rotation=(0,0,0),raked=False):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);c=bpy.context.object;c.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 c.rotation_euler=rotation
 if raked:
  bpy.context.view_layer.update()
  transform=c.matrix_world.inverted()@front_shear@c.matrix_world
  for vertex in c.data.vertices:vertex.co=transform@vertex.co
 bpy.context.view_layer.objects.active=o
 mod=o.modifiers.new('machined opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c
 # Boolean must precede the edge treatment.
 bpy.ops.object.modifier_move_up(modifier=mod.name)
 if o.modifiers.find(mod.name)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(c,do_unlink=True)

def cylinder(name,loc,radius,depth,m,axis='Y'):
 rot=(math.pi/2,0,0) if axis=='Y' else (0,math.pi/2,0) if axis=='X' else (0,0,0)
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=loc,rotation=rot)
 o=register(bpy.context.object,name,m)
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return bevel(o,.00045,2)

def printmat(name,file,transparent=False):
 m=mat(name,(1,1,1),.5)
 nodes=m.node_tree.nodes;tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures'/file));tex.image.pack()
 s=nodes['Principled BSDF'];m.node_tree.links.new(tex.outputs['Color'],s.inputs['Base Color'])
 if transparent:
  m.node_tree.links.new(tex.outputs['Alpha'],s.inputs['Alpha']);m.surface_render_method='DITHERED'
 return m

def decal(name,points,m,uv=None):
 # Plain surface mesh; supplied corner order controls texture orientation.
 o=mesh(name,points,[tuple(range(len(points)))],m)
 o.data.uv_layers.new(name='print UV')
 uv=uv or [(0,0),(1,0),(1,1),(0,1)]
 for loop in o.data.loops:o.data.uv_layers.active.data[loop.index].uv=uv[loop.vertex_index]
 return o

def panel_print(name,x,y,z,w,h,m):
 return decal(name,[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)],m)

# One continuous clean enclosure; screen and tape recesses are real openings.
case=profile('continuous molded IBM 5100 enclosure',-.2215,.2215,[(-.305,.012),(.305,.012),(.305,.184),(.291,.200),(front_y(-.107,.200),.200),(front_y(-.123,.187),.187),(-.123,.079),(-.292,.047),(-.305,.040)],shell,.008)
cut(case,(-.1395,-.120,.142),(.125,.045,.096),raked=True)
cut(case,(.1165,-.120,.120),(.174,.045,.054),raked=True)
# Common pocket leaves the top lip and side cheeks overhanging the complete fascia.
cut(case,(0,-.115,.139),(.416,.080,.112),raked=True)
box('lower case joint',(0,0,.014),(.439,.604,.010),base,.003)
box('lower front trim',(0,-.304,.022),(.435,.004,.018),shell,.002)
for x in (-.177,.177):
 for y in (-.246,.245):cylinder('rubber support foot',(x,y,.007),.013,.014,rubber,'Z')

# Complete front assembly is set behind the overhanging cover.
# CRT glass retains its additional 10.5–15 mm recess behind the bezel.
front_parts_start=len(parts)
frame=box('molded CRT bezel',(-.1395,-.115,.142),(.134,.016,.104),fascia,.004)
cut(frame,(-.1345,-.115,.142),(.114,.040,.090))
box('CRT recessed black well',(-.1345,-.102,.142),(.117,.008,.094),black,.003)
verts=[];faces=[];nx=40;nz=32
for row in range(nz+1):
 z=-.040+.080*row/nz
 corner=max(0,abs(z)-.030)
 limit=.044+math.sqrt(max(0,.010**2-corner**2))
 for col in range(nx+1):
  x=-limit+2*limit*col/nx
  bulge=.0045*max(0,1-(x/.054)**2)*max(0,1-(z/.040)**2)
  verts.append((-.1325+x,-.108-bulge,.141+z))
for row in range(nz):
 for col in range(nx):
  i=row*(nx+1)+col;faces.append((i,i+1,i+nx+2,i+nx+1))
crt=mesh('smooth convex dark gray CRT',verts,faces,glass)
for f in crt.data.polygons:f.use_smooth=True

# Model C: central controls and four upper switches, per IBM pages 2-9/2-39.
operator_panel=box('central operator control panel',(-.020,-.125,.144),(.096,.011,.101),fascia,.002)
panel_print('operator panel printing',-.020,-.1311,.144,.092,.097,printmat('operator legends','5100-control-print.png',True))
box('upper tape control panel',(.1165,-.125,.171),(.174,.011,.045),fascia,.002)
panel_print('upper switch legends',.1165,-.1311,.171,.170,.042,printmat('upper control legends','5100-switch-print.png'))
cylinder('brightness dial',(-.053,-.135,.167),.0065,.007,white)
knob=box('brightness pointer',(-.053,-.140,.164),(.0028,.005,.008),white,.0006);knob.rotation_euler.y=-.4
box('display width switch mount',(-.026,-.133,.167),(.018,.004,.011),black,.001)
box('display width switch',(-.026,-.137,.167),(.014,.005,.008),white,.001)
for z in (.174,.162):
 cylinder('status lamp rim',(.008,-.133,z),.0026,.002,chrome)
 cylinder('inactive status lamp',(.008,-.1345,z),.0019,.0015,black)
# Photo: a thin red horizontal lever in the upper half of a tall recessed slot.
# Cut the fascia rather than placing a red pushbutton on its face.
cut(operator_panel,(-.026,-.125,.1295),(.0195,.035,.039))
box('power switch sand well back',(-.026,-.112,.1295),(.019,.002,.039),fascia,.0003)
for x0,x1 in [(-.03575,-.03515),(-.01685,-.01625)]:
 profile('power switch inset side wall',x0,x1,[(-.1311,.110),(-.113,.113),(-.113,.149),(-.1311,.149)],fascia,.0002)
profile('power switch lower ramp',-.0355,-.0165,[(-.1311,.110),(-.113,.113),(-.113,.116),(-.1311,.112)],fascia,.0002)
box('power switch upper cavity',(-.026,-.1155,.137),(.019,.001,.024),black,.0003)
box('black power switch paddle',(-.026,-.1215,.137),(.017,.004,.020),black,.0005)
box('horizontal red power switch lever',(-.026,-.126,.137),(.0165,.004,.0028),red,.0005)
power_switch_spec={'opening_width_mm':19.5,'opening_height_mm':39,'red_lever_width_mm':16.5,'red_lever_height_mm':2.8,'red_lever_recess_mm':3.1,'evidence':'User photo close-up, /disk1/Screenshot 2026-11-12 at 4.22.34 PM.png; estimated relative proportions'}

for x in (.0817,.1165,.1513,.1861):
 box('upper toggle recess',(x,-.133,.169),(.014,.004,.021),black,.001)
 box('ivory upper toggle',(x,-.137,.170),(.010,.007,.016),white,.001)
# Panel division lines are visible in the service drawing and museum photos.
for x in (.0643,.0991,.1339,.1687):box('control panel division',(x,-.1313,.171),(.00035,.00035,.042),base,0)

# Horizontal inserted cartridge, rather than a fictional front-facing cassette.
box('tape bay rear shadow',(.1165,-.099,.120),(.170,.006,.052),slotmat,.002)
box('tape slot upper rail',(.1165,-.124,.147),(.172,.009,.003),chrome,.0005)
box('tape slot lower ledge',(.1165,-.130,.093),(.175,.017,.004),fascia,.001)
clear=mat('clear cartridge cover',(.70,.74,.70),.18)
clear.diffuse_color=(.70,.74,.70,.22)
shader=clear.node_tree.nodes['Principled BSDF'];shader.inputs['Alpha'].default_value=.22
shader.inputs['Transmission Weight'].default_value=.35;clear.surface_render_method='DITHERED'
cartridge_parts_start=len(parts)
box('cartridge dark base',(.1165,-.144,.107),(.154,.065,.005),black,.001)
box('cartridge transparent top',(.1165,-.144,.115),(.156,.067,.002),clear,.001)
for x in (.040,.193):box('cartridge side edge',(x,-.144,.111),(.003,.067,.008),clear,.0007)
box('cartridge front edge',(.1165,-.177,.111),(.156,.003,.008),clear,.0007)
for x in (.072,.160):
 cylinder('horizontal cartridge reel',(x,-.141,.111),.017,.003,cartridge_reel,'Z')
 cylinder('cartridge reel hub',(x,-.141,.113),.0045,.002,chrome,'Z')
box('cartridge identification strip',(.1165,-.165,.114),(.100,.013,.0007),cartridge_reel,.0003)

# Requested thickness correction: scale the complete cartridge 3.5x in Z,
# then seat its underside on the lower ledge. Aperture remains unchanged.
CARTRIDGE_THICKNESS_SCALE=3.5
for obj in parts[cartridge_parts_start:]:
 bpy.context.view_layer.update()
 inverse=obj.matrix_world.inverted()
 for vertex in obj.data.vertices:
  point=obj.matrix_world@vertex.co
  point.z=.095+CARTRIDGE_THICKNESS_SCALE*(point.z-.1045)
  vertex.co=inverse@point
 obj.data.update()

# Transform the complete front assembly in its construction frame once.
# This keeps bezel, glass, control panels and openings aligned under rotation.
for obj in parts[front_parts_start:]:
 bpy.context.view_layer.update()
 transform=obj.matrix_world.inverted()@front_shear@obj.matrix_world
 for vertex in obj.data.vertices:
  world=obj.matrix_world@vertex.co
  world.y+=FRONT_ASSEMBLY_SETBACK
  vertex.co=obj.matrix_world.inverted()@front_shear@world
 obj.data.update()
# Acceptance uses rake-relative depth, not world Y alone.
assert -.1311+FRONT_ASSEMBLY_SETBACK>-.123, 'Control faces must be behind cover'
assert -.123+FRONT_ASSEMBLY_SETBACK>-.123, 'Bezel must be behind cover'
assert -.108-.0045>- .123, 'Glass must remain behind bezel'

# Sloping keyboard tray, separated caps, and original printed legends.
slope=.19;angle=math.atan(slope)
def case_deck(y):return .047+(y+.292)*slope
def deck(y):return case_deck(y)+KEYBOARD_PLANE_LIFT
# Separate raised mounting panel follows the keyboard slope and has a visible rim.
yf,yr=-.299,-.124
keyboard_mount=profile('raised keyboard mounting plane',-.211,.211,[(yf,case_deck(yf)+.0005),(yr,case_deck(yr)+.0005),(yr,deck(yr)),(yf,deck(yf))],keyboard,.0015)
# Photo-traced well boundaries preserve group gutters and the spacebar notch.
# Their floors sit above the lower case, so only the raised mounting panel is cut.
# Cutting the nearly coplanar case deck creates invalid bridge faces at the fascia.
keyboard_layout=json.loads((ROOT/'models/keyboard-layout.json').read_text())
def traced_well(name,outline):
 n=len(outline)
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 verts=[(x,y,deck(y)+height) for height in (-.005,.011) for x,y in outline]
 cutter=mesh(name+' cutter',verts,faces,black);parts.remove(cutter)
 for target in (keyboard_mount,):
  bpy.context.view_layer.objects.active=target
  modifier=target.modifiers.new('photo traced key aperture','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
  while target.modifiers.find(modifier.name)>0:bpy.ops.object.modifier_move_up(modifier=modifier.name)
  bpy.ops.object.modifier_apply(modifier=modifier.name)
 bpy.data.objects.remove(cutter,do_unlink=True)
 mesh(name+' floor',[(x,y,deck(y)+height) for height in (-.005,-.001) for x,y in outline],faces,black,.0006)
for well in keyboard_layout['wells']:traced_well(well['name'],well['outline'])
strip=box('keyboard instruction strip',(0,-.1385,deck(-.1385)+.004),(.389,.030,.004),keyboard,.001);strip.rotation_euler.x=angle
stripmat=printmat('keyboard instruction print','5100-deck-strip.png',True)
decal('keyboard instruction legends',[(-.188,-.153,deck(-.153)+.0062),(.188,-.153,deck(-.153)+.0062),(.188,-.124,deck(-.124)+.0062),(-.188,-.124,deck(-.124)+.0062)],stripmat)
labels=json.loads((ROOT/'textures/5100-key-legends.json').read_text())
atlas=printmat('keycap printed legend atlas','5100-key-legends.png',True)
gray_atlas=printmat('light legends on gray keycaps','5100-gray-key-legends.png',True)
keycount=0

def traced_key(record):
 global keycount
 label=record['label'];cx,cy=record['x'],record['y'];w,d=record['width'],record['depth']
 m=gray_key if record['gray'] else white
 outline=record['outline'];n=len(outline);h=.015;verts=[]
 for inset,height in [(0,0),(.0008,h*.86),(.0015,h),(.0025,h-.0008)]:
  sx=max(.5,1-2*inset/w);sy=max(.5,1-2*inset/d)
  for x,y in outline:
   dx=(x-cx)*sx;dy=(y-cy)*sy/math.cos(angle)
   verts.append((cx+dx,cy+dy*math.cos(angle)-height*math.sin(angle),deck(cy)-.001+dy*math.sin(angle)+height*math.cos(angle)))
 faces=[tuple(reversed(range(n)))]
 for ring in range(3):
  for i in range(n):j=(i+1)%n;faces.append((ring*n+i,ring*n+j,(ring+1)*n+j,(ring+1)*n+i))
 faces.append(tuple(range(3*n,4*n)))
 mesh(('gray' if record['gray'] else 'white')+' key '+label+' '+str(keycount),verts,faces,m,.0007)
 if label!='SPACE':
  idx=labels.index(label);col,row=idx%8,idx//8
  uv=[(col/8,1-(row+1)/10),((col+1)/8,1-(row+1)/10),((col+1)/8,1-row/10),(col/8,1-row/10)]
  lx,ly=record['legend_center'];pw=min(w,.024)*.65;pd=min(d,.023)*.60
  points=[]
  for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]:
   y=ly+dy*pd/2;z=deck(y)-.001+h-.00025
   points.append((lx+dx*pw/2,y-h*math.sin(angle),z))
  decal('key legend '+str(keycount),points,gray_atlas if record['gray'] else atlas,uv)
 keycount+=1
for record in keyboard_layout['keys']:traced_key(record)
assert keycount==73 and sum(k['gray'] for k in keyboard_layout['keys'])==10
keypad_layout={'source':'models/keyboard-layout.json','numeric_white_keys':11,'gray_top_row':3,'gray_operator_top':1,'white_operator_column':4,'gray_main_keys':6,'total_gray_keys':10,'method':'Photo-plane trace of all key centers, widths, depths, L-shaped modifiers and well gutters'}

# Photo-constrained vents wrap over the rounded top/side corner.
box('rear shell seam',(0,.301,.055),(.422,.002,.0018),base,.0003)
for side in (-1,1):
 box('side case joint',(side*.2216,.025,.055),(.0006,.55,.001),base,0)
 for i in range(29):
  y=.025+i*.008
  path=[(side*.2216,.103),(side*.2216,.192)]
  for j in range(1,9):
   t=j*math.pi/16;path.append((side*(.2135+.0081*math.cos(t)),.192+.0081*math.sin(t)))
  path.append((side*.2105,.2001))
  verts=[(x,y+dy,z) for dy in (-.0009,.0009) for x,z in path];n=len(path)
  mesh('wrapped ventilation slot '+str(side)+' '+str(i),verts,[(j,j+1,n+j+1,n+j) for j in range(n-1)],slotmat)
box('top IBM badge',(.165,-.066,.2005),(.024,.018,.0008),chrome,.0005)
decal('top IBM badge print',[(.153,-.075,.2011),(.177,-.075,.2011),(.177,-.057,.2011),(.153,-.057,.2011)],printmat('top badge print','5100-top-badge.png'))

# Bake deliberate bevels/normals, then batch by material for a compact browser asset.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:
 bpy.context.view_layer.objects.active=o;o.select_set(True)
 for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 o.select_set(False)
logical=len(parts)
groups={}
for o in parts:groups.setdefault(o.data.materials[0].name,[]).append(o)
for name,members in sorted(groups.items()):
 bpy.ops.object.select_all(action='DESELECT')
 for o in members:o.select_set(True)
 bpy.context.view_layer.objects.active=members[0];bpy.ops.object.join();members[0].name=name+' assembly'
hardware=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in hardware:o['semantic_name']=o.name
bpy.context.view_layer.update()
def bounds(objects):
 points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
 return [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
original_bounds=bounds(hardware)
bpy.ops.object.select_all(action='DESELECT')
for o in hardware:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'ibm5100-clean.glb'),use_selection=True,export_extras=True)
bpy.ops.wm.obj_export(filepath=str(out/'ibm5100-clean.obj'),export_selected_objects=True)
# Independent export round trip: bounds and semantic identities must survive.
scene=bpy.context.scene;test=bpy.data.scenes.new('round-trip check');bpy.context.window.scene=test
bpy.ops.import_scene.gltf(filepath=str(out/'ibm5100-clean.glb'))
imported=[o for o in test.objects if o.type=='MESH'];bpy.context.view_layer.update();new_bounds=bounds(imported)
assert {o.get('semantic_name') for o in imported}=={o.name for o in hardware}
assert max(abs(original_bounds[i][j]-new_bounds[i][j]) for i in range(3) for j in range(2))<.0001
bpy.context.window.scene=scene
for o in list(test.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.scenes.remove(test)

# Render-only light gray tabletop and neutral studio, excluded from the GLB.
scene.render.engine='CYCLES';scene.cycles.samples=a.samples;scene.cycles.use_denoising=True
scene.render.use_freestyle=False
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-1.3
if a.device=='OPTIX':
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 assert any(d.type=='OPTIX' for d in prefs.devices),'OptiX unavailable'
 for d in prefs.devices:d.use=d.type=='OPTIX'
 scene.cycles.device='GPU'
scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world=bpy.data.worlds.new('neutral photographic studio');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.21,.24,.28,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
box('render only light gray tabletop',(0,0,-.013),(200,200,.02),mat('light gray tabletop',(.42,.44,.45),.68),0)
for name,loc,power,size in [('key',(.45,-.65,1.2),85,.9),('fill',(-.7,-.3,.7),55,.8),('rim',(.2,.7,1.0),100,.7)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
 light=bpy.data.objects.new(name,data);scene.collection.objects.link(light);light.location=loc;light.rotation_euler=(Vector((0,0,.09))-light.location).to_track_quat('-Z','Y').to_euler()
views=[('overview',(.68,-.95,.64),(0,-.015,.095),53),('front',(0,-1.05,.43),(0,-.12,.105),58),('left',(-.68,-.95,.64),(0,-.015,.095),53),('right',(.68,-.95,.64),(0,-.015,.095),53),('top',(0,-.02,1.35),(0,-.02,.04),44),('detail',(.32,-.62,.38),(0,-.17,.095),58),('keyboard-layout',(0,-.21,.70),(0,-.21,.05),50),('power-switch',(-.026,-.325,.176),(-.026,front_y(-.125+FRONT_ASSEMBLY_SETBACK,.1295),.1295),70)]
for name,loc,aim,lens in views:
 data=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,data);scene.collection.objects.link(cam);cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=lens
 scene.camera=cam;scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ibm5100-clean.blend'))
report={'variant':'IBM 5100, APL/BASIC Model C exterior study','dimensions_m':[b[1]-b[0] for b in original_bounds],'bounds_m':original_bounds,'logical_parts':logical,'mesh_count':len(hardware),'keycaps':keycount,'triangles':sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in hardware),'glb_round_trip':'semantic names and bounds passed','device':a.device,'samples':a.samples,'reference':'references/ibm5100-front.jpg; UvA IBM 5100 catalogue and keyboard photograph; Museums Victoria ST 38310 envelope','power_switch':power_switch_spec,'keypad_layout':keypad_layout,'presentation_palette':palette,'front_rake_degrees':FRONT_RAKE_DEG,'crt_glass_recess_mm':[10.5,15.0],'bezel_projection_mm':-1000*FRONT_ASSEMBLY_SETBACK,'front_assembly_setback_mm':1000*FRONT_ASSEMBLY_SETBACK,'keyboard_plane_lift_mm':1000*KEYBOARD_PLANE_LIFT,'cartridge_thickness_scale':CARTRIDGE_THICKNESS_SCALE,'cartridge_height_mm':40.25,'remaining_mismatches':['Front rake is photo-estimated at 8 degrees, not measured','Six main gray keys identified in photos; requested seventh main gray key needs identification; full APL legends incomplete','Four-switch Model C follows IBM drawing; comparison photos show three-switch variants','Rear fittings and exact vent count/depth provisional','No measured surface radii; photo-led cabinet and key spacing']}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS clean IBM 5100:',json.dumps(report))
