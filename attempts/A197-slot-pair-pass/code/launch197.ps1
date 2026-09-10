# A197 launcher: <= 2 python processes, BelowNormal, affinity 0xFFFF, PYTHONDONTWRITEBYTECODE=1.
#   powershell -NoProfile -File launch197.ps1 -Shard "1/2" -Wall 900 -Tag s1
param(
  [string]$Shard = "1/1",
  [int]$Wall = 900,
  [string]$Only = "",
  [string]$Tag = "run",
  [int]$Nsub = 8,
  [int]$Refine = 4
)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$att  = Split-Path -Parent $here
$logs = Join-Path $att "logs"
if (-not (Test-Path $logs)) { New-Item -ItemType Directory $logs | Out-Null }
$env:PYTHONDONTWRITEBYTECODE = "1"
$py = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
$argv = @("-u", "run197.py", "--shard", $Shard, "--wall", "$Wall", "--nsub", "$Nsub", "--refine", "$Refine")
if ($Only -ne "") { $argv += @("--only", $Only) }
$out = Join-Path $logs "$Tag.out"
$p = Start-Process -FilePath $py -ArgumentList $argv -WorkingDirectory $here `
       -RedirectStandardOutput $out -RedirectStandardError (Join-Path $logs "$Tag.err") `
       -PassThru -WindowStyle Hidden
Start-Sleep -Milliseconds 400
try { $p.PriorityClass = "BelowNormal"; $p.ProcessorAffinity = 0xFFFF } catch {}
"$($p.Id)" | Out-File -Encoding ascii (Join-Path $logs "$Tag.pid")
Write-Output "launched pid $($p.Id) shard $Shard -> $out"
