import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "iotdb")
DB_USER = os.getenv("POSTGRES_USER", "lab05")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "lab05pass")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS readings (
    reading_id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL,
    metric TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit TEXT,
    timestamp TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

if __name__ == "__main__":
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as cursor:
        cursor.execute(CREATE_TABLE_SQL)
    conn.close()
