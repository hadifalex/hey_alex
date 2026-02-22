import numpy as np
import sounddevice as sd

def beep(frequency=800, duration=0.15, samplerate=22050):
    """Generates a small 'beep' depending on parameters"""
    t = np.linspace(0, duration, int(samplerate * duration), False)
    tone = 0.5 * np.sin(2 * np.pi * frequency * t)
    sd.play(tone.astype(np.float32), samplerate)
    sd.wait()

# if __name__ == "__main__":
#     beep(1000, .25)   # higher tone
#     beep(500, .25)   # higher tone