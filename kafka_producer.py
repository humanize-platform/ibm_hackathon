from confluent_kafka import Producer
import time
import json

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# IBM Cloud Event Streams Credentials
KAFKA_BROKER = (
    os.getenv("KAFKA_BOOTSTRAP_SERVER")
)
KAFKA_API_KEY = os.getenv("KAFKA_SSL_PASSWORD")
TOPIC_NAME = "humanize"

# Kafka Producer Configuration for IBM Cloud Event Streams
producer_config = {
    "bootstrap.servers": KAFKA_BROKER,
    "security.protocol": "SASL_SSL",
    "sasl.mechanism": "PLAIN",
    "sasl.username": "token",
    "sasl.password": KAFKA_API_KEY,
}

producer = Producer(producer_config)

def sendToKafka(data):
    producer.produce(TOPIC_NAME, key="sensor1", value=json.dumps(data))
    producer.flush()
    print(f"Sent to Kafka: {data}")
