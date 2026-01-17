import wikipedia

def lookup(query: str) -> str:

    """
    Docstring for lookup
    
    :param query: Description
    :type query: str
    :return: Description
    :rtype: str
    """

    try:
        return wikipedia.summary(query, sentences = 2)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"That topic is ambiguous. For example: {e.options[:3]}"
    except wikipedia.exceptions.PageError:
        return "I couldn't find anything on that topic."