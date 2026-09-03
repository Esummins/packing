# A82 detached certificate emission (one LP slot).
#   powershell -File code\launch_emit.ps1 -Cls k4_08 -Side 3877/1000
param(
  [string]$Cls = "k4_08",
  [string]$Side = "3877/1000",
  [int]$Depth = 60,
  [int]$CertDepth = 56,
  [int]$Rounds = 4,
  [double]$TimeLimit = 420,
  [double]$ScaleCap = 1.15,
  [double]$Headroom = 6.0,
  [double]$EpsGeo = 0.0
)
$base = Split-Path -Parent $PSScriptRoot
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
$py = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
$argl = @("$base\code\emit82.py", "--cls", $Cls, "--side", $Side, "--depth", "$Depth",
          "--cert_depth", "$CertDepth", "--rounds", "$Rounds", "--time_limit", "$TimeLimit",
          "--scale_cap", "$ScaleCap", "--headroom", "$Headroom")
if ($EpsGeo -gt 0) { $argl += @("--eps_geo", "$EpsGeo") }
$stamp = "emit_$($Cls)_$($Side -replace '/','_')"
$p = Start-Process -FilePath $py -ArgumentList $argl -WorkingDirectory $base `
     -RedirectStandardOutput "$base\logs\$stamp.out" `
     -RedirectStandardError  "$base\logs\$stamp.err" `
     -WindowStyle Hidden -PassThru
Set-Content -Path "$base\logs\$stamp.pid" -Value $p.Id -Encoding utf8
Write-Output "$stamp pid=$($p.Id)"
