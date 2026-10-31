"""Convert actual emulator PPM captures to enlarged PNGs without interpolation."""
import argparse
from pathlib import Path
from PIL import Image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    captures = sorted(args.directory.glob("*.ppm"))
    if not captures:
        raise SystemExit("No emulator captures found; refusing to publish empty previews")
    for path in captures:
        with Image.open(path) as image:
            if image.size != (240, 160):
                raise SystemExit("Unexpected GBA capture size: " + path.name)
            image.resize((720, 480), Image.Resampling.NEAREST).save(path.with_suffix(".png"))
    print("Exported", len(captures), "actual emulator screenshots")

if __name__ == "__main__":
    main()
