# producer.py
import os
import json
import time
import random
from datetime import datetime, timezone
from kafka import KafkaProducer

# Load config (fallbacks for local dev)
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "sensor_data")

# Retry connection
producer = None
for i in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            request_timeout_ms=20000,
            max_block_ms=30000
        )
        print(f"[✓] Producer connected to Kafka at {KAFKA_BROKER}")
        break
    except Exception as e:
        print(f"[!] Kafka connection failed (attempt {i+1}/10): {e}")
        time.sleep(5)
else:
    raise RuntimeError("Failed to connect to Kafka after 10 attempts")

# Data generation
routes = ['New York, USA', 'Chennai, India', 'Bengaluru, India', 'London, UK']

print(f"[→] Starting to send sensor data to topic: '{KAFKA_TOPIC}'")
try:
    while True:
        route_from = random.choice(routes)
        route_to = random.choice(routes)
        if route_from == route_to:
            continue

        data = {
            "Device_ID": f"D{random.randint(1150, 1158)}",  # e.g., "D1151"
            "Battery_Level": round(random.uniform(2.0, 5.0), 2),
            "First_Sensor_temperature": round(random.uniform(10.0, 40.0), 1),
            "Route_From": route_from,
            "Route_To": route_to,
            "timestamp": datetime.now(timezone.utc)
        }

        producer.send(KAFKA_TOPIC, value=data)
        print(f"✅ Sent: {data['Device_ID']} | {data['Battery_Level']}V | {data['First_Sensor_temperature']}°C")
        time.sleep(10)  # Send every 10 sec

except KeyboardInterrupt:
    print("\n[!] Stopping producer...")
finally:
    if producer:
        producer.flush()
        producer.close()