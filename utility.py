from twilio.rest import Client
import os
import json
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

# Twilio Credentials
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
MY_WHATSAPP_NUMBER = os.getenv("MY_WHATSAPP_NUMBER")
twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@staticmethod
def sendWhatsAppMessage(mymessage: str):
    message = twilio_client.messages.create(
        body=mymessage,
        from_="whatsapp:+14155238886",
        to="whatsapp:+919903288470",
    )


@staticmethod
def getQualityData(url: str) -> str:
    response = tavily_client.search(query=url)
    all_content = ""

    if "results" in response:
        for result in response["results"]:
            if "content" in result:
                all_content += result["content"] + " "

    return all_content.strip()
