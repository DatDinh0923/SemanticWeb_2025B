$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$toolDir = Join-Path $repo 'tools'
New-Item -ItemType Directory -Force -Path $toolDir | Out-Null

function Download-Checked($url, $path, $algorithm, $expected) {
    if (-not (Test-Path -LiteralPath $path)) {
        & curl.exe --fail --location --silent --show-error --retry 2 --connect-timeout 20 --max-time 240 --output $path $url
        if ($LASTEXITCODE -ne 0) { throw "Download failed: $url" }
    }
    $actual = (Get-FileHash -LiteralPath $path -Algorithm $algorithm).Hash
    if ($actual -ne $expected) { throw "Checksum mismatch: $path. Remove this archive and run setup again." }
}

$javaZip = Join-Path $toolDir 'zulu21-jre.zip'
$javaUrl = 'https://cdn.azul.com/zulu/bin/zulu21.52.203-ca-jre21.0.12.1-win_x64.zip'
Download-Checked $javaUrl $javaZip 'SHA256' '37ad372b04da388c326f0507abec38b8e1d11e3bddf6128b215c8f0a06ff8177'
if (-not (Test-Path -LiteralPath (Join-Path $toolDir 'zulu21.52.203-ca-jre21.0.12.1-win_x64/bin/java.exe'))) {
    Expand-Archive -LiteralPath $javaZip -DestinationPath $toolDir
}

$fusekiZip = Join-Path $toolDir 'apache-jena-fuseki-6.2.0.zip'
$fusekiUrl = 'https://dlcdn.apache.org/jena/binaries/apache-jena-fuseki-6.2.0.zip'
$checksum = & curl.exe --fail --location --silent --show-error --max-time 60 ($fusekiUrl + '.sha512')
if ($LASTEXITCODE -ne 0) { throw 'Cannot retrieve Apache SHA512' }
$expected = [regex]::Match(($checksum -join ' '), '\b[0-9a-fA-F]{128}\b').Value
if (-not $expected) { throw 'Invalid Apache checksum response' }
Download-Checked $fusekiUrl $fusekiZip 'SHA512' $expected
if (-not (Test-Path -LiteralPath (Join-Path $toolDir 'apache-jena-fuseki-6.2.0/fuseki-server.jar'))) {
    Expand-Archive -LiteralPath $fusekiZip -DestinationPath $toolDir
}
Write-Host 'Portable Java 21 and Fuseki 6.2.0 ready. System Java unchanged.'
