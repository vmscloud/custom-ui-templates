# 13. 배포 및 통합

로컬에서 완성한 리모트 앱과 FastAPI 백엔드를 **Docker 이미지로 빌드해 사내 레지스트리에 푸시**하고, APS 호스트가 이를 로드하도록 통합하는 절차입니다.

> 실제 배포는 저장소 루트의 [`deploy-custom-ui.ps1`](../../deploy-custom-ui.ps1) 스크립트가 전담합니다. 이 문서는 그 스크립트가 무엇을 하는지와, 직접 빌드/통합할 때 알아야 할 점을 정리합니다.

## 산출물 한눈에 보기

| 구성 | 베이스 이미지 | 산출물 | 포트 |
|------|--------------|--------|------|
| frontend | `node:22-alpine` → `nginx:alpine` | `dist/` 정적 번들 (`remoteEntry.js` 포함) | 80 (`/ext`) |
| backend | `python:3.14.1-slim` | uvicorn ASGI 앱 | 18020 |

- 프론트는 빌드 후 nginx 로 `/ext` 경로에 서빙되며, 호스트가 `/ext/remoteEntry.js` 를 Module Federation 엔트리로 로드합니다.
- 두 이미지는 사내 레지스트리(`203.231.40.243:6007`)에 `custom-ui-frontend`, `custom-ui-backend` 이름으로 푸시됩니다.

## 1. 로컬 프로덕션 빌드

배포 이미지를 만들기 전, 로컬에서 빌드가 깨지지 않는지 먼저 확인합니다.

```powershell
# 프론트엔드: vue-tsc 타입체크 + vite build (Makefile 경유)
make build-frontend
# 또는 직접
cd frontend; pnpm run build
```

빌드 산출물 구조:

```
frontend/dist/
├── remoteEntry.js          ← ★ Module Federation 진입점 (이름 고정)
├── assets/
│   ├── *-[hash].js         ← 해시 기반 번들
│   └── *-[hash].css
└── index.html
```

> **`remoteEntry.js` 가 생성됐는지 반드시 확인하세요.** 이 파일이 없으면 호스트가 리모트를 로드할 수 없습니다. 누락 시 [14-troubleshooting](./14-troubleshooting.md) 의 "remoteEntry.js 생성 안 됨" 항목을 참고하세요.

## 2. 배포 스크립트 사용 (`deploy-custom-ui.ps1`)

저장소 루트에서 실행합니다. 빌드 → 사내 레지스트리 푸시까지 한 번에 처리합니다.

> 📍 **실제 배포는 `omn` 환경에서 수행하세요.** 아래의 사전 조건(GitHub Packages 토큰, insecure registry 등록)이 갖춰지고 사내 레지스트리(`203.231.40.243:6007`)로의 네트워크 경로가 열려 있는 환경이 `omn` 입니다. 로컬에서 빌드 검증(`make build-frontend`)까지 마친 뒤, 푸시는 `omn` 에서 진행합니다.

```powershell
# 둘 다 빌드/푸시
.\deploy-custom-ui.ps1

# 한쪽만
.\deploy-custom-ui.ps1 -Service frontend
.\deploy-custom-ui.ps1 -Service backend

# 캐시 무시하고 새로 빌드
.\deploy-custom-ui.ps1 -Service frontend -NoCache
```

주요 파라미터:

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `-Service` | `all` | `backend` / `frontend` / `all` |
| `-Tag` | `custom` | 이미지 태그 |
| `-HostIP` | `203.231.40.243` | 레지스트리 호스트. 환경이 다르면 override |
| `-RegistryPort` | `6007` | 레지스트리 포트 |
| `-GithubToken` | `$env:GITHUB_TOKEN` | 프론트 빌드용 GitHub Packages 토큰 |
| `-NoCache` | (off) | `docker build --no-cache` |

### 사전 조건 (한 번만 설정)

