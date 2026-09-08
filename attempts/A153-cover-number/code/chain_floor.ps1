$ErrorActionPreference='Continue'
$env:PYTHONDONTWRITEBYTECODE='1'
Set-Location 'C:\Users\esumm\code\packing\attempts\A153-cover-number'
& 'C:\Users\esumm\AppData\Local\Python\bin\python.exe' code/floor153.py --pop a148  *>> logs/floor.log
& 'C:\Users\esumm\AppData\Local\Python\bin\python.exe' code/floor153.py --pop k0    *>> logs/floor.log
& 'C:\Users\esumm\AppData\Local\Python\bin\python.exe' code/floor153.py --pop a137  *>> logs/floor.log
