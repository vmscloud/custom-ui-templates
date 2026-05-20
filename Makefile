.DEFAULT_GOAL := help

SHELL       := powershell.exe
.SHELLFLAGS := -NoProfile -Command

FRONTEND_DIR := frontend
BACKEND_DIR  := backend
TOOLS_DIR    := tools
CHECK_SCRIPT := check-prereqs.ps1

# 프론트엔드 패키지 매니저 (기본 pnpm). npm 사용 시: make install-frontend PM=npm
PM ?= pnpm

##@ General

.PHONY: help
help: ## 사용 가능한 명령어 목록 출력
	@[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-Content '$(firstword $(MAKEFILE_LIST))' -Encoding UTF8 | ForEach-Object { if ($$_ -match '^##@ (.*)') { ''; $$matches[1] } elseif ($$_ -match '^([a-zA-Z_-]+):.*?## (.*)') { '  {0,-20} {1}' -f $$matches[1], $$matches[2] } }

.PHONY: check
check: ## 사전 요구사항(node/npm/pnpm/uv) 점검 및 설치 가이드 출력
	$$env:PM='$(PM)'; & './$(CHECK_SCRIPT)'

##@ Install

.PHONY: install
install: check install-backend install-frontend install-tools ## 사전점검 후 프론트엔드 + 백엔드 + MCP 툴 의존성 모두 설치

.PHONY: install-frontend
install-frontend: ## 프론트엔드 의존성 설치 (기본 pnpm, PM=npm 으로 npm)
	Set-Location $(FRONTEND_DIR); $(PM) install

.PHONY: install-backend
install-backend: ## 백엔드 의존성 설치 (uv, dev 그룹 포함)
	Set-Location $(BACKEND_DIR); uv sync --dev

.PHONY: install-tools
install-tools: ## MCP 서버 의존성 설치 (.mcp.json 이 node 로 실행, lockfile 기반)
	Set-Location $(TOOLS_DIR); npm ci

.PHONY: mcp-local
mcp-local: ## 내부 MCP 서버(github/postgres)를 .env 기반으로 local 스코프에 등록 (공개 레포 미노출)
	& './$(TOOLS_DIR)/setup-local-mcp.ps1'

##@ Dev

.PHONY: dev-frontend
dev-frontend: ## 프론트엔드 개발 서버 실행 (vite, :5300)
	Set-Location $(FRONTEND_DIR); $(PM) run dev

.PHONY: dev-backend
dev-backend: ## 백엔드 개발 서버 실행 (uvicorn, :8000, reload)
	Set-Location $(BACKEND_DIR); uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

.PHONY: dev-mock
dev-mock: ## 백엔드 mock 서버 실행 (DB 연결 없이 캡처 데이터로 응답)
	Set-Location $(BACKEND_DIR); $$env:USE_MOCK='true'; uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

##@ Build

.PHONY: build
build: build-frontend ## 프로덕션 빌드 (프론트엔드)

.PHONY: build-frontend
build-frontend: ## 프론트엔드 프로덕션 빌드 (vue-tsc 타입체크 + vite build)
	Set-Location $(FRONTEND_DIR); $(PM) run build
