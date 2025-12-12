"""
SonicMesh - Acoustic Ultrasonic Data Transfer Library
-----------------------------------------------------

This package provides:
- High-level APIs for sending text and files over sound
- Ultrasonic FSK encoder (64-FSK)
- FFT-based ultrasonic decoder
- WAV utilities for saving/reading transmissions

Modules exposed at top-level:
    encode_message, encode_file
    transmit, transmitf
    decode_wav
    decode_signal, decode_file
"""

from .encoder import (
    encode_message,
    encode_file,
)

from .transmit import(
    transmit, transmitf,
)

from .decode_wav import decode_wav

from .decoder import (
    decode_signal, decode_file,
)

# re exporting key config consts
from .acoustic_config import(
    SAMPLE_RATE, 
    SYMBOL_DURATION,
    SYMBOL_BITS,
    FREQ_TABLE,
)

__all__ = [
    "encode_message", "encode_file",
    "transmit", "transmitf",
    "decode_wav",
    "decode_signal", "decode_file",
    "SAMPLE_RATE", "SYMBOL_DURATION",
    "SYMBOL_BITS", "FREQ_TABLE",
]