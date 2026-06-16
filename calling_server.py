from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import requests
import os
import base64
import tempfile
from dotenv import load_dotenv
from groq import Groq
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

app = Flask(__name__)
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
groq_client = Groq(api_key=os.getenv("API_KEY"))

# Static folder banao audio files ke liye
os.makedirs('static', exist_ok=True)

# Vector store load karo
print("Loading vector store...")
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = Chroma(
    persist_directory="vectorstore",
    embedding_function=embedding_model
)
print("Vector store ready!")

def translate_to_english(query):
    result = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": f"Translate to English only, nothing else:\n{query}"}],
        temperature=0
    )
    return result.choices[0].message.content.strip()

def get_rag_answer(user_query):
    english_query = translate_to_english(user_query)
    docs = vector_store.similarity_search(english_query, k=4)
    context = "\n".join([f"Chunk {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)])

    result = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": f"""
You are BharatVoice, AI assistant for Om Sai Medical Store Nashik.
Answer ONLY from Context below. Keep answer SHORT — max 2 lines. This is a voice call.
If not found: "Sorry, mujhe is baare mein nahi pata."
Reply in SAME language as user — Hindi, Hinglish, or Marathi.
Context: {context}"""},
            {"role": "user", "content": user_query}
        ],
        temperature=0.2
    )
    return result.choices[0].message.content

def sarvam_tts(text):
    response = requests.post(
        "https://api.sarvam.ai/text-to-speech",
        headers={
            "api-subscription-key": SARVAM_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "target_language_code": "hi-IN",
            "text": text,
            "speaker": "anushka",
            "pace": 1.0,
            "loudness": 1.5,
            "model": "bulbul:v2"
        }
    )
    if response.status_code == 200:
        return base64.b64decode(response.json()["audios"][0])
    print(f"TTS Error: {response.text}")
    return None

# ── ROUTE 1 — Jab call aaye ──────────────────────────────
@app.route("/incoming-call", methods=['GET', 'POST'])
def incoming_call():
    response = VoiceResponse()
    gather = Gather(
        input='speech',
        action='/process-speech',
        method='POST',
        language='hi-IN',
        speech_timeout='auto',
        timeout=5
    )
    gather.say(
        "Namaste! Om Sai Medical Store mein aapka swagat hai. Apna sawaal poochein.",
        language='hi-IN'
    )
    response.append(gather)
    response.say("Koi jawab nahi mila. Phir call karein.", language='hi-IN')
    return Response(str(response), mimetype='text/xml')

# ── ROUTE 2 — User ne kuch bola ─────────────────────────
@app.route("/process-speech", methods=['GET', 'POST'])
def process_speech():
    response = VoiceResponse()
    user_speech = request.form.get('SpeechResult', '')

    print(f"\nUser ne bola: {user_speech}")

    if not user_speech.strip():
        response.say("Mujhe aapki awaaz nahi aayi. Dobara poochein.", language='hi-IN')
        gather = Gather(
            input='speech',
            action='/process-speech',
            method='POST',
            language='hi-IN',
            speech_timeout='auto',
            timeout=5
        )
        response.append(gather)
        return Response(str(response), mimetype='text/xml')

    # RAG se answer lo
    answer = get_rag_answer(user_speech)
    print(f"Answer: {answer}")

    # Sarvam TTS se audio banao
    audio_data = sarvam_tts(answer)

    if audio_data:
        # Audio file temporarily save karo
        tmp = tempfile.NamedTemporaryFile(
            delete=False,
            suffix='.wav',
            dir='static',
            prefix='response_'
        )
        tmp.write(audio_data)
        tmp.close()
        filename = os.path.basename(tmp.name)
        audio_url = f"{request.host_url}static/{filename}"
        print(f"Audio URL: {audio_url}")
        response.play(audio_url)
    else:
        # Fallback — Twilio ki built-in voice use karo
        response.say(answer, language='hi-IN')

    # Agle sawaal ke liye gather
    gather = Gather(
        input='speech',
        action='/process-speech',
        method='POST',
        language='hi-IN',
        speech_timeout='auto',
        timeout=5
    )
    gather.say("Koi aur sawaal hai?", language='hi-IN')
    response.append(gather)
    response.say("Dhanyawad! Aapka din shubh rahe. Namaste!", language='hi-IN')

    return Response(str(response), mimetype='text/xml')

# ── Static files serve karo ─────────────────────────────
@app.route('/static/<filename>')
def serve_audio(filename):
    from flask import send_from_directory
    return send_from_directory('static', filename)

if __name__ == "__main__":
    print("=" * 60)
    print("BharatVoice Calling Server Starting...")
    print("Server: http://localhost:5000")
    print("Webhook: http://localhost:5000/incoming-call")
    print("=" * 60)
    app.run(port=5000, debug=True)