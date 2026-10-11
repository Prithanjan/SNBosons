"""
Multi-track standard MIDI file generation.
Section 2.9 of Agent PRD.
"""

from typing import List, Tuple
import mido

TICKS_PER_BEAT = 480
TEMPO_BPM = 100

CHORD_PROGRESSION: List[Tuple[List[int], int]] = [
    ([48, 52, 55], 36),  # C major (C3, E3, G3), C2 bass
    ([53, 57, 60], 41),  # F major (F3, A3, C4), F2 bass
    ([55, 59, 62], 43),  # G major (G3, B3, D4), G2 bass
    ([48, 52, 55], 36),  # C major (C3, E3, G3), C2 bass
]


def _build_timed_track(
    note_events: List[Tuple[int, int, int, int]], channel: int, track_name: str = ""
) -> mido.MidiTrack:
    """
    Build a single MIDI track from a list of (pitch, on_tick, off_tick, velocity).
    Automatically computes delta times.
    """
    track = mido.MidiTrack()
    if track_name:
        track.append(mido.MetaMessage("track_name", name=track_name, time=0))

    # Flatten into (tick, type, pitch, vel)
    timed_events = []
    for pitch, on_tick, off_tick, vel in note_events:
        timed_events.append((on_tick, "note_on", pitch, vel))
        timed_events.append((off_tick, "note_off", pitch, 0))

    # Sort by tick; note_off before note_on at identical tick
    timed_events.sort(key=lambda x: (x[0], 0 if x[1] == "note_off" else 1))

    last_tick = 0
    for tick, ev_type, pitch, vel in timed_events:
        delta = max(0, tick - last_tick)
        track.append(mido.Message(ev_type, note=pitch, velocity=vel, time=delta, channel=channel))
        last_tick = tick

    return track


def write_midi(
    path: str,
    events: List[Tuple[int, int, int]],
    upper: List[int] = None,
    lower: List[int] = None,
    tempo_bpm: int = TEMPO_BPM,
) -> None:
    """
    Write Type 1 multi-track MIDI file:
    - Track 0 (Channel 0): Lead Melody
    - Track 1 (Channel 1): Backing Chords
    - Track 2 (Channel 2): Bass
    - Track 3 (Channel 3): Upper and Lower Harmony Counterpoint
    Ticks per beat 480.
    Note-on: onset16 * 120 ticks.
    Note-off: (onset16 + d16) * 120 - 10 ticks.
    """
    mid = mido.MidiFile(ticks_per_beat=TICKS_PER_BEAT)

    # Track 0: Tempo meta and Lead Melody
    melody_note_events = []
    for pitch, d16, onset16 in events:
        on_tick = onset16 * 120
        off_tick = (onset16 + d16) * 120 - 10
        melody_note_events.append((pitch, on_tick, off_tick, 95))

    melody_track = _build_timed_track(melody_note_events, channel=0, track_name="Melody")
    # Insert tempo meta message at beginning
    melody_track.insert(0, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(tempo_bpm), time=0))
    mid.tracks.append(melody_track)

    total_d16 = events[-1][2] + events[-1][1]
    num_chords = int((total_d16 + 15) // 16)

    # Track 1: Backing Chords (Channel 1)
    chords_note_events = []
    for i in range(num_chords):
        chord_triad, _ = CHORD_PROGRESSION[i % len(CHORD_PROGRESSION)]
        onset16 = i * 16
        on_tick = onset16 * 120
        off_tick = (onset16 + 16) * 120 - 10
        for cp in chord_triad:
            chords_note_events.append((cp, on_tick, off_tick, 65))
    chords_track = _build_timed_track(chords_note_events, channel=1, track_name="Chords")
    mid.tracks.append(chords_track)

    # Track 2: Bass (Channel 2)
    bass_note_events = []
    for i in range(num_chords):
        _, bass_root = CHORD_PROGRESSION[i % len(CHORD_PROGRESSION)]
        onset16 = i * 16
        on_tick = onset16 * 120
        off_tick = (onset16 + 16) * 120 - 10
        bass_note_events.append((bass_root, on_tick, off_tick, 80))
    bass_track = _build_timed_track(bass_note_events, channel=2, track_name="Bass")
    mid.tracks.append(bass_track)

    # Track 3: Harmony Voices (Channel 3)
    if upper is not None and lower is not None:
        harmony_note_events = []
        for u, (_, d16, onset16) in zip(upper, events):
            on_tick = onset16 * 120
            off_tick = (onset16 + d16) * 120 - 10
            harmony_note_events.append((u, on_tick, off_tick, 75))
        for l, (_, d16, onset16) in zip(lower, events):
            on_tick = onset16 * 120
            off_tick = (onset16 + d16) * 120 - 10
            harmony_note_events.append((l, on_tick, off_tick, 75))
        harmony_track = _build_timed_track(harmony_note_events, channel=3, track_name="Harmony")
        mid.tracks.append(harmony_track)

    mid.save(path)
