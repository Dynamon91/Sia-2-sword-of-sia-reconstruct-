"""Regressions for sky rectangles that used to cut through the upper wall."""
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

class UpperWallAtlasTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  source=(ROOT/'assets/upper_background.bin').read_bytes()
  cls.source=np.frombuffer(source[512:],dtype=np.uint8).reshape(160,240)
  words=np.frombuffer(source[:512],dtype='<u2')
  cls.colors=np.array([[(int(w)>>s&31)*255//31 for s in (0,5,10)] for w in words],dtype=np.int16)
  cls.worlds=[np.frombuffer((ROOT/'assets'/name).read_bytes()[:810000],dtype=np.uint8).reshape(540,1500)
              for name in ('scroll_world.bin','scroll_world_open.bin')]

 def test_wall_stays_solid_in_jump_and_descent_corners(self):
  # Both controller-driven captures expose this strip beyond the photographed
  # right edge. It must continue the brown wall, rather than the sky fallback.
  for world in self.worlds:
   rgb=self.colors[world[189:292,1463:1498]]
   self.assertTrue(np.all((rgb[:,:,0]>rgb[:,:,2]+8)&(rgb[:,:,1]>rgb[:,:,2]+3)))

 def test_visible_wall_detail_is_preserved(self):
  # This wall patch is fully visible in the supplied upper-view reference.
  # Filling the missing corners must retain its exact indexed source pixels.
  for world in self.worlds:
   np.testing.assert_array_equal(world[256:291,1427:1463],self.source[45:80,204:240])

if __name__=='__main__':unittest.main()
