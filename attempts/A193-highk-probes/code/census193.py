import subprocess
out = subprocess.run(['powershell', '-NoProfile', '-Command',
    'Get-CimInstance Win32_Process -Filter "Name like \'python%\'" | ForEach-Object { "$($_.ProcessId)|$([int]($_.WorkingSetSize/1MB))|$($_.CommandLine)" }'],
    capture_output=True, text=True).stdout
n = 0
for l in out.splitlines():
    if not l.strip() or 'Claude Extensions' in l:
        continue
    n += 1
    i = l.find('python.exe')
    print(l[:l.find('|', l.find('|') + 1) + 1] + l[i + 10:][:110] if i > 0 else l[:140])
print('lab pythons', n)
