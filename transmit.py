import sounddevice as sd
from encoder import encode_message, encode_file
from scipy.io.wavfile import write
import numpy as np
from acoustic_config import SAMPLE_RATE

#transmitting messages
def transmit(msg, save_file=True):
    print(" Transmitting message..")


    #encoding the msg into ultrasonic tones
    signal = encode_message(msg)


    if save_file:
        # convert signal to 16bit pcm for wav
        scaled = np.int16(signal / np.max(np.abs(signal)) * 32767)
        write("message.wav", SAMPLE_RATE, scaled)
        print("saved mesg to 'message.wav'")

    #Play the signal
    sd.play(signal, SAMPLE_RATE)
    sd.wait()
    print("Transmission complete")

#transmitting ACTUAL FILES
def transmitf(file_path, save_file=True):
    print("[SonicMesh]  Transmitting file: ", file_path)

    #encode file into bitstr
    signal = encode_file(file_path)

    if save_file:
        scaled = np.int16(signal / np.max(np.abs(signal))*32767)
        write("file_message.wav", SAMPLE_RATE, scaled)
        print("saved file audio to 'file_message.wav'")

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