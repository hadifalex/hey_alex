# this code handles the sound to text part
## allows for a microphone to pick-up the question and converts it to text for the assistant to parse.

from vosk import SetLogLevel
SetLogLevel(-1)

import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import json

import contextlib
import sys
import os

MODEL_PATH = "models/vosk-model-small-en-us-0.15"   # where the model is stored

model = None            # to be initialised later
q = queue.Queue()

####### INITIALISING
def init_sst(diagnostic: bool):
    global model

    if diagnostic:
        SetLogLevel(0)
    
    model = Model(MODEL_PATH)


######### CALLBACK
def callback(indata, frames, time, status):
    """Callback from sound device input stream"""

    if status:
        print(status)
    q.put(bytes(indata))



def listen():
    """Capture audtio and return recognized text"""

    if model is None:
        raise RuntimeError("STT model not initialised. Call init_sst() first.")


    rec = KaldiRecognizer(model,16000)  # initialise the recorder with a model and samplerate
    
    with sd.RawInputStream(
        samplerate=16000, 
        blocksize=8000, 
        dtype="int16",
        channels=1,
        callback=callback
        ):
        
        print("Listening...")

        while True:
            data = q.get()
            
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                return result.get("text","")
            
