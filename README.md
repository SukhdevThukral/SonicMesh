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
from sonicmesh import transmit, decode_wav

#Encoding a message and transmitting over the speaker
transmit("Hello World!!")

# Decoding received signal (from WAV file for now - microphones later)
decoded = decode_wav("message.wav")
print(decoded)

```


## Research Focus
SonicMesh is **serious research project** aiming to pushing the limits of acoustic communication where users can:
- Experiment with **ultrasonic-FSK transmissionn**
- Test **basic audio-based file transfer, including images** (altho its still underdeveloped since the FSK decoding is still not optimized).
- Contribute to development of **high-frequency data transmission techniques**

## Architecture Overview
SonicMesh internally consists of three major components:

1. Encoder
- Convert raw bytes/text into symbols
- Maps each symbol to one of 64 frequencies (64-FSK)
- Generates the final audio waveform for transmission

2. Decoder
- Performs FFT based frequency detection
-  extracts symbol sequences from the spectrogram
- converts them back into bytes, text, or file data

3. Acoustic Configuration
Defines:
- Sample Rate
- Symbol Duration
- Frequency Table
- Bit depth per symbol (64-FSK -> 6 bits/ sybmol)


## Roadmap
Planned areas of development:
- High speed FSK enhancemeents for faster JPEG (and other file) transmission
- Better noise robustness using windowing and adaptive thresholding
- Microphone live decoding (real-time RX path)
- Spectrogram visualization tools for debugging
- Higher-order modulation (128-FSK or chirp based systems)
- Erorr correction codes (Hamming, BCH, or even Reed-Solomon)

## Current Limitations
To set the correct expectations:
- File transfer works but is slow at the moment
- FFT decoding still needs a lot of optimization and noise filtration
- Microphone live receive is still in experimental / "in-progress" stage.

## Contributing

Contributions are welcome especially inL
- Audio signal processing
- optimizing fsk encoding/decoding
- increasing data transfer speed

All contributions should maintain the **research oriented and experiment nature of the project.**

## License 
This project is licensed under the MIT License.
