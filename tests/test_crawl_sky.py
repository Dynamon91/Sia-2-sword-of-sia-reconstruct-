"""Keep the captured terrain intact when replacing copied parallax clouds."""
from pathlib import Path
import sys
import struct
import unittest
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from convert_crawl_passage import restored_sky_overlay,encode_sky_overlay

class CrawlSkyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.image=Image.open(ROOT/'assets/crawl_passage_background.png').convert('RGB')
  cls.header=(ROOT/'assets/continuation_palette.bin').read_bytes()
  cls.patch,cls.mask=restored_sky_overlay(cls.image,cls.header)

 def test_only_declared_sky_can_replace_world_pixels(self):
  allowed=np.zeros((160,240),bool)
  allowed[:14]=True
  allowed[:45,204:240]=True
  allowed[37:55,142:192]=True
  self.assertFalse(np.any(self.mask&~allowed))
  np.testing.assert_array_equal(self.patch!=0,self.mask[:55])
  self.assertFalse(np.any(self.mask[55:]))
  # Uncovered roots, ground and all pixels outside the mask keep their
  # existing world-bank value, including arbitrary overlap priorities.
  world=np.arange(160*240,dtype=np.uint16).reshape(160,240)%239+1
  rendered=world.copy();rendered[:55][self.patch!=0]=self.patch[self.patch!=0]
  np.testing.assert_array_equal(rendered[~self.mask],world[~self.mask])

 def test_sky_ignores_old_parallax_and_floor_colors(self):
  changed=np.asarray(self.image).copy()
  changed[37:55,142:192]=[255,0,255]
  changed[55:]=[255,0,0]
  patch,mask=restored_sky_overlay(Image.fromarray(changed),self.header)
  np.testing.assert_array_equal(patch,self.patch)
  np.testing.assert_array_equal(mask,self.mask)

 def test_no_warm_stipple_or_ui_palette_ink(self):
  ink=self.patch[self.patch!=0]
  self.assertGreater(len(ink),4000)
  self.assertTrue(np.all(ink<240))
  words=np.frombuffer(self.header,dtype='<u2')
  colors=np.array([[(int(w)>>s&31)*255//31 for s in (0,5,10)] for w in words],np.int16)
  rgb=colors[ink]
  self.assertTrue(np.all(rgb[:,1]>=rgb[:,0]))
  self.assertTrue(np.all(rgb[:,2]>=rgb[:,1]-8))

 def test_both_dma_banks_reproduce_the_same_sparse_overlay(self):
  data=encode_sky_overlay(self.patch)
  decoded=np.zeros_like(self.patch)
  for y in range(55):
   off=struct.unpack_from('<H',data,y*2)[0]
   self.assertEqual(off%2,0)
   count=data[off];off+=2
   for _ in range(count):
    x,n=data[off:off+2];off+=2
    self.assertGreater(n,0);self.assertLessEqual(x+n,240)
    self.assertEqual(off%2,0)
    even=data[off:off+n]
    odd_start=off+((n+1)&~1)+1
    self.assertEqual(odd_start%2,1)
    self.assertEqual(data[odd_start:odd_start+n],even)
    self.assertTrue(all(even))
    decoded[y,x:x+n]=np.frombuffer(even,np.uint8)
    off+=((n+1)&~1)+((n+2)&~1)
  np.testing.assert_array_equal(decoded,self.patch)

if __name__=='__main__':unittest.main()
