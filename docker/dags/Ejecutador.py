from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.ssh.operators.ssh import SSHOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'retries': 999,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
        dag_id='ejecutar_servidor_semanal',
        default_args=default_args,
        description='Ejecuta servidor.py semanalmente.',
        schedule='@once',
        start_date=datetime(2025, 5, 26),
        catchup=False,
        tags=['servidor'],
) as dag:
    ejecutar_script = SSHOperator(
        task_id='ejecutar_servidor',
        ssh_conn_id='ssh_host_3',
        command='python3 /home/debian/AlkamelGlobal/Servidor/Servidor.py > /tmp/servidor_debug.log 2>&1',
    )