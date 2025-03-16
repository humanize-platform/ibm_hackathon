from twilio.rest import Client
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Twilio Credentials
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
MY_WHATSAPP_NUMBER = os.getenv("MY_WHATSAPP_NUMBER")
twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)


@staticmethod
def sendWhatsAppMessage(mymessage: str):
    message = twilio_client.messages.create(
    body=mymessage,
    from_="whatsapp:+14155238886",
    to="whatsapp:+919903288470",
    )