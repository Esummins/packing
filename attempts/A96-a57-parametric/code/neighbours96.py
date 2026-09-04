"""A96: stamp every newly-solved node with the concurrency it was solved under.

The contention read wants per-node wall AT a known neighbour count. A57's tree rows carry no
timestamp and tree57.py is another campaign's code that is mid-run, so it is not instrumented;
instead this sampler watches the result files from outside and records, for each row that
APPEARS while it is running, the busy-process count at the moment it appeared.

Cheap by construction: one CIM query and a few small file reads every --interval seconds, then
sleep.  It is not a heavy process (0% of a core between samples) and does not count against the
process budget.  It never writes into another campaign's tree.

"Busy" = a python process burning >= 20% of one core between two consecutive samples, measured
from Win32_Process kernel+user time.  Idle drivers and watchers (campaign61.py, sweepfails.py,
param96.py itself) are correctly excluded; they hold no core.

Writes results/neighbours96.jsonl, one record per newly-seen row:
    {file, id, t, iso, busy, busy_by_owner, ws_sum_mb}
and results/neighbours96_timeline.jsonl, one record per sample, so a window with no new rows is
still attributable.
"""
import argparse, glob, json, os, subprocess, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A57 = os.path.abspath(os.path.join(BASE, "..", "A57-shadow-trees"))
OUT = os.path.join(BASE, "results")
PATTERNS = [os.path.join(A57, "results", "tree_k5_1*_interior_G1_s*.jsonl"),
            os.path.join(A57, "results", "tree_k5_1*_interior_G1_D2.jsonl"),
            os.path.join(OUT, "param96.jsonl")]

PS = r"""
$rows = Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
        Where-Object { $_.CommandLine -notlike '*windows-mcp*' }
$out = foreach ($p in $rows) {
  $g = Get-Process -Id $p.ProcessId -ErrorAction SilentlyContinue
  $ws = 0; if ($g) { $ws = [math]::Round($g.WorkingSet64/1MB,0) }
  $cl = $p.CommandLine
  $owner = 'other'
  if ($cl -like '*A96-a57*') { $owner = 'A96' }
  elseif ($cl -like '*A57-shadow*') { $owner = 'A57' }
  elseif ($cl -like '*A61-window*' -or $cl -like '*campaign61*' -or $cl -like '*A54-stragglers*') { $owner = 'A61' }
  elseif ($cl -like '*crowd92*' -or $cl -like '*pin1crowd*') { $owner = 'A92' }
  elseif ($cl -like '*slotcrowd94*') { $owner = 'A94' }
  '{0},{1},{2},{3}' -f $p.ProcessId, $owner, (([double]$p.KernelModeTime + [double]$p.UserModeTime)/1e7), $ws
}
$out -join ';'
"""


def sample():
    try:
        r = subprocess.run(["powershell", "-NonInteractive", "-Command", PS],
                           capture_output=True, text=True, timeout=60)
        out = {}
        for tok in (r.stdout or "").strip().split(";"):
            if not tok.strip():
                continue
            pid, owner, cpu, ws = tok.strip().split(",")
            out[int(pid)] = (owner, float(cpu), int(ws))
        return out
    except Exception:
        return {}


def ids():
    seen = {}
    for pat in PATTERNS:
        for f in sorted(glob.glob(pat)):
            b = os.path.basename(f)
            try:
                for ln in open(f):
                    ln = ln.strip()
                    if not ln:
                        continue
                    try:
                        seen.setdefault(b + "|" + str(json.loads(ln).get("id")), None)
                    except Exception:
                        pass
            except Exception:
                pass
    return set(seen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=float, default=30.0)
    ap.add_argument("--minutes", type=float, default=180.0)
    a = ap.parse_args()
    rec = os.path.join(OUT, "neighbours96.jsonl")
    tl = os.path.join(OUT, "neighbours96_timeline.jsonl")
    known = ids()
    prev = sample()
    t_end = time.time() + a.minutes * 60
    while time.time() < t_end:
        time.sleep(a.interval)
        cur = sample()
        busy, by_owner, ws = 0, {}, 0
        for pid, (owner, cpu, w) in cur.items():
            ws += w
            if pid in prev and (cpu - prev[pid][1]) / a.interval >= 0.20:
                busy += 1
                by_owner[owner] = by_owner.get(owner, 0) + 1
        prev = cur
        now = ids()
        new = sorted(now - known)
        known = now
        t = time.time()
        iso = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(tl, "a") as fh:
            fh.write(json.dumps(dict(t=t, iso=iso, busy=busy, by_owner=by_owner,
                                     ws_sum_mb=ws, new_rows=len(new))) + "\n")
        if new:
            with open(rec, "a") as fh:
                for k in new:
                    f, i = k.split("|", 1)
                    fh.write(json.dumps(dict(file=f, id=i, t=t, iso=iso, busy=busy,
                                             busy_by_owner=by_owner, ws_sum_mb=ws)) + "\n")
            print(f"{iso} busy={busy} {by_owner} +{len(new)} rows", flush=True)
    print("neighbours96 done", flush=True)


if __name__ == "__main__":
    main()
