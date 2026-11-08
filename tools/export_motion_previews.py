"""Export continuous native emulator captures with a lossless shared palette.

GIF timing has 10 ms precision: round cumulative GBA frame time, preserving
every captured display frame. No interpolation or hand-composited gameplay.
"""
from pathlib import Path
import argparse
import hashlib
import json
import io
import os

import numpy as np
from PIL import Image


def export(build, name, out, scale=2):
    source = build / f'{name}_sequence'
    count = int((source / 'frame_count.txt').read_text())
    frames = [Image.open(source / f'frame_{i:03}.ppm').convert('RGB') for i in range(count)]
    assert count > 30 and all(im.size == (240, 160) for im in frames)
    colors = sorted({rgb for im in frames for _, rgb in im.getcolors(65536)})
    assert len(colors) <= 256, 'Native sequence needs more than one GIF palette'
    palette = [v for rgb in colors for v in rgb] + [0] * (768 - 3 * len(colors))
    codes = np.array([r*65536+g*256+b for r,g,b in colors], dtype='uint32')
    encoded = []
    size=(240*scale,160*scale)
    for frame in frames:
        rgb = np.asarray(frame).astype('uint32')
        indices = np.searchsorted(codes, rgb[:,:,0]*65536+rgb[:,:,1]*256+rgb[:,:,2]).astype('uint8')
        im = Image.frombytes('P', (240,160), indices.tobytes());im.putpalette(palette)
        encoded.append(im.resize(size, Image.Resampling.NEAREST))
    # GBA: 16,777,216 Hz / 280,896 cycles per display frame.
    times = [round(i * 280896 / 16777216 * 100) * 10 for i in range(count + 1)]
    durations = [b-a for a,b in zip(times,times[1:])]
    target = out / f'{name}_gameplay.gif'
    output = io.BytesIO()
    encoded[0].save(output, format='GIF', save_all=True, append_images=encoded[1:], loop=0,
                    duration=durations, optimize=False, disposal=1)
    payload = output.getvalue()
    temporary = target.with_suffix('.gif.tmp')
    with temporary.open('wb') as stream:
        view = memoryview(payload)
        while view:
            written = stream.write(view[:65536])
            if not written:raise OSError('Incomplete GIF write')
            view = view[written:]
        stream.flush();os.fsync(stream.fileno())
    temporary.replace(target)
    assert target.read_bytes() == payload, 'Incomplete GIF on disk'
    # GIF may coalesce identical frames. Verify every decoded interval against
    # its corresponding native source, including exact RGB and total duration.
    gif = Image.open(target);offset=0
    for i in range(gif.n_frames):
        gif.seek(i);duration=gif.info['duration']
        actual = np.asarray(gif.convert('RGB'))
        while duration > 0:
            assert offset < count, 'GIF outlasts captured source'
            expected = np.asarray(frames[offset].resize(size,Image.Resampling.NEAREST))
            assert np.array_equal(actual,expected), f'Changed source pixels at frame {offset}'
            duration -= durations[offset];offset += 1
        assert duration == 0
    assert offset == count
    report = {'rom_sha256':hashlib.sha256((build/'sia2_lab.gba').read_bytes()).hexdigest(),
              'native_frames':count,'gif_frames':gif.n_frames,'duration_ms':times[-1],
              'gif_sha256':hashlib.sha256(payload).hexdigest(),'gif_bytes':len(payload),
              'source_resolution':[240,160],'preview_resolution':list(size),
              'palette_colors':len(colors),'all_source_pixels_preserved':True,
              'interpolated':False,'timing':'Cumulative native GBA time rounded to GIF 10 ms units'}
    (out/f'{name}_preview.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS {name} preview: {count} continuous native frames, exact RGB, {times[-1]} ms')


def main():
    p=argparse.ArgumentParser();p.add_argument('build',type=Path);p.add_argument('--out',type=Path,default=Path('previews'));p.add_argument('--scale',type=int,choices=[1,2,3],default=2);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    for name in ['jump','ledge','scenery','continuation','bridge_run']:export(a.build,name,a.out,a.scale)


if __name__=='__main__':main()
