import numpy as np
import zlib
from acoustic_config import SAMPLE_RATE, SYMBOL_DURATION, FREQ_TABLE

#important vv
bits_per_symbol = 5 #32-FSK

def decode_symbol(chunk):
    """
    Decode a single chunk of audio into '0' or '1'
    usign FFT frequency detection
    """

    #computing fft of the chunk
    fft = np.fft.rfft(chunk)
    freqs = np.fft.rfftfreq(len(chunk), 1 / SAMPLE_RATE)

    #finding the frequency with maximum magnitude
    peak_idx = np.argmax(np.abs(fft))
    peak_freq = freqs[peak_idx]

    # finding nearest freq_table index
    nearest_idx = np.argmin([abs(peak_freq - f ) for f in FREQ_TABLE])

    #conveting index to 5-bit string
    bits5 = f"{nearest_idx:05b}"
    return bits5
    
def decode_signal(signal):
    """
    Decode a full audio signal into a big bitstring
    """
    sample_per_symbol = int(SAMPLE_RATE*SYMBOL_DURATION)
    bits = ""

    for i in range(0, len(signal), sample_per_symbol):
        chunk = signal[i:i + sample_per_symbol]
        if len(chunk) < sample_per_symbol:
            break
        bit = decode_symbol(chunk)
        bits += bit

    return bits

def decode_file(bits, output_path):
    """
    Decode bitstring of PACKETIZED + COMPRESSED file.
    each packet structure:
        [LEN (1 byte)][DATA LEN bytes][CRC32 (4 bytes)]
    """

    print("[Decoder] Starting file bit parsing....")

    raw_bytes = bytearray()

    #taking 8 bits at a time
    for i in range(0, len(bits), 8):
        byte_bits = bits[i:i+8]
        if len(byte_bits) == 8:
            value = int(byte_bits, 2)
            raw_bytes.append(value)

    print("[Decoder] Total received bytes:", len(raw_bytes))
    
    #now parsing packets
    index = 0
    reconstructed = bytearray()

    while index < len(raw_bytes):

        # read length
        if index >= len(raw_bytes):
            break

        chunk_len = raw_bytes[index]
        index += 1

        #read data
        data_end = index + chunk_len

        if data_end > len(raw_bytes):
            print("[ERROR] Packet truncated! Stopping now.")
            break
        
        chunk_data = raw_bytes[index:data_end]
        index = data_end


        #read crc32
        if index + 4 > len(raw_bytes):
            print("[ERROR] Missing CRC at end. Stopping now.")
            break
            
        crc_bytes = raw_bytes[index:index+4]
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