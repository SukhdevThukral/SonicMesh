import numpy as np
import zlib

#======================
#acoustic parameters
#======================
SAMPLE_RATE = 44100
SYMBOL_DURATION = 0.01 #10ms per symbol (4bits)


# implementing 16-FSK frequency table (each represents 4bits = 1 symbol)
# Range: 17kHz - 20kHz (mostly inaudible)

FREQ_TABLE = [
    17500, 17800, 18100, 18400,
    18700, 19000, 19300, 19600, 
    19900, 20200, 20500, 20800,
    21100, 21400, 21700, 22000
]

#packet size (in bytes)
CHUNK_SIZE = 128

# ===========================
#  encoding a symbol (4bits)
# ===========================

def encode_symbol(bits4):
    """
    encode 4 bits (string) into an ultrasonic tone.
    """

    idx = int(bits4, 2)
    freq = FREQ_TABLE[idx]

    t = np.linspace(0, SYMBOL_DURATION, int(SAMPLE_RATE*SYMBOL_DURATION), endpoint=False)

    tone = 0.5*np.sin(2*np.pi*freq*t)
    return tone
    
def encode_bits_16fsk(bitstream):
    tones = []
    for i in range(0, len(bitstream),4):
        chunk = bitstream[i:i+4]
        if len(chunk) < 4:
            chunk = chunk.ljust(4,'0') #pad
        tone = encode_symbol(chunk)
        tones.append(tone)

    signal =  np.concatenate(tones)
    return signal.astype(np.float32)

# file + packets
def packetize_file(path):
    
    f = open(path, "rb")
    raw = f.read()
    f.close()

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

    # pad to multiple of 4(since 16-FSK)
    if len(bitstream) %4 != 0:
        pad_len= 4 - (len(bitstream)%4)
        bitstream+= "0" * pad_len

    print("[INFO] Total bits:", len(bitstream))
    return bitstream


# high level file encoder
def encode_file(path):
    packets = packetize_file(path)
    bitstream = packets_to_bits(packets)
    audio = encode_bits_16fsk(bitstream)
    return audio

# text msg encoder
def encode_message(msg):

    bitstream = ''

    for char in msg:
        bitstream += f"{ord(char):08b}"

    # pad for 16-FSK
    if len(bitstream) % 4 != 0:
        pad_len = 4 - (len(bitstream) % 4)
        bitstream += "0" * pad_len

    return encode_bits_16fsk(bitstream)