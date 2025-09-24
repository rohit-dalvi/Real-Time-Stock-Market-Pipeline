# Real-Time-Stock-Market-Pipeline
A real-time stock market data pipeline using Snowflake, DBT, Docker, and Apache Airflow. I've streamed live stock market data from an API, orchestrated transformations, managed data in Snowflake, and delivered powerful visualizations with Power BI.

## Project Overview & Architecture:
This project is my take on building an end-to-end data engineering pipeline for analyzing stock market data in real-time. The goal was to create something scalable, automated, and insightful - pulling live stock quotes, processing them through various stages, and ultimately visualizing key metrics. I designed it around a modern data stack that handles streaming data efficiently, inspired by the medallion architecture (bronze, silver, gold layers) for data quality and usability. 

<img width="1260" height="632" alt="image" src="https://github.com/user-attachments/assets/e02b6cd6-c46f-4c66-96ad-24a302a84784" />

- **Data Source:** Started with fetching stock quotes from the Finnhub API for a list of popular symbols like AAPL, MSFT, etc.
- **Streaming Layer:** Apache Kafka handles the real-time data ingestion, acting as a message broker to decouple producers and consumers.
- **Storage Layer:** MinIO (an S3-compatible object store) serves as a data lake for raw files, making it easy to store JSON records without a schema upfront.
- **Orchestration:** Apache Airflow schedules and manages the ETL workflows, ensuring data moves from MinIO to Snowflake periodically.
- **Data Warehouse:** Snowflake stores the processed data, allowing for scalable querying and separation of compute from storage.
- **Transformation:** dbt (data build tool) handles the SQL-based transformations, turning raw data into clean, analyzable tables.
- **Visualization:** Power BI connects to Snowflake for dashboards showing KPIs like current prices, changes, sector distribution, ratings, reviews, and sentiment stats.
- **Containerization:** Everything is wrapped in Docker via docker-compose.yml, so all the resources can spin up locally with one command.

I chose this setup because it's cloud-agnostic where possible, cost-effective for learning, and teaches key concepts like streaming, ETL, and data modeling.

## Key Objectives of the Project
When I started this, I had a few main goals in mind to make it practical and educational:

- **Real-Time Data Ingestion:** Learn how to fetch and stream live data from an API without losing any updates. This strengthens handling APIs, error resilience, and streaming patterns.
- **Scalable Storage:** Used a data lake approach with MinIO to store raw JSON files, simulating S3 in production. This objective was about understanding object storage and why it's better for unstructured data than traditional databases.
- **Automated ETL Pipelines:** Orchestrate data movement and transformation with Airflow and dbt, emphasizing workflow automation, scheduling (e.g., every minute), and version-controlled data models.
- **Data Quality and Layering:** Implement the medallion architecture—bronze for raw, silver for cleaned, gold for aggregated KPIs—to show how data evolves from messy to insightful.
- **Visualization and Insights:** Connect to Power BI to create dashboards, focusing on business value like tracking stock changes. This ties everything back to real-world use cases, like monitoring market trends.
- **Containerized Deployment:** Make it easy to run locally or deploy, learn Docker basics, and microservices.

## Technology & Tools Used:
To achieve the above objectives, this project leverages the following tech stack:
- **Docker:** For containerizing all components. It's the foundation—run docker-compose up to start everything.
- **Apache Kafka (with Zookeeper):** Handles streaming. Kafka is great for high-throughput, fault-tolerant messaging.
- **MinIO:** S3-compatible storage running locally. Mimics AWS S3, perfect for development without cloud bills.
- **Apache Airflow:** For DAGs (Directed Acyclic Graphs) that orchestrate tasks. Includes a web UI for monitoring.
- **Kafdrop:** A UI for Kafka topics, helpful for debugging.
- **PostgreSQL:** Airflow's metadata backend, simple and reliable.
- **Snowflake:** As the data warehouse. It's serverless, pay-per-use, and excels at handling semi-structured data like JSON.
- **Power BI:** For visualizations. Connects directly to Snowflake. Great for interactive dashboards without coding.

