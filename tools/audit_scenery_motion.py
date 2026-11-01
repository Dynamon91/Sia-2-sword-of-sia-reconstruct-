"""Measure observed scenery motion separately from camera movement and actors.
Outputs timestamped frames and a comparison sheet; these are video references,
not ROM screenshots or recovered original animation assets.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from convert_room import extract

def main():
 ap=argparse.ArgumentParser();ap.add_argument('video',type=Path);ap.add_argument('--start',type=float,default=114);ap.add_argument('--step',type=float,default=.2);ap.add_argument('--count',type=int,default=12);ap.add_argument('--out',type=Path,default=Path('build/scenery_motion'));a=ap.parse_args()
 if not 2<=a.count<=120 or a.step<=0:ap.error('count 2..120 and positive step required')
 a.out.mkdir(parents=True,exist_ok=True);frames=[];entries=[]
 # Upper sky avoids the original gameplay character, HUD and channel portrait.
 # Camera movement still requires registration before any ROM integration.
 box=(0,14,90,58)
 for i in range(a.count):
  t=round(a.start+i*a.step,6);im=extract(str(a.video),t);frames.append(im)
  name=f'frame_{i:03d}.png';im.save(a.out/name)
  crop=np.asarray(im.crop(box)).astype(np.int16)
  delta=None if i==0 else float(np.abs(crop-previous).mean())
  entries.append({'file':name,'seconds':t,'sky_mean_absolute_change':delta});previous=crop
 sheet=Image.new('RGB',(960,175*((a.count+3)//4)))
 for i,im in enumerate(frames):
  x=i%4*240;y=i//4*175;sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x+3,y+161),str(entries[i]['seconds'])+' s',fill='white')
 sheet.save(a.out/'comparison.png')
 h=hashlib.sha256()
 with a.video.open('rb') as source:
  for block in iter(lambda:source.read(1024*1024),b''):h.update(block)
 report={'source_sha256':h.hexdigest(),'sky_roi':box,'frames':entries,'status':'reference audit only','limits':['Camera/parallax must be registered before deriving animation','Compression noise also contributes to measured change','Not integrated in ROM; no inferred wind or movement is added']}
 (a.out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Scenery motion reference audit:',len(frames),'frames;',a.out)
if __name__=='__main__':main()
