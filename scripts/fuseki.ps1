param([ValidateSet('start', 'stop', 'status')][string]$Action = 'status')
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$runtime = Join-Path $repo '.runtime'
$statePath = Join-Path $runtime 'fuseki-process.json'
$java = Join-Path $repo 'tools/zulu21.52.203-ca-jre21.0.12.1-win_x64/bin/java.exe'
$jar = Join-Path $repo 'tools/apache-jena-fuseki-6.2.0/fuseki-server.jar'
$config = Join-Path $repo 'fuseki/config.ttl'
$existing = $null
if (Test-Path -LiteralPath $statePath) {
    $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    $candidate = Get-Process -Id $state.processId -ErrorAction SilentlyContinue
    if ($candidate -and $candidate.StartTime.ToUniversalTime().ToString('o') -eq $state.startedAt -and $candidate.Path -eq $java) {
        $command = (Get-CimInstance Win32_Process -Filter "ProcessId = $($candidate.Id)").CommandLine
        if ($command.Contains($jar) -and $command.Contains($config)) { $existing = $candidate }
    }
}
if ($Action -eq 'status') {
    if ($existing) { Write-Host "Running PID $($existing.Id): http://localhost:3035/" }
    else { Write-Host 'Stopped' }
    exit 0
}
if ($Action -eq 'stop') {
    if ($existing) { Stop-Process -Id $existing.Id; Write-Host 'Stopped phongph5 Fuseki. TDB2 data retained.' }
    else { Write-Host 'No owned Fuseki process to stop.' }
    exit 0
}
if ($existing) { Write-Host 'Already running'; exit 0 }
if (-not (Test-Path -LiteralPath $java) -or -not (Test-Path -LiteralPath $jar)) { throw 'Run scripts/setup-tools.ps1 first.' }
if (Get-NetTCPConnection -LocalPort 3035 -State Listen -ErrorAction SilentlyContinue) { throw 'Port 3035 is already occupied.' }
New-Item -ItemType Directory -Force -Path $runtime | Out-Null
$env:FUSEKI_BASE = Join-Path $runtime 'fuseki-base'
$env:FUSEKI_HOME = Split-Path -Parent $jar
$arguments = @('-Xmx1g', '-jar', ('"' + $jar + '"'), '--localhost', '--port=3035', ('--config="' + $config + '"'))
$process = Start-Process -FilePath $java -ArgumentList $arguments -WorkingDirectory $repo -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtime 'fuseki.stdout.log') -RedirectStandardError (Join-Path $runtime 'fuseki.stderr.log')
@{ processId=$process.Id; startedAt=$process.StartTime.ToUniversalTime().ToString('o') } | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
for ($i = 0; $i -lt 30; $i++) {
    if ($process.HasExited) { throw "Fuseki exited. See $runtime/fuseki.stderr.log" }
    try {
        & curl.exe --fail --silent --noproxy '*' --max-time 1 'http://localhost:3035/$/ping' | Out-Null
        if ($LASTEXITCODE -ne 0) { throw 'Not ready yet' }
        Write-Host 'Ready: http://localhost:3035/ ; dataset phongph5'
        exit 0
    } catch { Start-Sleep -Milliseconds 500 }
}
throw "Startup timeout. See $runtime/fuseki.stderr.log"
