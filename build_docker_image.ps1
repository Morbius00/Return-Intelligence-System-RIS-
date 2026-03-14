param(
    [string]$ImageName = "ris-api",
    [string]$Tag = "latest"
)

$fullTag = "$ImageName`:$Tag"

Write-Host "Building Docker image: $fullTag" -ForegroundColor Cyan
docker build -t $fullTag .

if ($LASTEXITCODE -eq 0) {
    Write-Host "Docker image created successfully: $fullTag" -ForegroundColor Green
} else {
    Write-Host "Docker image build failed." -ForegroundColor Red
    exit $LASTEXITCODE
}
