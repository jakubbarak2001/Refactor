"""
Procedural battle SFX for REFACTOR — stdlib only (no numpy), 44.1kHz mono 16-bit WAV.

Fills the silent slots the engine already calls via _play_battle_sfx():
    card_skill, card_power, end_turn, victory_sting, defeat_sting

These are tasteful synthesized PLACEHOLDERS — short, low-key, mixed under the
existing recorded SFX (card_attack / block_clang). Swap with real recordings any
time; the engine auto-picks .ogg/.mp3/.wav by filename, no code change needed.

    python tools/gen_sfx.py
"""

import math
import os
import random
import struct
import wave
from pathlib import Path

SR = 44100
OUT = Path(__file__).resolve().parent.parent / "REFACTOR" / "game" / "audio" / "sfx"

random.seed(7)  # deterministic output across runs


def _env(n, attack, release, sustain=1.0):
    """ADSR-ish envelope over n samples: linear attack, flat, linear release."""
    a = max(1, int(attack * n))
    r = max(1, int(release * n))
    out = []
    for i in range(n):
        if i < a:
            out.append(sustain * (i / a))
        elif i > n - r:
            out.append(sustain * ((n - i) / r))
        else:
            out.append(sustain)
    return out


def _sine(freq, n, phase=0.0):
    return [math.sin(2 * math.pi * freq * (i / SR) + phase) for i in range(n)]


def _mix(*tracks):
    n = max(len(t) for t in tracks)
    out = [0.0] * n
    for t in tracks:
        for i, v in enumerate(t):
            out[i] += v
    return out


def _normalize(buf, peak=0.6):
    m = max(1e-9, max(abs(v) for v in buf))
    return [v / m * peak for v in buf]


def _write(name, buf, peak=0.6):
    buf = _normalize(buf, peak)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.wav"
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v)) * 32767)) for v in buf)
        w.writeframes(frames)
    print(f"wrote {path.relative_to(OUT.parent.parent.parent.parent)}  ({len(buf)/SR:.2f}s)")


def card_skill():
    # Soft airy "thwip" — a quick downward sine sweep + a breath of filtered noise.
    n = int(0.16 * SR)
    sweep = [math.sin(2 * math.pi * (820 - 380 * (i / n)) * (i / SR)) for i in range(n)]
    noise = [(random.random() * 2 - 1) for _ in range(n)]
    # one-pole low-pass on the noise so it's air, not static
    lp, a = [], 0.0
    for v in noise:
        a += 0.06 * (v - a)
        lp.append(a)
    env = _env(n, 0.04, 0.7)
    buf = [(0.7 * sweep[i] + 0.5 * lp[i]) * env[i] for i in range(n)]
    _write("card_skill", buf, peak=0.45)


def card_power():
    # Warm rising swell — root + fifth + octave, pitch eases up, slow bloom.
    n = int(0.6 * SR)
    base = 196.0  # G3
    parts = []
    for mult, amp in ((1.0, 1.0), (1.5, 0.6), (2.0, 0.45), (3.0, 0.2)):
        track = []
        for i in range(n):
            t = i / n
            f = base * mult * (1.0 + 0.18 * t)  # gentle rise
            track.append(amp * math.sin(2 * math.pi * f * (i / SR)))
        parts.append(track)
    env = _env(n, 0.35, 0.45)  # slow attack = "powering up", long-ish fade
    mixed = _mix(*parts)
    buf = [mixed[i] * env[i] for i in range(n)]
    _write("card_power", buf, peak=0.55)


def end_turn():
    # "Lock-in" — a low thunk with a click transient and a short higher confirm.
    n = int(0.2 * SR)
    low = _sine(150, n)
    hi = _sine(430, n)
    env_low = _env(n, 0.01, 0.55)
    env_hi = _env(int(0.09 * SR), 0.02, 0.8)
    buf = [low[i] * env_low[i] for i in range(n)]
    for i in range(len(env_hi)):
        buf[i] += 0.4 * hi[i] * env_hi[i]
    buf[0] += 0.5  # click transient
    _write("end_turn", buf, peak=0.5)


def _note(freq, dur, n_total, start, amp=1.0, decay=0.6):
    """A plucked sine note (with a soft octave) placed into an n_total buffer."""
    n = int(dur * SR)
    out = [0.0] * n_total
    for i in range(n):
        idx = start + i
        if idx >= n_total:
            break
        t = i / n
        e = amp * math.exp(-3.0 * t) if decay else amp
        s = math.sin(2 * math.pi * freq * (i / SR)) + 0.35 * math.sin(2 * math.pi * freq * 2 * (i / SR))
        out[idx] += s * e
    return out


def victory_sting():
    # Ascending major arpeggio C5-E5-G5-C6, overlapping, warm.
    total = int(1.1 * SR)
    step = int(0.16 * SR)
    notes = [(523.25, 0), (659.25, 1), (783.99, 2), (1046.5, 3)]
    tracks = [_note(f, 0.7, total, k * step, amp=0.9, decay=True) for f, k in notes]
    _write("victory_sting", _mix(*tracks), peak=0.6)


def defeat_sting():
    # Descending minor — somber falling tones, slow and low.
    total = int(1.25 * SR)
    step = int(0.34 * SR)
    notes = [(220.0, 0), (174.61, 1), (130.81, 2)]  # A3 -> F3 -> C3
    tracks = [_note(f, 0.95, total, k * step, amp=0.9, decay=True) for f, k in notes]
    _write("defeat_sting", _mix(*tracks), peak=0.55)


if __name__ == "__main__":
    card_skill()
    card_power()
    end_turn()
    victory_sting()
    defeat_sting()
    print("done.")
