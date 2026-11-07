# CRONY-2.0
Crony: a free, local AI voice assistant
Crony is a voice assistant that runs on your own laptop. You talk to it, it understands you, answers out loud, and can control your PC. The AI model runs locally through Ollama, so there is no API key, no subscription, and no cost.
I built it as a student project with ₹0 budget, to learn how speech recognition, local LLMs and a web UI fit together.<img width="737" height="166" alt="image" src="https://github.com/user-attachments/assets/7ff4f4a4-7cc5-4559-8659-d48fbac9c7c8" />
Features
Voice input: speak naturally and Crony transcribes it
Local AI brain: Qwen 2.5 (1.5B) via Ollama, with short-term conversation memory
Spoken replies: uses the built-in Windows voice
PC and web commands: time, play a song on YouTube, search Google, open websites and apps
Chat UI: Streamlit interface with streaming replies, model picker and voice toggle
Name-mishearing fix: speech engines often hear "Crony" as "chronic", so those variants are cleaned up automatically
How it works
Microphone -> SpeechRecognition -> command check -> Ollama (Qwen) -> Windows voice
                                        |
                              built-in commands (time, YouTube, apps)
PyAudio captures audio from the microphone.
SpeechRecognition converts it to text.
If the text matches a built-in command, Crony runs it directly.
Otherwise the text, plus the last 10 messages, goes to the local model through Ollama.
The reply is shown in the chat UI and spoken aloud.
Requirements
Windows 10 or 11
Python 3.11 (PyAudio has no ready-made install for newer versions such as 3.14)
Ollama installed and running
A microphone
Internet connection for speech recognition (the AI itself works offline)
About 2 GB of free disk space (the model is about 1 GB)
Setup
bash
# 1. Clone the repository
git clone https://github.com/<your-username>/crony-ai-assistant.git
cd crony-ai-assistant

# 2. Download the AI model
ollama pull qwen2.5:1.5b

# 3. Install the Python packages
py -3.11 -m pip install -r requirements.txt

# 4. Start Crony
py -3.11 -m streamlit run crony_app.py

Your browser opens at http://localhost:8501. Click Tap and speak, or type in the box at the bottom.

If pip install PyAudio fails, try py -3.11 -m pip install pipwin followed by pipwin install pyaudio, or conda install -c conda-forge pyaudio.

Things to say
Say	What happens
"what time is it"	Crony tells you the time
"play Kalki songs"	Plays it on YouTube
"search for Python tutorials"	Opens a Google search
"open YouTube" / "open GitHub" / "open Google"	Opens the website
"open Notepad" / "open Calculator"	Opens the app
Anything else	Answered by the local AI
Configuration

Open crony_app.py and change:

USER_NAME to your own name
SYSTEM_PROMPT to change Crony's personality
the model in the sidebar. Any model installed in Ollama appears there, for example ollama pull qwen2.5:3b for better answers if you have the disk space
Known limitations
Tap-to-talk only. There is no always-listening wake word yet.
Speech recognition uses Google's free web service, so it needs internet.
A 1.5B model is fast but sometimes gives wrong or generic answers.
Windows only, because voice output and app launching use Windows tools.
The microphone is picked by name ("Microphone Array" with "Intel"). If yours is different, edit listen_once().
Roadmap
 Long-term memory with SQLite
 Offline speech recognition with Whisper
 Wake word ("Hey Crony")
 More PC controls: volume, screenshots, file search, reminders
 Linux and macOS support
Built with

Python · Streamlit · Ollama · Qwen 2.5 · SpeechRecognition · PyAudio · pywhatkit

License

MIT. See LICENSE.
