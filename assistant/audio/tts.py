from piper import PiperVoice
import sounddevice as sd
import numpy as np
import os
import wave
from pathlib import Path

BASE = Path(__file__).parent / "piper_voices"
voice_path = BASE/"en_GB-northern_english_male-medium.onnx"


voice = None

def init_tts():
    global voice
    voice = PiperVoice.load(VOICE_PATH)


def speak(text:str):
    if voice is None:
        raise RuntimeError("TTS not initialised. Call init_tts() first.")

    chunks = []
    for chunk in voice.synthesize(text):
        chunks.append(chunk)
    
    audio  = np.concatenate(chunks).astype(np.int16)

    sd.play(audio,samplerate=voice.config.sample_rate)

    sd.wait()






voice = PiperVoice.load(str(voice_path))

with wave.open("test.wav", "wb") as wav_file:
    voice.synthesize_wav(
        "Welcome to the world of speech synthesis!",
        wav_file
    )