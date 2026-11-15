"""Recover two manually masked prone poses from the supplied gameplay video."""
from pathlib import Path
import argparse,hashlib,io,json
import numpy as np
from PIL import Image
from repair_sprite_edges import indexed
ROOT=Path(__file__).resolve().parents[1]
# Row intervals are exclusive at the right edge. No scenery-colored padding is opaque.
POSES=[('185_0',185,(108,98,172,134),5,[(21,28),(20,31),(12,32),(11,32),(10,33),(10,34),(10,33),(10,34),(11,35),(11,36),(12,37),(12,37),(12,37),(12,38),(13,40),(13,49),(14,50),(11,51),(10,51),(8,51),(6,49),(6,44)]),
 ('186_1',186.1,(138,32,202,68),7,[(23,28),(21,31),(19,32),(14,32),(13,33),(12,35),(11,35),(11,34),(12,34),(13,35),(13,37),(13,38),(14,39),(14,40),(14,44),(14,48),(12,49),(11,50),(8,51),(6,51),(6,51),(7,51),(9,50)])]
def outputs():
 header=(ROOT/'assets/continuation_palette.bin').read_bytes();stream=bytearray();out={};records=[]
 for name,t,box,top,rows in POSES:
  path=ROOT/'reference/w1l1_crawl'/f'{name}.png';source=Image.open(path).convert('RGB').crop(box)
  a=np.asarray(source);mask=np.zeros((36,64),dtype='uint8')
  for y,(left,right) in enumerate(rows,top):mask[y,left:right]=255
  # The first pose has a small sky gap between upper arm and rear boot.
  if name=='185_0':mask[19,40:42]=0
  rgba=np.dstack((a,mask));pose=Image.fromarray(rgba)
  # Normalize facing and floor anchor without scaling any source pixels.
  canvas=Image.new('RGBA',(64,36));canvas.paste(pose.crop((0,top,64,top+len(rows))),(0,36-len(rows)))
  canvas=canvas.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
  indices=indexed(canvas,header);assert indices.max()<240 and np.any(indices==0) and np.any(indices)
  stream.extend(indices.tobytes());buf=io.BytesIO();canvas.save(buf,format='PNG');out[f'crawl_pose_{len(records)}.png']=buf.getvalue()
  records.append({'seconds':t,'source':str(path.relative_to(ROOT)),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'crop':box,'row_start':top,'row_intervals':rows,'observed_contact_y':box[1]+top+len(rows),'authored_floor_y':118 if name=='185_0' else 55,'opaque_pixels':int(np.count_nonzero(indices))})
 assert all(r['observed_contact_y']-r['authored_floor_y']==7 for r in records)
 assert '#define CRAWL_FLOOR_BIAS 7' in (ROOT/'src/game.h').read_text()
 manifest={'floor_bias_pixels':7,'video_sha256':'7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51','frames':records,'size':[64,36],'anchor':[32,36],'facing':'right; source poses mirrored without resampling','palette_sha256':hashlib.sha256(header).hexdigest(),'limits':['Manual silhouette masks from compressed video; palette quantized to existing 1..239 colors','Crawl timing and movement speed are provisional','Floor alignment uses current authored collision floor; not recovered original hitboxes']}
 out['crawl_cycle.bin']=bytes(stream);out['crawl_manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode();return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
 for name,data in outputs().items():
  path=ROOT/'assets'/name
  if args.check:
   if name.endswith('.png'):assert Image.open(path).convert('RGBA').tobytes()==Image.open(io.BytesIO(data)).convert('RGBA').tobytes(),name
   else:assert path.read_bytes()==data,name
  else:path.write_bytes(data)
 print('PASS crawl assets: two video-derived manually masked poses, lossless facing normalization, transparent zero and bounded palette')
if __name__=='__main__':main()
