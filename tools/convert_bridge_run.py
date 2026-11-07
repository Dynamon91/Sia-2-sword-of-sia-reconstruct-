"""Video-derived prototype backgrounds for the seventh and eighth viewports."""
from pathlib import Path
import argparse,io,json
import numpy as np
from PIL import Image
from scipy.ndimage import label,binary_fill_holes
from repair_sprite_edges import indexed
from convert_continuation_background import png,write,sha
ROOT=Path(__file__).resolve().parents[1];REF=ROOT/'reference/w1l1_continuation'

def warm_mask(a):
 r,g,b=a.astype(np.int16).transpose(2,0,1)
 ids,n=label((r>b+8)&(g>b+3));sizes=np.bincount(ids.ravel());sizes[0]=0
 return binary_fill_holes(sizes[ids]>=3) if n else np.zeros(a.shape[:2],dtype=bool)

def sky_fill(a,holes,strip=(132,146),last_sky_row=95):
 # In these two views the strip 132..146, rows 14..95, is visible sky.
 sky=np.median(a[:,strip[0]:strip[1]],axis=1).astype(np.float32);sky[:14]=sky[14]
 sky[last_sky_row+1:]=sky[last_sky_row]  # foreground below this row is never a sky color source
 work=a.astype(np.float32);foreground=warm_mask(a)
 seeds=np.broadcast_to(sky[:,None,:],work.shape)
 work[foreground]=seeds[foreground];work[holes]=seeds[holes]
 for iteration in range(5000):
  p=np.pad(work,((1,1),(1,1),(0,0)),mode='edge')
  average=(p[:-2,1:-1]+p[2:,1:-1]+p[1:-1,:-2]+p[1:-1,2:])/4
  delta=float(np.max(np.abs(work[holes]-average[holes])))
  work[holes]=average[holes]
  if delta<0.01:break
 else:raise ValueError('Sky fill did not converge')
 a[holes]=np.rint(work[holes]).clip(0,255).astype(np.uint8)
 return iteration+1