1. **GitHub Packages 토큰** — 프론트 이미지는 `@vmscloud/moz-ui-components` 를 받기 위해 인증이 필요합니다. 스크립트는 다음 순서로 토큰을 찾습니다.
   - `-GithubToken` 파라미터
   - `$env:GITHUB_TOKEN`
   - `frontend/.npmrc` 의 `_authToken=` 값
   토큰은 `docker build --secret` 로 주입되어 이미지 레이어에 남지 않습니다.

2. **insecure registry 등록** (Docker Desktop) — 아래 "레지스트리 IP 설정" 참고.

스크립트는 토큰 누락·빌드 실패·푸시 거부 시 원인과 해결 방법을 콘솔에 자세히 출력합니다. 막히면 그 메시지를 먼저 읽으세요.

### 레지스트리 IP 설정: 두 곳을 맞춰야 하는 이유

레지스트리 주소는 **서로 다른 역할의 두 곳**에 들어갑니다. 둘이 가리키는 엔드포인트가 **반드시 같아야** push 가 성공합니다.

| 위치 | 역할 | 비유 |
|------|------|------|
| Docker Desktop `daemon.json` 의 `insecure-registries` | "이 주소로는 HTTPS 없이 HTTP push 를 허용한다"는 **허용 목록(allowlist)** | 통과시킬 주소를 적어 둔 *출입 명단* |
| `deploy-custom-ui.ps1` 의 `-HostIP` / `-RegistryPort` | 이미지를 **실제로 밀어 넣는 목적지 경로** (`HostIP:Port/이미지:태그`) | 실제로 짐을 보내는 *배송 주소* |

> Docker 는 기본적으로 모든 레지스트리에 HTTPS 를 요구합니다. 사내 레지스트리는 HTTP(평문) 이라, 허용 목록에 등록하지 않으면 데몬이 push 를 **거부**합니다. 반대로 허용 목록에만 넣고 스크립트의 목적지가 다르면, 등록되지 않은 주소로 보내려다 다시 거부됩니다. **두 주소가 정확히 일치**해야 합니다.

#### ① Docker Desktop — 허용 목록 등록

Docker Desktop > **Settings** > **Docker Engine** 의 JSON 에 다음을 추가하고 **Apply & Restart**:

```json
{
  "insecure-registries": ["203.231.40.243:6007"]
}
```

- 기존에 다른 키가 있으면 `insecure-registries` 항목만 병합해 추가하세요(전체를 덮어쓰지 말 것).
- 직접 파일을 고치려면 `%USERPROFILE%\.docker\daemon.json` 을 수정합니다.
- **변경 후 Docker Desktop 을 반드시 재시작**해야 합니다. 데몬은 시작 시점에만 이 값을 읽기 때문에, 재시작 전에는 등록이 적용되지 않습니다.
- 적용 확인: `docker info` 출력의 `Insecure Registries` 목록에 `203.231.40.243:6007` 이 보이면 정상.

#### ② 스크립트 — 실제 푸시 경로

기본값은 스크립트 상단 `param` 블록에 박혀 있습니다.

```powershell
# deploy-custom-ui.ps1
param(
    ...
    [string]$HostIP = "203.231.40.243",
    [int]$RegistryPort = 6007,
    ...
)
```

이 값을 바꾸는 방법은 두 가지입니다.

- **일회성** — 실행할 때 파라미터로 override (권장, 스크립트 수정 불필요):
  ```powershell
  .\deploy-custom-ui.ps1 -HostIP 192.168.x.x -RegistryPort 6007
  ```
- **영구** — 레지스트리 주소 자체가 바뀐 경우에만 `param` 블록의 기본값을 직접 수정.

> 레지스트리 주소를 바꿨다면 **①의 허용 목록도 같은 주소로 갱신**해야 합니다. 한쪽만 바꾸면 push 가 거부됩니다. push 실패 시 스크립트가 현재 `daemon.json` 의 등록 상태와 불일치 여부를 진단해 출력하므로, 그 메시지를 먼저 확인하세요.

