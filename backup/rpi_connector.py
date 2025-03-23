# Below code is executed within Raspberry Pi to read water flow sensor data and send it to Kafka Producer.
import lgpio # type: ignore
import time
from kafka_producer import producer
import json

# Initialize variables
pulse_count = 0
last_time = time.time()

FLOW_PIN = 13
CALIBRATION_FACTOR = 7.5  # Pulses per liter per minute (from YF-S201 datasheet)
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_input(h, FLOW_PIN)

while True:
    current_time = time.time()
    elapsed = current_time - last_time
    pulse_ind = lgpio.gpio_read(h, FLOW_PIN)
   
    if pulse_ind == 0:
       pulse_count = pulse_count + 1

    if elapsed >= 2:  # Calculate every second
        flow_rate = (pulse_count / CALIBRATION_FACTOR)  # L/min
        #print(f"Flow Rate: {flow_rate:.2f} L/min | Total Pulses: {pulse_count}")
        # send to kafka producer
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "flow_rate": flow_rate,
            "pulses": pulse_count,
            "location": "Kitchen",
        }  
        # call Kafka Producer
        producer.sendToKafka(json.dumps(data)) 
                   
        # Reset counters
        pulse_count = 0
        last_time = current_time
       
    time.sleep(0.1)