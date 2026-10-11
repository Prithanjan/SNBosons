"""
Audio synthesis, additive partials, reverb, and RMS loudness calibration.
Section 2.8 of Agent PRD.
"""

from typing import List, Tuple
import wave
import numpy as np

SAMPLE_RATE = 44100
TEMPO_BPM = 100
SIXTEENTH_SEC = 60.0 / (TEMPO_BPM * 4.0)  # 0.15 s
TARGET_RMS = 0.1835

# Triads (octave 3-4, MIDI 48-62) and bass roots (MIDI root - 12)
CHORD_PROGRESSION: List[Tuple[List[int], int]] = [
    ([48, 52, 55], 36),  # C major (C3, E3, G3), C2 bass
    ([53, 57, 60], 41),  # F major (F3, A3, C4), F2 bass
    ([55, 59, 62], 43),  # G major (G3, B3, D4), G2 bass
    ([48, 52, 55], 36),  # C major (C3, E3, G3), C2 bass
]


def synth_note(pitch: int, d16: int, partials: List[float], amp: float, sr: int = SAMPLE_RATE) -> np.ndarray:
    """
    Synthesize single note with additive sine partials and exponential envelope:
    envelope: attack 0.01s (linear), exponential decay exp(-1.2 * t).
    """
    dur_sec = d16 * SIXTEENTH_SEC
    n_samples = int(np.round(dur_sec * sr))
    if n_samples <= 0:
        return np.zeros(0)

    t = np.linspace(0, dur_sec, n_samples, endpoint=False)
    freq = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
    sig = np.zeros(n_samples)
    for k, p_amp in enumerate(partials, start=1):
        sig += p_amp * np.sin(2.0 * np.pi * k * freq * t)

    env = np.exp(-1.2 * t)
    n_attack = int(np.round(0.01 * sr))
    if 0 < n_attack < n_samples:
        env[:n_attack] *= np.linspace(0.0, 1.0, n_attack)

    return amp * sig * env


def render_voice_track(
    notes: List[Tuple[int, int, int]], total_samples: int, partials: List[float], amp: float, sr: int = SAMPLE_RATE
) -> np.ndarray:
    """
    Render a sequence of (pitch, d16, onset16) notes into a mono signal buffer.
    """
    buffer = np.zeros(total_samples)
    for pitch, d16, onset16 in notes:
        start_samp = int(np.round(onset16 * SIXTEENTH_SEC * sr))
        sig = synth_note(pitch, d16, partials, amp, sr)
        n_samp = len(sig)
        if n_samp == 0 or start_samp >= total_samples:
            continue
        end_samp = min(start_samp + n_samp, total_samples)
        buffer[start_samp:end_samp] += sig[: end_samp - start_samp]
    return buffer


def create_reverb_ir(sr: int = SAMPLE_RATE, duration: float = 1.5, decay: float = 4.0, seed: int = 2026) -> np.ndarray:
    """
    Create exponentially decaying Gaussian noise impulse response:
    duration 1.5s, decay rate 4.0.
    """
    rng = np.random.default_rng(seed)
    n_samples = int(np.round(duration * sr))
    t = np.linspace(0, duration, n_samples, endpoint=False)
    ir = rng.normal(0, 1, n_samples) * np.exp(-decay * t)
    norm = np.sqrt(np.sum(ir**2))
    if norm > 0:
        ir /= norm
    return ir


def fft_convolve(x: np.ndarray, h: np.ndarray) -> np.ndarray:
    """
    Fast FFT convolution keeping the length of x.
    """
    n = len(x) + len(h) - 1
    n_fft = 1 << (n - 1).bit_length()
    X = np.fft.rfft(x, n_fft)
    H = np.fft.rfft(h, n_fft)
    y = np.fft.irfft(X * H, n_fft)
    return y[: len(x)]


