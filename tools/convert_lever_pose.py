"""Recover the observed lowered lever handle; preserve the existing world atlas."""
from pathlib import Path
import argparse, hashlib, io, json
import numpy as np
from PIL import Image, ImageDraw
from audit_route_continuation import match
from repair_sprite_edges import indexed

ROOT=Path(__file__).resolve().parents[1]

def outputs():
    ref=ROOT/'reference/w1l1_next'
    before=np.asarray(Image.open(ref/'180.png').convert('RGB'))
    after=np.asarray(Image.open(ref/'182.png').convert('RGB'))
    registrations=[match(before.astype('int16'),after.astype('int16'),box,0)
                   for box in [(65,139,73,149),(107,132,114,139)]]
    assert all(r['delta']==[-1,0] and r['mae_rgb']<9 and
               r['runner_up_mae_rgb']-r['mae_rgb']>3 for r in registrations)
    # The reference moves left one pixel. Reproject it into the area-13 atlas.
    crop=Image.fromarray(after).crop((63,104,103,148)).convert('RGBA')
    raised=Image.new('L',(240,160));d=ImageDraw.Draw(raised)
    d.line([(74,129),(91,111)],fill=255,width=11)
    d.ellipse((87,104,99,116),fill=255)
    lowered=Image.new('L',(240,160));d=ImageDraw.Draw(lowered)
    d.line([(74,129),(91,141)],fill=255,width=7)
    d.ellipse((66,121,81,138),fill=255)
    header=(ROOT/'assets/continuation_palette.bin').read_bytes()
    words=np.frombuffer(header,dtype='<u2')
    colors=np.array([[(int(w)>>shift&31)*255//31 for shift in (0,5,10)]
                     for w in words],dtype='int16')
    atlas_bytes=(ROOT/'assets/scroll_world.bin').read_bytes()
    atlas=np.frombuffer(atlas_bytes[:810000],dtype='uint8').reshape(540,1500)
    ox,oy=json.loads((ROOT/'assets/scroll_manifest.json').read_text())['origins'][13]
    x0,y0=64-ox,380-oy+104
    original=colors[atlas[y0:y0+44,x0:x0+40]]
    source=np.asarray(crop).copy();rgb=source[:,:,:3].astype('int16')
    def metal(a):return (a[:,:,0]>=a[:,:,2]-45)&(a[:,:,1]>=a[:,:,2]-35)
    erase=(np.asarray(raised.crop((64,104,104,148)))>0)&metal(original)
    ink=(np.asarray(lowered.crop((64,104,104,148)))>0)&metal(rgb)
    # Use this atlas's own sky colors, rather than a later cloud frame. Only
    # the sky hidden by the old handle is estimated between two observed edges.
    left=original[:,0,:].astype('float32');right=original[:,-1,:].astype('float32')
    fraction=np.arange(40,dtype='float32')[None,:,None]/39
    sky=np.rint(left[:,None,:]*(1-fraction)+right[:,None,:]*fraction).astype('uint8')
    result=np.zeros((44,40,4),dtype='uint8')
    result[erase,:3]=sky[erase];result[ink,:3]=source[ink,:3]
    result[:,:,3]=(erase|ink)*255;crop=Image.fromarray(result)
    data=indexed(crop,header).tobytes()
    assert len(data)==40*44 and max(data)<240 and any(data)
    png=io.BytesIO();crop.save(png,format='PNG')
    report={'video_sha256':'7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51',
            'source_seconds':182,'source_sha256':hashlib.sha256((ref/'182.png').read_bytes()).hexdigest(),
            'atlas_sha256':hashlib.sha256(atlas_bytes).hexdigest(),
            'registrations':registrations,'area':13,'destination':[64,104,40,44],
            'source_crop':[63,104,103,148], 'opaque_pixels':sum(bool(x) for x in data),
            'limits':['Two visual states only; original intermediate rotation timing is not recovered',
                      'Manual handle masks; hidden sky is interpolated from the current atlas edges to avoid cloud-frame seams',
                      'Palette quantization and one-pixel registration; physical thorn barrier remains pending']}
    return {'lever_lowered.bin':data,'lever_lowered.png':png.getvalue(),
            'lever_pose_manifest.json':(json.dumps(report,indent=2)+'\n').encode()}

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    for name,data in outputs().items():
        path=ROOT/'assets'/name
        if a.check:
            if name.endswith('.png'):
                assert Image.open(path).convert('RGBA').tobytes()==Image.open(io.BytesIO(data)).convert('RGBA').tobytes(),name
            else:assert path.read_bytes()==data,name
        else:path.write_bytes(data)
    print('PASS lever lowered pose: two independent registrations, observed handle, explicit hidden-sky estimate, bounded palette and reproducible patch')

if __name__=='__main__':main()
