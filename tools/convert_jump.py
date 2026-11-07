"""Three observed airborne poses, traced from W1L1 without scaling the sprite.

With --video, repeat the reference extraction. Without it, rebuild the indexed
buffer from the checked-in transparent PNGs; CI does not need the source video.
"""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion, label

from convert_room import extract
from repair_sprite_edges import indexed

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT, ANCHOR_X = 56, 56, 28
POSES = [
    {"state": "rise", "seconds": 120.08, "anchor": [71, 118],
     "outline": [(70,74),(73,74),(75,75),(77,77),(77,81),(76,82),(76,85),
                 (77,86),(77,89),(79,89),(79,91),(81,91),(81,93),(82,93),
                 (82,97),(80,98),(78,97),(78,94),(77,94),(77,99),(76,103),
                 (74,106),(72,108),(72,111),(73,113),(72,116),(70,117),
                 (65,117),(63,115),(63,110),(62,109),(62,107),(64,105),
                 (66,104),(67,100),(66,99),(64,100),(61,100),(60,103),
                 (59,104),(58,108),(56,111),(56,113),(54,114),(54,110),
                 (54,107),(55,106),(55,104),(57,102),(58,99),(60,98),
                 (58,97),(58,96),(60,95),(60,93),(62,91),(62,90),
                 (61,89),(59,88),(58,86),(57,85),(58,84),(58,81),
                 (60,79),(61,77),(63,77),(64,76),(66,75),(69,75)],
     "holes": [[(64,90),(67,91),(68,94),(67,95),(65,95),(64,93)],
               [(61,104),(65,103),(65,104),(63,106),(61,106)]],
     "background_runs": [[97,82,82]]},
    {"state": "apex", "seconds": 120.32, "anchor": [85, 106],
     "outline": [(84,62),(89,62),(92,64),(93,66),(93,70),(92,71),
                 (92,73),(93,74),(93,77),(95,78),(96,80),(96,82),
                 (97,83),(97,86),(95,87),(94,86),(94,89),(92,90),
                 (91,92),(89,94),(88,96),(90,97),(90,100),(88,102),
                 (87,103),(87,105),(81,105),(80,104),(80,102),(79,101),
                 (80,98),(80,96),(81,94),(83,93),(84,90),(82,89),
                 (81,87),(80,85),(79,86),(79,88),(78,89),(79,90),
                 (79,91),(77,91),(76,90),(76,88),(74,89),(73,91),
                 (70,92),(67,94),(66,97),(63,97),(63,96),(64,94),
                 (65,92),(68,90),(71,89),(74,87),(74,85),(75,84),
                 (76,81),(76,79),(74,78),(73,76),(72,75),(72,73),
                 (72,70),(74,68),(75,66),(77,65),(80,65),(82,64),
                 (84,64)],
     "holes": [[(80,79),(82,80),(82,83),(81,84),(80,82)]],
     "background_runs": [[86,97,97],[89,94,94],[99,86,86],[99,90,90],
                         [100,86,90],[101,87,89],[102,88,88],[105,87,87]]},
    {"state": "fall", "seconds": 119.5, "anchor": [65, 114],
     "outline": [(57,67),(58,67),(58,68),(62,69),(64,71),(65,73),
                 (70,73),(72,75),(73,78),(73,80),(74,80),(74,81),
                 (73,83),(72,84),(72,86),(74,87),(75,88),(77,88),
                 (78,89),(80,89),(80,91),(78,92),(76,93),(73,93),
                 (71,91),(71,95),(70,97),(71,99),(73,101),(73,104),
                 (72,106),(72,109),(73,111),(73,113),(69,113),
                 (67,111),(67,107),(67,105),(66,104),(65,104),
                 (63,107),(64,109),(64,111),(61,111),(58,110),
                 (57,108),(56,107),(57,105),(57,102),(59,101),
                 (61,99),(61,97),(60,96),(60,93),(61,91),
                 (61,88),(60,87),(59,88),(58,88),(57,90),(56,92),
                 (54,93),(55,94),(55,95),(53,96),(52,94),(51,93),
                 (48,92),(47,92),(47,91),(49,90),(48,88),(47,86),
                 (46,85),(46,83),(44,82),(44,80),(42,79),(41,77),
                 (43,77),(44,78),(46,79),(47,80),(47,82),(49,83),
                 (49,85),(50,87),(52,88),(54,88),(55,86),(56,85),
                 (57,84),(59,83),(60,82),(60,80),(57,79),(54,78),
                 (53,76),(52,76),(53,73),(54,72),(54,70),(56,69)],
     "holes": [[(63,88),(63,91),(62,92),(61,91),(62,89)],
               [(68,92),(70,92),(70,95),(69,95)]],
     "background_runs": []},
]


