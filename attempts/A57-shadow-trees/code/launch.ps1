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
