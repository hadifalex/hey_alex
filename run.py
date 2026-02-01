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
    parser.add_argument("--profile",default="default")
    args = parser.parse_args()

    profile = load_profile(args.profile)
    assistant_name = profile.get("name","Assistant")

    print(f"{assistant_name} is ready. Type your question")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("> ")

        if user_input.lower() in ("exit","quit"):
            break

        response = handle(user_input, profile)
        print(f"\n{assistant_name}: {response}\n")


if __name__ == "__main__":
    main()


