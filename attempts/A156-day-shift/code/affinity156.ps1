# A156 -- pin every LAB python process to the P-cores (logical CPUs 0-15, mask 0xFFFF).
#
# The PI's remote session owns CPUs 16-19 (the E-cores).  Windows children inherit their parent's
# affinity mask, so a worker launched with the mask covers the node child it spawns; this sweep is
# the hourly belt-and-braces pass over EVERY lab python process, including the other chores'
# (A149's re-emission, A151-A155's geometry) and anything they spawned before the rule landed.
#
# It only ever narrows an affinity mask.  It starts, stops and kills nothing, and it touches no
# pidfile and no sentinel.
param([int64]$Mask = 0xFFFF, [string]$LogFile = $null)
$changed = 0; $already = 0; $failed = 0
$rows = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
          Where-Object { $_.CommandLine -and
                         $_.CommandLine -notlike '*Claude Extensions*' -and
                         $_.CommandLine -notlike '*windows-mcp*' })
foreach ($r in $rows) {
  $p = Get-Process -Id $r.ProcessId -ErrorAction SilentlyContinue
  if (-not $p) { continue }
  try {
    if ([int64]$p.ProcessorAffinity -eq $Mask) { $already++ }
    else {
      $p.ProcessorAffinity = [IntPtr]$Mask
      $changed++
      $line = "{0} affinity 0x{1:X} -> 0x{2:X} pid {3} :: {4}" -f (Get-Date -Format 'HH:mm:ss'), [int64]$p.ProcessorAffinity, $Mask, $r.ProcessId, ($r.CommandLine -replace '\s+', ' ')
      if ($LogFile) { Add-Content -Path $LogFile -Value $line -Encoding utf8 }
    }
  } catch { $failed++ }
}
$msg = "{0} affinity sweep: {1} lab python, {2} set, {3} already 0x{4:X}, {5} failed" -f (Get-Date -Format 'HH:mm:ss'), $rows.Count, $changed, $already, $Mask, $failed
if ($LogFile) { Add-Content -Path $LogFile -Value $msg -Encoding utf8 }
$msg
