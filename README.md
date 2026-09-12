# 2D X-Ray Segmentation

> Medical Imaging portfolio project — independent open-source implementation.
> This is an original, from-scratch build. It is not affiliated with, and does not
> contain any code, prompts, data, or business logic from, any employer or client.

![status](https://img.shields.io/badge/status-phase%201%20in%20progress-yellow)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

## 1. Problem

Segmenting structures (bones, organs, lesions) in 2D X-rays is a foundational medical imaging task useful for triage and measurement tools.

## 2. Architecture

```text
X-Ray Image -> Augmentation -> U-Net -> Dice Loss -> Overlay Visualization + Metrics
```

## 3. Technology Stack

- Python
- PyTorch
- OpenCV
- Albumentations

## 4. Feature List

- U-Net segmentation architecture
- Data augmentation
- Dice loss training
- Image overlay visualization
- Validation metrics (Dice/IoU)

## 5. Implementation Plan

1. Phase 1: Data pipeline with augmentation on public X-ray dataset
2. Phase 2: U-Net training with Dice loss
3. Phase 3: Evaluation and overlay visualization tooling

## Task Tracking

Work is broken into phase-tagged user stories tracked as GitHub Issues, not in this file. To see what's open:

    gh issue list --repo faheemkhaskheli9/xray-image-segmentation --state open --label type:user-story

Implement Phase 1 issues first (later phases depend on it). When you start one, add label `status:in-progress`. When you finish, close it referencing the commit (e.g. `git commit -m "... Closes #4"`) and push.

## 6. Repository Structure

```text
xray-image-segmentation/
├── README.md
├── LICENSE
├── .gitignore
├── pyproject.toml
├── .env.example
├── docker/
├── docs/
│   ├── architecture.md
│   └── evaluation.md
├── src/
├── tests/
├── configs/
├── scripts/
├── notebooks/
├── examples/
├── assets/
└── .github/
    └── workflows/
```

## 7. Setup

```bash
git clone <this-repo-url>
cd xray-image-segmentation
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # or: pip install -e .
cp .env.example .env              # fill in API keys / config
```

## 8. Dataset

**Chest X-ray Masks and Labels** — a combined, CC0-licensed re-release of the
Shenzhen and Montgomery County chest X-ray sets with paired lung segmentation
masks, published on Kaggle by `nikhilpandey360`:
<https://www.kaggle.com/datasets/nikhilpandey360/chest-xray-masks-and-labels>.

Manual download steps (Kaggle requires an authenticated API key, so this is
not scripted):

1. `pip install kaggle` and place your API token at `~/.kaggle/kaggle.json`
   (see Kaggle's API docs).
2. `kaggle datasets download -d nikhilpandey360/chest-xray-masks-and-labels -p data/raw --unzip`
3. Arrange the extracted images/masks under
   `data/raw/chest-xray-masks-and-labels/{images,masks}/`, matched by filename
   stem (see `docs/architecture.md` for the exact layout).
4. Run `python scripts/organize_dataset.py` to validate the pairing and copy
   it into `data/processed/`.

No proprietary, employer-owned, or client-identifiable data is used in this project.

## 9. Training / Execution

Document the commands used to run training, ingestion, or the main pipeline, e.g.:

```bash
python -m src.main --config configs/default.yaml
```

## 10. Evaluation

Document evaluation metrics and how to reproduce them here (see `docs/evaluation.md`).

## 11. Results

_To be filled in as the implementation progresses — screenshots, metrics tables, and
sample outputs go here._

## 12. API

_If this project exposes an API, document the main endpoints here (or link to
auto-generated OpenAPI docs, e.g. `/docs` for FastAPI)._

## 13. Docker

```bash
docker build -t xray-image-segmentation .
docker run -p 8000:8000 xray-image-segmentation
```

## 14. Tests

```bash
pytest tests/
```

## 15. Limitations

- This is a from-scratch, independent recreation built for portfolio purposes.
- Performance numbers, once added, are based on public datasets and are not
  representative of any production system's real-world results.

## 16. Future Work

- Expand evaluation coverage and add CI-based regression checks.
- Add more configuration presets and deployment targets.
- Track open items as GitHub Issues.

## 17. Disclosure

This repository is an **independent open-source recreation inspired by the kind of
production systems I have worked on professionally**. It contains no employer or
client source code, prompts, datasets, credentials, architecture diagrams, or
business logic. All code, data, and documentation here are original or built on
publicly available datasets and open-source tools.

---
_Last updated: 2026-08-18_
