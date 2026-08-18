Set-Location C:\Users\esumm\code\packing\attempts\A11-abinitio-sweep
while (Get-Process -Id 27816 -ErrorAction SilentlyContinue) { Start-Sleep 15 }
python run_queue.py jobs_phase4.json --par 4 --workers 4 *> queue_phase4.log
