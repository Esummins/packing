# A57 detached shard launcher.  Usage:
#   powershell -File code\launch.ps1 -Name k5_11 -Shard 0/6 -Tag L1
param(
  [string]$Name = "k5_11",
  [string]$Zone = "interior",
  [string]$Shard = "0/6",
  [string]$Tag = "L1",
  [string]$Side = "969271/250000",
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
$env:PYTHONDONTWRITEBYTECODE = "1"   # no __pycache__ writes from campaign workers
# --- A96 side freeze -------------------------------------------------------
# Sides 4/3/2 are not run as fixed-side trees any more (A96: parametric certificates cover the
# whole window at 0.062 of their cost).  The gate lives HERE, not only in scaleup.ps1's queue,
# because the scaler holds its queue in memory: a scaler started before the freeze would still
# walk into G4.  It re-invokes THIS script per launch, so the gate binds immediately and without
# restarting anything (restarting the scaler would reset its queue index and relaunch G1 shards).
# Exit 0, not 1: the scaler must treat a frozen entry as consumed and move on to the next one.
$freezeFile = "$PSScriptRoot\FREEZE_TAGS.txt"
if (Test-Path $freezeFile) {
  $frozen = @(Get-Content $freezeFile | ForEach-Object { $_.Trim() } |
              Where-Object { $_ -ne '' -and -not $_.StartsWith('#') })
  if ($frozen -contains $Tag) {
    $msg = "$([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss')) FROZEN: refusing to launch $Name $Tag side=$Side shard $Shard (code\FREEZE_TAGS.txt; A96 covers this side parametrically)"
    for ($k = 0; $k -lt 5; $k++) {
      try { Add-Content -Path "$base\logs\scaleup.log" -Value $msg -ErrorAction Stop; break } catch { Start-Sleep -Milliseconds 200 }
    }
    Write-Output "FROZEN $Name $Tag $Shard"
    exit 0
  }
}
$si = ($Shard -split "/")[0]
$stamp = "$($Name)_$($Zone)_$($Tag)_s$si"
$py = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
$argl = @("$base\code\tree57.py","--name",$Name,"--zone",$Zone,"--tag",$Tag,"--shard",$Shard,
          "--side",$Side,"--time_limit",$TimeLimit,"--cert_time",$CertTime,"--rounds",$Rounds,"--jobs",$Jobs,
          "--wall_seconds",$Wall,"--fold_cap",$FoldCap,"--max_rows",$MaxRows)
$p = Start-Process -FilePath $py -ArgumentList $argl -WorkingDirectory $base `
     -RedirectStandardOutput "$base\logs\$stamp.out" -RedirectStandardError "$base\logs\$stamp.err" `
     -WindowStyle Hidden -PassThru
Set-Content -Path "$base\logs\$stamp.pid" -Value $p.Id -Encoding utf8
Write-Output "$stamp pid=$($p.Id)"
