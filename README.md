# Real-Time-Stock-Market-Pipeline
A real-time stock market data pipeline using Snowflake, DBT, Docker, and Apache Airflow. I've streamed live market data from an API, orchestrated transformations, managed data in Snowflake, and delivered powerful visualizations with Power BI.

## Project Overview & Architecture:
This project is my take on building an end-to-end data engineering pipeline for analyzing stock market data in real-time. The goal was to create something scalable, automated, and insightful—pulling live stock quotes, processing them through various stages, and ultimately visualizing key metrics. I designed it around a modern data stack that handles streaming data efficiently, inspired by the medallion architecture (bronze, silver, gold layers) for data quality and usability. 

At a high level, the architecture looks like this:
![image](https://github.com/user-attachments/assets/a170aa45-c999-4c04-a8b9-a2be026912cd)
- **Data Source:** We start with fetching stock quotes from the Finnhub API for a list of popular symbols like AAPL, MSFT, etc.
- **Streaming Layer:** Apache Kafka handles the real-time data ingestion, acting as a message broker to decouple producers and consumers.
- **Storage Layer:** MinIO (an S3-compatible object store) serves as our data lake for raw files, making it easy to store JSON records without a schema upfront.
- **Orchestration:** Apache Airflow schedules and manages the ETL workflows, ensuring data moves from MinIO to Snowflake periodically.
- **Data Warehouse:** Snowflake stores the processed data, allowing for scalable querying and separation of compute from storage.
- **Transformation:** dbt (data build tool) handles the SQL-based transformations, turning raw data into clean, analyzable tables.
- **Visualization:** Power BI connects to Snowflake for dashboards showing KPIs like current prices and changes.
- **Containerization:** Everything is wrapped in Docker via docker-compose.yml, so you can spin it up locally with one command.

I chose this setup because it's cloud-agnostic where possible, cost-effective for learning, and teaches key concepts like streaming, ETL, and data modeling.

## Key Objectives of the Project
When I started this, I had a few main goals in mind to make it practical and educational:

Real-Time Data Ingestion: Learn how to fetch and stream live data from an API without losing any updates. This teaches handling APIs, error resilience, and streaming patterns.
Scalable Storage: Use a data lake approach with MinIO to store raw JSON files, simulating S3 in production. This objective was about understanding object storage and why it's better for unstructured data than traditional databases.
Automated ETL Pipelines: Orchestrate data movement and transformation with Airflow and dbt, emphasizing workflow automation, scheduling (e.g., every minute), and version-controlled data models.
Data Quality and Layering: Implement the medallion architecture—bronze for raw, silver for cleaned, gold for aggregated KPIs—to show how data evolves from messy to insightful.
Visualization and Insights: Connect to Power BI to create dashboards, focusing on business value like tracking stock changes. This ties everything back to real-world use cases, like monitoring market trends.
Containerized Deployment: Make it easy to run locally or deploy, teaching Docker basics and microservices.

## Overall Technology & Tool Used:
To achieve the above objectives, this project leverages the following Azure services:

- **SQL Server Management Studio (SSMS):** Used to connect the on-premises SQL Server DB for integration into the Azure data pipeline.
- **Docker:** For containerizing all components. It's the foundation—run docker-compose up to start everything. Teaches isolation and reproducibility.
- **Apache Kafka (with Zookeeper):** Handles streaming. I used Confluent's images for ease. Kafka is great for high-throughput, fault-tolerant messaging.
- **MinIO:** S3-compatible storage running locally. Mimics AWS S3, perfect for development without cloud bills. Access the UI at http://localhost:9001.
- **Apache Airflow:** For DAGs (Directed Acyclic Graphs) that orchestrate tasks. Includes a web UI at http://localhost:8080 for monitoring.
- **Kafdrop:** A UI for Kafka topics, helpful for debugging (http://localhost:9000).
- **PostgreSQL:** Airflow's metadata backend, simple and reliable.
- **Snowflake:** As the data warehouse. It's serverless, pay-per-use, and excels at handling semi-structured data like JSON. I loaded data here for querying.
- **Power BI:** For visualizations. Connects directly to Snowflake. Great for interactive dashboards without coding.

## Steps Taken:
### Step 1: Set Up Environment:
- Edit producer.py and consumer.py with your Finnhub API key (get one free at finnhub.io) and MinIO password.
- Update minio_to_snowflake.py with your Snowflake credentials (user, password, account, etc.).
- Run docker-compose up -d to start all services. Check logs for errors

![image](https://github.com/user-attachments/assets/38be04bc-0a43-4dab-a2d4-f9538aa17265)

### Step 2: Data Ingestion with Producer:
- The producer.py script fetches quotes every 6 seconds (to avoid API limits) using requests library.
- It sends JSON data to Kafka topic "stock-quotes". Run it with python producer.py.

![image](https://github.com/user-attachments/assets/4c1b3300-f211-4e4a-8ed1-e59aa6be1851)

### Step 3: Consuming and Storing Data:
Create a Storage Account:
- consumer.py listens to Kafka, saves each message as a JSON file in MinIO's "bronze-transactions" bucket.
- Files are keyed like "symbol/timestamp.json" for organization. Run python consumer.py in another terminal.

### Step 4: Orchestrating with Airflow:
- Access Airflow UI, enable the DAG "minio_to_snowflake_stream".
- It runs every minute: Downloads files from MinIO to local temp, uploads to Snowflake stage, then COPY INTO a raw table.
- In Snowflake, create the table BRONZE_STOCK_QUOTES_RAW as variant type for JSON.

![image](https://github.com/user-attachments/assets/40a00002-e0c0-4dfc-8581-818d9e087f8f)

### Step 5: Transforming Data with dbt:
- Install dbt-snowflake: pip install dbt-snowflake.
- Configure profiles.yml with Snowflake creds.
- Models: bronze_stg_stock_quotes.sql parses JSON; silver_clean_stock_quotes.sql cleans and rounds; gold_kpi.sql gets latest KPIs.
- Run dbt run to build tables. Use sources.yml for referencing.

![image](https://github.com/user-attachments/assets/248437b0-ba71-4e10-bac6-140a784f80ec)

### Step 6: Visualization:
- In Power BI, connect to Snowflake, query the gold table.
- Build dashboards for symbols, prices, changes. Export or share as needed.

### Challenges Faced

- Integrating data from multiple sources (e.g., on-premises SQL Server and cloud-based GitHub repositories) due to differences in data formats & structures.
- Ensuring data quality and consistency across different data sources.
- Managing access for on-premise and cloud users with security credentials in Entra ID and key vault.
- Setting parameters for dynamic parsing and migration of source files to sink folder using JSON script.
- Mounting the storage account to azure data lake bronze container.
- Creating external tables in synapse analytics using CETAS which required scope credential, data source link, file formats etc.
- Integration of various azure services and applications, their linkage for effecient assembly.
- My experience with Power BI Desktop for data visualization is currently rusty. 
