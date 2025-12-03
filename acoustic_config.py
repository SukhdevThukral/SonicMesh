# ===============================
#  SonicMesh Acoustic Constants
# ===============================

SAMPLE_RATE = 44100

#symbol = 4bits
SYMBOL_DURATION = 0.01 #10ms per symbol
AMPLITUDE = 0.5 #AUDIO APMLITUDE

#16-FSK ultrasonic frequencies (mostly inaudible)
FREQ_TABLE = [
    17500, 17800, 18100, 18400,
    18700, 19000, 19300, 19600,
    19900, 20200, 20500, 20800,
    21100, 21400, 21700, 22000
]

# packet chunk size
CHUNK_SIZE = 128