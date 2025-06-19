# Big Data Web Log Analysis using Hadoop and Spark

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Hadoop](https://img.shields.io/badge/Hadoop-MapReduce-yellow.svg)
![Spark](https://img.shields.io/badge/Apache%20Spark-PySpark-orange.svg)

This project demonstrates the analysis of web server log files using two major big data processing frameworks: **Hadoop MapReduce** and **Apache Spark**. The goal is to extract meaningful insights from a standard `access_log` file, showcasing the power and approach of each technology.

## 📝 Project Overview

Web server logs are a rich source of information about website traffic, user behavior, and potential server issues. This project provides scripts to process a sample `access_log` file to answer common analytical questions.

The project is divided into two main parts:
1.  **Hadoop MapReduce:** A classic implementation using Python for the Mapper and Reducer scripts to count the frequency of requested URLs.
2.  **Apache Spark:** A more comprehensive analysis using PySpark to perform multiple aggregations and filtering operations on the log data, such as analyzing HTTP status codes, identifying frequent visitors, and finding top accessed pages.

## 📊 Dataset

The project uses a sample `access_log` file located in the `Dataset/` directory. This is a standard [Common Log Format](https://en.wikipedia.org/wiki/Common_Log_Format) file, where each line represents a single request to the web server.

A typical log entry looks like this:
127.0.0.1 - - [21/Jul/2014:10:55:36 -0700] "GET /home.html HTTP/1.1" 200 2048


## ✨ Features & Analysis Performed

### 1. Hadoop MapReduce Analysis

The Hadoop job (`Hadoop/mapper.py` and `Hadoop/reducer.py`) performs a single, fundamental task:

-   **URL Request Count:** It processes the log file to count the number of times each unique file/endpoint was requested. This is a "Word Count" equivalent for web traffic.

### 2. Apache Spark Analysis

The PySpark script (`Spark/spark.py`) performs a more diverse set of analyses in a single run:

-   **HTTP Response Code Analysis:** Counts the occurrences of each HTTP status code (e.g., 200 OK, 404 Not Found, 500 Server Error).
-   **Frequent Hosts:** Identifies the top 10 client IP addresses (hosts) that made more than 10 requests.
-   **Top 10 Endpoints:** Finds the 10 most frequently accessed pages/endpoints.
-   **Top 10 "Not Found" Endpoints:** Lists the top 10 endpoints that resulted in a `404 Not Found` error, which is useful for finding broken links.

## 💻 Technologies Used

-   **Language:** Python 3
-   **Big Data Frameworks:**
    -   Apache Hadoop (with Hadoop Streaming)
    -   Apache Spark (with PySpark)

## 🚀 Getting Started

### Prerequisites

To run this project, you need a working big data environment.
-   Python 3.x
-   A running Hadoop cluster (a single-node setup in a VM or Docker is sufficient).
-   A running Spark instance (can be standalone or on the same cluster).
-   Git, to clone the repository.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Nimalesh/BigData_Web_Log.git
    cd BigData_Web_Log
    ```

### How to Run

#### 1. Running the Hadoop MapReduce Job

The Hadoop job uses the **Hadoop Streaming** utility, which allows you to run MapReduce jobs with any executable script (in this case, our Python files).

1.  **Place the dataset on HDFS:**
    First, you need to copy the `access_log` file to your Hadoop Distributed File System (HDFS).
    ```bash
    hdfs dfs -mkdir /input
    hdfs dfs -put Dataset/access_log /input/
    ```

2.  **Execute the Hadoop Streaming job:**
    Run the following command from the root of the project directory. Make sure to replace `<path-to-hadoop-streaming-jar>` with the actual path to your `hadoop-streaming.jar` file, which is usually found in the Hadoop distribution.

    ```bash
    hadoop jar <path-to-hadoop-streaming-jar> \
    -files Hadoop/mapper.py,Hadoop/reducer.py \
    -mapper 'python3 mapper.py' \
    -reducer 'python3 reducer.py' \
    -input /input/access_log \
    -output /output_hadoop
    ```

3.  **View the results:**
    Once the job is complete, you can view the output in the HDFS directory `/output_hadoop`.
    ```bash
    hdfs dfs -cat /output_hadoop/part-00000 | head -n 10
    ```
    This will show the top 10 lines from the output file, with each line containing a URL and its corresponding request count.

#### 2. Running the Spark Job

The Spark job is executed using `spark-submit`. This example assumes you are running it in a local mode, but it can easily be adapted for a cluster. The script is configured to read the local file directly.

1.  **Execute the PySpark script:**
    From the root of the project directory, run the `spark-submit` command.
    ```bash
    spark-submit Spark/spark.py
    ```
    *Note: The script `Spark/spark.py` is hardcoded to read `Dataset/access_log`. If your dataset is elsewhere, please update the path inside the script.*

2.  **View the results:**
    The script will print the results of all four analyses directly to your console (stdout). You will see neatly formatted output for:
    -   Response Code Counts
    -   Top 10 Frequent Hosts
    -   Top 10 Endpoints
    -   Top 10 Not Found Endpoints

## 📄 License

This project is unlicensed. Please refer to the repository owner for usage rights.

---
