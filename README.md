
# Big Data Real-Time Web Log Analytics Pipeline

## Project Objectives

- Build a robust, fault-tolerant data pipeline for large-scale log analytics.
- Support real-time and batch analytics with minimal latency.
- Enable advanced anomaly detection and alerting using ML.
- Provide interactive dashboards for both real-time and historical data.

---


**Work flow:**
- **NiFi:** Ingests raw web logs and preprocesses them.
- **Kafka:** Acts as a scalable message queue.
- **Spark:** Performs real-time analytics and streaming ETL.
- **ML/Alerting:** ML/anomaly detection runs in parallel with Spark processing.
- **MongoDB:** Stores processed data for persistent, historical analysis.
- **Grafana:** Visualizes both real-time (direct) and stored (via MongoDB) metrics.

---

## Tech Stack

- **Data Ingestion:** Apache NiFi
- **Message Broker:** Apache Kafka
- **Stream Processing:** Apache Spark (Structured Streaming)
- **Storage:** MongoDB (via Docker)
- **Dashboard:** Grafana (with separate real-time and batch views)
- **Machine Learning:** Python/Scikit-learn (integrated alongside Spark)
- **Orchestration & Deployment:** Docker

---

## Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bigdata-weblog-analytics.git
cd bigdata-weblog-analytics
```

### 2. Environment Prerequisites

- Docker & Docker Compose
- Java 8+
- Python 3.9+
- Apache NiFi
- Apache Kafka & Zookeeper
- Apache Spark
- MongoDB

### 3. Running with Docker Compose

```bash
docker-compose up -d
```

_This spins up MongoDB and (optionally) other dependencies._

### 4. Start Services

- **NiFi:** Launch and configure your flow to pick up the web logs.
- **Kafka:** Start broker & create topic (`log_topic`).
- **Spark:** Run the Spark Streaming job:

```bash
python app.py
```

---

## Usage Guide

1. **Ingest Log Data:** Place your NASA logs in the designated NiFi source directory.
2. **Processing:** NiFi sends logs to Kafka; Spark consumes from Kafka, processes data, and writes results to MongoDB.
3. **ML/Alerting:** Runs in parallel, monitors anomalies, and can trigger alerts.
4. **Visualization:** Use Grafana dashboards for both real-time and batch analytics.

---

## Dashboarding

- **Real-Time Dashboard:**  
  Grafana connects to your Flask backend (usually running at `http://localhost:5001`), which exposes real-time data and metrics via REST API endpoints. Grafana panels can query:
  - `/query` for time series metrics (e.g., `msg_len`, `level_num`, `is_anomaly`)
  - `/annotations` for overlaying error or event markers
  - Other custom endpoints for stats and tables

- **Historical Dashboard:**  
  Grafana uses the same Flask endpoints, which fetch persisted analytics and log data from MongoDB. This enables deep exploration of historical trends, anomaly spikes, and system activity over any custom time range.

**Setup:**
1. **Added the [JSON API (SimpleJson)] data source in Grafana**  
   Exposed flask api from your backend - `http://localhost:5001`.
2. **Created Panels and Dashboards by Querying:**
    - `/query` – for time series metrics (`msg_len`, `level_num`, `is_anomaly`, etc.)
    - `/tables/raw_logs` – for the latest logs (Table panel)
    - `/tables/logs_by_level` – log levels (Bar/Pie chart)
    - `/tables/anomaly_by_pid` – anomaly processes (Bar/Table)
    - `/stats/total_logs` – total logs (Stat panel)
    - `/stats/anomaly_count` – total anomalies (Stat panel)
    - `/annotations` – to overlay error events

---


## Machine Learning/Alerting

- ML models can be trained on historical data (batch).
- Alerts (anomaly detection, outlier detection) are generated in real-time and can be pushed to dashboards.

---

## Results

- Real-time monitoring of web log traffic and anomalies.
- Efficient, scalable data processing pipeline.
- Custom dashboards for both live and historical insights.

---

## Challenges & Solutions

- **Scalability:** Used distributed technologies to handle large log volumes.
- **Low Latency:** Streaming architecture ensures minimal delay from log ingestion to dashboard visualization.
- **ML Integration:** Decoupled ML pipeline allows for flexible updates and experiments.

---

## Future Work

- Integration with more advanced deep learning-based anomaly detection.
- Automated dashboard provisioning and alert configuration.
- Support for additional log sources and schema evolution.

---

## References

- [Apache NiFi Docs](https://nifi.apache.org/docs.html)
- [Apache Kafka Docs](https://kafka.apache.org/documentation/)
- [Apache Spark Docs](https://spark.apache.org/docs/latest/)
- [MongoDB Docs](https://www.mongodb.com/docs/)
- [Grafana Docs](https://grafana.com/docs/)

---

