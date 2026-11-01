"""Observed W1L1 motion poses, gem digits and the gap at 155s.
Video extraction is reproducible; polygons are hand masks, not original assets.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageFilter
import numpy as np,json,argparse
from convert_room import extract
from repair_sprite_edges import clean,indexed
from convert_ui import digit,tiled

def mask_pose(im,points):
    mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon(points,fill=255)
    im=im.convert('RGBA');im.putalpha(mask)
    im=clean(im)
    a=np.array(im);rgb=a[:,:,:3].astype(int);r,g,b=rgb.transpose(2,0,1)
    terrain=(r>115)&(g>105)&(b>60)&(abs(r-g)<40)&(r>b+15)
    terrain[:int(im.height*.65)]=False
    alpha=a[:,:,3]>0
    for _ in range(4):
        inner=np.asarray(Image.fromarray((alpha*255).astype('uint8')).filter(ImageFilter.MinFilter(3)))>0
        alpha &= ~(terrain&alpha&~inner)
    a[:,:,3]=alpha*255
    from scipy.ndimage import label
    labels,count=label(alpha,np.ones((3,3)))
    sizes=np.bincount(labels.ravel())
    alpha &= sizes[labels]>2
    a[:,:,3]=alpha*255
    # Keep the final opaque boot row on the declared foot anchor in every pose.
    rows=np.where(alpha.any(axis=1))[0]
    if len(rows) and im.width in (48,80):
        shift=im.height-1-int(rows[-1])
        if shift:a=np.pad(a,((shift,0),(0,0),(0,0)))[:im.height]
    return Image.fromarray(a)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('video');args=ap.parse_args()
    out=Path(__file__).resolve().parents[1]/'assets'
    times=[142.9,142.95,143.05,137.9,138,138.2,132.5,134,150,155,156,157]
    frames={t:extract(args.video,t) for t in times}
    header=(out/'room.bin').read_bytes()[:512]
    runs=[
      (142.9,(79,70,127,126),[(18,12),(26,12),(30,17),(38,18),(41,23),(39,29),(35,32),(40,35),(42,39),(38,41),(33,39),(30,41),(32,46),(39,50),(42,51),(40,55),(34,55),(29,49),(25,45),(19,45),(17,48),(10,48),(8,46),(9,40),(14,38),(17,34),(12,32),(12,28),(17,25),(15,20)]),
      (142.95,(75,78,123,134),[(19,12),(27,12),(28,16),(35,16),(39,20),(38,26),(34,29),(34,36),(37,39),(33,42),(30,42),(30,47),(34,51),(35,55),(26,55),(25,49),(22,44),(20,47),(17,46),(14,40),(15,35),(12,32),(14,28),(18,25),(16,22),(15,18)]),
      (143.05,(71,81,119,137),[(21,12),(29,12),(31,16),(37,15),(41,19),(40,25),(36,29),(45,24),(47,26),(37,37),(32,39),(29,44),(28,50),(29,54),(21,55),(19,52),(20,47),(18,46),(20,40),(22,35),(21,30),(24,26),(19,23),(18,18)])]
    poses=[]
    for i,(t,box,poly) in enumerate(runs):
        im=mask_pose(frames[t].crop(box),poly);im.save(out/f'walk_{i}.png');poses.append(im)
    (out/'walk_cycle.bin').write_bytes(b''.join(indexed(im,header).tobytes() for im in poses))
    # The source attack faces left; normalize to the right, preserving the full arc.
    attacks=[
      (137.9,(128,40,208,104),[(35,20),(45,18),(49,22),(48,28),(44,33),(49,37),(53,36),(56,22),(59,20),(59,25),(55,39),(59,41),(55,45),(49,44),(44,41),(42,44),(44,51),(49,59),(49,63),(44,63),(38,54),(34,51),(31,58),(26,58),(25,54),(29,49),(27,44),(24,43),(21,45),(19,42),(23,38),(27,36),(25,30),(28,25)]),
      (138,(121,45,201,109),[(0,28),(5,19),(13,11),(23,7),(24,10),(16,16),(10,27),(9,36),(15,42),(25,45),(29,37),(34,33),(31,29),(31,23),(35,21),(40,22),(43,19),(48,19),(51,22),(48,29),(44,32),(47,38),(54,40),(55,43),(51,46),(47,43),(45,45),(49,50),(52,60),(49,63),(44,60),(42,53),(36,51),(31,58),(28,62),(23,61),(25,54),(28,48),(22,49),(11,47),(4,43),(0,36)]),
      (138.2,(120,45,200,109),[(37,19),(45,19),(49,23),(49,28),(45,30),(44,35),(42,38),(48,43),(47,47),(43,48),(45,52),(48,59),(45,63),(36,63),(32,60),(34,56),(36,52),(33,48),(31,41),(23,34),(20,30),(22,28),(30,33),(33,33),(31,28),(31,24)])]
    poses=[]
    for i,(t,box,poly) in enumerate(attacks):
        im=ImageOps.mirror(mask_pose(frames[t].crop(box),poly));im.save(out/f'attack_{i}.png');poses.append(im)
    (out/'attack_cycle.bin').write_bytes(b''.join(indexed(im,header).tobytes() for im in poses))
    # Camera/terrain registration: 145 -> 155 (-158,+18), 157 -> 155 (+20,0).
    bg=frames[155].copy()
    bg.paste(frames[150].crop((138,58,173,108)),(54,58))
    bg.paste(frames[156].crop((200,48,234,103)),(200,48))
    # Remove gem and channel overlays only. Sky hidden by the video is estimated.
    for left,top,right,bottom in [(126,40,144,58),(207,14,240,34)]:
        for y in range(top,bottom):
            lc=bg.getpixel((left-1,y));rc=bg.getpixel((right,y)) if right<240 else lc
            for x in range(left,right):
                w=(x-left+1)/(right-left+1);bg.putpixel((x,y),tuple(round(lc[k]*(1-w)+rc[k]*w) for k in range(3)))
    for y in range(14):
        for x in range(240):bg.putpixel((x,y),bg.getpixel((x,14)))
    bg.save(out/'gap_reference.png');(out/'gap.bin').write_bytes(header+indexed(bg,header).tobytes())
    enemy=mask_pose(frames[155].crop((200,49,234,104)),[(15,3),(22,5),(24,10),(22,15),(23,19),(21,25),(18,30),(17,38),(22,45),(22,49),(17,51),(13,47),(11,40),(10,39),(10,46),(8,50),(3,50),(3,47),(7,43),(6,35),(7,28),(5,25),(7,18),(11,13),(10,9)])
    enemy.save(out/'guard2_cutout.png');(out/'guard2_sprite.bin').write_bytes(indexed(enemy,header).tobytes())
    ui_header=(out/'ui_palette.bin').read_bytes();data=bytearray()
    for n,t in [(3,132.5),(4,134)]:
        im=digit(frames[t].crop((129,29,145,45)));im.save(out/f'ui_digit{n}_reference.png')
        data.extend(tiled(indexed(im,ui_header)))
    (out/'ui_more_tiles.bin').write_bytes(data)
    (out/'motion_gap_manifest.json').write_text(json.dumps({'walk_frames':3,'walk_sources':[142.9,142.95,143.05],'walk_size':[48,56],'walk_anchor':[24,56], 'attack_frames':3,'attack_sources':[137.9,138,138.2],'attack_size':[80,64],'attack_anchor':[39,64], 'gap_source':155,'guard_to_gap':[-158,18],'gap_surfaces':[[0,106,98],[172,98,68]],'gem':[126,40],'limits':['Manually traced compressed recording poses, not original sprite sheets','Animation timing estimated','Enemy firing behavior is not yet reconstructed','Unseen upper sky estimated; preceding corridor still incomplete']},indent=2)+'\n')
    print('Built three walk poses, three attack phases, gap viewport, second guard and original-style digits 3/4')
if __name__=='__main__':main()
