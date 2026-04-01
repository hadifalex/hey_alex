# Intro - Hey Alex

*Hey Alex* is my take for a motivational AI version of myself for friends and family.

*Alex* has an infamy for "alexplanations" and thus he's here to answer all your questions.
Despite that, he acknowledges limitations and will always defer to the "real" Alex if it cannot answer.

The LLM model is fully local and does not require internet connection to operate.

# The pipeline

*Alex* is made from different parts:
- Speech-to-Text (STT): via Vosk + Microphone, to allow the user to input with their voice.
- A Router: rule-based answering logic that taps into basic internet searches (wikipedia + weather).
- A persistent LLM (Ollama): for questions not directly addressable by the router (or if the user wants a fully local version of me).
- Text-to-Speech (TTS): via Piper, to allow for the LLM to respond in a voice of your choosing.
- Profiles: The LLM can be loaded with a YAML personality profile that can be fully customised.
- Operating modes: Can be initialised with parser arguments for:
    - Default (voice input -> voice + text output)
    - Text (text input -> voice + text output)
    - Diagnostic (enables diagnostic comments from Vosk, Ollama, GIN)


# Initialise the virtual environment

In bash, you can do this running
`source venv/Scripts/activate`

# parser arguments

You can run the file using
`python run.py`

which accepts the following additional arguments
--profile       : to select a user profile
--text          : to enter text mode only
--diagnostic    : to have full access to the diagnostic channels from Vosk, Ollama, and GIN.

# Command words

These are commands that allow you to pause, restart, or quit the interaction with "Alex".
These are currently hardcoded within `main()`.
They can be either spoken or written (when in pure text mode).

- waking commands (start engaging with user)
    - "hey Alex"
    - "Alex"
    - "wake up"
- sleeping commands (stay active but stop responding)
    - "bye"
    - "bye bye"
    - "goodbye"
    - "shut up"
    - "be quiet"
- quitting commands (quit the program)
    - "quit"
    - "exit"