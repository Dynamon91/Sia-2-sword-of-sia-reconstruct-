"""Next registered lower-strip view, recovered from the 186.1 s exposure."""
from pathlib import Path
import argparse,io,json,hashlib,struct
import numpy as np
from PIL import Image
from audit_route_continuation import match
from convert_bridge_run import sky_fill,quantize
def encode_sky_overlay(patch):
 # Row offsets and opaque runs avoid scanning empty pixels. Each run has
 # even/odd aligned copies, allowing GBA DMA for either camera parity.
 table=bytearray(55*2);runs=bytearray()
 for y,row in enumerate(patch):
  edges=np.diff(np.r_[False,row!=0,False].astype(np.int8))
  starts=np.flatnonzero(edges==1);ends=np.flatnonzero(edges==-1)
  struct.pack_into('<H',table,y*2,len(table)+len(runs))
  runs.extend([len(starts),0])
  for x,end in zip(starts,ends):
   pixels=row[x:end].tobytes();n=len(pixels)
   runs.extend([int(x),n]);runs.extend(pixels)
   if n&1:runs.append(0)
   runs.append(0);runs.extend(pixels)
   if not n&1:runs.append(0)
 return bytes(table+runs)

def restored_sky_overlay(image,header):
 # Registered lower terrain does not register parallax clouds. Reconstruct
 # only the sky above the recovered floor instead of copying its old exposure.
 a=np.asarray(image.convert('RGB')).copy();fixed=a.copy()
 actor_sky=np.zeros((160,240),bool);actor_sky[37:55,142:192]=True
 # The floor at row 55 is a boundary, never a source of cloud colors.
 work=a.copy();work[55:]=np.median(a[45,10:70],axis=0).astype(np.uint8)
 sky_fill(work,actor_sky,(10,70),45)
 fixed[actor_sky]=work[actor_sky]
 mask=actor_sky.copy();mask[:45,204:240]=True
 rgb=a.astype(np.int16)
 header_sky=(rgb[:,:,1]>=rgb[:,:,0])&(rgb[:,:,2]>=rgb[:,:,1]-8)
 mask[:14]|=header_sky[:14]
 patch=np.zeros((55,240),dtype=np.uint8)
 indices=sky_patch_indices(Image.fromarray(fixed[:55]),header)
 patch[mask[:55]]=indices[mask[:55]]
 return patch,mask

def sky_patch_indices(image,header):
 words=np.frombuffer(header,dtype='<u2')
 colors=np.array([[(int(w)>>s&31)*255//31 for s in (0,5,10)] for w in words],dtype=np.int32)
 candidates=colors[1:240]
 allowed=(candidates[:,1]>=candidates[:,0])&(candidates[:,2]>=candidates[:,1]-8)
 ids=np.flatnonzero(allowed)+1
 rgb=np.asarray(image.convert('RGB')).astype(np.int32)
 flat=rgb.reshape(-1,3);result=np.empty(len(flat),dtype=np.uint8)
 for start in range(0,len(flat),1024):
  delta=flat[start:start+1024,None,:]-colors[ids][None,:,:]
  result[start:start+1024]=ids[np.sum(delta*delta,axis=2).argmin(1)]
 return result.reshape(rgb.shape[:2])
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
 header=(ROOT/'assets/continuation_palette.bin').read_bytes()
 data,preview=quantize(a,holes,header)
 sky_patch,sky_mask=restored_sky_overlay(Image.fromarray(a),header)
 words=np.frombuffer(header,dtype='<u2')
 colors=np.array([[(int(w)>>s&31)*255//31 for s in (0,5,10)] for w in words],dtype=np.uint8)
 preview_pixels=np.asarray(preview).copy()
 changed=sky_patch!=0
 preview_pixels[:55][changed]=colors[sky_patch[changed]]
 assert np.all(colors[sky_patch[changed]][:,1]>=colors[sky_patch[changed]][:,0])
 assert np.all(colors[sky_patch[changed]][:,2].astype(np.int16)>=colors[sky_patch[changed]][:,1].astype(np.int16)-8)
 preview=Image.fromarray(preview_pixels)
 p=io.BytesIO();Image.fromarray(a).save(p,format='PNG');q=io.BytesIO();preview.resize((720,480),Image.Resampling.NEAREST).save(q,format='PNG')
 manifest={'video_sha256':'7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51','source_seconds':[185,186.1],'source_sha256':[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths],'patches':patches,'origin':[-790,204],'delta':[83,-63],'sky_patch':{'rect':[0,0,240,55],'world_origin':[790,176],'transparent_index':0,'pixels':int(sky_mask.sum()),'actor_sky_rect':[142,37,50,18],'method':'sparse nearest sky-compatible palette overlay; copied parallax sky replaced by harmonic fill with floor excluded; no ordered dither'},'limits':['Player terrain restored through measured lower-terrain registration; covered header/rock edge, avatar sky and sky behind removed actor estimated','Shared world source banks are unchanged; sparse runtime overlay preserves all pixels outside the declared repair mask','Collision floor y=55 and low rock are provisional, not recovered map data','Left boundary of this partial view is the current route limit; no next level is claimed','No intermediate thorn movement or thorn damage is implemented']}
 manifest['sky_patch']['encoding']='55 little-endian row offsets; count/padding, x/length, even and odd aligned opaque run banks'
 return {'crawl_passage_background.bin':data,'crawl_passage_background.png':p.getvalue(),'crawl_passage_background_preview.png':q.getvalue(),'crawl_passage_sky_patch.bin':encode_sky_overlay(sky_patch),'crawl_passage_manifest.json':(json.dumps(manifest,indent=2)+'\n').encode()}
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
 for name,data in outputs().items():
  path=ROOT/'assets'/name
  if a.check:
   if name.endswith('.png'):assert Image.open(path).convert('RGB').tobytes()==Image.open(io.BytesIO(data)).convert('RGB').tobytes(),name
   else:assert path.read_bytes()==data,name
  else:path.write_bytes(data)
 print('PASS crawl passage: registered terrain preserved; sparse sky repair removes copied parallax rectangle and colored header stipple')
if __name__=='__main__':main()
