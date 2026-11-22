"""A static, unoccupied ladder must not contain a recorded green sword flash."""
from pathlib import Path
import unittest
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]

class LadderScenery(unittest.TestCase):
 def test_no_sword_green_on_unoccupied_ladder(self):
  regions={'ladder_foot':(150,60,184,110),'ladder_upper':(115,120,150,160),
           'ladder_upper_exit':(103,111,138,160)}
  for name,box in regions.items():
   with self.subTest(view=name):
    rgb=np.asarray(Image.open(ROOT/'assets'/f'{name}_background.png').convert('RGB').crop(box)).astype(np.int16)
    r,g,b=rgb.transpose(2,0,1)
    self.assertFalse(np.any((g>r+30)&(g>b+30)&(g>85)), 'Recorded attack flash baked into ladder scenery')

if __name__=='__main__':unittest.main()
