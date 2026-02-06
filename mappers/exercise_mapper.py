def map_exercise(row: dict) -> dict:
    return {
        "exerciseId": row["exercise_id"],
        "name": row["name"],
        "gifUrl": row["gif_url"],
        "targetMuscles": row["target_muscles"],
        "bodyParts": row["body_parts"],
        "equipments": row["equipment"],
        "secondaryMuscles": row["secondary_muscles"],
        "instructions": row["instructions"],
    }


def map_exercises(rows: list[dict]) -> list[dict]:
    return [map_exercise(row) for row in rows]