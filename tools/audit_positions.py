"""Measure the shared foreground island between the two extracted viewports.
This audits observed image alignment, not original hidden collision metadata.
"""
from pathlib import Path
import json,re,argparse
import numpy as np
from PIL import Image

def main():
 root=Path(__file__).resolve().parents[1]
 p=argparse.ArgumentParser();p.add_argument('--output',default=str(root/'POSITION_AUDIT_v06.json'));args=p.parse_args()
 first=np.asarray(Image.open(root/'assets/room_background_reference.png').convert('RGB')).astype(int)
 second=np.asarray(Image.open(root/'assets/bridge_background_reference.png').convert('RGB')).astype(int)
 patch=first[39:64,187:234];candidates=[]
 for dx in range(-160,-144):
  for dy in range(52,70):
   crop=second[39+dy:64+dy,187+dx:234+dx]
   if crop.shape!=patch.shape:continue
   score=float(np.median(np.mean(abs(patch[:,:25]-crop[:,:25]),axis=2)))
   candidates.append((score,dx,dy))
 candidates.sort();score,dx,dy=candidates[0]
 header=(root/'src/alignment.h').read_text()
 def define(name):return int(re.search(r'#define\s+'+name+r'\s+(\d+)',header).group(1))
 configured=(-define('AREA_OFFSET_X'),define('AREA_OFFSET_Y'))
 assert configured==(dx,dy),(configured,(dx,dy))
 assert define('BRIDGE_SURFACE_Y')==40+dy
 report={'version':'0.6','source_images':['assets/room_background_reference.png','assets/bridge_background_reference.png'],
  'method':'median absolute RGB difference of the left, unobstructed shared-island patch',
  'first_patch_xyxy':[187,39,234,64],'comparison_patch_width':25,
  'measured_first_to_bridge':[dx,dy],'configured_first_to_bridge':list(configured),
  'median_rgb_error_8bit':score,'next_best_rgb_error_8bit':candidates[1][0],
  'configuration_matches_measurement':True,
  'corrections':{
   'forward_portal':'preserve position via registered offset instead of fixed (60,61); nominal correction +13..14 px X, -1 px Y',
   'return_portal':'preserve inverse registered offset instead of fixed (208,0); nominal correction about -24 px X',
   'bridge_collision_plane':'101 -> 100, matching shared upper-platform surface after +60 Y transform',
   'mirrored_sprite_anchor':'add the necessary one-pixel origin correction to keep source anchor fixed'},
  'ui_positions_unchanged':{'portrait':[0,102],'gem_icon':[95,11],'digit':[129,29],'menu_cursor':[16,44]},
  'limits':['registration measures visible shared foreground only','original collision map not recovered','discrete viewport change remains','later sections not yet implemented','video-covered sky still approximate']}
 Path(args.output).write_text(json.dumps(report,indent=2)+'\n')
 print('PASS: shared island transform',configured,'matches configured offsets; bridge plane',define('BRIDGE_SURFACE_Y'))
if __name__=='__main__':main()
