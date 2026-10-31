"""Partial sky/scene separation for the two observed viewports.
Keeps the upper sky still instead of stretching a source row when the camera rises.
Masks and occluded sky fill are estimates, not recovered original layer assets.
"""
from pathlib import Path
import json,struct
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation

def polygon(points):
 im=Image.new('1',(240,160));ImageDraw.Draw(im).polygon(points,fill=1);return np.asarray(im)
def main():
 root=Path(__file__).resolve().parents[1];out=root/'assets';reports=[]
 for name in ['room','bridge']:
  picture=(out/(name+'.bin')).read_bytes();palette_bytes=picture[:512]
  original=np.frombuffer(picture[512:],dtype='uint8').reshape(160,240)
  a=np.asarray(Image.open(out/(name+'_background_reference.png')).convert('RGB')).astype(float)
  r,g,b=[a[:,:,i] for i in range(3)];mask=np.zeros((160,240),dtype=bool)
  if name=='room':
   polygons=[[(185,38),(239,37),(239,59),(221,64),(197,61),(185,52)]]
  else:polygons=[]
  for points in polygons:mask|=polygon(points)
  mask[80:]=True
  color_seed=((g>r*1.1)&(g>b*.9))|((r>b+9)&(g>b+4));color_seed[:35]=False
  mask|=binary_dilation(color_seed,iterations=1);mask[:13]=False
  sky=a.astype('uint8').copy();blue=(b>g+5)&(b>r+10)
  for y in range(80):
   values=a[max(13,y-4):min(y+5,80)][blue[max(13,y-4):min(y+5,80)]]
   value=np.median(values,axis=0) if len(values)>16 else np.array([80,125,155])
   sky[y,mask[y]]=value.astype('uint8')
  values=a[79][blue[79]];base=np.median(values,axis=0) if len(values) else np.array([80,125,155])
  sky[80:]=base.astype('uint8')
  pvals=np.frombuffer(palette_bytes,dtype='<u2');colors=[]
  for v in pvals:colors.extend([int(((v>>s)&31)*255//31) for s in (0,5,10)])
  pal=Image.new('P',(1,1));pal.putpalette(colors)
  filled=np.asarray(Image.fromarray(sky).quantize(palette=pal,dither=Image.Dither.NONE))
  backdrop=original.copy();backdrop[mask]=filled[mask]
  stream=bytearray();reconstructed=backdrop.copy();span_count=0
  for y in range(160):
   edges=np.diff(np.r_[False,mask[y],False].astype(int));starts=np.flatnonzero(edges==1);ends=np.flatnonzero(edges==-1)
   stream.extend(struct.pack('<H',len(starts)));span_count+=len(starts)
   for x,end in zip(starts,ends):
    length=int(end-x);assert 0<length<=240
    stream.extend(bytes([int(x),length]));stream.extend(original[y,x:end].tobytes())
    if length&1:stream.append(0)
    reconstructed[y,x:end]=original[y,x:end]
  assert np.array_equal(reconstructed,original)
  (out/(name+'_backdrop.bin')).write_bytes(palette_bytes+backdrop.tobytes())
  (out/(name+'_spans.bin')).write_bytes(stream)
  Image.fromarray((mask*255).astype('uint8')).save(out/(name+'_layer_mask.png'))
  reports.append({'area':name,'spans':span_count,'stream_bytes':len(stream),
   'byte_identical_at_camera_zero':True,'upper_sky_scroll':'fixed','remaining_scene_scroll':'camera follows foreground',
   'limits':['estimated foreground mask','sky hidden by scenery approximated from observed colors','not the full original parallax engine']})
 (out/'layers_manifest.json').write_text(json.dumps({'format':'160 rows: uint16 run count, then uint8 x/length and pixel bytes padded to even length','areas':reports},indent=2)+'\n')
 print('PASS: both camera-zero composites match every original indexed pixel; layered streams built')
if __name__=='__main__':main()
