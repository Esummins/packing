# A57 generic detached job launcher (deepen / sweepfails / certify / probes).
# Exists so every A57 worker gets the same single-thread BLAS pinning as launch.ps1 -- see the
# comment there: BLAS oversubscription, not RAM, is what killed a shard and a deepen job while
# ~10 GB was free.
#   powershell -File code\run_job.ps1 -Script deepen.py -JobArgs "--key k5_11_interior_L1 --levels 3" -Tag deepen_k5_11
param(
  [Parameter(Mandatory=$true)][string]$Script,
  [string]$JobArgs = "",
  [Parameter(Mandatory=$true)][string]$Tag
)
$base = Split-Path -Parent $PSScriptRoot
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
$py = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
$argl = @("-u", "$base\code\$Script")
if ($JobArgs) { $argl += ($JobArgs -split '\s+') }
$p = Start-Process -FilePath $py -ArgumentList $argl -WorkingDirectory $base `
     -RedirectStandardOutput "$base\logs\$Tag.out" -RedirectStandardError "$base\logs\$Tag.err" `
     -WindowStyle Hidden -PassThru
Set-Content -Path "$base\logs\$Tag.pid" -Value $p.Id -Encoding utf8
Write-Output "$Tag pid=$($p.Id)"
