import json
import requests
from confluent_kafka import Consumer
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# IBM Cloudant Configuration (Use IAM API Key)
CLOUDANT_URL = os.getenv("CLOUDANT_URL")
IAM_API_KEY = os.getenv("CLOUDANT_APIKEY")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Obtain IAM Authentication Token
IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
auth_response = requests.post(
    IAM_TOKEN_URL,
    data={
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": IAM_API_KEY,
    },
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)

auth_response.raise_for_status()  # Raise error if authentication fails
iam_token = auth_response.json()["access_token"]
headers = {"Authorization": f"Bearer {iam_token}", "Content-Type": "application/json"}

print(headers)

# Kafka Consumer Configuration
consumer_config = {
    "bootstrap.servers": "broker-1-kr2k26jl1s2pl3nk.kafka.svc11.us-south.eventstreams.cloud.ibm.com:9093",
    "security.protocol": "SASL_SSL",
    "sasl.mechanism": "PLAIN",
    "sasl.username": "token",
    "sasl.password": "PuDyV6xS7M-PEGA__tjK7puXogq6f0zqVXKsUiQIF0dB",
    "group.id": "water-consumer-group",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,  # Manually commit after insertion
}

consumer = Consumer(consumer_config)
consumer.subscribe(["humanize"])

print("Waiting for messages...")
try:
    while True:
        msg = consumer.poll(1.0)  # Wait for message
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        # ✅ Parse Kafka JSON Data
        data = json.loads(msg.value().decode("utf-8"))

        # ✅ Insert Data into Cloudant as a JSON Document
        response = requests.post(
            f"{CLOUDANT_URL}/{DATABASE_NAME}", json=data, headers=headers
        )
        if response.status_code == 201:
            print(f"Inserted into Cloudant: {data}")
            consumer.commit()  # ✅ Commit offset (Remove from Kafka Queue)
        else:
            print(f"Failed to insert: {response.text}")

except KeyboardInterrupt:
    print("Stopping consumer...")
finally:
    consumer.close()
