"""Second viewport from 124 s, cleaned using a registered 123.5 s frame.
Keeps the first area's palette so Sia/gem assets can be shared.
"""
from pathlib import Path
import argparse,json,numpy as np
from PIL import Image
from convert_room import extract,pose

def main():
 p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('--out',default='assets');a=p.parse_args()
 out=Path(a.out);im=extract(a.video,124);earlier=extract(a.video,123.5);bg=im.copy()
 # Background registration: earlier -> current is (-60,+8) native pixels.
 # Sky is parallaxed independently: interpolate its local edges rather than
 # applying the foreground registration to the entire character rectangle.
 for y in range(56,98):
  left=im.getpixel((57,y));right=im.getpixel((98,y))
  for x in range(58,98):
   w=(x-57)/41
   bg.putpixel((x,y),tuple(round(left[k]*(1-w)+right[k]*w) for k in range(3)))
 bg.paste(earlier.crop((118,90,157,99)),(58,98))
 bg.paste(bg.crop((155,73,174,92)),(132,73))
 bg.paste(bg.crop((140,14,172,46)),(208,0))
 for y in range(13):
  for x in range(240):bg.putpixel((x,y),bg.getpixel((x,13)))
 run=pose(im,bg,75,105,(58,58,96,105))
 header=(out/'room.bin').read_bytes()[:512]
 values=np.frombuffer(header,dtype='<u2')
 colors=[]
 for v in values:
  colors.extend([int(((v>>s)&31)*255//31) for s in (0,5,10)])
 pal=Image.new('P',(1,1));pal.putpalette(colors)
 rgb=np.array(colors).reshape(256,3);black=1+np.argmin(np.sum(rgb[1:240].astype(float)**2,axis=1))
 def indexed(pic):
  arr=np.array(pic.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE));arr[arr==0]=black
  return arr
 (out/'bridge.bin').write_bytes(header+indexed(bg).tobytes())
 sky=Image.new('RGB',(240,48))
 for y in range(48):
  w=(y/47)**3
  for x in range(240):
   c=bg.getpixel((x,13));blue=(78,123,153)
   sky.putpixel((x,y),tuple(round(blue[k]*(1-w)+c[k]*w) for k in range(3)))
 (out/'bridge_sky.bin').write_bytes(indexed(sky).tobytes())
 arr=indexed(run);arr[np.asarray(run.getchannel('A'))==0]=0
 (out/'bridge_run.bin').write_bytes(arr.tobytes())
 bg.save(out/'bridge_background_reference.png');run.save(out/'bridge_run_reference.png')
 (out/'bridge_manifest.json').write_text(json.dumps({'source_times':[123.5,124],
  'registration':[-60,8],'method':'registered temporal patch, shared palette, approximate sprite mask',
  'platforms':[[33,100,48],[81,100,125],[206,100,34]],'gem':[141,82],
  'shared_island_first_to_bridge':[-152,60],'sprite_anchor':[24,56],
  'transition':'discrete viewport change, not continuous camera reconstruction',
  'limits':['no later cliff/crouch sections','no enemies or combat','approximate sky fill']},indent=2)+'\n')
 print('Built second viewport, sky extension and extra running pose')
if __name__=='__main__':main()