## 3. 이미지 내부 동작

직접 `docker build` 하거나 Dockerfile 을 수정해야 할 때 참고합니다.

### frontend ([`frontend/Dockerfile`](../../frontend/Dockerfile))

```dockerfile
FROM node:22-alpine AS builder
RUN corepack enable && corepack prepare pnpm@latest --activate
# .npmrc 에 GitHub Packages 토큰을 secret 으로 주입 → pnpm install → 토큰 제거
RUN node scripts/license.js
RUN pnpm build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

### nginx 캐싱 정책 ([`frontend/nginx.conf`](../../frontend/nginx.conf))

Module Federation 배포에서 **가장 자주 사고가 나는 지점**입니다.

| 대상 | 캐시 정책 | 이유 |
|------|-----------|------|
| `/ext/remoteEntry.js` | `no-store` | 이름이 고정이라 캐시되면 옛 엔트리가 옛 해시 번들을 가리켜 404 |
| `/ext/index.html` | `no-store` | 동일 |
| `/ext/assets/*-[hash].js\|css` | `immutable, 1y` | 해시 파일명이라 영구 캐시 안전 |
| 기타 정적 리소스 | `1h` | 폰트·로고 등 |

> 배포 후 리모트 화면이 통째로 비어 보이면 대개 `remoteEntry.js` 가 캐시되어 옛 해시를 따라가다 `/ext/assets/*.js` 가 404 난 경우입니다. 브라우저/CDN 캐시를 비우고 nginx 헤더가 위 표대로 나가는지 확인하세요.

헬스체크는 `/healthz` (200 `ok`) 로 노출됩니다.

### backend ([`backend/Dockerfile`](../../backend/Dockerfile))

```dockerfile
FROM python:3.14.1-slim
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv pip install --system -r pyproject.toml
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "18020"]
```

## 4. 호스트(APS) 통합

호스트는 Module Federation 으로 리모트의 `remoteEntry.js` 를 로드하고, `expose.ts` 의 `viewRegistry` 에서 뷰를 찾아 마운트합니다.

```
APS Host  ──(remoteEntry.js)──▶  custom-ui-frontend
   │                                   viewRegistry["MyPage"]()
   └──(/api/custom/backend/{pid}/...)─▶ custom-ui-backend  ──▶ Trino / PostgreSQL
```

- 호스트 환경에서는 `window.__POWERED_BY_APS_HOST__ === true` 이며, `provide('hostData', ...)` 로 `planVer`·`projectInfo`·`menu` 등이 주입됩니다. (아키텍처 상세: [03-architecture](./03-architecture.md))
- 공유 의존성(`vue`, `pinia`, `@vmscloud/moz-ui-components` 등)은 호스트와 **버전이 일치**해야 `provide/inject` 가 정상 동작합니다. 불일치 시 [14-troubleshooting](./14-troubleshooting.md) 의 "provide/inject 작동 안 함" 참고.

## 5. 배포 전 체크리스트

- [ ] `make build-frontend` 성공 (vue-tsc 타입체크 통과)
- [ ] `frontend/dist/remoteEntry.js` 생성 확인
- [ ] 공유 의존성 버전이 호스트와 일치 (`vue`, `pinia`, `@vmscloud/moz-ui-components`)
- [ ] GitHub Packages 토큰 준비 (`$env:GITHUB_TOKEN` 또는 `frontend/.npmrc`)
- [ ] insecure-registry 등록 + Docker Desktop 재시작
- [ ] `.\deploy-custom-ui.ps1` push 성공 (frontend + backend)
- [ ] 배포 후 `/ext/remoteEntry.js` 응답 헤더가 `no-store` 인지 확인
- [ ] 호스트에서 해당 뷰 라우트 진입 시 정상 렌더 + `/api/custom/...` 200

다음: [14-troubleshooting](./14-troubleshooting.md) 에서 설정·빌드·통합 단계의 문제 해결을 다룹니다.
