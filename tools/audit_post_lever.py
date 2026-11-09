"""Reject uncertain post-lever camera joins before authoring playable geometry."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image, ImageDraw
from audit_route_continuation import match

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'reference/w1l1_postlever'
PAIRS=[
    (180,182,[(65,139,73,149),(107,132,114,139)],[-1,0]),
    (180,183,[(176,152,184,158),(192,149,200,155)],[-144,-8]),
    (182,183,[(175,152,183,158),(191,149,199,155)],[-143,-8]),
    (183,184,[(170,60,178,68),(175,69,185,80)],[-160,32]),
    (182,185,[(67,133,75,141),(104,131,113,140)],None),
]

def registration(patches):
    confident=all(p['mae_rgb']<9 and p['runner_up_mae_rgb']-p['mae_rgb']>3
                  for p in patches)
    same=all(p['delta']==patches[0]['delta'] for p in patches)
    return confident and same

def audit():
    manifest=json.loads((REF/'manifest.json').read_text())
    frames={}
    for t,item in manifest['frames'].items():
        p=ROOT/item['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],p
        frames[int(t)]=np.asarray(Image.open(p).convert('RGB')).astype('int16')
    results=[]
    for a,b,boxes,expected in PAIRS:
        patches=[match(frames[a],frames[b],box,0) for box in boxes]
        # Patch boxes are disjoint: a repeated sample cannot count as independent evidence.
        x0,y0,x1,y1=boxes[0];u0,v0,u1,v1=boxes[1]
        assert x1<=u0 or u1<=x0 or y1<=v0 or v1<=y0
        accepted=registration(patches)
        assert accepted==(expected is not None),(a,b,patches)
        if accepted:assert patches[0]['delta']==expected
        results.append({'from':a,'to':b,'accepted':accepted,
                        'delta':patches[0]['delta'] if accepted else None,
                        'patches':patches,
                        'reason':'independent patches agree' if accepted else
                                 'high-confidence patches disagree; do not round or average'})
    by_pair={(r['from'],r['to']):r for r in results}
    assert np.array_equal(np.array(by_pair[180,182]['delta'])+
                          by_pair[182,183]['delta'],by_pair[180,183]['delta'])
    # Regression: confidence alone must not accept the real one-pixel vertical disagreement.
    rejected=by_pair[182,185]
    assert all(p['mae_rgb']<9 and p['runner_up_mae_rgb']-p['mae_rgb']>3
               for p in rejected['patches'])
    assert rejected['patches'][0]['delta']==[-53,-114]
    assert rejected['patches'][1]['delta']==[-53,-113]
    return {'video_sha256':manifest['video_sha256'],'frames':manifest['frames'],
            'registrations':results,'triangle_180_182_183_consistent':True,
            'playable_geometry_added':False,'overall_completion_estimate_percent':14.75,
            'limits':['Camera registrations are not collision geometry or player displacements',
                      'The thorn strip and later movement require separate tracking',
                      '182 to 185 is rejected; no complete post-lever route is claimed']}

def preview(destination):
    out=Image.new('RGB',(960,548),(12,24,40));d=ImageDraw.Draw(out)
    d.text((12,8),'RIFERIMENTI VIDEO - NON UNA NUOVA BUILD',fill='white')
    manifest=json.loads((REF/'manifest.json').read_text())
    for i,t in enumerate([182,183,184,185]):
        im=Image.open(ROOT/manifest['frames'][str(t)]['path']).convert('RGB')
        # Exclude recording header and avatar; source bytes remain unmodified for the audit.
        im=im.crop((0,46,240,160)).resize((480,228),Image.Resampling.NEAREST)
        x=(i%2)*480;y=32+(i//2)*258
        d.text((x+8,y+4),f'{t} s - riferimento originale, righe 46-159',fill='white')
        out.paste(im,(x,y+26))
    destination.parent.mkdir(parents=True,exist_ok=True);out.save(destination)

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true')
    p.add_argument('--preview',type=Path);args=p.parse_args()
    data=(json.dumps(audit(),indent=2)+'\n').encode();path=REF/'audit.json'
    if args.check:assert path.read_bytes()==data
    else:path.write_bytes(data)
    if args.preview:preview(args.preview)
    print('PASS post-lever audit: four agreed registrations, closed triangle, real one-pixel disagreement rejected; no playable map inferred')

if __name__=='__main__':main()
