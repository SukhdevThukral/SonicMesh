import sounddevice as sd
from encoder import encode_message
from scipy.io.wavfile import write
import numpy as np

SAMPLE_RATE = 44100

def transmit(msg, save_file=True):

    """
    Transmit a text message using ultrasonic audio.
    
    Parameters:
    msg (str): the message to send
    save_file (bool): If true, saves the signal to 'message.wav'
    """
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

#usage
if __name__ == "__main__":
    message = input("Enter message to transmit: ")
    transmit(message, save_file=True)
    