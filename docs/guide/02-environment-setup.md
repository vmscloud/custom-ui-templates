# 02. 환경 세팅

## 필수 도구

| 도구 | 버전 | 용도 |
|------|------|------|
| Node.js | 18+ | 프론트 빌드/개발 서버 |
| pnpm 또는 npm | 최신 | 패키지 매니저. 저장소엔 둘 다의 lockfile 존재 |
| Python | 3.11+ | FastAPI 실행 |
| uv | 최신 | 파이썬 가상환경·의존성. `backend/.venv` 자동 |
| PowerShell | Win 전용 | `run-dev.ps1`, `deploy-custom-ui.ps1` |
| Chrome | 최신 | 개발/디버깅 |

## 첫 세팅

### 1) NPM 토큰 준비 (`.npmrc` 설정)

`@vmscloud/*` 패키지는 GitHub Packages 프라이빗 레지스트리라 **PAT(Personal Access Token)** 가 필요합니다.

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. `read:packages` 권한으로 발급.
3. 아래 중 한 가지 방식으로 주입.

```bash
cd frontend
cp .npmrc.example .npmrc
# .npmrc 를 열어 <SET_PAT_TOKEN> 을 발급받은 ghp_... 값으로 교체
```

`.npmrc` 예시:

```
@vmscloud:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=ghp_xxxxxxxxxxxxxxxxxxxxx
```

환경 변수 방식도 허용합니다.

```powershell
$env:NPM_TOKEN="ghp_..."
```

> ⚠️ **`frontend/.npmrc` 는 `.gitignore` 에 포함돼 있어 절대 저장소에 커밋되지 않습니다.** 저장소에 올라가는 건 placeholder 가 들어간 `frontend/.npmrc.example` 뿐입니다. 실수로 토큰이 커밋됐다면 즉시 GitHub 토큰 설정에서 revoke + 새 토큰 발급하세요.

### 2) 의존성 설치

```powershell
# 백엔드
cd backend
uv sync                   # 가상환경 + 의존성

# 프론트엔드
cd ../frontend
pnpm install              # 혹은 npm install
```

`.env` 는 예제가 없으면 비워도 대부분 동작합니다. 필요한 키는 `backend/app/core/config.py` 에 정의되어 있습니다 (대표 키는 아래 표 참고).

## Dev 서버 두 개 띄우기

터미널 2개 사용. 각각 **reload 모드**로 실행되어 파일 수정 시 자동 재시작.

### 백엔드 (포트 8000)

```powershell
cd backend
./run-dev.ps1
# 내부적으로: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- Swagger UI: `http://localhost:8000/docs`
- 헬스 체크: `http://localhost:8000/health` 또는 `/api/v1/health`

### 프론트엔드 (포트 5300)

```powershell
cd frontend
./run-dev.ps1
# 내부적으로: vite (port 5300, base=/ext/)
```

- 단독 진입: `http://localhost:5300/ext/<path>`
- 라우트 목록은 `src/router/index.ts` 에 정의

### vite 의 두 가지 proxy

`frontend/vite.config.ts` 가 두 개의 API prefix를 다른 서버로 프록시합니다.

```ts
proxy: {
  "/api/aps/":   { target: "https://dev.mozart-cloud.com", ... },
  "/api":        { target: API_TARGET || "http://localhost:8000", ... },
}
```

- `api.post("/api/custom/backend/...")` → **로컬 FastAPI**
- `api.post("/api/aps/backend/...")` → **APS C# Host**

※ `/api/aps/` 호출은 세션 쿠키가 필요합니다. 로컬 dev에서는 401이 정상.

## 환경 변수 주요 키

`backend/.env` 에 덮어쓸 수 있는 것들(기본값은 `app/core/config.py` 참고).

| 키 | 설명 |
|----|------|
| `TRINO_CATALOG_ICEBERG` | Trino 카탈로그 이름(예: `iceberg`) |
| `TRINO_SCHEMA_APS` | Trino 스키마/테넌트(예: `mzc_aps`) |
| `APS_BACKEND_BASE_URL` | proxy 중계 시 C# BE 주소 |
| `QUERY_TIMEOUT_SECONDS` | httpx 타임아웃 |
| `DEBUG` | `true` 로 두면 FastAPI 에러 응답에 `detail` 포함 |
| (PG 관련) | `PG_HOST`, `PG_PORT`, `PG_DB`, `PG_USER`, `PG_PASSWORD` 등 |

## Mock 모드 (DB 없이 UI 작업)

백엔드를 mock 모드로 띄우면 `backend/mock_data/responses/` 의 JSON을 응답으로 돌려줍니다. DB/쿼리 실행 없이 화면 개발이 가능.

```powershell
cd backend
./run-mock.ps1
```

관련 코드:
- 미들웨어: `backend/app/core/mock_middleware.py`
- 저장소: `backend/mock_data/responses/<domain>/...`
- 캡처 스크립트: `backend/mock_data/capture.py` (실제 DB로 한 번 돌려 응답을 저장)

## 단독 dev 와 Host 통합 전환

### 단독 dev 실행

`http://localhost:5300/ext/my-page` 로 접근하면 `src/router/index.ts` 의 라우트가 `DeveloperTool` 컴포넌트를 통해 `hostData` 를 주입합니다. 실제 host 없이도 플랜 버전 / 프로젝트 ID 등을 수동으로 세팅할 수 있도록 구성되어 있습니다.

### Host에 올려 검증

완성된 프론트 빌드 산출물을 APS 호스트 쪽 static 경로에 배포하면 `window.__POWERED_BY_APS_HOST__=true` 환경에서 `viewRegistry["MyPage"]()` 가 호출됩니다. 배포 절차는 기존 `docs/EXTERNAL_DEVELOPER_GUIDE.md` 를 참고하세요.

## 빠른 점검 체크리스트

| 체크 | 명령/URL |
|------|---------|
| BE 떴나 | `curl http://localhost:8000/docs` |
| FE 떴나 | `curl http://localhost:5300/ext/` |
| BE→PG 접속 | Swagger 에서 간단한 `/cfg-*` 엔드포인트 호출 |
| BE→Trino 접속 | 어떤 커스텀 엔드포인트든 `/main` 호출 후 200·row 존재 |
| 프록시 (dev) | `/api/aps/backend/...` 호출 → 401 (정상, 세션 없음) |

## 개발 편의 팁

- VS Code 에서 `backend/` 를 파이썬 워크스페이스로 열고 `.venv` 를 interpreter 로 지정하면 자동완성·디버깅이 편합니다.
- `frontend/` 는 `pnpm dev` 대신 `pnpm run-dev` 등 별도 스크립트가 없다면 `./run-dev.ps1` 을 그대로 씁니다.
- 코드 수정 후 변경이 반영되지 않으면: 백엔드는 콘솔에 `Reloading...` 메시지가 떴는지, 프론트는 vite 가 HMR 메시지를 출력하는지 확인.

다음 문서: [03-architecture](./03-architecture.md) — 두 서버의 역할 분리와 데이터 흐름.
