# 작업 이력: pnpm-lock.yaml 동기화

- **날짜**: 2026-02-25
- **작업자**: Claude + 사용자
- **브랜치**: main

## 변경 요약

CI 빌드 실패를 해결하기 위해 `pnpm-lock.yaml`을 `package.json`과 동기화했습니다.
`--frozen-lockfile` 옵션으로 인해 lockfile과 package.json의 버전 불일치가 빌드 오류를 발생시켰습니다.

## 변경 파일 목록

### Frontend

- `frontend/pnpm-lock.yaml` - 3개 패키지 버전 동기화

## 상세 변경 내용

### 1. pnpm-lock.yaml 버전 동기화

Docker 빌드 시 `pnpm install --frozen-lockfile`에서 lockfile과 package.json 간 버전 불일치로 빌드 실패:

| 패키지 | lockfile (이전) | package.json (현재) |
|---|---|---|
| `@vmscloud/moz-ui-chart` | ^1.0.7 | ^1.0.11 |
| `@vmscloud/moz-ui-components` | ^1.2.3 | ^1.2.7 |
| `@vmscloud/moz-wijmo-grid` | ^1.0.13 | ^1.0.17 |

`pnpm install`을 실행하여 lockfile을 갱신했습니다.

## 테스트 방법

1. CI/CD 파이프라인에서 Docker 빌드가 정상적으로 통과하는지 확인

## 비고

- CI 환경에서 `--frozen-lockfile`은 기본적으로 활성화되어 있어, lockfile 동기화가 필수
