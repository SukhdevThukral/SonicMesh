import sounddevice as sd
from encoder import encode_message

def transmit(msg):

    """
    Transmit a text message using ultrasonic audio.
    
    Parameters:
    msg(str): The message to send
    """
    print("[SonicMesh] Preparing to transmit data: ", msg)


    #encoding the msg into ultrasonic tones
    signal = encode_message(msg)

    #Play the signal
    sd.play(signal, 44100)
    sd.wait()


    print("Transmission complete")

#usage
if __name__ == "__main__":
    message = input("Enter message to transmit: ")
    transmit(message)
    