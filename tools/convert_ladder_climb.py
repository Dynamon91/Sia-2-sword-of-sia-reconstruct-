"""Recorded ladder poses, mounted sword, upper guard and two cleaned upper views."""
from pathlib import Path
import argparse, hashlib, io, json
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, label
from audit_route_continuation import match
from convert_bridge_run import sky_fill
from convert_ladder_approach import foreground
from repair_sprite_edges import indexed, clean

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'reference/w1l1_ladder_climb'
SOURCES = {'foot': ROOT/'reference/w1l1_ladder/190_5.png',
           'top': ROOT/'reference/w1l1_ladder/191.png',
           '189_8': ROOT/'reference/w1l1_ladder/189_8.png',
           **{s: REF/(s+'.png') for s in ['189_0','190_6','190_7','191_4','191_5','191_6','192_7','193_1','194_3','194_5','193_5','193_7']}}
BODY = [
 [(15,18),(19,18),(22,18),(25,16),(25,14),(28,15),(29,18),(31,20),(31,24),(29,27),(28,31),(26,34),(28,36),(28,40),(26,43),(26,48),(25,52),(26,57),(26,62),(21,63),(18,60),(18,55),(16,55),(15,60),(15,63),(10,63),(10,60),(12,57),(12,52),(11,49),(12,44),(11,42),(13,39),(15,37),(14,34),(11,32),(8,31),(7,27),(8,23),(9,21),(12,19)],
 [(13,14),(16,14),(17,17),(18,19),(23,19),(26,20),(28,23),(30,24),(32,27),(31,31),(28,33),(27,36),(29,37),(28,41),(27,43),(27,48),(26,51),(27,57),(26,62),(21,63),(18,60),(18,55),(16,56),(15,61),(15,63),(10,63),(10,60),(11,56),(11,52),(12,49),(11,45),(12,41),(13,38),(15,35),(13,33),(11,31),(9,29),(8,25),(9,20),(10,17)],
 [(12,13),(15,14),(16,17),(17,19),(22,19),(26,20),(28,22),(29,25),(31,27),(31,31),(28,33),(27,36),(30,37),(29,41),(26,43),(26,47),(27,51),(27,57),(26,62),(22,63),(19,60),(19,55),(17,56),(16,61),(15,63),(11,63),(10,60),(12,56),(12,52),(13,48),(12,44),(13,40),(15,37),(14,34),(11,32),(9,29),(8,24),(9,20),(10,17)],
 [(14,18),(17,17),(20,17),(23,16),(26,14),(29,15),(30,18),(31,21),(31,26),(29,29),(27,33),(27,35),(30,36),(29,40),(27,42),(27,47),(28,51),(28,56),(27,62),(23,63),(20,60),(19,56),(17,58),(16,63),(12,63),(11,60),(12,55),(12,51),(13,47),(12,43),(13,39),(15,36),(13,33),(11,31),(10,28),(10,24),(12,21)]
]
# Narrow lower-leg contours exclude the rungs and floor visible between boots.
BODY[0][BODY[0].index((26,43)):BODY[0].index((11,42))] = [(26,43),(26,48),(26,52),(26,59),(24,60),(21,59),(20,54),(18,53),(17,56),(13,56),(12,54),(13,51),(12,49),(12,44)]
BODY[1][BODY[1].index((27,43)):BODY[1].index((12,41))] = [(27,43),(27,46),(26,49),(25,51),(27,54),(27,56),(24,58),(20,58),(18,56),(17,56),(16,58),(12,58),(11,55),(12,52),(12,49),(13,47),(13,43)]
BODY[2][BODY[2].index((26,43)):BODY[2].index((13,40))] = [(26,43),(26,47),(27,50),(27,53),(25,54),(22,53),(20,50),(18,51),(18,56),(16,61),(15,62),(11,62),(11,60),(12,56),(13,52),(13,48),(12,44)]
BODY[3][BODY[3].index((27,42)):BODY[3].index((13,39))] = [(27,42),(27,47),(28,50),(28,54),(26,55),(22,55),(20,53),(19,49),(18,52),(17,55),(12,55),(11,53),(12,49),(12,46),(13,42)]
GUARD = [(21,10),(28,10),(31,12),(32,16),(31,20),(29,22),(29,24),(31,26),(33,26),(35,29),(37,31),(37,35),(34,36),(31,35),(30,33),(28,34),(28,38),(26,40),(26,43),(24,46),(22,48),(21,51),(22,54),(24,56),(23,58),(16,58),(14,56),(14,52),(15,48),(17,45),(16,43),(15,40),(12,39),(12,36),(13,32),(14,29),(17,26),(18,23),(18,20),(17,18),(17,14),(19,11)]
ATTACK_BODY = [
 [(55,48),(58,49),(60,52),(64,52),(68,52),(69,50),(71,50),(73,53),(74,57),(76,59),(76,62),(74,64),(71,64),(71,68),(73,69),(73,72),(70,74),(70,78),(69,81),(70,85),(70,91),(67,92),(63,91),(62,88),(60,90),(57,90),(56,88),(57,84),(57,81),(58,77),(57,74),(58,72),(60,69),(59,67),(57,65),(55,63),(54,60),(54,55),(54,52)],
 [(43,46),(46,46),(48,48),(51,49),(54,52),(58,54),(58,51),(60,49),(62,47),(65,48),(68,50),(70,51),(71,50),(73,50),(74,53),(75,55),(75,58),(72,60),(70,60),(69,64),(69,67),(70,69),(70,73),(69,76),(70,80),(70,87),(68,89),(64,89),(62,86),(59,87),(57,86),(57,83),(58,79),(57,76),(58,73),(58,70),(59,67),(57,65),(57,61),(55,60),(51,57),(48,53),(45,51),(43,49)],
 [(63,46),(67,46),(69,48),(71,50),(72,51),(74,51),(76,54),(76,57),(73,60),(70,60),(70,64),(69,66),(70,70),(70,75),(69,77),(70,82),(70,87),(68,89),(64,88),(63,85),(61,86),(59,84),(59,80),(60,77),(58,76),(58,73),(59,70),(58,68),(59,64),(59,62),(58,60),(56,58),(54,56),(54,52),(57,49),(60,49),(60,47)]
]


