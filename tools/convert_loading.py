"""Recover the observed Please wait entry screen without recording overlays."""
from pathlib import Path
import argparse, io, json, hashlib
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]

def outputs():
    path=ROOT/'reference/w1l1_loading/107_3.png'
    rgb=np.asarray(Image.open(path).convert('RGB')).copy()
    rgb[:46]=0  # Recording banner/avatar only; game loading text is at y=141..156.
    words=(rgb[:,:,0].astype('uint16')>>3)|((rgb[:,:,1].astype('uint16')>>3)<<5)|((rgb[:,:,2].astype('uint16')>>3)<<10)
    palette,ids=np.unique(words,return_inverse=True)
    assert len(palette)<=256 and palette[0]==0
    header=np.zeros(256,dtype='<u2');header[:len(palette)]=palette
    pixels=ids.astype('uint8').reshape(160,240)
    assert np.array_equal(header[pixels],words)
    ys,xs=np.nonzero(words);assert [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]==[8,141,96,157]
    decoded=np.stack([((words>>shift)&31)*255//31 for shift in (0,5,10)],axis=2).astype('uint8')
    image=io.BytesIO();Image.fromarray(decoded).save(image,format='PNG')
    manifest={'video_sha256':'7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51',
              'reference_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
              'reference_seconds':107.3,'source_fps':[30,1],
              'transition_source_frames':[3211,3306],
              'visible_text_source_frames':[3216,3302],
              'native_phase_frames':{'black_before':10,'please_wait':171,'black_after':8},
              'native_total_frames':189,'source_duration_seconds':95/30,
              'text_bounds':[8,141,96,157],'gba_colors':int(len(palette)),
              'gameplay_zone_loading_intervals_confirmed':[],
              'limits':['Entry transition only; not a generic effect at collision-area portals',
                        'Original intro movie remains excluded',
                        'Observed timing resampled from 30-fps video to native GBA refresh',
                        'Recording overlay rows 0..45 cleared; loading text retains all observed GBA-quantized pixels']}
    return {'loading_screen.bin':header.tobytes()+pixels.tobytes(),
            'loading_screen.png':image.getvalue(),
            'loading_manifest.json':(json.dumps(manifest,indent=2)+'\n').encode()}

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    for name,data in outputs().items():
        path=ROOT/'assets'/name
        if args.check:
            if name.endswith('.png'):assert Image.open(path).convert('RGB').tobytes()==Image.open(io.BytesIO(data)).convert('RGB').tobytes(),name
            else:assert path.read_bytes()==data,name
        else:path.write_bytes(data)
    print('PASS authentic entry loading: observed Please wait pixels, 153 GBA colors, overlay removal and timing manifest')

if __name__=='__main__':main()
