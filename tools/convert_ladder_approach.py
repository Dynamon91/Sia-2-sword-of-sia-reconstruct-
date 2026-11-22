"""Two registered lower-route views; upper-route assets use convert_ladder_climb.py."""
from pathlib import Path
import argparse
import hashlib
import io
import json

import numpy as np
from PIL import Image

from audit_route_continuation import match
from convert_bridge_run import sky_fill
from repair_sprite_edges import indexed

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'reference/w1l1_ladder'


def foreground(rgb):
    a = rgb.astype(np.int16)
    r, g, b = a.transpose(2, 0, 1)
    warm = (r > b + 8) & (g > b + 3)
    neutral = (r >= b - 16) & (g >= b - 25) & (a.mean(axis=2) < 190)
    # Filling enclosed components would also copy clouds trapped between the
    # ladder rails and the wall, although those clouds move independently.
    return warm | neutral


def registration(source, target, boxes, expected, margin):
    patches = [match(source.astype(np.int16), target.astype(np.int16), box, 0) for box in boxes]
    assert all(p['delta'] == expected and p['mae_rgb'] < 5 and
               p['runner_up_mae_rgb'] - p['mae_rgb'] > margin for p in patches), patches
    return {'delta': expected, 'minimum_margin_rgb': margin, 'patches': patches}


def png(rgb):
    stream = io.BytesIO()
    Image.fromarray(rgb).save(stream, format='PNG')
    return stream.getvalue()


