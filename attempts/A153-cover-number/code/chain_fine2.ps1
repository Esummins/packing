$ErrorActionPreference='Continue'
$env:PYTHONDONTWRITEBYTECODE='1'
Set-Location 'C:\Users\esumm\code\packing\attempts\A153-cover-number'
while (Get-Process -Id 62012 -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 20 }
& 'C:\Users\esumm\AppData\Local\Python\bin\python.exe' code/run153.py --pop a137 --only 'k5_11_interior_Y1104_D01,k5_11_interior_Y1104_D04,k5_11_interior_Y1104_D05,k5_11_interior_Y1104_D06,k5_11_interior_Y0943,k5_11_interior_Y1110,k5_11_interior_Y0149,k5_11_interior_Y0652' --pitch 0.01 --ntilt 72 --exact-limit 8 --tc mid --out cover153_fine.jsonl *>> logs/fine2.log
& 'C:\Users\esumm\AppData\Local\Python\bin\python.exe' code/run153.py --pop a137 --only 'k5_11_interior_Y1104_D01,k5_11_interior_Y1110' --pitch 0.005 --ntilt 144 --exact-limit 8 --tc mid --out cover153_fine2.jsonl *>> logs/fine2.log
