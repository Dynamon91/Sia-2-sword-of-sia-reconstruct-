"""Remove recording banner from embedded stills without shifting observed pixels.
Run ONCE after unpack_assets.py on v0.6 bytes, never on an already-cleaned file.
Covered banner/avatar pixels are estimates, not recovered original art.
"""
from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def clean_frame(im):
    if im.size != (240,160):
        raise ValueError('Expected a native 240x160 frontend still')
    im=im.copy()
    # The round recording avatar covers part of the first clear game rows.
    avatar=im.crop((209,30,240,31)).resize((31,18),Image.Resampling.NEAREST)
    im.paste(avatar,(209,12))
    # Reconstruct only the obscured top 12 rows. Keep the observed 148 rows
    # at their original y coordinates instead of stretching them vertically.
    first_clear=im.crop((0,12,240,13)).resize((240,12),Image.Resampling.NEAREST)
    im.paste(first_clear,(0,0))
    return im
def main():
    p=ROOT/'assets/visuals.bin';raw=p.read_bytes();stride=38912
    report=ROOT/'assets/frontend_cleanup.json'
    if report.exists() and json.loads(report.read_text()).get('output_sha256')==hashlib.sha256(raw).hexdigest():
        print('Frontend already cleaned');raise SystemExit(0)
    archive=json.loads((ROOT/'assets/embedded_assets.json').read_text())
    expected=next(a['sha256'] for a in archive['assets'] if a['path']=='assets/visuals.bin')
    assert hashlib.sha256(raw).hexdigest()==expected, 'Restore original assets before cleanup'
    raw=raw[:9*stride]
    assert len(raw)==9*stride
    clean=bytearray()
    for i in range(9):
        frame=raw[i*stride:(i+1)*stride];palette=frame[:512]
        im=Image.frombytes('L',(240,160),frame[512:])
        im=clean_frame(im)
        clean.extend(palette+im.tobytes())
    p.write_bytes(clean)
    (ROOT/'assets/frontend_cleanup.json').write_text(json.dumps({
        'banner_removed_rows':12,
        'recording_avatar_removed_rect':[209,12,31,18],
        'occluded_pixels':'estimated from the first clear row; NOT original recovered art',
        'resampling':'none for observed rows 12:160; obscured top 12 rows extended from first clear row',
        'native_dimensions':[240,160],
        'intro_playback_removed':True,
        'output_sha256':hashlib.sha256(clean).hexdigest()},indent=2))
    print('PASS frontend cleanup: no banner/avatar, native 240x160 geometry, observed rows preserved')
if __name__=='__main__':main()
