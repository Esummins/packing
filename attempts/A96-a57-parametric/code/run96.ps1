# A96 self-gating launcher for the parametric pass.  Detached, single-instance, BLAS-pinned.
#   powershell -ExecutionPolicy Bypass -File code\run96.ps1
# param96.py itself holds the commit gate (6144 MB) and the >= 2-process cap, so this script only
# has to (a) pin BLAS for the whole child tree, (b) refuse to start a second copy, (c) detach.
param([int]$Procs = 2, [double]$NodeCap = 1500, [double]$GlobalCap = 1e9, [string]$Groups = "")
$base = Split-Path -Parent $PSScriptRoot
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"
$py = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
$pidFile = "$base\logs\param96.pid"
if (Test-Path $pidFile) {
  $prior = (Get-Content $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1) -as [int]
  if ($prior) {
    $p = Get-CimInstance Win32_Process -Filter "ProcessId=$prior" -ErrorAction SilentlyContinue
    # Match on the SCRIPT, not on the string "param96": a status check from a tool session names
    # the script in its own command line and would otherwise look like a running pass (this exact
    # false positive cost A57 two scalers -- see A57 notes/RESUME.md).
    if ($p -and $p.Name -like 'python*' -and $p.CommandLine -like '*code\param96.py*') {
      Write-Output "param96 already running (pid $prior)"; exit 0
    }
  }
}
$argl = @('-u', "$base\code\param96.py", '--procs', $Procs, '--node-cap', $NodeCap,
          '--global-cap', $GlobalCap)
if ($Groups -ne "") { $argl += @('--groups', $Groups) }
$proc = Start-Process -FilePath $py -ArgumentList $argl -WorkingDirectory $base `
        -RedirectStandardOutput "$base\logs\param96.out" `
        -RedirectStandardError "$base\logs\param96.err" -WindowStyle Hidden -PassThru
Set-Content -Path $pidFile -Value $proc.Id -Encoding utf8
Write-Output "param96 pid=$($proc.Id)"
