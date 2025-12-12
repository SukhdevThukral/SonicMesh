# ===================================
#  SonicMesh Acoustic Configurations
# ===================================

import numpy as np 

# base audio sample rate being used for tone synthesis.
SAMPLE_RATE = 44100

# =======================
# Symbol Encoding Props
# =======================
SYMBOL_BITS = 6

 # Duration of single FSK symbol (in s)
 # Shorter durations = faster transfers but harder decoding-
SYMBOL_DURATION = 0.011

AMPLITUDE = 0.45  

# =========================
# FFT / Windowing Settings
# =========================

WINDOW_OVERLAP = 0.4
WINDOW_FUNCTION = np.hanning # windowing function to reduce spectral leakage

#*64-FSK ultrasonic frequencies (mostly inaudible)
# keeping between 19kHz and 22kHz.
FREQ_TABLE = np.linspace(19000, 22000, 64 ,dtype=int).tolist()

# ==========================
# Packetization settings
# ==========================
# no. of payload bytes carried per packet before CRC is added.
CHUNK_SIZE = 800

# ===============================
# Transmission spacing
# ===============================
# silence inserted b/w packets (in s), been set to zero for speed
# unless debugging CRC or syncinc behavior.

SILENCE_BETWEEN_PACKETS = 0 

# Note:
# reduced symbol duration + slight overlap reduces total audio length
# lower amplitude + higher start frequency reduces the audiblity even further.
# window function and silence help reduce CRC mismatches