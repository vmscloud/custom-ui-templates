"""
Query Executor Adapter - Simple Library

외부 서비스에서 Query Executor API를 호출하기 위한 클라이언트

Usage:
    from query_executor_adapter import QueryExecutorAdapter

    client = QueryExecutorAdapter(
        base_url="http://localhost:18000",
        db_alias="com"  # Query Database alias (저장된 쿼리를 조회할 DB)
    )

    # 1. 저장된 쿼리 실행 (db_alias로 지정된 DB에서 쿼리 조회)
    result = await client.execute_query(
        project_id="dev",
        query_id="get_peg_info",
        parameters={"project_id": "EED70012"}
    )

    # 2. 직접 SQL 실행 (Trino 단일 연결 사용)
    result = await client.execute_direct_query(
        project_id="dev",
        query="SELECT * FROM out_peg_info LIMIT 5",
        catalog="iceberg",
        schema="dev"
    )
"""

from __future__ import annotations

import json
import traceback
from typing import TYPE_CHECKING, Any

import httpx
import orjson

# PyLogger 사용 시도, 없으면 표준 logging 사용
try:
    from pylogger.logger import logger_instance

    def _log(level: str, category: str, message: str) -> None:
        logger_instance.send_log(level=level, category=category, message=message)

except ImportError:
    import logging

    _std_logger = logging.getLogger("QueryExecutorAdapter")

    def _log(level: str, category: str, message: str) -> None:
        log_func = getattr(_std_logger, level, _std_logger.info)
        log_func(f"[{category}] {message}")


if TYPE_CHECKING:
    from fastapi import Request


