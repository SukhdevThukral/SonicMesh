import soundfile as sf
import numpy as np
from decoder import decode_signal

def decode_wav():
    print("[SonicMesh] Loading message.wav...")

    data, sr = sf.read("message.wav")

    if sr != 44100:
        print(f"[WARNING] WAV file sample rate is {sr}, expected 44100")

    #flattening in case if its stereo
    signal = np.array(data).flatten()

    print("[SonicMesh] Decoding...")
    msg  = decode_signal(signal)

    print("\n==========================")
    print(" DECODED MESSAGE: ", msg)
    print("\n==========================")

if __name__ == "__main__":
    decode_wav()