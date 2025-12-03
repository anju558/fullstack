import os
from dotenv import load_dotenv
load_dotenv()

from kafka import KafkaConsumer
from pymongo import MongoClient
import json
import time
import sys

def get_env_var(name):
    value = os.getenv(name)
    if not value:
        print(f"[✗] Missing required environment variable: {name}")
        sys.exit(1)
    return value

KAFKA_TOPIC = get_env_var("KAFKA_TOPIC")
KAFKA_BROKER = get_env_var("KAFKA_BROKER")
MONGO_URI = get_env_var("MONGO_URI")
DB_NAME = get_env_var("DB_NAME")
COLLECTION_NAME = get_env_var("DEVICE_DATA_COLLECTION")

def connect_kafka():
    for attempt in range(10):
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BROKER,
                auto_offset_reset='earliest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='route-group'
            )
            print("[✓] Connected to Kafka")
            return consumer
        except Exception as e:
            print(f"[!] Kafka connection failed (attempt {attempt + 1}/10): {e}")
            time.sleep(5)
    print("[✗] Failed to connect to Kafka after 10 attempts")
    sys.exit(1)

def connect_mongodb():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]  
        collection = db[COLLECTION_NAME]
        print("[✓] Connected to MongoDB")
        return collection
    except Exception as e:
        print(f"[✗] MongoDB connection error: {e}")
        sys.exit(1)

def main():
    consumer = connect_kafka()
    collection = connect_mongodb()
    collection.delete_many({})
    print("[*] Kafka consumer started. Waiting for messages...")
    
    try:
        for message in consumer:
            try:
                data = message.value
                collection.insert_one(data)
                print(f"[→] Inserted document with ID: {data.get('_id', 'N/A')}")
            except Exception as e:
                print(f"[!] Error processing message: {e}")
    except KeyboardInterrupt:
        print("[*] Shutting down consumer...")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()