"""
데이터베이스 연결 관리
Trino를 사용한 쿼리 방식
"""

import asyncio
from contextlib import contextmanager
from typing import Any, Generator

from app.core.config import settings
from trino.dbapi import connect


def _get_connection():
    """Trino 연결을 생성합니다."""
    return connect(
        host=settings.TRINO_HOST,
        port=settings.TRINO_PORT,
        user=settings.TRINO_USER,
        catalog=settings.TRINO_CATALOG,
        schema=settings.TRINO_SCHEMA,
        http_scheme="http",
        request_timeout=settings.QUERY_TIMEOUT_SECONDS,
    )


@contextmanager
def get_connection() -> Generator[Any, None, None]:
    """
    데이터베이스 연결을 가져옵니다.

    Usage:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM table")
            results = cur.fetchall()
    """
    conn = _get_connection()
    try:
        yield conn
    finally:
        conn.close()


def execute_query(query: str, params: tuple = None) -> list[dict]:
    """
    SELECT 쿼리를 실행하고 결과를 딕셔너리 리스트로 반환합니다.
    (동기 — def 엔드포인트에서 호출하거나, async 엔드포인트에서는 execute_query_async 사용)

    Args:
        query: SQL 쿼리 문자열
        params: 쿼리 파라미터 튜플

    Returns:
        결과 딕셔너리 리스트
    """
    with get_connection() as conn:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        return [dict(zip(columns, row)) for row in rows]


def execute_write(query: str, params: tuple = None) -> int:
    """
    DML(INSERT/UPDATE/DELETE) 쿼리를 실행하고 영향받은 행 수를 반환합니다.

    Args:
        query: SQL 쿼리 문자열
        params: 쿼리 파라미터 튜플

    Returns:
        영향받은 행 수 (rowcount)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.rowcount


async def execute_query_async(query: str, params: tuple = None) -> list[dict]:
    """
    SELECT 쿼리를 비동기로 실행합니다.
    동기 Trino 호출을 스레드풀에서 실행하여 event loop 블로킹을 방지합니다.
    """
    return await asyncio.to_thread(execute_query, query, params)
