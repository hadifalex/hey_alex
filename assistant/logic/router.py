from assistant.logic import rules
from typing import Callable, Optional


Rule = Callable[[str, dict], Optional[str]]

# Rules that never touch the network. Always active.
OFFLINE_RULES: list[Rule] = [
    rules.current_time,
    rules.current_date,
]

# Rules that need the internet (Wikipedia, weather).
# Only active when the profile does NOT say `no_internet: true`.
# Order matters: choose_location must come before weather.
ONLINE_RULES: list[Rule] = [
    rules.choose_location,
    rules.weather,
    rules.capital_question,
    rules.what_is_who_is,
]

# rules.greeting is intentionally left out: it bypasses the personality
# (the LLM should greet in character) and it crashes on dict-style nicknames.


def handle(text: str, profile: dict, llm=None) -> str:
    """
    Answer `text`: try the rule-based answers first, fall back to the LLM.

    :param text: what the user said or typed
    :param profile: the loaded personality profile
    :param llm: the PersistentLLM instance used as fallback
    :return: the reply, as a string
    """

    text = text.lower().strip()

    if profile.get("no_internet", False):
        active_rules = OFFLINE_RULES
    else:
        active_rules = OFFLINE_RULES + ONLINE_RULES

    # try rules first
    for rule in active_rules:
        result = rule(text, profile)
        if result:
            return result

    # if no rule matched -> ask the LLM
    if llm is None:
        raise RuntimeError("No LLM available for fallback")

    return llm.generate(text, profile)