"""
audit_driver.py

End-to-end driver for the Cantopop tone audit project.
Run cell-by-cell in VS Code (the `# %%` markers create interactive cells)
or as a script: python3 audit_driver.py

PIPELINE:
  1. Define dataset (3 human + 3 Suno snippets, matched by tempo).
  2. Manually annotate syllable timings per audio file (Audacity).
  3. Run F0 extraction + tone-tune audit per snippet.
  4. Aggregate human vs Suno violation rates by tempo bucket.
  5. Plot results for the video.
"""

# %% [markdown]
# # Cantonese Tone Audit: Suno vs. Human Composers
#
# **Thesis.** Human Cantopop composers align melodic direction with
# Cantonese tonal transitions at a measurable rate (~75-92% per Wong &
# Diehl 2002, Lo 2013). I tested whether Suno respects the same constraint
# in its own original Cantopop output.
#
# **Method.** 3 human Cantopop songs paired with 3 Suno-generated tracks
# matched by tempo (mid / ballad / uptempo). Suno wrote its own lyrics
# from style prompts; I picked one 7-10 syllable snippet from each.
# Same audit framework applied to all 6 snippets.

# %% imports
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

# Use a CJK-capable font so 中文 labels render instead of empty boxes.
# macOS ships with PingFang and Heiti; fall through to anything that works.
matplotlib.rcParams['font.family'] = [
    'PingFang HK', 'PingFang TC', 'PingFang SC',
    'Heiti TC', 'Heiti SC', 'Hiragino Sans GB',
    'Arial Unicode MS', 'sans-serif',
]
matplotlib.rcParams['axes.unicode_minus'] = False
from cantonese_tone_audit import (
    analyze_snippet,
    extract_syllable_f0,
    auto_segment_syllables,
    print_report,
    expected_direction,
    TONE_LEVEL,
)

# %% [markdown]
# ## 1. Dataset (verified)
#
# Each snippet:
# - 7-10 syllables
# - No 變調 (tone change), no English loanwords, no proper nouns
# - All citation tones cross-checked

# %% snippet definitions

# ---- HUMAN: 隔離 (Jace Chan, 2023) — MID-TEMPO ----
# Line: 想約他 私訊他 別無視我好嗎  (12 syllables)
H_GE_LEI = {
    'song':     '隔離',
    'artist':   'Jace Chan',
    'source':   'human',
    'tempo':    'mid',
    'lyrics':   ['想','約','他','私','訊','他','別','無','視','我','好','嗎'],
    'jyutping': ['soeng2','joek3','taa1','si1','seon3','taa1',
                 'bit6','mou4','si6','ngo5','hou2','maa3'],
    'tones':    [2, 3, 1, 1, 3, 1, 6, 4, 6, 5, 2, 3],
    'snippet_range': (25, 30),
    'syllable_times': [],
    'audio_path': 'audio/jace_gelei.mp3',
    'pitch_floor': 100, 'pitch_ceiling': 500,
}

# ---- SUNO MID: 玻璃杯邊 chorus
# "留低好嗎 留低一晚 玻璃杯邊" (12 syllables) ----
# Extended from 8 to 12 syllables to meet 10-14 chorus standard.
# Audio file is named jace_gelei-suno.mp3 (paired with 隔離 in mid bucket).
# TODO: confirm snippet_range now extends to ~12 syll worth of audio.
S_SUNO_MID = {
    'song':     '玻璃杯邊 (Suno)',
    'artist':   'Suno V5.5',
    'source':   'suno',
    'tempo':    'mid',
    'lyrics':   ['留','低','好','嗎','留','低','一','晚',
                 '玻','璃','杯','邊'],
    'jyutping': ['lau4','dai1','hou2','maa3','lau4','dai1','jat1','maan5',
                 'bo1','lei4','bui1','bin1'],
    'tones':    [4, 1, 2, 3, 4, 1, 1, 5, 1, 4, 1, 1],
    'snippet_range': (63, 72),   # 1:03-1:12 (12 syll chorus, verified)
    'syllable_times': [],
    'audio_path': 'audio/jace_gelei-suno.mp3',
    'pitch_floor': 70, 'pitch_ceiling': 500,
}