class QueryExecutorAdapter:
    """
    Query Executor API 클라이언트

    Args:
        base_url: Query Executor API URL (예: "http://localhost:18000")
        db_alias: Query Database 별칭 - 저장된 쿼리를 조회할 DB (예: "com")
                  execute_query, execute_query_columnar에서 사용됨
                  execute_direct_query는 Trino 단일 연결을 사용하므로 db_alias 불필요
        timeout: 타임아웃 초 (기본: 60.0)
    """

    def __init__(
        self,
        base_url: str,
        db_alias: str = "com",
        owner_id: str = "aps",
        timeout: float = 60.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.db_alias = db_alias  # Query Database alias (저장된 쿼리 조회용)
        self.owner_id = owner_id  # Query Owner ID
        self.timeout = timeout

        # HTTP 클라이언트 풀링 (연결 재사용)
        self._http_client: httpx.AsyncClient | None = None
        self._limits = httpx.Limits(max_connections=50, max_keepalive_connections=25)

    async def _get_http_client(self) -> httpx.AsyncClient:
        """재사용 가능한 HTTP 클라이언트 반환 (Lazy initialization)"""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=self._limits,
            )
        return self._http_client

    async def close(self) -> None:
        """HTTP 클라이언트 리소스 정리"""
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    def _build_headers(
        self,
        request: Request | None,
        custom_headers: dict[str, str] | None,
    ) -> dict[str, str]:
        """
        HTTP 요청 헤더 구성

        C# PropertyType과 동일한 헤더 이름을 사용합니다:
        - TraceID: 요청 추적 ID (서버에서 생성, 있으면 전달)
        - UserId: 사용자 ID
        - Tenant-Id: 테넌트 ID
        - Tenant-Name: 테넌트 이름
        - projectID: 프로젝트 ID
        - Project-Name: 프로젝트 이름

        TraceID 생성 정책:
        - Adapter는 TraceID를 생성하지 않음
        - 기존 TraceID가 있으면 전달 (API Gateway 경유 시)
        - 없으면 QueryExecutor Middleware에서 순차적 ID 생성

        우선순위: custom_headers > request headers

        Args:
            request: FastAPI Request 객체 (선택)
            custom_headers: 커스텀 헤더 딕셔너리 (선택)

        Returns:
            HTTP 요청에 사용할 헤더 딕셔너리
        """
        result: dict[str, str] = {}

        # 1단계: Request에서 헤더 추출 (C# PropertyType 기준)
        if request is not None:
            # 헤더 이름이 대소문자 무관하게 조회될 수 있으므로 다양한 형식 지원
            def get_header(name: str, *alternatives: str) -> str:
                value = request.headers.get(name, "")
                if not value:
                    for alt in alternatives:
                        value = request.headers.get(alt, "")
                        if value:
                            break
                return value

            result = {
                # C# PropertyType.TraceID = "TraceID"
                "TraceID": get_header("TraceID"),
                # C# PropertyType.UserID = "UserId"
                "UserId": get_header("UserId", "UserID", "userid"),
                # C# PropertyType.TenantID = "Tenant-Id"
                "Tenant-Id": get_header("Tenant-Id", "tenant-id", "TenantID"),
                # C# PropertyType.TenantName = "Tenant-Name"
                "Tenant-Name": get_header("Tenant-Name", "tenant-name", "TenantName"),
                # C# PropertyType.ProjectID = "projectID"
                "projectID": get_header("projectID", "project-id", "ProjectID"),
                # C# PropertyType.ProjectName = "Project-Name"
                "Project-Name": get_header(
                    "Project-Name", "project-name", "ProjectName"
                ),
                # User-Agent (표준 헤더)
                "User-Agent": get_header("User-Agent"),
            }

        # 2단계: 커스텀 헤더로 오버라이드
        if custom_headers:
            result.update(custom_headers)

        # 3단계: 빈 값 제거 (TraceID 없으면 서버에서 생성)
        return {k: v for k, v in result.items() if v}

    def _build_count_query(self, original_query: str) -> str:
        """
        원본 SELECT 쿼리를 COUNT(*) 쿼리로 변환

        서브쿼리로 감싸서 안전하게 COUNT를 수행합니다.

        Args:
            original_query: 원본 SQL 쿼리

        Returns:
            COUNT(*) 쿼리

        Example:
            원본: SELECT * FROM table WHERE id > 10
            변환: SELECT COUNT(*) as total FROM (SELECT * FROM table WHERE id > 10) as subquery
        """
        # 쿼리를 서브쿼리로 감싸서 COUNT 수행 (가장 안전한 방법)
        count_query = (
            f"SELECT COUNT(*) as total FROM ({original_query.rstrip(';')}) as subquery"
        )
        return count_query

    async def _get_total_count_direct(
        self,
        project_id: str,
        query: str,
        catalog: str,
        schema: str,
        parameters: dict[str, Any] | None = None,
    ) -> int | None:
        """
        직접 SQL 쿼리의 총 데이터 개수를 조회

        Args:
            project_id: 프로젝트 ID
            query: 원본 SQL 쿼리
            catalog: Trino 카탈로그
            schema: Trino 스키마
            parameters: 쿼리 파라미터

        Returns:
            총 데이터 개수 (실패 시 None)
        """
        try:
            count_query = self._build_count_query(query)
            endpoint = f"{self.base_url}/api/module/query-executor/{project_id}/query/execute-stream"

            payload = {
                "query": count_query,
                "catalog": catalog,
                "tenant_id": schema,
                "parameters": parameters or {},
                "page": 1,
                "limit": 1,
                "is_write": False,
            }

            result = await self._execute_request(endpoint, payload, columnar=False)

            if result.get("success") and result.get("row"):
                first_row = result["row"][0]
                # COUNT(*) as total 결과 추출
                if "total" in first_row:
                    return int(first_row["total"])
                # 컬럼 이름이 다를 수 있으므로 첫 번째 값 사용
                elif first_row:
                    return int(list(first_row.values())[0])

        except Exception:
            # COUNT 쿼리 실행 실패 시 None 반환 (원본 쿼리 실행은 계속 진행)
            pass

        return None

    async def _get_total_count_by_key(
        self,
        project_id: str,
        query_id: str,
        parameters: dict[str, Any] | None = None,
    ) -> int | None:
        """
        저장된 쿼리의 총 데이터 개수를 조회

        먼저 저장된 쿼리를 조회한 후, COUNT(*) 쿼리로 변환하여 실행합니다.

        Args:
            project_id: 프로젝트 ID
            query_id: 저장된 쿼리 ID
            parameters: 쿼리 파라미터

        Returns:
            총 데이터 개수 (실패 시 None)
        """
        try:
            # 1. 저장된 쿼리 정보 조회
            stored_query = await self.get_stored_query(project_id, query_id)

            if not stored_query.get("success") or not stored_query.get("data"):
                return None

            query_data = stored_query["data"]

            original_query = query_data.get("query")
            catalog = query_data.get("catalog", "iceberg")
            schema = query_data.get("schema", "mzc_com")

            if not original_query:
                return None

            # 2. COUNT 쿼리로 변환 및 실행
            return await self._get_total_count_direct(
                project_id=project_id,
                query=original_query,
                catalog=catalog,
                schema=schema,
                parameters=parameters,
            )

        except Exception:
            # 저장된 쿼리 조회 실패 시 None 반환
            pass

        return None

    def _parse_response(self, content: bytes) -> dict[str, Any]:
        """
        NDJSON 응답 파싱 및 데이터 집계 (Single-pass Implementation)

        스트리밍 응답을 한 줄씩 순회하며 상태(컬럼, 데이터, 업데이트 정보)를 수집합니다.
        초기 상태(QUEUED)나 통계만 있는 페이지는 자연스럽게 스킵됩니다.

        Returns:
            dict with keys:
                - success: bool
                - rowcount: int
                - columns: list[str]
                - row: list[dict]
                - has_next: bool (다음 페이지 존재 여부)
                - total_count: int (서버에서 제공한 경우)
                - update_type: str (DML인 경우)
                - update_count: int (DML인 경우)
        """
        lines = content.splitlines()
        columns: list[str] = []
        rows_out: list[dict[str, Any]] = []
        update_type: str | None = None
        update_count: int | None = None
        has_next: bool = False  # 다음 페이지 존재 여부
        total_count: int | None = None  # 서버에서 제공한 총 개수

        for line in lines:
            if not line:
                continue
            try:
                # orjson: Rust 기반으로 GIL 해제, 3-5배 빠른 JSON 파싱
                page = orjson.loads(line)
            except orjson.JSONDecodeError:
                continue

            if not isinstance(page, dict):
                continue

            # 0. total_count 체크 (서버에서 첫 줄로 전송)
            if "total_count" in page and len(page) == 1:
                total_count = int(page["total_count"])
                continue

            # 1. 에러 체크
            error_result = self._check_error_page(page)
            if error_result:
                return error_result

            # 2. 업데이트 정보 체크 (DML)
            u_type, u_count = self._extract_update_info(page)
            if u_type:
                update_type = u_type
            if u_count is not None:
                update_count = u_count

            # 3. 컬럼 정보 업데이트
            # (이미 컬럼이 있어도, 최신 페이지에 정보가 있다면 갱신/확인)
            new_cols = self._extract_columns(page)
            if new_cols:
                columns = new_cols

            # 4. 데이터 추출 및 매핑
            # (현재 확보된 컬럼 정보를 사용하여 매핑)
            self._process_data_rows(page, columns, rows_out)

            # 5. nextUri 체크 (마지막 페이지에서 업데이트됨)
            # nextUri가 있으면 다음 페이지가 존재함
            if page.get("nextUri"):
                has_next = True
            elif "nextUri" in page and not page["nextUri"]:
                has_next = False

        # 최종 결과 구성
        result = {
            "success": True,
            "rowcount": len(rows_out),
            "columns": columns,
            "row": rows_out,
            "has_next": has_next,  # 다음 데이터 존재 여부
        }

        if total_count is not None:
            result["total_count"] = total_count
        if update_type is not None:
            result["update_type"] = update_type
        if update_count is not None:
            result["update_count"] = update_count
            # rowcount가 0이고 update_count가 있으면 rowcount 보정 (선택 사항)
            if not rows_out and update_count > 0:
                result["rowcount"] = update_count

        return result

    def _parse_response_columnar(self, content: bytes) -> dict[str, Any]:
        """
        NDJSON 응답 파싱 - 컬럼 기반 (Column-oriented)

        Returns:
            {
                "success": True,
                "columns": ["id", "name"],
                "data": {
                    "id": [1, 2, ...],
                    "name": ["A", "B", ...]
                },
                "rowcount": 2,
                "has_next": bool (다음 페이지 존재 여부),
                "total_count": int (서버에서 제공한 경우)
            }
        """
        lines = content.splitlines()
        columns: list[str] = []
        # key: column_name, value: list of values
        data_cols: dict[str, list[Any]] = {}
        row_count = 0
        has_next: bool = False  # 다음 페이지 존재 여부
        total_count: int | None = None  # 서버에서 제공한 총 개수

        update_type: str | None = None
        update_count: int | None = None

        for line in lines:
            if not line:
                continue
            try:
                # orjson: Rust 기반으로 GIL 해제, 3-5배 빠른 JSON 파싱
                page = orjson.loads(line)
            except orjson.JSONDecodeError:
                continue

            if not isinstance(page, dict):
                continue

            # 0. total_count 체크 (서버에서 첫 줄로 전송)
            if "total_count" in page and len(page) == 1:
                total_count = int(page["total_count"])
                continue

            # 1. 에러 체크
            error_result = self._check_error_page(page)
            if error_result:
                return error_result

            # 2. 업데이트 정보 체크
            u_type, u_count = self._extract_update_info(page)
            if u_type:
                update_type = u_type
            if u_count is not None:
                update_count = u_count

            # 3. 컬럼 정보 업데이트
            new_cols = self._extract_columns(page)
            if new_cols:
                columns = new_cols
                # 새로운 컬럼이 발견되면 데이터 저장소 초기화 (또는 병합)
                for col in columns:
                    if col not in data_cols:
                        data_cols[col] = []

            # 4. 데이터 추출 (컬럼별 저장)
            page_data = page.get("data")
            if isinstance(page_data, list) and columns:
                for row in page_data:
                    if isinstance(row, list):
                        row_count += 1
                        # 각 컬럼에 값 추가
                        for i, col in enumerate(columns):
                            if i < len(row):
                                data_cols[col].append(row[i])
                            else:
                                data_cols[col].append(None)

            # 5. nextUri 체크
            if page.get("nextUri"):
                has_next = True
            elif "nextUri" in page and not page["nextUri"]:
                has_next = False

        result = {
            "success": True,
            "rowcount": row_count,
            "columns": columns,
            "data": data_cols,
            "has_next": has_next,  # 다음 데이터 존재 여부
        }

        if total_count is not None:
            result["total_count"] = total_count
        if update_type is not None:
            result["update_type"] = update_type
        if update_count is not None:
            result["update_count"] = update_count
            if row_count == 0 and update_count > 0:
                result["rowcount"] = update_count

        return result

    def _check_error_page(self, page: dict[str, Any]) -> dict[str, Any] | None:
        """페이지 내 에러 정보 확인"""
        if page.get("error"):
            err = page.get("error", {})
            reason = err.get("message") or err.get("errorName") or "Engine error"
            return {
                "success": False,
                "message": str(reason),
                "data": {"db_alias": self.db_alias, "error": err},
            }
        return None

    def _extract_update_info(
        self, page: dict[str, Any]
    ) -> tuple[str | None, int | None]:
        """DML 업데이트 정보 추출"""
        return page.get("updateType"), page.get("updateCount")

    def _extract_columns(self, page: dict[str, Any]) -> list[str]:
        """페이지에서 컬럼 이름 목록 추출"""
        cols_info = page.get("columns")
        if isinstance(cols_info, list) and cols_info:
            extracted = []
            for c in cols_info:
                if isinstance(c, dict) and isinstance(c.get("name"), str):
                    extracted.append(c["name"])
            return extracted
        return []

    def _process_data_rows(
        self, page: dict[str, Any], columns: list[str], rows_out: list[dict[str, Any]]
    ):
        """페이지 데이터를 추출하여 결과 리스트에 추가 (컬럼 매핑 포함)"""
        data = page.get("data")
        if isinstance(data, list):
            for row in data:
                if columns and isinstance(row, list):
                    # 컬럼명과 값 매핑 (안전하게 min length 사용)
                    mapped = {
                        columns[i]: row[i] for i in range(min(len(columns), len(row)))
                    }
                    rows_out.append(mapped)
                else:
                    # 컬럼 정보가 없거나 row가 리스트가 아닌 경우 (Fallback)
                    rows_out.append(row)

    async def execute_query(
        self,
        project_id: str,
        query_id: str,
        parameters: dict[str, Any] | None = None,
        page: int = 1,
        limit: int | None = None,
        include_total_count: bool = False,
        request: Request | None = None,
        headers: dict[str, str] | None = None,
        owner_id: str | None = None,
    ) -> dict[str, Any]:
        """
        저장된 쿼리 실행 (/query/execute-by-key)

        db_alias로 지정된 Query Database에서 쿼리를 조회하여 Trino로 실행합니다.

        Args:
            project_id: 프로젝트 ID
            query_id: 저장된 쿼리 ID
            parameters: 쿼리 파라미터 (선택)
            page: 페이지 번호 (기본: 1)
            limit: 페이지당 행 수 (선택)
            include_total_count: 총 데이터 개수 포함 여부 (page=1일 때만 동작, 기본: False)
            request: FastAPI Request 객체 (선택) - 헤더 자동 추출용
            headers: 커스텀 HTTP 헤더 (선택) - 직접 지정 시 사용
            owner_id: Query Owner ID (선택) - 지정하지 않으면 인스턴스 기본값 사용

        Returns:
            dict with keys:
                - success: bool
                - rowcount: int (현재 페이지의 행 수)
                - columns: list[str]
                - row: list[dict]
                - has_next: bool (다음 페이지 존재 여부)
                - total_count: int (include_total_count=True이고 page=1일 때만)

        Examples:
            # API에서 사용 (권장)
            result = await client.execute_query(
                request=request,
                project_id="demo",
                query_id="get_users",
            )

            # Service에서 사용 (trace_id 자동 생성)
            result = await client.execute_query(
                project_id="demo",
                query_id="get_users",
            )

            # 커스텀 헤더 전달
            result = await client.execute_query(
                project_id="demo",
                query_id="get_users",
                headers={"TraceID": "custom-trace-123"},
            )

            # owner_id 오버라이드
            result = await client.execute_query(
                project_id="demo",
                query_id="get_users",
                owner_id="aps",
            )
        """
        endpoint = f"{self.base_url}/api/module/query-executor/{project_id}/query/execute-by-key"

        payload = {
            "query_id": query_id,
            "alias": self.db_alias,  # Query DB alias
            "owner_id": owner_id or self.owner_id,  # Query Owner ID (오버라이드 가능)
            "parameters": parameters or {},
            "page": page,
        }
        if limit is not None:
            payload["limit"] = limit
        # include_total_count를 서버에 전달 (page=1일 때만 서버에서 처리)
        if include_total_count:
            payload["include_total_count"] = True

        # 헤더 구성 (request > headers > 자동 생성)
        req_headers = self._build_headers(request, headers)
        result = await self._execute_request(endpoint, payload, headers=req_headers)

        # 서버에서 total_count를 응답에 포함하므로 별도 처리 불필요
        return result

    async def execute_query_columnar(
        self,
        project_id: str,
        query_id: str,
        parameters: dict[str, Any] | None = None,
        page: int = 1,
        limit: int | None = None,
        include_total_count: bool = False,
        request: Request | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        저장된 쿼리 실행 - 컬럼 기반 반환 (Pandas DataFrame 변환 최적화)

        db_alias로 지정된 Query Database에서 쿼리를 조회하여 Trino로 실행합니다.

        Args:
            project_id: 프로젝트 ID
            query_id: 저장된 쿼리 ID
            parameters: 쿼리 파라미터 (선택)
            page: 페이지 번호 (기본: 1)
            limit: 페이지당 행 수 (선택)
            include_total_count: 총 데이터 개수 포함 여부 (page=1일 때만 동작, 기본: False)
            request: FastAPI Request 객체 (선택) - 헤더 자동 추출용
            headers: 커스텀 HTTP 헤더 (선택) - 직접 지정 시 사용

        Returns:
            Dict: {
                "success": True,
                "columns": ["col1", "col2"],
                "data": { "col1": [1, 2], "col2": ["a", "b"] },
                "has_next": bool,
                "total_count": int (include_total_count=True이고 page=1일 때만)
            }
        """
        endpoint = f"{self.base_url}/api/module/query-executor/{project_id}/query/execute-by-key"

        payload = {
            "query_id": query_id,
            "alias": self.db_alias,  # Query DB alias
            "owner_id": self.owner_id,  # Query Owner ID
            "parameters": parameters or {},
            "page": page,
        }
        if limit is not None:
            payload["limit"] = limit
        # include_total_count를 서버에 전달 (page=1일 때만 서버에서 처리)
        if include_total_count:
            payload["include_total_count"] = True

        # 헤더 구성 (request > headers > 자동 생성)
        req_headers = self._build_headers(request, headers)
        result = await self._execute_request(
            endpoint, payload, columnar=True, headers=req_headers
        )

        # 서버에서 total_count를 응답에 포함하므로 별도 처리 불필요

        return result

    async def execute_direct_query(
        self,
        project_id: str,
        query: str,
        catalog: str,
        schema: str,
        parameters: dict[str, Any] | None = None,
        page: int = 1,
        limit: int | None = None,
        is_write: bool = False,
        include_total_count: bool = False,
        request: Request | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        직접 SQL 쿼리 실행 (/query/execute-stream)

        Trino 단일 연결을 사용하여 SQL을 직접 실행합니다.
        (db_alias와 무관하게 서버에 설정된 Trino로 실행)

        Args:
            project_id: 프로젝트 ID
            query: 실행할 SQL 문
            catalog: Trino 카탈로그 (예: 'iceberg')
            schema: Trino 스키마 (예: 'dev')
            parameters: 쿼리 파라미터 (선택)
            page: 페이지 번호 (기본: 1)
            limit: 페이지당 행 수 (선택)
            is_write: WRITE 쿼리 여부 (INSERT/UPDATE/DELETE/DDL 등)
            include_total_count: 총 데이터 개수 포함 여부 (page=1일 때만 동작, 기본: False)
            request: FastAPI Request 객체 (선택) - 헤더 자동 추출용
            headers: 커스텀 HTTP 헤더 (선택) - 직접 지정 시 사용

        Returns:
            dict with keys:
                - success: bool
                - rowcount: int
                - columns: list[str]
                - row: list[dict]
                - has_next: bool
                - total_count: int (include_total_count=True이고 page=1일 때만)
        """
        endpoint = f"{self.base_url}/api/module/query-executor/{project_id}/query/execute-stream"

        payload = {
            "query": query,
            "catalog": catalog,
            "tenant_id": schema,  # API에서는 schema를 tenant_id로 매핑
            "parameters": parameters or {},
            "page": page,
            "is_write": is_write,
        }
        if limit is not None:
            payload["limit"] = limit

        # 헤더 구성 (request > headers > 자동 생성)
        req_headers = self._build_headers(request, headers)
        result = await self._execute_request(endpoint, payload, headers=req_headers)

        # 첫 페이지이고 total_count 요청 시, 별도로 COUNT 쿼리 실행
        # WRITE 쿼리인 경우 COUNT 불가
        if include_total_count and page == 1 and not is_write and result.get("success"):
            total_count = await self._get_total_count_direct(
                project_id=project_id,
                query=query,
                catalog=catalog,
                schema=schema,
                parameters=parameters,
            )
            if total_count is not None:
                result["total_count"] = total_count

        return result

    async def execute_direct_query_columnar(
        self,
        project_id: str,
        query: str,
        catalog: str,
        schema: str,
        parameters: dict[str, Any] | None = None,
        page: int = 1,
        limit: int | None = None,
        is_write: bool = False,
        include_total_count: bool = False,
        request: Request | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        직접 SQL 쿼리 실행 - 컬럼 기반 반환 (Pandas DataFrame 변환 최적화)

        Trino 단일 연결을 사용하여 SQL을 직접 실행합니다.

        Args:
            project_id: 프로젝트 ID
            query: 실행할 SQL 문
            catalog: Trino 카탈로그 (예: 'iceberg')
            schema: Trino 스키마 (예: 'dev')
            parameters: 쿼리 파라미터 (선택)
            page: 페이지 번호 (기본: 1)
            limit: 페이지당 행 수 (선택)
            is_write: WRITE 쿼리 여부 (INSERT/UPDATE/DELETE/DDL 등)
            include_total_count: 총 데이터 개수 포함 여부 (page=1일 때만 동작, 기본: False)
            request: FastAPI Request 객체 (선택) - 헤더 자동 추출용
            headers: 커스텀 HTTP 헤더 (선택) - 직접 지정 시 사용

        Returns:
            Dict: {
                "success": True,
                "columns": ["col1", "col2"],
                "data": { "col1": [1, 2], "col2": ["a", "b"] },
                "has_next": bool,
                "total_count": int (include_total_count=True이고 page=1일 때만)
            }
        """
        endpoint = f"{self.base_url}/api/module/query-executor/{project_id}/query/execute-stream"

        payload = {
            "query": query,
            "catalog": catalog,
            "tenant_id": schema,
            "parameters": parameters or {},
            "page": page,
            "is_write": is_write,
        }
        if limit is not None:
            payload["limit"] = limit

        # 헤더 구성 (request > headers > 자동 생성)
        req_headers = self._build_headers(request, headers)
        result = await self._execute_request(
            endpoint, payload, columnar=True, headers=req_headers
        )

        # 첫 페이지이고 total_count 요청 시, 별도로 COUNT 쿼리 실행
        # WRITE 쿼리인 경우 COUNT 불가
        if include_total_count and page == 1 and not is_write and result.get("success"):
            total_count = await self._get_total_count_direct(
                project_id=project_id,
                query=query,
                catalog=catalog,
                schema=schema,
                parameters=parameters,
            )
            if total_count is not None:
                result["total_count"] = total_count

        return result

    async def _execute_request(
        self,
        endpoint: str,
        payload: dict[str, Any],
        columnar: bool = False,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """API 요청 공통 처리

        Args:
            endpoint: API 엔드포인트 URL
            payload: 요청 페이로드
            columnar: 컬럼 기반 응답 여부
            headers: HTTP 요청 헤더 (TraceID, UserID 등)
        """
        # TraceID 추출 (로깅용)
        trace_id = (headers or {}).get("TraceID", "")

        # 요청 정보 로깅 (디버그)
        _log(
            level="debug",
            category="service",
            message=f"[Adapter] Request | trace_id={trace_id} | endpoint={endpoint} | payload={json.dumps(payload, ensure_ascii=False)[:500]}",
        )

        try:
            http_client = await self._get_http_client()
            response = await http_client.post(
                endpoint, json=payload, headers=headers
            )

            if response.status_code != 200:
                # HTTP 오류 로깅
                _log(
                    level="error",
                    category="service",
                    message=f"[Adapter] HTTP Error | trace_id={trace_id} | endpoint={endpoint} | status={response.status_code} | response={response.text[:500]}",
                )
                return {
                    "success": False,
                    "message": f"HTTP {response.status_code}",
                    "data": {"db_alias": self.db_alias, "error": response.text},
                }

            # 성공 로깅 (디버그)
            _log(
                level="debug",
                category="service",
                message=f"[Adapter] Response OK | trace_id={trace_id} | endpoint={endpoint} | size={len(response.content)} bytes",
            )

            if columnar:
                return self._parse_response_columnar(response.content)
            else:
                return self._parse_response(response.content)

        except httpx.TimeoutException:
            _log(
                level="error",
                category="service",
                message=f"[Adapter] Timeout | trace_id={trace_id} | endpoint={endpoint} | timeout={self.timeout}s",
            )
            return {
                "success": False,
                "message": "Request timeout",
                "data": {"db_alias": self.db_alias, "error": {"timeout": self.timeout}},
            }
        except httpx.NetworkError as e:
            _log(
                level="error",
                category="service",
                message=f"[Adapter] Network Error | trace_id={trace_id} | endpoint={endpoint} | error={e}",
            )
            return {
                "success": False,
                "message": f"Network error: {e}",
                "data": {"db_alias": self.db_alias, "error": str(e)},
            }
        except Exception as e:
            _log(
                level="error",
                category="service",
                message=f"[Adapter] Exception | trace_id={trace_id} | endpoint={endpoint} | error={e} | traceback={traceback.format_exc()}",
            )
            return {
                "success": False,
                "message": str(e),
                "data": {"db_alias": self.db_alias, "reason": str(e)},
            }

    # ========== Stored Query CRUD API (비활성화됨) ==========
    # NOTE: stored_query_api.py가 주석 처리되어 있어 CRUD API 비활성화
    # 필요시 QueryExecutor의 stored_query_api.py 활성화 후 아래 주석 해제

    # async def create_stored_query(
    #     self,
    #     project_id: str,
    #     query_id: str,
    #     query_name: str,
    #     query_content: str,
    #     catalog_id: str = "iceberg",
    #     schema_id: str = "mzc_com",
    #     query_param: dict[str, Any] | None = None,
    #     description: str | None = None,
    #     query_type: str = "SELECT",
    # ) -> dict[str, Any]:
    #     """
    #     저장된 쿼리 생성 (POST /stored-query)
    #     """
    #     endpoint = (
    #         f"{self.base_url}/api/module/query-executor/{project_id}/stored-query"
    #     )
    #     payload = {
    #         "query_id": query_id,
    #         "query_name": query_name,
    #         "query_content": query_content,
    #         "catalog_id": catalog_id,
    #         "schema_id": schema_id,
    #         "query_type": query_type,
    #     }
    #     if query_param is not None:
    #         payload["query_param"] = query_param
    #     if description is not None:
    #         payload["description"] = description
    #     params = {"alias": self.db_alias}
    #     return await self._execute_crud_request(
    #         "POST", endpoint, params=params, payload=payload
    #     )

    # async def list_stored_queries(
    #     self,
    #     project_id: str,
    # ) -> dict[str, Any]:
    #     """
    #     프로젝트의 저장된 쿼리 목록 조회 (GET /stored-query)
    #     """
    #     endpoint = (
    #         f"{self.base_url}/api/module/query-executor/{project_id}/stored-query"
    #     )
    #     params = {"alias": self.db_alias}
    #     return await self._execute_crud_request("GET", endpoint, params=params)

    # async def get_stored_query(
    #     self,
    #     project_id: str,
    #     query_id: str,
    # ) -> dict[str, Any]:
    #     """
    #     저장된 쿼리 단일 조회 (GET /stored-query/{query_id})
    #     """
    #     endpoint = f"{self.base_url}/api/module/query-executor/{project_id}/stored-query/{query_id}"
    #     params = {"alias": self.db_alias}
    #     return await self._execute_crud_request("GET", endpoint, params=params)

    # async def update_stored_query(
    #     self,
    #     project_id: str,
    #     query_id: str,
    #     query_name: str | None = None,
    #     query_content: str | None = None,
    #     catalog_id: str | None = None,
    #     schema_id: str | None = None,
    #     query_param: dict[str, Any] | None = None,
    #     description: str | None = None,
    #     query_type: str | None = None,
    # ) -> dict[str, Any]:
    #     """
    #     저장된 쿼리 수정 (PUT /stored-query/{query_id})
    #     """
    #     endpoint = f"{self.base_url}/api/module/query-executor/{project_id}/stored-query/{query_id}"
    #     params = {"alias": self.db_alias}
    #     payload = {}
    #     if query_name is not None:
    #         payload["query_name"] = query_name
    #     if query_content is not None:
    #         payload["query_content"] = query_content
    #     if catalog_id is not None:
    #         payload["catalog_id"] = catalog_id
    #     if schema_id is not None:
    #         payload["schema_id"] = schema_id
    #     if query_param is not None:
    #         payload["query_param"] = query_param
    #     if description is not None:
    #         payload["description"] = description
    #     if query_type is not None:
    #         payload["query_type"] = query_type
    #     return await self._execute_crud_request(
    #         "PUT", endpoint, params=params, payload=payload
    #     )

    # async def delete_stored_query(
    #     self,
    #     project_id: str,
    #     query_id: str,
    # ) -> dict[str, Any]:
    #     """
    #     저장된 쿼리 삭제 (DELETE /stored-query/{query_id})
    #     """
    #     endpoint = f"{self.base_url}/api/module/query-executor/{project_id}/stored-query/{query_id}"
    #     params = {"alias": self.db_alias}
    #     return await self._execute_crud_request("DELETE", endpoint, params=params)

    async def _execute_crud_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """CRUD API 요청 공통 처리"""
        try:
            http_client = await self._get_http_client()
            if method == "GET":
                response = await http_client.get(endpoint, params=params)
            elif method == "POST":
                response = await http_client.post(
                    endpoint, params=params, json=payload
                )
            elif method == "PUT":
                response = await http_client.put(
                    endpoint, params=params, json=payload
                )
            elif method == "DELETE":
                response = await http_client.delete(endpoint, params=params)
            else:
                return {
                    "success": False,
                    "message": f"Unsupported method: {method}",
                }

            # Parse JSON response
            try:
                result = response.json()
            except json.JSONDecodeError:
                return {"raw": response.text}

            # HTTP 에러 상태 코드 처리
            if response.status_code >= 400:
                return {
                    "success": False,
                    "message": result.get(
                        "message", f"HTTP {response.status_code}"
                    ),
                    "data": result.get("data", result),
                }

            return result

        except httpx.TimeoutException:
            return {"success": False, "message": "Request timeout"}
        except httpx.NetworkError as e:
            return {"success": False, "message": f"Network error: {e}"}
        except Exception as e:
            return {"success": False, "message": f"Request Failed: {e!s}"}

    # ============================================================================
    # Cache Management APIs
    # ============================================================================

    async def reload_cache_all(self) -> dict[str, Any]:
        """Reload cached queries from all database aliases.

        This reloads queries from both moz_stored_query and moz_stored_custom_query
        tables for all configured database aliases.

        Returns:
            Response dict with reload status and statistics
        """
        endpoint = f"{self.base_url}/api/module/query-executor/querymanager/reload"
        return await self._execute_crud_request("POST", endpoint)

    async def reload_cache_by_alias(self, alias: str) -> dict[str, Any]:
        """Reload cached queries for a specific database alias.

        Args:
            alias: Database alias to reload (e.g., "com", "dp")

        Returns:
            Response dict with reload status
        """
        endpoint = (
            f"{self.base_url}/api/module/query-executor/querymanager/reload/{alias}"
        )
        return await self._execute_crud_request("POST", endpoint)

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get statistics about cached queries for all database aliases.

        Returns:
            Response dict with cache statistics
        """
        endpoint = f"{self.base_url}/api/module/query-executor/querymanager/stats"
        return await self._execute_crud_request("GET", endpoint)

    async def get_cache_stats_by_alias(self, alias: str) -> dict[str, Any]:
        """Get statistics about cached queries for a specific database alias.

        Includes source breakdown (stored vs custom queries).

        Args:
            alias: Database alias (e.g., "com", "dp")

        Returns:
            Response dict with detailed cache statistics
        """
        endpoint = (
            f"{self.base_url}/api/module/query-executor/querymanager/stats/{alias}"
        )
        return await self._execute_crud_request("GET", endpoint)
