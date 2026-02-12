# Mozart APS - Custom Extension 개발 및 배포 아키텍처

## 1. 전체 개발-배포 파이프라인

```mermaid
flowchart TB
    subgraph DEV["1. 개발 단계"]
        direction TB
        DEV_FE["외주 개발자<br/>Frontend 개발<br/>(Vue 3 + TypeScript)"]
        DEV_BE["외주 개발자<br/>Backend 개발<br/>(FastAPI + Python)"]
        MOZ_UI["moz-ui-components<br/>(@vmscloud/moz-ui-components)<br/>GitHub Packages"]
        QM["Query Manager<br/>(쿼리 작성/저장 도구)"]

        DEV_FE -->|"pnpm install<br/>npm 토큰 인증"| MOZ_UI
        DEV_BE -->|"쿼리 작성 & 저장<br/>→ query_id 발급"| QM
    end

    subgraph RUNTIME["2. 런타임 아키텍처"]
        direction TB
        subgraph HOST["APS Host App (Port: 8080)"]
            RL["RemoteLoader.vue"]
            HD["provide('hostData')"]
            RL --> HD
        end

        subgraph REMOTE["Custom Extension Remote (Port: 5300)"]
            RE["remoteEntry.js"]
            EXP["expose.ts<br/>(viewRegistry)"]
            COMP["Vue Components<br/>ItemMaster, SalesChart, ..."]
            STORE["Pinia + TanStack Query"]
            RE --> EXP --> COMP --> STORE
        end

        subgraph BACKEND["FastAPI Backend (Port: 8000/18020)"]
            API["API Endpoints<br/>/api/v1/*"]
            SVC["Services<br/>(QueryExecuteService)"]
            ADP["QueryExecutorAdapter"]
            API --> SVC --> ADP
        end

        subgraph MOZART["Mozart Platform Services"]
            QE["Query Executor<br/>(execute-by-key)"]
            TRINO["Trino<br/>(분산 쿼리 엔진)"]
            QE --> TRINO
        end

        HOST -->|"Module Federation<br/>(singleton: vue, pinia)"| REMOTE
        HD -->|"inject('hostData')<br/>projectInfo, planCycle, menu"| COMP
        STORE -->|"API 호출<br/>(axios → proxy)"| API
        ADP -->|"HTTP POST<br/>query_id + parameters"| QE
    end

    subgraph CICD["3. CI/CD 파이프라인"]
        direction LR
        GH["GitHub Repository<br/>(Push / PR Merge)"]
        WF_FE["GitHub Workflow<br/>FE Docker Build"]
        WF_BE["GitHub Workflow<br/>BE Docker Build"]
        ECR_FE["AWS ECR<br/>FE Image<br/>(nginx + dist)"]
        ECR_BE["AWS ECR<br/>BE Image<br/>(python + uvicorn)"]

        GH --> WF_FE --> ECR_FE
        GH --> WF_BE --> ECR_BE
    end

    subgraph DEPLOY["4. 배포"]
        direction LR
        ONM["ONM 시스템<br/>(배포 관리)"]
        CUST["고객사 서버<br/>(Production)"]
        ECR_FE --> ONM
        ECR_BE --> ONM
        ONM -->|"Docker 배포"| CUST
    end

    DEV --> RUNTIME
    RUNTIME --> CICD
    CICD --> DEPLOY

    style DEV fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style RUNTIME fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style CICD fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style DEPLOY fill:#fce4ec,stroke:#c62828,stroke-width:2px
```

---

## 2. Frontend 개발 흐름 (Module Federation)

```mermaid
flowchart LR
    subgraph HOST_APP["APS Host App"]
        direction TB
        H_VIT["vite.config.ts<br/>name: 'aps_host'"]
        H_REM["remotes:<br/>external_app: '/ext/assets/remoteEntry.js'"]
        H_RL["RemoteLoader.vue"]
        H_PRO["provide('hostData', {<br/>  projectInfo,<br/>  planCycle,<br/>  menu<br/>})"]
        H_VIT --> H_REM --> H_RL --> H_PRO
    end

    subgraph REMOTE_APP["Custom Extension (이 레포)"]
        direction TB
        R_VIT["vite.config.ts<br/>name: 'external_app'"]
        R_EXP["expose.ts<br/>viewRegistry = {<br/>  ItemMaster: () => import(...),<br/>  SalesChart: () => import(...),<br/>}"]
        R_HOST["useHostStores()<br/>inject('hostData')"]
        R_VIEW["Vue Components"]
        R_VIT --> R_EXP --> R_VIEW
        R_HOST --> R_VIEW
    end

    subgraph SHARED["Singleton 공유 의존성"]
        S1["vue ^3.4.14"]
        S2["pinia ^2.1.7"]
        S3["moz-ui-components ^1.0.10"]
        S4["echarts ^5.0.0"]
    end

    HOST_APP <-->|"Module Federation<br/>런타임 통합"| REMOTE_APP
    SHARED ---|"동일 인스턴스 공유"| HOST_APP
    SHARED ---|"동일 인스턴스 공유"| REMOTE_APP

    style HOST_APP fill:#e8eaf6,stroke:#283593
    style REMOTE_APP fill:#e0f2f1,stroke:#00695c
    style SHARED fill:#fff9c4,stroke:#f9a825
```

---

## 3. Backend 데이터 흐름 (Query Executor)

