import psycopg2
from psycopg2.extras import execute_values
import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "http://exercisedb.dev/api/v1/exercises"
DB_CONFIG = {
    "host": os.getenv("DB_HOST") or "localhost",
    "database": os.getenv("DB_NAME") or "fitness_db",
    "user": os.getenv("DB_USER") or "postgres",
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT") or "5432",
}

LIMIT = 100
SORT_BY = "targetMuscles"
SORT_ORDER = "desc"
OFFSET = 600
NUM_REQUESTS = 2

# --- DATABASE SETUP ---
def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                exercise_id   TEXT PRIMARY KEY,
                name          TEXT NOT NULL,
                gif_url       TEXT,
                target_muscles   TEXT[],
                body_parts       TEXT[],
                equipments       TEXT[],
                secondary_muscles TEXT[],
                instructions     TEXT[]
            );
        """)
    conn.commit()

# --- FETCH ALL PAGES ---
def fetch_all_exercises(conn):
    all_exercises = []

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM exercises;")
    offset = cur.fetchone()[0]
    print(offset) # For resuming from last offset
    offset = max(offset, OFFSET)
    num_requests = 0

    while num_requests < NUM_REQUESTS:
        params = {
            "offset": offset,
            "limit": LIMIT,
            "sortBy": SORT_BY,
            "sortOrder": SORT_ORDER,
        }

        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()

        json_data = response.json()

        if not json_data.get("success"):
            print(f"API returned success=false at offset {offset}")
            break

        data = json_data.get("data", [])
        if not data:
            break  # no more results

        all_exercises.extend(data)
        print(f"Fetched {len(data)} exercises (offset={offset}, total so far={len(all_exercises)})")

        # Check if there's a next page
        if not json_data.get("metadata", {}).get("nextPage"):
            break

        offset += LIMIT
        print(f"Waiting before next request...")
        time.sleep(10)  # be polite to the API
        num_requests += 1
    return all_exercises

# --- SAVE TO DB ---
def save_exercises(conn, exercises):
    rows = [
        (
            ex["exerciseId"],
            ex["name"],
            ex.get("gifUrl"),
            ex.get("targetMuscles", []),
            ex.get("bodyParts", []),
            ex.get("equipments", []),
            ex.get("secondaryMuscles", []),
            ex.get("instructions", []),
        )
        for ex in exercises
    ]

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO exercises (
                exercise_id, name, gif_url,
                target_muscles, body_parts, equipments,
                secondary_muscles, instructions
            )
            VALUES %s
            ON CONFLICT (exercise_id) DO UPDATE SET
                name             = EXCLUDED.name,
                gif_url          = EXCLUDED.gif_url,
                target_muscles   = EXCLUDED.target_muscles,
                body_parts       = EXCLUDED.body_parts,
                equipments       = EXCLUDED.equipments,
                secondary_muscles = EXCLUDED.secondary_muscles,
                instructions     = EXCLUDED.instructions;
            """,
            rows,
        )
    conn.commit()
    print(f"Saved {len(rows)} exercises to the database.")


# --- MAIN ---
def main():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        exercises = fetch_all_exercises(conn)
        if not exercises:
            print("No exercises fetched.")
        else:
            create_table(conn)
            save_exercises(conn, exercises)
    finally:
        conn.close()

if __name__ == "__main__":
    main()