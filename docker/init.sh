#!/bin/bash
set -e
mkdir -p /opts/airflow/{logs,dags,plugins,config}
chown -R "${AIRFLOW_UID}:0" /opts/airflow/{logs,dags,plugins,config}
export AIRFLOW__CORE__SQL_ALCHEMY_CONN="postgresql+psycopg2://airflow:airflow@postgres/airflow"

echo "Waiting for database..."
timeout 60 bash -c 'until airflow db check; do sleep 5; done' || {
  echo "ERROR: Database not available after 60 seconds"
  exit 1
}

echo "Checking if airflow database exists..."
PGPASSWORD="${POSTGRES_PASSWORD}" psql -h postgres -U airflow -l | grep -qw airflow
if [ $? -ne 0 ]; then
  echo "Airflow database does not exist. Creating it..."
  PGPASSWORD="${POSTGRES_PASSWORD}" psql -h postgres -U postgres -c "CREATE DATABASE airflow OWNER airflow;"
  if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create airflow database."
    exit 1
  fi
else
  echo "Airflow database already exists."
fi

echo "Running migrations (Airflow version 3.0.0)..."
date
airflow version | grep "3.0.0" || {
  echo "ERROR: Expected Airflow version 3.0.0 but found $(airflow version)"
  exit 1
}
airflow db migrate
echo "Migrations finished."
date

if ! airflow db check; then
  echo "ERROR: Database migration failed"
  exit 1
fi
echo "Creating admin user..."
airflow users create --username "airflow3" --password "airflow" --firstname Admin --lastname User --role Admin --email admin3@example.com
echo "Initialization complete."

python /opt/airflow/scripts/create_admin.py