# 작업 이력: Host 환경 projectId resolver 자동 설정

- **날짜**: 2026-02-25
- **작업자**: Claude + 사용자
- **브랜치**: main

## 변경 요약

Module Federation으로 Host(APS)에서 컴포넌트를 로드할 때 `projectId resolver`가 설정되지 않는 버그를 수정했습니다.
`expose.ts`에서 각 뷰를 `withHostInit` 래퍼로 감싸 Host 환경에서 자동으로 resolver를 설정하도록 했습니다.

## 변경 파일 목록

### Frontend

- `frontend/src/expose.ts` - withHostInit 래퍼 추가, viewRegistry 엔트리 래핑

## 상세 변경 내용

### 1. withHostInit 래퍼 함수 추가

- Host(APS)에서 Remote 컴포넌트를 로드할 때 `DeveloperTool.vue`를 거치지 않아 `setProjectIdResolver`가 호출되지 않는 문제 해결
- `expose.ts`에서 각 뷰의 동적 import를 `withHostInit`으로 래핑
- 래퍼 컴포넌트가 `setup()` 시 `inject(HOST_DATA_KEY)`로 Host의 `hostData`를 가져와 resolver 자동 설정
- 새로운 뷰 추가 시에도 `withHostInit()`으로 감싸면 자동 적용

## 관련 커밋

- `(pending)` - Fix: Host 환경 projectId resolver 자동 설정

## 테스트 방법

1. Host(APS) 환경에서 Module Federation으로 Remote 컴포넌트 로드
2. DemandDistribution 페이지에서 조회 버튼 클릭
3. `[api] projectId resolver가 설정되지 않았습니다` 경고 없이 데이터가 정상 조회되는지 확인