## Steps Taken:
### Step 1: Set Up Environment:
- Build a producer.py and consumer.py with your Finnhub API key (get one free at finnhub.io) and MinIO password.
- Update minio_to_snowflake.py with your Snowflake credentials (user, password, account, etc.).
- Create a docker-compose.yml script by assigning dedicated ports and an environment that will spin up your resource in one command.
- Run docker-compose up -d to start all services.
<img width="1600" height="553" alt="image" src="https://github.com/user-attachments/assets/203e60ff-a76f-42b8-a798-6d89f6d2dbdf" />

### Step 2: Data Ingestion with Producer:
- The producer.py script fetches quotes every 6 seconds (to avoid API limits) using the requests library.
  <img width="1272" height="876" alt="image" src="https://github.com/user-attachments/assets/f4c4400a-9da1-4dd9-858d-6e06d0404fe6" />

- It sends JSON data to the Kafka topic "stock-quotes". Run it with python producer.py.
  <img width="1107" height="890" alt="image" src="https://github.com/user-attachments/assets/4971ca2f-1d14-4379-913f-4defac964542" />

### Step 3: Consuming and Storing Data:
- consumer.py listens to Kafka, saves each message as a JSON file in MinIO's "bronze-transactions" bucket.
  <img width="1822" height="757" alt="image" src="https://github.com/user-attachments/assets/ae2fee14-3042-40cc-96c2-fb9852d64d16" />
- Files are keyed like "symbol/timestamp.json" for organization. Run python consumer.py in another terminal.
<img width="1211" height="940" alt="image" src="https://github.com/user-attachments/assets/cae6c2f5-543c-44fc-a4dd-728495b66a83" />

### Step 4: Orchestrating with Airflow:
- Access Airflow UI, enable the DAG "minio_to_snowflake_stream".
  <img width="1822" height="423" alt="Screenshot 2025-09-23 174705" src="https://github.com/user-attachments/assets/13687d6f-e1b5-4851-84e9-9edc55c42b0a" />
- It runs every minute: Downloads files from MinIO to local temp, uploads to Snowflake stage, then COPY INTO a raw table.
- In Snowflake, create the table BRONZE_STOCK_QUOTES_RAW as a variant type for JSON.
<img width="1384" height="675" alt="image" src="https://github.com/user-attachments/assets/4c6839e0-c805-4958-9996-28daa53f65b0" />


### Step 5: Transforming Data with dbt and Snowflake Notebooks:
- Install dbt-snowflake: pip install dbt-snowflake.
- Configure profiles.yml with Snowflake creds.
- Hit dbt run to build tables. Use sources.yml for referencing.
- Models: bronze_stg_stock_quotes.sql parses JSON; silver_clean_stock_quotes.sql cleans and rounds; gold_kpi.sql gets latest KPIs.
- Performed exploratory data analysis with sentiment analysis on the ratings and reviews based on the US top Fortune stock companies. Refer to company_stock_details.jpynb

### Step 6: Visualization:
- In Power BI, connect to Snowflake, query the gold static and dynamic tables with direct query mode to fetch the latest data every time.
- Build dashboards for symbols, reviews, ratings, sector, sentiments, and price changes, respectively.
<img width="1258" height="709" alt="image" src="https://github.com/user-attachments/assets/861843dd-fa75-425c-a899-495d389693ab" />

### Challenges Faced

- Setting up the Docker: Containers and validating the handshake between each port, whether actively running or not.
- Configuration Complexity: Setting up Kafka and MinIO with Docker required careful network configuration (e.g., port mappings, host.docker.internal).
- API Rate Limits: Handling FinnHub API rate limits necessitated error handling and a 6-second delay between requests.
- Snowflake Integration: Initial credential issues and stage setup in Snowflake were resolved with proper configuration.
- Data Transformation & Exploration: It was time-consuming to clean and enrich the sample synthetic data I created to widen the dataset for analytical references.

