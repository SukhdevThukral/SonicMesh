import soundfile as sf
import numpy as np
from decoder import decode_signal, decode_file

def decode_wav(as_file=False, output_file=None):
    """
    Decode a WAV file saved from SonicMesh.
    
    Parameters:
    - as_file (bool): True if decoding a file, False for text
    - output_file (str): path to save reconstructed file if as_file=True
    """
    if as_file == False:
        wav_path = "message.wav"
    else:
        wav_path = "file_message.wav"

    print("[SonicMesh] Loading", wav_path, "....")

    data, sr = sf.read(wav_path)

    if sr != 44100:
        print(f"[WARNING] WAV file sample rate is {sr}, expected 44100")

    #flattening in case if its stereo
    signal = np.array(data).flatten()

    print("[SonicMesh] Decoding...")
    bits_msg  = decode_signal(signal)

    if as_file == True:
        if output_file== None:
            output_file = "received_file.bin"
        decode_file(bits_msg, output_file)
        print("File decoded and saved to", output_file)
    else:
        print("\n==========================")
        print(" DECODED MESSAGE: ", bits_msg)
        print("\n==========================")

if __name__ == "__main__":
    choice = input("Decode (T)ext or (F)ile? ").strip().lower()
    if choice == "t":
        decode_wav(as_file=False)
    elif choice == "f":
        output_file = input("save output as: ")
        decode_wav(as_file=True, output_file=output_file)
    else:
        print("Invalid choice")