# A57 detached shard launcher.  Usage:
#   powershell -File code\launch.ps1 -Name k5_11 -Shard 0/6 -Tag L1
param(
  [string]$Name = "k5_11",
  [string]$Zone = "interior",
  [string]$Shard = "0/6",
  [string]$Tag = "L1",
  [double]$TimeLimit = 240,
  [double]$CertTime = 240,
  [int]$Rounds = 2,
  [int]$Jobs = 2,
  [double]$Wall = 1000000,
  [int]$FoldCap = 9000,
  [int]$MaxRows = 30000
)
$base = Split-Path -Parent $PSScriptRoot
# Pin BLAS to one thread per worker.  These jobs are LP + numpy-oracle work, not BLAS-bound, but
# numpy/OpenBLAS otherwise spawns ~one thread per core (20 here) in EVERY process, and several
# concurrent jobs multiply the per-thread arenas until an allocation fails with gigabytes still
# free.  Observed: a 76 MiB numpy allocation failed and an OpenBLAS retry loop gave up while
# 9.9 GB was free, killing one tree shard and one deepen job at once.  (A54 W7 saw the same class
# of failure and worked around it by pruning columns; this addresses the cause.)
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
$si = ($Shard -split "/")[0]
$stamp = "$($Name)_$($Zone)_$($Tag)_s$si"
$py = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
$argl = @("$base\code\tree57.py","--name",$Name,"--zone",$Zone,"--tag",$Tag,"--shard",$Shard,
          "--time_limit",$TimeLimit,"--cert_time",$CertTime,"--rounds",$Rounds,"--jobs",$Jobs,
          "--wall_seconds",$Wall,"--fold_cap",$FoldCap,"--max_rows",$MaxRows)
$p = Start-Process -FilePath $py -ArgumentList $argl -WorkingDirectory $base `
     -RedirectStandardOutput "$base\logs\$stamp.out" -RedirectStandardError "$base\logs\$stamp.err" `
     -WindowStyle Hidden -PassThru
Set-Content -Path "$base\logs\$stamp.pid" -Value $p.Id -Encoding utf8
Write-Output "$stamp pid=$($p.Id)"
