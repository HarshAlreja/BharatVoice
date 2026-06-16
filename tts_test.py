import requests
import os
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

url = "https://api.sarvam.ai/text-to-speech"

payload = {
    "target_language_code": "hi-IN",
    "text": "Namaste! Main BharatVoice hoon. Om Sai Medical Store mein aapka swagat hai.",
    "speaker": "anushka",
    "pace": 1.0,
    "loudness": 1.5,
    "model": "bulbul:v2"
}

headers = {
    "api-subscription-key": SARVAM_API_KEY,
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    data = response.json()
    # Audio base64 mein aata hai — decode karke save karo
    import base64
    audio_data = base64.b64decode(data["audios"][0])
    with open("test_output.wav", "wb") as f:
        f.write(audio_data)
    print("Audio saved! test_output.wav open karo.")
else:
    print(f"Error: {response.status_code}")
    print(response.text)