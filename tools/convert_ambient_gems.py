"""Extract observed collectible animation without confusing camera motion with bobbing."""
from pathlib import Path
import argparse,json,numpy as np
from PIL import Image,ImageDraw
from convert_room import extract
from repair_sprite_edges import indexed
p=argparse.ArgumentParser();p.add_argument('video');a=p.parse_args();out=Path(__file__).resolve().parents[1]/'assets';header=(out/'room.bin').read_bytes()[:512];frames=[];info=[]
for i,t in enumerate([114,114.2,114.4,114.6]):
 im=extract(a.video,t);rgb=np.asarray(im).astype(int);r,g,b=rgb.transpose(2,0,1)
 mask=(g>r*1.25)&(g>b*1.1)&(g>90);region=np.zeros_like(mask);region[45:95,100:135]=True
 yy,xx=np.where(mask&region);assert len(xx)>5
 cx=round((xx.min()+xx.max())/2);cy=round((yy.min()+yy.max())/2)
 pose=im.crop((cx-8,cy-8,cx+8,cy+8)).convert('RGBA')
 alpha=Image.new('L',(16,16));ImageDraw.Draw(alpha).polygon([(8,0),(15,7),(8,15),(0,7)],fill=255)
 # Reject blue recording sky inside the crop, retaining the gem's dark outline.
 pixels=np.asarray(pose).astype(int);pr,pg,pb=pixels[:,:,:3].transpose(2,0,1)
 sky=(pb>pg+8)&(pb>pr+10)
 mask=np.asarray(alpha).copy();mask[sky]=0
 pose.putalpha(Image.fromarray(mask))
 frames.append(indexed(pose,header).tobytes());pose.save(out/f'ambient_gem_{i}.png');info.append({'seconds':t,'center':[cx,cy]})
(out/'ambient_gems.bin').write_bytes(b''.join(frames));(out/'ambient_gems.json').write_text(json.dumps({'frames':info,'size':[16,16],'timing':'estimated eight game ticks per pose','limits':['camera motion removed by tracking gem center','not original sprite sheet; other scenery layers remain pending']},indent=2)+'\n')
print('Built four observed ambient collectible poses')
