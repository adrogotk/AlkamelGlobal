import psycopg2
from psycopg2.extras import execute_values
from werkzeug.security import generate_password_hash
import uuid

# Parámetros de conexión (ajusta según tu docker-compose)
DB_HOST = "postgres"
DB_PORT = 5432
DB_NAME = "airflow"
DB_USER = "airflow"
DB_PASS = "airflow"

USERNAME = "airflow2"
PASSWORD = "airflow"
EMAIL = "admin2@example.com"
FIRST_NAME = "Admin"
LAST_NAME = "User"

def main():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
    )
    cur = conn.cursor()

    # Verificar si usuario ya existe
    cur.execute("SELECT id FROM ab_user WHERE username = %s", (USERNAME,))
    if cur.fetchone():
        print(f"Usuario '{USERNAME}' ya existe")
        cur.close()
        conn.close()
        return

    # Obtener id del rol Admin
    cur.execute("SELECT id FROM ab_role WHERE name = 'Admin'")
    admin_role = cur.fetchone()
    if not admin_role:
        print("No se encontró el rol 'Admin'. ¿La base de datos está inicializada?")
        cur.close()
        conn.close()
        return
    admin_role_id = admin_role[0]

    # Crear nuevo usuario
    user_id = str(uuid.uuid4())
    hashed_password = generate_password_hash(PASSWORD)

    cur.execute(
        """
        INSERT INTO ab_user (username, first_name, last_name, email, active, password)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (USERNAME, FIRST_NAME, LAST_NAME, EMAIL, True, hashed_password)
    )

    # Asignar rol admin al usuario
    cur.execute("SELECT id FROM ab_user WHERE username = %s", (USERNAME,))
    user=cur.fetchone()
    user_id=user[0]
    cur.execute(
        """
        INSERT INTO ab_user_role (user_id, role_id) VALUES (%s, %s)
        """,
        (user_id, admin_role_id)
    )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Usuario '{USERNAME}' creado con rol Admin.")

if __name__ == "__main__":
    main()