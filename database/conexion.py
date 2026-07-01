import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """
    Retorna una conexión a PostgreSQL (Supabase).
    La URL viene de la variable de entorno DATABASE_URL.
    """
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("La variable de entorno DATABASE_URL no está configurada.")

    conn = psycopg2.connect(database_url)
    return conn


def get_cursor(conn):
    """
    Retorna un cursor que devuelve filas como diccionarios (equivalente a dictionary=True de MySQL).
    Usar: cursor = get_cursor(conn)
    """
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)