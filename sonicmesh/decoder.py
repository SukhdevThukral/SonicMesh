import numpy as np
import lzma
import zlib
from .acoustic_config import (
    SAMPLE_RATE, SYMBOL_DURATION, FREQ_TABLE,
    SYMBOL_BITS, WINDOW_FUNCTION, SILENCE_BETWEEN_PACKETS)

# 64 FSK

bits_per_symbol = SYMBOL_BITS 

# synchronisation pattern (4 symbols: 63,0,63,0).

sync_indices = [63,0,63,0]
SYNC_BITS = ''.join(f"{i:0{bits_per_symbol}b}" for i in sync_indices)

SILENCE_THRESHOLD = 0.05


# ==========================
#  FFT-BASED FSK DECODER
# ==========================


def decode_symbol(chunk):
    """
    Decode a single chunk of audio to 5 bits (0-31 index)

    Steps:
    1. Applying a window function to reduce spectral leakage
    2. performing fft to get frequency spectrum
    3. find the frequency with maximum magnitude
    4. if the peak is below the "SILENCE_THRESHOLD", return None(silence)
    5. map peak frequency to closest fsk frequency index
    6. convert index to a bits strin of length "bits+per_symbol"
    """

    n_fft = len(chunk) * 8

    # applying window
    windowed = chunk  * WINDOW_FUNCTION(len(chunk))

    fft = np.fft.rfft(windowed, n=n_fft)
    magnitudes = np.abs(fft)

    freqs = np.fft.rfftfreq(n_fft, 1 / SAMPLE_RATE)

    freq_min = FREQ_TABLE[0] -500
    freq_max = FREQ_TABLE[-1] + 500
    freq_mask = (freqs >= freq_min) & (freqs <= freq_max)

    valid_mags = magnitudes[freq_mask]
    valid_freqs = freqs[freq_mask]

    if len(valid_mags) == 0:
        return None

    peak_idx = np.argmax(valid_mags)
    peak_mag = valid_mags[peak_idx]
    peak_freq = valid_freqs[peak_idx]

    mean_mag = np.mean(valid_mags)
    if peak_mag < SILENCE_THRESHOLD or peak_mag < mean_mag*2.5:
        return None
    
    # mapping to closest fsk frqncy indedx

    freq_diffs = np.abs(np.array(FREQ_TABLE)- peak_freq)

    idx = int(np.argmin(freq_diffs))
    # closest_freq = FREQ_TABLE[idx]
    
    bits = f"{idx:0{bits_per_symbol}b}"
    return bits
    
def decode_signal(signal):
    """
    Convert the full audio signal into a continous bitstream.

    Splitting the signal into fixed size symbol windows, and decodes each
    window, concatenates the resulting btstring.
    """

    sample_per_symbol = int(SAMPLE_RATE*SYMBOL_DURATION)

    if len(signal) <sample_per_symbol:
        return ""
    
    #quick energy check
    # total_energy = float(np.sum(np.abs(signal)))
    # max_amp = float(np.max(np.abs(signal)))

    #previewing first 50 samples for sanity (pritns truncated)
    
    decode_symbol.count = 0

    bitstream = ""
    symbols_decoded = 0
    symbols_skipped = 0

    for i in range(0, len(signal), sample_per_symbol):
        chunk = signal[i:i + sample_per_symbol]
        if len(chunk) < sample_per_symbol:
            break
        
        #normalizing chunk before FFT
        bits = decode_symbol(chunk)
        if bits is not None:
            bitstream+=bits
            symbols_decoded+=1
        else:
            symbols_skipped+=1

    # total_chunks = symbols_decoded + symbols_skipped

    # trimming extra bits to form full symbols        
    if len(bitstream) % bits_per_symbol != 0:
        bitstream = bitstream[:-len(bitstream)%bits_per_symbol]

    return bitstream


# ==============================
#   BITSTREAM => file rebuild
# ===============================


def find_sync(bits, min_match = 0.7, pattern = '111111000000111111000000'):
    """
    Searching for the synchronisation seq in the bitstream.
    Returning the index of the best match if above the given threshold,
    otherwise reutnring -1
    """
    
    
    L = len(pattern)
    best_pos = -1
    best_score = 0

    for i in range(len(bits)-L):
        window = bits[i:i+L]
        score = sum(a==b for a,b in zip(window,pattern))

        if score > best_score:
            best_score = score
            best_pos = i

    return best_pos if best_score >= L*min_match else -1
    
def decode_file(bitstream, output_path):
    """
    convert a coninuous bitstream into a reconstructed file

    steps:
    1. split bitstream into packets using SYNC_BITS as seperator
    2. convert packet bitstr to bytes
    3. validating packet length and CRC32
    4. Reconstruct originial compressed file
    5. decompressing using LZMA and write to disk
    """
    

    pattern = SYNC_BITS
    sync_pos = find_sync(bitstream, pattern=pattern)


    bitstream = bitstream[sync_pos:]
    while bitstream.startswith(SYNC_BITS):
        bitstream = bitstream[len(SYNC_BITS):]

    raw = bytearray()
    i = 0
    packet_count = 0
    
    # extracting packets until stream ends
    while True:
        next_sync = bitstream.find(SYNC_BITS, i)
        if next_sync == -1:
            packet_bits= bitstream[i:]
        else:
            packet_bits = bitstream[i:next_sync]
            i = next_sync + len(SYNC_BITS)

        if len(packet_bits) <8:
            if next_sync == -1:
                break
            continue

        # trimming bits tht dont form full bytes
        extra = len(packet_bits) % 8
        if extra != 0:
            packet_bits = packet_bits[:-extra]

        #convert bits into bytes
        for j in range(0, len(packet_bits), 8):
            byte = packet_bits[j:j+8]
            raw.append(int(byte,2))

        packet_count += 1
        
        if next_sync == -1:
            break
    
    # ==============================
    # parse packets and verify CRC
    # ==============================
    index = 0
    reconstructed = bytearray()
    valid_packets = 0
    crc_errors = 0

    # PACKET STRCUTURE:
    # [1 byte length][data][CRC32 4 bytes]

    while index+2 <= len(raw):
        chunk_len = int.from_bytes(raw[index:index+2], "big")
        index += 2

        data_end = index + chunk_len

        if data_end > len(raw):
            break
        
        chunk = raw[index:data_end]
        index = data_end


        # extract crc32
        if index + 4 > len(raw):
            break
            
        crc_bytes = raw[index:index+4]
        index += 4

        received_crc = int.from_bytes(crc_bytes, "big")
        computed_crc = zlib.crc32(chunk)

        # skipping packet if crc mismatches
        if received_crc != computed_crc:
            crc_errors+=1
            continue

        # append valid packet data

        reconstructed.extend(chunk)
        valid_packets +=1
    # ==========================
    # decompress and save file
    # ==========================
    try:
        decompressed = lzma.decompress(reconstructed)
    except Exception as e:
        print(f"[ERROR] Decompression failed. {e}.")
        return
    
    with open(output_path, "wb") as f:
        f.write(decompressed)
