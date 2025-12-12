import sounddevice as sd
from .encoder import encode_message, encode_file
from scipy.io.wavfile import write

import numpy as np
from .acoustic_config import SAMPLE_RATE

def _save_wav(path, signal):
    """Convert float32 => 16 bit PCM & store wav"""
    scaled = np.int16(signal / np.max(np.abs(signal)) * 32767)
    write(path, SAMPLE_RATE, scaled)

#transmitting messages
def transmit(msg: str, save_file=True):

    #encoding the msg into ultrasonic tones
    signal = encode_message(msg)


    if save_file:
        # convert signal to 16bit pcm for wav
        _save_wav("message.wav", signal)

    #Play the signal
    sd.play(signal, SAMPLE_RATE)
    sd.wait()

#transmitting ACTUAL FILES
def transmitf(file_path: str, save_file=True):
    print("[SonicMesh]  Encoding file: ", file_path)

    #encode file into bitstr
    signal = encode_file(file_path)

    if save_file:
        _save_wav("file_message.wav", signal)

    sd.play(signal, SAMPLE_RATE)
    sd.wait()