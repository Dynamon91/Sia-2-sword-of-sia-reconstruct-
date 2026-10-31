"""Reconstruct observed UI elements from the supplied video as native OBJ tiles
and separate dialogue ink. Not recovery of original game asset files.
"""
from pathlib import Path
import argparse,json,struct,numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation,binary_fill_holes,label,find_objects
from convert_room import extract

def white_mask(im):
 a=np.asarray(im.convert('RGB')).astype(int)
 return (a.min(axis=2)>170)&((a.max(axis=2)-a.min(axis=2))<100)
def outlined(mask):
 a=np.zeros((*mask.shape,4),dtype='uint8');outer=binary_dilation(mask)
 a[outer]=[0,0,0,255];a[mask]=[255,244,230,255]
 return Image.fromarray(a)
def digit(im):
 mask=white_mask(im);mask[:,11:]=False
 ids,n=label(mask,structure=np.ones((3,3),dtype=bool));sizes=np.bincount(ids.ravel());sizes[0]=0
 return outlined(ids==sizes.argmax())
def tiled(arr):
 h,w=arr.shape;assert h%8==0 and w%8==0
 return b''.join(arr[y:y+8,x:x+8].tobytes() for y in range(0,h,8) for x in range(0,w,8))
def main():
 p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('--out',default='assets');a=p.parse_args()
 out=Path(a.out);ims={t:extract(a.video,t) for t in [8,112,113.8,120.5,125.5,367]}
 portrait=Image.new('RGBA',(64,64));portrait.paste(ims[112].crop((0,102,64,160)),(0,0))
 # A recorded menu cursor is an actual UI sprite, not the channel portrait.
 cursor=ims[8].crop((16,44,32,60));c=np.asarray(cursor).astype(int)
 green=(c[:,:,1]>50)&(c[:,:,1]>c[:,:,0]*1.3)&(c[:,:,2]<120)
 alpha=binary_dilation(green);cur=np.zeros((16,16,4),dtype='uint8');cur[alpha]=[0,0,0,255]
 cur[green,:3]=c[green];cur[green,3]=255;cursor=Image.fromarray(cur)
 gem=ims[120.5].crop((95,11,127,43)).convert('RGBA');g=np.asarray(gem).astype(int)
 core=(g[:,:,1]>80)&(g[:,:,1]>g[:,:,0]*1.05)&(g[:,:,1]>g[:,:,2]*1.05)
 mask=binary_fill_holes(binary_dilation(core));gem.putalpha(Image.fromarray((mask*255).astype('uint8')))
 digits=[]
 zero=Image.new('RGB',(16,16));zero.paste(ims[367].crop((150,54,160,70)),(3,0));digits.append(digit(zero))
 for t in [120.5,125.5]:digits.append(digit(ims[t].crop((129,29,145,45))))
 objects=[('PORTRAIT',portrait),('GEM',gem),('DIGIT0',digits[0]),('DIGIT1',digits[1]),('DIGIT2',digits[2]),('CURSOR',cursor)]
 atlas=Image.new('RGB',(256,96))
 for i,(_,im) in enumerate(objects):atlas.paste(im.convert('RGB'),([0,72,112,136,160,184][i],0))
 quant=atlas.quantize(colors=239,dither=Image.Dither.NONE);colors=quant.getpalette()[:239*3]
 colors += [0]*(239*3-len(colors));pal=Image.new('P',(1,1));pal.putpalette(colors+colors[:3]*17)
 used=[tuple(colors[i:i+3]) for i in range(0,len(colors),3)];first={c:used.index(c) for c in used}
 all_colors=[tuple(pal.getpalette()[i:i+3]) for i in range(0,768,3)]
 lookup=np.array([first[c]+1 for c in all_colors],dtype='uint8')
 palette=[(0,0,0)]+used+[(0,0,0)]*16
 (out/'ui_palette.bin').write_bytes(b''.join(struct.pack('<H',(r>>3)|((g>>3)<<5)|((b>>3)<<10)) for r,g,b in palette))
 raw=bytearray();header=['#ifndef UI_ASSETS_H','#define UI_ASSETS_H']
 for name,im in objects:
  arr=lookup[np.asarray(im.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE))].copy()
  arr[np.asarray(im.getchannel('A'))==0]=0
  header.append(f'#define UI_{name}_TILE {512+len(raw)//32}')
  raw.extend(tiled(arr));im.save(out/f'ui_{name.lower()}_reference.png')
 assert len(raw)<=16384
 (out/'ui_tiles.bin').write_bytes(raw)
 # The source background is fixed in these two arrival shots. Difference masks
 # retain white letter strokes; an explicit dark outline avoids world-colored halos.
 bg=np.asarray(Image.open(out/'room_background_reference.png').convert('RGB')).astype(int)
 ink=bytearray()
 for i,t in enumerate([112,113.8]):
  src=np.asarray(ims[t]).astype(int);changed=np.max(abs(src-bg),axis=2)>24
  region=np.zeros((160,240),dtype=bool)
  if i==0:region[102:135,70:240]=True
  else:region[102:151,70:240]=True
  raw_mask=white_mask(ims[t])&region;ids,n=label(raw_mask);mask=np.zeros_like(raw_mask)
  for k,box in enumerate(find_objects(ids),1):
   if box is None:continue
   component=ids[box]==k
   if 2<=component.sum()<=100 and box[1].stop-box[1].start<=14 and box[0].stop-box[0].start<=16 and (changed[box]&component).any():
    mask[box] |= component
  outer=binary_dilation(mask);pixels=np.zeros((160,240),dtype='uint8');pixels[outer]=1;pixels[mask]=2
  cropped=pixels[102:160,64:240];ink.extend(cropped.tobytes())
  preview=np.zeros((58,176,4),dtype='uint8');preview[cropped==1]=[0,0,0,255];preview[cropped==2]=[255,244,230,255]
  Image.fromarray(preview).save(out/f'ui_dialog_{i}_reference.png')
 (out/'ui_dialogs.bin').write_bytes(ink)
 header += [f'#define UI_TILE_BYTES {len(raw)}','#define UI_DIALOG_W 176','#define UI_DIALOG_H 58',
  'extern const unsigned char ui_palette[],ui_tiles[],ui_dialogs[];','#endif']
 (out/'ui.h').write_text('\n'.join(header)+'\n')
 info={'source_times':[8,112,113.8,120.5,125.5,367],'portrait':{'source_box':[0,102,64,160],'native_position':[0,102]},
  'gem_counter':{'native_gem_position':[95,11],'native_digit_position':[129,29],'popup_ticks':150,'digits_observed':[0,1,2]},
  'menu_cursor':{'native_position':[16,44],'row_step':24},'obj_tile_bytes':len(raw),'dialogue_method':'source white ink difference masks with reconstructed black outline',
  'limits':['compressed video pixels, not original art','popup duration approximate','blue lower indicator and health behavior not identified','options/pause/credits not verified against original']}
 (out/'ui_manifest.json').write_text(json.dumps(info,indent=2)+'\n')
 print('Built native UI OBJ palette/tiles and two arrival caption masks')
if __name__=='__main__':main()
