
"""
AgriVision AI - Voice Assistant
Groq Whisper STT + Groq LLM + Edge TTS / gTTS
"""

import asyncio
import hashlib
import io
import os
import re

import streamlit as st

STT_MODEL = "whisper-large-v3"
LLM_MODEL = "openai/gpt-oss-20b"


LANGS = {
    "hi": {
        "label": "हिन्दी",
        "stt": "hi",
        "voice": "hi-IN-SwaraNeural",
        "gtts": "hi",
        "style": "simple spoken Hindi in Devanagari script"
    },
    "en": {
        "label": "English",
        "stt": "en",
        "voice": "en-IN-NeerjaNeural",
        "gtts": "en",
        "style": "simple spoken English"
    },
    "bho": {
        "label": "भोजपुरी",
        "stt": "hi",
        "voice": "hi-IN-SwaraNeural",
        "gtts": "hi",
        "style": "Bhojpuri in Devanagari script using simple everyday words"
    }
}


STT_HINT = {
    "hi": "खेती, फसल, पत्ती, रोग, फफूंद, छिड़काव, कीट, बीज, सिंचाई, दवा",
    "en": "farming, crop, leaf, disease, fungus, spray, pest, seed, irrigation"
}


UI = {
    "en": {
        "title": "Voice Assistant",
        "reply_lang": "Answer language",
        "hint": "Press the mic, ask your question, then press stop.",
        "mic": "Ask by voice",
        "typed": "Or type your question here",
        "thinking": "Listening and thinking...",
        "you": "You said",
        "nospeech": "Could not hear anything. Please try again.",
        "error": "Voice assistant error: {err}",
        "nokey": "Add GROQ_API_KEY in Streamlit Secrets to enable the voice assistant."
    },
    "hi": {
        "title": "वॉइस सहायक",
        "reply_lang": "जवाब की भाषा",
        "hint": "माइक दबाकर अपना सवाल बोलें।",
        "mic": "बोलकर पूछें",
        "typed": "या यहाँ अपना सवाल लिखें",
        "thinking": "सुन रहा हूँ और सोच रहा हूँ...",
        "you": "आपने कहा",
        "nospeech": "कुछ सुनाई नहीं दिया। कृपया दोबारा कोशिश करें।",
        "error": "वॉइस सहायक में त्रुटि: {err}",
        "nokey": "वॉइस सहायक चालू करने के लिए Secrets में GROQ_API_KEY जोड़ें।"
    }
}


def get_key(name):
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None

    return value or os.environ.get(name)


def build_system_prompt(scan, lang):

    if scan:
        ctx = (
            f"The farmer scanned a leaf.\n"
            f"Scan result: {scan['summary']}\n"
            f"Vetted advice:\n"
            + "\n".join(scan["advice"])
        )
    else:
        ctx = "The farmer has not scanned a leaf yet. Give general farming advice only."

    return f"""
You are AgriVision AI, a friendly farming advisor.

CURRENT FARMER CONTEXT:
{ctx}

RULES:
1. Answer only in {LANGS[lang]['style']}.
2. Give 2 to 4 short, useful sentences.
3. Understand and answer the exact latest question.
4. Do not repeat previous answers unless asked.
5. Use conversation history only for context.
6. If scan confidence is low, clearly say you are unsure.
7. Never invent a disease diagnosis.
8. Never recommend a specific pesticide brand or dosage.
9. For medicines, direct the farmer to the local agriculture officer,
   KVK or Kisan Call Centre (1800-180-1551).
10. Keep the answer simple and suitable for a small farmer.
11. If unrelated to farming, politely return to farming.
12. Do not use markdown, bullet points or emojis.
"""


def transcribe(audio_bytes, lang):

    from groq import Groq

    client = Groq(api_key=get_key("GROQ_API_KEY"))

    response = client.audio.transcriptions.create(
        file=("question.wav", audio_bytes),
        model=STT_MODEL,
        language=LANGS[lang]["stt"],
        prompt=STT_HINT.get(LANGS[lang]["stt"], ""),
        temperature=0
    )

    return (response.text or "").strip()


def ask_llm(question, history, scan, lang):

    from groq import Groq

    client = Groq(api_key=get_key("GROQ_API_KEY"))

    messages = [
        {
            "role": "system",
            "content": build_system_prompt(scan, lang)
        }
    ]

    for turn in history[-4:]:
        messages.append({"role": "user", "content": turn["q"]})
        messages.append({"role": "assistant", "content": turn["a"]})

    messages.append({
        "role": "user",
        "content": question
    })

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        max_tokens=350,
        temperature=0.7
    )

    answer = response.choices[0].message.content

    return answer.strip() if answer else "Sorry, I could not generate an answer."


