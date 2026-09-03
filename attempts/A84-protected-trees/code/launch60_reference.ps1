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
# A57 T18 (adopted 2026-09-01): pin every worker to ONE BLAS thread.  numpy/OpenBLAS spawns ~one
# thread per core (20 here) in EVERY process, each with its own allocation arenas; concurrent jobs
# multiply that until an allocation fails against fragmentation while GBs sit free.  Measured
# twice: A57 lost a shard and a deepen job to a 76.3 MiB failure at 9.9 GB free; A60 cover shard
# 1/2 died on 66.6 MiB at 9.1 GB free.  These jobs are LP + numpy-oracle work, not BLAS-bound, so
# the parallelism bought nothing.  Child processes (certify.py / verify_case.py) inherit these.
# code/blas1.py sets the same variables in-process, for workers started by hand.
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
$py   = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$base = Split-Path -Parent $here
$j    = ($Cond.Split(',') | Where-Object { $_ -ne "" }).Count
$sh   = $Shard.Replace('/','-')
$name = "$Job`_j$j`_s$sh$Tag"
$log  = Join-Path $base "logs\$name.out"

# PowerShell drops "" from an array literal, which silently shifts every later argument
# (measured: -Cond "" turned --shard into the value of --cond).  Pass it only when set.
$condArg = if ($Cond) { @("--cond", $Cond) } else { @() }

switch ($Job) {
  "falsify"    { $script = "falsify60.py"; $argl = $condArg + @("--n","$N","--shard",$Shard,"--lp_time","$LpTime","--cert_time","$CertTime","--wall","$Wall") }
  "cover"      { $script = "tree60.py";    $argl = @("cover") + $condArg + @("--shard",$Shard,"--lp_time","$LpTime","--cert_time","$CertTime","--wall","$Wall") }
  "ladder"     { $script = "tree60.py";    $argl = @("ladder") + $condArg + @("--shard",$Shard,"--levels","$Levels","--lp_time","$LpTime","--cert_time","$CertTime","--wall","$Wall") }
  "ladderscan" { $script = "tree60.py";    $argl = @("ladderscan") + $condArg + @("--levels","$Levels") }
  default      { throw "unknown job $Job" }
}
$all = @((Join-Path $here $script)) + $argl
$p = Start-Process -FilePath $py -ArgumentList $all -WorkingDirectory $base `
       -RedirectStandardOutput $log -RedirectStandardError "$log.err" -PassThru -WindowStyle Hidden
"$($p.Id)" | Out-File -Encoding ascii (Join-Path $base "progress\$name.pid")
Write-Output ("launched {0} pid {1} -> {2}" -f $name, $p.Id, $log)
