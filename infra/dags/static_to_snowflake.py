import os
import boto3
import snowflake.connector
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Configuration for MinIO
MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "enter_password"
BUCKET = "static-stock-data"
LOCAL_DIR = "/tmp/minio_downloads_static" 

# Snowflake configuration
SNOWFLAKE_USER = "enter_username"
SNOWFLAKE_PASSWORD = "enter_password"
SNOWFLAKE_ACCOUNT_IDENTIFIER = "enter_snowflake_account_identifier"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DB = "STOCKS_MDS"
SNOWFLAKE_SCHEMA = "COMMON"

# Table and stage mappings
FILE_TABLE_MAPPING = {
    "company_stocks.csv": {
        "table": "COMPANY_STOCKS",
        "stage": "@%COMPANY_STOCKS"
    },
    "company_reviews.csv": {
        "table": "COMPANY_REVIEWS",
        "stage": "@%COMPANY_REVIEWS"
    }
}

def download_from_minio():
    os.makedirs(LOCAL_DIR, exist_ok=True)
    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY
    )
    local_files = []
    for file_key in FILE_TABLE_MAPPING.keys():
        local_file = os.path.join(LOCAL_DIR, os.path.basename(file_key))
        s3.download_file(BUCKET, file_key, local_file)
        print(f"Downloaded {file_key} -> {local_file}")
        local_files.append({"file": local_file, "key": file_key})
    return local_files

def load_to_snowflake(**kwargs):
    local_files = kwargs['ti'].xcom_pull(task_ids='download_minio')
    if not local_files:
        print("No files to load.")
        return

    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT_IDENTIFIER,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DB,
        schema=SNOWFLAKE_SCHEMA
    )
    cur = conn.cursor()

    for file_info in local_files:
        local_file = file_info["file"]
        file_key = file_info["key"]
        table = FILE_TABLE_MAPPING[file_key]["table"]
        stage = FILE_TABLE_MAPPING[file_key]["stage"]

        # Upload to Snowflake stage
        cur.execute(f"PUT file://{local_file} {stage}")
        print(f"Uploaded {local_file} to Snowflake stage {stage}")

        # Copy into respective table
        cur.execute(f"""
            COPY INTO {SNOWFLAKE_DB}.{SNOWFLAKE_SCHEMA}.{table}
            FROM {stage}
            FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"' ERROR_ON_COLUMN_COUNT_MISMATCH=false)
        """)
        print(f"COPY INTO {table} executed")

    cur.close()
    conn.close()

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 9, 22),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "minio_to_snowflake_batch",
    default_args=default_args,
    schedule_interval=None,  # No scheduler for one-time load
    catchup=False,
) as dag:

    task1 = PythonOperator(
        task_id="download_minio",
        python_callable=download_from_minio,
    )

    task2 = PythonOperator(
        task_id="load_snowflake",
        python_callable=load_to_snowflake,
        provide_context=True,
    )

    task1 >> task2