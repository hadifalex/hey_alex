import os
from io import BytesIO
import wave

import numpy as np
import sounddevice as sd
from piper import PiperVoice
from pathlib import Path

import re


BASE = Path(__file__).parent / "piper_voices"
voice_path = BASE/"en_GB-northern_english_male-medium.onnx"
voice = PiperVoice.load(str(voice_path))                        # this creates the voice.


def apply_pronunciation(text, profile):

    owner = profile.get("owner", {})
    nicknames = owner.get("nicknames", {})

    for written, spoken in nicknames.items():
        pattern = r'\b' + re.escape(written) + r'\b'
        text = re.sub(pattern, spoken, text)

    return text


def speak(text:str,profile = None):
    
    if profile:
        text = apply_pronunciation(text,profile)

    # have piper write a wave data into a file-like object
    wav_buffer = BytesIO()

    with wave.open(wav_buffer,"wb") as wav_file:
        voice.synthesize_wav(text,wav_file)
    
    # go back to the start of the buffer
    wav_buffer.seek(0)  

    # read the WAV we create

    with wave.open(wav_buffer,"rb") as wav_file:
        samplerate = wav_file.getframerate()
        frames = wav_file.readframes(wav_file.getnframes())

    # convert to numpy int16
    audio = np.frombuffer(frames,dtype=np.int16)

    # play it

    sd.play(audio,samplerate=samplerate)
    sd.wait()


# if __name__ == "__main__":
#     speak("If you can hear this, your device is alive.")





# with wave.open("test.wav", "wb") as wav_file:
#     voice.synthesize_wav(
#         "Welcome to the world of speech synthesis!",
#         wav_file
#     )