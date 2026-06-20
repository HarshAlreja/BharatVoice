from flask import Flask, request
from dotenv import load_dotenv
import os
from bharatvoice import (
    load_vector_store,
    get_rag_answer
)
from whatsapp_api import send_whatsapp_message

load_dotenv()
app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
print("Loading Vector Store!....")
vector_store = load_vector_store()
print("Vector Store Ready!..")



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

    try:
        value = data["entry"][0]["changes"][0]["value"]
        if "messages" not in value:
            return "EVENT_RECEIVED" , 200
        message = value["messages"][0]

        if message["type"]!="text":
            return "EVENT_RECEIVED" , 200
        user_message = message["text"]["body"]
        sender_number = message["from"]
        print(f"\n User : {user_message}")
        print(f"\n Generating Answers !...")

        answer=get_rag_answer(
            user_message,
            vector_store
        )  
        print(f"\n AI Answer {answer}")

        send_whatsapp_message(
            sender_number,
            answer
        ) 
    except Exception as e:
        print(str(e))


    return "EVENT_RECEIVED", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("\n========== WEBHOOK RECEIVED ==========")
    print(data)

    return "EVENT_RECEIVED", 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)