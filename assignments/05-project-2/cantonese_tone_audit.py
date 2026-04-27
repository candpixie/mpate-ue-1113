"""
cantonese_tone_audit.py

Tone-tune mapping audit framework for Cantopop.
Compares expected melodic direction (from citation tones) against
actual melodic direction (from F0 extraction) per adjacent syllable pair.

Framework: Wong & Diehl (2002) ordinal mapping, 3-level reduction by tone ending.
Validated baseline: ~75-92% match in human Cantopop corpora.

Author: Candy Xie
Class: MPATE-UE 1113, Final Project, Spring 2026
"""

import numpy as np
import parselmouth


def load_sound(audio_path):
    """
    Load .wav or .mp3 into a parselmouth.Sound.
    mp3 goes through librosa to avoid ffmpeg dependency.
    """
    if str(audio_path).lower().endswith('.wav'):
        return parselmouth.Sound(str(audio_path))
    import librosa
    y, sr = librosa.load(str(audio_path), sr=None, mono=True)
    return parselmouth.Sound(y, sampling_frequency=sr)


# ============================================================
# 1. TONE TO PITCH LEVEL MAPPING (Wong & Diehl 2002)
# ============================================================
# Three-level reduction by tone ENDING (target pitch):
#   T1 陰平 55  -> H
#   T2 陰上 25  -> H   (rising target reaches high)
#   T3 陰去 33  -> M
#   T4 陽平 21  -> L
#   T5 陽上 23  -> M   (rising target reaches mid)
#   T6 陽去 22  -> L
# Entering tones (T7/T8/T9 in 9-tone) collapse onto T1/T3/T6.

TONE_LEVEL = {
    1: 'H',
    2: 'H',
    3: 'M',
    4: 'L',
    5: 'M',
    6: 'L',
    7: 'H',
    8: 'M',
    9: 'L',
}

LEVEL_RANK = {'L': 0, 'M': 1, 'H': 2}


# ============================================================
# 2. EXPECTED VS ACTUAL DIRECTION
# ============================================================

def expected_direction(tone_a, tone_b):
    """Expected melodic direction A -> B from citation tones."""
    a = LEVEL_RANK[TONE_LEVEL[tone_a]]
    b = LEVEL_RANK[TONE_LEVEL[tone_b]]
    if b > a:
        return 'up'
    elif b < a:
        return 'down'
    else:
        return 'same'


def actual_direction(f0_a, f0_b, threshold_semitones=1.0):
    """
    Direction from median F0 of A to B.
    1-semitone threshold filters micro-fluctuations.
    """
    if f0_a is None or f0_b is None or f0_a <= 0 or f0_b <= 0:
        return None
    semitones = 12 * np.log2(f0_b / f0_a)
    if semitones > threshold_semitones:
        return 'up'
    elif semitones < -threshold_semitones:
        return 'down'
    else:
        return 'same'


def is_violation(expected, actual, strict=False):
    """
    Wong & Diehl 2002 violation rule:
    - Hard violation: melody opposite to tone (up vs down).
    - Soft cases (level mismatch with same): default ignore.
    """
    if actual is None:
        return None
    if expected == 'up' and actual == 'down':
        return True
    if expected == 'down' and actual == 'up':
        return True
    if strict:
        if expected == 'same' and actual != 'same':
            return True
        if expected != 'same' and actual == 'same':
            return True
    return False


# ============================================================
# 3. F0 EXTRACTION (Parselmouth)
# ============================================================

def extract_syllable_f0(audio_path, syllable_times,
                        pitch_floor=75, pitch_ceiling=600,
                        time_step=0.01):
    """
    Median F0 (Hz) per manually-annotated syllable.
    Tune pitch_floor/ceiling per singer:
        female: floor=100, ceiling=500
        male:   floor=70,  ceiling=350
    """
    snd = load_sound(audio_path)
    pitch = snd.to_pitch(time_step=time_step,
                         pitch_floor=pitch_floor,
                         pitch_ceiling=pitch_ceiling)

    f0_per_syllable = []
    for start, end in syllable_times:
        values = []
        t = start
        while t < end:
            f = pitch.get_value_at_time(t)
            if not np.isnan(f) and f > 0:
                values.append(f)
            t += time_step
        f0_per_syllable.append(float(np.median(values)) if values else None)
    return f0_per_syllable


# ============================================================
# 3b. AUTO-SEGMENT SYLLABLES (no manual annotation needed)
# ============================================================

