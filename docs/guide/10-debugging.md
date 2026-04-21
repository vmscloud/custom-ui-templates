# 10. 디버깅 가이드

새 페이지를 만들 때, 또는 기존 화면을 건드릴 때 반복적으로 쓰는 디버깅 루틴을 모았습니다.

## 출발점: 증상 분류

증상이 발생하면 아래 순서로 좁혀 들어갑니다.

1. **응답이 오는가?** (Network 200/4xx/5xx)
2. **응답 바디가 기대한 구조인가?**
3. **값이 기대한 숫자인가?** (스케일/소수점/NULL)
4. **UI가 값을 올바르게 렌더하는가?** (format, 바인딩, v-model)

## 네트워크부터 확인

Chrome DevTools > Network 필터를 `Fetch/XHR` 로 두고:

1. 화면 진입/Search 시점의 `/api/custom/backend/<pid>/<domain>/<action>` 요청이 있는가.
2. Status 가 200 인가. 401/404/500 이면 각각 아래로 분기.
3. Request Payload 와 Response 를 펼쳐 의도대로인지 본다.

### 자주 나오는 상태코드

| 코드 | 원인 | 조치 |
|------|------|------|
| `404` | 라우터 등록 누락 | `api/v1/api.py` 의 `include_router` 확인 |
| `401` | 세션 없는 APS proxy 호출 | 해당 호출을 커스텀 BE 로 이전하거나 host 통합에서만 테스트 |
| `422` | Pydantic 스키마 불일치 | 요청 body 필드명/타입 확인 |
| `500` | 서비스 예외 | 백엔드 콘솔 로그 확인 (`logger.exception` 찍히는 위치) |

## 임시 `_debug` 필드 패턴

"쿼리는 성공했는데 데이터가 비어 있다"는 상황을 빠르게 진단하는 기법. 서비스 응답에 **임시**로 메타정보를 동봉합니다.

```python
async def get_main(self, project_id, params):
    # ... 기존 로직 ...
    plan_rows = self._safe_rows(plan_result)

    _debug = {
        "planVer": params.planVer,
        "partition_key": partition_key,
        "cycle_start": cycle_start,
        "cycle_end": cycle_end,
        "plan_rows_count": len(plan_rows),
        "plan_success": plan_result.get("success"),
        "plan_error": plan_result.get("error") or plan_result.get("message"),
        "plan_row_sample": plan_rows[:2],   # 첫 2개 샘플
    }

    # ... 집계 ...

    return {
        "success": True,
        "data": result_data[:30],     # TEMP: 샘플만 반환
        "_debug": _debug,
    }
```

DevTools 에서 응답을 저장한 뒤 Python 으로 펼쳐 보면 원인이 바로 드러납니다.

```bash
python -c "import json; d=json.load(open('response.json')); print(d['_debug'])"
```

검증이 끝나면 `_debug` 와 샘플 잘라내기(`[:30]`) 등을 반드시 **커밋 전에 제거**하세요.

## Swagger 로 엔드포인트 단독 호출

`http://localhost:8000/docs` 에서 원하는 엔드포인트를 찾아 `Try it out`.

- 요청 body 를 직접 바꿔가며 edge case 테스트.
- Frontend 없이 **서비스 로직만 분리 검증** 가능.

## curl 로 확인

```bash
curl -s "http://localhost:8000/api/custom/backend/<pid>/work-order/list" \
     -H "Content-Type: application/json" \
     -d '{"planVer":"20260420-M-01","fromDate":"2026-04-01","toDate":"2026-04-30","statuses":[]}' \
  | python -c "import json,sys; d=json.load(sys.stdin); print(len(d['data']), '샘플:', d['data'][:2])"
```

대량 응답이 DevTools 에 저장되지 않을 때 효과적입니다.

## 프론트 콘솔 로그

`ReExecutePlan.vue` 스타일의 대규모 composable 을 다룰 때는 핵심 이벤트(예: `onMainLoad` 시작/끝, 필터 변경) 에 `console.log` 를 잠깐 넣어 순서를 확인합니다.

```ts
console.log("[MyPage] onLoad start", { planVer: planVer.value });
```

검증 후 제거 또는 `if (import.meta.env.DEV)` 조건부로 남겨두기.

## Network 응답 저장

