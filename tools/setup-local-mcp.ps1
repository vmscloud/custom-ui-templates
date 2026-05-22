#!/usr/bin/env pwsh
# 내부 MCP 서버(github, postgres)를 Claude Code 의 "local 스코프"에 등록.
#
# 왜 local 스코프인가:
#   이 저장소(custom-ui-templates)는 공개 레포다. 내부 DB 종류·개수·이름이
#   공개 .mcp.json 에 드러나면 안 되므로, 내부 서버는 커밋되지 않는 local 스코프
#   (~/.claude.json, 레포 밖)에만 등록한다.
#
# 노출 안전성:
#   - 서버 정의/DB 이름/개수는 전부 .env 에서만 옴 (이 스크립트엔 하드코딩 없음).
#   - 비밀값(토큰/접속문자열)은 {{VAR}} 플레이스홀더로만 등록되고, 런타임에
#     tools/mcp-launch.mjs 가 .env 에서 주입한다. 따라서 ~/.claude.json 에도
#     비밀이 저장되지 않는다.
#
# 사용: make mcp-local   (또는  pwsh ./tools/setup-local-mcp.ps1)
#   .env 는 .env.example 을 복사해 채운다.

[Console]::OutputEncoding = [Text.Encoding]::UTF8

$root    = Split-Path $PSScriptRoot -Parent   # 프로젝트 루트 (tools/ 의 상위)
$envFile = Join-Path $root '.env'

if (-not (Test-Path $envFile)) {
    Write-Host '.env 가 없습니다. 먼저 템플릿을 복사해 채우세요:' -ForegroundColor Yellow
    Write-Host '  Copy-Item .env.example .env' -ForegroundColor Yellow
    exit 1
}
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Host 'claude CLI 가 PATH 에 없습니다. Claude Code 설치를 확인하세요.' -ForegroundColor Red
    exit 1
}

# --- .env 파싱 (KEY=VALUE, # 주석) ---
$envVars = [ordered]@{}
foreach ($line in Get-Content $envFile) {
    $t = $line.Trim()
    if (-not $t -or $t.StartsWith('#')) { continue }
    $i = $t.IndexOf('=')
    if ($i -lt 1) { continue }
    $envVars[$t.Substring(0, $i).Trim()] = $t.Substring($i + 1).Trim()
}

# 절대 경로(로컬 스코프는 cwd 보장이 약하므로 절대경로로 등록)
$launcher = Join-Path $root 'tools\mcp-launch.mjs'
$pgEntry  = Join-Path $root 'tools\node_modules\@modelcontextprotocol\server-postgres\dist\index.js'
$ghEntry  = Join-Path $root 'tools\node_modules\@modelcontextprotocol\server-github\dist\index.js'

function Add-LocalServer {
    param([string]$Name, [string[]]$Cmd)
    # idempotent: 기존 등록 제거 후 재등록
    & claude mcp remove --scope local $Name 2>$null | Out-Null
    $addArgs = @('mcp', 'add', '--scope', 'local', $Name, '--') + $Cmd
    & claude @addArgs
    if ($LASTEXITCODE -ne 0) { throw "claude mcp add 실패: $Name" }
    Write-Host ("  등록: {0}" -f $Name) -ForegroundColor Green
}

Write-Host ''
Write-Host '=== 내부 MCP 서버 local 스코프 등록 ===' -ForegroundColor Cyan
$count = 0

# GitHub: 토큰이 있으면 등록 (토큰은 런처가 .env 에서 child 환경으로 주입)
if ($envVars.Contains('GITHUB_PERSONAL_ACCESS_TOKEN')) {
    Add-LocalServer -Name 'github' -Cmd @('node', $launcher, '--', 'node', $ghEntry)
    $count++
}

# Postgres: POSTGRES_<NAME>_URL 키마다 등록. 서버명은 키에서 파생.
#   POSTGRES_MZC_COM_URL -> postgres-mzc-com  (URL 은 {{KEY}} 로만 등록 → .env 에서 주입)
foreach ($key in $envVars.Keys) {
    if ($key -match '^POSTGRES_(.+)_URL$') {
        $name = 'postgres-' + ($matches[1].ToLower() -replace '_', '-')
        Add-LocalServer -Name $name -Cmd @('node', $launcher, '--', 'node', $pgEntry, "{{$key}}")
        $count++
    }
}

Write-Host ''
if ($count -eq 0) {
    Write-Host '.env 에서 인식된 내부 서버 키가 없습니다 (.env.example 의 규칙 참고).' -ForegroundColor Yellow
} else {
    Write-Host ("완료: local 스코프에 MCP 서버 {0}개 등록 (~/.claude.json, 레포 밖)" -f $count) -ForegroundColor Cyan
    Write-Host '적용하려면 Claude Code 를 재시작하거나 /mcp 로 재연결하세요.'
}
