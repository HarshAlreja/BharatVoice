"""
WhatsApp Business API Module
Handles sending messages via Meta WhatsApp Business API
Supports text messages and audio files (when paid tier is active)
"""

import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")

print(" WhatsApp API Loaded")
print(f"   Phone ID: {WHATSAPP_PHONE_NUMBER_ID}")


# ────────────────────────────────────────────────────────
# SEND TEXT MESSAGE
# ────────────────────────────────────────────────────────

def send_whatsapp_message(to_number, message):
    """
    Send text message via WhatsApp Business API
    
    Args:
        to_number: Recipient's WhatsApp number (with country code, e.g., +919876543210)
        message: Text content to send
        
    Returns:
        Response object from API
    """
    try:
        print(f"\n Sending WhatsApp message...")
        print(f"   To: {to_number}")
        print(f"   Type: Text")
        print(f"   Content: {message[:50]}..." if len(message) > 50 else f"   Content: {message}")
        
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\n📬 WhatsApp Response:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get("messages", [{}])[0].get("id", "unknown")
            print(f"   Message ID: {message_id}")
            print(" Message sent successfully!")
        else:
            print(f"   Error: {response.text}")
            print(" Message sending failed!")
        
        return response
    
    except Exception as e:
        print(f" Exception: {str(e)}")
        return None


# ────────────────────────────────────────────────────────
# SEND AUDIO MESSAGE (PAID TIER ONLY)
# ────────────────────────────────────────────────────────

def send_audio_message(to_number, audio_file_path, caption=None):
    """
    Send audio file via WhatsApp Business API
    
  REQUIRES PAID TIER (not available in free tier)
    
    Args:
        to_number: Recipient's WhatsApp number (with country code)
        audio_file_path: Local path to audio file (.ogg, .wav, .mp3)
        caption: Optional caption (not supported for audio in all versions)
        
    Returns:
        Response object from API
    """
    try:
        print(f"\n Sending WhatsApp audio message...")
        print(f"   To: {to_number}")
        print(f"   Type: Audio")
        print(f"   File: {audio_file_path}")
        
        # Check if file exists
        if not os.path.exists(audio_file_path):
            print(f" Audio file not found: {audio_file_path}")
            return None
        
        # Get file size
        file_size = os.path.getsize(audio_file_path)
        print(f"   Size: {file_size} bytes")
        
        # Read and encode audio
        with open(audio_file_path, "rb") as f:
            audio_data = f.read()
        
        # Prepare API request
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Detect file type
        file_ext = audio_file_path.split(".")[-1].lower()
        mime_types = {
            "ogg": "audio/ogg",
            "wav": "audio/wav",
            "mp3": "audio/mpeg",
            "m4a": "audio/mp4"
        }
        mime_type = mime_types.get(file_ext, "audio/ogg")
        
        # For now, we'll use a simple approach (this works with some API versions)
        # In future, you might need to upload to Meta server first, then send URL
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "audio",
            "audio": {
                "data": base64.b64encode(audio_data).decode(),
            }
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"\n WhatsApp Response:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get("messages", [{}])[0].get("id", "unknown")
            print(f"   Message ID: {message_id}")
            print(" Audio sent successfully!")
        else:
            print(f"   Error: {response.text}")
            
            # Common errors
            if "Cannot find the requested media" in response.text:
                print("   → Audio format not supported")
            elif "FREE_PLAN_LIMIT" in response.text:
                print("   → Free tier limitation (upgrade to paid tier)")
            elif "Invalid recipient" in response.text:
                print("   → Invalid phone number")
            
            print(" Audio sending failed!")
        
        return response
    
    except Exception as e:
        print(f" Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


# ────────────────────────────────────────────────────────
# SEND MEDIA MESSAGE (Generic - for future use)
# ────────────────────────────────────────────────────────

def send_media_message(to_number, media_type, file_path, caption=None):
    """
    Send any media file via WhatsApp Business API
    Generic method for images, documents, audio, video
    
    Args:
        to_number: Recipient's WhatsApp number
        media_type: Type of media ('image', 'document', 'audio', 'video')
        file_path: Local path to media file
        caption: Optional caption
        
    Returns:
        Response object from API
    """
    try:
        print(f"\n Sending {media_type} via WhatsApp...")
        print(f"   To: {to_number}")
        print(f"   Type: {media_type}")
        
        if not os.path.exists(file_path):
            print(f" File not found: {file_path}")
            return None
        
        # Read file
        with open(file_path, "rb") as f:
            file_data = f.read()
        
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Prepare MIME type
        mime_types = {
            "image": "image/jpeg",
            "audio": "audio/ogg",
            "video": "video/mp4",
            "document": "application/pdf"
        }
        mime_type = mime_types.get(media_type, "application/octet-stream")
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": media_type,
            media_type: {
                "data": base64.b64encode(file_data).decode(),
            }
        }
        
        if caption and media_type != "audio":
            payload[media_type]["caption"] = caption
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f" {media_type.capitalize()} sent successfully!")
        else:
            print(f" Error: {response.text}")
        
        return response
    
    except Exception as e:
        print(f" Exception: {str(e)}")
        return None


# ────────────────────────────────────────────────────────
# SEND TEMPLATE MESSAGE (for future use)
# ────────────────────────────────────────────────────────

def send_template_message(to_number, template_name, template_language="hi"):
    """
    Send pre-approved template message
    Useful for welcome messages, notifications, etc.
    
    Args:
        to_number: Recipient's WhatsApp number
        template_name: Name of the approved template
        template_language: Language code of template
        
    Returns:
        Response object from API
    """
    try:
        print(f"\n Sending template message...")
        print(f"   To: {to_number}")
        print(f"   Template: {template_name}")
        
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": template_language
                }
            }
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Template message sent!")
        else:
            print(f" Error: {response.text}")
        
        return response
    
    except Exception as e:
        print(f" Exception: {str(e)}")
        return None


# ────────────────────────────────────────────────────────
# TESTING
# ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("WhatsApp API Module - Testing")
    print("=" * 60)
    
    # To test, uncomment and add your number:
    # test_number = "+919876543210"
    # response = send_whatsapp_message(test_number, "🧪 Test message from BharatVoice!")
    
    print("\n API module ready for use")
    print("   Use in webhook_server.py to send messages")