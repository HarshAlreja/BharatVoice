"""
Audio Handler Module
Handles speech-to-text (STT) and text-to-speech (TTS) for BharatVoice
Uses Sarvam AI API
"""

import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")

# ────────────────────────────────────────────────────────
# DOWNLOAD AUDIO FROM META
# ────────────────────────────────────────────────────────

def download_audio_from_meta(media_id):
    """
    Download audio file from WhatsApp via Meta API
    
    Args:
        media_id: Audio ID from WhatsApp webhook
        
    Returns:
        Filepath of downloaded audio, or None if failed
    """
    try:
        print(f"\n📥 Downloading audio from Meta... (ID: {media_id})")
        
        # Step 1: Get media URL
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Meta API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
        
        media_url = response.json().get("url")
        
        if not media_url:
            print("❌ No URL in Meta response")
            return None
        
        print(f"✅ Got media URL from Meta")
        
        # Step 2: Download actual audio file
        audio_response = requests.get(
            media_url,
            headers=headers,
            timeout=30
        )
        
        if audio_response.status_code != 200:
            print(f"❌ Audio download failed: {audio_response.status_code}")
            return None
        
        # Step 3: Save to temp folder
        os.makedirs("temp_audio", exist_ok=True)
        audio_path = f"temp_audio/{media_id}.ogg"
        
        with open(audio_path, "wb") as f:
            f.write(audio_response.content)
        
        file_size = os.path.getsize(audio_path)
        print(f"✅ Audio saved: {audio_path} ({file_size} bytes)")
        
        return audio_path
        
    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        return None


# ────────────────────────────────────────────────────────
# SPEECH TO TEXT (STT)
# ────────────────────────────────────────────────────────

def speech_to_text(audio_file, language_code="hi-IN"):
    """
    Convert audio file to text using Sarvam AI
    
    Args:
        audio_file: Path to audio file (.ogg, .wav, .mp3)
        language_code: Language code (default: hi-IN for Hindi)
        
    Returns:
        Transcript text, or None if failed
    """
    try:
        if not os.path.exists(audio_file):
            print(f"❌ Audio file not found: {audio_file}")
            return None
        
        print(f"\n🎙️ Converting audio to text...")
        print(f"   File: {audio_file}")
        print(f"   Language: {language_code}")
        
        with open(audio_file, "rb") as f:
            audio_data = f.read()
        
        # Detect file type from extension
        file_ext = audio_file.split(".")[-1].lower()
        mime_types = {
            "ogg": "audio/ogg",
            "wav": "audio/wav",
            "mp3": "audio/mpeg",
            "m4a": "audio/mp4"
        }
        mime_type = mime_types.get(file_ext, "audio/ogg")
        
        payload = {
            "file": ("audio", audio_data, mime_type),
            "language_code": (None, language_code),
            "model": (None, "saaras:v3")
        }
        
        response = requests.post(
            "https://api.sarvam.ai/speech-to-text",
            headers={"api-subscription-key": SARVAM_API_KEY},
            files=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            transcript = result.get("transcript", "").strip()
            
            if transcript:
                print(f"✅ Transcript: {transcript}")
                return transcript
            else:
                print("❌ No transcript in response")
                return None
        else:
            print(f"❌ STT Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ STT Exception: {str(e)}")
        return None


# ────────────────────────────────────────────────────────
# TEXT TO SPEECH (TTS)
# ────────────────────────────────────────────────────────

def text_to_speech(text, language_code="hi-IN", speaker="anushka"):
    """
    Convert text to speech audio using Sarvam AI
    
    Args:
        text: Text to convert to speech
        language_code: Language code (default: hi-IN for Hindi)
        speaker: Voice speaker (default: anushka)
        
    Returns:
        Filepath of generated audio, or None if failed
    """
    try:
        if not text or len(text.strip()) == 0:
            print("❌ Empty text provided for TTS")
            return None
        
        print(f"\n🔊 Converting text to speech...")
        print(f"   Text: {text[:50]}...")
        print(f"   Language: {language_code}")
        print(f"   Speaker: {speaker}")
        
        response = requests.post(
            "https://api.sarvam.ai/text-to-speech",
            headers={
                "api-subscription-key": SARVAM_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "target_language_code": language_code,
                "text": text,
                "speaker": speaker,
                "pace": 1.0,
                "loudness": 1.5,
                "model": "bulbul:v2"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if "audios" not in result or len(result["audios"]) == 0:
                print("❌ No audio in TTS response")
                return None
            
            audio_base64 = result["audios"][0]
            audio_data = base64.b64decode(audio_base64)
            
            # Save to temp folder
            os.makedirs("temp_audio", exist_ok=True)
            output_file = f"temp_audio/tts_{os.urandom(4).hex()}.ogg"
            
            with open(output_file, "wb") as f:
                f.write(audio_data)
            
            file_size = os.path.getsize(output_file)
            print(f"✅ Audio generated: {output_file} ({file_size} bytes)")
            
            return output_file
        else:
            print(f"❌ TTS Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ TTS Exception: {str(e)}")
        return None


# ────────────────────────────────────────────────────────
# CLEANUP (Remove old temp files)
# ────────────────────────────────────────────────────────

def cleanup_temp_audio(keep_last_n=10):
    """
    Remove old audio files from temp folder
    Keeps last N files to avoid disk bloat
    
    Args:
        keep_last_n: Number of latest files to keep
    """
    try:
        temp_dir = "temp_audio"
        if not os.path.exists(temp_dir):
            return
        
        files = [
            os.path.join(temp_dir, f)
            for f in os.listdir(temp_dir)
            if os.path.isfile(os.path.join(temp_dir, f))
        ]
        
        if len(files) > keep_last_n:
            # Sort by modification time, keep newest
            files.sort(key=os.path.getmtime, reverse=True)
            
            for old_file in files[keep_last_n:]:
                try:
                    os.remove(old_file)
                    print(f"🗑️ Cleaned: {old_file}")
                except:
                    pass
    except Exception as e:
        print(f"⚠️ Cleanup error: {str(e)}")


# ────────────────────────────────────────────────────────
# TESTING (Run directly)
# ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Audio Handler Module")
    print("=" * 60)
    
    # Test TTS (Text to Speech)
    print("\n📝 Testing TTS (Text to Speech)...")
    test_text = "Namaste! Aapka swagat hai BharatVoice mein!"
    audio_file = text_to_speech(test_text)
    if audio_file:
        print(f"✅ TTS Test Passed: {audio_file}")
    else:
        print("❌ TTS Test Failed")
    
    print("\n" + "=" * 60)
    print("Note: STT and Meta download require actual audio files")