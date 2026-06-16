import sounddevice as sd
import scipy.io.wavfile as wav
import requests
import os
import base64
import numpy as np
from dotenv import load_dotenv
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
groq_client = Groq(api_key=os.getenv("API_KEY"))

DATA_DIR = "data"
PERSIST_DIR = "vectorstore"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PERSIST_DIR, exist_ok=True)

# ── Vector Store ──────────────────────────────────────────
def load_vector_store():
    print("Embedding model loading...")
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = Chroma(persist_directory=PERSIST_DIR, embedding_function=embedding_model)

    all_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.txt') or f.endswith('.pdf')]
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

    for file_name in all_files:
        file_path = os.path.join(DATA_DIR, file_name)
        existing = vector_db.get(where={"source": file_path})
        if existing and len(existing['ids']) > 0:
            print(f"Skipping '{file_name}' — already parsed.")
            continue
        print(f"Processing '{file_name}'...")
        loader = PyPDFLoader(file_path) if file_name.endswith('.pdf') else TextLoader(file_path, encoding="utf-8")
        chunks = text_splitter.split_documents(loader.load())
        vector_db.add_documents(chunks)
        print(f"{len(chunks)} chunks added!")

    return vector_db

# ── Translate to English ──────────────────────────────────
def translate_to_english(query):
    result = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": f"Translate to English, return ONLY translation:\n{query}"}],
        temperature=0
    )
    return result.choices[0].message.content.strip()

# ── RAG Answer ────────────────────────────────────────────
def get_rag_answer(user_query, vector_store):
    english_query = translate_to_english(user_query)
    docs = vector_store.similarity_search(english_query, k=4)
    context = "\n".join([f"Chunk {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)])

    system_prompt = f"""
You are BharatVoice, a helpful AI assistant for Om Sai Medical Store in Nashik.
Answer ONLY from the Context below. 
If answer not found, say "Sorry, mujhe is baare mein nahi pata."
Reply in the SAME language the user asked in — Hindi, Hinglish, or Marathi.
Keep answer SHORT — max 2-3 lines. This is a voice response.

Context:
{context}
"""
    result = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=0.2
    )
    return result.choices[0].message.content

# ── Voice Input ───────────────────────────────────────────
def record_audio(filename="input.wav", duration=5, samplerate=16000):
    print(f"\nBolo abhi — {duration} seconds hain!")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    wav.write(filename, samplerate, audio)
    print("Recording done!")
    return filename

def speech_to_text(audio_file):
    with open(audio_file, "rb") as f:
        audio_data = f.read()

    payload={
        "file":("audio.wav",audio_data,"audio/wav"),
        "language_code":(None,"hi-IN"),
        "model":(None,"saaras:v3")
    }    



    response = requests.post(
        "https://api.sarvam.ai/speech-to-text",
        headers={"api-subscription-key": SARVAM_API_KEY},
        files=payload
    )
    if response.status_code == 200:
        return response.json().get("transcript", "")
    print(f"STT Error: {response.text}")
    return None

# ── Voice Output ──────────────────────────────────────────
def text_to_speech(text, output_file="output.wav"):
    response = requests.post(
        "https://api.sarvam.ai/text-to-speech",
        headers={"api-subscription-key": SARVAM_API_KEY, "Content-Type": "application/json"},
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
        audio_data = base64.b64decode(response.json()["audios"][0])
        with open(output_file, "wb") as f:
            f.write(audio_data)
        return output_file
    print(f"TTS Error: {response.text}")
    return None

def play_audio(filename):
    samplerate, data = wav.read(filename)
    sd.play(data, samplerate)
    sd.wait()

# ── Main Loop ─────────────────────────────────────────────
if __name__ == "__main__":
    vector_store = load_vector_store()
    print("\n🎙️ BharatVoice Ready!")
    print("=" * 60)

    while True:
        try:
            audio_file = record_audio(duration=6)
            user_text = speech_to_text(audio_file)

            if not user_text:
                print("Kuch samajh nahi aaya — dobara bolo!")
                continue

            print(f"Tune bola: {user_text}")

            if any(word in user_text.lower() for word in ["exit", "band karo", "bye", "ok bye"]):
                farewell = "Aapka din shubh rahe! Namaste!"
                output_audio = text_to_speech(farewell)
                if output_audio:
                    play_audio(output_audio)
                break

            print("Answer dhundh raha hoon...")
            answer = get_rag_answer(user_text, vector_store)
            print(f"Answer: {answer}")

            output_audio = text_to_speech(answer)
            if output_audio:
                play_audio(output_audio)

        except KeyboardInterrupt:
            print("\nBand kar diya!")
            break 