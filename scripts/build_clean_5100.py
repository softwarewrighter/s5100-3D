#!/usr/bin/env python3
"""Build the separate procedural 5100 preview; preserve previous outputs."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--device',choices=['CPU','OPTIX'],default='CPU')
p.add_argument('--samples',type=int,default=48)
p.add_argument('--timeout',type=int,default=600)
a=p.parse_args()
blender=shutil.which(os.environ.get('BLENDER_BIN','blender'))
if not blender:p.error('Blender not found; set BLENDER_BIN')
for name in ['5100-gray-key-legends.png','5100-key-legends.png','5100-key-legends.json','5100-control-print.png','5100-switch-print.png','5100-deck-strip.png','5100-top-badge.png']:
 if not (ROOT/'textures'/name).is_file():p.error('Missing print atlas; run just legends-clean')
work=ROOT/'work/ibm5100-clean';stamp=datetime.now().strftime('%Y%m%d-%H%M%S-%f')
candidate=work/('candidate-'+stamp);candidate.mkdir(parents=True)
env=os.environ.copy();env['BLENDER_USER_RESOURCES']=str(candidate/'blender-user')
cmd=[blender,'--background','--factory-startup','-noaudio','--python-exit-code','1','--python',str(ROOT/'scripts/ibm5100_clean_scene.py'),'--','--out',str(candidate),'--device',a.device,'--samples',str(a.samples)]
print('Building clean 5100; log:',candidate/'blender.log',flush=True)
with (candidate/'blender.log').open('w') as log:
 subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=a.timeout,check=True)
required=['ibm5100-clean.glb','ibm5100-clean.blend','ibm5100-clean.obj','report.json']+[v+'.png' for v in ['overview','front','left','right','top','detail','keyboard-layout','power-switch']]
for name in required:
 f=candidate/name
 if not f.is_file() or not f.stat().st_size:raise RuntimeError('Missing output: '+str(f))
report=json.loads((candidate/'report.json').read_text())
assert report['glb_round_trip']=='semantic names and bounds passed'
subprocess.run([sys.executable,str(ROOT/'scripts/make_clean_preview.py'),str(candidate)],check=True)
current=work/'out'
if current.exists():current.rename(work/('out-before-'+stamp))
candidate.rename(current)
subprocess.run([sys.executable,str(ROOT/'scripts/make_preview_index.py')],check=True)
print('Built',current)
