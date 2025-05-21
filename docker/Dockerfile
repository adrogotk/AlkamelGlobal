FROM apache/airflow:3.0.0

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
HEALTHCHECK NONE
RUN mkdir -p /opt/airflow/logs && chown -R airflow: /opt/airflow/logs
USER airflow
RUN pip install "apache-airflow[auth,celery]"
ENV _AIRFLOW_WWW_USER_USERNAME=airflow \
    _AIRFLOW_WWW_USER_PASSWORD=airflow \
    _AIRFLOW_WWW_USER_EMAIL=admin@example.com \
    _AIRFLOW_WWW_USER_FIRSTNAME=Admin \
    _AIRFLOW_WWW_USER_LASTNAME=User