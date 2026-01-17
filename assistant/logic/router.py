from assistant.logic import rules
from typing import Callable, Optional

Rule = Callable[[str,dict],Optional[str]]

RULES: list[Rule] = [
    rules.greeting,
    rules.choose_location,
    rules.weather,
    rules.current_time,
    rules.current_date,
    rules.capital_question,
    rules.what_is_who_is
]


def handle(text: str, profile: dict) -> str:

    """
    Docstring for handle
    
    :param text: Description
    :type text: str
    :param profile: Description
    :type profile: dict
    :return: Description
    :rtype: str
    """

    text = text.lower().strip()
    
    for rule in RULES:
        result = rule(text,profile)
        if result:
            return result
    
    return "I am not sure how to answer that yet."