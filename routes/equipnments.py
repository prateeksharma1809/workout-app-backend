from fastapi import APIRouter, Query, Request
from database import get_connection, release_connection
from utils.pagination import PaginationMeta, build_response

router = APIRouter(prefix="/api/v1", tags=["equipments"])

@router.get("/equipments")
def get_all_equipments(request: Request):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT *
            FROM equipments
            ORDER BY id;
        """)
        rows = cur.fetchall()
        cur.close()
    finally:
        release_connection(conn)

    return {
        "success": True,
        "data": [{"id": row["id"], "equipment": row["equipment"]} for row in rows],
    }


@router.get("/goals")
def get_all_goals():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, description
            FROM goals
            ORDER BY id;
        """)
        
        goals = cur.fetchall()
        cur.close()
    finally:
        release_connection(conn)

    return {
        "success": True,
        "data": goals
    }
