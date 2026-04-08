param(
    [ValidateSet("backend", "frontend", "all")]
    [string]$Service = "all",

    [string]$Tag = "custom",
    [string]$HostIP = "192.168.1.250",
    [int]$RegistryPort = 6007,
    [string]$GithubToken = $env:GITHUB_TOKEN,
    [switch]$NoCache
)

# 서비스별 이미지 매핑 (GitHub Actions 워크플로우 기준)
$services = @{
    backend  = @{ context = "backend";  image = "custom-ui-backend" }
    frontend = @{ context = "frontend"; image = "custom-ui-frontend" }
}

$targets = if ($Service -eq "all") { @("backend", "frontend") } else { @($Service) }

Write-Host "=== Custom UI Deploy (Internal Registry) ===" -ForegroundColor Cyan
Write-Host "  Registry: ${HostIP}:${RegistryPort}"
Write-Host "  Tag     : $Tag"
Write-Host "  Services: $($targets -join ', ')"
Write-Host ""

$step = 0
$totalSteps = $targets.Count * 2

foreach ($svc in $targets) {
    $cfg = $services[$svc]
    $fullImage = "${HostIP}:${RegistryPort}/$($cfg.image):${Tag}"

    if (-not (Test-Path "$($cfg.context)\Dockerfile")) {
        Write-Error "Dockerfile not found: $($cfg.context)\Dockerfile"
        exit 1
    }

    # Build
    $step++
    Write-Host "[$step/$totalSteps] Building $svc -> $fullImage" -ForegroundColor Yellow
    if ($svc -eq "frontend") {
        $tokenFile = [System.IO.Path]::GetTempFileName()
        try {
            [System.IO.File]::WriteAllText($tokenFile, $GithubToken)
            $cacheFlag = if ($NoCache) { "--no-cache" } else { "" }
            docker build $cacheFlag --secret "id=npm_token,src=$tokenFile" -t $fullImage $cfg.context
        } finally {
            Remove-Item $tokenFile -Force -ErrorAction SilentlyContinue
        }
    } else {
        $cacheFlag = if ($NoCache) { "--no-cache" } else { "" }
        docker build $cacheFlag -t $fullImage $cfg.context
    }
    if ($LASTEXITCODE -ne 0) {
        Write-Error "$svc build failed"
        exit 1
    }
    Write-Host "  Build OK" -ForegroundColor Green

    # Push
    $step++
    Write-Host "[$step/$totalSteps] Pushing $svc..." -ForegroundColor Yellow
    docker push $fullImage
    if ($LASTEXITCODE -ne 0) {
        Write-Error @"
$svc push failed. insecure-registries 설정을 확인하세요:
  Docker Desktop > Settings > Docker Engine:
  { "insecure-registries": ["${HostIP}:${RegistryPort}"] }
"@
        exit 1
    }
    Write-Host "  Push OK" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Done!" -ForegroundColor Cyan
foreach ($svc in $targets) {
    $cfg = $services[$svc]
    Write-Host "  $svc : ${HostIP}:${RegistryPort}/$($cfg.image):${Tag}" -ForegroundColor Green
}
