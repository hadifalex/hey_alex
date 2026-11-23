# Hey Alex

*Hey Alex* is my take on a motivational AI version of myself for friends and family.

*Alex* has an infamy for "alexplanations", and so he's here to answer all your questions. Despite that, he acknowledges his limitations and will always defer to the "real" Alex if he cannot answer.

# Privacy: what stays on the device

Alex is built to run fully offline. This repo is public so you can check for yourself.

- **Speech-to-text** (Vosk), **text-to-speech** (Piper) and the **language model** (Ollama) all run locally.
- With `no_internet: true` in the profile (the default), the only network calls in the code go to `localhost:11434`, the local Ollama server. The Wikipedia and weather code is switched off.
- Audio is never written to disk. The conversation memory lives in RAM only and is gone when the program exits.
- Alex has to listen to hear his wake word, so while "asleep" the microphone is still transcribing locally. Nothing from that is stored or sent anywhere.
- Internet is needed once, for setup (installing packages and downloading models). After that it can be disconnected. If you want a hard guarantee, block outbound traffic for the device or for Ollama. Some Ollama installs check for their own updates, so don't just assume.

If you ever change your mind, setting `no_internet: false` in a profile enables Wikipedia and weather lookups. Those rules are less tested than the rest.

# The pipeline

- **Speech-to-Text (STT):** Vosk + microphone, so you can talk to Alex.
- **Router:** rule-based answers for simple things (time, date, and, if the internet is allowed, Wikipedia and weather).
- **Persistent LLM (Ollama):** everything the router can't answer. It remembers the last few exchanges.
- **Text-to-Speech (TTS):** Piper, so Alex answers out loud.
- **Profiles:** a YAML personality per person, fully customisable.
- **Modes:** voice in (default), text in (`--text`), diagnostic (`--diagnostic`).

# Setup

You need Python 3.10 or newer, a microphone and a speaker.

## 1. Get the code and install the Python packages

Linux / Raspberry Pi / macOS:

```bash
git clone https://github.com/hadifalex/hey_alex.git
cd hey_alex
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows (Git Bash: `source venv/Scripts/activate`, PowerShell: `venv\Scripts\Activate.ps1`):

```bash
git clone https://github.com/hadifalex/hey_alex.git
cd hey_alex
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

On Raspberry Pi OS / Debian you may first need the system packages:

```bash
sudo apt install python3-venv libportaudio2
```

## 2. Install Ollama and a model

Install Ollama from https://ollama.com (on Linux: `curl -fsSL https://ollama.com/install.sh | sh`), then download a model. Alex was built for **llama3**, which is the one to use on a normal PC (it is about a 4.7 GB download and needs roughly 6 GB of free RAM or more):

```bash
ollama pull llama3
```

On a smaller machine, such as a Raspberry Pi with 2-4 GB of RAM, llama3 won't fit. Use a smaller model instead, for example:

```bash
ollama pull llama3.2:1b
```

Smaller models are faster and lighter, but less witty. Whichever you pick, put its name in `config/llm.yaml` (step 4); `config/llm.example.yaml` has a guide.

## 3. Download the speech models

- **Vosk (listening):** download `vosk-model-small-en-us-0.15` from https://alphacephei.com/vosk/models, unzip it, and put the folder in `models/`, so you end up with `models/vosk-model-small-en-us-0.15/`.
- **Piper (talking):** the voice lives in `assistant/audio/piper_voices/` and needs both the `.onnx` file and its `.onnx.json` file. The default is `en_GB-northern_english_male-medium`. Other voices are in the `rhasspy/piper-voices` collection on Hugging Face; if you change the voice, update the filename in `assistant/audio/tts.py`.

## 4. Create your config

The files in `config/` named `*.example.yaml` are templates. Copy each one without `.example` and edit your copy (your copies are ignored by git because they are specific to your machine):

```bash
cp config/audio.example.yaml config/audio.yaml
cp config/llm.example.yaml config/llm.yaml
```

- `audio.yaml`: which microphone to use (see Troubleshooting).
- `llm.yaml`: which Ollama model to use (`llama3` on a PC, something smaller on a low-memory machine). If this file is missing, `llama3` is used.

## 5. Run it

```bash
python run.py --profile default
```

Arguments:

- `--profile <name>`: which personality to load (default: `default`).
- `--text`: type instead of talk (replies are still spoken).
- `--diagnostic`: show the internal logs from Vosk and Ollama.

# Profiles

A profile is a folder in `profiles/` with a `personality.yaml`. It holds the system prompt (how Alex should behave and talk), the owner's nicknames, the wake, sleep and quit words, and the greeting lines.

To make one for a new person, copy `profiles/default` to `profiles/<name>`, edit the YAML, and run `python run.py --profile <name>`.

Only `profiles/default` is shared in this repo. Everything else in `profiles/` is ignored by git on purpose, since personal profiles contain notes about real people.

# Command words

These are set per profile (under `commands:`) and can be spoken or typed. The defaults:

- waking (start engaging again): "hey Alex", "Alex", "wake up"
- sleeping (stay on, but stop responding): "bye", "bye bye", "goodbye", "shut up", "be quiet"
- quitting (stop the program): "quit", "exit"

# Troubleshooting

**Alex doesn't hear me.** Run the microphone check from the repo root:

```bash
python mic_check.py
```

It lists the audio devices, records 4 seconds, shows how loud the signal was and what Vosk understood. If it is silent or quiet, pick another device with `python mic_check.py <number>`. When you find the right one, put its number in `config/audio.yaml`:

```yaml
input_device: 3
```

(note the space after the colon). Also check that the microphone isn't muted in your operating system and that desktop apps are allowed to use it (on Windows: Settings > Privacy & security > Microphone).

**"Vosk model not found".** Do step 3 above.

**Alex says "my brain isn't answering".** Ollama isn't running, or the model isn't installed. Run `ollama list` to see what you have, and make sure the `model:` in `config/llm.yaml` is in that list.

**Replies take forever.** The model is too big for the machine. Try a smaller one in `config/llm.yaml`.