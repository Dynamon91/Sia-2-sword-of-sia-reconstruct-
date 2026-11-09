"""Registered first landing below the lever, with actor restoration from later video."""
from pathlib import Path
import argparse,hashlib,io,json
import numpy as np
from PIL import Image
from audit_route_continuation import match
from convert_bridge_run import quantize,sky_fill
from scipy.ndimage import gaussian_filter,binary_dilation,binary_fill_holes
from repair_sprite_edges import indexed
ROOT=Path(__file__).resolve().parents[1]
def outputs():
 paths=[ROOT/'reference/w1l1_postlever/183.png',ROOT/'reference/w1l1_lower_landing/185.png',ROOT/'reference/w1l1_lower_landing/186_1.png']
 images=[np.asarray(Image.open(p).convert('RGB')) for p in paths];before,a,later=images
 registrations=[]
 for src,dst,boxes,delta in [(before,a,[(24,145,32,152),(44,151,52,158)],[90,-105]),(a,later,[(100,132,116,148),(45,124,61,140)],[83,-63])]:
  patches=[match(src.astype('int16'),dst.astype('int16'),box,0) for box in boxes]
  assert all(p['delta']==delta and p['mae_rgb']<9 and p['runner_up_mae_rgb']-p['mae_rgb']>3 for p in patches),patches
  registrations.append({'delta':delta,'patches':patches})
 a=a.copy();holes=np.zeros((160,240),bool)
 # Restore player and ground from an independently registered later exposure.
 a[102:127,114:157]=later[39:64,197:240]
 a[102:127,157:160]=a[102:127,160:161] # three occluded edge columns estimated
 holes[:14]=True;holes[13:45,204:240]=True
 sky_fill(a,holes,(176,196),45)
 # At left the recording banner hides upper-island terrain: edge extension is provisional.
 a[:14,:165]=a[14:15,:165]
 data,preview=quantize(a,holes,(ROOT/'assets/continuation_palette.bin').read_bytes())
 p=io.BytesIO();Image.fromarray(a).save(p,format='PNG');q=io.BytesIO();preview.resize((720,480),Image.Resampling.NEAREST).save(q,format='PNG')
 manifest={'video_sha256':'7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51','source_seconds':[183,185,186.1],'source_sha256':[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths],'registrations':registrations,'origin':[-873,267],'walk_plane':{'x_range':[0,192],'y':118,'geometry':'provisional'},'open_strip_pose_bounds':[0,80,160,144],'limits':['First lower landing; low rock stops standing movement at x=164, while separate crawl code handles passage','Legacy strip patch retained for audit; runtime uses the post-lever world atlas. Thorn collision and intermediate movement are not implemented','Player pixels restored from later registered video; three edge columns, covered header and sky behind removed tall thorns estimated','The older 182-to-185 inconsistent registration remains rejected; this uses independent 183 terrain patches']}
 # Replace old tall thorns without a rectangular block of mismatched sky.
 observed=np.frombuffer(data[512:],dtype='uint8').reshape(160,240)[80:144,:160]
 old=np.frombuffer((ROOT/'assets/scroll_world.bin').read_bytes()[:810000],dtype='uint8').reshape(540,1500)[193:257,873:1033]
 words=np.frombuffer(data[:512],dtype='<u2');pal=np.array([[(int(w)>>s&31)*255//31 for s in (0,5,10)] for w in words],dtype='int16')
 rgb=pal[old];r,g,b=rgb.transpose(2,0,1)
 foreground=(r>b+8)&(g>b+3)|((r>=b-16)&(g>=b-25)&(rgb.mean(axis=2)<190))
 sky=(~foreground).astype('float32');den=gaussian_filter(sky,5)
 estimated=np.stack([gaussian_filter(rgb[:,:,c]*sky,5)/np.maximum(den,.001) for c in range(3)],axis=2).clip(0,255).astype('uint8')
 repaired=indexed(Image.fromarray(estimated),data[:512])
 old_thorns=binary_dilation(binary_fill_holes(foreground),iterations=1)
 old_thorns[:4]=False;old_thorns[:,76:]=False;old_thorns[38:]=False
 patch=np.zeros((64,160),dtype='uint8');patch[old_thorns]=repaired[old_thorns]
 patch[38:]=observed[38:]
 strip=patch.tobytes()
 return {'lower_strip_open.bin':strip,'lower_landing_background.bin':data,'lower_landing_background.png':p.getvalue(),'lower_landing_background_preview.png':q.getvalue(),'lower_landing_manifest.json':(json.dumps(manifest,indent=2)+'\n').encode()}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
 for name,data in outputs().items():
  p=ROOT/'assets'/name
  if args.check:
   if name.endswith('.png'):assert Image.open(p).convert('RGB').tobytes()==Image.open(io.BytesIO(data)).convert('RGB').tobytes(),name
   else:assert p.read_bytes()==data,name
  else:p.write_bytes(data)
 print('PASS lower landing assets: two independent registrations, video-restored player region, provisional lower walk plane')
if __name__=='__main__':main()
