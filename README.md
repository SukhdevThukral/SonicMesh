# SonicMesh

**Acoustic Ultrasonic Data Transfer Library (Research Project)**

SonicMesh is a Python library designed for **high-frequency ultrasonic communication**, enabling data transfer over audio. This project is part of ongoing research into **ultrasonic FSK (frequency shift keying) communication** and aims to push the limits of audio based data transmission particularly for **file transfer tht includes images**.


## Features
- **Send text and files over sound** using ultrasonic frequencies
- **64-FSK encoder** for efficient data transmission
- **FFT-based ultrasonic decoder** for accurate reception.
- **WAV utils** to save and read transmissions
- Exoposes **high-level APIs** for quick experimentation

## Goals
- Enable **high speed audio-based transfer of data (images and text for now).**
- Explore **novel encoding strategies** for ultrasonic communication.
- provides a flexible library for **research and experimentation**

## Installation

```bash
pip install sonicmesh
```

## Quick Example
```bash
from sonicmesh import encode_message, transmit, decode_signal


#Encoding a message
signal = encode_message("Hello World!!")

# Transmit over speaker
transmit(signal)

# Decoding received signal (from WAV file for now - microphones later)
decoded = decode_signal("received.wav")
print(decoded)

```


## Research Focus
SonicMesh is **serious research project** aiming to pushing the limits of acoustic communication where users can:
- Experiment with **ultrasonic-FSK transmissionn**
- Test **basic audio-based file transfer, including images** (altho its still underdeveloped since the FSK decoding is still not optimized).
- Contribute to development of **high-frequency data transmission techniques**

## Contributing

Contributions are welcome especially inL
- Audio signal processing
- optimizing fsk encoding/decoding
- increasing data transfer speed

All contributions should maintain the **research oriented and experiment nature of the project.**

## License 
This project is licensed under the MIT License.
