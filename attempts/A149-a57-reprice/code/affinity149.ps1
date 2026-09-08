# A149 -- keep every process of THIS attempt on the P-core threads (logical CPUs 0-15).
#
# The PI's box rule (coordinator, 2026-09-08): lab work is confined to affinity mask 0xFFFF; the
# E-cores (16-19) belong to the PI's remote session.  `run149.py` sets the mask on itself every
# loop pass and on every node child at launch, so this sweeper exists for two cases only:
#   * workers started BEFORE the rule (w2/w3, launched at 06:57 on the BelowNormal config) and
#     the children they spawn;
#   * anything that loses the mask.
#
# It touches ONLY processes whose command line names this attempt -- never another agent's
# workers, never a pidfile, never a sentinel.  It exits when no A149 python process is left.
param(
  [int]$SleepSec = 300,
  [int]$Mask = 0xFFFF
)
while ($true) {
  $procs = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
             Where-Object { $_.CommandLine -like '*A149-a57-reprice*' })
  if ($procs.Count -eq 0) {
    "$(Get-Date -Format 'HH:mm:ss') no A149 python process left; sweeper exits"
    break
  }
  $fixed = 0
  foreach ($p in $procs) {
    try {
      $o = Get-Process -Id $p.ProcessId -ErrorAction Stop
      if ([int64]$o.ProcessorAffinity -ne $Mask) {
        $o.ProcessorAffinity = [IntPtr]$Mask
        $fixed++
      }
    } catch { }
  }
  "$(Get-Date -Format 'HH:mm:ss') A149 python $($procs.Count), re-masked $fixed"
  Start-Sleep -Seconds $SleepSec
}