def clean_for_tts(text):

    text = re.sub(r"[\U00010000-\U0010ffff\u2600-\u27bf]", "", text)
    text = re.sub(r"^\s*[-*•\d.]+\s+", "", text, flags=re.M)
    text = re.sub(r"[*_#`>]", "", text)

    return re.sub(r"\s+", " ", text).strip()


async def _edge(text, voice):

    import edge_tts

    buffer = bytearray()
    communicate = edge_tts.Communicate(text, voice)

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buffer.extend(chunk["data"])

    return bytes(buffer)


def speak(text, lang):

    text = clean_for_tts(text)

    try:
        audio_data = asyncio.run(_edge(text, LANGS[lang]["voice"]))

        if audio_data:
            return audio_data

    except Exception:
        pass

    from gtts import gTTS

    buffer = io.BytesIO()

    gTTS(
        text=text,
        lang=LANGS[lang]["gtts"]
    ).write_to_fp(buffer)

    return buffer.getvalue()


def answer_turn(question, scan, history, lang):

    answer = ask_llm(question, history, scan, lang)
    audio = speak(answer, lang)

    return {
        "q": question,
        "a": answer,
        "mp3": audio
    }


def voice_turn(audio_bytes, scan, history, lang):

    question = transcribe(audio_bytes, lang)

    if len(question) < 2:
        return None

    return answer_turn(question, scan, history, lang)


def render_voice_assistant(scan, ui_lang="en"):

    u = UI.get(ui_lang, UI["en"])

    st.divider()
    st.subheader("🎙️ " + u["title"])

    if not get_key("GROQ_API_KEY"):
        st.info(u["nokey"])
        return

    lang = st.radio(
        u["reply_lang"],
        list(LANGS.keys()),
        index=list(LANGS.keys()).index(ui_lang) if ui_lang in LANGS else 0,
        format_func=lambda key: LANGS[key]["label"],
        horizontal=True,
        key="va_lang"
    )

    st.caption(u["hint"])

    ss = st.session_state

    if "va_hist" not in ss:
        ss["va_hist"] = []

    if "va_last_text" not in ss:
        ss["va_last_text"] = None

    if "va_last_audio" not in ss:
        ss["va_last_audio"] = None

    if "va_text_value" not in ss:
        ss["va_text_value"] = ""

    hist = ss["va_hist"]

    sid = scan["id"] if scan else "none"

    if ss.get("va_scan") != sid:
        ss["va_scan"] = sid
        ss["va_hist"] = []
        ss["va_last_text"] = None
        ss["va_last_audio"] = None
        ss["va_text_value"] = ""
        hist = ss["va_hist"]

    audio = st.audio_input(
        u["mic"],
        key="va_audio"
    )

    typed = st.text_input(
        u["typed"],
        key="va_text"
    )

    col1, col2 = st.columns(2)

    with col1:
        ask_text = st.button(
            "Ask typed question",
            key="va_ask_text"
        )

    with col2:
        ask_audio = st.button(
            "Process voice recording",
            key="va_ask_audio"
        )

    new = None

    try:

        if ask_text and typed.strip():

            question = typed.strip()

            with st.spinner(u["thinking"]):
                new = answer_turn(question, scan, hist, lang)

            ss["va_last_text"] = question

        elif ask_audio and audio is not None:

            audio_bytes = audio.getvalue()

            audio_hash = hashlib.md5(audio_bytes).hexdigest()

            if audio_hash != ss["va_last_audio"]:

                with st.spinner(u["thinking"]):
                    new = voice_turn(audio_bytes, scan, hist, lang)

                ss["va_last_audio"] = audio_hash

                if new is None:
                    st.warning(u["nospeech"])

            else:
                st.info("This recording has already been processed. Please record a new question.")

    except Exception as error:

        st.error(
            u["error"].format(
                err=f"{type(error).__name__}: {str(error)[:250]}"
            )
        )

    if new:

        hist.append(new)

        st.rerun()

    for index, turn in enumerate(hist):

        with st.chat_message("user", avatar="🧑‍🌾"):
            st.write(turn["q"])

        with st.chat_message("assistant", avatar="🌿"):
            st.write(turn["a"])

            if turn.get("mp3"):
                st.audio(
                    turn["mp3"],
                    format="audio/mp3",
                    autoplay=(index == len(hist) - 1)
                )
