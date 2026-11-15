"""Source proof and bounds for the recording-covered crawl roof."""
from pathlib import Path
import sys,unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from restore_crawl_roof import build_overlay

class CrawlRoofTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.patch,cls.roof,cls.sky,cls.info=build_overlay()

 def test_independent_roots_register_without_parallax_sky(self):
  for p in self.info['registrations']:
   self.assertTrue(p['accepted'])
   self.assertEqual(p['delta'],[83,-63])
   self.assertGreaterEqual(p['foreground_pixels'],30)
  self.assertFalse(self.info['rejected_repeated_root']['accepted'])

 def test_only_recording_header_can_be_replaced(self):
  expected=np.zeros((55,240),bool);expected[:14,83:240]=True
  np.testing.assert_array_equal(self.patch!=0,expected)
  self.assertFalse(np.any(self.roof[14:]))
  self.assertEqual(self.info['observed_target_pixels_changed'],0)

 def test_recovered_terrain_keeps_exact_source_indices(self):
  source=(ROOT/'assets/lower_landing_background.bin').read_bytes()
  pixels=np.frombuffer(source[512:],np.uint8).reshape(160,240)[63:77,:157]
  mask=self.roof[:14,83:240]
  self.assertGreater(mask.sum(),500)
  np.testing.assert_array_equal(self.patch[:14,83:240][mask],pixels[mask])
  self.assertTrue(np.all(self.patch[self.patch!=0]<240))

 def test_reconstructed_sky_has_no_warm_stipple(self):
  words=np.frombuffer((ROOT/'assets/continuation_palette.bin').read_bytes(),dtype='<u2')
  colors=np.array([[(int(w)>>s&31)*255//31 for s in (0,5,10)] for w in words],np.int16)
  rgb=colors[self.patch[self.sky[:55]]]
  self.assertTrue(np.all(rgb[:,1]>=rgb[:,0]))
  self.assertTrue(np.all(rgb[:,2]>=rgb[:,1]-8))

if __name__=='__main__':unittest.main()
