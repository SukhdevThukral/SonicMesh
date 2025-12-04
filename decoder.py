import numpy as np
import lzma
import zlib
from acoustic_config import (
    SAMPLE_RATE, SYMBOL_DURATION, FREQ_TABLE,
    SYMBOL_BITS, WINDOW_FUNCTION, SILENCE_BETWEEN_PACKETS)

# 64 FSK

bits_per_symbol = SYMBOL_BITS 
sync_indices = [63,0,63,0]
SYNC_BITS = ''.join(f"{i:0{bits_per_symbol}b}" for i in sync_indices)

# threshold (tune later)
SILENCE_THRESHOLD = 1e-6

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

    # applying window
    windowed = chunk  * WINDOW_FUNCTION(len(chunk))

    fft = np.fft.rfft(windowed)
    magnitudes = np.abs(fft)

    peak_idx = np.argmax(magnitudes)
    peak = magnitudes[peak_idx]

    if peak < SILENCE_THRESHOLD:
        return None
    
    mean_mag = np.mean(magnitudes)
    if peak < mean_mag*4:
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
    Convert the full audio signal into a continous bitstream.

    Steps:
    1. split the audio into chunks, each representing one symbol
    2. normalise each chunk for fft
    3. decode each symbol to bits
    4. remove extra bits tht dont form a full symbol at the end
    """

    sample_per_symbol = int(SAMPLE_RATE*SYMBOL_DURATION)
    print(f"[DEBUG] signal len =  {len(signal)} samples, sample_per_symbol = {sample_per_symbol}")

    if len(signal) <sample_per_symbol:
        print("[DEBUG] signal shorter than one symbol -< no symbols decoded")
        return ""
    
    #quick energy check
    total_energy = float(np.sum(np.abs(signal)))
    max_amp = float(np.max(np.abs(signal)))
    print(f"[DEBUG] total_energy= {total_energy:.3f}. max_amp = {max_amp:.6f}")

    #previewing first 50 samples for sanity (pritns truncated)
    print("[DEBUG] first sampels: ", np.array2string(signal[:50], precision=3, separator=", "))
    
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

    # trimming extra bits to form full symbols        
    if len(bitstream) % bits_per_symbol != 0:
        bitstream = bitstream[:-len(bitstream)%bits_per_symbol]
    print(f"[DEBUG] final bitstream length = {len(bitstream)} bits")
    if len(bitstream) > 0:
        print("[DEBUG] bitstream sample:", bitstream[:200])
            
    return bitstream


# ==============================
#   BITSTREAM => file rebuild
# ===============================

def find_sync(bitstream, sync_indices, bits_per_symbol):
    sync_len = len(sync_indices)
    target_sync = sync_indices

    for offset in range(bits_per_symbol):
        symbols = []
        for i in range(offset, len(bitstream) - bits_per_symbol + 1, bits_per_symbol):
            sym = int(bitstream[i:i+bits_per_symbol],2)
            symbols.append(sym)
        
        repeats_needed = 2
        total_needed = sync_len * repeats_needed
        if len(symbols) < total_needed:
            continue

        for s_idx in range(len(symbols) - total_needed+1):
            match = True
            for r in range(repeats_needed):
                start = s_idx + r*sync_len
                if symbols[start:start+sync_len] != target_sync:
                    match=False
                    break
            if match:
                return offset + (s_idx + repeats_needed*sync_len)*bits_per_symbol
            
    return -1

def decode_file(bitstream, output_path):
    """
    convert a coninuous bitstream into a reconstructed file

    steps:
    1. split bitstream into packets using SYNC_BITS as seperator
    2. convert bits to bytes
    3. validating packet length and CRC32
    4. Reconstruct originial compressed file
    5. decompressing using LZMA and write to disk
    """
    
    # start = bitstream.find(SYNC_BITS)
    # if start == -1:
    #     print("[ERROR] No sync found in bitstream")
    #     return
    # bitstream = bitstream[start + len(SYNC_BITS):]
    # packets_bits = bitstream.split(SYNC_BITS)

    # --------- symbool aligned sync search ----
    print("\n [DEBUG] bitstream length:", len(bitstream))
    print("[DEBUG] bitstream head(200):", bitstream[:200])

    sync_bits_full = ''.join(f"{i:0{bits_per_symbol}b}" for i in sync_indices)
    sync_len_symbols = len(sync_indices)
    target_sync = [int(sync_bits_full[k:k+bits_per_symbol], 2) for k in range(0, len(sync_bits_full), bits_per_symbol)]

    found = False
    best = None 

    for offset in range(bits_per_symbol):
        symbols = []
        for i in range(offset, len(bitstream) - bits_per_symbol + 1, bits_per_symbol):
            sym = int(bitstream[i:i+bits_per_symbol],2)
            symbols.append(sym)

        repeats_needed = 3
        total_needed = sync_len_symbols * repeats_needed
        if len(symbols) < total_needed:
            continue

        for s_idx in range(0, len(symbols) - total_needed + 1):
            match = True
            for r in range(repeats_needed):
                start = s_idx + r* sync_len_symbols
                if symbols[start:start + sync_len_symbols] != target_sync:
                    match =  False
                    break
            if match:
                    bit_pos = offset + (s_idx + repeats_needed * sync_len_symbols) * bits_per_symbol
                    best = (offset, bit_pos)
                    found = True
                    break
        if found:
            break
    if not found:
        print("[DEBUG] No symbol-aligned SYNC found (tried offsets). failing back to naive search.") 
        naive = bitstream.find(SYNC_BITS)
        print("[DEBUG] naive string search index:", naive)
        if naive == -1:
            print("[ERROR] No SYNC. Returning.")
            return
        else:
            bitstream = bitstream[naive+ len(SYNC_BITS):]
    else:
        offset, bit_start = best
        print(f"[DEBUG] sync found: offset = {offset}, payload_bit_start={bit_start}")
        bitstream = bitstream[bit_start:]

    # === symbol-aligned finder: end  ========================================================
    print("\n[Decoder] Coverting bits to bytes....")

    raw = bytearray()
    i = 0
    while True:
        start = bitstream.find(SYNC_BITS, i)
        if start == -1:
            break
        i = start + len(SYNC_BITS)

        
        end = bitstream.find(SYNC_BITS, i)
        
        if end != -1:
            packet_bits = bitstream[i:end] 
        else:
            packet_bits = bitstream[i:]

        # trimming bits tht dont form full bytes
        extra = len(packet_bits) % 8
        if extra != 0:
            packet_bits = packet_bits[:-extra]

        #convert bits into bytes
        for j in range(0, len(packet_bits), 8):
            byte = packet_bits[j:j+8]
            raw.append(int(byte,2))
        
        if end == -1:
            break

        i = end

    # for packet_bits in packets_bits:
    #     extra = len(packet_bits) % 8
    #     if extra != 0:
    #         packet_bits = packet_bits[:-extra]

    #     for i in range(0, len(packet_bits), 8):
    #         byte = packet_bits[i:i+8]
    #         raw.append(int(byte, 2))

    print("[Decoder] Total received bytes:", len(raw))
    
    # ==============================
    # parse packets and verify CRC
    # ==============================
    index = 0
    reconstructed = bytearray()

    # PACKET STRCUTURE:
    # [1 byte length][data][CRC32 4 bytes]

    while index+2 <= len(raw):
        chunk_len = int.from_bytes(raw[index:index+2], "big")
        index += 2

        data_end = index + chunk_len

        if data_end > len(raw):
            print("[ERROR] Packet truncated! Stopping now.")
            break
        
        chunk = raw[index:data_end]
        index = data_end


        # extract crc32
        if index + 4 > len(raw):
            print("[ERROR] Missing CRC at end. Stopping now.")
            break
            
        crc_bytes = raw[index:index+4]
        index += 4

        received_crc = int.from_bytes(crc_bytes, "big")
        computed_crc = zlib.crc32(chunk)

        # skipping packet if crc mismatches
        # if received_crc != computed_crc:
        #     print("[WARNING] CRC mismatch: Skipping packet.")
        #     continue

        # append valid packet data

        reconstructed.extend(chunk)

    print("[Decoder] Total reconstructed bytes before decompress:", len(reconstructed))

    # ==========================
    # decompress and save file
    # ==========================
    try:
        decompressed = lzma.decompress(reconstructed)
    except:
        print("[ERROR] Decompression failed. File corrupted.")
        return
    
    with open(output_path, "wb") as f:
        f.write(decompressed)

    print("File saved to:", output_path)