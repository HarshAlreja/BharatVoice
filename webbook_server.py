from flask import Flask, request
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print(" Webhook Verified Successfully!")
        return challenge, 200

    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()

    print("\n Incoming Payload:")
    print(data)

    return "EVENT_RECEIVED", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("\n========== WEBHOOK RECEIVED ==========")
    print(data)

    return "EVENT_RECEIVED", 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)