def png(image):
    stream=io.BytesIO();image.save(stream,format='PNG');return stream.getvalue()


def register(images,a,b,boxes,expected,margin=3,maximum=9):
    records=[match(images[a].astype(np.int16),images[b].astype(np.int16),box,0) for box in boxes]
    assert all(p['delta']==expected and p['mae_rgb']<maximum and
               p['runner_up_mae_rgb']-p['mae_rgb']>margin for p in records),records
    return {'from':a,'to':b,'delta':expected,'patches':records,'minimum_runner_up_margin':margin}


def outputs():
    images={name:np.asarray(Image.open(path).convert('RGB')) for name,path in SOURCES.items()}
    measurements=[]
    for name,delta in [('190_6',[-6,12]),('190_7',[-12,24])]:
        measurements.append(register(images,'foot',name,[(140,20,149,30),(175,18,183,27)],delta))
    for name,delta in [('191_4',[-12,21]),('191_5',[-12,24]),('191_6',[-12,24]),('192_7',[-12,31]),('193_1',[-12,45]),('194_3',[28,60])]:
        measurements.append(register(images,'top',name,[(156,80,168,91),(178,79,190,91)],delta))
    measurements.append(register(images,'top','194_5',[(143,78,155,90),(70,50,80,62)],[55,31]))
    measurements.append(register(images,'top','193_5',[(156,80,168,91),(178,79,190,91)],[-12,69],maximum=12))
    for name,delta,margin in [('189_0',[-38,-12],1.5),('189_8',[-14,-13],2)]:
        measurements.append(register(images,'foot',name,[(130,42,140,56),(130,63,140,77)],delta,margin=margin))
    measurements.append(register(images,'top','193_7',[(180,40,192,50),(200,52,210,64)],[-12,88]))
    palette=(ROOT/'assets/continuation_palette.bin').read_bytes()
    words=np.frombuffer(palette,dtype='<u2')
    colors=np.array([[(int(w)>>s&31)*255//31 for s in (0,5,10)] for w in words],dtype=np.uint8)
    result={};poses=[];stream=bytearray()
    pose_specs=[('foot',(140,48,180,112),[0,0]),('190_6',(134,54,174,118),[-6,12]),
                ('190_7',(128,60,168,124),[-12,24]),('top',(110,80,150,144),[-30,60])]
    for i,(name,box,translation) in enumerate(pose_specs):
        rgb=Image.fromarray(images[name]).crop(box);mask=Image.new('L',(40,64));d=ImageDraw.Draw(mask);d.polygon(BODY[i],fill=255)
        # Ladder rungs in the arm/leg gaps are transparent, not part of Sia.
        d.polygon([(11,24),(13,23),(14,25),(13,28),(11,28)],fill=0)
        d.polygon([(17,47),(19,47),(20,51),(19,56),(17,56)],fill=0)
        rgba=rgb.convert('RGBA');rgba.putalpha(mask);rgba=clean(rgba);data=indexed(rgba,palette)
        assert data.max()<240 and data.min()==0
        stream.extend(data.tobytes());result[f'ladder_pose_{i}.png']=png(rgba)
        poses.append({'source':name,'crop':box,'anchor':[20,64],'camera_translation_from_foot':translation,
                      'logical_feet':box[3],'opaque_pixels':int(np.count_nonzero(data))})
    result['ladder_cycle.bin']=bytes(stream)
    attacks=[];stream=bytearray();row_bounds=bytearray()
    for i,(name,top) in enumerate([('191_4',53),('191_5',56),('191_6',56)]):
        rgb=Image.fromarray(images[name]).crop((54,top,166,top+96));a=np.asarray(rgb).astype(np.int16)
        mask=Image.new('L',(112,96));d=ImageDraw.Draw(mask)
        d.polygon(ATTACK_BODY[i],fill=255)
        r,g,b=a.transpose(2,0,1);green=(g>r+30)&(g>b+30)&(g>85)
        edge=binary_dilation(green,iterations=1)
        bright=(a.min(axis=2)>170)&(a.max(axis=2)-a.min(axis=2)<80)
        blade=edge&(((g>r+12)&(g>b+12))|bright)
        yy,xx=np.indices(blade.shape)
        # Enemy hit stars belong to a contact effect, not every sword swing.
        blade &= ((yy>=20)&(yy<52)&(xx>=32)&(xx<96)) if i==1 else ((yy>=60)&(xx>=30)&(xx<=63)) if i==2 else False
        components,n=label(blade)
        sizes=np.bincount(components.ravel());sizes[0]=0
        blade=(components==sizes.argmax()) if n else blade
        combined=np.maximum(np.asarray(mask),blade.astype(np.uint8)*255)
        rgba=rgb.convert('RGBA');rgba.putalpha(Image.fromarray(combined));rgba=clean(rgba);data=indexed(rgba,palette)
        assert data.max()<240 and data.min()==0
        for row in data:
            ink=np.flatnonzero(row)
            row_bounds.extend((int(ink[0]),int(ink[-1]-ink[0]+1)) if len(ink) else (0,0))
        stream.extend(data.tobytes());result[f'ladder_attack_{i}.png']=png(rgba)
        attacks.append({'source':name,'crop':[54,top,166,top+96],'anchor':[64,96],
                        'canonical_facing':'left','opaque_pixels':int(np.count_nonzero(data))})
    result['ladder_attack_cycle.bin']=bytes(stream)
    result['ladder_attack_bounds.bin']=bytes(row_bounds)
    guard=Image.fromarray(images['top']).crop((79,18,127,82)).convert('RGBA')
    mask=Image.new('L',(48,64));ImageDraw.Draw(mask).polygon(GUARD,fill=255);guard.putalpha(mask)
    result['ladder_upper_guard.bin']=indexed(guard,palette).tobytes();result['ladder_upper_guard.png']=png(guard)

    # Origin differences register static foreground only; clouds stay independent.
    shifts={'189_0':(-8,-72),'189_8':(16,-73),'foot':(30,-60),'190_6':(24,-48),'190_7':(18,-36),'top':(0,0),
            '191_4':(-12,21),'191_5':(-12,24),'191_6':(-12,24),'192_7':(-12,31),'193_1':(-12,45),'194_3':(28,60),'194_5':(55,31),'193_5':(-12,69),'193_7':(-12,88)}
    actor_boxes={
        '189_0':[(108,76,38,38),(147,58,45,58)],
        '189_8':[(155,61,38,49),(102,87,55,22)],
        'foot':[(140,60,45,55),(98,14,31,10)],
        '190_6':[(135,68,44,53),(94,14,37,24)],
        '190_7':[(128,75,44,52),(94,14,36,36)],
        'top':[(77,25,52,59),(109,94,45,63),(119,12,25,23)],
        '191_4':[(68,14,60,80),(79,77,86,83),(106,28,27,25)],
        '191_5':[(68,14,60,80),(79,77,86,83),(106,28,27,25)],
        '191_6':[(68,14,60,80),(79,77,86,83),(106,28,27,25)],
        '192_7':[(59,88,51,25),(100,70,46,49),(108,39,24,24)],
        '193_1':[(59,103,52,23),(105,77,46,49),(108,53,24,24)],
        '194_3':[(99,59,57,72),(0,132,48,28)],
        '194_5':[(94,70,48,67),(0,132,48,28)],
        '193_5':[(100,106,49,54),(105,90,28,25)],
        '193_7':[(96,80,62,80),(0,132,48,28),(16,14,26,22)]}
    usable={}
    for name in shifts:
        valid=np.ones((160,240),bool);valid[:14]=False;valid[13:45,204:240]=False
        for x,y,w,h in actor_boxes[name]:valid[y:y+h,x:x+w]=False
        usable[name]=valid&foreground(images[name])
        if name=='193_7':usable[name][:,:164]=False  # donor selected only to expose the upper-right tower header
    backgrounds=[];yy,xx=np.indices((160,240))
    for filename,target,origin,plane in [('ladder_upper','top',[-612,321],80),('ladder_upper_exit','192_7',[-624,352],111)]:
        original=images[target];a=original.copy();repair=np.zeros((160,240),bool)
        repair[:14]=True;repair[13:45,204:240]=True
        for x,y,w,h in actor_boxes[target]:repair[y:y+h,x:x+w]=True
        recovered=np.zeros_like(repair)
        for donor in ['foot','190_6','190_7','top','192_7','193_1','194_3','194_5','193_5','193_7']:
            if donor==target:continue
            dx=shifts[donor][0]-shifts[target][0];dy=shifts[donor][1]-shifts[target][1]
            sx,sy=xx+dx,yy+dy;inside=(sx>=0)&(sx<240)&(sy>=0)&(sy<160)
            sx=sx.clip(0,239);sy=sy.clip(0,159)
            take=repair&~recovered&inside&usable[donor][sy,sx]
            a[take]=images[donor][sy[take],sx[take]];recovered[take]=True
        missing=repair&~recovered
        # Remaining shaft pixels hidden in every exposure reuse the cleaned
        # foot view. They stay classified as estimates, including its small
        # explicitly documented repeated rung fragment.
        clean_foot=np.asarray(Image.open(ROOT/'assets/ladder_foot_background.png').convert('RGB'))
        dx,dy=30-shifts[target][0],-60-shifts[target][1]
        sx,sy=xx+dx,yy+dy;inside=(sx>=0)&(sx<240)&(sy>=0)&(sy<160)
        sx=sx.clip(0,239);sy=sy.clip(0,159)
        derived=missing&inside&(xx>=115+(0 if target=='top' else -12))&(xx<155+(0 if target=='top' else -12))&(yy>=plane)&foreground(clean_foot)[sy,sx]
        a[derived]=clean_foot[sy[derived],sx[derived]]
        # Only the remaining covered walk surface is interpolated laterally.
        surface=np.rint(np.interp(xx+(12 if target=='192_7' else 0),[0,20,40,80,100,118,148,175],[69,71,73,76,76,80,80,85])).astype(int)+(31 if target=='192_7' else 0)
        terrain_missing=missing&~derived&(yy>=surface-1)&(xx<176+(0 if target=='top' else -12))&(yy<surface+13)
        for y in range(160):
            for x in np.flatnonzero(terrain_missing[y]):
                left=x-1;right=x+1
                while left>=0 and missing[y,left]:left-=1
                while right<240 and missing[y,right]:right+=1
                if left>=0 and right<240:a[y,x]=np.rint((a[y,left].astype(float)*(right-x)+a[y,right].astype(float)*(x-left))/(right-left)).astype(np.uint8)
        sky_holes=missing&~terrain_missing&~derived
        a[:14][sky_holes[:14]]=np.median(a[14,136:166],axis=0).astype(np.uint8)
        sky_fill(a,sky_holes,(140,151),53 if target=='top' else 84)
        assert np.array_equal(a[~repair],original[~repair])
        indices=indexed(Image.fromarray(a),palette);assert indices.min()>=1 and indices.max()<240
        result[filename+'_background.bin']=palette+indices.tobytes()
        result[filename+'_background.png']=png(Image.fromarray(a))
        result[filename+'_background_preview.png']=png(Image.fromarray(colors[indices]).resize((720,480),Image.Resampling.NEAREST))
        result[filename+'_repair_mask.png']=png(Image.fromarray((missing.astype(np.uint8)*255)))
        backgrounds.append({'name':filename,'source':target,'origin':origin,'observed_rgb_pixels_preserved':int((~repair).sum()),
                            'registered_foreground_pixels':int(recovered.sum()),'estimated_pixels':int(missing.sum()),
                            'estimated_terrain_pixels':int(terrain_missing.sum()),'derived_ladder_pixels':int(derived.sum())})
    manifest={'video_sha256':'7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51',
              'sources':{name:{'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for name,path in SOURCES.items()},
              'registrations':measurements,'climb_poses':poses,'attack_poses':attacks,'guard':{'source':'top','crop':[79,18,127,82],'size':[48,64],'anchor':[24,58],'facing':'right'},
              'backgrounds':backgrounds,'climb_speed_pixels_per_update':1,
              'limits':['Silhouettes are manually masked from compressed video and quantized to the shared palette',
                        'Camera guide, patrol, timing and collision geometry remain authored approximations',
                        'Unseen sky/header and persistently covered grass are declared estimates',
                        'The blue floating object is removed from scenery; its unconfirmed behavior is not invented here',
                        'The next floating-island route and complete level/bosses remain unfinished']}
    result['ladder_climb_manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode();return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    for name,payload in outputs().items():
        path=ROOT/'assets'/name
        if args.check:
            if name.endswith('.png'):assert Image.open(path).convert('RGBA').tobytes()==Image.open(io.BytesIO(payload)).convert('RGBA').tobytes(),name
            else:assert path.read_bytes()==payload,name
        else:path.write_bytes(payload)
    print('PASS ladder climb assets: thirteen independent registrations, four climb poses, three mounted sword poses, captured guard and two masked upper backgrounds')


if __name__=='__main__':main()
