from assistant.logic import rules
from typing import Callable, Optional

# This is from the basic local LLM
from assistant.llm.ollama_client import ask_llm
from assistant.llm.prompt_builder import build_prompt
from assistant.llm.memory import append_message

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
    for rule in RULES:
        result = rule(text,profile)
        if result:
            return result
    
    # if no rules are matched -> ask the LLM (llama3)
    prompt = build_prompt(text,profile)
    if llm is not None:
        response = llm.generate(prompt)
    else:
        print("using ask_llm and NOT llm.generate!")
        response = ask_llm(prompt)

    # update short-term memory
    append_message("user",text)
    append_message("assistant",response)

    return response