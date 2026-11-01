"""Remove recording banner from embedded stills; covered pixels are estimates.
Run ONCE after unpack_assets.py on v06 bytes, never on an already-cleaned file.
"""
from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'assets/visuals.bin';raw=p.read_bytes();stride=38912
report=ROOT/'assets/frontend_cleanup.json'
if report.exists() and json.loads(report.read_text()).get('output_sha256')==hashlib.sha256(raw).hexdigest():
 print('Frontend already cleaned');raise SystemExit(0)
archive=json.loads((ROOT/'assets/embedded_assets.json').read_text())
expected=next(a['sha256'] for a in archive['assets'] if a['path']=='assets/visuals.bin')
assert hashlib.sha256(raw).hexdigest()==expected, 'Restore original assets before cleanup'
raw=raw[:9*stride]
assert len(raw)==9*stride
clean=bytearray()
for i in range(9):
 frame=raw[i*stride:(i+1)*stride];palette=frame[:512]
 im=Image.frombytes('L',(240,160),frame[512:])
 # Overlay occlusion persists below the black strip. Extend the first uncovered row into
 # the recording overlay footprint; no authentic recovery claim.
 for y in range(12,30):
  for x in range(209,240): im.putpixel((x,y),im.getpixel((x,30)))
 im=im.crop((0,12,240,160)).resize((240,160),Image.Resampling.NEAREST)
 clean.extend(palette+im.tobytes())
p.write_bytes(clean)
(ROOT/'assets/frontend_cleanup.json').write_text(json.dumps({
 'banner_removed_rows':12,'recording_avatar_removed_rect':[209,12,31,18],
 'occluded_pixels':'estimated from first uncovered row; NOT original recovered art',
 'resampling':'nearest, 240x148 to 240x160','intro_playback_removed':True,'output_sha256':hashlib.sha256(clean).hexdigest()},indent=2))
