# /// script
# dependencies = ["numpy", "scipy", "pillow>=11"]
# ///
"""Fit and freeze photo cameras from cabinet landmarks, not interior details."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'models/photo-views.json';cfg=json.loads(source.read_text())
out=ROOT/'work/photo-comparison';out.mkdir(parents=True,exist_ok=True)

def camera_matrix(v):
 az,el,roll=v[:3];ca,sa=np.cos(az),np.sin(az);ce,se=np.cos(el),np.sin(el)
 R=np.array([[ca,sa,0],[sa*se,-ca*se,-ce],[-sa*ce,ca*ce,-se]])
 cr,sr=np.cos(roll),np.sin(roll);return np.array([[cr,-sr,0],[sr,cr,0],[0,0,1]])@R

def project(points,v,size):
 R=camera_matrix(v);xyz=(points-np.array([0,0,.1]))@R.T+v[3:6]
 return xyz[:,:2]/xyz[:,2:3]*np.exp(v[6])+np.array(size)/2

results=[]
for view in cfg['views']:
 names=list(view['points']);xyz=np.array([cfg['landmarks'][n] for n in names]);uv=np.array(list(view['points'].values()))
 best=None
 for d in [.65,1.2,2.5,4]:
  f=d*(uv[:,0].max()-uv[:,0].min())/.443
  initial=[view['initial_azimuth'],view['initial_elevation'],0,0,0,d,np.log(f)]
  def residual(v):return (project(xyz,v,view['size'])-uv).ravel()
  fit=least_squares(residual,initial,bounds=([-1.3,.05,-.2,-3,-3,.35,np.log(250)],[1.3,1.5,.2,3,3,8,np.log(16000)]),max_nfev=1500)
  if best is None or np.linalg.norm(fit.fun)<np.linalg.norm(best.fun):best=fit
 v=best.x;R=camera_matrix(v);T=v[3:6];location=np.array([0,0,.1])-R.T@T
 blender_rotation=R.T@np.diag([1,-1,-1])
 result={**view,'parameters':v.tolist(),'camera_location':location.tolist(),'camera_rotation_matrix':blender_rotation.tolist(),'lens_mm':float(np.exp(v[6])*36/view['size'][0]),'cabinet_landmark_rms_px':float(np.sqrt(np.mean(best.fun**2))),'fit_points':{n:{'photo':view['points'][n],'projected':p.tolist()} for n,p in zip(names,project(xyz,v,view['size']))}}
 results.append(result)
 image=Image.open(ROOT/view['photo']).convert('RGB').resize(tuple(view['size']));draw=ImageDraw.Draw(image)
 for i,(name,pred) in enumerate(zip(names,project(xyz,v,view['size']))):
  target=view['points'][name];pred=tuple(pred);draw.line([tuple(target),pred],fill='red',width=3)
  draw.ellipse((target[0]-4,target[1]-4,target[0]+4,target[1]+4),outline='yellow',width=2);draw.text((target[0]+6,target[1]-10),name,fill='yellow')
  draw.ellipse((pred[0]-3,pred[1]-3,pred[0]+3,pred[1]+3),fill='cyan')
 image.save(out/(view['id']+'-camera-fit.jpg'))
 print(view['id'],'RMS coordinate error',result['cabinet_landmark_rms_px'],'lens',result['lens_mm'],'az/elev',np.degrees(v[:2]))
(out/'locked-cameras.json').write_text(json.dumps({'source':str(source.relative_to(ROOT)),'camera_policy':'Fixed after baseline alignment; no refitting between geometry candidates','views':results},indent=2)+'\n')
