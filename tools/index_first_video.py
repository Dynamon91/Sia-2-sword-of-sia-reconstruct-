"""Extract exact requested timestamps from the supplied first video, without audio."""
from pathlib import Path
import argparse,subprocess,json
from PIL import Image,ImageDraw

def main():
 p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('--out',type=Path,default=Path('reference/w1l1'));a=p.parse_args();(a.out/'frames').mkdir(parents=True,exist_ok=True)
 times=list(range(0,111,10))+list(range(114,365,5))+[367]
 frames=[]
 for i,t in enumerate(times):
  dest=a.out/'frames'/f'{i:03d}.png'
  subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',a.video,'-map','0:v:0','-frames:v','1','-vf','scale=240:160','-y',str(dest)],check=True)
  frames.append({'file':str(dest.relative_to(a.out)),'requested_video_seconds':t,'role':'reference_only_not_gameplay_asset'})
 out=Image.new('RGB',(1200,((len(frames)+4)//5)*184),'#151d2b');d=ImageDraw.Draw(out)
 for i,item in enumerate(frames):
  x=i%5*240;y=i//5*184;t=item['requested_video_seconds']
  with Image.open(a.out/item['file']) as im:out.paste(im,(x,y))
  d.text((x+5,y+163),f'{t//60:02d}:{t%60:02d}',fill='white')
 out.save(a.out/'full_route_overview.jpg',quality=88)
 (a.out/'frame_index.json').write_text(json.dumps({'source':Path(a.video).name,'audio_extracted':False,'frames':frames},indent=2)+'\n')
 print('Indexed',len(frames),'exact requested timestamps; reference only')
if __name__=='__main__':main()
