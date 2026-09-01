"""
A57 — retroactive T14 sweep: apply the `--eps_geo` repair to every cert-FAIL record.

`tree57.py` now runs the eps_geo retry inline (T14), but shards launched before that wiring
record a bare `FAIL(rc=1)`.  This sweep finds every such record across all level-1 and depth-2
jsonl files, re-certifies the node with a row-shrink margin, and appends a corrected record
(board.py keeps the LAST record per id, so the appended line supersedes the FAIL while both stay
on disk for the audit trail).

Only `rc=1` FAILs are eligible: `rc=3` means `certify.py` refused at total >= budget before the
verifier ran, which is the T11 knife edge and wants depth 2 (`deepen.py`), not a margin.

Idempotent and resumable: a node that already has a PASS record, or a `certs/epsgeo/<id>.json.PASS`
marker, is skipped.
"""
import argparse, glob, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
S_RAT = "969271/250000"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--margins", default="0.002,0.004")
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--depth", type=int, default=60)
    ap.add_argument("--cert_time", type=float, default=300)
    ap.add_argument("--scale_cap", type=float, default=1.40)
    ap.add_argument("--wall_seconds", type=float, default=10 ** 9)
    ap.add_argument("--dry_run", action="store_true")
    a = ap.parse_args()

    certdir = os.path.join(BASE, "certs", "epsgeo")
    os.makedirs(certdir, exist_ok=True)
    todo = []
    for p in sorted(glob.glob(os.path.join(BASE, "results", "tree_*.jsonl"))):
        last = {}
        for line in open(p):
            try:
                r = json.loads(line)
            except Exception:
                continue
            last[r["id"]] = r
        for i, r in last.items():
            c = str(r.get("cert", ""))
            if c.startswith("FAIL") and "rc=3" not in c:
                if os.path.exists(os.path.join(certdir, i + ".json.PASS")):
                    continue
                todo.append((p, r))
    print(json.dumps(dict(eligible=len(todo), ids=[r["id"] for _, r in todo])), flush=True)
    if a.dry_run or not todo:
        return

    t0 = time.time()
    for jsonl, r in todo:
        if time.time() - t0 > a.wall_seconds:
            print("wall_seconds reached", flush=True); break
        key = os.path.basename(jsonl)[5:].rsplit("_s", 1)[0].replace(".jsonl", "")
        node = None
        for cand in (os.path.join(BASE, "results", "tree", key, r["id"] + ".json"),
                     os.path.join(BASE, "results", "tree", key + "_D2", r["id"] + ".json")):
            if os.path.exists(cand):
                node = cand; break
        if node is None:
            print(json.dumps(dict(id=r["id"], skipped="node json not found")), flush=True)
            continue
        won = None
        for m in [float(x) for x in a.margins.split(",")]:
            out = os.path.join(certdir, r["id"] + ".json")
            cmd = [sys.executable, os.path.join(HERE, "certify.py"), node, "--s_rat", S_RAT,
                   "--eps_geo", f"{m:g}", "--rounds", str(a.rounds), "--jobs", str(a.jobs),
                   "--depth", str(a.depth), "--time_limit", str(a.cert_time),
                   "--resolve_time", str(a.cert_time), "--out", out, "--scale", "0",
                   "--scale_cap", f"{a.scale_cap:.5f}", "--max_w", "32", "--loop_cols"]
            t1 = time.time()
            p = subprocess.run(cmd, capture_output=True, text=True)
            if p.returncode == 0:
                open(out + ".PASS", "w").write("ok")
                won = (m, round(time.time() - t1, 1), out)
                break
        rec = dict(r)
        if won:
            m, secs, out = won
            rec.update(cert="PASS", cert_path=out, eps_geo_used=m, cert_seconds=secs,
                       note=f"T14 sweep: original {r.get('cert')} (0 holes / undecided witnesses); "
                            f"re-certified with EPS_GEO={m:g}")
        else:
            rec.update(cert="FAIL(eps_geo sweep exhausted) -> queued for depth 2",
                       note="T14 sweep tried " + a.margins)
        with open(jsonl, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(dict(id=r["id"], result=rec["cert"],
                              eps_geo=rec.get("eps_geo_used"))), flush=True)


if __name__ == "__main__":
    main()
