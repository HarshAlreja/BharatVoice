from flask import Flask, request
from dotenv import load_dotenv
import os
from bharatvoice import (
    load_vector_store,
    get_rag_answer
)
from whatsapp_api import (
    send_whatsapp_message,
    send_audio_message
)
from audio_handler import (
    download_audio_from_meta,
    speech_to_text,
    text_to_speech,
    cleanup_temp_audio
)

load_dotenv()
app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

print("=" * 60)
print(" BharatVoice Webhook Server Starting...")
print("=" * 60)

print("\n Loading Vector Store...")
vector_store = load_vector_store()
print(" Vector Store Ready!")

print("\n Server Configuration:")
print(f"   Phone ID: {WHATSAPP_PHONE_NUMBER_ID}")
print(f"   Webhook Endpoint: /webhook")
print("=" * 60)


# ────────────────────────────────────────────────────────
# WEBHOOK VERIFICATION (GET)
# ────────────────────────────────────────────────────────

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """
    Verify webhook with Meta
    Called when setting up webhook URL in Meta dashboard
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("\n Webhook Verified Successfully!")
        return challenge, 200

    print("\n Verification failed - Invalid token")
    return "Verification failed", 403


# ────────────────────────────────────────────────────────
# MESSAGE HANDLER (POST)
# ────────────────────────────────────────────────────────

@app.route("/webhook", methods=["POST"])
def receive_message():
    """
    Main webhook endpoint
    Receives messages from WhatsApp and processes them
    """
    data = request.get_json()

    print("\n" + "=" * 60)
    print(" INCOMING MESSAGE")
    print("=" * 60)
    print(data)

    try:
        # Extract message data
        value = data["entry"][0]["changes"][0]["value"]
        
        # Check if message exists
        if "messages" not in value:
            print(" No message in payload (status update)")
            return "EVENT_RECEIVED", 200
        
        message = value["messages"][0]
        sender_number = message["from"]
        message_type = message["type"]
        
        print(f"\n From: {sender_number}")
        print(f" Type: {message_type}")
        
        # ────────────────────────────────────────────────────────
        # TEXT MESSAGE HANDLING
        # ────────────────────────────────────────────────────────
        if message_type == "text":
            print("\n TEXT MESSAGE")
            
            user_message = message["text"]["body"]
            print(f"   Content: {user_message}")
            
            # Get answer from RAG
            print("\n Processing through RAG...")
            answer = get_rag_answer(user_message, vector_store)
            print(f"   Answer: {answer}")
            
            # Send text reply
            print("\n📤 Sending text reply...")
            send_whatsapp_message(sender_number, answer)
            print(" Text reply sent!")
            
            return "EVENT_RECEIVED", 200
        
        # ────────────────────────────────────────────────────────
        # AUDIO MESSAGE HANDLING
        # ────────────────────────────────────────────────────────
        elif message_type == "audio":
            print("\n AUDIO MESSAGE")
            
            audio_id = message["audio"]["id"]
            print(f"   Audio ID: {audio_id}")
            
            # Step 1: Download audio from Meta
            print("\n⬇ Step 1: Downloading audio from Meta...")
            audio_path = download_audio_from_meta(audio_id)
            
            if not audio_path:
                print(" Audio download failed!")
                send_whatsapp_message(
                    sender_number,
                    " Audio download fail gaya. Dobara try karo please."
                )
                return "EVENT_RECEIVED", 200
            
            # Step 2: Convert audio to text (STT)
            print("\n Step 2: Converting audio to text (Sarvam STT)...")
            transcript = speech_to_text(audio_path)
            
            if not transcript:
                print(" STT failed!")
                send_whatsapp_message(
                    sender_number,
                    " Audio samjh nahi aaya. Dobara bolo please."
                )
                return "EVENT_RECEIVED", 200
            
            # Step 3: Process through RAG
            print("\n Step 3: Processing through RAG...")
            answer = get_rag_answer(transcript, vector_store)
            print(f"   Answer: {answer}")
            
            # Step 4: Send text reply (free tier)
            print("\n Step 4: Sending text reply...")
            send_whatsapp_message(sender_number, answer)
            print(" Text reply sent!")
            
            # Step 5: Generate audio reply (for testing, not sent yet)
            print("\n Step 5 (Optional): Generating audio response...")
            audio_reply = text_to_speech(answer)
            if audio_reply:
                print(f" Audio generated: {audio_reply}")
                print("   (Will send via API once paid tier is activated)")
            
            return "EVENT_RECEIVED", 200
        
        # ────────────────────────────────────────────────────────
        # OTHER MESSAGE TYPES (ignore)
        # ────────────────────────────────────────────────────────
        else:
            print(f"\n Ignoring message type: {message_type}")
            print("   (Image, document, sticker, etc.)")
            return "EVENT_RECEIVED", 200
        
    except KeyError as e:
        print(f"\n Key Error: {str(e)}")
        print("   Malformed message payload")
        return "EVENT_RECEIVED", 200
    
    except Exception as e:
        print(f"\n Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return "EVENT_RECEIVED", 200
    
    finally:
        # Cleanup old temp files
        cleanup_temp_audio(keep_last_n=20)


# ────────────────────────────────────────────────────────
# HEALTH CHECK
# ────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint
    Use this to verify server is running
    """
    return {
        "status": "ok",
        "message": "BharatVoice Webhook Server is running!"
    }, 200


# ────────────────────────────────────────────────────────
# ERROR HANDLING
# ────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(error):
    return {"error": "Endpoint not found"}, 404

@app.errorhandler(500)
def internal_error(error):
    print(f"\n Server Error: {str(error)}")
    return {"error": "Internal server error"}, 500


# ────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n Starting Flask server...")
    print("   Host: 0.0.0.0")
    print("   Port: 5000")
    print("   Debug: True")
    print("\n Webhook URL: http://your-server:5000/webhook")
    print("   Health: http://your-server:5000/health")
    print("\n" + "=" * 60)
    
    app.run(host="0.0.0.0", port=5000, debug=True)