def auto_segment_syllables(audio_path, snippet_start, snippet_end,
                           n_syllables, method='onset',
                           pitch_floor=70, pitch_ceiling=500):
    """
    Subdivide a snippet's time range into n_syllables (start, end) tuples.

    method='onset':   librosa onset detection within the snippet range,
                      pick n-1 strongest onsets as boundaries.
    method='voiced':  parselmouth voicing — split at unvoiced gaps.
    method='even':    evenly spaced (fallback for legato vocals).

    Returns: list of (start_sec, end_sec) tuples, len = n_syllables.
    """
    import librosa
    import numpy as np

    if method == 'even':
        edges = np.linspace(snippet_start, snippet_end, n_syllables + 1)
        return [(edges[i], edges[i+1]) for i in range(n_syllables)]

    if method == 'onset':
        y, sr = librosa.load(str(audio_path), sr=None, mono=True,
                             offset=snippet_start,
                             duration=snippet_end - snippet_start)
        onset_times = librosa.onset.onset_detect(
            y=y, sr=sr, units='time', backtrack=True
        )
        onset_times = np.array(onset_times) + snippet_start
        # need n-1 internal boundaries
        needed = n_syllables - 1
        if len(onset_times) >= needed:
            # pick most evenly distributed n-1 onsets
            idx = np.linspace(0, len(onset_times) - 1, needed).astype(int)
            internal = onset_times[idx]
        else:
            # fall back to even spacing
            return auto_segment_syllables(audio_path, snippet_start,
                                          snippet_end, n_syllables,
                                          method='even')
        edges = np.concatenate([[snippet_start], internal, [snippet_end]])
        return [(float(edges[i]), float(edges[i+1]))
                for i in range(n_syllables)]

    if method == 'voiced':
        snd = load_sound(audio_path)
        snd_part = snd.extract_part(from_time=snippet_start,
                                    to_time=snippet_end,
                                    preserve_times=True)
        pitch = snd_part.to_pitch(time_step=0.01,
                                  pitch_floor=pitch_floor,
                                  pitch_ceiling=pitch_ceiling)
        # voiced/unvoiced timeline
        times = np.arange(snippet_start, snippet_end, 0.01)
        voiced = []
        for t in times:
            f = pitch.get_value_at_time(t)
            voiced.append(not np.isnan(f) and f > 0)
        # find transitions unvoiced -> voiced (syllable starts)
        starts = [snippet_start]
        for i in range(1, len(voiced)):
            if voiced[i] and not voiced[i-1]:
                starts.append(times[i])
        starts = sorted(set(starts))[:n_syllables]
        if len(starts) < n_syllables:
            return auto_segment_syllables(audio_path, snippet_start,
                                          snippet_end, n_syllables,
                                          method='onset')
        starts = starts + [snippet_end]
        return [(float(starts[i]), float(starts[i+1]))
                for i in range(n_syllables)]

    raise ValueError(f"unknown method: {method}")


# ============================================================
# 4. SNIPPET ANALYSIS
# ============================================================

def analyze_snippet(tones, f0_values, lyrics=None,
                    threshold_semitones=1.0, strict=False):
    """
    Compute violation rate for one snippet.

    tones:     list of citation tones (1-9), one per syllable
    f0_values: list of median F0 per syllable, None if unvoiced
    lyrics:    optional list of characters or jyutping
    """
    assert len(tones) == len(f0_values), \
        f"Tone count {len(tones)} != F0 count {len(f0_values)}"

    pairs = []
    violations = 0
    valid_pairs = 0

    for i in range(len(tones) - 1):
        exp = expected_direction(tones[i], tones[i + 1])
        act = actual_direction(f0_values[i], f0_values[i + 1],
                               threshold_semitones)
        viol = is_violation(exp, act, strict=strict)

        pair = {
            'idx': (i, i + 1),
            'tones': (tones[i], tones[i + 1]),
            'levels': (TONE_LEVEL[tones[i]], TONE_LEVEL[tones[i + 1]]),
            'expected': exp,
            'actual': act,
            'violation': viol,
        }
        if lyrics is not None:
            pair['lyrics'] = (lyrics[i], lyrics[i + 1])
        pairs.append(pair)

        if viol is not None:
            valid_pairs += 1
            if viol:
                violations += 1

    rate = violations / valid_pairs if valid_pairs else 0.0
    return {
        'violation_rate': rate,
        'match_rate': 1 - rate,
        'violations': violations,
        'valid_pairs': valid_pairs,
        'total_pairs': len(tones) - 1,
        'pairs': pairs,
    }


# ============================================================
# 5. PRETTY PRINT
# ============================================================

def print_report(result, title="Snippet"):
    print(f"\n=== {title} ===")
    print(f"Match rate:     {result['match_rate']:.1%}")
    print(f"Violation rate: {result['violation_rate']:.1%}")
    print(f"Valid pairs:    {result['valid_pairs']} / {result['total_pairs']}")
    print(f"\n{'Pair':<6} {'Tones':<8} {'Levels':<10} "
          f"{'Expected':<10} {'Actual':<10} {'Violation'}")
    print("-" * 60)
    for p in result['pairs']:
        viol_str = '!' if p['violation'] else ('-' if p['violation'] is False
                                               else 'skip')
        print(f"{p['idx'][0]}-{p['idx'][1]:<4} "
              f"T{p['tones'][0]}-T{p['tones'][1]:<5} "
              f"{p['levels'][0]}-{p['levels'][1]:<8} "
              f"{p['expected']:<10} "
              f"{str(p['actual']):<10} "
              f"{viol_str}")
