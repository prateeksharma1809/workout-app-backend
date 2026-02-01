from dotenv import load_dotenv
import os
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
import time

load_dotenv()

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING") or  ""

pool = ThreadedConnectionPool(
    minconn=2,
    maxconn=10,
    dsn=DB_CONNECTION_STRING,
    cursor_factory=RealDictCursor,
)

# Simple in-memory cache
_count_cache = {
    "total": None,
    "expires_at": 0,
}

CACHE_TTL = 300  # 5 minutes


def get_connection():
    return pool.getconn()

def release_connection(conn):
    pool.putconn(conn)

def get_total_count(conn) -> int:
    now = time.time()

    if _count_cache["total"] is not None and now < _count_cache["expires_at"]:
        return _count_cache["total"]

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as count FROM exercises;")
    total = cur.fetchone()["count"]
    cur.close()

    _count_cache["total"] = total
    _count_cache["expires_at"] = now + CACHE_TTL

    return total