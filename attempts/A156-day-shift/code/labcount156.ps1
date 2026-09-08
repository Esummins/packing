# A156 -- count the LAB python processes on the box (the ceiling the coordinator set is 16).
#
# "Lab" = every python process on the box EXCEPT the harness's own (the windows-mcp servers under
# Claude Extensions).  It is defined by exclusion on purpose: several chores launch with a relative
# script path (`python t2_sweep.py --shard 0/2`, `python code/lp154.py`), so a filter on
# "*code\packing*" silently misses them and undercounts the box by half.
#
# Emits one integer on stdout (and, with -Detail, one line per process).
param([switch]$Detail)
$rows = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
          Where-Object { $_.CommandLine -and
                         $_.CommandLine -notlike '*Claude Extensions*' -and
                         $_.CommandLine -notlike '*windows-mcp*' })
if ($Detail) {
  foreach ($r in $rows) {
    $p = Get-Process -Id $r.ProcessId -ErrorAction SilentlyContinue
    $aff = if ($p) { "0x{0:X}" -f [int64]$p.ProcessorAffinity } else { "?" }
    $pri = if ($p) { $p.PriorityClass } else { "?" }
    "{0,6}  aff={1,-8} pri={2,-11} {3}" -f $r.ProcessId, $aff, $pri, ($r.CommandLine -replace '\s+', ' ').Substring(0, [Math]::Min(150, ($r.CommandLine -replace '\s+', ' ').Length))
  }
}
$rows.Count
