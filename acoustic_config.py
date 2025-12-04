# ===============================
#  SonicMesh Acoustic Constants
# ===============================

import numpy as np 


SAMPLE_RATE = 44100

# SYMBOL PROPERTIES
SYMBOL_BITS = 6
SYMBOL_DURATION = 0.01 # 2.5x faster
AMPLITUDE = 0.45  # AUDIO APMLITUDE

# FFT optimization
WINDOW_OVERLAP = 0.25
WINDOW_FUNCTION = np.hanning # windowing function to reduce spectral leakage

#*64-FSK ultrasonic frequencies (mostly inaudible)
# keeping above ~20kHz to reduce audiblity, upper limit ~22kHz for most speakers
FREQ_TABLE = np.linspace(15000, 22000, 64 ,dtype=int).tolist()

# packet chunk size
CHUNK_SIZE = 800

# audio post-processing
SILENCE_BETWEEN_PACKETS = 0 # 4 ms silence to seperate packets for FFT detection

# Note:
# reduced symbol duration + slight overlap reduces total audio length
# lower amplitude + higher start frequency reduces the audiblity even further.
# window function and silence help reduce CRC mismatches