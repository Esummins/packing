# A131 T3 supervisor: one shard of the in-vitro clipped-box LP, restarted if the per-node wall fires.
#   powershell -ExecutionPolicy Bypass -File code\run131.ps1 -Shard 0/2 -CpuHours 3
# BLAS pinned here for the whole child tree; BelowNormal is set by the worker (survives restarts).
# A57's PAUSE is NOT touched: the worker watches attempts\A131-pin-clip\PAUSE only.
param(
  [string]$Shard = "0/2",
  [double]$Cap = 240,
  [double]$Cap2 = 900,
  [double]$NodeWall = 2400,
  [double]$CpuHours = 3,
  [int]$MaxRestarts = 12
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
$log = "$base\logs\lp131_s$si.log"
$n = 0
while ($n -lt $MaxRestarts) {
  $n++
  Add-Content -Path $log -Value ("=== {0} start #{1} shard {2} ===" -f (Get-Date -Format 'HH:mm:ss'), $n, $Shard)
  & $py -u "$base\code\lp131.py" --shard $Shard --cap $Cap --cap2 $Cap2 --node-wall $NodeWall --cpu-hours $CpuHours *>> $log
  $code = $LASTEXITCODE
  Add-Content -Path $log -Value ("=== {0} exit {1} ===" -f (Get-Date -Format 'HH:mm:ss'), $code)
  if ($code -ne 3) { break }
  if (Test-Path "$base\PAUSE") { break }
}
Add-Content -Path $log -Value ("=== supervisor finished after {0} run(s) ===" -f $n)
