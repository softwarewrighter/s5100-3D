# /// script
# dependencies = ["numpy", "scipy", "pillow>=11"]
# ///
"""Photo-plane keyboard trace; source original is preserved unmodified."""
import json
from pathlib import Path
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
im=Image.open(ROOT/'references/ibm5100-overhead.jpg').convert('RGB');a=np.array(im)
photo=np.array([[145,456],[1216,440],[1230,794],[147,790]],dtype=float)
world=np.array([[-.211,-.124],[.211,-.124],[.211,-.299],[-.211,-.299]])
A=[];b=[]
for (x,y),(u,v) in zip(photo,world):
 A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);b.extend([u,v])
H=np.append(np.linalg.solve(A,b),1).reshape(3,3)
def mappt(x,y):
 p=H@np.array([x,y,1]);return (p[:2]/p[2]).tolist()
mask=np.all(a>180,axis=2);mask[:500]=False;mask[760:]=False;mask[:,:200]=False;mask[:,1160:]=False
mask=ndimage.binary_opening(mask,iterations=2);mask=ndimage.binary_fill_holes(mask)
lab,n=ndimage.label(mask);boxes=[]
for i,sl in enumerate(ndimage.find_objects(lab),1):
 if sl is None:continue
 y,x=sl;w=x.stop-x.start;h=y.stop-y.start
 if np.sum(lab[sl]==i)>400 and 25<w<500 and 20<h<80:boxes.append([x.start,y.start,x.stop,y.stop])
keys=[];draw=ImageDraw.Draw(im)
def add(label,poly,gray=False,legend=None):
 points=[mappt(x,y) for x,y in poly];arr=np.array(points);lo=arr.min(axis=0);hi=arr.max(axis=0)
 # Rectangular bounding envelope removes photo-plane perspective skew from cap shape.
 shape=points if len(poly)>4 else [[lo[0],lo[1]],[hi[0],lo[1]],[hi[0],hi[1]],[lo[0],hi[1]]]
 center=((lo+hi)/2).tolist()
 keys.append({'label':label,'gray':gray,'x':center[0],'y':center[1],'width':float(hi[0]-lo[0]),'depth':float(hi[1]-lo[1]),'outline':shape,'photo_outline':poly,'legend_center':mappt(*legend) if legend else center})
 draw.line([tuple(p) for p in poly+[poly[0]]],fill='orange' if gray else 'red',width=2)
 draw.text(tuple(poly[0]),label,fill='yellow',stroke_width=1,stroke_fill='black')
def rect(label,box,gray=False):
 # Restore shadowed first numeric-row skirts that bright-pixel segmentation misses.
 if not gray and label in ('7','8','9') and box[0]>930 and box[1]<604:
  center=(box[0]+box[2])/2;box=[center-22,558,center+22,603]
 if not gray and label=='÷' and box[0]>1090:box=[1103,556,1147,602]
 x0,y0,x1,y1=box;add(label,[[x0,y0],[x1,y0],[x1,y1],[x0,y1]],gray)
def extract(labels,predicate):
 selected=sorted([b for b in boxes if predicate((b[0]+b[2])/2,(b[1]+b[3])/2)],key=lambda b:b[0])
 assert len(selected)==len(labels),(labels,selected)
 for label,box in zip(labels,selected):rect(label,box)
extract(list('1234567890')+['+','×'],lambda x,y:x<920 and y<550)
extract(list('QWERTYUIOP')+['[',']'],lambda x,y:x<920 and 555<y<604)
extract(list('ASDFGHJKL')+['[',']','@'],lambda x,y:x<920 and 604<y<655)
extract(list('ZXCVBNM')+[',','.','/','$'],lambda x,y:x<920 and 655<y<706)
extract(['SPACE'],lambda x,y:x<920 and y>706)
for labels,lower,upper in [(['7','8','9'],555,604),(['4','5','6'],604,655),(['1','2','3'],655,706),(['0','.'],706,760)]:
 extract(labels,lambda x,y:930<x<1090 and lower<y<upper)
