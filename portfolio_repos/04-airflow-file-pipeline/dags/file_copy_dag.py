from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


def _default_args():
    return {
        "owner": "you",
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
    }

 


with DAG(
    dag_id="file_copy_dag",
    default_args=_default_args(),
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["bronze", "file-transfer"],
) as dag:
    copy_task = BashOperator(
        task_id="copy_file_to_bronze",
        bash_command=(
            "mkdir -p /opt/airflow/dags/data/bronze && "
            "cp -f /opt/airflow/dags/data/input/sample.csv /opt/airflow/dags/data/bronze/sample.csv"
        ),
    )


