"""Approximate fourth viewport and guard cutout from supplied recording at 145s."""
from pathlib import Path
from PIL import Image,ImageDraw
import argparse,json,numpy as np
from convert_room import extract
p=argparse.ArgumentParser();p.add_argument('video');a=p.parse_args();out=Path(__file__).resolve().parents[1]/'assets';im=extract(a.video,145)
actor=im.crop((137,35,178,95)).convert('RGBA');mask=Image.new('L',actor.size);ImageDraw.Draw(mask).polygon([(11,4),(22,4),(29,12),(28,20),(34,21),(33,40),(28,44),(26,55),(12,55),(13,48),(16,44),(13,40),(13,31),(5,27),(1,20),(0,10),(8,9)],fill=255);actor.putalpha(mask)
bg=im.copy()
for left,top,right,bottom in [(0,0,240,14),(208,0,240,35),(56,57,94,115),(134,35,179,91),(95,14,114,37)]:
 for y in range(top,bottom):
  lc=im.getpixel((max(0,left-1),max(y,14)));rc=im.getpixel((min(239,right),max(y,14)))
  for x in range(left,right):
   w=(x-left)/max(1,right-left);bg.putpixel((x,y),tuple(round(lc[k]*(1-w)+rc[k]*w) for k in range(3)))
for y in range(14):
 for x in range(240):bg.putpixel((x,y),(78,123,153))
header=(out/'room.bin').read_bytes()[:512];colors=[]
for v in np.frombuffer(header,dtype='<u2'):colors.extend(int(((v>>s)&31)*255//31) for s in (0,5,10))
pal=Image.new('P',(1,1));pal.putpalette(colors)
def idx(image):
 arr=np.array(image.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE));arr[arr==0]=1;return arr
(out/'guard_room.bin').write_bytes(header+idx(bg).tobytes());arr=idx(actor);arr[np.asarray(mask)==0]=0;(out/'guard_sprite.bin').write_bytes(arr.tobytes())
bg.save(out/'guard_room_reference.png');actor.save(out/'guard_cutout.png')
(out/'guard_manifest.json').write_text(json.dumps({'source_seconds':145,'sprite_crop':[137,35,178,95],'sprite_size':[41,60],'sprite_anchor':[20,55],'mask':'hand traced approximate silhouette','background':'interpolated occlusions; shared first-area palette','limits':['single pose, no recovered animation','approximate collision and patrol','new transition skips unimplemented corridor between video127 and145']},indent=2)+'\n')
