"""A200 driver -- the composed/quick killer over the alive k5_16 pages, each page in its own subprocess under a wall
(the process TREE is killed), <= 3 workers at BelowNormal / affinity 0xFFFF, the lab ceiling (12 pythons excluding
"Claude Extensions") counted and WAITED on, resumable (results/quick200.jsonl: the LAST row per page is the verdict;
a page whose last row has chain_done is skipped), and a git commit after EVERY page verdict.

    python run200.py --list
    python run200.py --shard 0 --nshard 2            # the quick chain (window pad, then pad 0) over the pages
    python run200.py --deep --pages k5_16_interior_Y1056   # the deep path (pair test) in its own process
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, "..", ".."))
RES = os.path.join(ATT, "results", "quick200.jsonl")
CERTS = os.path.join(ATT, "certs")
LOGS = os.path.join(ATT, "logs")
SVGD = os.path.join(ROOT, "docs", "residue_map")
GALLERY = os.path.join(ROOT, "docs", "shadows", "a57v4")


def k516_pages():
    out = []
    for f in sorted(os.listdir(GALLERY)):
        m = re.match(r"(k5_16_interior_Y\d+)\.svg$", f)
        if m:
            out.append(m.group(1))
    return out


def last_rows():
    s = {}
    if os.path.exists(RES):
        for line in open(RES, encoding="utf-8"):
            try:
                d = json.loads(line)
                s[d["nid"]] = d
            except Exception:
                pass
    return s


def lab_count():
    cmd = ("Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { $_.CommandLine -match 'packing' "
           "-and $_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count")
    try:
        return int(subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True).stdout.strip() or 0)
    except Exception:
        return 0


def git_commit(paths, msg):
    """fetch + plain merge are the coordinator's business; here: add + commit the pathspecs, retried on index.lock."""
    for k in range(8):
        try:
            subprocess.run(["git", "add", "--"] + paths, cwd=ROOT, capture_output=True, text=True, timeout=120)
            r = subprocess.run(["git", "commit", "-q", "-m", msg, "--"] + paths, cwd=ROOT, capture_output=True, text=True, timeout=120)
            if r.returncode == 0 or "nothing to commit" in (r.stdout + r.stderr):
                return True
            if "index.lock" not in (r.stdout + r.stderr):
                print("git:", (r.stdout + r.stderr).strip()[:300], flush=True)
        except Exception as e:
            print("git exception:", e, flush=True)
        time.sleep(3 + 2 * k)
    return False


def run_one(nid, wall, mode, svg=True):
    os.makedirs(CERTS, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    cert = os.path.join(CERTS, "q200_%s%s.json" % (nid, "" if mode == "chain" else "_deep"))
    logp = os.path.join(LOGS, "q200_%s%s.log" % (nid, "" if mode == "chain" else "_deep"))
    log = open(logp, "a", encoding="utf-8")
    args = [sys.executable, os.path.join(HERE, "quick200.py"), nid, "--wall", str(wall), "--cert", cert, "--out", RES]
    svgp = os.path.join(SVGD, "quick200_%s.svg" % nid)
    if mode == "chain":
        args += ["--chain"]
    else:
        args += ["--deep", "--noseal"]
    if svg:
        args += ["--svg", svgp]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1")
    t0 = time.time()
    p = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, env=env, cwd=ROOT,
                         creationflags=getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0))
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-Process -Id %d).ProcessorAffinity = 0xFFFF" % p.pid],
                       capture_output=True)
    except Exception:
        pass
    total = wall * (2 if mode == "chain" else 1) + 300
    try:
        rc = p.wait(timeout=total)
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
        rc = "killed"
        with open(RES, "a", encoding="utf-8") as f:
            f.write(json.dumps(dict(nid=nid, verdict="ALIVE", path=mode, pad="-", chain_done=(mode == "chain"),
                                    leaf="wall %ss reached (process tree killed): undecided" % total,
                                    seconds=round(time.time() - t0, 1), killed=True, when=time.strftime("%Y-%m-%d %H:%M:%S"))) + "\n")
    log.close()
    paths = [os.path.relpath(RES, ROOT), os.path.relpath(cert, ROOT), os.path.relpath(logp, ROOT)]
    if os.path.exists(svgp):
        paths.append(os.path.relpath(svgp, ROOT))
    last = last_rows().get(nid, {})
    git_commit(paths, "A200: %s %s [%s; %s] %.0fs" % (nid, last.get("verdict", "?"), last.get("step_killed") or last.get("path") or mode,
                                                    last.get("pad", "-"), time.time() - t0))
    return rc, time.time() - t0


def worker(pages, wall, shard, nshard, svg, mode):
    for k, nid in enumerate(pages):
        if k % nshard != shard:
            continue
        last = last_rows().get(nid)
        if last and not FORCE:
            if mode == "chain" and (last.get("chain_done") or last.get("verdict") == "DEAD"):
                continue
            if mode == "deep" and (last.get("path") == "deep" or last.get("verdict") == "DEAD"):
                continue
        while lab_count() >= 12:
            time.sleep(60)
        rc, dt = run_one(nid, wall, mode, svg)
        print("%s %s rc=%s %.0fs" % (time.strftime("%H:%M:%S"), nid, rc, dt), flush=True)


FORCE = False
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--wall", type=float, default=900)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshard", type=int, default=1)
    ap.add_argument("--nosvg", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--deep", action="store_true")
    ap.add_argument("--pages", nargs="*")
    ap.add_argument("--skip", nargs="*", default=[])
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    FORCE = a.force
    pages = [p for p in (a.pages or k516_pages()) if p not in a.skip]
    if a.list:
        print(len(pages), pages)
        sys.exit()
    worker(pages, a.wall, a.shard, a.nshard, not a.nosvg, "deep" if a.deep else "chain")
