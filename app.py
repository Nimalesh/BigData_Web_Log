import os
import subprocess
import time

# Match the actual Kafka container name from `docker ps`
KAFKA_CONTAINER = "bigdata_web_log-kafka-1"
TOPIC_NAME = "log_topic"
LOG_FILE_PATH = "HDFS.log"  # or use a full path like logs/HDFS.log

def create_kafka_topic():
    print(f"Creating Kafka topic '{TOPIC_NAME}' if not exists----------------")
    result = subprocess.run([
        "docker", "exec", KAFKA_CONTAINER,
        "kafka-topics",
        "--create",
        "--if-not-exists",
        "--bootstrap-server", "localhost:19092",
        "--topic", TOPIC_NAME,
        "--partitions", "1",
        "--replication-factor", "1"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print("Failed to create topic:", result.stderr)
    else:
        print(" Kafka topic created or already exists.")

def run_kafka_producer():
    print("Running Kafka Producer+++++++++++++++++++")
    result = subprocess.run(["python", "kafka_producer.py"])
    if result.returncode != 0:
        print("Kafka Producer failed.")
        exit(1)

def run_spark_consumer():
    print("Starting Spark Consumer with increased memory@@@@@@@@@@@@@@@@@@@@")

    # Create a copy of the current environment to modify
    spark_env = os.environ.copy()

    # Set JAVA_HOME from Homebrew (if installed via brew)
    try:
        java_home_path = subprocess.check_output(['brew', '--prefix', 'openjdk@11']).strip().decode('utf-8')
        spark_env['JAVA_HOME'] = f"{java_home_path}/libexec/openjdk.jdk/Contents/Home"
        print(f"SUCCESS: Setting JAVA_HOME for Spark to: {spark_env['JAVA_HOME']}")
    except Exception as e:
        print(f"WARNING: Could not set JAVA_HOME using `brew`. Error: {e}")
        # Optional fallback
        # spark_env['JAVA_HOME'] = "/Library/Java/JavaVirtualMachines/openjdk-11.jdk/Contents/Home"

    # Add MongoDB Connector package to Spark
    spark_command = [
    "spark-submit",
    "--packages",  # The flag
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0",  # The value for the flag (NO SPACES inside the comma-separated list)
    "--driver-memory", "4g",
    "--executor-memory", "4g",
    "spark_consumer.py"  # The main application script
]

    # Run Spark job with extended environment
    result = subprocess.run(spark_command, env=spark_env)

    if result.returncode != 0:
        print("Spark consumer failed.")
    else:
        print("Spark consumer completed successfully.*****************")

    print("Starting Spark Consumer with increased memory@@@@@@@@@@@@@@@@@@@@")

    # --- START OF THE FIX ---
    # Create a copy of the current environment to modify
    spark_env = os.environ.copy()
    
    # Get the correct path to Java 11 from Homebrew and set it
    try:
        java_home_path = subprocess.check_output(['brew', '--prefix', 'openjdk@11']).strip().decode('utf-8')
        spark_env['JAVA_HOME'] = java_home_path
        print(f"SUCCESS: Setting JAVA_HOME for Spark to: {spark_env['JAVA_HOME']}")
    except Exception as e:
        print(f"WARNING: Could not set JAVA_HOME using `brew`. Error: {e}")
        # If brew command fails, you can add a hardcoded fallback for your machine
        # spark_env['JAVA_HOME'] = '/opt/homebrew/opt/openjdk@11'
    # --- END OF THE FIX ---

    spark_command = [
        "spark-submit",
       'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.mongodb spark:mongo-spark-connector_2.12:10.3.0', 
        "--driver-memory", "4g",
        "--executor-memory", "4g",
        "spark_consumer.py"
    ]
    
    # Run the spark-submit command with the modified environment
    # Note the `env=spark_env` argument
    result = subprocess.run(spark_command, env=spark_env)

    if result.returncode != 0:
        print("Spark consumer failed.")
    else:
        print("Spark consumer completed successfully.*****************")

def main():
    if not os.path.exists(LOG_FILE_PATH):
        print(f"Log file not found: {LOG_FILE_PATH}")
        return

    create_kafka_topic()
    run_kafka_producer()

    print("Waiting 2 seconds before starting Spark$$$$$$$$$$$$$$")
    time.sleep(2)

    run_spark_consumer()

if __name__ == "__main__":
    main()