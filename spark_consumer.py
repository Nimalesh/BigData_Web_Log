# Final Spark Streaming Script with Timestamp Generation

from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_extract, udf, length, when, col
from pyspark.sql.types import IntegerType, TimestampType  # <--- MODIFICATION: Added TimestampType
import joblib
import redis
import json
import pandas as pd
from datetime import datetime  # <--- MODIFICATION: Added datetime
import pytz  # <--- MODIFICATION: Added pytz

# ==============================================================================
# 1. DEFINE THE TIMESTAMP PARSING FUNCTION
# This UDF will convert your string date/time into a proper timestamp object.
# ==============================================================================
def parse_to_utc(date_str, time_str):
    """Parses DDMMYY and HHMMSS strings and returns a UTC-aware datetime object."""
    try:
        # Define the timezone your logs were originally generated in.
        # This is crucial for correct conversion to UTC.
        local_tz = pytz.timezone('Asia/Kolkata')
        format_code = "%d%m%y%H%M%S"
        
        # Combine the date and time strings for parsing
        full_timestamp_str = date_str + time_str
        dt_local = datetime.strptime(full_timestamp_str, format_code)
        
        # Make the datetime object timezone-aware
        dt_aware = local_tz.localize(dt_local)
        
        # Convert to UTC for standardized storage
        return dt_aware.astimezone(pytz.utc)
    except (ValueError, TypeError, AttributeError):
        # If parsing fails for any reason, return null
        return None

# Register the Python function as a Spark User Defined Function (UDF)
parse_udf = udf(parse_to_utc, TimestampType())


# ==============================================================================
# 2. DEFINE THE ANOMALY PREDICTION FUNCTION
# (Your original code for the machine learning model)
# ==============================================================================
# Load the model ONCE at the driver
anomaly_model = joblib.load("anomaly_model.pkl")

def predict_anomaly(pid, msg_len, level_num):
    """Predicts if a log is an anomaly using the pre-trained model."""
    try:
        # Convert inputs to float, handle potential errors
        pid_f = float(pid)
        msg_len_f = float(msg_len)
        level_num_f = float(level_num)
        
        features = pd.DataFrame([[pid_f, msg_len_f, level_num_f]], columns=["pid", "msg_len", "level_num"])
        pred = anomaly_model.predict(features)
        return int(pred[0])
    except (ValueError, TypeError):
        # If conversion fails, classify as not an anomaly (or handle as needed)
        return 0

anomaly_udf = udf(predict_anomaly, IntegerType())


# ==============================================================================
# 3. SETUP THE SPARK SESSION AND KAFKA SOURCE
# ==============================================================================
spark = SparkSession.builder \
    .appName("KafkaLogConsumer") \
    .config("spark.mongodb.connection.uri", "mongodb://localhost:27017") \
    .config("spark.mongodb.database", "logdb") \
    .config("spark.mongodb.collection", "parsed_logs") \
    .getOrCreate()

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:19092") \
    .option("subscribe", "log_topic") \
    .option("startingOffsets", "latest") \
    .load()

log_df = df.selectExpr("CAST(value AS STRING) as log_line")


# ==============================================================================
# 4. PARSE AND ENRICH THE LOG DATA
# ==============================================================================
# Extract fields from the raw log line using regular expressions
structured_df = log_df.select(
    regexp_extract("log_line", r"^(\d{6})", 1).alias("date"),
    regexp_extract("log_line", r"^\d{6}\s+(\d{6})", 1).alias("time"),
    regexp_extract("log_line", r"^\d{6}\s+\d{6}\s+(\d+)", 1).alias("pid"),
    regexp_extract("log_line", r"\s(INFO|WARN|ERROR)", 1).alias("level"),
    regexp_extract("log_line", r"^\d{6}\s+\d{6}\s+\d+\s+\w+\s+([\w\.\$\*]+):", 1).alias("component"),
    regexp_extract("log_line", r"^[^:]*:\s+(.*)", 1).alias("message")
)

# Add derived columns for analysis and machine learning
structured_df = structured_df.withColumn("msg_len", length(col("message")))

structured_df = structured_df.withColumn(
    "level_num",
    when(col("level") == "INFO", 0)
     .when(col("level") == "WARN", 1)
     .when(col("level") == "ERROR", 2)
     .otherwise(None)
)

# --- MODIFICATION: ADD THE NEW TIMESTAMP COLUMN ---
# This is the most important change. It creates the field Grafana needs.
structured_df = structured_df.withColumn(
    "timestamp",
    parse_udf(col("date"), col("time"))
)
# ---

# Predict anomalies using the machine learning model
structured_df = structured_df.withColumn(
    "is_anomaly",
    anomaly_udf(col("pid"), col("msg_len"), col("level_num"))
)


# ==============================================================================
# 5. DEFINE THE OUTPUT SINKS (MONGO AND REDIS)
# ==============================================================================

# Function to write micro-batches to Redis for real-time UI
def write_to_redis(batch_df, batch_id):
    """Converts a Spark DataFrame batch to Pandas and pushes to Redis."""
    logs = batch_df.toPandas().to_dict(orient="records")
    # It's better to create one connection per partition, but this is fine for now
    r = redis.Redis(host="localhost", port=6379, db=0)
    for log in logs:
        # Convert the datetime object to a string for JSON serialization
        if 'timestamp' in log and isinstance(log['timestamp'], datetime):
            log['timestamp'] = log['timestamp'].isoformat()
        
        r.lpush("realtime_logs", json.dumps(log))
    
    # Keep the Redis list from growing indefinitely
    r.ltrim("realtime_logs", 0, 999)

# Start the two output streams
# 1. Write the full enriched data to MongoDB for historical analysis
mongo_query = structured_df.writeStream \
    .format("mongodb") \
    .option("checkpointLocation", "/tmp/mongo_checkpoint") \
    .outputMode("append") \
    .trigger(processingTime="10 seconds") \
    .start()

# 2. Write the same data to Redis for a live-tail view
redis_query = structured_df.writeStream \
    .foreachBatch(write_to_redis) \
    .outputMode("append") \
    .trigger(processingTime="10 seconds") \
    .start()


# ==============================================================================
# 6. AWAIT TERMINATION
# ==============================================================================
# This keeps the Spark application running to process new messages from Kafka
mongo_query.awaitTermination()
redis_query.awaitTermination()