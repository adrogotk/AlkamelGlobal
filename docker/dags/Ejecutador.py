from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.ssh.operators.ssh import SSHOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'retries': 1,
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
    # Ejecuta el script de busqueda y descarga de CSVs (y de los pilotos contenidos en ellos) en Hive
    ejecutar_script = SSHOperator(
        task_id='ejecutar_servidor',
        ssh_conn_id='ssh_host_9',
        command="""
                cd /home/debian/AlkamelGlobal/Servidor && \
                /home/debian/AlkamelGlobal/.venv3/bin/python Servidor.py
                """,
        get_pty=True,
        cmd_timeout=86400,
    )
    ejecutar_script