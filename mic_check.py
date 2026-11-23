"""
Microphone check for hey_alex.

Put this file in the repo root (next to run.py) and run:

    python mic_check.py          # test the default input device
    python mic_check.py 3        # test device index 3 (see the list it prints)
    python mic_check.py "USB"    # test the first device whose name contains "USB"

It lists every audio device, records a few seconds, reports how loud the
signal was, and (if the Vosk model is present) shows what Vosk heard.
"""

import json
import sys
import time
from pathlib import Path

import numpy as np
import sounddevice as sd

SAMPLERATE = 16000
SECONDS = 4


def main():
    print(sd.query_devices())
    print("\nDefault device (input, output):", sd.default.device)

    device = None
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        device = int(arg) if arg.isdigit() else arg

    info = sd.query_devices(device, "input")
    print(f"\nTesting input: [{info['index']}] {info['name']}")
    print(f"  default rate {info['default_samplerate']:.0f} Hz, "
          f"{info['max_input_channels']} input channel(s)")

    input(f"\nPress Enter, then speak clearly for {SECONDS} seconds... ")
    time.sleep(0.4)  # let the key click die away
    audio = sd.rec(int(SECONDS * SAMPLERATE), samplerate=SAMPLERATE,
                   channels=1, dtype="int16", device=device)
    sd.wait()

    samples = audio[:, 0].astype(np.float32) / 32768.0
    peak = float(np.abs(samples).max())
    rms = float(np.sqrt((samples ** 2).mean()))
    print(f"\nPeak level: {peak:.3f}   RMS: {rms:.4f}")

    # Judge by RMS (average loudness), not peak: the click of pressing Enter
    # can spike the peak even when the microphone hears nothing else.
    # Normal speech at a normal distance is roughly RMS 0.02 - 0.1.
    if rms < 0.003:
        print("-> Basically silence (noise floor). Wrong device, muted mic, "
              "or Windows privacy setting blocking desktop apps.")
    elif rms < 0.01:
        print("-> Very quiet. Maybe the right device but with low gain "
              "(raise the input volume in the OS sound settings), or you "
              "spoke too softly / too far away.")
    else:
        print("-> Signal looks healthy.")

    model_dir = Path(__file__).parent / "models" / "vosk-model-small-en-us-0.15"
    if model_dir.exists():
        from vosk import KaldiRecognizer, Model, SetLogLevel

        SetLogLevel(-1)
        rec = KaldiRecognizer(Model(str(model_dir)), SAMPLERATE)
        rec.AcceptWaveform(audio.tobytes())
        text = json.loads(rec.FinalResult()).get("text", "")
        print(f"Vosk heard: {text!r}" if text else "Vosk heard: (nothing)")
    else:
        print(f"\n(Vosk model not found at {model_dir}, skipping transcription test.)")

    print("\nTo use a device permanently, put its index or a unique part of "
          "its name in config/audio.yaml:\n    input_device: 3")


if __name__ == "__main__":
    main()