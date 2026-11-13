"""Render a saved candidate with frozen photo-matched cameras."""
import argparse,json,sys
from pathlib import Path
import bpy
from mathutils import Matrix
p=argparse.ArgumentParser();p.add_argument('--blend',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--samples',type=int,default=24)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.out.mkdir(parents=True,exist_ok=True)
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(a.blend.resolve()))
scene=bpy.context.scene;scene.cycles.samples=a.samples
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
scene.cycles.device='GPU'
for view in json.loads((ROOT/'models/photo-cameras.json').read_text())['views']:
 data=bpy.data.cameras.new('photo '+view['id']);cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam)
 cam.location=view['camera_location'];cam.rotation_euler=Matrix(view['camera_rotation_matrix']).to_euler()
 data.lens=view['lens_mm'];data.sensor_fit='HORIZONTAL';data.sensor_width=36
 scene.camera=cam;scene.render.resolution_x,scene.render.resolution_y=view['size'];scene.render.resolution_percentage=100
 scene.render.filepath=str(a.out.resolve()/(view['id']+'.png'));bpy.ops.render.render(write_still=True)
print('Rendered frozen photo cameras:',a.out)
