import sounddevice as sd
import numpy as np
from decoder import decode_signal, decode_file
import soundfile as sf
from acoustic_config import SAMPLE_RATE

SAMPLE_RATE = 44100

def receive(duration=3):
    raise NotImplementedError("[SonicMesh] recieve() us not implemented in this release.")
    print("[SonicMesh] Listening...")
    
    #record audio from the microphone

    recording = sd.rec(int(duration*SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float64')
    sd.wait() #waiting until the rec is done

    #flattening the array to 1D
    signal = recording.flatten()

    #decoding the ultrasonic signal back into text
    bits = decode_signal(signal)

    print("Received bitstream:", bits)
    return bits

def receive_file(wav_path, output_file):
    raise NotImplementedError("[SonicMesh] receive_file() is not implemented in this release")
    print("[SonicMesh] Reading WAV file:", wav_path)
    signal, sr = sf.read(wav_path)
    signal = signal.flatten()

    bits = decode_signal(signal)
    decode_file(bits, output_file)
