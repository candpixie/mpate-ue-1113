# Video Plan — Cantonese Tone Audit (3.5 min)

**Format.** 3:30 hard cap. Talking head + screen-record + audio clips.
Course brief asks for **technology used, goal, how well you realized it.**
This plan hits all three, but the *framing* is now: "the audit numbers
are not the whole story — what's missing from them is the project."

---

## Framing — the project's actual claim

The original frame ("Suno fails Cantonese tone X% of the time") got
overturned by the data. After cleaning the dataset to n=8 chorus
snippets matched on tempo and section type, the audit shows:

- **Human pool: 74.3%** match rate (just under Wong & Diehl's 75–92% baseline).
- **Suno pool: 80.3%** match rate (comfortably inside the baseline).

Numerically, **Suno scores higher than humans.** That is almost certainly
wrong, and the project is about *why* — what the audit cannot see, and
what a native Cantonese ear catches anyway.

Three reasons the headline number lies:

1. **Auto-segmentation is fragile.** A one-second adjustment to the
   玻璃杯邊 snippet boundary moved its match rate from 91% → 73%. The
   pipeline is measuring boundary placement as much as tone fit.
2. **Suno's vocal articulation is "TTS-like":** crisper consonant
   attacks give the algorithm cleaner unvoiced gaps to split on, so
   F0 windows land more accurately. Cantopop human ballads are sung
   legato — fewer unvoiced gaps, more segmentation drift, lower
   apparent score.
3. **The audit measures direction-of-F0 only.** It cannot hear timbre,
   lyrical depth, or whether a syllable's pitch contour is *natural*
   versus *just-barely-correct-on-paper*.

The video is about (3) — what only a native speaker can hear.

---

## Methodology — fair-test rules (kept from prior plan)

- **n = 8** total: 4 human Cantopop + 4 Suno-generated chorus snippets.
- **Section type: chorus only** for every snippet.
- **Length: 10–14 syllables** ending at a phrase boundary.
- **Lyric cleanliness:** no English loanwords, no proper nouns, no
  變調; modern register (literary 的, colloquial 嗎) accepted on both sides.
- **Comparison framing:** human pool vs Suno pool means + within-pool spread.

**Not controlled** (and why it doesn't matter):
- Musical key — irrelevant; audit measures *direction*, not absolute pitch.
- Singer sex / vocal range — absorbed by per-snippet pitch_floor/ceiling.
- Absolute snippet duration — irrelevant; the unit is syllable-pair transitions.

---

## Tight script (read in ~3:25, leaves 5s buffer)

### 0:00–0:20 — Hook + concession (20s)

> "Cantonese has six tones. Change the tone, change the meaning. So when
> Suno writes a Cantopop song, the question isn't whether it sounds like
> Cantopop — the surprising answer is **yes**, and we'll get to that. The
> question is whether your ear catches what's wrong before your brain does."

**Visual.** Side-by-side waveform: 在錯誤的宇宙尋找愛 (On Chan, human, ballad)
left, 平行失手 (Suno-generated ballad chorus) right. Both play at low volume
under VO. Title card: *"What a Cantonese Ear Hears About AI Cantopop."*

---

### 0:20–0:55 — The constraint (35s)

> "Cantonese is a tone language. The pitch direction from one syllable
> to the next has to roughly match the tonal direction — or the lyric
> stops meaning what it's supposed to mean. Linguists Wong and Diehl
> measured this in 2002: human Cantopop respects the rule between 75
> and 92 percent of the time. That's not a stylistic preference — it's
> a structural constraint. **Sing 係 with the pitch shape of 西, and a
> Cantonese listener will hear 西** — a completely different word, and
> in this case a vulgar one."

**Visual.**
- 0:20–0:32: 6-tone chart with pitch contours; one arrow shows tone-direction.
- 0:32–0:45: Two syllables, expected up vs actual down — violation arrow.
- 0:45–0:55: 係 → 西 worked example. Audio: synthesized correct vs incorrect.

---

### 0:55–1:10 — Thesis & method preview (15s)

> "I built an audit. Four human Cantopop chorus lines, four Suno-generated
> chorus lines, all 10 to 14 syllables, matched by tempo across ballad,
> mid, and uptempo. For each line I extract the pitch contour with
> Parselmouth — the Python wrapper for Praat — and compare actual melodic
> direction against the direction Cantonese tones predict."

**Visual.** Eight track tiles fade in, grouped by source:
- HUMAN: 隔離 (Jace Chan, mid), 高山低谷 (Phil Lam, ballad),
  在錯誤的宇宙尋找愛 (On Chan 陳健安, ballad), 紅日 (Hacken Lee, uptempo).
- SUNO: 玻璃杯邊 (mid), 雨窗 (ballad), 平行失手 (ballad), 旺角快車 (uptempo).

---

### 1:10–1:50 — Pipeline (40s)

> "Pipeline. From each track, take a chorus line. Look up each character's
> citation tone in Words.hk — that gives the **expected** melodic direction.
> Then I take the audio. Parselmouth extracts the fundamental frequency,
> the F0, per syllable. The change in F0 from one syllable to the next is
> the **actual** direction. I follow Wong and Diehl's three-level reduction —
> every tone collapses to high, mid, or low based on its target pitch.
> Count violations: any pair where actual went the opposite way of expected."

**Visual (40s of screen-record).**
- 1:10–1:25: Show the snippet dict in `audit_driver.py` — lyrics, jyutping, tones.
- 1:25–1:40: Show terminal output of auto-segmented syllable boundaries
  for one snippet (e.g. `想: 12.34-12.51s (170ms)`).
- 1:40–1:50: Show the `analyze_snippet()` pair-by-pair violation table
  for one snippet, narration synced to one row.

---

### 1:50–2:25 — Results (35s) — **the surprise**

> "Here's where it gets interesting. The numbers say humans average **74
> percent** match rate, just under Wong and Diehl's baseline. **Suno
> averages 80 percent** — *better* than humans. That's not a real Suno
> advantage. The audit is measuring how cleanly each track segments,
> not how well it respects tone. Suno's vocals have crisper consonant
> attacks, which gives my algorithm cleaner places to split syllables.
> Human ballads are legato, which is harder. Move one snippet boundary
> by a single second and the score swings 18 points."

**Visual.**
- 1:50–2:10: Bar chart `figures/human_vs_suno.png` with pool means,
  individual snippet dots, baseline band shaded.
- 2:10–2:25: Animation: 玻璃杯邊 snippet boundary slides 1 sec; the bar
  visibly redraws from 91% to 73%. *"Fragile measurement."*

---

### 2:25–3:00 — What the audit can't see (35s) — **the heart**

> "So I listened. As a native Cantonese speaker. The Suno tracks pass
> the surface tests — the language is accurate, the genre is right, the
> melody could pass for Cantopop piano ballad. But three things give it
> away. One, the timbre is synthetic — there's a machine quality to the
> voice that isn't in human Cantopop. Two, the lyrics are 虛 — they're
> grammatically Cantonese and contextually coherent, but **literarily
> hollow**. Compare 黃偉文's *'這宇宙 這種深情根本虛構'* to Suno's
> *'平行宇宙入面 你會唔會愛我多一遍'*. Same theme. Same syllable count.
> The first one means something. The second one **fits**.
>
> And three — sometimes the words are weirdly fitted into the melody,
> like 係 sung where the pitch wants 西. The audit can score that as a
> down-up violation. A Cantonese listener doesn't need a chart for it."

**Visual.**
- 2:25–2:40: Audio plays: clean Wyman Wong line vs Suno line, lyrics on screen.
- 2:40–2:55: Concrete violation pair from `violation_examples()` — Suno
  syllable transition with F0 trace overlaid showing wrong direction.
- 2:55–3:00: Quick text: *"虛 (xū) — hollow, insubstantial."*

---

### 3:00–3:25 — Discussion + reflection (25s)

> "Why does this happen? Probably because Suno has trained on enough
> Cantopop to imitate the surface — the language, the chord changes, the
> chorus structure — without any architectural reason to encode tone
> constraints. The melody it picks is a *plausible Cantopop melody*, not
> a *Cantonese-tone-respecting melody*. Most listeners won't notice. And
> honestly, that's why Suno has a market. Someone who can't make music
> generates a track in their target genre, vibes with it, ships it.
> Vibing isn't the same as good. But it's enough for a lot of use cases.
>
> Most useful tool for this project: Parselmouth. Hardest part: realizing
> that the audit's headline number was wrong, and that the project's
> real finding was sitting in my own ears the whole time."

**Visual.**
- 3:00–3:15: Three quick callout cards: *"surface fluency ✓"*, *"tonal
  constraint ✗"*, *"native ear catches it"*.
- 3:15–3:25: Final card: project name, your name, repo link.

---

## Visual asset checklist

- [ ] `figures/human_vs_suno.png` — pool-mean bar chart with individual
      snippet dots and n labels. Already generated by `audit_driver.py`.
- [ ] 6-tone diagram — Cantonese tones with pitch contours (Keynote draw).
- [ ] 係 → 西 worked example — synthesized clean correct vs incorrect.
- [ ] Pipeline diagram — audio → Parselmouth → F0 → tones → audit.
- [ ] Terminal screenshot of auto-segmented syllable boundaries for one snippet.
- [ ] `analyze_snippet()` pair-by-pair violation table screenshot.
- [ ] Boundary-fragility animation: one-second slide of 玻璃杯邊 snippet
      causing match rate to swing 18 points (key visual for fragility claim).
- [ ] Side-by-side audio: 在錯誤的宇宙尋找愛 chorus line vs 平行失手 chorus line.
- [ ] Concrete violation pair clip — ~3 sec, Suno line with F0 trace overlay.
- [ ] Title card + closing card.

---

## Audio mixing notes

- Duck music under voiceover by ~12 dB throughout.
- For the **2:25–2:55 native-speaker section**, music plays clean (no
  duck) so the listener can actually hear what you're describing.
- For 係 → 西 worked example, use full clarity; this is the project's
  punchline-by-ear.
- Master loudness ~ -16 LUFS for assignment upload.

---

## What you must NOT do

1. Don't film yourself reading the script. Record VO separately, layer over visuals.
2. Don't claim Suno is "bad at Cantonese." It isn't. The point is sharper
   than that — surface fluency without structural constraint awareness.
3. Don't oversell the audit numbers. Lead with the surprise (Suno scores
   higher), explain why that's an artifact, then pivot to what your ear
   catches. Don't pretend the numbers showed what you originally hypothesized.
4. Don't show the full code. Show **outputs and one or two key dict entries**.
5. Don't pad. If you finish at 3:00, stop.
6. Don't translate 虛 word-for-word. Let the term sit; subtitle it once.
   It's part of the point that English doesn't have a tight equivalent.
