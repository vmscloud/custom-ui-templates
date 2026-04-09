# Backend Mock Server (DB 연결 없이 캡처된 데이터로 응답)
Set-Location $PSScriptRoot
& .venv\Scripts\Activate.ps1
$env:USE_MOCK = "true"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
