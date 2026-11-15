"""Recover the recording-covered crawl roof from independently tracked roots."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image
from convert_bridge_run import sky_fill
from convert_crawl_passage import encode_sky_overlay,sky_patch_indices

ROOT=Path(__file__).resolve().parents[1]
BOXES=[(83,77,99,85),(94,85,113,99)]

def match_root(source,target,box):
 # Sky moves independently. Score only warm interior foreground samples;
 # reject candidate rectangles touching the target's banner or avatar.
 x0,y0,x1,y1=box
 tile=source[y0:y1,x0:x1].astype(np.int16)
 r,g,b=tile.transpose(2,0,1)
 mask=(r>b+8)&(g>b+3)&(r<210)
 if mask.sum()<30:raise ValueError('Insufficient foreground evidence')
 h,w=mask.shape;scores=[]
 target=target.astype(np.int16)
 for y in range(14,161-h):
  for x in range(241-w):
   if y<45 and x+w>204:continue
   error=float(np.abs(target[y:y+h,x:x+w][mask]-tile[mask]).mean())
   scores.append((error,x-x0,y-y0))
 scores.sort();error,dx,dy=scores[0]
 return {'patch':list(box),'foreground_pixels':int(mask.sum()),
         'delta':[dx,dy],'mae_rgb':round(error,6),
         'runner_up_mae_rgb':round(scores[1][0],6),
         'accepted':error<9 and scores[1][0]-error>3}

def build_overlay():
 paths=[ROOT/'reference/w1l1_lower_landing/185.png',ROOT/'reference/w1l1_lower_landing/186_1.png']
 source,target=[np.asarray(Image.open(p).convert('RGB')) for p in paths]
 registrations=[match_root(source,target,box) for box in BOXES]
 assert all(p['accepted'] and p['delta']==[83,-63] for p in registrations)
 # The two boxes share no sampled pixel, including along their row boundary.
 a,b=BOXES
 assert a[2]<=b[0] or b[2]<=a[0] or a[3]<=b[1] or b[3]<=a[1]
 ambiguous=match_root(source,target,(99,77,113,99))
 assert not ambiguous['accepted']
 indexed=(ROOT/'assets/lower_landing_background.bin').read_bytes()
 palette=(ROOT/'assets/continuation_palette.bin').read_bytes()
 assert indexed[:512]==palette
 recorded=np.frombuffer(indexed[512:],np.uint8).reshape(160,240)[63:77,:157]
 rgb=source.astype(np.int16);r,g,b=rgb.transpose(2,0,1)
 warm=(r>b+8)&(g>b+3)
 neutral=(r>=b-16)&(g>=b-25)&(rgb.mean(axis=2)<190)
 roof=(warm|neutral)[63:77,:157]
 # This rectangle is fully hidden by the recording banner. Clear the former
 # stretched-root columns as well as adding recovered foreground. Never copy
 # the old exposure's parallax sky into the new view.
 fixed=np.asarray(Image.open(ROOT/'assets/crawl_passage_background.png').convert('RGB')).copy()
 recovered=np.zeros((160,240),bool);recovered[:14,83:240]=roof
 fixed[:14,83:240][roof]=source[63:77,:157][roof]
 sky=np.zeros((160,240),bool);sky[:14,83:240]=~roof
 sky_fill(fixed,sky,(100,132),45)
 patch=np.zeros((55,240),np.uint8)
 sky_indices=sky_patch_indices(Image.fromarray(fixed[:14]),palette)
 patch[:14,83:240]=sky_indices[:,83:240]
 patch[:14,83:240][roof]=recorded[roof]
 assert np.all((patch[:14,83:240]>0)&(patch[:14,83:240]<240))
 manifest={'video_sha256':'7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51',
  'source_seconds':[185,186.1],
  'source_sha256':[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths],
  'method':'Exhaustive integer search using foreground-only samples; banner/avatar targets excluded; two disjoint patches required',
  'registrations':registrations,'rejected_repeated_root':ambiguous,
  'source_rect':[0,63,157,14],'target_rect':[83,0,157,14],
  'world_origin':[790,176],'encoded_extent':[240,55],
  'recovered_foreground_pixels':int(roof.sum()),'estimated_sky_pixels':int(sky.sum()),
  'sampled_indexed_pixels_sha256':hashlib.sha256(recorded.tobytes()).hexdigest(),
  'palette_sha256':hashlib.sha256(palette).hexdigest(),
  'observed_target_pixels_changed':0,
  'limits':['Only the recording-covered header is repaired; visible roots and ground remain unchanged',
            'Foreground mask follows visible source colors; sky behind the recording is still estimated',
            'Other unrecorded corners and scenery seams remain unfinished; no moving-thorn behavior inferred']}
 return patch,recovered,sky,manifest

def outputs():
 patch,recovered,sky,manifest=build_overlay()
 manifest['encoded_bytes']=len(encode_sky_overlay(patch))
 return {'crawl_passage_roof_patch.bin':encode_sky_overlay(patch),
         'crawl_passage_roof_manifest.json':(json.dumps(manifest,indent=2)+'\n').encode()}

def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
 for name,data in outputs().items():
  path=ROOT/'assets'/name
  if args.check:assert path.read_bytes()==data,name
  else:path.write_bytes(data)
 print('PASS crawl roof: two disjoint foreground registrations; recorded header terrain restored without copying parallax sky')

if __name__=='__main__':main()
