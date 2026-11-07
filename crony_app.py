import os
import datetime
import subprocess
import webbrowser

import streamlit as st
import speech_recognition as sr
import ollama

# ----------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------
st.set_page_config(page_title="Crony", page_icon="🎙️", layout="centered")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;800&family=DM+Sans:wght@400;500&display=swap');

:root {
  --ink: #0D1B2A;
  --surface: #14283D;
  --surface-2: #1B3550;
  --text: #E6EEF5;
  --muted: #8FA5B8;
  --accent: #5CE1E6;
}

html, body, [class*="css"], .stApp {
  font-family: 'DM Sans', sans-serif;
  color: var(--text);
}
.stApp { background: var(--ink); }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 760px; padding-top: 2.2rem; }

.crony-title {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800;
  font-size: 3rem;
  letter-spacing: -0.03em;
  margin: 0;
  line-height: 1;
}
.crony-sub { color: var(--muted); margin: 0.4rem 0 0 0; }

.status {
  display: inline-flex; align-items: center; gap: 8px;
  background: var(--surface); border: 1px solid var(--surface-2);
  padding: 6px 12px; border-radius: 999px; font-size: 0.85rem; color: var(--muted);
}
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }
.dot.off { background: #E5636D; }

[data-testid="stChatMessage"] {
  background: var(--surface);
  border: 1px solid var(--surface-2);
  border-radius: 18px;
  padding: 14px 16px;
}

div.stButton > button[kind="primary"] {
  background: var(--accent);
  color: var(--ink);
  border: none;
  border-radius: 16px;
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 600;
  font-size: 1.1rem;
  padding: 0.8rem 1rem;
}
div.stButton > button[kind="primary"]:hover { filter: brightness(1.08); color: var(--ink); }
div.stButton > button:focus-visible { outline: 3px solid #fff; outline-offset: 2px; }

section[data-testid="stSidebar"] { background: var(--surface); }
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------
USER_NAME = "Goushik"
NAME_VARIANTS = ["chronic", "crony", "krony", "cronie", "crone", "krone", "cloney", "carney"]

SYSTEM_PROMPT = (
    f"You are Crony, a friendly voice assistant for {USER_NAME}. "
    "Answer in 1-2 short sentences. No markdown, no emojis."
)


def get_models():
    try:
        return [m.model for m in ollama.list().models] or ["qwen2.5:1.5b"]
    except Exception:
        return []


def clean_command(command):
    for v in NAME_VARIANTS:
        command = command.replace(v, "")
    return command.strip()


# ----------------------------------------------------------------------
# Voice output (Windows built-in voice, non-blocking)
# ----------------------------------------------------------------------
def speak(text):
    prev = st.session_state.get("speech_proc")
    if prev and prev.poll() is None:
        prev.terminate()
    env = os.environ.copy()
    env["CRONY_TEXT"] = text
    cmd = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$s.Rate = 1; $s.Speak($env:CRONY_TEXT)"
    )
    try:
        st.session_state.speech_proc = subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", cmd], env=env
        )
    except Exception:
        pass


# ----------------------------------------------------------------------
# Voice input
# ----------------------------------------------------------------------
def listen_once():
    """Returns (text, error_message)."""
    r = sr.Recognizer()
    names = sr.Microphone.list_microphone_names()
    idx = next(
        (i for i, n in enumerate(names) if "Microphone Array" in n and "Intel" in n),
        None,
    )
    try:
        with sr.Microphone(device_index=idx) as source:
            r.adjust_for_ambient_noise(source, duration=0.8)
            audio = r.listen(source, timeout=8, phrase_time_limit=10)
    except sr.WaitTimeoutError:
        return "", "I didn't hear anything. Tap the button and start speaking."
    except Exception as e:
        return "", f"Microphone problem: {type(e).__name__}"

    try:
        return r.recognize_google(audio), ""
    except sr.UnknownValueError:
        return "", "I couldn't understand that. Try again."
    except sr.RequestError:
        return "", "Speech recognition needs an internet connection."


