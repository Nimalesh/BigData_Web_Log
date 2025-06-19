# app.py
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import pytz # Recommended for handling timezones correctly

app = Flask(__name__)

# --- Database Connection ---
# Make sure MongoDB is running
client = MongoClient("mongodb://localhost:27017")
db = client["logdb"]
col = db["parsed_logs"]

# --- Helper Function ---
# This function parses the date/time from your logs.
# It's a potential performance bottleneck. For production, it's better
# to have a pre-computed ISODate or Unix timestamp field in MongoDB.
def parse_ts_to_utc(date_str, time_str):
    try:
        # Assuming your local timezone is IST for parsing
        local_tz = pytz.timezone('Asia/Kolkata')
        dt_local = datetime.strptime(date_str + time_str, "%d%m%y%H%M%S")
        dt_aware = local_tz.localize(dt_local)
        # Convert to UTC for consistency
        return dt_aware.astimezone(pytz.utc)
    except (ValueError, TypeError):
        return None

# ==============================================================================
# GRAFANA DATASOURCE BOILERPLATE (Required by JSON Datasource Plugin)
# ==============================================================================

@app.route("/", methods=["GET"])
def health_check():
    """A simple health check endpoint that Grafana pings."""
    return "OK"

@app.route("/metrics", methods=["POST"])
def search():
    """
    /search is used by Grafana to find available metrics for time series queries.
    """
    return jsonify(["msg_len", "level_num", "is_anomaly"])

@app.route("/tag-keys", methods=["POST"])
def tag_keys():
    """
    /tag-keys returns the dimensions you can filter by (dashboard variables).
    """
    return jsonify([
        {"type": "string", "text": "level"},
        {"type": "string", "text": "component"}
    ])

@app.route("/tag-values", methods=["POST"])
def tag_values():
    """
    /tag-values returns the possible values for a given tag key.
    """
    req = request.get_json()
    key = req.get("key")
    if not key:
        return jsonify([])
    
    values = col.distinct(key)
    return jsonify([{"text": str(v)} for v in values if v is not None])

# ==============================================================================
# CORE QUERY ENDPOINTS FOR VISUALIZATIONS
# ==============================================================================

# In your app.py file

# In app.py - REPLACE your old /query function with this one

# In app.py - REPLACE your old /query function again

# In app.py - REPLACE your /query function with this one

