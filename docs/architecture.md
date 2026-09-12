# Architecture Notes: 2D X-Ray Segmentation

## Pipeline

```text
X-Ray Image -> Augmentation -> U-Net -> Dice Loss -> Overlay Visualization + Metrics
```

## Components

- U-Net segmentation architecture
- Data augmentation
- Dice loss training
- Image overlay visualization
- Validation metrics (Dice/IoU)

## Dataset directory layout

Raw download (manually placed per README §8):

```text
data/raw/chest-xray-masks-and-labels/
├── images/   # <stem>.png source X-rays
└── masks/    # <stem>.png lung masks, one per image, same stem
```

Organized output of `scripts/organize_dataset.py` (only ever written
atomically — a failed/partial run never leaves this directory half-populated):

```text
data/processed/
├── images/<stem>.png
└── masks/<stem>.png
```

Every image must have a mask with the same filename stem and vice versa;
`organize_dataset.py` raises `UnmatchedPairError` rather than silently
dropping unmatched files, since training on a misaligned pairing would fail
silently otherwise.

## Design Notes

- Keep provider/model choices swappable behind interfaces (see `multi-llm-router`
  and similar projects in this portfolio for the general pattern).
- Prefer configuration-driven pipelines (YAML/JSON in `configs/`) over hardcoded
  parameters so experiments are reproducible.
