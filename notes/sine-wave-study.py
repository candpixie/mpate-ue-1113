import numpy as np
from IPython.display import Audio, display

# ─────────────────────────────────────────
# 1. SINE WAVE FUNCTION
# ─────────────────────────────────────────
def sine_wave(f):
    d  = 5                          # duration (seconds), hard-coded
    SR = 44000                      # sample rate
    PI = 3.14159265
    t  = np.linspace(0, d, SR * d)  # time array: 0 → 5s, 44000*5 samples
    return np.sin(2 * PI * f * t)

# Test: concert A
A = sine_wave(440)
display(Audio(A, rate=44000))


# ─────────────────────────────────────────
# 2. ADDING TWO SINE WAVES (pointwise)
# ─────────────────────────────────────────
A = sine_wave(440)
B = sine_wave(300)
C = A + B                           # adds sample-by-sample, NOT concatenation
display(Audio(C, rate=44000))


# ─────────────────────────────────────────
# 3. LFO — MULTIPLYING SIGNALS
# Low Frequency Oscillation as amplitude modulator
# ─────────────────────────────────────────
A = sine_wave(440)
B = sine_wave(300)
C = A + B

E = sine_wave(2)                    # LFO at 2 Hz (below hearing range)
modulated = C * E                   # amplitude modulation — creates rhythm/beats
display(Audio(modulated, rate=44000))

# Why you hear 4 beats with LFO of 2:
# sine goes +1 → 0 → -1 → 0 → +1 = 1 full cycle
# negative × negative = positive, so BOTH halves produce audible peaks
# 2 Hz LFO → 4 amplitude peaks per second


# ─────────────────────────────────────────
# 4. AUDIO EXTRACTION — slice 10s from middle
# Given: sample_rate, audio array, target start second
# ─────────────────────────────────────────
# Example: extract seconds 5–15 from a 20-min file
# audio = np.array([...])  # your loaded audio
# SR = 44000
# start = SR * 5           # sample index at second 5
# end   = SR * 15          # sample index at second 15  (= SR*5 + SR*10)
# clip  = audio[start:end]


# ─────────────────────────────────────────
# 5. SINE SWEEP FUNCTION
# Frequency changes linearly from start_f to end_f over length seconds
# ─────────────────────────────────────────
def sine_sweep(length, start_f, end_f):
    SR = 44000
    PI = 3.14159265
    t  = np.linspace(0, length, SR * length)        # time array
    f  = np.linspace(start_f, end_f, SR * length)   # frequency array (mirrors t)
    return np.sin(2 * PI * f * t)

# Test: 5-second sweep from 200 Hz → 300 Hz
sweep = sine_sweep(5, 200, 300)
display(Audio(sweep, rate=44000))

# Test: rising tone 100 Hz → 1000 Hz (like a hearing test)
sweep2 = sine_sweep(5, 100, 1000)
display(Audio(sweep2, rate=44000))