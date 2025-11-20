import json
import sys
import signal
import logging
from time import sleep
import os
from dotenv import load_dotenv

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable, KafkaError

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

# Load environment variables
load_dotenv()

# ------------------ Logging Setup ------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("consumer.log")
    ]
)

logger = logging.getLogger("KafkaMongoConsumer")


# ------------------ Configuration ------------------
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "shipment_data")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@mongodb:27017/")
MONGO_DB = os.getenv("MONGO_DB", "scmlitedb")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "shipment_data")


class KafkaMongoConsumer:
    def __init__(self):
        self.running = True
        self.consumer = None
        self.collection = None

        # Handle Ctrl+C and Docker stop signals
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        self.init_kafka()
        self.init_mongo()

    # ------------------ Kafka Setup ------------------
    def init_kafka(self):
        """Create Kafka consumer with retry logic."""
        retries = 5
        for attempt in range(1, retries + 1):
            try:
                self.consumer = KafkaConsumer(
                    KAFKA_TOPIC,
                    bootstrap_servers=[KAFKA_BOOTSTRAP],
                    value_deserializer=lambda x: self.safe_json(x),
                    auto_offset_reset="earliest",
                    enable_auto_commit=True,
                    group_id="consumer_group_1"
                )
                logger.info("Connected to Kafka")
                return
            except NoBrokersAvailable:
                logger.warning(f"Kafka not available. Retrying ({attempt}/{retries})...")
                sleep(5)
        logger.error("Could not connect to Kafka after retries")
        sys.exit(1)

    # ------------------ MongoDB Setup ------------------
    def init_mongo(self):
        """Connect to MongoDB with retry."""
        retries = 5
        for attempt in range(1, retries + 1):
            try:
                client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
                client.server_info()  # Forces connection
                self.collection = client[MONGO_DB][MONGO_COLLECTION]
                logger.info("Connected to MongoDB")
                return
            except ConnectionFailure:
                logger.warning(f"MongoDB not available. Retrying ({attempt}/{retries})...")
                sleep(5)
        logger.error("Could not connect to MongoDB after retries")
        sys.exit(1)

    # ------------------ Helper ------------------
    def safe_json(self, value):
        try:
            return json.loads(value.decode("utf-8"))
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON: {value}")
            return None

    # ------------------ Processing ------------------
    def process(self, data):
        if not data:
            logger.warning("Empty message received")
            return

        try:
            result = self.collection.insert_one(data)
            logger.info(f"Inserted document ID: {result.inserted_id}")
        except PyMongoError as e:
            logger.error(f"MongoDB Error: {e}")

    # ------------------ Run Consumer ------------------
    def run(self):
        logger.info("Consumer started. Listening for messages...")

        for msg in self.consumer:
            if not self.running:
                break
            self.process(msg.value)

    # ------------------ Graceful Shutdown ------------------
    def stop(self, signum, frame):
        logger.info("Stopping consumer...")
        self.running = False
        try:
            if self.consumer:
                self.consumer.close()
        except:
            pass
        sys.exit(0)


# ------------------------------------------------------------
def main():
    while True:
        try:
            consumer = KafkaMongoConsumer()
            consumer.run()
        except Exception as e:
            logger.error(f"Consumer crashed: {e}")
            logger.info("Restarting in 5 seconds...")
            sleep(5)


if __name__ == "__main__":
    main()
