"""Tests for scripts/organize_dataset.py, using tiny synthetic PNG stand-ins
in place of the real (multi-GB, auth-gated) Kaggle dataset."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from organize_dataset import (  # noqa: E402
    DatasetOrganizeError,
    UnmatchedPairError,
    find_pairs,
    organize_dataset,
)


def _make_raw_dataset(tmp_path: Path, image_names: list[str], mask_names: list[str]) -> Path:
    raw = tmp_path / "raw" / "demo-dataset"
    (raw / "images").mkdir(parents=True)
    (raw / "masks").mkdir(parents=True)
    for name in image_names:
        (raw / "images" / name).write_bytes(b"fake-png-image")
    for name in mask_names:
        (raw / "masks" / name).write_bytes(b"fake-png-mask")
    return raw


def test_find_pairs_matches_by_stem(tmp_path):
    raw = _make_raw_dataset(tmp_path, ["a.png", "b.png"], ["a.png", "b.png"])
    pairs = find_pairs(raw / "images", raw / "masks")
    assert [p[0].stem for p in pairs] == ["a", "b"]


def test_find_pairs_raises_on_unmatched_image(tmp_path):
    raw = _make_raw_dataset(tmp_path, ["a.png", "b.png"], ["a.png"])
    with pytest.raises(UnmatchedPairError):
        find_pairs(raw / "images", raw / "masks")


def test_find_pairs_raises_on_unmatched_mask(tmp_path):
    raw = _make_raw_dataset(tmp_path, ["a.png"], ["a.png", "extra.png"])
    with pytest.raises(UnmatchedPairError):
        find_pairs(raw / "images", raw / "masks")


def test_find_pairs_raises_on_missing_directory(tmp_path):
    with pytest.raises(DatasetOrganizeError):
        find_pairs(tmp_path / "nope" / "images", tmp_path / "nope" / "masks")


def test_organize_dataset_copies_matched_pairs(tmp_path):
    raw = _make_raw_dataset(tmp_path, ["a.png", "b.png"], ["a.png", "b.png"])
    processed = tmp_path / "processed"
    count = organize_dataset(raw, processed)
    assert count == 2
    assert (processed / "images" / "a.png").read_bytes() == b"fake-png-image"
    assert (processed / "masks" / "a.png").read_bytes() == b"fake-png-mask"


def test_organize_dataset_is_atomic_on_failure(tmp_path):
    """A raw dir with a mismatch must not leave a partial processed/ dir."""
    raw = _make_raw_dataset(tmp_path, ["a.png", "b.png"], ["a.png"])
    processed = tmp_path / "processed"
    with pytest.raises(UnmatchedPairError):
        organize_dataset(raw, processed)
    assert not processed.exists()


def test_organize_dataset_replaces_existing_processed_dir(tmp_path):
    raw = _make_raw_dataset(tmp_path, ["a.png"], ["a.png"])
    processed = tmp_path / "processed"
    processed.mkdir()
    (processed / "stale.txt").write_text("old run")

    organize_dataset(raw, processed)

    assert not (processed / "stale.txt").exists()
    assert (processed / "images" / "a.png").exists()
