import os

#os.environ["OLLAMA_LOG_LEVEL"] = "error"    # it is important that this occurs first

import sys
import time
import yaml
import argparse
import random

import requests
import subprocess

from assistant.logic.router import handle
from assistant.audio.stt import listen, init_sst        # speech to text (for input)
from assistant.audio.tts import speak                   # text to speech (for output)
from assistant.llm.ollama_wrapper import PersistentLLM  # import the Ollama LLM
from assistant.audio.utils import beep                  # create beep sounds

def get_random_line(profile, category, default):
    greetings = profile.get("greetings", {})
    lines = greetings.get(category, [])
    
    if lines:
        return random.choice(lines)
    
    return default

def random_nickname(profile):
    key = random.choice(list(profile["owner"]["nicknames"].keys()))
    return profile["owner"]["nicknames"][key]

def replace_name(text,profile):
    """Replace the main name with one of its nicknames"""
    name = profile["owner"]["name"]
    nickname = random_nickname(profile)
    text = text.replace(name, nickname)
    return text

def replace_nicknames_tts(text, profile):
    """
    Replace canonical names with pronunciation-friendly nicknames for TTS.
    """
    nick_dict = profile["owner"]["nicknames"]
    for canonical, nick in nick_dict.items():
        text = text.replace(canonical, nick)
    return text


def ensure_ollama_running(diagnostic_mode = False):
    try:
        # check if Ollama server responds
        requests.get("http://localhost:11434")
        print("[Ollama] Server already running")
        return
    except requests.exceptions.ConnectionError:
        print("[Ollama] Starting a Session...please wait while I boot up!")

    # find correct binary automatically
    if sys.platform.startswith("win"):
        ollama_bin = os.path.join(
            os.environ["LOCALAPPDATA"],
            "Programs",
            "Ollama",
            "ollama.exe"
        )
    else:
        ollama_bin = "ollama"

    env = os.environ.copy()

    if not diagnostic_mode:
        env["OLLAMA_LOG_LEVEL"] = "error"

    stdout = None if diagnostic_mode else subprocess.DEVNULL
    stderr = None if diagnostic_mode else subprocess.DEVNULL

    subprocess.Popen(
        [ollama_bin, "serve"],
        stdout=stdout,
        stderr=stderr,
        env=env)
    
    time.sleep(2)
    if diagnostic_mode:
        print("[Ollama] Server should now be ready (diagnostic mode)")
    else:
        print("[Ollama] Server should now be ready")


def load_profile(name: str)->str:
    """Load a YAML profile"""

    path = f"profiles/{name}/personality.yaml"
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():

    #####################################################################
    # The parser for the optional arguments when running the application
    #####################################################################
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile",default="default")                                                  # you can load `run.py --profile lachlan` to load with "lachlan's profile"
    parser.add_argument("--text",action = "store_true",help="Use text input instead of microphone")     # you can load `run.py --text` to be in text mode (rather than listen mode)
    parser.add_argument("--diagnostic",action = "store_true",help="Show Vosk, Ollama, and Gin internal logs")
    
    args = parser.parse_args()                                                                          # stores the arguments of the parser

    profile = load_profile(args.profile)                        # loads the desired profile
    assistant_name = profile.get("name","Assistant")            # extract the name of the assistant

    diagnostic_mode = args.diagnostic
    

    init_sst(diagnostic_mode)
    
    
    if not diagnostic_mode:
        os.environ["OLLAMA_LOG_LEVEL"] = "error"

    if diagnostic_mode:
        os.environ.pop("OLLAMA_LOG_LEVEL", None)
    


    

    print(f"{assistant_name} is ready. Type your question")     # splash-screen question
    print("Type 'exit' to quit.\n")

    
    # check that Ollama is running before creating the persistent LLM.
    ########################################################################
    ensure_ollama_running(diagnostic_mode = diagnostic_mode)
    
    
    
    # load the persistent llm
    #########################################################################
    llm = PersistentLLM(model_name="llama3",profile=profile)

    
    
    # This autoinitialises and does NOT store in memory.
    #########################################################################

    try:
        greeting = llm.generate(f"You have just powered on after being asleep for a while. \
                                Greet {profile["owner"]["name"]} like a slightly confused but cheerful person! Keep it short!",
                     profile=profile,
                       n_memory=0)  # n_memory=0 if you don't want this in short-term memory
        
        print(f"\n{assistant_name}: {greeting}\n")
        speak(greeting, profile)

    except Exception as e:
        print(f"[LLM] Warm-up failed: {e}")
    

    #########################################################################
    # The main while loop
    #########################################################################

    sleeping = False

    while True:
        
        start_total = time.time()                           # start timing - diagnostic

        # if text mode requested, await for typed result
        if args.text:                  
            user_input = input("> ")
        
        # else, default to listening mode
        else:                          
            t0 = time.time()                                # timing to check speed bottlenecks in STT
            user_input = listen()                       # set input to listening

            # beep(500, 0.25)                                 # lower tone
            print(f"[TIME] STT: {time.time() - t0:.2f}s")   # for speed bottlenecks in STT
            print("You said:",user_input)                   # repeat the input - diagnostic

        # remove silences to avoid using "" as an input
        if not user_input.strip():
            continue                            # go to the top of the loop

        #########################################################################
        # RESOLVE SLEEP STATE
        #########################################################################

        if sleeping:
            if any(w in user_input.lower() for w in ["hey alex", "alex", "wake up"]):
                sleeping=False
                beep(1000, 0.25)                # first beep
                beep(1300,0.25)                 # second beep
                wake_msg = get_random_line(profile,"wake","Hello there!")
                rnd_nickname = random_nickname(profile)
                print(wake_msg +" "+ rnd_nickname)
                speak(wake_msg +" "+ rnd_nickname,profile)
            continue                            # go to the top of the loop

        if any(w in user_input.lower() for w in ["bye","bye bye","goodbye","shut up","be quiet"]):
            sleeping = True
            sleep_msg = get_random_line(profile, "sleep", "Bye!")
            print(sleep_msg)
            speak(sleep_msg, profile)
            beep(1000, 0.25)                # first beep
            beep(500,0.25)                 # second beep
            continue                            # go to the top of the loop

        # break the session if the user wants you to quit.    
        if user_input.lower() in ("exit","quit"):
            print("Goodbye!")
            speak("Goodbye!",profile)
            beep(1000, 0.25)     # first beep
            beep(500,0.25)       # second beep
            beep(500,1)          # third beep
            break

    
        #########################################################################
        #   RESPONSE
        #########################################################################

        print("Thinking...")

        t1 = time.time()                                        # timing to check speed bottlenecks in LLM   
        response = handle(user_input, profile,llm=llm)
        response = replace_name(response,profile)
        print(f"[TIME] Router + LLM: {time.time() - t1:.2f}s")  # timing to check speed bottlenecks in LLM

        print(f"\n{assistant_name}: {response}\n")
        print(f"[TIME] TOTAL: {time.time() - start_total:.2f}s\n")  # total time
        speak(replace_nicknames_tts(response,profile),profile)

if __name__ == "__main__":
    main()


