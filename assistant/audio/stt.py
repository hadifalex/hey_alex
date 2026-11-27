# Speech-to-text via Vosk (fully offline).
# Captures audio from the microphone and converts it to text for the assistant.
#
# Which microphone is used (first match wins):
#   1. environment variable ALEX_MIC            (e.g.  ALEX_MIC=3)
#   2. `input_device:` in config/audio.yaml     (index, or part of the device name)
#   3. the system default input device
# Run mic_check.py to see the available devices.
#
# Sample rate: the Vosk model was trained on 16000 Hz audio, so that is tried first.
# Some microphones (e.g. many USB ones on a Raspberry Pi) refuse 16000 Hz; for those
# the microphone's own native rate is used instead, and Vosk resamples internally.

from vosk import SetLogLevel
SetLogLevel(-1)

import json
import os
import queue
import time
from pathlib import Path

import sounddevice as sd
import yaml
from vosk import Model, KaldiRecognizer

ROOT = Path(__file__).resolve().parents[2]          # repo root (assistant/audio/stt.py -> ../..)
MODEL_PATH = ROOT / "models" / "vosk-model-small-en-us-0.15"
CONFIG_PATH = ROOT / "config" / "audio.yaml"

PREFERRED_SAMPLERATE = 16000    # what the Vosk model was trained on
BLOCK_SECONDS = 0.25            # length of each chunk of audio we process
MAX_UTTERANCE_S = 15            # force a result if end-of-speech is never detected (noisy room)

model = None                    # initialised by init_sst()
q = queue.Queue()
_working_rate = None            # remembered after the first successful open


def _input_device():
    """Return the configured input device (int index, name fragment) or None for default."""
    device = os.environ.get("ALEX_MIC")

    if device is None and CONFIG_PATH.exists():
        try:
            data = yaml.safe_load(CONFIG_PATH.read_text()) or {}
            device = data.get("input_device")
        except Exception as e:
            print(f"[STT] Could not read {CONFIG_PATH}: {e}")

    if device is None or str(device).strip() == "":
        return None
    try:
        return int(device)
    except (TypeError, ValueError):
        return str(device)


def init_sst(diagnostic: bool = False):
    global model

    if diagnostic:
        SetLogLevel(0)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Vosk model not found at {MODEL_PATH}.\n"
            "Download 'vosk-model-small-en-us-0.15' from https://alphacephei.com/vosk/models "
            "and unzip it into the models/ folder."
        )
    model = Model(str(MODEL_PATH))

    # tell the user which microphone will be used
    try:
        info = sd.query_devices(_input_device(), "input")
        print(f"[STT] Using microphone: [{info['index']}] {info['name']}")
    except Exception as e:
        print(f"[STT] Warning: no usable microphone found ({e})")


def callback(indata, frames, time_info, status):
    """Called by sounddevice for every block of microphone audio."""
    if status:
        print(status)
    q.put(bytes(indata))


def _drain_queue():
    """Throw away audio left over from the previous listen()."""
    try:
        while True:
            q.get_nowait()
    except queue.Empty:
        pass


def _open_stream(device):
    """
    Open the microphone, at 16000 Hz if it allows it, otherwise at its native rate.
    Returns (stream, samplerate).
    """
    global _working_rate

    if _working_rate is not None:
        rates = [_working_rate]
    else:
        rates = [PREFERRED_SAMPLERATE]
        try:
            native = int(sd.query_devices(device, "input")["default_samplerate"])
            if native != PREFERRED_SAMPLERATE:
                rates.append(native)
        except Exception:
            pass

    errors = []
    for rate in rates:
        try:
            stream = sd.RawInputStream(
                samplerate=rate,
                blocksize=int(rate * BLOCK_SECONDS),
                dtype="int16",
                channels=1,
                device=device,
                callback=callback,
            )
        except Exception as e:
            errors.append(f"  {rate} Hz: {e}")
            continue

        if rate != PREFERRED_SAMPLERATE and _working_rate is None:
            print(f"[STT] This microphone doesn't support {PREFERRED_SAMPLERATE} Hz; "
                  f"using its native {rate} Hz instead (Vosk resamples).")
        _working_rate = rate
        return stream, rate

    _working_rate = None    # re-probe next time (e.g. the mic was unplugged)
    raise RuntimeError(
        f"Could not open the microphone (device={device!r}):\n" + "\n".join(errors) +
        "\nRun mic_check.py to list the devices, then set input_device in config/audio.yaml."
    )


def listen() -> str:
    """Capture audio and return the recognised text ('' if nothing was understood)."""
    if model is None:
        raise RuntimeError("STT model not initialised. Call init_sst() first.")

    device = _input_device()
    _drain_queue()
    stream, rate = _open_stream(device)
    rec = KaldiRecognizer(model, rate)

    with stream:
        print("Listening...")
        warned = False
        speech_started = None

        while True:
            try:
                data = q.get(timeout=1)
            except queue.Empty:
                if not warned:
                    print("[STT] No audio is arriving from the microphone. "
                          "Wrong device? Run mic_check.py.")
                    warned = True
                continue

            # normal end of utterance (Vosk detected silence after speech)
            if rec.AcceptWaveform(data):
                return json.loads(rec.Result()).get("text", "")

            # safety valve: never listen to one endless utterance
            if speech_started is None:
                if json.loads(rec.PartialResult()).get("partial"):
                    speech_started = time.time()
            elif time.time() - speech_started > MAX_UTTERANCE_S:
                return json.loads(rec.FinalResult()).get("text", "")