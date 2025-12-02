import sounddevice as sd
import numpy as np
from decoder import decode_signal

SAMPLE_RATE = 44100

def receive(duration=3):
    """
    Receive a message using the microphone and decode ultrasonic audio.

    Parameters:
    duration(float): How long to listen in seconds 
    """
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

#usage

if __name__ == "__main__":
    receive(duration=5)