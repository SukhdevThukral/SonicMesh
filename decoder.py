import numpy as np
SAMPLE_RATE = 44100
DURATION = 0.08
FREQ_0 = 17500
FREQ_1 = 18500

def decode_bit(chunk):
    """
    Decode a single chunk of audio into '0' or '1'
    """

    #computing fft of the chunk
    fft = np.fft.rfft(chunk)
    freqs = np.fft.rfftfreq(len(chunk), 1 / SAMPLE_RATE)

    #finding the frequency with maximum magnitude
    peak_idx = np.argmax(np.abs(fft))
    peak_freq = freqs[peak_idx]

    #determining the nearest frquency
    if abs(peak_freq - FREQ_1) < abs(peak_freq - FREQ_0):
        return '1'
    else:
        return '0'
    
def decode_signal(signal):
    """
    Decode a full audio signal into a single text msg
    """
    sample_per_bit = int(SAMPLE_RATE*DURATION)
    bits = ""

    for i in range(0, len(signal), sample_per_bit):
        chunk = signal[i:i + sample_per_bit]
        if len(chunk) < sample_per_bit:
            break
        bits += decode_bit(chunk)

    
    #cinvert bits to characters
    msg = ""
    for i in range(0, len(bits),8):
        byte = bits[i:i+8]
        if len(byte) == 8:
            msg += chr(int(byte,2))

    return msg

def decode_file(bits, output_path):
    byte_array = bytearray()

    #taking 8 bits at a time
    for i in range(0, len(bits), 8):
        byte_bits = bits[i:i+8]
        if len(byte_bits) == 8:
            value = int(byte_bits, 2)
            byte_array.append(value)
    
    f = open(output_path, "wb")
    f.write(byte_array)

    print("File saved to", output_path)