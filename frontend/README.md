# Custom Extension App

APS 커스텀 확장 개발을 위한 템플릿입니다.

## 개요

이 프로젝트는 APS(Host) 앱의 확장 기능을 개발하기 위한 템플릿입니다.
Module Federation을 통해 APS와 통합되며, 독립적으로 개발 및 테스트가 가능합니다.

**주요 특징**:

- 독립 개발 가능: APS 없이도 `pnpm dev`로 모든 기능 개발 가능
- Hot Module Replacement: 코드 변경 시 즉시 반영
- Host 스토어 연동: APS의 상태(PlanCycle, 사용자 정보 등)에 접근 가능
- Module Federation: 개발 완료 후 APS와 통합하여 배포

## Module Federation 아키텍처

### Host-Remote 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                         APS (Host)                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  RemoteLoader.vue                                        │   │
│  │  ┌─────────────────────────────────────────────────────┐│   │
│  │  │ provide('hostData', hostData)                       ││   │
│  │  │                                                     ││   │
│  │  │  ┌───────────────────────────────────────────────┐ ││   │
│  │  │  │     Remote Component (커스텀 확장앱)           │ ││   │
│  │  │  │                                               │ ││   │
│  │  │  │  - props로 hostData 수신                      │ ││   │
│  │  │  │  - inject('hostData')로도 접근 가능           │ ││   │
│  │  │  │  - useHostStores() 컴포저블 사용              │ ││   │
│  │  │  └───────────────────────────────────────────────┘ ││   │
│  │  └─────────────────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Module Federation
                              │ (remoteEntry.js)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Custom Extension App (Remote)                   │
│                                                                  │
│   expose.ts                                                      │
│   ├── viewRegistry                                               │
│   │   ├── ItemMaster                                             │
│   │   ├── HostInfo                                               │
│   │   └── ... (추가 뷰)                                          │
│   │                                                              │
│   vite.config.ts                                                 │
│   └── shared: { vue, pinia } (singleton)                         │
└─────────────────────────────────────────────────────────────────┘
```

### 공유 의존성 (Shared Dependencies)

Host(APS)와 Remote(커스텀 확장앱)는 다음 패키지를 공유합니다:

| 패키지  | 공유 방식 | 설명                   |
| ------- | --------- | ---------------------- |
| `vue`   | singleton | 단일 Vue 인스턴스 보장 |
| `pinia` | singleton | 상태 관리 공유         |

**singleton 모드**: 런타임에 하나의 인스턴스만 로드되어 충돌 방지

### 데이터 흐름

```
APS Host                          Custom Extension App
───────────                       ─────────────────────

PlanCycleStore ─────┐
ProjectInfoStore ───┼──► hostData ──► provide('hostData')
MenuStore ──────────┘                       │
                                            ▼
                                    ┌───────────────────┐
                                    │ useHostStores()   │
                                    │                   │
                                    │ planCycle:        │
                                    │   - planVer       │
                                    │   - fromDate      │
                                    │   - toDate        │
                                    │                   │
                                    │ projectInfo:      │
                                    │   - currentProject│
                                    │   - userInfo      │
                                    │   - isAdmin       │
                                    │                   │
                                    │ menu:             │
                                    │   - items         │
                                    │   - currentMenu   │
                                    └───────────────────┘