def extract_pose(source, pose):
    cx, feet = pose["anchor"]
    left, top = cx - ANCHOR_X, feet - HEIGHT
    result = source.crop((left, top, left + WIDTH, feet)).convert("RGBA")
    alpha = Image.new("L", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(alpha)
    for points, fill in [(pose["outline"], 255)] + [(p, 0) for p in pose["holes"]]:
        draw.polygon([(x - left, y - top) for x, y in points], fill=fill)
    # Explicitly traced scenery between/along the boots, including gray rock
    # that cannot safely be removed with a global color key.
    for y, x1, x2 in pose["background_runs"]:
        draw.line((x1-left, y-top, x2-left, y-top), fill=0)
    rgba = np.array(result)
    r, g, b = rgba[:, :, :3].astype(int).transpose(2, 0, 1)
    # Only remove blue sky along the traced boundary. Preserve the white/black
    # sword pixels, dark outlines and interior armor highlights.
    sky = (r > 55) & (b > r + 15) & (g > r + 10) & (b > g + 6) & (b - g < 50)
    mask = np.asarray(alpha) > 0
    for _ in range(2):
        mask &= ~(sky & ~binary_erosion(mask, np.ones((3, 3))))
    components, _ = label(mask, np.ones((3, 3)))
    sizes = np.bincount(components.ravel())
    mask &= sizes[components] > 2
    rgba[~mask] = 0
    rgba[:, :, 3] = mask * 255
    return Image.fromarray(rgba)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path)
    args = parser.parse_args()
    assets = ROOT / "assets"
    header = (assets / "room.bin").read_bytes()[:512]
    if args.video:
        for i, pose in enumerate(POSES):
            im = extract_pose(extract(str(args.video), pose["seconds"]), pose)
            im.save(assets / f"jump_{i}.png")
        manifest = {"source_sha256": hashlib.sha256(args.video.read_bytes()).hexdigest(),
                    "size": [WIDTH, HEIGHT], "anchor": [ANCHOR_X, HEIGHT], "poses": POSES,
                    "limits": ["Hand-traced compressed video, not recovered original sprite sheets.",
                               "Source frames retain their native 240x160 proportions.",
                               "Velocity thresholds and collision box are reconstruction estimates."]}
        (assets / "jump_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    frames = []
    for i in range(len(POSES)):
        im = Image.open(assets / f"jump_{i}.png").convert("RGBA")
        assert im.size == (WIDTH, HEIGHT)
        frame = indexed(im, header)
        assert frame[-1].any(), "Boot must meet the declared anchor"
        assert not frame[0].any(), "Head clipped by canvas"
        assert not frame[:, 0].any() and not frame[:, -1].any(), "Sword clipped by canvas"
        assert frame.max() < 240
        frames.append(frame.tobytes())
    assert len(set(frames)) == 3
    (assets / "jump_cycle.bin").write_bytes(b"".join(frames))
    print("PASS jump conversion: three distinct poses; fixed foot anchor; transparent zero; opaque palette 1..239")


if __name__ == "__main__":
    main()
