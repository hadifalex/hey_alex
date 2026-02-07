# this is here to ensure that the LLM has SOME meat to it.
## normally, the ask_llm would just be initialised with a "blank slate" and will not know what happened.
## This is to ensure that a conversation could be maintained. 


MAX_HISTORY = 20    # keep the last 20 exchanges

conversation_history = []

def append_message(role:str,content:str):
    """
    This is just to update the memory.
    It will store information, and if the total history is larger than MAX_HISTORY, 
    then pop the oldest out of the list.
    
    :role (str): whether the text is by the user or the LLM
    :content (str): the content of the conversation.
    """
    conversation_history.append({"role":role,"content":content})
    if len(conversation_history)>MAX_HISTORY:
        conversation_history.pop(0)


def get_recent_history() -> list:
    return conversation_history