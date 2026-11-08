"""Two registered lever-area views; geometry and covered pixels provisional."""
from pathlib import Path
import argparse,io,json
import numpy as np
from PIL import Image
from convert_bridge_run import warm_mask,sky_fill,quantize
from convert_continuation_background import png,write,sha
from audit_route_continuation import match
ROOT=Path(__file__).resolve().parents[1]
def terrain(a,restored,source,box,dx,dy):
 x0,y0,x1,y1=box;tile=source[y0:y1,x0:x1];mask=warm_mask(tile)
 for x in range(mask.shape[1]):
  ys=np.flatnonzero(mask[:,x])
  if len(ys):mask[ys[0]:,x]=True
 dst=a[y0+dy:y1+dy,x0+dx:x1+dx];dst[mask]=tile[mask]
 restored[y0+dy:y1+dy,x0+dx:x1+dx]|=mask

def compose():
 ref=ROOT/'reference/w1l1_next';frames={t:np.asarray(Image.open(ref/f'{t}.png').convert('RGB')) for t in [175,178,180]}
 registrations=[]
 for before,after,boxes,delta in [
  (175,178,[(23,67,31,75),(38,78,45,85)],[118,3]),
  (178,180,[(25,60,33,68),(27,49,34,56)],[44,86])]:
  patches=[match(frames[before].astype('int16'),frames[after].astype('int16'),box,0) for box in boxes]
  assert all(p['delta']==delta and p['mae_rgb']<8 and p['runner_up_mae_rgb']-p['mae_rgb']>3 for p in patches)
  registrations.append({'from':before,'to':after,'delta':delta,'patches':patches})
 output={};clean={}
 for t,name in [(178,'lever_entry'),(180,'lever_room')]:
  a=frames[t].copy();holes=np.zeros((160,240),bool);restored=holes.copy()
  holes[:14]=True;holes[13:45,204:240]=True
  if t==178:
   holes[16:67,50:83]=True # fourth guard rendered independently
   holes[52:103,157:199]=True # player and sword
   terrain(a,restored,frames[180],(94,102,127,153),-44,-86)
   previous=np.asarray(Image.open(ROOT/'assets/island_gap_background.png').convert('RGB'))
   terrain(a,restored,previous,(39,49,57,115),118,3)
   strip=(125,150);last=45
  else:
   holes[99:159,109:188]=True # player and broad sword arc
   terrain(a,restored,clean[178],(65,13,144,73),44,86)
   strip=(180,200);last=95
  holes &= ~restored
  a[:14]=a[14] # covered wall and hanging rock estimated from their visible edge
  sky_fill(a,holes,strip,last)
  # Preserve the estimated foreground edge underneath the former recording header.
  a[:14]=a[14]
  clean[t]=a.copy();binary,preview=quantize(a,holes,(ROOT/'assets/continuation_palette.bin').read_bytes())
  output[name+'_background.bin']=binary;output[name+'_background.png']=png(Image.fromarray(a))
  output[name+'_background_preview.png']=png(preview.resize((720,480),Image.Resampling.NEAREST))
 manifest={'video_sha256':'7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51',
  'sources':{str(t):sha((ref/f'{t}.png').read_bytes()) for t in frames},'registrations':registrations,
  'geometry':'provisional','limits':['Covered sky and recording header estimated; terrain restored through measured transforms',
   'Fourth guard uses the existing video-derived guard sprite and provisional patrol/combat',
   'Lever remains scenery; its activation, thorn barrier and following route are pending']}
 output['lever_route_manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode();return output

def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
 for name,data in compose().items():
  path=ROOT/'assets'/name
  if args.check:
   if name.endswith('.png'):assert Image.open(path).convert('RGBA').tobytes()==Image.open(io.BytesIO(data)).convert('RGBA').tobytes(),name
   else:assert path.read_bytes()==data,name
  else:write(path,data)
 print('PASS lever route assets: two registered views, separate guard and player, provisional geometry and covered scenery')
if __name__=='__main__':main()
