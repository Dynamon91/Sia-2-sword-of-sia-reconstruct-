"""Build a deterministic world atlas from registered viewports, with aligned DMA banks."""
from pathlib import Path
import argparse,hashlib,json,struct,re
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation,binary_fill_holes,gaussian_filter
from repair_sprite_edges import indexed
ROOT=Path(__file__).resolve().parents[1]
NAMES=['room','bridge','cliff','guard_room','gap','continuation_background','bridge_run_background','riser_background','upper_background','ramp_lower_background','ramp_upper_background','island_gap_background','lever_entry_background','lever_room_background']
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
 text=(ROOT/'src/view_camera.h').read_text();block=text.split('view_origin[VIEW_COUNT][2]=',1)[1].split(';',1)[0]
 numbers=list(map(int,re.findall(r'-?\d+',block)));origins=list(zip(numbers[::2],numbers[1::2]));assert len(origins)==14
 pictures=[];sources={};palette=None
 for name in NAMES:
  b=(ROOT/'assets'/f'{name}.bin').read_bytes();assert len(b)==38912
  if palette is None:palette=b[:512]
  assert b[:512]==palette
  sources[name]=hashlib.sha256(b).hexdigest();pictures.append(np.frombuffer(b[512:],dtype='uint8').reshape(160,240))
 width,height=1500,540
 atlas=np.empty((height,width),dtype='uint8');owner=np.full((height,width),255,dtype='uint8')
 for y in range(height):atlas[y]=pictures[0][max(14,min(34,y-380)),160]
 for area,((ox,oy),image) in enumerate(zip(origins,pictures)):
  x,y=-ox,380-oy;target=atlas[y:y+160,x:x+240];ids=owner[y:y+160,x:x+240];empty=ids==255
  target[empty]=image[empty];ids[empty]=area
 # Feather only sky at viewport borders; never blur platform or actor pixels.
 words=np.frombuffer(palette,dtype='<u2');colors=np.array([[(int(w)>>s&31)*255//31 for s in (0,5,10)] for w in words],dtype='uint8')
 rgb=colors[atlas].astype('float32');foreground=np.zeros((height,width),dtype=bool)
 for area,((ox,oy),image) in enumerate(zip(origins,pictures)):
  a=colors[image].astype('int16');r,g,b=a.transpose(2,0,1)
  warm=(r>b+8)&(g>b+3);neutral=(r>=b-16)&(g>=b-25)&(a.mean(axis=2)<190)
  terrain=binary_fill_holes(warm|(neutral&binary_dilation(warm,iterations=2)))
  terrain=binary_dilation(terrain,iterations=1)
  x,y=-ox,380-oy;foreground[y:y+160,x:x+240]|=terrain&(owner[y:y+160,x:x+240]==area)
 boundaries=np.zeros_like(foreground);boundaries[1:]|=owner[1:]!=owner[:-1];boundaries[:,1:]|=owner[:,1:]!=owner[:,:-1]
 editable=binary_dilation(boundaries,iterations=32)&~foreground&(owner>=2)
 weights=(~foreground).astype('float32');denominator=gaussian_filter(weights,12,mode='nearest')
 smooth=np.stack([gaussian_filter(rgb[:,:,i]*weights,12,mode='nearest')/np.maximum(denominator,.001) for i in range(3)],axis=2)
 # A smooth blend back to observed sky prevents a new edge around the repair band.
 from scipy.ndimage import distance_transform_edt
 distance=distance_transform_edt(~boundaries);alpha=np.clip(1-distance/32,0,1)
 fixed=np.rint(rgb*(1-alpha[:,:,None])+smooth*alpha[:,:,None]).clip(0,255).astype('uint8')
 before=atlas.copy();ys,xs=np.nonzero(editable)
 for start in range(0,len(xs),1024):
  yy,xx=ys[start:start+1024],xs[start:start+1024]
  d=fixed[yy,xx].astype('int32')[:,None,:]-colors[None,1:240,:].astype('int32')
  atlas[yy,xx]=(np.sum(d*d,axis=2).argmin(1)+1).astype('uint8')
 assert np.array_equal(atlas[foreground],before[foreground])
 banks=b''.join(np.roll(atlas,-shift,axis=1).tobytes() for shift in range(4))
 masks=[np.asarray(Image.open(ROOT/'assets'/f'{name}_layer_mask.png').convert('L')) for name in ['room','bridge']]
 # Independent per-view masks are retained for the host framebuffer regression.
 local_table=bytearray(320);local_runs=bytearray()
 for area in range(2):
  for y in range(80):
   row=masks[area][y]==0;edges=np.diff(np.r_[False,row,False].astype('int8'));starts=np.flatnonzero(edges==1);ends=np.flatnonzero(edges==-1)
   struct.pack_into('<H',local_table,(area*80+y)*2,320+len(local_runs));local_runs.append(len(starts))
   for x,end in zip(starts,ends):local_runs.extend([int(x),int(end-x)])
 table=bytearray(height*2);runs=bytearray()
 for y in range(height):
  spans=[];x=0
  while x<width:
   area=int(owner[y,x])
   if area>=2:x+=1;continue
   ox,oy=origins[area];sx=x+ox;sy=y-380+oy
   if sy>=80 or masks[area][sy,sx]:x+=1;continue
   start=x;local_x=sx;x+=1
   while x<width and owner[y,x]==area and x+ox<240 and not masks[area][sy,x+ox]:x+=1
   spans.append((start,x-start,sy,local_x))
  struct.pack_into('<H',table,y*2,height*2+len(runs));runs.append(len(spans))
  for x,n,sy,sx in spans:runs.extend(struct.pack('<HHBH',x,n,sy,sx))
 cloud=(ROOT/'assets/cloud_strip.bin').read_bytes()[:25600];cloud_banks=bytearray()
 for shift in range(4):
  for y in range(80):
   row=cloud[y*320:(y+1)*320];cloud_banks.extend(row[shift:]+row[:shift])
 manifest={'order':NAMES,'origins':origins,'width':width,'height':height,'world_top':-380,'sources':sources,
  'sky_repaired_pixels':int(np.count_nonzero(atlas!=before)),
  'foreground_pixels_preserved':bool(np.array_equal(atlas[foreground],before[foreground])),
  'method':'Fixed viewport priority independent of gameplay area; foreground source pixels preserved; four aligned atlas/cloud banks; animated sky spans.',
  'limits':['Sky at recorded viewport borders is feathered as an approximation; terrain pixels remain unchanged','Unrecorded atlas corners extend a fixed observed sky profile','Early cliff registrations and collision geometry remain provisional','Video-derived overlap seams remain subject to visual refinement']}
 outputs={'scroll_world.bin':banks,'scroll_world_sky.bin':bytes(table+runs),'scroll_sky.bin':bytes(local_table+local_runs),
  'scroll_cloud.bin':bytes(cloud_banks),'scroll_manifest.json':(json.dumps(manifest,indent=2)+'\n').encode()}
 for name,data in outputs.items():
  path=ROOT/'assets'/name
  if args.check:assert path.read_bytes()==data,name
  else:path.write_bytes(data)
 print('PASS world atlas: fourteen shared palettes, deterministic registrations, lossless aligned source rows and animated sky spans')
if __name__=='__main__':main()
