from assistant.retrieval.wikipedia import lookup

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

    if text.startswith("what is") or text.startswith("who is"):
        topic = text.replace("what is","").replace("who is","").strip()
        return lookup(topic)
    
    if "capital of" in text:
        topic = text.split("capital of")[-1].strip()
        return lookup(f"capital of {topic}")
    
    return "I am not sure how to answer that yet."