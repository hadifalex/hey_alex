import numpy as np

from assistant.audio.playback import play

def beep(frequency=800, duration=0.15, samplerate=22050):
    """Generates a small 'beep' depending on parameters"""
    t = np.linspace(0, duration, int(samplerate * duration), False)
    tone = 0.5 * np.sin(2 * np.pi * frequency * t)
    play(tone.astype(np.float32), samplerate)

# if __name__ == "__main__":
#     beep(1000, .25)   # higher tone
#     beep(500, .25)   # higher tone