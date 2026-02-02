import argparse
import yaml

from assistant.logic.router import handle
from assistant.audio.stt import listen

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

    while True:
        if args.text:
            user_input = input("> ")
        else:
            user_input = listen()
            print("You said:",user_input)

        if user_input.lower() in ("exit","quit"):
            break

        response = handle(user_input, profile)
        print(f"\n{assistant_name}: {response}\n")


if __name__ == "__main__":
    main()