# ---- HUMAN: 高山低谷 (Phil Lam 林奕匡, 2014) — BALLAD ----
# Chorus opening line: "你快樂過生活 我拼命去生存"  (12 syllables)
# (Repeats twice in the song — verified against official lyrics.)
H_GOU_SAAN = {
    'song':     '高山低谷',
    'artist':   'Phil Lam (林奕匡)',
    'source':   'human',
    'tempo':    'ballad',
    'lyrics':   ['你','快','樂','過','生','活','我','拼','命','去','生','存'],
    'jyutping': ['nei5','faai3','lok6','gwo3','sang1','wut6',
                 'ngo5','ping3','ming6','heoi3','sang1','cyun4'],
    'tones':    [5, 3, 6, 3, 1, 6, 5, 3, 6, 3, 1, 4],
    'snippet_range': (138, 144),   # 2:18-2:24
    'syllable_times': [],
    'audio_path': 'audio/gou-san.mp3',
    'pitch_floor': 70, 'pitch_ceiling': 500,     # Phil Lam = male vocal
}

# ---- SUNO BALLAD: 雨窗 chorus second half
# "我仲喺原地 等一個唔會返嚟的你" (14 syllables) ----
# Swapped from the previous pre-chorus snippet to satisfy chorus-only.
# Note: 會 has wui5/wui6 reading ambiguity — committing to wui5 (T5/M)
# as the modern Cantonese auxiliary reading.
# TODO: find timestamp where this chorus line plays (likely 1:30-1:40
# range based on typical pop song structure).
S_SUNO_BALLAD = {
    'song':     '雨窗 (Suno)',
    'artist':   'Suno V5.5',
    'source':   'suno',
    'tempo':    'ballad',
    'lyrics':   ['我','仲','喺','原','地','等','一',
                 '個','唔','會','返','嚟','的','你'],
    'jyutping': ['ngo5','zung6','hai2','jyun4','dei6','dang2','jat1',
                 'go3','m4','wui5','faan1','lai4','dik1','nei5'],
    'tones':    [5, 6, 2, 4, 6, 2, 1, 3, 4, 5, 1, 4, 1, 5],
    'snippet_range': (141, 150),   # 2:21-2:30 (final chorus)
    'syllable_times': [],
    'audio_path': 'audio/gou-san-suno.mp3',
    'pitch_floor': 70, 'pitch_ceiling': 500,
}

# ---- HUMAN: 紅日 (Hacken Lee 李克勤, 1992) — UPTEMPO ----
# Line: 我願能一生永遠陪伴你  (10 syllables)
H_HUNG_JAT = {
    'song':     '紅日',
    'artist':   'Hacken Lee (李克勤)',
    'source':   'human',
    'tempo':    'uptempo',
    'lyrics':   ['我','願','能','一','生','永','遠','陪','伴','你'],
    'jyutping': ['ngo5','jyun6','nang4','jat1','sang1',
                 'wing5','jyun5','pui4','bun6','nei5'],
    'tones':    [5, 6, 4, 1, 1, 5, 5, 4, 6, 5],
    'snippet_range': (48, 52),
    'syllable_times': [],
    'audio_path': 'audio/hong-jat.mp3',
    'pitch_floor': 70, 'pitch_ceiling': 500,
}

# ---- SUNO UPTEMPO: 旺角快車 chorus opening
# "一齊跑 一齊衝 旺角快車開動" (12 syllables) ----
# CORRECTION: the previous lyrics in this dict ("喺原地 等一個唔會返嚟的你")
# were Claude's misread — that line is from 雨窗 (Suno ballad), not from
# 旺角快車. The actual 旺角快車 chorus is "一齊跑 一齊衝 旺角快車開動".
# TODO: find timestamp where this chorus line plays in hong-jat-suno.mp3.
S_SUNO_UPTEMPO = {
    'song':     '旺角快車 (Suno)',
    'artist':   'Suno V5.5',
    'source':   'suno',
    'tempo':    'uptempo',
    'lyrics':   ['一','齊','跑','一','齊','衝',
                 '旺','角','快','車','開','動'],
    'jyutping': ['jat1','cai4','paau2','jat1','cai4','cung1',
                 'wong6','gok3','faai3','ce1','hoi1','dung6'],
    'tones':    [1, 4, 2, 1, 4, 1, 6, 3, 3, 1, 1, 6],
    'snippet_range': (59, 66),    # 0:59-1:06 (first chorus)
    'syllable_times': [],
    'audio_path': 'audio/hong-jat-suno.mp3',
    'pitch_floor': 70, 'pitch_ceiling': 500,
}