def render_backing(total_d16: int, total_samples: int, sr: int = SAMPLE_RATE) -> Tuple[np.ndarray, np.ndarray]:
    """
    Render backing chords and bass line.
    One chord every 4 beats (16 sixteenths).
    """
    chords_buf = np.zeros(total_samples)
    bass_buf = np.zeros(total_samples)

    num_chords = int(np.ceil(total_d16 / 16.0))
    for i in range(num_chords):
        chord_triad, bass_root = CHORD_PROGRESSION[i % len(CHORD_PROGRESSION)]
        onset16 = i * 16
        start_samp = int(np.round(onset16 * SIXTEENTH_SEC * sr))

        # Chord triad (partials [1, 0.3], amp 0.12)
        chord_sig = np.zeros(int(np.round(16 * SIXTEENTH_SEC * sr)))
        for chord_pitch in chord_triad:
            chord_sig += synth_note(chord_pitch, 16, [1.0, 0.3], 0.12, sr)

        # Bass root (partials [1, 0.1], amp 0.25)
        bass_sig = synth_note(bass_root, 16, [1.0, 0.1], 0.25, sr)

        # Mix into buffers
        for buf, sig in [(chords_buf, chord_sig), (bass_buf, bass_sig)]:
            n_samp = len(sig)
            if start_samp < total_samples:
                end_samp = min(start_samp + n_samp, total_samples)
                buf[start_samp:end_samp] += sig[: end_samp - start_samp]

    return chords_buf, bass_buf


def measure_rms(signal: np.ndarray) -> float:
    """
    Compute Root-Mean-Square (RMS) amplitude of signal.
    """
    if len(signal) == 0:
        return 0.0
    return float(np.sqrt(np.mean(signal**2)))


def render_mix(
    events: List[Tuple[int, int, int]],
    upper: List[int] = None,
    lower: List[int] = None,
    mode: str = "quantum",
    add_reverb: bool = True,
    target_rms: float = TARGET_RMS,
    sr: int = SAMPLE_RATE,
) -> np.ndarray:
    """
    Render full audio mix according to Section 2.8:
    mode in {"quantum", "independent", "original"}.
    Loudness-matches result to target_rms.
    """
    total_d16 = events[-1][2] + events[-1][1]
    # Add 1.5s ring-out tail
    tail_samples = int(np.round(1.5 * sr))
    total_samples = int(np.round(total_d16 * SIXTEENTH_SEC * sr)) + tail_samples

    # 1. Melody track (partials [1, 0.45, 0.15], amp 0.35)
    melody_buf = render_voice_track(events, total_samples, [1.0, 0.45, 0.15], 0.35, sr)

    # 2. Harmony voices (partials [1, 0.5, 0.25], amp 0.18)
    harmony_buf = np.zeros(total_samples)
    if mode in ("quantum", "independent") and upper is not None and lower is not None:
        upper_notes = [(u, d16, onset) for u, (_, d16, onset) in zip(upper, events)]
        lower_notes = [(l, d16, onset) for l, (_, d16, onset) in zip(lower, events)]
        upper_buf = render_voice_track(upper_notes, total_samples, [1.0, 0.5, 0.25], 0.18, sr)
        lower_buf = render_voice_track(lower_notes, total_samples, [1.0, 0.5, 0.25], 0.18, sr)
        harmony_buf = upper_buf + lower_buf

    lead_section = melody_buf + harmony_buf

    # 3. Optional Reverb on melody and harmony (wet mix 0.35)
    if add_reverb:
        ir = create_reverb_ir(sr=sr)
        reverb_tail = fft_convolve(lead_section, ir)
        lead_section = 0.65 * lead_section + 0.35 * reverb_tail

    # 4. Backing chords and bass
    chords_buf, bass_buf = render_backing(total_d16, total_samples, sr)
    full_mix = lead_section + chords_buf + bass_buf

    # 5. Strict RMS Loudness Matching
    current_rms = measure_rms(full_mix)
    if current_rms > 1e-9:
        scale_factor = target_rms / current_rms
        matched_mix = full_mix * scale_factor
    else:
        matched_mix = full_mix

    peak = float(np.max(np.abs(matched_mix)))
    if peak >= 1.0:
        raise RuntimeError(f"Clipping detected after RMS matching: peak={peak:.4f} >= 1.0")

    return matched_mix


def write_wav(path: str, signal: np.ndarray, sr: int = SAMPLE_RATE) -> None:
    """
    Write 16-bit mono PCM WAV file.
    """
    # Clip to avoid overflow
    clipped = np.clip(signal, -0.99999, 0.99999)
    int16_samples = (clipped * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(int16_samples.tobytes())
