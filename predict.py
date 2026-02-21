import joblib

from database import get_connection, get_total_count, release_connection

loaded_model = joblib.load("modals/exercise_level_model.pkl")

# # Test prediction
# sample = ["push up chest"]
# prediction = loaded_model.predict(sample)

# print("Predicted level:", prediction)

def map_exercise(row: dict[str, str]) -> str:
    return f"{row['name']} {row['target_muscles']} {row['equipment']}"
       


def get_data() -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT exercise_id, name, target_muscles,equipment  FROM exercises e join equipments eq on e.equipment_id = eq.id ORDER BY exercise_id;",
        )
        data = cur.fetchall()
        cur.close()
        cur.close()
    finally:
        release_connection(conn)
    samples= {}
    for row in data:
        samples[map_exercise(row)] =row["exercise_id"]
         
    return samples


def predict(samples):
    predictions = loaded_model.predict(samples)
    return predictions
    
def update_experience_levels(predictions_map):
    conn = get_connection()
    try:
        cur = conn.cursor()
        update_data = [
            (int(level), exercise_id)
            for exercise_id, level in predictions_map.items()
        ]
        cur.executemany(
            """
            UPDATE exercises
            SET experience_level = %s
            WHERE exercise_id = %s;
            """,
            update_data
        )

        conn.commit()
        cur.close()
    finally:
        release_connection(conn)

if __name__=="__main__":
    data = get_data()
    texts = list(data.keys())
    predictions = predict(texts)
    predictions_map = {
        data[text]: pred
        for text, pred in zip(texts, predictions)
    }

    update_experience_levels(predictions_map)

    print("Database updated successfully.")