FROM apache/airflow:3.0.0-python3.9

USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

RUN pip install --no-cache-dir \
    apache-airflow[celery,postgres,redis,ssh]==3.0.0
HEALTHCHECK NONE
RUN mkdir -p /opt/airflow/logs && chown -R airflow: /opt/airflow/logs
RUN pip install "apache-airflow[auth,celery]"
ENV _AIRFLOW_WWW_USER_USERNAME=airflow \
    _AIRFLOW_WWW_USER_PASSWORD=airflow \
    _AIRFLOW_WWW_USER_EMAIL=admin@example.com \
    _AIRFLOW_WWW_USER_FIRSTNAME=Admin \
    _AIRFLOW_WWW_USER_LASTNAME=User
RUN pip install apache-airflow[celery,postgres,redis,ssh]==3.0.0