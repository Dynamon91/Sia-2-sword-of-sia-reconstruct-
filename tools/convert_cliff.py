"""Third playable viewport from video 127s; occluded background is estimated."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image
from convert_room import extract
p=argparse.ArgumentParser();p.add_argument('video');a=p.parse_args();out=Path(__file__).resolve().parents[1]/'assets'
im=extract(a.video,127)
# Remove recording overlays and moving actor/bat; interpolation is an approximation.
for left,top,right,bottom in [(0,0,240,14),(208,0,240,35),(43,55,101,114),(110,17,147,36),(7,22,29,45)]:
 for y in range(top,bottom):
  lc=im.getpixel((max(0,left-1),max(14,y)));rc=im.getpixel((min(239,right),max(14,y)))
  for x in range(left,right):
   w=(x-left)/max(1,right-left);im.putpixel((x,y),tuple(round(lc[k]*(1-w)+rc[k]*w) for k in range(3)))
for y in range(14):
 for x in range(240):im.putpixel((x,y),(78,123,153))
header=(out/'room.bin').read_bytes()[:512];colors=[]
for v in np.frombuffer(header,dtype='<u2'):colors.extend(int(((v>>s)&31)*255//31) for s in (0,5,10))
pal=Image.new('P',(1,1));pal.putpalette(colors)
arr=np.asarray(im.quantize(palette=pal,dither=Image.Dither.NONE))
(out/'cliff.bin').write_bytes(header+arr.tobytes());im.save(out/'cliff_reference.png')
(out/'cliff_manifest.json').write_text(json.dumps({'video_seconds':127,'platforms':[[0,54,43],[96,115,144]],'limits':['Occluded pixels interpolated','Collision geometry approximated from visible ledges','Discrete transitions use provisional entry points','Later corridor not yet integrated']},indent=2))