# ----------------------------------------------------------------------
# Commands and AI
# ----------------------------------------------------------------------
def quick_command(command):
    """Handle built-in commands. Returns reply text, or None to use the AI."""
    if "time" in command:
        return "The time is " + datetime.datetime.now().strftime("%I:%M %p")
    if command.startswith("play"):
        song = command.replace("play", "", 1).strip()
        try:
            import pywhatkit
            pywhatkit.playonyt(song)
            return f"Playing {song} on YouTube."
        except Exception:
            return "I couldn't open YouTube. Check your internet connection."
    if "open google" in command:
        webbrowser.open("https://www.google.com")
        return "Opening Google."
    if "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."
    if "open linkedin" in command:
        webbrowser.open("https://www.linkedin.com")
        return "Opening LinkedIn."
    if "open github" in command:
        webbrowser.open("https://github.com")
        return "Opening GitHub."
    if command.startswith("search"):
        query = command.replace("search", "", 1).replace("for", "", 1).strip()
        if query:
            webbrowser.open("https://www.google.com/search?q=" + query.replace(" ", "+"))
            return f"Searching Google for {query}."
    if "open notepad" in command:
        subprocess.Popen(["notepad"])
        return "Opening Notepad."
    if "open calculator" in command:
        subprocess.Popen(["calc"])
        return "Opening Calculator."
    return None


def ai_stream(model):
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[-10:]
    ]
    stream = ollama.chat(
        model=model,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, *history],
        stream=True,
    )
    for chunk in stream:
        yield chunk["message"]["content"]


def process(raw_text, model, voice_on):
    command = clean_command(raw_text.lower())

    st.session_state.messages.append({"role": "user", "content": raw_text})
    with st.chat_message("user"):
        st.write(raw_text)

    with st.chat_message("assistant", avatar="🎙️"):
        if not command:
            reply = f"Yes {USER_NAME}?"
            st.write(reply)
        else:
            reply = quick_command(command)
            if reply is not None:
                st.write(reply)
            else:
                try:
                    reply = st.write_stream(ai_stream(model))
                except Exception:
                    reply = (
                        "I can't reach Ollama. Open the Ollama app and "
                        "make sure the model is installed."
                    )
                    st.error(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    if voice_on:
        speak(reply)


# ----------------------------------------------------------------------
# State
# ----------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

models = get_models()

# ----------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Settings")
    if models:
        model = st.selectbox(
            "Model",
            models,
            index=models.index("qwen2.5:1.5b") if "qwen2.5:1.5b" in models else 0,
        )
    else:
        model = "qwen2.5:1.5b"
        st.warning("Ollama isn't running. Open the Ollama app.")
    voice_on = st.toggle("Speak replies aloud", value=True)
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("Commands: what time is it, play <song>, search <topic>, open google / youtube / github / linkedin / notepad / calculator. Anything else goes to the AI.")

# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.markdown('<p class="crony-title">Crony</p>', unsafe_allow_html=True)
st.markdown(f'<p class="crony-sub">Your voice assistant, running on this laptop.</p>', unsafe_allow_html=True)

online = bool(models)
st.markdown(
    f'<div class="status" style="margin-top:14px;"><span class="dot {"" if online else "off"}"></span>'
    f'{"AI ready: " + model if online else "AI offline"}</div>',
    unsafe_allow_html=True,
)
st.write("")

# ----------------------------------------------------------------------
# Conversation
# ----------------------------------------------------------------------
if not st.session_state.messages:
    st.info(f"Hi {USER_NAME}. Tap the mic button and speak, or type a message below.")

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🎙️" if m["role"] == "assistant" else None):
        st.write(m["content"])

# ----------------------------------------------------------------------
# Input
# ----------------------------------------------------------------------
if st.button("🎤  Tap and speak", type="primary", use_container_width=True):
    with st.spinner("Listening… speak now"):
        heard, err = listen_once()
    if err:
        st.warning(err)
    elif heard:
        process(heard, model, voice_on)

typed = st.chat_input("Or type to Crony…")
if typed:
    process(typed, model, voice_on)
