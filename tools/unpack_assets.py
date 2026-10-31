"""Restore generated build assets embedded in the included ROM, without duplicating
large binary assets in the delivery ZIP. Validate all bytes before writing files.
"""
from pathlib import Path
import argparse,hashlib,json

def main():
    root=Path(__file__).resolve().parents[1]
    p=argparse.ArgumentParser();p.add_argument('rom',nargs='?',default=str(root/'Lady_Sia2_v06.gba'))
    args=p.parse_args();rom=Path(args.rom)
    if not rom.exists() and args.rom==str(root/'Lady_Sia2_v06.gba'):
        parts=[root/'rom-parts'/('Lady_Sia2_v06.gba.part'+str(i)) for i in range(4)]
        restored=b''.join(part.read_bytes() for part in parts)
        expected=json.loads((root/'assets/embedded_assets.json').read_text())['rom_sha256']
        if hashlib.sha256(restored).hexdigest()!=expected:
            raise SystemExit('ROM parts integrity check failed')
        rom.write_bytes(restored)
    data=rom.read_bytes()
    manifest=json.loads((root/'assets/embedded_assets.json').read_text())
    if hashlib.sha256(data).hexdigest()!=manifest['rom_sha256']:
        raise SystemExit('ROM hash mismatch: use the unchanged v0.6 ROM included in this package.')
    validated=[]
    for item in manifest['assets']:
        target=(root/item['path']).resolve()
        if target.parent!=(root/'assets').resolve():raise SystemExit('Invalid asset path')
        content=data[item['offset']:item['offset']+item['length']]
        if len(content)!=item['length'] or hashlib.sha256(content).hexdigest()!=item['sha256']:
            raise SystemExit('Asset integrity check failed: '+item['path'])
        validated.append((target,content))
    for target,content in validated:
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content)
    print('Verified and restored',len(validated),'assets from the included ROM.')
if __name__=='__main__':main()
