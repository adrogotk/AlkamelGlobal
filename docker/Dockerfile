FROM apache/airflow:3.0.0

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
HEALTHCHECK NONE
RUN mkdir -p /opt/airflow/logs && chown -R airflow: /opt/airflow/logs