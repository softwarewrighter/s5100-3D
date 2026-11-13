#!/usr/bin/env python3
"""Fetch original research evidence without resizing or overwriting local sources."""
import hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'references/ibm5100-photo-sources.json').read_text())
for r in records:
 path=ROOT/r['path'];path.parent.mkdir(parents=True,exist_ok=True)
 if not path.exists():
  request=urllib.request.Request(r['url'],headers={'User-Agent':'IBM5100ModelStudy/1.0 (reference research)'})
  with urllib.request.urlopen(request,timeout=90) as response:
   data=response.read()
  path.write_bytes(data)
 print(r['path'],hashlib.sha256(path.read_bytes()).hexdigest())
