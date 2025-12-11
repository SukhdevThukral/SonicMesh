import sounddevice as sd
from encoder import encode_message, encode_file
from scipy.io.wavfile import write

import numpy as np
from acoustic_config import SAMPLE_RATE

def _save_wav(path, signal):
    """Convert float32 => 16 bit PCM & store wav"""
    scaled = np.int16(signal / np.max(np.abs(signal)) * 32767)
    write(path, SAMPLE_RATE, scaled)

#transmitting messages
def transmit(msg: str, save_file=True):
    print("Encoding text msg....")


    #encoding the msg into ultrasonic tones
    signal = encode_message(msg)


    if save_file:
        # convert signal to 16bit pcm for wav
        _save_wav("message.wav", signal)
        print("saved mesg to 'message.wav'")

    print("Transmitting message..")
    #Play the signal
    sd.play(signal, SAMPLE_RATE)
    sd.wait()
    print("Transmission complete")

#transmitting ACTUAL FILES
def transmitf(file_path: str, save_file=True):
    print("[SonicMesh]  Encoding file: ", file_path)

    #encode file into bitstr
    signal = encode_file(file_path)

    if save_file:
        _save_wav("file_message.wav", signal)
        print("saved file audio to 'file_message.wav'")

    print("Transmitting..")
    sd.play(signal, SAMPLE_RATE)
    sd.wait()
    print("File transmission complete")

if __name__ == "__main__":
    choice = input("Send (T)ext or (F)ile? ").strip().lower()
    if choice == "t":
        msg = input("Enter message to transmit: ")
        transmit(msg, save_file=True)
    elif choice == "f":
        file_path = input("Enter file path to transmit: ")
        transmitf(file_path, save_file=True)
    else:
        print("Invalid choice")