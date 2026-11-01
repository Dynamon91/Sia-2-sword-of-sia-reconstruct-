"""Index a supplied World 1 reference video using its gameplay video stream."""
from pathlib import Path
import argparse,subprocess,json,hashlib,zipfile
from PIL import Image,ImageDraw

def main():
 p=argparse.ArgumentParser();p.add_argument('video',type=Path);p.add_argument('--key',required=True);p.add_argument('--step',type=int,default=5);p.add_argument('--out',type=Path,default=Path('reference'));a=p.parse_args()
 if a.step<1:raise SystemExit('step must be positive')
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(a.video)]))
 duration=float(probe['format']['duration']);out=a.out/a.key;(out/'frames').mkdir(parents=True,exist_ok=True)
 times=sorted(set(list(range(0,int(duration),a.step))+[max(0,int(duration)-1)]));frames=[]
 for i,t in enumerate(times):
  name=f'frames/{i:03d}.png'
  subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(a.video),'-map','0:v:0','-frames:v','1','-vf','scale=240:160','-y',str(out/name)],check=True)
  with Image.open(out/name) as im:assert im.size==(240,160)
  frames.append({'file':name,'requested_video_seconds':t})
 sheet=Image.new('RGB',(960,((len(frames)+3)//4)*184),'#142033');d=ImageDraw.Draw(sheet)
 for i,f in enumerate(frames):
  x=i%4*240;y=i//4*184;sheet.paste(Image.open(out/f['file']),(x,y));t=f['requested_video_seconds'];d.text((x+4,y+163),f'{t//60:02d}:{t%60:02d}',fill='white')
 sheet.save(out/'overview.jpg',quality=88)
 meta={'source':a.video.name,'source_sha256':hashlib.sha256(a.video.read_bytes()).hexdigest(),'duration_seconds':duration,'step_seconds':a.step,'status':'reference_only_not_integrated_in_rom','frames':frames}
 (out/'index.json').write_text(json.dumps(meta,indent=2)+'\n')
 archive=a.out/(a.key+'_reference.zip')
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for f in sorted(out.rglob('*')):
   if f.is_file():z.write(f,f.relative_to(a.out))
 with zipfile.ZipFile(archive) as z:assert z.testzip() is None
 print(a.key,len(frames),'frames;',archive.stat().st_size,'ZIP bytes')
if __name__=='__main__':main()
