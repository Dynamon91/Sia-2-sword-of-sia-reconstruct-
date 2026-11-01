"""Verify native animation buffers, palette contract and declared foot anchors."""
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]/'assets'
for name,w,h,n in [('walk_cycle.bin',48,56,3),('attack_cycle.bin',80,64,3)]:
 data=(root/name).read_bytes();assert len(data)==w*h*n,name
 frames=np.frombuffer(data,dtype='uint8').reshape(n,h,w)
 assert len({f.tobytes() for f in frames})==n,'Duplicate pose'
 assert (frames<240).all(),'Actor uses reserved UI colors'
 for f in frames:
  assert f[-1].any(),'Boot does not reach declared anchor'
  assert (f==0).sum()>w*h//3,'Missing alpha background'
assert (root/'gap.bin').stat().st_size==38912
assert (root/'ui_more_tiles.bin').stat().st_size==512
print('PASS motion assets: distinct 3-frame cycles, exact buffer sizes, opaque palette bounds, transparent background and fixed boot anchors')
