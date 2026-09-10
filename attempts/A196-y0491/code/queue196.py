"""run a command once the box gate (lab ceiling 12 incl. this one, memory) and the <= 3 own rule allow it.
    python queue196.py <log> -- <args...>"""
import subprocess
import sys

import prio196

log = sys.argv[1]
args = sys.argv[sys.argv.index("--") + 1:]
prio196.wait_mine(limit=3, max_wait=6 * 3600, log=lambda s: print(s, flush=True))
ok, mem = prio196.wait_box(own=1, max_wait=6 * 3600, log=lambda s: print(s, flush=True))
print("gate", ok, mem, flush=True)
if ok:
    subprocess.run([sys.executable, "-u"] + args, stdout=open(log, "a"), stderr=subprocess.STDOUT)
