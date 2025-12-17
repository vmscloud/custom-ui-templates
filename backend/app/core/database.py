"""
데이터베이스 연결 관리
psycopg2를 사용한 직접 쿼리 방식
"""

from contextlib import contextmanager
from typing import Any, Generator

from app.core.config import settings
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

# Connection pool 생성
connection_pool = pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=settings.DATABASE_URL,
)


@contextmanager
def get_connection() -> Generator[Any, None, None]:
    """
    데이터베이스 연결을 가져옵니다.

    Usage:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM table")
                results = cur.fetchall()
    """
    conn = connection_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        connection_pool.putconn(conn)


def execute_query(query: str, params: tuple = None) -> list[dict]:
    """
    SELECT 쿼리를 실행하고 결과를 딕셔너리 리스트로 반환합니다.

    Args:
        query: SQL 쿼리 문자열
        params: 쿼리 파라미터 튜플

    Returns:
        결과 딕셔너리 리스트
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            results = cur.fetchall()
            return [dict(row) for row in results]
