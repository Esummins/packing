"""A190 -- re-certify, WITHOUT an LP, the kill candidates whose certificate on disk did not PASS (e.g. the
certificates written before the (G3) inherited-mass fix of verify_case_v5): runs verify_case_v5 IN-PROCESS on
certs/<id>.json (one python; gated by the <= 2 rule) and appends a `leg: "recert"` row to results/run190.jsonl
carrying the previous row's LP data with the new verdict.    python recert190.py [--only ID,ID] [--depth 56]
"""
import argparse
import contextlib
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
RES, CERTS = os.path.join(BASE, "results"), os.path.join(BASE, "certs")
sys.path.insert(0, HERE)
import prio190                                                   # noqa: E402
import verify_case_v5 as v5                                      # noqa: E402

OUT = os.path.join(RES, "run190.jsonl")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--depth", type=int, default=56)
    a = ap.parse_args()
    last = {}
    for ln in open(OUT, encoding="utf-8"):
        if ln.strip():
            r = json.loads(ln)
            last[r["id"]] = r
    want = set(x for x in a.only.split(",") if x)
    for nid, r in sorted(last.items()):
        if want and nid not in want:
            continue
        if not r.get("kills") or r.get("certified") == "PASS":
            continue
        cert = os.path.join(CERTS, nid + ".json")
        if not os.path.exists(cert):
            continue
        prio190.wait_mine(limit=2, max_wait=7200)
        t0 = time.time()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = v5.main([cert, "--jobs", "1", "--depth", str(a.depth), "--max-witnesses", "64", "--quiet", "--report"])
        tail = [l for l in buf.getvalue().splitlines() if l.startswith(("PASS", "FAIL", "free clause", "window clause", "MALFORMED", "  guard"))]
        rec = dict(r)
        rec.update(leg="recert", certified=("PASS" if rc == 0 else ("REJECTED" if rc == 2 else "FAIL")), recert_rc=rc,
                   cert_log=(r.get("cert_log") or []) + [dict(round="recert", rc=rc, verifier=tail[:12])],
                   cert=os.path.relpath(cert, ROOT).replace("\\", "/"), when=time.strftime("%Y-%m-%d %H:%M"),
                   recert_s=round(time.time() - t0, 1))
        rec["verdict"] = ("DEAD(LP, v5 certified) [C under v5 ONLY]" if rc == 0
                          else "LP-dead, v5 certificate %s (kill candidate)" % rec["certified"])
        if rc == 0:
            json.dump(dict(cert=cert, rounds=rec["cert_log"], result="PASS", verifier="verify_case_v5 (A190)",
                           label="[C] under v5 only"), open(cert.replace(".json", ".certify.json"), "w"), indent=1)
        with open(OUT, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, default=str) + "\n")
        print("%-26s recert rc %s -> %s (%.1fs)" % (nid, rc, rec["verdict"], time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
