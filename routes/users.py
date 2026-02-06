from fastapi import APIRouter, Query, Request
from database import get_connection, release_connection
from modals.users import UpdateEquipmentsRequest, UpdateExperienceRequest, UpdateGoalRequest

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/{userId}/equipments")
def get_user_equipments(userId: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                eq.id,
                eq.equipment,
                CASE 
                    WHEN u.unavailable_equipment_ids IS NULL THEN true
                    WHEN eq.id = ANY(u.unavailable_equipment_ids) THEN false
                    ELSE true
                END as checked
            FROM equipments eq
            LEFT JOIN users u ON u.id = %s
            ORDER BY eq.equipment;
        """, (userId,))
        
        equipments = cur.fetchall()
        cur.close()
    finally:
        release_connection(conn)

    return {
        "success": True,
        "data": equipments
    }


@router.put("/{userId}/equipment-preferences")
def update_user_equipments(userId: int, request:  UpdateEquipmentsRequest):
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Upsert: insert if user doesn't exist, update if they do
        cur.execute("""
            INSERT INTO users (id, unavailable_equipment_ids)
            VALUES (%s, %s)
            ON CONFLICT (id) 
            DO UPDATE SET unavailable_equipment_ids = EXCLUDED.unavailable_equipment_ids;
        """, (userId, request.unavailableEquipmentIds))
        conn.commit()
        cur.close()
    finally:
        release_connection(conn)

    return {
        "success": True,
        "message": "Equipment preferences updated successfully"}


@router.put("/{userId}/goals")
def update_user_goal(userId: int, request:  UpdateGoalRequest):
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Upsert: insert if user doesn't exist, update if they do
        cur.execute("""
            INSERT INTO users (id, goal_id)
            VALUES (%s, %s)
            ON CONFLICT (id) 
            DO UPDATE SET goal_id = EXCLUDED.goal_id;
        """, (userId, request.id))
        conn.commit()
        cur.close()
    finally:
        release_connection(conn)

    return {
        "success": True,
        "message": "Experience level updated successfully"
        }

@router.put("/{userId}/experience-level")
def update_user_experience_level(userId: int, request:  UpdateExperienceRequest):
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Upsert: insert if user doesn't exist, update if they do
        cur.execute("""
            INSERT INTO users (id, experience_level)
            VALUES (%s, %s)
            ON CONFLICT (id) 
            DO UPDATE SET experience_level = EXCLUDED.experience_level;
        """, (userId, request.experienceLevel))
        conn.commit()
        cur.close()
    finally:
        release_connection(conn)

    return {
        "success": True,
        "message": "Experience level updated successfully"
        }

@router.get("/{userId}/experience-level")
def get_user_experience_level(userId: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT experience_level
                from users u where id = %s;
        """, (userId,))
        
        result  = cur.fetchone()
        cur.close()
    finally:
        release_connection(conn)

    if not result:
        return {
            "success": False,
            "message": "User not found",
            "data": None
        }

    return {
        "success": True,
        "data": {
            "experienceLevel": result["experience_level"]
        }
    }



@router.get("/{userId}/goals")
def get_user_goals(userId:int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
             SELECT 
                g.id,
                g.title,
				g.description,
                CASE 
                    WHEN u.goal_id=g.id Then true
                    ELSE false
                END as checked
            FROM goals g
            left JOIN users u ON u.id = %s order by g.id;
        """, (userId,))
        
        goals = cur.fetchall()
        cur.close()
    finally:
        release_connection(conn)

    return {
        "success": True,
        "data": goals
    }
