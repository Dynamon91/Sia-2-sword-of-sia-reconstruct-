"""Remove captured scenery from sprite alpha borders, preserving interior highlights.
Run after unpack_assets.py: the archived ROM remains an immutable source.
"""
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def clean(image):
    a=np.array(image.convert('RGBA')); mask=a[:,:,3]>0
    rgb=a[:,:,:3].astype(int);r,g,b=rgb.transpose(2,0,1)
    # Snow and sky were admitted by the old dilated difference mask.
    contamination=((rgb.min(2)>150)&((rgb.max(2)-rgb.min(2))<65))|((b>r+12)&(g>r+8)&(abs(b-g)<55)&(r>65))
    for _ in range(2):
        inner=np.asarray(Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.MinFilter(3)))>0
        mask &= ~(mask&~inner&contamination)
    a[:,:,3]=mask*255
    return Image.fromarray(a)

def indexed(image,header):
    words=np.frombuffer(header,dtype='<u2')
    colors=np.array([[(int(w)>>s&31)*255//31 for s in (0,5,10)] for w in words],dtype=np.int32)
    # Index zero is transparency; UI entries 240+ must never supply actor colors.
    rgb=np.asarray(image.convert('RGB')).astype(np.int32)
    flat=rgb.reshape(-1,3)
    result=np.empty(len(flat),dtype=np.uint8)
    for start in range(0,len(flat),1024):
        d=flat[start:start+1024,None,:]-colors[None,1:240,:]
        result[start:start+1024]=np.sum(d*d,axis=2).argmin(1)+1
    arr=result.reshape(rgb.shape[:2])
    if image.mode=='RGBA':arr[np.asarray(image)[:,:,3]==0]=0
    return arr

def main():
    out=ROOT/'assets';header=(out/'room.bin').read_bytes()[:512]
    stream=bytearray()
    for i in range(5):
        im=Image.open(out/f'room_pose_{i}.png').convert('RGBA')
        if i<4:im=clean(im)
        stream.extend(indexed(im,header).tobytes())
    (out/'room_sprites.bin').write_bytes(stream)
    im=clean(Image.open(out/'bridge_run_reference.png'))
    (out/'bridge_run.bin').write_bytes(indexed(im,header).tobytes())
    guard=clean(Image.open(out/'guard_cutout.png'))
    (out/'guard_sprite.bin').write_bytes(indexed(guard,header).tobytes())
    assert not np.isin(np.frombuffer(bytes(stream),dtype='uint8'),np.arange(240,256)).any()
    print('PASS sprite palette: transparent zero, opaque colors 1..239; snow/sky border cleanup')
if __name__=='__main__':main()
