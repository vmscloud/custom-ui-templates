param(
    [ValidateSet("backend", "frontend", "all")]
    [string]$Service = "all",

    [string]$Tag = "custom",
    [string]$HostIP = "203.231.40.243",
    [int]$RegistryPort = 6007,
    [switch]$NoCache
)

# PowerShell 버전 감지 (PS5.1 / PS7+ 모두 지원)
$script:IsPwsh7 = $PSVersionTable.PSVersion.Major -ge 7

# PS5.1은 빈 문자열 인자를 native exe에 그대로 전달하므로 조건별 분기 호출,
# PS7+는 배열 splatting으로 깔끔히 처리
function Invoke-DockerBuild {
    param(
        [Parameter(Mandatory)] [string]$Image,
        [Parameter(Mandatory)] [string]$Context,
        [switch]$NoCache
    )

    if ($script:IsPwsh7) {
        $buildArgs = @("build")
        if ($NoCache) { $buildArgs += "--no-cache" }
        $buildArgs += @("-t", $Image, $Context)
        & docker @buildArgs
        return
    }

    # PowerShell 5.x: 각 플래그 조합별 명시 호출
    if ($NoCache) {
        docker build --no-cache -t $Image $Context
    } else {
        docker build -t $Image $Context
    }
}

function Write-DeployError {
    param(
        [Parameter(Mandatory)] [string]$Title,
        [string[]]$Details = @(),
        [string[]]$Fixes = @(),
        [string[]]$Hints = @()
    )
    $line = ("=" * 72)
    Write-Host ""
    Write-Host $line -ForegroundColor Red
    Write-Host "[ERROR] $Title" -ForegroundColor Red
    Write-Host $line -ForegroundColor Red
    if ($Details.Count -gt 0) {
        Write-Host ""
        Write-Host "원인/진단:" -ForegroundColor Yellow
        foreach ($d in $Details) { Write-Host "  - $d" -ForegroundColor Gray }
    }
    if ($Fixes.Count -gt 0) {
        Write-Host ""
        Write-Host "해결 방법:" -ForegroundColor Yellow
        $i = 1
        foreach ($f in $Fixes) {
            Write-Host ("  {0}. {1}" -f $i, $f) -ForegroundColor White
            $i++
        }
    }
    if ($Hints.Count -gt 0) {
        Write-Host ""
        Write-Host "참고:" -ForegroundColor Yellow
        foreach ($h in $Hints) { Write-Host "  * $h" -ForegroundColor DarkGray }
    }
    Write-Host $line -ForegroundColor Red
    Write-Host ""
}

function Test-InsecureRegistryConfigured {
    param([Parameter(Mandatory)] [string]$Endpoint)

    $daemonJson = Join-Path $env:USERPROFILE ".docker\daemon.json"
    if (-not (Test-Path $daemonJson)) {
        return [pscustomobject]@{ Configured = $false; Path = $daemonJson; Current = @(); Exists = $false }
    }
    try {
        $raw = Get-Content $daemonJson -Raw -ErrorAction Stop
        $json = $raw | ConvertFrom-Json -ErrorAction Stop
        $current = @()
        if ($json.PSObject.Properties.Name -contains 'insecure-registries') {
            $current = @($json.'insecure-registries')
        }
        return [pscustomobject]@{
            Configured = ($current -contains $Endpoint)
            Path       = $daemonJson
            Current    = $current
            Exists     = $true
        }
    } catch {
        return [pscustomobject]@{ Configured = $false; Path = $daemonJson; Current = @(); Exists = $true; ParseError = $_.Exception.Message }
    }
}

# 서비스별 이미지 매핑 (GitHub Actions 워크플로우 기준)
$services = @{
    backend  = @{ context = "backend";  image = "custom-ui-backend" }
    frontend = @{ context = "frontend"; image = "custom-ui-frontend" }
}

$targets = if ($Service -eq "all") { @("backend", "frontend") } else { @($Service) }

Write-Host "=== Custom UI Deploy (Internal Registry) ===" -ForegroundColor Cyan
Write-Host "  PowerShell: $($PSVersionTable.PSVersion)"
Write-Host "  Registry  : ${HostIP}:${RegistryPort}"
Write-Host "  Tag       : $Tag"
Write-Host "  Services  : $($targets -join ', ')"
Write-Host ""

$step = 0
$totalSteps = $targets.Count * 2

