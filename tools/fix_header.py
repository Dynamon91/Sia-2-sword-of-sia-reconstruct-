from pathlib import Path
import sys

LOGO=bytes.fromhex('24ffae51699aa2213d84820a84e409ad11248b98c0817f21a352be199309ce2010464a4af82731ec58c7e83382e3cebf85f4df94ce4b09c194568ac01372a7fc9f844d73a3ca9a615897a327fc039876231dc7610304ae56bf38840040a70efdff52fe036f9530f197fbc08560d68025a963be03014e38e2f9a234ffbb3e0344780090cb88113a9465c07c6387f03cafd625e48b380aac7221d4f807')
def fix(path):
    data=bytearray(path.read_bytes())
    assert len(LOGO)==156 and len(data)>=192
    data[4:160]=LOGO
    data[160:172]=b'SIA2 V06'.ljust(12,b' ')
    data[172:176]=b'LS2L';data[176:178]=b'00'
    data[178]=0x96;data[179:189]=bytes(10)
    data[189]=(-sum(data[160:189])-0x19)&255
    data[190:192]=bytes(2)
    data.extend(bytes((-len(data))%4))
    path.write_bytes(data)
    assert (sum(data[160:190])+0x19)&255==0
    print(f'Header verified: {len(data)} bytes')
if __name__=='__main__':fix(Path(sys.argv[1]))
