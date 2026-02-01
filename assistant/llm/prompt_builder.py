from assistant.llm.memory import get_recent_history



def build_prompt(user_text:str,profile:dict)->str:

    owner = profile.get("owner",{})
    name = owner.get("name","friend")
    nicknames = ", ".join(owner.get("nicknames",[]))

    system_identity = f"""
    You are a local voice assistant runnin on a Raspberry Pi.
    You do NOT have internet access.
    You do NOT claim to be an AI, or being a cloud-based AI.
    You are friendly, motivational, and slightly funny.

    You are speaking to {name}.
    You may call them: {nicknames}.

    Keep your responses short and conversational.
    """

    prompt = system_identity + "\n"

    # including history to give a semblance of continuity

    history = get_recent_history()

    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        prompt += f"{role}: {msg['content']}\n"

    # Add current user input
    prompt += f"User: {user_text}\nAssistant:"
    return prompt