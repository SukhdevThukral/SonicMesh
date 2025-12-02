import sounddevice as sd
from encoder import encode_message, encode_file, encode_bit
from scipy.io.wavfile import write
import numpy as np

SAMPLE_RATE = 44100

#transmitting messages
def transmit(msg, save_file=True):
    print("[SonicMesh] Preparing to transmit data: ", msg)


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
    print("[SonicMesh] Preparing to transmit files: ", file_path)

    #encode file into bitstr
    bits = encode_file(file_path)

    #converting bits to audio signals
    all_tones = []
    for bit in bits:
        tone = encode_bit(bit)
        all_tones.append(tone)
    signal = np.concatenate(all_tones)


    if save_file:
        scaled = np.int16(signal / np.max(np.abs(signal))*32767)
        write("file_message.wav", SAMPLE_RATE, scaled)
        print("saved file audio to 'file_message.wav'")

    sd.play(signal, SAMPLE_RATE)
    sd.wait()
    print("File transmission complete")


#usage
if __name__ == "__main__":
    choice = input("Sent (T)ext or (F)ile? ").lower()
    if choice == "t":
        message = input("Enter message to transmit: ")
        transmit(message, save_file=True)
    elif choice == "f":
        file_path = input("Enter file path to transmit: ")
        transmitf(file_path, save_file=True)
    else:
        print("Invalid choice")
    