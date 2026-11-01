"""Approximate fourth viewport and guard cutout from supplied recording at 145s."""
from pathlib import Path
from PIL import Image,ImageDraw
import argparse,json,numpy as np
from convert_room import extract
p=argparse.ArgumentParser();p.add_argument('video');a=p.parse_args();out=Path(__file__).resolve().parents[1]/'assets';im=extract(a.video,145)
actor=im.crop((137,35,178,95)).convert('RGBA');mask=Image.new('L',actor.size);ImageDraw.Draw(mask).polygon([(15, 6), (18, 7), (21, 9), (23, 15), (26, 16), (29, 16), (29, 23), (27, 26), (29, 33), (29, 38), (26, 40), (25, 50), (28, 51), (28, 53), (16, 54), (15, 52), (18, 50), (19, 43), (16, 41), (16, 36), (18, 33), (15, 32), (11, 29), (9, 27), (6, 26), (3, 24), (1, 21), (0, 18), (3, 16), (7, 15), (9, 20), (11, 20), (10, 17), (9, 13), (9, 9), (12, 8)],fill=255);actor.putalpha(mask)
bg=im.copy()
# Reuse observed terrain instead of inventing a flat ramp. Registration was
# measured against the static rock texture; sky parallax is not identical.
earlier=extract(a.video,144);later=extract(a.video,146)
bg.paste(earlier.crop((160,43,207,102)),(44,55)) # (-116,+12)
bg.paste(later.crop((129,56,170,116)),(137,35)) # (+8,-21)
# Recording overlays hide the upper sky. Reconstruct only those occlusions,
# keeping actual trees, rocks and visible cloud pixels.
for left,top,right,bottom in [(94,14,140,46),(208,14,240,36)]:
 bg.paste(later.crop((left-8,top+21,right-8,bottom+21)),(left,top))
for left,top,right,bottom in [(151,47,168,65)]:
 for y in range(top,bottom):
  lc=bg.getpixel((left-1,y));rc=bg.getpixel((right,y)) if right<240 else bg.getpixel((200,y))
  for x in range(left,right):
   w=(x-left+1)/(right-left+1)
   bg.putpixel((x,y),tuple(round(lc[k]*(1-w)+rc[k]*w) for k in range(3)))
# Exclude the video title's white horizontal border at rows 11-13.
for y in range(14):
 for x in range(240):bg.putpixel((x,y),bg.getpixel((x,14)))
header=(out/'room.bin').read_bytes()[:512];colors=[]
for v in np.frombuffer(header,dtype='<u2'):colors.extend(int(((v>>s)&31)*255//31) for s in (0,5,10))
pal=Image.new('P',(1,1));pal.putpalette(colors)
def idx(image):
 arr=np.array(image.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE));arr[arr==0]=int(1+np.argmin(np.sum(np.array(colors).reshape(256,3)[1:240].astype(float)**2,axis=1)));return arr
(out/'guard_room.bin').write_bytes(header+idx(bg).tobytes());arr=idx(actor);arr[np.asarray(mask)==0]=0;(out/'guard_sprite.bin').write_bytes(arr.tobytes())
bg.save(out/'guard_room_reference.png');actor.save(out/'guard_cutout.png')
(out/'guard_manifest.json').write_text(json.dumps({'source_seconds':145,'sprite_crop':[137,35,178,95],'sprite_size':[41,60],'sprite_anchor':[20,55],'mask':'hand traced approximate silhouette','background':'registered terrain from 144s (-116,+12), 146s (+8,-21); upper overlay sky interpolated' ,'limits':['single pose, no recovered animation','approximate collision and patrol','new transition skips unimplemented corridor between video127 and145']},indent=2)+'\n')
