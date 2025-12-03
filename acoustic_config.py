# ===============================
#  SonicMesh Acoustic Constants
# ===============================

import numpy as np 


SAMPLE_RATE = 44100

# SYMBOL PROPERTIES
SYMBOL_BITS = 5
SYMBOL_DURATION = 0.02 # 2.5x faster
AMPLITUDE = 0.40  # AUDIO APMLITUDE

# FFT optimization
WINDOW_OVERLAP = 0.3
WINDOW_FUNCTION = np.hamming # windowing function to reduce spectral leakage

#*64-FSK ultrasonic frequencies (mostly inaudible)
# keeping above ~20kHz to reduce audiblity, upper limit ~22kHz for most speakers
FREQ_TABLE = np.linspace(15500, 20500, 32 ,dtype=int).tolist()

# packet chunk size
CHUNK_SIZE = 200

# audio post-processing
SILENCE_BETWEEN_PACKETS = 0.002 # 4 ms silence to seperate packets for FFT detection

# Note:
# reduced symbol duration + slight overlap reduces total audio length
# lower amplitude + higher start frequency reduces the audiblity even further.
# window function and silence help reduce CRC mismatches