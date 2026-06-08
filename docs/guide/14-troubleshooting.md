# 14. 문제 해결 (설정 · 빌드 · 통합)

환경 세팅, 빌드, 호스트 통합 단계에서 자주 막히는 지점을 모았습니다.

> **런타임/데이터 디버깅**(응답 상태코드, 빈 데이터, Trino 쿼리 오류, 값 스케일, 타이밍 버그)은 [10-debugging](./10-debugging.md) 에 별도로 정리되어 있습니다. 화면은 떴는데 값이 이상한 경우는 그쪽을 보세요. 이 문서는 **그 앞 단계** — 설치·빌드·호스트 연동이 아예 안 되는 경우를 다룹니다.

## 1. 의존성 / 설치

### `@vmscloud/moz-ui-components` 를 찾을 수 없음

```
원인: GitHub Packages 인증 토큰 미설정 또는 만료
```

`@vmscloud/moz-ui-components` 는 GitHub Packages 비공개 레지스트리에 있어 토큰이 필요합니다.

1. `frontend/.npmrc` 가 있는지 확인. 없으면 `frontend/.npmrc.example` 을 복사해 `<SET_PAT_TOKEN>` 을 본인 PAT(`ghp_...`)로 교체.
   ```
   @vmscloud:registry=https://npm.pkg.github.com
   //npm.pkg.github.com/:_authToken=ghp_xxxxxxxx
   ```
2. PAT 권한에 `read:packages` 가 포함됐는지 확인 (만료되었으면 재발급).
3. 캐시 정리 후 재설치:
   ```powershell
   cd frontend
   pnpm store prune
   pnpm install
   ```
4. 설치 확인: `pnpm ls @vmscloud/moz-ui-components`

> ⚠️ `.npmrc` 는 `.gitignore` 로 추적 제외됩니다. 토큰을 저장소에 커밋하지 마세요. 실수로 푸시했다면 즉시 해당 PAT 을 revoke 하고 재발급하세요.

### 공유 라이브러리 버전 충돌

```
원인: vue / pinia 등 호스트와 공유하는 라이브러리 버전 불일치
```

Module Federation 의 `singleton` 의존성은 호스트와 버전이 어긋나면 런타임에 예측 불가한 에러를 냅니다.

1. `frontend/package.json` 의 버전 확인 (`vue`, `pinia`, `@vmscloud/moz-ui-components`).
2. 호스트가 기대하는 버전과 일치시킵니다.
3. lockfile 갱신: `pnpm install`

## 2. 빌드

### Module Federation 빌드 실패

```
원인: exposes 설정 오류 또는 파일 경로 오류
```

1. `frontend/vite.config.ts` 의 `exposes` 경로가 실제 파일을 가리키는지 확인 (`./src/expose.ts`).
2. `src/expose.ts` 가 존재하고 `viewRegistry` 구조가 올바른지 확인.
3. 등록한 뷰의 dynamic import 경로 오타 확인.

```ts
// src/expose.ts
export const viewRegistry = {
  MyPage: () => import("./views/templates/.../MyPage.vue"),
} as const;
export type ViewName = keyof typeof viewRegistry;
```

### `remoteEntry.js` 생성 안 됨

```
원인: Module Federation 플러그인 미설정 또는 filename 누락
```

`vite.config.ts` 의 federation 플러그인에 `filename: 'remoteEntry.js'` 와 `exposes` 가 모두 있어야 합니다.

```ts
federation({
  name: 'external_app',
  filename: 'remoteEntry.js',   // 필수
  exposes: { './expose': './src/expose.ts' },
  shared: { vue: { singleton: true }, pinia: { singleton: true }, /* ... */ },
})
```

빌드 후 `frontend/dist/remoteEntry.js` 가 있는지 확인하세요. (배포 캐싱 이슈는 [13-deployment](./13-deployment.md) 의 nginx 캐싱 정책 참고.)

### 타입체크 실패 (`vue-tsc`)

`pnpm build` 는 `vue-tsc` 타입체크를 포함합니다. 타입 에러로 빌드가 멈추면:

1. `cd frontend; pnpm vue-tsc --noEmit` 로 에러 위치 확인.
2. 호스트 주입 타입은 `src/types/host.d.ts` 등 타입 정의를 보강 (가능하면 `as any` 대신 타입 추가).

## 3. 호스트 통합

### Host 데이터가 `undefined`

```
원인: 호스트 모드로 실행되지 않았거나, 주입 값이 아직 채워지지 않음
```

먼저 호스트 모드인지 진단합니다.

```ts
import { isRunningInHost } from "@/composables/useHostStores";
console.log("host mode:", isRunningInHost());
```

- **단독 dev** 에서는 호스트가 없으므로 `DeveloperTool` 이 mock 값을 주입합니다. 실제 host 데이터가 없는 게 정상입니다. (단독 dev ↔ host 전환은 [02-environment-setup](./02-environment-setup.md) 참고.)
- **호스트 모드인데도 비어 있다면**: `planVer` 같은 주입 값은 `""` → 실제 값으로 바뀌는 타이밍이 존재합니다. API 호출에 가드를 넣으세요.
  ```ts
  const onLoad = async () => {
    if (!planVer.value) return;   // 빈 값일 때 호출 차단
    // ...
  };
  ```
  (타이밍 버그 진단은 [10-debugging](./10-debugging.md) 의 "타이밍 버그 진단" 참고.)

### `provide` / `inject` 가 작동 안 함

```
원인: 공유 라이브러리 버전 불일치로 호스트와 리모트가 서로 다른 Vue 인스턴스를 사용
```

`provide/inject` 는 동일한 Vue 인스턴스 안에서만 동작합니다.

1. 호스트와 리모트의 `vue` 버전이 일치하는지 확인.
2. `vite.config.ts` 의 `shared` 에서 `vue: { singleton: true }` 인지 확인.
3. 캐시 정리: `pnpm store prune` 후 재설치.

### `/api/aps/...` 호출이 401

단독 dev 에서는 **정상**입니다. APS C# 호스트 API 는 세션 쿠키(`fusionauth.sid`)가 필요하고, dev 단독 실행에는 세션이 없습니다.

- 커스텀 로직이 필요하면 APS Host API(C) 대신 커스텀 백엔드(A: PostgreSQL / B: Trino)로 대체하는 쪽이 안전합니다. ([07-data-sources](./07-data-sources.md) 참고.)

## 4. 개발 서버

### API 프록시가 작동 안 함

```
원인: 프록시 설정 오류 또는 백엔드 미실행
```

1. 백엔드가 떠 있는지: `curl http://localhost:8000/docs`
2. `vite.config.ts` 의 `server.proxy` 가 `/api` → `http://localhost:8000` 으로 forward 하는지 확인.
3. DevTools > Network 에서 실제 요청 URL/상태 확인.

### HMR 이 작동 안 함

[10-debugging](./10-debugging.md) 의 "Vite HMR 확인" / "Uvicorn 리로드 확인" 항목을 참고하세요. 흔한 원인은 포트 충돌, syntax error 로 인한 서버 다운, 브라우저 캐시입니다.
