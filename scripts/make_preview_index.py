#!/usr/bin/env python3
"""Assemble a LAN preview index without replacing either model's output."""
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'work/preview';out.mkdir(parents=True,exist_ok=True)
cards=[]
for path,target,title,desc,image in [
 ('clean',ROOT/'work/ibm5100-clean/out','Clean procedural reconstruction','New enclosure, separate sculpted keys, curved CRT, printed legends, and studio lighting.','overview.png'),
 ('comparisons',ROOT/'work/photo-comparison/public','Photo-matched comparisons','Original photographs, locked-camera before/after renders, measurements, and remaining deviations.','snuci-after.jpg'),
 ('previous',ROOT/'work/ibm5100/out','Previous Trellis-based preview','Preserved previous model for comparison.','overview.png')]:
 if not (target/'index.html').exists():continue
 link=out/path
 if link.is_symlink():
  if link.resolve()!=target.resolve():link.unlink()
 if not link.exists():link.symlink_to(Path(os.path.relpath(target,out)),target_is_directory=True)
 cards.append(f'<a class="card" href="{path}/"><img src="{path}/{image}" alt="{title}"><div><span>IBM 5100</span><h2>{title}</h2><p>{desc}</p><b>Open preview →</b></div></a>')
if not cards:raise SystemExit('No built previews found; run just render-clean first.')
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>IBM 5100 · Preview index</title><link rel="icon" href="data:,"><style>
*{box-sizing:border-box}body{margin:0;background:#151b20;color:#edf0f1;font:16px system-ui}main{max-width:1240px;margin:auto;padding:60px 28px}header{margin-bottom:32px}small,span{font-size:12px;letter-spacing:.15em;text-transform:uppercase;color:#aeb9bc}h1{font-size:clamp(32px,5vw,54px);margin:12px 0}header p{color:#b9c4ca;line-height:1.6}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));gap:24px}.card{overflow:hidden;border:1px solid #3c4852;border-radius:16px;text-decoration:none;color:inherit;background:#202a32}.card:hover{border-color:#d9c694}.card img{display:block;width:100%;aspect-ratio:4/3;object-fit:cover}.card div{padding:24px}.card h2{font-size:24px;margin:10px 0}.card p{line-height:1.6;color:#b8c3cb;min-height:52px}.card b{color:#e7d49d;font-weight:500}footer{margin-top:30px;color:#aeb9c2;line-height:1.6}</style></head><body><main><header><small>Hardware studies / preview library</small><h1>IBM 5100</h1><p>Inspect the new reconstruction and compare it with the previous model.</p></header><div class="grid">CARDS</div><footer>Each preview includes an interactive 3D model and rendered images. If WebGL is unavailable, open the still renders on its preview page. This server is available to devices on the local network.</footer></main></body></html>'''
(out/'index.html').write_text(page.replace('CARDS',''.join(cards)))
print('Preview index:',out/'index.html')
