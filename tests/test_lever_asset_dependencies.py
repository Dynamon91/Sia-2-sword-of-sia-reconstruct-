"""A remote atlas edit must not invalidate an unchanged local lever patch."""
import json
from pathlib import Path
import shutil,sys,tempfile,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import convert_lever_pose as converter

class LeverDependencies(unittest.TestCase):
 def test_local_inputs_and_unrelated_world_change(self):
  original=converter.ROOT
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory)
   for name in ['reference/w1l1_next/180.png','reference/w1l1_next/182.png','assets/continuation_palette.bin','assets/scroll_world.bin','assets/scroll_manifest.json']:
    dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original/name,dest)
   with patch.object(converter,'ROOT',root):
    baseline=converter.outputs();world=root/'assets/scroll_world.bin';data=bytearray(world.read_bytes())
    data[-1]^=1;world.write_bytes(data)
    self.assertEqual(converter.outputs(),baseline)
    ox,oy=json.loads((root/'assets/scroll_manifest.json').read_text())['origins'][13]
    data[(380-oy+104)*1500+64-ox]^=1;world.write_bytes(data)
    changed=converter.outputs()
    self.assertNotEqual(json.loads(changed['lever_pose_manifest.json'])['atlas_region_sha256'],json.loads(baseline['lever_pose_manifest.json'])['atlas_region_sha256'])
if __name__=='__main__':unittest.main()
