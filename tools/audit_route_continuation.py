"""Audit measured foreground registrations; never manufacture a playable map.
Coordinates in the manifest refer to normalized 240x160 video frames.
Stored references omit the top 35 rows (recording banner and channel logo).
"""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'reference/w1l1_continuation'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def match(source,target,box,crop_y):
    x0,y0,x1,y1=box
    tile=source[y0-crop_y:y1-crop_y,x0:x1]
    h,w=tile.shape[:2]
    assert tile.shape==(y1-y0,x1-x0,3) and h>0 and w>0
    # Search every legal integer translation, not just the expected result.
    best=[]
    for y in range(target.shape[0]-h+1):
        for x in range(target.shape[1]-w+1):
            error=float(np.abs(target[y:y+h,x:x+w]-tile).mean())
            best.append((error,x-x0,y+crop_y-y0))
    best.sort()
    error,dx,dy=best[0]
    return {'delta':[dx,dy],'mae_rgb':round(error,6),
            'runner_up_mae_rgb':round(best[1][0],6),'patch':box}

def overview(manifest):
    times=[158,159,160,161,162,164]
    sheet=Image.new('RGB',(720,294),'#18212d');draw=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        x=(i%3)*240;y=(i//3)*147
        draw.text((x+5,y+5),f'VIDEO REFERENCE {t}s - NOT ROM',fill='white')
        sheet.paste(Image.open(DATA/f'frames/{t}.png').convert('RGB'),(x,y+22))
    sheet.resize((1440,588),Image.Resampling.NEAREST).save(DATA/'overview.png')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--video',type=Path)
    ap.add_argument('--output',type=Path,default=ROOT/'build/route-registration.json')
    ap.add_argument('--preview',action='store_true');args=ap.parse_args()
    manifest=json.loads((DATA/'manifest.json').read_text());crop_y=manifest['crop_top_rows']
    if args.video:
        if digest(args.video)!=manifest['video_sha256']:raise SystemExit('Different reference video')
        from convert_room import extract
        for entry in manifest['frames']:
            image=extract(str(args.video),entry['seconds']).crop((0,crop_y,240,160))
            if hashlib.sha256(image.tobytes()).hexdigest()!=entry['rgb_sha256']:
                raise SystemExit('Source pixels differ: '+entry['file'])
    frames={}
    for entry in manifest['frames']:
        p=DATA/entry['file']
        if digest(p)!=entry['sha256']:raise SystemExit('Reference bytes changed: '+entry['file'])
        im=Image.open(p).convert('RGB');assert im.size==(240,160-crop_y)
        assert hashlib.sha256(im.tobytes()).hexdigest()==entry['rgb_sha256']
        frames[entry['seconds']]=np.asarray(im).astype(np.int16)
    results=[]
    for pair in manifest['registrations']:
        patches=[match(frames[pair['from']],frames[pair['to']],box,crop_y) for box in pair['patches']]
        assert len(patches)>=2
        accepted=all(p['mae_rgb']<=manifest['max_mae_rgb'] for p in patches) and all(p['delta']==patches[0]['delta'] for p in patches)
        if pair['accepted']:
            assert accepted and patches[0]['delta']==pair['delta'],(pair,patches)
        else:
            assert not accepted,('Previously rejected registration now needs review',pair,patches)
        results.append({'from':pair['from'],'to':pair['to'],'accepted':accepted,
                        'delta':patches[0]['delta'] if accepted else None,'patches':patches})
    # Two disconnected components are deliberate: the bridge interval is unresolved.
    args.output.parent.mkdir(parents=True,exist_ok=True)
    report={'reference_only':True,'playable_area_added':False,
            'coordinate_convention':manifest['coordinate_convention'],'registrations':results}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    if args.preview:overview(manifest)
    accepted=sum(p['accepted'] for p in results)
    print(f'PASS route references: {accepted} registrations independently matched by two terrain patches; {len(results)-accepted} bridge registration rejected; no playable map inferred')
if __name__=='__main__':main()
