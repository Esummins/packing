# A96 resource census: which python processes are actually COMPUTING, what they own, and the
# working set (not commit -- after the PI's pagefile raise the box is working-set bound, so
# Get-Process WS is the number that matters and FreeVirtualMemory is slack).
#   powershell -File code\census96.ps1 [-Seconds 25]
param([int]$Seconds = 25)

function Snap {
  # CPU from Win32_Process kernel+user time (100-ns units).  Get-Process .CPU is null for
  # processes this session did not start, which silently reported every worker as idle.
  $h = @{}
  foreach ($p in (Get-CimInstance Win32_Process -Filter "Name like 'python%'")) {
    $h[[int]$p.ProcessId] = ([double]$p.KernelModeTime + [double]$p.UserModeTime) / 1e7
  }
  $h
}
$a = Snap
Start-Sleep -Seconds $Seconds
$b = Snap
$procs = Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
         Where-Object { $_.CommandLine -notlike '*windows-mcp*' }
$rows = @()
foreach ($p in $procs) {
  $g = Get-Process -Id $p.ProcessId -ErrorAction SilentlyContinue
  $ws = 0
  if ($g) { $ws = [math]::Round($g.WorkingSet64 / 1MB, 0) }
  # NB cast: CIM ProcessId is UInt32 and the snapshot keys are Int -- an uncast lookup misses
  # every entry and reports the whole box idle.
  $key = [int]$p.ProcessId
  $cpu = -1
  if ($a.ContainsKey($key) -and $b.ContainsKey($key)) {
    $cpu = [math]::Round(($b[$key] - $a[$key]) / $Seconds * 100, 0)
  }
  $cl = $p.CommandLine
  $owner = 'other'
  if ($cl -like '*A96-a57*')            { $owner = 'A96' }
  elseif ($cl -like '*A57-shadow*')     { $owner = 'A57' }
  elseif ($cl -like '*A61-window*' -or $cl -like '*campaign61*' -or $cl -like '*A54-stragglers*') { $owner = 'A61' }
  elseif ($cl -like '*crowd92*' -or $cl -like '*pin1crowd*') { $owner = 'A92' }
  elseif ($cl -like '*slotcrowd94*')    { $owner = 'A94' }
  $script = 'python'
  if ($cl -match '([A-Za-z0-9_]+\.py)') { $script = $Matches[1] }
  $rows += [pscustomobject]@{ PID = $p.ProcessId; Owner = $owner; Script = $script;
                              CPUpct = $cpu; WS_MB = $ws }
}
$rows | Sort-Object CPUpct -Descending | Format-Table -AutoSize
$busy = @($rows | Where-Object { $_.CPUpct -ge 20 })
$sum = ($rows | Measure-Object WS_MB -Sum).Sum
$os = Get-CimInstance Win32_OperatingSystem
Write-Output ("BUSY(>=20% core) = " + $busy.Count + " of " + $rows.Count +
              "   summed WS = " + $sum + " MB" +
              "   free phys = " + [math]::Round($os.FreePhysicalMemory / 1KB, 0) + " MB" +
              "   free commit = " + [math]::Round($os.FreeVirtualMemory / 1KB, 0) + " MB")
Write-Output ("busy by owner: " + (($busy | Group-Object Owner | ForEach-Object { $_.Name + "=" + $_.Count }) -join ' '))
