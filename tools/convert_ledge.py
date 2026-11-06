"""Extract observed ledge hang/pull-up poses from W1L1, with fixed ledge anchors.
Manual silhouettes and camera registration are reconstruction estimates.
"""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion
from convert_room import extract
from repair_sprite_edges import indexed

WIDTH, HEIGHT, ANCHOR_X, ANCHOR_Y = 48, 104, 24, 44
# Absolute coordinates in the normalized 240x160 video. Camera shifts were
# measured against the unoccluded right edge of the first rock platform.
POSES = [
 (120.72, 7, [(109,86),(111,86),(113,89),(119,89),(121,90),(120,94),(125,96),(128,99),(130,100),(130,102),(126,102),(120,98),(119,109),(121,110),(121,115),(120,118),(124,125),(124,131),(126,135),(126,141),(127,144),(124,147),(118,145),(114,144),(112,141),(112,136),(115,135),(113,129),(111,126),(110,123),(112,117),(110,114),(109,119),(105,119),(103,116),(102,116),(102,112),(100,112),(100,107),(104,103),(104,101),(108,99),(111,98),(112,96),(112,94),(110,92),(109,90),(108,89)]),
 (120.88,11, [(105,84),(111,84),(113,86),(114,91),(112,94),(115,94),(119,95),(120,98),(124,99),(127,102),(130,103),(130,105),(125,104),(120,101),(120,106),(121,110),(124,110),(125,112),(123,116),(118,118),(116,120),(117,123),(114,124),(110,122),(108,117),(107,112),(104,111),(103,108),(103,101),(99,101),(98,99),(98,92),(101,89),(103,88)]),
 (120.96,11, [(105,77),(111,77),(114,80),(114,85),(113,88),(115,92),(118,94),(119,98),(123,100),(124,102),(128,102),(130,104),(130,106),(126,106),(124,110),(120,110),(116,106),(114,103),(114,108),(115,111),(118,114),(120,117),(120,121),(116,122),(113,119),(112,115),(108,113),(106,110),(104,109),(103,106),(103,99),(104,95),(102,95),(99,92),(99,89),(98,88),(98,84),(102,81),(104,81)]),
 (121.04,11, [(106,70),(111,70),(113,72),(119,72),(121,75),(120,79),(119,81),(119,86),(118,88),(121,89),(124,92),(125,95),(125,98),(127,101),(127,104),(125,107),(120,106),(119,102),(120,99),(119,96),(117,95),(114,94),(114,99),(115,102),(111,103),(108,100),(108,95),(107,94),(106,91),(104,89),(103,85),(103,81),(101,82),(100,80),(99,78),(101,74),(103,73)])
]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('video',type=Path);a=ap.parse_args()
 root=Path(__file__).resolve().parents[1];out=root/'assets';header=(out/'room.bin').read_bytes()[:512]
 frames=[];records=[]
 for i,(seconds,shift,points) in enumerate(POSES):
  source=extract(str(a.video),seconds)
  left,top=115-ANCHOR_X,88+shift-ANCHOR_Y
  pose=source.crop((left,top,left+WIDTH,top+HEIGHT)).convert('RGBA')
  alpha=Image.new('L',(WIDTH,HEIGHT));ImageDraw.Draw(alpha).polygon([(x-left,y-top) for x,y in points],fill=255)
  # Remove sky admitted at polygon boundaries by video compression/hand masking.
  rgb=np.asarray(pose).astype(int);r,g,b=rgb[:,:,:3].transpose(2,0,1)
  sky=(b>r+15)&(g>r+10)&(b>g+6)&(b-g<50)&(r>55)
  mask=np.asarray(alpha)>0
  for _ in range(2):mask &= ~(sky & ~binary_erosion(mask,np.ones((3,3))))
  pose.putalpha(Image.fromarray((mask*255).astype('uint8')));encoded=indexed(pose,header)
  assert not encoded[0].any() and not encoded[-1].any()
  assert not encoded[:,0].any() and not encoded[:,-1].any()
  assert encoded.max()<240
  frames.append(encoded.tobytes());pose.save(out/f'ledge_pose_{i}.png')
  records.append({'seconds':seconds,'camera_shift_pixels':[0,shift],'source_ledge_anchor':[115,88+shift]})
 assert len(set(frames))==4
 (out/'ledge_cycle.bin').write_bytes(b''.join(frames))
 report={'source_sha256':hashlib.sha256(a.video.read_bytes()).hexdigest(),'size':[WIDTH,HEIGHT],'anchor':[ANCHOR_X,ANCHOR_Y],'poses':records,'states':['hanging','pull_start','pull_middle','pull_end'],'limits':['Hand-traced silhouettes from compressed video, not recovered original sprites.','The common anchor is the rock ledge, not the character boots.','Timing and collision catch window are reconstruction estimates.']}
 (out/'ledge_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS: four distinct ledge poses, fixed rock anchor, reserved palette excluded, transparent borders')
if __name__=='__main__':main()
