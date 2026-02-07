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

def handle(text: str, profile: dict,llm = None) -> str:

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
    
    # try rules first
    if not profile.get("no_internet",False):
        for rule in RULES:
            result = rule(text,profile)
            if result:
                return result
    
    # if no rules are matched -> ask the LLM (llama3)
    if llm is not None:
        response = llm.generate(text, profile)
    else:
        raise RuntimeError("No LLM available for fallback")

    return response