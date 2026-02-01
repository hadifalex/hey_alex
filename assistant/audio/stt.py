# this code handles the sound to text part
## allows for a microphone to pick-up the question and converts it to text for the assistant to parse.

import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import json

MODEL_PATH = "models/vosk-model-small-en-us-0.15"   # where the model is stored

model = Model(MODEL_PATH)   # load the model
q = queue.Queue()

def callback(indata, frames, time, status):
    """Callback from sound device input stream"""

    if status:
        print(status)
    q.put(bytes(indata))



def listen():
    """Capture audtio and return recognized text"""

    rec = KaldiRecognizer(model,16000)  # initialise the recorder with a model and samplerate
    
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",channels=1,callback=callback):
        print("Listening...")

        while True:
            data = q.get()
            
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                return result.get("text","")