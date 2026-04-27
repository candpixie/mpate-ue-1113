# MPATE-UE-1113 Final Project — Does AI-Generated Cantopop Respect Cantonese Tone?
by Candy Xie

A tone-tune mapping audit comparing human-sung Cantopop against Suno-generated Cantopop to test whether AI music generation respects Cantonese's six-tone system.

## Question

Cantonese is a tonal language in which the pitch direction between adjacent syllables has to roughly match the lexical tonal direction, or the lyric becomes unintelligible. Wong & Diehl (2002) showed human Cantopop respects this rule **75–92%** of the time. **What about for Suno?**

## Method

1. **Citation tones**: for each lyric snippet, look up every character's tone (1–6) in Words.hk and reduce to a 3-level target (High / Mid / Low) following Wong & Diehl.
2. **F0 extraction**: segment each audio snippet into syllables, then use [Parselmouth](https://parselmouth.readthedocs.io/) (Python wrapper for Praat) to extract the fundamental frequency per syllable.
3. **Direction comparison**: for every adjacent syllable pair, compare *expected* tonal direction against *actual* F0 direction. Count violations.
4. **Validate**: confirm the human songs land in Wong & Diehl's 75–92% band, then read off Suno's number against the same baseline.

## Dataset

Three human/Suno pairs matched by tempo. Audio in `assignments/06-final-project/audio/`.

| Tempo    | Human (track, artist)              | Suno (generated, V5.5)              |
| -------- | ---------------------------------- | ----------------------------------- |
| Mid      | 隔離 — Jace Chan (2023)            | 玻璃                                  |
| Ballad   | 高山低谷 — Phil Lam 林奕匡 (2014)  | 雨窗一封                                |
| Uptempo  | 紅日 — Hacken Lee 李克勤 (1992)    | 旺角快車                               |


## Files

- `assignments/06-final-project/cantonese_tone_audit.py` — core framework: tone mapping, F0 extraction, violation counting
- `assignments/06-final-project/audit_driver.py` — runs the audit across all 6 tracks, emits the comparison figure
- `assignments/06-final-project/audio/` — 3 human + 3 Suno mp3s
- `assignments/06-final-project/figures/human_vs_suno.png` — bar chart of match rate vs Wong & Diehl baseline

## Run

```bash
pip install praat-parselmouth librosa numpy pandas matplotlib
cd assignments/06-final-project
python audit_driver.py
```

Outputs:
- `figures/human_vs_suno.png` — bar chart of match rate per tempo bucket vs the Wong & Diehl baseline band
- per-snippet expected-direction tables and pair-by-pair violation reports to stdout
- top Suno violations grouped by track (b-roll material for the project video)

The CJK glyphs in matplotlib labels rely on a system CJK font (PingFang / Heiti / Hiragino — preinstalled on macOS). On Linux, install `fonts-noto-cjk` and add `'Noto Sans CJK TC'` to `matplotlib.rcParams['font.family']` near the top of `audit_driver.py`.

## Findings

See `figures/human_vs_suno.png` and the violation tables in the audit's stdout. Discussion and concrete failure pairs are walked through in the accompanying video.

---

# MPATE-UE-1113 Coursework

My personal work for NYU's *Music, Mind and Artificial Intelligence* course (Spring 2026). Python-based audio analysis, music information retrieval, and clustering — built around `librosa`, `music21`, `numpy`, and `scikit-learn`.

## Contents

- **`labs/`** — Lab notebooks
  - `01-python-basics` · `02-hello` · `03-leap-year` — warm-ups
  - `04-sine-wave` · `05-sine-square-saw` · `06-play-audio` — synthesis & playback
  - `07-librosa-tempo` — tempo / beat tracking with librosa
- **`assignments/`** — Graded assignments
  - `01-written-1+2` — written responses
  - `02-librosa` — audio feature extraction
  - `03-clustering` — clustering songs by audio features
  - `04-playlisting` — playlist generation
  - `05-project-2` — project 2
  - `06-final-project` — final project (Cantonese tone audit, see top of README)
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
