# A181 -- launch ONE renorm181 shard at BelowNormal / affinity 0xFFFF, BLAS pinned, waiting for a slot
# under the 16-lab-python box ceiling, and RELAUNCH it (resumable side files) after a per-node wall kill
# until it exits 0 (done) or 2 (sentinel).   Usage:  powershell -File launch176.ps1 <logname> <args...>
$ErrorActionPreference = 'Continue'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:OPENBLAS_NUM_THREADS = '1'; $env:OMP_NUM_THREADS = '1'; $env:MKL_NUM_THREADS = '1'
$py   = 'C:\Users\esumm\AppData\Local\Python\bin\python.exe'
$code = 'C:\Users\esumm\code\packing\attempts\A168-cascade-fable\code'
$logs = 'C:\Users\esumm\code\packing\attempts\A168-cascade-fable\logs'
Set-Location $code
$name = $args[0]
$rest = $args[1..($args.Count - 1)]
function WaitSlot($need) {
  for ($k = 0; $k -lt 360; $k++) {
    # every lab python counts (shards launched with a RELATIVE script path carry no 'packing' in
    # their command line): all python.exe minus the Claude-extension venv ones
    $n = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
           Where-Object { -not ($_.CommandLine -like '*Claude Extensions*') }).Count
    $os = Get-CimInstance Win32_OperatingSystem
    $free = [math]::Round($os.FreePhysicalMemory / 1KB, 0)
    if (($n + $need) -le 16 -and $free -ge 3072) { Write-Output ("slot ok: lab-python={0} freeMB={1}" -f $n, $free); return $true }
    Start-Sleep -Seconds 30
  }
  Write-Output ("SKIPPED: no slot after 3 h (lab-python={0})" -f $n)
  return $false
}
for ($round = 0; $round -lt 40; $round++) {
  if (-not (WaitSlot 1)) { exit 1 }
  $argv = @('-u', 'renorm181.py') + $rest
  $p = Start-Process -FilePath $py -ArgumentList $argv -NoNewWindow -PassThru `
        -RedirectStandardOutput "$logs\$name.r$round.log" -RedirectStandardError "$logs\$name.r$round.err"
  $p.ProcessorAffinity = 0xFFFF
  $p.PriorityClass = 'BelowNormal'
  Write-Output ("{0} round {1} pid {2} started" -f $name, $round, $p.Id)
  $p.WaitForExit()
  Write-Output ("{0} round {1} exit {2}" -f $name, $round, $p.ExitCode)
  if ($p.ExitCode -eq 0 -or $p.ExitCode -eq 2) { break }
  Start-Sleep -Seconds 10
}
