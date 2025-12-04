import numpy as np
import lzma
import zlib
from acoustic_config import(
    SAMPLE_RATE, SYMBOL_DURATION, AMPLITUDE, 
    FREQ_TABLE, CHUNK_SIZE, SYMBOL_BITS,
    SILENCE_BETWEEN_PACKETS, WINDOW_FUNCTION)


sync_indices = [63,0,63,0]
sync_bits = ''.join(f"{i:0{SYMBOL_BITS}b}" for i in sync_indices)
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
    if WINDOW_FUNCTION is not None:
        tone *= WINDOW_FUNCTION(len(t))

    return tone.astype(np.float32)
    
def encode_bits_fsk(bitstream: str):
    """Stream of bits => concatenatd ultrasonic tones + silence spacings"""
    tones = []
    silence = np.zeros(int(SAMPLE_RATE*SILENCE_BETWEEN_PACKETS), dtype=np.float32)
    

    for i in range(0, len(bitstream), bits_per_symbol):
        chunk = bitstream[i:i+bits_per_symbol]
        if len(chunk) < bits_per_symbol:
            chunk = chunk.ljust(bits_per_symbol,'0') #pad

        tone = encode_symbol(chunk)
        tones.append(tone) # it would hlep FFT distinguish symbols
        if SILENCE_BETWEEN_PACKETS > 0:
            tones.append(silence)

    signal =  np.concatenate(tones)
    return signal.astype(np.float32)


# ======================================
# FILE => PACKETS => BITSTREAM => AUDIO
# ======================================

def packetize_file(path):
    
    with open(path, "rb") as f:
        raw = f.read()


    print("[INFO] Original file size:", len(raw))

    compressed = lzma.compress(raw, preset=6)
    print("[INFO] Compressed size:", len(compressed))

    packets = []

    for i in range(0, len(compressed), CHUNK_SIZE):
        chunk = compressed[i:i + CHUNK_SIZE]

        packet = bytearray()
        packet += len(chunk).to_bytes(2, "big")
        packet += chunk
        packet += zlib.crc32(chunk).to_bytes(4, "big")

        packets.append(packet)

    print("[INFO] Total packets:", len(packets))
    return packets

# packets to binary string
def packets_to_bits(packets):
    bitstream = ""

    preamble_repeats = 8
    sync_bits = ''.join(f"{i:0{bits_per_symbol}b}" for i in sync_indices)
    for p in packets:
        bitstream += sync_bits * preamble_repeats
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
    print("[DEBUG] encoder bitstream len:", len(bitstream))
    print("[DEBUG] first 200 bits (encoder):", bitstream[:200])

    #quick synth of first symbol and printing its peak freq(sanity)

    if len(bitstream) >= bits_per_symbol:
        first_symbol = bitstream[:bits_per_symbol]
        idx = int(first_symbol,2)
        freq = FREQ_TABLE[idx]
        print(f"[DEBUG] first symbol index ={idx}, freq={freq} Hz")

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
