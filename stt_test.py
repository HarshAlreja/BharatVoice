import sounddevice as sd
import scipy.io.wavfile as wav
import requests
import os 
import numpy as np
from dotenv import load_dotenv

load_dotenv()
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

def record_audio(filename="input.wav", duration=5, samplerate=16000):
    print(f"Recording... {duration} seconds mein bolo!....")
    
    # Forceful Recording settings for Windows Laptop Mics
    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,         # Mono channel mandatory for Sarvam
        dtype='int16'       # 16-bit PCM mandatory
    )
    sd.wait()
    
    # Volume check to see what Python captured
    max_volume = np.max(np.abs(audio))
    print(f"🔊 Python Internal Volume Level Captured: {max_volume}")
    
    # Normalizing audio if it's too quiet
    if max_volume > 0:
        audio = (audio / max_volume * 32767).astype(np.int16)
        
    wav.write(filename, samplerate, audio)
    print("Recording complete!..... Processing with Sarvam AI...")
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
        return response.json().get("transcript", "")
    else:
        print(f"❌ STT Error: {response.status_code} - {response.text}")
        return None

# Execution
audio_file = record_audio(duration=5)
text = speech_to_text(audio_file)

if text is not None:
    if text.strip() == "":
        print("\n⚠️ Sarvam ne respond kiya par Text khali aaya!")
    else:
        print(f"\n✨ Tune bola: {text}")