# ---- HUMAN: 在錯誤的宇宙尋找愛 (陳健安 On Chan, 2019) — BALLAD ----
# Chorus opening line: "這宇宙 這種深情根本虛構" (11 syllables)
# Composer 馮穎琪, lyricist 黃偉文 (Wyman Wong) — verified via web search.
# 4th human snippet for the n=8 pool comparison.
# TODO: fill audio_path + snippet_range from QuickTime scrub.
H_WRONG_UNIVERSE = {
    'song':     '在錯誤的宇宙尋找愛',
    'artist':   '陳健安 On Chan',
    'source':   'human',
    'tempo':    'ballad',
    'lyrics':   ['這','宇','宙','這','種','深','情','根','本','虛','構'],
    'jyutping': ['ze2','jyu5','zau6','ze2','zung2','sam1','cing4',
                 'gan1','bun2','heoi1','kau3'],
    'tones':    [2, 5, 6, 2, 2, 1, 4, 1, 2, 1, 3],
    'snippet_range': (86, 92),                   # 1:26-1:32
    'syllable_times': [],
    'audio_path': 'audio/wrong-universe.wav',    # extracted from MP4 via afconvert
    'pitch_floor': 70, 'pitch_ceiling': 500,     # On Chan = male vocal
}

# ---- SUNO BALLAD #2: 平行失手 chorus opening
# "平行宇宙入面，你會唔會愛我多一遍" (15 syllables) ----
# 4th Suno snippet for the n=8 pool. Generated from a Cantopop-ballad
# style prompt with theme "regret + parallel universes."
# Slight overage on the 10-14 standard (15 syll) accepted because this
# is the chorus opener, parallel in role to the openers used in
# 玻璃杯邊 and 旺角快車 snippets.
# TODO: fill audio_path + snippet_range from the generated audio file.
S_SUNO_BALLAD_2 = {
    'song':     '平行失手 (Suno)',
    'artist':   'Suno V5.5',
    'source':   'suno',
    'tempo':    'ballad',
    'lyrics':   ['平','行','宇','宙','入','面','你','會','唔','會',
                 '愛','我','多','一','遍'],
    'jyutping': ['ping4','hang4','jyu5','zau6','jap6','min6',
                 'nei5','wui5','m4','wui5',
                 'oi3','ngo5','do1','jat1','pin3'],
    'tones':    [4, 4, 5, 6, 6, 6, 5, 5, 4, 5, 3, 5, 1, 1, 3],
    'snippet_range': (83, 89),                      # 1:23-1:29
    'syllable_times': [],
    'audio_path': 'audio/wrong-universe-suno.mp3',  # Suno-generated 平行失手
    'pitch_floor': 70, 'pitch_ceiling': 500,
}

SNIPPETS = [H_GE_LEI, S_SUNO_MID,
            H_GOU_SAAN, S_SUNO_BALLAD,
            H_HUNG_JAT, S_SUNO_UPTEMPO,
            H_WRONG_UNIVERSE, S_SUNO_BALLAD_2]

# %% [markdown]
# ## 2. Sanity check: expected directions (no audio yet)

# %% expected directions
def expected_directions_table(snippet):
    rows = []
    t = snippet['tones']
    lyr = snippet['lyrics']
    for i in range(len(t) - 1):
        rows.append({
            'pair':     f"{lyr[i]}->{lyr[i+1]}",
            'tones':    f"T{t[i]}->T{t[i+1]}",
            'levels':   f"{TONE_LEVEL[t[i]]}->{TONE_LEVEL[t[i+1]]}",
            'expected': expected_direction(t[i], t[i+1]),
        })
    return pd.DataFrame(rows)

for s in SNIPPETS:
    print(f"\n--- {s['song']} ({s['tempo']}, {s['source']}) ---")
    print(f"    syllables: {len(s['tones'])}, transitions: {len(s['tones'])-1}")
    print(expected_directions_table(s).to_string(index=False))

# %% [markdown]
# ## 3. Find the snippet's time range in each song
#
# **You only need 2 numbers per song.** Open each mp3 in QuickTime
# Player (or any audio player). Scrub until you hear the snippet line.
# Note:
#   - **start_sec** = time of the FIRST syllable's onset
#   - **end_sec**   = time AFTER the LAST syllable ends
#
# Set `snippet_range = (start_sec, end_sec)` in each dict above.
# The code subdivides into syllables automatically using onset detection.
#
# Total effort: ~5 min for 6 songs.
#
# **Tip — scrubbing in QuickTime:** drag the time slider; the time
# display shows mm:ss. Convert to seconds: e.g. 1:23 -> 83 sec.

# %% [markdown]
# ## 4. Auto-segment + F0 extraction + audit

