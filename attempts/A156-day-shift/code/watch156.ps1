# A156 -- compact watch loop: one line per pass, for -Minutes minutes, then exit.
#
# Per pass: the box's lab python count (ceiling 16), how many of them are A156's, this attempt's
# LP verdicts so far, the free physical/commit memory the LP gate tests, and any lab python
# process still missing the P-core mask (which it then sets).  It starts and stops nothing.
param(
  [string]$Base = "C:\Users\esumm\code\packing\attempts\A156-day-shift",
  [double]$Minutes = 9,
  [int]$EverySec = 180,
  [int64]$Mask = 0xFFFF
)
$py = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
$end = (Get-Date).AddMinutes($Minutes)
while ($true) {
  $rows = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
            Where-Object { $_.CommandLine -and $_.CommandLine -notlike '*Claude Extensions*' -and
                           $_.CommandLine -notlike '*windows-mcp*' })
  $lab = $rows.Count
  $mine = @($rows | Where-Object { $_.CommandLine -like '*A156-day-shift*' }).Count
  $nomask = 0
  foreach ($r in $rows) {
    $p = Get-Process -Id $r.ProcessId -ErrorAction SilentlyContinue
    if ($p -and [int64]$p.ProcessorAffinity -ne $Mask) {
      try { $p.ProcessorAffinity = [IntPtr]$Mask; $nomask++ } catch {}
    }
  }
  $res = @{}
  Get-ChildItem "$Base\results\lp156_*.jsonl" -ErrorAction SilentlyContinue | ForEach-Object {
    Get-Content $_ | ForEach-Object {
      if ($_ -match '"result":\s*"([^"]+)"') { $res[$matches[1]] = 1 + $res[$matches[1]] }
    }
  }
  $verd = ($res.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join " "
  $os = Get-CimInstance Win32_OperatingSystem
  $freeMB = [int]($os.FreePhysicalMemory / 1024)
  $commitMB = [int](($os.FreeVirtualMemory) / 1024)
  "{0} lab_py={1} (A156 {2}) | {3} | freePhys={4}MB | maskFixed={5}" -f (Get-Date -Format 'HH:mm:ss'), $lab, $mine, $verd, $freeMB, $nomask
  if ((Get-Date) -ge $end) { break }
  Start-Sleep -Seconds $EverySec
}
