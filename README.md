# MPATE-UE-1113 Final Project — Does AI-Generated Cantopop Respect Cantonese Tone?
by Candy Xie

A tone-tune mapping audit comparing **human-sung Cantopop** against **Suno-generated Cantopop** to test whether AI music generation respects Cantonese's six-tone system.

## Question

Cantonese is a tone language: pitch direction between adjacent syllables has to roughly match the lexical tonal direction, or the lyric becomes unintelligible. Wong & Diehl (2002) showed human Cantopop respects this rule **75–92%** of the time. **Does Suno?**

## Method

1. **Citation tones** — for each lyric snippet, look up every character's tone (1–6) in Words.hk and reduce to a 3-level target (High / Mid / Low) following Wong & Diehl.
2. **F0 extraction** — segment each audio snippet into syllables, then use [Parselmouth](https://parselmouth.readthedocs.io/) (Python wrapper for Praat) to extract the fundamental frequency per syllable.
3. **Direction comparison** — for every adjacent syllable pair, compare *expected* tonal direction against *actual* F0 direction. Count violations.
4. **Validate** — confirm the human songs land in Wong & Diehl's 75–92% band, then read off Suno's number against the same baseline.

## Dataset

Three human/Suno pairs matched by tempo:

| Tempo    | Human (track)              | Suno (generated)        |
| -------- | -------------------------- | ----------------------- |
| Ballad   | 高山低谷 (Phil Lam)        | 玻璃                    |
| Mid      | 隔離 (Jace Chan)           | 雨窗一封                |
| Uptempo  | 紅日 (Hacken Lee)          | 旺角快車                |

Audio in `assignments/05-project-2/audio/`.

## Files

- `assignments/06-final-project/cantonese_tone_audit.py` — core framework: tone mapping, F0 extraction, violation counting
- `assignments/06-final-project/audit_driver.py` — runs the audit across all 6 tracks, emits the comparison figure
- `assignments/06-final-project/audio/` — 3 human + 3 Suno mp3s
- `assignments/06-final-project/figures/human_vs_suno.png` — bar chart of match rate vs Wong & Diehl baseline

## Run

```bash
pip install parselmouth librosa numpy matplotlib
python assignments/06-final-project/audit_driver.py
```

Output: `figures/human_vs_suno.png` plus a per-pair violation table to stdout.

## Findings (TL;DR)

Human tracks fall inside the 75–92% baseline band, validating the method. Suno's match rate is meaningfully lower — gap is largest in uptempo where fast melodic motion overrides tonal targets. Concrete failures and discussion in the project video.

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
