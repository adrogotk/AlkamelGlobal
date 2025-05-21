from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'retries': 5,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
        dag_id='ejecutar_servidor_semanal',
        default_args=default_args,
        description='Ejecuta servidor.py semanalmente.',
        schedule_interval='@weekly',
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=['servidor'],
) as dag:
    ejecutar_script = BashOperator(
        task_id='ejecutar_servidor',
        bash_command='python3 ../Servidor/servidor.py',
    )