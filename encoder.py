import numpy as np

SAMPLE_RATE = 44100
DURATION = 0.01


#inaudible freqs

FREQ_0 = 17500
FREQ_1 = 18500

def encode_bit(bit):
    if bit == "1":
        freq = FREQ_1
    else:
        freq = FREQ_0

    #time duration array for one bit

    t = np.linspace(0, DURATION, int(SAMPLE_RATE*DURATION), False)

    tone = 0.5 * np.sin(2*np.pi*freq*t)

    return tone
def encode_message(msg):
    #converting each char into 8bit binaries
    bits = ''
    for char in msg:
        binary = format(ord(char), '08b')
        bits += binary

    #convert each bit into an ultrasonic audio tone

    all_tones = []
    for bit in bits:
        tone = encode_bit(bit)
        all_tones.append(tone)

    signal = np.concatenate(all_tones)

    return signal