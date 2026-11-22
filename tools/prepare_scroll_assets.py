"""Build a deterministic world atlas from registered viewports, with aligned DMA banks."""
from pathlib import Path
import argparse,hashlib,json,struct,re
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation,binary_fill_holes,gaussian_filter
from repair_sprite_edges import indexed
ROOT=Path(__file__).resolve().parents[1]
NAMES=['room','bridge','cliff','guard_room','gap','continuation_background','bridge_run_background','riser_background','upper_background','ramp_lower_background','ramp_upper_background','island_gap_background','lever_entry_background','lever_room_background','post_lever_background','lower_landing_background','crawl_passage_background','ladder_hall_background','ladder_foot_background','ladder_upper_background','ladder_upper_exit_background']
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
 text=(ROOT/'src/view_camera.h').read_text();block=text.split('view_origin[VIEW_COUNT][2]=',1)[1].split(';',1)[0]
 numbers=list(map(int,re.findall(r'-?\d+',block)));origins=list(zip(numbers[::2],numbers[1::2]));assert len(origins)==len(NAMES)
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
 # A reconstructed recording header must not cover an unobscured pixel from
 # another registered view. Preserve the original priority between real pixels.
 header_replaced=0
 for area in range(6,11):
  (ox,oy),image=origins[area],pictures[area]
  x,y=-ox,380-oy;ids=owner[y:y+160,x:x+240]
  yy,xx=np.indices(image.shape);valid=yy>=14
  valid[13:45,204:240]=False # recording avatar; estimated in each source
  replace=np.zeros(image.shape,dtype=bool)
  for previous in range(6,area):
   previous_top=380-origins[previous][1]
   replace|=(ids==previous)&(y+yy<previous_top+14)&valid
  target=atlas[y:y+160,x:x+240]
  target[replace]=image[replace];ids[replace]=area
  header_replaced+=int(replace.sum())
 # The upper wall continues beyond the captured rectangle. The former fixed
 # sky fallback cut rectangular holes through it as the camera rose or moved
 # right. Extend the nearest edge of this registered view only into unrecorded
 # pixels; the hidden wall/sky remains an explicit approximation.
 wall_area=8;wall_left,wall_top=-origins[wall_area][0],380-origins[wall_area][1]
 wy,wx=np.indices(atlas.shape)
 wall_extension=(owner==255)&(wx>=wall_left)&(wy<wall_top+160)
 wall_y=np.clip(wy-wall_top,0,159);wall_x=np.clip(wx-wall_left,0,239)
 recorded_before=atlas[owner!=255].copy()
 atlas[wall_extension]=pictures[wall_area][wall_y[wall_extension],wall_x[wall_extension]]
 assert np.array_equal(atlas[owner!=255],recorded_before)
 # Feather only sky at viewport borders; never blur platform or actor pixels.
 words=np.frombuffer(palette,dtype='<u2');colors=np.array([[(int(w)>>s&31)*255//31 for s in (0,5,10)] for w in words],dtype='uint8')
 rgb=colors[atlas].astype('float32');foreground=np.zeros((height,width),dtype=bool)
 for area,((ox,oy),image) in enumerate(zip(origins,pictures)):
  a=colors[image].astype('int16');r,g,b=a.transpose(2,0,1)
  warm=(r>b+8)&(g>b+3);neutral=(r>=b-16)&(g>=b-25)&(a.mean(axis=2)<190)
  terrain=binary_fill_holes(warm|(neutral&binary_dilation(warm,iterations=2)))
  terrain=binary_dilation(terrain,iterations=1)
  x,y=-ox,380-oy;foreground[y:y+160,x:x+240]|=terrain&(owner[y:y+160,x:x+240]==area)
  if area==wall_area:
   foreground[wall_extension]=terrain[wall_y[wall_extension],wall_x[wall_extension]]
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
 # The later, post-lever exposure has priority in its recorded rectangle only
 # after the switch is open. Do not leave old tall thorns/rock over this view.
 opened=atlas.copy();open_foreground=foreground.copy();boundary=np.zeros_like(open_foreground)
 # Later route exposures supersede recording-covered and older scene pixels.
 # Keeping only the old viewport priority left striped header rectangles in sky.
 for area in [16,17,18,19,20]:
  ox,oy=origins[area];left,top=-ox,380-oy
  opened[top:top+160,left:left+240]=pictures[area]
  a=colors[pictures[area]].astype('int16');r,g,b=a.transpose(2,0,1)
  warm=(r>b+8)&(g>b+3);neutral=(r>=b-16)&(g>=b-25)&(a.mean(axis=2)<190)
  terrain=binary_dilation(binary_fill_holes(warm|neutral),iterations=1)
  open_foreground[top:top+160,left:left+240]=terrain
  boundary[top:top+160,left]=True;boundary[top:top+160,left+239]=True
  boundary[top,left:left+240]=True;boundary[top+159,left:left+240]=True
 region=binary_dilation(boundary,iterations=16)&~open_foreground
 rgb=colors[opened].astype('float32');weight=(~open_foreground).astype('float32');den=gaussian_filter(weight,6,mode='nearest')
 smooth=np.stack([gaussian_filter(rgb[:,:,i]*weight,6,mode='nearest')/np.maximum(den,.001) for i in range(3)],axis=2)
 alpha=np.clip(1-distance_transform_edt(~boundary)/16,0,1)
 blend=np.rint(rgb*(1-alpha[:,:,None])+smooth*alpha[:,:,None]).clip(0,255).astype('uint8')
 before_open=opened.copy();ys,xs=np.nonzero(region)
 for start in range(0,len(xs),1024):
  yy,xx=ys[start:start+1024],xs[start:start+1024]
  d=blend[yy,xx].astype('int32')[:,None,:]-colors[None,1:240,:].astype('int32')
  opened[yy,xx]=(np.sum(d*d,axis=2).argmin(1)+1).astype('uint8')
 assert np.array_equal(opened[open_foreground],before_open[open_foreground])
 open_banks=b''.join(np.roll(opened,-shift,axis=1).tobytes() for shift in range(4))
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
  'header_pixels_replaced_by_visible_source':header_replaced,
  'upper_wall_edge_extension':{'area':wall_area,'pixels':int(wall_extension.sum()),'foreground_pixels':int((wall_extension&foreground).sum()),'observed_pixels_changed':0,'method':'Clamp the registered upper-view edge into unrecorded atlas corners; estimated detail'},
  'sky_repaired_pixels':int(np.count_nonzero(atlas!=before)),
  'open_view_priority':{'areas':[16,17,18,19,20],'rectangles':[[-origins[a][0],380-origins[a][1],240,160] for a in [16,17,18,19,20]],'sky_repaired_pixels':int(np.count_nonzero(opened!=before_open)),'foreground_preserved':True},
  'foreground_pixels_preserved':bool(np.array_equal(atlas[foreground],before[foreground])),
  'method':'Fixed priority between observed viewport pixels; visible source replaces covered headers; upper wall edge fills unrecorded corners; foreground source pixels preserved; four aligned atlas/cloud banks; animated sky spans.',
  'limits':['Sky at recorded viewport borders is feathered as an approximation; terrain pixels remain unchanged','Unrecorded upper-wall corners extend captured edge colors; hidden detail is not recovered','Other unrecorded atlas corners extend a fixed observed sky profile','Early cliff registrations and collision geometry remain provisional','Video-derived overlap seams remain subject to visual refinement','Post-lever bank uses the later recorded pose; intermediate scene movement is not recovered']}
 outputs={'scroll_world_open.bin':open_banks,'scroll_world.bin':banks,'scroll_world_sky.bin':bytes(table+runs),'scroll_sky.bin':bytes(local_table+local_runs),
  'scroll_cloud.bin':bytes(cloud_banks),'scroll_manifest.json':(json.dumps(manifest,indent=2)+'\n').encode()}
 for name,data in outputs.items():
  path=ROOT/'assets'/name
  if args.check:assert path.read_bytes()==data,name
  else:path.write_bytes(data)
 print('PASS world atlas: twenty-one shared palettes, deterministic registrations, lossless aligned source rows and animated sky spans')
if __name__=='__main__':main()

