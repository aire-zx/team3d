"""Extract reference crops from the component manifest. Requires Pillow."""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from PIL import Image, ImageChops, ImageOps
from team3d_manifest import load_components


INDEX = ".team3d-crops.json"
CROP_NAME = re.compile(r"[a-z0-9][a-z0-9_-]*-[0-9]{2,}\.png")


@contextmanager
def output_lock(directory):
    # Keep the lock file stable. The OS releases the lock if the process exits.
    with (directory / ".team3d-crops.lock").open("a+b") as lock:
        if os.name == "nt":
            import msvcrt
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def render_crop(crop, base):
    if not isinstance(crop, dict) or not isinstance(crop.get("source"), str):
        raise ValueError("expected a crop with a source image")
    box = crop.get("box")
    if not isinstance(box, list) or len(box) != 4 or any(type(n) is not int for n in box):
        raise ValueError("box must contain four integer pixel coordinates")
    with Image.open(base / crop["source"]) as original:
        source = ImageOps.exif_transpose(original)
        left, top, right, bottom = box
        if not (0 <= left < right <= source.width and 0 <= top < bottom <= source.height):
            raise ValueError(f"box {box} falls outside the oriented image {source.size} or is empty")
        result = source.crop(box).convert("RGBA")
        if "mask" in crop:
            if not isinstance(crop["mask"], str):
                raise ValueError("mask must be an image path")
            with Image.open(base / crop["mask"]) as original_mask:
                mask = ImageOps.exif_transpose(original_mask)
                if mask.size != source.size or mask.mode not in ("1", "L"):
                    raise ValueError("mask must be a full-size oriented binary or grayscale image")
                result.putalpha(ImageChops.multiply(result.getchannel("A"), mask.crop(box).convert("L")))
        return result


def publish(stage, output, names):
    index = output / INDEX
    previous = json.loads(index.read_text(encoding="utf-8")) if index.exists() else []
    if not isinstance(previous, list) or any(not isinstance(n, str) or not CROP_NAME.fullmatch(n) for n in previous):
        raise ValueError("Invalid crop ownership index. Choose a fresh output directory.")
    previous = set(previous)
    for entry in output.iterdir():
        untracked = entry.name not in previous
        legacy_crop = not index.exists() and CROP_NAME.fullmatch(entry.name.lower())
        if untracked and (legacy_crop or entry.name.lower() in names):
            raise ValueError(f"Untracked crop {entry.name!r}. Choose a fresh output directory.")
    backup = stage / "previous"
    backup.mkdir()
    touched = []
    try:
        for name in sorted(previous | names):
            dst = output / name
            if dst.is_symlink() or (dst.exists() and not dst.is_file()):
                raise ValueError(f"Expected a regular crop file at {dst}")
            if dst.exists():
                shutil.copy2(dst, backup / name)
            if name in names:
                (stage / name).replace(dst)
            elif dst.exists():
                dst.unlink()
            touched.append(name)
        new_index = stage / INDEX
        new_index.write_text(json.dumps(sorted(names)) + "\n", encoding="utf-8")
        new_index.replace(index)
    except BaseException:
        for name in reversed(touched):
            if (backup / name).exists():
                (backup / name).replace(output / name)
            else:
                (output / name).unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        components = load_components(args.manifest)
        args.output.mkdir(parents=True, exist_ok=True)
        with output_lock(args.output), tempfile.TemporaryDirectory(dir=args.output) as tmp:
            stage = Path(tmp)
            names = set()
            for component in components:
                identifier = component["id"]
                crops = component.get("crops", [])
                if not isinstance(crops, list):
                    raise ValueError(f"{identifier}: crops must be an array.")
                for index, crop in enumerate(crops, 1):
                    name = f"{identifier}-{index:02d}.png"
                    try:
                        render_crop(crop, args.manifest.parent).save(stage / name)
                    except (OSError, ValueError, Image.DecompressionBombError) as exc:
                        raise ValueError(f"{identifier} view {index}: {exc}") from exc
                    names.add(name)
            publish(stage, args.output, names)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
