"""First registered edge view after the lever; no thorn-strip motion is inferred."""
from pathlib import Path
import argparse, io, json, hashlib
import numpy as np
from PIL import Image
from audit_route_continuation import match
from convert_lever_route import terrain
from convert_bridge_run import sky_fill, quantize

ROOT=Path(__file__).resolve().parents[1]

def outputs():
    source=ROOT/'reference/w1l1_next/180.png'
    target=ROOT/'reference/w1l1_postlever/183.png'
    before=np.asarray(Image.open(source).convert('RGB'))
    a=np.asarray(Image.open(target).convert('RGB')).copy()
    patches=[match(before.astype('int16'),a.astype('int16'),box,0)
             for box in [(176,152,184,158),(192,149,200,155)]]
    assert all(p['delta']==[-144,-8] and p['mae_rgb']<9 and
               p['runner_up_mae_rgb']-p['mae_rgb']>3 for p in patches)
    holes=np.zeros((160,240),bool);restored=holes.copy()
    holes[94:160,54:103]=True
    previous=np.asarray(Image.open(ROOT/'assets/lever_room_background.png').convert('RGB'))
    terrain(a,restored,previous,(198,102,240,160),-144,-8)
    holes &= ~restored
    sky_fill(a,holes,(104,116),95)
    later_path=ROOT/'reference/w1l1_postlever/184.png'
    later=np.asarray(Image.open(later_path).convert('RGB'))
    roof=[match(np.asarray(Image.open(target)).astype('int16'),later.astype('int16'),box,0)
          for box in [(170,60,178,68),(175,69,185,80)]]
    assert all(p['delta']==[-160,32] and p['mae_rgb']<9 and
               p['runner_up_mae_rgb']-p['mae_rgb']>3 for p in roof)
    # Restore occluded rock from the next registered frame, not stretched logo pixels.
    sky=np.median(a[14:20,80:116],axis=(0,1)).astype('uint8')
    a[:14]=sky
    a[:14,160:240]=later[32:46,0:80]
    a[13:45,204:240]=later[45:77,44:80]
    data,preview=quantize(a,holes,(ROOT/'assets/continuation_palette.bin').read_bytes())
    p=io.BytesIO();Image.fromarray(a).save(p,format='PNG')
    q=io.BytesIO();preview.resize((720,480),Image.Resampling.NEAREST).save(q,format='PNG')
    manifest={'video_sha256':'7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51',
              'source_seconds':183,'source_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
              'registrations':patches,'roof_restoration_registrations':roof,'delta':[-144,-8],
              'later_source_sha256':hashlib.sha256(later_path.read_bytes()).hexdigest(),
              'restored_terrain_pixels':int(restored.sum()),
              'limits':['Covered player/sky estimated; overlap terrain restored from the cleaned preceding view',
                        'Occluded right roof recovered from registered 184s frame; unrecorded upper sky estimated',
                        'Left walk plane and upper rock bounds are provisional; following thorn strip not integrated']}
    return {'post_lever_background.bin':data,'post_lever_background.png':p.getvalue(),
            'post_lever_background_preview.png':q.getvalue(),
            'post_lever_manifest.json':(json.dumps(manifest,indent=2)+'\n').encode()}

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    for name,data in outputs().items():
        path=ROOT/'assets'/name
        if args.check:
            if name.endswith('.png'):
                assert Image.open(path).convert('RGBA').tobytes()==Image.open(io.BytesIO(data)).convert('RGBA').tobytes(),name
            else:assert path.read_bytes()==data,name
        else:path.write_bytes(data)
    print('PASS post-lever edge: measured portal, reproducible actor-free background, provisional walk plane')

if __name__=='__main__':main()
