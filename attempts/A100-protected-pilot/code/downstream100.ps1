# A100 downstream driver: everything after a class's cover leg, in one DETACHED process.
#   1. param100.py   -- A96 emission + frozen 4-D verify over W = [3.82, s0] on every s0 leaf
#   2. resolve100.py -- A96 resolver on the completed partials
#   3. tree84 ladderscan -- the EXACT residue ladder (the (D) leaves), no LP
#   4. tree84 deepen r1  -- level-2 descent on the cover resisters, at delta_pin = 1e-2
# One LP-capable child at a time; BLAS pinned; param100 self-gates on commit at 6144 MB.
param(
  [Parameter(Mandatory=$true)][string]$Cls,
  [int]$Levels = 26,
  [double]$DeepenWall = 5400,
  [double]$ParamNodeCap = 1500,
  [int]$Procs = 1,
  [double]$Delta2 = 0.01
)
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS      = "1"
$env:MKL_NUM_THREADS      = "1"
$env:NUMEXPR_NUM_THREADS  = "1"
$py   = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$base = Split-Path -Parent $here
Set-Location $base

function Step($name, $argv) {
  $log = Join-Path $base ("logs\down_{0}_{1}.out" -f $Cls, $name)
  ("=== {0} {1} start {2} ===" -f $Cls, $name, (Get-Date -Format s)) | Out-File -Append -Encoding utf8 $log
  & $py @argv *>&1 | Out-File -Append -Encoding utf8 $log
  ("=== {0} {1} end   {2} rc={3} ===" -f $Cls, $name, (Get-Date -Format s), $LASTEXITCODE) |
    Out-File -Append -Encoding utf8 $log
}

Step "param"      @((Join-Path $here "param100.py"), "--cls", $Cls, "--procs", "$Procs", "--node-cap", "$ParamNodeCap")
Step "resolve"    @((Join-Path $here "resolve100.py"))
Step "ladderscan" @((Join-Path $here "tree84.py"), "ladderscan", "--cls", $Cls, "--levels", "$Levels", "--zone", "interior")
Step "deepen"     @((Join-Path $here "tree84.py"), "deepen", "--cls", $Cls, "--round", "1", "--delta", "$Delta2", "--lp_time", "600", "--cert_time", "300", "--wall", "$DeepenWall")
("A100 downstream done for {0} at {1}" -f $Cls, (Get-Date -Format s)) |
  Out-File -Append -Encoding utf8 (Join-Path $base ("logs\down_{0}_DONE.out" -f $Cls))
