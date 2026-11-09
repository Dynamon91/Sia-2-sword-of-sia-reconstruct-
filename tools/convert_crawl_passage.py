"""Next registered lower-strip view, recovered from the 186.1 s exposure."""
from pathlib import Path
import argparse,io,json,hashlib
import numpy as np
from PIL import Image
from audit_route_continuation import match
from convert_bridge_run import sky_fill,quantize
ROOT=Path(__file__).resolve().parents[1]
def outputs():
 paths=[ROOT/'reference/w1l1_lower_landing/185.png',ROOT/'reference/w1l1_lower_landing/186_1.png']
 raw=[np.asarray(Image.open(p).convert('RGB')) for p in paths]
 patches=[match(raw[0].astype('int16'),raw[1].astype('int16'),box,0) for box in [(100,132,116,148),(45,124,61,140)]]
 assert all(p['delta']==[83,-63] and p['mae_rgb']<9 and p['runner_up_mae_rgb']-p['mae_rgb']>3 for p in patches)
 a=raw[1].copy()
 # The previous exposure has no actor in this independently registered region.
 a[37:65,142:192]=raw[0][100:128,59:109]
 holes=np.zeros((160,240),bool);holes[:14]=True;holes[13:45,204:240]=True
 sky_fill(a,holes,(10,70),45)
 # Upper rock is not registered by lower-strip patches: extend only the
 # visible header boundary; avatar-covered sky remains an explicit estimate.
 a[:14]=a[14:15]
 data,preview=quantize(a,holes,(ROOT/'assets/continuation_palette.bin').read_bytes())
 p=io.BytesIO();Image.fromarray(a).save(p,format='PNG');q=io.BytesIO();preview.resize((720,480),Image.Resampling.NEAREST).save(q,format='PNG')
 manifest={'video_sha256':'7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51','source_seconds':[185,186.1],'source_sha256':[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths],'patches':patches,'origin':[-790,204],'delta':[83,-63],'limits':['Player region restored through measured lower-terrain registration; covered header/rock edge and avatar sky estimated','Collision floor y=55 and low rock are provisional, not recovered map data','Left boundary of this partial view is the current route limit; no next level is claimed','No intermediate thorn movement or thorn damage is implemented']}
 return {'crawl_passage_background.bin':data,'crawl_passage_background.png':p.getvalue(),'crawl_passage_background_preview.png':q.getvalue(),'crawl_passage_manifest.json':(json.dumps(manifest,indent=2)+'\n').encode()}
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
 for name,data in outputs().items():
  path=ROOT/'assets'/name
  if a.check:
   if name.endswith('.png'):assert Image.open(path).convert('RGB').tobytes()==Image.open(io.BytesIO(data)).convert('RGB').tobytes(),name
   else:assert path.read_bytes()==data,name
  else:path.write_bytes(data)
 print('PASS crawl passage: registered next viewport, actor/overlay restoration from prior exposure and shared palette')
if __name__=='__main__':main()
