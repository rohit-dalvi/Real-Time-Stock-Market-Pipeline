import os
import boto3
import snowflake.connector
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta


MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "enter_password"
BUCKET = "bronze-transactions"
LOCAL_DIR = "/tmp/minio_downloads"  # use absolute path for Airflow

SNOWFLAKE_USER = "enter_username"
SNOWFLAKE_PASSWORD = "enter_password"
SNOWFLAKE_ACCOUNT_IDENTIFIER = "enter_snowflake_account_identifier"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DB = "enter_your_db_name"
SNOWFLAKE_SCHEMA = "enter_schema_name"

def download_from_minio():
    os.makedirs(LOCAL_DIR, exist_ok=True)
    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY
    )
    objects = s3.list_objects_v2(Bucket=BUCKET).get("Contents", [])
    local_files = []
    for obj in objects:
        key = obj["Key"]
        local_file = os.path.join(LOCAL_DIR, os.path.basename(key))
        s3.download_file(BUCKET, key, local_file)
        print(f"Downloaded {key} -> {local_file}")
        local_files.append(local_file)
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

    for f in local_files:
        cur.execute(f"PUT file://{f} @%bronze_stock_quotes_raw")
        print(f"Uploaded {f} to Snowflake stage")

    cur.execute("""
        COPY INTO STOCKS_MDS.COMMON.BRONZE_STOCK_QUOTES_RAW
        FROM @%bronze_stock_quotes_raw
        FILE_FORMAT = (TYPE='JSON')
    """)
    print("COPY INTO executed")

    cur.close()
    conn.close()

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 9, 19),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "minio_to_snowflake_stream",
    default_args=default_args,
    schedule_interval="*/1 * * * *",  # scheduler for every 1 minute streaming
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

