$ErrorActionPreference = "Stop"

$IMAGE = "203.231.40.242:6007/mzc-custom-ui-frontend:latest"

# 1. Docker 빌드 (@vmscloud 패키지는 public npm 에서 받으므로 토큰이 필요 없다)
Write-Host "Building $IMAGE ..." -ForegroundColor Cyan
$env:DOCKER_BUILDKIT = 1
docker build -t $IMAGE .
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker build failed."
    exit 1
}

# 2. Docker 푸시
Write-Host "Pushing $IMAGE ..." -ForegroundColor Cyan
docker push $IMAGE
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker push failed."
    exit 1
}

Write-Host "Done!" -ForegroundColor Green