Chrome DevTools > Network > 응답을 우클릭 → **Save response as…** 로 JSON 파일 저장. 분석 스크립트에 넣어 값 차이를 계산.

> ⚠️ 응답이 수 MB 이상이면 Chrome 이 바디를 자동 폐기합니다. 이럴 때는 **임시 `_debug` + `data[:30]`** 조합으로 크기를 줄여 저장하세요.

## 값 스케일 검사 체크리스트

원본(다른 탭) 또는 SQL 클라이언트(Trino UI 등) 값과 비교할 때:

- 같은 `planVer`, 같은 필터인지.
- 집계 그룹/열 순서가 동일한지 (피벗 rowFields 순서 차이).
- 소수점 반올림 방식 차이인지 (백엔드에서 `round()` 걸려있지 않은지 확인).
- 페이지네이션으로 일부 row가 잘린 건 아닌지 (`has_next: true` 무시 여부).
- **마스터 ↔ fact 값 풀 불일치**: 프론트 필터(`operGroupIDs` 등)가 마스터에서 가져온 리스트인지, fact 쪽에 누락된 값이 있는지.

## 타이밍 버그 진단

초기 진입 시 API 가 **빈 파라미터**로 먼저 나가는 현상이 자주 있습니다.

확인 방법:

1. DevTools > Network → `/main` 요청의 Payload 열어 `planVer: ""`, `operGroupIDs: []` 처럼 비어있는지 본다.
2. 비어있다면 호출을 트리거하는 watch/composable 의 조건을 재검토.
3. 가드 예:
   ```ts
   const onLoad = async () => {
     if (!planVer.value) return;
     if (!operGroupSource.value.length) return;
     // ...
   };
   ```
4. 각 master fetch 입구에도 `planVer` 가드를 넣어, master 응답 flag 가 `planVer=""` 상태에서 미리 `true` 로 세팅되지 않게 합니다.

## SQL 쿼리 검증

Trino 쿼리 실패는 응답에 다음과 같은 메시지가 담깁니다.

```json
{
  "success": false,
  "error": "Value cannot be cast to date: 20260401"
}
```

`_debug.plan_error` 같은 곳에 그대로 찍어 두세요. Trino 콘솔에 접근 가능하면 같은 SQL 을 직접 실행해 재현.

### Trino 에서 자주 마주치는 오류

- `CAST` 실패: `'YYYYMMDD'` 문자열 → DATE 캐스팅 불가. `substr` 로 `YYYY-MM-DD` 조립하거나 문자열 비교.
- `column not found`: Iceberg 스키마와 원본 PG 스키마가 다른 경우. 실제 `SHOW COLUMNS FROM <table>` 로 확인.
- 대소문자: Trino는 보통 lowercase. 대문자 컬럼을 쓰면 `"DEMAND_TYPE"` 식으로 따옴표 필요할 수도.

## Uvicorn 리로드 확인

백엔드를 수정했는데 반영이 안 되면:

- 터미널에 `Reloading...` 메시지가 떴는지.
- syntax error 로 앱이 내려가지 않았는지 (콘솔 마지막 출력 확인).
- 포트 충돌이면 `netstat -ano | grep 8000` 으로 PID 찾아 kill.

## Vite HMR 확인

- 프론트 변경 후 브라우저 DevTools Console 에 `[vite] hot updated: /src/...` 메시지가 뜨는지.
- 안 뜨면 Full Reload.
- 인터넷 연결/CORS 문제로 vite 가 리로드 요청을 전달 못 하는 경우가 있으니, 브라우저 캐시 완전 지우기도 시도.

## 최종 체크 루틴

- [ ] Status 200?
- [ ] Request/Response payload 로그 확인
- [ ] `_debug` 필드로 쿼리 실행 성공·row 개수 확인
- [ ] 원본 탭/SQL 클라이언트로 값 대조 (스케일·소수점)
- [ ] 페이지네이션으로 유실된 row 없는지 (`has_next` 무시 여부)
- [ ] 초기 진입 시 빈 파라미터로 호출되지 않는지 (타이밍 가드)
- [ ] 커밋 전에 `_debug`/`[:30]` 잘라내기 제거

다음: [11-reference](./11-reference.md) 에서 공용 훅·아이콘·환경변수 목록을 한 장에 모았습니다.
