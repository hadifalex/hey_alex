# Plays mono audio on the speaker, adapting to what the device supports.
#
# Many sound devices (e.g. USB speakers on a Raspberry Pi) only accept their own
# native sample rate and/or stereo. This tries the audio as-is first, then falls
# back to the device's native rate and/or two channels, and remembers what worked.
#
# Which speaker is used (first match wins):
#   1. environment variable ALEX_SPEAKER        (e.g.  ALEX_SPEAKER=2)
#   2. `output_device:` in config/audio.yaml    (index, or part of the device name)
#   3. the system default output device
# Run mic_check.py to see the available devices (it lists inputs and outputs).

import os
from pathlib import Path

import numpy as np
import sounddevice as sd
import yaml

ROOT = Path(__file__).resolve().parents[2]          # repo root (assistant/audio/playback.py -> ../..)
CONFIG_PATH = ROOT / "config" / "audio.yaml"

_working = {}       # device -> (samplerate, channels) that worked last time


def _output_device():
    """Return the configured output device (int index, name fragment) or None for default."""
    device = os.environ.get("ALEX_SPEAKER")

    if device is None and CONFIG_PATH.exists():
        try:
            data = yaml.safe_load(CONFIG_PATH.read_text()) or {}
            device = data.get("output_device")
        except Exception as e:
            print(f"[AUDIO] Could not read {CONFIG_PATH}: {e}")

    if device is None or str(device).strip() == "":
        return None
    try:
        return int(device)
    except (TypeError, ValueError):
        return str(device)


def _to_float32_mono(audio):
    audio = np.asarray(audio)
    if audio.dtype == np.int16:
        audio = audio.astype(np.float32) / 32768.0
    else:
        audio = audio.astype(np.float32)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    return audio


def _resample(audio, from_rate, to_rate):
    """Simple linear-interpolation resampling (plenty good enough for speech)."""
    if from_rate == to_rate or len(audio) == 0:
        return audio
    n_out = int(round(len(audio) * to_rate / from_rate))
    x_old = np.arange(len(audio)) / from_rate
    x_new = np.arange(n_out) / to_rate
    return np.interp(x_new, x_old, audio).astype(np.float32)


def play(audio, samplerate):
    """
    Play mono audio (int16 or float samples) at `samplerate` and wait until it finishes.
    Falls back to the speaker's native rate and/or stereo if the speaker refuses the original.
    """
    device = _output_device()
    audio = _to_float32_mono(audio)

    if device in _working:
        candidates = [_working[device]]
    else:
        rates = [samplerate]
        try:
            native = int(sd.query_devices(device, "output")["default_samplerate"])
            if native != samplerate:
                rates.append(native)
        except Exception:
            pass
        candidates = [(rate, channels) for rate in rates for channels in (1, 2)]

    errors = []
    for rate, channels in candidates:
        data = _resample(audio, samplerate, rate)
        if channels == 2:
            data = np.column_stack((data, data))
        try:
            sd.play(data, samplerate=rate, device=device)
            sd.wait()
        except sd.PortAudioError as e:
            errors.append(f"  {rate} Hz, {channels} ch: {e}")
            continue

        if device not in _working and (rate, channels) != (samplerate, 1):
            print(f"[AUDIO] The speaker doesn't accept {samplerate} Hz mono; "
                  f"using {rate} Hz, {channels} channel(s) instead.")
        _working[device] = (rate, channels)
        return

    _working.pop(device, None)      # re-probe next time (e.g. the speaker was unplugged)
    raise RuntimeError(
        f"Could not play audio on the speaker (device={device!r}):\n" + "\n".join(errors) +
        "\nRun mic_check.py to list the devices, then set output_device in config/audio.yaml."
    )