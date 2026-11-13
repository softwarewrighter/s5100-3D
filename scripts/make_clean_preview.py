#!/usr/bin/env python3
"""5100-specific presentation using Lucy's viewer and single controls source."""
import argparse
import hashlib
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
SHARED=ROOT.parent/'lucy-3D'/'shared'
sys.path.insert(0,str(SHARED))
from viewer import CAMERAS, write_viewer
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();out=a.out
CAMERAS['5100']=[('Overview',(.68,-.95,.64),(0,-.015,.095)),('Front',(0,-1.05,.43),(0,-.12,.105)),('Left',(-.68,-.95,.64),(0,-.015,.095)),('Right',(.68,-.95,.64),(0,-.015,.095)),('Top',(0,-.02,1.35),(0,-.02,.04)),('Keyboard',(.32,-.62,.38),(0,-.17,.095)),('Keyboard top',(0,-.21,.70),(0,-.21,.05)),('Power switch',(-.026,-.325,.176),(-.026,-.098,.1295))]
version=hashlib.sha256((out/'ibm5100-clean.glb').read_bytes()).hexdigest()[:12]
write_viewer(out,'5100',model='ibm5100-clean.glb?v='+version,title='IBM 5100 · Clean reconstruction')
page=(out/'index.html').read_text()
page=page.replace('<script type="module" src="vendor/model-viewer-4.0.0.min.js"></script>','')
page=page.replace("customElements.whenDefined('model-viewer').then(()=>{", "customElements.whenDefined('model-viewer').then(()=>{if(window.previewRenderMode)return;")
page=page.replace(" document.querySelectorAll('[data-action]').forEach", " window.previewControls=controls;\n document.querySelectorAll('[data-action]').forEach",1)
page=page.replace('</model-viewer>', '</model-viewer><img id="render-fallback" src="overview.png" alt="IBM 5100 Blender render" hidden style="width:100%;max-height:70vh;object-fit:contain;border-radius:14px"><p><a href="?renders=1">View renders without WebGL</a> · <a href="?">Try interactive 3D</a></p>',1)

page=page.replace('<h1>', '<p><a href="../">All previews</a> · <a href="../comparisons/">Photo comparisons</a></p><h1>',1)
page=page.replace('shadow-intensity="1"','shadow-intensity="1.4" exposure="0.85" poster="overview.png"')
page=page.replace('<nav>', '<p>New procedural enclosure · white caps and gray function keys · curved dark gray CRT</p><nav>',1)
page=page.replace('</style>', 'model-viewer{background:radial-gradient(ellipse at 50% 65%,#c8cbcd,#79848b);border-radius:14px}body{max-width:1440px;margin:auto}a{display:inline-block;text-decoration:none}figure{margin:0}figure img{width:100%;border-radius:10px}.renders{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;text-align:left}.renders a{padding:0;border:0;background:none}.renders figcaption{padding:8px 0;color:#bcc4ca}.note{max-width:900px;margin:24px auto;line-height:1.6;color:#b9c2ca}</style>')
gallery='<p><a href="ibm5100-clean.glb" download>Download 3D model</a> <a href="ibm5100-clean.blend" download>Blender scene</a> <a href="report.json">Validation report</a></p><div class="renders">'
for name,title in [('overview','Studio overview'),('front','Front panel'),('left','Left oblique'),('right','Right oblique'),('top','Top'),('detail','Keyboard and controls'),('keyboard-layout','Photo-traced keyboard layout from above'),('power-switch','Recessed power switch close-up')]:
 gallery+=f'<figure><a href="{name}.png"><img loading="lazy" src="{name}.png" alt="{title}"></a><figcaption>{title}</figcaption></figure>'
gallery+='</div><p class="note">Photo-led IBM 5100 APL/BASIC exterior study. Cabinet radii, exact keyboard spacing, full APL legends, rear fittings, and vent spacing remain provisional. White alphanumeric/numeric caps and gray function keys follow the photographed groups; the inactive screen remains dark gray. The light gray tabletop is used in the still renders; the interactive asset contains hardware only.</p><p class="note">References: <a href="https://commons.wikimedia.org/wiki/File:IBM_5100_(1).jpg">Snuci photograph (CC0)</a> · <a href="https://ub.fnwi.uva.nl/computermuseum/ibm5100.html">UvA computer museum</a> · <a href="https://collections.museumsvictoria.com.au/items/396687">Museums Victoria ST 38310</a></p>'
trace=ROOT/'work/photo-refinement/keyboard-photo-trace.jpg'
if trace.exists():
 shutil.copyfile(trace,out/'keyboard-photo-trace.jpg')
 gallery+='<p><a href="keyboard-photo-trace.jpg">Annotated original keyboard photograph (Snuci, public domain)</a> · <a href="keyboard-layout.json">Photo-traced layout coordinates</a></p>'
shutil.copyfile(ROOT/'models/keyboard-layout.json',out/'keyboard-layout.json')
page=page.replace('</html>',gallery+'<script src="clean-preview-bootstrap.js"></script></html>')
shutil.copyfile(ROOT/'web/clean-preview-bootstrap.js',out/'clean-preview-bootstrap.js')
(out/'index.html').write_text(page)
shutil.copyfile(ROOT/'references/ibm5100-front.jpg',out/'reference-front.jpg')
print('Wrote',out/'index.html')
