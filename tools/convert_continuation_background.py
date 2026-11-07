"""Prepare a video-derived background; not yet linked into the playable ROM.
Occluded sky is estimated. Terrain is recovered with a checked camera transform.
"""
from pathlib import Path
import argparse, hashlib, io, json, os
import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes, label
from repair_sprite_edges import indexed

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'reference/w1l1_continuation'

def sha(data):return hashlib.sha256(data).hexdigest()
def write(path,data):
    with path.open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def png(image):
    out=io.BytesIO();image.save(out,format='PNG');return out.getvalue()

def compose():
    source=Image.open(REF/'frames/159_full.png').convert('RGB')
    saved=Image.open(REF/'frames/159.png').convert('RGB')
    assert source.size==(240,160) and source.crop((0,35,240,160)).tobytes()==saved.tobytes()
    target=Image.open(REF/'frames/160.png').convert('RGB')
    manifest=json.loads((REF/'manifest.json').read_text())
    pair=next(p for p in manifest['registrations'] if p['from']==159 and p['to']==160 and p['accepted'])
    assert pair['delta']==[-54,34] and target.size==(240,125)
    a=np.array(source);original=a.copy();changed=np.zeros((160,240),dtype=bool)
    sky=np.median(original[:,150:196],axis=1).astype(np.uint8)
    sky[:14]=sky[14]
    holes=np.zeros((160,240),dtype=bool)
    regions=[(94,13,150,56),(207,13,240,35),(54,50,139,113),(0,0,240,14)]
    for x0,y0,x1,y1 in regions:holes[y0:y1,x0:x1]=True
    # Only paste connected rock pixels. Clouds cannot be translated with terrain.
    rock=np.asarray(target)[124-35:160-35,0:80]
    assert rock.shape==(36,80,3)
    r,g,b=rock.astype(np.int16).transpose(2,0,1)
    labels,n=label((r>b+8)&(g>b+3));assert n
    sizes=np.bincount(labels.ravel());sizes[0]=0
    rock_mask=binary_fill_holes(labels==sizes.argmax())
    assert 1000<int(rock_mask.sum())<2700
    terrain=np.zeros((160,240),dtype=bool);terrain[90:126,54:134]=rock_mask
    a[90:126,54:134][rock_mask]=rock[rock_mask]
    holes &= ~terrain
    # Harmonic sky fill matches the visible boundaries, avoiding rectangular seams.
    # Brown terrain is not a sky boundary: substitute same-row visible sky while
    # solving, then retain all actual terrain pixels in the output.
    r,g,b=a.astype(np.int16).transpose(2,0,1)
    foreground=((r>b+8)&(g>b+3))|terrain
    work=a.astype(np.float32)
    work[foreground]=np.broadcast_to(sky[:,None,:],work.shape)[foreground]
    work[holes]=np.broadcast_to(sky[:,None,:],work.shape)[holes]
    converged=False
    for iteration in range(5000):
        padded=np.pad(work,((1,1),(1,1),(0,0)),mode='edge')
        average=(padded[:-2,1:-1]+padded[2:,1:-1]+padded[1:-1,:-2]+padded[1:-1,2:])/4
        delta=float(np.max(np.abs(work[holes]-average[holes])))
        work[holes]=average[holes]
        if delta<0.01:converged=True;break
    assert converged
    a[holes]=np.rint(work[holes]).clip(0,255).astype(np.uint8)
    changed=holes|terrain
    assert np.array_equal(a[~changed],original[~changed])
    header=(ROOT/'assets/continuation_palette.bin').read_bytes();assert len(header)==512
    if (ROOT/'assets/room.bin').exists():assert header==(ROOT/'assets/room.bin').read_bytes()[:512]
    image=Image.fromarray(a);indices=indexed(image,header)
    assert indices.shape==(160,240) and indices.min()>=1 and indices.max()<240
    words=np.frombuffer(header,dtype='<u2')
    palette=np.array([[(int(w)>>s&31)*255//31 for s in (0,5,10)] for w in words],dtype=np.uint8)
    # Dither only reconstructed sky, retaining the nearest palette match on
    # observed pixels and on all recovered terrain.
    ys,xs=np.nonzero(holes)
    bayer=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=np.float32)
    candidates=palette[1:240].astype(np.int32)
    for start in range(0,len(xs),1024):
        y=ys[start:start+1024];x=xs[start:start+1024]
        colors=a[y,x].astype(np.int32);first=palette[indices[y,x]].astype(np.int32)
        differences=colors[:,None,:]-candidates[None,:,:]
        distances=np.sum(differences*differences,axis=2)
        duplicates=np.all(first[:,None,:]==candidates[None,:,:],axis=2)
        distances[duplicates]=2147483647
        second_id=np.argmin(distances,axis=1)+1;second=palette[second_id].astype(np.int32)
        direction=second-first;denominator=np.sum(direction*direction,axis=1)
        weight=np.clip(np.sum((colors-first)*direction,axis=1)/np.maximum(1,denominator),0,1)
        use_second=weight>(bayer[y%4,x%4]+0.5)/16
        indices[y[use_second],x[use_second]]=second_id[use_second]
    preview=Image.fromarray(palette[indices])
    untouched=int((~changed).sum());assert untouched>26000
    info={'artifact_type':'background_candidate','integrated_in_rom':False,
          'source_seconds':159,'terrain_patch_seconds':160,'terrain_delta_159_to_160':[-54,34],
          'source_video_sha256':manifest['video_sha256'],
          'source_full_png_sha256':sha((REF/'frames/159_full.png').read_bytes()),
          'source_160_png_sha256':sha((REF/'frames/160.png').read_bytes()),
          'palette_sha256':sha(header),'size':[240,160],
          'palette_conversion':'Nearest palette on observed pixels and terrain; ordered two-color dithering only on estimated sky',
          'unchanged_rgb_pixels':untouched,'replaced_or_recovered_pixels':int(changed.sum()),
          'estimated_sky_regions':[[0,0,240,14],[94,13,150,56],[207,13,240,35],[54,50,139,113]],
          'terrain_patch_destination':[54,90,134,126],
          'terrain_mask_pixels':int(rock_mask.sum()),'sky_fill_iterations':iteration+1,
          'sky_fill_method':'Harmonic boundary interpolation, with warm foreground excluded from sky boundaries',
          'terrain_patch_source_normalized':[0,124,80,160],
          'limits':['Video-derived compressed colors, not original GBA tiles',
                    'Hidden sky estimated by harmonic fill; top boundary initialized from row 14',
                    'Only connected terrain is copied; parallax sky is not copied from the aligned frame',
                    'Collision geometry, entities, scenery animation and ROM integration remain pending']}
    r,g,b=a.astype(np.int16).transpose(2,0,1)
    warm=(r>b+8)&(g>b+3)
    contours=[]
    for name,x0,x1 in [('left_island',0,140),('bridge_and_pillar',200,240)]:
        region=np.zeros((160,240),dtype=bool);region[75:,x0:x1]=True
        labels,n=label(warm&region);assert n
        sizes=np.bincount(labels.ravel());sizes[0]=0
        body=binary_fill_holes(labels==sizes.argmax())
        points=[]
        for x in range(x0,x1):
            ys=np.flatnonzero(body[:,x])
            if len(ys):points.append([x,int(ys[0])])
        assert len(points)>20
        contours.append({'name':name,'visual_upper_edge_pixels':points})
    geometry={'source_seconds':159,'registered_pixel_offset_from_155':[-188,25],
              'not_collision_geometry':True,'coordinate_size':[240,160],
              'method':'First warm connected foreground pixel per column, below row 75',
              'limits':['Grass tips and decorative bridge pixels are not walk planes',
                        'Foot anchors, solid volumes, collision responses and traversability remain unverified'],
              'regions':contours}
    return image,preview,header+indices.tobytes(),info,geometry

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    image,preview,binary,info,geometry=compose();out=ROOT/'assets'
    files={'continuation_background.png':png(image),'continuation_background.bin':binary,
           'continuation_background_gba.png':png(preview),
           'continuation_background_preview.png':png(preview.resize((720,480),Image.Resampling.NEAREST)),
           'continuation_background_manifest.json':(json.dumps(info,indent=2)+'\n').encode(),
           'continuation_visual_terrain.json':(json.dumps(geometry,indent=2)+'\n').encode()}
    for name,data in files.items():
        path=out/name
        if args.check:
            if name.endswith('.png'):
                assert Image.open(path).convert('RGB').tobytes()==Image.open(io.BytesIO(data)).convert('RGB').tobytes(),name
            else:assert path.read_bytes()==data,name
        else:write(path,data)
    print(f'PASS continuation background: {info["unchanged_rgb_pixels"]} original RGB pixels preserved; registered terrain patch; 1..239 palette; candidate not integrated in ROM')
if __name__=='__main__':main()