def quantize(a,holes,header):
 indices=indexed(Image.fromarray(a),header)
 words=np.frombuffer(header,dtype='<u2');pal=np.array([[(int(w)>>s&31)*255//31 for s in (0,5,10)] for w in words],dtype=np.uint8)
 ys,xs=np.nonzero(holes);bayer=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=np.float32)
 candidates=pal[1:240].astype(np.int32)
 for start in range(0,len(xs),1024):
  y=ys[start:start+1024];x=xs[start:start+1024];colors=a[y,x].astype(np.int32);first=pal[indices[y,x]].astype(np.int32)
  d=colors[:,None,:]-candidates[None,:,:];dist=np.sum(d*d,axis=2)
  dist[np.all(first[:,None,:]==candidates[None,:,:],axis=2)]=2147483647
  second_id=dist.argmin(axis=1)+1;direction=pal[second_id].astype(np.int32)-first
  weight=np.clip(np.sum((colors-first)*direction,axis=1)/np.maximum(1,np.sum(direction*direction,axis=1)),0,1)
  use=weight>(bayer[y%4,x%4]+0.5)/16;indices[y[use],x[use]]=second_id[use]
 assert indices.min()>=1 and indices.max()<240
 return header+indices.tobytes(),Image.fromarray(pal[indices])

def compose():
 frames={}
 for t in [161,162,164]:
  im=Image.open(REF/f'frames/{t}_full.png').convert('RGB');assert im.size==(240,160)
  assert im.crop((0,35,240,160)).tobytes()==Image.open(REF/f'frames/{t}.png').convert('RGB').tobytes()
  frames[t]=np.asarray(im).copy()
 old160=Image.open(REF/'frames/160.png').convert('RGB')
 outputs={};reports=[];header=(ROOT/'assets/continuation_palette.bin').read_bytes();assert len(header)==512
 if (ROOT/'assets/room.bin').exists():assert header==(ROOT/'assets/room.bin').read_bytes()[:512]
 for name,t in [('bridge_run',161),('riser',164)]:
  original=frames[t];a=original.copy();changed=np.zeros((160,240),dtype=bool);holes=changed.copy();terrain=changed.copy()
  if t==161:
   holes[45:106,43:130]=True;holes[13:45,204:240]=True
   # Recover static bridge wood beneath the actors; never copy parallax clouds.
   tile=np.asarray(old160)[128-35:145-35,168:240];mask=warm_mask(tile)
   a[103:120,52:124][mask]=tile[mask];terrain[103:120,52:124]=mask
   # Static fragment of the upper island hidden by the channel logo.
   tile=frames[162][12:44,180:204];mask=warm_mask(tile)
   a[13:45,204:228][mask]=tile[mask];terrain[13:45,204:228]=mask
   provenance='Bridge wood from 160s mapped by (-116,-25); upper island from 162s mapped by (+24,+1)'
  else:
   holes[45:112,35:96]=True;holes[69:88,90:108]=True
   tile=frames[162][78:132,164:240];mask=warm_mask(tile)
   # These columns lie inside the island all the way below the top edge.
   # Retain cool highlight pixels inside the rock, not just warm color seeds.
   for x in range(mask.shape[1]):
    ys=np.flatnonzero(mask[:,x])
    if len(ys):mask[ys[0]:,x]=True
   a[86:140,20:96][mask]=tile[mask];terrain[86:140,20:96]=mask
   # The logo covers a static wall; extend its visible columns, not blue sky.
   a[13:45,204:240]=a[60,204:240];changed[13:45,204:240]=True
   provenance='Island from 162s mapped by (-144,+8); hidden wall columns estimated from row 60'
  holes &= ~terrain
  # Remove the black recording banner before inpainting: it must not become
  # a dark boundary condition that bleeds back into the former logo region.
  strip=(132,146) if t==161 else (110,125)
  a[:14]=np.median(a[45,strip[0]:strip[1]],axis=0).astype(np.uint8)
  iterations=sky_fill(a,holes) if t==161 else sky_fill(a,holes,(110,125),85)
  # Smooth the hidden recording-header band without stretching terrain columns.
  top=a[:15].astype(np.float32);top[:14]=top[14]
  for _ in range(2000):
   p=np.pad(top,((1,1),(1,1),(0,0)),mode='edge')
   average=(p[:-2,1:-1]+p[2:,1:-1]+p[1:-1,:-2]+p[1:-1,2:])/4
   delta=float(np.max(np.abs(top[:14]-average[:14])))
   top[:14]=average[:14]
   if delta<0.01:break
  a[:14]=np.rint(top[:14]).clip(0,255).astype(np.uint8);changed[:14]=True
  changed |= holes|terrain
  assert np.array_equal(a[~changed],original[~changed])
  binary,preview=quantize(a,holes,header)
  outputs[f'{name}_background.bin']=binary
  outputs[f'{name}_background.png']=png(Image.fromarray(a))
  outputs[f'{name}_background_preview.png']=png(preview.resize((720,480),Image.Resampling.NEAREST))
  reports.append({'name':name,'source_seconds':t,'integrated_in_rom':True,'collision_geometry':'provisional',
                  'unchanged_rgb_pixels':int((~changed).sum()),'recovered_foreground_pixels':int(terrain.sum()),
                  'sky_fill_iterations':iterations,'provenance':provenance,
                  'limits':['Compressed video colors and estimated occluded sky/top/wall',
                            'Bridge and scenery animation still pending; prototype enemy behavior']})
 info={'palette_sha256':sha(header),'sources':{str(t):sha((REF/f'frames/{t}_full.png').read_bytes()) for t in frames},
       'rooms':reports,'size':[240,160],'buffer_bytes_with_palette':38912}
 outputs['bridge_run_manifest.json']=(json.dumps(info,indent=2)+'\n').encode()
 return outputs

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
 for name,data in compose().items():
  p=ROOT/'assets'/name
  if args.check:
   if name.endswith('.png'):assert Image.open(p).convert('RGB').tobytes()==Image.open(io.BytesIO(data)).convert('RGB').tobytes(),name
   else:assert p.read_bytes()==data,name
  else:write(p,data)
 print('PASS bridge/riser assets: two reproducible 240x160 backgrounds, registered terrain and shared GBA palette; provisional geometry')
if __name__=='__main__':main()
