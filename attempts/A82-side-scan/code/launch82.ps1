# A82 detached scan-chain launcher (A57 launch.ps1 pattern).
#   powershell -File code\launch82.ps1 -Chain A -Classes k4_08,k4_03,k3_05
# Pins BLAS to one thread per worker: these jobs are LP + numpy-oracle work, not BLAS-bound,
# but numpy/OpenBLAS otherwise spawns ~one thread per core in EVERY process and the per-thread
# arenas multiply until an allocation fails with gigabytes still free (A57 T18 / A60).
param(
  [string]$Chain = "A",
  [string[]]$Classes = @("k4_08"),
  [double]$LpTime = 600,
  [int]$MaxIter = 200,
  [double]$Headroom = 6.0,
  [double]$HeadroomWait = 7200,
  [string]$Tag = "",
  [string]$Sides = ""
)
$base = Split-Path -Parent $PSScriptRoot
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
$env:VECLIB_MAXIMUM_THREADS = "1"
$py = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
$cls = @($Classes | ForEach-Object { $_ -split "," } | Where-Object { $_ -ne "" })
$argl = @("$base\code\chain82.py", "--classes") + $cls + @(
  "--lp_time", $LpTime, "--max_iter", $MaxIter, "--headroom", $Headroom,
  "--headroom_wait", $HeadroomWait)
if ($Tag -ne "") { $argl += @("--tag", $Tag) }
if ($Sides -ne "") { $argl += @("--sides", $Sides) }
$argl = $argl | ForEach-Object { "$_" }
$p = Start-Process -FilePath $py -ArgumentList $argl -WorkingDirectory $base `
     -RedirectStandardOutput "$base\logs\chain$Chain.out" `
     -RedirectStandardError  "$base\logs\chain$Chain.err" `
     -WindowStyle Hidden -PassThru
Set-Content -Path "$base\logs\chain$Chain.pid" -Value $p.Id -Encoding utf8
Write-Output "chain$Chain pid=$($p.Id) classes=$($Classes -join ',')"
