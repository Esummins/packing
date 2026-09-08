# A156 -- day-shift scaler.  Adds ONE worker per pass as the box allows, and re-pins affinity.
#
# Guards (all hard):
#   * exits the moment this attempt's PAUSE sentinel appears (it launches nothing after that);
#   * exits at -StopHM (no launches after it; the workers' own --deadline stops them starting nodes);
#   * launches only through launch156.ps1, i.e. behind the pidfile gate and the box-cap gate --
#     never above -MaxLab LAB python processes counting the worker AND its one node child;
#   * never more than -MaxWorkers A156 workers;
#   * ONE launch per pass, then a full sleep, so a burst of exits cannot oversubscribe;
#   * every pass re-applies ProcessorAffinity 0xFFFF over every lab python process (the
#     coordinator's hourly requirement, run every pass instead);
#   * touches no pidfile and no sentinel of any other chore.
param(
  [string]$Base = "C:\Users\esumm\code\packing\attempts\A156-day-shift",
  [int]$MaxLab = 16,
  [int]$MaxWorkers = 5,
  [string]$StopHM = "22:45",
  [int]$SleepSec = 600,
  [string]$Deadline = "22:45",
  [int64]$Mask = 0xFFFF
)
$py = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
$env:PYTHONDONTWRITEBYTECODE = "1"
$log = "$Base\logs\scale156.log"
$stop = [datetime]::ParseExact((Get-Date -Format "yyyy-MM-dd") + " " + $StopHM, "yyyy-MM-dd HH:mm", $null)
if ($stop -lt (Get-Date)) { $stop = $stop.AddDays(1) }

function Say($m) { $line = "$(Get-Date -Format 'HH:mm:ss') $m"; Add-Content -Path $log -Value $line -Encoding utf8; $line }

Say "scaler up: MaxLab=$MaxLab MaxWorkers=$MaxWorkers stop=$StopHM sleep=${SleepSec}s mask=0x$('{0:X}' -f $Mask)"
while ($true) {
  if (Test-Path "$Base\PAUSE") { Say "PAUSE sentinel: scaler exits (launches nothing further)"; break }
  if ((Get-Date) -ge $stop) { Say "past ${StopHM}: scaler exits (no launches)"; break }

  & powershell -NonInteractive -ExecutionPolicy Bypass -File "$Base\code\affinity156.ps1" -Mask $Mask -LogFile $log | Out-Null

  $left = [int](& $py "$Base\code\mkqueue156.py")
  $lab  = [int](& powershell -NonInteractive -ExecutionPolicy Bypass -File "$Base\code\labcount156.ps1")
  $mine = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
            Where-Object { $_.CommandLine -like '*run156.py*' }).Count
  if ($left -gt 0 -and ($lab + 2) -le $MaxLab -and $mine -lt $MaxWorkers) {
    $w = "d" + (Get-Date -Format "HHmm")
    $r = & powershell -NonInteractive -ExecutionPolicy Bypass -File "$Base\code\launch156.ps1" `
           -Worker $w -Base $Base -MaxLab $MaxLab -Deadline $Deadline -Mask $Mask
    Say "launch attempt ($left unclaimed, lab python $lab, A156 workers $mine): $r"
  } else {
    Say "hold: lab python $lab (cap $MaxLab), A156 workers $mine (max $MaxWorkers), unclaimed $left"
  }
  Start-Sleep -Seconds $SleepSec
}
