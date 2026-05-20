#!/usr/bin/env pwsh
# 개발 환경 사전 요구사항 점검 스크립트
#   Makefile 의 `make check` 및 `make install`(선행 단계) 에서 호출됩니다.
#   누락된 필수 도구가 있으면 "왜 필요한지 + 설치 방법"을 표준 출력으로 안내하고
#   비정상 종료(exit 1)하여 make install 이 알 수 없는 에러로 죽기 전에 멈춥니다.
#
#   프론트엔드 패키지 매니저는 환경변수 PM 으로 선택 (기본 pnpm). 예) make check PM=npm
#
#   주의: 이 파일은 Windows PowerShell 5.1(make 의 SHELL) 이 한글을 올바로 읽도록
#   반드시 UTF-8 BOM 으로 저장해야 합니다.

[Console]::OutputEncoding = [Text.Encoding]::UTF8

$PM = if ($env:PM) { $env:PM } else { 'pnpm' }
$script:missing = @()

function Test-Tool {
    param(
        [string]$Name,                 # 점검할 명령어
        [string]$Why,                  # 왜 필요한지
        [string]$Install,              # 설치 방법
        [string]$Url = '',             # 참고 링크
        [string]$VersionArg = '--version',
        [bool]$Required = $true
    )
    if (Get-Command $Name -ErrorAction SilentlyContinue) {
        $ver = ''
        try { $ver = (& $Name $VersionArg 2>$null | Select-Object -First 1) } catch {}
        Write-Host ("  [OK]  {0,-7} {1}" -f $Name, $ver) -ForegroundColor Green
        return
    }
    $tag = if ($Required) { '[필수]' } else { '[선택]' }
    Write-Host ("  [X]   {0,-7} 없음  {1}" -f $Name, $tag) -ForegroundColor Red
    Write-Host ("          쓰임 : {0}" -f $Why)
    Write-Host ("          설치 : {0}" -f $Install)
    if ($Url) { Write-Host ("          참고 : {0}" -f $Url) }
    if ($Required) { $script:missing += $Name }
}

Write-Host ''
Write-Host '=== 개발 환경 사전 요구사항 점검 ===' -ForegroundColor Cyan
Write-Host ''

# node / npm — tools/ MCP 서버(node 직접 실행) + npm ci, 그리고 PM=npm 일 때 프론트
Test-Tool -Name 'node' -Why 'tools/ MCP 서버 실행(.mcp.json)·프론트엔드 빌드' -Install 'winget install OpenJS.NodeJS.LTS   (또는 https://nodejs.org 에서 LTS 설치)' -Url 'https://nodejs.org'
Test-Tool -Name 'npm' -Why 'tools/ MCP 의존성 설치 (npm ci)' -Install 'Node.js 설치 시 자동 포함 (위 node 설치)' -Url 'https://nodejs.org'

# 프론트엔드 패키지 매니저 (PM 에 따라 선택)
if ($PM -eq 'pnpm') {
    Test-Tool -Name 'pnpm' -Why '프론트엔드 의존성 설치/빌드 (기본 패키지 매니저)' -Install 'corepack enable; corepack prepare pnpm@latest --activate   (또는 npm install -g pnpm)' -Url 'https://pnpm.io/installation'
} else {
    Write-Host ("  [i]   PM={0} 사용 — pnpm 점검 생략 (npm 으로 프론트 설치)" -f $PM) -ForegroundColor DarkGray
}

# uv / uvx — 백엔드(uv sync) + serena MCP 서버(uvx)
Test-Tool -Name 'uv' -Why '백엔드 의존성 설치 (uv sync --dev)' -Install 'winget install astral-sh.uv   (또는 pip install uv)' -Url 'https://docs.astral.sh/uv/getting-started/installation/'
Test-Tool -Name 'uvx' -Why 'serena MCP 서버 실행(.mcp.json)' -Install 'uv 설치 시 자동 포함 (위 uv 설치)' -Url 'https://docs.astral.sh/uv'

# chrome-devtools MCP 런타임 안내 (설치 점검 대상 아님 — 도구 호출 시에만 필요)
Write-Host ''
Write-Host '  [i]   chrome-devtools MCP 도구 사용 시 디버그 모드 Chrome 필요:' -ForegroundColor DarkGray
Write-Host '          chrome.exe --remote-debugging-port=9222' -ForegroundColor DarkGray
Write-Host '          (MCP 서버 기동에는 불필요, 실제 도구 호출 때만 필요)' -ForegroundColor DarkGray

Write-Host ''
if ($script:missing.Count -gt 0) {
    Write-Host ("=== 누락된 필수 도구: {0} ===" -f ($script:missing -join ', ')) -ForegroundColor Red
    Write-Host '위 [설치] 안내대로 설치한 뒤 다시 `make install` 을 실행하세요.' -ForegroundColor Yellow
    exit 1
}
Write-Host '=== 모든 필수 도구 확인 완료. make install 진행 가능 ===' -ForegroundColor Green
exit 0
