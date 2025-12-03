# ===============================
#  SonicMesh Acoustic Constants
# ===============================

SAMPLE_RATE = 44100

#symbol = 6bits

SYMBOL_BITS = 6 
SYMBOL_DURATION = 0.015 #2ms per symbol
AMPLITUDE = 0.25 #AUDIO APMLITUDE

#*64-FSK ultrasonic frequencies (mostly inaudible)
# keeping above ~20kHz to reduce audiblity, upper limit ~22kHz for most speakers
import numpy as np 
FREQ_TABLE = np.linspace(20050, 22000, 64,dtype=int).tolist()

# packet chunk size
CHUNK_SIZE = 32


# switched to 64-fsk -> 6 bits per symbol