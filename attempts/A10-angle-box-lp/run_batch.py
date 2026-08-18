"""Run a list of lp_measure_box.py jobs with at most --procs concurrent processes.
Job file: JSON list of {"name": ..., "args": [...]} ; each job logs to logs/<name>.log and writes results/<name>.json.
Skips jobs whose results/<name>.json already exists (so a killed batch can simply be restarted).
"""
import json, subprocess, sys, time, os, argparse

ap = argparse.ArgumentParser()
ap.add_argument("jobs")
ap.add_argument("--procs", type=int, default=6)
ap.add_argument("--force", action="store_true")
a = ap.parse_args()
here = os.path.dirname(os.path.abspath(__file__))
jobs = json.load(open(a.jobs))
queue = []
for j in jobs:
    out = os.path.join(here, "results", j["name"] + ".json")
    logp = os.path.join(here, "logs", j["name"] + ".log")
    if (os.path.exists(out) or os.path.exists(logp)) and not a.force:
        print("skip (done or started):", j["name"]); continue
    queue.append(j)
running = []
while queue or running:
    while queue and len(running) < a.procs:
        j = queue.pop(0)
        out = os.path.join(here, "results", j["name"] + ".json")
        log = open(os.path.join(here, "logs", j["name"] + ".log"), "w")
        cmd = [sys.executable, os.path.join(here, "lp_measure_box.py"), "--out", out] + j["args"]
        p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=here)
        running.append((j["name"], p, log, time.time()))
        print(time.strftime("%H:%M:%S"), "start", j["name"], flush=True)
    time.sleep(5)
    still = []
    for name, p, log, t0 in running:
        if p.poll() is None:
            still.append((name, p, log, t0))
        else:
            log.close()
            print(time.strftime("%H:%M:%S"), f"done {name} rc={p.returncode} {time.time()-t0:.0f}s", flush=True)
    running = still
print("batch finished")
