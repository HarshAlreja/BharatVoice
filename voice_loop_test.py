import sounddevice as sd
import scipy.io.wavfile as wav
import requests
import os
import base64
import numpy as np
from dotenv import load_dotenv

load_dotenv()
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

def record_audio(filename="input.wav", duration=7, samplerate=16000):
    print(f"\n🎙️  Bharat Voice - {duration} seconds hain, bolo!....")
    audio = sd.rec(
       int(duration * samplerate),
       samplerate=samplerate,
       channels=1,
       dtype='int16'
    )
    sd.wait()
    
    # Volume Normalize (Bluetooth optimization)
    max_volume = np.max(np.abs(audio))
    if max_volume > 0:
        audio = (audio / max_volume * 32767).astype(np.int16)
        
    wav.write(filename, samplerate, audio)
    print("✅ Recording Done !....")
    return filename

def speech_to_text(audio_file):
    with open(audio_file, "rb") as f:
        audio_data = f.read()

    payload = {
          "file": ("audio.wav", audio_data, "audio/wav"),
          "language_code": (None, "hi-IN"),
          "model": (None, "saaras:v3")
    }

    response = requests.post(
        "https://api.sarvam.ai/speech-to-text",
        headers={"api-subscription-key": SARVAM_API_KEY},
        files=payload
    ) 
    
    if response.status_code == 200:
        # ✅ Fixed: lowercase 'transcript'
        return response.json().get("transcript", "")
    else:
        print(f"❌ STT Error: {response.status_code} - {response.text}")
        return None

def text_to_speech(text, output_file="output.wav"):  # ✅ Fixed: Added .wav extension
    response = requests.post(
        "https://api.sarvam.ai/text-to-speech",
        headers={
         "api-subscription-key": SARVAM_API_KEY,
         "Content-Type": "application/json"  # ✅ Fixed: Content-Type spelling
        },
        json={
            "target_language_code": "hi-IN",
            "text": text,
            "speaker": "anushka",
            "pace": 1.0,
            "loudness": 1.5,
            "model": "bulbul:v2"  # ✅ Fixed: bulbul:v2 stable model
        }
    ) 
    if response.status_code == 200:
        audio_data = base64.b64decode(response.json()["audios"][0])
        with open(output_file, "wb") as f:
            f.write(audio_data)
        return output_file
    else:
        print(f"❌ TTS Error: {response.status_code} - {response.text}")
        return None

def play_audio(filename):
    samplerate, data = wav.read(filename)
    sd.play(data, samplerate)
    sd.wait()

# --- Execution Main ---
print("----- BharatVoice Loop Test ----")
audio_file = record_audio(duration=7)
user_text = speech_to_text(audio_file)

if user_text:
    print(f"✨ You said: {user_text}")
    response_text = f"आपने कहा {user_text}. मैं भारत वॉइस हूँ, बताइए क्या सहायता करूँ?"
    print(f"🤖 Response Text: {response_text}")
    
    output_audio = text_to_speech(response_text)
    if output_audio:
         print("🔊 Playing response via Bluetooth/Speakers...")
         play_audio(output_audio)
else:
    print("⚠️ Audio empty aaya ya pipeline leak ho gayi.")