```

## 시작하기

### 1. 환경 설정

#### NPM 토큰 설정 (`@vmscloud/*` 패키지 설치용)

`@vmscloud/moz-ui-components`, `@vmscloud/moz-wijmo-grid` 등은 GitHub Packages 프라이빗 레지스트리에 배포되어 있어 **개인용 PAT(Personal Access Token)** 이 필요합니다.

1. GitHub → Settings → Developer settings → Personal access tokens → **Tokens (classic)**
2. `read:packages` 권한만 있는 토큰 생성 → 발급된 `ghp_xxx...` 값 복사

**⚠️ 보안 주의**
- 토큰 값은 **절대 저장소에 커밋하지 마세요.**
- `frontend/.npmrc` 는 `.gitignore` 로 관리됩니다 (토큰 유출 방지).
- 커밋되는 파일은 placeholder 가 들어있는 `frontend/.npmrc.example` 뿐입니다.

##### 옵션 A — `.npmrc` 파일 복사 (권장)

```bash
cd frontend
cp .npmrc.example .npmrc
# .npmrc 를 에디터로 열어 <SET_PAT_TOKEN> 부분을 발급받은 토큰으로 교체
```

`.npmrc` 포맷:

```
@vmscloud:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=<SET_PAT_TOKEN>
```

##### 옵션 B — 환경 변수 `NPM_TOKEN`

```bash
# Windows (PowerShell)
$env:NPM_TOKEN="ghp_your_token_here"

# macOS/Linux
export NPM_TOKEN="ghp_your_token_here"
```

`pnpm install` 시 파이프라인이 `NPM_TOKEN` 을 읽어 인증합니다.

##### 유출되었을 때

실수로 토큰이 커밋/푸시된 경우 **즉시 GitHub 토큰 설정에서 해당 PAT 을 revoke** 한 뒤 새 토큰을 발급하세요. 히스토리에서 완전히 제거하려면 `git filter-repo` 또는 BFG 사용이 추가로 필요합니다.

### 2. 의존성 설치

```bash
pnpm install
```

### 3. 개발 서버 실행

독립적으로 개발을 시작합니다:

```bash
pnpm dev
```

개발 서버는 `http://localhost:5300`에서 실행되며, Hot Module Replacement(HMR)가 지원됩니다.

**독립 개발 모드의 특징**:

- 빠른 개발 사이클 (빌드 불필요)
- HMR로 즉시 변경사항 반영
- 독립적인 라우팅 및 상태 관리
- Host 스토어는 빈 값으로 동작 (APS 통합 시 실제 데이터 제공)
- APS 없이 모든 기능 개발 가능

## 프로젝트 구조

```
src/
├── main.ts                 # 개발용 엔트리
├── bootstrap.ts            # 앱 부트스트랩 (Pinia, Vue Query 초기화)
├── App.vue                 # 개발용 래퍼 컴포넌트
├── expose.ts               # Module Federation 노출 정의
├── router/                 # 개발용 라우터
├── views/                  # 뷰 컴포넌트 (메뉴)
│   ├── templates/          # 템플릿 예제
│   │   └── basic1/
│   │       └── ItemMaster.vue
│   └── customs/            # 커스텀 뷰
│       └── host-info/
│           └── HostInfo.vue
├── components/             # 공통 컴포넌트
├── composables/            # 컴포저블
│   └── useHostStores.ts    # Host 스토어 접근
├── stores/                 # Pinia 스토어 (독립 실행 모드용)
│   └── mainStore.ts        # ProjectInfo 스토어
└── types/
    ├── host.d.ts           # Host 타입 정의
    └── moz-component.d.ts  # moz-component 타입 정의
```

### Nginx 설정 예시

커스텀 확장앱을 `/ext/` 경로에서 제공하도록 설정:

```nginx
map $host $external_app_server {
    default "http://host.docker.internal:5300";
}

location /ext/ {
    resolver 127.0.0.11 8.8.8.8 8.8.4.4 valid=10s ipv6=off;

    rewrite ^/ext/(.*)$ /$1 break;
    proxy_pass $external_app_server;

    proxy_http_version 1.1;
    proxy_set_header Host $proxy_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # CORS 헤더 (Module Federation 필수)
    add_header Access-Control-Allow-Origin * always;
    add_header Access-Control-Allow-Methods "GET, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept" always;

    # OPTIONS preflight 요청 처리
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept" always;
        add_header Content-Length 0;
        add_header Content-Type text/plain;
        return 204;
    }
}
```

## 개발 시 주의사항

1. **의존성 버전**: `vue`, `pinia` 버전이 APS와 일치해야 함
2. **스타일 충돌 주의**: scoped CSS 또는 고유한 클래스명 사용 권장
3. **전역 상태 변경 금지**: `useHostStores()`로 가져온 데이터는 읽기 전용으로만 사용
4. **moz-component 사용 제한**: 현재 moz-component는 사용 불가 (향후 커스텀 확장앱 전용 패키지 분리 예정)
