"""Two video-derived ramp views; hidden scenery and collision planes are provisional."""
from pathlib import Path
import argparse,io,json
import numpy as np
from PIL import Image
from convert_bridge_run import warm_mask,sky_fill,quantize
from convert_continuation_background import png,write,sha
from audit_route_continuation import match
ROOT=Path(__file__).resolve().parents[1]

def compose():
    ref=ROOT/'reference/w1l1_next'
    frames={n:np.asarray(Image.open(ref/f'{n}.png').convert('RGB')) for n in [173,174]}
    old=np.asarray(Image.open(ROOT/'reference/w1l1_continuation/frames/166_full.png').convert('RGB'))
    registrations=[]
    for a,b,source,target,boxes,delta in [
        (166,173,old,frames[173],[(45,112,52,122),(169,88,178,100)],[58,-15]),
        (173,174,frames[173],frames[174],[(10,18,16,24),(22,28,29,35)],[108,93])]:
        matches=[match(source.astype('int16'),target.astype('int16'),box,0) for box in boxes]
        assert all(m['delta']==delta and m['mae_rgb']<8 and m['runner_up_mae_rgb']-m['mae_rgb']>3 for m in matches)
        registrations.append({'from':a,'to':b,'delta':delta,'patches':matches})
    clean_upper=np.asarray(Image.open(ROOT/'assets/upper_background.png').convert('RGB'))
    outputs={};clean={}
    header=(ROOT/'assets/continuation_palette.bin').read_bytes()
    for n,name in [(173,'ramp_lower'),(174,'ramp_upper')]:
        a=frames[n].copy();holes=np.zeros((160,240),bool);restored=holes.copy()
        holes[:14]=True;holes[13:45,204:240]=True
        if n==173:
            holes[43:110,116:147]=True;holes[14:44,95:142]=True
            tile=clean_upper[95:139,58:83];mask=warm_mask(tile)
            for x in range(mask.shape[1]):
                ys=np.flatnonzero(mask[:,x])
                if len(ys):mask[ys[0]:,x]=True
            a[80:124,116:141][mask]=tile[mask];restored[80:124,116:141]=mask
            a[13:45,226:240]=clean_upper[28:60,168:182];restored[13:45,226:240]=True
            strip=(185,200)
        else:
            holes[102:160,139:184]=True;holes[45:66,8:30]=True
            # Recover visible wooden ramp pixels through the measured camera translation.
            source=clean[173];mask=warm_mask(source)
            for y in range(14,67):
                for x in range(31,76):
                    if -4<=y-x<=12 and mask[y,x] and y+93<160:
                        a[y+93,x+108]=source[y,x];restored[y+93,x+108]=True
            strip=(185,200)
        holes &= ~restored
        a[:14]=np.median(a[45,strip[0]:strip[1]],axis=0).astype('uint8')
        sky_fill(a,holes,strip,95)
        clean[n]=a.copy();binary,preview=quantize(a,holes,header)
        outputs[name+'_background.bin']=binary
        outputs[name+'_background.png']=png(Image.fromarray(a))
        outputs[name+'_background_preview.png']=png(preview.resize((720,480),Image.Resampling.NEAREST))
    manifest={'video_sha256':'7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51',
        'sources':{str(n):sha((ref/f'{n}.png').read_bytes()) for n in [173,174]},
        'registrations':registrations,'geometry':'provisional',
        'limits':['Hidden sky and island pixels estimated or restored from adjacent views',
                  'Wooden ramp is a provisional one-way slope; original collision timing not recovered',
                  'Small gem visible at 174 seconds removed; next gap and collectible not yet integrated',
                  'Recording header and logo removed; no source actor baked into gameplay background']}
    outputs['ramp_route_manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    return outputs

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    for name,data in compose().items():
        path=ROOT/'assets'/name
        if args.check:
            if name.endswith('.png'):assert Image.open(path).convert('RGBA').tobytes()==Image.open(io.BytesIO(data)).convert('RGBA').tobytes(),name
            else:assert path.read_bytes()==data,name
        else:write(path,data)
    print('PASS ramp route assets: two backgrounds and two independently measured camera registrations; occlusions and slopes provisional')
if __name__=='__main__':main()
