# QueryExecutorAdapter 사용 가이드

## 클라이언트 생성

```python
from query_executor_adapter import QueryExecutorAdapter

client = QueryExecutorAdapter(
    base_url="http://localhost:18000",  # QueryExecutor 서비스 URL
    db_alias="com",                      # 저장된 쿼리 DB 별칭
    owner_id="aps",                      # 쿼리 소유자 ID
    timeout=60.0                         # 타임아웃 (초)
)
```

---

## 1. execute_query - 저장된 쿼리 실행

DB에 미리 저장된 쿼리를 ID로 실행합니다.

### Parameters

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|:----:|--------|------|
| `project_id` | str | O | - | 프로젝트 ID |
| `query_id` | str | O | - | 저장된 쿼리 ID |
| `parameters` | dict | X | None | 쿼리에 전달할 파라미터 |
| `page` | int | X | 1 | 페이지 번호 |
| `limit` | int | X | None | 페이지당 행 수 |
| `include_total_count` | bool | X | False | 총 개수 포함 여부 (`page=1`일 때만 동작) |
| `request` | Request | X | None | FastAPI Request (헤더 전파용) |
| `headers` | dict | X | None | 커스텀 헤더 |

### 사용 예시

```python
# 기본 사용
result = await client.execute_query(
    project_id="mzcdev",
    query_id="get_peg_info"
)

# 파라미터 전달
result = await client.execute_query(
    project_id="mzcdev",
    query_id="get_peg_info",
    parameters={"project_id": "EED70012", "status": "active"},
    page=1,
    limit=100,
    include_total_count=True
)

# FastAPI에서 사용 (TraceID 자동 전파)
@router.get("/data")
async def get_data(request: Request):
    return await client.execute_query(
        request=request,
        project_id="mzcdev",
        query_id="get_peg_info"
    )
```

### Return

```python
# 성공
{
    "success": True,
    "rowcount": 3,                          # 현재 페이지 행 수
    "columns": ["id", "name", "status"],    # 컬럼명 목록
    "row": [                                # 데이터 (dict 리스트)
        {"id": 1, "name": "Alice", "status": "active"},
        {"id": 2, "name": "Bob", "status": "active"},
        {"id": 3, "name": "Carol", "status": "inactive"}
    ],
    "has_next": True,                       # 다음 페이지 존재 여부
    "total_count": 150                      # 총 개수 (include_total_count=True 시)
}

# 실패
{
    "success": False,
    "message": "Stored query not found: invalid_query",
    "data": {"db_alias": "com", "error": {...}}
}
```

---

## 2. execute_direct_query - 직접 SQL 실행

SQL 문을 직접 작성하여 실행합니다.

### Parameters

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|:----:|--------|------|
| `project_id` | str | O | - | 프로젝트 ID |
| `query` | str | O | - | SQL 쿼리문 |
| `catalog` | str | O | - | Trino 카탈로그 (예: "iceberg") |
| `schema` | str | O | - | Trino 스키마 (예: "mzc_com") |
| `parameters` | dict | X | None | 쿼리 파라미터 (@param 치환) |
| `page` | int | X | 1 | 페이지 번호 |
| `limit` | int | X | None | 페이지당 행 수 |
| `is_write` | bool | X | False | DML/DDL 여부 **(INSERT/UPDATE/DELETE 시 True 필수)** |
| `include_total_count` | bool | X | False | 총 개수 포함 여부 |
| `request` | Request | X | None | FastAPI Request (헤더 전파용) |
| `headers` | dict | X | None | 커스텀 헤더 |

### 사용 예시

```python
# SELECT 쿼리
result = await client.execute_direct_query(
    project_id="mzcdev",
    query="SELECT * FROM users WHERE status = @status",
    catalog="iceberg",
    schema="mzc_com",
    parameters={"status": "active"},
    limit=100
)

# INSERT 쿼리 (is_write=True 필수!)
result = await client.execute_direct_query(
    project_id="mzcdev",
    query="INSERT INTO logs (action) VALUES (@action)",
    catalog="iceberg",
    schema="mzc_com",
    parameters={"action": "LOGIN"},
    is_write=True
)

# DELETE 쿼리 (is_write=True 필수!)
result = await client.execute_direct_query(
    project_id="mzcdev",
    query="DELETE FROM temp_data WHERE created_at < @date",
    catalog="iceberg",
    schema="mzc_com",
    parameters={"date": "2024-01-01"},
    is_write=True
)
```

### Return

```python
# SELECT 성공
{
    "success": True,
    "rowcount": 2,
    "columns": ["id", "name"],
    "row": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ],
    "has_next": False,
    "total_count": 2
}

# DML 성공 (INSERT/UPDATE/DELETE)
{
    "success": True,
    "rowcount": 5,
    "update_type": "INSERT",    # INSERT, UPDATE, DELETE
    "update_count": 5           # 영향받은 행 수
}

# 실패
{
    "success": False,
    "message": "line 1:15: Table 'iceberg.mzc_com.invalid' does not exist",
    "data": {"db_alias": "com", "error": {...}}
}
```

---

## 결과 처리 패턴

```python
result = await client.execute_query(
    project_id="mzcdev",
    query_id="get_users"
)

# 항상 success 체크 후 데이터 접근
if result["success"]:
    print(f"조회 건수: {result['rowcount']}")

    for row in result["row"]:
        print(f"ID: {row['id']}, Name: {row['name']}")

    if result.get("has_next"):
        print("다음 페이지가 있습니다")
else:
    print(f"에러: {result['message']}")
```

---

## 주의사항

| 항목 | 설명 |
|------|------|
| `is_write=True` | INSERT/UPDATE/DELETE/DDL 실행 시 **반드시** 설정 |
| `include_total_count` | `page=1`일 때만 동작 (2페이지 이상에서는 True여도 무시됨) |
| `request` 전달 | API 핸들러에서는 TraceID 전파를 위해 전달 권장 |