@app.route("/query", methods=["POST"])
def query():
    req = request.get_json()
    from_dt = datetime.fromisoformat(req["range"]["from"].replace('Z', '+00:00'))
    to_dt = datetime.fromisoformat(req["range"]["to"].replace('Z', '+00:00'))

    # Build the efficient filter
    mongo_filter = {
        "timestamp": {
            "$gte": from_dt,
            "$lte": to_dt
        }
    }

    # Add ad-hoc filters if they exist
    if "adhocFilters" in req:
        for f in req["adhocFilters"]:
            if f.get("key") and f.get("value"):
                mongo_filter[f["key"]] = {"$in": f["value"] if isinstance(f["value"], list) else [f["value"]]}

    # --- THE MOST IMPORTANT DEBUGGING STEP ---
    print("="*50)
    print(f"Grafana requested time from: {from_dt}")
    print(f"Grafana requested time to:   {to_dt}")
    print(f"Executing MongoDB query with this filter:")
    print(mongo_filter)
    
    # Let's count the documents BEFORE we fetch them all
    doc_count = col.count_documents(mongo_filter)
    print(f"MongoDB found {doc_count} documents matching this filter.")
    print("="*50)
    # --- END DEBUGGING STEP ---

    results = []
    for target in req["targets"]:
        metric = target["target"]
        points = []
        
        # Only proceed if documents were found
        if doc_count > 0:
            for doc in col.find(mongo_filter):
                ts_ms = int(doc["timestamp"].timestamp() * 1000)
                metric_value = doc.get(metric)
                if isinstance(metric_value, (int, float)):
                    points.append([metric_value, ts_ms])

        results.append({"target": metric, "datapoints": points})
        
    return jsonify(results)
    req = request.get_json()
    
    # --- Time Range Filter ---
    range_from_str = req["range"]["from"]
    range_to_str = req["range"]["to"]
    from_dt = datetime.fromisoformat(range_from_str.replace('Z', '+00:00'))
    to_dt = datetime.fromisoformat(range_to_str.replace('Z', '+00:00'))

    # --- Build the MongoDB filter ---
    mongo_filter = {
        # This is the crucial part.
        # It tells MongoDB to only look at documents that have a 'timestamp'
        # field between the 'from' and 'to' dates.
        # NOTE: This assumes you have a 'timestamp' field of type Date in your DB.
        # If you don't, this query will not work and you'll need the slower method below.
        
        # PLEASE UNCOMMENT THE CORRECT BLOCK FOR YOUR DATABASE STRUCTURE

        # --- BLOCK 1: THE EFFICIENT METHOD (If you add a 'timestamp' field) ---
        "timestamp": {
            "$gte": from_dt,
            "$lte": to_dt
        }
        # --- END BLOCK 1 ---
    }

    # --- Ad-hoc Filter (for dashboard variables) ---
    if "adhocFilters" in req:
        for f in req["adhocFilters"]:
            mongo_filter[f["key"]] = {"$in": f["value"] if isinstance(f["value"], list) else [f["value"]]}

    # --- BLOCK 2: THE SLOW METHOD (If you MUST parse strings on the fly) ---
    # If you cannot add a 'timestamp' field to your database, you must use this slow method.
    # Delete or comment out Block 1 above and uncomment this section.
    # It queries ALL documents matching the ad-hoc filters first.
    # mongo_filter_no_time = {}
    # if "adhocFilters" in req:
    #     for f in req["adhocFilters"]:
    #         mongo_filter_no_time[f["key"]] = {"$in": f["value"] if isinstance(f["value"], list) else [f["value"]]}
    #
    # cursor = col.find(mongo_filter_no_time, {"_id": 0}) # Don't fetch _id
    # print(f"Found {col.count_documents(mongo_filter_no_time)} documents to process in Python...")
    # --- END BLOCK 2 ---


    results = []
    for target in req["targets"]:
        metric = target["target"]
        points = []

        # If using the EFFICIENT method, the find() is fast.
        cursor = col.find(mongo_filter, {"_id": 0})
        
        for doc in cursor:
            # If using EFFICIENT method, 'timestamp' is already a datetime object
            ts = doc.get("timestamp")
            
            # If using SLOW method, you must parse the strings here
            # ts = parse_ts_to_utc(doc.get("date", ""), doc.get("time", ""))
            
            # Check if ts is valid
            if not ts:
                continue

            # This time check is only needed for the SLOW method
            # if not (from_dt <= ts <= to_dt):
            #     continue
            
            ts_ms = int(ts.timestamp() * 1000)
            metric_value = doc.get(metric)
            if isinstance(metric_value, (int, float)):
                points.append([metric_value, ts_ms])

        print(f"Added {len(points)} datapoints for metric '{metric}'.")
        results.append({"target": metric, "datapoints": points})
        
    return jsonify(results)
    """
    /query is the main endpoint for time series data.
    It respects the time range and filters sent by Grafana.
    """
    req = request.get_json()
    
    # --- Time Range Filter (Essential for performance) ---
    range_from_str = req["range"]["from"]
    range_to_str = req["range"]["to"]
    from_dt = datetime.fromisoformat(range_from_str.replace('Z', '+00:00'))
    to_dt = datetime.fromisoformat(range_to_str.replace('Z', '+00:00'))

    # --- FIX #1: Initialize mongo_filter as an empty dictionary FIRST ---
    mongo_filter = {}

    # --- Ad-hoc Filter (for dashboard variables) ---
    if "adhocFilters" in req:
        for f in req["adhocFilters"]:
            mongo_filter[f["key"]] = {"$in": f["value"] if isinstance(f["value"], list) else [f["value"]]}

    results = []
    for target in req["targets"]:
        metric = target["target"]
        
        # --- DEBUGGING PRINT #1 ---
        print(f"--- Querying for metric: '{metric}' with filter: {mongo_filter} ---")
        
        # --- FIX #2: Now it's safe to use mongo_filter here ---
        all_docs = list(col.find(mongo_filter))
        
        # --- DEBUGGING PRINT #2 ---
        print(f"Found {len(all_docs)} documents in MongoDB matching the filter.")

        points = []
        # Loop through the found documents and filter by time
        for doc in all_docs:
            ts = parse_ts_to_utc(doc.get("date", ""), doc.get("time", ""))
            
            # This check is still very important
            if ts and from_dt <= ts <= to_dt:
                ts_ms = int(ts.timestamp() * 1000)
                # Ensure the metric value is a number, default to 0 if not
                metric_value = doc.get(metric)
                if isinstance(metric_value, (int, float)):
                    points.append([metric_value, ts_ms])

        # --- DEBUGGING PRINT #3 ---
        print(f"Added {len(points)} datapoints to the graph for the time range: {from_dt} to {to_dt}.")
        
        results.append({"target": metric, "datapoints": points})
        
    return jsonify(results)
    """
    /query is the main endpoint for time series data.
    """
    req = request.get_json()
    
    # ... (Time Range and Filter logic) ...
    # from_dt = ...
    # to_dt = ...
    # mongo_filter = ...

    results = []
    for target in req["targets"]:
        metric = target["target"]
        
        # --- ADD THIS FOR DEBUGGING ---
        print(f"--- Querying for metric: {metric} ---")
        
        points = []
        # Find all documents first (ignoring time for now)
        all_docs = list(col.find(mongo_filter))
        print(f"Found {len(all_docs)} documents matching the ad-hoc filters.")
        # --- END DEBUGGING ADDITION ---

        # Now loop through them and filter by time
        for doc in all_docs:
            ts = parse_ts_to_utc(doc.get("date", ""), doc.get("time", ""))
            
            # --- MORE DEBUGGING ---
            if not ts:
                print(f"Failed to parse timestamp for doc: {doc['_id']}")
                continue # Skip this document
            # --- END DEBUGGING ---

            if from_dt <= ts <= to_dt:
                ts_ms = int(ts.timestamp() * 1000)
                points.append([doc.get(metric), ts_ms])
        
        print(f"Added {len(points)} datapoints to the graph for the selected time range.")
        results.append({"target": metric, "datapoints": points})
        
    return jsonify(results)
