import numpy as np
import zlib
from acoustic_config import(
    SAMPLE_RATE, SYMBOL_DURATION, AMPLITUDE, 
    FREQ_TABLE, CHUNK_SIZE, SYMBOL_BITS,
    SILENCE_BETWEEN_PACKETS, WINDOW_FUNCTION)


bits_per_symbol = SYMBOL_BITS

def encode_symbol(bitchunk: str):
    """
    encode 6bits (string) into an ultrasonic tone.
    """

    idx = int(bitchunk, 2)
    freq = FREQ_TABLE[idx]

    samples = int(SAMPLE_RATE*SYMBOL_DURATION)

    t = np.linspace(0, SYMBOL_DURATION, samples, endpoint=False)

    # windowed tone to cleaner FFT peak
    tone = AMPLITUDE*np.sin(2*np.pi*freq*t)
    tone *= WINDOW_FUNCTION(len(t))

    return tone.astype(np.float32)
    
def encode_bits_fsk(bitstream: str):
    """Stream of bits => concatenatd ultrasonic tones + silence spacings"""
    tones = []
    

    for i in range(0, len(bitstream), bits_per_symbol):
        chunk = bitstream[i:i+bits_per_symbol]
        if len(chunk) < bits_per_symbol:
            chunk = chunk.ljust(bits_per_symbol,'0') #pad

        tone = encode_symbol(chunk)
        tones.append(tone) # it would hlep FFT distinguish symbols

    signal =  np.concatenate(tones)
    return signal.astype(np.float32)


# ======================================
# FILE => PACKETS => BITSTREAM => AUDIO
# ======================================

def packetize_file(path):
    
    with open(path, "rb") as f:
        raw = f.read()


    print("[INFO] Original file size:", len(raw))

    compressed = zlib.compress(raw, 9)
    print("[INFO] Compressed size:", len(compressed))

    packets = []

    for i in range(0, len(compressed), CHUNK_SIZE):
        chunk = compressed[i:i + CHUNK_SIZE]

        packet = bytearray()
        packet.append(len(chunk))
        packet.extend(chunk)

        crc = zlib.crc32(chunk)
        packet.extend(crc.to_bytes(4, "big"))

        packets.append(packet)

    print("[INFO] Total packets:", len(packets))
    return packets

# packets to binary string
def packets_to_bits(packets):
    bitstream = ""

    for p in packets:
        for byte in p:
            bitstream += f"{byte:08b}"

    # pad bitstream to full symbols
    remainder = len(bitstream) % bits_per_symbol
    if remainder  != 0:
        pad_len= bits_per_symbol - remainder
        bitstream+= "0" * pad_len

    print("[INFO] Total bits:", len(bitstream))
    return bitstream


# high level file encoder
def encode_file(path):
    packets = packetize_file(path)
    bitstream = packets_to_bits(packets)

    return encode_bits_fsk(bitstream)

# ========================================
#    TEXT MESSAGE ENCODING (simple mode)
# ========================================

def encode_message(msg: str):
    data = msg.encode("utf-8")
    length = len(data)

    header = length.to_bytes(2,"big")

    payload = header + data

    bitstream = ''.join(f"{byte:08b}" for byte in payload)

    if len(bitstream) % bits_per_symbol != 0:
        pad_len = bits_per_symbol - (len(bitstream) % bits_per_symbol)
        bitstream += "0" * pad_len

    return encode_bits_fsk(bitstream)
