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

def resolve_offsets(registrations,anchor):
    """Compose accepted translations; reject inconsistent loops, never use rejected edges."""
    from collections import deque
    edges={}
    for pair in registrations:
        if not pair['accepted']:continue
        a,b=pair['from'],pair['to'];dx,dy=pair['delta']
        edges.setdefault(a,[]).append((b,dx,dy))
        edges.setdefault(b,[]).append((a,-dx,-dy))
    offsets={anchor:[0,0]};queue=deque([anchor])
    while queue:
        source=queue.popleft()
        for target,dx,dy in edges.get(source,[]):
            candidate=[offsets[source][0]+dx,offsets[source][1]+dy]
            if target in offsets:
                if offsets[target]!=candidate:raise ValueError('Conflicting terrain registrations')
            else:offsets[target]=candidate;queue.append(target)
    return offsets

def bridge_preview(manifest):
    sheet=Image.new('RGB',(480,160),'#18212d');draw=ImageDraw.Draw(sheet)
    pair=next(p for p in manifest['registrations'] if p.get('method') and p['accepted'])
    boxes=pair['patches'];translation=pair['delta'];crop_y=manifest['crop_top_rows']
    for col,t in enumerate([pair['from'],pair['to']]):
        x=col*240;draw.text((x+4,4),f'VIDEO {t}s - NOT ROM',fill='white')
        sheet.paste(Image.open(DATA/f'frames/{t}.png').convert('RGB'),(x,20))
        for box,color in zip(boxes,['#00ff77','#ffb833']):
            x0,y0,x1,y1=box;dx,dy=(0,0) if col==0 else translation
            draw.rectangle((x+x0+dx,20+y0+dy-crop_y,x+x1+dx-1,20+y1+dy-crop_y-1),outline=color,width=1)
    draw.text((4,148),f'STATIC PILLAR: dx={translation[0]}, dy={translation[1]} px',fill='white')
    with (DATA/'bridge_alignment.png').open('wb') as f:
        sheet.resize((1440,480),Image.Resampling.NEAREST).save(f,format='PNG')
        f.flush()
        __import__('os').fsync(f.fileno())

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
        accepted=all(p['mae_rgb']<=pair.get('max_mae_rgb',manifest['max_mae_rgb']) and p['runner_up_mae_rgb']-p['mae_rgb']>=pair.get('min_runner_up_margin_rgb',0) for p in patches) and all(p['delta']==patches[0]['delta'] for p in patches)
        if pair['accepted']:
            assert accepted and patches[0]['delta']==pair['delta'],(pair,patches)
        else:
            assert not accepted,('Previously rejected registration now needs review',pair,patches)
        results.append({'from':pair['from'],'to':pair['to'],'accepted':accepted,
                        'delta':patches[0]['delta'] if accepted else None,'patches':patches,
                        'max_mae_rgb':pair.get('max_mae_rgb',manifest['max_mae_rgb']),
                        'min_runner_up_margin_rgb':pair.get('min_runner_up_margin_rgb',0)})
    anchor=manifest.get('registration_anchor_seconds',manifest['frames'][0]['seconds'])
    offsets=resolve_offsets(results,anchor)
    connected=len(offsets)==len(frames)
    if manifest.get('require_connected') and not connected:raise ValueError('Unresolved reference components')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    report={'reference_only':True,'playable_area_added':False,
            'coordinate_convention':manifest['coordinate_convention'],'registrations':results,
            'registration_anchor_seconds':anchor,'connected':connected,
            'registered_pixel_offsets_from_anchor':offsets}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    if args.preview:overview(manifest);bridge_preview(manifest)
    accepted=sum(p['accepted'] for p in results)
    print(f'PASS route references: {accepted} registrations independently matched by two terrain patches; {len(results)-accepted} context-window registration rejected; connected={connected}; no playable map inferred')
if __name__=='__main__':main()
