# A166 -- the two LP shards.  BelowNormal, affinity 0xFFFF, PYTHONDONTWRITEBYTECODE=1, a global
# deadline per shard so the total stays inside the 3 CPU-h cap; every sentinel honoured by lp166.py
# itself.  The box ceiling is 16 LAB python processes: wait for a slot, never exceed it.
$ErrorActionPreference = 'Continue'
$env:PYTHONDONTWRITEBYTECODE = '1'
$py   = 'C:\Users\esumm\AppData\Local\Python\bin\python.exe'
$code = 'C:\Users\esumm\code\packing\attempts\A166-nearest-corner-subtree\code'
$logs = 'C:\Users\esumm\code\packing\attempts\A166-nearest-corner-subtree\logs'
$res  = 'C:\Users\esumm\code\packing\attempts\A166-nearest-corner-subtree\results'
Set-Location $code

$pad      = if ($args.Count -ge 1) { $args[0] } else { 'wmax' }
$deadline = if ($args.Count -ge 2) { $args[1] } else { '5100' }

function WaitSlot($need) {
  for ($k = 0; $k -lt 120; $k++) {
    $n = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
           Where-Object { $_.CommandLine -like '*code\packing\attempts*' }).Count
    $os = Get-CimInstance Win32_OperatingSystem
    $free = [math]::Round($os.FreePhysicalMemory / 1KB, 0)
    if (($n + $need) -le 16 -and $free -ge 3072) { Write-Output ("slot ok: lab-python={0} freeMB={1}" -f $n, $free); return $true }
    Start-Sleep -Seconds 20
  }
  Write-Output ("SKIPPED: no slot for {0} processes after 40 min (lab-python={1})" -f $need, $n)
  return $false
}

if (-not (WaitSlot 2)) { exit 1 }

$procs = @()
foreach ($s in 0, 1) {
  $argv = @('-u', 'lp166.py', '--list', "$res\nodes166_$pad.json", '--cap', '240',
            '--shard', "$s", '--nshards', '2', '--cert', '1', '--cert_time', '120',
            '--deadline', $deadline, '--out', "$res\lp166_${pad}_s$s.jsonl")
  $p = Start-Process -FilePath $py -ArgumentList $argv -NoNewWindow -PassThru `
        -RedirectStandardOutput "$logs\lp166_${pad}_s$s.log" -RedirectStandardError "$logs\lp166_${pad}_s$s.err"
  $p.ProcessorAffinity = 0xFFFF
  $p.PriorityClass = 'BelowNormal'
  $procs += $p
  Write-Output ("shard {0} pid {1} started" -f $s, $p.Id)
  Start-Sleep -Seconds 3
}
foreach ($p in $procs) { $p.WaitForExit(); Write-Output ("pid {0} exit={1}" -f $p.Id, $p.ExitCode) }
Write-Output 'A166 LP done'
