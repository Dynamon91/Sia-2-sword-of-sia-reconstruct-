"""Remove the five-pixel actor fragment left by the original temporal patch.
The obscured sky is estimated from adjacent rows; no original-art recovery claim.
"""
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]
p=root/'assets/room.bin';data=bytearray(p.read_bytes())
words=np.frombuffer(data[:512],dtype='<u2')
colors=np.array([[(int(w)>>s&31)*255//31 for s in (0,5,10)] for w in words])
changed=0
for x in range(56,61):
 offset=512+114*240+x
 if colors[data[offset]].max()>45:continue
 above=colors[data[offset-240]];below=colors[data[offset+240]]
 assert above.min()>90 and below.min()>90
 target=(above+below)//2
 data[offset]=int(np.argmin(np.sum((colors[1:240]-target)**2,axis=1)))+1
 changed+=1
p.write_bytes(data)
print('Room residue cleanup:',changed,'pixels; adjacent-row sky estimate')
