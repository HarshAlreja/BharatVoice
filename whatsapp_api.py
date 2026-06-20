import os
import requests
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")

def send_whatsapp_message(to_number,message):
    url=f"https://graph.facebook.com/v23.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers={
        "Authorization":f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type":"application/json"

    }
    payload={
        "messaging_product":"whatsapp",
        "to":to_number,
        "type":"text",
        "text":{
            "body": message
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print("\n Whatsapp Response!...")
    print(response.status_code)
    print(response.text)

    return response