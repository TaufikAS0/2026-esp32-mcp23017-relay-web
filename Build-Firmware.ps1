param([string]$ArduinoCli = '')
$ErrorActionPreference = 'Stop'
$buildScript = Join-Path $PSScriptRoot 'scripts/build.py'
if ($ArduinoCli) { & python $buildScript --cli $ArduinoCli }
else { & python $buildScript }
if ($LASTEXITCODE -ne 0) { throw 'Build or identity verification failed' }
