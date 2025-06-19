from kafka import KafkaProducer
import os

# Configuration
KAFKA_BROKER = 'localhost:19092'

TOPIC_NAME = 'log_topic'
LOG_FILE_PATH = 'HDFS.log'

if not os.path.exists(LOG_FILE_PATH):
    raise FileNotFoundError(f"Log file not found at {LOG_FILE_PATH}")

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: v.encode('utf-8')
)

print(f"Sending logs from {LOG_FILE_PATH} to Kafka topic '{TOPIC_NAME}'...")

# Send each line as a separate Kafka message
with open(LOG_FILE_PATH, 'r') as file:
    for line in file:
        cleaned_line = line.strip()
        if cleaned_line:  # Avoid sending empty lines
            producer.send(TOPIC_NAME, cleaned_line)

producer.flush()
producer.close()

print("Log file successfully sent to Kafka.")
