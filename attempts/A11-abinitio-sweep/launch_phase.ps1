param([string]$phase)
Set-Location C:\Users\esumm\code\packing\attempts\A11-abinitio-sweep
Start-Process -FilePath python -ArgumentList "run_queue.py","jobs_$phase.json","--par","4","--workers","4" -RedirectStandardOutput "queue_$phase.log" -RedirectStandardError "queue_$phase.err" -WindowStyle Hidden
