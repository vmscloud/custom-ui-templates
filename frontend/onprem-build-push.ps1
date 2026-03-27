$ErrorActionPreference = "Stop"

$IMAGE = "192.168.1.250:6007/mzc-custom-ui-frontend:latest"
$TOKEN_FILE = Join-Path $PSScriptRoot ".npm_token"

# 1. .npmrc에서 토큰 추출
$npmrc = Get-Content ".npmrc" -Raw
$match = [regex]::Match($npmrc, '_authToken=(.+)')
if (-not $match.Success) {
    Write-Error ".npmrc에서 authToken을 찾을 수 없습니다."
    exit 1
}
$match.Groups[1].Value.Trim() | Out-File -NoNewline -Encoding ascii $TOKEN_FILE

# 2. Docker 빌드
Write-Host "Building $IMAGE ..." -ForegroundColor Cyan
$env:DOCKER_BUILDKIT = 1
docker build --secret "id=npm_token,src=$TOKEN_FILE" -t $IMAGE .
if ($LASTEXITCODE -ne 0) {
    Remove-Item $TOKEN_FILE -ErrorAction SilentlyContinue
    Write-Error "Docker build failed."
    exit 1
}

# 3. Docker 푸시
Write-Host "Pushing $IMAGE ..." -ForegroundColor Cyan
docker push $IMAGE
if ($LASTEXITCODE -ne 0) {
    Remove-Item $TOKEN_FILE -ErrorAction SilentlyContinue
    Write-Error "Docker push failed."
    exit 1
}

# 4. 정리
Remove-Item $TOKEN_FILE -ErrorAction SilentlyContinue
Write-Host "Done!" -ForegroundColor Green
