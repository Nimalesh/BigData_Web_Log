
# Big Data Real-Time Web Log Analytics Pipeline

## Overview

This project implements a scalable, real-time web log analytics pipeline using modern Big Data technologies. The system ingests, processes, analyzes, and visualizes NASA server logs, enabling both immediate insights (real-time) and historical analysis (batch). Machine Learning/alerting modules are integrated parallel to Spark for advanced analytics.

---

## Table of Contents

- [Project Objectives](#project-objectives)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [Usage Guide](#usage-guide)
- [Dashboarding](#dashboarding)
- [Machine Learning/Alerting](#machine-learningalerting)
- [Results](#results)
- [Challenges & Solutions](#challenges--solutions)
- [Future Work](#future-work)
- [References](#references)

---

## Project Objectives

- Build a robust, fault-tolerant data pipeline for large-scale log analytics.
- Support real-time and batch analytics with minimal latency.
- Enable advanced anomaly detection and alerting using ML.
- Provide interactive dashboards for both real-time and historical data.

---

## Architecture

```mermaid
graph TD
    A[NASA Log Source] --> B[Apache NiFi]
    B --> C[Kafka Broker]
    C --> D[Spark Streaming]
    D --> E[MongoDB (Docker)]
    E --> F[Grafana Dashboard]
    D --> G[ML/Alerting (Parallel)]
```

**Flow Explanation:**
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
python spark_streaming_app.py
```

- **ML/Alerting:** Start the ML process in parallel (see `/ml_alerting/`).

- **Grafana:** Import provided dashboards and configure data sources for both real-time (e.g., directly from Spark or via REST) and stored (MongoDB) data.

---

## Usage Guide

1. **Ingest Log Data:** Place your NASA logs in the designated NiFi source directory.
2. **Processing:** NiFi sends logs to Kafka; Spark consumes from Kafka, processes data, and writes results to MongoDB.
3. **ML/Alerting:** Runs in parallel, monitors anomalies, and can trigger alerts.
4. **Visualization:** Use Grafana dashboards for both real-time and batch analytics.

---

## Dashboarding

- **Real-Time Dashboard:** Connects directly to Spark/memory or REST endpoint.
- **Historical Dashboard:** Connects to MongoDB for persisted analytics.

Example Grafana panel queries and configuration can be found in `/dashboards/`.

---

## Machine Learning/Alerting

- ML models can be trained on historical data (batch) or streaming data (real-time).
- Alerts (anomaly detection, outlier detection) are generated in real-time and can be pushed to dashboards, email, or other systems.

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
- NASA HTTP Web Server Log Data: [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/227/nasa+access+log+jul+1995)

---

> _For academic/collaborative use only. For questions or contributions, please open an issue or pull request._