```mermaid
sequenceDiagram
    participant DEV as 개발자
    participant QM as Query Manager
    participant FE as Frontend (Vue)
    participant BE as FastAPI Backend
    participant ADP as QueryExecutorAdapter
    participant QE as Query Executor API
    participant TR as Trino

    Note over DEV,QM: 사전 준비: 쿼리 등록
    DEV->>QM: SQL 쿼리 작성
    QM-->>DEV: query_id 발급<br/>(예: "get_item_master")

    Note over FE,TR: 런타임: 데이터 조회
    FE->>BE: POST /api/v1/items<br/>{projectId, planVer}
    BE->>ADP: execute_query(<br/>  query_id="get_item_master",<br/>  parameters={...},<br/>  project_id="..."<br/>)
    ADP->>QE: POST /api/module/query-executor/<br/>{project_id}/query/execute-by-key<br/>{query_id, alias, owner_id, parameters}
    QE->>TR: 저장된 SQL 실행
    TR-->>QE: NDJSON 스트리밍 응답
    QE-->>ADP: HTTP 200 (NDJSON)
    ADP->>ADP: _parse_response()<br/>NDJSON → {columns, row, rowcount}
    ADP-->>BE: {success, columns, rows, row_count}
    BE-->>FE: JSON Response
    FE->>FE: TanStack Query 캐시 업데이트<br/>UI 렌더링
```

---

## 4. CI/CD & 배포 파이프라인

```mermaid
flowchart LR
    subgraph SOURCE["소스 코드"]
        GIT["GitHub Repository<br/>custom-ui-templates"]
    end

    subgraph BUILD_FE["FE 빌드 (GitHub Workflow)"]
        FE1["node:22-alpine"]
        FE2["pnpm install<br/>(npm_token secret)"]
        FE3["pnpm build<br/>→ dist/remoteEntry.js"]
        FE4["nginx:alpine<br/>+ dist + nginx.conf"]
        FE1 --> FE2 --> FE3 --> FE4
    end

    subgraph BUILD_BE["BE 빌드 (GitHub Workflow)"]
        BE1["python:3.14-slim"]
        BE2["uv pip install"]
        BE3["uvicorn app.main:app<br/>--port 18020"]
        BE1 --> BE2 --> BE3
    end

    subgraph REGISTRY["컨테이너 레지스트리"]
        ECR["AWS ECR"]
        IMG_FE["FE Image<br/>(nginx:80)"]
        IMG_BE["BE Image<br/>(uvicorn:18020)"]
        ECR --- IMG_FE
        ECR --- IMG_BE
    end

    subgraph CUSTOMER["고객사 환경"]
        ONM["ONM 시스템<br/>(배포 매니저)"]
        SRV["고객사 서버"]
        FE_CON["FE Container<br/>/ext/* 서빙"]
        BE_CON["BE Container<br/>/api/* 처리"]
        APS["APS Host App"]

        ONM --> SRV
        SRV --- FE_CON
        SRV --- BE_CON
        APS -->|"Module Federation<br/>remoteEntry.js 로드"| FE_CON
        FE_CON -->|"API proxy"| BE_CON
    end

    GIT -->|"push / merge"| BUILD_FE
    GIT -->|"push / merge"| BUILD_BE
    BUILD_FE -->|"docker push"| ECR
    BUILD_BE -->|"docker push"| ECR
    ECR -->|"이미지 Pull"| ONM

    style SOURCE fill:#f3e5f5,stroke:#6a1b9a
    style BUILD_FE fill:#e8f5e9,stroke:#2e7d32
    style BUILD_BE fill:#fff3e0,stroke:#e65100
    style REGISTRY fill:#e3f2fd,stroke:#1565c0
    style CUSTOMER fill:#fce4ec,stroke:#c62828
```

---

## 5. 프로젝트 구조 요약

```mermaid
graph TB
    subgraph REPO["custom-ui-templates/"]
        subgraph FE["frontend/"]
            FE_SRC["src/"]
            FE_MAIN["main.ts (개발 진입점)"]
            FE_EXPOSE["expose.ts (Federation 노출)"]
            FE_VIEWS["views/ (페이지 컴포넌트)"]
            FE_COMP["composables/ (useHostStores 등)"]
            FE_STORE["stores/ (Pinia)"]
            FE_VITE["vite.config.ts"]
            FE_DOCK["Dockerfile (node → nginx)"]
            FE_NGINX["nginx.conf (/ext 서빙)"]
        end

        subgraph BE["backend/"]
            BE_APP["app/"]
            BE_API["api/v1/endpoints/"]
            BE_SVC["services/"]
            BE_ADP["adapters/adapter.py<br/>(QueryExecutorAdapter)"]
            BE_SCH["schemas/"]
            BE_CORE["core/config.py"]
            BE_DOCK["Dockerfile (python:slim)"]
        end

        DOCS["docs/<br/>EXTERNAL_DEVELOPER_GUIDE.md"]
    end

    style FE fill:#e0f2f1,stroke:#00695c
    style BE fill:#fff3e0,stroke:#e65100
    style REPO fill:#fafafa,stroke:#424242
```

---

## 6. 핵심 포인트 요약

| 구분 | 설명 |
|------|------|
| **FE 라이브러리** | `@vmscloud/moz-ui-components` (GitHub Packages, npm 토큰 필요) |
| **FE-Host 연결** | Module Federation (`remoteEntry.js`), singleton 공유 (vue, pinia) |
| **Host → Remote 데이터** | `provide/inject` 패턴 (`projectInfo`, `planCycle`, `menu`) |
| **BE 쿼리 실행** | Query Manager에서 쿼리 저장 → `query_id` 발급 → `QueryExecutorAdapter.execute_query()` |
| **BE → Query Executor** | HTTP POST `/api/module/query-executor/{project_id}/query/execute-by-key` |
| **빌드** | GitHub Workflow → Docker (FE: nginx, BE: uvicorn) |
| **배포** | Docker Image → AWS ECR → ONM 시스템 → 고객사 서버 |
