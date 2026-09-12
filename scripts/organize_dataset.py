"""Organize a public chest X-ray segmentation dataset into a consistent layout.

Dataset: "Chest X-ray Masks and Labels" (Shenzhen + Montgomery sets, combined
and re-released with lung masks by Kaggle user nikhilpandey360), CC0-licensed
public data. See README.md section 8 "Dataset" for the download link and
manual-download steps — Kaggle requires an authenticated API key, so this
script does NOT fetch the archive itself; it organizes whatever has already
been downloaded and extracted into ``data/raw/``.

Expected raw layout (whatever the archive extracts to), one image directory
and one mask directory, matched by filename stem:

    data/raw/<dataset_name>/images/*.png
    data/raw/<dataset_name>/masks/*.png

Output layout (see docs/architecture.md "Dataset directory layout"):

    data/processed/images/<stem>.png
    data/processed/masks/<stem>.png

Every image must have a matching mask and vice versa; an unmatched file is a
loud error (``UnmatchedPairError``), not a silently-skipped file, since a
partial pairing would train on misaligned image/mask data without warning.

The copy is atomic per the portfolio's write-safety rule: files are copied
into a temporary sibling directory and the whole processed tree is published
via ``os.replace`` only once every pair has been verified and copied, so a
job killed partway through never leaves a half-populated ``data/processed/``
that a later run's ``.exists()`` check would mistake for "already done".
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


class DatasetOrganizeError(Exception):
    """Raised when the raw dataset directory is missing or malformed."""


class UnmatchedPairError(DatasetOrganizeError):
    """Raised when an image has no matching mask, or vice versa."""

    def __init__(self, images_only: set[str], masks_only: set[str]):
        self.images_only = images_only
        self.masks_only = masks_only
        parts = []
        if images_only:
            parts.append(f"{len(images_only)} image(s) with no mask: {sorted(images_only)[:5]}")
        if masks_only:
            parts.append(f"{len(masks_only)} mask(s) with no image: {sorted(masks_only)[:5]}")
        super().__init__("unmatched image/mask pairs — " + "; ".join(parts))


def _index_by_stem(directory: Path) -> dict[str, Path]:
    return {
        p.stem: p
        for p in sorted(directory.iterdir())
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    }


def find_pairs(images_dir: Path, masks_dir: Path) -> list[tuple[Path, Path]]:
    """Match images to masks by filename stem. Raises on any mismatch."""
    if not images_dir.is_dir():
        raise DatasetOrganizeError(f"images directory not found: {images_dir}")
    if not masks_dir.is_dir():
        raise DatasetOrganizeError(f"masks directory not found: {masks_dir}")

    images = _index_by_stem(images_dir)
    masks = _index_by_stem(masks_dir)
    if not images:
        raise DatasetOrganizeError(f"no image files found under {images_dir}")

    images_only = images.keys() - masks.keys()
    masks_only = masks.keys() - images.keys()
    if images_only or masks_only:
        raise UnmatchedPairError(images_only, masks_only)

    return [(images[stem], masks[stem]) for stem in sorted(images)]


def organize_dataset(raw_dir: Path, processed_dir: Path) -> int:
    """Copy matched image/mask pairs from ``raw_dir`` into ``processed_dir``.

    ``raw_dir`` must contain ``images/`` and ``masks/`` subdirectories.
    Returns the number of pairs organized. Writes atomically: nothing under
    ``processed_dir`` is visible until the full set of pairs has been copied
    and verified.
    """
    pairs = find_pairs(raw_dir / "images", raw_dir / "masks")

    processed_dir = Path(processed_dir)
    processed_dir.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(prefix=".processed-", dir=processed_dir.parent))
    try:
        (tmp_dir / "images").mkdir(parents=True)
        (tmp_dir / "masks").mkdir(parents=True)
        for image_path, mask_path in pairs:
            shutil.copy2(image_path, tmp_dir / "images" / image_path.name)
            shutil.copy2(mask_path, tmp_dir / "masks" / mask_path.name)

        if processed_dir.exists():
            shutil.rmtree(processed_dir)
        tmp_dir.replace(processed_dir)
    except BaseException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
    return len(pairs)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw/chest-xray-masks-and-labels"),
        help="Directory containing images/ and masks/ subdirectories",
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=Path("data/processed"),
        help="Destination directory for the organized dataset",
    )
    args = parser.parse_args(argv)

    try:
        count = organize_dataset(args.raw_dir, args.processed_dir)
    except DatasetOrganizeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        print(
            "See README.md section 8 'Dataset' for the manual download steps.",
            file=sys.stderr,
        )
        return 1

    print(f"organized {count} image/mask pair(s) into {args.processed_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
