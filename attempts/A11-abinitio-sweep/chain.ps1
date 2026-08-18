Set-Location C:\Users\esumm\code\packing\attempts\A11-abinitio-sweep
while (Get-Process -Id 1828 -ErrorAction SilentlyContinue) { Start-Sleep 20 }
foreach ($ph in @("phase1b","phase2","phase3")) {
  python run_queue.py "jobs_$ph.json" --par 4 --workers 4 *> "queue_$ph.log"
}
