import argparse
import yaml

from assistant.logic.router import handle
from assistant.audio.stt import listen
from assistant.llm.ollama_wrapper import PersistentLLM

import time

def load_profile(name: str)->str:
    """
    Docstring for load_profile
    
    :param name: Description
    :type name: str
    :return: Description
    :rtype: str
    """

    path = f"profiles/{name}/personality.yaml"
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile",default="default")                                                  # you can load `run.py --profile lachlan` to load with "lachlan's profile"
    parser.add_argument("--text",action = "store_true",help="Use text input instead of microphone")     # you can load `run.py --text` to be in text mode (rather than listen mode)
    args = parser.parse_args()                                                                          # stores the arguments of the parser

    profile = load_profile(args.profile)                        # loads the desired profile
    assistant_name = profile.get("name","Assistant")            # extract the name of the assistant

    print(f"{assistant_name} is ready. Type your question")     # splash-screen question
    print("Type 'exit' to quit.\n")

    # load the persistent llm
    llm = PersistentLLM(model_name="llama3")
    
    while True:
        start_total = time.time()

        if args.text:
            user_input = input("> ")
        else:
            t0 = time.time()                                # timing to check speed bottlenecks in STT
            user_input = listen()
            print(f"[TIME] STT: {time.time() - t0:.2f}s")   # for speed bottlenecks in STT
            print("You said:",user_input)
            print("Thinking...")

        if user_input.lower() in ("exit","quit"):
            break
        
        t1 = time.time()                                        # timing to check speed bottlenecks in LLM   
        response = handle(user_input, profile,llm=llm)
        print(f"[TIME] Router + LLM: {time.time() - t1:.2f}s")  # timing to check speed bottlenecks in LLM

        print(f"\n{assistant_name}: {response}\n")
        print(f"[TIME] TOTAL: {time.time() - start_total:.2f}s\n")  # total time

if __name__ == "__main__":
    main()