foreach ($svc in $targets) {
    $cfg = $services[$svc]
    $fullImage = "${HostIP}:${RegistryPort}/$($cfg.image):${Tag}"

    $dockerfilePath = Join-Path $cfg.context "Dockerfile"
    if (-not (Test-Path $dockerfilePath)) {
        Write-DeployError `
            -Title "Dockerfile을 찾을 수 없습니다 ($svc)" `
            -Details @(
                "기대 경로: $((Resolve-Path -Path . -ErrorAction SilentlyContinue).Path)\$dockerfilePath",
                "현재 작업 디렉터리: $(Get-Location)"
            ) `
            -Fixes @(
                "저장소 루트(custom-ui-templates)에서 스크립트를 실행했는지 확인하세요.",
                "$($cfg.context)\ 디렉터리가 존재하고 그 안에 Dockerfile이 있는지 확인하세요.",
                "git status 로 누락/삭제된 파일이 있는지 점검하세요."
            )
        exit 1
    }

    # Build
    $step++
    Write-Host "[$step/$totalSteps] Building $svc -> $fullImage" -ForegroundColor Yellow
    Invoke-DockerBuild -Image $fullImage -Context $cfg.context -NoCache:$NoCache
    if ($LASTEXITCODE -ne 0) {
        $buildExitCode = $LASTEXITCODE
        $commonCauses = @(
            "Dockerfile 내 명령 실패 (RUN 스텝이 0이 아닌 코드로 종료)",
            "베이스 이미지 pull 실패 (네트워크/프록시/rate-limit)",
            "빌드 컨텍스트 파일 누락 또는 .dockerignore 누락 항목",
            "디스크 공간 부족 또는 BuildKit 캐시 손상"
        )
        if ($svc -eq "frontend") {
            $commonCauses += "npm 의존성 resolve 실패 (pnpm-lock.yaml 불일치 또는 npm 레지스트리 접근 불가)"
        }
        Write-DeployError `
            -Title "$svc 이미지 빌드 실패 (docker build exit=$buildExitCode)" `
            -Details $commonCauses `
            -Fixes @(
                "위쪽 docker 출력에서 실제 실패 스텝을 확인하세요 (보통 'ERROR [스텝 N/M]' 라인).",
                "캐시 문제 의심 시 --NoCache 플래그로 재실행:  .\deploy-custom-ui.ps1 -Service $svc -NoCache",
                "BuildKit 상세 로그:  `$env:BUILDKIT_PROGRESS = 'plain' 후 재실행",
                "Docker 데몬 상태 확인:  docker info",
                "디스크 정리:  docker system prune -af"
            ) `
            -Hints @(
                "빌드 컨텍스트: $((Resolve-Path $cfg.context -ErrorAction SilentlyContinue).Path)",
                "이미지 태그: $fullImage"
            )
        exit 1
    }
    Write-Host "  Build OK" -ForegroundColor Green

    # Push
    $step++
    Write-Host "[$step/$totalSteps] Pushing $svc..." -ForegroundColor Yellow
    docker push $fullImage
    if ($LASTEXITCODE -ne 0) {
        $pushExitCode = $LASTEXITCODE
        $endpoint = "${HostIP}:${RegistryPort}"
        $check = Test-InsecureRegistryConfigured -Endpoint $endpoint

        $details = @(
            "대상 레지스트리: $endpoint",
            "이미지: $fullImage"
        )
        if (-not $check.Exists) {
            $details += "daemon.json 없음: $($check.Path)"
            $details += "→ Docker는 기본적으로 모든 레지스트리에 HTTPS를 요구하므로 HTTP 레지스트리로의 push가 거부됩니다."
        } elseif ($check.PSObject.Properties.Name -contains 'ParseError') {
            $details += "daemon.json 파싱 실패: $($check.ParseError)"
        } elseif (-not $check.Configured) {
            $currentList = if ($check.Current.Count -gt 0) { $check.Current -join ', ' } else { '(비어있음)' }
            $details += "daemon.json의 insecure-registries 에 $endpoint 가 없음"
            $details += "현재 등록된 값: $currentList"
        } else {
            $details += "insecure-registries 에는 등록되어 있음 → 네트워크/레지스트리 서비스 문제 가능성"
        }

        $fixes = @()
        if (-not $check.Configured) {
            $fixes += "Docker Desktop > Settings > Docker Engine 에서 아래 JSON 추가 후 'Apply & Restart':"
            $fixes += "     { `"insecure-registries`": [`"$endpoint`"] }"
            $fixes += "또는 $($check.Path) 직접 수정 후 Docker Desktop 재시작"
        }
        $fixes += "레지스트리 서버 응답 확인:  curl http://$endpoint/v2/"
        $fixes += "네트워크 연결 확인:  Test-NetConnection -ComputerName $HostIP -Port $RegistryPort"
        $fixes += "인증 필요 시:  docker login $endpoint"

        Write-DeployError `
            -Title "$svc 이미지 푸시 실패 (docker push exit=$pushExitCode)" `
            -Details $details `
            -Fixes $fixes `
            -Hints @(
                "insecure-registries 변경 후에는 반드시 Docker Desktop 재시작이 필요합니다 (데몬이 시작 시점에만 값을 읽음).",
                "HostIP 기본값이 작업 환경과 다르면 -HostIP 파라미터로 override:  .\deploy-custom-ui.ps1 -HostIP 192.168.x.x"
            )
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
