# 12. MCP 서버

Claude Code 등 LLM 에이전트가 이 저장소에서 쓰는 MCP 서버를 다룹니다. **공개 도구**와 **내부 데이터베이스 서버**는 노출 정책이 다릅니다.

## 두 가지 스코프

| 구분 | 등록 위치 | 커밋 여부 | 예시 |
|------|-----------|-----------|------|
| 공개 도구 | `.mcp.json` (프로젝트 스코프) | ✅ 커밋됨 | chrome-devtools, sequential-thinking, playwright, serena |
| 내부 DB/GitHub | local 스코프 (`~/.claude.json`, 레포 밖) | ❌ 커밋 안 됨 | github, postgres-\* |

## ⚠️ 내부 데이터베이스 MCP 노출 금지

이 저장소는 **공개 레포**입니다. 내부 DB의 **종류·개수·이름·접속 정보**가 공개 `.mcp.json` 에 드러나면 안 됩니다.

- 내부 DB MCP는 **반드시 local 스코프**(레포 밖 `~/.claude.json`)에만 등록합니다.
- 서버 정의·DB 이름·개수는 전부 로컬 `.env` 에서만 옵니다. 스크립트나 커밋되는 파일에 하드코딩하지 마세요.
- 비밀값(토큰·접속 문자열)은 `{{VAR}}` 플레이스홀더로만 등록되고, 런타임에 `tools/mcp-launch.mjs` 가 `.env` 에서 주입합니다. → `~/.claude.json` 에도 비밀이 저장되지 않습니다.
- 실수로 DB 이름이나 접속 정보를 커밋했다면 즉시 되돌리고 비밀값을 교체(rotate)하세요.

## 어떤 데이터베이스를 붙이는가 → 담당자에게 문의

**이 저장소는 의도적으로 내부 DB 정보를 담고 있지 않습니다.** 어떤 데이터베이스에 연결해야 하는지, 접속 정보(host/port/db/계정)는 무엇인지는 **저장소만 보고 알 수 없습니다.**

→ 연결 대상 DB와 접속 정보는 **프로젝트 관련 담당자에게 직접 문의**하세요. 받은 값은 로컬 `.env` 에만 채우고 절대 커밋하지 않습니다.

## 셋업 방법

```powershell
# 1) 템플릿 복사 후 담당자에게 받은 값으로 채우기
Copy-Item .env.example .env

# 2) 내부 MCP 서버를 local 스코프에 등록
make mcp-local
#   또는: pwsh ./tools/setup-local-mcp.ps1

# 3) Claude Code 재시작 또는 /mcp 로 재연결
```

`.env` 인식 규칙(`tools/setup-local-mcp.ps1`):

| `.env` 키 | 등록되는 서버 |
|-----------|---------------|
| `GITHUB_PERSONAL_ACCESS_TOKEN` | `github` |
| `POSTGRES_<NAME>_URL` | `postgres-<name>` (키 1개당 서버 1개) |

형식 예시는 `.env.example` 을 참고하세요. 실제 키 이름·개수는 환경에 맞게 정의합니다.

## 관련 파일

- `.mcp.json` — 공개 도구만 (커밋됨)
- `.env.example` — 내부 서버 비밀정보 템플릿
- `tools/setup-local-mcp.ps1` — local 스코프 등록 스크립트 (`make mcp-local`)
- `tools/mcp-launch.mjs` — 런타임에 `.env` 비밀값 주입

다음 문서: [README](./README.md) — 가이드 목차로 돌아가기.
