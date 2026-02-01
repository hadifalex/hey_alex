from datetime import datetime
from assistant.retrieval.wikipedia import lookup
from assistant.retrieval.weather import geocode, get_weather_from_coords, format_options, LAST_GEOCODE_RESULTS
import re
import random
import string

def get_owner_name(profile):
    owner = profile.get("owner",{})
    names = owner.get("nicknames",[])
    return random.choice(names) if names else "there"

def greeting(text:str, profile:dict):

    triggers = ["hello","hi","hey"]

    if any(text.startswith(t) for t in triggers):
        owner_name = get_owner_name(profile)
        return f"Hello {owner_name}! How can I help you today?"
    
    return None

def current_time(text: str, profile:dict):
    if "time" in text:
        now = datetime.now().strftime("%H:%M")
        return f"The time is {now}"
    return None

def current_date(text: str, profile:dict):
    if re.search(r"\b(date|day)\b", text):
        today = datetime.now().strftime("%A, %d %B %Y")
        return f"Today is {today}"
    return None

def capital_question(text: str, profile:dict):
    if "capital of" in text:
        topic = text.split("capital of")[-1].strip()
        return lookup(f"capital of {topic}")
    return None


def what_is_who_is(text: str, profile:dict):
    if text.startswith("what is") or text.startswith("who is"):
        topic = text.replace("what is", "").replace("who is", "").strip()
        topic = topic.translate(str.maketrans("", "", string.punctuation))
        result = lookup(topic)
        if result:
            return result
        return None


def clean_location(text: str) -> str:
    # remove punctuation and extra spaces
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()




def weather(text: str, profile: dict):
    if "weather" not in text:
        return None

    if "in " in text:
        location = text.split("in ")[-1].strip()
        location = clean_location(location)

        results = geocode(location)

        if not results:
            return "I couldn't find that location. Can you try again?"

        # Save results globally
        LAST_GEOCODE_RESULTS.clear()
        LAST_GEOCODE_RESULTS.extend(results)

        # If multiple results, ask user to choose
        if len(results) > 1:
            return (
                "I found multiple locations. "
                "Please choose one by number:\n"
                + format_options(results)
            )

        # only one result
        place = results[0]
        return get_weather_from_coords(place["latitude"], place["longitude"], place["name"])

    return "Sure — which city do you want the weather for?"



def choose_location(text: str, profile: dict):
    from assistant.retrieval.weather import LAST_GEOCODE_RESULTS, get_weather_from_coords

    if not LAST_GEOCODE_RESULTS:
        return None

    try:
        choice = int(text.strip())
    except ValueError:
        return "Please reply with a number."

    if choice < 1 or choice > len(LAST_GEOCODE_RESULTS):
        return "That number is not valid. Try again."

    place = LAST_GEOCODE_RESULTS[choice - 1]
    LAST_GEOCODE_RESULTS.clear()

    return get_weather_from_coords(place["latitude"], place["longitude"], place["name"])
