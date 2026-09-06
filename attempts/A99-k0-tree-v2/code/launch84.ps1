# A84 detached launcher (patterned on A60's launch.ps1 / launch60_reference.ps1).
# One process per call; writes a pid file under progress\ and per-job .out/.err logs under logs\.
#
# A57 T18: pin every worker to ONE BLAS thread.  numpy/OpenBLAS spawns ~one thread per core (20
# here) in EVERY process, each with its own allocation arenas; concurrent jobs multiply that
# until an allocation fails against fragmentation while GBs sit free.  Child processes
# (certify.py / verify_case.py) inherit these.  code/blas1.py sets the same in-process.
#
# COMMIT gate: the worker itself (tree84.wait_for_commit) polls available commit before EVERY LP
# and sleeps 60 s while it is under 6144 MB, logging each wait.  This launcher additionally
# refuses to START a job into a dip, and refuses to exceed 3 concurrent A84 LP processes.
param(
  [Parameter(Mandatory=$true)][string]$Job,   # census | cover | ladderscan | ladder | deepen | p1 | board | class
  [Parameter(Mandatory=$true)][string]$Cls,  # k4_08 | k3_05
  [string]$Cond = "",
  [string]$Shard = "0/1",
  [int]$Levels = 28,
  [int]$Sample = 0,
  [double]$LpTime = 600,
  [double]$CertTime = 300,
  [double]$Wall = 1e9,
  [string]$Source = "",
  [int]$Round = 1,
  [string]$Zone = "interior",
  [string]$Tag = "",
  [int]$MinFreeCommitMB = 6144,
  [int]$MaxSlots = 3,
  [switch]$NoGate
)
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS      = "1"
$env:MKL_NUM_THREADS      = "1"
$env:NUMEXPR_NUM_THREADS  = "1"
$py   = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$base = Split-Path -Parent $here
$j    = ($Cond.Split(',') | Where-Object { $_ -ne "" }).Count
$sh   = $Shard.Replace('/','-')
$name = "$Cls`_$Job`_j$j`_s$sh$Tag"
$log  = Join-Path $base "logs\$name.out"

# ---- slot accounting: count the A84 LP-capable workers already alive -----------------------
$lpJobs = @("cover","ladder","deepen","p1")
if ($lpJobs -contains $Job -and -not $NoGate) {
  $live = 0
  Get-ChildItem (Join-Path $base "progress") -Filter *.pid -ErrorAction SilentlyContinue | ForEach-Object {
    $pidv = (Get-Content $_.FullName -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($pidv) {
      $p = Get-Process -Id ([int]$pidv) -ErrorAction SilentlyContinue
      if ($p) { $live = $live + 1 }
    }
  }
  if ($live -ge $MaxSlots) { throw "A84 already has $live live workers (cap $MaxSlots) -- not launching $name" }
  $free = [int]((Get-CimInstance Win32_OperatingSystem).FreeVirtualMemory / 1024)
  if ($free -lt $MinFreeCommitMB) {
    Write-Output ("DEFER {0}: free commit {1} MB < {2} MB" -f $name, $free, $MinFreeCommitMB)
    exit 2
  }
  Write-Output ("gate ok: {0} live A84 workers, free commit {1} MB" -f $live, $free)
}

$condArg   = if ($Cond)   { @("--cond", $Cond) }     else { @() }
$srcArg    = if ($Source) { @("--source", $Source) } else { @() }
$sampleArg = if ($Sample -gt 0) { @("--sample", "$Sample") } else { @() }

switch ($Job) {
  "class"      { $script = "class84.py"; $argl = @("--cls", $Cls) }
  "census"     { $script = "tree84.py";  $argl = @("census") + @("--cls",$Cls) + $condArg + @("--zone",$Zone) }
  "ladderscan" { $script = "tree84.py";  $argl = @("ladderscan") + @("--cls",$Cls) + $condArg + @("--levels","$Levels","--zone",$Zone) }
  "p1"         { $script = "tree84.py";  $argl = @("p1") + @("--cls",$Cls,"--zone",$Zone,"--lp_time","$LpTime","--cert_time","$CertTime") }
  "cover"      { $script = "tree84.py";  $argl = @("cover") + @("--cls",$Cls) + $condArg + $sampleArg + @("--shard",$Shard,"--lp_time","$LpTime","--cert_time","$CertTime","--wall","$Wall","--zone",$Zone) }
  "ladder"     { $script = "tree84.py";  $argl = @("ladder") + @("--cls",$Cls) + $condArg + $sampleArg + @("--shard",$Shard,"--levels","$Levels","--lp_time","$LpTime","--cert_time","$CertTime","--wall","$Wall") }
  "deepen"     { $script = "tree84.py";  $argl = @("deepen") + @("--cls",$Cls) + $condArg + $srcArg + @("--round","$Round","--shard",$Shard,"--lp_time","$LpTime","--cert_time","$CertTime","--wall","$Wall") }
  "board"      { $script = "tree84.py";  $argl = @("board") + @("--cls",$Cls) }
  default      { throw "unknown job $Job" }
}
$all = @((Join-Path $here $script)) + $argl
$p = Start-Process -FilePath $py -ArgumentList $all -WorkingDirectory $base `
       -RedirectStandardOutput $log -RedirectStandardError "$log.err" -PassThru -WindowStyle Hidden
"$($p.Id)" | Out-File -Encoding ascii (Join-Path $base "progress\$name.pid")
Write-Output ("launched {0} pid {1} -> {2}" -f $name, $p.Id, $log)
