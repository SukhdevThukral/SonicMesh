# ===============================
#  SonicMesh Acoustic Constants
# ===============================

SAMPLE_RATE = 44100

#symbol = 4bits
SYMBOL_DURATION = 0.005 #10ms per symbol
AMPLITUDE = 0.5 #AUDIO APMLITUDE

#*32-FSK ultrasonic frequencies (mostly inaudible)
import numpy as np 
FREQ_TABLE = np.linspace(17000, 22000, 32,dtype=int).tolist()

# packet chunk size
CHUNK_SIZE = 128