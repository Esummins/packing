# A124 T1 supervisor: one shard of the ALIVE re-check, restarted when the per-node wall fires.
#   powershell -ExecutionPolicy Bypass -File code\run124.ps1 -Shard 0/2 -CpuHours 10 -Deadline 17:15
# BLAS is pinned here for the whole child tree; BelowNormal is set by the worker itself (so it
# survives restarts).  Exit code 3 from the worker means "watchdog killed a wedged node" -> loop.
param(
  [string]$Shard = "0/2",
  [double]$Cap = 900,
  [double]$NodeWall = 1500,
  [double]$CpuHours = 10,
  [string]$Deadline = "17:15",
  [int]$MaxRestarts = 40
)
$base = Split-Path -Parent $PSScriptRoot
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"
$py = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
$si = ($Shard -split "/")[0]
$log = "$base\logs\recheck124_s$si.log"
$n = 0
while ($n -lt $MaxRestarts) {
  $n++
  Add-Content -Path $log -Value ("=== {0} start #{1} shard {2} ===" -f (Get-Date -Format 'HH:mm:ss'), $n, $Shard)
  & $py -u "$base\code\recheck124.py" --shard $Shard --cap $Cap --node-wall $NodeWall `
        --cpu-hours $CpuHours --deadline $Deadline --trimmed *>> $log
  $code = $LASTEXITCODE
  Add-Content -Path $log -Value ("=== {0} exit {1} ===" -f (Get-Date -Format 'HH:mm:ss'), $code)
  if ($code -ne 3) { break }
  if (Test-Path "$base\PAUSE") { break }
}
Add-Content -Path $log -Value ("=== supervisor finished after {0} run(s) ===" -f $n)