@app.route("/annotations", methods=["POST"])
def annotations():
    """
    /annotations returns events to overlay on graphs, like deployments or errors.
    Here, we'll return all logs with 'ERROR' level.
    """
    req = request.get_json()
    range_from_str = req["annotation"]["range"]["from"]
    from_dt = datetime.fromisoformat(range_from_str.replace('Z', '+00:00'))
    range_to_str = req["annotation"]["range"]["to"]
    to_dt = datetime.fromisoformat(range_to_str.replace('Z', '+00:00'))

    annotation_list = []
    for doc in col.find({"level": "ERROR"}):
        ts = parse_ts_to_utc(doc.get("date", ""), doc.get("time", ""))
        if ts and from_dt <= ts <= to_dt:
            annotation_list.append({
                "annotation": req["annotation"]["name"], # The name from Grafana
                "time": int(ts.timestamp() * 1000),
                "title": doc.get("component", "Unknown Component"),
                "tags": ["error", doc.get("pid", "N/A")],
                "text": doc.get("message", "No message")
            })
    return jsonify(annotation_list)

# ==============================================================================
# CUSTOM AGGREGATION ENDPOINTS FOR SPECIFIC PANELS
# These do not need to be time-series aware.
# ==============================================================================

@app.route("/stats/total_logs", methods=["POST"])
def total_logs():
    """Stat Panel: Total number of logs."""
    count = col.count_documents({})
    return jsonify([{"total_count": count}])

@app.route("/stats/anomaly_count", methods=["POST"])
def anomaly_count():
    """Stat Panel: Total number of anomalies."""
    count = col.count_documents({"is_anomaly": 1})
    return jsonify([{"anomaly_count": count}])

@app.route("/stats/unique_pids", methods=["POST"])
def unique_pids():
    """Stat Panel: Count of unique process IDs."""
    count = len(col.distinct("pid"))
    return jsonify([{"unique_pids": count}])
    
@app.route("/tables/logs_by_level", methods=["POST"])
def logs_by_level():
    """Pie Chart or Bar Chart: Group logs by their level."""
    pipeline = [
        {"$group": {"_id": "$level", "count": {"$sum": 1}}},
        {"$project": {"Level": "$_id", "Count": "$count", "_id": 0}}
    ]
    result = list(col.aggregate(pipeline))
    return jsonify(result)

@app.route("/tables/anomaly_by_pid", methods=["POST"])
def anomaly_by_pid():
    """Bar Chart or Table: Top 10 PIDs with the most anomalies."""
    pipeline = [
        {"$match": {"is_anomaly": 1}},
        {"$group": {"_id": "$pid", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
        {"$project": {"PID": "$_id", "Count": "$count", "_id": 0}}
    ]
    result = list(col.aggregate(pipeline))
    return jsonify(result)

@app.route("/tables/raw_logs", methods=["POST"])
def raw_logs():
    """Table Panel: Show the most recent 100 logs."""
    # This endpoint could be enhanced to support pagination and filtering
    result = []
    for doc in col.find({}).sort([("_id", -1)]).limit(100):
        ts = parse_ts_to_utc(doc.get("date"), doc.get("time"))
        result.append({
            "Timestamp": ts.isoformat() if ts else "N/A",
            "Level": doc.get("level"),
            "Component": doc.get("component"),
            "Message": doc.get("message")
        })
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)