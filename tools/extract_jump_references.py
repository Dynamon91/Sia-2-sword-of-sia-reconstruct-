"""Extract unmasked jump references; these images are not runtime sprites."""
from pathlib import Path
import argparse,json,hashlib
from PIL import Image,ImageDraw
from convert_room import extract
p=argparse.ArgumentParser();p.add_argument('video',type=Path);p.add_argument('--out',type=Path,default=Path('build/jump_references'));a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
times=[119.5,119.6,119.68,119.76,120,120.08,120.16,120.24,120.32,120.4]
sheet=Image.new('RGB',(1200,360));frames=[]
for i,t in enumerate(times):
 im=extract(str(a.video),t);im.save(a.out/f'frame_{i:02}.png');x=i%5*240;y=i//5*180;sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x+4,y+162),f'{t:.2f}s - VIDEO REFERENCE',fill='white');frames.append({'seconds':t,'file':f'frame_{i:02}.png'})
sheet.save(a.out/'comparison.png')
report={'video_sha256':hashlib.sha256(a.video.read_bytes()).hexdigest(),'frames':frames,'integrated_in_rom':False,'status':'unmasked reference frames; candidate masks rejected for scenery contamination','next_checks':['trace full silhouette and sword','compensate camera shift','preserve boot anchor','select poses from actual vertical motion','verify rendered sprite in emulator']}
(a.out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Extracted',len(frames),'unmasked references; runtime assets unchanged')