for label,lower,upper in [('÷',555,604),('×',604,655),('−',655,706),('+',706,760)]:
 extract([label],lambda x,y:x>1090 and lower<y<upper)
for label,box in [('←',[818,506,864,550]),('→',[868,505,914,550]),('SHIFT',[218,661,298,706]),('SHIFT',[856,658,915,704]),('ATTN',[938,507,983,552]),('↑',[987,506,1032,551]),('↓',[1037,506,1082,551]),('HOLD',[1104,506,1148,551])]:rect(label,box,True)
add('CMD',[[219,562],[258,562],[258,608],[275,608],[275,654],[219,655]],True,legend=[240,631])
add('EXECUTE',[[841,556],[915,556],[915,652],[864,652],[864,605],[841,605]],True,legend=[878,580])
# Segmentation sees differently lit cap faces, not a mechanically exact base plane.
# Resolve small projected envelope overlaps while preserving row centers and offsets.
def resize(record,width=None,depth=None,y=None):
 record['width']=width if width is not None else record['width']
 record['depth']=depth if depth is not None else record['depth']
 if y is not None:record['y']=y
 x,y=record['x'],record['y'];w,d=record['width'],record['depth']
 record['outline']=[[x-w/2,y-d/2],[x+w/2,y-d/2],[x+w/2,y+d/2],[x-w/2,y+d/2]]
 record['layout_regularization']='Minimum 0.8 mm physical gap after photo-plane rectification'
for _ in range(3):
 for i,a in enumerate(keys):
  if len(a['outline'])!=4:continue
  for b in keys[i+1:]:
   if len(b['outline'])!=4:continue
   dx=min(a['x']+a['width']/2,b['x']+b['width']/2)-max(a['x']-a['width']/2,b['x']-b['width']/2)
   dy=min(a['y']+a['depth']/2,b['y']+b['depth']/2)-max(a['y']-a['depth']/2,b['y']-b['depth']/2)
   if dx<=.0002 or dy<=.0002:continue
   if a['label']=='SPACE' or b['label']=='SPACE':
    space=a if a['label']=='SPACE' else b;other=b if space is a else a
    front=space['y']-space['depth']/2;back=other['y']-other['depth']/2-.0008
    resize(space,depth=back-front,y=(front+back)/2)
   else:
    adjustment=dy+.0008;resize(a,depth=a['depth']-adjustment);resize(b,depth=b['depth']-adjustment)

assert len(keys)==73 and sum(k['gray'] for k in keys)==10
result={'source':'references/ibm5100-overhead.jpg','source_page':'https://commons.wikimedia.org/wiki/File:IBM-5100-overhead_view.jpg','method':'Perspective homography from four hand-selected mounting-panel corners; white-cap segmentation with hand-traced gray outlines. Approximate key-top-plane layout, not measured hardware.','photo_panel_corners':photo.tolist(),'world_panel_corners':world.tolist(),'homography':H.tolist(),'gray_main_keys':['CMD','SHIFT left','SHIFT right','EXECUTE','←','→'],'wells':[{'name':name,'outline':[mappt(x,y) for x,y in poly]} for name,poly in [('main key well and spacebar notch',[[213,500],[920,500],[920,712],[765,712],[765,762],[324,762],[324,712],[213,712]]),('gray keypad row well',[[932,500],[1088,500],[1088,557],[932,557]]),('white numeric block well',[[934,560],[1092,560],[1092,759],[934,759]]),('separate operator column well',[[1096,500],[1156,500],[1156,756],[1096,756]])]],'keys':keys}
(ROOT/'models/keyboard-layout.json').write_text(json.dumps(result,indent=2)+'\n')
im.crop((180,490,1170,765)).save(ROOT/'work/photo-refinement/keyboard-photo-trace.jpg')
print('Traced',len(keys),'keys;',sum(k['gray'] for k in keys),'gray')
print('Regular white cap widths mm:',np.median([k['width']*1000 for k in keys if k['label'] in list('QWERTYUIOP')]))
