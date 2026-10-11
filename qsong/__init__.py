"""
SNBosons / qsong package:
Quantum melody round trip, entangled harmony duet, and listening study pipeline.
"""

from .encode import (
    events_from_tune,
    encode_note,
    decode_index,
    roundtrip_note,
    roundtrip_melody,
)
from .harmony import (
    TWINKLE,
    ODE_TO_JOY,
    C_MAJOR_PITCH_CLASSES,
    get_scale_pitch_classes,
    pick,
    settings,
    duet_voices,
)
from .measure import (
    sample_bell_pair,
    measure_chsh_statistic,
    theoretical_chsh_s,
)
from .render import (
    render_mix,
    write_wav,
    measure_rms,
)
from .midi_io import (
    write_midi,
)
from .cli import (
    run_experiment,
)

__all__ = [
    "events_from_tune",
    "encode_note",
    "decode_index",
    "roundtrip_note",
    "roundtrip_melody",
    "TWINKLE",
    "ODE_TO_JOY",
    "C_MAJOR_PITCH_CLASSES",
    "pick",
    "settings",
    "duet_voices",
    "sample_bell_pair",
    "measure_chsh_statistic",
    "theoretical_chsh_s",
    "render_mix",
    "write_wav",
    "measure_rms",
    "write_midi",
    "run_experiment",
]
