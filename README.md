# MPATE-UE-1113 Coursework

My personal work for NYU's *Music Technology* course (Spring 2026). Python-based audio analysis, music information retrieval, and clustering — built around `librosa`, `music21`, `numpy`, and `scikit-learn`.

## Contents

- **`labs/`** — Lab notebooks
  - `01-python-basics` · `02-hello` · `03-leap-year` — warm-ups
  - `04-sine-wave` · `05-sine-square-saw` · `06-play-audio` — synthesis & playback
  - `07-librosa-tempo` — tempo / beat tracking with librosa
- **`assignments/`** — Five graded assignments
  - `01-written-1+2` — written responses
  - `02-librosa` — audio feature extraction
  - `03-clustering` — clustering songs by audio features
  - `04-playlisting` — playlist generation
  - `05-project-2` — final project
- **`demos/`** — Side explorations (drum clustering, music21 analysis)
- **`notes/`** — Personal study notes (sine-wave fundamentals)
- **`misc/`** — Tempo-extraction tutorial I wrote up while reviewing for an assignment

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install jupyter librosa music21 numpy scikit-learn matplotlib
jupyter lab
```

## Note on course materials

This repo contains only my own work. Course materials authored by the instructor (lecture slides, assigned readings, lab handouts) are not included and are not redistributable.
