import numpy as np
import lzma
import zlib
from acoustic_config import (
    SAMPLE_RATE, SYMBOL_DURATION, FREQ_TABLE,
    SYMBOL_BITS, WINDOW_FUNCTION, SILENCE_BETWEEN_PACKETS)

# 64 FSK
SYNC_BITS = "11111000001111100000"  # same as encoder
bits_per_symbol = SYMBOL_BITS #64-FSK

# threshold (tune later)
SILENCE_THRESHOLD = 0.003

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
            
    return bitstream


# ==============================
#   BITSTREAM => file rebuild
# ===============================

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

    print("\n[Decoder] Coverting bits to bytes....")

    raw = bytearray()
    i = 0
    while True:
        start = bitstream.find(SYNC_BITS, i)
        if start == -1:
            break
        i = start + len(SYNC_BITS)

        # find the start of the fllwing packet (end of the current packet)
        end = bitstream.find(SYNC_BITS, i)
        if end == -1:
            packet_bits = bitstream[i:] # last packet
        else:
            packet_bits = bitstream[i:end]

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

    while index < len(raw):

        # read length
        if index >= len(raw):
            break

        chunk_len = raw[index]
        index += 1

        # extract data
        data_end = index + chunk_len

        if data_end > len(raw):
            print("[ERROR] Packet truncated! Stopping now.")
            break
        
        chunk_data = raw[index:data_end]
        index = data_end


        # extract crc32
        if index + 4 > len(raw):
            print("[ERROR] Missing CRC at end. Stopping now.")
            break
            
        crc_bytes = raw[index:index+4]
        index += 4

        received_crc = int.from_bytes(crc_bytes, "big")
        computed_crc = zlib.crc32(chunk_data)

        # skipping packet if crc mismatches
        if received_crc != computed_crc:
            print("[WARNING] CRC mismatch: Skipping packet.")
            continue

        # append valid packet data

        reconstructed.extend(chunk_data)

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