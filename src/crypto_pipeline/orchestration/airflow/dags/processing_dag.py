# dags/processing_dag.py
import pendulum
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from crypto_pipeline.warehouse.duckdb.init_db import DuckDBManager

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': pendulum.datetime(2024,1,1, tz='UTC')
}

def init_duckdb(**context):
    """initialize duckdb with current S3 data"""
    db = DuckDBManager('crypto_trading.duckdb')
    with db.get_connection() as conn:
        # crypto_pipeline.db initialized & _setup_tables() run
        pass


with DAG(
    'crypto_processing',
    default_args=default_args,
    description='Load S3 data into DuckDB & transform with dbt',
    schedule_interval='0 * * * *',
    catchup=False,
) as dag:
    
    init_db = PythonOperator(
        task_id='init_duckdb',
        python_callable=init_duckdb
    )

    HOME = os.path.expanduser('~')
    DBT_PATH = os.path.join(HOME, 'crypto_pipeline/src/crypto_pipeline/transformers/dbt')

    run_dbt = BashOperator(
        task_id='run_dbt',
        bash_command=f'cd {DBT_PATH} && dbt run'
    )

    init_db >> run_dbt