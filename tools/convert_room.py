"""Extract a cleaned first viewport and a few masked poses from the recording.
This does not recover original sprite sheets. Patches and geometry are approximate.
"""
from pathlib import Path
import argparse, subprocess, tempfile, json, struct
from PIL import Image,ImageDraw
import numpy as np
from scipy.ndimage import binary_dilation,binary_fill_holes,label

def extract(video,t):
    from io import BytesIO
    b=subprocess.check_output(['ffmpeg','-loglevel','error','-ss',str(t),'-i',video,
       '-map','0:v:0','-frames:v','1','-f','image2pipe','-vcodec','png','-'])
    return Image.open(BytesIO(b)).convert('RGB').resize((240,160),Image.Resampling.NEAREST)

def pose(source,background,cx,feet,roi):
    box=(cx-24,feet-56,cx+24,feet)
    image=source.crop(box);bg=background.crop(box)
    a=np.asarray(image).astype(int);b=np.asarray(bg).astype(int)
    mask=np.max(abs(a-b),axis=2)>24
    bounds=Image.new('1',(48,56));d=ImageDraw.Draw(bounds)
    d.rectangle((roi[0]-box[0],roi[1]-box[1],roi[2]-box[0],roi[3]-box[1]),fill=1)
    mask &= np.asarray(bounds)
    mask=binary_dilation(mask,iterations=1)&np.asarray(bounds)
    ids,n=label(mask)
    sizes=np.bincount(ids.ravel());sizes[0]=0
    mask=binary_fill_holes(ids==sizes.argmax())
    image=image.convert('RGBA');image.putalpha(Image.fromarray((mask*255).astype('uint8')))
    return image

def main():
    p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('--out',default='assets');a=p.parse_args()
    out=Path(a.out);out.mkdir(exist_ok=True,parents=True)
    ims={t:extract(a.video,t) for t in [114,118,119.5,121]}
    bg=ims[114].copy()
    bg.paste(ims[118].crop((30,108,49,160)),(30,108))
    bg.paste(ims[118].crop((49,108,68,115)),(49,108))
    bg.paste(ims[119.5].crop((49,115,68,160)),(49,115))
    bg.paste(bg.crop((134,61,153,81)),(108,61))
    bg.paste(bg.crop((140,14,172,46)),(208,0))
    for y in range(13):
        for x in range(240):bg.putpixel((x,y),bg.getpixel((x,13)))
    shifted=Image.new('RGB',(240,160));shifted.paste(bg,(0,11))
    sprites=[pose(ims[114],bg,47,158,(31,110,66,159)),
             pose(ims[119.5],bg,64,115,(40,66,81,115)),
             pose(ims[121],shifted,111,129,(94,78,128,129)),
             pose(ims[118],bg,62,158,(47,110,86,159))]
    gem=ims[114].crop((109,62,125,78)).convert('RGBA')
    diamond=Image.new('L',(16,16));ImageDraw.Draw(diamond).polygon([(8,0),(15,6),(8,15),(0,6)],fill=255)
    gem.putalpha(diamond)
    sprites.append(gem)
    sky=Image.new('RGB',(240,48))
    for y in range(48):
        weight=(y/47)**3
        for x in range(240):
            base=bg.getpixel((x,13));blue=(78,123,153)
            sky.putpixel((x,y),tuple(round(blue[k]*(1-weight)+base[k]*weight) for k in range(3)))
    atlas=Image.new('RGB',(480,208));atlas.paste(bg,(0,0));atlas.paste(sky,(0,160))
    for i,im in enumerate(sprites):atlas.paste(im.convert('RGB'),(240+i*48,0))
    quant=atlas.quantize(colors=239,dither=Image.Dither.NONE)
    colors=quant.getpalette()[:239*3];colors += [0]*(239*3-len(colors))
    pal=Image.new('P',(1,1));pal.putpalette(colors+colors[:3]*17)
    used=[tuple(colors[i:i+3]) for i in range(0,len(colors),3)]
    first={c:used.index(c) for c in used}
    all_colors=[tuple(pal.getpalette()[i:i+3]) for i in range(0,768,3)]
    lookup=np.array([first[c]+1 for c in all_colors],dtype='uint8')
    def indexed(im):return lookup[np.asarray(im.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE))].copy()
    ui=[(0,0,0),(255,255,255),(255,210,80),(80,220,240),(15,25,50),(220,100,140)]+[(0,0,0)]*10
    palette=[(0,0,0)]+used+ui
    assert len(palette)==256
    data=b''.join(struct.pack('<H',(r>>3)|((g>>3)<<5)|((b>>3)<<10)) for r,g,b in palette)
    (out/'room.bin').write_bytes(data+indexed(bg).tobytes())
    (out/'room_sky.bin').write_bytes(indexed(sky).tobytes())
    stream=bytearray()
    for i,im in enumerate(sprites):
        arr=indexed(im);arr[np.asarray(im.getchannel('A'))==0]=0;stream.extend(arr.tobytes())
        im.save(out/f'room_pose_{i}.png')
    (out/'room_sprites.bin').write_bytes(stream)
    bg.save(out/'room_background_reference.png')
    (out/'room.h').write_text('''#ifndef ROOM_ASSETS_H
#define ROOM_ASSETS_H
#define ROOM_SPRITE_W 48
#define ROOM_SPRITE_H 56
#define ROOM_SPRITE_SIZE (48*56)
#define ROOM_GEM_OFFSET (ROOM_SPRITE_SIZE*4)
extern const unsigned char room_background[],room_sprites[],room_sky[];
#endif
''')
    info={'method':'temporal patches, difference masks and shared palette, not original asset recovery',
          'source_times':[114,118,119.5,121],'viewport':[240,160],
          'patches':['recorded Sia removed with later frames','gem removed and redrawn as collectible','sky approximated under channel overlays'],
          'poses':['idle','jump','climb','attack'],'sprite_size':[48,56],'sprite_anchor':[24,56],
          'ground_surface':'approximate piecewise heightfield','platforms':[[81,88,70],[186,40,54]],
          'ladder':{'center_x':115,'top':88,'bottom':154},'gem':{'x':117,'y':70},
          'vertical_camera':{'min':-40,'max':0,'unseen_sky':'approximate color gradient'},
          'limits':['one viewport only','no full walking cycle','no enemies or later rooms','compression/alpha fringes remain']}
    (out/'room_manifest.json').write_text(json.dumps(info,indent=2)+'\n')
    print('Built room background, four poses and collectible gem')
if __name__=='__main__':main()