# %% run audit
def audit_one(snippet, segment_method='onset', verbose=True):
    if snippet.get('snippet_range') is None and not snippet['syllable_times']:
        print(f"[skip] {snippet['song']} ({snippet['source']}) "
              f"— snippet_range not set")
        return None

    # Auto-segment if syllable_times empty
    if not snippet['syllable_times']:
        start, end = snippet['snippet_range']
        snippet['syllable_times'] = auto_segment_syllables(
            snippet['audio_path'], start, end,
            n_syllables=len(snippet['tones']),
            method=segment_method,
            pitch_floor=snippet['pitch_floor'],
            pitch_ceiling=snippet['pitch_ceiling'],
        )
        if verbose:
            print(f"  auto-segmented {snippet['song']} ({segment_method}):")
            for ch, (a, b) in zip(snippet['lyrics'], snippet['syllable_times']):
                print(f"    {ch}: {a:.2f}-{b:.2f}s ({(b-a)*1000:.0f}ms)")

    f0 = extract_syllable_f0(
        snippet['audio_path'],
        snippet['syllable_times'],
        pitch_floor=snippet['pitch_floor'],
        pitch_ceiling=snippet['pitch_ceiling'],
    )
    return analyze_snippet(
        tones=snippet['tones'],
        f0_values=f0,
        lyrics=snippet['lyrics'],
    )

# Lock segmentation to 'voiced' — most principled for tone work since
# F0 medians are computed on actually-voiced regions of each syllable.
SEGMENT_METHOD = 'voiced'

results = []
for s in SNIPPETS:
    s['syllable_times'] = []   # reset; auto-segment each run
    r = audit_one(s, segment_method=SEGMENT_METHOD, verbose=False)
    if r is None:
        continue
    print_report(r, title=f"{s['song']} — {s['source'].upper()} ({s['tempo']})")
    results.append({
        'song':           s['song'],
        'tempo':          s['tempo'],
        'source':         s['source'],
        'match_rate':     r['match_rate'],
        'violation_rate': r['violation_rate'],
        'violations':     r['violations'],
        'valid_pairs':    r['valid_pairs'],
    })

results_df = pd.DataFrame(results)
if not results_df.empty:
    print("\n=== AGGREGATE ===")
    print(results_df.to_string(index=False))

# %% [markdown]
# ## 5. Visualization

# %% bar chart
def plot_audit(df, save_path='figures/human_vs_suno.png'):
    import os
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    tempos = ['mid', 'ballad', 'uptempo']
    x = np.arange(len(tempos))
    width = 0.35

    def pool(t, src):
        return df[(df['tempo']==t) & (df['source']==src)]['match_rate'].tolist()
    human = [np.mean(pool(t, 'human')) if pool(t, 'human') else np.nan for t in tempos]
    suno  = [np.mean(pool(t, 'suno'))  if pool(t, 'suno')  else np.nan for t in tempos]
    human_n = [len(pool(t, 'human')) for t in tempos]
    suno_n  = [len(pool(t, 'suno'))  for t in tempos]

    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    bars_h = ax.bar(x - width/2, human, width, label='Human (pool mean)', color='#2E86AB')
    bars_s = ax.bar(x + width/2, suno,  width, label='Suno (pool mean)',  color='#E63946')

    # Overlay individual snippet dots so within-pool spread is visible.
    for i, t in enumerate(tempos):
        for v in pool(t, 'human'):
            ax.scatter(i - width/2, v, color='#0A2A47', s=30, zorder=3,
                       edgecolor='white', linewidth=0.8)
        for v in pool(t, 'suno'):
            ax.scatter(i + width/2, v, color='#7A0613', s=30, zorder=3,
                       edgecolor='white', linewidth=0.8)

    ax.axhspan(0.75, 0.92, alpha=0.12, color='gray',
               label='Wong & Diehl 2002 baseline (75-92%)')

    ax.set_ylabel('Tone-tune match rate', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels([t.upper() for t in tempos], fontsize=11)
    ax.set_ylim(0, 1.08)
    ax.set_title('Cantonese tone-tune match rate by tempo: Human vs Suno (n=8)',
                 fontsize=13)
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    for i, (h, s, hn, sn) in enumerate(zip(human, suno, human_n, suno_n)):
        if not np.isnan(h):
            ax.text(i - width/2, h + 0.02, f'{h:.0%}\nn={hn}',
                    ha='center', fontsize=9)
        if not np.isnan(s):
            ax.text(i + width/2, s + 0.02, f'{s:.0%}\nn={sn}',
                    ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    return fig

if not results_df.empty:
    plot_audit(results_df)

# %% [markdown]
# ## 6. Violation examples (for video b-roll)

# %% violations detail
def violation_examples(snippet, max_n=3):
    r = audit_one(snippet)
    if r is None:
        return []
    return [p for p in r['pairs'] if p['violation'] is True][:max_n]

for s in SNIPPETS:
    if s['source'] != 'suno':
        continue
    bad = violation_examples(s)
    if not bad:
        continue
    print(f"\n--- {s['song']} (Suno) — top violations ---")
    for b in bad:
        print(f"  {b.get('lyrics', b['idx'])}: "
              f"expected {b['expected']}, got {b['actual']} "
              f"(tones T{b['tones'][0]}-T{b['tones'][1]})")
