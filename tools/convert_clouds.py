"""Recover the observed upper-cloud strip and encode aligned GBA scroll banks.

The source confirms speed and dialogue stops, not a complete texture period.
The 320px loop and covered top band remain authored reconstruction estimates.
"""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, gaussian_filter1d
from convert_room import extract
from repair_sprite_edges import indexed

ROOT=Path(__file__).resolve().parents[1]
WIDTH,HEIGHT=320,80

def main():
 p=argparse.ArgumentParser();p.add_argument('--video',type=Path);a=p.parse_args()
 assets=ROOT/'assets';header=(assets/'room.bin').read_bytes()[:512]
 if a.video:
  times=[round(114+i*.2,2) for i in range(33)]
  frames=[np.asarray(extract(str(a.video),t)).astype(float) for t in times]
  shifts=[0];errors=[0.0]
  for previous,current in zip(frames,frames[1:]):
   patch=previous[14:34,40:180]
   error,dx=min((float(np.mean(abs(patch-current[14:34,40+dx:180+dx]))),dx) for dx in range(-10,3))
   assert error<2 and -6<=dx<=0,(error,dx)
   shifts.append(shifts[-1]-dx);errors.append(error)
  assert shifts[:6]==[0,6,12,18,24,30]
  assert len(set(shifts[6:15]))==1,'Observed dialogue should freeze cloud motion'
  valid=np.ones((HEIGHT,240),bool)
  valid[:16]=False;valid[16:35,204:]=False # recording overlays and compression fringe
  valid[35:68,183:]=False                # floating rock
  valid[62:,:33]=False                   # tree silhouette
  valid[58:,105:129]=False               # collectible
  valid[54:,25:105]=False                # moving character
  stack=np.full((len(times),HEIGHT,WIDTH,3),np.nan,dtype='float32')
  for i,(frame,shift) in enumerate(zip(frames,shifts)):
   n=min(240,WIDTH-shift);part=frame[:HEIGHT,:n].copy();part[~valid[:,:n]]=np.nan
   stack[i,:,shift:shift+n]=part
  # All-NaN cells are expected where overlays/occluders hide the recording.
  import warnings
  with warnings.catch_warnings():
   warnings.simplefilter('ignore',RuntimeWarning);strip=np.nanmedian(stack,axis=0)
  observed=np.isfinite(strip[:,:,0]);_,nearest=distance_transform_edt(~observed,return_indices=True)
  strip[~observed]=strip[tuple(nearest[:,~observed])]
  # The first visible recording rows contain a compression fringe. Estimate
  # the covered band from a smoothed vertical gradient, avoiding stretched
  # single-row columns and a hard horizontal boundary below the old banner.
  slope=gaussian_filter1d(strip[16]-strip[24],2,axis=0)/8
  for y in range(16):
   strip[y]=gaussian_filter1d(strip[16]+(16-y)*slope,(16-y)/8,axis=0)
  # Both ends are observed blue sky. Make a quiet, continuous authored join;
  # the source window is insufficient to claim the original repetition period.
  blue=np.median(np.concatenate((strip[:,:8],strip[:,-8:]),axis=1),axis=1)
  for x in range(12):
   weight=x/12
   strip[:,x]=blue*(1-weight)+strip[:,x]*weight
   strip[:,WIDTH-1-x]=blue*(1-weight)+strip[:,WIDTH-1-x]*weight
  palette=np.frombuffer(header,dtype='<u2')
  colors=np.array([[(int(w)>>s&31)*255//31 for s in (0,5,10)] for w in palette])
  backdrop=np.frombuffer((assets/'room_backdrop.bin').read_bytes()[512:],dtype='uint8').reshape(160,240)
  base=colors[int(backdrop[80,120])]
  # Dither between real palette colors over the clear lower sky rather than
  # introducing an abrupt band where a smooth RGB gradient gets quantized.
  bayer=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])
  for y in range(48,80):
   weight=(y-47)/32
   for x in range(WIDTH):
    if (bayer[y%4,x%4]+.5)/16<weight:strip[y,x]=base
  strip[:,-1]=strip[:,0]
  image=Image.fromarray(np.rint(strip).clip(0,255).astype('uint8'));image.save(assets/'cloud_strip.png')
  report={'source_sha256':hashlib.sha256(a.video.read_bytes()).hexdigest(),
   'samples':[{'seconds':t,'registered_x':s,'mean_rgb_error':round(e,4)} for t,s,e in zip(times,shifts,errors)],
   'observed_speed_pixels_per_second':30,'runtime_pixels_per_tick':0.5,
   'size':[WIDTH,HEIGHT],'observed_cells':int(observed.sum()),'total_cells':WIDTH*HEIGHT,
   'runtime_areas':[0,1],
   'limits':['320px repetition is authored; original complete cloud cycle not measured.',
    'Top 13 rows hidden by the banner plus 3 compression-fringe rows use an estimated smooth continuation.',
    'Unobserved cells use nearest observed sky; loop join and lower blend are estimated.',
    'Only the upper sky in the first two viewports is animated; full original parallax and later scenery remain pending.']}
  (assets/'cloud_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
 strip=indexed(Image.open(assets/'cloud_strip.png').convert('RGB'),header)
 assert strip.shape==(HEIGHT,WIDTH) and (strip>0).all() and (strip<240).all()
 assert np.array_equal(strip[:,0],strip[:,-1])
 # One pre-shifted bank keeps every DMA source/destination halfword aligned,
 # even when the visible scroll phase is an odd number of pixels.
 (assets/'cloud_strip.bin').write_bytes(strip.tobytes()+np.roll(strip,-1,axis=1).tobytes())
 print('PASS cloud assets: observed 30px/s drift and dialogue stop; transparent-free palette; seamless authored loop; aligned even/odd scroll banks')

if __name__=='__main__':main()
