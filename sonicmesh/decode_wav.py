import soundfile as sf
import numpy as np
from decoder import decode_signal, decode_file

def bits_to_text(bitstream):
    """"Convert an 8-bit aligned bitstream into a UTF-8 string."""
    text = ""
    for i in range(0, len(bitstream),8):
        byte = bitstream[i:i+8]
        if len(byte) == 8:
            text+=chr(int(byte,2))
    return text
    

def decode_wav(wav_path: str, as_file: bool = False, output_file: str = None ):
    """
    Decode a SonicMesh-generated WAV file.
    
    Parameters
    ==========
    wav_path : str
        Path to the WAV file containing the encoded ultrasonic signal.
    as_file : bool, optional
        If True, treating the payload as a binary fine and reconstructing it.
        If False, decode the payload as UTF-8 text.
    output_file : str, optional
        Filepath to write the reconstructedd binary output, used only 
        when `as_file=True`.

    Returns
    =======
    str
        - when `as_file= False`: decoded text msg.
        - when `as_file= True `: path to the reconstructed file

    """

    data, sr = sf.read(wav_path)

    #flattening in case if its stereo
    signal = np.array(data).flatten()

    # Core decoder to convert audio -> bitstream.
    bits = decode_signal(signal)

    if as_file == True:
        if output_file== None:
            output_file = "received_file.bin"

        # Reconstructed file from the decoded bistream
        decode_file(bits, output_file)
        return output_file
    
    else:
        
        return bits_to_text(bits)
