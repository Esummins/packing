$ErrorActionPreference='Continue'
$env:PYTHONDONTWRITEBYTECODE='1'
Set-Location 'C:\Users\esumm\code\packing\attempts\A153-cover-number'
while (Get-Process -Id 42496 -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 20 }
& 'C:\Users\esumm\AppData\Local\Python\bin\python.exe' code/run153.py --pop a148 --only 'f1_L10_0003,k5_11_interior_Y1110,k5_11_interior_Y0147,k5_11_interior_Y0308,k5_11_interior_Y0662,k5_11_interior_Y0985,k5_11_interior_Y1104,k5_11_interior_Y0130,k5_11_interior_Y0275,k5_16_interior_Y0881' --pitch 0.01 --ntilt 72 --exact-limit 8 --tc mid --out cover153_fine.jsonl *>> logs/fine.log
