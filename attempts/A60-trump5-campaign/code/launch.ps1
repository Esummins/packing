# A60 detached launcher.  One process per call; writes a pid file and a per-job log.
param(
  [Parameter(Mandatory=$true)][string]$Job,      # falsify | cover | ladder | ladderscan
  [string]$Cond = "",
  [string]$Shard = "0/1",
  [int]$N = 12,
  [int]$Levels = 30,
  [double]$LpTime = 300,
  [double]$CertTime = 240,
  [double]$Wall = 1e9,
  [string]$Tag = ""
)
$py   = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$base = Split-Path -Parent $here
$j    = ($Cond.Split(',') | Where-Object { $_ -ne "" }).Count
$sh   = $Shard.Replace('/','-')
$name = "$Job`_j$j`_s$sh$Tag"
$log  = Join-Path $base "logs\$name.out"

switch ($Job) {
  "falsify"    { $script = "falsify60.py"; $argl = @("--cond",$Cond,"--n","$N","--shard",$Shard,"--lp_time","$LpTime","--cert_time","$CertTime","--wall","$Wall") }
  "cover"      { $script = "tree60.py";    $argl = @("cover","--cond",$Cond,"--shard",$Shard,"--lp_time","$LpTime","--cert_time","$CertTime","--wall","$Wall") }
  "ladder"     { $script = "tree60.py";    $argl = @("ladder","--cond",$Cond,"--shard",$Shard,"--levels","$Levels","--lp_time","$LpTime","--cert_time","$CertTime","--wall","$Wall") }
  "ladderscan" { $script = "tree60.py";    $argl = @("ladderscan","--cond",$Cond,"--levels","$Levels") }
  default      { throw "unknown job $Job" }
}
$all = @((Join-Path $here $script)) + $argl
$p = Start-Process -FilePath $py -ArgumentList $all -WorkingDirectory $base `
       -RedirectStandardOutput $log -RedirectStandardError "$log.err" -PassThru -WindowStyle Hidden
"$($p.Id)" | Out-File -Encoding ascii (Join-Path $base "progress\$name.pid")
Write-Output ("launched {0} pid {1} -> {2}" -f $name, $p.Id, $log)
