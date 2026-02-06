from fastapi import APIRouter, Query, Request
from database import get_connection, get_total_count, release_connection
from mappers.exercise_mapper import map_exercises
from utils.pagination import PaginationMeta, build_response

router = APIRouter(prefix="/api/v1", tags=["exercises"])


@router.get("/exercises")
def get_exercises(
    request: Request,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    conn = get_connection()
    try:
        cur = conn.cursor()
        total = get_total_count(conn)

        cur.execute(
            "SELECT * FROM exercises e join equipments eq on e.equipment_id = eq.id ORDER BY exercise_id LIMIT %s OFFSET %s;",
            (limit, offset),
        )
        data = cur.fetchall()
        cur.close()
        cur.close()
    finally:
        release_connection(conn)

    meta = PaginationMeta(
        total=total,
        offset=offset,
        limit=limit,
        request=request,
    )

    return build_response(map_exercises(data), meta)


@router.get("/exercises/search")
def search_exercises(
    request: Request,
    q: str = Query(..., min_length=1),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    conn = get_connection()
    try:
        cur = conn.cursor()
        search_query = f"%{q}%"
        cur.execute(
            """
            SELECT *
            FROM exercises e join equipments eq on e.equipment_id = eq.id
            WHERE 
                name ILIKE %s OR
                %s = ANY(target_muscles) OR
                %s = ANY(body_parts) OR
                %s ILIKE equipment OR
                %s = ANY(secondary_muscles)
            ORDER BY exercise_id
            LIMIT %s OFFSET %s;
            """,
            (search_query, q, q, q, q, limit, offset),
        )
        data = cur.fetchall()
        total = get_total_count(conn)
        cur.close()
    finally:
        release_connection(conn)

    meta = PaginationMeta(
        total=total,
        offset=offset,
        limit=limit,
        request=request,
    )

    return build_response(map_exercises(data), meta)