def outputs():
    paths = [ROOT / 'reference/w1l1_lower_landing/186_1.png'] + [
        REF / f'{t}.png' for t in ['187_5', '189_8', '190_5', '190_75', '191']]
    paths.append(ROOT/'reference/w1l1_ladder_climb/189_0.png')
    old, hall, clear, shaft, higher, top, early = [np.asarray(Image.open(p).convert('RGB')) for p in paths]
    regs = [
        registration(old, hall, [(3, 64, 15, 73), (2, 73, 18, 87)], [92, 0], 2),
        registration(hall, shaft, [(70, 59, 86, 77), (88, 59, 104, 77)], [116, 57], 2),
        registration(shaft, clear, [(130, 42, 140, 56), (130, 63, 140, 77)], [-14, -13], 2),
        registration(shaft, higher, [(140, 20, 149, 30), (175, 18, 183, 27)], [-18, 36], 3),
        registration(shaft, top, [(140, 20, 149, 30), (175, 18, 183, 27)], [-30, 60], 3),
        registration(shaft, early, [(130,42,140,56),(130,63,140,77)], [-38,-12], 1.5),
    ]
    palette = (ROOT / 'assets/continuation_palette.bin').read_bytes()
    words = np.frombuffer(palette, dtype='<u2')
    colors = np.array([[(int(w) >> shift & 31) * 255 // 31 for shift in (0, 5, 10)]
                       for w in words], dtype=np.uint8)
    result = {}
    reports = []
    frames = [old, hall, clear, shaft, higher, top, early]
    shifts = [(-92, 0), (0, 0), (102, 44), (116, 57), (98, 93), (86, 117), (78,45)]
    actors = [[(142, 37, 50, 28)], [(30, 14, 42, 54), (128, 14, 60, 58)],
              [(155, 60, 42, 58), (102, 87, 55, 22)], [(142, 64, 42, 47), (102, 14, 22, 6)],
              [(130, 73, 32, 53), (97, 14, 27, 40)], [(77, 28, 49, 62), (111, 96, 43, 58)],
              [(108,54,40,60),(147,58,45,62)]]
    usable = []
    for frame, boxes in zip(frames, actors):
        valid = np.ones((160, 240), bool)
        valid[:14] = False
        valid[13:45, 204:240] = False
        for x, y, w, h in boxes:
            valid[y:y+h, x:x+w] = False
        usable.append(valid & foreground(frame))
    for name, original in [('ladder_hall', hall), ('ladder_foot', shaft)]:
        a = original.copy()
        estimated = np.zeros((160, 240), bool)
        recovered = estimated.copy()
        # The title and avatar hide the same native rectangles in each capture.
        estimated[:14] = True
        estimated[13:45, 204:240] = True
        target = 1 if name == 'ladder_hall' else 3
        for x, y, w, h in actors[target]:
            estimated[y:y+h, x:x+w] = True
        repair = estimated.copy()
        yy, xx = np.indices((160, 240))
        # Foreground can be transferred between registered exposures. Actor and
        # recording rectangles in the donor are always excluded. Parallax sky
        # is never pasted as a rectangular donor patch.
        for donor in [6, 5, 0, 2, 4, 3, 1]:
            if donor == target:
                continue
            dx = shifts[donor][0] - shifts[target][0]
            dy = shifts[donor][1] - shifts[target][1]
            sx, sy = xx + dx, yy + dy
            inside = (sx >= 0) & (sx < 240) & (sy >= 0) & (sy < 160)
            sx, sy = sx.clip(0, 239), sy.clip(0, 159)
            take = repair & ~recovered & inside & usable[donor][sy, sx]
            a[take] = frames[donor][sy[take], sx[take]]
            recovered[take] = True
        if target == 1:
            # The purple walkway is neutral foreground, not an actor-shaped
            # sky hole. Its whole registered surface is clear in the old view.
            a[55:72, 128:188] = old[55:72, 36:96]
            recovered[55:72, 128:188] = True
        # A small right-hand rail fragment is hidden by Sia in both useful
        # exposures. Repeat two observed 11-pixel rung intervals only there.
        dx = shifts[2][0] - shifts[target][0]
        dy = shifts[2][1] - shifts[target][1] - 22
        sx, sy = xx + dx, yy + dy
        rail = ((xx >= (37 if target == 1 else 153)) &
                (xx < (62 if target == 1 else 178)))
        inside = (sx >= 0) & (sx < 240) & (sy >= 0) & (sy < 160)
        sx, sy = sx.clip(0, 239), sy.clip(0, 159)
        repeated = repair & ~recovered & rail & inside & usable[2][sy, sx]
        a[repeated] = clear[sy[repeated], sx[repeated]]
        estimated &= ~recovered
        strip, sky_bottom, origin = ((190, 202), 50, [-698, 204]) if target == 1 else ((185, 200), 105, [-582, 261])
        # Remaining foreground in the recording-covered header is an edge
        # estimate. Recovered header pixels already came from visible donors.
        header_terrain = foreground(a[14:15])[0]
        header_terrain[204:] = False  # row 14 is still hidden by the avatar here
        header_missing = estimated[:14] & header_terrain[None, :]
        a[:14][header_missing] = np.broadcast_to(a[14:15], a[:14].shape)[header_missing]
        sky_holes = estimated.copy()
        sky_holes[:14][header_missing] = False
        sky_holes[repeated] = False
        a[sky_holes & (yy < 14)] = np.median(a[14, strip[0]:strip[1]], axis=0).astype(np.uint8)
        sky_work = a.copy()
        floor = 55 if target == 1 else 112
        sky_work[floor:] = np.median(a[sky_bottom, strip[0]:strip[1]], axis=0).astype(np.uint8)
        sky_fill(sky_work, sky_holes, strip, sky_bottom)
        a[sky_holes] = sky_work[sky_holes]
        if target == 3:
            # The upper guard's clipped foot is not scenery. No exposure shows
            # this tiny corner clear: interpolate its ground colors laterally.
            for y in range(20):
                for x in range(102, 124):
                    if estimated[y, x]:
                        a[y, x] = np.rint(a[y, 101].astype(float) * (124-x)/23 +
                                         a[y, 124].astype(float) * (x-101)/23).astype(np.uint8)
        assert np.array_equal(a[~(estimated | recovered)], original[~(estimated | recovered)])
        indices = indexed(Image.fromarray(a), palette)
        assert indices.min() >= 1 and indices.max() < 240
        result[name + '_background.bin'] = palette + indices.tobytes()
        result[name + '_background.png'] = png(a)
        result[name + '_background_preview.png'] = png(colors[indices].repeat(3, 0).repeat(3, 1))
        result[name + '_repair_mask.png'] = png((estimated.astype(np.uint8) * 255))
        reports.append({'name': name, 'origin': origin, 'observed_rgb_pixels_unchanged': int((~repair).sum()),
                        'registered_replacement_pixels': int(recovered.sum()),
                        'estimated_pixels': int(estimated.sum()), 'estimated_repeated_rail_pixels': int(repeated.sum()),
                        'collision_geometry': 'provisional'})
    manifest = {'video_sha256': '7773b43f66bb03375dc18d33e9d6bcbb57a9e7869f5afe7cc1824228ddf06d51',
                'source_seconds': [186.1, 187.5, 189.8, 190.5, 190.75, 191,189.0],
                'sources': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                'registrations': regs, 'views': reports,
                'limits': ['Compressed video palette; shared nearest-color GBA palette without dithering',
                           'Actor rectangles are excluded in all donors; hidden sky/header and a repeated rail fragment remain estimates',
                           'Single existing guard pose, patrol, timing and collision geometry remain provisional',
                           'These are lower approach assets; upper-route gameplay is described in ladder_climb_manifest.json']}
    result['ladder_approach_manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, payload in outputs().items():
        path = ROOT / 'assets' / name
        if args.check:
            if name.endswith('.png'):
                assert Image.open(path).tobytes() == Image.open(io.BytesIO(payload)).tobytes(), name
            else:
                assert path.read_bytes() == payload, name
        else:
            path.write_bytes(payload)
    print('PASS ladder approach assets: six independent terrain registrations, two cleaned views and explicit repair masks')


if __name__ == '__main__':
    main()
