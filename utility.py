from twilio.rest import Client
import os

from dotenv import load_dotenv
load_dotenv()

# Twilio Credentials
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
MY_WHATSAPP_NUMBER = os.getenv("MY_WHATSAPP_NUMBER")
twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

@staticmethod
def clean_nosql_response(raw_response: str) -> str:
    # Strip leading/trailing whitespace and remove code fences
    cleaned = raw_response.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json") :].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned

@staticmethod
def sendWhatsAppMessage(mymessage: str):
    twilio_client.messages.create(
        body=mymessage,
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        to=f"whatsapp:{MY_WHATSAPP_NUMBER}"
    )
    print("WhatsApp alert sent!")

#sendWhatsAppMessage("This is test!")