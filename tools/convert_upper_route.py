"""Reproducible ninth viewport; video occlusions are estimated, not original art."""
from pathlib import Path
import argparse,io,json
import numpy as np
from PIL import Image
from convert_bridge_run import sky_fill,quantize,warm_mask
from convert_continuation_background import png,write,sha
from convert_ui import digit,tiled
from repair_sprite_edges import indexed
ROOT=Path(__file__).resolve().parents[1]

def compose():
 ref=ROOT/'reference/w1l1_continuation/frames'
 original=np.asarray(Image.open(ref/'166_full.png').convert('RGB'));a=original.copy()
 lower=np.asarray(Image.open(ref/'164_full.png').convert('RGB'))
 holes=np.zeros((160,240),bool);terrain=holes.copy();changed=holes.copy()
 holes[51:109,24:85]=True # actor and sword
 holes[56:73,105:121]=True # collectible is rendered separately
 holes[132:160,4:50]=True # flying enemy remains pending
 # Visible island from the preceding camera, registered (+35,+81).
 tile=lower[14:58,0:48];mask=warm_mask(tile)
 for x in range(mask.shape[1]):
  ys=np.flatnonzero(mask[:,x])
  if len(ys):mask[ys[0]:,x]=True
 a[95:139,35:83][mask]=tile[mask];terrain[95:139,35:83]=mask
 # The logo lies entirely on the static wall. Hidden wall detail is estimated.
 a[13:45,204:240]=a[60,204:240];changed[13:45,204:240]=True
 a[:14]=np.median(a[45,90:103],axis=0).astype(np.uint8)
 holes &= ~terrain
 iterations=sky_fill(a,holes,(90,103),125)
 top=a[:15].astype(np.float32);top[:14]=top[14]
 for _ in range(2000):
  p=np.pad(top,((1,1),(1,1),(0,0)),mode='edge');avg=(p[:-2,1:-1]+p[2:,1:-1]+p[1:-1,:-2]+p[1:-1,2:])/4
  delta=np.max(np.abs(top[:14]-avg[:14]));top[:14]=avg[:14]
  if delta<.01:break
 a[:14]=np.rint(top[:14]).clip(0,255).astype('uint8');changed[:14]=True
 changed |= holes|terrain
 assert np.array_equal(a[~changed],original[~changed])
 header=(ROOT/'assets/continuation_palette.bin').read_bytes();binary,preview=quantize(a,holes,header)
 ui=(ROOT/'assets/ui_palette.bin').read_bytes()
 digit_source=Image.open(ref/'139_full.png').convert('RGB')
 five=digit(digit_source.crop((129,29,145,45)))
 manifest={'source_seconds':166,'camera_translation_from_164':[35,81],'geometry':'provisional',
 'unchanged_rgb_pixels':int((~changed).sum()),'sky_fill_iterations':iterations,
 'sources':{str(t):sha((ref/f'{t}_full.png').read_bytes()) for t in [139,164,166]},
 'limits':['Occluded sky, header and wall estimated from visible pixels','Flying enemy removed from background; behavior pending','High jump UP+A is a prototype control, original timing not recovered','Island and ramp geometry provisional']}
 return {'upper_background.bin':binary,'upper_background.png':png(Image.fromarray(a)),
 'upper_background_preview.png':png(preview.resize((720,480),Image.Resampling.NEAREST)),
 'ui_digit5_tiles.bin':bytes(tiled(indexed(five,ui))),'ui_digit5_reference.png':png(five),
 'upper_route_manifest.json':(json.dumps(manifest,indent=2)+'\n').encode()}

def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
 for name,data in compose().items():
  path=ROOT/'assets'/name
  if args.check:
   if name.endswith('.png'):assert Image.open(path).convert('RGBA').tobytes()==Image.open(io.BytesIO(data)).convert('RGBA').tobytes(),name
   else:assert path.read_bytes()==data,name
  else:write(path,data)
 print('PASS upper route assets: reproducible ninth background, separate fifth gem digit; occlusions estimated')
if __name__=='__main__':main()
