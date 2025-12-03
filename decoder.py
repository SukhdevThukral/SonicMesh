import numpy as np
import zlib
from acoustic_config import (
    SAMPLE_RATE, SYMBOL_DURATION, FREQ_TABLE,
    SYMBOL_BITS, WINDOW_FUNCTION, SILENCE_BETWEEN_PACKETS)

# 64 FSK
bits_per_symbol = SYMBOL_BITS #64-FSK

# threshold (tune later)
SILENCE_THRESHOLD = 0.003

# ==========================
#  FFT-BASED FSK DECODER
# ==========================


def decode_symbol(chunk):
    """
    Decode a single chunk of audio to 5 bits (0-31 index)
    """

    # applying window
    windowed = chunk  * WINDOW_FUNCTION(len(chunk))

    fft = np.fft.rfft(windowed)
    magnitudes = np.abs(fft)

    peak_idx = np.argmax(magnitudes)
    peak = magnitudes[peak_idx]

    if peak < SILENCE_THRESHOLD:
        return None
    
    freqs = np.fft.rfftfreq(len(chunk), 1 / SAMPLE_RATE)
    peak_freq = freqs[peak_idx]

    # finding closest fsk frqncy indedx
    idx = int(np.argmin(np.abs(np.array(FREQ_TABLE) - peak_freq)))
    idx = max(0, min(idx, len(FREQ_TABLE)-1))
    
    #conveting index to 6-bit string
    bits = f"{idx:0{bits_per_symbol}b}"
    return bits
    
def decode_signal(signal):
    """
    converting raw audio samples + bitstream of all symbols,
    accounting for silence between packets
    """

    sample_per_symbol = int(SAMPLE_RATE*SYMBOL_DURATION)

    bitstream = ""

    for i in range(0, len(signal), sample_per_symbol):
        chunk = signal[i:i + sample_per_symbol]
        if len(chunk) < sample_per_symbol:
            break
        
        #normalizing chunk before FFT
        chunk = chunk / (np.max(np.abs(chunk))+ 1e-9)
        bits = decode_symbol(chunk)
        if bits is not None:
            bitstream+=bits
    if len(bitstream) % bits_per_symbol != 0:
        bitstream = bitstream[:-len(bitstream)%bits_per_symbol]
            
    return bitstream


# ==============================
#   BITSTREAM => file rebuild
# ===============================

def decode_file(bitstream, output_path):

    print("\n[Decoder] Coverting bits to bytes....")
    extra_bits = len(bitstream) % 8 
    if extra_bits != 0:
        bitstream = bitstream[extra_bits:]

    raw = bytearray()
    for i in range(0, len(bitstream), 8):
        byte =bitstream[i:i+8]
        raw.append(int(byte, 2))

    print("[Decoder] Total received bytes:", len(raw))
    
    #now parsing packets
    index = 0
    reconstructed = bytearray()

    # PACKET STRCUTURE:
    # [1 byte length][data][CRC32 4 bytes]

    while index < len(raw):

        # read length
        if index >= len(raw):
            break

        chunk_len = raw[index]
        index += 1

        #read data
        data_end = index + chunk_len

        if data_end > len(raw):
            print("[ERROR] Packet truncated! Stopping now.")
            break
        
        chunk_data = raw[index:data_end]
        index = data_end


        #read crc32
        if index + 4 > len(raw):
            print("[ERROR] Missing CRC at end. Stopping now.")
            break
            
        crc_bytes = raw[index:index+4]
        index += 4

        received_crc = int.from_bytes(crc_bytes, "big")
        computed_crc = zlib.crc32(chunk_data)

        #CHECK CRC
        if received_crc != computed_crc:
            print("[WARNING] CRC mismatch: Skipping packet.")
            continue

        # append valid chunk

        reconstructed.extend(chunk_data)

    print("[Decoder] Total reconstructed bytes before decompress:", len(reconstructed))

    #decompress
    try:
        decompressed = zlib.decompress(reconstructed)
    except:
        print("[ERROR] Decompression failed. File corrupted.")
        return
    
    #write file
    f = open(output_path, "wb")
    f.write(decompressed)
    f.close()

    print("File saved to:", output_path)