"""Next island gap from the supplied video; covered sky and geometry provisional."""
from pathlib import Path
import argparse,io,json
import numpy as np
from PIL import Image
from convert_bridge_run import warm_mask,sky_fill,quantize
from convert_continuation_background import png,write,sha
from audit_route_continuation import match
ROOT=Path(__file__).resolve().parents[1]
def compose():
 ref=ROOT/'reference/w1l1_next'
 source=np.asarray(Image.open(ref/'174.png').convert('RGB'))
 original=np.asarray(Image.open(ref/'175.png').convert('RGB'))
 patches=[match(source.astype('int16'),original.astype('int16'),box,0)
          for box in [(65,103,73,112),(103,105,111,111)]]
 assert all(p['delta']==[76,44] and p['mae_rgb']<8 and p['runner_up_mae_rgb']-p['mae_rgb']>3 for p in patches)
 a=original.copy();holes=np.zeros((160,240),bool);restored=holes.copy()
 holes[:14]=True;holes[13:45,204:240]=True
 holes[102:151,140:184]=True # actor and sword
 holes[89:107,89:108]=True # collectible rendered later, not baked into terrain
 clean=np.asarray(Image.open(ROOT/'assets/ramp_upper_background.png').convert('RGB'))
 tile=clean[98:123,64:116];mask=warm_mask(tile)
 # Copy connected terrain from its independently registered preceding view.
 for x in range(mask.shape[1]):
  ys=np.flatnonzero(mask[:,x])
  if len(ys):mask[ys[0]:,x]=True
 a[142:160,140:192][mask[:18]]=tile[:18][mask[:18]]
 restored[142:160,140:192]=mask[:18]
 holes &= ~restored
 a[:14]=np.median(a[45,110:138],axis=0).astype('uint8')
 sky_fill(a,holes,(110,138),95)
 binary,preview=quantize(a,holes,(ROOT/'assets/continuation_palette.bin').read_bytes())
 changed=holes|restored
 assert np.array_equal(a[~changed],original[~changed])
 manifest={'video_sha256':'7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51',
  'sources':{str(t):sha((ref/f'{t}.png').read_bytes()) for t in [174,175]},
  'camera_translation':[76,44],'patches':patches,'geometry':'provisional',
  'limits':['Occluded sky estimated; island restored from preceding registered view',
            'Gem removed from background; collectible and flying enemy pending',
            'Upper-left ledge is a provisional one-way surface; next camera view pending']}
 return {'island_gap_background.bin':binary,'island_gap_background.png':png(Image.fromarray(a)),
  'island_gap_background_preview.png':png(preview.resize((720,480),Image.Resampling.NEAREST)),
  'island_gap_manifest.json':(json.dumps(manifest,indent=2)+'\n').encode()}
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
 for name,data in compose().items():
  path=ROOT/'assets'/name
  if args.check:
   if name.endswith('.png'):assert Image.open(path).convert('RGBA').tobytes()==Image.open(io.BytesIO(data)).convert('RGBA').tobytes(),name
   else:assert path.read_bytes()==data,name
  else:write(path,data)
 print('PASS island gap assets: registered (+76,+44) portal and separate actor-free background; geometry provisional')
if __name__=='__main__':main()
