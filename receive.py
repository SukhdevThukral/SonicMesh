import sounddevice as sd
import numpy as np
from decoder import decode_signal, decode_file
import soundfile as sf

SAMPLE_RATE = 44100

def receive(duration=3):
    print("[SonicMesh] Listening for message...")
    
    #record audio from the microphone

    recording = sd.rec(int(duration*SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float64')
    sd.wait() #waiting until the rec is done

    #flattening the array to 1D
    signal = recording.flatten()

    #decoding the ultrasonic signal back into text
    msg = decode_signal(signal)

    print("Received message:", msg)
    return msg

def receive_file(wav_path, output_file):
    print("[SonicMesh] Reading WAV file:", wav_path)
    signal, sr = sf.read(wav_path)
    signal = signal.flatten()

    bits = decode_signal(signal)
    decode_file(bits, output_file)


#usage

if __name__ == "__main__":
    choice = input("Receive (T)ext from mic or (F)ile from WAV? ").lower()
    if choice == "t":
        receive(duration=5)
    elif choice == "f":
        wav_path = input("Enter WAV file path: ")
        output_file = input("Save output as: ")
        receive_file(wav_path, output_file)
    else:
        print("Invalid choice")