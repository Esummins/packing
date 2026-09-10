"""A198 -- the a57v4 pass: every ALIVE page of docs/shadows/STATUS.md except k5_16_interior_Y0491 (A196), each in its
own subprocess under a per-page wall (the process TREE is killed), resumable (results/fastprop198.jsonl: one row per
page; pages already present are skipped), `--workers` processes at BelowNormal / affinity 0xFFFF.
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
RES = os.path.join(ATT, "results", "fastprop198.jsonl")
CERTS = os.path.join(ATT, "certs")
LOGS = os.path.join(ATT, "logs")
SVGD = os.path.join(ROOT, "docs", "residue_map")
FORCE = False


def alive_pages(skip=("k5_16_interior_Y0491",)):
    out = []
    for line in open(os.path.join(ROOT, "docs", "shadows", "STATUS.md"), encoding="utf-8"):
        m = re.match(r"\| \[ \] \[`([^`]+)\.svg`\]\(([^)]+)\) \| `([^`]+)` \| `([^`]+)` \|", line)
        if m and "ALIVE" in line and m.group(4) != "k0_00" and m.group(3) not in skip:
            out.append(m.group(3))
    return out


def done_pages():
    s = set()
    if os.path.exists(RES):
        for line in open(RES, encoding="utf-8"):
            try:
                s.add(json.loads(line)["nid"])
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


def run_one(nid, wall, svg=True):
    os.makedirs(CERTS, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    cert = os.path.join(CERTS, "fp198_%s.json" % nid)
    log = open(os.path.join(LOGS, "fp198_%s.log" % nid), "a", encoding="utf-8")
    args = [sys.executable, os.path.join(HERE, "fastprop.py"), nid, "--wall", str(wall), "--cert", cert, "--out", RES]
    if svg:
        args += ["--svg", os.path.join(SVGD, "fastprop_%s.svg" % nid)]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1")
    t0 = time.time()
    p = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, env=env, cwd=ROOT,
                         creationflags=getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0))
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-Process -Id %d).ProcessorAffinity = 0xFFFF" % p.pid],
                       capture_output=True)
    except Exception:
        pass
    try:
        rc = p.wait(timeout=wall + 120)
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
        rc = "killed"
        with open(RES, "a", encoding="utf-8") as f:
            f.write(json.dumps(dict(nid=nid, verdict="ALIVE", leaf="wall %ss reached (process tree killed): undecided" % wall,
                                    seconds=round(time.time() - t0, 1), killed=True)) + "\n")
    log.close()
    return rc, time.time() - t0


def worker(pages, wall, shard, nshard, svg):
    for k, nid in enumerate(pages):
        if k % nshard != shard:
            continue
        if nid in done_pages() and not FORCE:
            continue
        while lab_count() >= 12:
            time.sleep(60)
        rc, dt = run_one(nid, wall, svg)
        print("%s %s rc=%s %.0fs" % (time.strftime("%H:%M:%S"), nid, rc, dt), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--wall", type=float, default=600)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshard", type=int, default=1)
    ap.add_argument("--nosvg", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--pages", nargs="*")
    ap.add_argument("--force", action="store_true", help="re-run pages that already have a row (a new LAST row supersedes)")
    a = ap.parse_args()
    FORCE = a.force
    pages = a.pages or alive_pages()
    if a.list:
        print(len(pages), pages)
        sys.exit()
    worker(pages, a.wall, a.shard, a.nshard, not a.nosvg)
