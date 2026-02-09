from fastapi import APIRouter, HTTPException
from database import get_connection, release_connection
from constants.splits import split_to_target_muscles
from mappers.exercise_mapper import map_exercises
import random


router = APIRouter(prefix="/api/v1/workouts", tags=["workouts"])

@router.get("/{userId}/{workout_split}")
def get_all_equipments(userId:int, workout_split:str):
    # Validate workout_split exists
    if workout_split =='custom':
         return {
        "success": True,
        "data": {
            "workout_split": workout_split,
            "exercises": []
        }
    }

    if workout_split not in split_to_target_muscles:
        raise HTTPException(status_code=400, detail=f"Invalid workout split: {workout_split}")
    target_muscles = split_to_target_muscles[workout_split]
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Get user's excluded equipment IDs
        # Build the workout: 2 random exercises per target muscle
        all_exercises = []
    
        for muscle in target_muscles:
                # Exclude exercises that use unavailable equipment
            cur.execute("""
                        SELECT e.*, eq.* FROM exercises e
                            JOIN equipments eq ON e.equipment_id = eq.id
                            LEFT JOIN users u ON u.id = %s
                                WHERE NOT (eq.id = ANY (u.unavailable_equipment_ids)) 
                                AND %s=ANY(target_muscles);
            """, (userId,muscle,))
            
            exercises = cur.fetchall()
            
            # Randomly select 2 exercises (or fewer if not enough available)
            selected = random.sample(exercises, min(2, len(exercises))) if exercises else []
            
            all_exercises.extend(selected)
        
        cur.close()
    finally:
        release_connection(conn)

    return {
        "success": True,
        "data": {
            "workout_split": workout_split,
            "exercises": map_exercises(all_exercises)
        }
    }
